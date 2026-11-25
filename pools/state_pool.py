import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(HERE) not in sys.path:
    sys.path.insert(0, os.path.dirname(HERE))

from pools import sex_beats as SB
from pools import sex_router as SR
from pools import state as ST

META = {
    "id":      "state_pool",
    "cn":      "状态词库",
    "kind":    "pool",
    "tier":    "none",
    "parent":  None,
    "enabled": True,
    "desc":    "单抽版状态段：强度（分档）/ 表情·呼吸·手·腿（高频附加）/ 射精·高潮（可选）",
}

_REACT_EXACT = set(SR.REACTIONS_FACE) | set(SR.REACTIONS_HAND) | set(SR.REACTIONS_LEG)
_REACT_NEAR = {"legs interlocked", "arched back", "trembling thighs",
               "biting her lip, holding on", "breathless, speeding up"}

INTENSITY_FROM_LIB = [w for w in SB.INTENSITY_WORDS
                      if w not in _REACT_EXACT and w not in _REACT_NEAR]

INTENSITY_TIERS = {
    "light": ["a slow deliberate rhythm", "moving slowly", "rolling her hips"],
    "mid":   ["moving faster", "thrusting deeper", "picking up the pace", "a steady rhythm"],
    "heavy": ["harder thrusts", "hips slapping", "pounding into her"],
}
TIER_FROM_LIB = {"mid": ["moving faster", "thrusting deeper"],
                 "heavy": ["harder thrusts", "hips slapping"]}
TIER_P        = {"light": 0.30, "mid": 0.45, "heavy": 0.25}
TIER_P_CLIMAX = {"light": 0.00, "mid": 0.55, "heavy": 0.45}
THRUST_WORDS = ("thrusting deeper", "harder thrusts", "hips slapping", "pounding into her")

PARTS_OF = {
    "breathing a little faster":                ("breath",),
    "fingers curling loosely":                  ("hand",),
    "legs a little tense":                      ("leg",),
    "swallowing skin warm":                     ("throat", "skin"),
    "panting between gasps":                    ("breath",),
    "fingers curling clenching tight":          ("hand",),
    "toes curling legs going stiff":            ("foot", "leg"),
    "trembling slightly a sheen of sweat":      ("body", "sweat"),
    "crying out unable to hold it in":          ("voice",),
    "digging her nails in":                     ("hand",),
    "legs shaking unable to close":             ("leg",),
    "trembling all over damp with sweat":       ("body", "sweat"),
    "gone limp and boneless":                   ("body",),
    "breathing hard wanting another round":     ("breath", "att"),
    "clutching the sheets":          ("hand",),
    "gripping the sheets":           ("hand",),
    "hands gripping his back":       ("hand",),
    "arms wrapped around him":       ("hand",),
    "arms wrapped around his neck":  ("hand",),
    "hand covering her mouth":       ("hand", "mouth"),
    "clenching her fists":           ("hand",),
    "toes curling":                  ("foot",),
    "feet arched with toes pointed": ("foot",),
    "legs wrapped around him":       ("leg",),
    "trembling legs":                ("leg",),
    "knees pressed together":        ("leg",),
    "legs spread wide":              ("leg",),
    "parted lips":                   ("mouth",),
    "heavy blush":                   ("cheek",),
    "half-lidded eyes":              ("eyes",),
    "moaning":                       ("voice",),
    "eyes squeezed shut frowning":   ("eyes",),
    "brows furrowed":                ("eyes",),
}

def parts_all(word):
    return set(PARTS_OF.get(word, ()))

REACT_LIB = {
    "base": [
        ("breathing a little faster",          "voice"),
        ("fingers curling loosely",            "hand"),
        ("legs a little tense",                "leg"),
        ("swallowing skin warm",              "body"),
    ],
    "strong": [
        ("panting between gasps",              "voice"),
        ("fingers curling clenching tight",   "hand"),
        ("toes curling legs going stiff",     "leg"),
        ("trembling slightly a sheen of sweat", "body"),
    ],
    "climax": [
        ("crying out unable to hold it in",   "sound"),
        ("digging her nails in",               "hand"),
        ("legs shaking unable to close",      "leg"),
        ("trembling all over damp with sweat", "body"),
        ("gone limp and boneless",             "state"),
    ],
}
REACT_PHASE_P = {"base": 0.55, "strong": 0.60, "climax": 0.75}
REACT_ABS_MAX = 3
REACT_TIERS = ("base", "strong", "climax")

