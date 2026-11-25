import sys
import io
import json
import os
import random
import time
from datetime import datetime

from . import roll_params as P
from . import roll_io as IO
from . import orchestrator as OR

try:
    import paths as _PATHS
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import paths as _PATHS

try:
    _PATHS.setup_console()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _slug(x, n=18):
    t = str(x or "").strip().replace("/", "_").replace(" ", "_")
    return (t[:n] or "x")


def _pids_alive(pid):
    "跨平台看一个 pid 还活着没。"
    try:
        pid = int(pid or 0)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    if _PATHS.IS_WIN:
        try:
            import subprocess
            out = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/NH"],
                                 capture_output=True, text=True, timeout=8,
                                 encoding="utf-8", errors="replace").stdout
            return str(pid) in (out or "")
        except Exception:
            return False
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def _read_pid_file():
    try:
        with open(_PATHS.PID_FILE, encoding="utf-8") as f:
            return int((f.read() or "").strip() or 0)
    except Exception:
        return 0


def _clear_pid_file():
    try:
        if _read_pid_file() == os.getpid():
            os.remove(_PATHS.PID_FILE)
    except Exception:
        pass


def _acquire_lock():
    "单实例锁：已经有一个在跑就返回它的 pid。"
    for _ in range(2):
        try:
            fd = os.open(_PATHS.PID_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            old = _read_pid_file()
            if old and old != os.getpid() and _pids_alive(old):
                return old
            # 僵死的旧 pid 文件：清掉再来一次
            try:
                os.remove(_PATHS.PID_FILE)
            except Exception:
                return 0
            continue
        except Exception:
            return 0
        try:
            os.write(fd, str(os.getpid()).encode())
        finally:
            os.close(fd)
        return 0
    return 0


def _stop_requested():
    return os.path.exists(_PATHS.STOP_FILE)


def _wait_if_paused(quiet=False):
    "让路：相册面板冻结时在这里等着，不抢 GPU。"
    if not os.path.exists(_PATHS.PAUSE_FILE):
        return
    if not quiet:
        print("  [让路] 面板把 GPU 让出去了 ⇒ 暂停出图，解冻后自动继续", flush=True)
    while os.path.exists(_PATHS.PAUSE_FILE) and not _stop_requested():
        time.sleep(1.0)


def _clear_ctl_files():
    for p in (_PATHS.STOP_FILE, _PATHS.PAUSE_FILE):
        try:
            os.remove(p)
        except OSError:
            pass


def _job_log(job, prompt, ctx, ok, sec, path, err, timing):
    meta = (ctx or {}).get("meta") or {}
    tag = os.path.basename(path or "").rsplit(".", 1)[0] if path else ""
    return {
        "tag": tag,
        "character": (ctx or {}).get("char") or job.get("character") or "unknown",
        "tier": job.get("tier"),
        "ctx_tier": ctx.get("tier"),
        "sex_meta": bool((ctx.get("meta") or {}).get("sex")),
        "action": meta.get("action") or "",
        "style": meta.get("style") or "",
        "seed": job.get("seed"),
        "steps": job.get("steps"),
        "size": "%dx%d" % (job.get("w"), job.get("h")),
        "prompt": prompt,
        "outfit": meta.get("outfit_full") or meta.get("outfit_text") or "",
        "equip": meta.get("equip") or {},
        "equip_labeled": meta.get("equip_labeled") or "",
        "scene": meta.get("scene") or "",
        "place": meta.get("place") or "",
        "camera_vis": meta.get("camera_vis") or "",
        "facing_text": meta.get("facing_text") or "",
        "hairstyle": meta.get("hairstyle") or "",
        "pubic": meta.get("pubic") or "",
        "eros": meta.get("eros") or "",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ok": bool(ok),
        "seconds": sec,
        "error": err or "",
        "cli_timing": timing or {},
        "engine": (timing or {}).get("engine") or "",
        "file": os.path.basename(path or ""),
        "dir": os.path.basename(os.path.dirname(path or "")),
        "lora": _lora_file((ctx or {}).get("char") or job.get("character") or ""),
        "machine": "modular-roll",
        "doctor": meta.get("doctor") or [],
        "doctor_readonly": bool(getattr(OR, "DOCTOR_READONLY", True)),
        "pools_v3": _pool_versions(),
        "body_v3": meta.get("body_v3") or [],
        "scene_cat": meta.get("scene_cat") or "",
        "scene_prop": meta.get("scene_prop") or "",
        "status_str": meta.get("status_str") or {},
    }

def _pool_versions():
    try:
        from pools import roll_params as _P
    except Exception:
        try:
            import roll_params as _P
        except Exception:
            return {}
    keys = ("USE_POSES_FROM_V3", "USE_POSE_ACTIONS_FROM_V3", "USE_SCENE_FROM_V3",
            "USE_FACE_FROM_V3", "USE_WARDROBE_FROM_V3", "USE_STATUS_V3")
    out = {}
    for k in keys:
        on = bool(getattr(_P, k, False))
        out[k.replace("USE_", "").replace("_FROM_V3", "").replace("_V3", "").lower()] = "v3" if on else "v2"
    return out

def _lora_key(character):
    return (character or "").split("_(")[0].split(" (")[0].strip()

def _lora_file(character):
    try:
        from . import characters as CH
    except Exception:
        try:
            import characters as CH
        except Exception:
            return "none"
    try:
        return CH.lora_of(character) or "none"
    except Exception:
        return "none"

def _cfg_json(character, job):
    cfg: dict = {"sampler": P.SAMPLER}
    if getattr(P, "RESOLUTION_DEPENDENT_SHIFT", False):
        cfg["resolutionDependentShift"] = True
    else:
        cfg["shift"] = job.get("shift") or P.SHIFT
        cfg["resolutionDependentShift"] = False
    _g = job.get("gamma", getattr(P, "STOCHASTIC_GAMMA", None))
    if _g is not None:
        cfg["stochasticSamplingGamma"] = float(_g)
    try:
        from . import characters as CH
    except Exception:
        try:
            import characters as CH
        except Exception:
            CH = None
    if CH is not None:
        try:
            f = CH.lora_of(character)
        except Exception:
            f = (getattr(CH, "LORA_MAP", {}) or {}).get(_lora_key(character))
        if f:
            cfg["loras"] = [{"mode": "all", "file": f,
                             "weight": getattr(P, "LORA_WEIGHT", 1.0)}]
        elif _lora_key(character):
            cfg["loras"] = []
    return cfg

def one_shot(rng=None, tier=None, character=None, size=None, steps=None, cfg=None,
             draw=True):
    rng = rng or random.Random()
    job = P.next_job(rng, tier=tier, character=character, cfg=cfg)
    if size:
        job["w"], job["h"] = int(size[0]), int(size[1])
    if steps:
        job["steps"] = int(steps)
    prompt, ctx = OR.run(rng, tier=job["tier"], char=(job.get("character") or None),
                         size=(job.get("w"), job.get("h")))
    if not draw:
        return True, "", _job_log(job, prompt, ctx, True, 0, "", "", {})
    ok, sec, path, err, timing = IO.generate(
        P.make_tag(job["stamp"], (ctx.get("char") or "unknown"), job["tier"],
                   _slug((ctx.get("meta") or {}).get("action")
                         or (ctx.get("meta") or {}).get("play") or "action"),
                   _slug((ctx.get("meta") or {}).get("style") or "style"),
                   job["seed"]),
        prompt, _cfg_json((ctx.get("char") or job.get("character") or ""), job),
        job["seed"], job["outdir"],
        size=(job["w"], job["h"]), steps=job["steps"])
    rec = _job_log(job, prompt, ctx, ok, sec, path, err, timing)
    IO.log_line(rec)
    return ok, path, rec

def _w_sample_no_replace(rng, items, weights, k):
    items = list(items)
    weights = [float(x) for x in weights]
    out = []
    while items and len(out) < k:
        tot = sum(weights)
        if tot <= 0:
            rng.shuffle(items)
            out.extend(items[:k - len(out)])
            break
        r = rng.random() * tot
        acc = 0.0
        for i, w in enumerate(weights):
            acc += w
            if r <= acc:
                out.append(items.pop(i))
                weights.pop(i)
                break
        else:
            out.append(items.pop())
            weights.pop()
    return out

CHAR_DECAY_START = 3
CHAR_DECAY_RATE = 0.35

def plan_batch_chars(n=None, rng=None):
    from . import characters as CH
    rng = rng or random.Random()
    n = int(n or 1)
    pool = [c[0] for c in CH.CHARACTERS]
    try:
        import pool_gate as PG
        _off = PG.cached()
        pool = [c for c in pool if not PG.is_off(_off, c)] or pool
    except Exception:
        pass
    w_of = getattr(CH, "CHARACTER_WEIGHTS", {}) or {}
    cnt = {}
    plan = []
    for _ in range(n):
        ws = []
        for c in pool:
            w = float(w_of.get(c, 1.0))
            k = cnt.get(c, 0)
            if k >= CHAR_DECAY_START:
                w *= CHAR_DECAY_RATE ** (k - CHAR_DECAY_START + 1)
            ws.append(w if w > 1e-6 else 1e-6)
        c = rng.choices(pool, weights=ws, k=1)[0]
        cnt[c] = cnt.get(c, 0) + 1
        plan.append(c)
    return plan

def run_batch(n=None, rng=None, size=None, steps=None, draw=True, quiet=False):
    rng = rng or random.Random()
    n = int(n or 1)
    from . import characters as _CH
    _fav = getattr(_CH, "FAVORITE_WEIGHTS", {}) or {}
    plan = plan_batch_chars(n, rng)
    if not quiet:
        _nfav = sum(1 for c in plan if c in _fav)
        print("  [批] %d 张 · 角色按权重抽（撞 3 次后降权）✓" % n, flush=True)
    out = []
    for i in range(n):
        if _stop_requested():
            if not quiet:
                print("  [停止] 面板点了停止 ⇒ 本批收工", flush=True)
            break
        _wait_if_paused(quiet=quiet)
        if _stop_requested():
            break
        try:
            _ci = P.cap_info()
        except Exception:
            _ci = None
        if _ci and _ci.get("paused"):
            if not quiet:
                if _ci.get("hard_hit"):
                    print("  [cap] 已到**硬上限** %d（今日 %d 张）=> 产线今天收工，重抽不受影响"
                          % (_ci.get("hard"), _ci["n"]), flush=True)
                else:
                    print("  [cap] 已达软上限 %d（今日 %d 张）=> 本批提前收工"
                          % (_ci["cap"], _ci["n"]), flush=True)
            break
        ok, path, rec = one_shot(rng, character=plan[i], size=size, steps=steps, draw=draw)
        out.append((ok, path, rec))
        if not quiet:
            label = (os.path.basename(path or "") if path
                     else (rec.get("prompt") or "").replace("\n", " "))
            print("  [%d/%d] %s %s" % (i + 1, n, "OK" if ok else "FAIL",
                                       label[:72]), flush=True)
    return out

_CAP_LOGGED = [False]

STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "_运行状态.json")
_STOP_REASON = None

