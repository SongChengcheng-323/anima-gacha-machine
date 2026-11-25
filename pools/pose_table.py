import random

POSTURES = {
    "standing":                          dict(big="站", w=(1.0, 0.6, 0.5, 0.3), use=[], ok=("@all",)),
    "standing on one leg":               dict(big="站", w=(0.6, 0.6, 0.5, 0.3), use=["leg"], ok=("@all",)),
    "standing with legs crossed":       dict(big="站", w=(0.6, 0.7, 0.6, 0.3), use=["leg"], ok=("@all",)),
    "bent over":                         dict(big="站", w=(0.4, 0.5, 0.5, 0.6), use=["leg"], ok=("@all",)),
    "standing on tiptoes":               dict(big="站", w=(0.3, 0.6, 0.6, 0.3), use=["leg", "feet"], ok=("@all",)),
    "sitting":                           dict(big="坐", w=(1.0, 1.0, 1.0, 0.6), use=["leg"], ok=("@all",)),
    "sitting with knees together":       dict(big="坐", w=(0.9, 1.0, 0.8, 0.4), use=["leg"], ok=("@all",)),
    "sitting with knees apart":          dict(big="坐", w=(0.6, 0.8, 0.7, 0.5), use=["leg"], ok=("@all",)),
    "sitting elegantly, ankles crossed": dict(big="坐", w=(1.0, 0.9, 0.6, 0.3), use=["leg", "feet"], ok=("@all",)),
    "kneeling":                          dict(big="跪", w=(0.6, 1.0, 0.8, 0.8), use=["leg"], ok=("@all",)),
    "kneeling with thighs apart":        dict(big="跪", w=(0.4, 0.9, 0.8, 0.8), use=["leg"], ok=("@all",)),
    "seiza":                             dict(big="跪", w=(0.8, 0.9, 0.5, 0.5), use=["leg", "feet"], ok=("@all",)),
    "wariza":                            dict(big="跪", w=(0.5, 0.9, 0.6, 0.6), use=["leg", "feet"], ok=("@all",)),
    "kneeling on one knee":              dict(big="跪", w=(0.6, 0.8, 0.7, 0.6), use=["leg"], ok=("@all",)),
    "on all fours":                      dict(big="趴", w=(0.3, 0.5, 0.5, 0.9), use=["leg"],
                                              ok=("手.撑地", "头.@all", "脚.翘脚", "脚.冲镜头", "脚.趾部")),
    "crawling":                          dict(big="趴", w=(0.3, 0.4, 0.5, 0.8), use=["leg"],
                                              ok=("手.撑地", "头.@all", "脚.翘脚", "脚.冲镜头", "脚.趾部")),
    "prone":                             dict(big="趴", w=(0.4, 0.6, 0.5, 0.8), use=["leg"],
                                              ok=("手.撑地", "头.@all", "脚.翘脚", "脚.冲镜头", "脚.趾部")),
    "lying prone, propped on her elbows": dict(big="趴", w=(0.3, 0.5, 0.5, 0.7), use=["leg"],
                                                  ok=("手.撑地", "头.@all", "脚.翘脚", "脚.冲镜头", "脚.趾部")),
    "lying on her back":                 dict(big="躺", w=(0.6, 0.9, 1.0, 1.0), use=[],
                                              ok=("@all", "脚.@no_stand")),
    "lying on her side":                 dict(big="躺", w=(0.6, 0.9, 1.0, 1.0), use=[],
                                              ok=("@all", "脚.@no_stand")),
    "lying with legs up":                dict(big="躺", w=(0.4, 0.7, 0.9, 1.0), use=["leg"],
                                              ok=("头.@all", "手.@all", "脚.@no_stand")),
    "leaning back":                      dict(big="倚", w=(0.8, 1.0, 0.8, 0.6), use=[], ok=("@all",)),
    "leaning forward":                   dict(big="倚", w=(0.6, 1.0, 0.9, 0.8), use=[], ok=("@all",)),
    "leaning on her elbows":             dict(big="倚", w=(0.5, 0.9, 0.9, 0.9), use=[],
                                              ok=("手.撑地", "头.@all", "脚.@no_stand")),
    "reclining":                         dict(big="倚", w=(0.8, 1.0, 1.0, 0.9), use=[], ok=("@all",)),
}

