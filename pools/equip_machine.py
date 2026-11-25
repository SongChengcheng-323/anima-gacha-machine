import random
import re
import wardrobe as W
from pools import poses as _POSES
from pools.shot import slot_visible
from pools import sex_router as SR
from pools.set_slots import SET_SLOTS, SET_SEG_RATIO
from pools.characters import CHARACTERS, PUBIC
from pools import hairstyles as HS
from pools import wardrobe_v3 as _W3M
from pools import roll_params as _RP

SLOT_ORDER = ["character", "body", "head", "face", "eyes", "ears", "neck", "upper",
              "chest", "hand_l", "hand_r", "lower", "rear",
              "leg_l", "leg_r", "feet"]

SLOT_SPEC = {
    "character": {"bare": None},
    "body":      {"bare": None},
    "head":      {"bare": None},
    "face":      {"bare": None},
    "eyes":      {"bare": None},
    "ears":      {"bare": None},
    "neck":      {"bare": None},
    "upper":     {"bare": None},
    "chest":     {"bare": None},
    "hand_l":    {"bare": "bare arm"},
    "hand_r":    {"bare": "bare arm"},
    "lower":     {"bare": None},
    "rear":      {"bare": None},
    "leg_l":     {"bare": "bare leg"},
    "leg_r":     {"bare": "bare leg"},
    "feet":      {"bare": "barefoot"},
}

FEATURE_RULES = [
    ("eyes",  ("heterochromia", "star-shaped highlights in eyes", "highlights in eyes",
               "eyes", " eye", "eye ", "pupils")),
    ("ears",  ("elf-like ears", "elf ears", "pointy ears", "animal ears", "wolf ears",
               "cat ears", "fox ears")),
    ("chest", ("breasts", "chest jewel", "bust")),
    ("neck",  ("choker", "necklace", "collar")),
    ("head",  ("hair ornament", "hair flower", "hair ribbon", "hair clip", "hairpin",
               "headband", "ribbon hair tie", "veil", "ornaments", "ornament")),
    ("head",  ("hair", "ahoge", "twintails", "braids", "bangs", "ponytail",
               "sideburns", "horns", "halo")),
    ("hand_l", ("holding ", "wielding ", "carrying ")),
    ("hand_l", ("arm guards", "arm rings", "armband", "arm band")),
    ("leg_l", ("thigh ring", "anklets", "thigh strap", "garter")),
    ("feet",  ("bare feet", "barefoot")),
    ("upper", ("off-shoulder", "sleeveless", "detached sleeves")),
]

def split_features(feat):
    out = {s: [] for s in SLOT_ORDER}
    for tok in [t.strip() for t in (feat or "").split(",") if t.strip()]:
        low = " " + tok.lower() + " "
        for slot, kws in FEATURE_RULES:
            if any(k in low for k in kws):
                out[slot].append(tok)
                break
        else:
            out["body"].append(tok)
    return out

def _ch_feat(ch, override=None):
    lora = None
    for c in CHARACTERS:
        if c[0] == ch:
            lora = c[2]
            if override is None:
                return c[1], lora
            break
    return (override or ""), lora

def _split_bust(feat):
    if not feat:
        return feat, None
    parts = [p.strip() for p in feat.split(",") if p.strip()]
    bust = next((p for p in parts if "breast" in p), None)
    rest = [p for p in parts if p is not bust]
    return ", ".join(rest), bust

HEADWEAR = [
    ("beret", ["beige", "black", "cream"]),
    ("knit beanie", ["white", "grey", "black"]),
    ("sun hat", ["straw", "white"]),
    ("headband", ["black", "lace", "pearl"]),
    ("hair bow", ["pink", "white", "navy"]),
    ("newsboy cap", ["brown", "black"]),
    ("bandana", ["red", "blue"]),
]
HEAD_POSE = ["looking up", "looking down", "head tilted to one side", "head turned to the side",
             "chin slightly raised", "head lowered"]
GAZE_BY_TIER = {
    "fashion": ["looking at viewer", "looking away", "looking into the distance",
                "looking to the side"],
    "tease":   ["looking at viewer", "looking away blushing", "looking down blushing",
                "looking over her shoulder"],
    "exposed": ["looking at viewer", "looking down at him", "looking away blushing"],
    "sex":     ["looking at him", "looking at viewer", "eyes on him",
                "looking down at it", "watching him"],
}
HEAD_POSE_SAFE = [x for x in HEAD_POSE
                  if x not in ("head lowered", "head tilted back",
                                "looking up", "looking down")]

SEX_FACE = ["parted lips", "half-lidded eyes", "heavy blush", "flushed face",
            "moaning", "biting her lower lip", "dazed expression", "sweat drop",
            "eyes squeezed shut, frowning", "brows furrowed, eyes closed"]

SEX_FACE_WATCH = {
    "shy":  ["upturned eyes", "blushing glance upward", "nervous but eager look",
             "shy smile"],
    "bold": ["smirking", "teasing smile", "sultry gaze", "licking her lips"],
}
SEX_FACE_BY_ATT = {
    "shy":  ["shy blush", "flushed face, biting her lip",
             "embarrassed but pleased", "timid expression, heavy blush"],
    "bold": ["smug smile, half-lidded eyes", "challenging look",
             "sultry expression", "confident smile"],
}
WATCH_LIBS = {"handjob", "paizuri", "footjob", "fellatio", "toy_oral"}

