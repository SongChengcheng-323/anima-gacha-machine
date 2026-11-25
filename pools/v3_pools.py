SCENE_CATS = {
    "INDOOR_HOME": ["bedroom", "living room", "bathroom", "love hotel room"],
    "INDOOR_PUBLIC": ["cafe", "library", "classroom", "office"],
    "INDOOR_TRANSIT": ["train interior", "bus interior", "car interior"],
    "SEMI_PRIVATE": ["locker room", "fitting room", "karaoke room"],
    "OUTDOOR_CITY": ["city street", "rooftop", "park", "balcony"],
    "OUTDOOR_NATURE": ["forest", "lake shore", "campsite"],
    "WATERFRONT": ["beach", "poolside", "pier"],
    "JAPANESE_FESTIVAL": ["shrine", "summer festival", "onsen"],
    "ENTERTAINMENT": ["arcade", "observation deck"],
}

SCENE_ALL = [w for ws in SCENE_CATS.values() for w in ws]
SCENE_CAT_OF = {w: k for k, ws in SCENE_CATS.items() for w in ws}

SCENE_RETIRED = {
    "elevator": "2026-10-31 作者：电梯直接去掉，不管哪个档位都不要抽",
}

_OUT = {"OUTDOOR_CITY", "OUTDOOR_NATURE", "WATERFRONT", "JAPANESE_FESTIVAL"}
SCENE_PLACE = {w: ("outdoor" if k in _OUT else "indoor")
               for k, ws in SCENE_CATS.items() for w in ws}

PUBLIC_SCENES = frozenset({
    "classroom", "club room", "library", "cafe", "restaurant", "cafeteria",
    "convenience store", "bookstore", "museum", "art gallery", "aquarium",
    "movie theater", "office", "hotel lobby", "gymnasium",
    "city street", "shopping street", "market street", "crosswalk", "sidewalk",
    "plaza", "bus stop", "ferris wheel cabin", "ropeway cabin", "amusement park",
    "train interior", "subway interior", "bus interior", "tram interior",
    "train station platform", "festival street", "festival stall", "summer festival",
})

TIGHT_SPACES = frozenset({
    "fitting room", "photo booth", "toilet stall", "locker room", "karaoke room",
    "elevator", "stairwell", "parking garage", "capsule hotel room",
})

PRIVATE_SCENES = frozenset(SCENE_CATS["INDOOR_HOME"]) | TIGHT_SPACES

PROP_CATS = {
    "bag": {"cn": "包袋", "held": False, "items": [
        "shoulder bag",
        "tote bag",
        "crossbody bag",
        "satchel",
        "backpack",
        "clutch",
        "pouch",
        "handbag",
        "basket bag",
        "briefcase",
        "duffel bag",
        "drawstring bag",
    ]},
    "held_small": {"cn": "手持小物", "held": True, "items": [
        "folding fan",
        "uchiwa",
        "paper umbrella",
        "parasol",
        "hand mirror",
        "smartphone",
        "camera",
        "microphone",
        "plush toy",
        "balloon",
    ]},
    "book_stationery": {"cn": "书本文具", "held": True, "items": [
        "book",
        "open book",
        "notebook",
        "magazine",
        "newspaper",
        "letter",
        "chalk",
        "pencil",
        "sketchbook",
    ]},
    "light": {"cn": "灯具烛台", "held": False, "items": [
        "candle",
        "candle holder",
        "lantern",
        "paper lantern",
        "oil lamp",
        "flashlight",
        "string lights",
    ]},
    "flower_plant": {"cn": "花与植物", "held": True, "items": [
        "bouquet of flowers",
        "single flower",
        "rose",
        "flower petals",
        "potted plant",
        "flower basket",
        "flower crown",
    ]},
    "food_drink": {"cn": "饮食", "held": True, "items": [
        "coffee cup",
        "tea cup",
        "wine glass",
        "water bottle",
        "canned drink",
        "bento box",
        "plate of food",
        "ice cream cone",
        "apple",
    ]},
    "soft_bedding": {"cn": "寝具软物", "held": False, "items": [
        "pillow",
        "cushion",
        "blanket",
        "quilt",
        "folded blanket",
        "picnic sheet",
        "beach towel",
    ]},
    "weapon_wa": {"cn": "武装与和风持物", "held": True, "items": [
        "katana",
        "wooden staff",
        "sword",
        "greatsword",
        "dagger",
        "crossbow",
        "rifle",
        "spear",
        "shield",
        "anchor",
    ]},
    "adult_toy": {"cn": "成人玩具", "held": True, "items": [
        "dildo",
        "vibrator",
        "bullet vibrator",
        "butt plug",
        "anal beads",
        "strap-on harness",
        "blindfold",
        "tail plug",
    ]},
    "misc": {"cn": "其他随身小物", "held": False, "items": [
        "wooden bucket",
        "swim ring",
        "helmet",
        "basket",
        "tray",
        "telescope",
        "bicycle bell",
        "game console",
    ]},
}

