import random

POOL = {
    "tease": [
        ("nipples visible through the fabric", "乳头隔着衣服顶出来", 1.0),
        ("cleavage visible", "领口露出沟", 1.0),
        ("panty line visible through her clothes", "衣服下透出内裤的痕", 0.9),
        ("underwear visible above her waistband", "腰线上面露出内裤边", 0.8),
    ],
    "light": [
        ("one breast slips out of her clothing", "衣服滑下来，露出一边的乳头", 1.0),
        ("a nipple peeking out from her top", "衣服没兜住，露出一点乳头", 1.0),
        ("panties pulled aside, pussy just barely visible", "内裤扒开一条缝，私处露一点点", 0.8),
        ("her bottoms pulled down to her knees, pubic hair visible", "下装褪到膝上，看到一比小白虎", 0.7),
    ],
    "full": [
        ("bare breasts, nipples visible", "乳房裸露，乳头可见", 0.9),
        ("pussy exposed, bare thighs", "私处裸露，光着大腿", 0.6),
    ],
    "self": [
        ("she is touching herself, fingers between her legs", "她自己动手，手指在腿间", 0.4),
        ("she is spreading herself open, legs wide", "她自己扒开双腿", 0.2),
    ],
}

ACCEPT = {
    "soft": {"tease": 1.0, "light": 1.0, "full": 0.25, "self": 0.20},
    "mid":  {"tease": 1.0, "light": 1.0, "full": 0.60, "self": 0.30},
    "hot":  {"tease": 1.0, "light": 1.0, "full": 1.00, "self": 0.80},
}
SOFT = ("害羞", "腼腆", "纯真", "可爱", "内向", "文静", "温柔", "无口", "天然")
HOT = ("成熟", "魅惑", "强势", "大胆", "御姐", "冷艳")
MAX_CARDS = {"soft": 1, "mid": 2, "hot": 2}

def group_of(tnames):
    if any(t in SOFT for t in (tnames or [])):
        return "soft"
    if any(t in HOT for t in (tnames or [])):
        return "hot"
    return "mid"

def plan(rng, tnames=None, char_cn="", force_group=None):
    grp = force_group or group_of(tnames)
    acc = ACCEPT[grp]
    n_max = MAX_CARDS[grp]
    n = 0
    if acc["self"] > 0 and rng.random() < 0.35 * acc["self"]:
        n = 1
    elif rng.random() < (0.75 if grp != "soft" else 0.70):
        n = 1
    if grp != "soft" and n == 1 and rng.random() < 0.45:
        n = 2
    cards = []
    for _ in range(n):
        weights, items = [], []
        for deg, entries in POOL.items():
            a = acc.get(deg, 0.0)
            if a <= 0:
                continue
            for en, cn, w in entries:
                items.append((deg, en, cn))
                weights.append(w * a)
        if not items or sum(weights) <= 0:
            break
        deg, en, cn = rng.choices(items, weights=weights, k=1)[0]
        cards.append((deg, en, cn))
        if grp == "soft":
            break
    meta = {"group": grp, "want": n, "cards": len(cards),
            "degrees": [c[0] for c in cards],
            "accept": acc}
    return cards, meta

def describe(cards):
    return " → ".join(f"[{d}] {c}" for d, _e, c in cards) if cards else "（跳过暴露 ✓ 直接进性爱）"
