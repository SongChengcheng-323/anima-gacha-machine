import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OFF_FILE = os.path.join(HERE, "_禁用.json")

def key_of(x):
    if isinstance(x, str):
        return x
    if isinstance(x, (list, tuple)):
        return str(x[0]) if x else ""
    if isinstance(x, dict):
        for k in ("desc", "key", "name"):
            if x.get(k):
                return str(x[k])
        return ""
    return str(x)

def load():
    try:
        with open(OFF_FILE, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}

def save(d):
    tmp = OFF_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OFF_FILE)
    _CACHE["mtime"] = None

_CACHE = {"mtime": None, "data": {}}

def cached():
    try:
        m = os.path.getmtime(OFF_FILE)
    except OSError:
        m = 0
    if _CACHE["mtime"] != m:
        _CACHE["data"] = load()
        _CACHE["mtime"] = m
    return _CACHE["data"]

def _segs(s):
    out = [s]
    for t in s.split(","):
        t = t.strip()
        if t and t != s:
            out.append(t)
    return out

def is_off(off, x):
    if not off:
        return False
    k = key_of(x)
    if not k:
        return False
    banned = {b for items in off.values() for b in items}
    for seg in _segs(k):
        if seg in banned:
            return True
    return False

_WARNED = set()

def _warn_empty(seq):
    sig = key_of(seq[0]) if seq else ""
    if sig in _WARNED:
        return
    _WARNED.add(sig)
    print(f"[池子开关] ⚠️ 有个池子被禁空了（{len(seq)} 条全禁用）→ 本次退回原样。"
          f"例：{sig[:50]}", flush=True)

class FilteredRng:

    def __init__(self, rng, off=None):
        self._rng = rng
        self._off = off if off is not None else {}

    def _keep(self, seq):
        seq = list(seq)
        if not self._off:
            return seq
        kept = [x for x in seq if not is_off(self._off, x)]
        if not kept:
            _warn_empty(seq)
            return seq
        return kept

    def choice(self, seq):
        return self._rng.choice(self._keep(seq))

    def choices(self, seq, weights=None, k=1):
        seq = list(seq)
        if not self._off:
            return self._rng.choices(seq, weights=weights, k=k)
        if weights is None:
            return self._rng.choices(self._keep(seq), k=k)
        pairs = [(x, w) for x, w in zip(seq, weights) if not is_off(self._off, x)]
        if not pairs:
            pairs = list(zip(seq, weights))
        return self._rng.choices([x for x, _ in pairs],
                                 weights=[w for _, w in pairs], k=k)

    def sample(self, seq, k):
        return self._rng.sample(self._keep(seq), k)

    def shuffle(self, seq):
        return self._rng.shuffle(seq)

    def __getattr__(self, name):
        return getattr(self._rng, name)

if __name__ == "__main__":
    off = load()
    n = sum(len(v) for v in off.values())
    print(f"禁用表 {OFF_FILE}")
    print(f"  {len(off)} 个池子 / 共 {n} 条被禁用")
    for k, v in list(off.items())[:10]:
        print(f"   {k}: {len(v)} 条")
