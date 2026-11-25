CHAR_TRAITS = {
    "hatsune_miku": {"main": "可爱", "sub": []},
}

INFERRED = set()

VALID_TAGS = {"成熟", "可爱", "无口", "害羞"}

def traits_of(tag):
    t = CHAR_TRAITS.get(tag)
    if not t:
        return None, []
    return t["main"], list(t.get("sub", []))

def validate():
    problems = []
    conflicts = [{"成熟", "可爱"}]
    for tag, t in CHAR_TRAITS.items():
        main = t.get("main")
        sub = t.get("sub", [])
        if main not in VALID_TAGS:
            problems.append(f"{tag}: 主标签非法 {main!r}")
        if len(sub) > 2:
            problems.append(f"{tag}: 副标签超过 2 个 {sub}")
        for s in sub:
            if s not in VALID_TAGS:
                problems.append(f"{tag}: 副标签非法 {s!r}")
            if s == main:
                problems.append(f"{tag}: 副标签与主标签重复 {s}")
            for c in conflicts:
                if {main, s} == c:
                    problems.append(f"{tag}: 冲突组合 {main}+{s}")
    return problems

if __name__ == "__main__":
    print(f"角色数 = {len(CHAR_TRAITS)}")
    from collections import Counter
    c = Counter(v["main"] for v in CHAR_TRAITS.values())
    for k in ["成熟", "可爱", "无口", "害羞"]:
        print(f"  {k}: {c.get(k, 0)}")
    print(f"推断数 = {len(INFERRED)}")
    pb = validate()
    print("自检问题：", pb if pb else "无 ✓")

_OPEN_SOURCE_KEEP_TRAITS = {"hatsune_miku"}
CHAR_TRAITS = {k: v for k, v in CHAR_TRAITS.items() if k in _OPEN_SOURCE_KEEP_TRAITS}
