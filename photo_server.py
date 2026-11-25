import sys
import paths as PATHS
import json, os, random, re, shutil, signal, subprocess, sys, threading, time, urllib.parse
from collections import Counter, defaultdict
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

from album.util import *
from album.util import _norm, _NAME_IDX, _name_index, _norm_key

try:
    PATHS.setup_console()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


_cache = {"photos": None, "mtime": 0, "at": 0}
REDRAW_JOBS = {}

REDRAW_QUEUE = []

QUEUE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_重抽队列.json")

def _save_queue():
    try:
        data = {"queue": list(REDRAW_QUEUE), "jobs": {}}
        for jid, j in REDRAW_JOBS.items():
            data["jobs"][jid] = {k: v for k, v in j.items() if not k.startswith("_")}
        tmp = QUEUE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp, QUEUE_FILE)
    except Exception as e:
        print(f"[queue] 保存失败: {e}", flush=True)

def _restore_queue():
    try:
        with open(QUEUE_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return
    jobs = data.get("jobs") or {}
    order = data.get("queue") or []
    n_requeue = 0
    for jid in order:
        j = jobs.get(jid)
        if not isinstance(j, dict):
            continue
        st = j.get("status") or ""
        if st in ("running", "starting"):
            j["status"] = "queued"
            j.setdefault("log", []).append("🔄 相册重启过，这个任务重新排队")
            n_requeue += 1
        if j.get("status") == "queued":
            rels = j.get("rels")
            if isinstance(rels, list) and rels:
                j["_launch"] = (lambda jid=jid, rs=list(rels):
                                threading.Thread(target=do_redraw_multi,
                                                 args=(jid, rs), daemon=True).start())
            elif j.get("prompt") and not j.get("src"):
                try:
                    _w, _h = (j.get("size") or "1024x1536").split("x")
                    _od = j.get("outdir") or ""
                    if _od and not os.path.isabs(_od):
                        _od = os.path.join(ROOT, _od)
                    j["_launch"] = (lambda jid=jid, p=j.get("prompt") or "",
                                           c=int(j.get("total") or 1), od=_od,
                                           w=int(_w), h=int(_h), st=j.get("steps"),
                                           sm=j.get("seed_mode") or "random",
                                           tr=j.get("tier") or "", ac=j.get("action") or "":
                                    threading.Thread(target=do_gacha_job,
                                                     args=(jid, p, c, od, w, h, st, sm, tr, ac),
                                                     daemon=True).start())
                except Exception:
                    pass
            elif j.get("src"):
                try:
                    _w, _h = (j.get("size") or "1024x1536").split("x")
                    _od = j.get("outdir") or ""
                    if _od and not os.path.isabs(_od):
                        _od = os.path.join(ROOT, _od)
                    j["_launch"] = (lambda jid=jid, src=j["src"], p=j.get("prompt") or "",
                                           c=int(j.get("total") or 1), od=_od,
                                           w=int(_w), h=int(_h), st=j.get("steps"),
                                           sm=j.get("seed_mode") or "random":
                                    threading.Thread(target=do_redraw_job,
                                                     args=(jid, p, c, od, w, h, st, sm, None, src),
                                                     daemon=True).start())
                except Exception:
                    pass
        REDRAW_JOBS[jid] = j
        REDRAW_QUEUE.append(jid)
    if REDRAW_QUEUE:
        print(f"[queue] 恢复了 {len(REDRAW_QUEUE)} 个任务"
              f"（其中 {n_requeue} 个重新排队）", flush=True)
REDRAW_LOCK = threading.Lock()
_ROLL_PAUSED = {"v": False}
_ROLL_FROZEN = {"v": False}

def redraw_busy():
    return any(j.get("status") in ("running", "starting") for j in REDRAW_JOBS.values())

def _job_brief(jid, job):
    ch = ""
    src_rel = _norm(job.get("src") or "")
    try:
        for _p in scan_photos():
            if _p.get("rel") == src_rel or _norm(_p.get("rel", "")) == src_rel:
                _c = _p.get("char") or ""
                if _c and _c != "未知":
                    ch = _c
                break
    except Exception:
        pass
    if not ch:
        m = re.search(r"\b([a-z0-9_]+)_\(([a-z0-9_:]+)\)", job.get("prompt") or "", re.I)
        if m:
            ch = f"{m.group(1)}_({m.group(2)})"
    if not ch:
        src = os.path.basename(job.get("src") or "")
        m2 = re.match(r"\d{6}_(.+?)_(fashion|tease|exposed|sex|normal)_", src)
        if m2:
            ch = m2.group(1)
        else:
            m2b = re.match(r"\d{6}_(.+)", src)
            if m2b:
                ch = re.sub(r"\.(png|jpg|jpeg|webp)$", "", m2b.group(1))
    tier = job.get("tier") or ""
    if not tier:
        src = os.path.basename(job.get("src") or "")
        m3 = re.search(r"_(fashion|normal|tease|exposed|sex)_", src)
        if m3:
            tier = m3.group(1)
    if not tier:
        tier = "multi" if job.get("multi") else "?"
    tier_cn = {"fashion": "时尚", "tease": "擦边", "exposed": "暴露",
               "sex": "性爱", "normal": "日常", "multi": "批量(混档)"}.get(tier, tier)
    _files = job.get("files") or []
    out = ""
    if job.get("status") == "done" and _files:
        out = _files[-1] if isinstance(_files[-1], str) else str(_files[-1])
    return {
        "job": jid,
        "char": ch or "未知",
        "tier": tier,
        "tier_cn": tier_cn,
        "size": job.get("size") or "",
        "steps": job.get("steps"),
        "seed": job.get("seed"),
        "seed_mode": job.get("seed_mode") or "",
        "done_n": job.get("done") or 0,
        "prompt_len": len(job.get("prompt") or ""),
        "count": int(job.get("total") or 1),
        "multi": bool(job.get("multi")),
        "status": job.get("status") or "",
        "kind": job.get("kind") or ("multi" if job.get("multi") else "single"),
        "src": job.get("src") or "",
        "out": out,
        "files": [f for f in _files if isinstance(f, str)][-8:],
    }

def queue_snapshot():
    items = [jid for jid in REDRAW_QUEUE if jid in REDRAW_JOBS]
    briefs = [_job_brief(jid, REDRAW_JOBS[jid]) for jid in items]
    cnt = {"queued": 0, "running": 0, "done": 0, "failed": 0}
    for b in briefs:
        s = b.get("status") or ""
        if s in cnt:
            cnt[s] += 1
        elif s in ("starting", "cancelled"):
            cnt["running" if s == "starting" else "failed"] += 1
    running = next((b for b in briefs if b.get("status") in ("running", "starting")), None)
    return {
        "running": redraw_busy(),
        "queued": cnt["queued"],
        "done": cnt["done"],
        "failed": cnt["failed"],
        "total": len(briefs),
        "queue": briefs,
        "current": running,
    }

def enqueue_redraw(job_id, launcher):
    job = REDRAW_JOBS[job_id]
    job["_launch"] = launcher
    with REDRAW_LOCK:
        _busy = redraw_busy() or any(
            (REDRAW_JOBS.get(j) or {}).get("status") == "queued" for j in REDRAW_QUEUE)
        if not _busy:
            job["status"] = "running"
            pos = 0
        else:
            job["status"] = "queued"
            pos = 1 + sum(1 for j in REDRAW_QUEUE
                          if (REDRAW_JOBS.get(j) or {}).get("status") == "queued")
        if job_id not in REDRAW_QUEUE:
            REDRAW_QUEUE.append(job_id)
    _save_queue()
    if pos == 0:
        job["log"].append("▶️ 立刻开跑")
        launcher()
        return 0
    job["log"].append(f"⏳ 已排队，前面还有 {pos - 1} 个任务")
    return pos

def pump_redraw_queue():
    with REDRAW_LOCK:
        if redraw_busy():
            return
        nxt = None
        for jid in REDRAW_QUEUE:
            _j = REDRAW_JOBS.get(jid)
            if _j and _j.get("status") == "queued":
                nxt = _j
                break
        if nxt is None:
            if _ROLL_PAUSED["v"]:
                _ROLL_PAUSED["v"] = False
                _ROLL_FROZEN["v"] = False
                _unfreeze_roll()
                time.sleep(0.5)
                if _roll_pid() is None:
                    print("[重抽] ⚠️ 解冻后没有进程（可能被外部杀掉）→ 试 bootstrap", flush=True)
                    try:
                        _ok, _running = roll_ctl("start")
                        for _i in range(12):
                            if _roll_pid() is not None:
                                break
                            time.sleep(0.5)
                        if _roll_pid() is None:
                            print(f"[重抽] ❌ 抽卡机仍没能复工（ok={_ok} {_running}）—— 需要手动",
                                  flush=True)
                    except Exception as e:
                        print(f"[重抽] ⚠️ 复工异常: {type(e).__name__}: {e}", flush=True)
            return
        nxt["status"] = "running"
        nxt["log"].append("▶️ 轮到了，开始重抽")
        launcher = nxt.get("_launch")
    _save_queue()
    if launcher:
        launcher()
REDRAW_CLI = os.environ.get("DRAWTHINGS_CLI") or PATHS.DT_CLI
REDRAW_MODELS_DIR = os.environ.get(
    "DRAWTHINGS_MODELS_DIR",
    PATHS.DT_MODELS_DIR)
import pools.roll_params as _RP_MODEL
REDRAW_MODEL = _RP_MODEL.MODEL_FILE
REDRAW_STEPS = 6
_LORA_EXTRA = {}

def _min_png_bytes():
    return 20_000 if PATHS.engine() == "comfyui" else 200_000

def _gen_to(prompt, cfg, seed, out, w, h, steps):
    """按当前引擎（ComfyUI / Draw Things）出一张图到 out，返回 (ok, err)。"""
    from pools import roll_io as _EIO
    if _EIO.engine() == "comfyui":
        _outdir, _fname = os.path.split(out)
        ok, _sec, _path, err, _tm = _EIO.generate(
            os.path.splitext(_fname)[0], prompt, cfg, seed, _outdir,
            size=(w, h), steps=steps)
        return ok, (err or "")
    cmd = [REDRAW_CLI, "generate", "--models-dir", REDRAW_MODELS_DIR,
           "--model", REDRAW_MODEL, "--config-json", json.dumps(cfg),
           "--prompt", prompt, "--negative-prompt", "", "--steps", str(steps),
           "--cfg", "1.0", "--width", str(w), "--height", str(h),
           "--seed", str(seed), "--output", out]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=900, text=True,
                           encoding="utf-8", errors="replace")
    except Exception as e:
        return False, "%s: %s" % (type(e).__name__, e)
    ok = os.path.exists(out) and os.path.getsize(out) > _min_png_bytes()
    return ok, "" if ok else ((r.stderr or "") + (r.stdout or "")).strip()[:400]

def _short_tag(tag):
    try:
        from pools import characters as _CHR
        return _CHR.short_name(tag)
    except Exception:
        return re.split(r"[ _]\(", (tag or ""))[0].strip()

def _char_from_prompt(prompt):
    try:
        from pools import characters as _CH
        names = [d.get("tag") or "" for d in _CH.CHARACTERS_SPLIT]
    except Exception:
        names = []
    try:
        toks = set(_toks(prompt))
    except Exception:
        return ""
    hit = [n for n in names if n and n in toks]
    return max(hit, key=len) if hit else ""

def _redraw_cfg(char_full, prompt=""):
    cfg = {"sampler": 1}
    try:
        import pools.roll_params as _RP
        _auto = getattr(_RP, "RESOLUTION_DEPENDENT_SHIFT", False)
    except Exception:
        _auto = False
    if _auto:
        cfg["resolutionDependentShift"] = True
    else:
        cfg["shift"] = 3.5
    f = ""
    try:
        from pools import characters as _CH
        f = _CH.lora_of(char_full) or ""
    except Exception:
        f = ""
    if not f:
        for _ch, _l in _LORA_EXTRA.items():
            if _ch in (prompt or "") or _ch == (char_full or ""):
                f = _l
                break
    if f:
        cfg["loras"] = [{"mode": "all", "file": f, "weight": 0.7}]
    return cfg
NORM_CHAR = {}

try:
    from pools import characters as _CHR0
    for _d0 in _CHR0.CHARACTERS_SPLIT:
        try:
            _t0 = _d0["tag"]
            NORM_CHAR[_CHR0.short_name(_t0)] = _t0
            if " (" in _t0:
                _b0, _r0 = _t0.split(" (", 1)
                NORM_CHAR[_b0 + "_(" + _r0[:-1].replace(" ", "_") + ")"] = _t0
        except Exception:
            continue
except Exception:
    pass

TAGS_CACHE = {}
FAV_CACHE = set()
CHAR_CACHE = {}
TIER_CACHE = {}

ROLL_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "roll_config.json")
OFF_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_禁用.json")

POOL_FILES = [
    ("characters",  "角色池",  "🧑"),
    ("eros",        "福利池",  "✨"),
    ("actions",     "动作池",  "🎬"),
    ("poses",       "姿态池",  "🧍"),
    ("scenes",      "场景池",  "🏞"),
    ("cameras",     "机位池",  "📷"),
    ("styles",      "画风池",  "🎨"),
    ("preferences", "偏好池",  "💗"),
    ("fashion",     "时尚池",  "👗"),
    ("composition", "构图镜头", "🎬"),
    ("equip_machine", "装备机", "🧰"),
    ("sex_router",   "性爱路由", "🔀"),
]
_POOLS_CACHE = {"stamp": None, "data": None}

POOL_NAMES = {
    "CHARACTERS": "角色表", "CHARACTER_WEIGHTS": "角色权重", "STYLE_LOCK": "画风锁定",
    "PUBIC": "耻毛", "LORA_MAP": "LoRA 绑定",
    "EROS_FASHION": "时尚档", "EROS_TEASE_UNITS": "擦边单元", "EROS_EXPOSED_UNITS": "暴露单元",
    "ACTIONS": "动作表",
    "BODY_POSES": "基础姿势", "BODY_RULES": "姿态规则", "HAND_SINGLE": "单手", "HAND_BOTH": "双手",
    "SCENES": "场景表", "SCENE_INTERACT": "场景互动", "LIGHTS": "光线",
    "CAMERAS": "机位表",
    "SHOT_GAZE": "视线", "GAZE_WORDS": "注视词",
    "STYLES": "画风表", "HEAD": "头部",
    "HEAD_FASHION": "时尚头部", "_ECCHI_STYLE_WORDS": "擦边风格词",
    "ARMPIT_FITS": "腋下·服装",
    "BACKSHOT_BODY": "背影·身体", "BACKSHOT_CAMS": "背影·机位", "BACKSHOT_LEGS": "背影·腿",
    "FOOT_CHARS": "足·角色", "FOOT_CHAR_KW": "足·关键词",
    "FOOT_SHOE_KW": "足·鞋", "MATURE_KW": "成熟体型词",
    "EROS_WEIGHTS": "福利权重", "TIER_WEIGHTS": "尺度权重",
    "FRAMING": "性爱取景",
    "FASHION_ACTIONS": "时尚动作",
    "FASHION_ENV_EXTRA": "环境叙事",
    "FASHION_CAMS": "时尚机位", "FASHION_BODY": "时尚身体细节",
    "FASHION_ACCESSORY_SLOTS": "从头到脚配饰",
    "FASHION_PLACES": "场所", "FASHION_TIME_LIGHT": "时间·光线",
    "FASHION_ATMOSPHERE": "氛围",
    "ANGLES": "角度", "SCALES": "比例", "POSITIONS": "位置",
    "LENSES": "镜头", "FOREGROUND": "前景", "SEX_POSITIONS": "体位表", "SEX_MOOD_SHY": "害羞表情", "SEX_MOOD_SEDUCE": "魅惑表情",
    "SEX_LOWER_STATE": "下身状态", "PENETRATION_BY_POS": "结合处", "EJAC_INSERT": "射精·插入类",
    "EJAC_ORAL": "射精·口乳类",
}
_POOL_SKIP_RE = __import__("re").compile(
    r"(^_|_BAN$|_LABEL$|_WEIGHTS$|_W$|_RATIO$|_CHANCE$|_MAP$|_ORDER$|_SPEC$|_GROUP$|_LIBS$|_CATS$|_VIEWS$"
    r"|_STATES$|_PHRASES$|_KW$|_POS$|^PIV_|^QUOTA$|^PART_TO_|^MOUTH_|^INSERT_|^ORGAN_"
    r"|^REACTIONS_|^SLOT_|^ACTIVE_|^SEX_VIEW|^UPPER_BODY$|^EXCLUSIVE_"
    r"|_LEGACY$|^BASE_)")

_POOL_INTERNAL = {"_ECCHI_STYLE_WORDS",
                  "SEX_NEGATIVE",
                  "EJAC_CHANCE",
                  "SMALL_BUST_KW", "SIMPLE_OUTFIT_POS", "COMPLEX_OUTFIT_KW",
                  "ATTITUDE",
                  "NO_MIRROR_POS", "MIRROR_SCENE_KW", "SEX_BAD_LOWER", "MATURE_KW",
                  "FOOT_CHAR_KW", "FOOT_SHOE_KW", "SEX_MOOD_MAP",
                  "FASHION_DOCTOR", "FASHION_STYLE_LEVELS", "FASHION_BANNED_CAMS",
                  "FASHION_HAND_HOLDING", "FASHION_POCKET_OK",
                  "ANGLE_WEIGHTS", "SCALE_WEIGHTS", "POSITION_WEIGHTS", "LENS_WEIGHTS",
                  "FG_CHANCE_GUOFENG", "FG_CHANCE_OTHER",
                  "ANGLE_SCALE_MUTEX", "POSITION_SCALE_MUTEX", "ANGLE_POSITION_MUTEX",
                  }

POOL_MERGE = {
    "CHARACTER_WEIGHTS": ("CHARACTERS", "权重"),
    "PUBIC":             ("CHARACTERS", "耻毛"),
    "STYLE_LOCK":        ("CHARACTERS", "画风锁定"),
    "LORA_MAP":          ("CHARACTERS", "LoRA"),
    "BODY_RULES":        ("BODY_POSES", "规则"),
}
POOL_PKG = {"characters", "eros", "actions", "poses", "scenes", "cameras",
            "styles", "preferences", "fashion", "composition",
            "equip_machine", "sex_router"}

def _flatten_pool(val, cn, depth=0, cap=3000, show_keys=True):
    out = []
    if depth > 4 or len(out) > cap:
        return out
    if isinstance(val, str):
        for t in [x.strip() for x in val.split(",") if x.strip()]:
            out.append({"en": t, "cn": cn.get(t, "")})
    elif isinstance(val, (list, tuple)):
        for x in val:
            if isinstance(x, (list, tuple)) and len(x) > 1 and isinstance(x[0], str):
                out.append({"en": x[0], "cn": cn.get(x[0], "")})
            else:
                out += _flatten_pool(x, cn, depth + 1, cap, False)
    elif isinstance(val, dict):
        for k, v in val.items():
            ks = str(k)
            if show_keys:
                out.append({"en": ks, "cn": cn.get(ks, ""), "key": True})
                if isinstance(v, (int, float)):
                    out[-1]["weight"] = v
                    continue
                if isinstance(v, (list, tuple)) and v and all(isinstance(y, (int, float)) for y in v):
                    if len(v) == 1:
                        out[-1]["weight"] = v[0]
                        continue
            out += _flatten_pool(v, cn, depth + 1, cap, False)
    return out

def _char_items(v, cn):
    out = []
    for c in v:
        if not c:
            continue
        tag = str(c[0])
        nm = cn.get(tag) or cn.get(_short_tag(tag)) or ""
        out.append({"en": tag, "cn": nm})
    return out

