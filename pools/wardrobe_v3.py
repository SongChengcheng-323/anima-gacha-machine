try:
    from pools import v3_pools as V3
except Exception:
    import v3_pools as V3

W = V3.WARDROBE

_LAYER = {
    "fashion": ("fashion",),
    "tease":   ("fashion", "tease"),
    "exposed": ("fashion", "tease", "exposed"),
    "sex":     ("fashion", "tease", "exposed"),
}

def _ban(slot):
    return set((W.get(slot) or {}).get("sex_ban") or [])

def pool(slot, tier):
    d = W.get(slot) or {}
    out = []
    for k in _LAYER.get(tier, ("fashion",)):
        out.extend(d.get(k) or [])
    if tier == "sex":
        ban = _ban(slot)
        out = [w for w in out if w not in ban]
    seen, uniq = set(), []
    for w in out:
        if w not in seen:
            seen.add(w)
            uniq.append(w)
    return uniq

def upper(tier, rng):
    p = pool("upper", tier)
    return rng.choice(p) if p else ""

def lower(tier, rng):
    p = pool("lower", tier)
    return rng.choice(p) if p else ""

def under(tier, rng):
    p = pool("under", tier)
    return rng.choice(p) if p else ""

def legwear(tier, rng):
    p = pool("legwear", tier)
    return rng.choice(p) if p else ""

def shoes(tier, rng):
    p = pool("shoes", tier)
    return rng.choice(p) if p else ""

def headwear(tier, rng):
    p = pool("headwear", tier)
    return rng.choice(p) if p else ""

def neckwear(tier, rng):
    p = pool("neckwear", tier)
    return rng.choice(p) if p else ""

def accessory(tier, rng):
    p = pool("accessory", tier)
    return rng.choice(p) if p else ""

def handwear(tier, rng):
    p = pool("handwear", tier)
    return rng.choice(p) if p else ""

def set_names(tier, rng):
    p = pool("set", tier)
    return rng.choice(p) if p else ""

def covers_chest(word):
    return word in set((W.get("upper") or {}).get("cover") or [])

def is_sex_ban(slot, word):
    return word in _ban(slot)

def upper_exposed(tier, rng, need_expose=False):
    p = pool("upper", tier)
    if need_expose:
        p = [w for w in p if not covers_chest(w)]
    return rng.choice(p) if p else ""

def selfcheck():
    errs = []
    for slot in ("upper", "lower", "under", "legwear", "shoes",
                 "headwear", "neckwear", "accessory", "handwear", "set"):
        if slot not in W:
            errs.append(f"缺槽位 {slot}")
            continue
        for tier in ("fashion", "tease", "exposed", "sex"):
            if not pool(slot, tier):
                if slot == "under" and tier == "fashion":
                    continue
                errs.append(f"{slot}/{tier} 候选为空")
    for w in (W.get("upper") or {}).get("sex_ban") or []:
        if w in pool("upper", "sex"):
            errs.append(f"sex 档没排掉严实上衣: {w}")
    return errs

if __name__ == "__main__":
    e = selfcheck()
    for slot in ("upper", "lower", "under", "legwear", "shoes", "headwear",
                 "neckwear", "accessory", "handwear", "set"):
        print(f"  {slot:10s} " + "  ".join(
            f"{t}={len(pool(slot, t)):3d}" for t in ("fashion", "tease", "exposed", "sex")))
    if e:
        print(f"\n✗ {len(e)} 处问题：")
        for x in e:
            print("   ", x)
    else:
        print("\n✓ 自检通过")
