try:
    from pools.char_traits import CHAR_TRAITS
    from pools.characters_split import CHARACTERS_SPLIT
except Exception:
    from char_traits import CHAR_TRAITS
    from characters_split import CHARACTERS_SPLIT

def blank_profile():
    return {
        "性格": {"main": "", "sub": []},
        "喜欢的体位": [],
        "喜欢口味": [],
        "香水": "",
        "性癖": {
            "小玩具": {"喜欢": "", "种类": []},
            "肛交": "",
            "口交": "",
            "乳交": "",
            "蒙眼": "",
            "SM": "",
            "户外露出": "",
        },
        "_source": "",
    }

OVERRIDES = {'hatsune_miku': {'喜欢的体位': ['missionary', 'cowgirl'],
                  '喜欢口味': ['甜', '奶香'],
                  '香水': 'vanilla',
                  '性癖': {'小玩具': {'喜欢': '喜欢', '种类': ['vibrator', 'wand']},
                         '肛交': '可',
                         '口交': '接受',
                         '乳交': '可',
                         '蒙眼': '可',
                         'SM': '可',
                         '户外露出': '可'}}}

def _build():
    table = {}
    for c in CHARACTERS_SPLIT:
        tag = c["tag"]
        p = blank_profile()

        t = CHAR_TRAITS.get(tag)
        if t:
            p["性格"] = {"main": t.get("main", ""), "sub": list(t.get("sub", []))}

        p["_source"] = ""

        table[tag] = p
    return table

CHAR_PROFILE = _build()

def _apply_overrides():
    for tag, patch in OVERRIDES.items():
        if tag not in CHAR_PROFILE:
            continue
        p = CHAR_PROFILE[tag]
        for k, v in patch.items():
            if k in p:
                p[k] = v
        mark = p.get("_source", "")
        p["_source"] = (mark + "; 人工" if mark else "人工") if patch else mark

_apply_overrides()

def traits_of(tag):
    p = CHAR_PROFILE.get(tag)
    return dict(p["性格"]) if p else None

def sex_rates(tag):
    t = traits_of(tag)
    if not t or not t.get("main"):
        return {}
    try:
        from pools.trait_sex import rates_of
        return rates_of(t)
    except Exception:
        return {}

PREF_BOOST = 2.0
TRI_MULT = {"接受": 2.5, "可": 1.5, "不接受": 0.15, "": 1.0}
TOY_MULT = {"喜欢": 2.5, "不喜欢": 0.15, "": 1.0}
LIB_TO_SEX_FIELD = {"fellatio": "口交", "cunnilingus": "口交", "paizuri": "乳交",
                    "anal": "肛交", "toy_anal": "肛交"}
P_PENIS_BASE = 0.78
P_PENIS_BY_TOY = {"喜欢": 0.45, "不喜欢": 0.92, "": P_PENIS_BASE}

def position_weights(tag, keys):
    keys = list(keys or [])
    n = len(keys)
    w = [1.0] * n
    t = traits_of(tag)
    if t and t.get("main"):
        try:
            from pools.trait_sex import position_weights as _pw
            w = list(_pw(t, keys))
        except Exception:
            w = [1.0] * n
    prefs = set((CHAR_PROFILE.get(tag) or {}).get("喜欢的体位") or [])
    if prefs:
        w = [max(x, PREF_BOOST) if k in prefs else x for x, k in zip(w, keys)]
    return w

def route_weight(tag, lib):
    p = CHAR_PROFILE.get(tag) or {}
    w = 1.0
    if lib in set(p.get("喜欢的体位") or []):
        w *= PREF_BOOST
    sx = p.get("性癖") or {}
    f = LIB_TO_SEX_FIELD.get(lib)
    if f:
        w *= TRI_MULT.get(sx.get(f, ""), 1.0)
    if str(lib).startswith("toy_"):
        w *= TOY_MULT.get((sx.get("小玩具") or {}).get("喜欢", ""), 1.0)
    return w

