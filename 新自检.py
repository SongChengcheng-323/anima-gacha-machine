import io
import json
import os
import importlib
import random
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    import paths as _PATHS0
    _PATHS0.setup_console()
except Exception:
    pass
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CJK = re.compile(r"[\u4e00-\u9fff]")

VALID_TIERS = ("general", "fashion", "tease", "exposed", "sex")
SUB_TIER = {"擦边": "tease", "暴露": "exposed", "时尚福利": "fashion"}
BIG_TIER = {"性爱": "sex"}

N_PER_TIER = 30
SERVICE = "http://127.0.0.1:8900"

_WATCH = ("tag_library.json", "taglib_cn.json", "tag_tiers.json", "_禁用.json")

def _snapshot():
    snap = {}
    for name in _WATCH:
        fp = os.path.join(ROOT, name)
        try:
            st = os.stat(fp)
            snap[name] = (st.st_mtime_ns, st.st_size)
        except OSError:
            snap[name] = None
    return snap

class Report:
    def __init__(self, quiet=False):
        self.rows = []
        self.quiet = quiet

    def add(self, name, problems, note=""):
        self.rows.append((name, not problems, list(problems), note))

    def skip(self, name, why=""):
        self.rows.append((name, None, [], why))

    def render(self):
        bad = 0
        for name, ok, problems, note in self.rows:
            if ok is None:
                if not self.quiet:
                    print(f"[SKIP] {name}   —— {note}")
                continue
            if ok:
                if not self.quiet:
                    print(f"[OK] {name}" + (f"   （{note}）" if note else ""))
            else:
                bad += 1
                print(f"[FAIL] {name}   —— {len(problems)} 处问题")
                for p in problems[:20]:
                    print(f"     · {p}")
                if len(problems) > 20:
                    print(f"     · …（共 {len(problems)} 处，只列前 20）")
        return bad

def check_chain(rep):
    problems = []
    prompts = {}
    try:
        from pools import orchestrator as OR
    except Exception as e:
        rep.add("新链跑通（四档抽样）", [f"import orchestrator 失败：{type(e).__name__}: {e}"])
        return {}
    EXPECT = OR.expect_by_tier()
    for tier in ("fashion", "tease", "exposed", "sex"):
        rng = random.Random(20261007)
        got, tiers_seen = [], []
        for i in range(N_PER_TIER):
            try:
                p, ctx = OR.run(rng, tier=tier)
            except Exception as e:
                problems.append(f"[{tier}] 第 {i+1} 条抛异常：{type(e).__name__}: {e}")
                break
            if not p or not p.strip():
                problems.append(f"[{tier}] 第 {i+1} 条跑出空提示词 ✗")
                break
            for b in EXPECT[tier]:
                if OR.missing_block(tier, b, ctx):
                    problems.append(f"[{tier}] 第 {i+1} 条缺「{b}」块 ✗")
            got.append(p)
            tiers_seen.append(ctx.get("tier"))
        if tiers_seen and any(t != tier for t in tiers_seen):
            problems.append(f"[{tier}] 抽出的 ctx['tier'] 与请求不符 ✗")
        prompts[tier] = got
    rep.add("新链跑通（四档各 %d 条 · 无异常 + 块齐全）" % N_PER_TIER,
            problems, note="fashion/tease/exposed/sex")
    return prompts

def _load_lib():
    return json.load(io.open(os.path.join(ROOT, "tag_library.json"), encoding="utf-8"))

def check_cn(rep, lib):
    problems, total = [], 0
    for c in lib.get("categories", []):
        for s in c.get("subs", []) or []:
            for it in s.get("items", []) or []:
                total += 1
                en = (it.get("en") or "").strip()
                cn = (it.get("cn") or "").strip()
                if not cn:
                    problems.append(f"无中文：{en!r}（{c.get('label')}/{s.get('label')}）")
                elif not CJK.search(cn):
                    problems.append(f"中文栏不是中文：{en!r} → {cn!r}（{s.get('label')}）")
                elif cn.lower() == en.lower():
                    problems.append(f"中文=英文（未翻译）：{en!r}（{s.get('label')}）")
    rep.add("词库·每条有真中文（含汉字 且 ≠ 英文）", problems, note=f"共 {total} 条")