EXPRESSIONS_BY_TIER = {
    "fashion": ["closed-mouth smile", "soft smile", "calm neutral expression",
                "gentle smile", "quiet elegant expression"],
    "tease":   ["shy smile", "playful grin", "blushing, looking away", "soft smile",
                "embarrassed smile"],
    "exposed": ["seductive smile", "half-lidded eyes", "flushed cheeks",
                "parted lips", "shy but pleased expression"],
    "sex":     SEX_FACE,
}
EYEWEAR = [("sunglasses", ["black", "brown tortoiseshell", "rose"]),
           ("round glasses", ["thin gold-frame", "silver"]),
           ("glasses", ["black-framed"])]
EARRINGS = [("stud earrings", ["pearl", "small gold", "crystal"]),
            ("hoop earrings", ["silver", "gold"]),
            ("dangling earrings", ["star-shaped", "crescent-shaped"]),
            ("drop earrings", ["jade", "amber"])]
NECKWEAR = [("necklace", ["thin silver", "fine gold chain", "pearl"]),
            ("choker", ["black lace", "velvet", "ribbon"]),
            ("scarf", ["silk", "knit", "plaid"])]

TOPS = [
    ("hoodie", ["blue", "grey", "oversized black"]),
    ("t-shirt", ["white", "striped", "graphic"]),
    ("turtleneck sweater", ["cream", "ribbed grey", "navy"]),
    ("blouse", ["silk white", "sheer pink", "chiffon"]),
    ("cardigan", ["knit beige", "oversized grey"]),
    ("crop top", ["black", "white ribbed"]),
    ("camisole", ["satin ivory", "lace black"]),
    ("flannel shirt", ["red plaid", "blue plaid"]),
    ("denim jacket", ["light wash", "black"]),
]
BOTTOMS = [
    ("pleated skirt", ["black", "navy", "plaid"]),
    ("short shorts", ["denim", "white", "black"]),
    ("jeans", ["light-wash", "black", "ripped"]),
    ("wide-leg pants", ["cream", "charcoal"]),
    ("pencil skirt", ["grey", "black"]),
    ("flowy long skirt", ["floral", "cream"]),
]
LEGWEAR = [
    ("thighhighs", ["black", "white", "lace-topped black"]),
    ("knee-high socks", ["white", "black", "striped"]),
    ("over-knee socks", ["black", "charcoal"]),
    ("pantyhose", ["sheer black", "nude"]),
    ("ripped pantyhose", ["black"]),
]
SHOES = [
    ("loafers", ["black leather", "brown suede"]),
    ("boots", ["ankle black", "mid-calf brown"]),
    ("heels", ["strappy black", "nude stiletto"]),
    ("sneakers", ["white canvas", "chunky"]),
    ("mary jane shoes", ["black patent"]),
    ("sneakers", ["canvas"]),
]
LEGWEAR_STATES = [None, None, None, "with a tear", "with holes", "with lace trim"]

SLEEVES = ["long-sleeved", "short-sleeved", "sleeveless", "off-shoulder",
           "detached-sleeve", "puff-sleeved"]
TWO_HAND_ACTIONS = ["one hand holding her own arm", "one hand gripping her own arm",
                    "hand touching her own shoulder"]
HAND_ACTIONS = [x for x in _POSES.HAND_SINGLE if x not in TWO_HAND_ACTIONS]
HAND_BOTH = list(_POSES.HAND_BOTH)

PROP_RATIO = 0.18
CHAR_PROPS_ENABLED = False
WA_RATIO = 0.15
WA_SCENE_BOOST = 4.0
WA_CHAR_BOOST = 3.0
WA_RATIO_MAX = 0.5
CHAR_PROPS = {}
GENERIC_PROPS = ["holding a bouquet of flowers", "holding a plush toy"]
WA_PROPS = ["holding a katana", "holding a wooden staff",
            "holding a paper umbrella", "holding a folding fan"]
WA_WEIGHTS = {"holding a katana": 1.0,
              "holding a wooden staff": 3.0,
              "holding a paper umbrella": 3.0,
              "holding a folding fan": 3.0}
WA_SCENE_KW = ("japanese", "shrine", "torii", "tatami", "paper door", "paper screen",
               "onsen", "hot spring", "ryokan", "yukata", "kimono", "bamboo",
               "lantern", "matsuri", "festival", "zen garden", "kotatsu", "shoji")
WA_CHARS = set()

def _wa_ratio(char, scene):
    r = WA_RATIO
    if char in WA_CHARS:
        r *= WA_CHAR_BOOST
    if any(k in (scene or "").lower() for k in WA_SCENE_KW):
        r *= WA_SCENE_BOOST
    return min(r, WA_RATIO_MAX)

def _pick_prop(rng, char="", scene=""):
    if CHAR_PROPS_ENABLED and CHAR_PROPS.get(char):
        return CHAR_PROPS[char]
    if rng.random() < _wa_ratio(char, scene):
        return rng.choices(WA_PROPS, weights=[WA_WEIGHTS.get(x, 1.0) for x in WA_PROPS])[0]
    return rng.choice(GENERIC_PROPS)
TEASE_MARKS = ("nipple", "see-through", "visible through", "transparent", "cleavage",
               "camel toe", "upskirt", "underwear visible", "strap slipped", "slipping off",
               "about to come off", "riding up")
TEASE_MARK_THROUGH = ["nipples showing through the fabric", "see-through fabric",
                      "visible through clothes"]
TEASE_MARK_SLIP = ["strap slipped down", "shirt slipping off one shoulder",
                   "unbuttoned and slipping off", "skirt riding up a little",
                   "clothing about to come off"]
TEASE_THIN_KW = ("lace", "sheer", "see-through", "transparent", "mesh", "chiffon",
                 "silk", "satin", "thin", "lingerie", "swimsuit", "bikini", "towel",
                 "camisole", "slip dress")

