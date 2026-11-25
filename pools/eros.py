EROS_FASHION = {
    "casual": [
        "well-coordinated casual outfit, clean and natural styling",
        "casual but stylish look, relaxed natural pose",
        "neat and fresh appearance, everyday charm",
        "simple but tasteful outfit, comfortable posture",
        "effortless styling, pleasant and lively mood",
    ],
    "chic": [
        "elegant pose, refined gesture, chin slightly raised",
        "delicate gold earrings, fine necklace, subtle shine",
        "finely tailored outfit, elegant silhouette, flowing fabric",
        "luxurious fabric glinting softly in the light",
        "tasteful hair ornament, refined accessories",
    ],
    "uniform": [
        "polished professional look, neat upright posture",
        "round thin gold-rimmed glasses, delicate earrings",
        "fine necklace, tidy styling, confident composed stance",
        "well-groomed appearance, crisp clean lines",
        "subtle jewelry, precise and elegant details",
    ],
}

EROS_TEASE_UNITS = [
    ("nipples showing through the fabric", 6, ("wearing", "lingerie", "swim"), "upper", "front"),
    ("visible through clothes", 5, ("wearing", "lingerie", "swim"), "upper", "any"),
    ("see-through fabric", 5, ("wearing", "lingerie", "swim"), "upper", "any"),
    ("wet transparent fabric clinging to her body", 4, ("wearing", "swim"), "upper", "any"),
    ("damp clothes clinging to her body", 4, ("wearing", "swim"), "upper", "any"),
    ("strap slipped off shoulder", 5, ("wearing", "lingerie", "swim"), "upper", "any"),
    ("strap slipped down", 4, ("wearing", "lingerie", "swim"), "upper", "any"),
    ("clothing unbuttoned", 5, ("wearing",), "upper", "front"),
    ("cleavage visible", 6, ("wearing", "lingerie"), "upper", "front"),
    ("cleavage spilling out", 5, ("wearing", "lingerie"), "upper", "front"),
    ("underboob", 4, ("wearing", "swim"), "upper", "front"),
    ("sideboob", 4, ("wearing",), "upper", "any"),
    ("midriff and belly button exposed", 4, ("wearing",), "upper", "front"),
    ("bare shoulders", 5, ("semi", "nude"), "upper", "any"),
    ("collarbone visible", 4, ("semi", "nude"), "upper", "any"),
    ("soft curve of her breast visible at the side", 4, ("semi", "nude"), "upper", "any"),
    ("camel toe", 5, ("wearing", "lingerie", "swim"), "lower", "front"),
    ("tight fabric", 4, ("wearing", "lingerie", "swim"), "lower", "any"),
    ("upskirt", 4, ("wearing",), "lower", "front"),
    ("underwear visible", 6, ("wearing", "lingerie", "swim"), "lower", "any"),
    ("lower garment flipped up", 4, ("wearing", "swim"), "lower", "any"),
    ("lower garment slightly lifted", 4, ("wearing", "swim"), "lower", "any"),
    ("underwear peeking", 4, ("wearing", "swim"), "lower", "any"),
    ("hem lifted", 4, ("wearing",), "lower", "any"),
    ("legwear with a small tear", 4, ("wearing", "lingerie"), "lower", "any"),
    ("hint of her pussy between her thighs", 4, ("nude", "semi"), "lower", "front"),
    ("clothing riding up", 4, ("wearing", "swim"), "rear", "back"),
    ("buttocks partially visible", 5, ("wearing", "swim"), "rear", "back"),
    ("panty line visible", 3, ("wearing", "lingerie"), "rear", "back"),
]

EROS_EXPOSED_UNITS = [
    ("nipples visible", 8, ("wearing", "lingerie", "swim", "semi", "nude"), "upper", "front"),
    ("nipple fully visible", 6, ("wearing", "lingerie", "swim"), "upper", "front"),
    ("one breast out of her clothing", 5, ("wearing", "lingerie", "swim"), "upper", "front"),
    ("both breasts exposed", 5, ("wearing", "lingerie", "swim"), "upper", "front"),
    ("bare breasts", 6, ("nude", "semi", "lingerie"), "upper", "front"),
    ("bare breasts with hard nipples", 5, ("nude", "lingerie"), "upper", "front"),
    ("top pulled up over her breasts", 4, ("wearing", "swim"), "upper", "front"),
    ("clothing pulled open", 4, ("wearing", "lingerie"), "upper", "front"),
    ("bra pulled down completely", 3, ("lingerie",), "upper", "front"),
    ("completely nude", 7, ("nude",), "upper", "any"),
    ("soft bare stomach", 3, ("nude",), "upper", "front"),
    ("pussy visible", 6, ("lingerie", "swim", "nude"), "lower", "front"),
    ("pussy exposed", 5, ("nude",), "lower", "front"),
    ("underwear pulled down to thighs", 3, ("lingerie",), "lower", "front"),
    ("back and buttocks visible", 5, ("nude", "semi"), "rear", "back"),
    ("bare buttocks", 5, ("nude", "semi", "lingerie"), "rear", "back"),
    ("pussy visible from the rear", 5, ("nude", "semi"), "rear", "back"),
    ("anus visible", 4, ("nude", "semi"), "rear", "back"),
]

PART_BOOST = 2.0

_DUP_GROUPS = [
    ("chest", ("nipple", "breast", "cleavage", "underboob", "sideboob")),
    ("pubic", ("pussy", "camel toe")),
]

def _dup_group(t):
    tl = t.lower()
    for name, kws in _DUP_GROUPS:
        if any(k in tl for k in kws):
            return name
    return None

def pick_eros_units(rng, units, cat=None, framing=None, facing=None, want=2, allow_skirt=True):
    if not units:
        return ""
    parts = {"upper"} if framing in ("upper", "closeup") else {"upper", "lower", "rear"}

    def ok(t):
        _, _, cats, part, need = t
        if not allow_skirt and "skirt" in str(t[0]).lower():
            return False
        if cat and cats and cat not in cats:
            return False
        if part not in parts:
            return False
        if need == "back" and facing != "back":
            return False
        if need == "front" and facing == "back":
            return False
        return True

    pool = [list(t) for t in units if ok(t)]
    if not pool:
        return ""
    picked = []
    _used_grp = set()
    for _ in range(max(1, want)):
        if not pool:
            break
        cand = [x for x in pool if _dup_group(x[0]) not in _used_grp]
        if not cand:
            break
        t = rng.choices(cand, weights=[x[1] for x in cand])[0]
        picked.append(t[0])
        _g = _dup_group(t[0])
        if _g:
            _used_grp.add(_g)
        pool = [x for x in pool if x[0] != t[0]]
        for x in pool:
            if x[3] == t[3]:
                x[1] = x[1] * PART_BOOST
    return ", ".join(picked)
