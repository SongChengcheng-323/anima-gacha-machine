import re

META = {
    "id":      "sex_pool",
    "cn":      "性爱池",
    "kind":    "pool",
    "tier":    "sex",
    "parent":  None,
    "enabled": True,
    "desc":    "性爱级玩法与写法（CORE/ATTACH 保底结构 · 24 条路由覆盖）",
}

TIER = "sex"

SEX_ORGANS = ("penis", "crotch", "rear", "foot")

PENETRATION_MARKS = [
    "penis inserted into pussy",
    "visible penetration",
]

FAMILIES = {
    "on_top":   "女上位族 —— 女方在上，跨坐在男方身上（男方躺着或坐着）",
    "on_back":  "仰卧族 —— 女方仰躺，男方在其上方",
    "behind":   "后入族 —— 从背后进入",
    "side":     "侧卧族 —— 两人同向侧躺（⚠️ 也属背后进入，待约定是否并入）",
    "standing": "站立族 —— 两人站立完成",
}

SEX_POOL = {
    "cowgirl": {
        "parent": "position", "family": "on_top", "cn": "女上位", "canon": "cowgirl position",
        "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["cowgirl position",
                    "riding his cock", "riding",
                    "girl on top",
                    "she is riding his cock", "she straddles his lap"],
        "insert": [],
    },
    "reverse_cowgirl": {
        "parent": "position", "family": "on_top", "cn": "反向女上位", "canon": "reverse cowgirl",
        "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["reverse cowgirl", "reverse cowgirl position", "facing away from his body",
                    "riding his cock backwards", "riding him with her back turned"],
        "insert": [],
    },
    "squatting_cowgirl": {
        "parent": "position", "family": "on_top", "cn": "蹲坐女上位", "canon": "squatting over his cock",
        "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["squatting over his cock", "squatting on top of him",
                    "crouching on top", "girl squatting astride him"],
        "insert": [],
    },
    "missionary": {
        "parent": "position", "family": "on_back", "cn": "传教士", "canon": "missionary position",
        "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["missionary position",
                    "her legs on his shoulders", "legs pressed back"],
        "insert": [],
    },
    "mating_press": {
        "parent": "position", "family": "on_back", "cn": "压制", "canon": "mating press",
        "tier": "sex", "core": True, "exclusive": True, "off": True,
        "_legacy_aliases": ["mating press", "legs pushed back", "hips pressed together"],
        "insert": [],
    },
    "doggystyle": {
        "parent": "position", "family": "behind", "cn": "后入", "canon": "doggystyle",
        "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["doggystyle", "from behind",
                    "sex from behind",
                    "hips against her", "ass presented"],
        "insert": [],
    },
    "spooning": {
        "parent": "position", "family": "side", "cn": "侧卧", "canon": "spooning",
        "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["spooning", "spooning position",
                    "his body pressed against her back", "lying behind her"],
        "insert": [],
    },
    "standing_wall": {
        "parent": "position", "family": "standing", "cn": "站立", "canon": "standing sex",
        "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["standing sex", "against the wall",
                    "lifted against the wall"],
        "insert": [],
    },

    "fellatio": {
        "cn": "口交", "canon": "fellatio", "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["fellatio", "blowjob", "her mouth on his cock", "going down on his cock", "sucking off his cock",
                    "sucking his cock", "her mouth around his cock",
                    "her tongue on his cock", "tongue licking the tip of his cock", "licking his cock shaft",
                    "tongue running up the length of his cock", "tongue licking his cock from below",
                                        "penis resting on her face", "penis on her face", "her face against his cock",
                    "mouth open", "tongue out", "taking his cock in her mouth", "deepthroat", "deep throat",
                    "penis in her mouth", "cock between her lips"],
        "insert": ["cock in her mouth", "penis in her mouth"],
    },
    "cunnilingus": {
        "cn": "舔阴", "canon": "cunnilingus", "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["cunnilingus", "his face between her thighs", "his mouth between her legs",
                    "her pussy being licked", "his tongue on her pussy", "his tongue inside her pussy",
                    "licking her clit", "tongue on her clit", "tongue between her folds",
                    "licking her pussy"],
        "insert": ["his tongue inside her pussy"],
    },
    "handjob": {
        "cn": "手交", "canon": "handjob", "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["handjob", "jerking his cock off", "her hand around his cock",
                    "stroking his cock", "stroking his cock with her hand", "fingers wrapped around his cock shaft",
                    "pumping his cock with her hand", "rubbing his cock with her palm", "both hands on his cock",
                    "hand wrapped around the base of his cock"],
        "insert": ["hand wrapped around his penis"],
    },
    "paizuri": {
        "cn": "乳交", "canon": "paizuri", "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["paizuri", "titjob", "breasts around his cock", "breasts squeezing his cock",
                    "her breasts wrapped around his cock", "penis between her breasts",
                    "breasts pressed together around his cock", "nipples brushing his cock shaft"],
        "insert": ["cock between her breasts"],
    },
    "footjob": {
        "cn": "足交", "canon": "footjob", "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["footjob", "her feet on his cock", "soles pressing on his cock", "toes curled around his cock",
                    "both soles rubbing his cock", "toes teasing the tip of his cock", "feet wrapped around his cock",
                    "bare sole against his cock", "one foot stroking his cock",
                    "her soles wrapped around his cock shaft"],
        "insert": ["his cock between her soles", "penis between her feet"],
    },
    "anal": {
        "cn": "肛交", "canon": "anal sex", "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["anal sex", "anal", "anal penetration", "taking his cock in her ass",
                    "anus stretched around his cock",
                    "penis in her ass"],
        "insert": ["penis inserted into anus", "visible anal penetration"],
    },

    "masturbation": {
        "cn": "自慰", "canon": "masturbation", "tier": "sex", "core": True, "exclusive": True,
        "solo": True,
        "_legacy_aliases": ["masturbation", "masturbating", "self pleasure",
                    "solo masturbation", "1girl masturbating",
                    "girl masturbating alone", "solo, 1girl masturbating",
                    "fingering herself", "rubbing her own clit",
                    "her fingers rubbing her own clit",
                    "rubbing her pussy through her underwear",
                    "touching herself", "her own hand between her legs"],
        "insert": ["her fingers inside her own pussy"],
    },
    "toy": {
        "cn": "玩具", "canon": "dildo", "tier": "sex", "core": True, "exclusive": True,
        "solo": True,
        "_legacy_aliases": [
            "dildo", "realistic dildo", "silicone dildo", "double-ended dildo",
            "dragon dildo",
            "1girl using a dildo", "girl inserting a dildo into herself",
            "vibrator", "vibrating dildo", "g-spot vibrator", "vibrating wand",
            "1girl using a vibrator",
            "bullet vibrator", "egg vibrator", "love egg", "remote vibrator", "vibrating egg",
            "wand vibrator", "magic wand", "wand massager", "hitachi wand",
            "anal beads", "beads pulled out",
            "butt plug", "anal plug", "jeweled butt plug", "inflatable plug",
            "tail plug", "fox tail plug", "cat tail plug",
            "tentacle", "tentacles coiling around her"],
        "states": [
            "vibrator inserted", "dildo inserted", "plug inserted", "anal beads inserted",
            "butt plug inserted", "vibrator inside her", "dildo inside her pussy",
            "butt plug in her ass", "solo, dildo inserted",
            "dildo in her mouth", "sucking a dildo", "holding a vibrator against herself"],
        "insert": ["vibrator inserted", "dildo inserted", "plug inserted"],
    },

    "kiss": {
        "cn": "接吻", "canon": "kiss", "tier": "sex", "core": False, "exclusive": True,
        "_legacy_aliases": ["kiss", "mouth to mouth", "lips pressed together"],
    },
    "tonguekiss": {
        "cn": "舌吻", "canon": "tongue kiss", "tier": "sex", "core": False, "exclusive": True,
        "_legacy_aliases": ["tongue kiss", "deep kiss", "her tongue touching his tongue", "kissing deeply"],
    },
    "suck_fingers": {
        "cn": "含手指", "canon": "sucking his fingers", "tier": "sex", "core": False, "exclusive": True,
        "_legacy_aliases": ["sucking his fingers", "his fingers in her mouth", "his fingers between her lips"],
        "off": True,
    },
    "suck_nipple": {
        "cn": "吸乳", "canon": "sucking her nipple", "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["sucking her nipple", "mouth on her breast", "his mouth on her nipple"],
    },
    "lick_nipple": {
        "cn": "舔乳", "canon": "tongue on her nipple", "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["tongue on her nipple", "licking her breast", "his tongue circling her nipple"],
    },
    "self_pinch": {
        "cn": "自己摸胸", "canon": "pinching her own nipple", "tier": "sex", "core": False,
        "solo": True,
        "_legacy_aliases": ["pinching her own nipple", "her hand pinching her own nipple",
                    "fingertips pinching her nipple", "her hand on her own breast"],
    },
    "fingering": {
        "cn": "指交", "canon": "fingering", "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["fingering", "his fingers inside her pussy", "fingers pumping into her pussy",
                    "fingers inside her pussy", "his fingers between her folds"],
        "insert": ["fingers inside her pussy"],
    },
    "kiss_hand": {
        "cn": "亲手", "canon": "kissing her hand", "tier": "sex", "core": False, "exclusive": True,
        "_legacy_aliases": ["kissing her hand", "his lips on her fingers"],
        "off": True,
    },
    "hold_hands": {
        "cn": "牵手", "canon": "holding hands", "tier": "sex", "core": False, "exclusive": True,
        "_legacy_aliases": ["holding hands", "interlocked fingers", "fingers laced together"],
        "off": True,
    },
    "lick_hand": {
        "cn": "舔手", "canon": "licking her hand", "tier": "sex", "core": False, "exclusive": True,
        "_legacy_aliases": ["licking her hand", "tongue on her fingers"],
        "off": True,
    },
    "lick_ass": {
        "cn": "舔肛", "canon": "licking her ass", "tier": "sex", "core": True, "exclusive": True,
        "_legacy_aliases": ["licking her ass", "his tongue at her anus"],
    },
    "spank": {
        "cn": "拍臀", "canon": "spanking", "tier": "sex", "core": False, "exclusive": True,
        "off": True,
        "_legacy_aliases": ["spanking", "grabbing her buttocks", "hand on her buttocks"],
    },

    "licking": {
        "cn": "舔", "canon": "licking", "tier": "sex", "core": False, "exclusive": False,
        "_legacy_aliases": ["licking", "licking her neck", "licking her armpit", "licking her face",
                    "licking her inner thigh", "licking her leg", "trailing her tongue along his body",
                    "tongue on her armpit", "tongue on her skin"],
    },
    "fondle": {
        "cn": "摸", "canon": "grabbing her breast", "tier": "sex", "core": False, "exclusive": False,
        "_legacy_aliases": ["grabbing her breast", "groping her breast", "hand on her breast",
                    "cupping her breast", "pinching her nipple between his fingers",
                    "grabbing her pussy", "grabbing her thigh", "caressing her inner thigh",
                    "grabbing her face", "hand on her cheek",
                    "kissing her neck", "kissing her thigh", "kissing her cheek",
                    "kissing her armpit", "fondling"],
    },
}

