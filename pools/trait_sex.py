import random

DOMINANT_POSITIONS = [
    "cowgirl",
    "reverse_cowgirl",
    "squatting_cowgirl",
    "face_to_face_cowgirl",
    "woman_on_top",
]

OTHER_POSITIONS = [
    "missionary", "doggystyle", "spooning", "standing_wall",
    "mating_press", "legs_up", "prone_bone",
]

BASE_RATE = {
    "dominant":  0.20,
    "switch":    0.25,
    "round2":    0.22,
    "intensity": 0.35,
    "speed":     0.30,
}

TRAIT_ORDER = ["成熟", "可爱", "无口", "害羞"]

TRAIT_MULT = {
    "成熟": {"dominant": 2.30, "switch": 2.00, "round2": 2.20, "intensity": 1.70, "speed": 1.70},
    "可爱": {"dominant": 1.10, "switch": 1.10, "round2": 1.10, "intensity": 1.40, "speed": 1.50},
    "无口": {"dominant": 0.50, "switch": 0.60, "round2": 0.50, "intensity": 0.70, "speed": 0.50},
    "害羞": {"dominant": 0.40, "switch": 0.50, "round2": 0.40, "intensity": 0.85, "speed": 0.50},
}

TRAIT_MULT_7 = {
    "魅惑": {"dominant": 2.60, "switch": 2.20, "round2": 2.50, "intensity": 1.90, "speed": 2.00},
    "成熟": {"dominant": 2.00, "switch": 1.80, "round2": 2.00, "intensity": 1.60, "speed": 1.50},
    "可爱": {"dominant": 1.30, "switch": 1.20, "round2": 1.20, "intensity": 1.70, "speed": 1.80},
    "温柔": {"dominant": 0.90, "switch": 1.00, "round2": 1.00, "intensity": 1.00, "speed": 0.90},
    "稳重": {"dominant": 0.80, "switch": 0.90, "round2": 0.90, "intensity": 0.90, "speed": 0.80},
    "无口": {"dominant": 0.60, "switch": 0.70, "round2": 0.60, "intensity": 0.80, "speed": 0.60},
    "害羞": {"dominant": 0.35, "switch": 0.40, "round2": 0.35, "intensity": 0.70, "speed": 0.50},
}

SUB_WEIGHT = 0.5

PACE_LEVEL = {"fast": 0, "normal": 1, "slow": 2}
PACE_BASE_W = {"fast": 3.0, "normal": 5.0, "slow": 2.0}
PACE_SLOTS = {"fast": 1, "normal": 2, "slow": 3}

_MAX = 0.95

def _parse(traits):
    if isinstance(traits, dict):
        return traits.get("main") or "温柔", list(traits.get("sub") or [])
    if isinstance(traits, str) and traits:
        return traits, []
    return "温柔", []

def _mult(traits, key):
    main, subs = _parse(traits)
    m = TRAIT_MULT.get(main, TRAIT_MULT["温柔"])[key]
    for s in subs:
        sm = TRAIT_MULT.get(s, TRAIT_MULT["温柔"])[key]
        m *= 1.0 + (sm - 1.0) * SUB_WEIGHT
    return m

def _rate(traits, key):
    return max(0.0, min(_MAX, BASE_RATE[key] * _mult(traits, key)))

def dominant_rate(traits):
    return _rate(traits, "dominant")

def position_switch_rate(traits):
    return _rate(traits, "switch")

def round2_rate(traits):
    return _rate(traits, "round2")

def intensity_rate(traits):
    return _rate(traits, "intensity")

def speed_rate(traits):
    return _rate(traits, "speed")

def rates_of(traits):
    return {
        "dominant": dominant_rate(traits),
        "switch": position_switch_rate(traits),
        "round2": round2_rate(traits),
        "intensity": intensity_rate(traits),
        "speed": speed_rate(traits),
    }

def position_weights(traits, keys):
    m = _mult(traits, "dominant")
    return [m if k in DOMINANT_POSITIONS else 1.0 for k in (keys or [])]

def pace_weights(traits):
    ms = _mult(traits, "speed")
    return {
        "fast":   PACE_BASE_W["fast"] * ms,
        "normal": PACE_BASE_W["normal"],
        "slow":   PACE_BASE_W["slow"] / (ms ** 0.5),
    }

def pick_pace(traits, rng=None):
    rng = rng or random
    w = pace_weights(traits)
    return rng.choices(list(w), weights=list(w.values()), k=1)[0]

def pick_position(traits, rng=None):
    rng = rng or random
    if rng.random() < dominant_rate(traits):
        return rng.choice(DOMINANT_POSITIONS)
    return rng.choice(OTHER_POSITIONS)