ACTIONS = {
    "头": {
        "抬头": ["head slightly raised, chin up"],
        "低头": [],
        "仰头": ["head tilted back", "head leaning back", "head resting back"],
        "侧头": ["head tilted to one side", "head turned to the side"],
        "枕手": [],
    },
    "手": {
        "撑地": ["both hands down, supporting her weight", "hands supporting her weight",
                 "one hand down, the other reaching back"],
        "举臂": ["both arms raised above her head", "one arm raised above her head",
                 "one arm raised high above her head, the other bent behind her head",
                 "arms stretched upward, elbows up", "one arm lifted with her elbow up",
                 "reaching upward, both arms extended above her", "arms up, back slightly arched"],
        "放身": ["one hand on her own chest", "one hand on her own thigh", "one hand resting on her thigh",
                 "hand resting on her own hip", "hand touching her own cheek",
                 "fingers loosely touching her lips",
                 "chin resting on her hand"],
        "背后": ["hands behind her back"],
        "遮胸": ["hands covering her chest", "one hand covering her chest",
                 "hands covering between her legs",
                 "hands on her lap"],
        "拉衣": ["hand pulling at her clothing", "hands pulling at her collar", "hand holding her skirt hem",
                 "one hand tugging her neckline", "pulling at her collar", "lifting her skirt",
                 "pulling down her top strap", "hand slipping under her top", "unbuttoning her shirt",
                 "tugging her neckline lower"],
        "时尚": ["hands relaxed at her sides",
                 "one hand resting on her waist", "one hand adjusting her hair"],
        "插兜": ["hands in her pockets"],
        "脱袜": [],
    },
    "腿": {
        "并拢": ["legs together, knees touching", "knees together", "kneeling, legs together"],
        "分开": ["legs slightly apart", "legs apart, relaxed", "kneeling with thighs apart",
                 "knees apart, back arched", "legs apart, weight on all fours"],
        "交叉": ["one leg crossed over the other"],
        "抬起": ["one knee raised", "one leg bent, knee raised", "knees drawn up toward her chest",
                 "legs folded under her", "legs stretched out to the side"],
    },
    "脚": {
        "裸足": ["barefoot, toes pointed, high arch visible", "toes relaxed, soft soles",
                 "ankles crossed"],
        "翘脚": ["one foot lifted, toes curled"],
        "冲镜头": ["feet toward the camera, soles visible",
                   "foot sole toward the camera"],
        "趾部": ["curling toes",
                 "spread toes"],

    },
}

CAT_W = {
    ("手", "时尚"): (1.0, 0.1, 0.1, 0.1),
    ("手", "遮胸"): (0.2, 1.0, 0.4, 0.2),
    ("手", "拉衣"): (0.1, 1.0, 0.6, 0.4),
    ("手", "举臂"): (0.6, 0.4, 0.3, 0.1),
    ("手", "撑地"): (0.4, 0.5, 0.5, 0.4),
    ("手", "放身"): (0.8, 0.8, 0.7, 0.6),
    ("手", "背后"): (0.6, 0.7, 0.7, 0.5),
    ("手", "插兜"): (1.0, 0.3, 0.1, 0.1),
    ("头", "抬头"): (0.8, 0.7, 0.6, 0.5), ("头", "低头"): (0.8, 0.8, 0.7, 0.6),
    ("头", "仰头"): (0.6, 0.9, 0.9, 0.9), ("头", "侧头"): (0.8, 0.8, 0.8, 0.8),
    ("腿", "并拢"): (0.9, 0.9, 0.8, 0.6), ("腿", "分开"): (0.7, 0.9, 0.9, 0.9),
    ("腿", "交叉"): (0.8, 1.0, 0.7, 0.4), ("腿", "抬起"): (0.5, 0.8, 0.9, 1.0),
    ("脚", "裸足"): (0.9, 0.9, 0.9, 0.8), ("脚", "翘脚"): (0.4, 0.9, 1.0, 0.9),
    ("脚", "冲镜头"): (0.2, 0.7, 1.0, 0.9), ("脚", "趾部"): (0.3, 0.8, 0.9, 0.9),
    ("手", "脱袜"): (0.3, 0.6, 0.5, 0.9),
}

