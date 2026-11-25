---
name: setup-anima-gacha-windows
description: 在 Windows 上从零搭起 anima 抽卡机（ComfyUI 后端）。装 ComfyUI、放三件套模型、验证出图。
---

# Windows 搭建 anima 抽卡机

Windows 这条路走 ComfyUI 的 HTTP API。**抽卡机的组词部分和 macOS 完全一样**，
只有「出图那一步」换成了 `pools/backend_comfy.py`。

## 前置检查

```powershell
# 显卡（ComfyUI 要 CUDA，N 卡最省事）
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
# 显存 8G 够跑 1024×1536；6G 建议降到 768×1152
python --version    # 3.11+
```

## 1. 装 ComfyUI

推荐用官方便携版或 git 克隆：

```powershell
git clone https://github.com/comfyanonymous/ComfyUI D:\AI\ComfyUI   # 目录随你
cd D:\AI\ComfyUI
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

启动：

```powershell
python main.py --listen 127.0.0.1 --port 8188
```

浏览器能打开 <http://127.0.0.1:8188> 就说明好了。
**默认只绑 127.0.0.1**，别随手改成 `0.0.0.0`（除非你清楚自己在干什么）。

## 2. 放三件套模型

Windows 上 Anima 不是单体 checkpoint，拆成三件，分别放到对应目录：

```
ComfyUI/models/diffusion_models/anima-turbo-v1.1.safetensors
ComfyUI/models/text_encoders/qwen_3_06b_base.safetensors
ComfyUI/models/vae/qwen_image_vae.safetensors
```

模型来源：

- HuggingFace：<https://huggingface.co/circlestone-labs/Anima>
- CivitAI：<https://civitai.com/models/2458426/anima>
- 国内把域名换成 `hf-mirror.com`

> ⚠️ 非商业许可（CircleStone Labs Non-Commercial License）。
> ⚠️ **最高频的坑**：在 ComfyUI 里填模型名时只写文件名，**不带子目录**。
> 写 `diffusion_models/anima-turbo-v1.1.safetensors` 会报 `invalid unet_name`，
> 正确写法是 `anima-turbo-v1.1.safetensors`。

## 3. 探活

```powershell
cd 抽卡机
python -m pools.backend_comfy
```

期望输出里能看到版本号、显卡名、`unet_ok: true`。`unet_ok: false` 就是上面那条坑。

## 4. 出一张验证

别用 `python -c` 拼长命令（Windows shell 会吃掉引号），直接用模块自带的单发入口：

```powershell
cd 抽卡机
python -m pools.roll_machine --once 1 --size 512x768 --steps 6
```

图会落在 `output\<日期>\` 里。RTX 4060 上 512×768 / 6 步约 5 秒（模型热了以后 3 秒上下）。

## 5. 参数对照（和 Draw Things 的差异）

| | Draw Things | ComfyUI |
|---|---|---|
| 模型 | 单体 `.ckpt`（i8x） | UNET + CLIP + VAE 三件套 |
| 采样器 | `TCD Trailing` | `er_sde` |
| scheduler | — | `simple` |
| shift / gamma | 6.0 / 0.66 | **没有这两个参数** |
| cfg | 1.0 | 1.0 |
| 质量词 | `masterpiece, best quality` | 同左，可加 `score_7` / 负向 `score_1..3` |

完整对照和踩坑记录见仓库根的 `Win接口对照表.md`。

## 6. 开相册、出一批

```powershell
python photo_server.py        # 相册 + 面板，默认 http://127.0.0.1:8900
```

浏览器打开后点「⚙️ → 抽卡机」：设张数 / 比例 / 尺度权重，点**启动**就开始跑，
点**停止**会等当前这张画完再退。Windows 上没有 launchd，面板是用子进程 + 标记文件实现的
（`_抽卡机.pid` / `_停止标记`），同时只允许跑一个实例。

也可以不开面板直接跑：

```powershell
python -m pools.roll_machine
```

默认只出「时尚」档。想开其他三档改 `pools/roll_params.py` 的 `DEFAULT_CONFIG["tier_weights"]`，
或者在面板的抽卡机设置里直接调权重。

## 常见故障

| 现象 | 原因 | 处理 |
|---|---|---|
| `invalid unet_name` | 模型名带了目录前缀 | 只写文件名 |
| `Connection refused` | ComfyUI 没起 / 端口不对 | 先浏览器打开 8188 确认 |
| 提交成功但一直等待 | `/history` 查的 id 不完整 | 必须用完整 UUID，截断的永远查不到 |
| 出图慢得离谱 | 用 CPU 跑了 | `system_stats` 里看 device 是不是 `cuda:0` |
| `ModuleNotFoundError: PIL` | 用错了 python | 转图要用 ComfyUI 自己的 `venv\Scripts\python.exe`，不是系统的 |
| `python -c` 报语法错、中文乱码 | Windows shell 吃引号 | 把脚本写成 `.py` 文件再执行，别用 `-c` 拼长命令 |
| 面板点「启动」显示已停止 | 抽卡机进程起来就退了 | 看仓库根的 `_产线.out.log`；多半是 ComfyUI 没起或模型名不对 |
| 出了图但相册里 0 张 | 图落盘的目录和相册扫的目录不是同一个 | 正常情况都该是 `<项目>\output`；设了 `ROLL_GALLERY` 才可能不一致 |
| 面板里「让路 / 优先级」没反应 | 那个开关改的是 launchd plist | Windows 下本来就不生效，不影响出图 |
| 找不到「放大」和「故事机」 | 这两个功能已下线 | 见 `Win接口对照表.md` 第〇节 |
