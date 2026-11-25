import random
from . import sex_sents as SS
from . import sex_router as SR
from . import sex_beats as SB

BOY_FORE = ["handjob", "fellatio", "paizuri", "footjob"]
GIRL_FORE = ["fingering", "cunnilingus"]
FINGERING = [("his fingers are between her legs, moving slowly", "他手指在她腿间，慢慢地动"),
             ("his hand is working between her thighs, unhurried", "他的手在她腿间，不慌不忙")]

def position_keep(lib):
    return list(SR.POSITION_PHRASES.get(lib, [])) or [lib]

ORGASM_BODY = [
    ("her whole body shuddering, back arching off the bed", "整个人在抖，背绷得离开床面"),
    ("her toes curling, legs going stiff", "脚趾蜷起来，腿绷直"),
    ("one hand gripping the sheets, knuckles white", "一只手抓着床单，指节发白"),
    ("her hand grabbing his hair, holding on", "抓着男生的头发不放"),
    ("shaking all over, breath caught in her throat", "全身抖，气憋在喉咙里"),
]
ORGASM_SOFT = [
    ("gone limp and boneless, whimpering, unable to hold herself up",
     "整个人软了，哼哼着，撑不住自己"),
    ("too much for her, twitching with every touch, eyes unfocused",
     "太多了受不了，被碰一下就抽一下，眼神发散"),
    ("dewy-eyed and shaking, no strength left in her arms",
     "眼睛湿湿的，发着抖，手臂一点力气都没有"),
]
ORGASM_HOT = [
    ("coming down from it and already pushing back for more, eyes hungry",
     "还没缓过来就往后迎，眼神很亮"),
    ("shuddering through it and pulling him deeper, breath harsh",
     "一边抖一边把他往里带，呼吸很重"),
    ("flushed and smiling through it, riding out the aftershocks, wanting more",
     "红着脸笑着，余韵里还想要"),
]

def still_line(rng, lib, inside):
    if inside:
        return rng.choice([("pushed in to the hilt, holding still", "捅到底，一动不动"),
                           ("buried as deep as he can, gone still", "埋到最深处，整个人定住"),
                           ("bottomed out, both of them frozen in place", "顶到底，两个人一起僵住")])
    return rng.choice([("pulling out at the last second, cum landing on her skin",
                        "最后一下拔出来，射在她皮肤上"),
                       ("withdrawing just in time, spilling over her", "及时抽出来，洒在她身上")])

def cum_line(rng, lib, inside):
    where = SB.WHERE_BY_POS.get(lib) or ["inside her pussy"]
    if inside:
        w = [x for x in where if x.startswith("inside")] or ["inside her pussy"]
        return "creampie, cum inside her", ["creampie"]
    w = [x for x in where if not x.startswith("inside")] or ["on her stomach"]
    c = rng.choice(w)
    return f"cum {c}", [c]

def _sent(rng, lib):
    if lib == "fingering":
        return rng.choice(FINGERING)
    pool = SS.SEX_SENTS.get(lib)
    return rng.choice(pool) if pool else ("PIV", "PIV")

def build(lib, phase, rng, *, org=False, ejac=False, inside=None, second=False,
          soft=False, hot=False):
    s = _sent(rng, lib)
    en_parts, cn_parts, tags = [s[0]], [s[1]], []
    en_extra = []

    if phase >= 2:
        inten = rng.choice(SB.INTENSITY_WORDS)
        if isinstance(inten, (list, tuple)):
            inten = inten[0]
        en_parts.append(inten)
        en_extra.append(inten)
        tags.append(inten)

    if phase >= 2:
        if lib not in SR.REACTION_HAND_BAN:
            r = rng.choice(SR.REACTIONS_HAND)
            en_parts.append(r); en_extra.append(r)
        if lib not in SR.REACTION_LEG_BAN:
            r = rng.choice(SR.REACTIONS_LEG)
            en_parts.append(r); en_extra.append(r)
        f = rng.choice(SR.REACTIONS_FACE)
        en_parts.append(f); en_extra.append(f)

    if phase == 3 and not ejac:
        en_parts.append("still going")
        en_extra.append("still going")

    if org:
        b = rng.choice(SR.REACTIONS_HAND + SR.REACTIONS_LEG)
        en_parts.append(b); en_extra.append(b)
        pool = ORGASM_SOFT if soft else (ORGASM_HOT if hot else ORGASM_SOFT + ORGASM_HOT)
        w = rng.choice(pool)
        en_parts.append(w[0]); cn_parts.append(w[1])
        en_parts.append("flushed cheeks, blush spreading down her neck")
        cn_parts.append("脸颊泛红晕（一直带着）")

    if ejac:
        st = still_line(rng, lib, bool(inside))
        en_parts.append(st[0]); cn_parts.append(st[1])
        cum_en, cum_tags = cum_line(rng, lib, bool(inside))
        en_parts.append(cum_en); cn_parts.append("射精（" + ("体内" if inside else "体外") + "）")
        tags += cum_tags
        if second:
            en_parts.append("coming a second time"); cn_parts.append("第二发")

    if en_extra:
        cn_parts.append("＋" + " / ".join(en_extra))
    return ", ".join(en_parts), "；".join(cn_parts), tags