TOY_BANNED = ("toy", "sex toy", "adult toy", "toys", "toy_oral", "toy_insert", "toy_anal")

FEMALE_PARTS = ["mouth", "chest", "hand", "crotch", "rear", "foot"]
MALE_ORGANS  = ["mouth", "hand", "penis"]

ROUTE_KIND = {
    ("mouth",  "mouth"):  "kiss",    ("mouth",  "tongue"): "lick",
    ("mouth",  "penis"):  "lick",    ("mouth",  "hand"):   "lick",   ("mouth",  "toy"): "lick",
    ("chest",  "mouth"):  "kiss",    ("chest",  "tongue"): "lick",   ("chest",  "hand"): "touch",
    ("chest",  "penis"):  "touch",   ("chest",  "self"):   "touch",
    ("hand",   "mouth"):  "kiss",    ("hand",   "tongue"): "lick",
    ("hand",   "hand"):   "touch",   ("hand",   "penis"):  "touch",
    ("crotch", "mouth"):  "kiss",    ("crotch", "tongue"): "lick",   ("crotch", "hand"): "touch",
    ("crotch", "penis"):  "touch",   ("crotch", "self"):   "touch",  ("crotch", "toy"): "touch",
    ("rear",   "mouth"):  "kiss",    ("rear",   "tongue"): "lick",   ("rear",   "hand"): "touch",
    ("rear",   "penis"):  "touch",   ("rear",   "toy"):    "touch",
    ("foot",   "mouth"):  "kiss",    ("foot",   "tongue"): "lick",
    ("foot",   "hand"):   "touch",   ("foot",   "penis"):  "touch",
}

