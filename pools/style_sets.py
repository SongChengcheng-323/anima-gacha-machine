STYLE_SETS = {
    "minimal": {
        "cn": "极简",
        "palette": ["black", "white", "cream", "charcoal", "beige"],
        "tops": [
            "oversized white shirt", "fine-knit turtleneck", "cashmere crewneck sweater",
            "tailored blazer", "crisp cotton poplin shirt", "longline cardigan",
        ],
        "bottoms": [
            "straight-leg trousers", "high-waisted wide-leg pants", "tailored slacks",
            "dark denim jeans", "midi pencil skirt",
        ],
        "layers": [
            "layered over a fine turtleneck", "blazer worn open over the shirt",
            "cardigan layered over a simple tee",
        ],
        "acc": ["thin silver necklace", "small gold stud earrings", "minimalist watch",
                "slim leather belt", "structured shoulder bag"],
        "note": "黑白灰米，靠版型和面料质感，不靠花色",
    },
    "french": {
        "cn": "法式",
        "palette": ["camel", "cream", "off-white", "dusty rose", "sage green", "navy blue"],
        "tops": [
            "striped boat-neck top", "silk blouse with a soft drape", "fitted knit cardigan",
            "cropped tweed jacket", "wrap top with a deep neckline",
        ],
        "bottoms": [
            "high-waisted straight jeans", "corduroy straight pants", "A-line midi skirt",
            "suede mini skirt", "wide-leg linen trousers",
        ],
        "layers": [
            "tweed jacket over a fine knit", "knit vest layered over a shirt",
            "trench coat draped over the shoulders",
        ],
        "acc": ["silk scarf at the neck", "gold hoop earrings", "vintage shoulder bag",
                "thin gold chain", "beret"],
        "note": "低饱和大地色 + 莫兰迪色，叠穿但薄厚有序、不臃肿",
    },
    "commute": {
        "cn": "通勤",
        "palette": ["charcoal", "navy blue", "cream", "black", "camel", "grey"],
        "tops": [
            "crisp white shirt", "structured blazer", "silk blouse", "fine-gauge knit top",
            "tailored vest",
        ],
        "bottoms": [
            "high-waisted suit trousers", "pencil skirt", "pleated midi skirt",
            "straight-leg dress pants",
        ],
        "layers": [
            "blazer over a silk blouse", "knit vest under the blazer",
            "shirt with a fine turtleneck beneath",
        ],
        "acc": ["slim leather belt", "structured tote bag", "classic watch",
                "small gold earrings", "silk scarf"],
        "note": "利落线条 + 中性色，腰线要清楚",
    },
    "guochao": {
        "cn": "国潮",
        "palette": ["ink black", "cream", "wine red", "sage green", "jade green", "ivory"],
        "tops": [
            "mandarin-collar shirt", "frog-button silk top", "ink-wash print blouse",
            "embroidered stand-collar jacket", "hanfu-style wrapped top",
        ],
        "bottoms": [
            "modernized horse-face skirt", "wide-leg silk trousers", "high-waisted wrap skirt",
            "pleated long skirt",
        ],
        "layers": ["sheer outer robe over the top", "qipao-style top under a light jacket"],
        "acc": ["jade pendant", "tassel hairpin", "embroidered pouch", "hair stick"],
        "note": "盘扣 / 水墨印花 / 改良马面裙，飘逸感靠层次不靠印花堆叠",
    },
    "ballet": {
        "cn": "芭蕾",
        "palette": ["pastel pink", "cream", "ivory", "powder blue", "soft grey"],
        "tops": [
            "ribbed knit wrap top", "off-shoulder knit", "sheer mesh top", "fitted long-sleeve top",
        ],
        "bottoms": [
            "tulle midi skirt", "layered chiffon skirt", "pleated mini skirt",
            "sheer layered skirt",
        ],
        "layers": ["tulle skirt over leggings", "sheer top layered over a fitted camisole"],
        "acc": ["satin ribbon around the neck", "ballet flats", "ribbon hair tie",
                "pearl hair clip", "leg warmers"],
        "note": "纱 + 缎带 + 珍珠，柔和粉调；把芭蕾元素拆到基础款里",
    },
    "street": {
        "cn": "街头",
        "palette": ["black", "grey", "white", "charcoal", "denim blue"],
        "tops": [
            "oversized graphic hoodie", "cropped cargo jacket", "boxy tee",
            "varsity jacket", "windbreaker",
        ],
        "bottoms": [
            "cargo pants", "baggy wide-leg jeans", "track pants", "denim shorts",
        ],
        "layers": ["hoodie under a varsity jacket", "tee over a long-sleeve top",
                   "open shirt over a graphic tee"],
        "acc": ["beanie", "chunky sneakers", "crossbody bag", "layered chains",
                "canvas tote"],
        "note": "廓形大 + 运动感，层次靠长短不靠花色",
    },
    "mori": {
        "cn": "森系",
        "palette": ["sage green", "cream", "beige", "warm brown", "off-white"],
        "tops": [
            "loose linen shirt", "cotton peasant blouse", "chunky knit sweater",
            "smocked cotton top",
        ],
        "bottoms": [
            "long cotton skirt", "loose linen pants", "high-waisted wide skirt",
        ],
        "layers": ["knit cardigan over a linen dress", "shirt over a smocked top"],
        "acc": ["straw hat", "canvas shoulder bag", "small pendant necklace",
                "woven belt", "floral hair clip"],
        "note": "棉麻 + 大地色 + 宽松，天然材质感",
    },
    "vintage": {
        "cn": "复古",
        "palette": ["wine red", "mustard", "camel", "cream", "deep green"],
        "tops": [
            "polka-dot blouse", "silk blouse with a neck bow", "checked cropped jacket",
            "retro knit top", "puff-sleeve blouse",
        ],
        "bottoms": [
            "high-waisted plaid skirt", "corduroy A-line skirt", "wide-leg trousers",
            "pleated midi skirt",
        ],
        "layers": ["cropped jacket over a silk blouse with a neck bow"],
        "acc": ["gold statement earrings", "pearl necklace", "vintage clasp bag",
                "silk scarf tied at the neck"],
        "note": "波点 / 格纹 / 复古剪裁，金色配饰定调",
    },
}

SEASON_ACC = {
    "summer": ["straw hat", "woven straw bag", "sandals", "sunglasses"],
    "winter": ["wool beanie", "knit scarf", "snow boots", "long wool coat"],
    "autumn": ["beret", "leather ankle boots", "knit scarf", "trench coat"],
    "spring": ["light cardigan", "ballet flats", "canvas tote", "hair ribbon"],
}

ACC_MOOD = {
    "silver": {"items": ["thin silver necklace", "small silver stud earrings",
                         "silver chain bracelet", "minimalist silver watch"],
               "mood": "cool and understated"},
    "gold": {"items": ["gold hoop earrings", "layered gold chains",
                       "gold statement earrings", "delicate gold necklace"],
             "mood": "warm and retro"},
    "pearl": {"items": ["pearl hair clip", "pearl strand necklace", "pearl stud earrings"],
              "mood": "elegant and classic"},
}
