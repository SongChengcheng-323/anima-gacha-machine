import random

META = {
    "id": "wardrobe_pools",
    "cn": "装备池（四档）",
    "kind": "pool",
    "tier": "none",
    "parent": "wardrobe_route",
    "enabled": True,
    "desc": "装备词库：每件一行、带四档权重（0=该档不出现）；含暴露档的裸露占位词",
    "version": "v0.99.0",
    "refs": [],
}

TIERS = ("fashion", "tease", "exposed", "sex")
_W = lambda f, t, e, s: {"fashion": f, "tease": t, "exposed": e, "sex": s}

def _it(en, cn, w, slot, src="core", attr=False):
    return {"en": en, "cn": cn, "w": w, "slot": slot, "src": src, "attr": attr}

GEAR = {
    "chest": [
        _it('', '', _W(1.00, 1.00, 1.00, 1.00), 'chest'),
        _it('nipples visible through the fabric', '乳头隔衣顶出', _W(0.00, 1.00, 0.00, 0.00), 'chest'),
        _it('cleavage visible', '领口露沟', _W(0.00, 1.00, 0.00, 0.00), 'chest'),
        _it('bare breasts', '胸部裸露', _W(0.00, 0.00, 0.40, 0.50), 'chest'),
        _it('nipples visible', '乳头可见', _W(0.00, 0.00, 0.40, 0.50), 'chest'),
    ],
    "ears": [
        _it('stud earrings', '耳钉', _W(1.00, 0.60, 0.45, 0.45), 'ears'),
        _it('hoop earrings', '圈形耳环', _W(1.00, 0.60, 0.45, 0.45), 'ears'),
        _it('dangling earrings', '垂坠耳环', _W(1.00, 0.60, 0.45, 0.45), 'ears'),
    ],
    "eyes": [
        _it('sunglasses', '太阳镜', _W(1.00, 0.60, 0.45, 0.00), 'eyes'),
        _it('round glasses', '圆框眼镜', _W(1.00, 0.60, 0.45, 0.00), 'eyes'),
        _it('glasses', '眼镜', _W(1.00, 0.60, 0.45, 0.00), 'eyes'),
        _it('semi-rimless eyewear', '半框眼镜', _W(1.00, 0.60, 0.45, 0.00), 'eyes'),
        _it('under-rim eyewear', '下框眼镜', _W(1.00, 0.60, 0.45, 0.00), 'eyes'),
        _it('over-rim eyewear', '上框眼镜', _W(1.00, 0.60, 0.45, 0.00), 'eyes'),
        _it('thick-framed eyewear', '粗框眼镜', _W(1.00, 0.60, 0.45, 0.00), 'eyes'),
        _it('thin-framed eyewear', '细框眼镜', _W(1.00, 0.60, 0.45, 0.00), 'eyes'),
        _it('cat eye eyewear', '猫眼眼镜', _W(1.00, 0.60, 0.45, 0.00), 'eyes'),
        _it('heart-shaped eyewear', '心形眼镜', _W(1.00, 0.60, 0.45, 0.00), 'eyes'),
        _it('tinted eyewear', '有色镜片眼镜', _W(1.00, 0.60, 0.45, 0.00), 'eyes'),
        _it('pince-nez', '夹鼻眼镜', _W(1.00, 0.60, 0.45, 0.00), 'eyes'),
    ],
    "feet": [
        _it('loafers', '乐福鞋', _W(1.00, 0.60, 0.45, 0.00), 'feet'),
        _it('boots', '靴子', _W(1.00, 0.60, 0.45, 0.00), 'feet'),
        _it('heels', '高跟鞋', _W(1.00, 0.60, 0.45, 0.00), 'feet'),
        _it('sneakers', '运动鞋', _W(1.00, 0.60, 0.45, 0.00), 'feet'),
        _it('mary jane shoes', '玛丽珍鞋', _W(1.00, 0.60, 0.45, 0.00), 'feet'),
        _it('barefoot', '裸足', _W(0.00, 0.00, 0.40, 0.50), 'feet'),
    ],
    "hand_l": [
        _it('', '', _W(1.00, 1.00, 1.00, 1.00), 'hand_l'),
        _it('bare arm', '手臂裸露', _W(0.00, 0.00, 0.40, 0.50), 'hand_l'),
    ],
    "head": [
        _it('beret', '贝雷帽', _W(1.00, 0.60, 0.45, 0.00), 'head'),
        _it('newsboy cap', '报童帽', _W(1.00, 0.60, 0.45, 0.00), 'head'),
        _it('straw hat', '草帽', _W(1.00, 0.60, 0.45, 0.00), 'head'),
        _it('hair bow', '发带蝴蝶结', _W(1.00, 0.60, 0.45, 0.45), 'head'),
        _it('lace headband', '蕾丝发箍', _W(0.80, 0.48, 0.36, 0.36), 'head'),
        _it('bandana', '头巾', _W(1.00, 0.60, 0.45, 0.00), 'head'),
        _it('lace blindfold over her eyes', '蕾丝眼罩', _W(0.00, 0.00, 0.00, 0.00), 'head'),
    ],
    "leg_l": [
        _it('thighhighs', '过膝袜', _W(0.00, 0.90, 0.75, 0.75), 'leg_l'),
        _it('knee-high socks', '及膝袜', _W(0.90, 0.54, 0.41, 0.41), 'leg_l'),
        _it('over-knee socks', '过膝长袜', _W(0.90, 0.54, 0.41, 0.41), 'leg_l'),
        _it('pantyhose', '连裤袜', _W(0.90, 0.54, 0.41, 0.41), 'leg_l'),
        _it('bare legs', '腿裸露', _W(0.00, 0.00, 0.40, 0.50), 'leg_l'),
    ],
    "lower": [
        _it('pleated skirt', '百褶裙', _W(1.00, 0.60, 0.45, 0.70), 'lower'),
        _it('short shorts', '短裤', _W(0.90, 0.54, 0.41, 0.70), 'lower'),
        _it('jeans', '牛仔裤', _W(1.00, 0.60, 0.45, 0.00), 'lower'),
        _it('wide-leg pants', '阔腿裤', _W(1.00, 0.60, 0.45, 0.00), 'lower'),
        _it('pencil skirt', '包臀裙', _W(0.80, 0.48, 0.36, 0.55), 'lower'),
        _it('flowy long skirt', '长裙', _W(1.00, 0.60, 0.45, 0.45), 'lower'),
        _it('micro skirt', '超短裙', _W(0.00, 0.90, 0.75, 0.85), 'lower'),
        _it('towel around waist', '浴巾围腰', _W(0.00, 0.90, 0.75, 0.80), 'lower'),
        _it('bare lower body', '下半身裸露', _W(0.00, 0.00, 0.40, 0.50), 'lower'),
        _it('bare thighs', '大腿裸露', _W(0.00, 0.00, 0.40, 0.50), 'lower'),
    ],
    "neck": [
        _it('choker', '颈圈', _W(0.60, 0.36, 0.27, 0.27), 'neck'),
        _it('thin gold chain', '细金链', _W(1.00, 0.60, 0.45, 0.45), 'neck'),
        _it('silk scarf', '丝巾', _W(1.00, 0.60, 0.45, 0.00), 'neck'),
    ],
    "rear": [
        _it('panties', '内裤', _W(0.00, 0.90, 0.75, 0.65), 'rear'),
        _it('shorts', '平角内裤', _W(0.00, 0.00, 0.00, 0.00), 'rear'),
        _it('panty line visible', '透出内裤痕', _W(0.00, 1.00, 0.00, 0.00), 'rear'),
        _it('underwear visible above her waistband', '腰线露出内裤边', _W(0.00, 1.00, 0.00, 0.00), 'rear'),
        _it('bare buttocks', '臀部裸露', _W(0.00, 0.00, 0.40, 0.00), 'rear'),
        _it('pussy exposed', '外阴裸露', _W(0.00, 0.00, 0.40, 0.00), 'rear'),
        _it('anus visible', '肛门可见', _W(0.00, 0.00, 0.40, 0.00), 'rear'),
    ],
    "upper": [
        _it('hoodie', '连帽衫', _W(1.00, 0.60, 0.45, 0.00), 'upper'),
        _it('t-shirt', 'T恤', _W(1.00, 0.60, 0.45, 0.45), 'upper'),
        _it('turtleneck sweater', '高领毛衣', _W(1.00, 0.60, 0.45, 0.00), 'upper'),
        _it('blouse', '衬衫', _W(1.00, 0.60, 0.45, 0.45), 'upper'),
        _it('cardigan', '开衫', _W(1.00, 0.60, 0.45, 0.00), 'upper'),
        _it('crop top', '短上衣', _W(0.80, 0.48, 0.36, 0.36), 'upper'),
        _it('camisole', '吊带衫', _W(0.70, 0.42, 0.32, 0.32), 'upper'),
        _it('flannel shirt', '格子衬衫', _W(1.00, 0.60, 0.45, 0.00), 'upper'),
        _it('denim jacket', '牛仔外套', _W(1.00, 0.60, 0.45, 0.00), 'upper'),
        _it('oversized t-shirt only', '只穿大T恤', _W(1.00, 0.60, 0.45, 0.45), 'upper'),
        _it('towel wrapped around body', '浴巾裹身', _W(0.00, 0.90, 0.75, 0.80), 'upper'),
        _it('unbuttoned white dress shirt', '敞开的衬衫', _W(0.10, 0.06, 0.05, 0.05), 'upper'),
        _it('white lace lingerie set', '白蕾丝内衣', _W(0.00, 0.90, 0.75, 0.80), 'upper'),
        _it('black lace lingerie set', '黑蕾丝内衣', _W(0.00, 0.90, 0.75, 0.80), 'upper'),
        _it('white bikini', '白比基尼', _W(0.00, 0.90, 0.75, 0.80), 'upper'),
        _it('blue one-piece swimsuit', '蓝色连体泳衣', _W(1.00, 0.60, 0.45, 0.45), 'upper'),
        _it('bare upper body', '上半身裸露', _W(0.00, 0.00, 0.40, 0.50), 'upper'),
        _it('topless', '上身赤裸', _W(0.00, 0.00, 0.40, 0.50), 'upper'),
        _it('naked apron', '裸体围裙', _W(0.35, 0.85, 0.55, 0.85), 'upper'),
        _it('sailor school uniform', '水手服', _W(0.80, 0.85, 0.50, 0.80), 'upper'),
        _it('school uniform', '制服', _W(0.85, 0.80, 0.50, 0.75), 'upper'),
    ],
}

