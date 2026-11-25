import random

STYLES = {"casual": 42, "chic": 28, "uniform": 16, "home": 14}

_HIDE_KW = {
    "lower": ("skirt", "shorts", "pants", "jeans", "trousers", "leggings",
              "panties", "thong", "briefs", "underwear", "bikini bottom"),
    "legs":  ("thighhigh", "over-knee", "knee-high", "pantyhose", "stocking", "socks",
              "garter", "thigh ring"),
    "feet":  ("boots", "heels", "sneakers", "sandals", "mary jane", "shoes", "footwear",
              "flats", "slippers", "tip-toe"),
}

def _visible_filter(items, framing):
    if not framing:
        return list(items)
    try:
        from pools.shot import slot_visible
    except Exception:
        return list(items)
    hide = []
    for slot in ("lower", "legs", "feet"):
        if not slot_visible(slot, framing):
            hide += _HIDE_KW[slot]
    if not hide:
        return list(items)
    kept = [x for x in items if not any(k in x.lower() for k in hide)]
    return kept or list(items)

TOPS = {
    "casual": ["t-shirt", "oversized hoodie", "striped t-shirt", "flannel shirt",
               "knit cardigan", "oversized t-shirt", "tank top", "zip-up hoodie"],
    "chic": ["silk blouse", "satin slip dress", "corset top", "turtleneck sweater",
             "halter neck dress", "silk blouse with ribbon", "high-neck knit dress"],
    "uniform": ["sailor school uniform", "maid outfit", "nurse uniform", "office lady blouse",
                "flight attendant uniform", "school uniform", "waitress uniform"],
    "home": ["boyfriend shirt", "loose knit sweater", "satin pajama top"],
}
COLORS = ["white", "black", "cream", "pastel pink", "lavender", "navy blue", "sage green",
          "wine red", "charcoal", "dusty rose", "ivory", "baby blue"]
MATERIALS = ["", "lace", "silk", "satin", "sheer", "knit", "denim", "leather", "velvet",
             "chiffon", "ribbed", "frilled", "cotton"]
SLEEVES = ["long sleeves", "short sleeves", "sleeveless", "detached sleeves", "puff sleeves",
           "flared sleeves", "off-shoulder sleeves", "half sleeves"]
NECKLINES = ["crew neck", "v-neck", "turtleneck", "halter neck", "deep v neckline",
             "sailor collar", "square neckline", "sweetheart neckline", "keyhole neckline"]
FASHION_BAD_NECKLINE = ("deep v neckline", "sweetheart neckline")

BOTTOMS = {
    "casual": ["denim shorts", "wide-leg pants", "denim skirt", "slim pants"],
    "chic": ["pencil skirt", "long flowy skirt", "satin midi skirt", "high-slit long skirt",
             "pleated midi skirt"],
    "uniform": ["pleated mini skirt", "short pleated skirt", "wide skirt"],
    "home": ["loose shorts", "pleated skirt"],
}

TOPS["flirty"] = [
    "camisole", "ribbed tank top", "satin camisole", "crop top", "off-shoulder knit top",
    "sheer robe", "lace blouse", "babydoll nightgown",
] + TOPS["uniform"]
BOTTOMS["flirty"] = [
    "short shorts", "high-waisted shorts", "sleep shorts", "tight mini skirt",
] + BOTTOMS["uniform"]

BOTTOM_LEN = ["", "", "", "above knee", "knee-length", "micro mini", "over the knee"]
SLITS = ["", "", "", "with a high slit", "with a side slit", "with a front slit"]

LEGWEAR = ["thighhighs", "over-knee socks", "knee-high socks", "pantyhose",
           "garter belt with stockings", "sheer pantyhose", "bare legs"]
LEGWEAR_COLOR = ["white", "black", "beige", "charcoal", "striped", "cream"]
LEGWEAR_STATE = ["", "", "", "", "with a small tear", "ripped", "wet and clinging"]

