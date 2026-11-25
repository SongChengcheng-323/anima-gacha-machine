import random
try:
    from pools import pose_quota as PQ
except Exception:
    import pose_quota as PQ
try:
    from pools import orchestrator as OR
    from pools import poses as P
    from pools import body_pool as BP
    from pools import roll_params as _RP
    from pools import eros as E
    from pools import expose as EX
except Exception:
    import orchestrator as OR
    import poses as P
    import body_pool as BP
    import roll_params as _RP
    import eros as E
    import expose as EX

META = {
    "id": "tease_draw",
    "cn": "擦边机",
    "kind": "machine",
    "tier": "tease",
    "parent": None,
    "enabled": True,
    "desc": "擦边档：擦边保底（达标判定，不硬塞）+ 姿势；眼神归 face 层 flirty 池（⚠️ 未接入）",
    "version": "v0.98.0",
    "refs": ["pools.eros", "pools.poses"],
}

OUTFIT_CATS = ("wearing", "lingerie", "swim", "semi", "nude")

def outfit_cat(ctx):
    cat = (ctx.get("meta") or {}).get("outfit_cat")
    if cat in OUTFIT_CATS:
        return cat
    outf = ((ctx.get("meta") or {}).get("outfit_text") or "").lower()
    if any(k in outf for k in ("completely nude", "nude,", " nude", "topless")):
        return "nude"
    if any(k in outf for k in ("bikini", "swimsuit", "one-piece swim")):
        return "swim"
    if any(k in outf for k in ("lingerie", "bra", "panties", "underwear", "garter")):
        return "lingerie"
    if any(k in outf for k in ("micro", "sheer", "open front", "unbuttoned")):
        return "semi"
    return "wearing"

BODY_WEIGHT = {"standing": 0.35, "leaning back": 1.8, "sitting": 1.8,
               "reclining": 1.8, "kneeling": 1.8, "on all fours": 1.8}

def body_weights(framing="full"):
    return [0.35 if b == "standing" and framing == "full" else
            (0.6 if b == "standing" else BODY_WEIGHT.get(b, 1.0))
            for b in P.BODY_POSES]

def pick_pose(rng, framing="full", allow_skirt=True, shoes_on=False):
    if getattr(_RP, "USE_BODY_V3", False):
        return BP.compose_pair(rng, "tease", shoes_on=shoes_on)
    if PQ.USE_POSE_V2:
        return PQ.draw_pose(rng, 'tease', allow_skirt=allow_skirt, shoes_on=shoes_on)
    body = rng.choices(P.BODY_POSES, weights=body_weights(framing), k=1)[0]
    rules = P.BODY_RULES.get(body) or {}
    tail = [rng.choice(rules[s]) for s in ("head", "hand", "leg") if rules.get(s)]
    return body, tail

_ENOUGH_KW = (
    "wet", "damp",
    "blush",
    "lean", "bend", "stoop",
    "unbutton", "unzip", "pull open", "pulled open", "collar", "slip",
    "cleavage", "see-through", "through the fabric", "transparent",
    "underboob", "strap",
)

def _wearing_skirt(ctx):
    try:
        from pools import wardrobe_route as WR
    except Exception:
        import wardrobe_route as WR
    return WR.wearing_skirt(ctx.get("meta") or {})

def teasing_enough(text, face_text=""):
    blob = f"{text} {face_text}".lower()
    hits = sorted({k for k in _ENOUGH_KW if k in blob})
    return bool(hits), hits

