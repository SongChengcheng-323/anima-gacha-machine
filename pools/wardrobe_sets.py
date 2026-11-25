SETS = {
    '__random__': {"cn": '随机', "tier": 'fashion', "slots": {
        'head': [
            ('beret', '贝雷帽', ()),
            ('wide-brim hat', '宽檐帽', ()),
            ('baseball cap', '棒球帽', ()),
            ('hair bow', '发间蝴蝶结', ()),
            ('headband', '发箍', ()),
        ],
        'eyes': [
            ('glasses', '眼镜', ()),
            ('sunglasses', '墨镜', ()),
            ('cat eye eyewear', '猫眼眼镜', ()),
        ],
        'ears': [
            ('stud earrings', '耳钉', ()),
            ('hoop earrings', '圈形耳环', ()),
            ('dangling earrings', '垂坠耳环', ()),
            ('ear cuffs', '耳骨夹', ()),
        ],
        'neck': [
            ('choker', '颈圈', ()),
            ('pendant necklace', '吊坠项链', ()),
            ('chain necklace', '链条项链', ()),
            ('silk scarf', '丝巾', ()),
        ],
        'upper_set': [
            ('slip dress', '吊带连衣裙', ('upper', 'lower')),
            ('wrap dress', '裹身裙', ('upper', 'lower')),
            ('knit dress', '针织连身裙', ('upper', 'lower')),
            ('shirt dress', '衬衫裙', ('upper', 'lower')),
            ('sundress', '夏日连衣裙', ('upper', 'lower')),
            ('jumpsuit', '连体裤', ('upper', 'lower')),
            ('overalls', '背带裤', ('upper', 'lower')),
        ],
        'upper_base': [
            ('camisole', '吊带背心', ('upper',)),
            ('halterneck', '挂脖背心', ('upper',)),
            ('tube top', '抹胸上衣', ('upper',)),
            ('crop top', '短款露脐上衣', ('upper',)),
            ('t-shirt', 'T恤', ('upper',)),
        ],
        'upper_outer': [
            ('blouse', '衬衫', ('upper',)),
            ('turtleneck sweater', '高领毛衣', ('upper',)),
            ('knit cardigan', '针织开衫', ('upper',)),
            ('blazer', '西装外套', ('upper',)),
            ('trench coat', '风衣', ('upper',)),
            ('long coat', '长大衣', ('upper',)),
            ('denim jacket', '牛仔外套', ('upper',)),
            ('leather jacket', '皮夹克', ('upper',)),
        ],
        'lower': [
            ('pleated skirt', '百褶裙', ('lower',)),
            ('satin skirt', '缎面半裙', ('lower',)),
            ('leather skirt', '皮短裙', ('lower',)),
            ('pencil skirt', '包臀裙', ('lower',)),
            ('denim shorts', '牛仔短裤', ('lower',)),
            ('wide-leg pants', '阔腿裤', ('lower', 'leg_l')),
            ('jeans', '牛仔裤', ('lower', 'leg_l')),
            ('cargo pants', '工装裤', ('lower', 'leg_l')),
            ('black tights', '黑丝袜', ('lower', 'leg_l')),
            ('thighhighs', '过膝袜', ('lower', 'leg_l')),
        ],
        'leg_l': [
            ('knee-high socks', '及膝袜', ()),
            ('crew socks', '中筒袜', ()),
            ('leg warmers', '腿套', ()),
            ('thigh strap', '大腿绑带', ()),
        ],
        'feet': [
            ('sneakers', '球鞋', ()),
            ('combat boots', '马丁靴', ()),
            ('ankle boots', '短靴', ()),
            ('knee boots', '长筒靴', ()),
            ('stiletto heels', '细高跟鞋', ()),
            ('ballet flats', '芭蕾平底鞋', ()),
            ('loafers', '乐福鞋', ()),
            ('mary janes', '玛丽珍鞋', ()),
        ],
        'hand_l': [
            ('shoulder bag', '单肩包', ()),
            ('tote bag', '托特包', ()),
            ('mini handbag', '迷你手提包', ()),
            ('bracelet', '手链', ()),
            ('wristwatch', '手表', ()),
        ],
    }},
    'ballet': {"cn": '芭蕾', "tier": 'fashion', "slots": {
        'head': [
            ('wide ribbon headband', '宽缎带发箍', ()),
            ('tulle bow', '纱质蝴蝶结', ()),
            ('lace headband', '蕾丝发箍', ()),
        ],
        'eyes': [
            ('round glasses', '圆框眼镜', ()),
            ('glasses with chain', '挂链眼镜', ()),
        ],
        'ears': [
            ('pearl drop earrings', '珍珠垂坠耳环', ()),
            ('ribbon earrings', '缎带耳饰', ()),
        ],
        'neck': [
            ('pearl ribbon choker', '珍珠缎带颈圈', ()),
            ('ribbon neck bow', '颈间缎带结', ()),
            ('cameo pendant', '浮雕吊坠', ()),
        ],
        'upper_base': [
            ('white t-shirt', '白T', ('upper',)),
            ('lace-trimmed knit top', '蕾丝边针织上衣', ('upper',)),
            ('corset top', '束腰上衣', ('upper',)),
        ],
        'upper_outer': [
            ('ballet wrap top', '芭蕾围裹上衣', ('upper',)),
            ('sheer chiffon blouse', '雪纺纱上衣', ('upper',)),
            ('angora sweater', '安哥拉毛衣', ('upper',)),
        ],
        'lower': [
            ('tulle tiered skirt', '层叠纱裙', ('lower',)),
            ('wrap mini skirt', '围裹短裙', ('lower',)),
            ('chiffon maxi skirt', '雪纺长裙', ('lower',)),
            ('satin gathered skirt', '缎面抽褶裙', ('lower',)),
            ('black pantyhose', '黑丝', ('lower', 'leg_l')),
            ('white thighhighs', '白过膝袜', ('lower', 'leg_l')),
        ],
        'leg_l': [
            ('knee-high socks', '及膝袜', ()),
            ('leg warmers', '腿套', ()),
        ],
        'feet': [
            ('ballet slippers', '芭蕾软鞋', ()),
            ('ribbon ballet flats', '缎带芭蕾平底鞋', ()),
            ('patent mary janes', '漆皮玛丽珍', ()),
        ],
        'hand_l': [
            ('small quilted bag', '小绗缝包', ()),
            ('satin pouch', '缎面手拿包', ()),
            ('mini handbag', '迷你手袋', ()),
        ],
    }},
    'commute': {"cn": '通勤', "tier": 'fashion', "slots": {
        'head': [
            ('silk headband', '真丝发箍', ()),
            ('thin barrette', '细发夹', ()),
        ],
        'eyes': [
            ('thin-framed eyewear', '细框眼镜', ()),
            ('sunglasses', '墨镜', ()),
        ],
        'ears': [
            ('small gold studs', '小金耳钉', ()),
            ('thin silver hoops', '细银圈耳环', ()),
        ],
        'neck': [
            ('thin chain necklace', '细链项链', ()),
            ('silk neck scarf', '颈部丝巾', ()),
        ],
        'upper_base': [
            ('white t-shirt', '白T', ('upper',)),
            ('turtleneck top', '高领上衣', ('upper',)),
        ],
        'upper_outer': [
            ('button-down shirt', '系扣衬衫', ('upper',)),
            ('knit polo', '针织polo', ('upper',)),
            ('fitted blazer', '修身西装外套', ('upper',)),
            ('long wool coat', '长款羊毛大衣', ('upper',)),
        ],
        'lower': [
            ('wide-leg dress trousers', '阔腿西裤', ('lower', 'leg_l')),
            ('tapered suit pants', '锥形西装裤', ('lower', 'leg_l')),
            ('straight-leg jeans', '直筒牛仔裤', ('lower', 'leg_l')),
            ('pleated suit skirt', '百褶西装裙', ('lower',)),
            ('wrap pencil skirt', '围裹铅笔裙', ('lower',)),
            ('black pantyhose', '黑丝', ('lower', 'leg_l')),
        ],
        'leg_l': [
            ('sheer ankle socks', '薄款短袜', ('leg_l',)),
        ],
        'feet': [
            ('pointed pumps', '尖头高跟鞋', ()),
            ('heeled loafers', '粗跟乐福鞋', ()),
            ('square-toe flats', '方头平底鞋', ()),
            ('ankle boots', '踝靴', ()),
        ],
        'hand_l': [
            ('structured satchel', '结构手提包', ()),
            ('leather briefcase', '皮质公文包', ()),
            ('leather strap watch', '皮带手表', ()),
        ],
    }},
    'french': {"cn": '法式', "tier": 'fashion', "slots": {
        'head': [
            ('tortoiseshell hair clip', '玳瑁发夹', ()),
            ('ribbon headband', '缎带发箍', ()),
            ('silk scarf headband', '丝巾发箍', ()),
        ],
        'eyes': [
            ('round glasses', '圆框眼镜', ()),
            ('cat eye eyewear', '猫眼墨镜', ()),
        ],
        'ears': [
            ('small gold hoops', '小金圈耳环', ()),
            ('pearl drop earrings', '珍珠垂坠耳环', ()),
        ],
        'neck': [
            ('gold locket', '金质吊坠盒', ()),
            ('silk neck scarf', '颈部丝巾', ()),
            ('pearl strand', '珍珠串链', ()),
        ],
        'upper_base': [
            ('white t-shirt', '白T', ('upper',)),
            ('breton striped top', '布列塔尼条纹上衣', ('upper',)),
            ('lace-trimmed camisole', '蕾丝边吊带', ('upper',)),
        ],
        'upper_outer': [
            ('silk blouse', '真丝衬衫', ('upper',)),
            ('wrap blouse', '系带衬衫', ('upper',)),
            ('cropped cardigan', '短款开衫', ('upper',)),
            ('trench coat', '风衣', ('upper',)),
        ],
        'lower': [
            ('cropped jeans', '九分牛仔裤', ('lower', 'leg_l')),
            ('pleated midi skirt', '百褶中长裙', ('lower',)),
            ('gathered waist skirt', '抽褶半裙', ('lower',)),
            ('linen shorts', '亚麻短裤', ('lower',)),
            ('black pantyhose', '黑丝', ('lower', 'leg_l')),
            ('dotted tights', '波点连裤袜', ('lower', 'leg_l')),
        ],
        'leg_l': [
            ('ankle socks', '短袜', ('leg_l',)),
        ],
        'feet': [
            ('ballet flats', '芭蕾平底鞋', ()),
            ('slingback kitten heels', '后空猫跟鞋', ()),
            ('woven espadrilles', '编织麻底鞋', ()),
            ('white sneakers', '白球鞋', ()),
        ],
        'hand_l': [
            ('woven basket bag', '编织篮包', ()),
            ('structured leather bag', '结构皮包', ()),
            ('quilted shoulder bag', '绗缝单肩包', ()),
        ],
    }},
    'guochao': {"cn": '国潮', "tier": 'fashion', "slots": {
        'head': [
            ('jade hairpin', '玉簪', ()),
            ('tassel hairpin', '流苏发簪', ()),
            ('pearl hair comb', '珍珠发梳', ()),
            ('silk hair band', '真丝发带', ()),
        ],
        'ears': [
            ('jade drop earrings', '玉坠耳环', ()),
            ('tassel earrings', '流苏耳环', ()),
        ],
        'neck': [
            ('jade pendant', '玉坠', ()),
            ('tassel necklace', '流苏项链', ()),
            ('red string necklace', '红绳项链', ()),
            ('side slit', '侧开衩', ()),
            ('frog closure', '盘扣', ()),
            ('wide sleeves', '宽袖', ()),
        ],
        'upper_set': [
            ('qipao', '旗袍', ('upper', 'lower')),
            ('hanfu', '汉服', ('upper', 'lower')),
            ('silk dress', '真丝连衣裙', ('upper', 'lower')),
            ('china dress', '中华风连衣裙', ('upper', 'lower')),
            ('cheongsam', '长衫旗袍', ('upper', 'lower')),
        ],
        'upper_base': [
            ('camisole', '吊带背心', ('upper',)),
        ],
        'upper_outer': [
            ('qipao-style top', '旗袍式上衣', ('upper',)),
            ('lace-up hanfu top', '系带汉服上衣', ('upper',)),
            ('bamboo print blouse', '竹纹衬衫', ('upper',)),
            ('silk wrap blouse', '真丝系带上衣', ('upper',)),
            ('embroidered linen top', '绣花亚麻上衣', ('upper',)),
            ('mandarin collar top', '立领上衣', ('upper',)),
            ('mandarin collar blouse', '立领衬衫', ('upper',)),
            ('chinese clothes', '中式服装', ('upper',)),
        ],
        'lower': [
            ('qipao skirt', '旗袍裙', ('lower',)),
            ('pleated wrap skirt', '百褶围裹裙', ('lower',)),
            ('embroidered skirt', '刺绣半裙', ('lower',)),
            ('layered hanfu skirt', '层叠汉服裙', ('lower',)),
            ('silk long skirt', '真丝长裙', ('lower',)),
            ('wide-leg cropped pants', '阔腿九分裤', ('lower', 'leg_l')),
            ('sheer black tights', '黑色透丝袜', ('lower', 'leg_l')),
        ],
        'leg_l': [
            ('embroidered socks', '绣花袜', ()),
            ('knee-high socks', '及膝袜', ()),
        ],
        'feet': [
            ('embroidered flats', '绣花平底鞋', ()),
            ('cloth shoes', '布鞋', ()),
            ('canvas sneakers', '帆布鞋', ()),
        ],
        'hand_l': [
            ('hand fan', '团扇', ()),
            ('silk pouch', '真丝香囊', ()),
            ('beaded bag', '串珠包', ()),
        ],
    }},
    'lingerie': {"cn": '擦边', "tier": 'tease', "slots": {
        'head': [
            ('rabbit ears', '兔耳发箍', ()),
            ('nurse cap', '护士帽', ()),
            ('maid headdress', '女仆头饰', ()),
        ],
        'neck': [
            ('lace choker', '蕾丝颈圈', ()),
        ],
        'upper_set': [
            ('nightgown', '睡裙', ('upper', 'lower')),
            ('negligee', '薄纱蕾丝睡裙', ('upper', 'lower')),
            ('chemise', '真丝吊带衬裙', ('upper', 'lower')),
            ('lingerie', '蕾丝内衣套装', ('upper', 'lower')),
            ('babydoll', '娃娃款情趣内衣', ('upper', 'lower')),
            ('open bodysuit', '开襟镂空连体衣', ('upper', 'lower')),
            ('naked towel', '只裹一条浴巾', ('upper', 'lower')),
            ('playboy bunny', '兔女郎装', ('upper', 'lower')),
            ('leotard', '紧身连体衣', ('upper', 'lower')),
            ('nurse', '护士服', ('upper', 'lower')),
            ('maid', '女仆装', ('upper', 'lower')),
            ('police uniform', '警服', ('upper', 'lower')),
            ('military uniform', '军装', ('upper', 'lower')),
            ('serafuku', '水手服', ('upper', 'lower')),
            ('bikini', '比基尼', ('upper', 'lower')),
            ('one-piece swimsuit', '连体泳衣', ('upper', 'lower')),
            ('highleg one-piece swimsuit', '高叉连体泳衣', ('upper', 'lower')),
            ('school swimsuit', '死库水', ('upper', 'lower')),
            ('oversized shirt', '只套一件大衬衫', ('upper', 'lower')),
            ('bandage wrap', '绷带缠身', ('upper',)),
            ('see-through clothes', '透视装', ('upper',)),
            ('sheer fabric, see-through top', '薄纱透视上衣', ('upper',)),
            ('tape on skin', '胶带贴肤', ('upper',)),
        ],
        'upper_base': [
            ('lace bra', '蕾丝文胸', ('upper',)),
            ('lace corset', '蕾丝束身衣', ('upper',)),
        ],
        'upper_outer': [
            ('bathrobe', '浴袍', ('upper',)),
        ],
        'lower': [
            ('lace panties', '蕾丝内裤', ('lower',)),
            ('towel around waist', '浴巾围腰', ('lower',)),
            ('black thighhighs', '黑色过膝袜', ('lower', 'leg_l')),
            ('white thighhighs', '白过膝袜', ('lower', 'leg_l')),
            ('white pantyhose', '白色连裤丝袜', ('lower', 'leg_l')),
            ('ripped pantyhose', '破洞连裤袜', ('lower', 'leg_l')),
            ('torn thighhighs', '破洞过膝袜', ('lower', 'leg_l')),
            ('fishnets', '渔网袜', ('lower', 'leg_l')),
            ('striped panties', '条纹内裤', ('lower',)),
            ('frilled panties', '荷叶边内裤', ('lower',)),
            ('side-tie panties', '侧绑带内裤', ('lower',)),
            ('high-cut panties', '高叉内裤', ('lower',)),
            ('white bloomers', '白色灯笼裤', ('lower',)),
            ('lace-trimmed panties', '蕾丝边内裤', ('lower',)),
        ],
        'leg_l': [
            ('garter straps', '吊袜带', ()),
        ],
        'feet': [
            ('high heels', '高跟鞋', ()),
            ('thigh boots', '过膝长靴', ()),
        ],
    }},
    'minimal': {"cn": '极简', "tier": 'fashion', "slots": {
        'head': [
            ('thin headband', '细发箍', ()),
            ('silk hair scarf', '真丝发巾', ()),
        ],
        'eyes': [
            ('thin-framed eyewear', '细框眼镜', ()),
            ('sunglasses', '墨镜', ()),
        ],
        'ears': [
            ('small silver studs', '小银耳钉', ()),
            ('thin gold hoops', '细金圈耳环', ()),
        ],
        'neck': [
            ('delicate bar necklace', '细条项链', ()),
            ('simple pearl pendant', '简约珍珠吊坠', ()),
        ],
        'upper_base': [
            ('white t-shirt', '白T', ('upper',)),
            ('tank top', '背心', ('upper',)),
            ('silk camisole top', '真丝吊带', ('upper',)),
        ],
        'upper_outer': [
            ('poplin shirt', '府绸衬衫', ('upper',)),
            ('merino wool sweater', '美利奴毛衣', ('upper',)),
            ('long wool coat', '长款羊毛大衣', ('upper',)),
        ],
        'lower': [
            ('tapered trousers', '锥形西裤', ('lower', 'leg_l')),
            ('straight-leg jeans', '直筒牛仔裤', ('lower', 'leg_l')),
            ('bias-cut satin skirt', '斜裁缎面裙', ('lower',)),
            ('column maxi skirt', '直筒长裙', ('lower',)),
            ('wrap midi skirt', '一片式中长裙', ('lower',)),
            ('tailored shorts', '西装短裤', ('lower',)),
            ('black pantyhose', '黑丝', ('lower', 'leg_l')),
        ],
        'leg_l': [
            ('ankle socks', '短袜', ('leg_l',)),
        ],
        'feet': [
            ('white sneakers', '白球鞋', ()),
            ('pointed-toe flats', '尖头平底鞋', ()),
            ('slingback pumps', '后空高跟鞋', ()),
            ('square-toe boots', '方头短靴', ()),
        ],
        'hand_l': [
            ('minimal leather backpack', '简约皮双肩包', ()),
            ('structured pouch', '结构感手拿包', ()),
            ('leather strap watch', '皮带手表', ()),
        ],
    }},
    'mori': {"cn": '森系', "tier": 'fashion', "slots": {
        'head': [
            ('crochet hat', '钩花帽', ()),
            ('linen headscarf', '亚麻头巾', ()),
            ('felt hat', '毛毡帽', ()),
            ('flower hair wreath', '花环头饰', ()),
        ],
        'eyes': [
            ('round glasses', '圆框眼镜', ()),
        ],
        'ears': [
            ('wooden earrings', '木质耳环', ()),
            ('small brass hoop earrings', '小黄铜圈耳环', ()),
        ],
        'neck': [
            ('wooden bead necklace', '木珠项链', ()),
            ('linen scarf', '亚麻围巾', ()),
            ('dried flower pendant', '干花吊坠', ()),
        ],
        'upper_set': [
            ('sundress', '棉麻吊带连衣裙', ('upper', 'lower')),
            ('linen dress', '亚麻连衣裙', ('upper', 'lower')),
        ],
        'upper_base': [
            ('camisole', '吊带背心', ('upper',)),
            ('cotton tank top', '棉布背心', ('upper',)),
        ],
        'upper_outer': [
            ('oversized knit cardigan', '宽松针织开衫', ('upper',)),
            ('cotton gauze blouse', '棉纱上衣', ('upper',)),
            ('embroidered linen top', '绣花亚麻上衣', ('upper',)),
            ('crochet vest', '钩花马甲', ('upper',)),
            ('layered long shirt', '层叠长衬衫', ('upper',)),
            ('knit sweater', '针织毛衣', ('upper',)),
        ],
        'lower': [
            ('gathered cotton skirt', '抽褶棉裙', ('lower',)),
            ('tiered prairie skirt', '多层田园长裙', ('lower',)),
            ('patchwork skirt', '拼布半裙', ('lower',)),
            ('linen wide pants', '亚麻阔腿裤', ('lower', 'leg_l')),
            ('plain cotton tights', '素色棉连裤袜', ('lower', 'leg_l')),
        ],
        'leg_l': [
            ('wool knee socks', '羊毛及膝袜', ()),
            ('ribbed knit socks', '罗纹针织袜', ()),
            ('knit leg warmers', '针织腿套', ()),
        ],
        'feet': [
            ('suede boots', '麂皮靴', ()),
            ('woven sandals', '编织凉鞋', ()),
            ('canvas slip-ons', '帆布一脚蹬', ()),
            ('canvas sneakers', '帆布鞋', ()),
        ],
        'hand_l': [
            ('woven basket bag', '编织篮包', ()),
            ('canvas sling bag', '帆布斜挎包', ()),
            ('macrame bag', '绳编包', ()),
        ],
    }},
    'sport': {"cn": '运动户外', "tier": 'fashion', "slots": {
        'head': [
            ('baseball cap', '棒球帽', ()),
            ('visor cap', '空顶帽', ()),
            ('headband', '运动发带', ()),
            ('headphones', '头戴耳机', ()),
        ],
        'neck': [
            ('towel around neck', '搭在脖子上的毛巾', ()),
        ],
        'upper_set': [
            ('track suit', '运动套装', ('upper', 'lower')),
        ],
        'upper_base': [
            ('sports bra', '运动内衣', ('upper',)),
            ('tank top', '运动背心', ('upper',)),
            ('compression shirt', '紧身运动上衣', ('upper',)),
            ('jersey', '运动球衣', ('upper',)),
        ],
        'upper_outer': [
            ('hoodie', '连帽卫衣', ('upper',)),
            ('track jacket', '运动夹克', ('upper',)),
            ('letterman jacket', '棒球外套', ('upper',)),
        ],
        'lower': [
            ('track pants', '运动长裤', ('lower', 'leg_l')),
            ('yoga pants', '瑜伽裤', ('lower', 'leg_l')),
            ('sweatpants', '束脚卫裤', ('lower', 'leg_l')),
            ('bike shorts', '骑行短裤', ('lower',)),
            ('gym shorts', '运动短裤', ('lower',)),
            ('tennis skirt', '网球裙', ('lower',)),
        ],
        'leg_l': [
            ('ankle socks', '运动短袜', ('leg_l',)),
            ('leg warmers', '运动腿套', ('leg_l',)),
        ],
        'feet': [
            ('sneakers', '运动鞋', ()),
            ('platform shoes', '厚底老爹鞋', ()),
        ],
        'hand_l': [
            ('water bottle', '运动水壶', ()),
            ('wristband', '护腕', ()),
            ('duffel bag', '运动手提包', ()),
            ('tennis racket', '网球拍', ()),
        ],
    }},
    'street': {"cn": '街头', "tier": 'fashion', "slots": {
        'head': [
            ('snapback cap', '棒球帽', ()),
            ('bucket hat', '渔夫帽', ()),
            ('beanie', '针织帽', ()),
        ],
        'eyes': [
            ('sunglasses', '墨镜', ()),
        ],
        'ears': [
            ('silver hoop earrings', '银圈耳环', ()),
            ('stud earrings', '耳钉', ()),
        ],
        'neck': [
            ('chain necklace', '链条项链', ()),
            ('choker', '颈圈', ()),
        ],
        'upper_set': [
            ('overalls', '背带裤', ('upper', 'lower')),
        ],
        'upper_base': [
            ('t-shirt', 'T恤', ('upper',)),
            ('crop top', '露脐上衣', ('upper',)),
            ('ribbed tank top', '罗纹背心', ('upper',)),
            ('sports jersey', '运动球衣', ('upper',)),
            ('graphic band tee', '印花乐队T', ('upper',)),
        ],
        'upper_outer': [
            ('oversized bomber jacket', '宽松飞行夹克', ('upper',)),
            ('zip-up hoodie', '拉链连帽衫', ('upper',)),
            ('cropped puffer vest', '短款羽绒马甲', ('upper',)),
            ('denim trucker jacket', '牛仔夹克', ('upper',)),
            ('track jacket', '运动外套', ('upper',)),
        ],
        'lower': [
            ('jogger pants', '束脚裤', ('lower', 'leg_l')),
            ('parachute pants', '降落伞裤', ('lower', 'leg_l')),
            ('cargo pants', '工装裤', ('lower', 'leg_l')),
            ('ripped jeans', '破洞牛仔裤', ('lower', 'leg_l')),
            ('cargo skirt', '工装裙', ('lower',)),
            ('ribbed bike shorts', '罗纹骑行短裤', ('lower',)),
            ('fishnet tights', '渔网袜', ('lower', 'leg_l')),
            ('sheer black tights', '黑色透丝袜', ('lower', 'leg_l')),
        ],
        'leg_l': [
            ('crew socks', '中筒袜', ()),
            ('sporty striped socks', '运动条纹袜', ()),
            ('ribbed ankle socks', '罗纹短袜', ()),
        ],
        'feet': [
            ('chunky platform sneakers', '厚底运动鞋', ()),
            ('high-top sneakers', '高帮运动鞋', ()),
            ('platform boots', '厚底靴', ()),
        ],
        'hand_l': [
            ('bumbag', '腰包', ()),
            ('mini backpack', '迷你双肩包', ()),
        ],
    }},
    'vintage': {"cn": '复古', "tier": 'fashion', "slots": {
        'head': [
            ('pillbox hat', '药盒帽', ()),
            ('velvet bow', '天鹅绒蝴蝶结', ()),
            ('pearl headpiece', '珍珠发饰', ()),
            ('beret', '贝雷帽', ()),
        ],
        'eyes': [
            ('cat eye eyewear', '猫眼眼镜', ()),
        ],
        'ears': [
            ('pearl earrings', '珍珠耳环', ()),
            ('cameo earrings', '浮雕耳环', ()),
        ],
        'neck': [
            ('pearl necklace', '珍珠项链', ()),
            ('cameo pendant', '浮雕吊坠', ()),
            ('silk neck scarf', '颈部丝巾', ()),
        ],
        'upper_set': [
            ('swing dress', '伞摆连衣裙', ('upper', 'lower')),
            ('a-line dress', 'A字收腰连衣裙', ('upper', 'lower')),
        ],
        'upper_base': [
            ('lace-trimmed camisole', '蕾丝边吊带', ('upper',)),
            ('turtleneck top', '高领上衣', ('upper',)),
        ],
        'upper_outer': [
            ('pussy-bow blouse', '蝴蝶结领衬衫', ('upper',)),
            ('polka dot top', '波点上衣', ('upper',)),
            ('houndstooth jacket', '千鸟格外套', ('upper',)),
            ('ribbon blouse', '缎带衬衫', ('upper',)),
            ('cropped knit cardigan', '短款针织开衫', ('upper',)),
        ],
        'lower': [
            ('circle skirt', '伞裙', ('lower',)),
            ('houndstooth skirt', '千鸟格半裙', ('lower',)),
            ('pleated plaid skirt', '格纹百褶裙', ('lower',)),
            ('button-front skirt', '前排扣半裙', ('lower',)),
            ('high-waisted slacks', '高腰长裤', ('lower', 'leg_l')),
            ('seam tights', '背缝丝袜', ('lower', 'leg_l')),
            ('dotted tights', '波点连裤袜', ('lower', 'leg_l')),
        ],
        'leg_l': [
            ('knee-high socks', '及膝袜', ()),
            ('ribbed socks', '罗纹短袜', ()),
        ],
        'feet': [
            ('t-strap heels', '丁字带高跟鞋', ()),
            ('mary jane pumps', '玛丽珍高跟', ()),
            ('oxford shoes', '牛津鞋', ()),
            ('vintage boots', '复古靴', ()),
        ],
        'hand_l': [
            ('carpet bag', '复古手提包', ()),
            ('framed handbag', '框式手袋', ()),
            ('beaded clutch', '珠绣手拿包', ()),
        ],
    }},
}

