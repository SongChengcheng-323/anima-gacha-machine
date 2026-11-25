import json
import os
import time
import urllib.parse
import urllib.request
import uuid

COMFY_URL = os.environ.get("COMFY_URL", "http://127.0.0.1:8188").rstrip("/")

UNET_NAME = os.environ.get("COMFY_UNET", "anima-turbo-v1.1.safetensors")
CLIP_NAME = os.environ.get("COMFY_CLIP", "qwen_3_06b_base.safetensors")
VAE_NAME = os.environ.get("COMFY_VAE", "qwen_image_vae.safetensors")

SAMPLER = os.environ.get("COMFY_SAMPLER", "er_sde")
SCHEDULER = os.environ.get("COMFY_SCHEDULER", "simple")
CFG = 1.0

DEFAULT_NEGATIVE = ("worst quality, low quality, score_1, score_2, score_3, "
                    "artist name, blurry, jpeg artifacts, chromatic aberration")

MIN_BYTES = 20_000
POLL_INTERVAL = 1.5
WAIT_TIMEOUT = float(os.environ.get("COMFY_TIMEOUT", "900"))

def _post_json(url, payload, timeout=30):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        # ComfyUI 把真正的校验失败写在响应体 node_errors 里，不读出来就只剩 400
        body = ""
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:
            pass
        raise RuntimeError("ComfyUI 校验失败 %s: %s" % (e.code, body[:800])) from e

def _get_json(url, timeout=20):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.load(r)

def build_workflow(prompt, width, height, seed, steps, prefix,
                   negative=None, cfg=None, sampler=None, scheduler=None,
                   batch_size=1):
    return {
        "44": {"class_type": "UNETLoader",
               "inputs": {"unet_name": UNET_NAME, "weight_dtype": "default"}},
        "45": {"class_type": "CLIPLoader",
               "inputs": {"clip_name": CLIP_NAME, "type": "stable_diffusion",
                          "device": "default"}},
        "15": {"class_type": "VAELoader",
               "inputs": {"vae_name": VAE_NAME}},
        "11": {"class_type": "CLIPTextEncode",
               "inputs": {"text": prompt, "clip": ["45", 0]}},
        "12": {"class_type": "CLIPTextEncode",
               "inputs": {"text": negative or DEFAULT_NEGATIVE, "clip": ["45", 0]}},
        "28": {"class_type": "EmptyLatentImage",
               "inputs": {"width": int(width), "height": int(height),
                          "batch_size": int(batch_size)}},
        "19": {"class_type": "KSampler",
               "inputs": {"seed": int(seed), "steps": int(steps),
                          "cfg": float(cfg if cfg is not None else CFG),
                          "sampler_name": sampler or SAMPLER,
                          "scheduler": scheduler or SCHEDULER,
                          "denoise": 1.0,
                          "model": ["44", 0],
                          "positive": ["11", 0],
                          "negative": ["12", 0],
                          "latent_image": ["28", 0]}},
        "8":  {"class_type": "VAEDecode",
               "inputs": {"samples": ["19", 0], "vae": ["15", 0]}},
        "9":  {"class_type": "SaveImage",
               "inputs": {"images": ["8", 0], "filename_prefix": prefix}},
    }

def submit(workflow):
    r = _post_json("%s/prompt" % COMFY_URL,
                   {"prompt": workflow, "client_id": str(uuid.uuid4())})
    pid = r.get("prompt_id")
    if not pid:
        raise RuntimeError("ComfyUI 没返回 prompt_id：%s" % (r,))
    return pid

def wait(pid, timeout=None):
    timeout = WAIT_TIMEOUT if timeout is None else timeout
    t0 = time.time()
    while time.time() - t0 < timeout:
        h = _get_json("%s/history/%s" % (COMFY_URL, pid))
        if pid in h:
            return h[pid], time.time() - t0
        time.sleep(POLL_INTERVAL)
    return None, time.time() - t0

def fetch(record, out_path):
    imgs = [i for node in (record.get("outputs") or {}).values()
            for i in (node.get("images") or [])]
    if not imgs:
        return False, "任务完成但没有输出图"
    im = imgs[0]
    q = urllib.parse.urlencode({
        "filename": im.get("filename", ""),
        "subfolder": im.get("subfolder", "") or "",
        "type": im.get("type", "output") or "output",
    })
    try:
        with urllib.request.urlopen("%s/view?%s" % (COMFY_URL, q), timeout=600) as r:
            data = r.read()
    except Exception as e:
        return False, "%s: %s" % (type(e).__name__, e)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(data)
    from pools.imgcheck import is_image_bytes
    if not is_image_bytes(data, MIN_BYTES):
        return False, "下载到的不是有效图片（%d 字节）" % len(data)
    return True, ""

def generate(tag, prompt, cfg_json, seed, outdir, size=None, steps=None,
             negative=None, timeout=None, keep_remote=False):
    out = os.path.join(outdir, "%s.png" % tag)
    w, h = (size or (1024, 1536))
    _steps = int(steps or 12)
    t0 = time.time()
    timing: dict = {"engine": "comfyui"}
    try:
        wf = build_workflow(prompt, w, h, seed, _steps, tag, negative=negative)
        t_sub = time.time()
        pid = submit(wf)
        timing["submit_s"] = round(time.time() - t_sub, 2)
        rec, waited = wait(pid, timeout=timeout)
        timing["wait_s"] = round(waited, 1)
        if rec is None:
            return False, round(time.time() - t0, 2), out, \
                "等待超时（%.0fs）" % waited, timing
        st = (rec.get("status") or {}).get("status_str")
        timing["status"] = st
        if st and st != "success":
            return False, round(time.time() - t0, 2), out, "任务状态 %s" % st, timing
        if keep_remote:
            timing["remote_only"] = True
            return True, round(time.time() - t0, 2), "", "", timing
        t_dl = time.time()
        ok, err = fetch(rec, out)
        timing["download_s"] = round(time.time() - t_dl, 1)
        if not ok:
            return False, round(time.time() - t0, 2), out, err, timing
        timing["bytes"] = os.path.getsize(out)
        return True, round(time.time() - t0, 2), out, "", timing
    except Exception as e:
        return False, round(time.time() - t0, 2), out, \
            "%s: %s" % (type(e).__name__, e), timing

def probe():
    try:
        stats = _get_json("%s/system_stats" % COMFY_URL, timeout=10)
    except Exception as e:
        return {"alive": False, "error": "%s: %s" % (type(e).__name__, e)}
    devs = stats.get("devices") or []
    info = {"alive": True,
            "version": (stats.get("system") or {}).get("comfyui_version"),
            "device": devs[0].get("name") if devs else None,
            "vram_gb": round((devs[0].get("vram_total") or 0) / 1e9, 1) if devs else None,
            "unet": UNET_NAME, "clip": CLIP_NAME, "vae": VAE_NAME}
    try:
        oi = _get_json("%s/object_info/UNETLoader" % COMFY_URL, timeout=15)
        have = set(oi["UNETLoader"]["input"]["required"]["unet_name"][0])
        info["unet_ok"] = UNET_NAME in have
    except Exception:
        info["unet_ok"] = None
    return info

if __name__ == "__main__":
    print(json.dumps(probe(), ensure_ascii=False, indent=1))