def check_category(rep, lib):
    problems = []
    cats = lib.get("categories") or []
    if not cats:
        problems.append("tag_library.json 没有 categories ✗")
    for c in cats:
        if not c.get("key"):
            problems.append(f"大类缺 key：{c.get('label')!r}")
        if not c.get("label"):
            problems.append(f"大类缺 label：{c.get('key')!r}")
        subs = c.get("subs")
        if not subs:
            problems.append(f"大类 {c.get('key')!r} 没有小类（subs）✗")
            continue
        for s in subs:
            if not (s.get("label") or "").strip():
                problems.append(f"小类缺 label（大类 {c.get('key')}）")
            if not (s.get("items") or []):
                problems.append(f"小类「{s.get('label')}」没有词条 ✗")
            for it in (s.get("items") or []):
                if not (it.get("en") or "").strip():
                    problems.append(f"词条缺 en（{c.get('label')}/{s.get('label')}）")
    rep.add("词库·分类非空（大类/小类/词条层级完整）", problems,
            note=f"{len(cats)} 大类")

def _tier_map(lib, tag_tiers):
    t = dict((tag_tiers or {}).get("tags") or {})
    m = {}
    for c in lib.get("categories", []):
        big = c.get("label") or ""
        for s in c.get("subs", []) or []:
            lab = s.get("label") or ""
            tier = SUB_TIER.get(lab) or BIG_TIER.get(big) or "general"
            for it in s.get("items", []) or []:
                en = it.get("en")
                if not en:
                    continue
                if big in BIG_TIER:
                    m[en] = tier
                else:
                    m.setdefault(en, t.get(en, tier))
    return m

def check_tier(rep, lib):
    problems = []
    fp = os.path.join(ROOT, "tag_tiers.json")
    try:
        tt = json.load(io.open(fp, encoding="utf-8"))
    except Exception as e:
        rep.add("词库·尺度归属", [f"读不到 tag_tiers.json：{type(e).__name__}: {e}"])
        return {}
    tags = tt.get("tags") or {}
    for w, v in tags.items():
        if v not in VALID_TIERS:
            problems.append(f"tag_tiers 尺度非法：{w!r} → {v!r}")
    m = _tier_map(lib, tt)
    for c in lib.get("categories", []):
        big = c.get("label") or ""
        for s in c.get("subs", []) or []:
            lab = s.get("label") or ""
            tiered = (lab in SUB_TIER) or (big in BIG_TIER)
            if not tiered:
                continue
            for it in s.get("items", []) or []:
                en = it.get("en")
                if en and m.get(en) in (None, "", "general"):
                    problems.append(f"分档小类的词没有尺度：{en!r}（{lab or big}）→ {m.get(en)!r}")
    missing = [en for en in (it.get("en") for c in lib.get("categories", [])
                             for s in c.get("subs", []) for it in s.get("items", []))
               if en and m.get(en) not in VALID_TIERS]
    for en in missing[:20]:
        problems.append(f"词无法定尺度：{en!r}")
    rep.add("词库·尺度归属（每词有尺度 · 分档词不许落 general）", problems,
            note=f"tag_tiers {len(tags)} 词 / 树 {len(m)} 词")
    return m

def check_prompt_quality(rep, prompts):
    problems, n = [], 0
    single = re.compile(r"^[a-z]$")
    for tier, ps in prompts.items():
        for p in ps:
            n += 1
            toks = [x.strip() for x in p.split(",") if x.strip()]
            for t in toks:
                if single.match(t.lower()):
                    problems.append(f"[{tier}] 单字母碎片：{t!r}（{p[:60]}…）")
            if CJK.search(p):
                problems.append(f"[{tier}] 提示词里有中文残留：{CJK.search(p).group()}（{p[:60]}…）")
            low = [t.lower() for t in toks]
            dup = {x for x in low if low.count(x) > 1}
            for d in dup:
                problems.append(f"[{tier}] 重复段：{d!r}（{p[:60]}…）")
    rep.add("提示词质量（无单字母碎片 / 无中文残留 / 无重复段）", problems,
            note=f"共 {n} 条提示词")