ORDER = ("head", "eyes", "ears", "neck", "upper", "lower", "leg_l", "feet", "hand_l")

_LONG_KW = ("pants", "jeans", "trousers", "slacks", "joggers", "leggings",
            "tights", "pantyhose", "stockings", "thighhighs", "fishnets")

FASHION_SETS = tuple(k for k, v in SETS.items()
                     if v["tier"] == "fashion" and not k.startswith("__"))
TEASE_SETS = tuple(k for k, v in SETS.items() if v["tier"] == "tease")

def set_names(tier=None):
    if tier is None:
        return tuple(k for k in SETS if not k.startswith("__"))
    return tuple(k for k, v in SETS.items()
                 if v["tier"] == tier and not k.startswith("__"))

def generic_slots():
    return (SETS.get("__random__") or {}).get("slots") or {}

VACANT_P = {
    "head":   0.72,
    "eyes":   0.78,
    "ears":   0.50,
    "neck":   0.42,
    "hand_l": 0.68,
    "leg_l":  0.52,
    "feet":   0.06,
}

ITEM_W = {
    "cat eye eyewear": 0.35,
}

def pick_item(rng, items):
    if not items:
        return None
    ws = [ITEM_W.get((it[0] or "").strip(), 1.0) for it in items]
    if all(w == ws[0] for w in ws):
        return rng.choice(items)
    return rng.choices(items, weights=ws, k=1)[0]

