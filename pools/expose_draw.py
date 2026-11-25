import io
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
    "id": "expose_draw",
    "cn": "暴露机",
    "kind": "machine",
    "tier": "exposed",
    "parent": None,
    "enabled": True,
    "desc": "暴露档：露点/程度（带角色接受度）+ 露点描述 + 相应动作；全裸露占位归装备机（⚠️ 未接入）",
    "version": "v0.98.0",
    "refs": ["pools.expose", "pools.eros", "pools.poses"],
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
        return BP.compose_pair(rng, "exposed", shoes_on=shoes_on)
    if PQ.USE_POSE_V2:
        return PQ.draw_pose(rng, 'exposed', allow_skirt=allow_skirt, shoes_on=shoes_on)
    body = rng.choices(P.BODY_POSES, weights=body_weights(framing), k=1)[0]
    rules = P.BODY_RULES.get(body) or {}
    tail = [rng.choice(rules[s]) for s in ("head", "hand", "leg") if rules.get(s)]
    return body, tail

def pick(ctx):
    if ctx.get("tier") != "exposed":
        raise ValueError(f"expose_draw 只服务 exposed 档，收到 tier={ctx.get('tier')!r} ✗")
    rng = ctx["rng"]
    framing = ctx.get("framing") or "full"
    facing = ctx.get("facing") or "front"
    try:
        from pools import wardrobe_route as _WR
    except Exception:
        import wardrobe_route as _WR
    _sk = _WR.wearing_skirt(ctx.get("meta") or {})

    try:
        from pools import pose_pools as _PPB
    except Exception:
        import pose_pools as _PPB
    _bond = _PPB.pick_bondage(rng, "exposed")
    if _bond:
        ctx["meta"]["pose_cat"] = "bondage"
        ctx["meta"]["pose_pool"] = "bondage"
        ctx["meta"]["bondage"] = _bond
        OR.add(ctx, "branch", _bond)
        return {"pose": _bond, "cards": [], "unit": ""}

    if getattr(_RP, "USE_POSE_POOLS", False):
        try:
            from pools import pose_pools as PP
        except Exception:
            import pose_pools as PP
        _kept = (ctx.get("meta") or {}).get("outfit_kept") or {}
        _have = []
        if _kept.get("eyes"):
            _have.append("glasses")
        _act, _fm = PP.pick_flat(rng, "exposed")
        _head, _hm = PP.pick_part(rng, "exposed", "head")
        if _fm.get("scene_force") or _hm.get("scene_force"):
            ctx["meta"]["scene_force"] = _fm.get("scene_force") or _hm.get("scene_force")
        ctx["meta"]["pose_cat"] = "flat"
        ctx["meta"]["pose_pool"] = "exposed_flat"
        pose_text = ", ".join([w for w in (_act, _head) if w])
    else:
        body, tail = pick_pose(rng, framing, allow_skirt=_sk,
                                shoes_on=BP.wearing_shoes(ctx))
        pose_text = ", ".join([body] + tail)
    OR.add(ctx, "branch", pose_text)

    tnames = (ctx.get("meta") or {}).get("traits") or None
    cards, meta = EX.plan(rng, tnames=tnames, char_cn=ctx.get("meta", {}).get("char_cn", ""))
    chest_said = bool((ctx.get("meta") or {}).get("chest_state"))
    _CHEST_KW = ("breast", "nipple", "chest", "cleavage", "through the fabric", "slipping off")
    dropped = []
    _kept_outfit = (ctx.get("meta") or {}).get("outfit_kept") or {}
    _has_lower = bool(_kept_outfit.get("lower"))
    for _deg, en, _cn in cards:
        if (not _has_lower) and ("waistband" in en.lower()):
            dropped.append(en)
            continue
        _has_upper = bool(_kept_outfit.get("upper"))
        _CLOTH_DEP = ("through the fabric", "through her clothes", "through her clothing",
                      "panty line", "waistband", "slips out of her clothing",
                      "slipping out of her clothing", "underwear visible",
                      "visible above her waistband", "under her clothes")
        if (not _has_upper) and (not _has_lower) and any(k in en.lower() for k in _CLOTH_DEP):
            dropped.append(en)
            continue
        if chest_said and any(k in en.lower() for k in _CHEST_KW):
            dropped.append(en)
            continue
        if "pubic hair" in en.lower():
            try:
                from pools import characters as _CH
            except Exception:
                import characters as _CH
            _tg = ctx.get("char") or ""
            _pv = _CH.pubic_of(_tg)
            if _pv:
                OR.add(ctx, "branch", _pv)
            elif _CH.is_small_bust(_tg):
                OR.add(ctx, "branch", "her bottoms pulled down to her knees")
                dropped.append(en)
            else:
                OR.add(ctx, "branch", en)
            continue
        OR.add(ctx, "branch", en)
    ctx["meta"]["expose_dropped"] = dropped

    unit = ""
    ctx["meta"]["expose"] = {"cat": outfit_cat(ctx), "degrees": meta.get("degrees"),
                             "unit": unit, "chest_from_equip": bool(chest_said)}
    return {"pose": pose_text, "cards": cards, "unit": unit}

