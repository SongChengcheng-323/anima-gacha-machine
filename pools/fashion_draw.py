import random
try:
    from pools import pose_quota as PQ
except Exception:
    import pose_quota as PQ
try:
    from pools import orchestrator as OR
    from pools import poses as P
    from pools import fashion as FA
    from pools import actions_pool as AP
    from pools import pose_table as _PT
    from pools import body_pool as BP
    from pools import roll_params as _RP
except Exception:
    import orchestrator as OR
    import poses as P
    import fashion as FA
    import actions_pool as AP
    import pose_table as _PT
    import body_pool as BP
    import roll_params as _RP

META = {
    "id": "fashion_draw",
    "cn": "时尚机",
    "kind": "machine",
    "tier": "fashion",
    "parent": None,
    "enabled": True,
    "desc": "时尚档：抽姿势 + 道具（服装归装备机 · 景别裁剪归第⑧阶段）（⚠️ 未接入）",
    "version": "v0.98.0",
    "refs": ["pools.poses", "pools.equip_machine"],
}

def _prop_pool(char=""):
    try:
        from pools import equip_machine as EM
    except Exception:
        import equip_machine as EM
    def _flat(v):
        if not v:
            return []
        if isinstance(v, str):
            return [v]
        if isinstance(v, dict):
            out = []
            for x in v.values():
                if isinstance(x, str):
                    out.append(x)
                elif isinstance(x, (list, tuple)):
                    out += [y for y in x if isinstance(y, str)]
            return out
        return [x for x in v if isinstance(x, str)]

    own = _flat((EM.CHAR_PROPS or {}).get(char, []))
    return [], [], []

PROP_P = (0.55, 0.35, 0.10)

def pick_prop(rng, char=""):
    own, generic, wa = _prop_pool(char)
    buckets = [(own, PROP_P[0]), (generic, PROP_P[1]), (wa, PROP_P[2])]
    buckets = [(b, w) for b, w in buckets if b and w > 0]
    if not buckets:
        return ""
    who = rng.choices([b for b, _w in buckets], weights=[w for _b, w in buckets], k=1)[0]
    return rng.choice(who)

BODY_WEIGHT = {
    "standing": 0.35,
    "leaning back": 1.8, "sitting": 1.8, "reclining": 1.8,
    "kneeling": 1.8, "on all fours": 1.8,
}

def body_weights(framing="full"):
    w = []
    for b in P.BODY_POSES:
        if b == "standing":
            w.append(0.35 if framing == "full" else 0.6)
        elif b in BODY_WEIGHT:
            w.append(BODY_WEIGHT[b])
        else:
            w.append(1.0)
    return w

def pick_pose(rng, framing="full", allow_skirt=True, shoes_on=False, has_bag=True):
    if PQ.USE_POSE_V2:
        return PQ.draw_pose(rng, "fashion", shoes_on=shoes_on,
                            fashion_tail=[FA.FASHION_BODY.get(x) for x in ("head", "hand", "leg")],
                            allow_skirt=allow_skirt, has_bag=has_bag)
    body = rng.choices(P.BODY_POSES, weights=body_weights(framing), k=1)[0]
    fb = FA.FASHION_BODY
    tail = []
    for slot in ("head", "hand", "leg"):
        opts = fb.get(slot) or []
        if opts:
            tail.append(rng.choice(opts))
    return body, tail

def pick_action(rng):
    acts = FA.FASHION_ACTIONS
    wmap = getattr(FA, "FASHION_ACTION_W", {}) or {}
    wts = [wmap.get(a, 1.0) for a in acts]
    return rng.choices(acts, weights=wts, k=1)[0]

def _n_hands(text):
    return P.count_hands(text)

def _wearing_skirt(ctx):
    try:
        from pools import wardrobe_route as WR
    except Exception:
        import wardrobe_route as WR
    return WR.wearing_skirt(ctx.get("meta") or {})

