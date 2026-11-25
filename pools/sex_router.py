import random

PARTS = ["face", "mouth", "chest", "hand_l", "hand_r", "crotch", "rear",
         "foot_l", "foot_r", "neck", "thigh", "armpit"]

UPPER_BODY = ["face", "mouth", "chest", "hand_l", "hand_r", "neck", "armpit"]
INSERT_LIBS = {"PIV", "anal", "toy_insert", "toy_anal", "cunnilingus"}
EXCLUSIVE_LIBS = {"fellatio", "paizuri", "footjob", "handjob", "toy_oral"}

def allowed_extra(main_lib):
    if main_lib in EXCLUSIVE_LIBS:
        return []
    return UPPER_BODY

QUOTA = {"penis": 1, "toy": 1, "mouth": 1, "tongue": 1, "hand": 2, "self": 1}

MOUTH_GROUP = {"mouth", "tongue"}

PART_TO_SLOT = {
    "face": "face", "mouth": "face", "chest": "chest",
    "hand_l": "hand_l", "hand_r": "hand_r", "crotch": "rear", "rear": "rear",
    "foot_l": "feet", "foot_r": "feet", "neck": "neck", "thigh": "leg_l",
    "armpit": "chest",
}

ROUTES = {
    ("mouth", "penis"):  {"lib": "fellatio", "tier": "sex",
                          "ph": ["fellatio", "one hand around the base", "tongue on it"]},
    ("mouth", "toy"):    {"lib": "toy_oral", "tier": "sex",
                          "ph": ["dildo in her mouth", "sucking a dildo"]},
    ("mouth", "mouth"):  {"lib": "kiss", "tier": "edge",
                          "ph": ["kiss", "mouth to mouth", "tongue kiss"]},
    ("mouth", "tongue"): {"lib": "tongue", "tier": "edge",
                          "ph": ["licking", "trailing her tongue along it"]},
    ("mouth", "hand"):   {"lib": "suck_fingers", "tier": "edge",
                          "ph": ["sucking his fingers", "fingers in her mouth"]},
    ("face", "penis"):   {"lib": "facial", "tier": "edge",
                          "ph": ["penis on her face", "face against it"]},
    ("face", "tongue"):  {"lib": "lick_face", "tier": "edge", "ph": ["licking her face"]},
    ("face", "hand"):    {"lib": "hold_face", "tier": "edge",
                          "ph": ["grabbing her face", "hand on her cheek"]},
    ("face", "mouth"):   {"lib": "kiss_face", "tier": "edge", "ph": ["kissing her cheek"]},
    ("chest", "penis"):  {"lib": "paizuri", "tier": "sex",
                          "ph": ["paizuri", "penis between her breasts", "breasts around it"]},
    ("chest", "mouth"):  {"lib": "suck_nipple", "tier": "sex",
                          "ph": ["sucking her nipple", "mouth on her breast"]},
    ("chest", "tongue"): {"lib": "lick_nipple", "tier": "sex",
                          "ph": ["tongue on her nipple", "licking her breast"]},
    ("chest", "hand"):   {"lib": "grope_breast", "tier": "edge",
                          "ph": ["grabbing her breast", "groping her breast", "hand on her breast",
                                 "pinching her nipple between his fingers"]},
    ("chest", "self"):   {"lib": "self_pinch", "tier": "edge",
                          "ph": ["her hand pinching her own nipple",
                                 "fingertips pinching her nipple",
                                 "pinching her own nipple"]},
    ("hand_l", "penis"): {"lib": "handjob", "tier": "sex",
                          "ph": ["handjob", "hand around it", "stroking it"]},
    ("hand_r", "penis"): {"lib": "handjob", "tier": "sex",
                          "ph": ["handjob", "hand around it", "stroking it"]},
    ("hand_l", "mouth"): {"lib": "kiss_hand", "tier": "edge", "ph": ["kissing her hand"]},
    ("hand_r", "mouth"): {"lib": "kiss_hand", "tier": "edge", "ph": ["kissing her hand"]},
    ("hand_l", "tongue"): {"lib": "lick_hand", "tier": "edge",
                           "ph": ["licking her hand", "tongue on her fingers"]},
    ("hand_r", "tongue"): {"lib": "lick_hand", "tier": "edge",
                           "ph": ["licking her hand", "tongue on her fingers"]},
    ("hand_l", "hand"):  {"lib": "hold_hands", "tier": "edge",
                          "ph": ["holding hands", "interlocked fingers"]},
    ("hand_r", "hand"):  {"lib": "hold_hands", "tier": "edge",
                          "ph": ["holding hands", "interlocked fingers"]},
    ("armpit", "tongue"): {"lib": "lick_armpit", "tier": "edge",
                           "ph": ["licking her armpit", "tongue on her armpit"]},
    ("armpit", "mouth"):  {"lib": "kiss_armpit", "tier": "edge",
                           "ph": ["kissing her armpit"]},
    ("crotch", "penis"): {"lib": "PIV", "tier": "sex", "ph": []},
    ("crotch", "toy"):   {"lib": "toy_insert", "tier": "sex",
                          "ph": ["dildo inserted", "toy inside her pussy"]},
    ("crotch", "mouth"): {"lib": "cunnilingus", "tier": "sex",
                          "ph": ["cunnilingus", "his face between her thighs"]},
    ("crotch", "tongue"): {"lib": "cunnilingus", "tier": "sex",
                           "ph": ["licking her pussy", "tongue on her clit"]},
    ("crotch", "hand"):  {"lib": "fingering", "tier": "sex",
                          "ph": ["grabbing her pussy", "fingering", "fingers inside her pussy"]},
    ("rear", "penis"):   {"lib": "anal", "tier": "sex",
                          "ph": ["anal", "penis in her ass", "anal sex"]},
    ("rear", "toy"):     {"lib": "toy_anal", "tier": "sex",
                          "ph": ["toy in her ass", "plug inserted"]},
    ("rear", "hand"):    {"lib": "spank", "tier": "edge",
                          "ph": ["grabbing her buttocks"]},
    ("rear", "tongue"):  {"lib": "lick_ass", "tier": "edge", "ph": ["licking her ass"]},
    ("foot_l", "penis"): {"lib": "footjob", "tier": "sex",
                          "ph": ["footjob", "her feet on it", "soles pressing on it"]},
    ("foot_r", "penis"): {"lib": "footjob", "tier": "sex",
                          "ph": ["footjob", "her feet on it", "toes curled around it"]},
    ("foot_l", "mouth"): {"lib": "suck_toes", "tier": "edge",
                          "ph": ["mouth on her foot", "sucking her toes"]},
    ("foot_r", "mouth"): {"lib": "suck_toes", "tier": "edge",
                          "ph": ["mouth on her foot", "sucking her toes"]},
    ("foot_l", "tongue"): {"lib": "lick_foot", "tier": "edge",
                           "ph": ["licking her foot", "tongue on her sole"]},
    ("foot_r", "tongue"): {"lib": "lick_foot", "tier": "edge",
                           "ph": ["licking her foot", "tongue on her sole"]},
    ("foot_l", "hand"):  {"lib": "touch_foot", "tier": "edge",
                          "ph": ["grabbing her foot", "holding her ankle"]},
    ("foot_r", "hand"):  {"lib": "touch_foot", "tier": "edge",
                          "ph": ["grabbing her foot", "holding her ankle"]},
    ("neck", "mouth"):   {"lib": "kiss_neck", "tier": "edge", "ph": ["kissing her neck"]},
    ("neck", "tongue"):  {"lib": "lick_neck", "tier": "edge", "ph": ["licking her neck"]},
    ("thigh", "hand"):   {"lib": "touch_thigh", "tier": "edge",
                          "ph": ["grabbing her thigh", "caressing her inner thigh"]},
    ("thigh", "mouth"):  {"lib": "kiss_thigh", "tier": "edge", "ph": ["kissing her thigh"]},
    ("thigh", "tongue"): {"lib": "lick_thigh", "tier": "edge",
                          "ph": ["licking her inner thigh"]},
}

