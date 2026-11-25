META = {
    "id": "wardrobe_route",
    "cn": "装备路由",
    "kind": "router",
    "tier": "none",
    "parent": None,
    "enabled": True,
    "desc": "判定各部位能有几件装备 + 去哪个池子找；不产出任何提示词（判定定死，只调加权）",
    "version": "v0.99.0",
    "refs": ["pools.wardrobe_pools"],
}

TIERS = ("fashion", "tease", "exposed", "sex")

def _pools():
    try:
        from pools import wardrobe_pools as WP
    except Exception:
        import os as _os
        import sys as _sys
        _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
        from pools import wardrobe_pools as WP
    return WP

TIER_CAP = {
    "fashion": None,
    "tease": 4,
    "exposed": 2,
    "sex": None,
}
DECO_CAP = {"fashion": 5, "tease": 5, "exposed": 3, "sex": 3}

GARMENT_SLOTS = ("upper", "lower", "rear")
DECO_SLOTS = ("head", "eyes", "ears", "neck", "hand_l", "waist")

SET_STYLE_SLOTS = ("upper", "lower", "leg_l", "feet", "head", "neck", "hand_l", "waist")

NO_WRITE = {
    ("rear", "fashion"): "时尚档不特地写内裤✓",
}

POOL_OF = {}
DEFAULT_POOL = "wardrobe_pools"

GEAR_TIER = {}

def gear_tier(tier):
    return GEAR_TIER.get(tier, tier)

def pool_name(slot, tier):
    return POOL_OF.get((slot, tier), DEFAULT_POOL)

def route(tier, char="", rng=None):
    WP = _pools()
    out = {}
    for slot in GARMENT_SLOTS + DECO_SLOTS:
        cands = WP.candidates(slot, gear_tier(tier))
        out[slot] = {
            "pool": pool_name(slot, tier),
            "cap": 1,
            "candidates": len(cands),
            "filled": bool(cands),
        }
    return {"tier": tier, "slots": out,
            "cap": {"garment": TIER_CAP.get(tier), "deco": DECO_CAP.get(tier)},
            "note": "判定层只回答「能不能填、去哪找」；具体词在 wardrobe_pools ✓"}

def selfcheck(verbose=False):
    problems = []
    WP = _pools()
    for tier in TIERS:
        for slot in GARMENT_SLOTS:
            if not WP.candidates(slot, tier):
                if (slot, tier) in NO_WRITE:
                    continue
                problems.append(f"[{tier}] 部位 {slot} 没有候选词 ✗（判定会指向空洞；"
                                f"若属设计如此，请登记进 NO_WRITE ✓）")
    for t in TIERS:
        if t not in TIER_CAP or t not in DECO_CAP:
            problems.append(f"上限表缺档位 {t} ✗")
    for tier in TIERS:
        for slot in GARMENT_SLOTS + DECO_SLOTS:
            for it in WP.candidates(slot, tier):
                if it.get("tier") != tier:
                    problems.append(f"池子跨档借词：[{tier}] {slot} 抽到了 {it.get('tier')} 档的 {it.get('en')} ✗")
                    break
    _NOT_INHERIT = ("through the fabric", "see-through", "visible above", "panty line visible",
                    "cleavage visible", "bare ", "topless", "exposed", "nude",
                    "nipples visible", "pussy visible", "anus visible", "barefoot",
                    "bare arm", "bare legs", "towel")
    for slot, items in list(WP.GEAR.items()) + list(WP.GEAR_EXT.items()):
        for it in items:
            if any(k in it["en"].lower() for k in _NOT_INHERIT):
                continue
            w = it["w"]
            if w["fashion"] > 0 and (w["tease"] <= 0 or w["exposed"] <= 0):
                problems.append(f"继承断了：{it['en']!r} 时尚有(w={w['fashion']}) "
                                f"但擦边{w['tease']}/暴露{w['exposed']} 没有 ✗")
            if w["tease"] > 0 and w["exposed"] <= 0:
                problems.append(f"继承断了：{it['en']!r} 擦边有、暴露没有 ✗")
    SEXY_KW = ("lingerie", "bikini", "panties", "underwear", "bra", "garter",
               "thighhigh", "micro", "topless", "nude", "blindfold")
    for slot in list(WP.GEAR) + list(WP.GEAR_EXT):
        for it in WP.candidates(slot, "fashion"):
            if any(k in it["en"].lower() for k in SEXY_KW):
                problems.append(f"时尚档混进性暗示服装：{it['en']!r} ✗")
    for tier, groups in MUST.items():
        for slot, words in groups:
            avail = {it["en"] for it in WP.candidates(slot, tier, want_attr=True)}
            if not (set(words) & avail):
                problems.append(f"[{tier}] 保底词 {words} 在池子的 {slot} 里一个都没有 ✗")
    _SEX_BAN = ("jeans", "pants", "trousers", "slacks", "hoodie", "jacket", "blazer",
                "sweater", "cardigan", "vest", "tote", "bag", "pouch", "watch")
    for slot in GARMENT_SLOTS + DECO_SLOTS:
        for it in WP.candidates(slot, "sex"):
            _low = (it["en"] or "").lower()
            _hit = [b for b in _SEX_BAN if b in _low]
            if _hit:
                problems.append(f"性爱档混进不该穿/不该带的：{it['en']!r}（命中 {_hit}）✗")
    _sex_lower = {it["en"] for it in WP.candidates("lower", "sex")}
    if not any("skirt" in (x or "") or "shorts" in (x or "") or "towel" in (x or "") for x in _sex_lower):
        problems.append("性爱档 lower 一条裙子/短裤/浴巾都没有 ✗（改过头了）")
    for w in ("nipples visible through the fabric", "panty line visible", "cleavage visible",
              "underwear visible above her waistband", "visible through clothes"):
        if is_bare(w):
            problems.append(f"隔衣词 {w!r} 被误判成裸 ✗（⇒ 让位词会跑到擦边档 ✗）")
    if verbose:
        print(f"  装备路由自检：{'✗ ' + '；'.join(problems[:4]) if problems else '✓ 全过'}")
        print(f"    档 {len(TIERS)} · 衣位 {len(GARMENT_SLOTS)} · 饰品位 {len(DECO_SLOTS)} · "
              f"上限 {TIER_CAP} / 饰品 {DECO_CAP}")
    return problems