ROUTE = {
    ("mouth",  "penis"):  "fellatio",
    ("mouth",  "mouth"):  "kiss",
    ("mouth",  "hand"):   "suck_fingers",
    ("mouth",  "tongue"): "tonguekiss",
    ("mouth",  "toy"):    "toy",
    ("chest",  "penis"):  "paizuri",
    ("chest",  "mouth"):  "suck_nipple",
    ("chest",  "hand"):   "fondle",
    ("chest",  "self"):   "self_pinch",
    ("chest",  "tongue"): "lick_nipple",
    ("hand",   "penis"):  "handjob",
    ("hand",   "mouth"):  "kiss_hand",
    ("hand",   "hand"):   "hold_hands",
    ("hand",   "tongue"): "lick_hand",
    ("crotch", "penis"):  "position",
    ("crotch", "mouth"):  "cunnilingus",
    ("crotch", "hand"):   "fingering",
    ("crotch", "self"):   "masturbation",
    ("crotch", "tongue"): "cunnilingus",
    ("crotch", "toy"):    "toy",
    ("rear",   "penis"):  "anal",
    ("rear",   "mouth"):  "lick_ass",
    ("rear",   "tongue"): "lick_ass",
    ("rear",   "hand"):   "spank",
    ("rear",   "toy"):    "toy",
    ("foot",   "penis"):  "footjob",
}