def _get(path, timeout=6):
    req = urllib.request.Request(SERVICE + path, headers={"User-Agent": "selfcheck"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")

def _service_up():
    try:
        code, _ = _get("/api/version")
        return code == 200
    except Exception:
        return False

def check_service(rep):
    if not _service_up():
        rep.skip("服务健康（:8900）", "相册没启动，跳过")
        return
    problems = []
    for path in ("/api/version", "/api/taglib"):
        try:
            code, body = _get(path)
            if code != 200:
                problems.append(f"{path} 返回 HTTP {code}")
        except Exception as e:
            problems.append(f"{path} 不可达：{type(e).__name__}: {e}")
    rep.add("服务健康（:8900 可达）", problems, note=SERVICE)

def check_frontend_contract(rep):
    problems = []
    try:
        code, body = _get("/api/taglib")
        d = json.loads(body)
    except Exception as e:
        rep.skip("前端数据契约（/api/taglib）", "相册没启动，跳过")
        return
    cats = d.get("categories") or []
    keys = {c.get("key") for c in cats}
    _V3MAP = {"char": "L02", "scene": "L06", "outfit": "L04"}
    _SUBKEY = {"char": "char_name", "scene": "scene_place", "eq_scene": "scene_place"}
    _LBLKW = {"char": "角色", "scene": "场景", "outfit": "装备"}
    _CHECK = ("char", "scene", "eq_scene")
    _n = {}
    for _want in _CHECK:
        sub = None
        for c in cats:
            for x in (c.get("subs") or []):
                if x.get("key") in (_want, _SUBKEY.get(_want)):
                    sub = x
                    break
            if sub:
                break
        if sub is None:
            kw = _LBLKW.get(_want)
            for c in cats:
                if kw and kw in str(c.get("label") or ""):
                    subs = c.get("subs") or []
                    sub = subs[0] if subs else None
                    break
        cnt = len((sub or {}).get("items") or [])
        _n[_want] = cnt
        if cnt == 0:
            problems.append(f"「{_want}」下拉会取到空列表 → 前端 gcSlotPool 的 "
                            f"key/子池/标签三级映射都没命中（v3 大类改名后最容易断这里）")
    if not (d.get("cat_of") or {}):
        problems.append("cat_of 为空 → 词→分类查表失效")
    if not (d.get("tiers") or {}):
        problems.append("tiers 为空 → 词没有尺度色标")
    cw = d.get("char_works") or {}
    if not cw:
        problems.append("char_works 为空（前端『作品→角色』级联会失效）")
    rep.add("前端数据契约（/api/taglib 供词→分类 / 作品→角色）", problems,
            note=("大类 key=" + ",".join(sorted(k for k in keys if k))
                  + " ｜ 下拉可用条数 " + " ".join(f"{k}:{v}" for k, v in _n.items())))

def check_modules(rep):
    problems = []
    ok_n = 0
    root = os.path.dirname(os.path.abspath(__file__))
    tops = ["paths", "works", "wardrobe", "tag_compose", "pool_gate"]
    for m in tops:
        if not os.path.exists(os.path.join(root, m + ".py")):
            problems.append("缺文件: " + m + ".py"); continue
        try:
            importlib.import_module(m); ok_n += 1
        except Exception as e:
            problems.append(m + " 导入失败: " + type(e).__name__ + ": " + str(e)[:60])
    podir = os.path.join(root, "pools")
    mods = sorted(f[:-3] for f in os.listdir(podir)
                  if f.endswith(".py") and f != "__init__.py"
                  and not f.startswith(".") and not f.startswith("._"))
    for m in mods:
        try:
            importlib.import_module("pools." + m); ok_n += 1
        except Exception as e:
            problems.append("pools." + m + " 导入失败: " + type(e).__name__ + ": " + str(e)[:60])
    rep.add("模块完整（%d 个核心模块可导入）" % (len(tops) + len(mods)), problems,
            note="顶层 %d + pools %d" % (len(tops), len(mods)))


def main():
    quiet = "--quiet" in sys.argv
    before = _snapshot()
    rep = Report(quiet=quiet)
    if not quiet:
        print("=== 新链路只读自检（新自检.py）===\n")
    try:
        lib = _load_lib()
    except Exception as e:
        print(f"[X] 读 tag_library.json 失败：{type(e).__name__}: {e}")
        return 1

    check_modules(rep)
    prompts = check_chain(rep)
    check_cn(rep, lib)
    check_category(rep, lib)
    check_tier(rep, lib)
    check_prompt_quality(rep, prompts)

    after = _snapshot()
    touched = [k for k in before if before[k] != after[k]]
    rep.add("只读自证（自检未改任何数据文件）",
            [f"{k} 被改动 ✗（自检有副作用！）" for k in touched],
            note="、".join(_WATCH))

    bad = rep.render()
    if not quiet:
        print("\n" + ("=" * 34))
        print(f"结论：{'全部通过' if not bad else f'{bad} 项未通过'}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
