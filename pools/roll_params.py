import io
import time
import json
import os
import random as _random
import random
from datetime import datetime

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import paths as _P
HERE = _P.PROJECT_ROOT
WORK = _P.WORK
ROOT = _P.GALLERY_ROOT
CONFIG_FILE = _P.CONFIG_PATH
LOG_FILE = _P.LOG_PATH
OUT_ROOT = _P.OUT_ROOT

MODEL_FILE = os.environ.get("ROLL_MODEL") or "anima_turbo_v1.1_i8x.ckpt"

SIZES = [
    (1024, 1536, 55, 12, 6.0),
    (896,  1984, 15, 12, 6.0),
    (1536, 1024, 10, 12, 6.0),
    (1536, 1536, 20, 12, 6.0),
    (1024, 1536, 100, 12, 6.0),
]
_PROD_SIZES = [x for x in SIZES if int(x[2]) < 100]
if not _PROD_SIZES:
    _PROD_SIZES = list(SIZES[:1])
_ARCHIVE = next((x for x in SIZES if int(x[2]) >= 100), SIZES[-1])
SIZE_PREF = 0.60
SIZE_OTHER = 0.20
SIZE_MODE_OPTIONS = ('1024×1536 55% / 896×1984 15% / 1536×1024 10% / 1536×1536 20%（产线档 · 12 步）',
                     '1024×1536 55% / 896×1984 15% / 1536×1024 10% / 1536×1536 20%（产线档 · 12 步）',
                     '1024×1536 55% / 896×1984 15% / 1536×1024 10% / 1536×1536 20%（产线档 · 12 步）',
                     '🧪 珍藏档 1024×1536 / 12 步（单尺寸 100%）')
SAMPLER, SHIFT, CFG = 19, 6.0, 1.0
STOCHASTIC_GAMMA = 0.66
RESOLUTION_DEPENDENT_SHIFT = False

USE_GUI_API = True
GUI_API_URL = "http://127.0.0.1:7860"

USE_BODY_V3 = False
USE_SCENE_V3 = False
USE_PROP_V3 = False
USE_PROP = False
SEX_NAKED = True
AFTER_P = 0.1
AFTER_FREE_POSE = True

AFTER_MIN_PRIVACY = 7

USE_AMBIENCE = False
AFTER_ALLOW_SURFACE = True
USE_FACE_V3 = False
USE_WARDROBE_V3 = False
USE_STATUS_V3 = True
USE_STATUS_FROM_V3 = USE_STATUS_V3

USE_POSE_POOLS = True

USE_WARDROBE_FROM_V3 = True

USE_POSES_FROM_V3 = True
USE_POSE_ACTIONS_FROM_V3 = True

USE_SCENE_FROM_V3 = True
USE_FACE_FROM_V3 = True

LORA_WEIGHT = 1.0

SWEEP_GUI_DUPE = False
GUI_API_TIMEOUT = 900

LUCKY_SEEDS = [50, 99, 256, 377, 1000, 111, 323, 929, 1024, 2025]
LUCKY_RATIO = 0.0
BAN_SEEDS = {1, 128, 768}

TIERS = ("fashion", "tease", "exposed", "sex")

DEFAULT_CONFIG = {
    "tier_weights": {"fashion": 100, "tease": 0, "exposed": 0, "sex": 0},
    "size_weights": {"1024x1536": 55, "896x1984": 15, "1536x1024": 10, "1536x1536": 20},
    "size_idx": 1,
    "steps": 8,
    "seed_mode": "random",
    "seed_fixed": None,
    "equip_mode": False,
    "daily_cap": 100,
    "daily_cap_hard": 200,
}

def _cap_file():
    return _P.CAP_FILE