LEG_POSES = ["legs straight", "one knee raised", "legs crossed",
             "legs slightly apart", "one leg folded under her"]

CHEST_EXPOSE = {
    "tease":   [None, "nipples visible through the fabric", "cleavage visible"],
    "exposed": ["bare breasts", "nipples visible", "one breast out of her clothing"],
    "sex":     ["bare breasts", "nipples visible"],
}
REAR_EXPOSE = {
    "tease":   [None, "panty line visible", "underwear visible"],
    "exposed": ["pussy visible", "pussy exposed", "anus visible", "bare buttocks"],
    "sex":     ["pussy exposed", "anus visible", "pussy and anus visible"],
}
UNDERWEAR = [("panties", ["black lace", "white cotton", "striped"]),
             ("shorts", ["lace-trimmed black"])]

PUBIC_STATES = {}
for _ch, _txt in PUBIC.items():
    parts = [p.strip() for p in _txt.replace("pubic hair", "").split(",") if p.strip()]
    color = next((p for p in parts if any(c in p for c in
                 ("pink", "blonde", "blue", "black", "purple", "red", "silver", "white", "green"))), "")
    shape = next((p for p in parts if p != color), "neatly trimmed")
    PUBIC_STATES[_ch] = (color or "soft", shape)

TOYS = [
    ("dildo", [None], ["inserted", "inserted deep"], "crotch"),
    ("vibrator", ["turned on", "turned off"],
     ["pressed against her crotch", "held against her clit"], "crotch"),
    ("remote-controlled egg vibrator", ["turned on"], ["inside her pussy"], "crotch"),
    ("strap-on harness", [None], ["worn"], "crotch"),
    ("butt plug", ["metal", "jeweled pink", "black"], ["inserted"], "rear"),
    ("anal beads", [None], ["inserted"], "rear"),
    ("fox tail", ["fluffy black", "white fluffy"], ["plug inserted under it"], "rear"),
    ("blindfold", ["black silk", "lace"], ["over her eyes"], "eyes"),
]
TOY_BOTH_HANDS = set()

def _blindfold_mult(char):
    try:
        from pools.char_profile import blindfold_mult
        return blindfold_mult(char)
    except Exception:
        return 1.0

def _sex_scene(char, outdoor_weighted=True):
    if not outdoor_weighted:
        return None
    try:
        from pools.char_profile import outdoor_mult
        m = outdoor_mult(char)
    except Exception:
        m = 1.0
    if m == 1.0:
        return None
    return [(m if sc in SEX_SCENES_OUTDOOR else 1.0) for sc in SEX_SCENES]

def merge(noun, prefix=None, suffix=None):
    pre = [s for s in (prefix or []) if s]
    suf = [s for s in (suffix or []) if s]
    return " ".join(pre + [noun] + suf)

SLOT_TO_WS = {
    "head": "head", "eyes": "head", "face": "head", "ears": "ears", "neck": "neck",
    "upper": "upper", "chest": "upper", "hand_l": "hands", "hand_r": "hands",
    "lower": "lower", "rear": "lower", "leg_l": "legs", "leg_r": "legs", "feet": "feet",
}

SEX_SCENES_INDOOR = [
    "bedroom, on the bed", "hotel room, on the bed, messy sheets",
    "bedroom, white sheets, morning light", "love hotel, neon outside the window",
    "shower, wet tiles, steam", "bathtub, water and bubbles",
    "bathroom counter, mirror", "sofa in the living room",
    "kitchen counter, late at night", "capsule hotel, narrow bunk",
    "changing room, clothes on a hook", "office desk after hours",
]
SEX_SCENES_OUTDOOR = [
    "on the beach at night, waves in the dark",
    "in the car, parked on a quiet street",
    "public park at night, dim streetlight",
    "rooftop at night, city lights below",
    "outdoor hot spring, steam and rocks",
    "forest clearing, dappled moonlight",
    "empty train car, late at night",
    "against the wall in a dark alley",
]
SEX_SCENES = SEX_SCENES_INDOOR + SEX_SCENES_OUTDOOR
_SEX_FOREGROUND_DISABLED = [
    "shot through a slightly open door", "view through the doorway",
    "framed by the door frame", "peeking through the keyhole",
    "through the window, curtains partly drawn", "obscured by the foreground furniture",
    "shot through the gap between curtains", "foreground out of focus, doorway in frame",
]
MALE_TAGS = ["1boy, young man"]
MALE_TAG = MALE_TAGS[0]

POV_POSITIONS = {"missionary", "cowgirl"}
POV_LIBS = {"fellatio", "paizuri", "handjob", "toy_oral"}

def pov_ok(lib=None, pos=None):
    return (str(pos or "") in POV_POSITIONS) or (str(lib or "") in POV_LIBS)
SEX_PARTNER = [MALE_TAG]

MOUTH_ORNS = {"mouth", "tongue"}

SEX_CATS = [("nude", 45), ("lingerie", 30), ("semi", 15), ("swim", 5), ("wearing", 5)]
SEX_CATS_WEIGHTS = [45, 30, 15, 5, 5]

SEX_VIEWS = ["side", "pov", "normal"]
SEX_VIEW_WEIGHTS = [45, 35, 20]
LOCAL_LIBS = {"fellatio", "paizuri", "toy_oral", "handjob"}
SIDE_TEXT = "side view, viewed from the side"
MALE_FEET = "man's lower body and feet visible"

USE_SENTENCES = True
_SENT_USED = set()

_PIV_LIBS = ("PIV", "anal", "toy_insert", "toy_anal")