BONUS = {
    "school swimsuit":            [("wet, wet clothes, water droplets on skin", 0.50)],
    "one-piece swimsuit":         [("wet, wet clothes, water droplets on skin", 0.50)],
    "highleg one-piece swimsuit": [("wet, wet clothes, water droplets on skin", 0.50)],
    "bikini":                     [("wet, wet clothes, water droplets on skin", 0.50)],
    "nightgown":       [("nipples visible through the fabric", 0.80)],
    "chemise":         [("nipples visible through the fabric", 0.80)],
    "negligee":        [("nipples visible through the fabric", 0.80)],
    "babydoll":        [("nipples visible through the fabric", 0.80)],
    "oversized shirt": [("nipples visible through the fabric", 0.80)],
    "camisole":        [("nipples visible through the fabric", 0.70)],
    "naked towel": [("wet hair, water droplets on skin", 0.45)],
    "bathrobe":    [("wet hair, water droplets on skin", 0.45)],
}

VARIANT = {
    "jeans":               [("ripped jeans", 0.40, "破洞牛仔裤")],
    "straight-leg jeans":  [("ripped jeans", 0.40, "破洞牛仔裤")],
    "baggy wide-leg jeans": [("distressed jeans", 0.35, "做旧破洞牛仔裤")],
    "denim shorts":        [("ripped denim shorts", 0.35, "破洞牛仔短裤")],
    "black thighhighs":    [("ripped pantyhose", 0.35, "破洞连裤袜")],
    "white thighhighs":    [("torn thighhighs", 0.30, "破洞过膝袜")],
    "pantyhose":           [("ripped pantyhose", 0.35, "破洞连裤袜")],
    "white pantyhose":     [("ripped pantyhose", 0.25, "破洞连裤袜")],
}

