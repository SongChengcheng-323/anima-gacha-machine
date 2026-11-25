BODY_POSES = [
    "standing",
    "sitting",
    "kneeling",
    "on all fours",
    "lying on her back",
    "lying on her side",
    "reclining",
    "leaning back",
]

BODY_RULES = {
    "on all fours": {
        "head": ["head lowered", "head turned to the side",
                 "head down, hair falling forward"],
        "hand": ["both hands down, supporting her weight", "hands supporting her weight",
                 "one hand down, the other reaching back"],
        "leg": ["knees together", "knees apart, back arched",
                "legs apart, weight on all fours"],
    },
    "lying on her back": {
        "head": ["head tilted to one side", "head turned to the side"],
        "hand": ["one hand on her own chest", "one hand resting on her thigh", "one arm raised above her head",
                 "hand touching her own cheek", "hand resting on her own hip", "fingers loosely touching her lips"],
        "leg": ["legs together, knees touching", "legs slightly apart", "knees drawn up toward her chest",
                "one knee raised", "legs stretched out to the side", "ankles crossed", "legs apart, relaxed"],
    },
    "lying on her side": {
        "head": ["head tilted to one side", "head turned to the side", "head tilted back"],
        "hand": ["one hand on her own chest", "one hand resting on her thigh",                  "hand resting on her own hip"],
        "leg": ["legs together, knees touching", "knees drawn up toward her chest", "one leg bent, knee raised",
                "ankles crossed", "legs apart, relaxed"],
    },
    "reclining": {
        "head": ["head tilted back", "head tilted to one side", "head tilted back", "head resting back"],
        "hand": ["one hand on her own chest", "one hand resting on her thigh", "one arm raised above her head",
                 "hand touching her own cheek", "fingers loosely touching her lips"],
        "leg": ["legs together, knees touching", "one leg crossed over the other", "legs slightly apart",
                "one knee raised", "legs stretched out to the side", "ankles crossed"],
    },
    "sitting": {
        "head": ["head tilted back", "head tilted to one side", "head lowered",
                 "head turned to the side", "chin resting on her hand"],
        "hand": ["one hand on her own chest", "one hand resting on her thigh", "hands behind her back",
                 "hand touching her own cheek", "one hand on her own thigh", "hand pulling at her clothing",
                 "fingers loosely touching her lips"],
        "leg": ["legs together, knees touching", "one leg crossed over the other", "legs slightly apart",
                "knees drawn up toward her chest", "one knee raised", "legs folded under her",
                "one leg bent, knee raised", "ankles crossed"],
    },
    "kneeling": {
        "head": ["head lowered", "head tilted back", "head tilted back",
                 "head turned to the side"],
        "hand": ["one hand on her own chest", "one hand resting on her thigh", "hands behind her back",
                 "hand touching her own cheek", "one hand on her own thigh", "hand pulling at her clothing"],
        "leg": ["kneeling, legs together", "kneeling with thighs apart", "one knee raised"],
    },
    "standing": {
        "head": ["head tilted back", "head tilted to one side", "head lowered",
                 "head turned to the side", "head tilted back"],
        "hand": ["one hand on her own chest", "one hand resting on her thigh", "hands behind her back",
                 "one arm raised above her head", "hand touching her own cheek", "one hand on her own thigh",
                 "hand pulling at her clothing"],
        "leg": ["legs together, knees touching", "one leg crossed over the other", "legs slightly apart",
                "one knee raised", "legs apart, relaxed", "ankles crossed"],
    },
    "leaning back": {
        "head": ["head leaning back", "head tilted back", "head tilted to one side",
                 "head lowered", "head tilted back"],
        "hand": ["one hand on her own chest", "hands behind her back", "one arm raised above her head",
                 "hand touching her own cheek", "hand pulling at her clothing"],
        "leg": ["legs together, knees touching", "one leg crossed over the other", "legs slightly apart",
                "one knee raised", "ankles crossed"],
    },
}

_LEGACY_HAND_SINGLE_1 = [
    "one hand resting on her hip",
    "one hand on her waist",
    "one hand holding her own arm",
    "one hand touching her collar",
    "one hand on the back of her head",

    "one hand on her chest",
    "one hand resting on her thigh",
            "hand adjusting her hair",
    "one hand supporting her weight",
]

HAND_BOTH = [
    "hands behind her back",
    "both hands on her thighs",
]

_LEGACY_HAND_SINGLE_2 = [
    "one hand on her own thigh",
    "one hand on her own chest",
    "one hand resting on her thigh",
    "one hand down, the other reaching back",
]

HAND_SINGLE = list(dict.fromkeys(_LEGACY_HAND_SINGLE_1 + _LEGACY_HAND_SINGLE_2))

