import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(_HERE) not in sys.path:
    sys.path.insert(0, os.path.dirname(_HERE))

PRIVACY = {
    "love hotel room": 10,
    "bedroom": 9,
    "bathroom": 9,
    "onsen": 8,
    "fitting room": 8,
    "living room": 7,
    "karaoke room": 7,
    "locker room": 6,
    "car interior": 6,
    "arcade": 4,
    "observation deck": 4,
    "office": 3,
    "cafe": 3,
    "classroom": 3,
    "elevator": 2,
    "library": 2,
    "train interior": 1,
    "campsite": 8,
    "forest": 8,
    "lake shore": 7,
    "balcony": 7,
    "rooftop": 7,
    "pier": 6,
    "poolside": 5,
    "shrine": 5,
    "beach": 4,
    "summer festival": 2,
    "park": 2,
    "city street": 1,
    "bus interior": 1,
}

TRAIT_ACCEPT = {
    "成熟": {"high": 1.00, "mid": 1.00, "low": 0.75, "public": 0.50},
    "可爱": {"high": 1.00, "mid": 0.70, "low": 0.50, "public": 0.20},
    "无口": {"high": 1.00, "mid": 0.80, "low": 0.40, "public": 0.12},
    "害羞": {"high": 0.85, "mid": 0.45, "low": 0.15, "public": 0.10},
}
DEFAULT_TRAIT = "可爱"

TIER_PEAK = {"tease": 6, "exposed": 6, "sex": 9}
FASHION_HIGH_CUT = 0.9
DECAY = 0.5

def band(p):
    if p >= 8:
        return "high"
    if p >= 5:
        return "mid"
    if p >= 2:
        return "low"
    return "public"

def privacy_of(scene, default=5):
    return PRIVACY.get((scene or "").strip().lower(), default)

def weight(scene, tier, trait=None):
    p = privacy_of(scene)
    if tier in (None, "", "fashion"):
        return FASHION_HIGH_CUT if p >= 8 else 1.0
    peak = TIER_PEAK.get(tier, 5)
    w = max(0.05, 1.0 - abs(p - peak) / 10.0 * DECAY)
    acc = (TRAIT_ACCEPT.get(trait or DEFAULT_TRAIT) or TRAIT_ACCEPT[DEFAULT_TRAIT])[band(p)]
    return w * acc

def weights_for(scenes, tier, trait=None):
    return [weight(s, tier, trait) for s in scenes]

def selfcheck():
    bad = []
    for t, peak in TIER_PEAK.items():
        hi = weight("love hotel room", t, "成熟")
        lo = weight("city street", t, "成熟")
        if not (hi > lo):
            bad.append(f"{t}: 高私密 {hi:.2f} 没高于低私密 {lo:.2f}")
    if weight("bedroom", "fashion") != FASHION_HIGH_CUT:
        bad.append("fashion 高私密权重≠0.9")
    if weight("city street", "fashion") != 1.0:
        bad.append("fashion 低私密权重≠1.0")
    if crowd_prob(1) != 0.80 or crowd_prob(2) != 0.60:
        bad.append("人群概率锚点不对（应为 1→0.8 / 2→0.6）")
    for _p in range(0, 5):
        if crowd_prob(_p) < crowd_prob(_p + 1):
            bad.append(f"人群概率在私密度 {_p}→{_p+1} 反向上升")
    if crowd_prob(6) != 0 or crowd_prob(9) != 0:
        bad.append("高私密场景不该附带人群")
    import random as _rnd
    for _t in (None, "tease", "exposed", "sex"):
        if crowd_for(_rnd.Random(0), "city street", _t):
            bad.append(f"人群出现在 {_t!r} 档（应只有 fashion）")
    for _tr, _bands in EXPR_W.items():
        for _bd, _tab in (_bands or {}).items():
            _tot = sum(_tab.values())
            if _tot <= 0:
                bad.append(f"表情权重 {_tr}/{_bd} 全是 0")
                continue
            _mx = max(_tab.values()) / _tot
            if _mx > 0.45:
                bad.append(f"表情权重 {_tr}/{_bd} 单类占 {_mx:.0%} 过高（该有波动）")
    if EXPR_W["成熟"]["high"]["flirty"] < EXPR_W["成熟"]["public"]["flirty"] * 0.7:
        bad.append("成熟：高私密处 flirty 被压得太低（她在那儿也可以调情）")
    if EXPR_W["害羞"]["public"]["shy"] <= EXPR_W["害羞"]["high"]["shy"]:
        bad.append("害羞：公开处 shy 没高于私密处")
    for _tr, _tab in MODE_P.items():
        _vals = [_tab[q] for q in sorted(_tab)]
        if any(_vals[i] < _vals[i + 1] for i in range(len(_vals) - 1)):
            bad.append(f"{_tr}：模式概率没有随私密度递减")
        if min(_vals) <= 0 or max(_vals) >= 1:
            bad.append(f"{_tr}：模式概率出现 0 或 1（波动被掐死了）")
    return bad

