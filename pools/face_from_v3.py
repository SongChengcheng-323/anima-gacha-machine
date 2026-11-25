from __future__ import annotations

try:
    from pools import v3_pools as V3
except Exception:
    try:
        from . import v3_pools as V3
    except Exception:
        import v3_pools as V3

DIMS = ("expression", "mouth", "eyes", "gaze")

SKIP_GAZE = True

_SMILE_KEYS = ("smile", "laugh", "grin", "smirk")
_EYES_NON_SEX = ("eyes_open", "eyes_half")

def _cats_of(dim, allowed=None):
    cs = [c for c in V3.FACE_MERGED if V3.DIM_OF.get(c) == dim]
    if allowed is not None:
        cs = [c for c in cs if c in allowed]
    return cs

def _pick(rng, tier, dim, cats, ban_extra=(), wtab=None):
    ban = (tuple(V3.FACE_DIM_BAN.get(tier, {}).get(dim, ()))
           + tuple(V3.FACE_BAN)
           + tuple(ban_extra))
    cands = []
    for c in cats:
        ws = [w for w in (V3.FACE_MERGED.get(c) or [])
              if not any(b in w.lower() for b in ban)]
        if ws:
            cands.append((c, ws))
    if not cands:
        return "", ""
    if wtab:
        weights = [max(1e-6, float(wtab.get(c, 1.0))) for c, _ in cands]
        c, ws = rng.choices(cands, weights=weights, k=1)[0]
    else:
        c, ws = rng.choice(cands)
    return c, rng.choice(ws)

def pick_face_v3(rng, tier, pose_text="", has_male=False, privacy=None, trait=None,
                 sex_degree=None):
    tier = tier if tier in V3.FACE_CAT_BY_TIER else "tease"

    if tier == "fashion":
        _f = rng.choice(V3.FASHION_FACE)
        return ({"expression": _f, "mouth": "", "eyes": "", "gaze": ""},
                {"expression": "fashion_single"})

    allowed = list(V3.FACE_CAT_BY_TIER.get(tier) or [])

    _wtab = {}
    if tier == "sex" and sex_degree is not None:
        try:
            try:
                from pools import scene_privacy as SPR
            except Exception:
                from . import scene_privacy as SPR
            _wtab = SPR.sex_degree_weights(trait, sex_degree)
        except Exception:
            _wtab = {}
    elif privacy is not None and tier != "fashion":
        try:
            try:
                from pools import scene_privacy as SPR
            except Exception:
                from . import scene_privacy as SPR
            _wtab = SPR.expr_weights(trait, privacy, rng=rng, tier=tier)
        except Exception:
            _wtab = {}

    out = {"expression": "", "mouth": "", "eyes": "", "gaze": ""}
    sub = {}

    _c, _w = _pick(rng, tier, "expression", _cats_of("expression", allowed), wtab=_wtab)
    out["expression"] = _w
    if _c:
        sub["expression"] = _c

    _smiling = bool(_w) and any(k in _w.lower() for k in _SMILE_KEYS)

    _eyes_allow = (V3.FACE_DIM_ALLOW.get(tier) or {}).get("eyes")
    if tier == "sex":
        _eye_cats = _cats_of("eyes")
    else:
        _eye_cats = _cats_of("eyes", _eyes_allow or _EYES_NON_SEX)
    if _smiling:
        _eye_cats = [c for c in _eye_cats if c != "eyes_closed"]
    _c, _w = _pick(rng, tier, "eyes", _eye_cats)
    out["eyes"] = _w
    if _c:
        sub["eyes"] = _c

    _c, _w = _pick(rng, tier, "mouth", _cats_of("mouth", allowed), wtab=_wtab)
    out["mouth"] = _w
    if _c:
        sub["mouth"] = _c

    if not SKIP_GAZE:
        _gaze_cats = _cats_of("gaze", ("gaze", "gaze_male") if has_male else ("gaze",))
        _c, _w = _pick(rng, tier, "gaze", _gaze_cats)
        out["gaze"] = _w
        if _c:
            sub["gaze"] = _c

    _e = out["eyes"].lower()
    if (("closed" in _e) or ("shut" in _e)) and "half" not in _e and out["gaze"]:
        _GW = ("looking", "gaze", "stare", "glance", "eye contact", "bedroom eyes")
        _keep = [x.strip() for x in out["gaze"].split(",") if x.strip()
                 and not any(g in x.lower() for g in _GW)]
        out["gaze"] = ", ".join(_keep)
        if not out["gaze"]:
            sub.pop("gaze", None)

    return out, sub

if __name__ == "__main__":
    import random
    r = random.Random(1)
    for _t in ("fashion", "tease", "exposed", "sex"):
        for _i in range(3):
            d, s = pick_face_v3(r, _t)
            print("%-8s %s | %s" % (_t, d, s))
    print("--- has_male=True（sex）---")
    for _i in range(3):
        print(pick_face_v3(r, "sex", has_male=True))