def build_pools():
    import importlib
    cn = load_json(os.path.join(WORK, "taglib_cn.json"), {})
    off = load_json(os.path.join(WORK, "_禁用.json"), {})
    all_off = {x for v in off.values() for x in v}

    def _hit(en, offs):
        for seg in [en] + [t.strip() for t in en.split(",") if t.strip()]:
            if seg in offs:
                return True
        return False

    groups = []
    for mod_name, label, icon in POOL_FILES:
        try:
            mod = importlib.import_module(
                "pools." + mod_name if mod_name in POOL_PKG else mod_name)
        except Exception as e:
            print(f"[pools] 跳过 {mod_name}: {e}", flush=True)
            continue

        raw_map = {}
        for name in sorted(dir(mod)):
            if (not name.isupper() or name in _POOL_INTERNAL
                    or _POOL_SKIP_RE.search(name)):
                continue
            raw_map[name] = getattr(mod, name)

        attached = defaultdict(list)
        for src, (dst, tag) in POOL_MERGE.items():
            if src not in raw_map:
                continue
            attached[dst].append((tag, raw_map.pop(src)))

        pools = []
        for name, raw in raw_map.items():
            gkey = f"{mod_name}.{name}"
            offs = set(off.get(gkey) or []) | all_off
            try:
                if mod_name == "characters" and name == "CHARACTERS":
                    flat = _char_items(raw, cn)
                elif mod_name == "fashion" and isinstance(raw, dict):
                    flat = _flatten_pool([x for v in raw.values()
                                          if isinstance(v, (list, tuple, set, str))
                                          for x in (v.split(",") if isinstance(v, str) else v)], cn)
                else:
                    flat = _flatten_pool(raw, cn)
            except Exception as _e:
                print(f"[pools] 跳过 {gkey}（结构不是词表）: {type(_e).__name__}: {_e}", flush=True)
                continue

            extra_of = defaultdict(list)
            for tag, src in attached.get(name, []):
                if isinstance(src, dict):
                    for k, v in src.items():
                        ks, vs = str(k), v
                        if isinstance(vs, (list, tuple)):
                            vs = ", ".join(str(x) for x in vs)
                        vs = str(vs)
                        zh = [cn.get(t.strip()) for t in vs.split(",") if t.strip()]
                        if zh and all(zh):
                            vs = "·".join(x for x in zh if x)
                        extra_of[ks].append((tag, vs))

            seen, items = set(), []
            for it in flat:
                if not it["en"] or it["en"] in seen:
                    continue
                seen.add(it["en"])
                it["off"] = _hit(it["en"], offs)
                ex = list(extra_of.get(it["en"], []))
                short = _short_tag(it["en"])
                if short != it["en"]:
                    ex += extra_of.get(short, [])
                if ex:
                    it["extra"] = [f"{t}: {v}" for t, v in ex]
                items.append(it)
            if items:
                pools.append({"key": name, "name": POOL_NAMES.get(name, name),
                              "gkey": gkey, "items": items})
        if pools:
            groups.append({"key": mod_name, "label": label, "icon": icon, "pools": pools})
    return {"groups": groups}

def _pools_stamp():
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pools")
    try:
        return max(os.path.getmtime(os.path.join(d, f)) for f in os.listdir(d) if f.endswith(".py"))
    except Exception:
        return 0

def get_pools_cached():
    stamp = _pools_stamp()
    if _POOLS_CACHE["data"] is None or _POOLS_CACHE["stamp"] != stamp:
        _POOLS_CACHE["data"] = build_pools()
        _POOLS_CACHE["stamp"] = stamp
    return _POOLS_CACHE["data"]

ROLL_LABEL = PATHS.AUTO_ROLL_LABEL
ROLL_PLIST = PATHS.AUTO_ROLL_PLIST

IS_WIN = PATHS.IS_WIN
IS_MAC = PATHS.IS_MAC
PID_FILE = PATHS.PID_FILE
STOP_FILE = PATHS.STOP_FILE
PAUSE_FILE = PATHS.PAUSE_FILE

_SPAWNED = {"pid": None}

def _pid_alive(pid):
    "跨平台判断进程还在不在。Windows 上绝不能用 os.kill(pid, 0)（那会真杀进程）。"
    try:
        pid = int(pid or 0)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    if IS_WIN:
        try:
            import ctypes
            k32 = ctypes.windll.kernel32
            h = k32.OpenProcess(0x1000, False, pid)   # PROCESS_QUERY_LIMITED_INFORMATION
            if not h:
                return False
            code = ctypes.c_ulong()
            ok = k32.GetExitCodeProcess(h, ctypes.byref(code))
            k32.CloseHandle(h)
            return bool(ok) and code.value == 259      # STILL_ACTIVE
        except Exception:
            return False
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False

def _read_pid_file():
    try:
        with open(PID_FILE, encoding="utf-8") as f:
            return int((f.read() or "").strip() or 0)
    except Exception:
        return 0

def _clear_pid_files():
    for p in (PID_FILE, STOP_FILE, PAUSE_FILE):
        try:
            os.remove(p)
        except OSError:
            pass

def _request_stop():
    try:
        with open(STOP_FILE, "w", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S"))
        return True
    except Exception as e:
        print("[停止] 写停止标记失败:", e, flush=True)
        return False

def _kill_roll():
    "硬停：Windows/macOS 都能用的最后手段。"
    pid = _roll_pid()
    if pid is None:
        _clear_pid_files()
        return False
    try:
        if IS_WIN:
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                           capture_output=True, timeout=15)
        else:
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.5)
            if _pid_alive(pid):
                os.kill(pid, signal.SIGKILL)
    except Exception as e:
        print("[停止] 强停失败:", e, flush=True)
    for _ in range(20):
        if not _pid_alive(pid):
            break
        time.sleep(0.25)
    _clear_pid_files()
    return True

def _comfy_busy():
    "ComfyUI 里还有任务在跑吗（Windows 上用它判断「正在画」）。"
    try:
        from pools import backend_comfy as _CB
        q = _CB._get_json(_CB.COMFY_URL + "/queue", timeout=3)
        return bool(q.get("queue_running"))
    except Exception:
        return False

def roll_is_running():
    return _roll_pid() is not None

def roll_ctl(action):
    try:
        if action == "stop":
            return _roll_stop_graceful()
        if action == "restart":
            _roll_log_note("**手动重启**（相册面板点了「重启」）✓")
            _roll_stop_graceful(wait=False)
            time.sleep(1.0)
        if action in ("start", "restart"):
            if IS_MAC and ROLL_PLIST and os.path.exists(ROLL_PLIST):
                subprocess.run(["launchctl", "bootstrap", "gui/%d" % os.getuid(), ROLL_PLIST],
                               capture_output=True, timeout=15)
            else:
                _spawn_roll()
            for _ in range(20):
                if _roll_pid() is not None:
                    break
                time.sleep(0.25)
            _roll_log_note("**手动启动**（相册面板点了「%s」）✓" % action)
        return True, roll_is_running()
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

_STOPPING = {"v": False}

def _spawn_roll():
    root = os.path.dirname(os.path.abspath(__file__))
    env = dict(os.environ)
    env.setdefault("PYTHONPATH", root)
    try:
        os.remove(STOP_FILE)
    except OSError:
        pass
    logf = os.path.join(root, "_产线.out.log")
    cmd = [sys.executable, "-u", "-m", "pools.roll_machine"]
    kw = {"cwd": root, "env": env}
    if IS_WIN:
        kw["creationflags"] = (subprocess.CREATE_NEW_PROCESS_GROUP
                               | getattr(subprocess, "DETACHED_PROCESS", 0))
    else:
        kw["start_new_session"] = True
    try:
        with open(logf, "ab") as lf:
            p = subprocess.Popen(cmd, stdout=lf, stderr=lf, **kw)
    except Exception:
        p = subprocess.Popen(cmd, **kw)
    _SPAWNED["pid"] = p.pid
    return p.pid

def _roll_pid():
    if IS_MAC:
        try:
            out = subprocess.run(["launchctl", "list"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                                 timeout=8).stdout
            for ln in out.splitlines():
                parts = ln.split()
                if len(parts) >= 3 and parts[-1] == ROLL_LABEL:
                    p = parts[0]
                    if p.isdigit():
                        return int(p)
        except Exception:
            pass
    pid = _read_pid_file()
    if pid and _pid_alive(pid):
        return pid
    if _SPAWNED["pid"] and _pid_alive(_SPAWNED["pid"]):
        return _SPAWNED["pid"]
    return None

def _freeze_roll():
    pid = _roll_pid()
    if pid is None:
        return False
    if IS_WIN:
        try:
            with open(PAUSE_FILE, "w", encoding="utf-8") as f:
                f.write(time.strftime("%Y-%m-%d %H:%M:%S"))
            _ROLL_FROZEN["v"] = True
            return True
        except Exception as e:
            print("[让路] 暂停标记写不进去:", e, flush=True)
            return False
    try:
        os.kill(pid, signal.SIGSTOP)
        _ROLL_FROZEN["v"] = True
        return True
    except Exception as e:
        print("[让路] 冻结失败:", e, flush=True)
        return False

def _unfreeze_roll():
    pid = _roll_pid()
    if pid is None:
        return False
    if IS_WIN:
        try:
            os.remove(PAUSE_FILE)
        except OSError:
            pass
        _ROLL_FROZEN["v"] = False
        return True
    try:
        os.kill(pid, signal.SIGCONT)
        _ROLL_FROZEN["v"] = False
        return True
    except Exception as e:
        print("[让路] 解冻失败:", e, flush=True)
        return False

def _drawing():
    if PATHS.engine() == "comfyui":
        return _comfy_busy()
    try:
        r = subprocess.run(["pgrep", "-f", "[d]raw-things-cli generate"],
                           capture_output=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False

def _ppid_of(pid):
    try:
        out = subprocess.run(["ps", "-o", "ppid=", "-p", str(pid)],
                             capture_output=True, text=True, timeout=5).stdout.strip()
        return int(out) if out.isdigit() else None
    except Exception:
        return None

def _descends_from(pid, anc, hops=8):
    seen = set()
    for _ in range(hops):
        if pid in (None, 0, 1) or pid in seen:
            return False
        if pid == anc:
            return True
        seen.add(pid)
        pid = _ppid_of(pid)
    return False

def _roll_drawing():
    if not IS_MAC:
        return _comfy_busy()
    pid = _roll_pid()
    if pid is None:
        return False
    try:
        r = subprocess.run(["pgrep", "-f", "[d]raw-things-cli generate"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5)
        draws = [int(x) for x in r.stdout.split() if x.strip().isdigit()]
    except Exception:
        return False
    return any(_descends_from(d, pid) for d in draws)

def _wait_stop_done(timeout=240):
    t0 = time.time()
    while _STOPPING["v"] and time.time() - t0 < timeout:
        time.sleep(0.5)
    return not _STOPPING["v"]

def _roll_log_note(text):
    try:
        p = os.path.join(WORK, "launchd.out.log")
        with open(p, "a", encoding="utf-8") as f:
            f.write("[面板] %s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), text))
    except Exception:
        pass

def _bootout():
    if IS_MAC:
        subprocess.run(["launchctl", "bootout", "gui/%d/%s" % (os.getuid(), ROLL_LABEL)],
                       capture_output=True, timeout=15)
        return
    _kill_roll()

def _roll_stop_graceful(wait=True):
    pid = _roll_pid()
    if pid is None:
        _clear_pid_files()
        return True, {"stopping": False, "running": False, "detail": "本来就没在跑"}
    _roll_log_note("**手动停**（相册面板点了「停止」）—— 不是出错 ✓"
                   + ("" if wait else "（重启流程里先停）"))
    if IS_MAC and wait and _drawing():
        # macOS：冻住 → 等当前这张画完 → 卸载 job（这张图不会作废）
        try:
            os.kill(pid, signal.SIGSTOP)
        except Exception as e:
            _bootout()
            return True, {"stopping": False, "running": roll_is_running(),
                          "detail": f"冻不住（{type(e).__name__}），已直接停"}
        _STOPPING["v"] = True
        threading.Thread(target=_wait_then_stop, args=(pid,), daemon=True).start()
        return True, {"stopping": True, "running": True, "detail": "等这张画完就停"}
    if not wait:
        _bootout()
        time.sleep(1.0)
        return True, {"stopping": False, "running": roll_is_running(),
                      "detail": "没有在画的图，已停"}
    # 其它情况：下停止标记让它自己收工，最多等 25 秒，再不走就强停
    _request_stop()
    t0 = time.time()
    while time.time() - t0 < 25 and _pid_alive(pid):
        time.sleep(0.3)
    if _pid_alive(pid):
        _kill_roll()
        return True, {"stopping": False, "running": roll_is_running(),
                      "detail": "等 25 秒没退出，已强制结束"}
    _clear_pid_files()
    return True, {"stopping": False, "running": False, "detail": "已停"}

def _wait_then_stop(pid, timeout=1800):
    t0 = time.time()
    try:
        while time.time() - t0 < timeout and _drawing():
            time.sleep(2)
    finally:
        try:
            os.kill(pid, signal.SIGCONT)
        except Exception:
            pass
        _bootout()
        _STOPPING["v"] = False
        print("[抽卡机] 优雅停完成（当前那张已画完）", flush=True)

ROLL_PRIO = {"high": "高性能（出图快，但会抢 CPU）",
             "low": "让路（电脑用着跟手，出图慢 16s/张）"}

ALBUM_PLIST = PATHS.PHOTO_ALBUM_PLIST
ALBUM_LABEL = PATHS.PHOTO_ALBUM_LABEL
PRIO_PLISTS = tuple(p for p in (ROLL_PLIST, ALBUM_PLIST) if p)

def _prio_apply(plist, mode):
    if not plist or not IS_MAC:
        return
    if mode == "high":
        subprocess.run(["plutil", "-remove", "Nice", plist], capture_output=True, timeout=10)
        subprocess.run(["plutil", "-replace", "ProcessType", "-string", "Standard", plist],
                       capture_output=True, timeout=10)
    else:
        subprocess.run(["plutil", "-replace", "Nice", "-integer", "10", plist],
                       capture_output=True, timeout=10)
        subprocess.run(["plutil", "-replace", "ProcessType", "-string", "Background", plist],
                       capture_output=True, timeout=10)

def _prio_of(plist):
    if not plist or not IS_MAC:
        return "high", 0, ""
    try:
        out = subprocess.run(["plutil", "-p", plist], capture_output=True, text=True, encoding="utf-8", errors="replace",
                             timeout=10).stdout
        m_nice = re.search(r'"Nice"\s*=>\s*(\d+)', out)
        m_pt = re.search(r'"ProcessType"\s*=>\s*"([A-Za-z]+)"', out)
        nice = int(m_nice.group(1)) if m_nice else 0
        pt = m_pt.group(1) if m_pt else ""
        return ("low" if (nice > 0 or pt == "Background") else "high"), nice, pt
    except Exception:
        return "?", 0, ""

def roll_prio_get():
    if not IS_MAC:
        return {"mode": "high", "nice": 0, "proctype": "",
                "album_mode": "high", "album_nice": 0,
                "label": ROLL_PRIO["high"], "running": roll_is_running(),
                "unsupported": True,
                "detail": "Windows 下不调 launchd 优先级（不影响出图）"}
    try:
        out = subprocess.run(["plutil", "-p", ROLL_PLIST],
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10).stdout
        m_nice = re.search(r'"Nice"\s*=>\s*(\d+)', out)
        m_pt = re.search(r'"ProcessType"\s*=>\s*"([A-Za-z]+)"', out)
        pt = m_pt.group(1) if m_pt else ""
        nice = int(m_nice.group(1)) if m_nice else 0
        mode = "low" if (nice > 0 or pt == "Background") else "high"
        _am, _an, _ap = _prio_of(ALBUM_PLIST)
        return {"mode": mode, "nice": nice, "proctype": pt,
                "album_mode": _am, "album_nice": _an,
                "label": ROLL_PRIO[mode], "running": roll_is_running()}
    except Exception as e:
        return {"mode": "?", "error": f"{type(e).__name__}: {e}"}

def roll_prio_set(mode):
    if mode not in ("high", "low"):
        return False, "mode 只能是 high / low"
    if not IS_MAC:
        return True, dict(roll_prio_get(), ok=True,
                          detail="Windows 下不用改优先级（面板这个开关只在 macOS 生效）")
    uid = os.getuid()
    was_running = roll_is_running()
    try:
        for _pl in PRIO_PLISTS:
            _prio_apply(_pl, mode)
        if was_running:
            subprocess.run(["launchctl", "bootout", f"gui/{uid}/{ROLL_LABEL}"],
                           capture_output=True, timeout=15)
            time.sleep(1.5)
            subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", ROLL_PLIST],
                           capture_output=True, timeout=15)
            time.sleep(1)
        subprocess.Popen(["sh", "-c",
                          f"sleep 2; launchctl bootout gui/{uid}/{ALBUM_LABEL}; "
                          f"sleep 1; launchctl bootstrap gui/{uid} {ALBUM_PLIST}"],
                         start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, roll_prio_get()
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

TUNNEL_PASSWORD = os.environ.get("ALBUM_TUNNEL_PASSWORD", "")


PUBLIC_BASE = os.environ.get("ALBUM_PUBLIC_BASE", "").rstrip("/")

_LOOPBACK = ("127.0.0.1", "::1", "localhost", "::ffff:127.0.0.1")

def _is_external(client_addr, headers):
    if headers.get("CF-Connecting-IP"):
        return True
    ip = (client_addr or ("", 0))[0]
    return ip not in _LOOPBACK

def _auth_ok(headers):
    if not TUNNEL_PASSWORD:
        return False
    import base64, hmac
    h = headers.get("Authorization") or ""
    if not h.startswith("Basic "):
        return False
    try:
        raw = base64.b64decode(h[6:]).decode("utf-8", "ignore")
        _u, _, pwd = raw.partition(":")
        return hmac.compare_digest(pwd, TUNNEL_PASSWORD)
    except Exception:
        return False

# 访客（经隧道进来的）只看这个子目录；留空 = 整个图库可见。
# 你的图散在多个目录、又想只放其中一块时，设 ALBUM_VISITOR_ROOT=<那个目录名>。
_VISITOR_ROOT_REL = os.environ.get("ALBUM_VISITOR_ROOT", "").strip("/")

def _visible_to_visitor(rel, external):
    if not external or not _VISITOR_ROOT_REL:
        return True
    return rel.replace(os.sep, "/").startswith(_VISITOR_ROOT_REL + "/")

SHARE_FILE = os.path.join(WORK, "_分享集合.json")

def load_shares():
    try:
        with open(SHARE_FILE, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}

def save_shares(d):
    try:
        tmp = SHARE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        os.replace(tmp, SHARE_FILE)
        return True
    except Exception as e:
        print("[share] 保存失败：%s" % e, flush=True)
        return False

def new_share_token():
    import secrets
    return secrets.token_urlsafe(9)

def share_of(token):
    tok = (token or "").strip()
    if not tok:
        return None
    s = load_shares().get(tok)
    return s if isinstance(s, dict) and s.get("rels") else None

def char_filter_data():
    from pools import characters as CH
    try:
        import works as _W
    except Exception:
        _W = None
    try:
        from pypinyin import lazy_pinyin
    except Exception:
        lazy_pinyin = None
    off = {}
    try:
        import pool_gate as _PG
        off = _PG.load() or {}
    except Exception:
        pass
    banned = set(off.get("characters.CHARACTERS") or [])
    cnmap = (LAYERLIB.get("cn") or {})

    def _key(name):
        if lazy_pinyin and name and any("\u4e00" <= ch <= "\u9fff" for ch in name):
            return "".join(lazy_pinyin(name)).lower()
        return (name or "").lower()

    groups = {}
    seen = set()
    for d in (CH.CHARACTERS or []):
        tag = d[0] if isinstance(d, (tuple, list)) else (d.get("tag") if isinstance(d, dict) else "")
        if not tag or tag in seen:
            continue
        seen.add(tag)
        cn = cnmap.get(tag) or tag
        wk = ""
        wcn = "其它作品"
        if _W is not None:
            try:
                wk = _W.work_of(tag) or ""
                wcn = _W.work_cn(wk) or wcn
            except Exception:
                wk = ""
        gk = wk or "__other__"
        g = groups.setdefault(gk, {"key": gk, "cn": wcn, "_cn_key": _key(wcn), "chars": []})
        g["chars"].append({"tag": tag, "cn": cn, "off": tag in banned, "_k": _key(cn)})

    out = []
    for gk in sorted(groups, key=lambda k: (groups[k]["_cn_key"], k)):
        g = groups[gk]
        for c in g["chars"]:
            c.pop("_k", None)
        g["chars"].sort(key=lambda c: _key(c["cn"] or c["tag"]))
        g.pop("_cn_key", None)
        out.append(g)
    total = sum(len(g["chars"]) for g in out)
    return {"works": out, "total": total,
            "off_count": sum(1 for g in out for c in g["chars"] if c["off"])}

def set_char_filter(disable=None, enable=None):
    import pool_gate as _PG
    off = _PG.load() or {}
    cur = set(off.get("characters.CHARACTERS") or [])
    cur |= {str(x) for x in (disable or []) if x}
    cur -= {str(x) for x in (enable or []) if x}
    if cur:
        off["characters.CHARACTERS"] = sorted(cur)
    else:
        off.pop("characters.CHARACTERS", None)
    _PG.save(off)
    try:
        _POOLS_CACHE["data"] = None
    except Exception:
        pass
    return len(cur)

def share_allows(token, rel):
    s = share_of(token)
    if not s:
        return False
    r = (rel or "").replace(os.sep, "/")
    return r in {str(x).replace(os.sep, "/") for x in (s.get("rels") or [])}

def _share_page_html(token, sh):
    title = (sh.get("title") or "分享给你").strip()
    rels = [str(x) for x in (sh.get("rels") or [])]
    import html as _html
    import urllib.parse as _up
    cells = "".join(
        '<a class="cell" href="/img?p=%s&k=%s" target="_blank" rel="noopener">'
        '<img loading="lazy" src="/img?p=%s&t=thumb&k=%s" alt=""></a>'
        % (_up.quote(r), _up.quote(token), _up.quote(r), _up.quote(token))
        for r in rels)
    return ("""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>%s</title>
<style>
:root{color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:#14101a;color:#f2eaf6;font:15px/1.5 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}
header{position:sticky;top:0;z-index:2;padding:14px 16px;background:rgba(20,16,26,.86);
 backdrop-filter:blur(12px);border-bottom:1px solid rgba(255,142,196,.18)}
h1{margin:0;font-size:16px;font-weight:600;color:#ffd7ea}
.sub{margin-top:3px;font-size:12px;color:#9d93a8}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(30vw,1fr));gap:6px;padding:8px}
@media(min-width:700px){.grid{grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;padding:14px}}
.cell{display:block;border-radius:10px;overflow:hidden;background:#221a2b;aspect-ratio:2/3}
.cell img{width:100%%;height:100%%;object-fit:cover;display:block}
footer{padding:16px;text-align:center;font-size:12px;color:#6f6879}
</style></head><body>
<header><h1>%s</h1><div class="sub">共 %d 张 · 点开看大图 · 长按可保存</div></header>
<div class="grid">%s</div>
<footer>只读分享页 · 不含相册其它内容</footer>
</body></html>""" % (_html.escape(title), _html.escape(title), len(rels), cells))

def parse_filename(fn):
    m = re.match(r"(\d{6})_((?:(?!_(?:fashion|normal|tease|exposed|sex|unknown)_).)+?)_(missionary|doggystyle|reverse[-_]cowgirl|cowgirl|spooning|standing_wall|mating_press|fellatio|paizuri|cunnilingus)(?:-(pov|closeup|girl))?_(semi|watercolor|gradient|yabuki)_(\d+)\.png$", fn)
    if m:
        return {"time": m.group(1), "char": m.group(2), "tier": "sex",
                "action": m.group(3), "framing": m.group(4),
                "style": m.group(5), "seed": m.group(6)}
    m = re.match(r"(\d{6})_((?:(?!_(?:fashion|normal|tease|exposed|sex|unknown)_).)+?)_(fashion|normal|tease|exposed|sex|unknown)_(semi|watercolor|gradient|yabuki)_(\d+)\.png$", fn)
    if m:
        return {"time": m.group(1), "char": m.group(2),
                "tier": m.group(3), "style": m.group(4), "seed": m.group(5)}
    m = re.match(r"(\d{6})_((?:(?!_(?:fashion|normal|tease|exposed|sex|unknown)_).)+?)_(fashion|normal|tease|exposed|sex|unknown)_([a-z_-]+)_(semi|watercolor|gradient|yabuki)_(\d+)\.png$", fn)
    if m:
        return {"time": m.group(1), "char": m.group(2), "tier": m.group(3),
                "action": m.group(4), "style": m.group(5), "seed": m.group(6)}
    m = re.match(r"b\d+_(\d+)_(\d{6})_((?:(?!_(?:fashion|normal|tease|exposed|sex|unknown)_).)+?)_(fashion|normal|tease|exposed|sex)_(yabuki|semi|watercolor|gradient)_(\d+)\.png$", fn)
    if m:
        return {"idx": m.group(1), "time": m.group(2), "char": m.group(3),
                "tier": m.group(4), "style": m.group(5), "seed": m.group(6)}
    m = re.match(r"b\d+_(\d+)_(\d{6})_((?:(?!_(?:fashion|normal|tease|exposed|sex|unknown)_).)+?)_(semi|watercolor|gradient|yabuki)_(\d+)\.png$", fn)
    if m:
        return {"idx": m.group(1), "time": m.group(2), "char": m.group(3),
                "tier": "unknown", "style": m.group(4), "seed": m.group(5)}
    m = re.match(r"b\d+_(\d+)_((?:(?!_(?:fashion|normal|tease|exposed|sex|unknown)_).)+?)_(semi|watercolor|gradient|yabuki)_(\d+)\.png$", fn)
    if m:
        return {"idx": m.group(1), "time": "000000", "char": m.group(2),
                "tier": "unknown", "style": m.group(3), "seed": m.group(4)}
    return None

def load_log():
    recs = {}
    if os.path.exists(LOG):
        for l in open(LOG, encoding="utf-8"):
            l = l.strip()
            if not l:
                continue
            try:
                r = json.loads(l)
            except Exception:
                continue
            if r.get("tag"):
                recs[r["tag"]] = r
    return recs

TAGLIB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tag_library.json")
try:
    TAGLIB = json.load(open(TAGLIB_FILE, encoding="utf-8"))
except Exception:
    TAGLIB = {"categories": [], "cn": {}}

USE_LAYER_TAGLIB = True
LAYERLIB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "taglib_layer.json")
try:
    LAYERLIB = json.load(open(LAYERLIB_FILE, encoding="utf-8"))
except Exception:
    LAYERLIB = {}

try:
    TAG_TIERS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            "tag_tiers.json"), encoding="utf-8"))