GEAR_EXT = {
    "ears": [
        _it('gold statement earrings', 'gold statement earrings', _W(1.00, 0.60, 0.45, 0.45), 'ears', src='set:vintage'),
        _it('pearl stud earrings', '珍珠耳钉', _W(1.00, 0.60, 0.45, 0.45), 'ears', src='log'),
        _it('gold hoop earrings', '金圈耳环', _W(1.00, 0.60, 0.45, 0.45), 'ears', src='log'),
        _it('silver hoop earrings', '银圈耳环', _W(1.00, 0.60, 0.45, 0.45), 'ears', src='log'),
        _it('amber drop earrings', '琥珀垂坠耳环', _W(1.00, 0.60, 0.45, 0.45), 'ears', src='log'),
        _it('jade drop earrings', '翡翠垂坠耳环', _W(1.00, 0.60, 0.45, 0.45), 'ears', src='log'),
        _it('delicate gold earrings', '精致金耳饰', _W(1.00, 0.60, 0.45, 0.45), 'ears', src='log'),
        _it('small gold stud earrings', '小金耳钉', _W(1.00, 0.60, 0.45, 0.45), 'ears', src='log'),
        _it('star-shaped dangling earrings', '星形垂坠耳环', _W(1.00, 0.60, 0.45, 0.45), 'ears', src='log'),
        _it('crescent-shaped dangling earrings', '月牙垂坠耳环', _W(1.00, 0.60, 0.45, 0.45), 'ears', src='log'),
        _it('crystal stud earrings', '水晶耳钉', _W(1.00, 0.60, 0.45, 0.45), 'ears', src='log'),
    ],
    "eyes": [
        _it('silver round glasses', '银框圆眼镜', _W(1.00, 0.60, 0.45, 0.00), 'eyes', src='log'),
        _it('black-framed glasses', '黑框眼镜', _W(1.00, 0.60, 0.45, 0.00), 'eyes', src='log'),
    ],
    "feet": [
        _it('leather loafers', 'leather loafers', _W(1.00, 0.60, 0.45, 0.00), 'feet', src='set:minimal'),
        _it('kitten heels', 'kitten heels', _W(1.00, 0.60, 0.45, 0.00), 'feet', src='set:minimal'),
        _it('mary jane shoes', 'mary jane shoes', _W(1.00, 0.60, 0.45, 0.00), 'feet', src='set:guochao'),
        _it('chunky sneakers', 'chunky sneakers', _W(1.00, 0.60, 0.45, 0.00), 'feet', src='set:street'),
        _it('chunky boots', 'chunky boots', _W(1.00, 0.60, 0.45, 0.00), 'feet', src='set:street'),
        _it('canvas sneakers', 'canvas sneakers', _W(1.00, 0.60, 0.45, 0.00), 'feet', src='set:mori'),
        _it('ankle boots', '短靴', _W(1.00, 0.60, 0.45, 0.00), 'feet', src='log'),
        _it('strappy heels', '绑带高跟', _W(0.90, 0.54, 0.41, 0.00), 'feet', src='log'),
    ],
    "hand_l": [
        _it('minimalist watch', 'minimalist watch', _W(1.00, 0.60, 0.45, 0.00), 'hand_l', src='set:minimal'),
        _it('structured shoulder bag', 'structured shoulder bag', _W(1.00, 0.60, 0.45, 0.00), 'hand_l', src='set:minimal'),
        _it('leather tote bag', 'leather tote bag', _W(1.00, 0.60, 0.45, 0.00), 'hand_l', src='set:minimal'),
        _it('vintage shoulder bag', 'vintage shoulder bag', _W(1.00, 0.60, 0.45, 0.00), 'hand_l', src='set:french'),
        _it('classic watch', 'classic watch', _W(1.00, 0.60, 0.45, 0.00), 'hand_l', src='set:commute'),
        _it('structured tote bag', 'structured tote bag', _W(1.00, 0.60, 0.45, 0.00), 'hand_l', src='set:commute'),
        _it('embroidered pouch', 'embroidered pouch', _W(1.00, 0.60, 0.45, 0.00), 'hand_l', src='set:guochao'),
        _it('small crossbody bag', 'small crossbody bag', _W(1.00, 0.60, 0.45, 0.00), 'hand_l', src='set:ballet'),
        _it('canvas tote', 'canvas tote', _W(1.00, 0.60, 0.45, 0.00), 'hand_l', src='set:street'),
        _it('crossbody bag', 'crossbody bag', _W(1.00, 0.60, 0.45, 0.00), 'hand_l', src='set:street'),
        _it('canvas shoulder bag', 'canvas shoulder bag', _W(1.00, 0.60, 0.45, 0.00), 'hand_l', src='set:mori'),
        _it('vintage clasp bag', 'vintage clasp bag', _W(1.00, 0.60, 0.45, 0.00), 'hand_l', src='set:vintage'),
    ],
    "head": [
        _it('beret', 'beret', _W(1.00, 0.60, 0.45, 0.00), 'head', src='set:french'),
        _it('silk headband', 'silk headband', _W(1.00, 0.60, 0.45, 0.45), 'head', src='set:french'),
        _it('flower hairpin', 'flower hairpin', _W(1.00, 0.60, 0.45, 0.45), 'head', src='set:guochao'),
        _it('hair ribbon', 'hair ribbon', _W(1.00, 0.60, 0.45, 0.45), 'head', src='set:guochao'),
        _it('ribbon hair tie', 'ribbon hair tie', _W(1.00, 0.60, 0.45, 0.45), 'head', src='set:ballet'),
        _it('pearl hair clip', 'pearl hair clip', _W(1.00, 0.60, 0.45, 0.45), 'head', src='set:ballet'),
        _it('knit beanie', 'knit beanie', _W(1.00, 0.60, 0.45, 0.00), 'head', src='set:street'),
        _it('straw hat', 'straw hat', _W(1.00, 0.60, 0.45, 0.00), 'head', src='set:mori'),
        _it('wool beret', 'wool beret', _W(1.00, 0.60, 0.45, 0.00), 'head', src='set:mori'),
    ],
    "leg_l": [
        _it('sheer pantyhose', 'sheer pantyhose', _W(1.00, 0.60, 0.45, 0.60), 'leg_l', src='set:minimal'),
        _it('patterned tights', 'patterned tights', _W(1.00, 0.60, 0.45, 0.45), 'leg_l', src='set:french'),
        _it('over-knee socks', 'over-knee socks', _W(1.00, 0.60, 0.45, 0.45), 'leg_l', src='set:guochao'),
        _it('lace-trimmed thighhighs', 'lace-trimmed thighhighs', _W(0.00, 0.90, 0.75, 0.75), 'leg_l', src='set:ballet'),
        _it('ribbed knee socks', 'ribbed knee socks', _W(1.00, 0.60, 0.45, 0.45), 'leg_l', src='set:ballet'),
    ],
    "lower": [
        _it('straight-leg trousers', 'straight-leg trousers', _W(1.00, 0.60, 0.45, 0.00), 'lower', src='set:minimal'),
        _it('high-waisted wide-leg pants', 'high-waisted wide-leg pants', _W(1.00, 0.60, 0.45, 0.00), 'lower', src='set:minimal'),
        _it('midi pencil skirt', 'midi pencil skirt', _W(1.00, 0.60, 0.45, 0.55), 'lower', src='set:minimal'),
        _it('high-waisted straight jeans', 'high-waisted straight jeans', _W(1.00, 0.60, 0.45, 0.00), 'lower', src='set:french'),
        _it('A-line midi skirt', 'A-line midi skirt', _W(1.00, 0.60, 0.45, 0.55), 'lower', src='set:french'),
        _it('wide-leg linen trousers', 'wide-leg linen trousers', _W(1.00, 0.60, 0.45, 0.00), 'lower', src='set:french'),
        _it('high-waisted suit trousers', 'high-waisted suit trousers', _W(1.00, 0.60, 0.45, 0.00), 'lower', src='set:commute'),
        _it('pencil skirt', 'pencil skirt', _W(0.80, 0.48, 0.36, 0.55), 'lower', src='set:commute'),
        _it('straight-leg dress pants', 'straight-leg dress pants', _W(1.00, 0.60, 0.45, 0.00), 'lower', src='set:commute'),
        _it('modernized horse-face skirt', 'modernized horse-face skirt', _W(1.00, 0.60, 0.45, 0.45), 'lower', src='set:guochao'),
        _it('wide-leg silk trousers', 'wide-leg silk trousers', _W(1.00, 0.60, 0.45, 0.00), 'lower', src='set:guochao'),
        _it('pleated long skirt', 'pleated long skirt', _W(1.00, 0.60, 0.45, 0.55), 'lower', src='set:guochao'),
        _it('tulle midi skirt', 'tulle midi skirt', _W(1.00, 0.60, 0.45, 0.60), 'lower', src='set:ballet'),
        _it('layered chiffon skirt', 'layered chiffon skirt', _W(1.00, 0.60, 0.45, 0.60), 'lower', src='set:ballet'),
        _it('pleated mini skirt', 'pleated mini skirt', _W(1.00, 0.60, 0.45, 0.80), 'lower', src='set:ballet'),
        _it('cargo pants', 'cargo pants', _W(1.00, 0.60, 0.45, 0.00), 'lower', src='set:street'),
        _it('baggy wide-leg jeans', 'baggy wide-leg jeans', _W(1.00, 0.60, 0.45, 0.00), 'lower', src='set:street'),
        _it('denim shorts', 'denim shorts', _W(1.00, 0.60, 0.45, 0.65), 'lower', src='set:street'),
        _it('long cotton skirt', 'long cotton skirt', _W(1.00, 0.60, 0.45, 0.45), 'lower', src='set:mori'),
        _it('loose linen pants', 'loose linen pants', _W(1.00, 0.60, 0.45, 0.00), 'lower', src='set:mori'),
        _it('high-waisted wide skirt', 'high-waisted wide skirt', _W(1.00, 0.60, 0.45, 0.45), 'lower', src='set:mori'),
        _it('high-waisted plaid skirt', 'high-waisted plaid skirt', _W(1.00, 0.60, 0.45, 0.55), 'lower', src='set:vintage'),
        _it('corduroy A-line skirt', 'corduroy A-line skirt', _W(1.00, 0.60, 0.45, 0.55), 'lower', src='set:vintage'),
        _it('wide-leg trousers', 'wide-leg trousers', _W(1.00, 0.60, 0.45, 0.00), 'lower', src='set:vintage'),
        _it('slim pants', '修身长裤', _W(1.00, 0.60, 0.45, 0.00), 'lower', src='log'),
        _it('flared skirt', '喇叭裙', _W(1.00, 0.60, 0.45, 0.60), 'lower', src='log'),
    ],
    "neck": [
        _it('thin silver necklace', 'thin silver necklace', _W(1.00, 0.60, 0.45, 0.45), 'neck', src='set:minimal'),
        _it('fine gold chain necklace', 'fine gold chain necklace', _W(1.00, 0.60, 0.45, 0.45), 'neck', src='set:minimal'),
        _it('thin gold chain', 'thin gold chain', _W(1.00, 0.60, 0.45, 0.45), 'neck', src='set:french'),
        _it('silk scarf', 'silk scarf', _W(1.00, 0.60, 0.45, 0.00), 'neck', src='set:commute'),
        _it('delicate pendant necklace', 'delicate pendant necklace', _W(1.00, 0.60, 0.45, 0.45), 'neck', src='set:guochao'),
        _it('ribbon choker', 'ribbon choker', _W(1.00, 0.60, 0.45, 0.45), 'neck', src='set:ballet'),
        _it('layered chains', 'layered chains', _W(1.00, 0.60, 0.45, 0.45), 'neck', src='set:street'),
        _it('small pendant necklace', 'small pendant necklace', _W(1.00, 0.60, 0.45, 0.45), 'neck', src='set:mori'),
        _it('pearl choker', 'pearl choker', _W(1.00, 0.60, 0.45, 0.45), 'neck', src='set:vintage'),
        _it('fine necklace', '细项链', _W(1.00, 0.60, 0.45, 0.45), 'neck', src='log'),
    ],
    "rear": [
        _it('white cotton panties', '白色棉内裤', _W(0.00, 0.90, 0.75, 0.65), 'rear', src='log'),
        _it('lace-trimmed black shorts', '蕾丝边短裤', _W(0.00, 0.00, 0.00, 0.00), 'rear', src='log'),
    ],
    "upper": [
        _it('oversized white shirt', 'oversized white shirt', _W(1.00, 0.60, 0.45, 0.00), 'upper', src='set:minimal'),
        _it('fine-knit turtleneck', 'fine-knit turtleneck', _W(1.00, 0.60, 0.45, 0.00), 'upper', src='set:minimal'),
        _it('cashmere crewneck sweater', 'cashmere crewneck sweater', _W(1.00, 0.60, 0.45, 0.00), 'upper', src='set:minimal'),
        _it('longline cardigan', 'longline cardigan', _W(1.00, 0.60, 0.45, 0.00), 'upper', src='set:minimal'),
        _it('striped boat-neck top', 'striped boat-neck top', _W(1.00, 0.60, 0.45, 0.45), 'upper', src='set:french'),
        _it('fitted knit cardigan', 'fitted knit cardigan', _W(1.00, 0.60, 0.45, 0.00), 'upper', src='set:french'),
        _it('cropped tweed jacket', 'cropped tweed jacket', _W(1.00, 0.60, 0.45, 0.00), 'upper', src='set:french'),
        _it('crisp white shirt', 'crisp white shirt', _W(1.00, 0.60, 0.45, 0.00), 'upper', src='set:commute'),
        _it('structured blazer', 'structured blazer', _W(1.00, 0.60, 0.45, 0.00), 'upper', src='set:commute'),
        _it('silk blouse', 'silk blouse', _W(1.00, 0.60, 0.45, 0.45), 'upper', src='set:commute'),
        _it('tailored vest', 'tailored vest', _W(1.00, 0.60, 0.45, 0.00), 'upper', src='set:commute'),
        _it('mandarin-collar shirt', 'mandarin-collar shirt', _W(1.00, 0.60, 0.45, 0.00), 'upper', src='set:guochao'),
        _it('frog-button silk top', 'frog-button silk top', _W(1.00, 0.60, 0.45, 0.45), 'upper', src='set:guochao'),
        _it('ink-wash print blouse', 'ink-wash print blouse', _W(1.00, 0.60, 0.45, 0.45), 'upper', src='set:guochao'),
        _it('hanfu-style wrapped top', 'hanfu-style wrapped top', _W(1.00, 0.60, 0.45, 0.45), 'upper', src='set:guochao'),
        _it('ribbed knit wrap top', 'ribbed knit wrap top', _W(1.00, 0.60, 0.45, 0.45), 'upper', src='set:ballet'),
        _it('off-shoulder knit', 'off-shoulder knit', _W(1.00, 0.60, 0.45, 0.45), 'upper', src='set:ballet'),
        _it('fitted long-sleeve top', 'fitted long-sleeve top', _W(1.00, 0.60, 0.45, 0.45), 'upper', src='set:ballet'),
        _it('oversized graphic hoodie', 'oversized graphic hoodie', _W(1.00, 0.60, 0.45, 0.00), 'upper', src='set:street'),
        _it('cropped cargo jacket', 'cropped cargo jacket', _W(1.00, 0.60, 0.45, 0.00), 'upper', src='set:street'),
        _it('boxy tee', 'boxy tee', _W(1.00, 0.60, 0.45, 0.45), 'upper', src='set:street'),
        _it('varsity jacket', 'varsity jacket', _W(1.00, 0.60, 0.45, 0.00), 'upper', src='set:street'),
        _it('loose linen shirt', 'loose linen shirt', _W(1.00, 0.60, 0.45, 0.00), 'upper', src='set:mori'),
        _it('cotton peasant blouse', 'cotton peasant blouse', _W(1.00, 0.60, 0.45, 0.45), 'upper', src='set:mori'),
        _it('chunky knit sweater', 'chunky knit sweater', _W(1.00, 0.60, 0.45, 0.00), 'upper', src='set:mori'),
        _it('polka-dot blouse', 'polka-dot blouse', _W(1.00, 0.60, 0.45, 0.45), 'upper', src='set:vintage'),
        _it('checked cropped jacket', 'checked cropped jacket', _W(1.00, 0.60, 0.45, 0.00), 'upper', src='set:vintage'),
        _it('puff-sleeve blouse', 'puff-sleeve blouse', _W(1.00, 0.60, 0.45, 0.45), 'upper', src='set:vintage'),
        _it('sleeveless', '无袖', _W(1.00, 1.00, 0.70, 0.60), 'upper', src='log', attr=True),
        _it('detached-sleeve', '袖套', _W(1.00, 1.00, 0.50, 0.50), 'upper', src='log', attr=True),
        _it('long-sleeved', '长袖', _W(1.00, 1.00, 0.50, 0.50), 'upper', src='log', attr=True),
        _it('short-sleeved', '短袖', _W(1.00, 1.00, 0.55, 0.55), 'upper', src='log', attr=True),
        _it('off-shoulder', '露肩', _W(1.00, 1.00, 0.60, 0.55), 'upper', src='log', attr=True),
    ],
}
SET_EXTRA = {
    "minimal": {
        "upper": [
            [
                "boxy white tee",
                "方版白T"
            ],
            [
                "silk camisole top",
                "真丝吊带"
            ],
            [
                "poplin shirt",
                "府绸衬衫"
            ],
            [
                "bateau neck top",
                "一字领上衣"
            ],
            [
                "ribbed tank top",
                "罗纹背心"
            ],
            [
                "mohair cardigan",
                "马海毛开衫"
            ],
            [
                "merino wool sweater",
                "美利奴毛衣"
            ],
            [
                "silk shell top",
                "真丝无袖上衣"
            ]
        ],
        "lower": [
            [
                "tapered trousers",
                "锥形西裤"
            ],
            [
                "bias-cut satin skirt",
                "斜裁缎面裙"
            ],
            [
                "column maxi skirt",
                "直筒长裙"
            ],
            [
                "straight-leg jeans",
                "直筒牛仔裤"
            ],
            [
                "wrap midi skirt",
                "一片式中长裙"
            ],
            [
                "tailored shorts",
                "西装短裤"
            ]
        ],
        "leg_l": [
            [
                "opaque black tights",
                "不透明黑丝袜"
            ],
            [
                "ribbed tights",
                "罗纹连裤袜"
            ],
            [
                "seamless tights",
                "无缝连裤袜"
            ]
        ],
        "feet": [
            [
                "pointed-toe flats",
                "尖头平底鞋"
            ],
            [
                "minimal white sneakers",
                "小白鞋"
            ],
            [
                "slingback pumps",
                "后空高跟鞋"
            ],
            [
                "suede mules",
                "麂皮拖鞋"
            ],
            [
                "ballet flats",
                "芭蕾平底鞋"
            ],
            [
                "square-toe boots",
                "方头短靴"
            ]
        ],
        "neck": [
            [
                "delicate bar necklace",
                "细条项链"
            ],
            [
                "simple pearl pendant",
                "简约珍珠吊坠"
            ],
            [
                "thin leather choker",
                "细皮颈圈"
            ]
        ],
        "hand_l": [
            [
                "minimal leather backpack",
                "简约皮双肩包"
            ],
            [
                "structured pouch",
                "结构感手拿包"
            ]
        ],
        "head": [
            [
                "thin headband",
                "细发箍"
            ],
            [
                "silk hair scarf",
                "真丝发巾"
            ]
        ],
        "ears": [
            [
                "small silver studs",
                "小银耳钉"
            ],
            [
                "thin gold hoops",
                "细金圈耳环"
            ]
        ]
    },
    "french": {
        "upper": [
            [
                "breton striped top",
                "布列塔尼条纹上衣"
            ],
            [
                "lace-trimmed camisole",
                "蕾丝边吊带"
            ],
            [
                "silk blouse",
                "真丝衬衫"
            ],
            [
                "wrap blouse",
                "系带衬衫"
            ],
            [
                "ruffled blouse",
                "荷叶边衬衫"
            ],
            [
                "cropped cardigan",
                "短款开衫"
            ],
            [
                "trench coat",
                "风衣"
            ]
        ],
        "lower": [
            [
                "cropped jeans",
                "九分牛仔裤"
            ],
            [
                "pleated midi skirt",
                "百褶中长裙"
            ],
            [
                "gathered waist skirt",
                "抽褶半裙"
            ],
            [
                "linen shorts",
                "亚麻短裤"
            ],
            [
                "tailored shorts",
                "西装短裤"
            ]
        ],
        "leg_l": [
            [
                "sheer black tights",
                "黑色透丝袜"
            ],
            [
                "dotted tights",
                "波点连裤袜"
            ],
            [
                "lace-top tights",
                "蕾丝边长袜"
            ]
        ],
        "feet": [
            [
                "ballet flats",
                "芭蕾平底鞋"
            ],
            [
                "slingback kitten heels",
                "后空猫跟鞋"
            ],
            [
                "woven espadrilles",
                "编织麻底鞋"
            ],
            [
                "ankle strap heels",
                "踝带高跟"
            ]
        ],
        "head": [
            [
                "tortoiseshell hair clip",
                "玳瑁发夹"
            ],
            [
                "ribbon headband",
                "缎带发箍"
            ],
            [
                "silk scarf headband",
                "丝巾发箍"
            ]
        ],
        "neck": [
            [
                "gold locket",
                "金质吊坠盒"
            ],
            [
                "silk neck scarf",
                "颈部丝巾"
            ],
            [
                "pearl strand",
                "珍珠串链"
            ]
        ],
        "hand_l": [
            [
                "woven basket bag",
                "编织篮包"
            ],
            [
                "structured leather bag",
                "结构皮包"
            ],
            [
                "quilted shoulder bag",
                "绗缝单肩包"
            ]
        ],
        "ears": [
            [
                "small gold hoops",
                "小金圈耳环"
            ],
            [
                "pearl drop earrings",
                "珍珠垂坠耳环"
            ]
        ]
    },
    "commute": {
        "upper": [
            [
                "button-down shirt",
                "系扣衬衫"
            ],
            [
                "knit polo",
                "针织polo"
            ],
            [
                "fitted blazer",
                "修身西装外套"
            ],
            [
                "double-breasted blazer",
                "双排扣西装"
            ],
            [
                "turtleneck top",
                "高领上衣"
            ],
            [
                "silk shell blouse",
                "真丝无袖衬衫"
            ]
        ],
        "lower": [
            [
                "wide-leg dress trousers",
                "阔腿西裤"
            ],
            [
                "pleated suit skirt",
                "百褶西装裙"
            ],
            [
                "tapered suit pants",
                "锥形西装裤"
            ],
            [
                "wrap pencil skirt",
                "围裹铅笔裙"
            ]
        ],
        "leg_l": [
            [
                "sheer nude tights",
                "裸色透丝袜"
            ],
            [
                "opaque tights",
                "不透明连裤袜"
            ]
        ],
        "feet": [
            [
                "pointed pumps",
                "尖头高跟鞋"
            ],
            [
                "heeled loafers",
                "粗跟乐福鞋"
            ],
            [
                "square-toe flats",
                "方头平底鞋"
            ],
            [
                "ankle boots",
                "踝靴"
            ]
        ],
        "neck": [
            [
                "thin chain necklace",
                "细链项链"
            ],
            [
                "small stud pendant",
                "小吊坠"
            ],
            [
                "leather choker",
                "皮颈圈"
            ]
        ],
        "hand_l": [
            [
                "structured satchel",
                "结构手提包"
            ],
            [
                "leather briefcase",
                "皮质公文包"
            ],
            [
                "structured handbag",
                "结构手袋"
            ]
        ],
        "head": [
            [
                "silk headband",
                "真丝发箍"
            ],
            [
                "thin barrette",
                "细发夹"
            ]
        ],
        "ears": [
            [
                "small gold studs",
                "小金耳钉"
            ],
            [
                "thin silver hoops",
                "细银圈耳环"
            ]
        ]
    },
    "guochao": {
        "upper": [
            [
                "qipao-style top",
                "旗袍式上衣"
            ],
            [
                "lace-up hanfu top",
                "系带汉服上衣"
            ],
            [
                "bamboo print blouse",
                "竹纹衬衫"
            ],
            [
                "silk wrap blouse",
                "真丝系带上衣"
            ],
            [
                "embroidered linen top",
                "绣花亚麻上衣"
            ],
            [
                "mandarin collar top",
                "立领上衣"
            ]
        ],
        "lower": [
            [
                "qipao skirt",
                "旗袍裙"
            ],
            [
                "pleated wrap skirt",
                "百褶围裹裙"
            ],
            [
                "embroidered skirt",
                "刺绣半裙"
            ],
            [
                "wide-leg cropped pants",
                "阔腿九分裤"
            ],
            [
                "layered hanfu skirt",
                "层叠汉服裙"
            ],
            [
                "silk long skirt",
                "真丝长裙"
            ]
        ],
        "leg_l": [
            [
                "embroidered socks",
                "绣花袜"
            ],
            [
                "silk knee socks",
                "真丝及膝袜"
            ]
        ],
        "feet": [
            [
                "embroidered flats",
                "绣花平底鞋"
            ],
            [
                "platform sandals",
                "厚底凉鞋"
            ],
            [
                "cloth shoes",
                "布鞋"
            ]
        ],
        "head": [
            [
                "jade hairpin",
                "玉簪"
            ],
            [
                "tassel hairpin",
                "流苏发簪"
            ],
            [
                "pearl hair comb",
                "珍珠发梳"
            ],
            [
                "silk hair band",
                "真丝发带"
            ]
        ],
        "neck": [
            [
                "jade pendant",
                "玉坠"
            ],
            [
                "tassel necklace",
                "流苏项链"
            ],
            [
                "red string necklace",
                "红绳项链"
            ],
            [
                "beaded necklace",
                "串珠项链"
            ]
        ],
        "hand_l": [
            [
                "hand fan",
                "团扇"
            ],
            [
                "silk pouch",
                "真丝香囊"
            ],
            [
                "beaded bag",
                "串珠包"
            ],
            [
                "embroidered handbag",
                "绣花手袋"
            ]
        ],
        "ears": [
            [
                "jade drop earrings",
                "玉坠耳环"
            ],
            [
                "tassel earrings",
                "流苏耳环"
            ]
        ]
    },
    "ballet": {
        "upper": [
            [
                "lace-trimmed knit top",
                "蕾丝边针织上衣"
            ],
            [
                "sheer chiffon blouse",
                "雪纺纱上衣"
            ],
            [
                "corset top",
                "束腰上衣"
            ],
            [
                "ballet wrap top",
                "芭蕾围裹上衣"
            ],
            [
                "camisole with lace",
                "蕾丝吊带"
            ],
            [
                "puff-sleeve knit top",
                "泡泡袖针织上衣"
            ]
        ],
        "lower": [
            [
                "tulle tiered skirt",
                "层叠纱裙"
            ],
            [
                "wrap mini skirt",
                "围裹短裙"
            ],
            [
                "chiffon maxi skirt",
                "雪纺长裙"
            ],
            [
                "satin gathered skirt",
                "缎面抽褶裙"
            ],
            [
                "layered tulle skirt",
                "多层纱裙"
            ]
        ],
        "leg_l": [
            [
                "white lace thighhighs",
                "白色蕾丝过膝袜"
            ],
            [
                "crossover leg warmers",
                "交叉腿套"
            ],
            [
                "opaque pink tights",
                "不透粉丝袜"
            ],
            [
                "ribbed knee socks",
                "罗纹及膝袜"
            ]
        ],
        "feet": [
            [
                "ballet slippers",
                "芭蕾软鞋"
            ],
            [
                "ribbon ballet flats",
                "缎带芭蕾平底鞋"
            ],
            [
                "patent mary janes",
                "漆皮玛丽珍"
            ]
        ],
        "head": [
            [
                "wide ribbon headband",
                "宽缎带发箍"
            ],
            [
                "pearl ribbon",
                "珍珠缎带"
            ],
            [
                "tulle bow",
                "纱质蝴蝶结"
            ],
            [
                "lace headband",
                "蕾丝发箍"
            ]
        ],
        "neck": [
            [
                "pearl ribbon choker",
                "珍珠缎带颈圈"
            ],
            [
                "cameo pendant",
                "浮雕吊坠"
            ],
            [
                "ribbon neck bow",
                "颈间缎带结"
            ]
        ],
        "hand_l": [
            [
                "small quilted bag",
                "小绗缝包"
            ],
            [
                "satin pouch",
                "缎面手拿包"
            ],
            [
                "mini handbag",
                "迷你手袋"
            ]
        ],
        "ears": [
            [
                "pearl drop earrings",
                "珍珠垂坠耳环"
            ],
            [
                "ribbon earrings",
                "缎带耳饰"
            ]
        ]
    },
    "street": {
        "upper": [
            [
                "oversized bomber jacket",
                "宽松飞行夹克"
            ],
            [
                "zip-up hoodie",
                "拉链连帽衫"
            ],
            [
                "cropped puffer vest",
                "短款羽绒马甲"
            ],
            [
                "sports jersey",
                "运动球衣"
            ],
            [
                "graphic band tee",
                "印花乐队T"
            ],
            [
                "denim trucker jacket",
                "牛仔夹克"
            ],
            [
                "track jacket",
                "运动外套"
            ]
        ],
        "lower": [
            [
                "jogger pants",
                "束脚裤"
            ],
            [
                "parachute pants",
                "降落伞裤"
            ],
            [
                "cargo skirt",
                "工装裙"
            ],
            [
                "ribbed bike shorts",
                "罗纹骑行短裤"
            ],
            [
                "ripped jeans",
                "破洞牛仔裤"
            ],
            [
                "wide-leg track pants",
                "阔腿运动裤"
            ]
        ],
        "leg_l": [
            [
                "crew socks",
                "中筒袜"
            ],
            [
                "sporty striped socks",
                "运动条纹袜"
            ],
            [
                "ribbed ankle socks",
                "罗纹短袜"
            ]
        ],
        "feet": [
            [
                "chunky platform sneakers",
                "厚底运动鞋"
            ],
            [
                "high-top sneakers",
                "高帮运动鞋"
            ],
            [
                "dad sneakers",
                "老爹鞋"
            ],
            [
                "platform boots",
                "厚底靴"
            ]
        ],
        "head": [
            [
                "snapback cap",
                "棒球帽"
            ],
            [
                "bucket hat",
                "渔夫帽"
            ],
            [
                "sporty headband",
                "运动发带"
            ]
        ],
        "neck": [
            [
                "chain necklace",
                "链条项链"
            ],
            [
                "pendant chain",
                "吊坠链"
            ],
            [
                "choker",
                "颈圈"
            ]
        ],
        "hand_l": [
            [
                "bumbag",
                "腰包"
            ],
            [
                "mini backpack",
                "迷你双肩包"
            ],
            [
                "drawstring bag",
                "束口包"
            ],
            [
                "duffel bag",
                "圆筒包"
            ]
        ],
        "ears": [
            [
                "silver hoops",
                "银圈耳环"
            ],
            [
                "stud earring set",
                "耳钉套装"
            ]
        ]
    },
    "mori": {
        "upper": [
            [
                "oversized knit cardigan",
                "宽松针织开衫"
            ],
            [
                "cotton gauze blouse",
                "棉纱上衣"
            ],
            [
                "embroidered linen top",
                "绣花亚麻上衣"
            ],
            [
                "crochet vest",
                "钩花马甲"
            ],
            [
                "flannel shirt",
                "法兰绒衬衫"
            ],
            [
                "layered long shirt",
                "层叠长衬衫"
            ]
        ],
        "lower": [
            [
                "gathered cotton skirt",
                "抽褶棉裙"
            ],
            [
                "tiered prairie skirt",
                "多层田园长裙"
            ],
            [
                "linen wide pants",
                "亚麻阔腿裤"
            ],
            [
                "cropped trousers",
                "九分裤"
            ],
            [
                "patchwork skirt",
                "拼布半裙"
            ]
        ],
        "leg_l": [
            [
                "wool knee socks",
                "羊毛及膝袜"
            ],
            [
                "ribbed knit socks",
                "罗纹针织袜"
            ],
            [
                "plain cotton tights",
                "素色棉连裤袜"
            ]
        ],
        "feet": [
            [
                "suede boots",
                "麂皮靴"
            ],
            [
                "woven sandals",
                "编织凉鞋"
            ],
            [
                "canvas slip-ons",
                "帆布一脚蹬"
            ],
            [
                "leather ankle boots",
                "皮短靴"
            ]
        ],
        "head": [
            [
                "crochet hat",
                "钩花帽"
            ],
            [
                "linen headscarf",
                "亚麻头巾"
            ],
            [
                "felt hat",
                "毛毡帽"
            ],
            [
                "flower hair wreath",
                "花环头饰"
            ]
        ],
        "neck": [
            [
                "wooden bead necklace",
                "木珠项链"
            ],
            [
                "linen scarf",
                "亚麻围巾"
            ],
            [
                "dried flower pendant",
                "干花吊坠"
            ]
        ],
        "hand_l": [
            [
                "woven basket bag",
                "编织篮包"
            ],
            [
                "canvas sling bag",
                "帆布斜挎包"
            ],
            [
                "macrame bag",
                "绳编包"
            ],
            [
                "leather satchel",
                "皮挎包"
            ]
        ],
        "ears": [
            [
                "wooden earrings",
                "木质耳环"
            ],
            [
                "small brass hoops",
                "小黄铜圈耳环"
            ]
        ]
    },
    "vintage": {
        "upper": [
            [
                "pussy-bow blouse",
                "蝴蝶结领衬衫"
            ],
            [
                "polka dot top",
                "波点上衣"
            ],
            [
                "houndstooth jacket",
                "千鸟格外套"
            ],
            [
                "ribbon blouse",
                "缎带衬衫"
            ],
            [
                "puff-sleeve top",
                "泡泡袖上衣"
            ],
            [
                "cropped knit cardigan",
                "短款针织开衫"
            ]
        ],
        "lower": [
            [
                "circle skirt",
                "伞裙"
            ],
            [
                "houndstooth skirt",
                "千鸟格半裙"
            ],
            [
                "pleated plaid skirt",
                "格纹百褶裙"
            ],
            [
                "high-waisted slacks",
                "高腰长裤"
            ],
            [
                "button-front skirt",
                "前排扣半裙"
            ]
        ],
        "leg_l": [
            [
                "seam tights",
                "背缝丝袜"
            ],
            [
                "dotted tights",
                "波点连裤袜"
            ],
            [
                "patterned pantyhose",
                "花纹连裤袜"
            ]
        ],
        "feet": [
            [
                "t-strap heels",
                "丁字带高跟鞋"
            ],
            [
                "mary jane pumps",
                "玛丽珍高跟"
            ],
            [
                "oxford shoes",
                "牛津鞋"
            ],
            [
                "vintage boots",
                "复古靴"
            ]
        ],
        "head": [
            [
                "pillbox hat",
                "药盒帽"
            ],
            [
                "velvet bow",
                "天鹅绒蝴蝶结"
            ],
            [
                "pearl headpiece",
                "珍珠发饰"
            ]
        ],
        "neck": [
            [
                "pearl necklace",
                "珍珠项链"
            ],
            [
                "cameo brooch",
                "浮雕胸针"
            ],
            [
                "silk neck scarf",
                "颈部丝巾"
            ]
        ],
        "hand_l": [
            [
                "carpet bag",
                "复古手提包"
            ],
            [
                "framed handbag",
                "框式手袋"
            ],
            [
                "beaded clutch",
                "珠绣手拿包"
            ]
        ],
        "ears": [
            [
                "pearl earrings",
                "珍珠耳环"
            ],
            [
                "cameo earrings",
                "浮雕耳环"
            ]
        ]
    }
}

