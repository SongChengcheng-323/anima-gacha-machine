# Draw Things 参数表 & Anima 模型规格（2026-10-04 深挖）

> 起因：作者问「GUI 里那个"跳过 clip"有什么说法」→ 顺藤摸出「CLI 里到底还有多少能设的」。
> 结论先放这：**命令行只暴露 ~20 个 flag，但 `--config-json` 能传 83 个参数**（JSGenerationConfiguration 全文）。

## 一、Anima 的模型规格（`dt-models/custom.json` 里明明白白写着）

```json
{
  "name": "Anima Turbo 1.1",
  "text_encoder": "qwen_3_0.6b_q8p.ckpt",       // ← 文本编码器（独立文件）
  "autoencoder": "qwen_image_vae_f16.ckpt",      // ← VAE 也是 Qwen-Image 的
  "clip_encoder": "anima_turbo_v1.1_f16.ckpt",
  "version": "cosmos2.5_2b",                     // ← 跟源码 case .cosmos2_5_2b 对上
  "padded_text_encoding_length": 512,            // ★ 提示词容量 = 512 token（不是 77！）
  "default_scale": 16, "hires_fix_scale": 24,
  "noise_discretization": { "rf": { "_0": {"condition_scale": 1, "sigma_max": 1, "sigma_min": 0} } },
  "upcast_attention": false,
  "objective": { "u": { "condition_scale": 1 } }
}
```

**由此定案的三件事**
1. **编码器是 Qwen3-0.6B，不是 CLIP** → `clipSkip` 之类 CLIP 时代参数对它无意义（源码 `encodeAnima` 里 0 处引用）。
2. `version = cosmos2.5_2b`，源码里**只有这一个分支** → **base / turbo 走同一条编码路**，没有"turbo 专属设置"。
3. **容量 512 token**（SD1.5/SDXL 是 77）≈ 英文 350~400 词 / 中文 400~500 字。
   我们那些长 tag 串根本没到上限 —— 这解释了为什么从来没被截断过。

## 二、83 个参数全表（分组）

命令行 flag 只覆盖粗体那些；**其余全部只能靠 `--config-json` / `--config-file` 传**。

| 组 | 参数 |
|---|---|
| **基础/输出** | **model** / **width** / **height** / **steps** / **seed** / seedMode / batchSize / batchCount / targetImageWidth / targetImageHeight / originalImageWidth / originalImageHeight / cropLeft / cropTop |
| **采样** | **sampler** / **shift** / **cfg(=guidanceScale)** / **strength** / resolutionDependentShift / stochasticSamplingGamma / stage2Steps / stage2Shift / stage2Guidance / startFrameGuidance |
| **CFG/引导** | guidanceScale / imageGuidanceScale / guidanceEmbed / speedUpWithGuidanceEmbed / **cfgZeroStar** / cfgZeroInitSteps / **zeroNegativePrompt** |
| **文本编码器** | clipSkip / clipWeight / clipLText / openClipGText / t5Text / t5TextEncoder / separateClipL / separateOpenClipG / separateT5 / **causalInference** / causalInferencePad / **expandPromptToJson** |
| **画质/色彩** | aestheticScore / negativeAestheticScore / sharpness / colorCalibration / compressionArtifacts / compressionArtifactsQuality |
| **放大/修复** | **hiresFix** / hiresFixWidth / hiresFixHeight / hiresFixStrength / upscaler / upscalerScaleFactor / faceRestoration |
| **精修两阶段** | refinerModel / refinerStart / imagePriorSteps / negativePromptForImagePrior |
| **重绘/遮罩** | maskBlur / maskBlurOutset / preserveOriginalAfterInpaint |
| **瓦片（大图/省显存）** | tiledDecoding / decodingTileWidth / decodingTileHeight / decodingTileOverlap / tiledDiffusion / diffusionTileWidth / diffusionTileHeight / diffusionTileOverlap |
| **缓存加速** | teaCache / teaCacheStart / teaCacheEnd / teaCacheThreshold / teaCacheMaxSkipSteps |
| **视频** | fps / numFrames / motionScale / guidingFrameNoise |
| **其他** | **loras** / controls（ControlNet 栈） |

