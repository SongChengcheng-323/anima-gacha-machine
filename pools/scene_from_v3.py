from __future__ import annotations

try:
    from pools import v3_pools as V3
except Exception:
    try:
        from . import v3_pools as V3
    except Exception:
        import v3_pools as V3

SCENES = list(V3.SCENE_ALL)
SCENE_PLACE = dict(V3.SCENE_PLACE)
SCENE_CAT_OF = dict(V3.SCENE_CAT_OF)
SCENE_CATS = {k: list(v) for k, v in V3.SCENE_CATS.items()}

PUBLIC_SCENES = frozenset(V3.PUBLIC_SCENES)
PRIVATE_SCENES = frozenset(V3.PRIVATE_SCENES)
TIGHT_SPACES = frozenset(V3.TIGHT_SPACES)

CAT_LEVEL = {
    "INDOOR_HOME":       "高",
    "SEMI_PRIVATE":      "高",
    "INDOOR_PUBLIC":     "中",
    "INDOOR_TRANSIT":    "中",
    "WATERFRONT":        "中",
    "JAPANESE_FESTIVAL": "中",
    "OUTDOOR_CITY":      "低",
    "OUTDOOR_NATURE":    "低",
    "ENTERTAINMENT":     "低",
}
SCENE_LEVEL = {w: CAT_LEVEL.get(cat, "中") for w, cat in SCENE_CAT_OF.items()}

def _selfcheck():
    bad = []
    if len(SCENES) != len(set(SCENES)):
        bad.append("SCENES 有重复")
    _miss = [w for w in SCENES if w not in SCENE_PLACE]
    if _miss:
        bad.append("缺室内外标记: %d 条" % len(_miss))
    _miss2 = [w for w in SCENES if w not in SCENE_LEVEL]
    if _miss2:
        bad.append("缺级别: %d 条" % len(_miss2))
    return bad

if __name__ == "__main__":
    print("场景 %d 条 / %d 类" % (len(SCENES), len(SCENE_CATS)))
    print("室内 %d · 室外 %d" % (
        sum(1 for v in SCENE_PLACE.values() if v == "indoor"),
        sum(1 for v in SCENE_PLACE.values() if v == "outdoor")))
    print("公共 %d · 居家私密 %d · 狭窄 %d" % (
        len(PUBLIC_SCENES), len(PRIVATE_SCENES), len(TIGHT_SPACES)))
    print("级别分布:", {lv: sum(1 for v in SCENE_LEVEL.values() if v == lv)
                     for lv in ("高", "中", "低")})
    _b = _selfcheck()
    print("自检:", "通过" if not _b else "✗ " + "；".join(_b))
