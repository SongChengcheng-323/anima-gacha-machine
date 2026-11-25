try:
    from pools import status_pool as STP
except Exception:
    import status_pool as STP

PHASE_V2_TO_V3 = {
    "base":   "soft",
    "strong": "mid",
    "climax": "climax",
}

EJAC_FORCES_CLIMAX = True

def band_of(phase, ejac=False):
    if ejac and EJAC_FORCES_CLIMAX:
        return "climax"
    return PHASE_V2_TO_V3.get(phase, "")

def status_pair_from_v3(rng, phase, ejac=False, p_mul=1.0, force=False):
    band = band_of(phase, ejac=ejac)
    if not band:
        return "", "", ""
    items = STP.SEX_STATUS.get(band) or []
    if not items:
        return band, "", ""
    p = min(0.98, max(0.0, STP.STATUS_P.get(band, 0.6) * float(p_mul or 1.0)))
    if force:
        p = 1.0
    if rng.random() > p:
        return band, "", ""
    en, cn = rng.choice(items)
    return band, en, cn

def react_from_v3(rng, phase, ejac=False, p_mul=1.0, force=False):
    _band, en, _cn = status_pair_from_v3(rng, phase, ejac=ejac, p_mul=p_mul, force=force)
    return en

def check():
    bad = []
    for ph in PHASE_V2_TO_V3:
        b = PHASE_V2_TO_V3[ph]
        if b not in STP.SEX_STATUS:
            bad.append("映射到不存在的档位：%s → %s" % (ph, b))
        if b not in STP.STATUS_P:
            bad.append("档位 %s 没有概率" % b)
        if not STP.SEX_STATUS.get(b):
            bad.append("档位 %s 是空的" % b)
    for b, items in STP.SEX_STATUS.items():
        for it in items:
            if not (isinstance(it, tuple) and len(it) == 2):
                bad.append("%s 里有不是 (en, cn) 的条目：%r" % (b, it))
            elif not it[0].strip():
                bad.append("%s 里有空串" % b)
    return bad

if __name__ == "__main__":
    import random
    rng = random.Random(1)
    print("状态串适配层 —— 阶段映射：", PHASE_V2_TO_V3)
    print("自检：", check() or "✓ 全过")
    print("\n抽样（每阶段 4 次，看「出/不出」和整串）：")
    for ph in ("base", "strong", "climax"):
        print("  %-7s →" % ph)
        for _ in range(4):
            s = react_from_v3(rng, ph)
            print("     ", s or "（不抽）")
    print("\n射精提档：", react_from_v3(rng, "base", ejac=True) or "（不抽）")