COVER = {
    "chest": ("blazer","jacket","coat","trench","parka","puffer","bomber","varsity","trucker",
              "cardigan","sweater","turtleneck","knit","polo","jersey","hoodie","flannel",
              "shirt","vest","uniform","kimono","yukata","robe","pajama","nightgown",
              "hanfu","qipao","cheongsam"),
    "legs":  ("jeans","trousers","pants","slacks","leggings","joggers","cargo","overalls","jumpsuit"),
    "tight": ("fitted","slim","skinny","tight","bodycon","corset","pencil","ribbed","bustier"),
}
def covers(item):
    t = " " + item["en"].lower().replace("-", " ") + " "
    return {k: any(x in t for x in v) for k, v in COVER.items()}

WARDROBE = {
    "upper": {
        "fashion": [
            "t-shirt", "oversized t-shirt only", "blouse", "silk blouse", "button-down shirt",
            "flannel shirt", "poplin shirt", "knit sweater", "turtleneck sweater",
            "cashmere crewneck sweater", "cardigan", "cropped cardigan", "longline cardigan",
            "hoodie", "zip-up hoodie", "denim jacket", "structured blazer", "fitted blazer",
            "double-breasted blazer", "oversized bomber jacket", "varsity jacket",
            "track jacket", "trench coat", "long wool coat", "tailored vest", "knit polo",
            "sports jersey", "wrap blouse", "puff-sleeve blouse", "mandarin-collar shirt",
            "hanfu-style wrapped top", "qipao-style top", "sailor school uniform",
            "school uniform", "uniform", "kimono", "yukata", "apron", "pajama", "nightgown",
        ],
        "tease": [
            "camisole", "lace-trimmed camisole", "crop top", "ribbed tank top", "corset top",
            "off-shoulder knit", "sheer chiffon blouse", "unbuttoned white dress shirt",
            "towel wrapped around body", "naked apron", "leotard", "highleg leotard",
            "strapless leotard", "bodysuit",
        ],
        "exposed": [
            "lingerie set", "bikini", "one-piece swimsuit", "bare upper body", "topless",
        ],
        "sex_ban": [
            "structured blazer", "fitted blazer", "double-breasted blazer",
            "oversized bomber jacket", "varsity jacket", "track jacket", "denim jacket",
            "trench coat", "long wool coat", "cardigan", "cropped cardigan",
            "longline cardigan", "knit sweater", "turtleneck sweater",
            "cashmere crewneck sweater", "hoodie", "zip-up hoodie", "flannel shirt",
            "button-down shirt", "poplin shirt", "tailored vest", "knit polo", "sports jersey",
            "school uniform", "uniform", "sailor school uniform",
            "kimono", "yukata", "suit", "military uniform", "police uniform", "nurse uniform",
        ],
        "cover": [
            "structured blazer", "fitted blazer", "double-breasted blazer",
            "oversized bomber jacket", "varsity jacket", "track jacket", "denim jacket",
            "trench coat", "long wool coat", "cardigan", "cropped cardigan",
            "longline cardigan", "knit sweater", "turtleneck sweater",
            "cashmere crewneck sweater", "hoodie", "zip-up hoodie", "flannel shirt",
            "button-down shirt", "poplin shirt", "tailored vest", "knit polo", "sports jersey",
            "mandarin-collar shirt", "sailor school uniform", "school uniform", "uniform",
            "kimono", "yukata",
        ],
    },
    "lower": {
        "fashion": [
            "pleated skirt", "A-line midi skirt", "circle skirt", "pencil skirt",
            "long flowy skirt", "wrap midi skirt", "tiered prairie skirt", "tulle midi skirt",
            "jeans", "straight-leg jeans", "baggy wide-leg jeans", "wide-leg pants",
            "straight-leg trousers", "wide-leg trousers", "slim pants", "cropped trousers",
            "high-waisted slacks", "cargo pants", "jogger pants", "parachute pants",
            "denim shorts", "short shorts", "tailored shorts", "linen shorts",
            "ripped jeans", "distressed jeans", "ripped denim shorts",
            "modernized horse-face skirt", "layered hanfu skirt", "qipao skirt",
        ],
        "tease": [
            "micro skirt", "pleated mini skirt", "wrap mini skirt", "ribbed bike shorts",
            "towel around waist", "sleep shorts",
        ],
        "exposed": [
            "bare lower body", "bare thighs",
        ],
        "sex_ban": [
            "jeans", "straight-leg jeans", "baggy wide-leg jeans", "wide-leg pants",
            "straight-leg trousers", "wide-leg trousers", "slim pants", "cropped trousers",
            "high-waisted slacks", "cargo pants", "jogger pants", "parachute pants",
            "ripped jeans", "distressed jeans",
        ],
        "cover": [
            "jeans", "straight-leg jeans", "baggy wide-leg jeans", "wide-leg pants",
            "straight-leg trousers", "wide-leg trousers", "slim pants", "cropped trousers",
            "high-waisted slacks", "cargo pants", "jogger pants", "parachute pants",
            "ripped jeans", "distressed jeans",
        ],
    },
    "under": {
        "fashion": [],
        "tease": [
            "panties", "cotton panties", "frilled panties", "high-cut panties",
            "side-tie panties", "lace-trimmed panties", "striped panties", "bloomers",
        ],
        "exposed": [
            "pussy exposed", "bare buttocks", "anus visible",
        ],
        "sex_ban": [],
        "cover": [],
    },
    "legwear": {
        "fashion": [
            "knee-high socks", "over-knee socks", "crew socks", "ribbed ankle socks",
            "opaque tights", "plain cotton tights", "patterned tights", "seamless tights",
            "pantyhose", "sheer pantyhose", "patterned pantyhose",
            "white thighhighs", "white pantyhose", "white tights",
        ],
        "tease": [
            "thighhighs", "lace-trimmed thighhighs", "white lace thighhighs",
            "single thighhigh", "lace-top tights", "sheer black tights", "ripped pantyhose",
            "seam tights", "crossover leg warmers", "thigh ring", "garter belt",
            "torn thighhighs", "ripped socks", "torn pantyhose",
        ],
        "exposed": [
            "bare legs",
        ],
        "sex_ban": [],
        "cover": [],
    },
    "shoes": {
        "fashion": [
            "loafers", "leather loafers", "heeled loafers", "oxford shoes", "mary jane shoes",
            "ballet flats", "pointed-toe flats", "embroidered flats", "sneakers",
            "minimal white sneakers", "canvas sneakers", "high-top sneakers", "dad sneakers",
            "boots", "ankle boots", "leather ankle boots", "platform boots", "thigh boots",
            "heels", "kitten heels", "strappy heels", "pointed pumps", "slingback pumps",
            "t-strap heels", "slingback kitten heels", "platform sandals", "woven sandals",
            "woven espadrilles", "suede mules", "canvas slip-ons", "cloth shoes",
            "house slippers", "ballet slippers",
        ],
        "tease": [],
        "exposed": [
            "barefoot",
        ],
        "sex_ban": ["*"],
        "cover": [],
    },
    "accessory": {
        "fashion": [
            "stud earrings", "pearl stud earrings", "small gold stud earrings",
            "hoop earrings", "gold hoop earrings", "silver hoop earrings", "dangling earrings",
            "drop earrings", "star-shaped dangling earrings",
            "crescent-shaped dangling earrings", "geometric earrings", "tassel earrings",
            "wooden earrings", "pearl drop earrings", "glasses", "round glasses",
            "silver round glasses", "black-framed glasses", "thin-framed eyewear",
            "thick-framed eyewear", "semi-rimless eyewear", "cat eye eyewear",
            "heart-shaped eyewear", "sunglasses", "pince-nez", "silver bangle",
            "thin bracelet", "beaded bracelet", "layered bracelets", "delicate ring",
            "classic watch", "gold watch", "leather strap watch", "silver ear cuffs",
        ],
        "tease": [],
        "exposed": [],
        "sex_ban": [],
        "cover": [],
    },
    "headwear": {
        "fashion": [
            "beret", "wool beret", "knit beanie", "snapback cap", "newsboy cap", "bucket hat",
            "wide-brim hat", "straw sun hat", "pillbox hat", "felt hat", "crochet hat",
            "bandana", "linen headscarf", "headband", "silk headband", "thin headband",
            "wide ribbon headband", "sporty headband", "lace headband", "hair bow",
            "hair ribbon", "ribbon hair tie", "pearl hair clip", "flower hairpin",
            "jade hairpin", "tassel hairpin", "thin barrette", "tortoiseshell hair clip",
            "pearl hair comb", "pearl headpiece", "flower hair wreath",
        ],
        "tease": [],
        "exposed": [],
        "sex_ban": [],
        "cover": [],
    },
    "neckwear": {
        "fashion": [
            "necklace", "thin gold chain", "fine gold chain necklace", "thin silver necklace",
            "beaded necklace", "pearl necklace", "pearl strand", "cameo pendant",
            "jade pendant", "dried flower pendant", "delicate bar necklace",
            "small pendant necklace", "choker", "pearl choker", "ribbon choker",
            "pearl ribbon choker", "leather choker", "thin leather choker", "gold locket",
            "cameo brooch", "scarf", "silk scarf", "silk neck scarf", "linen scarf",
            "knit scarf", "patterned neck scarf", "ribbon neck bow",
        ],
        "tease": [],
        "exposed": [],
        "sex_ban": [],
        "cover": [],
    },
    "handwear": {
        "fashion": [
            "gloves", "elbow gloves", "fingerless gloves", "arm warmers", "wrist cuffs",
            "leather tote bag", "structured tote bag", "structured shoulder bag",
            "canvas shoulder bag", "canvas tote", "crossbody bag", "small crossbody bag",
            "vintage shoulder bag", "quilted shoulder bag", "vintage clasp bag",
            "embroidered pouch", "beaded clutch", "mini handbag", "leather satchel",
            "structured satchel", "minimal leather backpack", "bumbag", "woven basket bag",
            "hand fan",
        ],
        "tease": [
            "lace blindfold over her eyes",
        ],
        "exposed": [
            "bare arm",
        ],
        "sex_ban": [
            "leather tote bag", "structured tote bag", "structured shoulder bag",
            "canvas shoulder bag", "canvas tote", "crossbody bag", "small crossbody bag",
            "vintage shoulder bag", "quilted shoulder bag", "vintage clasp bag",
            "embroidered pouch", "beaded clutch", "mini handbag", "leather satchel",
            "structured satchel", "minimal leather backpack", "bumbag", "woven basket bag",
            "hand fan",
        ],
        "cover": [],
    },
    "set": {
        "fashion": [
            "sailor school uniform", "maid outfit", "nurse uniform", "jumpsuit",
            "one-piece dress", "long dress", "satin slip dress", "cheongsam", "qipao",
            "kimono", "yukata", "overalls", "pajama",
        ],
        "tease": [
            "babydoll nightgown", "naked apron", "towel wrapped around body",
        ],
        "exposed": [],
        "sex_ban": [
            "sailor school uniform", "maid outfit", "nurse uniform", "overalls",
        ],
        "cover": [],
    },
}