def pick_v3(ctx):
    rng = ctx["rng"]
    tier = ctx["tier"]
    posture, picked = BP.compose(rng, tier, shoes_on=BP.wearing_shoes(ctx))
    words = [posture] + [w for _p, _c, w in picked]
    pose_text = ", ".join(words)
    OR.add(ctx, "branch", pose_text)

    prop = pick_prop(rng, ctx.get("char", ""))
    if prop:
        OR.add(ctx, "branch", prop)

    ctx["meta"]["pose"] = posture
    ctx["meta"]["body_v3"] = [f"{p}.{c}" for p, c, _w in picked]
    ctx["meta"]["prop"] = prop
    ctx["meta"]["action"] = ""
    return {"pose": pose_text, "prop": prop, "action": ""}

def pick(ctx):
    if getattr(_RP, "USE_BODY_V3", False):
        return pick_v3(ctx)
    if ctx.get("tier") != "fashion":
        raise ValueError(f"fashion_draw 只服务 fashion 档，收到 tier={ctx.get('tier')!r} ✗")
    rng = ctx["rng"]
    char = ctx.get("char", "")

    if getattr(_RP, "USE_POSE_POOLS", False):
        try:
            from pools import pose_pools as PP
        except Exception:
            import pose_pools as PP
        _kept = (ctx.get("meta") or {}).get("outfit_kept") or {}
        _have = []
        _POCKET = ("jeans", "trousers", "pants", "slacks", "shorts", "joggers",
                   "sweatpants", "cargo", "overalls", "jacket", "coat", "blazer",
                   "cardigan", "vest", "hoodie", "parka", "bomber")
        _cloth = " ".join(str(_kept.get(_s) or "") for _s in
                          ("upper", "lower", "upper_outer", "upper_base")).lower()
        if any(k in _cloth for k in _POCKET):
            _have.append("pockets")
        if _kept.get("eyes"):
            _have.append("glasses")
        _pose, _cat, _use, _ban = PP.pick_pose(rng, "fashion", tuple(_have))
        _head, _hm = PP.pick_part(rng, "fashion", "head")
        _hand, _gm = PP.pick_part(rng, "fashion", "hand", tuple(_have) + tuple(_use), body=_cat)
        if _hm.get("scene_force") or _gm.get("scene_force"):
            ctx["meta"]["scene_force"] = _hm.get("scene_force") or _gm.get("scene_force")
        _tail = [w for w in (_head, _hand) if w]
        ctx["meta"]["pose_cat"] = _cat
        ctx["meta"]["scene_ban"] = list(_ban)
        ctx["meta"]["pose_pool"] = "fashion"
        ctx["meta"]["pose_use"] = list(_use)
        OR.add(ctx, "branch", ", ".join([_pose] + _tail))
        ctx["meta"]["prop"] = ""
        ctx["meta"]["action"] = ""
        return {"pose": _pose, "prop": "", "action": ""}

    framing = ctx.get("framing") or "full"
    _sk = _wearing_skirt(ctx)
    body, tail = pick_pose(rng, framing, allow_skirt=_sk,
                           shoes_on=BP.wearing_shoes(ctx),
                           has_bag=bool((ctx.get("meta") or {}).get("outfit_kept", {}).get("hand_l")))
    if _n_hands(body) >= 2:
        _HANDWORD = ("hand", "arm", "elbow", "wrist", "palm", "finger")
        _kept_tail = [t for t in tail
                      if _n_hands(t) == 0 and not any(w in t.lower() for w in _HANDWORD)]
        if len(_kept_tail) != len(tail):
            ctx["meta"]["pose_tail_hand_dropped"] = [t for t in tail if _n_hands(t) > 0]
        tail = _kept_tail
    pose_text = ", ".join([body] + tail)
    _used = _n_hands(pose_text)
    _big = (_PT.POSTURES.get(body) or {}).get("big", "")
    _has_bag = bool((ctx.get("meta") or {}).get("outfit_kept", {}).get("hand_l"))
    act, _act_hands = AP.pick(rng, budget=max(0, 2 - _used), tier="fashion", body_big=_big,
                              hands_busy=(_used >= 2), has_bag=_has_bag)
    if not act:
        ctx["meta"]["fashion_act"] = {"budget": 2 - _used, "picked": "", "hands": 0}

    if act and _n_hands(act) > 0:
        _FREE = ("hands relaxed at her sides", "hands hanging naturally, fingers relaxed",
                 "arms hanging loose, casual stance", "arms hanging by her sides, relaxed shoulders")
        _kept = [t for t in tail if t.strip().lower() not in _FREE]
        if len(_kept) != len(tail):
            ctx["meta"]["fashion_free_hand_dropped"] = tail
            tail = _kept

    pose_text = ", ".join([body] + tail)
    if act and "reaching up" in act.lower() and any(
            k in body.lower() for k in ("sitting", "seiza", "kneeling", "lying",
                                        "prone", "crouch", "on all fours", "squat")):
        ctx["meta"]["fashion_act_dropped"] = f"{act}（体态冲突：{body}）"
        act = ""
    if act and _n_hands(pose_text) + _n_hands(act) > 2:
        ctx["meta"]["fashion_act_dropped"] = act
        act = ""
    if pose_text:
        OR.add(ctx, "branch", pose_text)
    if act:
        OR.add(ctx, "branch", act)

    prop = pick_prop(rng, char)
    if prop:
        OR.add(ctx, "branch", prop)

    ctx["meta"]["prop"] = prop
    ctx["meta"]["pose"] = body
    ctx["meta"]["action"] = act
    return {"pose": pose_text, "prop": prop, "action": act}

