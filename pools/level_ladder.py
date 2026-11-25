import random
import re

from pools import sex_router as SR
from pools.equip_machine import (TOYS, SEX_FACE, SEX_FACE_BY_ATT, SEX_FACE_WATCH,
                                 CHEST_EXPOSE, REAR_EXPOSE, PUBIC_STATES,
                                 GAZE_BY_TIER)

LEVELS = ["fashion", "tease", "exposed", "foreplay", "sex", "ejac", "after"]
LEVEL_LABEL = {"fashion": "穿着", "tease": "擦边", "exposed": "露点",
               "foreplay": "自慰/前戏", "sex": "做爱", "ejac": "射精", "after": "事后"}

A_MALE = "handsome young man, short black hair, 20 years old"
A_POSITIONS = [("missionary position", "lying on her back"),
               ("doggystyle", "on all fours", "from behind"),
               ("cowgirl position", "sitting on top", "straddling"),
               ("reverse cowgirl", "sitting on top", "facing away from him")]

def _whitelist():
    w = set(SR.ORGAN_ALWAYS)
    for v in SR.ORGAN_BY_POSITION.values():
        w |= set(v)
    for r in SR.ROUTES.values():
        w |= set(r["ph"])
    for v in SR.POSITION_PHRASES.values():
        w |= set(v)
    w |= set(SR.PIV_POSITIONS)
    w |= set(SR.REACTIONS_HAND) | set(SR.REACTIONS_LEG) | set(SR.REACTIONS_FACE)
    for v in SR.CUM_BY_PART.values():
        w |= set(v)
    w |= set(SEX_FACE)
    for v in list(SEX_FACE_BY_ATT.values()) + list(SEX_FACE_WATCH.values()):
        w |= set(v)
    for v in CHEST_EXPOSE.values():
        w |= {x for x in v if x}
    for v in REAR_EXPOSE.values():
        w |= {x for x in v if x}
    for c, sh in PUBIC_STATES.values():
        w.add(f"{sh} {c} pubic hair")
    for gs in GAZE_BY_TIER["sex"]:
        w.add(gs)
    for n, a, b, _p in TOYS:
        w.add(n)
        for s in list(a) + list(b):
            if s:
                w.add(s)
                w.add(f"{s} {n}")
    w |= {A_MALE, "explicit", "1boy", "faceless male",
          "man's lower body and feet visible", "side view, viewed from the side"}
    return w

_WL = _whitelist()
_WL_KEYS = re.compile(
    r"(penis|pussy|anal|cum|creampie|fellatio|paizuri|footjob|handjob|cunnilingus|"
    r"nipple|clitoris|penetrat|inserted|dildo|vibrator|plug|beads|fox tail|strap-on|"
    r"handcuff|blindfold|pubic hair|masturbat|fingering|orgasm|aroused|climax|"
    r"sex,|, sex|explicit|penetration)", re.I)

def _is_sex_tok(t):
    tl = t.lower().strip()
    if tl in _WL:
        return True
    return bool(_WL_KEYS.search(t))

def detect_level(prompt, rec=None):
    rec = rec or {}
    blk = (rec.get("sex_block") or "").lower()
    txt = (blk + ", " + (prompt or "")).lower() if blk else (prompt or "").lower()
    if re.search(r"exhausted|panting|afterglow|cum dripping|cum on her body.*panting", txt):
        return "after"
    if re.search(r"creampie|cum inside|cum in her ass|cum on her face|cum on her breasts|"
                 r"cum on her body|cumshot|cum in her mouth", txt):
        return "ejac"
    if re.search(r"penis inserted|visible penetration|\bsex\b", txt) and \
       re.search(r"missionary|doggystyle|cowgirl|spooning|standing sex|on all fours|straddling", txt):
        return "sex"
    if re.search(r"masturbation|fingering herself|masturbating|kiss|tongue kiss|foreplay|"
                 r"half-naked|crotchless", txt):
        return "foreplay"
    if re.search(r"nipples visible|pussy exposed|bare breasts|top pulled up|unbuttoned", txt):
        return "exposed"
    if re.search(r"see-through|visible through|showing through|cleavage|camel toe|upskirt|"
                 r"strap slipped|hem lifted", txt):
        return "tease"
    return "fashion"

_GARMENT = [
    (("bra",), "bra unhooked"),
    (("panties",), "panties around one thigh"),
    (("blouse", "shirt"), "shirt lifted up"),
    (("skirt",), "skirt pulled up"),
    (("jeans", "pants", "trousers", "shorts"), "pants pulled down"),
    (("dress", "gown"), "dress pulled down"),
    (("cardigan", "jacket", "hoodie", "sweater"), "cardigan slipping off her shoulder"),
]

