# Windows / ComfyUI 接口对照表

> 抽卡机的**组词部分一行都不用改**。要动的只有「出图那一步」。
> 2026-11-11 在 Win11 + i5-13500 + RTX 4060 8GB + ComfyUI 0.44.0 上复测：四档都能出图。

## 〇、Windows 上现在是什么样

| 事 | 状态 |
|---|---|
| 出图引擎 | **自动选**：macOS 找得到 `draw-things-cli` 就走 Draw Things，否则走 ComfyUI。Windows 不用设 `ROLL_ENGINE` |
| 相册面板「启动 / 停止」 | 能用。Windows 上没有 launchd，改成**子进程 + 标记文件**（`_抽卡机.pid` / `_停止标记` / `_暂停标记`） |
| 进程守护 | 启动会写 `_抽卡机.pid`，同一时间只允许跑一个（面板外手动 `python -m pools.roll_machine` 也一样） |
| 停止的语义 | 写停止标记 → 让它把手头这张画完再退（不打断当前图），25 秒不退出才强停 |
| 「让路」（重抽时暂停产线） | Windows 用暂停标记实现，效果相同：当前这张画完就停手，队列跑完自动解冻 |
| 调度优先级开关 | 只在 macOS 生效（改的是 launchd plist）。Windows 下面板会显示「不支持」，不影响出图 |
| 放大（ESRGAN / img2img） | **已下线**：ComfyUI 侧没有放大器模型，Draw Things 的 `realesrgan_x2plus_f16.ckpt` 用不了 |
| 故事机 / 去约会 | **已下线**：`pools/story_roll.py` 早就归档了，相关入口一并移除 |

> Windows 上这套分支没有实机验证过，跑不通就把报错贴出来，作者没见过 Windows 机器。

## 一、两条链路怎么换

Mac（Draw Things）：

```
roll_machine.one_shot()
  → roll_io.generate(tag, prompt, cfg_json, seed, outdir, size, steps)
      → draw-things-cli generate --prompt ... --output xxx.png
      → 直接落盘，一步到位
```

Windows（ComfyUI）：

```
roll_machine.one_shot()                    ← 完全不动
  → roll_io.generate(...)                  ← 按平台自动分支（engine == "comfyui"）
      → backend_comfy.generate(...)        ← 同签名，同返回值
          → POST /prompt（JSON 节点图）
          → 轮询 /history/<完整UUID>
          → GET /view 下载到 outdir
```

`backend_comfy.generate()` 的返回值与 `roll_io.generate()` **完全一致**：
`(ok, 耗时秒, 输出路径, 错误信息, timing)`

相册里的「重抽 / 批量重抽 / 自定义抽卡」也走同一个入口（`_gen_to()`），所以 Windows 上这些按钮都能用。

## 二、参数对照

| 项目 | Mac（Draw Things） | Windows（ComfyUI） |
|---|---|---|
| 调用方式 | 命令行 `draw-things-cli generate` | HTTP `POST /prompt` + 轮询 + 下载 |
| 模型形态 | **单体** `.ckpt`（i8x 量化） | **三件套**：UNET + CLIP + VAE |
| 模型名 | `anima_turbo_v1.1_i8x.ckpt` | `anima-turbo-v1.1.safetensors`<br>`qwen_3_06b_base.safetensors`<br>`qwen_image_vae.safetensors` |
| 模型实际位置 | `~/dt-models/` | `models/diffusion_models/`、`models/text_encoders/`、`models/vae/` |
| 采样器 | `TCD Trailing` | `er_sde` |
| scheduler | —（DT 没有这个概念） | `simple` |
| shift | `6.0` | **没有这个参数** |
| stochastic_sampling_gamma | `0.66` | **没有这个参数** |
| cfg | `1.0` | `1.0`（一样） |
| 步数 | 12（壁纸档 16） | 12（实测 10~12 都行） |
| 质量词 | `masterpiece, best quality` | 同左；另可在开头加 `score_7`、负向加 `score_1/2/3` |
| 出图 | 直接写 `outdir/xxx.png` | SaveImage 落 ComfyUI 的 `output/`，再 `/view` 下载 |

## 三、坑（都踩过）

- 🔴 **模型名不能带子目录前缀。** 文件在 `models/diffusion_models/anima-turbo-v1.1.safetensors`，
  但 `UNETLoader` 的 `unet_name` 只能写 `anima-turbo-v1.1.safetensors`。
  写 `diffusion_models/xxx` 会 probe 失败、提交报错。
  ⇒ 作者要的「相对路径」在 ComfyUI 世界里 = **相对该类目录的纯文件名**。
- 🔴 **`/history/<id>` 的 id 必须是完整 UUID。** 用截断的 `051e2ea3-5d4` 永远查不到，
  会误判成「任务卡住」（踩过，白等 2 分钟）。
- 🔴 **ComfyUI 默认只绑 127.0.0.1。** 跨机要 `ssh -N -L 8188:127.0.0.1:8188 user@host` 开隧道，
  或者启动时加 `--listen 0.0.0.0`（不建议）。
- 🔴 **Windows 上跑远端 Python 脚本，别用 `python -c` 拼命令**，引号会被 shell 吃成乱码。
  写 `.py` 文件再执行，最省心。
- 🔴 **ComfyUI 自带 venv 才有 PIL 和 CUDA 版 torch**：
  用 `<ComfyUI目录>\venv\Scripts\python.exe`，别用系统那个（系统 Python 没 CUDA 版的 torch）。

## 四、速度实测（1024×1536）

| 步骤 | Mac M4 | RTX 4060 |
|---|---|---|
| 出图（12 步） | 62 s | **20~25 s** |
| 出图（10 步） | ~55 s | **17 s** |
| 出图（512×768，6 步） | ~17 s | **5 s**（模型已热时 3 s 上下） |

## 五、怎么配

```bash
# 一般什么都不用设：引擎按平台自动选
# 想强制指定：
ROLL_ENGINE=comfyui          # 或 drawthings

COMFY_URL=http://127.0.0.1:8188      # 隧道或本机
COMFY_UNET=anima-turbo-v1.1.safetensors
COMFY_CLIP=qwen_3_06b_base.safetensors
COMFY_VAE=qwen_image_vae.safetensors
COMFY_SAMPLER=er_sde
COMFY_SCHEDULER=simple
```

探活：`python -m pools.backend_comfy` → 打印版本/显卡/模型是否齐全。
`python -m pools.roll_io` → 按当前引擎做一次自检。
