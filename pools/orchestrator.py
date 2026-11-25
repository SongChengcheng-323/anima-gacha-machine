try:
    from pools import roll_params as _PARAMS
except Exception:
    try:
        from . import roll_params as _PARAMS
    except Exception:
        import roll_params as _PARAMS

META = {
    "id": "orchestrator",
    "cn": "编排层",
    "kind": "machine",
    "tier": "none",
    "parent": None,
    "enabled": True,
    "desc": "按固定顺序串模块：顺序 / ctx / 机位申请制（⚠️ 未接入）",
    "version": "v0.98.0",
    "refs": [],
}

STAGES = [
    ("00", "quality",  "质量前缀",   "@fixed",          True, "固定值，含 1girl ✓"),
    ("01b", "style_front", "画风·画师(前置)", "styles",    True, "⭐ 画师 tag（`@名字`）放**质量词正后方** ✓ 与 style 二选一（同维度只抽一个）"),
    ("01", "tier",     "尺度",       "@tier",           True, "⭐ 最先定 ⇒ 后面每个模块都受影响"),
    ("02", "char",     "角色名",     "characters",      True, "只写名字 ✓ ＋ 男漂也插在这一段（⚠️ 由性爱机申请插入）"),
    ("03", "framing",  "景别",       "@framing",        False, "⛔ 2026-10-14 作者：整体停用（模型不按景别画，大部分其实全身）"),
    ("04", "outfit",   "装备",       "equip_machine",   True, "特征串 + 衣服（只抽衣服 ✗ 不做动作）"),
    ("05", "branch",   "分流四模块", "@branch",         True, "按尺度走其中一个 ✓（**性爱体位也在这里抽**，作者 10-27）"),
    ("05c", "sexstate", "状态/射精",  "@sex",            True, "⭐ 只 sex 档：是否射精 ⇒ 高潮 ⇒ 反应强度；表情层据此定程度"),
    ("06", "scene",    "场景/氛围",  "scenes",          True, "受尺度影响 ✓ ＋ 低私密场合附带人群 ✓"),
    ("06b", "face",    "五官/表情",  "face",            True, "⭐ 吃 scene 的私密度 × 角色性格；只出五官，**视线归姿态层**"),
    ("07", "ambience", "氛围/光线",  "ambience",        True, "⭐ 作者 15:59：时间段/光线/氛围/冷暖/霓虹**归氛围池专门出** ✗ 场景池不许夹带 ✓"),
    ("08", "camera",   "机位",       "@camera",         True, "⭐ **申请制**：模块申请的优先，都没申请机位层才调控 ✓"),
    ("10", "state",    "状态/反应",  "state_pool",      True, "已有 ✓（性爱档才产出 ✓）"),
    ("11", "style",    "画风",       "styles",          True, "✓"),
    ("12", "merge",    "合并",       "@self",           True, "⚠️ 收敛/精简最后再做（）"),
]

_GIRL = "1girl"

DOCTOR_READONLY = True

def _doctor(ctx, rule, removed=None, kept=None, detail=None):
    try:
        rec = {"rule": rule}
        if removed:
            rec["removed"] = list(removed)
        if kept:
            rec["kept"] = list(kept)
        if detail:
            rec["detail"] = detail
        ctx.setdefault("meta", {}).setdefault("doctor", []).append(rec)
    except Exception:
        pass

def _count_hands(txt, base=0):
    try:
        from pools import poses as _PZ
    except Exception:
        import poses as _PZ
    return _PZ.count_hands(txt, base)

def quality_prefix(tier):
    try:
        from pools import styles as ST
    except Exception:
        try:
            from pools import styles as ST
        except Exception:
            import styles as ST
    if tier == "fashion":
        return ST.HEAD_FASHION
    if tier == "sex":
        return ", ".join(x for x in ("masterpiece", "best quality", ST.QUALITY_TAGS,
                                     "uncensored", "ecchi", "explicit", _GIRL) if x)
    if tier == "exposed":
        return ST.HEAD_EXPOSED
    return ST.HEAD

def new_ctx(tier, char, rng, weights=None, solo=None, **kw):
    return {
        "tier": tier,
        "char": char,
        "rng": rng,
        "weights": weights or {},
        "solo": solo,
        "segs": [],
        "by_stage": {},
        "camera_claims": [],
        "outfit_state": None,
        "meta": dict(kw),
    }

def add(ctx, stage, text):
    if not text:
        return
    ctx["segs"].append((stage, text))
    ctx["by_stage"].setdefault(stage, text)

PRIORITY_FROM_MODULE = 100
PRIORITY_FROM_CAMERA_LAYER = 10

def claim_camera(ctx, module, text, priority=PRIORITY_FROM_MODULE):
    if text:
        ctx["camera_claims"].append((module, text, priority))

def resolve_camera(ctx):
    if not ctx["camera_claims"]:
        return ""
    best = sorted(ctx["camera_claims"], key=lambda x: -x[2])[0]
    return best[1]

def assemble(ctx):
    rank = {s[1]: i for i, s in enumerate(STAGES)}
    segs = sorted(ctx["segs"], key=lambda x: rank.get(x[0], 99))
    seen, parts = set(), []
    _chunks, _weird = [], []
    for _seg in segs:
        _v = _seg[1] if isinstance(_seg, (tuple, list)) and len(_seg) > 1 else _seg
        if isinstance(_v, (list, tuple)):
            _weird.append((_seg[0] if isinstance(_seg, (tuple, list)) else "?", repr(_v)[:80]))
            _v = ", ".join(str(x) for x in _v if x)
        if _v is None:
            continue
        _v = str(_v)
        if _v:
            _chunks.append(_v)
    if _weird:
        ctx.setdefault("meta", {})["assemble_weird"] = _weird
    for chunk in _chunks:
        for piece in [x.strip() for x in chunk.split(",") if x.strip()]:
            k = piece.lower()
            if k not in seen:
                seen.add(k)
                parts.append(piece)
    return ", ".join(parts)