VACANT_SLOTS = ("head", "eyes", "ears", "neck", "waist")
VACANT_P = 1.0 / 3.0
VACANT_P_BY_SLOT = {"eyes": 0.5}

_SEX_NEVER = (
    "bag", "clutch", "pouch", "satchel", "briefcase", "backpack", "bumbag", "hand fan",
    "boots", "heels", "sneakers", "flats", "mules", "pumps", "sandals", "espadrilles",
    "slip-ons", "loafers", "oxford", "mary janes", "slippers", "shoes",
    "blazer", "jacket", "coat", "sweater", "cardigan", "hoodie", "vest", "polo",
    "jersey", "shirt",
    "jeans", "trousers", "pants", "slacks",
)
_SEX_W_BY_SLOT = {
    "upper":  0.35,
    "lower":  0.40,
    "leg_l":  0.55,
    "neck":   0.45,
    "head":   0.45,
    "ears":   0.45,
    "hand_l": 0.0,
    "feet":   0.0,
}

def _set_sex_w(slot, en):
    low = (en or "").lower()
    if any(k in low for k in _SEX_NEVER):
        return 0.0
    return _SEX_W_BY_SLOT.get(slot, 0.45)

_SET_CN = {}
for _s, _slots in SET_EXTRA.items():
    for _slot, _words in _slots.items():
        _lst = GEAR_EXT.setdefault(_slot, [])
        _have = {it["en"] for it in _lst}
        for _en, _cn in _words:
            if _en in _have:
                continue
            _lst.append(_it(_en, _cn,
                            _W(1.00, 0.60, 0.45, _set_sex_w(_slot, _en)),
                            _slot, src="set:" + _s))
            _have.add(_en)
            _SET_CN[_en] = _cn