SHOES = ["", "", "heels", "mary jane shoes", "thigh boots", "ankle boots", "sneakers",
         "sandals", "barefoot", "strappy heels"]
ACCESSORIES = ["", "", "choker", "lace choker with a small pendant", "garter belt",
               "hair ribbon", "thigh ring", "gold earrings", "delicate necklace",
               "off-shoulder strap slipped down"]

LINGERIE = ["black lace lingerie", "white lace lingerie", "satin lingerie set",
            "sheer lace babydoll nightgown", "white lace bra and panties",
            "silk lingerie with garter belt", "ribbon-tied lingerie"]
LINGERIE_EXTRA = ["with black stockings", "with white thighhighs", "with a garter belt",
                  "", "", "with lace thighhighs"]

SWIM = ["white bikini", "black high-cut one-piece swimsuit", "school swimsuit",
        "blue one-piece swimsuit", "striped bikini", "halter bikini", "frilled one-piece swimsuit"]
SWIM_EXTRA = ["", "", "with a sheer cover-up", "with a sun hat", "with a pareo"]

SEMI = ["towel wrapped around body", "naked apron", "unbuttoned white dress shirt",
        "oversized t-shirt only", "silk robe half open", "shirt only, no bottom"]

MATERIAL_OK = {
    "lace": ["blouse", "camisole", "camisole top", "corset top", "lingerie", "top", "dress", "bra"],
    "sheer": ["blouse", "camisole", "robe", "dress", "top", "pantyhose", "lingerie"],
    "satin": ["slip dress", "camisole", "blouse", "skirt", "pajama top", "dress"],
    "silk": ["blouse", "camisole", "robe", "dress", "pajama top"],
    "knit": ["cardigan", "sweater", "top", "dress", "tank top"],
    "denim": ["skirt", "shorts", "jacket", "top"],
    "leather": ["skirt", "jacket", "pants", "shorts"],
    "velvet": ["dress", "top", "skirt"],
    "chiffon": ["blouse", "dress", "skirt"],
    "ribbed": ["tank top", "top", "sweater", "camisole"],
    "frilled": ["blouse", "top", "apron", "lingerie"],
    "cotton": ["t-shirt", "shirt", "shorts", "top", "pajama top"],
}

def _mat_ok(mat, item):
    if not mat:
        return True
    allowed = MATERIAL_OK.get(mat)
    if not allowed:
        return True
    return any(a in item.lower() for a in allowed)

def _top(rng, ostyle, details, framing=None, tier=None):
    item = rng.choice(_visible_filter(TOPS[ostyle], framing))
    prefix = []
    if "color" in details:
        prefix.append(rng.choice(COLORS))
    if "material" in details:
        mats = [m for m in MATERIALS if m and _mat_ok(m, item)]
        if mats:
            prefix.append(rng.choice(mats))
    head = " ".join(prefix)
    out = [f"{head} {item}".strip()] if head else [item]
    if "sleeve" in details:
        if not any(k in item for k in ("camisole", "slip dress", "halter", "tank")):
            out.append(rng.choice(SLEEVES))
    if "neckline" in details:
        if not any(k in item for k in ("turtleneck", "halter")):
            _nl = NECKLINES
            if tier == "fashion":
                _nl = [x for x in NECKLINES if x not in FASHION_BAD_NECKLINE] or NECKLINES
            out.append(rng.choice(_nl))
    return ", ".join(out)

def _bottom(rng, ostyle, details, framing=None):
    item = rng.choice(_visible_filter(BOTTOMS[ostyle], framing))
    out = [item]
    is_skirt = "skirt" in item
    if "bottom_len" in details and is_skirt:
        l = rng.choice(BOTTOM_LEN)
        if l:
            out.append(l)
    if "slit" in details and is_skirt and any(k in item for k in ("long", "midi", "flowy")):
        s = rng.choice(SLITS)
        if s:
            out.append(s)
    return ", ".join(out)