def selfcheck(verbose=False):
    problems = []
    keys = [s[1] for s in STAGES]
    if len(keys) != len(set(keys)):
        problems.append("顺序表里有重复的阶段键 ✗")
    if keys[0] != "quality" or keys[-1] != "merge":
        problems.append("顺序表首尾不对（应 quality → merge）✗")
    if not (PRIORITY_FROM_MODULE > PRIORITY_FROM_CAMERA_LAYER):
        problems.append("机位优先级不对：模块给的必须高于机位层自调的 ✗")
    t = new_ctx("sex", "x", None)
    claim_camera(t, "sex_draw", "from the side")
    claim_camera(t, "camera_layer", "from above", PRIORITY_FROM_CAMERA_LAYER)
    if resolve_camera(t) != "from the side":
        problems.append("机位裁决错：前面模块给了侧拍，却被机位层盖掉了 ✗")
    t2 = new_ctx("fashion", "x", None)
    if resolve_camera(t2) != "":
        problems.append("没人申请机位时不该凭空产出 ✗")
    claim_camera(t2, "camera_layer", "from above", PRIORITY_FROM_CAMERA_LAYER)
    if resolve_camera(t2) != "from above":
        problems.append("无人申请时，机位层应该能自己调控 ✗")
    t3 = new_ctx("sex", "x", None)
    add(t3, "state", "panting")
    add(t3, "quality", "masterpiece, 1girl")
    add(t3, "char", "hatsune_miku")
    p = assemble(t3)
    if p != "masterpiece, 1girl, hatsune_miku, panting":
        problems.append(f"拼装顺序不对：{p}")
    known = {"@fixed", "@tier", "@framing", "@branch", "@camera", "@self",
             "sex_draw", "characters", "equip_machine", "scenes", "state_pool", "styles",
             "face", "actions", "ambience", "scene_pool"}
    for _n, _k, _cn, prod, _w, _note in STAGES:
        if prod not in known:
            problems.append(f"阶段 {_n} 的生产者 '{prod}' 不认识 ✗")
    fw = quality_prefix("fashion")
    if "ecchi" in fw or "explicit" in fw:
        problems.append("时尚档前缀混进了 ecchi/explicit ✗（作者 v29.16 明禁）")
    for t in ("fashion", "tease", "exposed", "sex"):
        if _GIRL not in quality_prefix(t):
            problems.append(f"{t} 档前缀缺 1girl ✗")
    for t in ("fashion", "tease", "exposed", "sex"):
        _qp = quality_prefix(t).lower()
        if "solo" in _qp:
            problems.append(f"{t} 档前缀混进了 solo ✗")
        if "score_" in _qp:
            problems.append(f"{t} 档前缀混进了 score_* ✗")
    if verbose:
        print(f"  编排层自检：{'✗ ' + '；'.join(problems) if problems else '✓ 全过'}")
        print(f"    阶段 {len(STAGES)} 个 · 机位优先级 模块{PRIORITY_FROM_MODULE} > 层{PRIORITY_FROM_CAMERA_LAYER}")
    return problems

if __name__ == "__main__":
    import sys
    sys.exit(1 if selfcheck(verbose=True) else 0)

SOLO_P = 0.05
ORIG_OUTFIT_P = 0.10
CAMERA_FILL_P = 0.30

_ORIG_TAKEOVER = ("upper", "lower", "rear", "leg_l", "leg_r", "feet")

def _framing_and_facing(rng, tier):
    if tier == "sex":
        return "", "", ""
    try:
        from pools import layer_tables as LT
    except Exception:
        try:
            from pools import layer_tables as LT
        except Exception:
            import layer_tables as LT
    name = rng.choice(LT.FRAMING)
    vis = LT.FRAMING_VIS.get(name, "full")
    facing = rng.choice(["front", "front", "back"])
    facing_text = ""
    return name, facing, facing_text

def _pick_from(pool, rng, w=None):
    if w:
        return rng.choices(list(pool), weights=list(w), k=1)[0]
    return rng.choice(list(pool))

