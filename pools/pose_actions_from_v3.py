try:
    from pools import body_pool as BP
    from pools import pose_table as PT
except Exception:
    import body_pool as BP
    import pose_table as PT

CAT_MAP = {
    "自然": "时尚",
}
KEEP_EMPTY = {("手", "脱袜")}

ALL_BIG = ("站", "坐", "跪", "趴", "躺", "倚")

def _bigs_for(part, cat):
    allowed = BP.NEED.get((part, cat))
    if not allowed:
        return None
    bigs = set()
    for pose in allowed:
        d = BP.POSTURES.get(pose) or PT.POSTURES.get(pose)
        if d and d.get("big"):
            bigs.add(d["big"])
    return bigs or None

def build(tier_word_limit=None):
    src = {"手": BP.HANDS, "头": BP.HEADS, "腿": BP.LEGS, "脚": BP.FEET}
    actions = {}
    restrict_add = {}
    for part, cats in src.items():
        out = {}
        for cat, words in cats.items():
            pc = (part, cat)
            if pc in KEEP_EMPTY:
                out[cat] = []
                continue
            name = CAT_MAP.get(cat, cat)
            words = [w for w in words if w]
            out[name] = words
            bigs = _bigs_for(part, cat)
            if bigs is not None:
                for w in words:
                    restrict_add[w] = restrict_add.get(w, set()) | bigs
        actions[part] = out
    return actions, restrict_add

def apply():
    actions, restrict_add = build()
    PT.ACTIONS = actions
    PT.RESTRICT = dict(PT.RESTRICT)
    for w, bigs in restrict_add.items():
        PT.RESTRICT[w] = tuple(sorted(bigs))
    for part, cats in actions.items():
        for c in cats:
            PT.CAT_W.setdefault((part, c), (1.0, 1.0, 1.0, 1.0))
    PT.CAT_W[("头", "低头")] = (0.0, 0.0, 0.0, 0.0) if ("头", "低头") in PT.CAT_W else (0, 0, 0, 0)
    return actions, restrict_add

def summary():
    a, r = build()
    lines = []
    for part in ("头", "手", "腿", "脚"):
        n = sum(len(v) for v in (a.get(part) or {}).values())
        cats = len(a.get(part) or {})
        lines.append(f"{part}: {cats} 类 / {n} 条")
    return " | ".join(lines), len(r)

def selfcheck():
    errs = []
    a, r = build()
    for part in ("头", "手", "腿", "脚"):
        if not a.get(part):
            errs.append(f"{part} 为空")
    for w in (a.get("脚") or {}).get("趾部", []):
        if "barefoot" in w.lower():
            errs.append(f"脚池带穿鞋状态: {w}")
    import re
    HEAD = re.compile(r"\b(head|chin)\b", re.I)
    for cat, ws in (a.get("手") or {}).items():
        for w in ws:
            if HEAD.search(w) and cat != "托腮":
                errs.append(f"手池带头: [{cat}] {w}")
    return errs

if __name__ == "__main__":
    s, n = summary()
    print(s)
    print(f"RESTRICT 新增 {n} 条")
    e = selfcheck()
    print("自检:", e or "✓ 通过")
