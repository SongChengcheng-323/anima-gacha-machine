import collections
import random

META = {
    "id": "sex_draw",
    "cn": "性爱·单抽机",
    "kind": "machine",
    "tier": "sex",
    "parent": None,
    "enabled": True,
    "desc": "单抽版性爱场景生成：动作层 + 状态层 + 三层互斥 + 挂载 + 提示词拼装（⚠️ 未接入）",
    "version": "v0.97.0",
    "refs": ["pools.sex_pool", "pools.state_pool"],
}
try:
    from pools import sex_pool as SP
    from pools import state_pool as SPL
    from pools import roll_params as _RP
except Exception:
    import sex_pool as SP
    import state_pool as SPL
    import roll_params as _RP

OCCUPY = {
    "missionary": {"her.crotch", "him.penis"}, "doggystyle": {"her.crotch", "him.penis"},
    "cowgirl": {"her.crotch", "him.penis"}, "reverse_cowgirl": {"her.crotch", "him.penis"},
    "squatting_cowgirl": {"her.crotch", "him.penis"},
    "mating_press": {"her.crotch", "him.penis"}, "spooning": {"her.crotch", "him.penis"},
    "standing_wall": {"her.crotch", "him.penis"},
    "fellatio": {"her.mouth", "him.penis"},
    "cunnilingus": {"him.mouth", "her.crotch"},
    "handjob": {"her.hand", "him.penis"},
    "paizuri": {"her.chest", "him.penis"},
    "footjob": {"her.foot", "him.penis"},
    "anal": {"her.rear", "him.penis"},
    "fingering": {"him.hand", "her.crotch"},
    "masturbation": {"her.hand", "her.crotch"},
    "toy": {"her.hand", "her.crotch"},
    "lick_ass": {"him.mouth", "her.rear"},
    "kiss": {"her.mouth", "him.mouth"},
    "tonguekiss": {"her.mouth", "him.mouth"},
    "suck_fingers": {"her.mouth", "him.hand"},
    "suck_nipple": {"him.mouth", "her.chest"},
    "lick_nipple": {"him.mouth", "her.chest"},
    "self_pinch": {"her.hand", "her.chest"},
    "kiss_hand": {"him.mouth", "her.hand"},
    "hold_hands": {"her.hand", "him.hand"},
    "lick_hand": {"him.mouth", "her.hand"},
    "spank": {"him.hand", "her.rear"},
    "licking": {"her.mouth"},
    "fondle": {"him.hand"},
}

RES_QUOTA = {
    "her.mouth": 1, "her.hand": 2, "her.chest": 1,
    "her.crotch": 1, "her.rear": 1, "her.foot": 2,
    "him.mouth": 1, "him.hand": 2,
    "him.penis": 1, "him.foot": 2,
}

MOUTH_ATTACH = {"kiss", "tonguekiss", "suck_fingers", "suck_nipple",
                "lick_nipple", "kiss_hand", "lick_hand", "licking"}

NO_MOUTH = {
    "doggystyle": "后入 —— 背向，亲不到",
    "anal": "肛交（后入式）—— 背向",
    "lick_ass": "舔肛 —— 她趴着，他嘴在她后面",
    "cowgirl": "女上位 —— 她跪坐在上方，上半身有高度差",
    "reverse_cowgirl": "反向女上位 —— 背对，双重",
    "squatting_cowgirl": "蹲坐女上位 —— 蹲着，更高",
    "footjob": "⭐ 足交 —— 设计动机：上半身离得远、她坐高位踩下来",
    "paizuri": "乳交 —— 胸忙、脸也贴在那儿 ⇒ **不给嘴部附加动作**",
}

MOUTH_FREE = {
    "missionary": "传教士 —— 面对面贴合，上身抬起就能亲 ⭐已约定",
    "spooning": "侧卧 —— 侧躺贴着她，她转头就够到 ⭐已约定（侧入）",
    "standing_wall": "站立 —— 面对面抱着，头能靠过来 ⭐已约定",
    "mating_press": "压制 —— 面对面贴合（腿虽被压，上半身是贴的）",
    "fellatio": "口交 —— 她嘴虽忙，但**他俯身**够得到她胸口",
    "cunnilingus": "舔阴 —— 他嘴忙（资源层会拦），她的手自由",
    "handjob": "手交 —— 站/跪位置灵活",
    "fingering": "指交 —— 位置灵活（她可以坐/躺）",
    "suck_nipple": "吸乳 —— 面对面贴近（他的嘴忙，资源层会拦他嘴上的互动）",
    "lick_nipple": "舔乳 —— 同上",
    "masturbation": "自慰（单人）—— 无嘴部互动",
    "toy": "玩具（单人）—— 无嘴部互动",
}

FOOTJOB_EXTRA_BAN = {"hold_hands", "fondle", "spank"}

MOUNT = [
    {"pose": "mating_press", "other": "*", "add": {"camera": "from the side"}},
]

def mounts_for(plays):
    out = {}
    for m in MOUNT:
        if m["pose"] not in plays:
            continue
        if m["other"] != "*" and m["other"] not in plays:
            continue
        for k, v in m["add"].items():
            out.setdefault(k, v)
    return out