PIV_POSITIONS = ["missionary", "doggystyle", "cowgirl", "reverse_cowgirl",
                 "spooning", "standing_wall", "squatting_cowgirl"]

POSITION_ALIASES = {
    "woman_on_top": "cowgirl",
    "face_to_face_cowgirl": "cowgirl",
}
INSERT_WEIGHTS = {"crotch": 62, "mouth": 14, "chest": 9, "foot_l": 7, "rear": 5, "hand_l": 3}

POSITION_PHRASES = {
    "missionary":     ["missionary position", "lying on her back",
                       "penis inserted into pussy", "visible penetration"],
    "doggystyle":     ["doggystyle", "on all fours", "from behind",
                       "penis inserted into pussy", "visible penetration"],
    "cowgirl":        ["cowgirl position", "sitting on top", "straddling",
                       "penis inserted into pussy", "visible penetration"],
    "reverse_cowgirl": ["reverse cowgirl", "sitting on top", "facing away from him",
                        "penis inserted into pussy"],
    "spooning":       ["spooning", "lying on her side", "penis inserted into pussy"],
    "standing_wall":  ["standing sex", "against the wall", "standing, leaning against the wall",
                       "penis inserted into pussy", "visible penetration"],
    "squatting_cowgirl": ["squatting cowgirl", "crouching on top", "squatting over him",
                          "penis inserted into pussy", "visible penetration"],
    "lotus_position":    ["lotus position", "sitting in his lap facing him", "legs wrapped around",
                          "penis inserted into pussy", "visible penetration"],
    "fellatio":       ["fellatio", "kneeling"],
    "paizuri":        ["paizuri", "kneeling, leaning forward"],
    "footjob":        ["footjob", "sitting on the floor, legs extended"],
    "cunnilingus":    ["cunnilingus", "lying on her back, legs apart"],
    "anal":           ["anal", "on all fours", "from behind"],
    "toy_insert":     ["lying on her back", "legs apart"],
    "toy_oral":       ["kneeling"],
    "toy_anal":       ["on all fours"],
}