def carry_tokens(org_done=False, cum_done=False, inside=True, soft=False, hot=False):
    out = []
    if org_done:
        out.append("flushed cheeks, blush still on her skin")
    if cum_done:
        out.append("cum inside her, creampie" if inside else "cum on her body")
    return out

FORE_SKIP_W = {"成熟": 2.8, "魅惑": 2.2, "大胆": 2.1, "强势": 2.0, "御姐": 2.0,
               "冷艳": 1.9, "稳重": 1.0, "天然": 1.0, "开朗": 1.0, "元气": 1.1,
               "温柔": 0.9, "文静": 0.7, "可爱": 0.6, "内向": 0.5, "纯真": 0.4,
               "害羞": 0.35, "腼腆": 0.35}
EXPOSE_SKIP_W = {"害羞": 2.4, "腼腆": 2.3, "纯真": 2.2, "可爱": 2.0, "内向": 1.9,
                 "文静": 1.5, "温柔": 1.4, "无口": 1.3, "天然": 1.2, "元气": 1.1,
                 "稳重": 0.8, "大胆": 0.6, "强势": 0.5, "御姐": 0.4,
                 "冷艳": 0.4, "成熟": 0.35, "魅惑": 0.3}
SKIP_BASE = 0.30

def skip_prob(tnames, kind="fore"):
    tbl = FORE_SKIP_W if kind == "fore" else EXPOSE_SKIP_W
    w = max([tbl.get(t, 1.0) for t in (tnames or [])] or [1.0])
    return min(0.95, SKIP_BASE * w)

SOFT_TRAITS = ("可爱", "温柔", "无口", "害羞", "腼腆", "纯真", "内向", "文静", "天然")
HOT_TRAITS = ("成熟", "魅惑", "强势", "大胆", "御姐", "冷艳")
ORG_START_CARD = 3
ORG_HOLD_CARDS = 2

ORG_BASE = {"害羞": 0.16, "纯真": 0.17, "腼腆": 0.15, "可爱": 0.14, "内向": 0.13,
            "元气": 0.11, "文静": 0.10, "温柔": 0.10, "无口": 0.09, "天然": 0.09,
            "稳重": 0.07, "大胆": 0.06, "强势": 0.05, "冷艳": 0.04,
            "御姐": 0.04, "成熟": 0.035, "魅惑": 0.03}
ORG_ACCEL = {"害羞": 0.07, "纯真": 0.075, "腼腆": 0.07, "可爱": 0.065, "内向": 0.06,
             "元气": 0.05, "文静": 0.045, "温柔": 0.045, "无口": 0.04, "天然": 0.04,
             "稳重": 0.03, "大胆": 0.025, "强势": 0.02, "冷艳": 0.015,
             "御姐": 0.015, "成熟": 0.01, "魅惑": 0.01}

ORG_BY_CHAR = {}

def orgasm_profile(char_cn, tnames):
    if char_cn in ORG_BY_CHAR:
        return {"base": ORG_BY_CHAR[char_cn], "accel": 0.0, "mode": "fixed", "eager": True}
    rng = random.Random(abs(hash(("org", char_cn))) % 99991)
    base = max([ORG_BASE.get(t, 0.06) for t in (tnames or [])] or [0.06])
    accel = max([ORG_ACCEL.get(t, 0.03) for t in (tnames or [])] or [0.03])
    base *= rng.uniform(0.8, 1.25)
    return {"base": round(base, 3), "accel": round(accel, 3),
            "mode": "accel" if rng.random() < 0.70 else "fixed", "eager": False}

def orgasm_p(prof, card_i):
    if not prof.get("eager") and card_i < ORG_START_CARD:
        return 0.0
    if prof.get("mode") == "fixed":
        return prof["base"]
    return min(0.95, prof["base"] + prof["accel"] * (card_i - ORG_START_CARD))

def is_soft(tn):
    return any(t in SOFT_TRAITS for t in (tn or []))

def is_hot(tn):
    return any(t in HOT_TRAITS for t in (tn or []))