def run(rng, tier=None, char=None, solo=None, char_pool=None, tier_w=None,
        size=None):
    if tier is None:
        if tier_w:
            tier = rng.choices(list(tier_w), weights=list(tier_w.values()), k=1)[0]
        else:
            try:
                from pools import roll_params as _RP0
            except Exception:
                import roll_params as _RP0
            tier = _RP0.pick_tier(rng)
    try:
        import pool_gate as PG
        rng = PG.FilteredRng(rng, PG.cached())
        ctx_gated = True
    except Exception:
        ctx_gated = False
    if not char:
        try:
            from pools import characters as CH
        except Exception:
            import characters as CH
        pool = char_pool or [c[0] for c in CH.CHARACTERS]
        _w = getattr(CH, "CHARACTER_WEIGHTS", None) or {}
        try:
            _ws = [max(0.0, float(_w.get(c, 1))) for c in pool]
            char = rng.choices(pool, weights=_ws, k=1)[0] if any(_ws) else rng.choice(pool)
        except Exception:
            char = rng.choice(pool)
    ctx = new_ctx(tier, char, rng)
    ctx["meta"]["pool_gate"] = ctx_gated
    ctx["framing"] = None

    add(ctx, "quality", quality_prefix(tier))

    add(ctx, "char", char)
    try:
        from pools import char_traits as _CT
        _tr = (_CT.CHAR_TRAITS.get(char) or {}).get("main") or ""
        ctx["meta"]["traits"] = _tr
    except Exception:
        ctx["meta"]["traits"] = ""
    ctx["_male_tag"] = ""
    if tier == "sex":
        if solo is None:
            _sp = SOLO_P
            try:
                from pools import sex_draw as _SDp
                _sp = _SDp.SOLO_P_BY_TRAIT.get(ctx["meta"].get("traits"),
                                               getattr(_SDp, "SOLO_P_DEFAULT", SOLO_P))
            except Exception:
                pass
            solo = rng.random() < _sp
        _after_p = float(getattr(_PARAMS, "AFTER_P", 0.0) or 0.0)
        ctx["_after"] = bool(_after_p > 0 and rng.random() < _after_p)
        if ctx["_after"]:
            solo = True
        ctx["solo"] = solo
        if not solo:
            try:
                from pools import sex_draw as _SD
            except Exception:
                import sex_draw as _SD
            ctx["_male_tag"] = _SD.MALE_TAG

    try:
        from pools import layer_tables as _LT
        _fr_on = getattr(_LT, "LAYER_FRAMING_ENABLED", True)
    except Exception:
        _LT, _fr_on = None, False
    if _fr_on:
        fr_name, facing, facing_text = _framing_and_facing(rng, tier)
        ctx["meta"]["framing"] = fr_name
        try:
            ctx["meta"]["framing_vis"] = _LT.FRAMING_VIS.get(fr_name, "full")
        except Exception:
            ctx["meta"]["framing_vis"] = "full"
        if fr_name:
            add(ctx, "framing", fr_name)
            if facing_text:
                add(ctx, "framing", facing_text)
    else:
        ctx["meta"]["framing"] = ""
        ctx["meta"]["framing_vis"] = ""
        ctx["meta"]["framing_layer"] = "disabled"
        _, facing, _ = _framing_and_facing(rng, tier)
    ctx["facing"] = facing or "front"

    try:
        from pools import wardrobe_route as WR
        from pools import wardrobe_pools as WP
    except Exception:
        try:
            from pools import wardrobe_route as WR
        except Exception:
            import wardrobe_route as WR
        try:
            from pools import wardrobe_pools as WP
        except Exception:
            import wardrobe_pools as WP
    gt = WR.gear_tier(tier)

    try:
        from pools import characters as CH2
    except Exception:
        import characters as CH2
    _feat = ""
    for row in CH2.CHARACTERS:
        if row and row[0] == char:
            _feat = row[1] or ""
            break
    try:
        from pools import hairstyles as HS
    except Exception:
        import hairstyles as HS
    ctx["meta"]["hair_change"] = rng.random() < getattr(HS, "HAIR_RATE", 0.35)
    if ctx["meta"]["hair_change"]:
        _shape = tuple(getattr(HS, "_SHAPE_WORDS", ()))
        _keep = [t.strip() for t in _feat.split(",") if t.strip()
                 and not any(w in t.lower() for w in _shape)]
        _feat = ", ".join(_keep)
        _opts = getattr(HS, "HAIR_OPTIONS", {}).get(char) or [e for e, _c in getattr(HS, "HAIR_ALL", [])]
        if _opts:
            _hs = rng.choice(_opts)
            add(ctx, "char", _hs)
            ctx["meta"]["hair_style"] = _hs
    if _feat:
        add(ctx, "char", _feat)
    if ctx.get("_male_tag"):
        add(ctx, "char", ctx["_male_tag"])

    judge = WR.route(tier, char, rng)
    cap_g = judge["cap"]["garment"]
    cap_d = judge["cap"]["deco"]

    picks, n_g, n_d = {}, 0, 0
    _deco = list(WR.DECO_SLOTS)
    SLOTS_ALL = list(WR.GARMENT_SLOTS) + _deco + ["chest", "feet", "leg_l"]
    try:
        from pools import wardrobe_sets as WS
    except Exception:
        import wardrobe_sets as WS
    try:
        from pools import characters as _CHW
    except Exception:
        import characters as _CHW

    _set, _force_orig = "", False
    if tier == "fashion":
        if rng.random() < 0.6:
            _cands = list(WS.FASHION_SETS)
            if (getattr(_CHW, "DEFAULT_OUTFIT", {}) or {}).get(char):
                _cands.append("__ORIG__")
            _pick = rng.choice(_cands)
            if _pick == "__ORIG__":
                _force_orig = True
            else:
                _set = _pick
        else:
            _set = "__random__"
    elif tier == "tease":
        _set = (WS.TEASE_SETS[0] if WS.TEASE_SETS else "__random__")
    ctx["meta"]["style_set"] = _set
    ctx["meta"]["wardrobe_mode"] = ("orig" if _force_orig
                                    else ("random" if _set == "__random__"
                                          else ("set" if _set else "none")))

    picks = {} if _force_orig else dict(picks)
    if _force_orig:
        pass
    elif tier == "exposed" or (tier == "sex" and getattr(_PARAMS, "SEX_NAKED", True)):
        picks["chest"] = "naked"
        _gen = WS.generic_slots()
        for _s in ("leg_l", "eyes", "ears", "neck"):
            if _gen.get(_s) and rng.random() < 0.55:
                _it = WS.pick_item(rng, _gen[_s])
                if _it:
                    picks[_s] = _it[0]
        if rng.random() < 0.35:
            _PASTIES = [("pasties", "乳头贴"),
                        ("bandaid on nipple", "乳头创可贴"),
                        ("bandaid on pussy", "小穴创可贴")]
            _pw = rng.choice(_PASTIES)
            picks["bonus"] = ", ".join(x for x in (picks.get("bonus"), _pw[0]) if x)
            ctx["meta"]["pasties"] = _pw[0]
            ctx["meta"]["pasties_cn"] = _pw[1]
    elif _set:
        _filled = WS.fill_from_set(rng, _set, full=(tier != "tease"))
        _up_seq = [(_s, _pair[0]) for _s, _pair in _filled.items()
                   if _s in ("upper_set", "upper_base", "upper_outer")]
        _bonus = _filled.pop("__bonus__", None)
        _sty = _filled.pop("__stylize__", None)
        _bw = [x[0] for x in (_bonus, _sty) if x]
        if _bw:
            picks["bonus"] = ", ".join(_bw)
            ctx["meta"]["lingerie_bonus"] = picks["bonus"]
        for _s, _pair in _filled.items():
            if _s.startswith("upper"):
                continue
            picks[_s] = _pair[0]
        if _up_seq:
            picks["upper"] = ", ".join(x[1] for x in _up_seq)
            ctx["meta"]["upper_kind"] = [x[0] for x in _up_seq]
        n_g = sum(1 for _s in picks if _s in WR.GARMENT_SLOTS)
        n_d = sum(1 for _s in picks if _s not in WR.GARMENT_SLOTS)
    else:
        pass

    if not picks and not _force_orig and tier not in ("exposed", "sex"):
        for slot in SLOTS_ALL:
            w = WP.pick_slot(slot, gt, rng)
            if not w:
                continue
            if slot in WR.GARMENT_SLOTS:
                if cap_g is not None and n_g >= cap_g:
                    continue
                n_g += 1
            else:
                if cap_d is not None and n_d >= cap_d:
                    continue
                n_d += 1
            picks[slot] = w

    _op_only = WR.one_piece_covers(picks.get("upper"))
    _op_cover = set(_op_only)
    if (ctx.get("meta") or {}).get("framing_vis") == "upper" \
            and getattr(_LT, "LAYER_FRAMING_ENABLED", True):
        _op_cover = set(_op_cover) | {"lower", "rear"}
        ctx["meta"]["framing_covers"] = ["lower", "rear"]
    for _cs in _op_cover:
        picks.pop(_cs, None)
    if _op_only:
        ctx["meta"]["one_piece"] = {"upper": picks.get("upper"), "covers": sorted(_op_only)}

    import collections as _C
    def _w(sl):
        _c = [x for x in WP.candidates(sl, gt) if x["en"] == picks.get(sl)]
        return _c[0]["w"][gt] if _c else 0.0
    if cap_g is not None:
        while len([k for k in picks if k in WR.GARMENT_SLOTS]) > cap_g:
            _victim = min([k for k in picks if k in WR.GARMENT_SLOTS], key=_w)
            picks.pop(_victim, None)
    if cap_d is not None:
        _deco_order = ["head", "eyes", "ears", "neck", "hand_l"]
        while len([k for k in picks if k in _deco_order]) > cap_d:
            for _k in _deco_order:
                if _k in picks:
                    picks.pop(_k)
                    break
    ctx["meta"]["caps"] = {"garment": cap_g, "deco": cap_d,
                           "garment_used": len([k for k in picks if k in WR.GARMENT_SLOTS]),
                           "deco_used": len([k for k in picks if k in _deco_order])}

    kept, yielded, _info = WR.resolve(tier, picks, rng)

    for _psl, _pv in (WR.PLACEHOLDER.get(tier) or {}).items():
        if _psl in _op_cover:
            continue
        if not kept.get(_psl) and _pv:
            kept[_psl] = _pv
    if WR.is_long_pants(kept.get("lower")):
        kept.pop("leg_l", None)
        ctx["meta"]["long_pants_no_barelegs"] = True
    if tier == "sex":
        if any(WR.is_one_piece(kept.get(_s)) for _s in ("upper", "lower")):
            if kept.get("feet"):
                kept["feet"] = None
                ctx["meta"]["sex_shoes_off"] = True
        _plays = (ctx.get("_sex_body") or {}).get("plays") or []
        if any(p == "footjob" for p in _plays):
            kept["feet"] = "barefoot"
            kept.pop("leg_l", None)
            ctx["meta"]["footjob_barefoot"] = True

    _orig_do = None

    if tier == "fashion" or _force_orig:
        try:
            from pools import characters as _CHO
        except Exception:
            import characters as _CHO
        _cand = (getattr(_CHO, "DEFAULT_OUTFIT", {}) or {}).get(char)
        if _cand and tier == "sex":
            _HEAVY_O = ("uniform", "blazer", "jacket", "coat", "sweater", "turtleneck",
                        "crewneck", "cardigan", "hoodie", "kimono", "yukata", "suit",
                        "military", "armor", "maid outfit", "nurse")
            if any(_k in _cand.lower() for _k in _HEAVY_O):
                _cand = None
                ctx["meta"]["orig_outfit_skipped"] = "sex 档严实原皮"
        if _cand and (_force_orig or rng.random() < ORIG_OUTFIT_P):
            _orig_do = _cand
    if _orig_do:
        _os = _CHO.split_orig_outfit(_orig_do)
        for _s in _ORIG_TAKEOVER:
            kept[_s] = _os.get(_s) or None
        for _s, _v in _os.items():
            if _s not in _ORIG_TAKEOVER and _v:
                kept[_s] = ", ".join(x for x in (kept.get(_s), _v) if x)
        ctx["meta"]["orig_outfit_used"] = _orig_do
        ctx["meta"]["orig_outfit_slots"] = dict(_os)
        _orig_head = (_os.get("head") or "")
        if _orig_head and kept.get("head"):
            _head_low = kept["head"].lower()
            ctx["meta"]["head_dropped_by_orig"] = kept.pop("head")
            ctx["meta"]["head_kept_orig"] = _orig_head

    def _has_skirt(_txt):
        for _w in (_txt or "").split(","):
            _w = _w.strip().lower()
            if not _w:
                continue
            if WR.is_skirt(_w):
                return True
            if any(_u in _w for _u in getattr(WR, "SKIRT_UNIFORMS", ())):
                return True
        return False
    _sk_top = (kept.get("upper") or "")
    _sk_bot = (kept.get("lower") or "")
    if ((getattr(WR, "SKIRT_BIND_PANTIES", False) or getattr(WR, "TEASE_SKIRT_PANTIES", False))
            and tier in ("fashion", "tease")
            and (_has_skirt(_sk_top) or _has_skirt(_sk_bot))
            and (tier == "tease" or getattr(WR, "SKIRT_BIND_PANTIES", False))):
        _rl = (kept.get("rear") or "").lower()
        if not any(k in _rl for k in WR.PANTY_MARKS):
            _pn = (list(getattr(WR, "PANTY_STYLES", ()))
                   if tier == "tease"
                   else list(getattr(WR, "SKIRT_GUARD_PANTIES", ())))
            _pn = _pn or ["panties"]
            kept["rear"] = ", ".join(x for x in (kept.get("rear"), rng.choice(_pn)) if x)
            ctx["meta"]["skirt_panties"] = kept["rear"]
            ctx["meta"]["skirt_panties_note"] = "裙类 ⇒ 保底 bloomers（防走光）"

    _SLEEVE_SELF = (
        "t-shirt", "tee", "tank top", "camisole", "tube top", "halter", "crop top",
        "sleeveless", "long-sleeve", "long sleeve", "short-sleeve", "short sleeve",
        "off-shoulder", "detached-sleeve", "puff-sleeve", "hoodie", "sweater",
        "cardigan", "blazer", "turtleneck", "sweatshirt", "pullover",
        "topless", "bare breasts", "towel", "bikini", "swimsuit", "one-piece swimsuit",
        "naked apron", "apron only",
    )
    _up_low = (kept.get("upper") or "").lower()
    _has_sleeve = any(k in _up_low for k in _SLEEVE_SELF)
    _upper_only = " only" in _up_low
    ctx["meta"]["attr_skipped"] = "袖型词已退场(2026-10-26)"
    if _upper_only and kept.get("lower"):
        ctx["meta"]["lower_dropped_by_only"] = kept.pop("lower")
        ctx["meta"].setdefault("only_note", "上衣标了 only ⇒ 下装不成立，已撤")

    _CHEST_BARE = ("bare breasts", "nipples visible")
    _REAR_BARE = ("pussy exposed", "anus visible", "bare buttocks")
    _HEAVY_TOP = ("sweater", "turtleneck", "crewneck", "cardigan", "blazer", "hoodie",
                  "sweatshirt", "pullover", "coat", "jacket", "shirt", "vest", "knit")
    _PANTS_KW = ("trousers", "pants", "jeans", "slacks", "shorts")
    _c_low = (kept.get("chest") or "").lower()
    _r_low = (kept.get("rear") or "").lower()
    _u_low = (kept.get("upper") or "").lower()
    _l_low = (kept.get("lower") or "").lower()
    _seen = ", ".join(v for _s, v in ctx.get("segs", [])
                      if _s in ("outfit", "state", "branch")).lower()
    _c_all = _c_low + " " + _seen
    _r_all = _r_low + " " + _seen

    if tier == "tease":
        pass
    elif any(k in _c_all for k in _CHEST_BARE) and _u_low:
        if any(k in _u_low for k in _HEAVY_TOP):
            kept["upper"] = "top pulled up over her breasts"
            ctx["meta"]["chest_yield"] = "严实上衣 ⇒ 推上去"
        elif "bare upper body" in _u_low or _u_low.strip() in ("topless", "bare chest"):
            ctx["meta"]["chest_yield"] = "已裸上身 ⇒ 清袖型"

    if any(k in _r_all for k in _REAR_BARE) and _l_low:
        if any(k in _l_low for k in _PANTS_KW):
            kept["lower"] = "pants pulled down to her knees"
            ctx["meta"]["rear_yield"] = "裤子 ⇒ 褪到膝盖"
        elif "skirt" in _l_low:
            if "lifted" not in _l_low:
                kept["lower"] = _l_low + ", skirt lifted"
            ctx["meta"]["rear_yield"] = "裙子 ⇒ 掀起"

    _SET_LINGERIE = ("bikini", "lingerie set", "one-piece swimsuit", "swimsuit", "bra set")
    if any(k in _u_low for k in _SET_LINGERIE):
        if any(k in _c_all for k in _CHEST_BARE):
            kept["upper"] = "bra pulled aside"
            ctx["meta"]["lingerie_yield_chest"] = "套装内衣 ⇒ 胸罩拨到一边"
        if any(k in _r_all for k in _REAR_BARE):
            if not (kept.get("lower") or "").strip():
                kept["lower"] = "bottoms pulled aside"
            ctx["meta"]["lingerie_yield_lower"] = "套装内衣 ⇒ 下装拨到一边"

    if " only" in _u_low and any(k in _c_low for k in _CHEST_BARE):
        kept["upper"] = "top pulled up over her breasts"
        ctx["meta"]["only_vs_bare"] = "only 与裸胸互斥 ⇒ 改成推上去"

    if kept.get("hand_l"):
        try:
            _occ = _count_hands(", ".join(v for _s, v in ctx["segs"]
                                          if _s in ("pose", "branch", "state")))
        except Exception:
            _occ = 0
        if _occ + _count_hands(kept["hand_l"]) > 2:
            ctx["meta"]["hand_prop_dropped"] = kept.pop("hand_l")

    ctx["meta"]["outfit_kept"] = {k: v for k, v in kept.items() if v}

    for slot in ("upper", "lower", "rear", "chest", "bonus"):
        if kept.get(slot):
            add(ctx, "outfit", kept[slot])
    for w in yielded:
        _wh = _count_hands(w)
        if _count_hands(", ".join(x for _s, x in ctx["segs"] if _s in ("pose", "branch", "state", "outfit"))) + _wh > 2:
            ctx["meta"].setdefault("yield_skipped_hands", []).append(w)
            continue
        add(ctx, "outfit", w)
    for slot in ("head", "eyes", "ears", "neck", "hand_l", "feet", "leg_l"):
        if kept.get(slot):
            add(ctx, "outfit", kept[slot])

    txt = ", ".join(v for _s, v in ctx["segs"] if _s == "outfit")
    try:
        from pools import equip_machine as _EM
        _SL = getattr(_EM, "SLOT_LABEL", {})
    except Exception:
        _SL = {}
    _ORDER = ("upper", "lower", "rear", "chest", "head", "eyes", "ears", "neck",
              "hand_l", "feet", "leg_l")
    _parts = []
    for _sl in _ORDER:
        _v = kept.get(_sl) or ""
        if _v:
            _parts.append("%s：%s" % (_SL.get(_sl, _sl), _v))
    if _parts:
        ctx["meta"]["equip_labeled"] = "，".join(_parts)
    ctx["meta"]["equip"] = {k: v for k, v in kept.items() if v}
    cat = ("nude" if not any(kept.get(x) for x in WR.GARMENT_SLOTS)
           else "lingerie" if any(k in txt.lower() for k in ("lingerie", "panties", "underwear", "bra"))
           else "swim" if any(k in txt.lower() for k in ("bikini", "swimsuit"))
           else "wearing")
    ctx["meta"]["outfit_cat"] = cat
    ctx["meta"]["outfit_text"] = txt
    ctx["meta"]["outfit_full"] = txt
    _CHEST_MARK = ("nipple", "breast", "cleavage", "through the fabric",
                   "see-through", "transparent", "visible through", "pussy", "anus", "buttocks")
    _blob = ", ".join(str(v) for v in kept.values() if v).lower()
    _hit = [k for k in _CHEST_MARK if k in _blob]
    ctx["meta"]["chest_state"] = ", ".join(_hit)
    ctx["meta"]["upper_state"] = ctx["meta"].get("upper_state") or kept.get("upper") or ""

    if tier == "fashion":
        from pools import fashion_draw as M
    elif tier == "tease":
        from pools import tease_draw as M
    elif tier == "exposed":
        from pools import expose_draw as M
    elif tier == "sex":
        M = None
    else:
        raise ValueError("未知档位 %r ✗ —— 不许静默掉进性爱档 ✓(2026-10-12)" % (tier,))
    if M is not None:
        M.pick(ctx)
    else:
        try:
            from pools import sex_draw as SD
        except Exception:
            import sex_draw as SD
        if ctx.get("_after"):
            try:
                from pools import after_draw as AD
            except Exception:
                import after_draw as AD
            body = AD.as_body(rng)
        else:
            body = ctx.get("_sex_body") or SD.draw(rng, solo=ctx.get("solo"),
                                                trait=ctx["meta"].get("traits"))
        ctx["_sex_body"] = body
        ctx["meta"]["sex"] = {"plays": body["plays"], "cn": body["act_cn"]}
        if ctx.get("_after"):
            ctx["meta"]["after"] = dict(body["state_meta"])
            ctx["meta"]["after"]["pose"] = body["act_en"][0] if body["act_en"] else ""
            ctx["meta"]["after"]["trace_en"] = body["state_en"][-1] if body["state_en"] else ""
            ctx["meta"]["sex_degree"] = 2
        for w in body["act_en"]:
            add(ctx, "branch", w)
        for w in body["state_en"]:
            add(ctx, "sexstate", w)
        if body.get("camera"):
            claim_camera(ctx, "sex_draw", body["camera"])
        try:
            from pools import characters as _CHP
        except Exception:
            import characters as _CHP
        _pv = _CHP.pubic_of(ctx.get("char") or "")
        if _pv:
            add(ctx, "branch", _pv)

    try:
        _allvals = [x for _s, x in ctx.get("segs", [])]
        _chest0 = ((ctx.get("meta") or {}).get("outfit_kept") or {}).get("chest") or ""
        if any(WR.is_bare(x) for x in (_allvals + [_chest0])):
            _drop = [x for x in _allvals if WR.is_cloth_mark(x)]
            if _drop:
                _doctor(ctx, "late_cloth_drop", removed=_drop,
                        detail={"stage": "裸露 ⇒ 清隔衣词", "bare": True})
                if not DOCTOR_READONLY:
                    _dset = set(_drop)
                    ctx["segs"] = [(s, x) for (s, x) in ctx["segs"] if x not in _dset]
                    ctx["meta"]["late_cloth_drop"] = _drop
    except Exception as _e:
        ctx["meta"]["late_cloth_drop"] = {"error": "%s: %s" % (type(_e).__name__, _e)}

    try:
        from pools import scene_pool as SCP
        from pools import v3_pools as V3
        from pools import ambience as AMB
        from pools import roll_params as _RP
        from pools import scene_privacy as PR
    except Exception:
        try:
            from pools import scene_pool as SCP
            from pools import v3_pools as V3
        except Exception:
            import scene_pool as SCP
            import v3_pools as V3
        try:
            from pools import ambience as AMB
        except Exception:
            import ambience as AMB
        try:
            from pools import roll_params as _RP
        except Exception:
            import roll_params as _RP
        try:
            from pools import scene_privacy as PR
        except Exception:
            import scene_privacy as PR
    _pose_w = ""
    _branch_txt = " ".join(x for _s, x in ctx.get("segs", []) if _s == "branch")
    try:
        try:
            from pools import pose_quota as _PQ
        except Exception:
            import pose_quota as _PQ
        _CANON = {"站": "standing", "坐": "sitting", "跪": "kneeling",
                  "躺": "lying on her back", "趴": "on all fours", "蹲": "crouching",
                  "flat": "standing"}
        _pc = (ctx.get("meta") or {}).get("pose_cat") or ""
        if _pc in _CANON:
            _pose_w = _CANON[_pc]

        for _s0, _x0 in ctx.get("segs", []):
            if _s0 != "branch":
                continue
            _ws = [w.strip() for w in _x0.split(",") if w.strip()]
            for _n in range(min(4, len(_ws)), 0, -1):
                _cand = ", ".join(_ws[:_n])
                if _cand in _PQ.POSTURES:
                    _pose_w = _cand
                    break
            if _pose_w:
                break
        if not _pose_w:
            _pl0 = (ctx.get("_sex_body") or {}).get("plays") or []
            if _pl0:
                _pose_w = _PQ.pose_of_play(_pl0[0]) or ""
    except Exception:
        pass
    _scat, _splace = "", ""
    _minp = (getattr(_RP, "AFTER_MIN_PRIVACY", None)
             if ctx.get("_after") else None)
    if getattr(_RP, "USE_SCENE_V3", False):
        _scene, _scat, _splace = V3.pick_scene(rng, tier)
        ctx["meta"]["scene_cat"] = _scat
        ctx["meta"]["place"] = _splace
    else:
        _scene = SCP.pick(rng, tier, plays=(ctx.get("_sex_body") or {}).get("plays"),
                          force_place=ctx["meta"].get("scene_force"),
                          trait=ctx["meta"].get("traits"), min_privacy=_minp)
    if _pose_w:
        _v3 = getattr(_RP, "USE_SCENE_V3", False)
        for _try in range(24):
            _pl = (_splace if _v3 else SCP.place_of(_scene))
            try:
                try:
                    from pools import pose_quota as _PQ
                except Exception:
                    import pose_quota as _PQ
            except Exception:
                break
            if _PQ.pose_scene_ok(_pose_w, _scene, _pl):
                break
            if _v3:
                _scene, _scat, _splace = V3.pick_scene(rng, tier)
                ctx["meta"]["scene_cat"] = _scat
                ctx["meta"]["place"] = _splace
            else:
                _scene = SCP.pick(rng, tier, plays=(ctx.get("_sex_body") or {}).get("plays"),
                          force_place=ctx["meta"].get("scene_force"),
                          trait=ctx["meta"].get("traits"), min_privacy=_minp)
        ctx["meta"]["scene_filtered_by_pose"] = _pose_w
    add(ctx, "scene", _scene)
    _prop = ""
    if getattr(_RP, "USE_PROP", True):
        _prop = (V3.pick_prop_v3(rng, tier, _scene)
                 if getattr(_RP, "USE_PROP_V3", False)
                 else SCP.pick_prop(rng, tier, _scene))
    if _prop:
        add(ctx, "scene", _prop)
        ctx["meta"]["scene_prop"] = _prop
    _crowd = PR.crowd_for(rng, _scene, tier)
    if _crowd:
        add(ctx, "scene", _crowd)
        ctx["meta"]["scene_crowd"] = _crowd
    _place = (ctx["meta"].get("place") if getattr(_RP, "USE_SCENE_V3", False)
              else SCP.place_of(_scene))
    _amb = AMB.pick(rng, _place) if getattr(_RP, "USE_AMBIENCE", True) else ""
    if _amb:
        add(ctx, "ambience", _amb)
    ctx["meta"]["scene"] = _scene
    ctx["meta"]["place"] = _place
    ctx["meta"]["ambience"] = _amb
    ctx["meta"]["privacy"] = PR.privacy_of(_scene)
    ctx["meta"]["privacy_band"] = PR.band(ctx["meta"]["privacy"])

    if tier == "sex":
        _sm0 = (ctx.get("_sex_body") or {}).get("state_meta") or {}
        if ctx.get("_after"):
            _deg = 2
        else:
            _deg = 1 if (_sm0.get("ejac") or _sm0.get("orgasm_parts")) else 0
        ctx["meta"]["sex_degree"] = _deg
    if not ctx["camera_claims"]:
        try:
            from pools import layer_tables as LT
        except Exception:
            try:
                from pools import layer_tables as LT
            except Exception:
                import layer_tables as LT
        _ok_ = ctx["meta"].get("outfit_kept") or {}
        _skirt_ = any(WR.is_skirt(_w) for _k in ("upper", "lower")
                      for _w in str(_ok_.get(_k) or "").split(","))
        _squat_ = (ctx["meta"].get("pose_cat") in ("蹲",))
        _cam_pool = LT.CAMERA_ANGLES
        if (tier == "fashion" and _skirt_ and _squat_):
            _cam_pool = ("from above", "from the side")
            ang_text = rng.choice(_cam_pool)
            ctx["meta"]["camera_squat_skirt"] = ang_text
        elif rng.random() >= (0.55 if tier == "tease" else CAMERA_FILL_P):
            ctx["meta"]["camera_skipped"] = True
            ang_text = ""
        else:
            if tier == "tease":
                _tw = [2.6 if a == "from below" else (1.2 if a == "from above" else 1.0)
                       for a in LT.CAMERA_ANGLES]
                ang_text = rng.choices(list(LT.CAMERA_ANGLES), weights=_tw, k=1)[0]
                ctx["meta"]["camera_tease_weighted"] = ang_text
            else:
                ang_text = rng.choice(LT.CAMERA_ANGLES)
        try:
            from pools import pose_quota as _PQ
        except Exception:
            import pose_quota as _PQ
        _try = 0
        _fc = (ctx.get("facing") or "front")
        _facing = (["facing away from the viewer, back turned"] if _fc == "back" else ["front"])
        if ang_text:
            if not ctx["meta"].get("camera_squat_skirt"):
                for _try in range(24):
                    if not _PQ.camera_conflict(_facing, ang_text):
                        break
                    ang_text = rng.choice(_cam_pool)
                ctx["meta"]["camera_interlock"] = {"facing": _facing, "picked": ang_text, "tries": _try}
            claim_camera(ctx, "camera_layer", ang_text, PRIORITY_FROM_CAMERA_LAYER)

    _cam_final = resolve_camera(ctx)
    if _cam_final:
        add(ctx, "camera", _cam_final)

    try:
        from pools import face as FA
    except Exception:
        try:
            from pools import face as FA
        except Exception:
            import face as FA
    _pose_now = ", ".join(v for _s, v in ctx["segs"] if _s in ("branch", "pose"))
    _state_txt = " ".join(v for _s, v in ctx["segs"] if _s in ("state", "sexstate")).lower()
    _state_has_eyes = any(k in _state_txt for k in (
        "eyes closed", "eyes squeezed", "eyes half", "half-lidded", "eyes unfocused"))
    _state_has_smile = any(k in _state_txt for k in ("smile", "laugh", "grin", "smirk"))
    if getattr(_RP, "USE_FACE_V3", False):
        _fd = {}
        _has_male = bool(ctx.get("_male_tag")) or (tier == "sex" and not ctx.get("solo"))
        for _cat in V3.DIM_OF:
            if _cat == "gaze_male" and not _has_male:
                continue
            _fd.setdefault(V3.DIM_OF[_cat], []).append(_cat)
        _allowed = V3.FACE_CAT_BY_TIER.get(tier) or list(V3.FACE_MERGED)
        _eyes_allow = (V3.FACE_DIM_ALLOW.get(tier) or {}).get("eyes")
        face_d, sub = {}, {}
        _expr_cats = [c for c in _fd.get("expression", []) if c in _allowed]
        _expr_word = ""
        if _expr_cats:
            _c = rng.choice(_expr_cats)
            _c2, _expr_word = V3.face_words(tier, "expression", [_c], rng)
            if _expr_word:
                face_d["expression"] = _expr_word
                sub["expression"] = _c2
        _smiling = bool(_expr_word) and any(
            k in _expr_word.lower() for k in ("smile", "laugh", "grin", "smirk"))
        for _dim, _cats in _fd.items():
            if _dim == "expression":
                continue
            if _dim == "eyes":
                if _eyes_allow:
                    _cats = [c for c in _cats if c in _eyes_allow]
                if _smiling:
                    _cats = [c for c in _cats if c != "eyes_closed"]
                if not _cats:
                    continue
            _c = rng.choice(_cats)
            _c2, _w = V3.face_words(tier, _dim, [_c], rng)
            if not _w:
                continue
            _c = _c2
            if _dim == "mouth":
                face_d["mouth"] = _w
            elif _dim == "eyes":
                face_d["eyes"] = _w
            elif _dim == "gaze":
                face_d["gaze"] = _w
            sub[_dim] = _c
        for k in ("expression", "mouth", "eyes", "blush"):
            if face_d.get(k):
                add(ctx, "face", face_d[k])
        add(ctx, "face", face_d.get("gaze") or "")
    else:
        face_d, sub = FA.pick_face(
            rng, tier, pose_text=_pose_now,
            has_male=bool(ctx.get("_male_tag")) or (tier == "sex" and not ctx.get("solo")),
            privacy=ctx["meta"].get("privacy"),
            trait=ctx["meta"].get("traits"),
            sex_degree=ctx["meta"].get("sex_degree"))
        if _state_has_smile:
            _ey = (face_d.get("eyes") or "").lower()
            if any(k in _ey for k in ("closed", "squeezed")):
                face_d["eyes"] = "half-lidded eyes"
                ctx["meta"]["eyes_replaced"] = "状态串已有笑 ⇒ 眼改半闭"
        if _state_has_eyes:
            face_d.pop("eyes", None)
            ctx["meta"]["face_eyes_skipped"] = "状态串已含眼状态"
            _ex = (face_d.get("expression") or "").lower()
            if any(k in _ex for k in ("smile", "laugh", "grin", "smirk")):
                face_d["expression"] = "a pleased satisfied look"
                ctx["meta"]["expr_replaced"] = "状态串闭眼 ⇒ 表情不带笑"
        _fk = ["expression", "mouth", "eyes"] + ([] if (tier == "sex" and getattr(_RP, "USE_STATUS_V3", False)) else ["blush"])
        for k in _fk:
            add(ctx, "face", face_d.get(k) or "")
        add(ctx, "face", face_d.get("gaze") or "")
    ctx["meta"]["face_sub"] = sub

    _sm0 = (ctx.get("_sex_body") or {}).get("state_meta") or {}
    if (tier == "sex" and getattr(_RP, "USE_STATUS_V3", False)
            and not _sm0.get("status_src") and not ctx.get("_after")):
        try:
            from pools import status_pool as STP
            _sm = (ctx.get("_sex_body") or {}).get("state_meta") or {}
            _phy = "climax" if (_sm.get("ejac_ready") or _sm.get("react_phase") == "climax") else ""
            if not _phy:
                _plays = (ctx.get("_sex_body") or {}).get("plays") or []
                _phy = STP.phase_of(_plays[0] if _plays else "",
                                    _sm.get("intensity", "mid"), False)
            _band, _sen, _scn = STP.pick_status(rng, _phy, force=True)
            if _sen:
                add(ctx, "state", _sen)
            ctx["meta"]["status_str"] = {"phase": _phy, "band": _band,
                                         "en": _sen, "cn": _scn}
        except Exception as _e:
            ctx["meta"]["status_str"] = {"error": "%s: %s" % (type(_e).__name__, _e)}

    try:
        from pools import styles as ST
    except Exception:
        try:
            from pools import styles as ST
        except Exception:
            import styles as ST
    _kind, _text, _key = ST.pick_style(rng, ctx.get("tier"), size=size)
    if _kind == "artist":
        add(ctx, "style_front", _text)
    else:
        add(ctx, "style", _text)
    ctx["meta"]["style"] = _key
    ctx["meta"]["style_kind"] = _kind

    try:
        from pools import wardrobe_route as _WR2
    except Exception:
        import wardrobe_route as _WR2
    _ym = set((getattr(_WR2, "YIELD_MARKS", {}) or {}).values())
    _ym |= {"clothing pulled aside"}
    try:
        from pools import body_pool as _BP2
        _ym |= set(_BP2.HANDS.get("拉衣") or [])
        _ym |= {"hem lifted", "skirt lifted", "skirt hem lifted",
                "strap slipped down", "strap slipped off shoulder",
                "lower garment flipped up", "lower garment slightly lifted"}
    except Exception:
        pass
    _yseen = False
    _segs2 = []
    _ydup = []
    for _s, _v in ctx["segs"]:
        if any(y in _v for y in _ym):
            if _yseen:
                _ydup.append(_v)
                if not DOCTOR_READONLY:
                    continue
            _yseen = True
        _segs2.append((_s, _v))
    if _ydup:
        _doctor(ctx, "yield_unique", removed=_ydup,
                detail={"rule_note": "整张图最多一个让位词"})
    ctx["segs"] = _segs2
    _hs = lambda: _count_hands(", ".join(v for _s, v in ctx["segs"]
                                        if _s in ("pose", "branch", "state", "outfit")))
    _SUP_KW = ("propped on her elbows", "supporting her weight", "both hands down")
    _seen_sup = False
    for _s, _v in list(ctx["segs"]):
        if _s not in ("pose", "branch", "state", "outfit"):
            continue
        _pcs = [x.strip() for x in _v.split(",") if x.strip()]
        _hit = [i for i, p in enumerate(_pcs) if any(k in p.lower() for k in _SUP_KW)]
        if not _hit:
            continue
        if _seen_sup:
            _keep4 = [p for i, p in enumerate(_pcs) if i not in _hit]
        else:
            _seen_sup = True
            _keep4 = [p for i, p in enumerate(_pcs) if i not in _hit[1:]]
        if len(_keep4) != len(_pcs):
            ctx["segs"] = [((_s, ", ".join(_keep4)) if (ss == _s and vv == _v and _keep4)
                            else (ss, vv))
                           for ss, vv in ctx["segs"]
                           if not (ss == _s and vv == _v and not _keep4)]
            ctx["meta"].setdefault("support_dedup", []).append(_v)
    _up_now = ""
    _lo_now = ""
    for _sl, _vv in ctx["segs"]:
        if _sl == "outfit":
            _up_now += " " + _vv.lower()
    _TOP_GONE = ("topless", "bare upper body", "bare chest", "naked apron")
    _NEED_TOP = ("unbuttoning", "tugging her neckline", "pulling at her collar",
                 "pulling down her top strap", "slipping under her top")
    if any(k in _up_now for k in _TOP_GONE):
        _drop = []
        for _s, _v in list(ctx["segs"]):
            if _s not in ("pose", "branch", "state", "outfit"):
                continue
            _pieces = [x.strip() for x in _v.split(",") if x.strip()]
            _keep = [x for x in _pieces
                     if not any(k in x.lower() for k in _NEED_TOP)]
            if len(_keep) != len(_pieces):
                _drop.append(_v)
                ctx["segs"] = [((_s, ", ".join(_keep)) if (ss == _s and vv == _v and _keep)
                                else (ss, vv))
                               for ss, vv in ctx["segs"]
                               if not (ss == _s and vv == _v and not _keep)]
        if _drop:
            ctx["meta"]["action_needs_top_dropped"] = _drop

    if _hs() > 2:
        try:
            from pools import poses as _PZ3
        except Exception:
            _PZ3 = None
        if _PZ3 is not None:
            _prop_cut = []
            for _s, _v in list(ctx["segs"]):
                if _s != "outfit":
                    continue
                _pcs = [x.strip() for x in _v.split(",") if x.strip()]
                _keep3 = [x for x in _pcs
                          if not _PZ3.is_carry_prop(x) and "hand fan" not in x.lower()
                          and not x.lower().startswith("holding a bag")]
                if len(_keep3) != len(_pcs):
                    _prop_cut.append(_v)
                    ctx["segs"] = [((_s, ", ".join(_keep3)) if (ss == _s and vv == _v and _keep3)
                                    else (ss, vv))
                                   for ss, vv in ctx["segs"]
                                   if not (ss == _s and vv == _v and not _keep3)]
            if _prop_cut:
                ctx["meta"]["hand_prop_cut"] = _prop_cut
    if _hs() > 2:
        _cands = [v for ss, v in ctx["segs"]
                  if ss in ("outfit", "pose", "branch", "state")
                  and any(ym in v for ym in _ym)]
        _doctor(ctx, "hand_quota", removed=_cands,
                detail={"hands": _hs(), "note": "手数>2，按让位词优先撤（已执行）"})
        _cut = []
        for _s in ("outfit", "pose", "branch", "state"):
            for _x in [v for ss, v in ctx["segs"]
                       if ss == _s and any(ym in v for ym in _ym)]:
                _keepv = ", ".join(p.strip() for p in _x.split(",")
                                   if not any(ym in p.strip() for ym in _ym))
                ctx["segs"] = [((_s, _keepv) if (ss == _s and vv == _x and _keepv) else (ss, vv))
                               for ss, vv in ctx["segs"]
                               if not (ss == _s and vv == _x and not _keepv)]
                _cut.append(_x)
                if _hs() <= 2:
                    break
            if _hs() <= 2:
                break
        if _cut:
            ctx["meta"]["hand_quota_cut"] = _cut

    _SYN = (
        ("neckline", True, ("tugging her neckline", "neckline lower", "pulling at her collar",
                      "pulling her collar", "pulling down her top strap", "unbuttoning her shirt",
                      "hand slipping under her top", "pulling at her clothing")),
        ("skirt",    True, ("lifting her skirt", "holding her skirt hem", "skirt lifted",
                            "hem lifted", "lifting her hem", "skirt hem lifted")),
        ("covering", True, ("covering her chest", "covering between her legs")),
        ("elbow_support", True, ("propped on her elbows", "leaning on her elbows",
                                 "supporting her weight",
                                 "both hands down", "hands down, supporting",
                                 "hands pressing into the", "palms flat on the")),
        ("hair_touch", True, ("adjusting her hair", "brushing hair back", "tying her hair up",
                        "one hand adjusting her hair", "running her hands through")),
        ("panties_item", False, ("underwear visible above her waistband", "white cotton panties",
                          "underwear visible", "panties")),
        ("open_top", False, ("chest area pulled aside", "top pulled up over her breasts",
                      "hands pulling at her collar", "pulling at her collar",
                      "one hand tugging her neckline", "tugging her neckline")),
    )
    for _gname, _enforce, _kw in _SYN:
        _seen = False
        _newsegs = []
        _drop = []
        for _s, _v in ctx["segs"]:
            _parts = [p.strip() for p in _v.split(",") if p.strip()]
            _hit = [i for i, p in enumerate(_parts) if any(k in p.lower() for k in _kw)]
            if not _hit:
                _newsegs.append((_s, _v))
                continue
            if not _seen:
                _seen = True
                _keep = [p for i, p in enumerate(_parts) if i not in _hit[1:]]
            else:
                _keep = [p for i, p in enumerate(_parts) if i not in _hit]
            _drop += [p for i, p in enumerate(_parts) if p not in _keep]
            if _keep:
                _newsegs.append((_s, ", ".join(_keep)))
        if _drop:
            _doctor(ctx, "syn:" + _gname, removed=_drop,
                    detail={"stage": "同义去重(段内按逗号拆)",
                            "same_dimension": bool(_enforce)})
        if _enforce:
            ctx["segs"] = _newsegs

    _SYN_SPECIFIC = (
        ("hair_len",    ("very long hair", "long hair", "medium hair", "short hair")),
        ("ears_pointy", ("long pointy ears", "pointy ears")),
        ("ears_animal", ("long upright animal ears", "animal ears")),
        ("ponytail",    ("high ponytail", "low twintails", "side ponytail", "ponytail")),
        ("earrings",    ("earrings",)),
        ("necklace",    ("necklace",)),
        ("gloves",      ("gloves",)),
        ("choker",      ("choker",)),
        ("hair_orn",    ("hair ornament", "hair flower", "hairclip")),
        ("sidelocks",   ("long sidelocks", "braided sidelocks", "sidelocks")),
        ("thighs",      ("thick thighs", "bare thighs", "thighs")),
    )
    for _gname, _kw in _SYN_SPECIFIC:
        _hits = []
        _segs = []
        for _s, _v in ctx["segs"]:
            _parts = [p.strip() for p in _v.split(",") if p.strip()]
            _segs.append([_s, _parts])
            for _i, _p in enumerate(_parts):
                if any(k in _p.lower() for k in _kw):
                    _hits.append((len(_segs) - 1, _i, _p))
        if len(_hits) <= 1:
            continue
        _best = max(_hits, key=lambda x: (len(x[2]), -_hits.index(x)))
        _drop = {(si, pi) for si, pi, _t in _hits if (si, pi) != (_best[0], _best[1])}
        _doctor(ctx, "syn_specific:" + _gname,
                removed=[t for si, pi, t in _hits if (si, pi) in _drop],
                kept=[_best[2]], detail={"stage": "上下位同义，留最长"})
        if DOCTOR_READONLY:
            continue
        for si, pi in sorted(_drop, reverse=True):
            if pi < len(_segs[si][1]):
                _segs[si][1][pi] = None
        ctx["segs"] = [(_s, ", ".join(p for p in parts if p))
                       for _s, parts in _segs if any(parts)]

    _GENERIC = {
        "tattoo": ("chest tattoo", "forehead tattoo", "thigh tattoo", "back tattoo"),
    }
    for _g, _family in _GENERIC.items():
        _all = set()
        for _s, _v in ctx["segs"]:
            _all |= {p.strip().lower() for p in _v.split(",") if p.strip()}
        if _g not in _all or not (_all & set(_family)):
            continue
        _doctor(ctx, "generic:" + _g, removed=[_g],
                kept=sorted(_all & set(_family)), detail={"stage": "概括词有同族具体词"})
        if DOCTOR_READONLY:
            continue
        ctx["segs"] = [(_s, ", ".join(p for p in (x.strip() for x in _v.split(","))
                                     if p and p.lower() != _g))
                       for _s, _v in ctx["segs"]]

    return assemble(ctx), ctx

