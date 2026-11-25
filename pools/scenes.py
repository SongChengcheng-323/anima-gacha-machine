SCENES = [
    "bedroom", "bathroom", "kitchen", "classroom", "office",
    "beach", "poolside", "japanese room", "balcony", "library",
    "shrine", "rainy window", "cafe", "hotel room",
]

SCENE_INTERACT = [
    "", "", "", "", "",
    "tying her hair up", "adjusting her clothes",
]

LIGHTS = [
    "soft natural light", "warm sunset light", "cool moonlight",
    "warm lamp light", "neon lighting, colorful", "candle light, dim",
]

_CHAIN_SCENES = ['shopping street', 'city street', 'crosswalk', 'shop window', 'crowd', 'table', 'chair', 'window seat', 'movie theater', 'seat', 'armrest', 'screen glow', 'popcorn', 'bed', 'on bed', 'pillow', 'lamp', 'suitcase', 'living room', 'sofa', 'couch', 'tv', 'game console', 'carpet', 'kitchen counter', 'fridge', 'stove', 'plate', 'blanket', 'tent', 'sleeping bag', 'camping', 'lantern', 'flashlight', 'campsite', 'campfire', 'starry sky', 'log', 'forest', 'park', 'path', 'tree', 'stone', 'grass', 'sand', 'towel', 'ocean', 'seaside', 'sun', 'wave', 'pool', 'swim ring', 'lounger', 'water', 'onsen', 'hot spring', 'steam', 'rock', 'wooden bucket', 'ryokan', 'tatami', 'futon', 'sliding door', 'low table', 'school desk', 'blackboard', 'chalk', 'bookshelf', 'desk', 'books', 'rooftop', 'fence', 'city view', 'sky', 'water tank', 'festival', 'matsuri', 'stall', 'yukata', 'fireworks', 'night sky', 'riverbank', 'aquarium', 'fish tank', 'blue light', 'glass', 'car interior', 'car seat', 'steering wheel', 'window', 'train interior', 'handrail', 'photo booth', 'curtain', 'stool', 'torii', 'stone steps']
SCENES = list(SCENES) + [w for w in _CHAIN_SCENES if w not in SCENES]

SCENE_OUTDOOR = {
    "beach", "poolside", "balcony", "shrine",
    "shopping street", "city street", "crosswalk", "shop window", "crowd",
    "tent", "camping", "campsite", "campfire",
    "starry sky", "night sky", "sky", "fireworks", "city view",
    "forest", "park", "path", "tree", "grass", "stone", "stone steps",
    "sand", "ocean", "seaside", "sun", "wave", "riverbank",
    "pool", "swim ring", "lounger", "water", "onsen", "hot spring", "rock",
    "rooftop", "fence", "water tank", "festival", "matsuri", "stall", "torii",
}
_miss = SCENE_OUTDOOR - set(SCENES)
assert not _miss, f"SCENE_OUTDOOR 里这些不在 SCENES 里: {_miss}"