REACT_HOT = {
    "strong": [
        ("breathing hard and uneven",         "breath"),
        ("hands gripping tight, knuckles pale", "hand"),
        ("legs pressing together restlessly", "leg"),
    ],
    "climax": [
        ("drawing it out, unwilling to stop", "voice"),
        ("a long shudder running through her", "body"),
        ("breathing hard wanting another round", "voice"),
    ],
}

PROFILE_DEFAULT = {
    "name":          "默认",
    "orgasm_mul":    1.0,
    "ejac_mul":      1.0,
    "intensity_mul": {"light": 1.0, "mid": 1.0, "heavy": 1.0},
    "phase_mul":     {"base": 1.0, "strong": 1.0, "climax": 1.0},
    "react_count":   1.0,
    "allow_hot":     False,
}

PROFILE_EXAMPLES = {
    "cute": {
        "name": "可爱型（示例·小卡）",
        "react_count": 0.6,
        "phase_mul": {"base": 1.2, "strong": 1.0, "climax": 0.7},
        "intensity_mul": {"light": 1.3, "mid": 1.0, "heavy": 0.7},
        "allow_hot": False,
    },
    "mature": {
        "name": "成熟型（示例·卡芙卡/常莉）",
        "react_count": 1.15,
        "phase_mul": {"base": 1.0, "strong": 1.2, "climax": 1.3},
        "intensity_mul": {"light": 0.7, "mid": 1.1, "heavy": 1.3},
        "allow_hot": True,
        "orgasm_mul": 0.85,
    },
}

def apply_profile(profile=None):
    out = {k: (dict(v) if isinstance(v, dict) else v) for k, v in PROFILE_DEFAULT.items()}
    for k, v in (profile or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k].update(v)
        else:
            out[k] = v
    return out

def react_lib_for(profile):
    lib = {ph: list(items) for ph, items in REACT_LIB.items()}
    if profile.get("allow_hot"):
        for ph, items in REACT_HOT.items():
            lib.setdefault(ph, [])
            lib[ph] = lib[ph] + [x for x in items if x not in lib[ph]]
    return lib

def react_phase(intensity_tier, has_orgasm):
    if has_orgasm:
        return "climax"
    if intensity_tier in ("mid", "heavy"):
        return "strong"
    return "base"

def roll_react(rng, phase, cap=3, profile=None, standing=False):
    pf = profile or PROFILE_DEFAULT
    cap = max(1, round(cap * pf.get("react_count", 1.0)))
    p_layer = REACT_PHASE_P[phase] * pf.get("phase_mul", {}).get(phase, 1.0)
    used_parts, out = set(), []
    pool = [(w, part) for w, part in react_lib_for(pf).get(phase, [])]
    if standing:
        _LIMP = ("gone limp", "boneless", "unable to hold herself up", "collapsing")
        pool = [(w, part) for w, part in pool if not any(k in w.lower() for k in _LIMP)]
    rng.shuffle(pool)
    for w, part in pool:
        if len(out) >= cap:
            break
        ps = parts_all(w) or {part}
        if ps & used_parts:
            continue
        if rng.random() < min(0.95, p_layer):
            out.append(w); used_parts |= ps
    return out
ORGASM_MAX = 3
ORGASM_PART_MAX = 1
STATE_MAX = 3

LINK = {
    "ejac":   {"orgasm": +0.25},
    "orgasm": {"face": +0.30, "breath": +0.30,
               "leg": +0.25, "hand": +0.25},
}
RARE_LAYERS = ("ejac", "orgasm")

PENIS_PLAYS = {"missionary", "doggystyle", "cowgirl", "reverse_cowgirl",
               "squatting_cowgirl", "mating_press",
               "spooning", "standing_wall", "anal"}
CROTCH_PLAYS = {"cunnilingus", "fingering",
                "masturbation", "toy"}
SELF_PLAYS = {"self_pinch"}
ORGASM_LEVEL_P = {3: 0.35, 2: 0.22, 1: 0.08, 0: 0.0}