命令行 flag 里**没在 `--help` 出现但实际存在**的：
`--clip-skip` / `--noise-offset` / `--scale` / `--warmup-steps` / `--weights-memory`（这几个是 **`train lora`** 的）；
`--json`（`auth login/logout`）；`--dry-run`（`train lora` 与 `models import`，**打印解析后的配置不落盘**）；
`--prompt-file` / `--negative-prompt-file`（长/多行提示词走文件，比命令行参数干净）。

## 三、还没挖的宝（按价值排序）

1. ~~**`teaCache`**~~ ❌ **已查证：对 Anima 是死的（2026-10-04 深夜）**
   - 机制：相邻去噪步输出相似 → 缓存上一步残差，用"时间步嵌入调制的噪声输入"差值做门控，
     超阈值才真算。**免训练**，属"可调画质取舍"，阈值越高越快越糊。
   - **为什么 Anima 用不了**：`ModelZoo.swift:3444 teaCacheCoefficientsForModel()` 里，
     `cosmos2_5_2b`（= Anima 的 version）落在** `return nil` 那一串**；只有
     `flux1 / hunyuanVideo / hiDreamI1` 有硬编码多项式系数（minimaxH3 用 (0,0,0,1,0)）。
     我们 `custom.json` 也没写 `tea_cache_coefficients` → 系数 nil → 缓存被短路成空。
   - 唯一开锁方式：**自己给它拟合一组系数**写进 `custom.json`
     （`tea_cache_coefficients`，4 次多项式 5 个 float）。但——
   - **就算补上，8 步也太短**：默认 `teaCacheStart=5` 意味着只有第 5/6/7 步可缓存；
     且社区实测在**蒸馏短 schedule**（4~8 步）上门控"从不触发"（蒸馏轨迹相邻步变化太大），
     反而多 1~2% 开销。Cosmos 系论文数据也就 1.4x(阈值0.3)~2.0x(阈值0.4)，且要 20+ 步才有空间。
   - **结论：不值得在 Anima 上折腾 TeaCache。** 要提速看别的（更小分辨率 / 量化 / 换更少步数）。
   - 附：各档默认值 `teaCache=false` / `Start=5` / `End=-1`(=-1 指最后一步) / `Threshold=0.06(保守)~0.2(均衡)` / `MaxSkipSteps=3`
   - 另：`resolutionDependentShift` **默认就是 true**（按分辨率自动算 shift；手动设 shift 会自动关掉它）
     —— 我们现在手动给 3.5/4.5，等于把它关了。**"手动 shift vs 让它自动"值得对比一次。**
2. **`hiresFix` 家族** ⭐⭐ DT 原生两段式放大（比我们"一键放大=重跑大图"便宜得多）。
3. **`faceRestoration`** ⭐ 崩脸修复（作者最讨厌崩坏图）。需确认要不要额外模型文件。
4. **`refinerModel` / `refinerStart`** 两段精修 —— 低步数下补救细节。
5. **`controls`** ControlNet 栈 —— 姿势/构图硬控（对"剧情模式"的镜头稳定性有用）。
6. **`expandPromptToJson`** 提示词扩展（LLM 改写）—— **中文测试时要注意这个是不是开着**。
7. `separateT5` / `clipLText` / `t5Text` / `openClipGText` —— 多编码器模型可以**给不同编码器喂不同文本**（Anima 是单编码器，多半用不上）。
8. `aestheticScore` / `colorCalibration` —— Anima 是否吃评分条件待确认。

## 四、待办 & 备忘
- `--clip-skip` 是 **train lora** 的参数（训练时用），**推理时对 Anima 无效** → 已从抽卡机全线移除（v89.49）。
- `--cfg 1.0` + 空 negative → 负面提示词数学上不生效；`zeroNegativePrompt` 是 DT 处理这事的开关，留待研究。
- 长提示词一律建议走 `--prompt-file`（避免命令行长度/转义问题）。