CROWD_WORDS = {
    "crowd":       {"en": "crowd, silhouettes",              "cn": "人群（街头剪影）"},
    "many people": {"en": "many people, blurred background", "cn": "人群（虚化背景）"},
}
CROWD_P = {0: 0.85, 1: 0.80, 2: 0.60, 3: 0.35, 4: 0.15, 5: 0.05}
CROWD_STREET = {"city street", "summer festival", "arcade", "train interior", "elevator"}
CROWD_ONLY_TIERS = ("fashion",)

def crowd_prob(privacy):
    try:
        p = int(round(float(privacy)))
    except Exception:
        return 0.0
    return CROWD_P.get(max(0, min(10, p)), 0.0)

def crowd_for(rng, scene, tier=None):
    if tier not in CROWD_ONLY_TIERS:
        return ""
    prob = crowd_prob(privacy_of(scene))
    if prob <= 0 or rng.random() >= prob:
        return ""
    key = "crowd" if (scene or "").strip().lower() in CROWD_STREET else "many people"
    return CROWD_WORDS[key]["en"]

EXPR_W = {
    "成熟": {
        "public": {"flirty": 1.5, "laugh": 1.4, "smile_soft": 1.2, "calm": 1.0,
                   "shy": 0.8, "pleasure": 1.3, "serious": 0.6, "surprised": 0.5},
        "low":    {"flirty": 1.6, "laugh": 1.4, "smile_soft": 1.3, "calm": 1.0,
                   "shy": 0.8, "pleasure": 1.3, "serious": 0.6, "surprised": 0.5},
        "mid":    {"flirty": 1.4, "smile_soft": 1.5, "calm": 1.3, "laugh": 1.3,
                   "pleasure": 1.1, "shy": 1.0, "serious": 0.7, "surprised": 0.5},
        "high":   {"smile_soft": 1.6, "calm": 1.5, "flirty": 1.3, "laugh": 1.2,
                   "shy": 1.1, "pleasure": 1.1, "serious": 0.8, "surprised": 0.5},
    },
    "可爱": {
        "public": {"laugh": 1.7, "shy": 1.5, "smile_soft": 1.4, "flirty": 1.0,
                   "calm": 0.9, "pleasure": 1.0, "serious": 0.5, "surprised": 0.9},
        "low":    {"laugh": 1.9, "shy": 1.4, "smile_soft": 1.5, "flirty": 1.0,
                   "calm": 1.0, "pleasure": 1.0, "serious": 0.5, "surprised": 0.8},
        "mid":    {"laugh": 1.7, "smile_soft": 1.6, "shy": 1.3, "flirty": 1.1,
                   "calm": 1.2, "pleasure": 1.1, "serious": 0.6, "surprised": 0.7},
        "high":   {"smile_soft": 1.8, "laugh": 1.5, "calm": 1.4, "shy": 1.2,
                   "flirty": 1.1, "pleasure": 1.2, "serious": 0.7, "surprised": 0.6},
    },
    "无口": {
        "public": {"calm": 1.7, "serious": 1.2, "shy": 1.3, "smile_soft": 1.0,
                   "laugh": 0.8, "flirty": 0.7, "pleasure": 0.9, "surprised": 0.6},
        "low":    {"calm": 1.7, "shy": 1.1, "serious": 1.0, "smile_soft": 1.1,
                   "laugh": 0.9, "flirty": 0.8, "pleasure": 1.0, "surprised": 0.6},
        "mid":    {"calm": 1.6, "smile_soft": 1.3, "shy": 0.95, "serious": 0.8,
                   "laugh": 1.1, "flirty": 0.9, "pleasure": 1.1, "surprised": 0.6},
        "high":   {"smile_soft": 1.6, "calm": 1.4, "laugh": 1.3, "pleasure": 1.2,
                   "shy": 1.0, "flirty": 1.1, "serious": 0.6, "surprised": 0.5},
    },
    "害羞": {
        "public": {"shy": 2.0, "smile_soft": 1.2, "calm": 1.0, "laugh": 1.0,
                   "flirty": 0.8, "pleasure": 0.8, "serious": 0.6, "surprised": 0.8},
        "low":    {"shy": 2.0, "smile_soft": 1.3, "calm": 1.0, "laugh": 1.1,
                   "flirty": 0.9, "pleasure": 1.0, "serious": 0.6, "surprised": 0.7},
        "mid":    {"shy": 1.6, "smile_soft": 1.5, "calm": 1.2, "laugh": 1.3,
                   "flirty": 1.0, "pleasure": 1.1, "serious": 0.6, "surprised": 0.6},
        "high":   {"smile_soft": 1.7, "calm": 1.5, "shy": 1.3, "laugh": 1.4,
                   "flirty": 1.2, "pleasure": 1.3, "serious": 0.6, "surprised": 0.5},
    },
}