def camera_hint(plays):
    return mounts_for(plays).get("camera", "")

RELEASE_OVERRIDE = {
    "footjob": {"self_pinch"},
}

def released(pose, other):
    if other in MOUTH_ATTACH and pose in NO_MOUTH:
        return False
    if pose == "footjob" and other in FOOTJOB_EXTRA_BAN:
        return False
    ov = RELEASE_OVERRIDE.get(pose)
    return (other in ov) if ov is not None else True

CORE_WEIGHT = {
    "position": 49.0,
    "fellatio": 8.0, "cunnilingus": 7.0, "handjob": 6.0, "paizuri": 6.0,
    "anal": 6.0, "fingering": 5.0, "footjob": 4.0,
    "lick_ass": 1.5,
    "masturbation": 6.0, "toy": 6.0,
}
ATTACH_P = {
    "kiss": 0.25, "tonguekiss": 0.15, "suck_fingers": 0.18,
    "suck_nipple": 0.18, "lick_nipple": 0.15, "self_pinch": 0.10,
    "kiss_hand": 0.17, "hold_hands": 0.24, "lick_hand": 0.14, "spank": 0.28,
    "licking": 0.12, "fondle": 0.15,
}

SAME_SLOT = [
    {"kiss", "tonguekiss"},
    {"suck_fingers", "kiss_hand", "lick_hand"},
]

SOLO_OK_ATTACH = {"self_pinch"}
MAX_ATTACH = 2

def _coverage_check():
    return [p for p in SP.core_plays() if p not in MOUTH_FREE and p not in NO_MOUTH]

def core_key(p):
    return "position" if SP.SEX_POOL[p].get("parent") == "position" else p

def check_resource(plays):
    t = collections.Counter()
    for p in plays:
        for r in OCCUPY.get(p, ()):
            t[r] += 1
    return [f"{r} 用了 {n}（配额 {RES_QUOTA[r]}）"
            for r, n in t.items() if n > RES_QUOTA.get(r, 1)]

def check_pose(plays):
    bad = []
    for p in plays:
        if p in NO_MOUTH:
            for b in plays:
                if b in MOUTH_ATTACH:
                    bad.append(f"{SP.SEX_POOL[p]['cn']} 与 {SP.SEX_POOL[b]['cn']} 姿态互斥")
        if p == "footjob":
            for b in plays:
                if b in FOOTJOB_EXTRA_BAN:
                    bad.append(f"足交 与 {SP.SEX_POOL[b]['cn']} 姿态互斥")
    return sorted(set(bad))

def check_solo(plays):
    if not plays or not SP.is_solo(plays[0]):
        return []
    bad = [p for p in plays[1:] if p not in SOLO_OK_ATTACH]
    return [f"单人场景却出现需要对方的：{' / '.join(bad)}"] if bad else []

def check_same_slot(plays):
    return [f"{' / '.join(sorted(g))} 是同一槽位（语义重复）"
            for g in SAME_SLOT if len(g & set(plays)) > 1]

def check_release(plays):
    bad = []
    for p in plays:
        for o in plays:
            if p != o and not released(p, o):
                bad.append(f"{SP.SEX_POOL[p]['cn']} **没有释放** {SP.SEX_POOL[o]['cn']}")
    return sorted(set(bad))

def is_legal(plays):
    return not (check_resource(plays) or check_pose(plays) or check_solo(plays)
                or check_same_slot(plays) or check_release(plays)
                or SP.check_bottom_line(plays))

def _canon_of(play):
    v = (SP.SEX_POOL or {}).get(play) or {}
    c = (v.get("canon") or "").strip() if isinstance(v, dict) else ""
    if c:
        return c
    al = SP.aliases_of(play)
    return al[0] if al else play

SOLO_P_BY_TRAIT = {
    "成熟": 0.22,
    "可爱": 0.14,
    "无口": 0.12,
    "害羞": 0.06,
}
SOLO_P_DEFAULT = 0.12

PLAY_TRAIT_W = {
    "成熟": {"masturbation": 1.7, "toy": 1.9},
    "可爱": {"masturbation": 1.0, "toy": 1.2},
    "无口": {"masturbation": 0.8, "toy": 0.6},
    "害羞": {"masturbation": 0.45, "toy": 0.30},
}