def p_penis(tag):
    sx = (CHAR_PROFILE.get(tag) or {}).get("性癖") or {}
    return P_PENIS_BY_TOY.get((sx.get("小玩具") or {}).get("喜欢", ""), P_PENIS_BASE)

MONO_MULT = {"接受": 3.0, "可": 1.8, "不接受": 0.1, "": 1.0}
OUTDOOR_MULT = {"接受": 4.0, "可": 2.0, "不接受": 0.1, "": 1.0}

def _sx(tag, field):
    sx = (CHAR_PROFILE.get(tag) or {}).get("性癖") or {}
    return sx.get(field, "")

def blindfold_mult(tag):
    return MONO_MULT.get(_sx(tag, "蒙眼"), 1.0)

def outdoor_mult(tag):
    return OUTDOOR_MULT.get(_sx(tag, "户外露出"), 1.0)

REQUIRED_FIELDS = [
    "性格", "喜欢的体位", "喜欢口味", "香水", "性癖", "_source",
]
REQUIRED_NESTED = {
    "性格": ["main", "sub"],
    "性癖": ["小玩具", "肛交", "口交", "乳交", "蒙眼", "SM", "户外露出"],
}
REQUIRED_IN_TOY = ["喜欢", "种类"]

_FILLABLE = [
    ("喜欢的体位",), ("喜欢口味",), ("香水",),
    ("性癖", "小玩具", "喜欢"), ("性癖", "小玩具", "种类"),
    ("性癖", "肛交"), ("性癖", "口交"), ("性癖", "乳交"),
    ("性癖", "蒙眼"), ("性癖", "SM"), ("性癖", "户外露出"),
]

def _get(p, path):
    cur = p
    for k in path:
        cur = cur[k]
    return cur

def validate():
    problems = []
    if len(CHAR_PROFILE) != len(CHARACTERS_SPLIT):
        problems.append(f"角色数 {len(CHAR_PROFILE)} != 拆分表 {len(CHARACTERS_SPLIT)}")
    for tag, p in CHAR_PROFILE.items():
        for k in REQUIRED_FIELDS:
            if k not in p:
                problems.append(f"{tag}: 缺字段 {k}")
        for k, subs in REQUIRED_NESTED.items():
            if k not in p:
                continue
            for s in subs:
                if s not in p[k]:
                    problems.append(f"{tag}: {k} 缺子字段 {s}")
        toy = p.get("性癖", {}).get("小玩具", {})
        for s in REQUIRED_IN_TOY:
            if s not in toy:
                problems.append(f"{tag}: 性癖.小玩具 缺子字段 {s}")
        if not isinstance(p.get("喜欢的体位"), list):
            problems.append(f"{tag}: 喜欢的体位 非列表")
        if not isinstance(p.get("喜欢口味"), list):
            problems.append(f"{tag}: 喜欢口味 非列表")
    return problems

def stats():
    n = len(CHAR_PROFILE)
    all_blank = sum(
        1 for p in CHAR_PROFILE.values()
        if all(not _get(p, path) for path in _FILLABLE)
    )
    return {"角色数": n, "除性格外全空": all_blank}

if __name__ == "__main__":
    print("═══ char_profile 自检 ═══")
    from collections import Counter
    s = stats()
    print(f"  角色数        : {s['角色数']}")
    print(f"  除性格外全空  : {s['除性格外全空']}")

    pb = validate()
    if pb:
        print(f"\n  ✗ 字段完整性问题 {len(pb)} 条：")
        for x in pb[:10]:
            print("    -", x)
    else:
        print(f"\n  ✅ 字段完整性：{len(CHAR_PROFILE)} 人 × 全部字段（含嵌套）全在 ✓")

    c = Counter(p["性格"]["main"] for p in CHAR_PROFILE.values())
    print("\n  性格分布（引自 char_traits）:",
          " ".join(f"{k}:{v}" for k, v in c.most_common()))
    print("\n  样例：")
    for tag in ("hatsune_miku", "hatsune_miku"):
        print(f"    {tag}: {CHAR_PROFILE[tag]}")
