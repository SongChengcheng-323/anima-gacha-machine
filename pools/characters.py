CHARACTERS_SPLIT = [
    {"tag": "hatsune_miku", "official": "", "hair": "aqua hair, very long twintails", "eyes": "aqua eyes", "body": "", "face": "", "extra": "", "default_outfit": "detached sleeves", "props": ""},
]

_SHORT = {}

_MOODS = {
    "hatsune_miku": [
        "cheerful smile, blushing",
        "shy smile, blushing",
        "shy smile, looking away",
        "playful wink, blushing",
    ],
}

_BUST_SET = {}

def _one_bust(text):
    parts = [p.strip() for p in (text or "").split(",") if p.strip()]
    idx = [i for i, p in enumerate(parts) if p.lower() in _BUST_SET]
    if len(idx) <= 1:
        return text
    spec = [i for i in idx if parts[i].lower() != "breasts"]
    keep = spec[0] if spec else idx[0]
    return ", ".join(p for i, p in enumerate(parts) if i == keep or i not in idx)

_ONBODY_KW = ("halo", "wings", "wing", "tail", "horn",
              "pointy ears", "fox ears", "cat ears", "elf ears", "animal ears",
              "mole", "freckles", "tattoo", "scar", "eyelashes", "heterochromia")
_DECO_KW = ("earrings", "earring", "hair ornament", "hairclip", "hair clip",
            "hairpin", "hair stick", "chinese hairpin", "headdress", "headwear",
            "hat", "beret", "cap", "crown", "tiara", "headband", "headphones",
            "hair bow", "hair ribbon", "hairband", "hair flower",
            "necklace", "choker", "collar", "pendant", "brooch", "scarf", "ascot",
            "bracelet", "bangle", "wristband", "armlet", "thighlet", "garter",
            "glasses", "eyewear", "sunglasses", "goggles", "monocle", "pince-nez",
            "mask", "eyepatch", "veil", "piercing", "jewelry", "jewellery")

def _is_deco_word(t):
    low = (t or "").strip().lower()
    if not low:
        return False
    for k in _ONBODY_KW:
        if k in low:
            return False
    return any(k in low for k in _DECO_KW)

def _split_deco(text):
    keep, deco = [], []
    for t in (text or "").split(","):
        t = t.strip()
        if not t:
            continue
        (deco if _is_deco_word(t) else keep).append(t)
    return ", ".join(keep), ", ".join(deco)

def _feat(d):
    if d.get("official"):
        raw = d["official"]
    else:
        raw = ", ".join(x for x in (d.get("hair"), d.get("eyes"), d.get("body"),
                                    d.get("face"), d.get("extra")) if x)
    keep, _ = _split_deco(raw)
    return _one_bust(keep)

def _deco_of(d):
    raw = d.get("official") or ", ".join(
        x for x in (d.get("hair"), d.get("eyes"), d.get("body"),
                    d.get("face"), d.get("extra")) if x)
    _, deco = _split_deco(raw)
    return deco

_DEFAULT_MOODS = ["slight smile, looking at viewer", "calm expression, looking at viewer",
                  "soft smile, blushing faintly", "gentle expression, relaxed brows"]
CHARACTERS = [
    (d["tag"], _feat(d), _SHORT.get(d["tag"]), list(_MOODS.get(d["tag"]) or _DEFAULT_MOODS))
    for d in CHARACTERS_SPLIT
]

ORIG_SLOT_KW = (
    ("feet",   ("boots", "shoes", "sandals", "heels", "sneakers", "loafers", "geta", "clogs", "mules")),
    ("leg_l",  ("thighhighs", "thigh highs", "stockings", "pantyhose", "socks", "garter", "legwear",
                "thigh strap", "leg warmers", "anklet")),
    ("lower",  ("skirt", "shorts", "pants", "jeans", "hakama", "trousers", "bloomers")),
    ("head",   ("hair ornament", "hair bow", "hair ribbon", "hair stick", "hair flower", "hair belt",
                "hair ring", "hair vine", "hair band", "hairband", "hairclip", "chinese hairpin",
                "headphones", "headband", "beret", "bonnet", "laurel", "kanzashi", "tiara", "crown",
                "veil", "hat", "cap")),
    ("eyes",   ("sunglasses", "glasses", "eyepatch", "monocle")),
    ("ears",   ("earrings", "earring", "ear piercing")),
    ("neck",   ("choker", "necklace", "necktie", "pendant", "scarf")),
    ("hand_l", ("gloves", "bracelet", "bangle", "armlet", "wristband", "nail polish", "arm warmers")),
    ("upper",  ("serafuku", "sailor", "leotard", "uniform", "tabard", "bodysuit", "camisole",
                "corset", "blouse", "sweater", "hoodie", "cardigan", "jacket", "sweatshirt",
                "shirt", "coat", "dress", "gown", "robe", "cloak", "cape", "vest", "bra",
                "kimono", "yukata", "qipao", "apron", "tunic", "shawl", "suit", "blazer", "wetsuit",
                "top")),
)

def _norm_txt(s):
    return " " + (s or "").lower().replace("_", " ").replace("-", " ") + " "

def _kw_hit(low, k):
    if len(k) >= 6 or (" " in k):
        return k in low
    return (" " + k + " ") in low

