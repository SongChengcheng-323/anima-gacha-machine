import json, os

TIERS = ["fashion", "tease", "exposed", "sex"]
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
_TAGS_FILE = os.path.join(ROOT, "tier_tags.json")

_CACHE = {"tags": None, "hard": None}

def _toks(s):
    return [x.strip().lower() for x in (s or "").split(",") if x.strip()]

def load():
    if _CACHE["tags"] is not None:
        return _CACHE["tags"], _CACHE["hard"]
    tags, hard = None, None
    try:
        d = json.load(open(_TAGS_FILE, encoding="utf-8"))
        tags = {t: set(d["tier_tags"].get(t, [])) for t in TIERS}
        hard = list(d.get("hard") or [])
    except Exception:
        pass
    if tags is None:
        tags, hard = {t: set() for t in TIERS}, []
    _CACHE["tags"], _CACHE["hard"] = tags, list(hard)
    return _CACHE["tags"], _CACHE["hard"]

def classify_tier(prompt, default="fashion"):
    tags, hard = load()
    low = (prompt or "").lower()
    ts = set(_toks(low))
    got = None
    for T in reversed(TIERS):
        if ts & tags[T]:
            got = T
            break
    if got != "sex" and hard and any(k in low for k in hard):
        got = "sex"
    return got or default

def matched(prompt):
    tags, _ = load()
    ts = set(_toks(prompt))
    return {T: sorted(ts & tags[T]) for T in TIERS}