def _pick_sent(lib, pos=None, ph=None):
    if not USE_SENTENCES or not lib:
        return None
    try:
        from .sex_sents import SEX_SENTS
    except Exception:
        try:
            from sex_sents import SEX_SENTS
        except Exception:
            return None
    keys = ([pos] if (lib in _PIV_LIBS and pos) else []) + [lib]
    for k in keys:
        rows = SEX_SENTS.get(k)
        if not rows:
            continue
        avail = [r for r in rows if r[0] not in _SENT_USED] or rows
        en = rng_pick(avail)
        _SENT_USED.add(en)
        return en
    return None

def rng_pick(rows):
    import random
    return random.choice(rows)[0]

def orig_outfit_off(item):
    try:
        import pool_gate as PG
        return bool(item) and PG.is_off(PG.cached(), item)
    except Exception:
        return False

def _build_sex(rng, char, eq, F, allow_mouth=True, view="normal"):
    _SENT_USED.clear()
    slots, reactions, main_orn, _selfie = SR.plan(rng, allow_mouth=allow_mouth, char=char)
    pos = next((v.get("position") for v in slots.values() if v.get("position")), None)
    org = SR.organs(pos)
    BLK = []
    org_chest = [o for o in org if "nipple" in o or "breast" in o]
    org_rear = [o for o in org if o not in org_chest]

    _ORIG_SLOTS = _orig_outfit_slots(rng, "sex", char)
    if _ORIG_SLOTS:
        _apply_orig_outfit(eq, _ORIG_SLOTS, F, "sex")
        cat = "orig"
    else:
        cat = rng.choices([c for c, _ in SEX_CATS], weights=[w for _, w in SEX_CATS])[0]
    bust = ", ".join(F["chest"]) or None
    if cat == "orig":
        pass
    elif cat == "nude":
        pass
    elif cat == "lingerie":
        eq["upper"] = rng.choice(["black lace lingerie set", "white lace lingerie set"])
        eq["rear"] = "panties pulled aside"
    elif cat == "semi":
        _semi_up = rng.choice(["oversized t-shirt only", "unbuttoned white dress shirt",
                               "towel wrapped around body"])
        eq["upper"] = _semi_up
        if _semi_up == "towel wrapped around body":
            eq["rear"] = "towel lifted"
        else:
            eq["rear"] = "underwear pulled aside"
            eq["lower"] = "panties pulled aside"
    elif cat == "swim":
        eq["upper"] = rng.choice(["halter bikini", "blue one-piece swimsuit"])
        eq["rear"] = "swimsuit pulled aside"
    else:
        if _w3_on():
            eq["upper"] = _W3M.upper("sex", rng) or None
            eq["lower"] = _W3M.lower("sex", rng) or None
            eq["rear"] = "underwear pulled aside" if eq.get("lower") else None
        else:
            eq["upper"] = ", ".join(x for x in (merge(rng.choice(TOPS)[0],
                                                      [rng.choice(rng.choice(TOPS)[1])]),) if x)
            eq["lower"] = merge(rng.choice(BOTTOMS)[0], [rng.choice(rng.choice(BOTTOMS)[1])])
            eq["rear"] = "underwear pulled aside"

    eq["face"] = None
    _gz_all = {g for v in GAZE_BY_TIER.values() for g in v}
    _hp = [x.strip() for x in (eq.get("head") or "").split(",") if x.strip()]
    _gz = [x for x in _hp if x in _gz_all]
    if _gz:
        BLK += _gz
        eq["head"] = ", ".join(x for x in _hp if x not in _gz) or None

    _ml2 = next((v for v in slots.values() if v["tier"] == "sex"), {}).get("lib") or ""
    if _ml2 in ("PIV", "anal", "toy_insert", "toy_anal") and (eq.get("lower") or eq.get("rear")) and cat != "orig":
        _lw = (eq.get("lower") or "").lower()
        if any(k in _lw for k in ("jeans", "pants", "trousers", "shorts")):
            eq["rear"] = ", ".join(x for x in (eq.get("rear"), "pants pulled down") if x)
        elif "skirt" in _lw:
            eq["rear"] = ", ".join(x for x in (eq.get("rear"), "skirt pulled up") if x)
        elif eq.get("rear"):
            eq["rear"] = ", ".join(x for x in (eq["rear"], "clothing pulled aside") if x)

    eq["chest"] = (bust or None)
    BLK += org_chest + org_rear
    if char in PUBIC_STATES and any("pussy" in o or "anus" in o for o in org_rear):
        _c, _sh = PUBIC_STATES[char]
        BLK.append(merge("pubic hair", [_sh, _c]))

    _injected = []
    for part, v in slots.items():
        _sent = _pick_sent(v.get("lib"), pos, v.get("ph"))
        if _sent:
            BLK.append(_sent)
            _injected.append(_sent)
            continue
        BLK += [x for x in v["ph"] if x]

    _HAND_W = (" hand", "hands", "palm", "fingers", "wrist", "knuckles")
    _hand_taken = any(any(w in x.lower() for w in _HAND_W) for x in _injected)
    if reactions.get("hand") and not _hand_taken:
        BLK.append(reactions["hand"])
    if reactions.get("leg"):
        BLK.append(reactions["leg"])
    from pools.characters import attitude_of
    _att = attitude_of(char)
    _mains = next((v for v in slots.values() if v["tier"] == "sex"), {})
    if _mains.get("lib") in WATCH_LIBS:
        _f1 = rng.choice(SEX_FACE_WATCH[_att])
        _f2 = ""
    else:
        _f1 = rng.choice(SEX_FACE_BY_ATT[_att])
        _kw = ("frown", "eyes", "squeezed", "biting", "blush", "smile", "gaze")
        _f2 = rng.choice([x for x in SR.REACTIONS_FACE
                          if x not in ("eyes rolled up", "hand covering her mouth")
                          and "biting" not in x
                          and not any(k in x.lower() and k in _f1.lower() for k in _kw)] or [""])
    BLK += [x for x in (_f1, _f2) if x]

    _blk_low = " ".join(BLK).lower()
    if re.search(r"eyes\s+(squeezed\s+)?shut|eyes\s+closed|closed\s+eyes", _blk_low):
        _GZ_KILL = ("watching him", "looking at him", "eyes on him",
                    "looking at viewer", "looking up at viewer", "looking at it")
        BLK = [x for x in BLK if not any(g in x.lower() for g in _GZ_KILL)]
    _licked = {p for p, v in slots.items() if v["orn"] in MOUTH_ORNS}
    if "chest" in _licked or (slots.get("chest") or {}).get("orn") == "self":
        eq["upper"] = "top pulled up over her breasts"
    if "crotch" in _licked:
        eq["rear"] = "panties pulled aside"
        eq["lower"] = None
    if _licked & {"foot_l", "foot_r"}:
        eq["feet"] = "barefoot"
    if _licked & {"hand_l", "hand_r", "armpit"}:
        if eq.get("upper"):
            eq["upper"] = re.sub(r",?\s*(long-sleeved|short-sleeved|detached-sleeve|puff-sleeved|off-shoulder|sleeveless)", "", eq["upper"]).strip(", ")
        eq["hand_l"] = ", ".join(x for x in (eq.get("hand_l"), "bare arm") if x)
    if "thigh" in _licked:
        eq["lower"] = "skirt lifted" if (eq.get("lower") or "").lower().find("skirt") >= 0 else eq.get("lower")

    _main = next((v for v in slots.values() if v["tier"] == "sex"), {})
    _ml = _main.get("lib")
    if _ml in ("toy_insert", "toy_anal", "toy_oral"):
        _tp = [t for t in TOYS if t[3] in ("hands", "chest", "eyes")]
    elif main_orn == "penis":
        _tp = [t for t in TOYS if t[3] != "crotch"]
    else:
        _tp = list(TOYS)
    if _tp and rng.random() < 0.45:
        _tw = [(_blindfold_mult(char) if t[3] == "eyes" else 1.0) for t in _tp]
        ty = rng.choices(_tp, weights=_tw, k=1)[0]
        _phrase = merge(ty[0], [rng.choice(ty[1])], [rng.choice(ty[2])])
        _pt = ty[3]
        if _pt == "eyes":
            eq["eyes"] = ", ".join(x for x in (eq.get("eyes"), _phrase) if x)
        else:
            BLK.append(_phrase)
            if _pt == "hands":
                eq["hand_r"] = None

    _seen = set()
    for _sl in list(eq):
        if _sl.startswith("_") or not eq.get(_sl):
            continue
        _out = []
        for _x in [y.strip() for y in str(eq[_sl]).split(",") if y.strip()]:
            if _x not in _seen:
                _seen.add(_x); _out.append(_x)
        eq[_sl] = ", ".join(_out) or None
    _main = next((v for v in slots.values() if v["tier"] == "sex"), {})
    if _main.get("lib") in LOCAL_LIBS and view == "pov":
        for _sl in ("lower", "rear", "leg_l", "leg_r"):
            eq[_sl] = None
    _cap_deco(eq, "sex", F)
    _unc = "uncensored"
    if _unc not in " ".join(BLK).lower() and _unc not in (eq.get("upper") or "").lower():
        BLK.append(_unc)
    if _selfie:
        BLK.append(_selfie)
    eq["_sex_block"] = [x for x in BLK if x]
    eq["_sex_meta"] = {"position": pos, "lib": _main.get("lib"), "view": view,
                       "main_orn": main_orn, "cat": cat,
                       "slots": {k: v["orn"] for k, v in slots.items()}}
    return eq

