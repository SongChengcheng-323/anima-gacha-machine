# 画风占位
#
# 这里只放「方向」，不放配方。
# 值是空字符串：选了方向也不会往提示词里塞任何东西，
# 文件名和相册分类照常记录方向名。
# 想用某个方向，把那一格填成自己的提示词片段即可。

# 每格只给这个方向最小的一组词，够让产线跑起来；
# 具体配方自己填，别照抄别人。
STYLES = {
    "flat":      "flat color, clean lineart",          # 平涂
    "painterly": "painterly, visible brush strokes",   # 厚涂
    "oil":       "oil painting",                       # 油画
    "realistic": "realistic proportions, natural lighting",  # 写实
}

STYLE_PREFIX = {}

STYLE_W = {
    "flat":      1.0,
    "painterly": 1.0,
    "oil":       1.0,
    "realistic": 1.0,
}

QUALITY_TAGS = ""

HEAD = "masterpiece, best quality, ecchi, 1girl"

HEAD_FASHION = "masterpiece, best quality, safe, 1girl"

HEAD_EXPOSED = ("masterpiece, best quality, uncensored, ecchi, explicit, "
                "bare arms, 1girl")

_ECCHI_STYLE_WORDS = ("uncensored", "skin gloss", "glossy highlights",
                      "subsurface scattering", "soft luminous skin", "moist skin")

ACTIVE_STYLES = list(STYLES)

STYLE_W_BY_TIER = {
    "fashion": {"style:flat": 1.0, "style:painterly": 1.0,
                "style:oil": 1.0, "style:realistic": 1.0},
    "tease":   {"style:flat": 0.8, "style:painterly": 0.2},
    "exposed": {"style:flat": 0.8, "style:painterly": 0.2},
    "sex":     {"style:flat": 0.8, "style:painterly": 0.2},
}


def style_pool():
    return dict(STYLE_W)


def pick_style(rng, tier=None, size=None):
    full = {"style:%s" % k: w for k, w in style_pool().items() if w > 0}
    try:
        from pools import artists as AR
    except Exception:
        try:
            import artists as AR
        except Exception:
            AR = None
    if AR is not None:
        for t, w in (AR.weights() or {}).items():
            if w > 0:
                full["artist:%s" % t] = w

    tier_w = STYLE_W_BY_TIER.get(tier or "fashion")
    if tier_w is None:
        pool = full
    else:
        pool = {k: w for k, w in tier_w.items() if w > 0 and k in full}

    if not pool:
        pool = full
    if not pool:
        return "style", "", ""

    keys = list(pool)
    k = rng.choices(keys, weights=[pool[x] for x in keys], k=1)[0]
    kind, val = k.split(":", 1)
    if kind == "artist":
        return "artist", "@%s" % val, val
    return "style", _purge_ecchi(STYLES.get(val) or "", tier), val


def _purge_ecchi(text, tier=None):
    if (tier or "fashion") != "fashion" or not text:
        return text
    out = [w for w in text.split(",")
           if w.strip().lower() not in _ECCHI_STYLE_WORDS]
    return ", ".join(w.strip() for w in out if w.strip())