EXPR_MODE = {
    "成熟": {"label": "小恶魔", "w": {
        "flirty": 3.4, "laugh": 1.6, "smile_soft": 1.1, "calm": 0.5,
        "shy": 0.7, "pleasure": 1.8, "serious": 0.4, "surprised": 0.4}},
    "害羞": {"label": "绷不住", "w": {
        "shy": 3.6, "smile_soft": 0.7, "calm": 0.4, "laugh": 0.8,
        "flirty": 0.3, "pleasure": 0.6, "serious": 0.5, "surprised": 0.7}},
}
MODE_P = {
    "成熟": {0: 0.60, 1: 0.55, 2: 0.50, 3: 0.45, 4: 0.35, 5: 0.28,
             6: 0.22, 7: 0.18, 8: 0.14, 9: 0.12, 10: 0.12},
    "害羞": {0: 0.65, 1: 0.65, 2: 0.60, 3: 0.55, 4: 0.45, 5: 0.35,
             6: 0.25, 7: 0.18, 8: 0.12, 9: 0.08, 10: 0.08},
}

def mode_prob(trait, privacy):
    if trait not in MODE_P:
        return 0.0
    try:
        p = int(round(float(privacy)))
    except Exception:
        return 0.0
    return MODE_P[trait].get(max(0, min(10, p)), 0.0)