def _legwear(rng, details, framing=None):
    if not _slot_ok("legs", framing):
        return ""
    if rng.random() < 0.22:
        return "bare legs"
    item = rng.choice(_visible_filter(LEGWEAR, framing))
    if item == "bare legs":
        return item
    out = []
    if "legwear_color" in details:
        out.append(rng.choice(LEGWEAR_COLOR))
    if "legwear_state" in details:
        st = rng.choice(LEGWEAR_STATE)
        if st:
            out.append(st)
    out.append(item)
    return " ".join(out)

def _acc(rng, framing=None):
    a = rng.choice(_visible_filter(ACCESSORIES, framing))
    return a

def _detail_pick(rng, framing=None):
    all_dims = ["material", "color", "sleeve", "neckline", "bottom_len", "slit",
                "legwear_color", "legwear_state", "shoe", "acc"]
    if framing:
        if not _slot_ok("legs", framing):
            all_dims = [d for d in all_dims if not d.startswith("legwear")]
        if not _slot_ok("feet", framing):
            all_dims = [d for d in all_dims if d != "shoe"]
        if not _slot_ok("lower", framing):
            all_dims = [d for d in all_dims if d not in ("bottom_len", "slit")]
    n = rng.choices([1, 2, 3], weights=[30, 45, 25])[0]
    return set(rng.sample(all_dims, min(n, len(all_dims))))

def build_wearing(rng, pref=None, tier=None, framing=None):
    if tier and tier != "fashion":
        ostyle = "flirty"
    else:
        keys, ws = list(STYLES.keys()), list(STYLES.values())
        if pref:
            ws = [w * 3 if k in pref else w for k, w in zip(keys, ws)]
        ostyle = rng.choices(keys, weights=ws)[0]
    d = _detail_pick(rng, framing)
    parts = [_top(rng, ostyle, d, framing, tier)]
    if _slot_ok("lower", framing):
        parts.append(_bottom(rng, ostyle, d, framing))
    parts.append(_legwear(rng, d, framing))
    if tier == "fashion":
        _shoe_pool = [x for x in _visible_filter(SHOES, framing)
                      if x and "barefoot" not in x.lower()]
        if _shoe_pool:
            parts.append(rng.choice(_shoe_pool))
    elif "shoe" in d:
        s = rng.choice(_visible_filter(SHOES, framing))
        if s:
            parts.append(s)
    if "acc" in d:
        a = _acc(rng, framing)
        if a:
            parts.append(a)
    return ", ".join(p for p in parts if p), ostyle

def _slot_ok(slot, framing):
    if not framing:
        return True
    try:
        from pools.shot import slot_visible
        return slot_visible(slot, framing)
    except Exception:
        return True

def build_lingerie(rng, pref=None, tier=None, framing=None):
    d = _detail_pick(rng, framing)
    parts = [rng.choice(_visible_filter(LINGERIE, framing))]
    if "legwear_color" in d or "legwear_state" in d:
        parts.append(_legwear(rng, d, framing))
    else:
        e = rng.choice(_visible_filter(LINGERIE_EXTRA, framing))
        if e:
            parts.append(e)
    if "acc" in d:
        a = rng.choice(_visible_filter(["garter belt", "lace choker", "thigh ring", ""], framing))
        if a:
            parts.append(a)
    return ", ".join(p for p in parts if p), "chic"

def build_swim(rng, pref=None, tier=None, framing=None):
    parts = [rng.choice(_visible_filter(SWIM, framing))]
    e = rng.choice(_visible_filter(SWIM_EXTRA, framing))
    if e:
        parts.append(e)
    return ", ".join(parts), "casual"

def build_semi(rng, pref=None, tier=None, framing=None):
    parts = [rng.choice(_visible_filter(SEMI, framing))]
    d = _detail_pick(rng, framing)
    if "legwear_color" in d:
        parts.append(_legwear(rng, d, framing))
    return ", ".join(parts), "home"