def cap_state():
    try:
        d = json.load(io.open(_cap_file(), encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}

def _write_cap_state(d):
    try:
        json.dump(d, io.open(_cap_file(), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return True
    except Exception:
        return False

def cap_override_on():
    st = cap_state()
    return st.get("date") == time.strftime("%Y%m%d") and bool(st.get("override"))

def set_cap_override(on=True):
    if not on:
        _write_cap_state({})
        return True
    cfg = load_config()
    try:
        cap = int(cfg.get("daily_cap") or 0)
    except (TypeError, ValueError):
        cap = 0
    try:
        hard = int(cfg.get("daily_cap_hard") or 0)
    except (TypeError, ValueError):
        hard = 0
    n = daily_count()
    if hard > 0 and n >= hard:
        return False
    if cap > 0 and n < cap:
        return False
    today = time.strftime("%Y%m%d")
    st = cap_state()
    st.update({"date": today, "override": True})
    _write_cap_state(st)
    return True

def daily_count():
    d = os.path.join(OUT_ROOT, time.strftime("%Y%m%d"))
    try:
        return len([f for f in os.listdir(d) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
    except Exception:
        return 0

def cap_info():
    cfg = load_config()
    try:
        cap = int(cfg.get("daily_cap") or 0)
    except Exception:
        cap = 0
    try:
        hard = int(cfg.get("daily_cap_hard") or 0)
    except Exception:
        hard = 0
    n = daily_count()
    hard_hit = bool(hard > 0 and n >= hard)
    ov = False if hard_hit else cap_override_on()
    hit = bool(cap > 0 and n >= cap and not ov and not hard_hit)
    st = cap_state()
    if cap > 0 and n >= cap and not ov and not hard_hit and (
            st.get("date") != time.strftime("%Y%m%d") or not st.get("hit")):
        st = {"date": time.strftime("%Y%m%d"), "hit": True, "n": n, "cap": cap}
        _write_cap_state(st)
    return {"cap": cap, "hard": hard, "n": n, "hit": hit, "hard_hit": hard_hit,
            "override": ov, "paused": bool(hit or hard_hit),
            "date": time.strftime("%Y%m%d")}

def cap_reached():
    return cap_info()["paused"]

def load_config():
    cfg = dict(DEFAULT_CONFIG)
    try:
        if os.path.exists(CONFIG_FILE):
            d = json.load(io.open(CONFIG_FILE, encoding="utf-8"))
            if isinstance(d, dict):
                for k, v in d.items():
                    if k in cfg:
                        cfg[k] = v
                if isinstance(cfg.get("tier_weights"), dict):
                    cfg["tier_weights"] = {t: float(cfg["tier_weights"].get(t, 25))
                                           for t in TIERS}
    except Exception:
        pass
    return cfg

def _write(cfg):
    io.open(CONFIG_FILE, "w", encoding="utf-8").write(
        json.dumps(cfg, ensure_ascii=False, indent=1))
    return cfg

def save_config(cfg):
    cur = load_config()
    for k in DEFAULT_CONFIG:
        if k in (cfg or {}):
            cur[k] = cfg[k]
    return _write(cur)

def describe(cfg=None):
    cfg = cfg or load_config()
    ws = cfg.get("tier_weights") or {}
    return {
        "daily_cap": cfg.get("daily_cap"),
        "daily_cap_hard": cfg.get("daily_cap_hard"),
        "size_weights": cfg.get("size_weights") or {},
        "tier_weights": ws,
        "size_mode": size_mode_text(cfg),
        "seed_mode": ("固定 %s" % cfg.get("seed_fixed") if str(cfg.get("seed_mode") or "").lower() == "fixed"
                      else "随机"),
        "steps_note": "横竖 8 步/Shift 6.0 · 1536 方 12 步/Shift 6.0 · 🧪 测试档 1024×1536 / 8 步",
    }

def _size_idx(cfg=None):
    try:
        i = int((cfg or load_config()).get("size_idx") or 1)
    except Exception:
        i = 1
    return i if i in (1, 2, 3, 4) else 1

def size_mode_text(cfg=None):
    pairs = []
    try:
        _sw = ((cfg or load_config()).get("size_weights") or {})
    except Exception:
        _sw = {}
    for x in _PROD_SIZES:
        k = "%dx%d" % (x[0], x[1])
        try:
            v = float(_sw.get(k, x[2]))
        except (TypeError, ValueError):
            v = float(x[2])
        if v > 0:
            pairs.append((k, v))
    if not pairs:
        return SIZE_MODE_OPTIONS[0]
    tot = sum(p[1] for p in pairs) or 1
    txt = " / ".join("%s %d%%" % (k.replace("x", "×"), round(v / tot * 100))
                     for k, v in pairs)
    return "%s（产线档）" % txt

def effective_size_weights():
    try:
        _sw = (load_config().get("size_weights") or {})
    except Exception:
        _sw = {}
    pairs = []
    for x in _PROD_SIZES:
        k = "%dx%d" % (x[0], x[1])
        try:
            v = float(_sw.get(k, x[2]))
        except (TypeError, ValueError):
            v = float(x[2])
        if v > 0:
            pairs.append((x, v))
    if not pairs:
        pairs = [(x, float(x[2])) for x in _PROD_SIZES]
    return pairs

def pick_size(rng, size_idx=1):
    try:
        idx = int(size_idx)
    except Exception:
        idx = 1
    if idx not in (1, 2, 3, 4):
        idx = 1
    if idx == 4:
        return _ARCHIVE[0], _ARCHIVE[1], _ARCHIVE[3], _ARCHIVE[4]
    _pairs = effective_size_weights()
    _w = [p[1] for p in _pairs]
    x = rng.choices([p[0] for p in _pairs], weights=_w, k=1)[0]
    return x[0], x[1], x[3], x[4]

def pick_seed(rng, cfg=None):
    cfg = cfg if isinstance(cfg, dict) else load_config()
    mode = str(cfg.get("seed_mode") or "").strip().lower()
    if mode == "fixed":
        try:
            s = int(cfg.get("seed_fixed"))
            if 1 <= s < 2_000_000_000:
                return s
        except Exception:
            pass
    elif mode == "":
        try:
            s = int(cfg.get("seed"))
            if 1 <= s < 2_000_000_000:
                return s
        except Exception:
            pass
    while True:
        s = rng.randint(1, 2_000_000_000)
        if s not in BAN_SEEDS:
            return s

def pick_tier(rng, weights=None):
    ws = weights or load_config().get("tier_weights") or {}
    names = [t for t in TIERS if float(ws.get(t, 0) or 0) > 0]
    if not names:
        names = list(TIERS)
        ws = {t: 25 for t in TIERS}
    return rng.choices(names, weights=[float(ws.get(t, 0) or 0) for t in names], k=1)[0]

def make_tag(stamp, character, tier, action, style, seed):
    try:
        from . import characters as _CH
    except Exception:
        try:
            import characters as _CH
        except Exception:
            _CH = None
    ch = (_CH.short_name(character) if _CH else
          (character or "unknown").split("_(")[0])
    return f"{stamp}_{ch}_{tier}_{action}_{style}_{seed}"

def day_dir(when=None):
    d = os.path.join(OUT_ROOT, (when or datetime.now()).strftime("%Y%m%d"))
    os.makedirs(d, exist_ok=True)
    return d

def next_job(rng=None, tier=None, character=None, cfg=None):
    rng = rng or random.Random()
    cfg = cfg or load_config()
    tier = tier or pick_tier(rng, cfg.get("tier_weights"))
    try:
        from pools import characters as _CH
    except Exception:
        try:
            import characters as _CH
        except Exception:
            _CH = None
    _lock = _CH.tier_lock_of(character) if (_CH and character) else ()
    if _lock and tier not in _lock:
        tier = rng.choice(list(_lock))
    w, h, steps, shift = pick_size(rng, _size_idx(cfg))
    return {
        "tier": tier,
        "character": character,
        "w": w, "h": h, "steps": steps, "shift": shift,
        "seed": pick_seed(rng, cfg),
        "sampler": SAMPLER, "cfg": CFG,
        "stamp": datetime.now().strftime("%H%M%S"),
        "outdir": day_dir(),
        "log_file": LOG_FILE,
    }

def selfcheck():
    bad = []
    if sum(x[2] for x in _PROD_SIZES) != 100:
        bad.append("产线尺寸权重和 ≠ 100（%s）" % [x[2] for x in _PROD_SIZES])
    try:
        _r = _random.Random(0)
        for _i in (1, 2, 3, 4):
            _w2, _h2, _st2, _sh2 = pick_size(_r, _i)
            if (_w2, _h2) not in [(a, b) for a, b, _c, _d, _e in SIZES]:
                bad.append("尺寸档 %s 抽出了不存在的尺寸 %sx%s ✗" % (_i, _w2, _h2))
    except Exception as _e:
        bad.append("尺寸档抽取报错（%s）✗ —— 检查权重与 SIZES 是否匹配" % _e)
    for w, h, _wt, st, sh in SIZES:
        if not (4 <= st <= 16):
            bad.append(f"步数越界: {w}x{h} steps={st}")
    if 1 in LUCKY_SEEDS or any(s in BAN_SEEDS for s in LUCKY_SEEDS):
        bad.append("幸运池里混进了禁用种子")
    rng = random.Random(7)
    for _ in range(200):
        t = pick_tier(rng)
        if t not in TIERS:
            bad.append("pick_tier 出了非法档位")
            break
        w, h, st, sh = pick_size(rng)
        if (w, h) not in [(a, b) for a, b, _c, _d, _e in SIZES]:
            bad.append("pick_size 出了非法尺寸")
            break
    rng2 = random.Random(11)
    _eff = effective_size_weights()
    _tot_w = sum(x[1] for x in _eff)
    _seen = {(x[0][0], x[0][1]): 0 for x in _eff}
    _N = 4000
    for _ in range(_N):
        w, h, _st, _sh = pick_size(rng2, 1)
        _seen[(w, h)] = _seen.get((w, h), 0) + 1
    for _row, _wt in _eff:
        _got = _seen[(_row[0], _row[1])] / _N
        _want = _wt / _tot_w
        if abs(_got - _want) > 0.03:
            bad.append("尺寸 %sx%s 实测 %.1f%% ≠ 配置 %.1f%%"
                       % (_row[0], _row[1], _got * 100, _want * 100))
    _aw, _ah, _ast, _ash = pick_size(random.Random(3), 4)
    if (_aw, _ah) != (_ARCHIVE[0], _ARCHIVE[1]):
        bad.append("珍藏档（size_idx=4）没走单尺寸表项")
    if pick_seed(random.Random(1), {"seed_mode": "fixed", "seed_fixed": 12345}) != 12345:
        bad.append("固定种子没生效")
    if pick_seed(random.Random(1), {"seed_mode": "fixed", "seed_fixed": None}) in BAN_SEEDS:
        bad.append("固定种子非法时没退回随机")
    print("roll_params 自检：%s" % ("通过" if not bad else "✗ " + "；".join(bad)))
    return not bad

if __name__ == "__main__":
    import sys
    ok = selfcheck()
    print("  配置:", json.dumps(describe(), ensure_ascii=False))
    j = next_job(random.Random(1))
    print("  样例任务:", json.dumps({k: v for k, v in j.items() if k != "outdir"},
                                    ensure_ascii=False))
    sys.exit(0 if ok else 1)
