POSTURES = {
    "standing":            {"big": "站", "w": (1.0, 0.6, 0.5, 0.3), "ok": ("@all",)},
    "bent over":           {"big": "站", "w": (0.4, 0.5, 0.5, 0.6), "ok": ("@all",)},
    "sitting":             {"big": "坐", "w": (1.0, 1.0, 1.0, 0.6), "ok": ("@all",)},
    "sitting elegantly":   {"big": "坐", "w": (1.0, 0.9, 0.6, 0.3), "ok": ("@all",)},
    "kneeling":            {"big": "跪", "w": (0.6, 1.0, 0.8, 0.8), "ok": ("@all",)},
    "kneeling on one knee": {"big": "跪", "w": (0.6, 0.8, 0.7, 0.6), "ok": ("@all",)},
    "seiza":               {"big": "跪", "w": (0.8, 0.9, 0.5, 0.5), "ok": ("@all",)},
    "wariza":              {"big": "跪", "w": (0.5, 0.9, 0.6, 0.6), "ok": ("@all",)},
    "on all fours":        {"big": "趴", "w": (0.3, 0.5, 0.5, 0.9),
                            "ok": ("手.撑地", "头.@all", "脚.翘脚", "脚.趾部")},
    "crawling":            {"big": "趴", "w": (0.3, 0.4, 0.5, 0.8),
                            "ok": ("手.撑地", "头.@all", "脚.翘脚", "脚.趾部")},
    "prone":               {"big": "趴", "w": (0.4, 0.6, 0.5, 0.8),
                            "ok": ("手.撑地", "头.@all", "脚.翘脚", "脚.趾部")},
    "lying on her back":   {"big": "躺", "w": (0.6, 0.9, 1.0, 1.0),
                            "ok": ("@all", "脚.@no_stand")},
    "lying on her side":   {"big": "躺", "w": (0.6, 0.9, 1.0, 1.0),
                            "ok": ("@all", "脚.@no_stand")},
    "leaning back":        {"big": "倚", "w": (0.8, 1.0, 0.8, 0.6), "ok": ("@all",)},
    "leaning forward":     {"big": "倚", "w": (0.6, 1.0, 0.9, 0.8), "ok": ("@all",)},
    "reclining":           {"big": "倚", "w": (0.8, 1.0, 1.0, 0.9), "ok": ("@all",)},
}

POSTURE_SPLIT = {
    "standing on one leg":              ("standing",   "腿.单腿"),
    "standing with legs crossed":       ("standing",   "腿.交叉"),
    "standing on tiptoes":              ("standing",   "脚.踮脚"),
    "sitting with knees together":      ("sitting",    "腿.并拢"),
    "sitting with knees apart":         ("sitting",    "腿.分开"),
    "sitting elegantly, ankles crossed": ("sitting elegantly", "腿.交叉"),
    "kneeling with thighs apart":       ("kneeling",   "腿.分开"),
    "lying with legs up":               ("lying on her back", "腿.抬起"),
    "lying prone, propped on her elbows": ("prone",    "手.撑地"),
    "leaning on her elbows":            ("reclining",  "手.撑地"),
}

HANDS = {
    "撑地": ["both hands down, supporting her weight", "hands supporting her weight"],
    "举臂": ["both arms raised above her head", "one arm raised above her head",
             "arms up, back slightly arched", "both arms stretched upward"],
    "放身": ["one hand on her own chest", "one hand resting on her thigh",
             "hand resting on her own hip", "hand touching her own cheek"],
    "背后": ["hands behind her back"],
    "遮胸": ["hands covering her chest", "one hand covering her chest",
             "hands covering between her legs"],
    "自然": ["hands relaxed at her sides", "one hand adjusting her hair"],
    "插兜": ["hands in her pockets"],
    "托腮": ["chin resting on her hand"],
    "整理": ["adjusting her clothes"],
}

HAND_ONE = ("one hand", "one arm", "hand ", "fingers ")
HAND_TWO = ("hands ", "both hands", "both arms", "arms up", "arms stretched",
            "elbows up", "reaching")

HEADS = {
    "抬头": ["head slightly raised, chin up"],
    "仰头": ["head tilted back", "head leaning back", "head resting back"],
    "侧头": ["head tilted to one side", "head turned to the side"],
    "低头": ["head lowered"],
}

HEAD_W = {"抬头": 1.0, "仰头": 1.0, "侧头": 1.0, "低头": 0.0}

LEGS = {
    "并拢": ["legs together, knees touching", "knees together"],
    "分开": ["legs slightly apart", "knees apart", "thighs apart"],
    "交叉": ["one leg crossed over the other", "ankles crossed"],
    "抬起": ["one knee raised", "knees drawn up toward her chest",
             "legs stretched out to the side"],
    "单腿": ["standing on one leg", "weight on one leg"],
}

FEET = {
    "踮脚": ["standing on tiptoes", "on tiptoes"],
    "翘脚": ["one foot lifted, toes curled"],
    "冲镜头": ["feet toward the camera, soles visible", "foot sole toward the camera"],
    "趾部": ["curling toes", "spread toes", "toes pointed", "toes relaxed"],
}

FEET_STAND = {"踮脚"}

EXCLUSIVE = [
    (("腿", "单腿"), ("脚", "踮脚")),
]

NEED = {
    ("手", "插兜"):   {"standing", "sitting", "sitting elegantly", "leaning back", "leaning forward"},
    ("腿", "单腿"):   {"standing", "bent over"},
    ("腿", "抬起"):   {"lying on her back", "lying on her side", "sitting", "reclining", "seiza", "wariza"},
    ("手", "撑地"):   {"on all fours", "crawling", "prone", "reclining"},
    ("手", "托腮"):   {"standing", "sitting", "sitting elegantly", "kneeling",
                      "seiza", "wariza", "reclining", "leaning back", "leaning forward"},
    ("脚", "踮脚"):   {"standing", "bent over"},
    ("脚", "冲镜头"): {"lying on her back", "lying on her side", "reclining",
                      "leaning back", "sitting", "sitting elegantly"},
}