FACE_MERGED = {
    "smile_soft": ["soft smile", "gentle smile"],
    "shy": ["shy expression", "flustered but pleased"],
    "afterglow": ["satisfied smile, half-lidded eyes"],
    "flirty": ["teasing smile"],
    "calm": ["serene expression"],
    "serious": ["serious expression"],
    "surprised": ["curious look"],
    "pleasure": ["aroused expression", "blissful expression"],
    "pain": ["pained expression"],
    "mouth": ["lips slightly parted", "mouth open", "biting her lower lip"],
    "breath": ["panting", "moaning", "gasping for air"],
    "eyes_open": ["relaxed brows"],
    "eyes_half": ["half-lidded eyes"],
    "eyes_closed": ["eyes closed", "eyes squeezed shut"],
    "gaze": ["looking at viewer", "looking away", "looking up at viewer",
             "looking down", "looking into the distance",
             "looking at something off-screen"],
}

GAZE_MALE = [
    "looking at him",
]

FACE_MERGED["gaze_male"] = GAZE_MALE

DIM_OF = {
    **{c: "expression" for c in ("smile_soft", "shy", "flirty", "afterglow",
                                 "calm", "serious", "surprised", "pleasure", "pain")},
    "mouth": "mouth", "breath": "mouth",
    "eyes_open": "eyes", "eyes_half": "eyes", "eyes_closed": "eyes",
    "gaze": "gaze", "gaze_male": "gaze",
}