QUOTA = {"penis": 1, "crotch": 1, "rear": 1, "chest": 1,
         "mouth": 1, "tongue": 1, "self": 1, "hand": 2, "foot": 2}

EXCLUSIVE_GROUPS = []

CLAIMS = {
    "missionary": {"penis": 1, "crotch": 1}, "doggystyle": {"penis": 1, "crotch": 1},
    "cowgirl": {"penis": 1, "crotch": 1}, "reverse_cowgirl": {"penis": 1, "crotch": 1},
    "spooning": {"penis": 1, "crotch": 1}, "standing_wall": {"penis": 1, "crotch": 1},
    "squatting_cowgirl": {"penis": 1, "crotch": 1},
    "mating_press": {"penis": 1, "crotch": 1},
    "fellatio": {"mouth": 1, "penis": 1, "hand": 1},
    "cunnilingus": {"mouth": 1, "tongue": 1, "crotch": 1},
    "handjob": {"hand": 1, "penis": 1},
    "paizuri": {"chest": 1, "penis": 1},
    "footjob": {"foot": 2, "penis": 1},
    "anal": {"penis": 1, "rear": 1},
    "masturbation": {"self": 1, "crotch": 1, "hand": 1},
    "toy": {"toy": 1, "hand": 1},
    "kiss": {"mouth": 1}, "tonguekiss": {"mouth": 1, "tongue": 1},
    "suck_fingers": {"mouth": 1, "hand": 1},
    "suck_nipple": {"mouth": 1, "chest": 1},
    "lick_nipple": {"tongue": 1, "chest": 1},
    "self_pinch": {"self": 1, "chest": 1, "hand": 1},
    "fingering": {"hand": 1, "crotch": 1},
    "kiss_hand": {"mouth": 1, "hand": 1}, "hold_hands": {"hand": 2},
    "lick_hand": {"tongue": 1, "hand": 1},
    "lick_ass": {"tongue": 1, "rear": 1}, "spank": {"hand": 1, "rear": 1},
    "licking": {"mouth": 1, "tongue": 1}, "fondle": {"hand": 1},
}

