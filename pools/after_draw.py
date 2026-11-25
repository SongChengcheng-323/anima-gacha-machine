from __future__ import annotations

import random

AFTER_POSES = [
    {"en": "lying on her back", "cn": "仰躺", "w": 3.0,
     "parts": ("mouth", "breasts", "stomach", "pussy")},
    {"en": "lying on her side", "cn": "侧躺", "w": 2.0,
     "parts": ("mouth", "breasts", "stomach", "buttocks")},
    {"en": "lying on her stomach", "cn": "趴着（手肘撑）", "w": 1.6,
     "parts": ("mouth", "breasts", "back", "buttocks")},
    {"en": "on all fours", "cn": "四肢着地", "w": 1.2,
     "parts": ("mouth", "back", "pussy", "ass")},
    {"en": "sitting up", "cn": "坐起", "w": 1.0,
     "parts": ("mouth", "breasts", "stomach")},
]

FREE_POSE_PARTS = {"pussy", "ass"}

SURFACE_WORDS = {"semen on her face"}

AFTER_TRACES = {
    "mouth": {
        "cn": "口",
        "w": 1.0,
        "words": [
            ("semen in her mouth", "嘴里含着"),
            ("semen on her face", "脸上"),
            ("semen dripping from her lips", "从唇边流下"),
        ],
    },
    "back": {
        "needs_actor": True,
        "cn": "背",
        "w": 1.1,
        "words": [
            ("semen on her back", "背上"),
            ("semen on her lower back", "后腰"),
        ],
    },
    "buttocks": {
        "needs_actor": True,
        "cn": "臀",
        "w": 1.1,
        "words": [
            ("semen on her buttocks", "臀部"),
            ("semen on her ass", "屁股上"),
        ],
    },
    "breasts": {
        "needs_actor": True,
        "cn": "胸",
        "w": 1.2,
        "words": [
            ("semen on her breasts", "胸口"),
            ("semen between her breasts", "乳沟间"),
        ],
    },
    "stomach": {
        "needs_actor": True,
        "cn": "腹",
        "w": 1.3,
        "words": [
            ("semen on her stomach", "腹部"),
            ("semen on her belly", "肚子上"),
        ],
    },
    "pussy": {
        "cn": "穴",
        "w": 1.4,
        "words": [
            ("semen dripping from her pussy", "从小穴流出"),
            ("semen overflow", "满溢"),
            ("creampie", "内射痕迹"),
        ],
    },
    "ass": {
        "cn": "肛",
        "w": 1.0,
        "words": [
            ("semen dripping from her ass", "从臀缝流出"),
            ("semen in her ass", "射在屁股里"),
            ("semen leaking from her anus", "肛门渗出"),
            ("ass focus, cum dripping from her asshole", "肛门特写流出"),
        ],
    },
}

AFTER_STATE = [
    ("deep blush, half-lidded eyes, breathing slowly", "深红晕未退，眼半睁，缓慢呼吸"),
    ("flushed and limp, breathing softly", "脸还红着、身子发软，轻呼吸"),
    ("still flushed, a satisfied smile, catching her breath", "红晕未退，满足地笑，缓着气"),
    ("heavy blush, messy hair, breathing evening out", "重红晕，头发凌乱，呼吸渐平"),
    ("blushing, trembling slightly, breathing slowly", "脸红，微微发抖，慢慢呼吸"),
]

_BANNED = ("missionary", "doggystyle", "cowgirl", "spooning", "standing sex",
           "penis", "inserted", "ejaculating", "1boy", "male_rover")

def _allow_surface():
    try:
        from pools import roll_params as RP
    except Exception:
        try:
            from . import roll_params as RP
        except Exception:
            return False
    return bool(getattr(RP, "AFTER_ALLOW_SURFACE", False))

def _free_pose_enabled():
    try:
        from pools import roll_params as RP
    except Exception:
        try:
            from . import roll_params as RP
        except Exception:
            return False
    return bool(getattr(RP, "AFTER_FREE_POSE", False))

def _pick_weighted(rng, items, key="w", default=1.0):
    ws = [float(it.get(key, default)) for it in items]
    return rng.choices(items, weights=ws, k=1)[0]