DECO_CAP = {"fashion": 6, "tease": 4, "exposed": 3, "sex": 2}
_HOLD_KW = ("bag", "purse", "phone", "cup", "umbrella", "book", "tote", "clutch", "pouch",
            "basket", "hat in hand")

def _n_deco(eq, F):
    n = 0
    if eq.get("eyes"):
        _e = [x.strip() for x in eq["eyes"].split(",") if x.strip()]
        n += len([x for x in _e if x not in F.get("eyes", [])])
    if eq.get("neck"):
        _n2 = [x.strip() for x in eq["neck"].split(",") if x.strip()]
        n += len([x for x in _n2 if x not in F.get("neck", [])])
    hl = (eq.get("hand_l") or "").lower()
    if any(k in hl for k in _HOLD_KW):
        n += 1
    _hd = [x.strip() for x in (eq.get("head") or "").split(",") if x.strip()]
    n += len([x for x in _hd if x not in F.get("head", [])
              and any(k in x.lower() for k, _v in HEADWEAR)])
    _ears = [x.strip() for x in (eq.get("ears") or "").split(",") if x.strip()]
    n += len([x for x in _ears if x not in F.get("ears", [])])
    return n

def _cap_deco(eq, tier, F):
    cap = DECO_CAP.get(tier)
    if not cap:
        return eq
    n_deco = lambda: _n_deco(eq, F)

    for slot, mode in (("hand_l", "unhold"), ("eyes", "clear"), ("neck", "clear"),
                       ("head", "unhat"), ("ears", "trim")):
        if n_deco() <= cap:
            break
        if mode == "clear":
            eq[slot] = None
        elif mode == "unhold":
            parts = [x.strip() for x in (eq.get("hand_l") or "").split(",") if x.strip()]
            parts = [x for x in parts if not any(k in x.lower() for k in _HOLD_KW)]
            eq["hand_l"] = ", ".join(parts) or None
        elif mode == "unhat":
            parts = [x.strip() for x in (eq.get("head") or "").split(",") if x.strip()]
            parts = [x for x in parts if not any(k in x.lower() for k, _v in HEADWEAR)]
            eq["head"] = ", ".join(parts) or None
        elif mode == "trim":
            parts = [x.strip() for x in (eq.get("ears") or "").split(",") if x.strip()]
            keep = [x for x in parts if x in F.get("ears", [])]
            extra = [x for x in parts if x not in F.get("ears", [])]
            if extra:
                extra.pop()
            eq["ears"] = ", ".join(keep + extra) or None
    return eq