EJAC_STATES = ["ejaculation", "cum on her body", "cumshot", "cum on her face", "creampie"]

def check_quota(plays):
    total, bad = {}, []
    for p in plays:
        for k, n in (CLAIMS.get(p) or {}).items():
            total[k] = total.get(k, 0) + n
    for k, n in total.items():
        if n > QUOTA.get(k, 99):
            bad.append(f"{k} 用了 {n} 个（配额 {QUOTA.get(k, 99)}）")
    for grp in EXCLUSIVE_GROUPS:
        hit = [k for k in grp if k in total]
        if len(hit) > 1:
            bad.append(f"{' / '.join(hit)} 互斥（同属'进入物'，只能来一个）")
    return bad

def part_claims(part, organ):
    c = {part: 1}
    if organ in ("penis", "toy"):
        pass
    elif organ in ("mouth", "tongue"):
        c["tongue" if organ == "tongue" else "mouth"] = 1
    elif organ == "hand":
        c["hand"] = 1
    if organ == "penis":
        c["penis"] = 1
    return c

def check_route(pairs):
    total, bad = {}, []
    for part, organ in pairs:
        for k, n in part_claims(part, organ).items():
            total[k] = total.get(k, 0) + n
    for k, n in total.items():
        if n > QUOTA.get(k, 99):
            bad.append(f"{k} 用了 {n} 个（配额 {QUOTA.get(k, 99)}）")
    return bad

def route_of(part, organ):
    return ROUTE.get((part, organ))

def route_coverage():
    miss = []
    for f in FEMALE_PARTS:
        for m in MALE_ORGANS:
            pool = ROUTE.get((f, m))
            if not pool:
                miss.append((f, m, "没路由"))
            elif pool == "position":
                if not [k for k in SEX_POOL if SEX_POOL[k].get("parent") == "position"]:
                    miss.append((f, m, "体位池是空的"))
            elif pool not in SEX_POOL:
                miss.append((f, m, f"路由到 {pool} 但它不在池子里"))
            elif not aliases_of(pool):
                miss.append((f, m, f"{pool} 是空池子"))
    return miss

def _index():
    idx = {}
    for k, v in SEX_POOL.items():
        for field in ("canon", "aliases", "states", "insert"):
            val = v.get(field)
            if isinstance(val, str):
                val = [val]
            for x in (val or []):
                idx.setdefault(str(x).strip().lower(), k)
    return idx

def parent_of(phrase):
    k = _index().get(str(phrase or "").strip().lower())
    return (k, SEX_POOL[k]["cn"]) if k else (None, None)

def group_of(phrase):
    k = parent_of(phrase)[0]
    if not k:
        return None
    return SEX_POOL[k].get("parent") or k

def tier_of(phrase):
    k = parent_of(phrase)[0]
    return SEX_POOL[k].get("tier", TIER) if k else None

def exclusive_of(phrase):
    k = parent_of(phrase)[0]
    return bool(SEX_POOL[k].get("exclusive")) if k else None

def aliases_of(key):
    v = SEX_POOL.get(key) or {}
    c = (v.get("canon") or "").strip()
    if c:
        return [c]
    return [key]

def legacy_aliases_of(key):
    v = SEX_POOL.get(key) or {}
    out = []
    for field in ("canon", "_legacy_aliases", "states"):
        val = v.get(field)
        if isinstance(val, str):
            val = [val]
        out += [x for x in (val or []) if x not in out]
    return out

