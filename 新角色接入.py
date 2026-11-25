"""把一个新角色接进抽卡机：检查 / 写入 / 自检一条龙。

用法：
    python3 新角色接入.py --check 资料.json   只体检，看还缺哪一处
    python3 新角色接入.py --add   资料.json   真写进去
    python3 新角色接入.py --list             列出已接入的角色

资料 json 最少这三项（其余可省，省略的走默认值）：

    {
      "tag":       "hatsune_miku",              // 角色 tag，全库唯一
      "work":      "vocaloid",                  // 所属作品，决定相册分类
      "features":  "aqua hair, very long twintails, aqua eyes"
    }

可选：`outfit`（默认服装）、`moods`（表情池）、`short`（短名）。
"""

import json
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

_CN_CACHE = {}

def _load(path):
    return open(os.path.join(HERE, path), encoding="utf-8").read()

def _compile_ok(src, path):
    try:
        compile(src, path, "exec")
        return True, ""
    except SyntaxError as e:
        return False, "%s（第 %s 行）" % (e.msg, e.lineno)

def _insert_before_closing(src, anchor_pat, block):
    m = re.search(anchor_pat, src, re.M)
    if not m:
        return None, "找不到锚点 %s" % anchor_pat
    line_start = src.rfind("\n", 0, m.start()) + 1
    anchor_indent = m.start() - line_start
    at = None
    pos = m.end()
    for ln in src[m.end():].split("\n"):
        stripped = ln.lstrip(" \t")
        indent = len(ln) - len(stripped)
        if stripped[:1] in ("]", "}") and indent <= anchor_indent + 1:
            at = pos
            break
        pos += len(ln) + 1
    if at is None:
        return None, "%s 之后找不到收尾行" % anchor_pat
    head = src[:at]
    stripped_head = head.rstrip(" \t\n")
    if stripped_head and stripped_head[-1] not in ",{[":
        head = stripped_head + "," + head[len(stripped_head):]
    return head + block + src[at:], ""

def _import_ok():
    code = ("import sys;sys.path.insert(0,'.');"
            "import pools.characters,pools.char_traits;print('OK')")
    r = subprocess.run([sys.executable, "-c", code], capture_output=True,
                       text=True, cwd=HERE)
    if "OK" in (r.stdout or ""):
        return True, ""
    return False, (r.stderr or "").strip().split("\n")[-1][:200]

def i_get(en):
    if not _CN_CACHE:
        try:
            _CN_CACHE.update(json.load(open(os.path.join(HERE, "taglib_cn.json"),
                                            encoding="utf-8")))
        except Exception:
            pass
    return _CN_CACHE.get(en)

def entry_points(prof):
    tag = prof["tag"]
    sp = prof.get("split") or {}
    short = prof.get("short") or tag.split("_(")[0]
    moods = prof.get("moods") or [
        "gentle smile, looking at viewer", "soft smile, blushing",
        "looking away, slight blush", "calm expression, looking at viewer"]

    e1 = ('    {"tag": %s, "hair": %s, "eyes": %s, "body": %s, "face": %s, '
          '"extra": %s, "default_outfit": %s, "props": %s},\n' % tuple(
              json.dumps(x if x is not None else "", ensure_ascii=False) for x in (
                  tag, sp.get("hair", ""), sp.get("eyes", ""), sp.get("body", ""),
                  sp.get("face", ""), sp.get("extra", ""),
                  sp.get("default_outfit", ""), sp.get("props", ""))))

    e_moods = '    "%s": [\n%s    ],\n' % (
        tag, "".join('        "%s",\n' % m for m in moods))

    tr = prof.get("traits") or {}
    e3 = '    %s: {"main": %s, "sub": %s},\n' % (
        json.dumps(tag, ensure_ascii=False),
        json.dumps(tr.get("main", "温柔"), ensure_ascii=False),
        json.dumps(list(tr.get("sub") or []), ensure_ascii=False))

    e_short = ', "%s": "%s"' % (tag, short) if short else ""

    return {"split": e1, "moods": e_moods, "traits": e3, "short": e_short,
            "short_name": short}

