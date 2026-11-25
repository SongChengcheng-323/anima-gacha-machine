SEX_STATUS = {
    "soft": [
        ("faint blush, half-lidded eyes, lips slightly parted", "淡红晕，眼半闭，唇微启"),
        ("shy blush, looking away briefly, breathing softly", "羞涩红晕，移开视线，轻呼吸"),
        ("soft blush, lips parted just a little, a quiet sigh", "淡淡红晕，唇微开，一声轻叹"),
        ("gentle blush, eyes slightly hazy, breathing slowly", "温柔红晕，眼神微朦，缓慢呼吸"),
        ("warm blush, a small smile, breathing a little faster", "暖红晕，浅笑，呼吸稍快"),
    ],
    "mid": [
        ("flushed cheeks, lips parted, breathing faster", "脸红，唇张开，呼吸加快"),
        ("blushing, half-lidded eyes, a soft moan escaping", "脸红，眼半睁，漏出轻哼"),
        ("warm blush, mouth open slightly, panting softly", "暖红晕，嘴微张，轻喘"),
        ("flushed face, lips parted, ragged breathing", "脸红，唇张，呼吸乱"),
        ("pink cheeks, biting her lower lip, short of breath", "脸颊泛红，咬下唇，气短"),
        ("blush spreading down her neck, lips parted, panting", "红晕蔓延到脖子，唇张，喘"),
    ],
    "intense": [
        ("deep blush, tongue out, panting hard", "深红晕，吐舌，急喘"),
        ("flushed all over, mouth open gasping, a sheen of sweat", "全身泛红，张嘴喘，一层薄汗"),
        ("heavy blush, half-lidded eyes unfocused, breathing hard", "重红晕，眼神失焦，喘得厉害"),
        ("blushing deeply, biting her lip, trembling slightly", "深红，咬唇，微微发抖"),
        ("red cheeks, sweat on her skin, breathless moans", "脸红，皮肤出汗，喘着哼"),
        ("flushed, lips parted, a long shudder running through her", "脸红，唇张，一阵长颤"),
    ],
    "climax": [
        ("deep blush, tongue out, crying out, trembling all over", "深红晕，吐舌，叫出声，全身发颤"),
        ("flushed red, eyes squeezed shut, gasping for air, sweat on skin", "涨红，紧闭双眼，大口喘，皮肤出汗"),
        ("mouth open wide, tongue out, back arched, tears at the corners of her eyes", "张大嘴，吐舌，背弓起，眼角落泪"),
        ("blushing crimson, eyes rolled back slightly, panting hard, legs shaking", "绯红，眼微微上翻，急喘，腿抖"),
        ("tongue out, drooling a little, blissful expression, trembling", "吐舌，微微流口水，恍惚的表情，发抖"),
        ("face flushed, crying out, nails digging in, body going stiff", "脸涨红，叫出声，指甲掐进去，身体绷紧"),
    ],
    "after": [
        ("soft blush fading, half-lidded eyes, catching her breath", "红晕渐褪，眼半闭，平复呼吸"),
        ("flushed and limp, breathing slowly, a satisfied smile", "红着脸，瘫软，缓慢呼吸，满足的笑"),
        ("gentle blush, eyes closed, catching her breath", "淡淡红晕，闭眼，平复呼吸"),
        ("still flushed, a blissful look, breathing evening out", "还红着，恍惚的神情，呼吸渐稳"),
    ],
}

PHASE_TO_STATUS = {
    "foreplay":     "soft",
    "masturbation": "soft",
    "light":        "soft",
    "mid":          "mid",
    "heavy":        "intense",
    "climax":       "climax",
    "ejac":         "climax",
    "after":        "after",
}

STATUS_P = {"soft": 0.55, "mid": 0.65, "intense": 0.75, "climax": 0.95, "after": 0.70}

def pick_status(rng, phase, force=False):
    band = PHASE_TO_STATUS.get(phase)
    if not band:
        return "", "", ""
    if not force and rng.random() > STATUS_P.get(band, 0.6):
        return band, "", ""
    en, cn = rng.choice(SEX_STATUS[band])
    return band, en, cn

SELF_PLAYS = {"masturbation", "toy", "self_pinch"}
FOREPLAY_PLAYS = {"fellatio", "cunnilingus", "handjob", "paizuri", "footjob",
                  "lick_nipple", "suck_nipple", "lick_ass", "kiss"}

def phase_of(play, intensity="mid", has_climax=False):
    if has_climax:
        return "climax"
    if play in SELF_PLAYS:
        return "masturbation"
    if play in FOREPLAY_PLAYS:
        return "foreplay"
    if intensity == "heavy":
        return "heavy"
    if intensity == "light":
        return "light"
    return "mid"

if __name__ == "__main__":
    import random
    rng = random.Random(1)
    print(f"状态串共 {sum(len(v) for v in SEX_STATUS.values())} 条 / "
          f"{len(SEX_STATUS)} 档\n")
    for phase in ("foreplay", "masturbation", "light", "mid", "heavy", "climax", "after"):
        band, en, cn = pick_status(rng, phase)
        print(f"  {phase:14s} → [{band:7s}] {en or '（不抽）'}")
    print("\n阶段反推：")
    for play, inten, cl in (("fellatio", "mid", False), ("masturbation", "mid", False),
                            ("missionary", "mid", False), ("doggystyle", "heavy", False),
                            ("missionary", "mid", True), ("cowgirl", "heavy", True)):
        print(f"  {play:14s} intensity={inten:6s} climax={cl!s:5s} → {phase_of(play,inten,cl)}")