def family_of(phrase):
    k = parent_of(phrase)[0]
    return SEX_POOL[k].get("family") if k else None

def plays_of_family(fam):
    return [k for k, v in SEX_POOL.items() if v.get("family") == fam]

def is_solo(phrase):
    if phrase in SEX_POOL:
        return bool(SEX_POOL[phrase].get("solo"))
    k = parent_of(phrase)[0]
    return bool(SEX_POOL[k].get("solo")) if k else None

def solo_plays():
    return [k for k, v in SEX_POOL.items() if v.get("solo")]

def duo_plays():
    return [k for k, v in SEX_POOL.items() if v.get("exclusive") and not v.get("solo")]

def everything_of(key):
    v = SEX_POOL.get(key) or {}
    out = []
    for field in ("canon", "aliases", "states", "insert"):
        val = v.get(field)
        if isinstance(val, str):
            val = [val]
        out += [x for x in (val or []) if x not in out]
    return out

def refs():
    return {"uses": [], "used_by": ["equip_machine（待接）", "sex_router（有重叠）"]}

def core_plays():
    return [k for k, v in SEX_POOL.items() if v.get("core") and not v.get("off")]

def attach_plays():
    return [k for k, v in SEX_POOL.items()
            if not v.get("core") and not v.get("off")]

def check_bottom_line(plays):
    bad = []
    cores = [p for p in plays if SEX_POOL.get(p, {}).get("core")]
    atts  = [p for p in plays if p in SEX_POOL and not SEX_POOL[p].get("core")]
    unknown = [p for p in plays if p not in SEX_POOL]
    if unknown:
        bad.append(f"不认识的玩法：{unknown}")
    if atts and not cores:
        bad.append(f"附加项单独出现（缺保底）：{' / '.join(atts)}")
    return bad

def pick_combo(rng, attach_prob=0.5):
    core = rng.choice(core_plays())
    out = [core]
    for a in attach_plays():
        if rng.random() < attach_prob:
            out.append(a)
    return out

def plays_of_group(g):
    return [k for k, v in SEX_POOL.items() if v.get("parent") == g]

_POSITION_FAMILIES = tuple(FAMILIES)

_INSERTIVE_EXTRA = ("anal", "fingering", "toy", "masturbation")

def insert_style(plays):
    for p in (plays or []):
        v = SEX_POOL.get(p) or {}
        if v.get("family") in _POSITION_FAMILIES or p == "anal":
            return "penis"
    for p in (plays or []):
        if p == "toy":
            return "toy"
        if p in ("fingering", "masturbation"):
            return "digits"
    return ""

def is_insertive(plays):
    return bool(insert_style(plays))

def organ_rear(plays):
    return "anus visible" if any(p == "anal" for p in (plays or [])) else "pussy exposed"

def yield_parts_of(plays):
    parts = []
    for p in (plays or []):
        if (SEX_POOL.get(p) or {}).get("family") in _POSITION_FAMILIES or p == "anal":
            parts.append("crotch")
        elif p == "footjob":
            parts.append("foot")
        elif p in ("self_pinch", "fondle", "paizuri", "suck_nipple", "lick_nipple"):
            parts.append("chest")
    return sorted(set(parts))

def main_plays():
    return [k for k, v in SEX_POOL.items() if v.get("exclusive")]

def addon_plays():
    return [k for k, v in SEX_POOL.items() if not v.get("exclusive")]

POSE_WORDS = ("on all fours", "on her back", "lying on her back", "lying on her side",
              "kneeling", "bent over", "legs extended", "leaning against the wall",
              "sitting on the floor", "knees drawn up", "intimate position",
              "straddling him", "sitting on top", "on her stomach")

def pose_leak():
    bad = []
    for k, v in SEX_POOL.items():
        for field in ("canon", "aliases", "states", "insert"):
            val = v.get(field)
            if isinstance(val, str):
                val = [val]
            for x in (val or []):
                lx = str(x).lower()
                for w in POSE_WORDS:
                    if w in lx:
                        bad.append((k, x, w))
    return bad