SEX_DEGREE_W = {
    "成熟": {
        0: {"pleasure": 2.2, "mouth": 1.5, "breath": 1.0, "shy": 0.3, "pain": 0.2, "afterglow": 0.10},
        1: {"pleasure": 3.0, "mouth": 1.5, "breath": 1.8, "pain": 0.8, "shy": 0.3, "afterglow": 0.30},
        2: {"pleasure": 3.4, "mouth": 1.6, "breath": 1.4, "shy": 0.6, "pain": 0.3, "afterglow": 4.6},
    },
    "可爱": {
        0: {"pleasure": 1.8, "shy": 1.6, "mouth": 1.4, "breath": 1.0, "pain": 0.3, "afterglow": 0.10},
        1: {"pleasure": 2.6, "breath": 2.0, "shy": 1.2, "mouth": 1.4, "pain": 0.6, "afterglow": 0.30},
        2: {"pleasure": 3.0, "breath": 1.6, "shy": 1.4, "mouth": 1.4, "pain": 0.3, "afterglow": 4.2},
    },
    "无口": {
        0: {"pleasure": 1.6, "shy": 1.0, "mouth": 1.2, "breath": 0.9, "pain": 0.3, "afterglow": 0.10},
        1: {"pleasure": 2.4, "breath": 1.6, "mouth": 1.3, "pain": 0.8, "shy": 0.8, "afterglow": 0.30},
        2: {"pleasure": 2.6, "breath": 1.4, "shy": 1.0, "mouth": 1.2, "pain": 0.4, "afterglow": 5.0},
    },
    "害羞": {
        0: {"shy": 2.6, "mouth": 1.5, "pleasure": 1.2, "breath": 0.8, "pain": 0.4, "afterglow": 0.10},
        1: {"pain": 1.8, "shy": 1.6, "breath": 2.2, "pleasure": 1.6, "mouth": 1.4, "afterglow": 0.30},
        2: {"shy": 2.2, "pleasure": 2.0, "breath": 2.0, "mouth": 1.6, "pain": 0.8, "afterglow": 3.8},
    },
}

def sex_degree_weights(trait=None, degree=None):
    if degree is None:
        return {}
    try:
        d = int(degree)
    except Exception:
        return {}
    tr = trait if trait in SEX_DEGREE_W else DEFAULT_TRAIT
    return dict(SEX_DEGREE_W[tr].get(max(0, min(2, d))) or {})

TEASE_EXPR_BOOST = {
    "成熟": {"flirty": 2.0, "shy": 0.8, "calm": 0.5},
    "可爱": {"shy": 1.9, "flirty": 1.2, "calm": 0.6},
    "无口": {"shy": 1.6, "flirty": 1.4, "calm": 0.7},
    "害羞": {"shy": 2.2, "flirty": 0.9, "calm": 0.5},
}

def expr_weights(trait=None, privacy=None, rng=None, tier=None):
    if privacy is None:
        return {}
    tr = trait if trait in EXPR_W else DEFAULT_TRAIT
    base = dict(EXPR_W[tr].get(band(privacy)) or {})
    if tier == "tease":
        for _k, _m in (TEASE_EXPR_BOOST.get(tr) or {}).items():
            if _k in base:
                base[_k] = base[_k] * _m
    if rng is not None and tr in EXPR_MODE:
        if rng.random() < mode_prob(tr, privacy):
            return dict(EXPR_MODE[tr]["w"])
    return base

if __name__ == "__main__":
    print("场景 %d 个：室内 %d / 室外 %d" % (
        len(PRIVACY),
        sum(1 for s in PRIVACY if s not in
            {"city street", "rooftop", "park", "balcony", "forest", "lake shore",
             "campsite", "beach", "poolside", "pier", "shrine", "summer festival", "onsen"}),
        sum(1 for s in PRIVACY if s in
            {"city street", "rooftop", "park", "balcony", "forest", "lake shore",
             "campsite", "beach", "poolside", "pier", "shrine", "summer festival", "onsen"})))
    print("自检:", selfcheck() or "✓")
    for tr in TRAIT_ACCEPT:
        row = []
        for sc in ("love hotel room", "bedroom", "karaoke room", "cafe", "city street"):
            row.append(f"{sc[:12]}={weight(sc, 'sex', tr):.2f}")
        print(f"  {tr} (sex档): " + "  ".join(row))