BUILDERS = {
    "wearing": build_wearing,
    "lingerie": build_lingerie,
    "swim": build_swim,
    "semi": build_semi,
    "nude": lambda rng, pref=None, tier=None, framing=None: ("", "home"),
}

CAT_WEIGHTS = {"wearing": 52, "lingerie": 17, "swim": 8, "semi": 13, "nude": 10}

CAT_WEIGHTS_TIER = {
    "fashion": {"wearing": 100, "lingerie": 0,  "swim": 0,  "semi": 0,  "nude": 0},
    "tease":   {"wearing": 25,  "lingerie": 50, "swim": 40, "semi": 30, "nude": 5},
    "exposed": {"wearing": 15,  "lingerie": 25, "swim": 20, "semi": 45, "nude": 50},
    "sex":     {"wearing": 20,  "lingerie": 20, "swim": 10, "semi": 35, "nude": 55},
}

def weights_for(tier):
    return dict(CAT_WEIGHTS_TIER.get(tier or "", CAT_WEIGHTS))

def compose(rng, used=None, pref_cats=None, allowed_cats=None, tier=None,
            prefer_sleeveless=False, prefer_barefoot=False, framing=None):
    used = used if used is not None else set()
    pref_cats = pref_cats or []
    cat_pref = [c for c in pref_cats if c in CAT_WEIGHTS]
    style_pref = [s for s in pref_cats if s in STYLES]
    w = weights_for(tier)
    _base = weights_for(tier)
    if allowed_cats:
        w = {k: v for k, v in w.items() if k in allowed_cats} or _base
    for k in cat_pref:
        w[k] = w.get(k, 5) * 3
    if prefer_sleeveless:
        for k in ("swim", "lingerie", "semi"):
            if k in w:
                w[k] = w[k] * 2
    outfit, cat, ostyle = "", "wearing", "casual"
    best = None
    for _ in range(24):
        cat = rng.choices(list(w.keys()), weights=list(w.values()))[0]
        outfit, ostyle = BUILDERS[cat](rng, style_pref, tier, framing)
        if outfit in used:
            continue
        if prefer_sleeveless and any(k in outfit.lower() for k in _SLEEVE_KW):
            best = best or (outfit, cat, ostyle)
            continue
        if prefer_barefoot and any(k in outfit.lower() for k in _SHOE_KW):
            best = best or (outfit, cat, ostyle)
            continue
        try:
            from pools.wardrobe_slots import equip_filter
            _kept, _ = equip_filter(outfit)
            if _kept:
                outfit = _kept
        except Exception:
            pass
        return outfit, cat, ostyle
    try:
        from pools.wardrobe_slots import equip_filter
        _kept, _ = equip_filter(outfit)
        if _kept:
            outfit = _kept
    except Exception:
        pass
    return best or (outfit, cat, ostyle)

_SLEEVE_KW = ("sleeve", "sleeves", "shirt", "blazer", "jacket", "coat", "hoodie",
              "sweater", "cardigan", "sweatshirt", "turtleneck", "kimono", "haori")
_SHOE_KW = ("shoes", "boots", "heels", "sneakers", "sandals", "loafers", "flats",
            "mary jane", "pumps", "slippers")

if __name__ == "__main__":
    r = random.Random()
    print("=== 随机组合 12 套（看看花样够不够）===")
    for i in range(12):
        o, c, s = compose(r)
        print(f"  [{c:8}/{s:8}] {o}")
    import math
    n = 0
    for st, tops in TOPS.items():
        n += len(tops) * len(BOTTOMS[st]) * len(LEGWEAR) * (len(SHOES) + 1) * (len(ACCESSORIES) + 1)
    print(f"\n日常穿着（保守估算）≈ {n * 10:,} 种组合；含内衣/泳装/半遮共 5 大类")