MUST_P = 0.60

MUST = {}

BARE_MARKS = ("bare breasts", "bare upper body", "bare lower body", "bare buttocks",
              "bare thighs", "bare chest", "topless", "completely nude",
              "pussy exposed", "anus visible", "nipples visible",
              "one breast out", "breasts exposed")
CLOTH_MARKS = ("through the fabric", "see-through", "visible through", "cleavage visible",
               "panty line visible", "visible above her waistband", "transparent")
YIELD_ENABLED = False

YIELD_MARKS = {}

def must_for(tier, rng):
    WP = _pools()
    items = list(MUST.get(tier, []))
    if not items:
        return []
    out = []
    for i, (slot, words) in enumerate(items):
        if i > 0 and rng.random() >= MUST_P:
            continue
        avail = {it["en"] for it in WP.candidates(slot, gear_tier(tier), want_attr=True)}
        pool = [w for w in words if w in avail] or list(words)
        if pool:
            out.append((slot, rng.choice(pool)))
    return out

def is_bare(text):
    low = (text or "").lower()
    if is_cloth_mark(text):
        return False
    return any(k in low for k in BARE_MARKS)

def is_cloth_mark(text):
    low = (text or "").lower()
    return any(k in low for k in CLOTH_MARKS)

GUARANTEE = {}

SKIRT_BIND_PANTIES = False

SKIRT_PANTIES = (
    "white panties", "black panties", "striped panties", "lace-trimmed panties",
    "frilled panties", "high-cut panties", "side-tie panties", "cotton panties",
    "white bloomers",
)
PANTY_MARKS = ("panties", "briefs", "underwear", "thong", "bloomers",
               "bike shorts", "boyshorts", "spats")

PANTY_STYLES = (
    "sheer panties", "see-through panties", "string panties", "thong",
    "lace panties", "lace-trimmed panties", "frilled panties",
    "cotton panties", "striped panties", "white panties",
    "side-tie panties", "high-cut panties", "lowleg panties",
    "satin panties", "silk panties",
)

TEASE_SKIRT_PANTIES = True

SKIRT_UNIFORMS = ("serafuku", "sailor", "maid", "nurse", "police uniform",
                  "school uniform", "cheerleader", "sukeban")