NO_ORIGINAL_OUTFIT = False

ORIG_OUTFIT_RATIO = 0.10
ORIG_OUTFIT_TIERS = ("fashion", "tease", "sex")
ORIG_OUTFIT_KEEP_ACCESSORY = True

def _orig_outfit_slots(rng, tier, char):
    if NO_ORIGINAL_OUTFIT or tier not in ORIG_OUTFIT_TIERS:
        return None
    try:
        from .characters import DEFAULT_OUTFIT as _DO, split_orig_outfit as _SPLIT
    except Exception:
        try:
            from characters import DEFAULT_OUTFIT as _DO, split_orig_outfit as _SPLIT
        except Exception:
            return None
    _do = _DO.get(char)
    if not _do or orig_outfit_off(_do):
        return None
    if tier == "sex":
        _low = _do.lower()
        _HEAVY = ("uniform", "blazer", "jacket", "coat", "sweater", "turtleneck",
                  "crewneck", "cardigan", "hoodie", "kimono", "yukata", "suit",
                  "military", "armor", "maid outfit", "nurse")
        if any(k in _low for k in _HEAVY):
            return None
    if rng.random() >= ORIG_OUTFIT_RATIO:
        return None
    return _SPLIT(_do) or {"upper": _do}

def _apply_orig_outfit(eq, slots, F, tier=""):
    if not slots:
        return
    _pose = eq.pop("_leg_pose", None)
    for _s in ("upper", "lower", "leg_l", "leg_r", "feet"):
        eq[_s] = slots.get(_s) or None
    if _pose:
        eq["leg_l"] = ", ".join(x for x in (eq.get("leg_l"), _pose) if x) or None
    if not eq.get("feet"):
        eq["feet"] = ", ".join(F.get("feet") or []) or None
    for _s in ("eyes", "ears", "neck"):
        _o = slots.get(_s)
        eq[_s] = _o or (eq.get(_s) if ORIG_OUTFIT_KEEP_ACCESSORY else None)
    for _s in ("head", "hand_l", "hand_r"):
        _o = slots.get(_s)
        if _o:
            eq[_s] = ", ".join(x for x in (eq.get(_s), _o) if x)
    if tier == "sex":
        _main = eq.get("upper") or ""
        _lw = _main.lower()
        if any(k in _lw for k in ("coat", "jacket", "cardigan", "shirt")):
            eq["upper"] = (_main + ", slipping off shoulders").strip(", ")
        elif any(k in _lw for k in ("dress", "gown")):
            eq["upper"] = (_main + ", skirt lifted, clothing pulled aside").strip(", ")
        elif any(k in _lw for k in ("uniform", "sailor")):
            eq["upper"] = (_main + ", unbuttoned, clothing pulled aside").strip(", ")
        else:
            eq["upper"] = (_main + ", clothing pulled aside").strip(", ")
        eq["lower"] = "clothing pulled aside"
        eq["rear"] = ", ".join(x for x in (eq.get("rear"), "clothing pulled aside") if x)

def _w3_on():
    return bool(getattr(_RP, "USE_WARDROBE_V3", False))

