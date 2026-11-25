import json
import os
import re
import socket
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
LOG_PATH = os.path.join(WORK, "_日志.jsonl")

import os as _os2, sys as _sys2
_sys2.path.insert(0, _os2.path.dirname(_os2.path.dirname(_os2.path.abspath(__file__))))
import paths as _P
CLI_BIN = _P.DT_CLI
MODELS_DIR = _P.DT_MODELS_DIR
from pools import roll_params as _RP_MODEL
BASE_MODEL = _RP_MODEL.MODEL_FILE
WIDTH, HEIGHT, STEPS = 1024, 1536, 8

def engine():
    return _P.engine()

USE_DT_SERVER = os.environ.get("DT_SERVER", "0") == "1"
DT_SERVER_PORT = 7859
_REMOTE_STATE = {"checked": False, "up": False}

_CLI_RE_TOTAL = re.compile(
    r"Total generation time \(including model loading\):\s*([\d.]+)\s*(ms|s)\b")
_CLI_RE_STEP = re.compile(
    r"Sampling step time \((\d+)\s*step\(s\)\):\s*avg\s*([\d.]+)\s*(ms|s)\b")

def _cli_sec(val, unit):
    try:
        v = float(val)
    except (TypeError, ValueError):
        return None
    return round(v / 1000.0, 3) if str(unit).lower() == "ms" else round(v, 3)

DT_SERVER_PORTS = (DT_SERVER_PORT, 7860)

def dt_server_up(port=None):
    if not USE_DT_SERVER:
        return False
    if _REMOTE_STATE["checked"]:
        return _REMOTE_STATE["up"]
    for _p in (DT_SERVER_PORTS if port is None else (port,)):
        sk = socket.socket()
        sk.settimeout(0.3)
        try:
            sk.connect(("127.0.0.1", _p))
            _REMOTE_STATE.update({"up": True, "port": _p})
            break
        except Exception:
            _REMOTE_STATE["up"] = False
        finally:
            sk.close()
    _REMOTE_STATE["checked"] = True
    print("[io] Draw Things server %s" %
          ("已启用（端口 %s）→ 走 --remote" % _REMOTE_STATE.get("port")
           if _REMOTE_STATE["up"] else "未启用 → 本地加载（每张多花 ~15 秒 ✗）"), flush=True)
    return _REMOTE_STATE["up"]

def parse_cli_timing(stdout):
    r = {"cli_total_sec": None, "cli_step_avg_sec": None,
         "cli_step_n": None, "cli_load_sec": None}
    if not stdout:
        return r
    m = _CLI_RE_TOTAL.search(stdout)
    if m:
        r["cli_total_sec"] = _cli_sec(m.group(1), m.group(2))
    m2 = _CLI_RE_STEP.search(stdout)
    if m2:
        r["cli_step_n"] = int(m2.group(1))
        r["cli_step_avg_sec"] = _cli_sec(m2.group(2), m2.group(3))
    return r

def _sampler_name(n):
    return {
        0: "DPM++ 2M Karras", 1: "Euler A", 2: "DDIM", 3: "UniPC",
        4: "DPM++ SDE Karras", 5: "PLMS", 6: "LCM",
        7: "Euler A Substep", 8: "DPM++ SDE Substep", 9: "TCD",
        10: "Euler A Trailing", 11: "DPM++ SDE Trailing",
        12: "DPM++ 2M AYS", 13: "Euler A AYS", 14: "DPM++ SDE AYS",
        15: "DPM++ 2M Trailing", 16: "DDIM Trailing",
        17: "UniPC Trailing", 18: "UniPC AYS", 19: "TCD Trailing",
    }.get(int(n), "TCD Trailing")

def _gui_alive():
    try:
        import urllib.request
        base = getattr(_RP_MODEL, "GUI_API_URL", "http://127.0.0.1:7860").rstrip("/")
        req = urllib.request.Request(base + "/sdapi/v1/options",
                                     headers={"User-Agent": "roll_machine"})
        with urllib.request.urlopen(req, timeout=3) as r:
            return 200 <= r.status < 300
    except Exception:
        return False

def _gui_dupe_dir():
    import paths as _P
    import datetime as _dt
    d = os.path.join(os.path.dirname(_P.OUT_ROOT), "_GUI重复归档",
                     _dt.datetime.now().strftime("%Y%m%d"))
    os.makedirs(d, exist_ok=True)
    return d

def _sweep_gui_dupe(seed, keep_path):
    try:
        import time
        import paths as _P
        root = os.path.dirname(_P.OUT_ROOT)
        tail = "_%s.png" % seed
        now = time.time()
        moved = []
        for fn in os.listdir(root):
            if not fn.endswith(tail):
                continue
            p = os.path.join(root, fn)
            if not os.path.isfile(p):
                continue
            if os.path.abspath(p) == os.path.abspath(keep_path):
                continue
            if now - os.path.getmtime(p) > 600:
                continue
            try:
                os.rename(p, os.path.join(_gui_dupe_dir(), fn))
                moved.append(fn)
            except Exception:
                pass
        return moved
    except Exception:
        return []