SKIRT_GUARD_PANTIES = ("panties",)

PLACEHOLDER = {
    "tease":   {},
    "exposed": {},
    "sex":     {},
}

try:
    from . import wardrobe_slots as _WS
except Exception:
    try:
        import wardrobe_slots as _WS
    except Exception:
        _WS = None

_MULTI = set()
if _WS is not None:
    for _k, _v in getattr(_WS, "EQUIPMENT", {}).items():
        try:
            if isinstance(_v, (list, tuple)) and isinstance(_v[0], (list, tuple)) and len(_v[0]) > 1:
                _MULTI.add(_k)
        except Exception:
            pass

_ADDED = {
    "naked apron",
    "blue one-piece swimsuit",
    "towel wrapped around body",
    "school uniform",
    "cheongsam", "qipao",
    "yukata", "kimono",
    "white lace lingerie set",
    "black lace lingerie set",
    "white bikini",
}
ONE_PIECE = frozenset(_MULTI | _ADDED)

_COVERS = ("lower", "rear")

def one_piece_covers(word):
    if not word:
        return set()
    for _part in str(word).split(","):
        if _part.strip() in ONE_PIECE:
            return set(_COVERS)
    return set()

def is_one_piece(word):
    if not word:
        return False
    return any(_p.strip() in ONE_PIECE for _p in str(word).split(","))

LONG_PANTS_KW = ("jeans", "pants", "trousers", "leggings", "jogger", "slack")

def is_long_pants(word):
    w = (word or "").lower()
    return bool(w) and any(k in w for k in LONG_PANTS_KW)

SKIRT_KW = ("skirt",)

def is_skirt(word):
    w = (word or "").lower()
    if not w:
        return False
    if "swimsuit" in w or "bikini" in w:
        return False
    if any(x in w for x in ("dress trousers", "dress shirt", "headdress", "qipao-style top")):
        return False
    return ("skirt" in w or "dress" in w or "qipao" in w or "cheongsam" in w)

def wearing_skirt(meta_or_word):
    if isinstance(meta_or_word, dict):
        eq = (meta_or_word.get("equip") or {})
        txt = " ".join(str(eq.get(k) or "") for k in ("lower", "rear")) or (meta_or_word.get("outfit_text") or "")
    else:
        txt = meta_or_word or ""
    return is_skirt(txt)

def resolve(tier, picks, rng):
    WP = _pools()
    bare = any(is_bare(v) for v in picks.values() if v)
    kept, yielded, dropped = {}, [], []
    for slot, v in picks.items():
        if not v:
            continue
        if bare and is_cloth_mark(v):
            dropped.append(v)
            continue
        kept[slot] = v
    if bare and not YIELD_ENABLED:
        pass
    elif bare:
        _crotch_bare = is_bare(picks.get("rear")) or is_bare(picks.get("lower"))
        if picks.get("chest") and is_bare(picks["chest"]) and kept.get("upper") \
                and YIELD_MARKS.get("chest"):
            yielded.append(YIELD_MARKS["chest"])
        _lower_worn = bool(kept.get("lower")) and not is_bare(kept.get("lower"))
        _one_piece = bool(one_piece_covers(picks.get("upper"))) or bool(one_piece_covers(picks.get("lower")))
        if _crotch_bare and YIELD_MARKS.get("rear"):
            if _lower_worn and not yielded:
                yielded.append(YIELD_MARKS["rear"])
            elif _one_piece and not yielded:
                if not yielded:
                    yielded.append(YIELD_MARKS["onepiece"])
    return kept, yielded, {"bare": bare, "dropped": dropped}

YIELD_BY_PART = {
    "chest":  {"upper": "top pulled up over her breasts"},
    "crotch": {"rear": "panties pulled aside", "lower": None},
    "foot":   {"feet": "barefoot"},
    "thigh":  {"lower": "__SKIRT_LIFTED__"},
}
_SLEEVE_KILL = ("long-sleeved", "short-sleeved", "detached-sleeve", "puff-sleeved",
                "off-shoulder", "sleeveless")