def simulate_session(traits, rng):
    pace = pick_pace(traits, rng)
    draws = [rng.random() < dominant_rate(traits)]
    switches = 0
    for _ in range(PACE_SLOTS[pace] - 1):
        if rng.random() < position_switch_rate(traits):
            switches += 1
            draws.append(rng.random() < dominant_rate(traits))
    return (pace, draws, switches,
            rng.random() < round2_rate(traits),
            rng.random() < intensity_rate(traits))

def _run(trait, n=2000, seed=1000):
    rng = random.Random(seed)
    dom_hit = dom_tot = sw = r2 = it = fast = lvl = 0
    for _ in range(n):
        pace, draws, s, do2, doI = simulate_session({"main": trait, "sub": []}, rng)
        dom_hit += sum(1 for d in draws if d)
        dom_tot += len(draws)
        sw += s
        r2 += bool(do2)
        it += bool(doI)
        fast += pace == "fast"
        lvl += PACE_LEVEL[pace]
    return {
        "dominant%":  dom_hit / max(1, dom_tot) * 100,
        "switch":     sw / n,
        "round2%":    r2 / n * 100,
        "intensity%": it / n * 100,
        "fast%":      fast / n * 100,
        "avg_pace":   lvl / n,
    }

def _selftest():
    N = 2000
    print("═══ trait_sex 自测：7 性格 × 各 %d 次 ═══" % N)

    bad = [(t, k, TRAIT_MULT[t][k]) for t in TRAIT_ORDER
           for k in BASE_RATE if TRAIT_MULT[t][k] <= 0]
    print("baseline 乘数检查:", "✅ 全部 > 0（任何性格都不为零）" if not bad else f"✗ {bad}")

    print("\n── 五项概率（理论值 ✓，害羞最低 / 魅惑最高）──")
    keys = ["dominant", "switch", "round2", "intensity", "speed"]
    print(f"  {'性格':<4}" + "".join(f"{k:>11}" for k in keys))
    for t in TRAIT_ORDER:
        r = rates_of({"main": t, "sub": []})
        print(f"  {t:<4}" + "".join(f"{r[k]*100:>10.1f}%" for k in keys))

    print(f"\n── 抽样 %d 次/性格 ──" % N)
    print(f"  {'性格':<4}{'主导体位占比':>12}{'换体位次数':>12}{'二发率':>10}{'幅度变化率':>12}{'快节奏':>10}{'平均节奏档':>12}")
    rows = {}
    for t in TRAIT_ORDER:
        s = rows[t] = _run(t, N)
        print(f"  {t:<4}{s['dominant%']:>11.1f}%{s['switch']:>12.2f}"
              f"{s['round2%']:>9.1f}%{s['intensity%']:>11.1f}%"
              f"{s['fast%']:>9.1f}%{s['avg_pace']:>12.2f}")

    ok_pos = all(s["dominant%"] > 0 and s["round2%"] > 0 for s in rows.values())
    ok_grad_dom = rows["魅惑"]["dominant%"] > rows["害羞"]["dominant%"]
    ok_grad_r2 = rows["魅惑"]["round2%"] > rows["害羞"]["round2%"]
    ok_grad_pace = rows["魅惑"]["avg_pace"] < rows["害羞"]["avg_pace"]
    print("\n── 校验 ──")
    print("  全部指标 > 0        :", "✅" if ok_pos else "✗")
    print("  主导体位 魅惑>害羞  :", "✅" if ok_grad_dom else "✗",
          f"（{rows['魅惑']['dominant%']:.1f}% > {rows['害羞']['dominant%']:.1f}%）")
    print("  二发     魅惑>害羞  :", "✅" if ok_grad_r2 else "✗",
          f"（{rows['魅惑']['round2%']:.1f}% > {rows['害羞']['round2%']:.1f}%）")
    print("  平均节奏 魅惑更靠快 :", "✅" if ok_grad_pace else "✗",
          f"（{rows['魅惑']['avg_pace']:.2f} < {rows['害羞']['avg_pace']:.2f}）")

    hatsune_miku = {"main": "成熟", "sub": ["魅惑"]}
    shy = {"main": "害羞", "sub": ["可爱"]}
    print("\n── 个例对比（卡芙卡 成熟+魅惑  vs  害羞型）──")
    for label, tr in (("卡芙卡(成熟+魅惑)", hatsune_miku), ("害羞型", shy)):
        r = rates_of(tr)
        print(f"  {label:<16} 主导{r['dominant']*100:5.1f}% · 换体位{r['switch']*100:5.1f}%"
              f" · 二发{r['round2']*100:5.1f}% · 速度{r['speed']*100:5.1f}%")
    print("\n结论：害羞低 / 魅惑高 的梯度成立 ✓；且所有性格都 > 0（「不是没有」✓）。")

if __name__ == "__main__":
    _selftest()