def selfcheck(verbose=False):
    problems = []
    for b in P.BODY_POSES:
        if b not in P.BODY_RULES:
            problems.append(f"姿势 {b!r} 没有对应的 head/hand/leg 规则 ✗")
    for b in P.BODY_RULES:
        if b not in P.BODY_POSES:
            problems.append(f"规则表里的 {b!r} 不在姿势池里 ✗（改一处漏一处）")
    for slot in ("head", "hand", "leg"):
        if not FA.FASHION_BODY.get(slot):
            problems.append(f"FASHION_BODY 缺 {slot} 槽 ✗")
    if len(body_weights("full")) != len(P.BODY_POSES):
        problems.append("姿势权重表长度与 BODY_POSES 不一致 ✗")
    SCENE_WORDS = ("bed", "wall", "sofa", "couch", "floor", "chair", "grass", "sand", "beach")
    for b in P.BODY_POSES:
        low = b.lower()
        hit = [w for w in SCENE_WORDS if w in low]
        if hit:
            problems.append(f"姿势 {b!r} 夹带了场景词 {hit} ✗")
    if abs(sum(PROP_P) - 1.0) > 1e-9:
        problems.append(f"道具三桶权重之和不是 1（{PROP_P}）✗")
    rng = random.Random(20261007)
    miss = 0
    for _ in range(2000):
        body, tail = pick_pose(rng, "full")
        if body not in P.BODY_POSES and body not in PQ.POSTURES:
            miss += 1
        for i, slot in enumerate(("head", "hand", "leg")):
            if i < len(tail) and tail[i] not in (FA.FASHION_BODY.get(slot) or []):
                miss += 1
    for _ in range(500):
        if pick_action(rng) not in FA.FASHION_ACTIONS:
            miss += 1
    if miss:
        problems.append(f"抽姿势时出现池外词 {miss} 次 ✗")
    try:
        pick({"tier": "sex", "rng": random.Random(1), "char": "x", "segs": [], "by_stage": [],
              "camera_claims": [], "meta": {}})
        problems.append("非时尚档调用居然没报错 ✗")
    except ValueError:
        pass
    if verbose:
        print(f"  时尚机自检：{'✗ ' + '；'.join(problems) if problems else '✓ 全过'}")
        print(f"    姿势 {len(P.BODY_POSES)} 种（带景别权重 ✓）· 时尚专用头/手/腿 "
              f"{[len(FA.FASHION_BODY.get(k) or []) for k in ('head','hand','leg')]} · "
              f"时尚动作 {len(FA.FASHION_ACTIONS)} 条（含 2 条轮空）· 道具三桶 {PROP_P}")
    return problems

if __name__ == "__main__":
    import sys
    sys.exit(1 if selfcheck(verbose=True) else 0)