def cloth_advance(toks, tgt, rng):
    ti = LEVELS.index(tgt)
    if ti <= LEVELS.index("tease"):
        return toks, []
    notes, drop, add = [], set(), []
    for i, t in enumerate(toks):
        tl = t.lower()
        for kws, un in _GARMENT:
            if any(re.search(r"\b" + re.escape(k) + r"s?\b", tl) for k in kws):
                if ti == LEVELS.index("exposed"):
                    add.append(un)
                    notes.append(f"让位：{un}")
                else:
                    if rng.random() < 0.5:
                        drop.add(i)
                        notes.append("脱掉了：" + t)
                    else:
                        add.append(un)
                        notes.append(f"让位：{un}")
                break
    out = [t for i, t in enumerate(toks) if i not in drop] + add
    return out, notes

def build_block(level, rng, char=None):
    f1 = lambda d: rng.choice(d)
    daily = ["closed-mouth smile", "soft smile", "calm neutral expression"]
    if level == "fashion":
        return [f1(daily), f1(GAZE_BY_TIER["fashion"])]
    if level == "tease":
        return [f1(["nipples showing through the fabric", "see-through fabric",
                    "visible through clothes", "cleavage visible"]),
                f1(SEX_FACE_BY_ATT["shy"][:2] + ["shy smile"]),
                f1(GAZE_BY_TIER["tease"])]
    if level == "exposed":
        org = list(SR.ORGAN_ALWAYS)
        if char in PUBIC_STATES:
            c, sh = PUBIC_STATES[char]
            org.append(f"{sh} {c} pubic hair")
        return org + [f1(["seductive smile", "half-lidded eyes", "flushed cheeks"]),
                      f1(GAZE_BY_TIER["exposed"])]
    if level == "foreplay":
        org = list(SR.ORGAN_ALWAYS)
        pre = rng.choice([["masturbation", "fingering herself", "half-naked"],
                          ["kiss", "tongue kiss", "foreplay", "half-naked"]])
        return org + pre + [f1(["parted lips", "heavy blush", "moaning"]),
                            f1(GAZE_BY_TIER["sex"])]
    pos = f1(A_POSITIONS)
    core = list(SR.ORGAN_ALWAYS) + list(pos) + ["penis inserted into pussy", "visible penetration"]
    if level == "sex":
        return core + [A_MALE, f1(SR.REACTIONS_LEG), f1(SEX_FACE_BY_ATT["bold"]),
                       f1(GAZE_BY_TIER["sex"])]
    if level == "ejac":
        ej = rng.choice([["creampie", "cum inside her pussy"],
                         ["cum on her body"], ["cumshot", "cum on her face"]])
        return core + ej + [A_MALE, f1(SR.REACTIONS_LEG), f1(["heavy blush", "parted lips"]),
                            f1(GAZE_BY_TIER["sex"])]
    return list(SR.ORGAN_ALWAYS) + ["lying on her back", "panting", "heavy blush",
                                    "cum on her body", "cum dripping", "exhausted expression",
                                    "afterglow", f1(daily)]

def advance(prompt, rng, rec=None, steps=1):
    rec = rec or {}
    cur = detect_level(prompt, rec)
    i = LEVELS.index(cur)
    tgt = LEVELS[min(len(LEVELS) - 1, i + steps)]
    if tgt == cur:
        return prompt, cur, tgt, False, ["已经是最高档（事后）"]
    toks = [t.strip() for t in (prompt or "").split(",") if t.strip()]

    blk = [x.strip() for x in (rec.get("sex_block") or "").split(",") if x.strip()]
    if blk:
        bs = set(blk)
        toks = [t for t in toks if t not in bs]
    toks = [t for t in toks if not _is_sex_tok(t)]

    toks, cnotes = cloth_advance(toks, tgt, rng)

    if tgt == "fashion":
        toks = [t for t in toks if t.lower() not in ("ecchi", "explicit", "1boy")]
        if not any("casual fashion" in t.lower() for t in toks):
            toks = ["masterpiece, best quality, casual fashion, everyday outfit, 1girl, solo"]
            toks += [t for t in [x.strip() for x in (prompt or "").split(",")]
                     if t and t.lower() not in ("masterpiece", "best quality", "ecchi",
                                                "explicit", "1girl", "solo")][:1]
    toks = [t.strip() for t in toks if t and t.strip()]
    toks += [x for x in build_block(tgt, rng, rec.get("character") or "") if x]
    return ", ".join(toks), cur, tgt, True, cnotes
