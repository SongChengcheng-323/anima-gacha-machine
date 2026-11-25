import re

WORK_CN = {
    "vocaloid": "VOCALOID",
    "original": "原创",
}

CHAR_WORK = {
    "hatsune_miku": "vocaloid",
}

def _norm_key(key):
    return (key or "").strip().lower().replace(" ", "_")

def work_of(tag):
    t = (tag or "").strip()
    if not t:
        return ""
    low = t.lower()
    for _k in (low, low.replace("_", " "), low.replace(" ", "_")):
        if _k in CHAR_WORK:
            return _norm_key(CHAR_WORK[_k])
    m = re.search(r"\(([^()]+)\)\s*$", t)
    if m:
        return _norm_key(m.group(1))
    return ""

def work_cn(key):
    if not key:
        return ""
    return WORK_CN.get(key) or WORK_CN.get(_norm_key(key)) or key

if __name__ == "__main__":
    for t in ["hatsune_miku"]:
        k = work_of(t)
        print(f"  {t:34s} -> {k:22s} {work_cn(k)}")