def build(rng, tier, char, facing="front", framing="full", allow_mouth=True, view="normal",
          feat_override=None, scene=""):
    eq = {s: None for s in SLOT_ORDER}
    feat, lora = _ch_feat(char, feat_override)
    _ORIG_SLOTS = _orig_outfit_slots(rng, tier, char)
    _set_key = None
    if not _ORIG_SLOTS and tier in SET_SEG_RATIO and rng.random() < SET_SEG_RATIO[tier]:
        _set_key = rng.choice(list(SET_SLOTS))

    def _setpick(slot):
        if _set_key and SET_SLOTS[_set_key].get(slot):
            return rng.choice(SET_SLOTS[_set_key][slot])
        return None

    F = split_features(feat)
    eq["character"] = char
    eq["body"] = ", ".join(F["body"]) or None

    head = list(F["head"])
    if rng.random() < HS.HAIR_RATE:
        _new_head = HS.apply_hair(rng, char, head)
        if _new_head:
            head = _new_head
    _have = " ".join(F["head"] + F["ears"] + F["neck"]).lower()
    if _setpick("head"):
        head.append(_setpick("head"))
    elif rng.random() < 0.5:
        hv = rng.choice(HEADWEAR)
        _cand = merge(hv[0], [rng.choice(hv[1])])
        if _cand.lower() not in _have:
            head.append(_cand)
    if rng.random() < 0.5:
        head.append(rng.choice(HEAD_POSE_SAFE))
    _gz = [g for g in GAZE_BY_TIER.get(tier, GAZE_BY_TIER["tease"])]
    if facing == "back":
        _gz = [g for g in _gz if "at viewer" not in g and "at him" not in g] or ["looking away"]
    head.append(rng.choice(_gz))
    eq["head"] = ", ".join(head) or None

    eq["face"] = rng.choice(EXPRESSIONS_BY_TIER.get(tier) or EXPRESSIONS_BY_TIER["tease"])
    eyes = list(F["eyes"])
    if rng.random() < 0.3:
        ew = rng.choice(EYEWEAR)
        eyes.append(merge(ew[0], [rng.choice(ew[1])]))
    eq["eyes"] = ", ".join(eyes) or None

    ears = list(F["ears"])
    if _setpick("ears"):
        ears.append(_setpick("ears"))
    for _ in range(rng.choice([1, 1, 0] if _setpick("ears") else [1, 1, 2])):
        e = rng.choice(EARRINGS)
        cand = merge(e[0], [rng.choice(e[1])])
        if cand not in ears and cand.lower() not in _have:
            ears.append(cand)
    eq["ears"] = ", ".join(ears) or None

    neck = list(F["neck"])
    if _setpick("neck"):
        neck.append(_setpick("neck"))
    elif rng.random() < 0.5:
        nk = rng.choice(NECKWEAR)
        cand = merge(nk[0], [rng.choice(nk[1])])
        if cand not in neck:
            neck.append(cand)
    eq["neck"] = ", ".join(neck) or None

    if tier == "sex":
        eq.update({k: v for k, v in _build_sex(rng, char, eq, F,
                                               allow_mouth=allow_mouth, view=view).items()})
        return eq

    if tier == "fashion":
        cat = "wearing"
    else:
        _CW = {"tease":   [42, 26, 12, 20, 0],
               "exposed": [22, 20, 10, 20, 28]}.get(tier, [45, 25, 12, 10, 8])
        cat = rng.choices(["wearing", "lingerie", "swim", "semi", "nude"],
                          weights=_CW)[0]
    _up_feat = " ".join(F["upper"])
    sleeve = rng.choice([x for x in SLEEVES if x not in _up_feat] or SLEEVES)
    upper = list(F["upper"])
    if cat == "wearing":
        _su, _sl = _setpick("upper"), _setpick("lower")
        if _su:
            upper.append(_su)
        elif _w3_on():
            upper.append(_W3M.upper(tier, rng))
        else:
            t = rng.choice(TOPS)
            upper.append(merge(t[0], [rng.choice(t[1])]))
        if _sl:
            eq["lower"] = _sl
        elif _w3_on():
            eq["lower"] = _W3M.lower(tier, rng)
        else:
            b = rng.choice(BOTTOMS)
            eq["lower"] = merge(b[0], [rng.choice(b[1])])
        if tier != "fashion":
            if _w3_on():
                eq["rear"] = _W3M.under(tier, rng)
            else:
                u = rng.choice(UNDERWEAR)
                eq["rear"] = merge(u[0], [rng.choice(u[1])])
        upper.append(sleeve)
    elif cat == "lingerie":
        upper.append(rng.choice(["black lace lingerie set", "white lace lingerie set"]))
        u = rng.choice(UNDERWEAR)
        eq["rear"] = merge(u[0], [rng.choice(u[1])])
        upper.append("sleeveless")
    elif cat == "swim":
        upper.append(rng.choice(["white bikini", "blue one-piece swimsuit"]))
        upper.append("sleeveless")
    elif cat == "semi":
        upper.append(rng.choice(["towel wrapped around body", "oversized t-shirt only",
                                 "unbuttoned white dress shirt"]))
    eq["upper"] = ", ".join(upper) or None

    bust = ", ".join(F["chest"]) or None
    if tier == "fashion":
        eq["chest"] = bust
    else:
        st = rng.choice(CHEST_EXPOSE.get(tier, [None]))
        eq["chest"] = st or (bust or "bare breasts")

    hands = [None, None]
    if rng.random() < 0.35:
        hands = [rng.choice(HAND_BOTH), None]
    elif rng.random() < 0.75:
        hands = rng.sample(HAND_ACTIONS, 2)
    else:
        hands = [rng.choice(HAND_ACTIONS), None]
    if not _ORIG_SLOTS and tier not in ("tease", "exposed", "sex") and rng.random() < PROP_RATIO:
        hands = [_pick_prop(rng, char, scene), None]
    if tier != "sex" and _setpick("hands") and not eq.get("hand_l"):
        eq["hand_l"] = _setpick("hands")
    _bare_arm = eq["upper"] is None
    _has_both = any(h in HAND_BOTH for h in hands if h)
    for i, slot in enumerate(("hand_l", "hand_r")):
        parts = list(F[slot])
        if i == 0 and _bare_arm and not _has_both:
            parts.append("bare arm")
        if hands[i]:
            parts.append(hands[i])
        eq[slot] = ", ".join(parts) or None

    rear_parts = [eq["rear"]] if eq["rear"] else []
    if tier != "fashion":
        st = rng.choice(REAR_EXPOSE.get(tier, [None]))
        if st:
            rear_parts.append(st)
    _rear_txt = " ".join(rear_parts)
    if char in PUBIC_STATES and any(k in _rear_txt for k in ("pussy", "anus", "buttocks")):
        color, shape = PUBIC_STATES[char]
        rear_parts.append(merge("pubic hair", [shape, color]))
    eq["rear"] = ", ".join(rear_parts) or None

    pose = rng.choice(LEG_POSES)
    eq["_leg_pose"] = pose
    leg_base = list(F["leg_l"])
    sock = None
    if _ORIG_SLOTS:
        pass
    elif _setpick("legs"):
        sock = _setpick("legs")
    elif _w3_on() and rng.random() < 0.7:
        sock = _W3M.legwear(tier, rng)
    elif rng.random() < 0.7:
        lw = rng.choice(LEGWEAR)
        sock = merge(lw[0], [rng.choice(lw[1])], [rng.choice(LEGWEAR_STATES)])
    left = leg_base + ([sock] if sock else ([] if leg_base else ["bare legs"]))
    eq["leg_l"] = ", ".join(left + [pose]) or None
    eq["leg_r"] = sock or None

    if _ORIG_SLOTS:
        _of = _ORIG_SLOTS.get("feet")
        eq["feet"] = _of or (", ".join(F["feet"]) if F["feet"] else None)
    elif F["feet"]:
        eq["feet"] = ", ".join(F["feet"])
    elif _setpick("feet"):
        eq["feet"] = "a pair of " + _setpick("feet")
    elif _w3_on() and rng.random() < 0.75:
        _s3 = _W3M.shoes(tier, rng)
        eq["feet"] = ("a pair of " + _s3) if _s3 else None
    elif rng.random() < 0.75:
        sh = rng.choice(SHOES)
        eq["feet"] = "a pair of " + merge(sh[0], [rng.choice(sh[1])])
    elif not sock:
        eq["feet"] = "barefoot"

    if tier == "exposed" and framing in ("upper", "closeup") \
            and "nipple" not in (eq.get("chest") or "").lower():
        eq["chest"] = "nipples visible"

    if tier == "tease":
        _tx = ((eq.get("chest") or "") + (eq.get("rear") or "") +
               (eq.get("upper") or "") + (eq.get("lower") or "")).lower()
        if not any(k in _tx for k in TEASE_MARKS):
            _cloth = (eq.get("upper") or "").lower()
            if not _cloth.strip():
                pass
            elif any(k in _cloth for k in TEASE_THIN_KW):
                eq["chest"] = ", ".join(x for x in (eq.get("chest"),
                                    rng.choice(TEASE_MARK_THROUGH)) if x)
            else:
                eq["upper"] = ", ".join(x for x in (eq.get("upper"),
                                   rng.choice(TEASE_MARK_SLIP)) if x)

    _LOWER_LIKE = ("skirt", "jeans", "pants", "trousers", "shorts", "lingerie",
                   "bodysuit", "leotard", "swimsuit", "one-piece", "dress")
    if tier in ("exposed", "sex"):
        _cov = eq.get("lower") or ""
        if not any(k in _cov.lower() for k in _LOWER_LIKE):
            _cov = eq.get("upper") or ""
        _has_yield = any(k in (eq.get("rear") or "").lower() for k in
                         ("pulled aside", "pulled down", "lifted", "pulled up", "clothing pulled"))
        if "pussy" in (eq.get("rear") or "").lower() and not _has_yield \
                and any(k in _cov.lower() for k in _LOWER_LIKE):
            _lw = _cov.lower()
            _dis = ("skirt lifted" if "skirt" in _lw
                    else "pants pulled down" if any(k in _lw for k in
                                                    ("jeans", "pants", "trousers", "shorts"))
                    else "clothing pulled aside")
            eq["rear"] = ", ".join(x for x in (eq.get("rear"), _dis) if x)

    _apply_orig_outfit(eq, _ORIG_SLOTS, F, tier)

    try:
        from pools import layer_tables as _LT0
        _fr_on0 = getattr(_LT0, "LAYER_FRAMING_ENABLED", True)
    except Exception:
        _fr_on0 = False
    if _fr_on0:
        for _s, _ws in SLOT_TO_WS.items():
            if _ws and not slot_visible(_ws, framing):
                eq[_s] = None
    eq["_set_key"] = _set_key
    _cap_deco(eq, tier, F)
    return eq

