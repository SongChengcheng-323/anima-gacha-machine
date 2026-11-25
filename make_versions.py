"""从 _日志.jsonl 重建 _vidx.json（版本分组索引）。

用途：相册的「版本栏」和缩略图角标要显示「这张图有几个版本」。
如果每次都遍历 15000 条日志 + 查文件，一个请求要 3~4 秒。
这个脚本把结果算成静态索引，相册直接读，变成毫秒级。

用法：
    python make_versions.py            # 重建
    python make_versions.py --check    # 只看统计，不写文件
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

VIDX_JSON = os.path.join(HERE, "_vidx.json")
LOG = os.path.join(HERE, "_日志.jsonl")


def build():
    import photo_server as PS
    parent = PS.build_parent_map()

    def root_of(x):
        seen = set()
        while x in parent and x not in seen:
            seen.add(x)
            x = parent[x]
        return x

    groups = {}
    for rel in parent:
        groups.setdefault(root_of(rel), set()).add(rel)
    for rel, r in parent.items():
        groups.setdefault(r, set()).add(r)

    counts = {}
    for r, members in groups.items():
        n = len(members)
        for m in members:
            counts[m] = n

    out = {
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "groups": {k: sorted(v) for k, v in groups.items() if len(v) >= 2},
        "counts": counts,
    }
    return out, len(parent)


def main():
    check = "--check" in sys.argv
    if not os.path.exists(LOG):
        print("找不到 _日志.jsonl: %s" % LOG)
        return 1
    lines = 0
    with open(LOG, encoding="utf-8") as f:
        for _ in f:
            lines += 1
    t0 = time.time()
    data, n_edges = build()
    sec = time.time() - t0
    n_groups = len(data["groups"])
    n_cnt = len(data.get("counts") or {})
    n_members = sum(len(v) for v in data["groups"].values())
    print("日志 %d 条 · 重抽关系 %d 条 · 版本组 %d 个（共 %d 张图）· 计数表 %d 张 · 耗时 %.2fs"
          % (lines, n_edges, n_groups, n_members, n_cnt, sec))
    if check:
        print("（--check，未写文件）")
        for root in list(data["groups"])[:5]:
            print("  %s → %d 张" % (root, len(data["groups"][root])))
        return 0
    tmp = VIDX_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, VIDX_JSON)
    print("已写入 %s（%.1f KB）" % (VIDX_JSON, os.path.getsize(VIDX_JSON) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
