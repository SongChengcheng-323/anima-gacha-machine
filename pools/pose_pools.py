_OUTDOOR_BAN = ("OUTDOOR_CITY", "OUTDOOR_NATURE", "WATERFRONT", "JAPANESE_FESTIVAL")

POSES = {
    "fashion": {
        "cn": "时尚",
        "cats": {
            "站": {"w": 4.5, "items": [
                {"en": "standing",                     "use": (),          "scene_ban": ()},
                {"en": "standing with legs crossed",   "use": ("leg",),    "scene_ban": ()},
                {"en": "standing on one leg",          "use": ("leg",),    "scene_ban": ()},
                {"en": "contrapposto",                 "use": ("leg",),    "scene_ban": ()},
                {"en": "walking",                      "use": ("leg",),    "scene_ban": ()},
                {"en": "standing on tiptoes",          "use": ("leg", "feet"), "scene_ban": ()},
            ]},
            "坐": {"w": 3.0, "items": [
                {"en": "sitting",                      "use": ("leg",),    "scene_ban": ()},
                {"en": "sitting with legs crossed",    "use": ("leg",),    "scene_ban": ()},
                {"en": "sitting with knees up",        "use": ("leg",),    "scene_ban": ()},
                {"en": "sitting sideways",             "use": ("leg",),    "scene_ban": ()},
            ]},
            "蹲": {"w": 1.0, "items": [
                {"en": "crouching",                    "use": ("leg",),    "scene_ban": ()},
                {"en": "squatting",                    "use": ("leg",),    "scene_ban": ()},
            ]},
        },
        "head": [
            {"en": "",                                  "w": 6.2},
            {"en": "head tilted to one side",           "w": 1.0},
            {"en": "head slightly raised, chin up",     "w": 0.8},
            {"en": "looking away",                      "w": 0.8},
            {"en": "head lowered",                      "w": 0.6},
            {"en": "looking into the distance",         "w": 0.6},
        ],
        "hand": [
            {"en": "",                           "cn": "不做动作", "w": 3.0},
            {"en": "hand on hip",                "cn": "叉腰",     "w": 1.0, "body": ("站", "坐")},
            {"en": "hands in her pockets",       "cn": "手插口袋", "w": 0.9, "body": ("站", "坐", "蹲"), "needs": ("pockets",)},
            {"en": "arms crossed",               "cn": "抱臂",     "w": 0.8, "body": ("站", "坐", "躺")},
            {"en": "one hand touching her hair", "cn": "手撩头发", "w": 0.8, "body": ("站", "坐", "躺", "蹲")},
            {"en": "adjusting glasses",          "cn": "扶眼镜",   "w": 0.7, "body": ("站", "坐", "躺", "蹲"), "needs": ("glasses",)},
            {"en": "hand shading eyes",          "cn": "手遮太阳", "w": 0.6, "body": ("站", "坐", "蹲"), "force_scene": "outdoor"},
        ],
    },

    "tease": {
        "cn": "擦边",
        "cats": {
            "站": {"w": 2.2, "items": [
                {"en": "standing",                   "use": (),       "scene_ban": ()},
                {"en": "standing with legs crossed", "use": ("leg",), "scene_ban": ()},
                {"en": "standing on one leg",        "use": ("leg",), "scene_ban": ()},
                {"en": "contrapposto",               "use": ("leg",), "scene_ban": ()},
            ]},
            "坐": {"w": 3.0, "items": [
                {"en": "sitting",                    "use": ("leg",), "scene_ban": ()},
                {"en": "sitting with knees apart",   "use": ("leg",), "scene_ban": ()},
            ]},
            "跪": {"w": 3.2, "items": [
                {"en": "kneeling",                   "use": ("leg",), "scene_ban": ()},
                {"en": "kneeling with thighs apart", "use": ("leg",), "scene_ban": ()},
                {"en": "kneeling on one knee",       "use": ("leg",), "scene_ban": ()},
                {"en": "on knees, leaning back",     "use": ("leg",), "scene_ban": ()},
            ]},
            "躺": {"w": 2.5, "items": [
                {"en": "lying on her back",          "use": (),       "scene_ban": ()},
                {"en": "lying on her side",          "use": (),       "scene_ban": ()},
                {"en": "lying with legs up",         "use": ("leg",), "scene_ban": ()},
            ]},
            "趴": {"w": 1.6, "items": [
                {"en": "on all fours",               "use": ("leg",), "scene_ban": ()},
                {"en": "prone",                      "use": ("leg",), "scene_ban": ()},
                {"en": "lying prone, propped on her elbows", "use": ("leg", "hand"), "scene_ban": ()},
            ]},
            "蹲": {"w": 2.2, "items": [
                {"en": "crouching",                  "use": ("leg",), "scene_ban": ()},
                {"en": "squatting",                  "use": ("leg",), "scene_ban": ()},
            ]},
        },
        "head": [
            {"en": "",                                  "w": 4.0},
            {"en": "head tilted to one side",           "w": 1.0},
            {"en": "head tilted back",                  "w": 0.9},
            {"en": "looking up at viewer",              "w": 0.9},
            {"en": "looking down",                      "w": 0.7},
            {"en": "looking away",                      "w": 0.8},
        ],
        "hand": [
            {"en": "",                           "cn": "不做动作",     "w": 2.2},
            {"en": "hands covering her chest",   "cn": "双手遮胸",     "w": 1.0, "body": ("站", "坐", "跪", "蹲")},
            {"en": "one hand on her own chest",  "cn": "单手放在胸口", "w": 0.7, "body": ("站", "坐", "跪", "躺")},
            {"en": "one hand on her own thigh",  "cn": "手放在大腿上", "w": 0.9, "body": ("坐", "跪", "躺")},
            {"en": "hand on her own stomach",    "cn": "手放在肚子上", "w": 0.7, "body": ("坐", "跪", "躺")},
            {"en": "fingers loosely touching her lips", "cn": "手指碰嘴唇",   "w": 0.8, "body": ("站", "坐", "跪", "躺", "蹲")},
            {"en": "touching her own neck",      "cn": "摸自己的脖子", "w": 0.7, "body": ("站", "坐", "跪", "躺", "蹲")},
            {"en": "one hand touching her hair", "cn": "手撩头发",     "w": 0.8, "body": ("站", "坐", "跪", "躺", "蹲")},
            {"en": "hand on hip",                "cn": "叉腰",         "w": 0.6, "body": ("站", "坐")},
            {"en": "hand under clothes",         "cn": "手伸进衣服里", "w": 0.6, "body": ("站", "坐", "跪", "躺")},
            {"en": "clothes lift",               "cn": "掀起衣服",     "w": 0.5, "body": ("站", "坐", "跪", "躺"), "needs": ("garment",)},
            {"en": "pull aside",                 "cn": "拨开衣服",     "w": 0.6, "body": ("站", "坐", "跪", "躺")},
            {"en": "wardrobe malfunction",       "cn": "走光",         "w": 0.6, "body": ("站", "坐", "跪", "躺")},
            {"en": "strap slip",                 "cn": "肩带掉落",     "w": 0.6, "body": ("站", "坐", "跪", "躺"), "needs": ("straps",)},
            {"en": "adjusting glasses",          "cn": "扶眼镜",       "w": 0.5, "body": ("站", "坐", "跪", "躺", "蹲"), "needs": ("glasses",)},
        ],
        "extra": [
            {"en": "",                                  "w": 3.2},
            {"en": "upskirt",                           "w": 1.0, "needs": ("skirt",)},
            {"en": "panties visible",                   "w": 0.9, "needs": ("skirt",)},
            {"en": "skirt blowing up",                  "w": 0.5, "needs": ("skirt",)},
        ],
    },
    "exposed": {
        "cn": "暴露",
        "flat": [
            {"en": "standing",                              "cn": "站立",       "w": 1.0},
            {"en": "sitting with knees apart",              "cn": "分腿坐",     "w": 1.2},
            {"en": "kneeling",                              "cn": "跪坐",       "w": 1.2},
            {"en": "kneeling with thighs apart",            "cn": "跪分腿",     "w": 1.1},
            {"en": "lying on her back",                     "cn": "仰躺",       "w": 1.2},
            {"en": "lying on her side",                     "cn": "侧躺",       "w": 0.9},
            {"en": "lying on her back with legs up",        "cn": "躺抬腿",     "w": 1.2},
            {"en": "lying on her back, m legs",             "cn": "M 字开腿",   "w": 1.3},
            {"en": "lying on her back, legs spread wide",   "cn": "躺大张开",   "w": 1.2},
            {"en": "lying on her side, one leg raised",     "cn": "侧躺抬腿",   "w": 1.1},
            {"en": "on all fours",                          "cn": "四肢着地",   "w": 1.1},
            {"en": "prone",                                 "cn": "趴",         "w": 0.8},
            {"en": "on all fours, arching her back",        "cn": "塌腰翘臀",   "w": 1.3},
            {"en": "presenting",                            "cn": "撅臀",       "w": 1.3},
            {"en": "bent over",                             "cn": "弯腰",       "w": 1.1},
            {"en": "hips up",                               "cn": "抬臀",       "w": 1.0},
            {"en": "leaning back on her hands",             "cn": "撑手后仰",   "w": 1.1},
            {"en": "stretching",                            "cn": "伸懒腰",     "w": 1.0},
            {"en": "leaning forward",                       "cn": "前倾",       "w": 1.2},
            {"en": "spread legs, hands on knees",           "cn": "张腿按膝",   "w": 1.2},
            {"en": "kneeling, leaning back",                "cn": "跪后仰",     "w": 1.3},
            {"en": "sitting on her knees, hands on her thighs",
                                                            "cn": "跪坐手放腿", "w": 1.0},
            {"en": "arms up",                               "cn": "双臂上举",   "w": 1.1},
            {"en": "hands on her own breasts",              "cn": "双手托捏胸部", "w": 1.1},
            {"en": "pinching her own nipples",              "cn": "捏自己的乳头", "w": 1.1},
            {"en": "arms crossed covering her chest",       "cn": "抱胸遮住",   "w": 0.9},
            {"en": "hand covering her crotch",              "cn": "手遮私处",   "w": 0.9},
            {"en": "holding her own thighs with both hands", "cn": "双手抱大腿", "w": 1.2},
            {"en": "spreading her pussy",                   "cn": "扒开私处",   "w": 0.8},
            {"en": "spreading her pussy with both hands",   "cn": "双手扒开私处", "w": 1.0},
        ],
        "head": [
            {"en": "",                           "cn": "不做动作", "w": 3.5},
            {"en": "head tilted to one side",    "cn": "歪头",     "w": 0.8},
            {"en": "head tilted back",           "cn": "仰头",     "w": 0.8},
            {"en": "looking at viewer",          "cn": "看镜头",   "w": 0.7},
            {"en": "looking over her shoulder",  "cn": "回头看",   "w": 0.7},
        ],
    },
}