REACTIONS_HAND = ["clutching the sheets", "gripping the sheets", "hands gripping his back",
                  "arms wrapped around him", "arms wrapped around his neck",
                  "hand covering her mouth", "clenching her fists"]
REACTIONS_LEG = ["toes curling", "feet arched with toes pointed", "legs wrapped around him",
                 "trembling legs", "knees pressed together", "legs spread wide"]
NEEDS_PARTNER = ("arms wrapped around him", "arms wrapped around his neck",
                 "hands gripping his back", "legs wrapped around him",
                 "sucking his fingers", "hand around it", "stroking it",
                 "one hand around the base")

PARTNER_ONLY_ROUTES = {("mouth", "hand"), ("crotch", "mouth"), ("crotch", "tongue"),
                       ("rear", "tongue")}

REACTION_HAND_BAN = {
    "cowgirl":         ["arms wrapped around him", "arms wrapped around his neck"],
    "reverse_cowgirl": ["arms wrapped around him", "arms wrapped around his neck"],
    "footjob":         ["hands gripping his back"],
    "paizuri":         ["hands gripping his back"],
    "doggystyle":      ["arms wrapped around his neck", "legs wrapped around him"],
    "anal":            ["arms wrapped around his neck"],
}

ORGAN_BY_POSITION = {
    "paizuri":  ["nipples visible"],
    "footjob":  ["nipples visible"],
    "handjob":  ["nipples visible"],
    "toy_oral": ["nipples visible"],
    "fellatio": ["nipples visible"],
}

REACTION_LEG_BAN = {
    "fellatio":        ["legs wrapped around him", "legs spread wide"],
    "toy_oral":        ["legs wrapped around him", "legs spread wide"],
    "paizuri":         ["legs wrapped around him"],
    "footjob":         ["legs wrapped around him"],
    "doggystyle":      ["legs wrapped around him"],
    "anal":            ["legs wrapped around him"],
    "toy_anal":        ["legs wrapped around him"],
    "reverse_cowgirl": ["legs wrapped around him"],
}
REACTIONS_FACE = ["parted lips", "heavy blush", "half-lidded eyes",
                  "biting her lower lip", "moaning",
                  "eyes squeezed shut frowning", "brows furrowed"]