def draw(rng):
    _pool = [dict(k=k, **AFTER_TRACES[k]) for k in AFTER_TRACES
             if _allow_surface() or not AFTER_TRACES[k].get("needs_actor")]
    if not _pool:
        _pool = [dict(k=k, **AFTER_TRACES[k]) for k in AFTER_TRACES]
    part_key = _pick_weighted(rng, _pool)["k"]
    part = AFTER_TRACES[part_key]
    _free = _free_pose_enabled() and part_key in FREE_POSE_PARTS
    if _free:
        pose = {"en": "", "cn": "自由姿态", "parts": tuple(AFTER_TRACES)}
    else:
        _okp = [p for p in AFTER_POSES if part_key in (p.get("parts") or ())]
        pose = _pick_weighted(rng, _okp or AFTER_POSES)
    _words = [w for w in part["words"]
              if _allow_surface() or w[0] not in SURFACE_WORDS]
    trace_en, trace_cn = rng.choice(_words or part["words"])
    st_en, st_cn = rng.choice(AFTER_STATE)
    return {
        "poses": [] if _free else [pose["en"]],
        "pose_cat": ("自由姿态" if _free else pose["cn"]),
        "state_en": st_en,
        "state_cn": st_cn,
        "trace_en": trace_en,
        "trace_cn": trace_cn,
        "trace_part": part_key,
        "trace_part_cn": part["cn"],
        "pose_parts": list(pose.get("parts") or ()),
    }

def as_body(rng):
    d = draw(rng)
    return {
        "plays": [],
        "act_en": list(d["poses"]),
        "act_cn": [d["pose_cat"]],
        "state_en": [d["state_en"], d["trace_en"]],
        "state_cn": [d["state_cn"], d["trace_cn"]],
        "state_meta": {"after": True, "ejac": d["trace_en"],
                       "trace_part": d["trace_part"], "trace_part_cn": d["trace_part_cn"],
                       "trace_en": d["trace_en"], "react_phase": "after"},
        "solo": True,
        "camera": "",
    }

def selfcheck():
    bad = []
    for need in ("mouth", "breasts", "stomach", "pussy", "ass"):
        if not AFTER_TRACES.get(need, {}).get("words"):
            bad.append(f"痕迹部位 {need} 是空的")
    if not AFTER_STATE:
        bad.append("状态串是空的")
    for st, _cn in AFTER_STATE:
        if "blush" not in st.lower() and "flushed" not in st.lower():
            bad.append(f"状态串没有高潮红：{st!r}")
    for p in AFTER_POSES:
        if any(b in p["en"].lower() for b in _BANNED):
            bad.append(f"事后姿态里混进了体位词：{p['en']!r}")
    for p in AFTER_POSES:
        for k in (p.get("parts") or ()):
            if k not in AFTER_TRACES:
                bad.append(f"姿态 {p['en']!r} 声明了不存在的部位 {k!r}")
    for p in AFTER_POSES:
        if p["en"] == "on all fours":
            for k in ("stomach", "breasts", "buttocks"):
                if k in (p.get("parts") or ()):
                    bad.append("四肢着地里混进了挂不住的部位：%s" % k)
    for p in AFTER_POSES:
        if p["en"] == "lying on her stomach":
            for k in ("pussy", "ass"):
                if k in (p.get("parts") or ()):
                    bad.append("趴姿里混进了看不见的部位：%s" % k)
    for k, part in AFTER_TRACES.items():
        for w, _cn in part["words"]:
            if any(b in w.lower() for b in _BANNED):
                bad.append(f"痕迹词里混进了插入类词：{w!r}")
    return bad

if __name__ == "__main__":
    import sys
    print("事后池：姿态", len(AFTER_POSES), "· 部位", len(AFTER_TRACES),
          "· 痕迹", sum(len(v["words"]) for v in AFTER_TRACES.values()),
          "· 状态", len(AFTER_STATE))
    print("自检:", selfcheck() or "✓")
    r = random.Random(1)
    for _ in range(3):
        d = draw(r)
        print(" ", d["poses"], "|", d["state_en"], "|", d["trace_part_cn"], d["trace_en"])