def shared_mark_check():
    bad = []
    for k, v in SEX_POOL.items():
        for x in (v.get("insert") or []):
            if x in PENETRATION_MARKS:
                bad.append((k, x))
    return bad

def long_phrase_check(max_words=8):
    bad = []
    for k, v in SEX_POOL.items():
        for x in everything_of(k):
            if len(str(x).split()) > max_words:
                bad.append((k, x, len(str(x).split())))
    return bad

def family_check():
    bad = []
    for k, v in SEX_POOL.items():
        if v.get("parent") == "position":
            f = v.get("family")
            if not f:
                bad.append((k, "没标族"))
            elif f not in FAMILIES:
                bad.append((k, f"族 {f} 不在 FAMILIES 里"))
    return bad

def solo_duo_check():
    bad = []
    for k in solo_plays():
        for x in everything_of(k):
            if re.search(r"\b(his|him|1boy|man|male|cock|penis)\b", str(x).lower()):
                bad.append((k, x))
    return bad

def selfcheck():
    seen, dup = {}, []
    for k, v in SEX_POOL.items():
        for field in ("canon", "aliases", "states", "insert"):
            val = v.get(field)
            if isinstance(val, str):
                val = [val]
            for x in (val or []):
                lx = str(x).strip().lower()
                if lx in seen and seen[lx] != k:
                    dup.append((lx, seen[lx], k))
                seen[lx] = k
    return dup