def yield_for_parts(kept, parts):
    if not YIELD_ENABLED:
        return dict(kept), [], ["yield_disabled"]
    """动作要接触哪些部位 ⇒ 给对应格子让位 ✓（**纯函数** ✓ 不改入参 ✓）

    parts: `chest` 胸/乳头 · `crotch` 小穴 · `foot` 脚 · `hand` 手 · `armpit` 腋 · `thigh` 大腿
    返回  (新 kept, 让位词清单, 说明清单)
    """
    import re as _re
    out = dict(kept or {})
    yields, notes = [], []
    for part in sorted(set(parts or ())):
        if part in YIELD_BY_PART:
            for slot, v in YIELD_BY_PART[part].items():
                if v == "__SKIRT_LIFTED__":
                    if "skirt" in (out.get("lower") or "").lower():
                        out["lower"] = "skirt lifted"
                        yields.append("skirt lifted")
                        notes.append("thigh: 裙子 ⇒ 掀裙 ✓")
                    else:
                        notes.append("thigh: 不是裙子 ⇒ 不动 ✗")
                elif v is None:
                    if out.get(slot):
                        notes.append("%s: 清空 %s（原 %s）✓" % (part, slot, out[slot]))
                        out[slot] = None
                else:
                    if is_bare(out.get(slot)):
                        notes.append("%s: %s 已是器官裸露 ⇒ 让位词不覆盖（交给 resolve 补）✓" % (part, slot))
                        continue
                    out[slot] = v
                    yields.append(v)
                    notes.append("%s ⇒ %s = %s" % (part, slot, v))
        elif part in ("hand", "armpit"):
            up = out.get("upper") or ""
            if up:
                up2 = _re.sub(r",?\s*(%s)" % "|".join(_SLEEVE_KILL), "", up).strip(", ")
                out["upper"] = up2 or None
            out["hand_l"] = ", ".join(x for x in (out.get("hand_l"), "bare arm") if x)
            yields.append("bare arm")
            notes.append("%s ⇒ 去袖型 + bare arm ✓" % part)
    return out, yields, notes

CONTACT_KW = (
    ("chest", ("hand slipping under her top", "pinching her own nipple", "hand on her bare breast",
               "hands on her bare breasts", "squeezing her own breast", "hand under her clothes",
               "自摸胸", "捏乳头")),
    ("crotch", ("masturbat", "fingering", "dildo", "vibrator", "hand between her legs",
                "clitoris", "squeezing her own pussy", "touching herself", "自慰", "插入")),
    ("foot", ("footjob", "licking her foot", "toes sucked",
              "foot worship", "足交", "舔脚")),
    ("thigh", ("hand on her own thigh", "hand resting on her thigh", "rubbing her thigh",
               "groping her thigh", "摸大腿")),
    ("armpit", ("both arms raised", "arms raised above", "reaching upward",
                "hands clasped behind her head", "arms stretched upward", "armpits visible",
                "举手", "腋下")),
)

def parts_from_words(text):
    low = (text or "").lower()
    out = []
    for part, kws in CONTACT_KW:
        if any(k in low for k in kws):
            out.append(part)
    return out

def yield_selftest():
    bad = []
    k = {"upper": "silk blouse, long-sleeved", "lower": "pleated skirt", "rear": "panties",
         "feet": "loafers", "hand_l": ""}
    if yield_for_parts(k, ["chest"])[0]["upper"] != "top pulled up over her breasts":
        bad.append("胸 ⇒ 撩上衣 失败")
    o = yield_for_parts(k, ["crotch"])[0]
    if o["rear"] != "panties pulled aside" or o["lower"] is not None:
        bad.append("小穴 ⇒ 拉开内裤 + 清下装 失败")
    if "barefoot" not in (yield_for_parts(k, ["foot"])[0]["feet"] or ""):
        bad.append("脚 ⇒ 裸足 失败")
    o = yield_for_parts(k, ["hand"])[0]
    if "long-sleeved" in (o["upper"] or "") or "bare arm" not in (o["hand_l"] or ""):
        bad.append("手 ⇒ 去袖型 + bare arm 失败")
    if yield_for_parts(k, ["thigh"])[0]["lower"] != "skirt lifted":
        bad.append("大腿+裙子 ⇒ 掀裙 失败")
    if yield_for_parts({"lower": "jeans"}, ["thigh"])[0]["lower"] != "jeans":
        bad.append("大腿+长裤 ⇒ 不该动 失败")
    return bad

if __name__ == "__main__":
    import sys
    sys.exit(1 if selfcheck(verbose=True) else 0)