NEW_SET_TRANSLATIONS = dict(_SET_CN)

GEAR_EXT["waist"] = [
    _it('slim leather belt', '细皮带', _W(1.00, 0.60, 0.45, 0.45), 'waist', src='set:commute'),
    _it('woven belt', '编织腰带', _W(1.00, 0.60, 0.45, 0.45), 'waist', src='set:mori'),
    _it('belt', '腰带', _W(1.00, 0.60, 0.45, 0.45), 'waist', src='log'),
]

def candidates(slot, tier, want_attr=False):
    if tier not in TIERS:
        return []
    out = []
    for it in list(GEAR.get(slot, [])) + list(GEAR_EXT.get(slot, [])):
        if it.get("attr") and not want_attr:
            continue
        if it["w"].get(tier, 0) > 0:
            d = dict(it)
            d["tier"] = tier
            out.append(d)
    return out

def pick(slot, tier, rng):
    cands = candidates(slot, tier)
    if not cands:
        return None
    by_en = {c["en"]: c for c in cands}
    ens = list(by_en)
    w = [by_en[k]["w"][tier] for k in ens]
    chosen = rng.choices(ens, weights=w, k=1)[0]
    return chosen or None

def selfcheck(verbose=False):
    problems = []
    for slot, items in list(GEAR.items()) + list(GEAR_EXT.items()):
        for it in items:
            if set(it["w"]) != set(TIERS):
                problems.append(f"{slot}/{it['en']!r} 的权重缺档 ✗")
    for slot in ("upper", "lower"):
        for tier in TIERS:
            if not candidates(slot, tier):
                problems.append(f"[{tier}] {slot} 无候选 ✗")
    for tier in TIERS:
        for it in candidates("upper", tier):
            if it.get("attr"):
                problems.append(f"[{tier}] 属性词 {it['en']!r} 混进了上衣候选 ✗")
    for slot in ("upper", "lower", "rear"):
        for it in candidates(slot, "fashion"):
            if any(k in it["en"] for k in ("bare ", "topless", "exposed", "visible")):
                problems.append(f"时尚档 {slot} 出现了裸露词 {it['en']!r} ✗")
    for slot in ("upper", "lower"):
        if not any("bare" in it["en"] or "exposed" in it["en"] for it in candidates(slot, "exposed")):
            problems.append(f"暴露档 {slot} 缺裸露占位词 ✗（默认该裸 ✓）")
    if verbose:
        tot = sum(len(v) for v in GEAR.values()) + sum(len(v) for v in GEAR_EXT.values())
        zero = sum(1 for v in list(GEAR.values()) + list(GEAR_EXT.values()) for it in v
                   for t in TIERS if it["w"][t] == 0)
        print(f"  装备池自检：{'✗ ' + '；'.join(problems[:4]) if problems else '✓ 全过'}")
        print(f"    部位 {len(GEAR)} · 条目 {tot} · 四档总权重位 {tot*4}（其中为 0 的 {zero} 个 = 该档不出现 ✓）")
    return problems

