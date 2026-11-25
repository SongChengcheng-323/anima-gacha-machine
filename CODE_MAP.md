# 代码地图

这份地图是**按仓库里的真实文件生成的**，只列存在的模块。

## 顶层

| 文件 | 函数 | 顶层常量 | 干什么 |
|---|---:|---:|---|
| `paths.py` | 3 | 27 | 所有路径的来源，支持环境变量覆盖 |
| `photo_server.py` | 133 | 97 | 相册后端（HTTP 服务） |
| `works.py` | 3 | 2 | 角色 → 作品映射 |
| `wardrobe.py` | 14 | 27 | 服装组装 |
| `tag_compose.py` | 4 | 4 | 英文标签 ↔ 中文 |
| `pool_gate.py` | 7 | 4 | 池子过滤 |
| `新自检.py` | 14 | 8 | 七项只读体检 |
| `新角色接入.py` | 12 | 2 | 加角色的工具 |
| `make_versions.py` | 2 | 3 | 一次出多尺寸 |

## pools/ （66 个模块，含 `imgcheck.py` —— 出图结果判定，认魔数不认体积）

| 文件 | 函数 | 常量 | 首个常量 |
|---|---:|---:|---|
| `pools/actions.py` | 0 | 1 | `ACTIONS` |
| `pools/actions_pool.py` | 3 | 1 | `ACTIONS` |
| `pools/after_draw.py` | 6 | 6 | `AFTER_POSES` |
| `pools/ambience.py` | 2 | 5 | `META` |
| `pools/artists.py` | 3 | 5 | `META` |
| `pools/backend_comfy.py` | 8 | 11 | `COMFY_URL` |
| `pools/body_pool.py` | 6 | 12 | `POSTURES` |
| `pools/cameras.py` | 0 | 3 | `CAMERAS` |
| `pools/char_profile.py` | 14 | 14 | `OVERRIDES` |
| `pools/char_traits.py` | 2 | 5 | `CHAR_TRAITS` |
| `pools/characters.py` | 16 | 39 | `CHARACTERS_SPLIT` |
| `pools/characters_split.py` | 0 | 0 | `` |
| `pools/composition.py` | 0 | 14 | `ANGLES` |
| `pools/equip_machine.py` | 25 | 76 | `SLOT_ORDER` |
| `pools/eros.py` | 2 | 5 | `EROS_FASHION` |
| `pools/expose.py` | 3 | 5 | `POOL` |
| `pools/expose_draw.py` | 5 | 3 | `META` |
| `pools/face.py` | 1 | 7 | `FACE_DAILY` |
| `pools/face_from_v3.py` | 3 | 4 | `DIMS` |
| `pools/fashion.py` | 0 | 18 | `FASHION_ACTIONS` |
| `pools/fashion_draw.py` | 10 | 3 | `META` |
| `pools/hairstyles.py` | 8 | 10 | `_COLOR_TOKENS` |
| `pools/layer_index.py` | 22 | 9 | `_HERE` |
| `pools/layer_tables.py` | 1 | 11 | `PIPELINE` |
| `pools/level_ladder.py` | 6 | 7 | `LEVELS` |
| `pools/orchestrator.py` | 15 | 10 | `META` |
| `pools/pose_actions_from_v3.py` | 5 | 3 | `CAT_MAP` |
| `pools/pose_pools.py` | 6 | 4 | `_OUTDOOR_BAN` |
| `pools/pose_quota.py` | 5 | 2 | `USE_POSE_V2` |
| `pools/pose_table.py` | 3 | 21 | `POSTURES` |
| `pools/poses.py` | 4 | 17 | `BODY_POSES` |
| `pools/poses_from_v3.py` | 9 | 4 | `_HEAD_DROP_CATS` |
| `pools/preferences.py` | 0 | 8 | `ARMPIT_FITS` |
| `pools/roll_io.py` | 12 | 12 | `HERE` |
| `pools/roll_machine.py` | 24 | 5 | `CHAR_DECAY_START` |
| `pools/roll_params.py` | 22 | 45 | `HERE` |
| `pools/scene_from_v3.py` | 1 | 9 | `SCENES` |
| `pools/scene_pool.py` | 6 | 17 | `META` |
| `pools/scene_privacy.py` | 10 | 16 | `_HERE` |
| `pools/scenes.py` | 0 | 6 | `SCENES` |
| `pools/set_slots.py` | 0 | 2 | `SET_SLOTS` |
| `pools/sex_beats.py` | 3 | 8 | `PACE_RANGE` |
| `pools/sex_draw.py` | 16 | 19 | `META` |
| `pools/sex_pool.py` | 36 | 19 | `META` |
| `pools/sex_router.py` | 6 | 24 | `PARTS` |
| `pools/sex_sents.py` | 0 | 1 | `SEX_SENTS` |
| `pools/shot.py` | 1 | 20 | `ANGLES` |
| `pools/state.py` | 11 | 16 | `BOY_FORE` |
| `pools/state_from_v3.py` | 4 | 2 | `PHASE_V2_TO_V3` |
| `pools/state_pool.py` | 18 | 42 | `HERE` |
| `pools/status_pool.py` | 2 | 5 | `SEX_STATUS` |
| `pools/style_sets.py` | 0 | 3 | `STYLE_SETS` |
| `pools/styles.py` | 3 | 11 | `STYLES` |
| `pools/tease_draw.py` | 10 | 6 | `META` |
| `pools/tier_classify.py` | 4 | 5 | `TIERS` |
| `pools/trait_sex.py` | 16 | 11 | `DOMINANT_POSITIONS` |
| `pools/transit_scenes.py` | 4 | 1 | `TRANSIT` |
| `pools/v3_pools.py` | 4 | 21 | `SCENE_CATS` |
| `pools/wardrobe_from_v3.py` | 10 | 16 | `W_FASHION` |
| `pools/wardrobe_pools.py` | 8 | 19 | `META` |
| `pools/wardrobe_route.py` | 17 | 35 | `META` |
| `pools/wardrobe_sets.py` | 7 | 10 | `SETS` |
| `pools/wardrobe_slots.py` | 7 | 5 | `SLOTS` |
| `pools/wardrobe_v3.py` | 16 | 2 | `W` |