def pick(ctx):
    if ctx.get("tier") != "tease":
        raise ValueError(f"tease_draw 只服务 tease 档，收到 tier={ctx.get('tier')!r} ✗")
    rng = ctx["rng"]
    framing = ctx.get("framing") or "full"
    facing = ctx.get("facing") or "front"
    _sk = _wearing_skirt(ctx)

    try:
        from pools import pose_pools as _PPB
    except Exception:
        import pose_pools as _PPB
    _bond = _PPB.pick_bondage(rng, "tease")
    if _bond:
        ctx["meta"]["pose_cat"] = "bondage"
        ctx["meta"]["pose_pool"] = "bondage"
        ctx["meta"]["bondage"] = _bond
        OR.add(ctx, "branch", _bond)
        return {"pose": _bond, "prop": "", "action": _bond}

    if getattr(_RP, "USE_POSE_POOLS", False):
        try:
            from pools import pose_pools as PP
        except Exception:
            import pose_pools as PP
        _kept = (ctx.get("meta") or {}).get("outfit_kept") or {}
        _have = ["pockets"] if (_kept.get("upper") or _kept.get("lower")) else []
        _ut = [t.strip() for t in str(_kept.get("upper") or "").lower().split(",") if t.strip()]
        _lt = [t.strip() for t in str(_kept.get("lower") or "").lower().split(",") if t.strip()]
        _LING = ("bra", "bikini", "panties", "naked", "towel", "swimsuit",
                 "one-piece", "leotard", "thong", "bloomers")
        if any(not any(k in t for k in _LING) for t in _ut + _lt):
            _have.append("garment")
        _STRAP = ("bra", "camisole", "lingerie", "babydoll", "nightgown", "negligee",
                  "chemise", "slip dress", "sundress", "swimsuit", "one-piece",
                  "bikini", "leotard", "tank")
        if any(k in t for t in _ut for k in _STRAP):
            _have.append("straps")
        if _kept.get("eyes"):
            _have.append("glasses")
        _pose, _cat, _use, _ban = PP.pick_pose(rng, "tease", tuple(_have))
        _head, _hm = PP.pick_part(rng, "tease", "head")
        _hand, _gm = PP.pick_part(rng, "tease", "hand", tuple(_have) + tuple(_use), body=_cat)
        _u = str(_kept.get("upper") or "").lower()
        _l = str(_kept.get("lower") or "").lower()
        _NO_SKIRT = ("swimsuit", "bikini", "leotard", "bodysuit", "one-piece", "towel")
        _UNIFORM = ("serafuku", "nurse", "maid", "police", "military", "uniform",
                    "skirt", "dress", "nightgown", "chemise", "negligee", "babydoll")
        _blocked = any(k in _u or k in _l for k in _NO_SKIRT)
        if not _blocked and (_wearing_skirt(ctx)
                             or any(k in _u for k in _UNIFORM)
                             or any(k in _l for k in _UNIFORM)):
            _have.append("skirt")
        _extra, _em = PP.pick_part(rng, "tease", "extra", tuple(_have))
        if _hm.get("scene_force") or _gm.get("scene_force"):
            ctx["meta"]["scene_force"] = _hm.get("scene_force") or _gm.get("scene_force")
        ctx["meta"]["pose_cat"] = _cat
        ctx["meta"]["pose_pool"] = "tease"
        ctx["meta"]["scene_ban"] = list(_ban)
        pose_text = ", ".join([w for w in (_pose, _head, _hand, _extra) if w])
        OR.add(ctx, "branch", pose_text)
        return {"pose": pose_text, "prop": "", "action": ""}

    body, tail = pick_pose(rng, framing, allow_skirt=_sk,
                            shoes_on=BP.wearing_shoes(ctx))
    pose_text = ", ".join([body] + tail)
    OR.add(ctx, "branch", pose_text)

    if getattr(_RP, "USE_BODY_V3", False):
        grp = guard_group((ctx.get("meta") or {}).get("traits") or None)
        guard = ""
        n_hands = 0
        ctx["meta"]["tease_guard"] = {"group": grp, "word": "", "hands": 0,
                                      "skipped": "v3 身体池自带擦边类目"}
    else:
        tnames = (ctx.get("meta") or {}).get("traits") or None
        grp = guard_group(tnames)
        _gpool = [w for w in TEASE_GUARD[grp] if _sk or "skirt" not in w.lower()] or TEASE_GUARD[grp]
        guard = rng.choice(_gpool)
        ok, n_hands = check_guard_hand_quota(pose_text, guard)
        if not ok:
            for _ in range(8):
                cand = rng.choice(_gpool)
                ok, n_hands = check_guard_hand_quota(pose_text, cand)
                if ok:
                    guard = cand
                    break
            else:
                guard = ""
        if guard:
            OR.add(ctx, "branch", guard)
        ctx["meta"]["tease_guard"] = {"group": grp, "word": guard, "hands": n_hands}

    cat = outfit_cat(ctx)
    outf = (ctx.get("meta", {}).get("outfit_text") or "").lower()

    face_text = ctx.get("by_stage", {}).get("face", "")
    enough, why = teasing_enough(pose_text + " " + outf, face_text)
    unit = ""
    if not enough:
        unit = E.pick_eros_units(rng, E.EROS_TEASE_UNITS, cat=cat,
                                 framing=framing, facing=facing, want=2, allow_skirt=_sk)
    chest_said = bool((ctx.get("meta") or {}).get("chest_state"))
    _CHEST_KW = ("breast", "nipple", "chest", "cleavage", "through the fabric",
                 "see-through", "transparent", "visible through")
    kept, dropped = [], []
    for _u in [x.strip() for x in (unit or "").split(",") if x.strip()]:
        (dropped if (chest_said and any(k in _u.lower() for k in _CHEST_KW)) else kept).append(_u)
    if not kept:
        for _try in range(6):
            _u2 = E.pick_eros_units(rng, E.EROS_TEASE_UNITS, cat=cat,
                                    framing=framing, facing=facing, want=2, allow_skirt=_sk)
            _k2 = [x.strip() for x in (_u2 or "").split(",") if x.strip()
                   and not (chest_said and any(k in x.lower() for k in _CHEST_KW))]
            if _k2:
                kept, unit = _k2, _u2
                break
    if not kept:
        _cands = [w for _g in TEASE_GUARD.values() for w in _g
                  if w != guard and any(k in w.lower() for k in _ENOUGH_KW)]
        if _cands:
            _extra = rng.choice(_cands)
            kept = [_extra]
            ctx["meta"]["tease_fallback"] = _extra
    if kept:
        OR.add(ctx, "branch", ", ".join(kept))
    _e2, _w2 = teasing_enough(pose_text + " " + outf + " " + ", ".join(kept), face_text)
    ctx["meta"]["tease_dropped"] = dropped
    ctx["meta"]["tease"] = {"cat": cat, "enough": enough, "why": why, "unit": unit,
                            "final_enough": bool(_e2), "final_why": _w2}
    return {"pose": pose_text, "eros": unit}