HAND_OCCUPY_KW = (
    "crossed", "clasped", "folded across", "overlapping", "arms folded",
    "behind her back", "hands behind",
    "touching her face", "on her face", "on her chest", "on her breast",
    "on her thigh", "on her own thigh", "on her legs",
    "behind her head", "on the back of her head",
    "on her hip", "on her waist", "hands on hips", "hand on hip",
    "adjusting her", "touching her ear", "holding the hem",
    "in her pockets", "in her pocket",
    "pulled aside", "pulling at her collar", "pulling at her clothes",
    "skirt lifted", "lifting her skirt", "holding her skirt hem",
    "tugging her neckline", "tugging her neckline lower",
    "covering her chest", "covering between her legs", "hands on her lap",
    "pulling down her top strap", "slipping under her top", "unbuttoning",
    "holding her bag", "holding a bag", "carrying her bag",
    "hem lifted", "hand on her cheek", "touching her own cheek",
    "supporting her weight", "resting on a railing",
    "leaning on her elbows", "propped on her elbow", "elbows on",
    "her own arm",
    "brushing", "hair back", "tying her hair", "putting her hair up",
    "running her hands through", "playing with her hair",
    "reaching up",
)

HAND_TWO_KW = tuple(HAND_BOTH) + (
    "in her pockets", "in her pocket",
    "both hands", "her own arm",
    "hands behind", "arms folded", "hands on hips",
    "hands covering", "hands on her lap", "arms crossed",
    "reaching up",
    "leaning on her elbows",
    "propped on her elbows",
    "hands pulling at her collar",
    "hands supporting her weight",
    "both hands down, supporting her weight",
    "one hand down, the other reaching back",
    "hands on the sheets", "hands on the bed",
)

RAISE_POSES = ['both arms raised above her head', 'one arm raised high above her head, the other bent behind her head', 'arms stretched upward, elbows up', 'one arm lifted with her elbow up', 'reaching upward, both arms extended above her', 'arms up, back slightly arched']
POINT_POSES = ['one foot lifted, toes curled', 'barefoot, toes pointed, high arch visible', 'barefoot, standing on tiptoes', 'feet toward the camera, soles visible', 'ankles crossed', 'toes relaxed, soft soles']

for _b, _r in BODY_RULES.items():
    _r["hand"] = list(_r["hand"]) + list(RAISE_POSES)
    _r["leg"] = list(_r["leg"]) + list(POINT_POSES)

_LEG_WORDS = ("leg", "ankle", "knee", "thigh", "foot", "feet", "toes")

_LEG_PHRASES = ("ankles crossed", "legs crossed", "one leg crossed over the other",
                "legs together", "knees together",
                "knees touching", "legs apart", "thighs apart", "legs up",
                "straight legs", "long legs", "bent legs", "legs stretched",
                "wide stance", "crossed legs")

_YIELD_STATES = ("bra pulled aside", "bottoms pulled aside",
                 "panties pulled aside", "clothing pulled aside",
                 "top pulled up over her breasts", "skirt lifted", "chest area pulled aside")

PROP_CARRY_KW = ("handbag", "tote bag", "duffel", "carpet bag", "beaded bag",
                 "quilted bag", "satin pouch", "clutch", "satchel", "pouch",
                 "shopping bag", "paper bag", " bag")
PROP_CARRY_EXCLUDE = ("shoulder bag", "backpack", "crossbody", "sling bag",
                      "mini backpack", "sleeping bag", "body bag")

def is_carry_prop(word):
    low = (word or "").lower()
    if not low:
        return False
    if any(x in low for x in PROP_CARRY_EXCLUDE):
        return False
    return any(x in low for x in PROP_CARRY_KW)

def count_hands(text, base=0):
    n = base
    for piece in (text or "").split(","):
        low = piece.strip().lower()
        if not low:
            continue
        if any(p in low for p in _LEG_PHRASES):
            continue
        if any(y in low for y in _YIELD_STATES) and "hands" not in low:
            continue
        if any(t in low for t in HAND_TWO_KW):
            n += 2
            continue
        if any(t in low for t in HAND_SINGLE) or any(k in low for k in HAND_OCCUPY_KW):
            n += 1
            continue
        if False and is_carry_prop(low):
            n += 1
            continue
        if any(b in low for b in _LEG_WORDS):
            continue
    return n

def hands_of_word(w):
    return count_hands(w)

_LEGACY_BODY_POSES = list(BODY_POSES)
_LEGACY_BODY_RULES = BODY_RULES

def _poses_from_v3_on():
    try:
        from pools import roll_params as _RP
    except Exception:
        import roll_params as _RP
    return bool(getattr(_RP, "USE_POSES_FROM_V3", True))

if _poses_from_v3_on():
    try:
        from pools import poses_from_v3 as _PFV
    except Exception:
        import poses_from_v3 as _PFV
    BODY_POSES = list(_PFV.BODY_POSES)
    BODY_RULES = _PFV.BODY_RULES
