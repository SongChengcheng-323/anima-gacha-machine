FASHION_ACTIONS = [
    "",
    "",
    "adjusting her hair",
    "brushing hair back",
    "turning slightly",
    "adjusting her earrings",
    "tying her hair up",
    "adjusting her clothes",
    None,
    "reaching up to a shelf",
]

FASHION_HAND_W = {
    "hands relaxed at her sides":      1.0,
    "one hand holding her bag":        0.30,
    "hands in her pockets":            0.80,
    "one hand adjusting her hair":     0.25,
    "one hand resting on her waist":   0.90,
}

FASHION_ACTION_W = {
    "adjusting her hair":      0.25,
    "brushing hair back":      0.30,
    "tying her hair up":       0.30,
    "reaching up to a shelf":  0.60,
    "adjusting her earrings":  1.00,
    "turning slightly":        1.00,
    "adjusting her clothes":   1.00,
}

FASHION_ENV_EXTRA = [
    "environment detailed and atmospheric",
    "background in focus",
    "intricate background details",
    "richly detailed surroundings",
]

FASHION_CAMS = [
    "full body",
    "establishing shot, full body",
]

FASHION_BANNED_CAMS = {
    "close-up on breasts, nipples", "close-up on chest, nipples",
    "close-up on pussy", "close-up on hips and thighs, pussy",
}

FASHION_DOCTOR = {
    "slim": False,
    "dedupe": True,
    "fix_mutex": True,
    "max_len": 1200,
}

FASHION_BODY = {
    "head": [
        "head tilted to one side",
        "head turned to the side",
        "head slightly raised, chin up",
    ],
    "hand": [
        "hands relaxed at her sides",
        "one hand holding her bag",
        "hands in her pockets",
        "one hand adjusting her hair",
        "one hand resting on her waist",
    ],
    "leg": [
        "legs together, knees touching",
        "one leg crossed over the other",
        "legs slightly apart",
        "legs apart, relaxed",
        "ankles crossed",
        "straight legs",
    ],
}

FASHION_ACCESSORY_SLOTS = {
    "head": [
        "wool beret", "wide-brim hat", "straw sun hat", "knit beanie",
        "silk headband", "hair ribbon", "pearl hair clip", "flower hairpin",
    ],
    "ears": [
        "small gold hoop earrings", "pearl stud earrings", "droplet earrings",
        "geometric earrings", "delicate drop earrings", "silver ear cuffs",
    ],
    "neck": [
        "fine gold chain necklace", "layered necklaces", "pearl choker",
        "silk scarf around the neck", "delicate pendant necklace",
        "patterned neck scarf", "ribbon choker",
    ],
    "wrist": [
        "thin bracelet", "gold watch", "layered bracelets",
        "leather strap watch", "beaded bracelet", "silver bangle",
    ],
    "hands": [
        "holding a small handbag", "leather tote bag", "small crossbody bag",
        "delicate ring", "clutch purse",
        "carrying a book against her chest",
        "holding a takeaway coffee cup", "holding a folded umbrella",
        "carrying a paper shopping bag",
    ],
    "waist": [
        "wide leather belt", "thin waist belt", "chain belt",
        "fabric sash at the waist", "decorative belt with buckle",
    ],
    "legs": [
        "sheer pantyhose", "over-knee socks", "patterned tights",
        "lace-trimmed thighhighs", "ribbed knee socks",
    ],
    "feet": [
        "leather loafers", "ankle boots", "strappy heels", "canvas sneakers",
        "mary jane shoes", "chunky boots", "kitten heels",
    ],
}

FASHION_STYLE_LEVELS = [
    ("minimal", 0.30, (1, 2)),
    ("normal",  0.50, (3, 4)),
    ("rich",    0.20, (5, 7)),
]

FASHION_PLACES = [
    "modern cafe interior", "city street sidewalk", "library reading area",
    "art gallery hall", "rooftop terrace", "train station platform",
    "flower garden path", "japanese garden", "seaside promenade",
    "boutique storefront", "museum corridor", "office with tall windows",
    "quiet residential alley", "park bench area", "balcony overlooking the city",
    "old bookstore", "greenhouse", "riverside walkway", "hotel lobby",
    "university campus courtyard", "pier with wooden planks", "market street",
]

FASHION_PLACES_INDOOR = {
    "modern cafe interior", "library reading area", "art gallery hall", "museum corridor",
    "office with tall windows", "old bookstore", "greenhouse", "hotel lobby",
    "boutique storefront",
}

FASHION_LIGHT_WEATHER = {
    "overcast day, soft diffused light",
    "after rain, wet reflective surfaces, soft grey light",
    "light snow, cool pale light, quiet atmosphere",
    "spring breeze, dappled light through leaves",
}

FASHION_TIME_LIGHT = [
    "early morning, soft warm light",
    "late morning, bright clear daylight",
    "noon, crisp overhead light",
    "afternoon, golden warm light",
    "golden hour, warm rim light",
    "dusk, soft ambient glow",
    "evening, warm streetlights",
    "night, cool moonlight",
    "overcast day, soft diffused light",
    "after rain, soft grey light",
    "light snow, cool pale light",
    "spring breeze, dappled light",
]

FASHION_ATMOSPHERE = [
    "calm and serene mood",
    "lively bustling atmosphere",
    "quiet intimate atmosphere",
    "quiet elegant atmosphere",
    "nostalgic warm atmosphere",
    "fresh clean atmosphere",
    "bright cheerful atmosphere",
    "solitary contemplative mood",
    "cozy sheltered atmosphere",
]

FASHION_HANDS = {
    "free": [
        "hands relaxed at her sides",
        "hands hanging naturally, fingers relaxed",
        "arms hanging loose, casual stance",
        "arms hanging by her sides, relaxed shoulders",
        "", "", "",
    ],
    "one": [
        "one hand on her hip",
        "one hand resting on her thigh",
        "one hand touching her own arm",
        "one hand adjusting her hair",
        "one hand adjusting her collar",
        "one hand touching her earring",
        "one hand holding the hem of her skirt",
        "one hand resting on her waist",
        "one hand tucked into her pocket",
        "one hand on the back of her head",
        "one hand on her chest",
    ],
    "both": [
        "hands in her pockets",
        "hands behind her back",
        "both hands on her thighs",
        "both hands holding her hair",
    ],
}

FASHION_POCKET_OK = [
    "pants", "jeans", "shorts", "trousers", "cargo", "overalls", "dungarees",
    "jacket", "coat", "blazer", "cardigan", "hoodie", "sweater",
]

FASHION_HAND_HOLDING = ("bag", "purse", "bouquet", "mirror", "coffee", "cup", "phone")