def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def _write_state(d):
    try:
        tmp = STATE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
        os.replace(tmp, STATE_FILE)
    except Exception:
        pass

def _read_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}

def _last_exit_note():
    st = _read_state()
    if not st:
        return "无记录（初次运行 / 状态文件被清过）"
    if st.get("clean"):
        return "✅ **%s**（%s）—— **不是出错** ✓" % (st.get("reason") or "正常停止",
                                                    st.get("at") or "?")
    return ("⚠️ **没有干净退出记录** ⇒ 上一次可能是崩溃 / `kill -9` / 断电"
            "（pid %s，起于 %s）—— 这一类才值得查 ✗"
            % (st.get("pid"), st.get("started")))

def _finish(reason, clean):
    st = _read_state()
    _write_state({"pid": os.getpid(), "started": st.get("started") or _now(),
                  "clean": bool(clean), "reason": reason, "at": _now()})

def _install_signal_handlers():
    import signal as _sg

    def _h(sig, _frm):
        global _STOP_REASON
        try:
            name = _sg.Signals(sig).name
            if _STOP_REASON:
                print("[停止] %s ⇒ %s ✓ @ %s" % (name, _STOP_REASON, _now()), flush=True)
            else:
                _finish("手动停（%s）" % name, True)
                print("[停止] 收到 %s ⇒ **手动停**（面板「停止」/ launchctl / kill / "
                      "Ctrl-C 都是它）—— **不是崩溃** ✓ @ %s" % (name, _now()), flush=True)
        except Exception:
            pass
        raise SystemExit(0)

    for _s in ("SIGTERM", "SIGINT", "SIGHUP"):
        try:
            _sg.signal(getattr(_sg, _s), _h)
        except Exception:
            pass