def selfcheck(verbose=False):
    problems = []
    for deg in ("tease", "light", "full", "self"):
        if deg not in EX.POOL:
            problems.append(f"expose.POOL 缺 {deg} 档 ✗")
            continue
        for it in EX.POOL[deg]:
            if len(it) != 3:
                problems.append(f"expose.POOL[{deg}] 条目结构不对（应为 3 元组）：{it}")
                break
    for grp in ("soft", "mid", "hot"):
        acc = EX.ACCEPT.get(grp)
        if not acc:
            problems.append(f"expose.ACCEPT 缺 {grp} ✗")
            continue
        for deg in ("tease", "light", "full", "self"):
            if deg not in acc:
                problems.append(f"expose.ACCEPT[{grp}] 缺 {deg} 档 ✗")
    if EX.MAX_CARDS.get("soft") != 1:
        problems.append(f"可爱系格数上限应为 1，实际 {EX.MAX_CARDS.get('soft')} ✗")
    if not E.EROS_EXPOSED_UNITS:
        problems.append("EROS_EXPOSED_UNITS 是空的 ✗")
    import ast as _ast
    _tree = _ast.parse(io.open(__file__, encoding="utf-8").read())
    _calls = [n.func.attr for n in _ast.walk(_tree)
              if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Attribute)]
    if "pick_eros_units" in _calls:
        problems.append("暴露机又在调 eros 单元了 ✗（该维度应由装备机独占）")
    _KW = ("breast", "nipple", "chest", "cleavage", "through the fabric")
    _fake = {"tier": "exposed", "rng": random.Random(3), "segs": [], "by_stage": {},
             "camera_claims": [], "meta": {"chest_state": "bare breasts"},
             "framing": "full", "facing": "front"}
    pick(_fake)
    _txt = " ".join(x[1] for x in _fake["segs"]).lower()
    if any(k in _txt for k in _KW):
        problems.append(f"装备机已说胸，本机仍出了胸相关词 ✗：{[x[1] for x in _fake['segs']][:3]}")
    try:
        pick({"tier": "tease", "rng": random.Random(1), "segs": [], "by_stage": {},
              "camera_claims": [], "meta": {}})
        problems.append("非暴露档调用居然没报错 ✗")
    except ValueError:
        pass
    rng = random.Random(20261007)
    allwords = {en for deg in EX.POOL for en, _cn, _w in EX.POOL[deg]}
    bad = over_soft = 0
    heavy = {"soft": 0, "hot": 0}
    for i in range(2000):
        grp = "soft" if i % 2 == 0 else "hot"
        names = ["可爱", "害羞", "温柔"] if grp == "soft" else ["成熟", "魅惑", "御姐"]
        cards, _m = EX.plan(rng, tnames=names)
        if grp == "soft" and len(cards) > EX.MAX_CARDS["soft"]:
            over_soft += 1
        for deg, en, _cn in cards:
            if en not in allwords:
                bad += 1
            if deg in ("full", "self"):
                heavy[grp] += 1
    if bad:
        problems.append(f"抽到池外词 {bad} 次 ✗")
    if over_soft:
        problems.append(f"可爱系超出格数上限 {over_soft} 次 ✗")
    if not heavy["hot"] > heavy["soft"]:
        problems.append(f"可爱系的重档出现率没有低于成熟系（soft {heavy['soft']} / hot {heavy['hot']}）✗")
    if verbose:
        print(f"  暴露机自检：{'✗ ' + '；'.join(problems) if problems else '✓ 全过'}")
        print(f"    程度池 4 档（{[len(EX.POOL[d]) for d in ('tease','light','full','self')]} 条）"
              f" · 露点单元 {len(E.EROS_EXPOSED_UNITS)} 条 · 接受度 3 组")
    return problems

if __name__ == "__main__":
    import sys
    sys.exit(1 if selfcheck(verbose=True) else 0)