def draw(rng, solo=None, profile=None, trait=None):
    pool = [p for p in SP.core_plays()
            if solo is None
            or (SP.is_solo(p) if solo else not SP.is_solo(p))]
    if not pool:
        pool = list(SP.core_plays())
    keys = sorted({core_key(p) for p in pool})
    _tw = PLAY_TRAIT_W.get(trait or "", {})
    w = [CORE_WEIGHT.get(k, 1.0) * float(_tw.get(k, 1.0)) for k in keys]
    k = rng.choices(keys, weights=w, k=1)[0]
    if k == "position":
        opts = [p for p in SP.plays_of_group("position") if p in pool]
        core = rng.choice(opts or list(pool))
    else:
        core = k

    plays = [core]
    is_solo = SP.is_solo(core)
    cands = [a for a in SP.attach_plays()
             if rng.random() < ATTACH_P.get(a, 0.0)
             and (not is_solo or a in SOLO_OK_ATTACH)]
    rng.shuffle(cands)
    for a in cands:
        if len(plays) - 1 >= MAX_ATTACH:
            break
        if is_legal(plays + [a]):
            plays.append(a)

    insert_en = []
    _is_anal = any(p == "anal" for p in plays)
    if (not _is_anal) and any(p in ("missionary", "doggystyle", "cowgirl", "reverse_cowgirl",
                                    "squatting_cowgirl", "mating_press",
                                    "spooning", "standing_wall") for p in plays):
        insert_en = [rng.choice(SP.PENETRATION_MARKS)]

    if "cunnilingus" in plays and "fondle" in plays:
        plays.remove("fondle")

    st_en, st_cn, st_meta = SPL.state_for(plays, rng, profile=profile)
    if getattr(_RP, "USE_STATUS_V3", False):
        _ej = st_meta.get("ejac") or ""
        _ss = (st_meta.get("status_str") or "") if isinstance(st_meta.get("status_str"), str) else ""
        _keep = {w for w in (_ej, _ss) if w}
        _pairs = [(e, c) for e, c in zip(st_en, st_cn) if e in _keep]
        st_en = [e for e, _c in _pairs]
        st_cn = [c for _e, c in _pairs]
    return {
        "plays": plays,
        "act_en": (insert_en
                   + ([_canon_of(plays[0])] if plays else [])
                   + [_canon_of(k) for k in plays[1:]]),
        "act_cn": [SP.SEX_POOL[k]["cn"] for k in plays],
        "state_en": st_en,
        "state_cn": st_cn,
        "state_meta": st_meta,
        "solo": is_solo,
        "camera": camera_hint(plays),
        "mounts": mounts_for(plays),
    }

DEFAULT_PREFIX = "masterpiece, best quality, uncensored, ecchi, explicit, 1girl"
MALE_TAG = "1boy, young man"

def assemble(char, body, solo=False, prefix=DEFAULT_PREFIX,
             male=MALE_TAG, camera=True):
    parts = [prefix, char]
    if not solo:
        parts.append(male)
    parts.extend(body["act_en"])
    parts.extend(body["state_en"])
    if camera and body.get("camera"):
        parts.append(body["camera"])
    return ", ".join(p for p in parts if p)

def pick(rng, solo=False, char=None, camera=True, prefix=DEFAULT_PREFIX, male=MALE_TAG,
         profile=None):
    body = draw(rng, solo=solo, profile=profile)
    return {"body": body,
            "prompt": assemble(char, body, solo=solo, prefix=prefix, male=male,
                               camera=camera) if char else None}

def selfcheck(verbose=False):
    problems = []
    miss = _coverage_check()
    if miss:
        problems.append(f"核心玩法没有姿态归属：{miss}")
    for p in SP.SEX_POOL:
        if p not in OCCUPY:
            problems.append(f"{p} 没登记资源占用")
    for p in OCCUPY:
        if p not in SP.SEX_POOL:
            problems.append(f"{p} 已从池子删除，但资源表还在 ✗")
    for k in CORE_WEIGHT:
        if k != "position" and k not in SP.SEX_POOL:
            problems.append(f"主戏权重表里的 {k} 不在池子里 ✗")
    for k in ATTACH_P:
        if k not in SP.SEX_POOL:
            problems.append(f"附加概率表里的 {k} 不在池子里 ✗")
    rng = random.Random(20261007)
    viol = []
    for _ in range(5000):
        plays = draw(rng)["plays"]
        v = (check_resource(plays) + check_pose(plays) + check_solo(plays)
             + check_same_slot(plays) + check_release(plays) + SP.check_bottom_line(plays))
        if v:
            viol.append((plays, v))
    if viol:
        problems.append(f"抽选违反互斥 {len(viol)} 次，例：{viol[0]}")
    r = random.Random(7)
    for _ in range(3000):
        c = draw(r)["plays"]
        if "footjob" in c and set(c) & {"kiss", "tonguekiss", "suck_nipple", "hold_hands"}:
            problems.append(f"足交搭上了嘴部/牵手：{c}")
            break
    for _ in range(3000):
        c = draw(r)["plays"]
        if len({"suck_fingers", "kiss_hand", "lick_hand"} & set(c)) > 1:
            problems.append(f"互相含手指同现：{c}")
            break
    if verbose:
        print(f"  性爱单抽机自检：{'✗ ' + '；'.join(problems) if problems else '✓ 全过'}")
        print(f"    核心 {len(SP.core_plays())} · 附加 {len(SP.attach_plays())} · "
              f"资源槽 {len(RES_QUOTA)} · 挂载 {len(MOUNT)} · 语义互斥 {len(SAME_SLOT)} 组")
    return problems

if __name__ == "__main__":
    import sys
    sys.exit(1 if selfcheck(verbose=True) else 0)