def split_orig_outfit(text):
    parts = [p.strip() for p in (text or "").split(",") if p.strip()]
    out = {}
    for p in parts:
        low = _norm_txt(p)
        slot = "upper"
        for s, kws in ORIG_SLOT_KW:
            if any(_kw_hit(low, k) for k in kws):
                slot = s
                break
        out.setdefault(slot, [])
        if p not in out[slot]:
            out[slot].append(p)
    if not any(out.get(s) for s in ("upper", "lower")):
        _up = list(out.get("upper") or [])
        for s in list(out):
            if s != "upper":
                _up += out.pop(s)
        out["upper"] = _up
    return {k: ", ".join(v) for k, v in out.items() if v}

def _outfit_of(d):
    parts = [x for x in (d.get("default_outfit"), _deco_of(d)) if x]
    return ", ".join(parts)

DEFAULT_OUTFIT = {
    d["tag"]: _outfit_of(d) for d in CHARACTERS_SPLIT if _outfit_of(d)
}

FEAT_VARIANTS = {}

CHARACTER_WEIGHTS_LEGACY = {
    "hatsune_miku": 1,
}

BASE_CHAR_WEIGHT = 1.0

FAVORITE_WEIGHTS = {}

CHARACTER_WEIGHTS = {d["tag"]: FAVORITE_WEIGHTS.get(d["tag"], BASE_CHAR_WEIGHT)
                     for d in CHARACTERS_SPLIT}

CHARACTER_WEIGHTS.update({
    "hatsune_miku": 6.0,
})

NO_HAIR_CHANGE = set()

STYLE_LOCK = {}

PUBIC = {}

LORA_MAP = {}

WUWA_ALL_LORA = ""
WUWA_KEYWORD = ""

TIER_LOCK = {
}

def tier_lock_of(character):
    return tuple(TIER_LOCK.get(character or "") or ())

WUWA_LORA_CHARS = frozenset({
    "mornye",
    "lynae",
    "sigrika",
    "denia",
    "hiyuki",
    "suisui",
    "yangyang (xuanling)",
    "lucilla",
    "hsin",
    "qingxiao",
    "suoming",
})

def lora_of(character):
    key = (character or "").split("_(")[0].split(" (")[0].strip()
    if key in LORA_MAP:
        return LORA_MAP[key]
    return ""

ATTITUDE = {
    "shy": [],
    "bold": [],
}

def attitude_of(ch):
    if ch in ATTITUDE.get("shy", []):
        return "shy"
    if ch in ATTITUDE.get("bold", []):
        return "bold"
    return "bold"

def short_name(tag):
    import re as _re
    t = (tag or "").strip()
    if not t:
        return "unknown"
    _all = _re.findall(r"\(([^)]*)\)", t)
    base = _re.split(r"[ _]\(", t)[0].strip() or t
    if len(_all) >= 2:
        base = base + "_" + _all[0].strip().replace(" ", "_")
    return _re.sub(r"[^0-9A-Za-z_.]+", "_", base) or "unknown"

_SMALL_BUST_KW = (
    "flat chest", "small breasts", "petite", "loli", "child",
    "modest bust", "tiny breasts", "flat chested",
)
_BY_TAG = {_d["tag"]: _d for _d in CHARACTERS_SPLIT if _d.get("tag")}

def is_small_bust(tag):
    d = _BY_TAG.get((tag or "").strip())
    if not d:
        return False
    feat = " ".join(str(d.get(k) or "") for k in
                    ("official", "hair", "eyes", "body", "extra", "default_outfit")).lower()
    return any(k in feat for k in _SMALL_BUST_KW)

def pubic_of(tag):
    if is_small_bust(tag):
        return ""
    try:
        d = _BY_TAG.get((tag or "").strip())
        feat = _feat(d) if d else ""
        _COLORS = ("white", "black", "brown", "blonde", "blond", "grey", "gray",
                   "silver", "purple", "pink", "blue", "red", "green", "orange",
                   "yellow", "aqua", "cyan", "magenta", "gold", "golden", "ash",
                   "platinum", "lavender", "violet", "crimson", "scarlet", "navy",
                   "teal", "mint", "peach", "beige", "turquoise", "amber", "ivory")
        color = ""
        _LEN = ("very", "absurdly", "long", "short", "medium", "huge", "big")
        _BAD = ("multicolored", "gradient", "two-tone", "colored inner",
                "streaked", "highlights", "split-color")
        for t in feat.split(","):
            t = t.strip().lower()
            if not t.endswith(" hair"):
                continue
            head = t[:-5].strip()
            if any(b in head for b in _BAD):
                continue
            words = [w for w in head.split() if w not in _LEN]
            head = " ".join(words).strip()
            if head and any(c in head for c in _COLORS):
                color = head
                break
        if not color:
            return ""
        return f"{color} pubic hair, neatly trimmed"
    except Exception:
        return ""

CHARACTERS = [
    (d["tag"], _feat(d), _SHORT.get(d["tag"]), list(_MOODS.get(d["tag"]) or _DEFAULT_MOODS))
    for d in CHARACTERS_SPLIT
]
NO_HAIR_CHANGE = set()
WUWA_LORA_CHARS = frozenset()

WUWA_ALL_LORA = ""
WUWA_KEYWORD = ""
