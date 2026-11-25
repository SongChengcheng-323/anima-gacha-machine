import re

_COLOR_TOKENS = [
    ("light blue", "blue"), ("dark blue", "blue"),
    ("light purple", "purple"), ("dark purple", "purple"),
    ("blue-green", "green"),
    ("blonde", "gold"), ("golden", "gold"), ("gold", "gold"),
    ("amber", "amber"),
    ("aqua", "aqua"), ("cyan", "cyan"),
    ("magenta", "magenta"), ("pink", "pink"),
    ("purple", "purple"), ("silver", "silver"),
    ("grey", "grey"), ("gray", "grey"),
    ("green", "green"), ("blue", "blue"),
    ("red", "red"), ("black", "black"),
    ("white", "white"), ("brown", "brown"),
    ("yellow", "yellow"),
]
COLOR_WORDS = [c for c, _canon in _COLOR_TOKENS]

HAIR_BY_GROUP = {
    "长直": [
        ("very long straight hair", "超长直发"),
        ("long straight hair, blunt bangs", "长直发·齐刘海"),
        ("hime cut", "公主切（姬发式）"),
        ("long hair, hair spread out", "长发披散"),
    ],
    "卷发": [
        ("long wavy hair", "长卷发"),
        ("curly hair", "卷发"),
        ("drill hair", "钻头卷"),
        ("wavy hair, curled ends", "微卷·发尾内扣"),
        ("fluffy hair", "蓬松发"),
    ],
    "马尾": [
        ("high ponytail", "高马尾"),
        ("ponytail", "马尾"),
        ("side ponytail", "侧马尾"),
        ("low ponytail", "低马尾"),
        ("ponytail, long hair", "长马尾"),
    ],
    "双马尾": [
        ("twintails", "双马尾"),
        ("low twintails", "低双马尾"),
        ("short twintails", "短双马尾"),
        ("twin braids", "双麻花辫"),
        ("uneven twintails", "不对称双马尾"),
    ],
    "编发": [
        ("braid", "麻花辫"),
        ("single braid", "单辫"),
        ("french braid", "法式编发"),
        ("braided crown", "编发头冠"),
        ("braid, hair over one eye", "侧辫遮眼"),
    ],
    "盘发/丸子": [
        ("hair bun", "丸子头"),
        ("double bun", "双丸子头"),
        ("space buns", "太空丸子头"),
        ("messy bun", "凌乱丸子头"),
        ("updo", "盘发"),
        ("half updo", "半盘发"),
    ],
    "短发": [
        ("short hair", "短发"),
        ("bob cut", "波波头"),
        ("pixie cut", "精灵短发"),
        ("short hair, hair between eyes", "短发·碎发遮眼"),
        ("wolf cut", "狼尾"),
        ("hush cut", "韩系层次剪"),
    ],
    "刘海（可叠加）": [
        ("blunt bangs", "齐刘海"),
        ("swept bangs", "斜刘海"),
        ("parted bangs", "中分刘海"),
        ("crossed bangs", "交叉刘海"),
        ("see-through bangs", "空气刘海"),
        ("asymmetrical bangs", "不对称刘海"),
        ("hair intakes", "刘海内收"),
    ],
    "特殊造型": [
        ("hair over one eye", "头发遮一只眼"),
        ("hair pulled back, hair intakes", "后梳·露出额头"),
        ("messy hair", "凌乱发"),
        ("hair flaps", "翘发"),
        ("sidelocks", "鬓发"),
        ("ahoge", "呆毛"),
    ],
}

HAIR_ALL = [(en, cn) for grp in HAIR_BY_GROUP.values() for en, cn in grp]

HAIR_OPTIONS = {    }

HAIR_RATE = 0.0

_FALLBACK_LOCKED = {
    "hatsune_miku",
    "kagamine_rin", "kagamine_len",
    "sailor_moon",
}

_HAIR_ACC = ("hair ornament", "hair flower", "hair ribbon", "hair clip", "hairpin",
             "headband", "hair tie", "veil")
_SHAPE_WORDS = ("very long", "long", "medium", "short", "twintails", "twin tails",
                "ponytail", "braids", "braid", "bangs", "ahoge", "sideburns",
                "hair flaps", "bun", "bob", "hime cut")
_KEEP_HAIR = ("hair",)

def _is_hair(tok):
    t = (tok or "").lower()
    if any(a in t for a in _HAIR_ACC):
        return False
    return ("hair" in t) or _has_shape(t)

def _has_shape(tok):
    t = (tok or "").lower()
    for w in _SHAPE_WORDS:
        if re.search(r"\b" + re.escape(w) + r"\b", t):
            return True
    return False

def hair_color(tokens):
    for tok in tokens or []:
        t = " " + (tok or "").lower() + " "
        for c in COLOR_WORDS:
            if re.search(r"\b" + re.escape(c) + r"\b", t):
                return c
    return ""

def _color_phrase(tok):
    t = (tok or "").lower()
    t = re.sub(r"\bhair\b", " ", t)
    for w in sorted(_SHAPE_WORDS, key=len, reverse=True):
        t = re.sub(r"\b" + re.escape(w) + r"\b", " ", t)
    t = re.sub(r"[,，]", " ", t)
    return " ".join(t.split()).strip()

def apply_hair(rng, char_tag, head_tokens):
    locked = set(_FALLBACK_LOCKED)
    try:
        from pools.characters import NO_HAIR_CHANGE
        locked |= set(NO_HAIR_CHANGE or ())
    except Exception:
        pass
    if char_tag in locked:
        return None

    opts = HAIR_OPTIONS.get(char_tag) or [en for en, _cn in HAIR_ALL]
    if not opts:
        return None
    style = rng.choice(opts)

    keep, dropped, phrases = [], [], []
    for t in head_tokens or []:
        if _is_hair(t) and _has_shape(t):
            dropped.append(t)
            p = _color_phrase(t)
            if p and p not in phrases:
                phrases.append(p)
        else:
            keep.append(t)
    if not dropped:
        return None
    if not phrases:
        _c = hair_color(head_tokens)
        phrases = [_c] if _c else []
    if not phrases:
        return None

    new = list(keep)
    new += [s.strip() for s in str(style).split(",") if s.strip()]
    _kept = " ".join(keep).lower()
    for p in phrases:
        if p.lower() not in _kept:
            new.append(f"{p} hair")
    return new

def _locked():
    s = set(_FALLBACK_LOCKED)
    try:
        from pools.characters import NO_HAIR_CHANGE
        s |= set(NO_HAIR_CHANGE or ())
    except Exception:
        pass
    return s

def pick_hair(rng, char_tag):
    if char_tag in _locked():
        return None
    opts = HAIR_OPTIONS.get(char_tag)
    if not opts:
        return None
    return rng.choice(opts)

def pool_group(name):
    return list(HAIR_BY_GROUP.get(name, []))

if __name__ == "__main__":
    print(f"发型池：{len(HAIR_BY_GROUP)} 组 / {len(HAIR_ALL)} 条\n")
    for g, rows in HAIR_BY_GROUP.items():
        print(f"  {g:<12} {len(rows)} 条 → {rows[0][0]} …")
    print(f"\n已配候选发型的角色：{list(HAIR_OPTIONS)}")
    print(f"保护名单（不换发型）：{sorted(_locked())}")
