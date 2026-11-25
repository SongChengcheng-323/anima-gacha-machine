import json
import os

W_FASHION = (1.00, 0.90, 0.60, 0.35)
W_TEASE = (0.00, 1.00, 0.80, 0.60)
W_EXPOSED = (0.00, 0.00, 1.00, 0.80)

SLOT_OF = {
    "upper": "upper",
    "lower": "lower",
    "under": "rear",
    "legwear": "leg_l",
    "shoes": "feet",
    "headwear": "head",
    "neckwear": "neck",
    "handwear": "hand_l",
    "set": "upper",
}

_ACC_RULES = (
    (("eyewear", "glasses", "sunglasses", "pince-nez"), "eyes"),
    (("earring", "ear cuff"), "ears"),
    (("bangle", "bracelet", "ring", "watch"), "hand_l"),
)
_ACC_FALLBACK = "neck"

GARMENT_SLOTS = ("upper", "lower", "rear")
DECO_SLOTS = ("head", "eyes", "ears", "neck", "hand_l", "waist")
GEAR_SLOTS = ("upper", "lower", "rear", "leg_l", "feet")
EXT_SLOTS = ("head", "eyes", "ears", "neck", "hand_l", "waist")

KEEP_SLOT_ALL = ("chest", "waist")
KEEP_SRC_PREFIX = ("set:",)

_STATE_KW = ("bare", "topless", "exposed", "visible", "nude")

SEX_ZERO_SLOTS = ()
SEX_ZERO_WORDS = ("watch",)

def _v3():
    try:
        from . import v3_pools as _V
    except Exception:
        import v3_pools as _V
    return _V

def _root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_CN_CACHE = {}

def _cn_map():
    if _CN_CACHE:
        return _CN_CACHE
    for name in ("taglib_cn.json",):
        p = os.path.join(_root(), name)
        try:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                _CN_CACHE.update(data)
                break
        except Exception:
            continue
    return _CN_CACHE

def _slot_of(vslot, word):
    if vslot == "accessory":
        low = (word or "").lower()
        for keys, slot in _ACC_RULES:
            if any(k in low for k in keys):
                return slot
        return _ACC_FALLBACK
    return SLOT_OF.get(vslot, vslot)

def _w_from_tiers(tiers, banned, slot, en):
    if "fashion" in tiers:
        f, t, e, s = W_FASHION
    elif "tease" in tiers:
        f, t, e, s = W_TEASE
    else:
        f, t, e, s = W_EXPOSED
    if banned or slot in SEX_ZERO_SLOTS:
        s = 0.00
    low = (en or "").lower()
    if any(k in low for k in SEX_ZERO_WORDS):
        s = 0.00
    return {"fashion": f, "tease": t, "exposed": e, "sex": s}

def collect():
    V = _v3()
    wardrobe = getattr(V, "WARDROBE", {}) or {}
    recs = {}
    for vslot, pool in wardrobe.items():
        for key in ("fashion", "tease", "exposed"):
            for en in pool.get(key) or ():
                slot = _slot_of(vslot, en)
                r = recs.setdefault((slot, en), {"tiers": set(), "sex_ban": False,
                                                 "srcs": []})
                r["tiers"].add(key)
                if vslot not in r["srcs"]:
                    r["srcs"].append(vslot)
    for vslot, pool in wardrobe.items():
        for ban in pool.get("sex_ban") or ():
            if ban == "*":
                for key in ("fashion", "tease", "exposed"):
                    for en in pool.get(key) or ():
                        if any(k in (en or "").lower() for k in _STATE_KW):
                            continue
                        r = recs.get((_slot_of(vslot, en), en))
                        if r:
                            r["sex_ban"] = True
            else:
                r = recs.get((_slot_of(vslot, ban), ban))
                if r:
                    r["sex_ban"] = True
    return recs

def _item(en, cn, w, slot, src):
    return {"en": en, "cn": cn, "w": w, "slot": slot, "src": src, "attr": False}

def build(legacy_gear=None, legacy_gear_ext=None):
    legacy_gear = legacy_gear or {}
    legacy_gear_ext = legacy_gear_ext or {}
    cn_map = _cn_map()
    recs = collect()

    new_gear = {s: [] for s in GEAR_SLOTS}
    new_ext = {s: [] for s in EXT_SLOTS}

    seen = set()
    for table, target in ((legacy_gear, new_gear), (legacy_gear_ext, new_ext)):
        for slot, items in table.items():
            for it in items:
                src = str(it.get("src") or "")
                keep = (slot in KEEP_SLOT_ALL or it.get("attr")
                        or any(src.startswith(p) for p in KEEP_SRC_PREFIX))
                if not keep:
                    continue
                target.setdefault(slot, []).append(dict(it))
                seen.add((slot, it["en"]))

    for (slot, en), r in recs.items():
        tgt = new_gear if slot in new_gear else new_ext
        if slot not in tgt:
            continue
        if (slot, en) in seen:
            continue
        seen.add((slot, en))
        src = "v3:" + "+".join(r["srcs"])
        tgt[slot].append(_item(en, cn_map.get(en, en),
                               _w_from_tiers(r["tiers"], r["sex_ban"], slot, en),
                               slot, src))
    return new_gear, new_ext

def stats(gear, ext):
    tiers = ("fashion", "tease", "exposed", "sex")
    out = {}
    for name, tbl in (("GEAR", gear), ("GEAR_EXT", ext)):
        out[name] = {}
        for slot, items in tbl.items():
            out[name][slot] = {t: sum(1 for it in items if it["w"][t] > 0) for t in tiers}
    return out

def selfcheck(verbose=False):
    gear, ext = build()
    problems = []
    if not gear.get("upper") or not gear.get("lower"):
        problems.append("upper/lower 生成失败 ✗")
    for slot in GEAR_SLOTS + tuple(s for s in EXT_SLOTS if s != "waist"):
        tbl = gear if slot in GEAR_SLOTS else ext
        items = tbl.get(slot) or []
        for t in ("fashion", "tease", "exposed", "sex"):
            n = sum(1 for it in items if it["w"][t] > 0)
            if n:
                continue
            if slot == "rear" and t == "fashion":
                continue
            if slot in SEX_ZERO_SLOTS and t == "sex":
                continue
            problems.append(f"[{t}] {slot} 无候选 ✗")
    if verbose:
        print("  v3→v2 服装投影自检：", "✓ 全过" if not problems else "✗ " + "；".join(problems[:6]))
        st = stats(gear, ext)
        tot = sum(len(v) for v in gear.values()) + sum(len(v) for v in ext.values())
        print(f"    条目 {tot} · 部位 {len(gear)+len(ext)}")
        for name in ("GEAR", "GEAR_EXT"):
            for slot, d in st[name].items():
                print(f"      {name:8s} {slot:8s} {d}")
    return problems

if __name__ == "__main__":
    import sys
    sys.exit(1 if selfcheck(verbose=True) else 0)
