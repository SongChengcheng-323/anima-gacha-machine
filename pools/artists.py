META = {
    "id": "artists",
    "cn": "画师池",
    "kind": "pool",
    "tier": "none",
    "parent": None,
    "enabled": True,
    "version": "v1.0.0",
    "desc": "画师 tag 池；与画风同维度（二选一）；写法 `@名字` 且放质量词正后方",
}

# 键 = 画师 tag，值 = 抽取权重（> 0）。写法统一 `@tag`。
# 留空即不抽画师；想用就自己往里加。
ARTIST_POOL = {}

# 键 = 已退役的画师 tag，值 = 下架原因（自由文本）。
ARTIST_OFF = {}

ENABLED = False
ARTIST_ON = ()


def weights():
    if not ENABLED:
        return {}
    return {k: v for k, v in ARTIST_POOL.items() if k in ARTIST_ON}


def prompt_tag(name):
    return "@%s" % name


def selfcheck(verbose=False):
    problems = []
    for k, v in ARTIST_POOL.items():
        if not isinstance(v, (int, float)) or v <= 0:
            problems.append("画师 %r 权重非法：%r" % (k, v))
        if k.startswith("_"):
            problems.append("停用的画师 %r 混进了池子" % k)
    for k in ARTIST_OFF:
        if k in ARTIST_POOL:
            problems.append("已退役的画师 %r 又在池子里" % k)
    for k in ARTIST_ON:
        if k not in ARTIST_POOL:
            problems.append("在用名单里的画师 %r 不在池子里" % k)
        if k in ARTIST_OFF:
            problems.append("在用名单里的画师 %r 已被退役" % k)
    if verbose:
        print("  画师池自检：%s" % ("；".join(problems) if problems else "全过"))
        print("    在用 %d 位 · 停用 %d 位 · 权重合计 %.1f"
              % (len(ARTIST_POOL), len(ARTIST_OFF), sum(ARTIST_POOL.values())))
    return problems


if __name__ == "__main__":
    import sys
    sys.exit(1 if selfcheck(verbose=True) else 0)
