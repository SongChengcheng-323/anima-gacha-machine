import os as _os, sys as _sys
if _os.path.dirname(_os.path.abspath(__file__)) not in _sys.path:
    _sys.path.append(_os.path.dirname(_os.path.abspath(__file__)))

"""候选池总入口。

orchestrator / roll_params 等模块从这里拿池子数据：
    from pools import SCENES, STYLES, ...
这样"逻辑"和"数据"就分开住了 —— 改池子只动 pools/ 下的文件。
"""

from .characters import (
    CHARACTERS,
    CHARACTER_WEIGHTS,
    STYLE_LOCK,
    PUBIC,
    LORA_MAP,
    FEAT_VARIANTS,
)

from .eros import (
    EROS_FASHION,
    EROS_TEASE_UNITS,
    EROS_EXPOSED_UNITS,
    pick_eros_units,
)

from .actions import (
    ACTIONS,
)

from .poses import (
    BODY_POSES,
    BODY_RULES,
    HAND_SINGLE,
    HAND_OCCUPY_KW,
    HAND_BOTH,
)

from .scenes import (
    SCENES,
    SCENE_INTERACT,
    LIGHTS,
    SCENES,
    SCENE_INTERACT,
    LIGHTS,
    SCENE_OUTDOOR,
)

from .cameras import (
    CAMERAS,
    SHOT_GAZE,
    GAZE_WORDS,
)

from .styles import (
    STYLES,
    STYLE_PREFIX,
    STYLE_W,
    ACTIVE_STYLES,
    HEAD,
    HEAD_FASHION,
    _ECCHI_STYLE_WORDS,
)

from .preferences import (
    ARMPIT_FITS,
    BACKSHOT_BODY,
    BACKSHOT_CAMS,
    BACKSHOT_LEGS,
    MATURE_KW,
    FOOT_CHARS,
    FOOT_CHAR_KW,
    FOOT_SHOE_KW,
)

from .fashion import (
    FASHION_ACTIONS,
    FASHION_ENV_EXTRA,
    FASHION_CAMS,
    FASHION_BANNED_CAMS,
    FASHION_DOCTOR,
    FASHION_BODY,
    FASHION_HANDS,
    FASHION_POCKET_OK,
    FASHION_HAND_HOLDING,
    FASHION_ACCESSORY_SLOTS,
    FASHION_STYLE_LEVELS,
    FASHION_PLACES,
    FASHION_PLACES_INDOOR,
    FASHION_LIGHT_WEATHER,
    FASHION_TIME_LIGHT,
    FASHION_ATMOSPHERE,
)

from .composition import (
    ANGLES,
    ANGLE_WEIGHTS,
    SCALES,
    SCALE_WEIGHTS,
    POSITIONS,
    POSITION_WEIGHTS,
    LENSES,
    LENS_WEIGHTS,
    FOREGROUND,
    FG_CHANCE_GUOFENG,
    FG_CHANCE_OTHER,
    ANGLE_SCALE_MUTEX,
    POSITION_SCALE_MUTEX,
    ANGLE_POSITION_MUTEX,
)

from .style_sets import (
    STYLE_SETS,
    SEASON_ACC,
    ACC_MOOD,
)

from .face import (
    FACE_DAILY,
    FACE_FLIRTY,
    FACE_SEX,
    FACE_POOLS,
    FACE_BY_TIER,
    pick_face,
)

from .shot import (
    ANGLES as SHOT_ANGLES,
    DISTANCES,
    POSITIONS as SHOT_POSITIONS,
    LENSES as SHOT_LENSES,
    FOREGROUND as SHOT_FOREGROUND,
    FACING,
    FACING_WEIGHTS,
    FACING_GAZE_MUTEX,
    FACING_BODY_MUTEX,
    FRAMING_PARTS,
    FRAMING_LENS_OK,
    FRAMING_ANGLE_BAN,
    FRAMING_BY_TIER,
    FRAMING_TO_VIS,
    FRAMING_SLOTS,
    FRAMING_HIDDEN_KW,
    slot_visible,
)

from .sex_sents import SEX_SENTS
from .transit_scenes import TRANSIT, pick as pick_transit, variants as transit_variants
