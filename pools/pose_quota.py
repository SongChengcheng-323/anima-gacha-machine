import random

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
try:
    from pools.pose_table import (POSTURES, ACTIONS, CAT_W, RESTRICT, FEEL_SOFT,
                                  NEEDS_FEET, PART_KEY, TIERS,
                                  camera_conflict, pose_scene_ok, pose_of_play,
                                  FACING_TO_CAMERA, FURNITURE_SCENES)
except Exception:
    import pose_table as _pt
    POSTURES, ACTIONS, CAT_W = _pt.POSTURES, _pt.ACTIONS, _pt.CAT_W
    RESTRICT, FEEL_SOFT, NEEDS_FEET = _pt.RESTRICT, _pt.FEEL_SOFT, _pt.NEEDS_FEET
    PART_KEY, TIERS = _pt.PART_KEY, _pt.TIERS
    camera_conflict, pose_scene_ok = _pt.camera_conflict, _pt.pose_scene_ok
    pose_of_play = _pt.pose_of_play
try:
    from pools import fashion as FA
except Exception:
    import fashion as FA

def cat_allowed(pose, part, cat):
    ok = POSTURES[pose]["ok"]
    if "@all" in ok and part != "脚":
        return True
    if part == "脚":
        if "脚.@no_stand" in ok and cat in ("裸足", "翘脚", "冲镜头", "趾部", "脱袜"):
            return True
        if ("脚." + cat) in ok:
            return True
        return False
    return ("%s.%s" % (part, cat)) in ok

def pick_posture(rng, tier):
    ks = [k for k, v in POSTURES.items() if v["w"][TIERS.index(tier)] > 0]
    ws = [POSTURES[k]["w"][TIERS.index(tier)] for k in ks]
    k = rng.choices(ks, weights=ws, k=1)[0]
    return k, POSTURES[k]["big"]

def pick_actions(rng, tier, pose, max_per_part=1, allow_skirt=True, shoes_on=False):
    used = set(POSTURES[pose]["use"])
    out = {}
    for part in ("头", "手", "腿", "脚"):
        if part == "脚" and shoes_on:
            continue
        if PART_KEY[part] in used:
            continue
        big = POSTURES[pose]["big"]
        cats, cands = [], {}
        for c in ACTIONS[part]:
            words = [w for w in ACTIONS[part][c]
                     if big in RESTRICT.get(w, ("站", "坐", "跪", "趴", "躺", "倚"))
                     and (allow_skirt or "skirt" not in w.lower())]
            if words and cat_allowed(pose, part, c):
                cats.append(c)
                cands[c] = words
        if not cats:
            continue
        ws = [CAT_W.get((part, c), (1.0, 1.0, 1.0, 1.0))[TIERS.index(tier)] for c in cats]
        if sum(ws) <= 0:
            continue
        for i, c in enumerate(cats):
            f = FEEL_SOFT.get((pose, part, c))
            if f is not None:
                ws[i] *= f
        c = rng.choices(cats, weights=ws, k=1)[0]
        pool = [w for w in cands[c]
                if not (w in NEEDS_FEET and "feet" in POSTURES[pose]["use"])]
        if not pool:
            continue
        out[part] = [rng.choice(pool)]
    return out

USE_POSE_V2 = True
TIER_OK = ("fashion", "tease", "exposed")

def draw_pose(rng, tier, fashion_tail=None, allow_skirt=True, shoes_on=False,
              has_bag=True):
    pose, _big = pick_posture(rng, tier)
    if tier not in TIER_OK:
        raise ValueError("档位 %r 不走姿势层（层1 定稿 ✓ 性爱档跳过 ✓）" % (tier,))
    if fashion_tail is not None:
        _P = POSTURES.get(pose) or {}
        _used = set(_P.get("use") or ())
        _big = _P.get("big") or ""
        _allbig = ("站", "坐", "跪", "趴", "躺", "倚")
        _tail = []
        for _i, _part in enumerate(("头", "手", "腿")):
            if _i >= len(fashion_tail) or not fashion_tail[_i]:
                continue
            _pk = PART_KEY.get(_part)
            if _pk and _pk in _used:
                continue
            _cands = [w for w in fashion_tail[_i]
                      if _big in (RESTRICT.get(w) or _allbig)
                      and w.lower() not in (pose or "").lower()]
            if not has_bag:
                _cands = [w for w in _cands if "bag" not in w.lower()]
            if _cands:
                _wmap = getattr(FA, "FASHION_HAND_W", {}) if _part == "手" else {}
                _wt = [_wmap.get(w, 1.0) for w in _cands]
                _tail.append(rng.choices(_cands, weights=_wt, k=1)[0])
        if not allow_skirt:
            _tail = [w for w in _tail if "skirt" not in w.lower()]
        return pose, _tail
    acts = pick_actions(rng, tier, pose, allow_skirt=allow_skirt, shoes_on=shoes_on)
    tail = []
    for part in ("头", "手", "腿", "脚"):
        tail.extend(acts.get(part, []))
    return pose, tail

def selfcheck(verbose=False):
    bad = []
    ti = {t: i for i, t in enumerate(TIERS)}
    for k, v in POSTURES.items():
        if set(v) != {"big", "w", "use", "ok"}:
            bad.append("%s 字段不对" % k)
        if len(v["w"]) != 4 or sum(v["w"]) <= 0:
            bad.append("%s 权重不对" % k)
        if v["big"] not in ("站", "坐", "跪", "趴", "躺", "倚"):
            bad.append("%s 大类不对" % k)
    rng = random.Random(1)
    for _ in range(300):
        p, _b = pick_posture(rng, "tease")
        acts = pick_actions(rng, "tease", p)
        if p in ("on all fours", "crawling", "prone",
                "lying prone with elbows on the ground",
                "lying prone, propped on her elbows"):
            if "手" in acts and acts["手"][0] in ACTIONS["手"]["举臂"]:
                bad.append("趴着抽到了举臂 ✗")
            if "腿" in acts:
                bad.append("趴着抽到了腿的动作 ✗（下半身被遮 ✓）")
        for part in ("头", "手", "腿", "脚"):
            if part in acts and len(acts[part]) > 1:
                bad.append("同一部位抽了多个动作 ✗")
            for w in acts.get(part, []):
                big = POSTURES[p]["big"]
                if big not in RESTRICT.get(w, ("站", "坐", "跪", "趴", "躺", "倚")):
                    bad.append("姿态 %s（%s）抽到了 %r ✗" % (p, big, w))
    return bad

if __name__ == "__main__":
    import sys
    b = selfcheck()
    print("pose_quota 自检：%s" % ("✓ 通过" if not b else "✗ " + "；".join(b[:6])))
    rng = random.Random(7)
    for tier in TIERS:
        p, big = pick_posture(rng, tier)
        print("  %-8s 姿态[%s] %-36s + %s" % (tier, big, p, pick_actions(rng, tier, p)))
    sys.exit(0 if not b else 1)