def variant_of(word, rng):
    for alt, p, cn in VARIANT.get((word or "").strip(), ()):
        if rng.random() < p:
            return alt, cn
    return None

STYLIZE = {
    "jeans":                 [("frayed hem", 0.30, ("fashion",))],
    "baggy wide-leg jeans":  [("frayed hem", 0.25, ("fashion",))],
    "denim shorts":          [("frayed hem", 0.30, ("fashion",))],
    "ripped jeans":          [("frayed hem", 0.25, ("fashion",))],
    "distressed jeans":      [("faded denim", 0.25, ("fashion",))],
    "pleated skirt":         [("frayed hem", 0.20, ("fashion",))],
    "circle skirt":          [("frayed hem", 0.18, ("fashion",))],
    "long wool coat":        [("frayed hem", 0.15, ("fashion",))],
    "see-through clothes":   [("wet clothes", 0.35, ("tease",))],
    "sheer fabric, see-through top": [("wet clothes", 0.30, ("tease",))],
    "white pantyhose":       [("wet clothes", 0.25, ("tease",))],
    "black thighhighs":      [("wet clothes", 0.20, ("tease",))],
    "white thighhighs":      [("wet clothes", 0.20, ("tease",))],
    "oversized shirt":       [("see-through, wet shirt", 0.25, ("tease",))],
    "nightgown":             [("see-through, sheer fabric", 0.25, ("tease",))],
    "camisole":              [("see-through, sheer fabric", 0.25, ("tease",))],
}