except Exception:
    TAG_TIERS = {"tags": {}, "colors": {}, "classes": {}}

APP_VERSION = "v1.0.0"   # 版本号唯一来源
APP_NAME = "壁纸相册"


def project_version():
    try:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CHANGELOG.md")
        _txt = open(p, encoding="utf-8").read()
        vs = (re.findall(r"\*\*v(\d+(?:\.\d+)*)", _txt)
              + re.findall(r"^#+\s*v(\d+(?:\.\d+)*)", _txt, re.M)
              + re.findall(r"^#+[^\n]*?[（(]\s*v(\d+(?:\.\d+)*)", _txt, re.M))
        if vs:
            def _k(v):
                _p = [int(x) for x in v.split(".")]
                if len(_p) >= 3 and _p[0] >= 1:
                    return (1, _p)
                return (0, _p[1:] if _p and _p[0] == 0 else _p)
            return "v" + max(vs, key=_k)
    except Exception:
        pass
    return APP_VERSION

def _compose_tables():
    try:
        import tag_compose as TC
        return {"COLOR": TC.COLOR, "ITEM": TC.ITEM, "PRE": TC.PRE, "POST": TC.POST}
    except Exception:
        return {}
CN_MAP = TAGLIB.get("cn", {})

SEX_POS_KEYS = ["missionary position", "doggystyle", "cowgirl position", "reverse cowgirl",
                "spooning", "standing sex", "mating press", "fellatio", "paizuri", "cunnilingus",
                "footjob"]

def _toks(prompt):
    return [t.strip() for t in (prompt or "").split(",") if t.strip()]

def prompt_similarity(a, b):
    sa, sb = set(_toks(a)), set(_toks(b))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)

def infer_meta(prompt, src_rec):
    low = (prompt or "").lower()
    tier = src_rec.get("tier", "unknown")
    action = src_rec.get("action", "redraw")
    pos = next((k for k in SEX_POS_KEYS if k in low), None)
    if pos or "explicit" in low or "sex, explicit" in low:
        tier = "sex"
        action = pos.replace(" ", "_") if pos else action
    elif "completely nude" in low or "pussy exposed" in low:
        tier = "exposed"
    elif "nipples showing through the fabric" in low or "see-through fabric" in low:
        tier = "tease"
    style = src_rec.get("style", "semi")
    if "watercolor" in low:
        style = "watercolor"
    elif "semi-painterly" in low:
        style = "semi"
    elif "smooth gradient shading" in low or "anime coloring" in low:
        style = "gradient"
    return tier, action, style

def auto_cn_tags(prompt, limit=6):
    low = (prompt or "").lower()
    out = []
    pos_cn = {"missionary": "传教士", "doggystyle": "后入", "reverse cowgirl": "反向女上",
              "cowgirl": "女上", "spooning": "侧入", "standing sex": "站立",
              "mating press": "压制位", "fellatio": "口交", "paizuri": "乳交",
              "cunnilingus": "舔阴"}
    for k, v in pos_cn.items():
        if k in low:
            out.append(v)
    if out:
        out.insert(0, "性爱")
    elif "creampie" in low:
        out.append("内射")
    elif "cum on her face" in low:
        out.append("颜射")
    elif "cum" in low or "ejaculation" in low:
        out.append("射精")
    elif "completely nude" in low or "pussy exposed" in low:
        out.append("全裸")
    elif "nipples showing through the fabric" in low or "see-through fabric" in low:
        out.append("擦边")
    toks = set(_toks(prompt))
    order = ["scene", "camera", "light", "mood", "outfit"]
    hit = {}
    for cat in TAGLIB.get("categories", []):
        if cat["key"] not in order:
            continue
        for it in cat["items"]:
            if it["cn"] and (it["en"] in toks or it["en"] in low):
                hit.setdefault(cat["key"], []).append(it["cn"])
    for k in order:
        for cn in hit.get(k, []):
            if cn not in out:
                out.append(cn)
            if len(out) >= limit:
                return out
    return out[:limit]

_SPLIT_DROP = {"scene", "light", "eq_scene", "fashion_place", "fashion_time",
               "fashion_atmo", "comp_fg"}
_SPLIT_LABEL = {"eq_head": "head", "eq_face": "expression", "eq_ears": "ears",
                "eq_neck": "neck", "eq_top": "top", "eq_chest": "chest",
                "eq_hand": "hands", "eq_bottom": "bottom", "eq_hip": "hips",
                "eq_leg": "legs", "eq_feet": "feet", "outfit": "outfit"}
_SPLIT_PRI = ["sexpos", "penetration", "sexframing", "ejac", "sexroute", "eq_scene",
              "eq_male", "eq_hip", "eq_chest", "eq_face", "eq_top", "eq_bottom",
              "eq_leg", "eq_feet", "eq_head", "eq_ears", "eq_neck", "eq_hand",
              "eros_exposed", "eros_tease", "eros_fashion"]
_SPLIT_CAT = {"data": None}

def _tiers_all():
    t = dict(TAG_TIERS.get("tags") or {})
    SUB_TIER = {"擦边": "tease", "暴露": "exposed", "时尚福利": "fashion"}
    BIG_TIER = {"性爱": "sex"}
    try:
        _cats = list(TAGLIB.get("categories") or [])
        _cats.sort(key=lambda c: 1 if ((c.get("label") or "") in BIG_TIER) else 0)
        for c in _cats:
            big = c.get("label") or ""
            for sub in (c.get("subs") or [c]):
                lab = sub.get("label") or ""
                tier = SUB_TIER.get(lab) or BIG_TIER.get(big) or "general"
                force = big in BIG_TIER
                for i in (sub.get("items") or []):
                    en = i.get("en")
                    if not en:
                        continue
                    if force:
                        t[en] = tier
                    elif en not in t:
                        t[en] = tier
    except Exception:
        pass
    return t

def _tag_flat_index():
    cat_of, order, labels = {}, [], {}
    for c in (TAGLIB.get("categories") or []):
        subs = c.get("subs")
        if not subs:
            k = c.get("key")
            if k:
                order.append(k)
                labels[k] = "%s·%s" % (c.get("label") or k, "") if False else (c.get("label") or k)
            for i in (c.get("items") or []):
                cat_of.setdefault(i.get("en"), k)
            continue
        for sub in subs:
            k = sub.get("key") or sub.get("label")
            if not k:
                continue
            order.append(k)
            labels[k] = (c.get("label") or "") + ("·" + (sub.get("label") or "") if sub.get("label") else "")
            for i in (sub.get("items") or []):
                cat_of.setdefault(i.get("en"), k)
    return cat_of, order, labels

def _tag_cats_flat():
    out = {}
    for c in (TAGLIB.get("categories") or []):
        subs = c.get("subs")
        if not subs:
            for i in (c.get("items") or []):
                out.setdefault(i.get("en"), []).append(c.get("key"))
            continue
        for sub in subs:
            keys = [sub.get("key") or sub.get("label")] + list(sub.get("from") or [])
            for i in (sub.get("items") or []):
                for k in keys:
                    if k:
                        out.setdefault(i.get("en"), []).append(k)
    return out

def _split_catmap():
    if _SPLIT_CAT["data"] is None:
        tl = load_json(os.path.join(WORK, "tag_library.json"), {})
        pairs = []
        for c in tl.get("categories", []):
            subs = c.get("subs")
            if not subs:
                pairs.append((c.get("key"), c.get("items") or []))
                continue
            for sub in subs:
                keys = [k for k in (sub.get("from") or []) if k] or [sub.get("key") or sub.get("label")]
                for k in keys:
                    pairs.append((k, sub.get("items") or []))
        pairs.sort(key=lambda kv: _SPLIT_PRI.index(kv[0]) if kv[0] in _SPLIT_PRI else 999)
        m = {}
        for _k, items in pairs:
            for i in items:
                _key = i.get("k") or _k
                m.setdefault(i["en"], _key)
                for t in i["en"].split(","):
                    t = t.strip()
                    if t:
                        m.setdefault(t, _key)
        _kb = sorted([k for k in m if (len(k) >= 7 or " " in k)],
                     key=len, reverse=True)
        _SPLIT_CAT["data"] = (m, _kb)
    return _SPLIT_CAT["data"]

def _cat_of(tok, catmap):
    m, keys = catmap
    if tok in m:
        return m[tok]
    tl = tok.lower()
    import re as _re
    for k in keys:
        if _re.search(r"\b" + _re.escape(k) + r"\b", tl):
            return m[k]
    return None

def split_prompt(prompt):
    m = _split_catmap()
    toks = [t.strip() for t in (prompt or "").split(",") if t.strip()]
    cats = [_cat_of(t, m) for t in toks]
    ci = next((i for i, c in enumerate(cats) if c == "char"), -1)
    out, seen, dropped, added = [], set(), 0, 0
    for i, t in enumerate(toks):
        c = cats[i]
        if c in _SPLIT_DROP:
            dropped += 1
            continue
        if i > ci and c in _SPLIT_LABEL and c not in seen:
            out.append(_SPLIT_LABEL[c] + ":")
            seen.add(c)
            added += 1
        out.append(t)
    return ", ".join(out), dropped, added

OUTFITS_FILE = os.path.join(WORK, "搭配库.json")
MYTAGS_FILE = os.path.join(WORK, "自定义标签.json")
OUTFIT_THUMB = os.path.join(WORK, "_搭配缩略图")

_CLOTH_CATS = {"eq_top", "eq_bottom", "eq_leg", "eq_feet", "eq_head", "eq_ears",
               "eq_neck", "eq_hand", "outfit", "fit_top", "fit_bottom", "fit_set", "fit_acc", "fit_leg", "fit_shoe", "eq_hip", "eq_chest"}

_NON_CLOTH = {"data": None}

def _non_cloth():
    if _NON_CLOTH["data"] is None:
        import pools.equip_machine as _E
        bad = set(_E.LEG_POSES) | set(_E.HEAD_POSE_SAFE) | set(_E.HEAD_POSE)
        for v in _E.GAZE_BY_TIER.values():
            bad |= set(v)
        for v in _E.EXPRESSIONS_BY_TIER.values():
            bad |= set(v)
        for v in list(_E.SEX_FACE_BY_ATT.values()) + list(_E.SEX_FACE_WATCH.values()):
            bad |= set(v)
        bad |= set(_E.HAND_ACTIONS) | set(_E.HAND_BOTH)
        _NON_CLOTH["data"] = bad
    return _NON_CLOTH["data"]

def _outfit_parts(rec):
    eq = (rec or {}).get("equip") or {}
    m = _split_catmap()
    parts = {}
    for k in ("upper", "lower", "leg_l", "leg_r", "feet", "head", "ears", "neck",
              "hand_l", "hand_r", "rear", "eyes", "chest"):
        v = eq.get(k)
        if not v:
            continue
        _bad = _non_cloth()
        keep = [t.strip() for t in v.split(",")
                if t.strip() and t.strip() not in _bad
                and _cat_of(t.strip(), m) in _CLOTH_CATS]
        if keep:
            parts[k] = ", ".join(dict.fromkeys(keep))
    seg = ", ".join(parts.values())
    return parts, seg

def _strip_clothing(prompt):
    m = _split_catmap()
    keep = []
    for t in [x.strip() for x in (prompt or "").split(",") if x.strip()]:
        c = _cat_of(t, m)
        if c in _CLOTH_CATS:
            continue
        keep.append(t)
    return keep

def load_outfits():
    return load_json(OUTFITS_FILE, {"outfits": []})