def orgasm_level(plays):
    ps = set(plays)
    if ps & PENIS_PLAYS:
        return 3
    if ps & CROTCH_PLAYS:
        return 2
    if ps & SELF_PLAYS:
        return 1
    return 0

def orgasm_gate(plays):
    return ORGASM_LEVEL_P[orgasm_level(plays)]

def coverage_check():
    import pools.sex_pool as _SP
    known = PENIS_PLAYS | CROTCH_PLAYS | SELF_PLAYS
    level0 = {"fellatio", "handjob", "paizuri", "footjob",
              "lick_ass",
              "suck_nipple", "lick_nipple", "kiss", "tonguekiss", "suck_fingers",
              "kiss_hand", "hold_hands", "lick_hand", "spank", "licking", "fondle"}
    miss = [k for k in _SP.SEX_POOL
            if k not in known and k not in level0 and k not in {"self_pinch"}]
    return [f"⚠️ 新玩法 {k} 还没归到高潮分层里" for k in miss]

BREATH = [
    ("breathless", "喘不上气"),
    ("panting softly", "轻轻喘着"),
    ("ragged breathing", "呼吸乱了"),
    ("short of breath chest heaving", "气短，胸口起伏"),
    ("gasping between thrusts", "一下一下地吸气"),
    ("a shaky exhale", "呼出一口气，发抖"),
    ("biting back a moan", "忍着不叫出来"),
]

OUTSIDE_OK = {"missionary", "mating_press", "doggystyle", "spooning"}

FACING = {
    "missionary":   "face_up",
    "mating_press": "face_up",
    "doggystyle":   "face_down",
    "spooning":     "side",
}
FRONT_PARTS = ["on her stomach", "on her chest", "on her breasts", "on her thigh"]
BACK_PARTS  = ["on her back", "on her ass", "on her buttocks",
               "on her lower back", "on her thigh"]
SIDE_PARTS  = ["on her hip", "on her thigh", "on her side"]

def can_ejac_outside(pos):
    return pos in OUTSIDE_OK

def allowed_parts(pos):
    return {"face_up": list(FRONT_PARTS),
            "face_down": list(BACK_PARTS),
            "side": list(SIDE_PARTS + BACK_PARTS),
            }.get(FACING.get(pos), [])

EJAC_LOCAL = {
    "fellatio":  ["cum in her mouth", "cum on her tongue", "facial", "cum on her face"],
    "handjob":   ["cum on her hand", "cum on her stomach", "cum on her breasts"],
    "footjob":   ["cum on her feet", "cum on her legs"],

    "fingering":    [],
    "paizuri":      [],
    "suck_nipple":  [],
    "lick_nipple":  [],
    "lick_ass":     [],
    "cunnilingus":  [],
}

EJAC_POSITION = {
    "missionary":  None,
    "doggystyle":  None,
    "spooning":    None,
}

EJAC_ANAL = {
    "inside":  ["cum in her ass", "cum inside her ass"],
    "outside": ["on her back", "on her buttocks", "on her lower back"],
}

EJAC_INSIDE_ONLY = {"cowgirl", "reverse_cowgirl", "squatting_cowgirl",
                    "mating_press", "standing_wall"}

EJAC_INSIDE = ["creampie", "cum inside her pussy"]

EJAC_BY_PLAY = EJAC_LOCAL

def pick_ejac(plays, rng):
    plays = list(plays or [])
    if not plays:
        return ""
    main = plays[0]

    if main in EJAC_LOCAL:
        pool = EJAC_LOCAL[main]
        return rng.choice(pool) if pool else ""

    if main == "anal":
        if rng.random() < 0.5:
            return rng.choice(EJAC_ANAL["inside"])
        return "cum " + rng.choice(EJAC_ANAL["outside"])

    if main in EJAC_POSITION:
        if rng.random() < 0.5:
            return rng.choice(EJAC_INSIDE)
        parts = EJAC_POSITION[main] or allowed_parts(main)
        if parts:
            return "cum " + rng.choice(parts)
        return rng.choice(EJAC_INSIDE)

    if main in EJAC_INSIDE_ONLY:
        return rng.choice(EJAC_INSIDE)

    return ""

