import random

META = {
    "id": "ambience",
    "cn": "氛围池",
    "kind": "pool",
    "tier": "none",
    "parent": None,
    "enabled": True,
    "desc": "氛围/光线/冷暖/霓虹；按场所互斥（⚠️ 未接入）",
    "version": "v0.99.0",
    "refs": [],
}

INDOOR_OK = [
    "soft natural light",
    "warm lamp light",
    "dim candle light",
    "bright even lighting",
    "dim indoor lighting",
    "cool blue tone",
    "warm amber tone",
    "deep shadow, low key",
    "harsh fluorescent light",
]

OUTDOOR_OK = [
    "overcast day, soft diffused light",
    "early morning, soft warm light",
    "late morning, bright clear daylight",
    "noon, crisp overhead light",
    "afternoon, golden warm light",
    "golden hour, warm rim light",
    "dusk, soft ambient glow",
    "evening warm streetlights",
    "night cool moonlight",
    "after rain, soft grey light",
    "light snow, cool pale light",
    "spring breeze, dappled light",
    "warm sunset light",
    "starry night",
    "neon lighting colorful",
    "foggy morning, hazy light",
]

AMBIENCE = INDOOR_OK + OUTDOOR_OK

AMB_W = {
    "neon lighting colorful": 0.3,
    "neon signs colorful glow": 0.0,
}

def pick(rng, place="indoor"):
    pool = OUTDOOR_OK if place == "outdoor" else INDOOR_OK
    pool = list(pool or INDOOR_OK)
    if not pool:
        return ""
    w = [AMB_W.get(x, 1.0) for x in pool]
    if sum(w) <= 0:
        return rng.choice(pool)
    return rng.choices(pool, weights=w, k=1)[0]

def candidates(place="indoor"):
    return list(OUTDOOR_OK if place == "outdoor" else INDOOR_OK)
