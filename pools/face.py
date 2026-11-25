FACE_DAILY = {
    "expression": [
        "soft slight smile", "slight smile", "gentle shy smile", "bright natural smile",
        "calm confident expression", "serene expression", "poised expression",
        "quiet elegant expression", "thoughtful expression", "natural relaxed expression",
        "soft natural smile", "happy smile",
    ],
    "eyes":   ["", "", "relaxed brows"],
    "blush":  ["", "", "", "blushing"],
    "gaze":   ["looking at viewer", "looking away",
               "looking into the distance", "gazing into the distance",
               "gazing into the distance", "looking at something off-screen",
               "looking over her shoulder"],
}

RARE_GAZE_P = 0.12
GAZE_RARE = ("looking down", "head lowered, looking down")

FACE_FLIRTY = {
    "expression": [
        "teasing smile", "sultry smile", "seductive smile", "flustered but pleased",
        "shy smile", "biting her lower lip", "provocative look", "shy expression",
        "pleased expression",
    ],
    "eyes":   ["", "", "half-lidded eyes", "eyes slightly closed"],
    "blush":  ["blushing", "shy blush", "heavy blush", "flushed cheeks"],
    "gaze":   ["looking at viewer", "looking up at viewer",
               "seductive gaze", "looking away"],
}

FACE_SEX = {
    "expression": [
        "aroused expression", "lustful expression", "mouth open", "lips slightly parted",
        "moaning", "blissful expression", "sultry expression", "panting",
        "pleased expression",
        "lips parted just a little", "biting her lower lip", "mouth open gasping for air",
        "a knowing pleased smile", "a pleased satisfied look", "tongue out breathing hard",
        "a soft moan escaping her",
    ],
    "eyes":   ["eyes half closed", "half-lidded eyes", "eyes closed tight",
               "soft slightly hazy eyes", "half-lidded eyes unfocused",
               "eyes squeezed shut, brows drawn together", "tears at the corners of her eyes",
               "licking her lips eyes hungry", "watching him thoroughly pleased"],
    "blush":  ["deep blush", "heavy blush", "flushed face",
               "a faint blush", "flushed cheeks breathing hard",
               "a deep flush spreading to her chest"],
    "gaze":   ["looking at him", "looking at viewer", "looking up at viewer",
               "looking at him with half-smile", "a teasing look wanting more"],
}

FACE_POOLS = {"daily": FACE_DAILY, "flirty": FACE_FLIRTY, "sex": FACE_SEX}

FACE_BY_TIER = {
    "fashion": {"daily": 100, "flirty": 0, "sex": 0},
    "tease":   {"daily": 40, "flirty": 60, "sex": 0},
    "exposed": {"daily": 15, "flirty": 85, "sex": 0},
    "sex":     {"daily": 0, "flirty": 40, "sex": 60},
}

def pick_face(rng, tier, pose_text="", has_male=False, privacy=None, trait=None,
              sex_degree=None):
    try:
        from pools import roll_params as _RP
    except Exception:
        try:
            from . import roll_params as _RP
        except Exception:
            try:
                import roll_params as _RP
            except Exception:
                _RP = None
    if getattr(_RP, "USE_FACE_FROM_V3", True):
        try:
            from pools.face_from_v3 import pick_face_v3
        except Exception:
            try:
                from .face_from_v3 import pick_face_v3
            except Exception:
                from face_from_v3 import pick_face_v3
        return pick_face_v3(rng, tier, pose_text=pose_text, has_male=has_male,
                            privacy=privacy, trait=trait, sex_degree=sex_degree)

    w = FACE_BY_TIER.get(tier) or FACE_BY_TIER["tease"]
    keys = [k for k, v in w.items() if v > 0] or ["daily"]
    sub = rng.choices(keys, weights=[w[k] for k in keys])[0]
    pool = FACE_POOLS[sub]
    out = {}
    for dim, items in pool.items():
        if dim == "gaze" and rng.random() < RARE_GAZE_P:
            _rare = tuple(GAZE_RARE)
            if "head" in (pose_text or "").lower():
                _rare = tuple(x for x in _rare if "head" not in x.lower())
            out[dim] = rng.choice(_rare) if _rare else ""
        else:
            out[dim] = rng.choice(items)
    _e = (out.get("eyes") or "").lower()
    if (("closed" in _e) or ("shut" in _e)) and "half" not in _e:
        _g = (out.get("gaze") or "")
        _gl = _g.lower()
        _GAZE_W = ("looking", "gaze", "stare", "glance", "eye contact", "bedroom eyes")
        if any(w in _gl for w in _GAZE_W):
            _parts = [x.strip() for x in _g.split(",") if x.strip()]
            _keep = [x for x in _parts if not any(w in x.lower() for w in _GAZE_W)]
            out["gaze"] = ", ".join(_keep)
    return out, sub