MOUNT = [
    {"trigger": "*", "layer": "intensity", "p": 0.70},
    {"trigger": "male", "layer": "ejac",   "p": 0.46},
    {"trigger": "*",    "layer": "orgasm", "p": 0.15},
]
MALE_PLAYS = ("missionary", "doggystyle", "cowgirl", "reverse_cowgirl", "squatting_cowgirl",
              "mating_press", "spooning", "standing_wall",
              "fellatio", "cunnilingus", "handjob", "paizuri", "footjob", "anal",
              "fingering", "lick_ass",
              "suck_nipple", "lick_nipple", "kiss", "tonguekiss")

def _pick(rng, lst):
    return rng.choice(lst)

def _rn(pair):
    return pair if isinstance(pair, tuple) else (pair, pair)

_CONCRETE_BAN = {
    "clutching the sheets", "gripping the sheets",
    "one hand gripping the sheets, knuckles white",
    "back arching off the bed", "feet arched with toes pointed",
}

def _banned(lib, part):
    ban = getattr(SR, f"REACTION_{part}_BAN", {}) or {}
    return set(ban.get(lib, ()))

def _react(rng, lib, pool, part):
    bad = _banned(lib, part) | _CONCRETE_BAN
    ok = [x for x in pool if x not in bad]
    return _pick(rng, ok or pool)

def _use_status_v3():
    try:
        try:
            from pools import roll_params as _RP
        except Exception:
            import roll_params as _RP
        return bool(getattr(_RP, "USE_STATUS_V3",
                            getattr(_RP, "USE_STATUS_FROM_V3", False)))
    except Exception:
        return False

def state_for(plays, rng, char_cn="", tnames=None, profile=None):
    plays = list(plays or [])
    main = plays[0] if plays else ""
    _STANDING = ("standing sex", "standing_wall")
    _no_limp = main in _STANDING or any(p in _STANDING for p in plays)
    pf = apply_profile(profile)
    meta_pf = {"profile": pf["name"]}
    has_male = any(p in MALE_PLAYS for p in plays) or main in MALE_PLAYS
    try:
        from pools import sex_pool as _SPX
        _style = _SPX.insert_style(plays)
        _insertive = (_style == "penis")
    except Exception:
        _style, _insertive = "penis", True
    en, cn, meta = [], [], {}

    fired = set()

    def fire(layer, bonus=0.0, base=None, mul=1.0):
        for m in MOUNT:
            if m["layer"] != layer:
                continue
            if m["trigger"] == "male" and not has_male:
                return False
            p = (m["p"] if base is None else base) * mul
            ok = rng.random() < min(0.95, p + bonus)
            if ok:
                fired.add(layer)
            return ok
        return False

    def bonus_of(layer):
        return sum(LINK.get(f, {}).get(layer, 0.0) for f in fired)

    cap = STATE_MAX

    if fire("ejac", mul=pf.get("ejac_mul", 1.0)):
        meta["ejac_ready"] = True
        _ej = pick_ejac(plays, rng)
        if _ej and len(en) < cap:
            en.append(_ej); cn.append(_ej)
            meta["ejac"] = _ej
    if meta.get("ejac") and not meta.get("orgasm_parts"):
        meta["orgasm_parts"] = ["(射精 ⇒ 必高潮)"]
        meta["orgasm_forced"] = True
        cap = max(cap, STATE_MAX + 1)
    gate = orgasm_gate(plays)
    gate = gate * pf.get("orgasm_mul", 1.0)
    if gate > 0 and fire("orgasm", bonus_of("orgasm"), base=min(0.95, gate)) and len(en) < cap:
        meta["orgasm_parts"] = ["(反应见反应段 ▲)"]

        cap = STATE_MAX + 1

    if fire("intensity") and len(en) < cap:
        _tp = dict(TIER_P_CLIMAX if meta.get("orgasm_parts") else TIER_P)
        if not _insertive:
            _tp.pop("heavy", None)
        _im = pf.get("intensity_mul", {})
        _w = [_tp[k] * _im.get(k, 1.0) for k in _tp]
        tier = rng.choices(list(_tp), weights=_w, k=1)[0]
        _pool = [x for x in INTENSITY_TIERS[tier] if _insertive or x not in THRUST_WORDS]
        w = _pick(rng, _pool or INTENSITY_TIERS[tier])
        en.append(w); cn.append(w); meta["intensity"] = tier

    phase = react_phase(meta.get("intensity"), bool(meta.get("orgasm_parts")))
    meta["react_phase"] = phase
    if _use_status_v3():
        try:
            from pools import state_from_v3 as SFV
        except Exception:
            import state_from_v3 as SFV
        _band, _sen, _scn = SFV.status_pair_from_v3(
            rng, phase,
            ejac=bool(meta.get("ejac")),
            p_mul=pf.get("phase_mul", {}).get(phase, 1.0),
            force=True)
        meta["status_src"] = "state_from_v3"
        meta["status_band"] = _band
        meta["status_str"] = _sen
        if _sen:
            en.append(_sen); cn.append(_scn)
    else:
        _rcap = min(REACT_ABS_MAX, max(1, cap - len(en)))
        for w in roll_react(rng, phase, cap=_rcap, profile=pf, standing=_no_limp):
            en.append(w); cn.append(w)

    meta["profile"] = pf["name"]
    return en, cn, meta