def selfcheck(verbose=False):
    problems = []
    if not E.EROS_TEASE_UNITS:
        problems.append("EROS_TEASE_UNITS 是空的 ✗")
    for t in E.EROS_TEASE_UNITS:
        if len(t) != 5:
            problems.append(f"福利单元结构不对（应为 5 元组）：{t}")
            break
    for b in P.BODY_RULES:
        if b not in P.BODY_POSES:
            problems.append(f"BODY_RULES 里的 {b!r} 不在 BODY_POSES ✗")
    if len(body_weights("full")) != len(P.BODY_POSES):
        problems.append("姿势权重表长度与 BODY_POSES 不一致 ✗")
    ok1, _ = teasing_enough("damp clothes clinging to her body", "blushing")
    if not ok1:
        problems.append("「湿身 + 脸红」居然判成不够 ✗（已约定这个就算擦边）")
    ok2, _ = teasing_enough("leaning forward", "collar open")
    if not ok2:
        problems.append("「低下身子 + 拉开领口」居然判成不够 ✗（已约定不露点也算）")
    ok3, _ = teasing_enough("standing, hands relaxed at her sides", "soft smile")
    if ok3:
        problems.append("干净的日常姿势被判成「够擦边」了 ✗（会漏掉真保底）")
    for grp in ("soft", "mid", "hot"):
        g = TEASE_GUARD.get(grp) or []
        if len(g) < 5:
            problems.append(f"保底姿态 {grp} 组只有 {len(g)} 种")
        for w in g:
            if len(w.split()) > 6 or any(k in w.lower() for k in ("with a", "at the", "that ")):
                problems.append(f"保底姿态 {w!r} 不是标签形式 ✗")
    if _n_hands("hands in her pockets") != 2:
        problems.append("双手类词没被计成 2 只手 ✗（手部配额会形同虚设）")
    if _n_hands("hand adjusting her hair") < 1:
        problems.append("撩头发类没被计入占手 ✗")
    if check_guard_hand_quota("hands in her pockets", "hand adjusting her hair")[0]:
        problems.append("互斥没生效：插兜 + 撩头发应判超配额 ✗")
    if not check_guard_hand_quota("standing", "hand adjusting her hair")[0]:
        problems.append("互斥过严：空姿势 + 单手动作应判合法 ✗")
    _KW = ("breast", "nipple", "chest", "cleavage", "through the fabric", "see-through")
    _fake = {"tier": "tease", "rng": random.Random(3), "segs": [], "by_stage": {},
             "camera_claims": [], "meta": {"chest_state": "breast, see-through"},
             "framing": "full", "facing": "front"}
    pick(_fake)
    _txt = " ".join(str(x[1]) for x in _fake["segs"]).lower()
    if any(k in _txt for k in _KW):
        problems.append("装备机已说胸，擦边机仍出了胸相关词 ✗：" + str([x[1] for x in _fake["segs"]][:4]))
    try:
        pick({"tier": "fashion", "rng": random.Random(1), "segs": [], "by_stage": {},
              "camera_claims": [], "meta": {}})
        problems.append("非擦边档调用居然没报错 ✗")
    except ValueError:
        pass
    rng = random.Random(20261007)
    miss = 0
    for _ in range(2000):
        body, tail = pick_pose(rng, "full")
        if body not in P.BODY_POSES and body not in PQ.POSTURES:
            miss += 1
        if PQ.USE_POSE_V2:
            continue
        rules = P.BODY_RULES.get(body) or {}
        for i, slot in enumerate(("head", "hand", "leg")):
            if i < len(tail) and tail[i] not in (rules.get(slot) or []):
                miss += 1
    if miss:
        problems.append(f"抽姿势出现池外词 {miss} 次 ✗")
    if verbose:
        print(f"  擦边机自检：{'✗ ' + '；'.join(problems) if problems else '✓ 全过'}")
        print(f"    福利单元 {len(E.EROS_TEASE_UNITS)} 条 · 姿势 {len(P.BODY_POSES)} 种")
    return problems

TEASE_GUARD = {
    "soft": [
        "hands covering her chest",
        "one hand covering her chest",
        "hands covering between her legs",
        "hands on her lap",
    ],
    "mid": [
        "hands pulling at her collar",
        "hand holding her skirt hem",
        "one hand tugging her neckline",
    ],
    "hot": [
        "pulling at her collar",
        "lifting her skirt",
        "pulling down her top strap",
        "hand slipping under her top",
        "unbuttoning her shirt",
        "tugging her neckline lower",
    ],
}
GUARD_GROUP_BY_TIER = {"soft": "soft", "mid": "mid", "hot": "hot"}

def guard_group(tnames=None):
    names = " ".join(tnames or [])
    if any(k in names for k in EX.SOFT):
        return "soft"
    if any(k in names for k in EX.HOT):
        return "hot"
    return "mid"

def _n_hands(text, base=0):
    return P.count_hands(text, base)

def check_guard_hand_quota(pose_text, guard_text, max_hands=2):
    n = _n_hands(pose_text, _n_hands(guard_text))
    return n <= max_hands, n

if __name__ == "__main__":
    import sys
    sys.exit(1 if selfcheck(verbose=True) else 0)