if __name__ == "__main__":
    import sys
    sys.exit(1 if selfcheck(verbose=True) else 0)

SET_IN_P = 0.70

def set_names():
    out = set()
    for tbl in (GEAR, GEAR_EXT):
        for items in tbl.values():
            for it in items:
                src = it.get("src") or ""
                if src.startswith("set:"):
                    out.add(src[4:])
    return sorted(out)

def set_of(item):
    src = (item or {}).get("src") or ""
    return src[4:] if src.startswith("set:") else ""

def pick_slot(slot, tier, rng, want_set="", in_set_p=SET_IN_P, vacant_p=None):
    cands = candidates(slot, tier)
    if not cands:
        return None
    if vacant_p is None:
        vacant_p = (VACANT_P_BY_SLOT.get(slot, VACANT_P) if slot in VACANT_SLOTS else 0.0)
    if vacant_p and rng.random() < vacant_p:
        return None
    vacant = []
    if want_set:
        in_set = [c for c in cands if set_of(c) == want_set] + vacant
        if not in_set:
            return None
        pool = in_set if rng.random() < in_set_p else cands
    else:
        pool = cands
    by_en = {c["en"]: c for c in pool}
    ens = list(by_en)
    w = [by_en[k]["w"][tier] for k in ens]
    return rng.choices(ens, weights=w, k=1)[0] or None

USE_WARDROBE_FROM_V3 = False
GEAR_V2_LEGACY = GEAR
GEAR_EXT_V2_LEGACY = GEAR_EXT
V3_STATS = {}

try:
    try:
        from . import roll_params as _rp3
    except Exception:
        import roll_params as _rp3
except Exception:
    _rp3 = None

USE_WARDROBE_FROM_V3 = bool(getattr(_rp3, "USE_WARDROBE_FROM_V3", False))

if USE_WARDROBE_FROM_V3:
    try:
        try:
            from . import wardrobe_from_v3 as _WV3
        except Exception:
            import wardrobe_from_v3 as _WV3
        _g3, _e3 = _WV3.build(GEAR_V2_LEGACY, GEAR_EXT_V2_LEGACY)
        GEAR, GEAR_EXT = _g3, _e3
        V3_STATS = _WV3.stats(GEAR, GEAR_EXT)
    except Exception as _e:
        print(f"[wardrobe_pools] v3 词库注入失败，回退 v2 老表：{_e!r}")