def selfcheck():
    bad = []
    for tier, ws in TIER_FROM_LIB.items():
        for w in ws:
            if w not in SB.INTENSITY_WORDS:
                bad.append(f"⚠️ 共享库漂移：强度词 {w!r} 已不在 sex_beats.INTENSITY_WORDS 里")
    bad += coverage_check()
    for ph, items in REACT_LIB.items():
        for w, part in items:
            if any(b in w for b in ("sheet", "bed", "sofa", "floor")):
                bad.append(f"反应词里有具象/场景依赖：{w!r}")
            if len(w.split()) > 7:
                bad.append(f"反应词超过 7 个词：{w!r}")
    for ph in REACT_TIERS:
        if not REACT_LIB.get(ph):
            bad.append(f"反应阶段 {ph!r} 是空的")
    if any("eyes rolling back" in w for w, _ in REACT_LIB["climax"]):
        bad.append("翻白眼已按要求删除，不该再出现")
    for pos in OUTSIDE_OK:
        if pos not in FACING:
            bad.append(f"外射体位 {pos} 没标朝向")
    for pos, f in FACING.items():
        if not allowed_parts(pos):
            bad.append(f"{pos}（{f}）推不出可用射精部位")
    for pos in ("cowgirl", "reverse_cowgirl", "squatting_cowgirl",
                "standing_wall"):
        if can_ejac_outside(pos):
            bad.append(f"⚠️ {pos} 是女上位/站立族，应禁止外射 ✗")
    if not INTENSITY_FROM_LIB:
        bad.append("⚠️ 共享库漂移：sex_beats.INTENSITY_WORDS 里已取不到纯强度词")
    reacts = set(SR.REACTIONS_FACE) | set(SR.REACTIONS_HAND) | set(SR.REACTIONS_LEG)
    for tier, ws in INTENSITY_TIERS.items():
        for w in ws:
            if w in reacts:
                bad.append(f"强度词里混了反应词：{w}")
    if set(INTENSITY_TIERS) != set(TIER_P):
        bad.append("档位表对不上")
    for n in ("REACTIONS_FACE", "REACTIONS_HAND", "REACTIONS_LEG"):
        if not getattr(SR, n, None):
            bad.append(f"引用缺失：sex_router.{n}")
    for n in ("ORGASM_BODY",):
        if not getattr(ST, n, None):
            bad.append(f"引用缺失：state.{n}")
    return bad

if __name__ == "__main__":
    rng = random.Random(7)
    print("状态词库（单抽版）")
    print(f"  强度 {sum(len(v) for v in INTENSITY_TIERS.values())} 条 / {len(INTENSITY_TIERS)} 档")
    print(f"  呼吸 {len(BREATH)} 条")
    print(f"  反应 表情 {len(SR.REACTIONS_FACE)} / 手 {len(SR.REACTIONS_HAND)} / 腿 {len(SR.REACTIONS_LEG)}（引用 sex_router ✓）")
    print(f"  挂载规则 {len(MOUNT)} 条")
    print(f"  自检：{selfcheck() or '✓ 全过'}\n")
    print("  抽样（同一组玩法，跑 5 次看状态段的差别）：")
    for _ in range(5):
        en, cn, meta = state_for(["missionary", "kiss"], rng)
        print(f"    {', '.join(en)}")
        print(f"      ↳ {' / '.join(cn)}   meta={meta}")
