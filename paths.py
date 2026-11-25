import os
import sys

IS_WIN = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

WORK = os.environ.get("ROLL_WORK") or PROJECT_ROOT
GALLERY_ROOT = os.environ.get("ROLL_GALLERY") or os.path.join(PROJECT_ROOT, "output")

# 出图落盘 = 相册扫描的同一个根（否则相册看不到刚画的图）
OUT_ROOT = GALLERY_ROOT

CONFIG_PATH = os.path.join(WORK, "roll_config.json")
LOG_PATH = os.path.join(WORK, "_日志.jsonl")
CAP_FILE = os.path.join(WORK, "_每日上限.json")
DISABLE_FILE = os.path.join(WORK, "_禁用.json")

# 抽卡机进程的跨平台控制文件（Windows 没有 launchd，用这几个标记文件代替信号）
PID_FILE = os.path.join(WORK, "_抽卡机.pid")
STOP_FILE = os.path.join(WORK, "_停止标记")
PAUSE_FILE = os.path.join(WORK, "_暂停标记")

CHAR_FILE = os.path.join(GALLERY_ROOT, ".photo_char.json")
TIER_FILE = os.path.join(GALLERY_ROOT, ".photo_tier.json")
TAG_FILE = os.path.join(GALLERY_ROOT, ".photo_tags.json")
FAV_FILE = os.path.join(GALLERY_ROOT, ".photo_favs.json")
THUMB_DIR = os.path.join(GALLERY_ROOT, ".photo_thumbs")

# ── Draw Things（只有 macOS 这条路用得上；Windows 走 ComfyUI）──
_DT_MODELS_DEFAULT = (os.path.expanduser(
    "~/Library/Containers/com.liuliu.draw-things/Data/Documents/Models")
    if IS_MAC else "")
_DT_CLI_DEFAULT = "/opt/homebrew/bin/draw-things-cli" if IS_MAC else ""
DT_MODELS_DIR = (os.environ.get("DRAWTHINGS_MODELS_DIR")
                 or os.environ.get("DT_MODELS_DIR")
                 or _DT_MODELS_DEFAULT)
DT_CLI = os.environ.get("DRAWTHINGS_CLI") or _DT_CLI_DEFAULT

# ── launchd（只有 macOS 有；Windows 上留空串，面板会退回「直接起子进程」）──
LAUNCH_AGENTS = os.path.expanduser("~/Library/LaunchAgents") if IS_MAC else ""
AUTO_ROLL_LABEL = os.environ.get("ROLL_LABEL", "com.autogacha.auto-roll")
PHOTO_ALBUM_LABEL = os.environ.get("ALBUM_LABEL", "com.autogacha.photo-album")
AUTO_ROLL_PLIST = (os.path.join(LAUNCH_AGENTS, AUTO_ROLL_LABEL + ".plist")
                   if LAUNCH_AGENTS else "")
PHOTO_ALBUM_PLIST = (os.path.join(LAUNCH_AGENTS, PHOTO_ALBUM_LABEL + ".plist")
                     if LAUNCH_AGENTS else "")

def setup_console():
    "Windows 控制台默认是 GBK/437，中文会变成乱码 ⇒ 统一切成 UTF-8。"
    if not IS_WIN:
        return
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except Exception:
        pass

def engine():
    "出图引擎：comfyui / drawthings。环境变量优先，没设就按平台猜。"
    e = (os.environ.get("ROLL_ENGINE") or "").strip().lower()
    if e in ("comfyui", "comfy"):
        return "comfyui"
    if e in ("drawthings", "draw-things", "dt", "gui", "cli"):
        return "drawthings"
    if IS_MAC and DT_CLI and os.path.exists(DT_CLI):
        return "drawthings"
    return "comfyui"

def selfcheck(verbose=True):
    bad = []
    if not os.path.isdir(PROJECT_ROOT):
        bad.append("PROJECT_ROOT 不存在: %s" % PROJECT_ROOT)
    if not os.path.isdir(GALLERY_ROOT):
        bad.append("GALLERY_ROOT 不存在: %s（环境变量 ROLL_GALLERY 可改）" % GALLERY_ROOT)
    for k in ("CONFIG_PATH", "LOG_PATH"):
        p = globals()[k]
        if not os.path.isdir(os.path.dirname(p)):
            bad.append("%s 的目录不存在: %s" % (k, os.path.dirname(p)))
    if verbose:
        print("路径来源自检：")
        print("  平台         = %s" % ("Windows" if IS_WIN else "macOS" if IS_MAC else sys.platform))
        print("  出图引擎     = %s（环境变量 ROLL_ENGINE 可改）" % engine())
        print("  PROJECT_ROOT = %s" % PROJECT_ROOT)
        print("  WORK         = %s%s" % (WORK, "（环境变量 ROLL_WORK）" if os.environ.get("ROLL_WORK") else ""))
        print("  GALLERY_ROOT = %s%s" % (GALLERY_ROOT, "（环境变量 ROLL_GALLERY）" if os.environ.get("ROLL_GALLERY") else ""))
        print("  OUT_ROOT     = %s" % OUT_ROOT)
        if IS_MAC:
            print("  DT_MODELS_DIR= %s" % DT_MODELS_DIR)
            print("  DT_CLI       = %s" % DT_CLI)
        if bad:
            print("  ✗ 有 %d 处问题：" % len(bad))
            for b in bad:
                print("     ·", b)
        else:
            print("  ✓ 全部正常")
    return 0 if not bad else 1

if __name__ == "__main__":
    import sys as _sys
    setup_console()
    try:
        _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    raise SystemExit(selfcheck())