def main():
    _install_signal_handlers()
    global _STOP_REASON
    try:
        from . import layer_tables as _LT
        print("[启动] %s" % _LT.STAMP, flush=True)
    except Exception:
        try:
            import layer_tables as _LT
            print("[启动] %s" % _LT.STAMP, flush=True)
        except Exception:
            pass
    try:
        print("[启动] 上次结束：%s" % _last_exit_note(), flush=True)
    except Exception:
        pass
    _write_state({"pid": os.getpid(), "started": _now(), "clean": False})
    _other = _acquire_lock()
    if _other:
        print("[启动] 已经有抽卡机在跑（pid %d）⇒ 本进程直接退出" % _other, flush=True)
        return 0
    _clear_ctl_files()
    """跑批循环（launchd / 相册面板 的执行体 ✓ 逻辑全在模块里 ✗ 这里只有循环 ✗）"""
    import sys
    rng = random.Random()
    if "--once" in sys.argv:
        i = sys.argv.index("--once")
        nxt = sys.argv[i + 1] if len(sys.argv) > i + 1 else ""
        n = int(nxt) if nxt.isdigit() else 1
        size = steps = None
        if "--size" in sys.argv:
            size = tuple(int(x) for x in sys.argv[sys.argv.index("--size") + 1].split("x"))
        if "--steps" in sys.argv:
            steps = int(sys.argv[sys.argv.index("--steps") + 1])
        draw = "--nodraw" not in sys.argv
        res = run_batch(n, rng, size=size, steps=steps, draw=draw)
        okn = sum(1 for ok, _p, _r in res if ok)
        print("\n本批 %d 张 · 成功 %d · 失败 %d" % (len(res), okn, len(res) - okn))
        # --once 也算一次正常退出：留下 clean 记录，否则下次启动会误报「崩溃」
        _finish("跑完 %d 张（--once）" % len(res), okn == len(res))
        return 0 if okn == len(res) else 1
    while True:
        if _stop_requested():
            _STOP_REASON = "手动停（相册面板）"
            _finish(_STOP_REASON, True)
            print("[停止] 面板点了停止 ⇒ 收工 ✓ @ %s" % _now(), flush=True)
            return 0
        _wait_if_paused()
        _ci = P.cap_info()
        if _ci["paused"]:
            if _ci.get("hard_hit"):
                print("[cap] 今日已生成 %d 张 >= **硬上限** %d => 产线今天彻底收工"
                      "（怎么点启动都没用，明天零点复位；重抽不受影响）"
                      % (_ci["n"], _ci.get("hard")), flush=True)
            else:
                print("[cap] 今日已生成 %d 张 >= 软上限 %d => 自动暂停"
                      "（在面板点「启动」可继续，今天不再自动暂停）"
                      % (_ci["n"], _ci["cap"]), flush=True)
            if _PATHS.IS_MAC:
                try:
                    import subprocess
                    _STOP_REASON = "到顶自动暂停（今日 %d/%d 张）" % (_ci["n"], _ci["cap"])
                    subprocess.run(["launchctl", "bootout",
                                    "gui/%d/%s" % (os.getuid(), _PATHS.AUTO_ROLL_LABEL)],
                                   timeout=60)
                    print("[cap] 已卸载 job（面板会显示 已停止，点「启动」即复工）", flush=True)
                except Exception as _e:
                    print("[cap] bootout 失败（改为进程内待命）:", _e, flush=True)
            else:
                print("[cap] 进程内待命（面板显示 已暂停，点「启动」即复工）", flush=True)
            _STOP_REASON = "到顶自动暂停（今日 %d/%d 张）" % (_ci["n"], _ci["cap"])
            while P.cap_reached() and not _stop_requested():
                _wait_if_paused()
                time.sleep(5)
            continue
        if _CAP_LOGGED[0]:
            print("[cap] 已解除自动暂停（override 或已跨天 ✓）继续出图 ✓", flush=True)
            _CAP_LOGGED[0] = False
        _room = int(_ci.get("cap") or 0) - int(_ci.get("n") or 0)
        _n = _room if _room > 0 else 100
        run_batch(rng=rng, n=_n)

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as _e:
        try:
            _finish("⚠️ 异常退出: %s: %s" % (type(_e).__name__, _e), False)
            print("[停止] ⚠️ 异常退出：%s: %s" % (type(_e).__name__, _e), flush=True)
        except Exception:
            pass
        raise
    finally:
        _clear_pid_file()
        _clear_ctl_files()