ORGAN_ALWAYS = ["nipples visible", "pussy exposed"]
ORGAN_OVERRIDE = {
}

CUM_BY_PART = {
    "face":  ["facial", "cum on her face"],
    "mouth": ["cum in her mouth", "cum on her tongue"],
    "chest": ["cum on her breasts"],
    "crotch": ["cum inside her pussy", "creampie"],
    "hand_l": ["cum on her hand"],
    "hand_r": ["cum on her hand"],
    "foot_l": ["cum on her feet"],
    "foot_r": ["cum on her feet"],
    "rear": ["cum in her ass"],
}

SELFIE = ["holding a phone, taking a selfie", "phone in her hand, selfie angle"]

def _piv_weights(char):
    try:
        from pools.char_profile import position_weights
        return position_weights(char, PIV_POSITIONS)
    except Exception:
        return [1.0 for _ in PIV_POSITIONS]

def _route_boost(char, lib):
    try:
        from pools.char_profile import route_weight
        return route_weight(char, lib)
    except Exception:
        return 1.0

def _p_penis_bias(char):
    try:
        from pools.char_profile import p_penis
        return p_penis(char)
    except Exception:
        return 0.78

def plan(rng, want_penis=None, allow_mouth=True, char=None):
    slots = {}
    used = {"penis": 0, "toy": 0, "mouth": 0, "tongue": 0, "hand": 0, "self": 0}
    mouth_open = [True]

    def can(orn):
        if orn in MOUTH_GROUP:
            return mouth_open[0]
        return used[orn] < QUOTA[orn]

    def take(part, orn, r=rng):
        if not can(orn):
            return False
        route = ROUTES.get((part, orn))
        if not route:
            return False
        if part in slots:
            return False
        lib = route["lib"]
        ph = list(route["ph"])
        pos = None
        def _mix(pos_words, act_words):
            out = [pos_words[0]]
            rest = pos_words[1:]
            if rest:
                out.append(rng.choice(rest))
            if act_words:
                _a = [x for x in act_words if x not in out]
                if _a:
                    out.append(rng.choice(_a))
            return out

        _mixed = False
        if lib == "PIV":
            pos = rng.choices(PIV_POSITIONS, weights=_piv_weights(char), k=1)[0]
            ph = _mix(POSITION_PHRASES[pos], [])
            _mixed = True
        elif lib in POSITION_PHRASES:
            pos = lib
            ph = _mix(POSITION_PHRASES[lib], ph)
            _mixed = True
        if not _mixed:
            ph = [ph[0]] + ([] if len(ph) <= 2 else [rng.choice(ph[1:])])
        slots[part] = {"orn": orn, "lib": lib, "tier": route["tier"],
                       "ph": ph, "position": pos}
        if orn in MOUTH_GROUP:
            mouth_open[0] = False
        else:
            used[orn] += 1
        return True

    if want_penis is None:
        want_penis = rng.random() < _p_penis_bias(char)
    main_orn = "penis" if want_penis else "toy"
    parts = [p for p in INSERT_WEIGHTS if (p, main_orn) in ROUTES]
    w = [INSERT_WEIGHTS[p] * _route_boost(char, ROUTES[(p, main_orn)]["lib"]) for p in parts]
    while parts:
        p = rng.choices(parts, weights=w)[0]
        if take(p, main_orn):
            break
        i = parts.index(p)
        parts.pop(i); w.pop(i)

    edges = [("crotch", "hand"), ("mouth", "hand"),
             ("chest", "mouth"), ("chest", "tongue"), ("chest", "hand"),
             ("mouth", "hand"), ("neck", "hand"), ("neck", "mouth"), ("neck", "tongue"),
             ("face", "hand"), ("face", "tongue"), ("face", "mouth"),
             ("rear", "hand"), ("rear", "tongue"), ("thigh", "hand"), ("thigh", "tongue"),
             ("foot_l", "hand"), ("foot_r", "hand"),
             ("foot_l", "tongue"), ("foot_r", "tongue"),
             ("mouth", "mouth"),
             ("armpit", "tongue"), ("armpit", "mouth"), ("armpit", "hand")]
    _main_lib = next((v["lib"] for v in slots.values() if v["tier"] == "sex"), None)
    _allow = allowed_extra(_main_lib)
    edges = [(p, o) for (p, o) in edges if p in _allow]
    if _main_lib in ("paizuri", "footjob", "handjob", "toy_oral"):
        edges = [(p_, o_) for (p_, o_) in edges if o_ not in MOUTH_GROUP and o_ != "hand"]
    elif main_orn != "penis":
        edges = [(p_, o_) for (p_, o_) in edges if (p_, o_) not in PARTNER_ONLY_ROUTES]
    if not allow_mouth:
        edges = [(p, o) for (p, o) in edges if o not in MOUTH_GROUP and p != "mouth"]
    if rng.random() < 0.2:
        edges += [("hand_l", "hand"), ("hand_r", "hand")]
    _self_touch = False
    if (_main_lib not in EXCLUSIVE_LIBS and "chest" not in slots
            and rng.random() < 0.30):
        _self_touch = take("chest", "self")

    rng.shuffle(edges)
    _hand_first = sorted(edges, key=lambda e: 0 if e[1] == "hand" else 1)
    want_edge = 0 if _self_touch else (1 if _allow else 0)
    got_edge = 0
    for part, orn in _hand_first:
        if got_edge >= want_edge:
            break
        if take(part, orn):
            got_edge += 1

    if rng.random() < 0.12:
        BLK_SELFIE = rng.choice(SELFIE)
    else:
        BLK_SELFIE = None

    _penis_part = next((pp for pp, vv in slots.items() if vv["orn"] == "penis"), None)
    if _penis_part and _penis_part in CUM_BY_PART and rng.random() < 0.35:
        _c = rng.choice(CUM_BY_PART[_penis_part])
        if _c not in slots[_penis_part]["ph"]:
            slots[_penis_part]["ph"].append(_c)

    if not slots:
        for part, orn in edges:
            if take(part, orn):
                break
    if not any(v["tier"] == "sex" for v in slots.values()):
        for part in ("crotch", "mouth", "rear"):
            if take(part, main_orn):
                break

    reactions = {}
    _pos_key = next((v.get("position") for v in slots.values() if v.get("position")), None)
    _watch = _main_lib in ("handjob", "paizuri", "footjob", "fellatio", "toy_oral")
    _rh = REACTIONS_HAND
    if _watch:
        _rh = [x for x in REACTIONS_HAND if "covering her mouth" not in x]
    _hban = list(REACTION_HAND_BAN.get(_pos_key or "", REACTION_HAND_BAN.get(_main_lib, [])))
    if main_orn != "penis":
        _hban += ["arms wrapped around him", "arms wrapped around his neck",
                  "hands gripping his back"]
    _rh = [x for x in _rh if x not in _hban] or _rh
    if used["hand"] + (0 if mouth_open[0] else 0) < QUOTA["hand"] and rng.random() < 0.7:
        reactions["hand"] = rng.choice(_rh)
    _ban = list(REACTION_LEG_BAN.get(_pos_key or "", REACTION_LEG_BAN.get(_main_lib, [])))
    if main_orn != "penis":
        _ban += ["legs wrapped around him"]
    reactions["leg"] = rng.choice([x for x in REACTIONS_LEG if x not in _ban] or REACTIONS_LEG)
    reactions["face"] = rng.choice(REACTIONS_FACE)
    return slots, reactions, main_orn, BLK_SELFIE

def organs(position_key=None):
    if position_key in ORGAN_BY_POSITION:
        return list(ORGAN_BY_POSITION[position_key])
    return list(ORGAN_OVERRIDE.get(position_key, ORGAN_ALWAYS))