def wearing_shoes(ctx):
    eq = ((ctx or {}).get("meta") or {}).get("equip") or {}
    ft = (eq.get("feet") or "").lower()
    return bool(ft.strip()) and "barefoot" not in ft

def compose(rng, tier, posture=None, shoes_on=False):
    tier_i = {"fashion": 0, "tease": 1, "exposed": 2, "sex": 3}[tier]
    if posture is None:
        names, weights = [], []
        for p, d in POSTURES.items():
            w = d["w"][tier_i]
            if w > 0:
                names.append(p)
                weights.append(w)
        posture = rng.choices(names, weights)[0]

    allow = _ok_set(posture)
    picked = []
    for part, table in (("手", HANDS), ("头", HEADS), ("腿", LEGS), ("脚", FEET)):
        if part == "脚" and shoes_on:
            continue
        cats = [c for (p, c) in allow if p == part]
        cats = [c for c in cats
                if posture in NEED.get((part, c), {posture})]
        if part == "头":
            cats = [c for c in cats if HEAD_W.get(c, 1.0) > 0]
        if not cats:
            continue
        cat = rng.choice(cats)
        words = table[cat]
        picked.append((part, cat, rng.choice(words)))
    have = {(p, c) for p, c, _ in picked}
    for a, b in EXCLUSIVE:
        if a in have and b in have:
            picked = [x for x in picked if (x[0], x[1]) != b]
    return posture, picked

def compose_text(rng, tier, posture=None, shoes_on=False):
    posture, picked = compose(rng, tier, posture, shoes_on)
    return ", ".join([posture] + [w for _p, _c, w in picked])

def compose_pair(rng, tier, posture=None, shoes_on=False):
    return compose_text(rng, tier, posture, shoes_on), []

def _ok_set(posture):
    allow = set()
    for o in POSTURES[posture]["ok"]:
        if o == "@all":
            allow |= {("手", c) for c in HANDS} | {("头", c) for c in HEADS}
            allow |= {("腿", c) for c in LEGS} | {("脚", c) for c in FEET}
        elif o == "脚.@no_stand":
            allow |= {("脚", c) for c in FEET if c not in FEET_STAND}
        elif o.startswith("头.@all"):
            allow |= {("头", c) for c in HEADS}
        elif "." in o:
            p, c = o.split(".", 1)
            if p == "手" and c in HANDS:
                allow.add((p, c))
            elif p == "头" and c in HEADS:
                allow.add((p, c))
            elif p == "腿" and c in LEGS:
                allow.add((p, c))
            elif p == "脚" and c in FEET:
                allow.add((p, c))
    return allow

def _selfcheck():
    import re
    HAND = re.compile(r"\b(hand|hands|palm|palms|finger|fingers|arm|arms|elbow|elbows|wrist|fist)\b", re.I)
    HEAD = re.compile(r"\b(head|chin|forehead|cheek|temples?)\b", re.I)
    LEG = re.compile(r"\b(leg|legs|knee|knees|thigh|thighs|ankles?|shin|calf|calves)\b", re.I)
    FOOT = re.compile(r"\b(foot|feet|toe|toes|soles?)\b", re.I)
    SCENE = re.compile(r"\b(bed|sofa|couch|chair|stool|floor|wall|table|desk)\b", re.I)
    errs = []
    _OK_HAND = ("above her head", "own cheek", "on her own cheek")

    def _hits(pat, s):
        for m in pat.finditer(s):
            if any(k in s.lower() for k in _OK_HAND):
                continue
            return True
        return False

    for p in POSTURES:
        if HAND.search(p): errs.append(f"体位带手: {p}")
        if HEAD.search(p): errs.append(f"体位带头: {p}")
        if FOOT.search(p): errs.append(f"体位带脚: {p}")
        if SCENE.search(p): errs.append(f"体位带家具: {p}")
    for cat, ws in HANDS.items():
        for w in ws:
            if cat == "托腮":
                continue
            if _hits(HEAD, w): errs.append(f"手池带头: [{cat}] {w}")
            if FOOT.search(w): errs.append(f"手池带脚: [{cat}] {w}")
            if "barefoot" in w.lower(): errs.append(f"手池带穿鞋状态: {w}")
    for cat, ws in HEADS.items():
        for w in ws:
            if HAND.search(w) and cat != "托腮":
                errs.append(f"头池带手（非托腮）: [{cat}] {w}")
            if FOOT.search(w): errs.append(f"头池带脚: {w}")
    for cat, ws in FEET.items():
        for w in ws:
            if "barefoot" in w.lower(): errs.append(f"脚池带穿鞋状态: {w}")
            if HAND.search(w): errs.append(f"脚池带手: {w}")
    return errs

if __name__ == "__main__":
    e = _selfcheck()
    n_pos = len(POSTURES)
    n_hand = sum(len(v) for v in HANDS.values())
    n_head = sum(len(v) for v in HEADS.values())
    n_leg = sum(len(v) for v in LEGS.values())
    n_foot = sum(len(v) for v in FEET.values())
    print(f"体位 {n_pos} / 手 {n_hand} / 头 {n_head} / 腿 {n_leg} / 脚 {n_foot}"
          f"  合计 {n_pos+n_hand+n_head+n_leg+n_foot}")
    if e:
        print(f"\n✗ 越界 {len(e)} 处：")
        for x in e: print("   ", x)
    else:
        print("✓ 自检通过：没有任何一个池子带别的维度的词")