def stylize_of(word, rng, tier=None):
    for tag, p, tiers in STYLIZE.get((word or "").strip(), ()):
        if tier and tiers and tier not in tiers:
            continue
        if rng.random() < p:
            return tag
    return ""

def bonus_of(word, rng):
    for tag, p in BONUS.get((word or "").strip(), ()):
        if rng.random() < p:
            return tag
    return ""

def fill_from_set(rng, name, full=True, p_outer=0.6, p_onepiece=0.5):
    pool = SETS.get(name)
    if not pool:
        return {}
    slots = pool["slots"]
    skip = set() if full else {"head"}
    picked, used = {}, set()

    def take(slot):
        if slot not in slots:
            return None
        _vp = VACANT_P.get(slot, 0.0)
        if _vp and rng.random() < _vp:
            return None
        it = pick_item(rng, slots[slot])
        if not it:
            return None
        _var = variant_of(it[0], rng)
        if _var:
            picked[slot] = (_var[0], _var[1])
        else:
            picked[slot] = (it[0], it[1])
        _sty = stylize_of(picked[slot][0], rng, pool["tier"])
        if _sty:
            picked["__stylize__"] = (_sty, "质感")
        if pool["tier"] == "tease":
            _b = bonus_of(it[0], rng)
            if _b:
                picked["__bonus__"] = (_b, "附带")
        for s in it[2]:
            used.add(s)
        return it

    for slot in ORDER:
        if slot in skip:
            continue
        if slot == "upper":
            if "upper_set" in slots and rng.random() < p_onepiece:
                take("upper_set")
                continue
            take("upper_base")
            if "upper_outer" in slots and rng.random() < p_outer:
                take("upper_outer")
            continue
        if slot == "lower":
            if "lower" in used:
                continue
            it = take("lower")
            if it and any(k in it[0].lower() for k in _LONG_KW):
                used.add("leg_l")
            continue
        if slot == "leg_l" and "leg_l" in used:
            continue
        take(slot)
    return picked