def check(prof):
    tag = prof["tag"]
    rows = []
    try:
        import pools.characters as C
        sp = {d["tag"] for d in C.CHARACTERS_SPLIT}
        have = {c[0] for c in C.CHARACTERS}
        rows.append(("① characters.py CHARACTERS_SPLIT（唯一源）", tag in sp, "必填"))
        rows.append(("② └ 派生到 CHARACTERS", tag in have, "自动"))
        rows.append(("③ characters.py _MOODS（必填！少了 import 会 KeyError）",
                     tag in getattr(C, "_MOODS", {}), "必填"))
        for nm, obj, lab in (("⑧ CHARACTER_WEIGHTS", C.CHARACTER_WEIGHTS, "可选"),
                             ("⑨ PUBIC", C.PUBIC, "可选"),
                             ("⑩ LORA_MAP", C.LORA_MAP, "可选"),
                             ("⑪ STYLE_LOCK", C.STYLE_LOCK, "可选"),
                             ("⑫b NO_HAIR_CHANGE", C.NO_HAIR_CHANGE, "可选")):
            rows.append((nm, tag in obj, lab))
        rows.append(("⑫ _SHORT（文件名短名）",
                     tag in getattr(C, "_SHORT", {}), "可选"))
    except Exception as e:
        rows.append(("① characters.py", False, "读不了: %s" % e))
    try:
        from pools.char_traits import CHAR_TRAITS
        rows.append(("④ char_traits.CHAR_TRAITS", tag in CHAR_TRAITS, "必填"))
    except Exception as e:
        rows.append(("④ char_traits", False, "读不了: %s" % e))
    try:
        CN = json.load(open(os.path.join(HERE, "taglib_cn.json"), encoding="utf-8"))
        rows.append(("⑤ taglib_cn.json 中文名", tag in CN, "必填"))
    except Exception as e:
        rows.append(("⑤ taglib_cn.json", False, "读不了: %s" % e))
    try:
        import works as W
        w = W.work_of(tag)
        rows.append(("⑥ works 作品归属", bool(w),
                     "自动 → %s" % (w or "⚠️ 取不到（检查 tag 括号后缀）")))
    except Exception as e:
        rows.append(("⑥ works", False, "读不了: %s" % e))
    try:
        tl = json.load(open(os.path.join(HERE, "tag_library.json"), encoding="utf-8"))
        ens = set()
        for c in tl.get("categories", []):
            for s2 in c.get("subs", []):
                if s2.get("label") == "角色":
                    ens = {i["en"] for i in s2["items"] if isinstance(i, dict)}
        rows.append(("⑦ tag_library「角色」分类", tag in ens, "必填"))
    except Exception as e:
        rows.append(("⑦ tag_library 角色分类", False, "读不了: %s" % e))
    try:
        from pools.hairstyles import HAIR_OPTIONS
        rows.append(("⑬ hairstyles.HAIR_OPTIONS", tag in HAIR_OPTIONS, "可选"))
    except Exception:
        pass
    try:
        import pools.char_profile as CP
        p = CP.CHAR_PROFILE.get(tag) or {}
        rows.append(("⑭ char_profile 设定档案",
                     bool(p.get("喜欢的体位") or p.get("香水")), "可选"))
    except Exception:
        pass
    return rows

def missing_cn():
    try:
        lib = json.load(open(os.path.join(HERE, "tag_library.json"), encoding="utf-8"))
    except Exception:
        return None
    out = []
    for c in lib.get("categories", []):
        for s in c.get("subs", []):
            for i in s.get("items", []):
                out.append((s.get("label") or "?", i["en"]))
    return [(lab, en) for lab, en in out if not i_get(en)]

def verify_sync():
    import pools.characters as C
    for d in C.CHARACTERS_SPLIT:
        assert "_feat" not in d
    SP = {d["tag"] for d in C.CHARACTERS_SPLIT}
    CH = {c[0]: c[1] for c in C.CHARACTERS}
    only_ch = sorted(set(CH) - SP)
    only_sp = sorted(SP - set(CH))
    diff = []
    for d in C.CHARACTERS_SPLIT:
        t = d["tag"]
        if t in CH and CH[t].strip() != C._feat(d).strip():
            diff.append(t)
    return only_ch, only_sp, diff