FASHION_FACE = [
    "soft smile", "gentle smile", "confident smile", "smug smile",
    "embarrassed smile", "serene expression", "serious expression", "curious look",
]

FACE_CAT_BY_TIER = {
    "fashion": ["smile_soft", "calm", "serious", "surprised"],
    "tease":   ["smile_soft", "shy", "flirty", "calm", "mouth"],
    "exposed": ["shy", "flirty", "smile_soft", "mouth"],
    "sex":     ["pleasure", "pain", "mouth", "breath", "shy", "afterglow"],
}

FACE_BAN = ("tongue out", "eyes rolled up", "ahegao", "heart-shaped pupils",
            "heart pupils", "drooling", "saliva", "rolling eyes")

SCENE_BAN_BY_TIER = {
    "fashion": frozenset(),
    "tease":   frozenset(),
    "exposed": frozenset(),
    "sex":     PUBLIC_SCENES,
}

def pick_scene(rng, tier):
    ban = SCENE_BAN_BY_TIER.get(tier, frozenset())
    pool = []
    for cat, ws in SCENE_CATS.items():
        for w in ws:
            if w not in ban:
                pool.append((w, cat))
    if not pool:
        pool = [("bedroom", "INDOOR_HOME")]
    w, cat = rng.choice(pool)
    return w, cat, SCENE_PLACE.get(w, "indoor")