RESTRICT = {
    "kneeling, legs together":                    ("跪",),
    "kneeling with thighs apart":                 ("跪",),
    "legs folded under her":                      ("跪",),
    "legs apart, weight on all fours":            ("趴",),
    "knees apart, back arched":                   ("趴",),
    "knees drawn up toward her chest":            ("坐", "躺"),
    "legs stretched out to the side":             ("坐", "躺"),
    "one knee raised":                            ("坐", "躺", "倚"),
    "one leg bent, knee raised":                  ("坐", "躺", "倚"),
    "one leg crossed over the other":             ("坐",),
    "both hands down, supporting her weight":     ("趴",),
    "hands supporting her weight":                ("趴", "跪"),
    "one hand down, the other reaching back":     ("趴",),
    "arms up, back slightly arched":              ("趴", "躺", "倚"),
    "hands behind her back":                      ("站", "坐", "跪"),
    "hands on her lap":                        ("坐",),
    "hand holding her skirt hem":                 ("站", "坐", "跪", "倚"),
    "lifting her skirt":                          ("站", "坐", "跪", "倚"),
    "hand slipping under her top":                 ("站", "坐", "跪", "躺", "倚"),
    "one hand resting on her waist":               ("站", "坐", "倚"),
    "hands in her pockets":                        ("站",),
    "one hand resting on her thigh":               ("坐", "躺", "倚"),
    "one hand on her own thigh":                   ("坐", "躺", "倚"),
    "chin resting on her hand":                    ("站", "坐", "跪", "倚"),
    "reaching up to a shelf":                      ("坐", "跪", "躺", "趴"),
    "foot sole toward the camera":                 ("坐", "躺", "跪", "倚"),
    "pulling off her sock":                        ("坐", "躺", "跪", "站", "倚"),
    "one foot lifted, toes curled":                ("坐", "躺", "跪", "趴"),
    "feet toward the camera, soles visible":       ("坐", "躺", "趴", "跪"),
    "toes relaxed, soft soles":                    ("坐", "躺", "趴", "跪"),
    "barefoot, toes pointed, high arch visible":   ("坐", "躺", "趴", "跪"),
    "ankles crossed":                   ("坐", "躺", "跪", "趴"),
    "head resting back":                           ("躺", "倚", "坐", "跪"),
    "head leaning back":                           ("躺", "倚", "坐", "跪"),
}

FEEL_SOFT = {
    ("leaning back", "头", "低头"): 0.15,
    ("leaning forward", "头", "仰头"): 0.15,
    ("standing on tiptoes", "手", "背后"): 0.3,
}
NEEDS_FEET = {"pulling off her sock", "curling toes", "spread toes",
              "foot sole toward the camera", "one foot lifted, toes curled",
              "feet toward the camera, soles visible"}

PART_KEY = {"头": "head", "手": "hand", "腿": "leg", "脚": "feet"}
TIERS = ("fashion", "tease", "exposed", "sex")

FACING_TO_CAMERA = {
    "front":        ("from front",),
    "threequarter": ("from the side",),
    "side":         ("from the side",),
    "back":         ("from behind",),
}

FURNITURE_SCENES = ("bed", "on bed", "sofa", "couch", "chair", "stool", "desk",
                    "school desk", "lounger", "seat", "window seat", "car seat")
STANDING_LIKE = ("standing", "standing on one leg", "standing with legs crossed",
                 "bent over", "standing on tiptoes", "kneeling", "kneeling with thighs apart",
                 "seiza", "wariza", "kneeling on one knee")

OUTDOOR_NO_PRONE = ("on all fours", "crawling", "prone",
                    "lying prone with elbows on the ground",
                    "lying prone, propped on her elbows")
