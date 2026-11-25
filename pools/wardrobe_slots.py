SLOTS = {
    "head":  ("头部（帽/发饰）", 2, False),
    "neck":  ("颈部（项链/围巾/领）", 2, False),
    "ears":  ("耳部（耳饰）", 2, False),
    "wrist": ("手腕（手链/手表）", 2, False),
    "hands": ("手部（手套/戒指）", 2, False),
    "upper": ("上身（上衣）", 2, True),
    "lower": ("下身（下装）", 1, True),
    "waist": ("腰部（腰带）", 1, False),
    "legs":  ("腿部（袜）", 2, False),
    "feet":  ("脚部（鞋）", 2, False),
}

EQUIPMENT = {
    "white t-shirt":            (("upper",), False),
    "oversized hoodie":         (("upper",), False),
    "striped t-shirt":          (("upper",), False),
    "knit sweater":             (("upper",), False),
    "silk blouse":              (("upper",), False),
    "satin slip dress":         (("upper", "lower"), True),
    "corset top":               (("upper",), False),
    "sailor school uniform":    (("upper", "lower"), True),
    "maid outfit":              (("upper", "lower"), True),
    "nurse uniform":            (("upper", "lower"), True),
    "camisole":                 (("upper",), False),
    "boyfriend shirt":          (("upper",), False),
    "babydoll nightgown":       (("upper", "lower"), True),
    "flannel shirt":            (("upper",), False),
    "denim jacket":             (("upper",), False),
    "long dress":               (("upper", "lower"), True),
    "one-piece dress":          (("upper", "lower"), True),
    "jumpsuit":                 (("upper", "lower"), True),

    "denim shorts":             (("lower",), False),
    "short shorts":             (("lower",), False),
    "high-waisted shorts":      (("lower",), False),
    "pencil skirt":             (("lower",), False),
    "long flowy skirt":         (("lower",), False),
    "satin midi skirt":         (("lower",), False),
    "pleated mini skirt":       (("lower",), False),
    "short pleated skirt":      (("lower",), False),
    "loose shorts":             (("lower",), False),
    "sleep shorts":             (("lower",), False),
    "jeans":                    (("lower",), False),
    "wide-leg pants":           (("lower",), False),

    "thighhighs":               (("legs",), False),
    "over-knee socks":          (("legs",), False),
    "knee-high socks":          (("legs",), False),
    "pantyhose":                (("legs",), False),
    "striped knee-high socks":  (("legs",), False),
    "single thighhigh":         (("legs",), False),

    "heels":                    (("feet",), False),
    "mary jane shoes":          (("feet",), False),
    "thigh boots":              (("feet",), False),
    "ankle boots":              (("feet",), False),
    "sneakers":                 (("feet",), False),
    "sandals":                  (("feet",), False),
    "strappy heels":            (("feet",), False),
    "barefoot":                 (("feet",), False),

    "choker":                   (("neck",), False),
    "lace choker with a small pendant": (("neck",), False),
    "delicate necklace":        (("neck",), False),
    "gold earrings":            (("ears",), False),
    "hair ribbon":              (("head",), False),
    "beret":                    (("head",), False),
    "garter belt":              (("waist",), False),
    "thigh ring":               (("legs",), False),
}

FASHION_REQUIRED_SLOTS = ("upper", "lower", "feet")

def slots_of(item):
    it = (item or "").strip().lower()
    if it in EQUIPMENT:
        return EQUIPMENT[it][0]
    if any(k in it for k in ("dress", "gown", "jumpsuit", "overall", "uniform", "nightgown")):
        return ("upper", "lower")
    if any(k in it for k in ("skirt", "shorts", "pants", "jeans", "trousers")):
        return ("lower",)
    if any(k in it for k in ("sock", "thighhigh", "tights", "pantyhose", "stocking")):
        return ("legs",)
    if any(k in it for k in ("shoes", "boots", "heels", "sneakers", "sandals", "loafers",
                             "flats", "slippers", "barefoot")):
        return ("feet",)
    if any(k in it for k in ("necklace", "choker", "scarf", "pendant")):
        return ("neck",)
    if any(k in it for k in ("earring", "earrings")):
        return ("ears",)
    if any(k in it for k in ("bracelet", "watch")):
        return ("wrist",)
    if any(k in it for k in ("ring", "gloves")):
        return ("hands",)
    if any(k in it for k in ("hat", "beret", "ribbon", "clip", "hairpin")):
        return ("head",)
    if any(k in it for k in ("belt", "sash")):
        return ("waist",)
    return ("upper",)

def can_equip(equipped, item):
    _key = (item or "").strip().lower()
    if _key and any((it or "").strip().lower() == _key for it, _ in equipped):
        return False
    need = slots_of(item)
    used = {}
    for it, sl in equipped:
        for s in sl:
            used[s] = used.get(s, 0) + 1
    for s in need:
        cap = SLOTS.get(s, ("", 1, False))[1]
        if used.get(s, 0) >= cap:
            return False
    if "upper" in need and "lower" in need:
        if used.get("upper") or used.get("lower"):
            return False
    if ("upper" in need or "lower" in need):
        for it, sl in equipped:
            if "upper" in sl and "lower" in sl:
                return False
    _it_low = (item or "").lower()
    _have_bare = any("barefoot" in i.lower() for i, _ in equipped)
    _have_shoe = any(_is_shoe(i) for i, _ in equipped)
    if "feet" in need:
        if _have_bare and _is_shoe(_it_low):
            return False
        if _have_shoe and "barefoot" in _it_low:
            return False
    return True

_SHOE_KW = ("shoes", "boots", "heels", "sneakers", "sandals", "loafers", "flats",
            "mary jane", "pumps", "slippers", "strappy")

def _is_shoe(item):
    return any(k in (item or "").lower() for k in _SHOE_KW) and "barefoot" not in (item or "").lower()

def equip(equipped, item):
    if not item:
        return list(equipped)
    if not can_equip(equipped, item):
        return None
    return list(equipped) + [(item, slots_of(item))]

def is_fashion_complete(equipped):
    used = set()
    for it, sl in equipped:
        for s in sl:
            if not (s == "feet" and "barefoot" in it):
                used.add(s)
    return all(s in used for s in FASHION_REQUIRED_SLOTS)

def render(equipped):
    return ", ".join(it for it, _ in equipped if it)

GARMENT_KW = ("dress", "gown", "jumpsuit", "overall", "uniform", "nightgown",
              "skirt", "shorts", "pants", "jeans", "trousers", "sock", "thighhigh",
              "tights", "pantyhose", "stocking", "shoes", "boots", "heels",
              "sneakers", "sandals", "loafers", "flats", "slippers", "necklace",
              "choker", "scarf", "pendant", "earring", "bracelet", "watch", "ring",
              "gloves", "hat", "beret", "ribbon", "hairpin", "belt", "sash",
              "hoodie", "t-shirt", "shirt", "blouse", "sweater", "cardigan",
              "camisole", "corset", "robe", "bikini", "bra", "panties", "swimsuit",
              "coat", "jacket", "blazer", "apron", "sarashi", "towel", "veil")

def equip_filter(text):
    kept, dropped, equipped = [], [], []
    for piece in [x.strip() for x in (text or "").split(",") if x.strip()]:
        if any(k in piece.lower() for k in GARMENT_KW):
            if can_equip(equipped, piece):
                equipped.append((piece, slots_of(piece)))
                kept.append(piece)
            else:
                dropped.append(piece)
        else:
            equipped.append((piece, ()))
            kept.append(piece)
    return ", ".join(kept), dropped