def render(eq, drop_bare=True):
    out = []
    for s in SLOT_ORDER:
        v = eq.get(s)
        if not v and not drop_bare:
            v = SLOT_SPEC[s].get("bare")
        if v:
            out.append(v)
    return ", ".join(out)

SLOT_LABEL = {
    "character": "角色", "body": "体型", "head": "头部", "face": "表情", "eyes": "眼部",
    "ears": "耳部", "neck": "脖子", "upper": "上衣", "chest": "胸部", "hand_l": "左手",
    "hand_r": "右手", "lower": "下身", "rear": "臀部", "leg_l": "左腿", "leg_r": "右腿",
    "feet": "脚",
}

EN_LABEL = {
    "character": "character", "body": "body", "head": "head", "face": "expression",
    "eyes": "eyes", "ears": "ears", "neck": "neck", "upper": "top", "chest": "chest",
    "hand_l": "left arm", "hand_r": "right arm", "lower": "bottom", "rear": "hips",
    "leg_l": "left leg", "leg_r": "right leg", "feet": "feet",
}

def render_prompt(eq, labeled=True, skip=()):
    out = []
    for s in SLOT_ORDER:
        if s in skip or s.startswith("_"):
            continue
        v = eq.get(s)
        if not v:
            continue
        out.append(f"{EN_LABEL.get(s, s)}: {v}" if labeled else v)
    if eq.get("_sex_block"):
        out.extend(eq["_sex_block"])
    return ", ".join(out)

def render_labeled(eq):
    parts = []
    for s in SLOT_ORDER:
        v = eq.get(s)
        parts.append(f"{SLOT_LABEL.get(s, s)}：{v if v else '无'}")
    return "，".join(parts)

def drop_bare_name(s):
    return False