def expect_by_tier():
    common = {"quality", "char", "outfit", "branch", "scene", "ambience", "face", "style"}
    if not getattr(_PARAMS, "USE_AMBIENCE", True):
        common -= {"ambience"}
    return {
        "fashion": set(common),
        "tease": set(common),
        "exposed": set(common),
        "sex": (set(common) - {"outfit"}) | {"sexstate"},
    }

def missing_block(tier, key, ctx):
    bs = ctx.get("by_stage") or {}
    _m = ctx.get("meta") or {}
    if key == "branch" and _m.get("after") and (_m["after"].get("pose") in (None, "", "自由姿态")):
        return False
    if bs.get(key) or (key == "style" and bs.get("style_front")):
        return False
    return True

def selfcheck_run(verbose=False):
    import random as _r
    problems = []
    EXPECT_BY_TIER = expect_by_tier()
    rng = _r.Random(20261007)
    miss = {}
    for tier in ("fashion", "tease", "exposed", "sex"):
        for _ in range(60):
            p, c = run(rng, tier=tier)
            if not p:
                problems.append(f"{tier} 跑出空提示词 ✗")
                break
            for b in EXPECT_BY_TIER[tier]:
                if missing_block(tier, b, c):
                    miss.setdefault((tier, b), 0)
                    miss[(tier, b)] += 1
    if miss:
        for (t, b), n in sorted(miss.items()):
            if b == "sexstate" and n <= 6:
                continue
            problems.append(f"{t} 档缺「{b}」{n} 次 ✗")
    try:
        from pools import ambience as _AMB
    except Exception:
        try:
            from pools import ambience as _AMB
        except Exception:
            import ambience as _AMB
    _r2 = _r.Random(4242)
    _leak = 0
    for _ in range(300):
        _p, _c = run(_r2, tier="fashion")
        if _c["meta"].get("place") == "indoor":
            if _c["meta"].get("ambience") in set(_AMB.OUTDOOR_OK):
                _leak += 1
    if _leak:
        problems.append(f"室内场景配到了室外氛围 {_leak} 次 ✗（霓虹/天气不该进室内 ✗）")
    if verbose:
        print(f"  全链路自检：{'✗ ' + '；'.join(problems) if problems else '✓ 全过（四档按档期望块齐全 ✓）'}")
    return problems
