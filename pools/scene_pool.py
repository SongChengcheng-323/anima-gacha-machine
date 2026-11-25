import random

META = {
    "id": "scene_pool",
    "cn": "纯场景池",
    "kind": "pool",
    "tier": "none",
    "parent": None,
    "enabled": True,
    "desc": "只写场景；每条带 indoor/outdoor 标记（⚠️ 未接入）",
    "version": "v0.99.0",
    "refs": [],
}

SCENES = [
    "bedroom",
    "bathroom",
    "kitchen",
    "classroom",
    "office",
    "beach",
    "poolside",
    "japanese room",
    "balcony",
    "library",
    "shrine",
    "rainy window",
    "cafe",
    "hotel room",
    "shopping street",
    "city street",
    "crosswalk",
    "shop window",
    "crowd",
    "table",
    "chair",
    "window seat",
    "movie theater",
    "bed",
    "on bed",
    "pillow",
    "suitcase",
    "living room",
    "sofa",
    "couch",
    "game console",
    "carpet",
    "kitchen counter",
    "fridge",
    "stove",
    "plate",
    "blanket",
    "tent",
    "sleeping bag",
    "camping",
    "lantern",
    "campsite",
    "campfire",
    "starry sky",
    "log",
    "forest",
    "park",
    "path",
    "tree",
    "stone",
    "grass",
    "sand",
    "towel",
    "ocean",
    "seaside",
    "sun",
    "wave",
    "pool",
    "swim ring",
    "lounger",
    "water",
    "onsen",
    "hot spring",
    "rock",
    "wooden bucket",
    "ryokan",
    "tatami",
    "futon",
    "sliding door",
    "low table",
    "school desk",
    "blackboard",
    "chalk",
    "bookshelf",
    "desk",
    "books",
    "rooftop",
    "fence",
    "city view",
    "sky",
    "water tank",
    "festival",
    "matsuri",
    "stall",
    "fireworks",
    "riverbank",
    "aquarium",
    "fish tank",
    "glass",
    "car interior",
    "car seat",
    "steering wheel",
    "window",
    "train interior",
    "handrail",
    "photo booth",
    "curtain",
    "stool",
    "torii",
    "stone steps",
]

SCENE_PLACE = {
    "bedroom": "indoor",
    "bathroom": "indoor",
    "kitchen": "indoor",
    "classroom": "indoor",
    "office": "indoor",
    "beach": "outdoor",
    "poolside": "outdoor",
    "japanese room": "indoor",
    "balcony": "outdoor",
    "library": "indoor",
    "shrine": "outdoor",
    "rainy window": "indoor",
    "cafe": "indoor",
    "hotel room": "indoor",
    "shopping street": "outdoor",
    "city street": "outdoor",
    "crosswalk": "outdoor",
    "shop window": "outdoor",
    "crowd": "outdoor",
    "table": "indoor",
    "chair": "indoor",
    "window seat": "indoor",
    "movie theater": "indoor",
    "seat": "indoor",
    "armrest": "indoor",
    "popcorn": "indoor",
    "bed": "indoor",
    "on bed": "indoor",
    "pillow": "indoor",
    "suitcase": "indoor",
    "living room": "indoor",
    "sofa": "indoor",
    "couch": "indoor",
        "game console": "indoor",
    "carpet": "indoor",
    "kitchen counter": "indoor",
    "fridge": "indoor",
    "stove": "indoor",
    "plate": "indoor",
    "blanket": "indoor",
    "tent": "outdoor",
    "sleeping bag": "indoor",
    "camping": "outdoor",
    "lantern": "outdoor",
    "campsite": "outdoor",
    "campfire": "outdoor",
    "starry sky": "outdoor",
    "log": "outdoor",
    "forest": "outdoor",
    "park": "outdoor",
    "path": "outdoor",
    "tree": "outdoor",
    "stone": "outdoor",
    "grass": "outdoor",
    "sand": "outdoor",
    "towel": "outdoor",
    "ocean": "outdoor",
    "seaside": "outdoor",
    "sun": "outdoor",
    "wave": "outdoor",
    "pool": "outdoor",
    "swim ring": "outdoor",
    "lounger": "outdoor",
    "water": "outdoor",
    "onsen": "outdoor",
    "hot spring": "outdoor",
    "rock": "outdoor",
    "wooden bucket": "outdoor",
    "ryokan": "indoor",
    "tatami": "indoor",
    "futon": "indoor",
    "sliding door": "indoor",
    "low table": "indoor",
    "school desk": "indoor",
    "blackboard": "indoor",
    "chalk": "indoor",
    "bookshelf": "indoor",
    "desk": "indoor",
    "books": "indoor",
    "rooftop": "outdoor",
    "fence": "outdoor",
    "city view": "outdoor",
    "sky": "outdoor",
    "water tank": "outdoor",
    "festival": "outdoor",
    "matsuri": "outdoor",
    "stall": "outdoor",
    "fireworks": "outdoor",
    "riverbank": "outdoor",
    "aquarium": "indoor",
    "fish tank": "indoor",
    "glass": "indoor",
    "car interior": "indoor",
    "car seat": "indoor",
    "steering wheel": "indoor",
    "window": "indoor",
    "train interior": "indoor",
    "handrail": "indoor",
    "photo booth": "indoor",
    "curtain": "indoor",
    "stool": "indoor",
    "torii": "outdoor",
    "stone steps": "outdoor",
}

def place_of(scene):
    return SCENE_PLACE.get(scene, "indoor")

TIER_IDX = {"fashion": 0, "tease": 1, "exposed": 2, "sex": 3}