def _meets(needs, have):
    if not needs:
        return True
    return all(n in have for n in needs)

def pick_pose(rng, tier="fashion", have=()):
    spec = POSES.get(tier)
    if not spec:
        return "", "", (), ()
    cats, items = [], []
    for name, c in spec["cats"].items():
        cand = [i for i in c["items"] if _meets(i.get("needs"), have)]
        if not cand:
            continue
        cats.append((name, c["w"], cand))
    if not cats:
        return "", "", (), ()
    name = rng.choices([c[0] for c in cats], weights=[c[1] for c in cats], k=1)[0]
    pool = next(c[2] for c in cats if c[0] == name)
    it = rng.choice(pool)
    return it["en"], name, tuple(it.get("use") or ()), tuple(it.get("scene_ban") or ())

BONDAGE = {
    "tease": [
        ("rope bondage, bound wrists",                        1.0),
        ("rope bondage, arms bound behind back",              0.9),
        ("shibari, rope bondage",                             0.8),
        ("rope bondage, bound arms, rope around chest",       0.7),
        ("rope bondage, bound legs, bound wrists",            0.5),
        ("rope bondage, bound wrists, blindfold",             0.4),
    ],
    "exposed": [
        ("rope bondage, bound wrists",                        1.0),
        ("rope bondage, arms bound behind back",              0.9),
        ("shibari, rope bondage",                             0.9),
        ("rope bondage, bound arms, rope around chest",       0.8),
        ("rope bondage, hogtie",                              0.5),
        ("rope bondage, suspended, bound arms",               0.4),
    ],
}