def add_role_to_taglib(tag, cn, feat_words):
    path = os.path.join(HERE, "tag_library.json")
    try:
        tl = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print("\n  ⚠️ tag_library.json 读不了（%s）⇒ 跳过角色分类" % e)
        return
    block = ([{"en": tag, "cn": cn, "c": "#7c3aed", "k": "char"}] +
             [{"en": w, "cn": i_get(w) or "", "c": "", "k": "charfeat"}
              for w in feat_words])
    work = tag.split("_(")[-1].rstrip(")") if "_(" in tag else ""
    for c in tl.get("categories", []):
        for s in c.get("subs", []):
            if s.get("label") != "角色":
                continue
            items = s["items"]
            pos, last = len(items), None
            if work:
                for i, it in enumerate(items):
                    if isinstance(it, dict) and it.get("k") == "char" \
                            and ("_(%s)" % work) in (it.get("en") or ""):
                        last = i
                if last is not None:
                    pos = last + 1
                    while pos < len(items) and isinstance(items[pos], dict) \
                            and items[pos].get("k") != "char":
                        pos += 1
            items[pos:pos] = block
            json.dump(tl, open(path, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            print("\n  ✅ tag_library.json「角色」分类：插入 %d 条（现 %d 条）%s"
                  % (len(block), len(items),
                     "（接在 %s 组后面）" % work if last is not None else "（追加末尾）"))
            return
    print("\n  ⚠️ 没找到「角色」分类 ⇒ 跳过")

def do_add(prof):
    tag = prof["tag"]
    if tag in {c[0] for c in __import__("pools.characters", fromlist=["x"]).CHARACTERS}:
        print("  ⚠️ %s 已经在名册里了 —— 本工具只做「新增」，不做改（要改请直接编辑）" % tag)
        return 1
    ep = entry_points(prof)

    edits = [
        ("pools/characters.py", r"(?m)^CHARACTERS_SPLIT = \[", ep["split"]),
        ("pools/characters.py", r"(?m)^_MOODS = \{", ep["moods"]),
        ("pools/char_traits.py", r"(?m)^CHAR_TRAITS = \{", ep["traits"]),
    ]
    pending = {}
    for path, pat, block in edits:
        src = pending.get(path) or _load(path)
        new, err = _insert_before_closing(src, pat, block)
        if err:
            print("  ❌ %s: %s" % (path, err))
            return 1
        ok, msg = _compile_ok(new, path)
        if not ok:
            print("  ❌ %s 拼接后语法错误: %s" % (path, msg))
            return 1
        pending[path] = new
        print("  ✅ %s 试拼 + 编译通过" % path)

    cn_path = os.path.join(HERE, "taglib_cn.json")
    CN = json.load(open(cn_path, encoding="utf-8"))
    for key, dictname in (("pubic", "PUBIC"), ("weight", "CHARACTER_WEIGHTS"),
                          ("lora", "LORA_MAP"), ("style_lock", "STYLE_LOCK")):
        if prof.get(key) is None:
            continue
        path = "pools/characters.py"
        src = pending.get(path) or _load(path)
        m = re.search(r"(?m)^%s = \{" % dictname, src)
        if not m:
            print("  ⚠️ 找不到 %s，跳过 %s" % (dictname, key))
            continue
        line = "    %s: %s,\n" % (json.dumps(tag, ensure_ascii=False),
                                  json.dumps(prof[key], ensure_ascii=False))
        new = src[:m.end()] + line + src[m.end():]
        ok, msg = _compile_ok(new, path)
        if not ok:
            print("  ⚠️ 写 %s 会语法错（%s）→ 跳过" % (dictname, msg))
            continue
        pending[path] = new
        print("  ✅ %s 的 %s 试拼通过" % (path, dictname))

    if ep["short"]:
        path = "pools/characters.py"
        src = pending.get(path) or _load(path)
        m = re.search(r"(?m)^_SHORT = \{([^}]*)\}", src)
        if m:
            new = src[:m.end() - 1] + ep["short"] + src[m.end() - 1:]
            ok, msg = _compile_ok(new, path)
            if ok:
                pending[path] = new
                print("  ✅ pools/characters.py 的 _SHORT 试拼通过")
            else:
                print("  ⚠️ 写 _SHORT 会语法错（%s）→ 跳过" % msg)

    for path, new in pending.items():
        open(os.path.join(HERE, path), "w", encoding="utf-8").write(new)
    if prof.get("cn"):
        CN[tag] = prof["cn"]
        json.dump(CN, open(cn_path, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        _CN_CACHE.clear()
    print("\n✅ 已写入：characters.py（SPLIT/_MOODS/可选表/_SHORT）+ char_traits.py%s"
          % (" + taglib_cn.json" if prof.get("cn") else ""))

    ok, err = _import_ok()
    if not ok:
        print("\n  ❌❌ 落盘后 characters.py **import 不了**：")
        print("      " + err)
        print("      ⇒ 立刻回滚： git checkout pools/characters.py pools/char_traits.py")
        return 1
    print("  ✅ 落盘后真 import 通过（_MOODS / 派生链都活着 ✓）")

    sp = next((d for d in __import__("pools.characters", fromlist=["x"]).CHARACTERS_SPLIT
               if d["tag"] == tag), {})
    feats = [x.strip() for k in ("hair", "eyes", "body", "face", "extra")
             for x in (sp.get(k) or "").split(",") if x.strip()]
    add_role_to_taglib(tag, prof.get("cn", tag), feats)

    miss = missing_cn()
    if miss:
        print("\n  ── tag_library.json 里还有 %d 条**缺中文** ──" % len(miss))
        for lab, en in miss[:12]:
            print("     [%s] %s" % (lab, en))
        if len(miss) > 12:
            print("     … 还有 %d 条" % (len(miss) - 12))
        print("   （补进 taglib_cn.json 即可；**只增不减** ✗ 别删旧的 ✓）")
    else:
        print("\n  ✅ 中文翻译齐全，不用补")

    if prof.get("hair_options"):
        print("  · 发型候选：手动加进 pools/hairstyles.py 的 HAIR_OPTIONS")
    if prof.get("profile"):
        print("  · 设定档案已记录")

    print("\n  ── 别忘了 ──")
    print("   · 相册要**重启**才认新分类：launchctl bootout/bootstrap photo-album ✓")
    print("   · 出图链路要**重启**才认新角色：同上，auto-roll ✓")
    return 0

def main():
    args = sys.argv[1:]
    if not args or args[0] == "--list":
        print(__doc__)
        na, nb, diff = verify_sync()
        import pools.characters as C
        print("\n【一致性自检】")
        print("  名册 %d 人 · 只在一处: %s %s · 特征串不一致: %d %s"
              % (len(C.CHARACTERS), na or "无", nb or "无", len(diff), diff[:5]))
        print("  _MOODS %d 条 · SPLIT %d 人（应相等 ✓）"
              % (len(getattr(C, "_MOODS", {})), len(C.CHARACTERS_SPLIT)))
        return 0
    if len(args) < 2:
        print("用法: 新角色接入.py --check|--add <资料.json>")
        return 1
    mode, path = args[0], args[1]
    prof = json.load(open(path, encoding="utf-8"))
    tag = prof["tag"]
    print("═══ 新角色接入：%s（%s）═══\n" % (prof.get("cn", tag), tag))
    if mode == "--check":
        rows = check(prof)
        miss_req = []
        for name, have, note in rows:
            mark = "✅" if have else ("✗" if note == "必填" else "·")
            print("  %s %-46s %s" % (mark, name, note))
            if not have and note == "必填":
                miss_req.append(name)
        print()
        na, nb, diff = verify_sync()
        print("  ⚠️ 一致性: 只在一处 %s / %s / 特征串不一致 %d"
              % (na or "无", nb or "无", len(diff)))
        print("\n  还缺 %d 处必填: %s" % (len(miss_req), miss_req or "无 ✓"))
        print("  （可选项目即使缺也能跑，只是少点效果）")
        return 0
    if mode == "--add":
        return do_add(prof)
    print("未知模式 %s" % mode)
    return 1

if __name__ == "__main__":
    sys.exit(main())
