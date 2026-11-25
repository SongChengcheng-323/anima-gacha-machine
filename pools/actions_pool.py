ACTIONS = [
    {"en": "",                                         "hands": 0, "w": 1.0, "tiers": ("fashion", "tease")},
    {"en": "",                                         "hands": 0, "w": 1.0, "tiers": ("fashion", "tease")},

    {"en": "turning slightly",                        "hands": 0, "w": 1.0, "tiers": ("fashion", "tease")},
    {"en": "hands relaxed at her sides",              "hands": 0, "w": 1.0, "tiers": ("fashion", "tease")},

    {"en": "adjusting her hair",                      "hands": 1, "w": 0.25, "tiers": ("fashion", "tease")},
    {"en": "one hand adjusting her hair",             "hands": 1, "w": 0.25, "tiers": ("fashion", "tease")},
    {"en": "brushing hair back",                      "hands": 1, "w": 0.30, "tiers": ("fashion", "tease")},
    {"en": "tying her hair up",                       "hands": 1, "w": 0.30, "tiers": ("fashion", "tease")},
    {"en": "adjusting her earrings",                  "hands": 1, "w": 1.0, "tiers": ("fashion", "tease")},
    {"en": "adjusting her clothes",                   "hands": 1, "w": 1.0, "tiers": ("fashion", "tease")},
    {"en": "one hand resting on her waist",           "hands": 1, "w": 1.0, "tiers": ("fashion", "tease")},
    {"en": "one hand holding her bag",                "hands": 1, "w": 0.30, "tiers": ("fashion",)},
    {"en": "one hand on her own thigh",               "hands": 1, "w": 1.0, "tiers": ("fashion", "tease")},

    {"en": "hands behind her back",                   "hands": 2, "w": 1.0, "tiers": ("fashion", "tease", "exposed")},
    {"en": "hands in her pockets",                    "hands": 2, "w": 0.80, "tiers": ("fashion", "tease")},
    {"en": "both hands on her thighs",                "hands": 2, "w": 1.0, "tiers": ("fashion", "tease")},
    {"en": "reaching up to a shelf",                  "hands": 2, "w": 0.60, "tiers": ("fashion",),
     "body": ("站",)},
]

def pick(rng, budget=2, tier=None, body_big=None, hands_busy=False, has_bag=True):
    cand = []
    for a in ACTIONS:
        if a["hands"] > budget:
            continue
        if hands_busy and any(w in a["en"].lower() for w in
                              ("hand", "hands", "arm", "arms", "elbow", "palm")):
            continue
        if a.get("tiers") and tier not in a["tiers"]:
            continue
        if a.get("body") and body_big and body_big not in a["body"]:
            continue
        if not has_bag and "bag" in a["en"].lower():
            continue
        cand.append(a)
    if not cand:
        return "", 0
    ws = [a.get("w", 1.0) for a in cand]
    if sum(ws) <= 0:
        return "", 0
    a = rng.choices(cand, weights=ws, k=1)[0]
    return a["en"], a["hands"]

def hands_of(word):
    w = (word or "").strip()
    for a in ACTIONS:
        if a["en"] == w:
            return a["hands"]
    try:
        from . import poses as P
    except Exception:
        try:
            import poses as P
        except Exception:
            return 0
    low = w.lower()
    if not low:
        return 0
    if any(b in low for b in ("leg", "ankle", "knee", "thigh", "foot", "feet", "toes")):
        return 0
    two = tuple(getattr(P, "HAND_BOTH", ()) or ()) + (
        "in her pockets", "in her pocket", "both hands", "hands behind",
        "arms folded", "hands on hips")
    if any(k in low for k in two):
        return 2
    if any(k in low for k in getattr(P, "HAND_OCCUPY_KW", ())):
        return 1
    return 0

def audit():
    bad = []
    for a in ACTIONS:
        if a.get("hands") not in (0, 1, 2):
            bad.append(a)
    return bad