NOT_SCENE = frozenset(('towel', 'chalk', 'plate', 'glass', 'books', 'swim ring', 'wooden bucket', 'flashlight', 'lantern', 'fridge', 'stove', 'tv', 'game console', 'pillow', 'blanket', 'armrest', 'steering wheel', 'handrail', 'sliding door', 'curtain', 'carpet', 'blackboard', 'sun', 'sky', 'starry sky', 'night sky', 'wave', 'water', 'sand', 'grass', 'rock', 'stone', 'log', 'fence', 'fireworks', 'campfire', 'steam', 'torii',
                      'fish tank', 'water tank',
                      'rainy window', 'car seat',
                      'suitcase', 'tree', 'window', 'city view'))

def candidates_ok():
    return [s for s in SCENES
            if s not in NOT_SCENE and s not in FURNITURE and s not in DROPPED]

FURNITURE = frozenset({
    "bed", "on bed", "futon", "tatami", "lounger", "sleeping bag",
    "sofa", "couch", "chair", "stool", "window seat",
    "table", "low table", "desk", "school desk", "kitchen counter",
    "bookshelf",
})

PROPS = frozenset({
    "pillow", "blanket", "carpet", "curtain", "books", "lantern", "cushion",
})

DROPPED = frozenset({"sleeping bag"})

def pick_prop(rng, tier=None, scene=""):
    if rng.random() > (0.30 if tier != "fashion" else 0.20):
        return ""
    pool = sorted(PROPS)
    return rng.choice(pool) if pool else ""

PUBLIC_SCENES = frozenset((
    "crowd", "crosswalk", "city street", "shopping street", "shop window",
    "matsuri", "festival", "stall", "train interior", "movie theater",
    "cafe", "classroom", "school desk", "library", "office", "aquarium",
    "photo booth",
))
MILD_PLAYS = frozenset(("kiss", "tonguekiss", "hold_hands", "kiss_hand",
                        "lick_hand", "spank", "fondle", "licking", "self_pinch"))

BED_SCENES = frozenset({
    "bedroom", "bathroom", "hotel room", "bed", "on bed", "sofa", "couch",
    "sleeping bag", "onsen", "tatami", "futon",
})

FASHION_BAN_SCENES = frozenset({"poolside", "bathroom", "love hotel room", "onsen"})

def pick(rng, tier=None, plays=None, force_place=None, trait=None, min_privacy=None):
    pool = candidates_ok()
    if force_place == "outdoor":
        _out = [s for s in pool if place_of(s) == "outdoor"]
        pool = _out or pool
    if tier == "fashion" and FASHION_BAN_SCENES:
        _ok = [s for s in pool if s not in FASHION_BAN_SCENES]
        pool = _ok or pool
    if plays and any(p not in MILD_PLAYS for p in plays):
        _ok = [s for s in pool if s not in PUBLIC_SCENES]
        pool = _ok or pool
    if min_privacy is not None:
        try:
            from pools import scene_privacy as _SP
        except Exception:
            import scene_privacy as _SP
        _hi = [s for s in pool if _SP.privacy_of(s) >= min_privacy]
        pool = _hi or pool
    if tier:
        try:
            from pools import scene_privacy as SPV
        except Exception:
            import scene_privacy as SPV
        w = SPV.weights_for(pool, tier, trait)
        if sum(w) <= 0:
            return rng.choice(pool)
        return rng.choices(pool, weights=w, k=1)[0]

    if tier:
        try:
            from pools import layer_tables as LT
        except Exception:
            try:
                from pools import layer_tables as LT
            except Exception:
                import layer_tables as LT
        try:
            _SW = getattr(LT, "SCENE_WEIGHTS", None) or LT.SCENE_W
            _FLAT = (1.0, 1.0, 1.0, 1.0)
            w = [_SW.get(LT.scene_level(s), _FLAT)[TIER_IDX[tier]] for s in pool]
            return rng.choices(pool, weights=w, k=1)[0]
        except Exception:
            pass
    return rng.choice(pool)

def candidates():
    return candidates_ok()

SCENES_V2 = SCENES
SCENE_PLACE_V2 = SCENE_PLACE
PUBLIC_SCENES_V2 = PUBLIC_SCENES
BED_SCENES_V2 = BED_SCENES

def _use_scene_from_v3():
    try:
        from pools import roll_params as _RP
    except Exception:
        try:
            from . import roll_params as _RP
        except Exception:
            try:
                import roll_params as _RP
            except Exception:
                return True
    return bool(getattr(_RP, "USE_SCENE_FROM_V3", True))

USE_SCENE_FROM_V3 = _use_scene_from_v3()

if USE_SCENE_FROM_V3:
    try:
        from pools import scene_from_v3 as _SV3
    except Exception:
        try:
            from . import scene_from_v3 as _SV3
        except Exception:
            import scene_from_v3 as _SV3
    SCENES = list(_SV3.SCENES)
    SCENE_PLACE = dict(_SV3.SCENE_PLACE)
    PUBLIC_SCENES = frozenset(_SV3.PUBLIC_SCENES)
    BED_SCENES = frozenset(_SV3.PRIVATE_SCENES)
    TIGHT_SPACES = frozenset(_SV3.TIGHT_SPACES)
    SCENE_LEVEL_V3 = dict(_SV3.SCENE_LEVEL)
    try:
        try:
            from pools import layer_tables as _LT
        except Exception:
            from . import layer_tables as _LT
        for _w, _lv in SCENE_LEVEL_V3.items():
            _LT.SCENE_LEVEL.setdefault(_w, _lv)
    except Exception:
        pass