OUTDOOR_SIT_NEEDS = ("chair", "stool", "lounger", "seat", "log", "stone", "rock",
                     "fence", "wooden bucket", "towel", "stone steps")

_HORIZ = ("from front", "from the side", "from behind")
_FACING_WANT = {"front": "from front", "threequarter": "from front",
                "side": "from the side", "back": "from behind"}

def camera_conflict(facing_words, camera):
    if camera not in _HORIZ:
        return False
    low = [w.lower() for w in (facing_words or ())]
    for f, want in _FACING_WANT.items():
        hit = any(f in w or (f == "front" and "front view" in w) for w in low)
        if f == "back":
            hit = hit or any(("facing away" in w or "back turned" in w) for w in low)
        if hit:
            return camera != want
    return False

NO_OUTDOOR_BIG = frozenset(("跪", "趴", "躺"))
_NO_OUTDOOR_KW = ("kneel", "seiza", "wariza", "prone", "all fours", "crawl",
                  "lying", "on her back", "on her side")

PUBLIC_NO_LIE = frozenset(("躺", "趴"))

TIGHT_SPACES = frozenset({"car interior", "photo booth", "water tank"})
TIGHT_OK_BIG = frozenset({"坐", "倚", "跪"})

def pose_scene_ok(pose, scene, place):
    _big_t = (POSTURES.get(pose) or {}).get("big", "")
    if scene in TIGHT_SPACES and _big_t not in TIGHT_OK_BIG:
        return False
    if scene in FURNITURE_SCENES and pose in STANDING_LIKE:
        return False
    _big0 = (POSTURES.get(pose) or {}).get("big", "")
    if _big0 in PUBLIC_NO_LIE:
        try:
            from . import scene_pool as _SCP
        except Exception:
            try:
                import scene_pool as _SCP
            except Exception:
                _SCP = None
        if _SCP is not None and scene in getattr(_SCP, "PUBLIC_SCENES", ()):
            return False
    if place == "outdoor":
        _big = (POSTURES.get(pose) or {}).get("big", "")
        if _big in NO_OUTDOOR_BIG:
            return False
        if any(k in pose.lower() for k in _NO_OUTDOOR_KW):
            return False
        if pose in OUTDOOR_NO_PRONE:
            return False
        if pose.startswith("sitting") and scene not in OUTDOOR_SIT_NEEDS:
            return False
    return True

PLAY_POSE = {
    "missionary":        "lying on her back",
    "doggystyle":        "on all fours",
    "cowgirl":           "sitting with knees apart",
    "reverse_cowgirl":   "sitting",
    "squatting_cowgirl": "sitting with knees apart",
    "mating_press":      "lying on her back",
    "spooning":          "lying on her side",
    "standing_wall":     "standing",
    "anal":              "on all fours",
    "fellatio":    "kneeling",
    "cunnilingus": "lying on her back",
    "handjob":     "sitting",
    "paizuri":     "sitting",
    "footjob":     "sitting",
    "fingering":   "lying on her back",
    "masturbation": "lying on her back",
    "toy":         "lying on her back",
    "lick_ass":    "on all fours",
    "suck_nipple": "sitting",
    "lick_nipple": "sitting",
    "kiss":        "sitting",
    "tonguekiss":  "sitting",
    "self_pinch":  "sitting",
}

_bad = {k: v for k, v in PLAY_POSE.items() if v not in POSTURES}
assert not _bad, "PLAY_POSE 里有不存在的姿态：%r" % _bad

def pose_of_play(play):
    return PLAY_POSE.get(play or "", "")

try:
    from pools import roll_params as _RP
except Exception:
    import roll_params as _RP

if getattr(_RP, "USE_POSE_ACTIONS_FROM_V3", False):
    try:
        from pools import pose_actions_from_v3 as _PAV3
    except Exception:
        import pose_actions_from_v3 as _PAV3
    ACTIONS_LEGACY = ACTIONS
    RESTRICT_LEGACY = RESTRICT
    CAT_W_LEGACY = CAT_W
    _a, _r = _PAV3.apply()
    N_POSE_ACTIONS_V3 = len(_r)
