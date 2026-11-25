import random

PACE_RANGE = {"fast": (4, 4), "normal": (4, 6), "slow": (5, 8)}
PACE_WEIGHT = {"fast": 3, "normal": 5, "slow": 2}

PLANS = {
    "fast":   ["undress", "insert", "intensity", "climax"],
    "normal": ["foreplay", "insert", "position", "climax"],
    "slow":   ["bath", "foreplay", "foreplay", "insert", "position", "intensity", "climax"],
}
FILL = {"fast": ["intensity"], "normal": ["foreplay", "intensity"],
        "slow": ["position", "afterglow"]}

INTENSITY_WORDS = [
    "moving faster", "thrusting deeper", "harder thrusts", "hips slapping",
    "gripping the sheets", "legs interlocked", "arched back", "trembling thighs",
    "biting her lip, holding on", "breathless, speeding up",
]

CLIMAX_RATE = 0.85
WHERE_BY_POS = {
    "missionary":       ["inside her pussy", "on her stomach", "on her chest"],
    "doggystyle":       ["inside her pussy", "on her back", "on her ass"],
    "cowgirl":          ["inside her pussy", "on her stomach", "on her chest"],
    "reverse_cowgirl":  ["inside her pussy", "on her back"],
    "spooning":         ["inside her pussy", "on her thigh"],
    "standing_wall":    ["inside her pussy", "on her stomach"],
    "fellatio":         ["in her mouth", "on her face", "on her tongue"],
    "paizuri":          ["on her chest", "on her face"],
    "handjob":          ["on her hand", "on her stomach"],
    "footjob":          ["on her feet", "on her legs"],
    "anal":             ["inside her ass", "on her back"],
}
WHERE_DEFAULT = ["on her stomach", "on her chest", "on the sheets"]

def pick_pace(rng, pace=None):
    if pace in PACE_RANGE:
        return pace
    keys = list(PACE_WEIGHT)
    return rng.choices(keys, weights=[PACE_WEIGHT[k] for k in keys], k=1)[0]

def plan_beats(rng, branch="clothed_quick", pace=None, pos=None):
    pace = pick_pace(rng, pace)
    lo, hi = PACE_RANGE[pace]
    beats = list(PLANS[pace])

    if branch == "undress_bath":
        beats = [b for b in beats if b != "bath"] or beats
    elif branch in ("clothed_quick",) and pace == "fast":
        beats[0] = "undress"

    while len(beats) < lo:
        beats.insert(beats.index("climax"), rng.choice(FILL[pace]))
    if pace != "fast":
        while len(beats) < hi and rng.random() < 0.45:
            beats.insert(beats.index("climax"), rng.choice(FILL[pace]))
    beats = beats[:hi]

    if "insert" in beats and not {"position", "intensity"} & set(beats):
        beats.insert(beats.index("climax"), rng.choice(FILL[pace]))

    do_climax = rng.random() < CLIMAX_RATE
    where = rng.choice(WHERE_BY_POS.get(pos or "", WHERE_DEFAULT)) if do_climax else None
    if not do_climax and "climax" in beats:
        beats[beats.index("climax")] = "intensity"

    round2 = False
    if do_climax and pace in ("normal", "slow") and len(beats) + 2 <= hi and rng.random() < 0.22:
        beats = beats[:beats.index("climax") + 1] + ["afterglow", "round2", "climax"][:hi - len(beats) - (beats.index("climax") + 1) + 1]
        beats = [b for b in beats][:hi]
        round2 = True

    if "insert" in beats and "climax" in beats:
        _i, _c = beats.index("insert"), beats.index("climax")
        if _i < _c:
            _mid = beats[_i + 1:_c]
            rng.shuffle(_mid)
            beats = beats[:_i + 1] + _mid + beats[_c:]
    return {"pace": pace, "beats": beats, "climax": do_climax, "where": where,
            "round2": round2, "count": len(beats)}

def render_beat(beat, rng, pos=None):
    return {
        "undress":   rng.choice(["clothing pulled open", "pants pulled down", "undressing"]),
        "bath":      rng.choice(["bathroom, bathtub, wet", "shower, steam, wet hair"]),
        "foreplay":  rng.choice(["handjob", "fellatio", "paizuri", "licking"]),
        "insert":    "penetration",
        "position":  "position change",
        "intensity": rng.choice(INTENSITY_WORDS),
        "climax":    "ejaculation" + (f", {WHERE_BY_POS.get(pos or '', [''])[0]}" if pos else ""),
        "afterglow": rng.choice(["panting, lying together", "cum on her body", "hugging"]),
        "round2":    "getting hard again, starting over",
    }.get(beat, beat)

if __name__ == "__main__":
    import collections
    rng = random.Random(1000)
    cnt, cnt2, cnt3, where, r2 = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), 0
    N = 3000
    for _ in range(N):
        b = rng.choice(["clothed_quick", "undress_bath", "naked_bed", "car_clothed"])
        r = plan_beats(rng, b, pos="doggystyle")
        cnt[r["pace"]] += 1
        cnt2[r["count"]] += 1
        cnt3[r["climax"]] += 1
        if r["where"]:
            where[r["where"]] += 1
        r2 += r["round2"]
    print(f"═══ 抽样 {N} 条 ═══")
    print("节奏档分布:", {k: f"{v*100/N:.0f}%" for k, v in cnt.most_common()})
    print("章数分布  :", dict(sorted(cnt2.items())))
    bad = [k for k in cnt2 if not (4 <= k <= 8)]
    print("  区间检查: ", "✅ 全部 4~8 张" if not bad else f"✗ 越界 {bad}")
    print("  各档区间: ", {p: PACE_RANGE[p] for p in PACE_RANGE})
    print("射精比例  :", {k: f"{v*100/N:.0f}%" for k, v in cnt3.items()})
    print("射在哪里  :", {k: v for k, v in where.most_common(4)})
    print(f"二发比例  : {r2*100/N:.0f}%")
    print()
    for pace in ("fast", "normal", "slow"):
        r = plan_beats(random.Random(7), "undress_bath", pace=pace, pos="cowgirl")
        print(f"  {pace:<7} {r['count']} 章 → {' → '.join(r['beats'])}  | 射: {r['where']}")
