try:
    from pools import body_pool as BP
except Exception:
    import body_pool as BP

_HEAD_DROP_CATS = ("低头", "托腮")

_LEG_FORBIDDEN = ("barefoot", "bare feet", "high arch", "soles visible")

def _uniq(seq):
    out = []
    for x in seq:
        if x and x not in out:
            out.append(x)
    return out

def _words(cats, table):
    return _uniq([w for c in cats for w in (table.get(c) or [])])

def _ok_cats(pose, part, table):
    allow = BP._ok_set(pose)
    return [c for c in table if (part, c) in allow]

def _need_ok(pose, part, cats):
    return [c for c in cats if pose in BP.NEED.get((part, c), {pose})]

def head_words(pose):
    cats = [c for c in _ok_cats(pose, "头", BP.HEADS) if c not in _HEAD_DROP_CATS]
    return _words(cats, BP.HEADS)

def hand_words(pose):
    cats = _need_ok(pose, "手", _ok_cats(pose, "手", BP.HANDS))
    return _words(cats, BP.HANDS)

def leg_words(pose):
    cats = _need_ok(pose, "腿", list(BP.LEGS))
    ws = _words(cats, BP.LEGS)
    low = [w.lower() for w in ws]
    return [w for w, lw in zip(ws, low) if not any(k in lw for k in _LEG_FORBIDDEN)]

BODY_POSES = list(BP.POSTURES.keys())

BODY_RULES = {
    p: {"head": head_words(p), "hand": hand_words(p), "leg": leg_words(p)}
    for p in BODY_POSES
}

def summary():
    return {p: {k: len(v) for k, v in r.items()} for p, r in BODY_RULES.items()}

def selfcheck():
    problems = []
    if len(BODY_POSES) != len(BP.POSTURES):
        problems.append(f"BODY_POSES {len(BODY_POSES)} 条 ≠ POSTURES {len(BP.POSTURES)} 条 ✗")
    for p in BODY_POSES:
        r = BODY_RULES.get(p) or {}
        for slot in ("head", "hand", "leg"):
            if not r.get(slot):
                problems.append(f"{p!r} 的 {slot} 是空的 ✗")
        all_words = {w for ws in BP.HANDS.values() for w in ws}
        all_words |= {w for ws in BP.HEADS.values() for w in ws}
        all_words |= {w for ws in BP.LEGS.values() for w in ws}
        for slot in ("head", "hand", "leg"):
            for w in r.get(slot) or []:
                if w not in all_words:
                    problems.append(f"{p!r}.{slot} 里的 {w!r} 不在 body_pool ✗")
    heads_all = {w for ws in BODY_RULES.values() for w in ws["head"]}
    for w in BP.HEADS.get("低头") or []:
        if w in heads_all:
            problems.append(f"低头词 {w!r} 还在 head 里 ✗")
    legs_all = {w.lower() for ws in BODY_RULES.values() for w in ws["leg"]}
    for w in legs_all:
        for k in ("barefoot", "bare feet"):
            if k in w:
                problems.append(f"leg 里混进了穿鞋状态词 {w!r} ✗（那是装备层的维度）")
    return problems

if __name__ == "__main__":
    e = selfcheck()
    s = summary()
    print(f"BODY_POSES {len(BODY_POSES)} 条 / BODY_RULES {len(BODY_RULES)} 条")
    for p, d in s.items():
        print(f"  {p:22s} head {d['head']:2d}  hand {d['hand']:2d}  leg {d['leg']:2d}")
    if e:
        print(f"\n✗ 问题 {len(e)} 处：")
        for x in e:
            print("   ", x)
    else:
        print("\n✓ 自检通过：每个体位 head/hand/leg 都非空 · 无 barefoot · 无低头")
