---
name: setup-anima-gacha-macos
description: 在 macOS 上从零搭起 anima 抽卡机（Draw Things 后端）。装软件、放模型、验证出图、开相册。
---

# macOS 搭建 anima 抽卡机

目标是让 `python3 新自检.py` 全绿、`one_shot()` 能真出一张图。

## 前置检查

```bash
sw_vers                      # 需要 macOS 13+
sysctl -n hw.memsize         # 建议 >= 16G
python3 --version            # 需要 3.10+
```

## 1. 装 Draw Things

两种来源，任选：

- App Store 搜「Draw Things」
- 官网 <https://drawthings.ai>

**装完必须打开一次**，让它初始化模型目录。DT 的默认位置是 App 容器里的
`~/Library/Containers/com.liuliu.draw-things/Data/Documents/Models`；
想用别的目录（比如放外置盘），跑之前 export 一下：`export DRAWTHINGS_MODELS_DIR=~/dt-models`。
然后在 App 的「设置 → 高级」里确认 **Allow CLI/API access** 是开的——
否则命令行调不动它，只会返回 `command not found` 或者超时。

验证：

```bash
which draw-things-cli    # 正常应在 /opt/homebrew/bin/ 下；找不到回 App 设置里开 Allow CLI/API access
```

## 2. 放模型

模型不是仓库自带的，自己下。

- HuggingFace：<https://huggingface.co/circlestone-labs/Anima>
- 国内可用 `hf-mirror.com` 替换域名

需要的是 **Draw Things 用的 i8x 量化版**：`anima_turbo_v1.1_i8x.ckpt`
（ComfyUI 用的 safetensors 在这条路上不能用，格式不一样）

⚠️ 这个文件是**索引 + 权重分离**的：`.ckpt` 本体只有 236KB，真正的 2.0GB 权重在同目录的
`.ckpt-tensordata` 里。**只拷 `.ckpt` 会得到一个空模型**，跑起来会报错或出黑图。

最稳的做法是让 CLI 自己下（会把依赖的 CLIP / VAE 一起带上）：

```bash
mkdir -p ~/dt-models
export DRAWTHINGS_MODELS_DIR="$HOME/dt-models"     # 想永久生效就写进 ~/.zshrc

draw-things-cli models ensure --models-dir "$HOME/dt-models" --model anima_turbo_v1.1_i8x.ckpt
```

如果是别人给你的模型文件，两个一起拷：

```bash
cp anima_turbo_v1.1_i8x.ckpt anima_turbo_v1.1_i8x.ckpt-tensordata "$DRAWTHINGS_MODELS_DIR/"
```

装完确认一下大小（应该是 GB 级，不是几百 KB）：

```bash
ls -lh ~/dt-models/anima_turbo_v1.1_i8x*
```

⚠️ `draw-things-cli` 是**独立的 brew formula**，不是 App 自带的。
装法：App Store 搜 Draw Things（免费），装完在 App 设置里打开 **Allow CLI/API access**，
命令行工具就在 `/opt/homebrew/bin/draw-things-cli`（没有的话在 App 的 Preferences 里点一次安装）。
不要去找 `Draw Things.app/Contents/MacOS/`，那里没有它。

> ⚠️ License 是 CircleStone Labs Non-Commercial License，非商业用途。

## 3. 拉代码并自检

```bash
git clone <repo> 抽卡机 && cd 抽卡机
python3 新自检.py
```

期望输出最后一行是 `结论：✅ 全部通过`。
如果报 `GALLERY_ROOT 不存在`，是项目没有被放在「图库根/项目」这种两级结构里——
按 `paths.py` 文件头的说明设 `ROLL_GALLERY`，或者把项目放进一个父目录。

## 4. 干跑（零成本验证组词）

```bash
python3 -c "
import sys, random; sys.path.insert(0,'.')
from pools import roll_machine as RM
ok,_,rec = RM.one_shot(random.Random(1), tier='fashion', size=(1024,1536), steps=12, draw=False)
print(rec['prompt'])"
```

能打印出一整串提示词就说明组词链路通了。这一步**不花显卡时间**，排查问题先用它。

## 5. 真出图

先用小图快速验证通路：

```bash
python3 -c "
import sys, random, os; sys.path.insert(0,'.')
from pools import roll_machine as RM
ok,path,rec = RM.one_shot(random.Random(2), tier='fashion', size=(512,768), steps=6)
print(ok, path, os.path.getsize(path)//1024, 'KB')"
```

512×768 / 6 步在 M4 上约 17 秒。成功了再上 1024×1536 / 12 步（约 62 秒）。

**成功判据不要看退出码**，看文件是否存在且 > 200KB。CLI 偶尔退出码正常但没出图。

## 6. 开相册

```bash
python3 photo_server.py     # 默认 8900
```

浏览器打开 <http://127.0.0.1:8900>。
相册扫的是 `GALLERY_ROOT` 下的日期目录，和抽卡机写的是同一处。

## 7. 想让它自己跑（可选）

```bash
# 连续出图，撞每日上限自动停
python3 -m pools.roll_machine
```

只有单实例锁 `_抽卡机.pid`，第二个进程会直接退出——这是故意的，
两个进程同时跑会让统计和权重全部失真（我们踩过：某画师占比莫名翻倍）。

要开机自启就写 launchd plist，label 从 `paths.py` 的 `AUTO_ROLL_LABEL` 取
（默认 `com.autogacha.auto-roll`，可用 `ROLL_LABEL` 环境变量覆盖）。

## 常见故障

| 现象 | 原因 | 处理 |
|---|---|---|
| `draw-things-cli: command not found` | 没开 CLI 访问 | App 设置里打开，或设 `DRAWTHINGS_CLI` 指到二进制 |
| 出图超时但进程正常退出 | GUI 没启动 | 先手动打开 Draw Things |
| 报 `No space left on device` | 磁盘满 | `df -h` 看，出图很吃盘 |
| 组词正常但图是空白的 | 模型没找对 | 确认 `DRAWTHINGS_MODELS_DIR` 和文件名 |