def _generate_gui(prompt, cfg_json, seed, out, w, h, steps):
    import base64
    import urllib.request

    import roll_params as _P
    url = getattr(_P, "GUI_API_URL", "http://127.0.0.1:7860").rstrip("/") + "/sdapi/v1/txt2img"
    body = {
        "prompt": prompt,
        "negative_prompt": "",
        "steps": int(steps),
        "width": int(w),
        "height": int(h),
        "cfg_scale": float(getattr(_P, "CFG", 1.0)),
        "seed": int(seed),
        "sampler_name": _sampler_name(cfg_json.get("sampler", _P.SAMPLER)),
    }
    if "shift" in cfg_json:
        body["shift"] = float(cfg_json["shift"])
    if "resolutionDependentShift" in cfg_json:
        body["resolution_dependent_shift"] = bool(cfg_json["resolutionDependentShift"])
    if "stochasticSamplingGamma" in cfg_json:
        body["stochastic_sampling_gamma"] = float(cfg_json["stochasticSamplingGamma"])
    loras = cfg_json.get("loras")
    if loras is None:
        body["loras"] = []
    else:
        body["loras"] = [
            {"file": x.get("file"), "weight": x.get("weight", 1.0),
             "mode": x.get("mode", "all")}
            for x in loras if isinstance(x, dict)
        ]
    t0 = time.time()
    try:
        req = urllib.request.Request(
            url, data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=getattr(_P, "GUI_API_TIMEOUT", 900)) as r:
            data = json.load(r)
        imgs = data.get("images") or []
        if not imgs:
            return False, round(time.time() - t0, 2), "GUI 返回空 images", 0
        raw = base64.b64decode(imgs[0].split(",")[-1])
        with open(out, "wb") as f:
            f.write(raw)
        ok = os.path.exists(out) and os.path.getsize(out) > 20_000
        if ok and getattr(_RP_MODEL, "SWEEP_GUI_DUPE", False):
            _mv = _sweep_gui_dupe(seed, out)
            if _mv:
                print("  [GUI重复已归档] %s" % _mv[0], flush=True)
        return ok, round(time.time() - t0, 2), ("" if ok else "GUI 出图过小"), len(raw)
    except Exception as e:
        return False, round(time.time() - t0, 2), "%s: %s" % (type(e).__name__, e), 0

def generate(tag, prompt, cfg_json, seed, outdir, size=None, steps=None):
    out = os.path.join(outdir, "%s.png" % tag)
    w, h = (size or (WIDTH, HEIGHT))
    _steps = int(steps or STEPS)

    if engine() == "comfyui":
        from . import backend_comfy
        return backend_comfy.generate(tag, prompt, cfg_json, seed, outdir,
                                      size=(w, h), steps=_steps)

    if getattr(_RP_MODEL, "USE_GUI_API", False):
        if _gui_alive():
            ok, sec, err, _n = _generate_gui(prompt, cfg_json, seed, out, w, h, _steps)
            if ok:
                return ok, sec, out, "", {"engine": "gui"}
            _gui_err = err
        else:
            _gui_err = "GUI 未响应"
    else:
        _gui_err = ""

    cmd = [CLI_BIN, "generate", "--models-dir", MODELS_DIR, "--model", BASE_MODEL,
           "--config-json", json.dumps(cfg_json), "--prompt", prompt,
           "--negative-prompt", "", "--steps", str(_steps),
           "--cfg", str(float(getattr(_P, "CFG", 1.0))),
           "--width", str(w), "--height", str(h), "--seed", str(seed), "--output", out]
    if dt_server_up():
        cmd += ["--remote", "--remote-url", "127.0.0.1",
                "--remote-port", str(_REMOTE_STATE.get("port") or DT_SERVER_PORT),
                "--remote-tls"]
    t0 = time.time()
    err = ""
    timing: dict = {}
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=900, text=True,
                           encoding="utf-8", errors="replace")
        from pools.imgcheck import is_image_file
        ok = is_image_file(out)
        if not ok:
            err = ((r.stderr or "") + (r.stdout or "")).strip()[:1200]
        timing = parse_cli_timing(r.stdout)
        timing["engine"] = "cli"
        if _gui_err:
            timing["gui_fallback"] = _gui_err
    except Exception as e:
        ok, err = False, "%s: %s" % (type(e).__name__, e)
    return ok, round(time.time() - t0, 2), out, err, timing

def log_line(obj):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def selfcheck():
    bad = []
    if engine() == "comfyui":
        from . import backend_comfy
        info = backend_comfy.probe()
        if not info.get("alive"):
            bad.append("ComfyUI 连不上: %s（环境变量 COMFY_URL 可改）" % info.get("error"))
        elif info.get("unet_ok") is False:
            bad.append("ComfyUI 里没有 UNET %s（模型名别带目录前缀）"
                       % backend_comfy.UNET_NAME)
        print("roll_io 自检（引擎 comfyui）：%s" % ("通过" if not bad else "✗ " + "；".join(bad)))
        return not bad
    if not os.path.exists(CLI_BIN):
        bad.append("CLI 不存在: %s" % CLI_BIN)
    if not os.path.isdir(MODELS_DIR):
        bad.append("模型目录不存在: %s" % MODELS_DIR)
    else:
        p = os.path.join(MODELS_DIR, BASE_MODEL)
        if not os.path.exists(p):
            bad.append("主模型不在: %s" % p)
        elif not os.path.exists(p + "-tensordata"):
            bad.append("主模型的权重件不在: %s-tensordata" % p)
    t = parse_cli_timing("Total generation time (including model loading): 12.3s\n"
                         "Sampling step time (8 step(s)): avg 980ms")
    if t["cli_total_sec"] != 12.3 or t["cli_step_n"] != 8 or t["cli_step_avg_sec"] != 0.98:
        bad.append("耗时解析不对: %s" % t)
    print("roll_io 自检（引擎 drawthings）：%s" % ("通过" if not bad else "✗ " + "；".join(bad)))
    return not bad

if __name__ == "__main__":
    import sys
    _P.setup_console()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(0 if selfcheck() else 1)