BONDAGE_P = {"tease": 0.15, "exposed": 0.18}

def pick_bondage(rng, tier):
    pool = BONDAGE.get(tier) or []
    if not pool:
        return ""
    p = float(BONDAGE_P.get(tier, 0.0))
    if p <= 0 or rng.random() >= p:
        return ""
    return rng.choices([x[0] for x in pool], weights=[x[1] for x in pool], k=1)[0]

def pick_flat(rng, tier):
    flat = (POSES.get(tier) or {}).get("flat") or []
    if not flat:
        return "", {}
    it = rng.choices(flat, weights=[i["w"] for i in flat], k=1)[0]
    meta = {}
    if it.get("force_scene"):
        meta["scene_force"] = it["force_scene"]
    return it["en"], meta

def pick_part(rng, tier, part, have=(), body=None):
    if part == "hand" and "hand" in (have or ()):
        return "", {}
    spec = POSES.get(tier) or {}
    pool = [i for i in (spec.get(part) or []) if _meets(i.get("needs"), have)]
    if body:
        pool = [i for i in pool if (not i.get("body")) or (body in i["body"])]
    if not pool:
        return "", {}
    it = rng.choices(pool, weights=[i["w"] for i in pool], k=1)[0]
    meta = {}
    if it.get("force_scene"):
        meta["scene_force"] = it["force_scene"]
    return it["en"], meta

def selfcheck():
    bad = []
    for tier, spec in POSES.items():
        if not spec.get("cats") and not spec.get("flat"):
            bad.append(f"{tier}: 既没有大类也没有 flat 池")
        for name, c in (spec.get("cats") or {}).items():
            if not c["items"]:
                bad.append(f"{tier}.{name}: 空大类")
            if c["w"] <= 0:
                bad.append(f"{tier}.{name}: 权重非正")
            for i in c["items"]:
                if not i.get("en"):
                    bad.append(f"{tier}.{name}: 空姿态词")
    return bad
