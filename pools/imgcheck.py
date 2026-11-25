"""出图结果的「像不像一张真图」判定。

体积不是画质的代理：896×1984 的干净图完全可能不到 200KB。
所以先认魔数，再看一个下限体积，别再用一个大阈值卡小图。
"""

import os

MIN_BYTES = 20_000

_MAGIC = (
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpg"),
)


def sniff(data):
    """返回 'png' / 'jpg' / 'webp' / ''。"""
    if not data:
        return ""
    for magic, name in _MAGIC:
        if data.startswith(magic):
            return name
    if len(data) > 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return ""


def is_image_bytes(data, min_bytes=MIN_BYTES):
    return bool(sniff(data)) and len(data) >= min_bytes


def is_image_file(path, min_bytes=MIN_BYTES):
    try:
        if not path or not os.path.exists(path):
            return False
        with open(path, "rb") as f:
            head = f.read(32)
        if not sniff(head):
            return False
        return os.path.getsize(path) >= min_bytes
    except Exception:
        return False
