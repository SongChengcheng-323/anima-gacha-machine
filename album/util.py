import hashlib
import json
import os
import time
from datetime import datetime

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import paths as _P
ROOT = _P.GALLERY_ROOT
WORK = _P.WORK
LOG = os.path.join(WORK, "_日志.jsonl")
OBSOLETE = {"自动抽卡"}
SKIP_DIRS = {"web_icons"}
SKIP_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "跳过目录.txt")
CHAR_FILE = _P.CHAR_FILE
TIER_FILE = _P.TIER_FILE
TIER_ALL = ("normal", "fashion", "tease", "exposed", "sex")

def load_tier_map():
    d = load_json(TIER_FILE, {})
    return {_norm_key(k): v for k, v in d.items()} if isinstance(d, dict) else {}

def save_tier_map(d):
    save_json(TIER_FILE, d)

def load_char_map():
    d = load_json(CHAR_FILE, {})
    return {_norm_key(k): v for k, v in d.items()} if isinstance(d, dict) else {}

def save_char_map(d):
    save_json(CHAR_FILE, d)

def load_skip_dirs():
    out = set(SKIP_DIRS)
    try:
        if os.path.isfile(SKIP_FILE):
            for line in open(SKIP_FILE, encoding="utf-8"):
                s = line.strip()
                if s and not s.startswith("#"):
                    out.add(s.strip("/"))
    except Exception:
        pass
    return out
PORT = int(os.environ.get("ALBUM_PORT", "8900"))
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")
TAG_FILE = _P.TAG_FILE
FAV_FILE = _P.FAV_FILE
THUMB_DIR = _P.THUMB_DIR
THUMB_W = 360
THUMB_Q = 72

def load_json(path, default):
    try:
        if os.path.exists(path):
            return json.load(open(path, encoding="utf-8"))
    except Exception:
        pass
    return default

def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)

def _norm(k):
    return k[len("自动抽卡/"):] if k.startswith("自动抽卡/") else k

_NAME_IDX = {"stamp": None, "map": {}}

def _name_index():
    try:
        stamp = os.path.getmtime(ROOT)
    except OSError:
        stamp = 0
    if _NAME_IDX["stamp"] == stamp and _NAME_IDX["map"]:
        return _NAME_IDX["map"]
    idx = {}
    for dp, dns, fns in os.walk(ROOT, followlinks=True):
        dns[:] = [d for d in dns if not d.startswith(".") and d not in SKIP_DIRS]
        for fn in fns:
            if fn.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                idx.setdefault(fn, os.path.relpath(os.path.join(dp, fn), ROOT))
    _NAME_IDX["map"] = idx
    _NAME_IDX["stamp"] = stamp
    return idx

def _norm_key(f):
    if not f or not isinstance(f, str):
        return f
    f = _norm(f)
    if os.path.exists(os.path.join(ROOT, f)):
        return f
    alt = os.path.join(ROOT, "自动抽卡", f)
    if os.path.exists(alt):
        return "自动抽卡/" + f
    real = _name_index().get(os.path.basename(f))
    if real:
        return real
    return f

def save_tags(tags):
    try:
        if not tags and os.path.exists(TAG_FILE):
            old = load_json(TAG_FILE, {})
            if old:
                save_json(TAG_FILE + ".safety", old)
    except Exception:
        pass
    save_json(TAG_FILE, tags)

def load_tags():
    d = load_json(TAG_FILE, {})
    return {_norm_key(k): v for k, v in d.items()} if isinstance(d, dict) else {}

def load_favs():
    d = load_json(FAV_FILE, [])
    if not isinstance(d, list):
        return []
    out = []
    for x in d:
        f = _norm(x)
        if f and not f.startswith("自动抽卡/") \
                and os.path.exists(os.path.join(ROOT, "自动抽卡", f)):
            f = "自动抽卡/" + f
        out.append(f)
    return out

def log_line(obj):
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        return True
    except Exception as e:
        print(f"[log_line] 写入失败: {type(e).__name__}: {e}", flush=True)
        return False

def make_thumb(full_path, rel):
    import hashlib
    try:
        os.makedirs(THUMB_DIR, exist_ok=True)
        key = hashlib.md5(rel.encode("utf-8")).hexdigest()
        out = os.path.join(THUMB_DIR, f"{key}.jpg")
        if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(full_path):
            return out
        from PIL import Image
        im = Image.open(full_path).convert("RGB")
        w, h = im.size
        if w > THUMB_W:
            im = im.resize((THUMB_W, int(h * THUMB_W / w)), Image.LANCZOS)
        tmp = out + ".tmp"
        im.save(tmp, "JPEG", quality=THUMB_Q, optimize=True)
        os.replace(tmp, out)
        return out
    except Exception:
        return None