def save_outfits(d):
    json.dump(d, open(OUTFITS_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def do_redraw_job(job_id, prompt, count, outdir, w, h, steps=None, seed_mode="random",
                  base_seed=None, src_rel="", tier=None, action=None):
    job = REDRAW_JOBS[job_id]
    steps = int(steps or REDRAW_STEPS)
    pause_roll_for_gpu(job)
    try:
        os.makedirs(outdir, exist_ok=True)
        cfg = _redraw_cfg(_char_from_prompt(prompt), prompt)
        _src_tag = os.path.basename(src_rel or job.get("src", "")).rsplit(".", 1)[0]
        _src_rec = load_log().get(_src_tag) or {}
        _tier, _action, _style = infer_meta(prompt, _src_rec)
        if tier:
            _tier = tier
        if action:
            _action = action
        _char_full = _char_from_prompt(prompt) or _src_rec.get("character") or ""
        if not _char_full:
            _m = re.search(r"([a-z0-9_]+_\([a-z_:]+\))", prompt)
            _char_full = _m.group(1) if _m else "unknown"
        _char_short = _short_tag(_char_full)
        _src_norm = _norm(src_rel or job.get("src", ""))
        _src_tags = TAGS_CACHE.get(_src_norm, [])
        _sim = prompt_similarity(prompt, _src_rec.get("prompt", ""))
        _tags = auto_cn_tags(prompt) if _sim < 0.60 else list(_src_tags)
        job["log"].append(f"标签策略: 相似度 {_sim:.2f} → " +
                          ("按新提示词重打 " + "/".join(_tags) if _sim < 0.60
                           else "继承原图 " + ("/".join(_tags) or "(无)")))
        for k in range(count):
            if seed_mode == "inherit" and base_seed:
                seed = base_seed
            else:
                _src_seed = base_seed if base_seed is not None else _src_rec.get("seed")
                try:
                    _src_seed = int(_src_seed) if _src_seed not in (None, "") else None
                except Exception:
                    _src_seed = None
                while True:
                    seed = random.randint(1, 2000000000)
                    if seed not in BAN_SEEDS and seed != _src_seed:
                        break
            fname = f"{time.strftime('%H%M%S')}_{_char_short}_{_tier}_{_action}_{_style}_{seed}.png"
            out = os.path.join(outdir, fname)
            ok, _err = _gen_to(prompt, cfg, seed, out, w, h, steps)
            if ok:
                rel_out = os.path.relpath(out, ROOT)
                job["files"].append(rel_out)
                try:
                    log_line({
                        "tag": fname[:-4],
                        "character": _char_full or _src_rec.get("character")
                        or (parse_filename(os.path.basename(src_rel)) or {}).get("char") or "未知",
                        "style": _style,
                        "tier": _tier,
                        "action": _action,
                        "outfit": _src_rec.get("outfit", "same as source"),
                        "scene": _src_rec.get("scene", ""),
                        "seed": seed, "prompt": prompt,
                        "is_redraw": True, "source": src_rel or job.get("src", ""),
                        "size": f"{w}x{h}", "steps": steps,
                        "seed_mode": seed_mode, "tags": _tags,
                        "prompt_similarity": round(_sim, 3),
                        "ok": True, "elapsed_sec": 0,
                        "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    })
                    if _tags:
                        _tl = load_json(TAG_FILE, {})
                        _tl[rel_out] = _tags
                        save_tags(_tl)
                        TAGS_CACHE[rel_out] = _tags
                except Exception as _e:
                    job["log"].append(f"❌ 写日志失败: {type(_e).__name__}: {_e}")
            else:
                job["log"].append(f"seed {seed} 失败: {(_err or '')[:200]}")
            job["done"] = k + 1
        job["status"] = "done" if job["files"] else "failed"
        _save_queue()
        for _f in (job.get("files") or []):
            try:
                _index_add(_f if isinstance(_f, str) else str(_f))
            except Exception:
                pass
    except Exception as e:
        job["status"] = "failed"
        job["error"] = f"{type(e).__name__}: {e}"
    finally:
        resume_roll_after(job)
        _cache["photos"] = None
        _cache["at"] = 0

def _redraw_one(job, src_rel, src_rec, prompt, w, h, steps, seed, outdir):
    cfg = _redraw_cfg(_char_from_prompt(prompt), prompt)
    tier, action, style = infer_meta(prompt, src_rec)
    char_full = _char_from_prompt(prompt) or src_rec.get("character") or "unknown"
    char_short = _short_tag(char_full)
    _sim = prompt_similarity(prompt, src_rec.get("prompt", ""))
    _tags = auto_cn_tags(prompt) if _sim < 0.60 else list(TAGS_CACHE.get(_norm(src_rel), []))
    fname = f"{time.strftime('%H%M%S')}_{char_short}_{tier}_{action}_{style}_{seed}.png"
    out = os.path.join(outdir, fname)
    ok, _err = _gen_to(prompt, cfg, seed, out, w, h, steps)
    if ok:
        rel_out = os.path.relpath(out, ROOT)
        job["files"].append(rel_out)
        try:
            log_line({
                "tag": fname[:-4], "character": char_full, "style": style, "tier": tier,
                "action": action, "outfit": src_rec.get("outfit", "same as source"),
                "scene": src_rec.get("scene", ""), "seed": seed, "prompt": prompt,
                "is_redraw": True, "source": src_rel, "size": f"{w}x{h}", "steps": steps,
                "seed_mode": "random", "tags": _tags, "prompt_similarity": round(_sim, 3),
                "ok": True, "elapsed_sec": 0, "batch": "multi_quick",
                "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
            })
            if _tags:
                _tl = load_json(TAG_FILE, {})
                _tl[rel_out] = _tags
                save_tags(_tl)
                TAGS_CACHE[rel_out] = _tags
        except Exception as _e:
            job["log"].append(f"❌ 写日志失败: {type(_e).__name__}: {_e}")
    else:
        job["log"].append(f"❌ {fname[:-4]} 生成失败: {(_err or '')[:200]}")
    return ok

def wait_gpu_idle(timeout=300):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if not _drawing():
            return True
        time.sleep(4)
    return False

base_seed_g = None
GACHA_LOCK = threading.Lock()
GACHA_FILE = os.path.join(WORK, "gacha_jobs.jsonl")

def gacha_lint(prompt):
    low = " " + (prompt or "").lower() + " "
    warns = []

    def _has(rx):
        return re.search(rx, low) is not None

    t = TIERC.classify_tier(prompt or "")
    if t in ("fashion", "general") and _has(r"\b(uncensored|ecchi|explicit|nsfw)\b"):
        warns.append(f"档位={t} 却带了情色词(uncensored/ecchi) —— 前缀没按档位切？")
    _st = [w for w in ("standing", "sitting on", "lying on her back", "lying on her side",
                       "on all fours", "kneeling")
           if w in low]
    if len(_st) > 1:
        warns.append("姿态矛盾：" + " + ".join(_st))
    _shoe = [w for w in ("heels", "boots", "sneakers", "sandals", "shoes", "loafers",
                         "mary janes", "flats") if w in low]
    if _shoe and _has(r"\b(barefoot|bare feet|barefooted)\b"):
        warns.append("有鞋又裸足：" + "/".join(_shoe[:2]) + " + barefoot")
    if _has(r"\bwarm\b") and _has(r"\bcool\b"):
        warns.append("光线可能两个来源（warm + cool）")
    if _has(r"close-?up on (her )?(breasts|chest|pussy|face|hips|thighs)"):
        warns.append("机位带了具体部位（机位库只应有景别状态词）")
    if t in ("fashion", "general") and _has(r"\b(barefoot|bare feet|soles visible)\b"):
        warns.append(f"档位={t} 却有裸足词")
    return t, warns

def gacha_status(job_id):
    with GACHA_LOCK:
        j = REDRAW_JOBS.get(job_id)
        if not j:
            return None
        return {"job": job_id, "status": j.get("status"), "done": j.get("done", 0),
                "total": j.get("total", 0), "files": list(j.get("files") or []),
                "outdir": j.get("outdir", ""), "error": j.get("error", ""),
                "log": (j.get("log") or [])[-8:], "prompt": j.get("prompt", "")}

def do_gacha_job(job_id, prompt, count, outdir, w, h, steps=None,
                 seed_mode="random", tier=None, action=None):
    job = REDRAW_JOBS[job_id]
    steps = int(steps or REDRAW_STEPS)
    _tier = _action = _style = ""
    pause_roll_for_gpu(job)

    def _log(msg):
        with GACHA_LOCK:
            job.setdefault("log", []).append(msg)

    def _save_trace():
        try:
            with open(GACHA_FILE, "a", encoding="utf-8") as _f:
                _f.write(json.dumps(
                    {"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "job": job_id,
                     "prompt": prompt, "tier": _tier, "action": _action,
                     "size": f"{w}x{h}", "steps": steps, "count": count,
                     "status": job.get("status"), "files": job.get("files") or [],
                     "error": job.get("error") or ""}, ensure_ascii=False) + "\n")
        except Exception:
            pass

    try:
        os.makedirs(outdir, exist_ok=True)
        cfg = _redraw_cfg(_char_from_prompt(prompt), prompt)
        _tier, _action, _style = infer_meta(prompt, {})
        _tier = tier or _tier
        _action = action or _action
        _toks_now = set(_toks(prompt))
        _char_full = ""
        for _c in TAGLIB.get("categories", []):
            if _c["key"] == "char":
                for _it in _c["items"]:
                    if _it["en"] in _toks_now:
                        _char_full = _it["en"]
                        break
            if _char_full:
                break
        if not _char_full:
            _m = re.search(r"([a-z0-9_]+_\([a-z_:]+\))", prompt)
            _char_full = _m.group(1) if _m else "未知"
        _char_short = _short_tag(_char_full)
        _tags = auto_cn_tags(prompt)
        for k in range(count):
            if seed_mode == "inherit" and base_seed_g is not None:
                seed = base_seed_g
            elif random.random() < LUCKY_RATIO:
                seed = random.choice(LUCKY_SEEDS)
            else:
                while True:
                    seed = random.randint(1, 2000000000)
                    if seed not in BAN_SEEDS:
                        break
            fname = f"{time.strftime('%H%M%S')}_{_char_short}_{_tier}_{_action}_{_style}_{seed}.png"
            out = os.path.join(outdir, fname)
            _log(f"🎨 第 {k + 1}/{count} 张 · seed {seed}")
            t0 = time.time()
            ok, _err = _gen_to(prompt, cfg, seed, out, w, h, steps)
            if not ok:
                _log(f"❌ {fname[:-4]} 生成失败: {(_err or '')[:200]}")
                with GACHA_LOCK:
                    job["error"] = (_err or "").strip()[:600]
                continue
            rel_out = os.path.relpath(out, ROOT)
            with GACHA_LOCK:
                job["files"].append(rel_out)
                job["done"] = k + 1
            try:
                log_line({
                    "tag": fname[:-4], "character": _char_full,
                    "tier": _tier, "action": _action, "style": _style,
                    "prompt": prompt, "seed": seed, "size": f"{w}x{h}", "steps": steps,
                    "seed_mode": seed_mode,
                    "is_gacha": True, "batch": "gacha", "source": "",
                    "ok": True, "elapsed_sec": round(time.time() - t0, 1),
                    "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
                })
            except Exception as _e:
                _log(f"❌ 写日志失败: {type(_e).__name__}: {_e}")
        with GACHA_LOCK:
            job["status"] = "done" if job.get("files") else "failed"
        _cache["photos"] = None
        _cache["at"] = 0
    except Exception as e:
        with GACHA_LOCK:
            job["status"] = "failed"
            job["error"] = f"{type(e).__name__}: {e}"
        _log(f"❌ 任务异常: {type(e).__name__}: {e}")
    finally:
        _save_trace()
        try:
            resume_roll_after(job)
        except Exception:
            pass

def pause_roll_for_gpu(job):
    if _ROLL_PAUSED["v"]:
        job["roll_was_running"] = True
        return
    was = roll_is_running()
    job["roll_was_running"] = was
    if not was:
        return
    _wait_stop_done()
    _freeze_roll()
    job["log"].append("⏸ 已让抽卡机停手，等它把当前这张画完…")
    t0 = time.time()
    while time.time() - t0 < 180:
        if not _roll_drawing():
            break
        time.sleep(3)
    _ROLL_PAUSED["v"] = True
    _ROLL_FROZEN["v"] = True
    job["log"].append("⏸ 抽卡机已让路（这张出完就完全停下，队列跑完自动解冻）")

def resume_roll_after(job):
    job["_launch"] = None
    pump_redraw_queue()

def do_redraw_multi(job_id, rels):
    job = REDRAW_JOBS[job_id]
    logmap = load_log()
    outdir = os.path.join(ROOT, f"重抽_{time.strftime('%Y%m%d')}")
    pause_roll_for_gpu(job)
    try:
        os.makedirs(outdir, exist_ok=True)
        for idx, rel in enumerate(rels):
            try:
                full = os.path.normpath(os.path.join(ROOT, rel))
                if not full.startswith(ROOT + os.sep) or not os.path.isfile(full):
                    job["log"].append(f"❌ 文件不存在: {rel}")
                else:
                    tag = os.path.basename(rel).rsplit(".", 1)[0]
                    rec = logmap.get(tag) or parse_filename(os.path.basename(rel)) or {}
                    prompt = rec.get("prompt") or ""
                    if not prompt:
                        job["log"].append(f"❌ 无提示词记录: {tag}")
                    else:
                        try:
                            from PIL import Image
                            with Image.open(full) as im:
                                w, h = im.size
                        except Exception:
                            w, h = WIDTH, HEIGHT
                        steps = max(4, min(12, int(rec.get("steps") or REDRAW_STEPS)))
                        _redraw_one(job, rel, rec, prompt, w, h, steps,
                                    random.randint(1, 2000000000), outdir)
            except Exception as e:
                job["log"].append(f"❌ {rel}: {type(e).__name__}: {e}")
            job["done"] = idx + 1
        job["status"] = "done" if job["files"] else "failed"
        _save_queue()
        for _f in (job.get("files") or []):
            try:
                _index_add(_f if isinstance(_f, str) else str(_f))
            except Exception:
                pass
    except Exception as e:
        job["status"] = "failed"
        job["error"] = f"{type(e).__name__}: {e}"
    finally:
        resume_roll_after(job)
        _cache["photos"] = None
        _cache["at"] = 0

def _all_source_paths(logmap):
    out = set()
    for rec in logmap.values():
        sp = rec.get("source")
        if sp:
            out.add(_norm(sp))
    return out

def _rel_of_tag(tag, rec, refs=None):
    name = tag + ".png"
    if refs:
        for sp in refs:
            if os.path.basename(sp) == name:
                return sp
    day = str(rec.get("time") or "")[:10].replace("-", "")
    cands = ([f"重抽_{day}/{name}", f"{day}/{name}", f"1001/{name}"] if day else [f"重抽_{name}"])
    for c in cands:
        if os.path.exists(os.path.join(ROOT, c)):
            return c
    return cands[0]

def load_logmap():
    m = {}
    if not os.path.exists(LOG):
        return m
    for line in open(LOG, encoding="utf-8"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("tag"):
            m[d["tag"]] = d
    return m

def _parent_stamp():
    t = 0
    for f in (LOG, VIDX_JSON):
        try:
            t = max(t, os.path.getmtime(f))
        except OSError:
            pass
    return t

_PMAP_CACHE = {"stamp": None, "map": {}}
VIDX_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_vidx.json")
_VIDX_JSON_OLD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_重抽索引.json")

def _vidx():
    try:
        src = VIDX_JSON if os.path.exists(VIDX_JSON) else _VIDX_JSON_OLD
        with open(src, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

_PMAP_CACHE = {"stamp": None, "map": {}}

def build_parent_map_cached():
    stamp = _parent_stamp()
    if _PMAP_CACHE["stamp"] == stamp and _PMAP_CACHE["map"]:
        return _PMAP_CACHE["map"]
    vi = _vidx()
    if vi and vi.get("groups"):
        pmap = {}
        for root, members in vi["groups"].items():
            r = _norm(root)
            for m in members:
                k = _norm(m)
                if k != r:
                    pmap[k] = r
        _PMAP_CACHE["map"] = pmap
    else:
        _PMAP_CACHE["map"] = build_parent_map()
    _PMAP_CACHE["stamp"] = stamp
    return _PMAP_CACHE["map"]

def build_parent_map():
    logmap = load_logmap()
    refs = _all_source_paths(logmap)
    parent = {}
    for tag, rec in logmap.items():
        if not (rec.get("is_redraw") or rec.get("is_upscale")) or not rec.get("source"):
            continue
        child = _norm(rec["rel"]) if rec.get("rel") else _rel_of_tag(tag, rec, refs)
        if child:
            parent[child] = _norm(rec["source"])
    return parent

def version_counts():
    parent = build_parent_map()
    cnt = {}

    def root_of(x):
        seen = set()
        while x in parent and x not in seen:
            seen.add(x)
            x = parent[x]
        return x

    group = {}
    for rel in parent:
        r = root_of(rel)
        group.setdefault(r, set()).add(rel)
    for rel, r in parent.items():
        group.setdefault(r, set()).add(r)
    for r, members in group.items():
        n = len(members)
        for m in members:
            cnt[m] = n
    return cnt

_VERCACHE = {"stamp": None, "map": {}}

def _index_write(vi):
    tmp = VIDX_JSON + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(vi, f, ensure_ascii=False)
        os.replace(tmp, VIDX_JSON)
    except Exception as e:
        print(f"[versions] 写索引失败: {e}", flush=True)

def _index_drop(rels):
    try:
        with open(VIDX_JSON, encoding="utf-8") as f:
            vi = json.load(f)
    except Exception:
        return
    counts = vi.get("counts") or {}
    groups = vi.get("groups") or {}
    targets = set()
    for r in rels:
        targets.add(_norm(r))
        targets.add(r)
    changed = False
    for root in list(groups.keys()):
        members = groups[root]
        hit = [m for m in members if m in targets]
        if not hit:
            continue
        changed = True
        for m in hit:
            members.remove(m)
            counts.pop(m, None)
        if len(members) < 2:
            for m in members:
                counts.pop(m, None)
            del groups[root]
        else:
            for m in members:
                counts[m] = len(members)
    member = vi.get("member") or {}
    batches = vi.get("batches") or {}
    for r in rels:
        for v in (r, _norm(r)):
            if v in member:
                bid = (member.pop(v, None) or {}).get("batch")
                if bid in batches:
                    batches[bid]["chapters"] = [
                        c for c in batches[bid].get("chapters", []) if c.get("rel") != v]
                counts.pop(v, None)
                changed = True
                break
    if changed:
        vi["member"] = member
        vi["batches"] = batches
        _index_write(vi)
        _VERCACHE["stamp"] = None
        _VERCACHE["map"] = {}
        _PMAP_CACHE["stamp"] = None
        _PMAP_CACHE["map"] = {}

def _index_add(rel):
    try:
        with open(VIDX_JSON, encoding="utf-8") as f:
            vi = json.load(f)
    except Exception:
        return
    counts = vi.get("counts") or {}
    groups = vi.get("groups") or {}

    variants = [rel, _norm(rel)]
    for root, members in groups.items():
        if any(v in members for v in variants):
            return

    rec = load_log().get(os.path.splitext(os.path.basename(rel))[0]) or {}
    src_raw = rec.get("source") or ""
    if not src_raw:
        return
    src = src_raw if src_raw.endswith(".png") else src_raw + ".png"
    src_variants = [src, _norm(src)]

    for root, members in groups.items():
        if any(v in members for v in src_variants):
            members.append(rel)
            for m in members:
                counts[m] = len(members)
            _index_write(vi)
            _VERCACHE["stamp"] = None
            _VERCACHE["map"] = {}
            return

    if os.path.exists(os.path.join(ROOT, src)):
        groups[src] = [src, rel]
        counts[src] = 2
        counts[rel] = 2
        _index_write(vi)
        _VERCACHE["stamp"] = None
        _VERCACHE["map"] = {}

def version_counts_cached():
    stamp = _parent_stamp()
    if _VERCACHE["stamp"] == stamp and _VERCACHE["map"]:
        return _VERCACHE["map"]
    vi = _vidx()
    if vi and vi.get("counts"):
        _VERCACHE["map"] = {_norm(k): v for k, v in vi["counts"].items()}
    else:
        _VERCACHE["map"] = version_counts()
    _VERCACHE["stamp"] = stamp
    return _VERCACHE["map"]

def version_group(rel, parent=None):
    parent = parent if parent is not None else build_parent_map()
    rel = _norm(rel)
    root, seen = rel, set()
    while root in parent and root not in seen:
        seen.add(root)
        root = parent[root]
    members, todo = set(), [root]
    while todo:
        cur = todo.pop()
        if cur in members:
            continue
        members.add(cur)
        for c, p in parent.items():
            if p == cur:
                todo.append(c)
    return sorted(members)

from pools.styles import STYLES as _ST, ACTIVE_STYLES as _AS

STYLE_MARK = {
    "semi": "semi-painterly illustration",
    "watercolor": "watercolor illustration",
    "gradient": "soft cel shading",
    "gacha": "semi-realistic anime illustration",
    "guofeng": "guofeng fantasy illustration",
    "digital": "digital painterly illustration",
}

def _style_seg_for(tier, key):
    seg = _ST.get(key, "")
    if tier == "fashion":
        for _w in ("uncensored", "skin gloss", "glossy highlights",
                   "subsurface scattering", "soft luminous skin", "moist skin"):
            seg = seg.replace(_w + ", ", "").replace(", " + _w, "").replace(_w, "")
        seg = ", ".join(x.strip() for x in seg.split(",") if x.strip())
    return seg

import pools.level_ladder as LL
import pools.tier_classify as TIERC

from pools import (
    BODY_POSES as POOLS_BODY_POSES, BODY_RULES as POOLS_BODY_RULES,
    HAND_SINGLE as POOLS_HAND_SINGLE, HAND_BOTH as POOLS_HAND_BOTH,
    LIGHTS as POOLS_LIGHTS, CAMERAS as POOLS_CAMERAS,
    FACE_DAILY as POOLS_FACE_DAILY, FACE_FLIRTY as POOLS_FACE_FLIRTY,
    FACE_SEX as POOLS_FACE_SEX,
)
from works import work_of, work_cn, WORK_CN
from pools.roll_params import LUCKY_SEEDS, BAN_SEEDS, LUCKY_RATIO
LEVELS = LL.LEVELS
LEVEL_LABEL = LL.LEVEL_LABEL

STATE_LIB = {
    "exposure": [
        {"key": "dressed", "label": "穿着", "kw": [], "gen": []},
        {"key": "undress", "label": "半脱",
         "kw": ["clothing slipping", "one shoulder bare", "clothing sliding", "underwear visible",
                "clothing pulled open", "unbuttoned", "strap slipped", "clothing pulled aside"],
         "gen": ["clothing slipping off her shoulder, one shoulder bare",
                 "clothing sliding down, one shoulder bare",
                 "clothing pulled open, strap slipped off her shoulder"]},
        {"key": "expose", "label": "露点",
         "kw": ["nipple", "breast out", "breasts exposed", "topless", "pussy exposed",
                "panties pulled aside"],
         "gen": ["one breast out of her clothing, nipple visible",
                 "clothing pulled aside, both breasts exposed, nipples visible",
                 "panties pulled aside, pussy exposed, one breast out"]},
        {"key": "nude", "label": "全裸",
         "kw": ["completely nude", "nude,", "naked"],
         "gen": ["completely nude, nipples and pussy visible",
                 "completely nude, bare breasts, pussy exposed"]},
    ],
    "gaze": [
        {"key": "calm", "label": "平静", "kw": [], "gen": []},
        {"key": "tease", "label": "挑逗",
         "kw": ["half-lidded", "teasing", "provocative", "sultry", "biting her lip", "seductive"],
         "gen": ["half-lidded eyes, provocative look, biting her lip",
                 "sultry gaze, looking at viewer, blushing"]},
        {"key": "pleasure", "label": "情动",
         "kw": ["eyes half closed", "mouth open", "panting", "moaning", "flushed cheeks"],
         "gen": ["eyes half closed, mouth open, panting, heavy blush",
                 "flushed face, parted lips, aroused expression"]},
        {"key": "climax", "label": "高潮",
         "kw": ["eyes rolled up", "blissful", "orgasm", "climax"],
         "gen": ["eyes rolled up, mouth open, blissful expression",
                 "blissful expression, trembling, tears of pleasure"]},
        {"key": "aftermath", "label": "事后",
         "kw": ["satisfied expression", "spent", "exhausted", "afterglow"],
         "gen": ["satisfied expression, spent, soft smile",
                 "relaxed afterglow, gentle smile, messy hair"]},
    ],
    "act": [
        {"key": "idle", "label": "常态", "kw": [], "gen": []},
        {"key": "tease", "label": "勾引",
         "kw": ["provocative pose", "arching her back", "teasing pose"],
         "gen": ["provocative pose, arching her back"]},
        {"key": "mast", "label": "自慰",
         "kw": ["masturbation", "touching her own pussy", "fingering herself",
                "fingers between her legs"],
         "gen": ["masturbation, touching her own pussy, fingers between her legs",
                 "fingering herself, hips lifted, aroused expression"]},
        {"key": "sex", "label": "做爱",
         "kw": ["sex", "penetration", "penis", "doggystyle", "missionary", "cowgirl",
                "spooning", "straddling", "fellatio", "paizuri", "cunnilingus", "mating press"],
         "gen": ["doggystyle, from behind, on all fours, ass up, sex, explicit",
                 "missionary position, on her back, legs spread apart, sex, explicit",
                 "cowgirl position, girl on top, straddling him, sex, explicit",
                 "spooning, lying on her side, from behind, sex, explicit"]},
    ],
    "stage": [
        {"key": "none", "label": "前戏", "kw": [], "gen": []},
        {"key": "sex", "label": "交合",
         "kw": ["visible penetration", "penis inserted", "penis penetrating", "genital contact"],
         "gen": ["penis inserted into pussy, pussy and penis visible, visible penetration",
                 "penis penetrating her pussy, genital contact clearly visible"]},
        {"key": "orgasm", "label": "高潮",
         "kw": ["orgasm", "climaxing"],
         "gen": ["orgasm, trembling, body arched, toes curled"]},
        {"key": "ejac", "label": "射精",
         "kw": ["ejaculation", "cum on", "creampie", "cumshot"],
         "gen": ["ejaculation", "cum on her body", "creampie"]},
        {"key": "after", "label": "事后",
         "kw": ["afterglow", "after sex", "lying exhausted", "spent"],
         "gen": ["afterglow, lying exhausted, satisfied expression",
                 "after sex, spent, messy hair, soft smile"]},
    ],
}

def _gen_frags(gen_list):
    out = []
    for g in gen_list:
        for part in str(g).split(","):
            part = part.strip()
            if len(part) >= 4:
                out.append(part)
    return out

_STATE_KW = sorted({k for dims in STATE_LIB.values() for d in dims
                    for k in (d["kw"] + _gen_frags(d["gen"]))}, key=len, reverse=True)

def is_state_token(tok):
    tl = tok.lower()
    return any(k in tl for k in _STATE_KW)

def detect_level(prompt):
    tl = (prompt or "").lower()
    def hit(dim):
        for d in reversed(STATE_LIB[dim]):
            if d["kw"] and any(k in tl for k in d["kw"]):
                return d["key"]
        return STATE_LIB[dim][0]["key"]
    stage = hit("stage")
    act = hit("act")
    if stage in ("after",):
        return "after"
    if stage in ("ejac",):
        return "ejac"
    if stage == "orgasm":
        return "orgasm"
    if act == "sex" or stage == "sex":
        return "sex"
    if act == "mast":
        return "mast"
    exp = hit("exposure")
    if exp in ("nude", "expose"):
        return "expose"
    if exp == "undress":
        return "undress"
    return "none"

def role_body_feat(prompt):
    kw = ["mature", "large breasts", "huge breasts", "big breasts", "tall",
          "petite", "flat chest", "small breasts", "loli", "small"]
    tl = (prompt or "").lower()
    return ", ".join(k for k in kw if k in tl)

def mast_tendency(role_feat, ch=""):
    low = (role_feat or "").lower()
    if any(k in low for k in ("mature", "large breasts", "huge breasts", "big breasts", "tall")):
        return 0.85
    if any(k in low for k in ("petite", "flat chest", "small breasts", "loli", "small")):
        return 0.30
    return 0.60

def detect_cloth_state(prompt):
    tl = (prompt or "").lower()
    if "completely nude" in tl or "nude," in tl or "naked" in tl:
        return "nude"
    return "clothed"

def build_state_words(level, rng, role_feat="", cloth="clothed"):
    def gen(dim, key):
        for d in STATE_LIB[dim]:
            if d["key"] == key and d["gen"]:
                return rng.choice(d["gen"])
        return ""
    words = []
    if level == "undress":
        words.append(gen("exposure", "undress"))
    elif level in ("expose", "mast", "sex", "orgasm", "ejac", "after"):
        if level == "expose" and cloth == "clothed":
            cloth = "clothed" if rng.random() < 0.35 else "nude"
        if cloth == "nude":
            words.append(gen("exposure", "nude"))
        else:
            words.append(gen("exposure", "undress") if level in ("undress",)
                         else gen("exposure", "expose"))
    gaze_map = {"none": "calm", "undress": "tease", "expose": "tease", "mast": "pleasure",
                "sex": "pleasure", "orgasm": "climax", "ejac": "climax", "after": "aftermath"}
    g = gen("gaze", gaze_map.get(level, "calm"))
    if g:
        words.append(g)
    if level == "mast":
        words.append(gen("act", "mast"))
    elif level in ("sex", "orgasm", "ejac", "after"):
        words.append(gen("act", "sex"))
        words.append(gen("stage", "sex"))
        if level in ("orgasm", "ejac", "after"):
            words.append(gen("stage", "orgasm"))
        if level in ("ejac", "after"):
            words.append(gen("stage", "ejac"))
        if level == "after":
            words.append(gen("stage", "after"))
    return [w for w in words if w]

def advance_prompt(prompt, rng, role_feat="", steps=1):
    if not role_feat:
        role_feat = role_body_feat(prompt)
    cur = detect_level(prompt)
    i = LEVELS.index(cur) if cur in LEVELS else 0
    tgt = LEVELS[min(len(LEVELS) - 1, i + steps)]
    skipped_mast = False
    if tgt == "mast" and rng.random() > mast_tendency(role_feat):
        tgt = "sex"
        skipped_mast = True
    if tgt == cur:
        return prompt, cur, tgt, False, False
    cloth = detect_cloth_state(prompt)
    kept = [t.strip() for t in (prompt or "").split(",")
            if t.strip() and not is_state_token(t.strip())]
    state = build_state_words(tgt, rng, role_feat, cloth)
    return ", ".join(kept + state), cur, tgt, True, skipped_mast

_STYLE_TABLES = None
_ARTIST_VOCAB = None
_ARTIST_PREFIX = None

def _artist_vocab():
    global _ARTIST_VOCAB, _ARTIST_PREFIX
    if _ARTIST_VOCAB is not None:
        return _ARTIST_VOCAB
    s, pre = set(), set()
    try:
        p = os.path.join(WORK, "_提取表_AnimaTools", "画师.csv")
        with open(p, encoding="utf-8-sig") as f:
            for i, line in enumerate(f):
                if i == 0:
                    continue
                t = line.split(",")[0].strip().strip('"').lower()
                if t:
                    s.add(t)
                    s.add(t.replace(" ", "_"))
                    pre.add(t.split()[0])
    except Exception:
        pass
    _ARTIST_VOCAB = s
    _ARTIST_PREFIX = pre
    return s

_STYLE_HINT = (
    "lineart", "line art", "shading", "illustration", "painting", "brushwork",
    "brush stroke", "canvas texture", "skin gloss", "glossy highlight", "watercolor",
    "watercolour", "pigment", "subsurface", "rim light", "cel shading", "flat color",
    "ink wash", "semi-realistic", "luminous skin", "moist skin", "uncensored",
    "year 20", "anime style", "2d illustration", "anime coloring", "detailed face",
)

def _is_style_token(tok, toks=None):
    if not tok:
        return False
    if tok in (toks or {}):
        return True
    low = tok.lower()
    if low.startswith("@"):
        return True
    if low in _artist_vocab():
        return True
    _pre = low.split("_")[0]
    if "_" in low and len(_pre) >= 5 and _pre in (_ARTIST_PREFIX or ()):
        return True
    if "hair" in low or "eye" in low:
        return False
    return any(h in low for h in _STYLE_HINT)

def _style_tables():
    global _STYLE_TABLES
    if _STYLE_TABLES is not None:
        return _STYLE_TABLES
    keys, toks = {}, {}
    try:
        from pools import artists as _A
        for name in (_A.weights() or {}):
            k = _A.prompt_tag(name)
            keys[k] = k
            toks[k] = k
    except Exception:
        pass
    try:
        from pools import styles as _S
        for k, v in (_S.STYLES or {}).items():
            if k.startswith("_"):
                continue
            if isinstance(v, str) and v.strip():
                keys[k] = v.strip()
                for t in v.split(","):
                    t = t.strip()
                    if t:
                        toks[t] = k
    except Exception:
        pass
    _STYLE_TABLES = (keys, toks)
    return _STYLE_TABLES

def style_options():
    out = []
    try:
        from pools import styles as _S
        for k in (_S.style_pool() or {}):
            out.append({"key": k, "label": "%s（画风）" % k})
    except Exception:
        pass
    try:
        from pools import artists as _A
        for name in (_A.weights() or {}):
            out.append({"key": _A.prompt_tag(name), "label": "@" + name})
    except Exception:
        pass
    return out

def set_style(prompt, want=""):
    import random as _rnd
    parts = [t.strip() for t in (prompt or "").split(",") if t.strip()]
    _, toks = _style_tables()
    idx = [i for i, p in enumerate(parts) if _is_style_token(p, toks)]
    opts = style_options()
    if not opts:
        return prompt, ""
    keys = [o["key"] for o in opts]
    cur = parts[idx[0]] if idx else ""
    want = (want or "").strip()
    if want and want not in keys:
        want = ""
    if not want:
        others = [k for k in keys if k != cur] or keys
        want = _rnd.choice(others)
    kept = [p for i, p in enumerate(parts) if i not in idx]
    if idx:
        at = idx[0]
    else:
        at = next((i + 1 for i, p in enumerate(kept) if p.lower() == "solo"),
                  min(3, len(kept)))
    kept.insert(max(0, min(at, len(kept))), want)
    return ", ".join(kept), want

def rotate_style(prompt, tier="", want=""):
    return set_style(prompt, want)[0]

_STYLE_RULES = [
    ("平涂",   ("flat color", "flat shading", "no lineart")),
    ("厚涂",   ("painterly", "brush stroke", "brushwork")),
    ("油画",   ("oil painting", "oil on canvas")),
    ("写实",   ("realistic", "photorealistic", "semi-realistic")),
]

def style_cat(style_str):
    t = (style_str or "").strip()
    if not t:
        return ""
    low = t.lower()
    for cn, marks in _STYLE_RULES:
        if any(m in low for m in marks):
            return cn
    _KEY = {"flat": "平涂", "painterly": "厚涂", "oil": "油画", "realistic": "写实"}
    k = t.split(",")[0].strip()
    if k.lower() in _KEY:
        return _KEY[k.lower()]
    import re as _re
    k2 = _re.sub(r"(_[a-z0-9]+)+$", "", k).strip("_")
    if k2.lower() in _KEY:
        return _KEY[k2.lower()]
    return k2 or k

def _flat_str(v):
    if not v:
        return []
    if isinstance(v, str):
        return [v]
    if isinstance(v, dict):
        out = []
        for x in v.values():
            out += _flat_str(x)
        return out
    if isinstance(v, (list, tuple, set)):
        out = []
        for x in v:
            out += _flat_str(x)
        return out
    return [str(v)]

_CLOTH_WHITE = None

def _cloth_white():
    global _CLOTH_WHITE
    if _CLOTH_WHITE is not None:
        return _CLOTH_WHITE
    W = set()

    def add(x):
        if isinstance(x, str) and x.strip() and len(x) < 90:
            W.add(" ".join(x.strip().lower().split()))

    try:
        from pools import wardrobe_pools as WP
        for tbl in (WP.GEAR, getattr(WP, "GEAR_EXT", {}) or {}):
            for _slot, items in (tbl or {}).items():
                for it in items:
                    if isinstance(it, dict):
                        add(it.get("en"))
    except Exception:
        pass
    try:
        from pools import equip_machine as EM
        for nm in ("TOPS", "BOTTOMS", "SHOES", "HEADWEAR", "EYEWEAR", "EARRINGS",
                   "NECKWEAR", "LEGWEAR", "UNDERWEAR", "SLEEVES"):
            for it in (getattr(EM, nm, None) or []):
                if isinstance(it, str):
                    add(it)
                elif isinstance(it, (list, tuple)) and it:
                    base = it[0]
                    add(base)
                    mods = it[1] if len(it) > 1 else []
                    if isinstance(mods, (list, tuple)):
                        for m in mods:
                            if isinstance(m, str) and m:
                                add("%s %s" % (m, base))
                                add("%s %s" % (base, m))
                                for w in m.split():
                                    add("%s %s" % (w, base))
        for _k, sm in (getattr(EM, "SET_SLOTS", {}) or {}).items():
            if isinstance(sm, dict):
                for _sl, words in sm.items():
                    for x in _flat_str(words):
                        add(x)
    except Exception:
        pass
    for w in ("t-shirt", "shirt", "hoodie", "jeans", "skirt", "dress", "coat", "jacket",
              "sweater", "blouse", "pants", "shorts", "socks", "thighhighs", "pantyhose",
              "glasses", "earrings", "necklace", "choker", "ribbon", "hairband", "beret",
              "hat", "gloves", "boots", "shoes", "heels", "sneakers", "belt", "scarf",
              "lingerie", "panties", "bra", "bikini", "swimsuit", "nude", "topless",
              "bare feet", "barefoot", "bare legs", "bare shoulders", "detached-sleeve",
              "sleeveless", "long-sleeved", "short-sleeved", "off-shoulder", "wet clothes",
              "towel", "apron", "kimono", "yukata", "maid", "qipao", "hanfu"):
        add(w)
    _BAD = ("visible", "see-through", "nipple", "cleavage", "pussy", "penetration",
            "no bra", "underboob", "sideboob",
            "bare", "barefoot", "nude", "topless",
            "off-shoulder", "sleeveless", "shoulderless")
    W = {w for w in W if not any(b in w for b in _BAD)}
    _CLOTH_WHITE = W
    return W

def _outfit_all(rec):
    rec = rec or {}
    pr = rec.get("prompt") or ""
    if pr:
        W = _cloth_white()
        keep = [t.strip() for t in pr.split(",")
                if t.strip() and " ".join(t.strip().lower().split()) in W]
        if keep:
            return ", ".join(keep)
    for k in ("outfit_full", "outfit_text", "outfit"):
        v = rec.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""

def _album_sort_key(name):
    m = re.search(r"(\d{8})", name)
    return (1, m.group(1), name) if m else (0, "", name)

_POS_KW = [("fellatio", ("fellatio", "in her mouth", "on her tongue", "around the tip")),
           ("paizuri", ("paizuri", "between her breasts", "breasts squeezing", "breasts wrapped")),
           ("footjob", ("footjob", "feet wrapped", "toes gripping", "sole pressed", "sole sliding")),
           ("cunnilingus", ("cunnilingus", "his tongue on her pussy", "between her thighs")),
           ("anal", ("anal sex", "penis in her ass", ", anal", "anal,")),
           ("doggystyle", ("doggystyle", "from behind", "all fours")),
           ("cowgirl", ("cowgirl", "girl on top", "straddling him")),
           ("reverse_cowgirl", ("reverse cowgirl", "facing away from him")),
           ("spooning", ("spooning", "lying on her side")),
           ("standing_wall", ("standing sex", "one leg lifted")),
           ("mating_press", ("mating press", "legs pushed up", "knees near her shoulders")),
           ("missionary", ("missionary", "on her back, legs spread")),
           ("handjob", ("handjob", "hand around it", "stroking it")),
           ("masturbation", ("masturbation", "fingering herself", "fingering")),
           ("toy", ("dildo", "vibrator", "butt plug", "anal beads", "fox tail",
                    "egg vibrator", "toy inside", "plug inserted", "strap-on")),
           ("69", ("69", "mutual oral"))]

_TIER_KW = [
    ("sex",     ("explicit", "penis in", "paizuri", "fellatio", "cunnilingus", "footjob",
                 "penetration", "creampie", "ejaculat", "cum ", "vaginal", "handjob",
                 "cowgirl", "doggystyle", "mating press", "missionary")),
    ("exposed", ("completely nude", "nipples visible", "pussy exposed", "pussy visible",
                 "bare breasts", "topless", "bottomless")),
    ("tease",   ("see-through", "camel toe", "upskirt", "underboob", "sideboob",
                 "cleavage", "visible through clothes", "lingerie")),
]

def _infer_tier(meta):
    t = meta.get("tier")
    if t in ("fashion", "tease", "exposed", "sex"):
        return t
    low = (meta.get("prompt") or "").lower()
    for key, kws in _TIER_KW:
        if any(k in low for k in kws):
            return key
    return "normal"

_POS_CN = [("handjob", "手交"), ("masturbation", "自慰"), ("fellatio", "口交"),
           ("paizuri", "乳交"), ("footjob", "足交"), ("cunnilingus", "舔阴"),
           ("doggystyle", "后入"), ("cowgirl", "骑乘"), ("missionary", "传教士"),
           ("spooning", "侧入"), ("reverse_cowgirl", "反向骑乘"), ("mating_press", "压制"),
           ("standing_wall", "站立"), ("69", "69"), ("titfuck", "乳交"),
           ("blowjob", "口交"), ("anal", "肛交"), ("tribadism", "磨镜")]

_POS_LIB_KEYS = ("sexpos", "sexroute")

def _POS_LIB_LABELS():
    global _POS_LIB_CACHE
    if _POS_LIB_CACHE is not None:
        return _POS_LIB_CACHE
    out = {}
    try:
        from collections import Counter
        cnt = Counter()
        for c in (TAGLIB.get("categories") or []):
            for sub in (c.get("subs") or []):
                for i in (sub.get("items") or []):
                    if i.get("en"):
                        cnt[i["en"]] += 1
        for c in (TAGLIB.get("categories") or []):
            for sub in (c.get("subs") or []):
                if (sub.get("label") or "") in ("体位", "玩具"):
                    for i in (sub.get("items") or []):
                        en = i.get("en")
                        if en and cnt[en] == 1:
                            out[en] = (i.get("cn") or en).strip()
    except Exception:
        pass
    _POS_LIB_CACHE = out
    return out

_POS_LIB_CACHE = None

_POS_POOL_CACHE = None

def _pos_from_pool(prompt):
    global _POS_POOL_CACHE
    if _POS_POOL_CACHE is not None:
        return _POS_POOL_CACHE
    out = {}
    try:
        from pools import sex_pool as _SP
        pool = getattr(_SP, "SEX_POOL", {}) or {}
        seen = {}
        for k, v in pool.items():
            if not isinstance(v, dict):
                continue
            cn = (v.get("cn") or "").strip()
            if not cn:
                cn = (v.get("canon") or k)
            words = []
            if v.get("canon"):
                words.append(v["canon"])
            words += list(v.get("aliases") or [])
            for w in words:
                w = (w or "").strip().lower()
                if not w:
                    continue
                if w in seen and seen[w] != cn:
                    seen[w] = ""
                else:
                    seen[w] = cn
        out = {w: cn for w, cn in seen.items() if cn}
    except Exception:
        out = {}
    _POS_POOL_CACHE = out
    return out

def _pos_from_library(prompt):
    if not prompt:
        return ""
    pool = _pos_from_pool(prompt)
    for seg in prompt.split(","):
        seg = seg.strip().lower()
        if seg in pool:
            return pool[seg]
    want = _POS_LIB_LABELS()
    if not want:
        return ""
    for seg in prompt.split(","):
        seg = seg.strip()
        if seg in want:
            return want[seg]
    return ""

def _LANG_CN():
    global _LANG_CN_CACHE
    if _LANG_CN_CACHE is None:
        try:
            _LANG_CN_CACHE = load_json(os.path.join(WORK, "taglib_cn.json"), {}) or {}
        except Exception:
            _LANG_CN_CACHE = {}
    return _LANG_CN_CACHE

_LANG_CN_CACHE = None

def _infer_pos(meta, tier=None):
    if (tier or _infer_tier(meta)) != "sex":
        return meta.get("action") or ""
    pos = (meta.get("sex_position") or "").strip()
    if pos:
        return pos
    low = (meta.get("prompt") or "").lower()
    for key, kws in _POS_KW:
        if any(k in low for k in kws):
            return key
    _lib = _pos_from_library(meta.get("prompt") or "")
    if _lib:
        return _lib
    name = (meta.get("name") or meta.get("_name") or "").lower()
    for key, kws in _POS_KW:
        if any(k in name for k in kws):
            return key
    for key, cn in _POS_CN:
        if cn in name:
            return key
    tm = meta.get("title") or meta.get("tag") or ""
    for key, cn in _POS_CN:
        if cn in tm:
            return key
    return "sex"

SIZE_INDEX_PATH = os.path.join(WORK, "_尺寸索引.json")
_SIZE_IDX = {"data": None, "mtime": 0}

def load_size_index():
    try:
        mt = os.path.getmtime(SIZE_INDEX_PATH)
    except OSError:
        return {}
    if _SIZE_IDX["data"] is not None and _SIZE_IDX["mtime"] == mt:
        return _SIZE_IDX["data"]
    try:
        _SIZE_IDX["data"] = json.load(open(SIZE_INDEX_PATH, encoding="utf-8"))
        _SIZE_IDX["mtime"] = mt
    except Exception:
        _SIZE_IDX["data"] = {}
    return _SIZE_IDX["data"]

def ratio_of(size_text):
    try:
        w, h = [int(x) for x in str(size_text).lower().split("x")]
    except Exception:
        return ""
    if w <= 0 or h <= 0:
        return ""
    r = w / h
    if abs(r - 1) < 0.02:
        return "square"
    if r > 1:
        return "landscape"
    if r < 0.52:
        return "narrow"
    return "portrait"

FACETS_JSON = os.path.join(WORK, "_facets_cache.json")
_FACETS_JSON_OLD = os.path.join(WORK, "_facets缓存.json")


_FACETS_MEM = {"at": 0.0, "data": None}


def build_facets():
    ps = scan_photos(force=True)
    tagcnt = Counter()
    for p in ps:
        for tg in p.get("tags", []):
            tagcnt[tg] += 1
    return {
        "total": len(ps),
        "chars": [list(x) for x in Counter(p["char"] for p in ps).most_common()],
        "styles": [list(x) for x in Counter(p["style"] for p in ps if p["style"] != "未知").most_common()],
        "albums": [list(x) for x in sorted(Counter(p["album"] for p in ps).items(),
                                           key=lambda x: _album_sort_key(x[0]), reverse=True)],
        "works": [[k, work_cn(k), n] for k, n in
                  Counter(p.get("work") for p in ps if p.get("work")).most_common()],
        "tags": tagcnt.most_common(),
        "favs": sum(1 for p in ps if p.get("fav")),
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


_FACETS_REBUILD = {"at": 0.0, "thread": None}


def _facets_total_now():
    """当前图片总数（用 scan_counts 的缓存，冷一次 0.08s、之后 0ms）"""
    try:
        return sum(scan_counts().values())
    except Exception:
        return -1


def _rebuild_facets_bg():
    """后台重建 facets 缓存（防重：60 秒内只起一次）"""
    now = time.time()
    if now - _FACETS_REBUILD["at"] < 60:
        return
    th = _FACETS_REBUILD["thread"]
    if th is not None and th.is_alive():
        return
    _FACETS_REBUILD["at"] = now

    def _work():
        try:
            save_facets_cache(build_facets())
        except Exception as e:
            print("[facets] 后台重建失败: %s" % e, flush=True)

    th = threading.Thread(target=_work, daemon=True)
    _FACETS_REBUILD["thread"] = th
    th.start()


def load_facets_cache():
    """读缓存。图片总数跟缓存对不上（有新增/删除）→ 后台重建，本次仍返回旧数据。"""
    now = time.time()
    d = _FACETS_MEM["data"]
    if d is None or (now - _FACETS_MEM["at"]) >= 60:
        try:
            src = FACETS_JSON if os.path.exists(FACETS_JSON) else _FACETS_JSON_OLD
            with open(src, encoding="utf-8") as f:
                d = json.load(f)
            _FACETS_MEM["data"] = d
            _FACETS_MEM["at"] = now
        except Exception:
            return None
    cur = _facets_total_now()
    if cur >= 0 and d.get("total") != cur:
        _rebuild_facets_bg()
    return d


def save_facets_cache(d):
    try:
        tmp = FACETS_JSON + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
        os.replace(tmp, FACETS_JSON)
        print("[facets] 缓存已写 %d 字节" % os.path.getsize(FACETS_JSON), flush=True)
    except Exception as e:
        import traceback
        print("[facets] 写缓存失败: %r" % (e,), flush=True)
        traceback.print_exc()


def post_roll_rebuild():
    """产线停下后重建相册缓存（只在有新增/删除时才需要）。

    等 2 秒让最后一张图落盘，然后：
      · facets 缓存重算（角色/画风/相册/标签计数）
      · 版本索引重算（重抽分组）
    两者都在后台线程里跑，不卡面板。
    """
    def _work():
        time.sleep(2)
        try:
            save_facets_cache(build_facets())
            print("[facets] 产线停止后已重建", flush=True)
        except Exception as e:
            print("[facets] 停止后重建失败: %s" % e, flush=True)
        try:
            script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_versions.py")
            if os.path.exists(script):
                import subprocess as _sp
                import sys as _sys
                _sp.Popen([_sys.executable, script],
                          cwd=os.path.dirname(os.path.abspath(__file__)),
                          stdout=_sp.DEVNULL, stderr=_sp.DEVNULL,
                          start_new_session=True)
        except Exception:
            pass
    threading.Thread(target=_work, daemon=True).start()


def _facets_warmup():
    time.sleep(3)
    try:
        scan_photos()
        save_facets_cache(build_facets())
    except Exception as e:
        print("[facets] 预热失败: %s" % e, flush=True)


_ALBUM_KEY_RD = re.compile(r"^(重抽_)(\d{8})(?:_\d{6})?$")


def _album_key_of(rel):
    """从图片的相对路径算出它属于哪个相册（与 scan_photos 的规则一致）"""
    parts = rel.split(os.sep)
    if len(parts) == 1:
        key = "(根目录)"
    elif re.fullmatch(r"\d{8}", parts[0]):
        key = parts[0]
    elif parts[0] == "自动抽卡" and len(parts) >= 3:
        key = parts[1]
    elif parts[0] == "社媒" and len(parts) >= 3:
        key = "社媒/" + parts[1]
    else:
        key = parts[0]
    m = _ALBUM_KEY_RD.match(key)
    if m:
        key = m.group(1) + m.group(2)
    return key


_COUNT_CACHE = {"at": 0.0, "data": None}


def scan_counts(force=False):
    """只数每个相册有多少张图 —— 不 stat、不查日志、不算版本。

    冷启动时相册列表页只要数量，用这个比 scan_photos() 快两个数量级。
    """
    if not force and _COUNT_CACHE["data"] is not None and (time.time() - _COUNT_CACHE["at"]) < 30:
        return _COUNT_CACHE["data"]
    agg = defaultdict(int)
    skip = load_skip_dirs()
    for dirpath, dirnames, filenames in os.walk(ROOT, followlinks=True):
        dirrel = os.path.relpath(dirpath, ROOT).replace(os.sep, "/")
        keep = []
        for d in dirnames:
            if d.startswith(("_", ".")):
                continue
            full = d if dirrel in (".", "") else dirrel + "/" + d
            if d in skip or full in skip:
                continue
            keep.append(d)
        dirnames[:] = keep
        for fn in filenames:
            if not fn.lower().endswith(IMG_EXT):
                continue
            rel = os.path.join(os.path.relpath(dirpath, ROOT), fn)
            agg[_album_key_of(rel)] += 1
    data = dict(agg)
    _COUNT_CACHE["at"] = time.time()
    _COUNT_CACHE["data"] = data
    return data


def scan_photos(force=False):
    try:
        mtime = os.path.getmtime(LOG) if os.path.exists(LOG) else 0
    except OSError:
        mtime = 0
    fresh = (time.time() - _cache.get("at", 0)) < 30
    if not force and _cache["photos"] is not None and mtime <= _cache["mtime"] and fresh:
        return _cache["photos"]

    global TAGS_CACHE, FAV_CACHE, CHAR_CACHE, TIER_CACHE
    TAGS_CACHE = load_tags()
    CHAR_CACHE = load_char_map()
    TIER_CACHE = load_tier_map()
    FAV_CACHE = set(load_favs())
    logmap = load_log()
    _SIZE_IDX_CACHE = load_size_index()
    _vmap = version_counts_cached()
    photos = []
    _skip = load_skip_dirs()
    for dirpath, dirnames, filenames in os.walk(ROOT, followlinks=True):
        _dirrel = os.path.relpath(dirpath, ROOT).replace(os.sep, "/")
        _keep = []
        for d in dirnames:
            if d.startswith(("_", ".")):
                continue
            _full = d if _dirrel in (".", "") else f"{_dirrel}/{d}"
            if d in _skip or _full in _skip:
                continue
            _keep.append(d)
        dirnames[:] = _keep
        for fn in filenames:
            if not fn.lower().endswith(IMG_EXT):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT)
            try:
                st = os.stat(full)
            except OSError:
                continue
            tag = fn.rsplit(".", 1)[0]
            meta = logmap.get(tag) or parse_filename(fn) or {}
            meta.setdefault("tag", tag)
            meta.setdefault("name", fn)
            _tier_val = TIER_CACHE.get(rel) or _infer_tier(meta)
            tags = TAGS_CACHE.get(rel, [])
            parts = rel.split(os.sep)
            if len(parts) == 1:
                album_key = "(根目录)"
            elif re.fullmatch(r"\d{8}", parts[0]):
                album_key = parts[0]
            elif parts[0] == "自动抽卡" and len(parts) >= 3:
                album_key = parts[1]
            elif parts[0] == "社媒" and len(parts) >= 3:
                album_key = "社媒/" + parts[1]
            else:
                album_key = parts[0]
            m_rd = re.match(r"^(重抽_)(\d{8})(?:_\d{6})?$", album_key)
            if m_rd:
                album_key = m_rd.group(1) + m_rd.group(2)
            _ch = (CHAR_CACHE.get(rel) or meta.get("character")
                   or meta.get("char") or "未知")
            _ch = NORM_CHAR.get(_ch, _ch)
            _ot = _outfit_all(meta)
            _el = meta.get("equip_labeled") or ""
            _size_val = meta.get("size") or ""
            if not _size_val:
                _si = _SIZE_IDX_CACHE.get(rel) or _SIZE_IDX_CACHE.get(_norm(rel))
                if _si:
                    _size_val = "%dx%d" % (_si.get("w", 0), _si.get("h", 0))
            photos.append({
                "tags": tags,
                "fav": rel in FAV_CACHE,
                "outfit": _ot,
                "style_cat": style_cat(meta.get("style") or ""),
                "equip_labeled": _el,
                "vcount": _vmap.get(_norm(rel), 1),
                "name": fn,
                "rel": rel,
                "album": album_key,
                "dir": os.path.dirname(rel),
                "bytes": st.st_size,
                "mtime": st.st_mtime,
                "char": _ch,
                "work": work_of(_ch),
                "char_manual": bool(CHAR_CACHE.get(rel)),
                "style": meta.get("style") or "未知",
                "tier": _tier_val,
                "tier_manual": bool(TIER_CACHE.get(rel)),
                "action": _infer_pos(meta, _tier_val),
                "seed": meta.get("seed"),
                "steps": meta.get("steps"),
                "size": _size_val,
                "ratio": ratio_of(_size_val),
                "prompt": meta.get("prompt", ""),
                "eros": meta.get("eros", ""),
            })
    photos.sort(key=lambda p: -p["mtime"])
    _cache["photos"] = photos
    _cache["mtime"] = mtime
    _cache["at"] = time.time()
    return photos

WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
_WEB_CACHE = {}

def load_web(name, cache=True):
    if cache and name in _WEB_CACHE:
        return _WEB_CACHE[name]
    try:
        with open(os.path.join(WEB_DIR, name), encoding="utf-8") as f:
            data = f.read()
        if name == "index.html":
            for _f in ("app.css", "app.js", "app.js", "sw.js"):
                try:
                    _mt = int(os.path.getmtime(os.path.join(WEB_DIR, _f)))
                except OSError:
                    continue
                data = re.sub(rf"/{re.escape(_f)}\?v=\d+", f"/{_f}?v={_mt}", data)
        if cache:
            _WEB_CACHE[name] = data
        return data
    except Exception:
        return ""

HTML = load_web("index.html", cache=False)

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    timeout = 30

    def _stream_zip(self, files, zipname=None):
        import zipfile

        class _ChunkedSink:
            def __init__(self, wfile):
                self.w = wfile

            def write(self, b):
                if b:
                    self.w.write(("%x\r\n" % len(b)).encode("ascii"))
                    self.w.write(b)
                    self.w.write(b"\r\n")
                return len(b)

            def flush(self):
                pass

        if zipname is None:
            zipname = "相册_%s_%d张.zip" % (time.strftime("%Y%m%d-%H%M%S"), len(files))
        from urllib.parse import quote as _q
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Disposition",
                         'attachment; filename="album.zip"; filename*=UTF-8\'\'%s' % _q(zipname))
        self.send_header("Transfer-Encoding", "chunked")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        sink = _ChunkedSink(self.wfile)
        try:
            with zipfile.ZipFile(sink, "w", zipfile.ZIP_STORED) as z:
                for full, arc in files:
                    try:
                        z.write(full, arc)
                    except OSError:
                        continue
        except (BrokenPipeError, ConnectionResetError):
            return
        try:
            self.wfile.write(b"0\r\n\r\n")
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _drain_body(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if n > 0:
                self.rfile.read(n)
        except Exception:
            pass
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False)
        if isinstance(body, str):
            body = body.encode("utf-8")
        _gzip = False
        if len(body) > 1024 and "gzip" in (self.headers.get("Accept-Encoding") or "").lower():
            import gzip as _gz
            try:
                _zb = _gz.compress(body, 6)
                if len(_zb) < len(body):
                    body, _gzip = _zb, True
            except Exception:
                _gzip = False
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        if _gzip:
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Vary", "Accept-Encoding")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        # CSRF 防护：浏览器发起的跨站请求一定会带 Origin，同源才是我们自己页面
        _origin = self.headers.get("Origin") or ""
        if _origin and not re.match(r"^https?://(127\.0\.0\.1|localhost|\[::1\])(:|$)", _origin):
            return self._send(403, {"error": "cross-origin blocked"})
        if _is_external(self.client_address, self.headers):
            if not _auth_ok(self.headers):
                body = "需要密码访问".encode("utf-8")
                self.send_response(401)
                self.send_header("WWW-Authenticate", 'Basic realm="Album"')
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                self._drain_body()
                return
            body = "访客只读，不能进行修改操作".encode("utf-8")
            self.send_response(403)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            self._drain_body()
            return
        u = urllib.parse.urlparse(self.path)
        try:
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            self._drain_body()
            return self._send(400, {"error": "bad json"})

        if u.path == "/api/tags":
            paths = body.get("paths") or []
            add = body.get("add") or []
            remove = body.get("remove") or []
            clear = bool(body.get("clear"))
            tags = load_tags()
            for rel in paths:
                if clear:
                    tags.pop(rel, None)
                    continue
                cur = set(tags.get(rel, []))
                cur.update(add)
                cur.difference_update(remove)
                if cur:
                    tags[rel] = sorted(cur)
                else:
                    tags.pop(rel, None)
            save_tags(tags)
            _cache["photos"] = None; _cache["at"] = 0
            return self._send(200, {"ok": True, "affected": len(paths),
                                    "tags": sorted({t for v in tags.values() for t in v})})

        if u.path == "/api/roll/ctl":
            action = (body.get("action") or "status").lower()
            if action in ("start", "restart", "resume", "go"):
                try:
                    import pools.roll_params as _RP
                    _ci = _RP.cap_info()
                    if _ci.get("hard_hit"):
                        return self._send(200, {
                            "ok": False, "running": roll_is_running(), "hard_hit": True,
                            "detail": "今天已到硬上限 %d 张（现在 %d）—— 产线今天停工了，"
                                      "明天零点自动复位；重抽不受影响，可以照常用。"
                                      % (_ci.get("hard") or 0, _ci.get("n") or 0)})
                    _RP.set_cap_override(True)
                except Exception as _e:
                    print("[cap] 写 override 失败:", _e, flush=True)
            ok, res = roll_ctl(action)
            if isinstance(res, bool):
                return self._send(200, {"ok": ok, "running": res, "detail": ""})
            if isinstance(res, dict):
                return self._send(200, dict(res, ok=ok))
            return self._send(200, {"ok": ok, "running": False, "detail": str(res)})

        if u.path == "/api/roll/prio":
            mode = (body.get("mode") or "").lower()
            if not mode:
                return self._send(200, roll_prio_get())
            ok, res = roll_prio_set(mode)
            if isinstance(res, dict):
                return self._send(200, dict(res, ok=ok))
            return self._send(200, {"ok": ok, "detail": str(res)})

        if u.path == "/api/pools/off":
            off = body.get("off")
            if not isinstance(off, dict):
                return self._send(400, {"ok": False, "detail": "off 必须是对象"})
            clean = {}
            for k, v in off.items():
                if not isinstance(k, str) or not isinstance(v, (list, tuple)):
                    continue
                items = sorted({str(x) for x in v if x})
                if items:
                    clean[k] = items
            tmp = OFF_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(clean, f, ensure_ascii=False, indent=1)
            os.replace(tmp, OFF_FILE)
            _POOLS_CACHE["data"] = None
            total = sum(len(v) for v in clean.values())
            return self._send(200, {"ok": True, "pools": len(clean), "total": total,
                                    "restart_needed": True})

        if u.path == "/api/char_filter/set":
            try:
                n = set_char_filter(disable=body.get("disable") or [],
                                    enable=body.get("enable") or [])
                return self._send(200, {"ok": True, "off_count": n, "restart_needed": True})
            except Exception as e:
                return self._send(500, {"error": "%s: %s" % (type(e).__name__, e)})

        if u.path == "/api/roll/config":
            cfg = load_json(ROLL_CONFIG_FILE, {})
            for k in ("daily_cap", "daily_cap_hard"):
                if k in body:
                    try:
                        cfg[k] = int(body[k])
                    except (TypeError, ValueError):
                        pass
            if isinstance(body.get("size_weights"), dict):
                sw = {}
                for k, v in body["size_weights"].items():
                    try:
                        kk = str(k).strip().lower().replace("×", "x").replace(" ", "")
                        vv = float(v)
                    except (TypeError, ValueError):
                        continue
                    if kk and vv >= 0:
                        sw[kk] = vv
                if sw and any(x > 0 for x in sw.values()):
                    cfg["size_weights"] = sw
            if isinstance(body.get("tier_weights"), dict):
                tw = cfg.get("tier_weights") or {}
                for k in ("fashion", "tease", "exposed", "sex"):
                    if k in body["tier_weights"]:
                        try:
                            tw[k] = float(body["tier_weights"][k])
                        except (TypeError, ValueError):
                            pass
                cfg["tier_weights"] = tw
            for k in ("size_idx", "steps", "seed"):
                if k in body:
                    try:
                        cfg[k] = int(body[k])
                    except (TypeError, ValueError):
                        pass
            if "seed_mode" in body:
                cfg["seed_mode"] = "fixed" if str(body["seed_mode"]).lower() == "fixed" else "random"
            if "seed_fixed" in body:
                v = body["seed_fixed"]
                if v in (None, "", "null"):
                    cfg["seed_fixed"] = None
                else:
                    try:
                        cfg["seed_fixed"] = int(v)
                    except (TypeError, ValueError):
                        cfg["seed_fixed"] = None
            if "equip_mode" in body:
                cfg["equip_mode"] = bool(body["equip_mode"])
            save_json(ROLL_CONFIG_FILE, cfg)
            return self._send(200, {"ok": True, "config": cfg, "restart_needed": True})

        if u.path == "/api/outfit/save":
            rel = (body.get("rel") or "").strip()
            tag = os.path.basename(rel).rsplit(".", 1)[0]
            rec = load_log().get(tag) or {}
            if rec.get("tier") != "fashion":
                return self._send(400, {"error": "保存搭配只在**时尚档**生效"})
            parts, seg = _outfit_parts(rec)
            if not seg:
                return self._send(400, {"error": "这张没有可保存的服装段"})
            os.makedirs(OUTFIT_THUMB, exist_ok=True)
            oid = "o%d" % (int(time.time() * 1000) % 10 ** 10)
            thumb = os.path.join(OUTFIT_THUMB, oid + ".jpg")
            try:
                from PIL import Image
                im = Image.open(os.path.join(ROOT, rel)).convert("RGB")
                w, h = im.size
                tw = int(w * 0.62)
                th = min(h, int(tw * 4 / 3))
                tw = int(th * 3 / 4)
                left = (w - tw) // 2
                top = int((h - th) * 0.26)
                im.crop((left, top, left + tw, top + th)).resize((240, 320)).save(thumb, quality=88)
            except Exception as e:
                return self._send(500, {"error": f"缩略图生成失败: {e}"})
            d = load_outfits()
            d["outfits"].insert(0, {
                "id": oid,
                "name": (body.get("name") or (rec.get("outfit") or "搭配"))[:60],
                "set": rec.get("style_set") or "",
                "thumb": os.path.relpath(thumb, ROOT),
                "src": rel, "parts": parts, "prompt_seg": seg,
                "tier": rec.get("tier"), "time": time.strftime("%Y-%m-%d %H:%M"),
            })
            d["outfits"] = d["outfits"][:300]
            save_outfits(d)
            return self._send(200, {"ok": True, "id": oid, "prompt_seg": seg})

        if u.path == "/api/outfit/list":
            from pools.set_slots import SET_SLOTS
            from pools.style_sets import STYLE_SETS
            sets = [{"key": k, "label": (STYLE_SETS.get(k) or {}).get("cn", k)} for k in SET_SLOTS]
            d = load_outfits()
            return self._send(200, {"outfits": d.get("outfits", []), "sets": sets})

        if u.path == "/api/mytags":
            d = load_json(MYTAGS_FILE, {"tags": []})
            cats = [{"key": c["key"], "label": c.get("label", c["key"])}
                    for c in TAGLIB.get("categories", [])]
            return self._send(200, {"tags": d.get("tags", []), "cats": cats})

        if u.path == "/api/mytags/save":
            en = (body.get("en") or "").strip()
            if not en:
                return self._send(400, {"error": "英文标签不能为空"})
            cn = (body.get("cn") or "").strip()
            cat = (body.get("cat") or "custom").strip()
            tier = (body.get("tier") or "").strip()
            d = load_json(MYTAGS_FILE, {"tags": []})
            arr = [t for t in d.get("tags", []) if t.get("en") != en]
            arr.append({"en": en, "cn": cn, "cat": cat, "tier": tier,
                        "t": time.strftime("%Y-%m-%dT%H:%M:%S")})
            d["tags"] = arr[:600]
            save_json(MYTAGS_FILE, d)
            return self._send(200, {"ok": True, "tags": d["tags"]})

        if u.path == "/api/mytags/del":
            en = (body.get("en") or "").strip()
            d = load_json(MYTAGS_FILE, {"tags": []})
            d["tags"] = [t for t in d.get("tags", []) if t.get("en") != en]
            save_json(MYTAGS_FILE, d)
            return self._send(200, {"ok": True, "tags": d["tags"]})

        if u.path == "/api/tier_guess":
            _p = (body.get("prompt") or "").strip()
            _t = TIERC.classify_tier(_p)
            _a = "gacha"
            if _t == "sex":
                _pl = _p.lower()
                _pp = next((k for k in SEX_POS_KEYS if k in _pl), None)
                _a = _pp.replace(" ", "_") if _pp else "sex"
            return self._send(200, {"tier": _t, "action": _a, "matched": TIERC.matched(_p)})

        if u.path == "/api/gacha/fill":
            import random as _r
            rng_ = _r.Random()
            cat = (body.get("pose_cat") or "").strip()
            tier = (body.get("tier") or "").strip()
            want = body.get("want") or {}
            reroll = bool(body.get("reroll"))
            out = {}

            def _one(seq):
                seq = [x for x in (seq or []) if x]
                return rng_.choice(seq) if seq else ""

            _CAT = {"##stand": r"(standing|stand|stance|gait|leaning)",
                    "##sit": r"(sitting|seated|reclining|squatting|upright)",
                    "##lie": r"(lying|on her back|on her side)",
                    "##kneel": r"(kneel)", "##bend": r"(all fours|prone|bent|crouch|stomach)"}
            if cat and cat != "##rand":
                rx = _CAT.get(cat)
                pool = [p for p in POOLS_BODY_POSES if rx and re.search(rx, p.lower(), re.I)]
                pool = pool or list(POOLS_BODY_POSES)
            elif cat:
                pool = list(POOLS_BODY_POSES)
            else:
                pool = []
            _fashion = tier not in ("tease", "exposed", "sex")

            def _cat(key):
                for _c in (TAGLIB.get("categories") or []):
                    if _c.get("key") == key:
                        return [i["en"] for i in (_c.get("items") or []) if i.get("en")]
                return []

            if want.get("outfit"):
                if not _fashion:
                    out["outfit"] = _one(_cat("outfit"))
                else:
                    _dre = re.compile(r"(dress|gown|one-piece|qipao|cheongsam|kimono|yukata)", re.I)
                    _tops = [x for x in _cat("fit_top") if not _dre.search(x)]
                    _dres = [x for x in _cat("fit_top") if _dre.search(x)]
                    _bots, _shoes = _cat("fit_bottom"), _cat("fit_shoe")
                    if _dres and rng_.random() < 0.40:
                        out["outfit"] = ", ".join(x for x in (_one(_dres), _one(_shoes)) if x)
                    else:
                        out["outfit"] = ", ".join(x for x in (_one(_tops), _one(_bots), _one(_shoes)) if x)

            def _leg_pool(seq):
                seq = [x for x in (seq or []) if x]
                if _fashion:
                    seq = [x for x in seq
                           if not re.search(r"feet toward|soles|toes|tiptoes|barefoot|bare feet",
                                             x, re.I)]
                return seq or [x for x in (seq or []) if x]

            pose = _one(pool) if want.get("pose") else ""
            if pose:
                out["pose"] = pose
                rule = POOLS_BODY_RULES.get(pose) or {}
                for k in ("head", "hand", "leg"):
                    if want.get(k):
                        out[k] = _one(_leg_pool(rule.get(k)) if k == "leg"
                                      else rule.get(k))
            elif want.get("hand"):
                out["hand"] = _one(POOLS_HAND_SINGLE) or _one(POOLS_HAND_BOTH)
            if want.get("mood"):
                _fp = {"fashion": POOLS_FACE_DAILY, "tease": POOLS_FACE_FLIRTY,
                       "exposed": POOLS_FACE_FLIRTY, "sex": POOLS_FACE_SEX}.get(tier,
                                                                              POOLS_FACE_DAILY)
                out["mood"] = _one(_fp.get("expression"))
            if want.get("light"):
                out["light"] = _one(POOLS_LIGHTS)
            if want.get("camera"):
                _cams = [c for c in POOLS_CAMERAS
                         if not _fashion
                         or (isinstance(c, (list, tuple)) and c[1] in ("full", "upper"))]
                out["camera"] = _one([c[0] if isinstance(c, (list, tuple)) else c for c in _cams])
            return self._send(200, {"slots": out})

        if u.path == "/api/gacha":
            gp = (body.get("prompt") or "").strip()
            if not gp:
                return self._send(400, {"error": "empty prompt"})
            pre = (body.get("prefix") or "").strip()
            suf = (body.get("suffix") or "").strip()
            full = ", ".join([x for x in (pre, gp, suf) if x])
            _clean = [t.strip() for t in full.split(",") if t.strip()]
            _clean = [t for t in _clean if t.lower() not in ("uncensored", "ecchi")]
            for _need in ("safe", "fashion"):
                if not any(t.lower() == _need for t in _clean):
                    _clean.append(_need)
            _clean = ", ".join(_clean)
            _tclean = TIERC.classify_tier(_clean)
            if _tclean in ("fashion", "general") and _clean != full:
                full = _clean
            g_tier = TIERC.classify_tier(full)
            _ltier, _lwarns = gacha_lint(full)
            g_action = "gacha"
            if g_tier == "sex":
                _gl = full.lower()
                _gpos = next((k for k in SEX_POS_KEYS if k in _gl), None)
                g_action = _gpos.replace(" ", "_") if _gpos else "sex"
            try:
                w = int(body.get("width") or 1024)
                h = int(body.get("height") or 1536)
                steps = int(body.get("steps") or REDRAW_STEPS)
                cnt = max(1, min(int(body.get("count") or 1), 8))
            except Exception:
                return self._send(400, {"error": "bad numeric args"})
            seed_mode = body.get("seed_mode") or "random"
            folder = body.get("folder") or f"自定义抽卡_{time.strftime('%Y%m%d')}"
            outdir = os.path.join(ROOT, folder)
            job_id = f"gc{int(time.time())}{random.randint(100, 999)}"
            REDRAW_JOBS[job_id] = {
                "status": "queued", "done": 0, "total": cnt, "files": [], "error": "",
                "log": (["ガチャ · 自定义抽卡（单次任务）"]
                        + (["⚠️ 自检: " + w for w in _lwarns] if _lwarns else [])), "src": "",
                "outdir": os.path.relpath(outdir, ROOT), "prompt": full,
                "tier": g_tier, "action": g_action,
                "size": f"{w}x{h}", "steps": steps, "seed_mode": seed_mode,
                "multi": False,
            }
            _pos = enqueue_redraw(job_id, lambda: threading.Thread(
                target=do_gacha_job,
                args=(job_id, full, cnt, outdir, w, h),
                kwargs={"steps": steps, "seed_mode": seed_mode,
                        "tier": g_tier, "action": g_action},
                daemon=True).start())
            _save_queue()
            return self._send(200, {"ok": True, "job": job_id, "count": cnt,
                                    "queued": _pos, "position": _pos, "prompt": full,
                                    "tier": g_tier, "action": g_action,
                                    "warnings": _lwarns})

        if u.path == "/api/redraw":
            def _log_job(kind, data):
                try:
                    with open(os.path.join(WORK, "redraw_jobs.jsonl"), "a", encoding="utf-8") as f:
                        f.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                            "kind": kind, **data}, ensure_ascii=False) + "\n")
                except Exception:
                    pass

            rels = [r for r in (body.get("rels") or []) if r]
            if rels:
                rels = rels[:30]
                job_id = f"rm{int(time.time())}{random.randint(100, 999)}"
                outdir = os.path.join(ROOT, f"重抽_{time.strftime('%Y%m%d')}")
                REDRAW_JOBS[job_id] = {"status": "queued", "done": 0, "total": len(rels),
                                       "files": [], "error": "", "log": [], "src": "",
                                       "outdir": os.path.relpath(outdir, ROOT),
                                       "prompt": "", "multi": True,
                                       "rels": list(rels)}
                _log_job("multi", {"job": job_id, "count": len(rels), "rels": rels})
                _pos = enqueue_redraw(job_id, lambda: threading.Thread(
                    target=do_redraw_multi, args=(job_id, rels), daemon=True).start())
                _save_queue()
                return self._send(200, {"ok": True, "job": job_id, "count": len(rels),
                                        "multi": True, "queued": 0, "position": 0})

            rel = body.get("rel") or ""
            count = int(body.get("count") or 1)
            gmode = body.get("mode") or "newseed"
            seed_mode = body.get("seed_mode") or ("inherit" if gmode == "same" else "random")
            full = os.path.normpath(os.path.join(ROOT, rel))
            if not full.startswith(ROOT + os.sep) or not os.path.isfile(full):
                return self._send(404, {"error": "image not found"})
            tag = os.path.basename(rel).rsplit(".", 1)[0]
            logmap = load_log()
            rec = logmap.get(tag)
            prompt = (body.get("prompt") or "").strip()
            if not prompt:
                prompt = (rec or {}).get("prompt") or ""
            if not prompt:
                return self._send(400, {"error": "日志里没有这张的提示词，无法重抽"})

            quick = (body.get("quick") or "").lower()
            quick_note = ""
            if quick == "style":
                prompt, _sw = set_style(prompt, body.get("style") or "")
                seed_mode = "inherit"
                quick_note = f"🎨 换成画风 {_sw}" if _sw else "🎨 换画风（没找到画风段）"
            elif quick == "split":
                prompt, _dropped, _added = split_prompt(prompt)
                w, h = 1536, 1024
                seed_mode = "inherit"
                count = 1
                quick_note = f"🔧 拆分·设定图（加标签 {_added} 个 / 去环境 {_dropped} 段 / 强制横屏）"
            elif quick in ("outfit", "set"):
                from pools.set_slots import SET_SLOTS
                import pools.equip_machine as _EM
                _keep = _strip_clothing(prompt)
                if quick == "outfit":
                    _oid = (body.get("outfit_id") or "").strip()
                    _o = next((x for x in load_outfits()["outfits"] if x["id"] == _oid), None)
                    if not _o:
                        return self._send(400, {"error": "找不到这套搭配"})
                    _cl = _o.get("prompt_seg") or ""
                    quick_note = f"👗 换成保存的搭配「{_o.get('name') or _oid}」"
                else:
                    _sk = (body.get("set_key") or "").strip()
                    if _sk not in SET_SLOTS:
                        return self._send(400, {"error": "没有这个套装"})
                    _r = random.Random()
                    _cl = ", ".join(_r.choice(v) for v in SET_SLOTS[_sk].values() if v)
                    quick_note = f"👗 换成套装「{_sk}」（套内随机组合）"
                _mm = _split_catmap()
                _ins = 0
                for _i, _t in enumerate(_keep):
                    if _cat_of(_t, _mm) in ("char", "charfeat"):
                        _ins = _i + 1
                prompt = ", ".join(_keep[:_ins] + [x.strip() for x in _cl.split(",") if x.strip()]
                                   + _keep[_ins:])
                seed_mode = "inherit"
                count = 1
            elif quick == "advance":
                prompt, _f, _t, _ok, _notes = LL.advance(prompt, random, rec=rec)
                seed_mode = "inherit"
                if not _ok:
                    return self._send(400, {"error": f"已经是最后一级（{LEVEL_LABEL.get(_f, _f)}），没法再进一步了"})
                quick_note = f"⏩ {LEVEL_LABEL.get(_f, _f)} → {LEVEL_LABEL.get(_t, _t)}"
                if _notes:
                    quick_note += "　｜" + "；".join(_notes[:4])
                count = 1
            try:
                w = int(body.get("width") or 0)
                h = int(body.get("height") or 0)
            except (TypeError, ValueError):
                w = h = 0
            if not (w and h):
                try:
                    from PIL import Image
                    with Image.open(full) as im:
                        w, h = im.size
                except Exception:
                    w, h = WIDTH, HEIGHT
            _src_steps = (rec or {}).get("steps")
            try:
                steps = max(4, min(12, int(body.get("steps") or _src_steps or REDRAW_STEPS)))
            except (TypeError, ValueError):
                steps = REDRAW_STEPS
            base_seed = None
            if seed_mode == "inherit":
                base_seed = (rec or {}).get("seed") or body.get("seed")
                try:
                    base_seed = int(base_seed)
                except (TypeError, ValueError):
                    base_seed = None
                if base_seed is None:
                    return self._send(400, {"error": "原图没有可用种子，无法继承"})
                count = 1
            count = max(1, min(4, count))
            if len(REDRAW_JOBS) > 30:
                for _k in sorted(REDRAW_JOBS, key=lambda x: REDRAW_JOBS[x].get("status") == "running")[:10]:
                    if REDRAW_JOBS[_k].get("status") != "running":
                        REDRAW_JOBS.pop(_k, None)
            job_id = f"r{int(time.time())}{random.randint(100, 999)}"
            outdir = os.path.join(ROOT, f"重抽_{time.strftime('%Y%m%d')}")
            REDRAW_JOBS[job_id] = {"status": "queued", "done": 0, "total": count,
                                   "files": [], "error": "", "log": [], "src": rel,
                                   "outdir": os.path.relpath(outdir, ROOT), "prompt": prompt,
                                   "size": f"{w}x{h}", "steps": steps, "seed_mode": seed_mode,
                                   "seed": base_seed}
            _log_job("single", {"job": job_id, "src": rel, "count": count,
                                "size": f"{w}x{h}", "steps": steps, "seed_mode": seed_mode,
                                "quick": quick or ""})
            if quick_note:
                REDRAW_JOBS[job_id]["log"].append(quick_note)
            _pos = enqueue_redraw(job_id, lambda: threading.Thread(
                target=do_redraw_job,
                args=(job_id, prompt, count, outdir, w, h),
                kwargs={"steps": steps, "seed_mode": seed_mode,
                        "base_seed": base_seed, "src_rel": rel},
                daemon=True).start())
            return self._send(200, {"ok": True, "job": job_id, "count": count,
                                    "size": f"{w}x{h}", "steps": steps,
                                    "seed_mode": seed_mode,
                                    "queued": 0, "position": 0})

        if u.path == "/api/delete":
            paths = body.get("paths") or []
            # Windows 没有 ~/.Trash，落到用户目录下的 .Trash 里，语义保持一致
            trash = (os.path.join(os.path.expanduser("~"), ".Trash") if IS_WIN
                     else os.path.expanduser("~/.Trash"))
            os.makedirs(trash, exist_ok=True)
            moved, failed = [], []
            import time as _t
            for rel in paths:
                full = os.path.normpath(os.path.join(ROOT, rel))
                if not full.startswith(ROOT + os.sep) or not os.path.isfile(full):
                    failed.append(rel); continue
                dst = os.path.join(trash, os.path.basename(rel))
                if os.path.exists(dst):
                    stem, ext = os.path.splitext(os.path.basename(rel))
                    stamp = _t.strftime("%H%M%S")
                    dst = os.path.join(trash, f"{stem}_{stamp}{ext}")
                    i = 1
                    while os.path.exists(dst):          # 同名就继续加序号，别覆盖
                        dst = os.path.join(trash, f"{stem}_{stamp}_{i}{ext}")
                        i += 1
                try:
                    shutil.move(full, dst)
                    moved.append(rel)
                    tags = load_tags()
                    if rel in tags:
                        tags.pop(rel, None)
                        save_tags(tags)
                except Exception:
                    failed.append(rel)
            _cache["photos"] = None
            _index_drop(moved)
            return self._send(200, {"ok": True, "moved": len(moved),
                                    "failed": failed, "to": "废纸篓 (%s)" % trash})

        if u.path == "/api/redraw/reorder":
            order = [x for x in (body.get("order") or []) if x]
            with REDRAW_LOCK:
                _pending = [j for j in REDRAW_QUEUE
                            if (REDRAW_JOBS.get(j) or {}).get("status") == "queued"]
                valid = [j for j in order if j in _pending]
                for j in _pending:
                    if j not in valid:
                        valid.append(j)
                it = iter(valid)
                REDRAW_QUEUE[:] = [
                    (next(it) if (REDRAW_JOBS.get(j) or {}).get("status") == "queued" else j)
                    for j in REDRAW_QUEUE]
                for i, jid in enumerate(REDRAW_QUEUE, 1):
                    _j = REDRAW_JOBS.get(jid)
                    if _j is not None:
                        _j["position"] = i
            return self._send(200, {"ok": True, **queue_snapshot()})

        if u.path == "/api/redraw/cancel":
            jid = body.get("job") or ""
            with REDRAW_LOCK:
                if jid in REDRAW_QUEUE:
                    REDRAW_QUEUE.remove(jid)
                    _save_queue()
            _j = REDRAW_JOBS.get(jid)
            if _j and _j.get("status") == "queued":
                _j["status"] = "cancelled"
                _j["log"].append("🚫 已从队列移除")
            return self._send(200, {"ok": True, **queue_snapshot()})

        if u.path == "/api/redraw/clear-done":
            with REDRAW_LOCK:
                keep = []
                for jid in REDRAW_QUEUE:
                    j = REDRAW_JOBS.get(jid) or {}
                    if j.get("status") == "done":
                        REDRAW_JOBS.pop(jid, None)
                        continue
                    keep.append(jid)
                REDRAW_QUEUE[:] = keep
                _save_queue()
            return self._send(200, {"ok": True, **queue_snapshot()})

        if u.path == "/api/redraw/retry-failed":
            n = 0
            with REDRAW_LOCK:
                for jid in REDRAW_QUEUE:
                    j = REDRAW_JOBS.get(jid)
                    if not j or j.get("status") != "failed":
                        continue
                    rels = j.get("rels")
                    if isinstance(rels, list) and rels:
                        j["_launch"] = (lambda jid=jid, rs=list(rels):
                                        threading.Thread(target=do_redraw_multi,
                                                         args=(jid, rs), daemon=True).start())
                    elif j.get("src"):
                        try:
                            _w, _h = (j.get("size") or "1024x1536").split("x")
                            _od = j.get("outdir") or ""
                            if _od and not os.path.isabs(_od):
                                _od = os.path.join(ROOT, _od)
                            j["_launch"] = (lambda jid=jid, src=j["src"],
                                                   p=j.get("prompt") or "",
                                                   c=int(j.get("total") or 1),
                                                   od=_od,
                                                   w=int(_w), h=int(_h),
                                                   st=j.get("steps"),
                                                   sm=j.get("seed_mode") or "random":
                                            threading.Thread(
                                                target=do_redraw_job,
                                                args=(jid, p, c, od, w, h, st, sm, None, src),
                                                daemon=True).start())
                        except Exception:
                            continue
                    else:
                        continue
                    j["status"] = "queued"
                    j["error"] = ""
                    j.setdefault("log", []).append("🔄 重新排队（失败重跑）")
                    n += 1
                _save_queue()
            if n:
                threading.Timer(1.0, pump_redraw_queue).start()
            return self._send(200, {"ok": True, "retried": n, **queue_snapshot()})

        if u.path == "/api/merge-redraw":
            album = (body.get("album") or "").strip().strip("/")
            m = re.match(r"^重抽_(\d{8})$", album)
            if not m:
                return self._send(400, {"error": "只能合并「重抽_日期」这种文件夹"})
            date = m.group(1)
            src_dir = os.path.realpath(os.path.join(ROOT, album))
            dst_dir = os.path.realpath(os.path.join(ROOT, date))
            root_real = os.path.realpath(WORK)
            if not src_dir.startswith(root_real) or not dst_dir.startswith(root_real):
                return self._send(400, {"error": "路径不合法"})
            if not os.path.isdir(src_dir):
                return self._send(404, {"error": f"文件夹不存在：{album}"})
            os.makedirs(dst_dir, exist_ok=True)
            moved, renamed, skipped = [], [], []
            for fn in sorted(os.listdir(src_dir)):
                if not fn.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    continue
                src = os.path.join(src_dir, fn)
                if not os.path.isfile(src):
                    continue
                dst = os.path.join(dst_dir, fn)
                if os.path.exists(dst):
                    stem, ext = os.path.splitext(fn)
                    i = 1
                    while os.path.exists(os.path.join(dst_dir, f"{stem}_{i}{ext}")):
                        i += 1
                    dst = os.path.join(dst_dir, f"{stem}_{i}{ext}")
                    renamed.append(os.path.basename(dst))
                try:
                    shutil.move(src, dst)
                    moved.append(os.path.basename(dst))
                except Exception as e:
                    skipped.append(f"{fn}: {type(e).__name__}")
            left = [f for f in os.listdir(src_dir)
                    if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
            if left:
                return self._send(200, {"ok": False, "moved": len(moved), "renamed": renamed,
                                        "error": f"还有 {len(left)} 张没搬走，暂不删除文件夹"})
            try:
                shutil.rmtree(src_dir)
                removed = True
            except Exception as e:
                removed = False
                skipped.append(f"删文件夹失败: {e}")
            _cache["photos"] = None
            _cache["at"] = 0
            try:
                if os.path.exists(VIDX_JSON):
                    os.remove(VIDX_JSON)
            except Exception as e:
                print(f"[merge] 索引失效失败（下次请求会用旧索引）: {e}", flush=True)
            if renamed:
                print(f"[merge] ⚠️ 有 {len(renamed)} 张因重名被改名，这些会脱离版本链: {renamed[:5]}",
                      flush=True)
            return self._send(200, {"ok": True, "date": date, "album": album,
                                    "target": date, "moved": len(moved),
                                    "renamed": renamed, "skipped": skipped,
                                    "dir_removed": removed})

        if u.path == "/api/tier":
            paths = [p for p in (body.get("paths") or []) if p]
            newtier = (body.get("tier") or "").strip()
            if newtier and newtier not in TIER_ALL:
                return self._send(400, {"error": "invalid tier"})
            tm = load_tier_map()
            for rel in paths:
                if newtier: tm[rel] = newtier
                else: tm.pop(rel, None)
            save_tier_map(tm)
            _cache["photos"] = None; _cache["at"] = 0
            return self._send(200, {"ok": True, "affected": len(paths), "tier": newtier})

        if u.path == "/api/char":
            paths = [p for p in (body.get("paths") or []) if p]
            newchar = (body.get("char") or "").strip()
            cm = load_char_map()
            for rel in paths:
                if newchar:
                    cm[rel] = newchar
                else:
                    cm.pop(rel, None)
            save_char_map(cm)
            _cache["photos"] = None; _cache["at"] = 0
            return self._send(200, {"ok": True, "affected": len(paths), "char": newchar})

        if u.path == "/api/fav":
            paths = body.get("paths") or []
            value = bool(body.get("value", True))
            favs = set(load_favs())
            for rel in paths:
                if value:
                    favs.add(rel)
                else:
                    favs.discard(rel)
            save_json(FAV_FILE, sorted(favs))
            _cache["photos"] = None; _cache["at"] = 0
            return self._send(200, {"ok": True, "affected": len(paths),
                                    "count": len(favs)})

        return self._send(404, {"error": "not found"})

    def do_GET(self):
        self._authed = _auth_ok(self.headers)
        if _is_external(self.client_address, self.headers) and not _auth_ok(self.headers):
            body = "需要密码访问（用户名随意，密码见分享说明）".encode("utf-8")
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Album"')
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        _ext = _is_external(self.client_address, self.headers)
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        path = u.path

        if path == "/":
            return self._send(200, load_web("index.html", cache=False),
                              "text/html; charset=utf-8")

        if path == "/api/dl/zip":
            _raw = []
            for _k in ("rel", "rels", "p"):
                _raw += q.get(_k) or []
            _rels = []
            for _chunk in _raw:
                _rels += [x for x in str(_chunk).split(",") if x.strip()]
            _files, _seen = [], set()
            for _r in _rels:
                _r = _r.strip()
                _full = os.path.normpath(os.path.join(ROOT, _r))
                if not _full.startswith(ROOT + os.sep) or not os.path.isfile(_full):
                    continue
                if not _visible_to_visitor(_r, _ext):
                    continue
                _arc = os.path.basename(_full)
                if _arc in _seen:
                    _arc = "%s_%s" % (os.path.basename(os.path.dirname(_full)) or "x", _arc)
                _seen.add(_arc)
                _files.append((_full, _arc))
            if not _files:
                return self._send(400, {"error": "没有可下载的图"})
            return self._stream_zip(_files)

        if path in ("/app.css", "/app.js"):
            name = path.lstrip("/")
            ctype = "text/css; charset=utf-8" if name.endswith(".css") else "application/javascript; charset=utf-8"
            data = load_web(name, cache=False)
            if not data:
                return self._send(404, {"error": "not found"})
            return self._send(200, data, ctype)

        if path in ("/manifest.webmanifest", "/sw.js"):
            fp = os.path.join(WORK, "web_icons", path.lstrip("/"))
            if os.path.isfile(fp):
                ctype = ("application/manifest+json" if path.endswith(".webmanifest")
                         else "application/javascript")
                with open(fp, "rb") as f:
                    return self._send(200, f.read(), ctype)
            return self._send(404, {"error": "not found"})

        if path == "/favicon.ico" or re.match(r"^/icon-\d+\.png$", path):
            name = "favicon.ico" if path == "/favicon.ico" else path.lstrip("/")
            fp = os.path.join(WORK, "web_icons", name)
            if os.path.isfile(fp):
                ctype = "image/x-icon" if name.endswith(".ico") else "image/png"
                with open(fp, "rb") as f:
                    data = f.read()
                return self._send(200, data, ctype)
            return self._send(404, {"error": "icon not found"})

        if path == "/api/gacha/status":
            _gj = q.get("job", [""])[0]
            _st = gacha_status(_gj)
            if not _st:
                return self._send(404, {"error": "no such gacha job"})
            return self._send(200, _st)

        if path == "/api/redraw_status":
            jid = q.get("job", [""])[0]
            j = REDRAW_JOBS.get(jid)
            if not j:
                return self._send(404, {"error": "job not found"})
            safe = {k: v for k, v in j.items() if not k.startswith("_")}
            safe["position"] = (REDRAW_QUEUE.index(jid) + 1) if jid in REDRAW_QUEUE else 0
            safe["queued"] = len(REDRAW_QUEUE)
            return self._send(200, safe)

        if path == "/api/version":
            return self._send(200, {"version": project_version()})

        if path == "/api/styles":
            return self._send(200, {"styles": style_options()})

        if path == "/api/taglib":
            _cw = {}
            for _c in (TAGLIB.get("categories") or []):
                if not (_c.get("key") == "char"
                        or _c.get("label") == "人物"
                        or any("char" in (x.get("from") or []) for x in (_c.get("subs") or []))):
                    continue
                _citems = []
                _subs = _c.get("subs")
                if not _subs:
                    _citems = list(_c.get("items") or [])
                else:
                    for _sub in _subs:
                        if _sub.get("label") == "角色" or "char" in (_sub.get("from") or []):
                            _citems += list(_sub.get("items") or [])
                for _it in _citems:
                    try:
                        import works as _W
                        _k = _W.work_of(_it["en"])
                    except Exception:
                        _k = ""
                    if _k:
                        _cw[_it["en"]] = _k
                break
            if USE_LAYER_TAGLIB and LAYERLIB.get("categories"):
                _co = LAYERLIB.get("cat_of") or {}
                _ord = LAYERLIB.get("order") or []
                _lab = LAYERLIB.get("cat_labels") or {}
                _cw = {}
                _char_keys = [k for k, v in _lab.items() if v in ("角色",)]
                try:
                    import works as _W2
                except Exception:
                    _W2 = None
                for _en, _k in _co.items():
                    if _k in _char_keys and _W2 is not None:
                        try:
                            _wk = _W2.work_of(_en)
                        except Exception:
                            _wk = ""
                        if _wk:
                            _cw[_en] = _wk
                return self._send(200, dict(TAGLIB,
                                            compose=_compose_tables(), works=WORK_CN,
                                            categories=LAYERLIB["categories"],
                                            cat_of=_co, order=_ord, cat_labels=_lab,
                                            cat_tiers=LAYERLIB.get("cat_tiers") or {},
                                            cat_by_tier=LAYERLIB.get("cat_by_tier") or {},
                                            char_works=_cw,
                                            char_feats=LAYERLIB.get("char_feats") or {},
                                            tiers=LAYERLIB.get("tiers") or {},
                                            taglib_version=LAYERLIB.get("version", "layer-1"),
                                            tier_colors=TAG_TIERS.get("colors", {}),
                                            tier_classes=TAG_TIERS.get("classes", {})))

            _co, _ord, _lab = _tag_flat_index()
            return self._send(200, dict(TAGLIB, compose=_compose_tables(), works=WORK_CN,
                                        cat_of=_co, order=_ord, cat_labels=_lab,
                                        char_works=_cw,
                                        tiers=_tiers_all(),
                                        tier_colors=TAG_TIERS.get("colors", {}),
                                        tier_classes=TAG_TIERS.get("classes", {})))

        if path == "/api/redraw_active":
            snap = queue_snapshot()
            run_jid = ""
            for jid, j in REDRAW_JOBS.items():
                if j.get("status") in ("running", "starting"):
                    run_jid = jid
                    snap.update({"job": jid, "status": j["status"],
                                 "done": j.get("done", 0), "total": j.get("total", 0),
                                 "log": (j.get("log") or [])[-5:],
                                 "outdir": j.get("outdir", "")})
                    break
            if not run_jid:
                snap["job"] = ""
            return self._send(200, snap)

        if path == "/api/fav/get":
            rel = q.get("rel", [""])[0]
            _favs = set(load_favs())
            return self._send(200, {"fav": _norm_key(rel) in _favs or rel in _favs})

        if path == "/api/versions":
            rel = q.get("rel", [""])[0]
            grp = version_group(rel, build_parent_map_cached())
            ps = {p["rel"]: p for p in scan_photos()}
            grp = [_norm_key(r) for r in grp]
            items = [ps[r] for r in grp if r in ps and _visible_to_visitor(ps[r]["rel"], _ext)]
            keys = ("name", "rel", "dir", "char", "style", "tier", "action", "seed",
                    "steps", "size", "prompt", "eros", "tags", "fav", "mtime")
            out = [{k: p[k] for k in keys} for p in items]
            return self._send(200, {"root": grp[0] if grp else rel,
                                    "count": len(out),
                                    "items": out})

        if path == "/api/pools":
            return self._send(200, get_pools_cached())

        if path == "/api/char_filter":
            try:
                return self._send(200, char_filter_data())
            except Exception as e:
                return self._send(500, {"error": "%s: %s" % (type(e).__name__, e)})

        if path == "/api/roll/params":
            try:
                import pools.roll_params as _RP
                return self._send(200, {"params": _RP.describe(), "config": _RP.load_config()})
            except Exception as e:
                return self._send(500, {"error": "%s: %s" % (type(e).__name__, e)})

        if path == "/api/roll/status":
            cfg = load_json(ROLL_CONFIG_FILE, {})
            day = time.strftime("%Y%m%d")
            daydir = os.path.join(ROOT, day)
            try:
                today = len([f for f in os.listdir(daydir) if f.lower().endswith(".png")])
            except Exception:
                today = 0
            tail = ""
            try:
                with open(os.path.join(WORK, "launchd.out.log"), encoding="utf-8", errors="ignore") as f:
                    tail = "".join(f.readlines()[-8:])
            except Exception:
                pass
            try:
                import pools.roll_params as _RP
                _daily = _RP.cap_info()
            except Exception:
                _daily = {}
            return self._send(200, {"running": roll_is_running(), "config": cfg,
                                    "today": today, "log": tail, "day": day,
                                    "stopping": _STOPPING["v"],
                                    "frozen": _ROLL_FROZEN["v"],
                                    "drawing": _drawing(),
                                    "daily": _daily})

        if path == "/api/facets":
            _fc = load_facets_cache()
            if _fc is None:
                _fc = build_facets()
                save_facets_cache(_fc)
            return self._send(200, _fc)

        if path == "/api/albums":
            ps = [p for p in scan_photos() if _visible_to_visitor(p["rel"], _ext)]
            agg = defaultdict(lambda: [0, 0])
            for p in ps:
                agg[p["album"]][0] += 1
                agg[p["album"]][1] += p["bytes"]

            albums = [{"name": k, "count": v[0], "size": v[1]} for k, v in
                      sorted(agg.items(), key=lambda x: _album_sort_key(x[0]), reverse=True)]
            return self._send(200, {"albums": albums})

        if path == "/api/photos":
            ps = [p for p in scan_photos() if _visible_to_visitor(p["rel"], _ext)]
            def g(k):
                return q.get(k, [""])[0]
            chars_param = g("chars") or g("char")
            if chars_param:
                want = set(x for x in chars_param.split(",") if x)
                ps = [p for p in ps if p["char"] in want]
            if g("work"):
                ps = [p for p in ps if p.get("work") == g("work")]
            if g("style"):
                ps = [p for p in ps if p["style"] == g("style")]
            _tier_want = g("tier")
            if _tier_want == "takeoff":
                ps = [p for p in ps if p["tier"] in ("tease", "exposed", "sex")]
            elif _tier_want:
                ps = [p for p in ps if p["tier"] == _tier_want]
            _ratio_want = g("ratio")
            if _ratio_want:
                ps = [p for p in ps if p.get("ratio") == _ratio_want]

            if g("album"):
                ps = [p for p in ps if p["album"] == g("album")]
            if g("tag"):
                ps = [p for p in ps if g("tag") in p.get("tags", [])]
            if g("fav") == "1":
                ps = [p for p in ps if p.get("fav")]
            s = g("sort") or "new"
            if s == "old":
                ps = sorted(ps, key=lambda p: p["mtime"])
            elif s == "name":
                ps = sorted(ps, key=lambda p: p["name"])
            elif s == "size":
                ps = sorted(ps, key=lambda p: -p["bytes"])
            total = len(ps)
            try:
                limit = int(g("limit") or 0)
            except ValueError:
                limit = 0
            try:
                offset = int(g("offset") or 0)
            except ValueError:
                offset = 0
            if limit > 0:
                ps = ps[offset: offset + limit]
            out = [{k: p[k] for k in ("name", "rel", "dir", "char", "work", "style", "tier",
                                      "action", "seed", "steps", "size", "ratio", "prompt",
                                      "eros", "tags", "fav", "mtime", "vcount", "outfit",
                                      "style_cat") if k in p}
                   for p in ps]
            return self._send(200, {"total": total, "offset": offset, "limit": limit, "photos": out})

        if path == "/img":
            rel = q.get("p", [""])[0]
            want_thumb = q.get("t", [""])[0] == "thumb"
            full = os.path.normpath(os.path.join(ROOT, rel))
            if not full.startswith(ROOT + os.sep) or not os.path.isfile(full):
                return self._send(404, {"error": "not found"})
            # 只发图片：没有这一步的话 ?p=xxx/_日志.jsonl 会把日志甚至源码读走
            if not full.lower().endswith(IMG_EXT):
                return self._send(404, {"error": "not found"})
            if not _visible_to_visitor(rel, _ext):
                return self._send(404, {"error": "not found"})
            if want_thumb:
                tp = make_thumb(full, rel)
                if tp:
                    full = tp
            ctype = "image/jpeg" if full.lower().endswith((".jpg", ".jpeg")) else "image/png"
            try:
                _st = os.stat(full)
                _lm = int(_st.st_mtime)
                _etag = '"%x-%x"' % (_lm, _st.st_size)
            except OSError:
                _lm, _etag = 0, ""
            _immutable = bool(q.get("v", [""])[0])
            if _etag and self.headers.get("If-None-Match") == _etag:
                self.send_response(304)
                self.send_header("ETag", _etag)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            try:
                with open(full, "rb") as f:
                    data = f.read()
            except OSError:
                return self._send(500, {"error": "read fail"})
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            if _etag:
                self.send_header("ETag", _etag)
            if _lm:
                self.send_header("Last-Modified", self.date_time_string(_lm))
            if _immutable:
                self.send_header("Cache-Control", "public, max-age=31536000, immutable")
            else:
                self.send_header("Cache-Control", "public, max-age=86400")
            if q.get("dl", [""])[0] == "1":
                from urllib.parse import quote
                fn = os.path.basename(full)
                _q = quote(fn)
                self.send_header("Content-Disposition",
                                 f"attachment; filename=\"{_q}\"; filename*=UTF-8''{_q}")
            self.end_headers()
            self.wfile.write(data)
            return

        return self._send(404, {"error": "not found"})

if __name__ == "__main__":
    _restore_queue()
    try:
        threading.Timer(6.0, pump_redraw_queue).start()
    except Exception:
        pass
    print(f"相册服务启动 → http://0.0.0.0:{PORT}")
    threading.Thread(target=_facets_warmup, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
