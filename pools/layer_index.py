import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

OUT = os.path.join(_ROOT, "taglib_layer.json")

LAYER_ORDER = ["L00", "L01b", "L01", "L02", "L04", "L05", "L05c",
               "L06", "L09", "L07", "L08", "L10", "L11", "L12"]

LAYER_LABEL = {
    "L00": "00 · 质量前缀",
    "L01b": "01b · 画风 / 画师",
    "L01": "01 · 尺度",
    "L02": "02 · 角色",
    "L04": "04 · 装备",
    "L05": "05 · 姿态 / 动作",
    "L05c": "05c · 状态 / 射精",
    "L06": "06 · 场景",
    "L07": "07 · 氛围 / 光线",
    "L08": "08 · 机位",
    "L09": "06b · 表情",
    "L10": "10 · 状态",
    "L11": "11 · 画风",
    "L12": "12 · 合并",
}

def _load_cn():
    try:
        with open(os.path.join(_ROOT, "taglib_cn.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

_CN = _load_cn()

def _cn(word, own=None):
    return (own or _CN.get(word) or word).strip()

def _split_items(words, seen, cn_map=None):
    out = []
    for w in words:
        for part in str(w or "").split(","):
            part = part.strip()
            if not part or part in seen:
                continue
            seen.add(part)
            out.append({"en": part, "cn": (cn_map or {}).get(part) or _cn(part)})
    return out

def _leaves(v, out=None):
    if out is None:
        out = []
    if isinstance(v, str):
        if v.strip() and len(v.split()) <= 6:
            out.append(v)
    elif isinstance(v, dict):
        for x in v.values():
            _leaves(x, out)
    elif isinstance(v, (list, tuple, set)):
        for x in v:
            _leaves(x, out)
    return out

def _layer_quality():
    from pools import orchestrator as OR
    words, seen = [], set()
    for tier in ("fashion", "tease", "exposed", "sex"):
        words += _split_items([OR.quality_prefix(tier)], seen)
    return [{"key": "quality", "label": "质量前缀", "tier": "general", "items": words}]

def _layer_style():
    from pools import styles as S
    subs = []
    seen = set()
    items = []
    for k in (S.ACTIVE_STYLES or []):
        items += _split_items([k], seen)
        items += _split_items([(S.STYLES or {}).get(k, "")], seen)
    if items:
        subs.append({"key": "style_recipe", "label": "画风", "tier": "general", "items": items})
    artists = []
    w = getattr(S, "STYLE_W_BY_TIER", {}) or {}
    for tier, mp in w.items():
        for k in (mp or {}):
            k = str(k)
            if k.startswith("artist:"):
                a = k.split(":", 1)[1]
                if a not in [x["en"] for x in artists]:
                    artists.append({"en": a, "cn": _cn(a, "画师·" + a)})
    if artists:
        subs.append({"key": "style_artist", "label": "画师", "tier": "general", "items": artists})
    return subs

def _layer_tier():
    subs = []
    for k, lab in (("fashion", "时尚"), ("tease", "擦边"),
                   ("exposed", "暴露"), ("sex", "性爱")):
        subs.append({"key": "tier_" + k, "label": lab, "tier": k,
                     "items": [{"en": k, "cn": lab}]})
    return subs

def _layer_char():
    from pools import characters as CH
    names, feats = [], []
    nseen, fseen = set(), set()
    for d in (CH.CHARACTERS or []):
        tag = d[0] if isinstance(d, (tuple, list)) else (d.get("tag") or "")
        if not tag or tag in nseen:
            continue
        nseen.add(tag)
        names.append({"en": tag, "cn": _cn(tag)})
        blob = d[1] if isinstance(d, (tuple, list)) and len(d) > 1 else ""
        _own = []
        for w in str(blob or "").split(","):
            w = w.strip()
            if not w:
                continue
            if w not in _own:
                _own.append(w)
            if w not in fseen:
                fseen.add(w)
                feats.append({"en": w, "cn": _cn(w)})
        CHAR_FEATS[tag] = _own
    subs = [{"key": "char_name", "label": "角色", "tier": "general", "items": names}]
    return subs

CHAR_FEATS = {}

def _layer_outfit():
    from pools import wardrobe_sets as WS
    subs = []
    for name, d in (WS.SETS or {}).items():
        items, seen = [], set()
        for slot, arr in (d.get("slots") or {}).items():
            for it in arr:
                en = it[0] if isinstance(it, (tuple, list)) else it.get("en")
                cn = it[1] if isinstance(it, (tuple, list)) and len(it) > 1 else None
                if not en or en in seen:
                    continue
                seen.add(en)
                items.append({"en": en, "cn": _cn(en, cn)})
        if items:
            subs.append({"key": "outfit_" + name, "label": d.get("cn") or name,
                         "tier": d.get("tier") or "fashion", "items": items})
    try:
        braw = []
        for _k, arr in (WS.BONUS or {}).items():
            for it in arr:
                braw += _leaves(it[0] if isinstance(it, (tuple, list)) else it)
        bitems = _split_items(braw, set())
        if bitems:
            subs.append({"key": "outfit_bonus", "label": "附带判定", "tier": "tease",
                         "items": bitems})
    except Exception as e:
        print("⚠️ 附带判定失败：%s" % e, file=sys.stderr)
    return subs

def _layer_pose():
    from pools import pose_pools as PP
    subs = []
    for tier, spec in (PP.POSES or {}).items():
        if spec.get("flat"):
            items, seen = [], set()
            for it in spec["flat"]:
                if it.get("en") and it["en"] not in seen:
                    seen.add(it["en"])
                    items.append({"en": it["en"], "cn": _cn(it["en"], it.get("cn"))})
            if items:
                subs.append({"key": "pose_%s_flat" % tier, "label": "平铺动作",
                             "tier": tier, "items": items})
        for cat, d in (spec.get("cats") or {}).items():
            items = []
            for it in (d.get("items") or []):
                en = it.get("en")
                if en:
                    items.append({"en": en, "cn": _cn(en, it.get("cn"))})
            if items:
                subs.append({"key": "pose_%s_%s" % (tier, cat), "label": cat,
                             "tier": tier, "items": items})
        for part, lab in (("head", "头部"), ("hand", "手部"), ("extra", "裙底")):
            items, seen = [], set()
            for it in (spec.get(part) or []):
                en = it.get("en")
                if not en or en in seen:
                    continue
                seen.add(en)
                items.append({"en": en, "cn": _cn(en, it.get("cn"))})
            if items:
                subs.append({"key": "pose_%s_%s" % (tier, part), "label": lab,
                             "tier": tier, "items": items})
    try:
        from pools import sex_pool as SPX
        items, seen = [], set()
        for k, v in (getattr(SPX, "SEX_POOL", {}) or {}).items():
            en = v.get("canon") or ""
            if not en or en in seen:
                continue
            seen.add(en)
            items.append({"en": en, "cn": _cn(en, v.get("cn"))})
        if items:
            subs.append({"key": "pose_sex_position", "label": "性爱体位",
                         "tier": "sex", "items": items})
    except Exception:
        pass
    try:
        from pools import after_draw as AD
        _ai = [{"en": p["en"], "cn": p["cn"]} for p in AD.AFTER_POSES]
        if _ai:
            subs.append({"key": "pose_after", "label": "事后姿态", "tier": "sex", "items": _ai})
    except Exception:
        pass
    try:
        from pools import pose_quota as PQ
        for name, d in (PQ.POSTURES or {}).items():
            cat = d.get("big") or ""
            ws = d.get("w") or ()
            for idx, tier in enumerate(("fashion", "tease", "exposed", "sex")):
                if idx < len(ws) and ws[idx] > 0 and cat:
                    key = "pose_%s_%s" % (tier, cat)
                    hit = [x for x in subs if x["key"] == key]
                    if not hit:
                        hit = [{"key": key, "label": cat, "tier": tier, "items": []}]
                        subs.append(hit[0])
                    seen = {i["en"] for i in hit[0]["items"]}
                    hit[0]["items"] += _split_items([name], seen)
        for tier, spec in (PP.POSES or {}).items():
            pass
    except Exception as e:
        print("⚠️ pose_quota 补充失败：%s" % e, file=sys.stderr)
    try:
        from pools import actions_pool as AP
        for it in (AP.ACTIONS or []):
            en = it.get("en") if isinstance(it, dict) else None
            if not en:
                continue
            for tier in (it.get("tiers") or ("fashion", "tease")):
                key = "pose_%s_hand" % tier
                hit = [x for x in subs if x["key"] == key]
                if hit:
                    seen = {i["en"] for i in hit[0]["items"]}
                    hit[0]["items"] += _split_items([en], seen)
    except Exception as e:
        print("⚠️ actions_pool 补充失败：%s" % e, file=sys.stderr)
    return subs

def _layer_state():
    from pools import state_pool as ST
    raw = []
    for attr in ("REACT_LIB", "REACT_HOT", "THRUST_WORDS", "CROTCH_PLAYS",
                 "MALE_PLAYS", "PENIS_PLAYS", "SELF_PLAYS", "MILD_PLAYS",
                 "FACING", "MOUNT", "BREATH", "FRONT_PARTS", "BACK_PARTS",
                 "SIDE_PARTS", "EJAC_LOCAL", "EJAC_POSITION", "ORGASM_LEVEL_P"):
        if hasattr(ST, attr):
            raw += _leaves(getattr(ST, attr))
    items = _split_items(raw, set())
    return [{"key": "state_sex", "label": "状态", "tier": "sex", "items": items}] if items else []

def _layer_sexstate():
    from pools import status_pool as STP
    from pools import state_pool as ST
    raw = []
    for part in (getattr(STP, "SEX_STATUS", {}) or {}).values():
        for it in part or []:
            if isinstance(it, (tuple, list)) and it:
                raw.append(str(it[0]))
            elif isinstance(it, str):
                raw.append(it)
    for attr in ("EJAC_LOCAL", "EJAC_POSITION", "ORGASM_LEVEL_P"):
        if hasattr(ST, attr):
            raw += _leaves(getattr(ST, attr))
    try:
        from pools import after_draw as AD
        raw += [w for w, _cn in AD.AFTER_STATE]
        for _part in AD.AFTER_TRACES.values():
            raw += [w for w, _cn in _part["words"]]
    except Exception:
        pass
    items = _split_items(raw, set())
    return [{"key": "sexstate", "label": "状态 / 射精", "tier": "sex", "items": items}] if items else []

def _layer_face_extra():
    from pools import face as F
    from pools import cameras as C
    raw = []
    for attr in ("FACE_BY_TIER", "FACE_DAILY", "FACE_FLIRTY", "FACE_POOLS",
                 "FACE_SEX", "GAZE_RARE"):
        if hasattr(F, attr):
            raw += _leaves(getattr(F, attr))
    if hasattr(C, "GAZE_WORDS"):
        raw += _leaves(C.GAZE_WORDS)
    return _split_items(raw, set())

def _layer_props():
    from pools import scene_pool as SP
    ws = sorted(x for x in (getattr(SP, "PROPS", frozenset()) or []) if isinstance(x, str))
    items = _split_items(ws, set())
    return [{"key": "scene_prop", "label": "道具", "tier": "general", "items": items}] if items else []

def _layer_scene():
    from pools import scene_pool as SP
    items = [{"en": w, "cn": _cn(w)} for w in (getattr(SP, "SCENES", []) or [])]
    subs = [{"key": "scene_place", "label": "场景", "tier": "general", "items": items}] if items else []
    try:
        from pools import scene_privacy as SPR
        _cw = [v["en"] for v in SPR.CROWD_WORDS.values()]
    except Exception:
        _cw = []
    _ci = _split_items(_cw, set())
    if _ci:
        subs.append({"key": "scene_crowd", "label": "人群", "tier": "general", "items": _ci})
    return subs

def _layer_ambience():
    from pools import ambience as A
    items = [{"en": w, "cn": _cn(w)} for w in (getattr(A, "AMBIENCE", []) or [])]
    return [{"key": "amb_light", "label": "光线", "tier": "general", "items": items}] if items else []

def _layer_camera():
    from pools import composition as C
    subs = []
    for attr, lab in (("ANGLES", "机位"), ("LENSES", "镜头"), ("POSITIONS", "构图")):
        blk = getattr(C, attr, {}) or {}
        vals = list(blk.values()) if isinstance(blk, dict) else list(blk)
        items, seen = [], set()
        for v in vals:
            for w in str(v).split(","):
                w = w.strip()
                if w and w not in seen:
                    seen.add(w)
                    items.append({"en": w, "cn": _cn(w)})
        if items:
            subs.append({"key": "cam_" + attr.lower(), "label": lab,
                         "tier": "general", "items": items})
    return subs

def _layer_face():
    from pools import v3_pools as V3
    items, seen = [], set()
    for _k, v in (getattr(V3, "FACE_MERGED", {}) or {}).items():
        for w in (v or []) if isinstance(v, (list, tuple)) else [v]:
            w = str(w).strip()
            if w and w not in seen:
                seen.add(w)
                items.append({"en": w, "cn": _cn(w)})
    return [{"key": "face_expr", "label": "表情", "tier": "general", "items": items}] if items else []

_GAZE_MARK = ("looking", "gaze", "stare", "glance", "eye contact", "bedroom eyes")

def _is_gaze(w):
    return any(k in str(w).lower() for k in _GAZE_MARK)

def _gaze_items():
    from pools import v3_pools as V3
    from pools import face as F
    raw = []
    for k, v in (getattr(V3, "FACE_MERGED", {}) or {}).items():
        if "gaze" in str(k).lower():
            raw += list(v or [])
    for attr in ("FACE_POOLS", "FACE_BY_TIER"):
        blk = getattr(F, attr, None)
        if isinstance(blk, dict):
            raw += _leaves(blk)
    return [x for x in _split_items(raw, set()) if _is_gaze(x["en"])]

_BUILDERS = {"L00": _layer_quality, "L01b": _layer_style, "L01": _layer_tier,
             "L02": _layer_char, "L04": _layer_outfit, "L05": _layer_pose,
             "L05c": _layer_sexstate,
             "L10": _layer_state, "L06": _layer_scene, "L07": _layer_ambience, "L08": _layer_camera,
             "L09": _layer_face}

def _tier_map(cats):
    out = {}
    for c in cats:
        for s_ in (c.get("subs") or []):
            t = s_.get("tier") or "general"
            for i in (s_.get("items") or []):
                out.setdefault(i["en"], {})[t] = s_["key"]
    return out

def build():
    cats, cat_of, order, labels, cat_tiers, tiers = [], {}, [], {}, {}, {}
    for key in LAYER_ORDER:
        subs = []
        fn = _BUILDERS.get(key)
        if fn:
            try:
                subs = fn() or []
            except Exception as e:
                print("⚠️ %s 生成失败：%s" % (key, e), file=sys.stderr)
                subs = []
        if key == "L09" and subs:
            seen = {i["en"] for i in subs[0]["items"]}
            subs[0]["items"] += _split_items(_layer_face_extra(), seen)
            subs[0]["items"] = [i for i in subs[0]["items"] if not _is_gaze(i["en"])]
        if key == "L05":
            gz = [i for i in _gaze_items() if i["en"] not in
                  {x["en"] for s_ in subs for x in s_["items"]}]
            if gz:
                subs.append({"key": "pose_gaze", "label": "视线",
                             "tier": "general", "items": gz})
        if key == "L06" and subs:
            subs += _layer_props()
        cats.append({"key": key, "label": LAYER_LABEL.get(key, key), "subs": subs})
    cat_by_tier = _tier_map(cats)
    for c in cats:
        for s in (c.get("subs") or []):
            k = s["key"]
            if k not in order:
                order.append(k)
            labels[k] = s.get("label") or k
            cat_tiers[k] = s.get("tier") or "general"
            for i in s.get("items") or []:
                en = i.get("en")
                if not en:
                    continue
                cat_of.setdefault(en, k)
                tiers.setdefault(en, s.get("tier") or "general")
    if "zz_other" not in order:
        order.append("zz_other")
        labels["zz_other"] = "旧表归档"
        cat_tiers["zz_other"] = "general"
    return {
        "version": "layer-1",
        "note": "重抽面板分类唯一来源 —— 大类=管线层，小类=子池，颜色=子池档位",
        "categories": cats,
        "cat_of": cat_of,
        "order": order,
        "cat_labels": labels,
        "cat_tiers": cat_tiers,
        "cat_by_tier": cat_by_tier,
        "tiers": tiers,
        "cn": _CN,
        "char_feats": {k: list(v) for k, v in CHAR_FEATS.items()},
    }

if __name__ == "__main__":
    d = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print("✓ %s" % OUT)
    print("  层 %d · 子池 %d · 词 %d" % (len(d["categories"]), len(d["order"]), len(d["cat_of"])))
    for c in d["categories"]:
        n = sum(len(s.get("items") or []) for s in (c.get("subs") or []))
        print("  %-22s 子池 %2d  词 %4d" % (c["label"], len(c.get("subs") or []), n))