if __name__ == "__main__":
    main, add = main_plays(), addon_plays()
    print(f"性爱池 v3 —— {len(SEX_POOL)} 个玩法")
    print(f"  主玩法·**互斥**（抽一个）{len(main)} 个   |   附加层·可叠加 {len(add)} 个\n")
    print("  ── 主玩法（互斥 · 有此无彼）──")
    for k in main:
        v = SEX_POOL[k]
        par = f'   [父集 {v["parent"]}]' if v.get("parent") else ""
        print(f"    {v['cn']:<8} {k:<18} tier={v['tier']:<6} 写法 {len(aliases_of(k)):>3}{par}")
    print("  ── 附加层（不互斥 · 可叠加）──")
    for k in add:
        v = SEX_POOL[k]
        print(f"    {v['cn']:<8} {k:<18} tier={v['tier']:<6} 写法 {len(aliases_of(k)):>3}")

    print("  ── ⭐ CORE（自身占性器官 · 可单独出现）──")
    print(f"    {len(core_plays())} 个：" + " / ".join(SEX_POOL[k]['cn'] for k in core_plays()))
    print("  ── ⭐ ATTACH（附加项 · 必须有 CORE 陪）──")
    print(f"    {len(attach_plays())} 个：" + " / ".join(SEX_POOL[k]['cn'] for k in attach_plays()))
    print()
    print("  ── 体位 · 按「源」归族 ──")
    for fam, desc in FAMILIES.items():
        ps = plays_of_family(fam)
        print(f"    {fam:<9} {len(ps)} 个 · {' / '.join(SEX_POOL[k]['cn'] for k in ps)}")
    print(f"\n  ── 单人玩法（前缀不许带 1boy）──  {', '.join(SEX_POOL[k]['cn'] for k in solo_plays())}")

    tot = sum(len(everything_of(k)) for k in SEX_POOL)
    print(f"\n  写法合计 {tot} 条（canon+aliases+states+insert，全量测试用）")
    print(f"  其中 aliases 口径 {sum(len(aliases_of(k)) for k in SEX_POOL)} 条")
    d = selfcheck()
    print(f"  自检·写法冲突（一个写法只能属一个玩法）：{len(d)} 条" + (f" → {d[:4]}" if d else " ✓"))
    bad = [x for x in TOY_BANNED if parent_of(x)[0] is not None]
    print(f"  自检·玩具禁用词能查到玩法吗：{('✗ ' + str(bad)) if bad else '都查不到 ✓（符合铁律）'}")
    pl = pose_leak()
    print(f"  自检·玩法池里混进纯姿态写法：{('✗ ' + str(pl[:5])) if pl else '0 ✓（都归姿态层）'}")
    bad_bl = [c for c in (["kiss"], ["suck_fingers"], ["lick_hand"], ["kiss", "lick_ass"],
                          ["missionary", "kiss"], ["footjob"], ["masturbation", "licking"]) if check_bottom_line(c)]
    print(f"  自检·保底规则（附加项不能单独出现）：{('✗ ' + str(bad_bl[:3])) if bad_bl else '全部 ✓'}")
    lp = long_phrase_check()
    print(f"  自检·词条长度>8个单词的：{len(lp)} 条" + (f" → {[x[1] for x in lp[:3]]}" if lp else " ✓（都很干净）"))
    sm = shared_mark_check()
    print(f"  自检·通用标记被复制进体位：{('✗ ' + str(sm[:5])) if sm else '0 ✓（只在 PENETRATION_MARKS 里）'}")
    fc = family_check()
    print(f"  自检·体位族完整性：{('✗ ' + str(fc[:5])) if fc else '全都有族 ✓'}")
    sc = solo_duo_check()
    print(f"  自检·单人词条混进男伴：{('✗ ' + str(sc[:5])) if sc else '0 ✓（干净）'}")
    print(f"\n  ── 族查找演示 ──")
    for t in ("cowgirl position", "lotus position", "spooning", "missionary position", "blowjob"):
        print(f"    {t:<20} → 族={str(family_of(t)):<10} 单人={is_solo(t)}")

    print("\n  ══ 路由覆盖（女方 6 部位 × 对方 3 器官，**每格都要有池子**）══")
    miss = route_coverage()
    print(f"    {len(FEMALE_PARTS)*len(MALE_ORGANS)} 格，缺口：{miss or '0 ✓'}")
    for f in FEMALE_PARTS:
        row = "  ".join(f"{m}→{(ROUTE.get((f,m)) or '✗'):<13}" for m in MALE_ORGANS)
        print(f"    {f:<8} {row}")

    print("\n  ══ 配额 / 互斥 测试（例子）══")
    for plays in (["toy", "missionary"], ["fellatio", "masturbation"],
                  ["toy", "anal"], ["paizuri", "masturbation"], ["toy", "toy"]):
        bad = check_quota(plays)
        print(f"    {' + '.join(plays):<28} → {'✗ ' + '；'.join(bad) if bad else '✓ 合法'}")

    print("\n  ══ 配额·按**配对**算══")
    for pairs in ([("crotch", "toy"), ("rear", "penis")],
                  [("crotch", "toy"), ("crotch", "penis")],
                  [("mouth", "penis"), ("crotch", "self")],
                  [("crotch", "toy"), ("rear", "toy")]):
        desc = " + ".join(f"{p}×{o}" for p, o in pairs)
        bad = check_route(pairs)
        print(f"    {desc:<38} → {'✗ ' + '；'.join(bad) if bad else '✓ 合法'}")

    print("\n  父集查找演示（写法 → 玩法 → 父集 → 尺度 | 互斥?）：")
    for t in ("blowjob", "magic wand", "doggystyle", "tongue kiss",
              "grabbing her breast", "licking her ass"):
        print(f"    {t:<22} → {str(parent_of(t)):<24} 父集={str(group_of(t)):<10} "
              f"tier={tier_of(t)} 互斥={exclusive_of(t)}")

_RETIRED = {
    "lotus_position": {
        "parent": "position", "family": "on_top", "cn": "莲花坐", "canon": "lotus position",
        "tier": "sex", "core": True, "exclusive": True, "off": True,
        "_legacy_aliases": ["lotus position", "yab-yum", "legs wrapped around his waist",
                    "sitting cross-legged in his lap"],
        "insert": [],
    },
}