def pick_prop_v3(rng, tier, scene=None, p=0.30):
    if rng.random() > p:
        return ""
    cats = list(PROP_CATS)
    cat = rng.choice(cats)
    return rng.choice(PROP_CATS[cat]["items"])

FACE_DIM_ALLOW = {
    "fashion": {"eyes": ("eyes_open",)},
    "tease":   {"eyes": ("eyes_open", "eyes_half")},
    "exposed": {"eyes": ("eyes_open", "eyes_half")},
}

FACE_DIM_BAN = {
    "fashion": {
        "mouth": ("tongue out", "moaning", "panting", "gasping", "breathless",
                  "drooling", "biting her lower lip", "licking her lips"),
        "eyes":  ("teary eyes", "tears at the corners of her eyes",
                  "eyes squeezed shut", "brows drawn together"),
    },
    "tease": {
        "mouth": ("tongue out", "drooling", "gasping for air"),
        "eyes":  ("eyes squeezed shut",),
    },
}

def face_words(band, dim, cats, rng):
    ban = FACE_DIM_BAN.get(band, {}).get(dim, ())
    cands = []
    for c in cats:
        ws = [w for w in FACE_MERGED[c] if not any(b in w.lower() for b in ban)]
        if ws:
            cands.append((c, ws))
    if not cands:
        return "", ""
    c, ws = rng.choice(cands)
    return c, rng.choice(ws)
