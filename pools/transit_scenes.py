TRANSIT = {

"bus": {
  "cn": "公交车",
  "props": ["bus interior", "bus seat", "handrail", "window", "fare box"],
  "daily_1": [
    ("she is standing by the pole holding the handrail, swaying with the bus, looking out the window",
     "她扶着立柱站在车上，随车身轻晃，望着窗外", "pose+prop"),
    ("she is sitting by the window with her bag on her lap, watching the street go by",
     "她靠窗坐着，包放腿上，看街景流过", "pose+prop"),
    ("they are standing side by side, sharing one earbud, quietly talking",
     "两人并排站着，共用一副耳机，小声聊天", "inter"),
  ],
  "daily_2": [
    ("she is leaning against him as the bus turns, one hand on his arm to steady herself",
     "车转弯她顺势靠向他，一只手扶着他手臂稳住", "inter+motion"),
    ("she is sitting on the inside seat with her shoulder pressed to his, half asleep and nodding",
     "她坐里座，肩靠着他，困得点头打盹", "pose+expr"),
    ("she is standing in front of him holding the same pole, his other hand resting on her back",
     "她站在他身前扶同一根立柱，他另一只手护在她背上", "inter"),
  ],
  "daily_3": [
    ("she is dozing off with her head on his shoulder, the bus nearly empty now, late light through the windows",
     "车快空了，她把头靠在他肩上打盹，夕照透进窗", "pose+expr"),
    ("they are the last two on the bus, sitting close, talking quietly the whole way",
     "车上只剩他俩，一路挨着小声说话", "inter"),
  ],
  "flirt": [
    ("she is sitting on his lap in the empty back row, her hand resting on his thigh, biting her lip",
     "末排空座上她坐在他腿上，一只手按在他大腿，咬着唇", "inter+expr"),
    ("they are standing in the back corner, her back to his chest, swaying with every turn",
     "两人站在车尾角落，她背贴着他胸口，随每次转弯晃", "inter+motion"),
  ],
  "variants": [
    ("she is holding the handrail with both hands, pressed in by the crowd, keeping her eyes down",
     "她双手抓扶手，被人群挤着，低着头", "pose"),
    ("she is threading through the crowded aisle toward the door, muttering 'excuse me'",
     "她挤过拥挤过道往车门走，小声说借过", "act+motion"),
  ],
},

"taxi": {
  "cn": "出租车",
  "props": ["taxi interior", "back seat", "taxi window", "taxi meter"],
  "daily_1": [
    ("she is sitting on the back seat looking out the window, her handbag beside her, city lights sliding by",
     "她坐后座看窗外，包放旁边，城市灯火流过", "pose+prop"),
    ("she is giving the driver an address while he leans in from the other door",
     "她跟司机报地址，他从另一侧上车", "act"),
    ("they are both on the back seat, her head tilted back against the headrest, tired but smiling",
     "两人都在后座，她头靠头枕，累但笑着", "pose+expr"),
  ],
  "daily_2": [
    ("she is leaning her head on his shoulder in the back seat while the meter ticks",
     "后座上她把头靠在他肩上，计价器一跳一跳", "inter"),
    ("she is holding his hand on the seat between them, watching the road ahead",
     "她握着座位中间他的手，看着前方的路", "inter"),
    ("she is whispering something to him so the driver will not hear, hand cupped by his ear",
     "她凑到他耳边小声说，免得司机听见", "inter+act"),
  ],
  "daily_3": [
    ("she is half asleep against the window, forehead on the glass, the taxi humming",
     "她额头抵着车窗半睡，车里嗡嗡的", "pose+motion"),
    ("they are almost home, her hand still in his, both quiet and content",
     "快到家了，两人的手还牵着，安静而满足", "inter"),
  ],
  "flirt": [
    ("she is sitting on his lap on the back seat with the partition up, watching the driver's mirror",
     "后座隔板已经拉上，她坐在他腿上，盯着司机那面镜子", "inter+gaze"),
    ("his hand is resting high on her thigh in the dark of the back seat, her breath going shallow",
     "后座昏暗里他的手搁在她大腿高处，她呼吸变浅", "inter"),
  ],
  "variants": [
    ("she is checking her phone in the back seat, showing him something funny on the screen",
     "她后座刷手机，给他看屏幕上好玩的东西", "act+prop"),
    ("she is paying through the window while he holds the door open for her",
     "她隔着车窗扫码付钱，他扶着车门等她", "act"),
  ],
},

"subway": {
  "cn": "地铁",
  "props": ["subway car", "subway seat", "handrail", "platform", "ticket gate"],
  "daily_1": [
    ("she is standing in the subway car holding the overhead rail, looking at the ads across from her",
     "她在地铁车厢里扶着吊环，看对面广告", "pose+prop"),
    ("they are on the platform waiting for the train, her hand in his so they do not get separated",
     "两人在站台等车，她牵着他的手怕走散", "inter"),
    ("she is sitting on the subway seat with her bag between her feet, checking the map on the wall",
     "她坐地铁座位上，包夹在脚间，看墙上的线路图", "pose+act"),
  ],
  "daily_2": [
    ("she is standing in front of him holding the same overhead rail, his arms boxed around her in the crowd",
     "她站在他身前扶同一根吊环，人群里他双臂圈着她", "inter+pose"),
    ("she is pressed against his side when the train lurches, both laughing it off",
     "列车一晃她整个人撞到他身上，两人都笑了", "inter+motion"),
    ("she is telling him which station to get off at, one finger tapping the glass map",
     "她告诉他哪站下，手指敲着玻璃线路图", "act+gaze"),
  ],
  "daily_3": [
    ("they are riding the last train, the car mostly empty, her head on his shoulder, the windows black",
     "末班车，车厢几乎空了，她头靠他肩，窗外漆黑", "pose+expr"),
    ("she is standing at the door holding the rail, watching the tunnel lights strobe past",
     "她站在门边扶栏杆，看隧道灯一闪一闪掠过", "pose+motion"),
  ],
  "flirt": [
    ("she is standing in the corner of the car with her back to his chest, his hand sliding to her waist in the crush",
     "车厢角落里她背贴他胸口，拥挤中他的手滑到她腰上", "inter+pose"),
    ("they are pressed together in the crowd, her fingers hooked in his belt loop, eyes locked",
     "人群里两人贴在一起，她手指勾着他裤腰，四目相对", "inter+gaze"),
  ],
  "variants": [
    ("she is scanning her card at the ticket gate, looking over her shoulder for him",
     "她在闸机口刷卡，回头找他", "act+gaze"),
    ("she is standing on the escalator, hand on the rail, waiting for him to catch up",
     "她站在扶梯上，手扶梯带，等他和自己并排", "pose"),
  ],
},

"driving": {
  "cn": "自己开车",
  "props": ["car interior", "driver seat", "passenger seat", "steering wheel", "rearview mirror"],
  "daily_1": [
    ("she is in the passenger seat with the window down, one hand out catching the wind",
     "她坐副驾开着窗，一只手伸出去兜风", "pose+prop"),
    ("he is driving and she is reading the navigation, telling him where to turn",
     "他开车她看导航，告诉他在哪转", "act+inter"),
    ("she is buckling her seatbelt, looking up at him to say she is ready",
     "她系好安全带，抬头跟他说可以走了", "act+gaze"),
  ],
  "daily_2": [
    ("she is resting her bare feet on the dashboard, singing along to the radio",
     "她把脚搭在仪表盘上，跟着电台唱歌", "pose+prop"),
    ("she is leaning over and feeding him a snack while he keeps one hand on the wheel",
     "她凑过去喂他吃零食，他单手扶方向盘", "inter"),
    ("she is rolling the window back up as the rain starts, laughing at how fast the weather turned",
     "开始下雨了她把车窗摇上，笑天气变得真快", "act+expr"),
  ],
  "daily_3": [
    ("she is asleep in the passenger seat with his jacket over her, the highway lights going by",
     "她盖着他外套在副驾睡着，高速路灯一盏盏过去", "pose+motion"),
    ("she is sitting up again as he parks, stretching with both arms",
     "他停车时她坐直了伸个懒腰", "pose"),
  ],
  "flirt": [
    ("she is leaning over the center console to kiss him at a red light, one hand on the back of his neck",
     "红灯时她探过中央扶手去吻他，一只手扶着他后颈", "inter"),
    ("she is unbuckling his belt and sliding down in the passenger seat while he keeps his eyes on the road",
     "她解开他腰带在副驾俯下身，他眼睛还盯着路面", "inter+act"),
  ],
  "variants": [
    ("she is taking a photo out the window of the scenery flying past",
     "她对着窗外掠过的风景拍照", "act+prop"),
    ("she is handing him a coffee from the cup holder and taking a sip of her own",
     "她从杯架递给他咖啡，自己也喝一口", "act"),
  ],
},

"cycling": {
  "cn": "骑车",
  "props": ["bicycle", "handlebar", "bike basket", "bike path", "bell"],
  "daily_1": [
    ("she is holding the handlebars of a rental bike, testing the bell twice",
     "她握着租来的单车车把，按了两下车铃", "act+prop"),
    ("they are unlocking their bikes side by side at the stand, talking about the route",
     "两人在车架旁并排开锁，商量走哪条路", "inter"),
    ("she is pedaling slowly beside him on a tree-lined bike path, hair lifting in the wind",
     "她沿着林荫车道慢慢骑在他旁边，头发被风掀起来", "pose+motion"),
  ],
  "daily_2": [
    ("she is riding ahead and looking back over her shoulder to see if he is keeping up",
     "她骑在前头回头看，看他跟没跟上", "pose+gaze"),
    ("they are stopped on a small bridge, leaning on the handlebars, watching the river",
     "两人停在小桥上，靠着车把看河", "pose+prop"),
    ("she is ringing the bell at a slow walker and apologizing with a sheepish smile",
     "她朝前面慢走的人按了下铃，不好意思地笑", "act+expr"),
  ],
  "daily_3": [
    ("she is coasting downhill with both feet off the pedals, laughing out loud",
     "她顺着下坡滑行，双脚离开踏板，笑出声", "pose+motion"),
    ("they are pushing their bikes back at dusk, too tired to ride, shoulders touching",
     "黄昏时两人推着车走回去，累得不想骑了，肩膀挨着", "act+inter"),
  ],
  "flirt": [
    ("they are stopped in a hidden corner of the park, her back against a tree, the bikes leaning nearby",
     "两人停在公园隐蔽角落，她背靠树，两辆车斜靠在旁", "inter"),
    ("she is standing straddling the bike with his hands on her waist, glancing around for anyone watching",
     "她跨站在车边，他双手扶着她腰，她四顾看有没有人", "inter+gaze"),
  ],
  "variants": [
    ("she is adjusting her seat height with a wrench, tongue between her teeth",
     "她拿扳手调坐垫高度，咬着舌尖很专注", "act+expr"),
    ("she is putting a water bottle into the basket and buckling the strap",
     "她把水壶放进车筐，扣好带子", "act+prop"),
  ],
},

"motorcycle": {
  "cn": "摩托车",
  "props": ["motorcycle", "helmet", "leather seat", "engine", "headlight"],
  "daily_1": [
    ("she is buckling on a helmet and swinging her leg over the back seat",
     "她系好头盔，抬腿跨上后座", "act+prop"),
    ("he is kicking the engine to life and she is holding the grab bar behind her",
     "他打火起步，她抓着身后的扶手", "act"),
    ("they are pulling out of the parking lot, her arms loose at her sides",
     "两人开出停车场，她双臂还松着", "motion"),
  ],
  "daily_2": [
    ("she is holding his waist as they ride out of the city, wind pressing her jacket flat",
     "出城路上她抱着他的腰，风把外套压平", "inter+motion"),
    ("she is sitting behind him with her chin near his shoulder, watching the road unroll",
     "她坐在他身后，下巴靠近他肩头，看路在眼前铺开", "pose+motion"),
    ("they are stopped at a light, her helmet tilted until it touches his",
     "红灯前停下，她头盔一歪，靠到他头盔上", "inter"),
  ],
  "daily_3": [
    ("they are parked on a hill overlook, helmets off, hair messed up, looking at the view",
     "停在山顶观景处，头盔摘了，头发乱糟糟，看风景", "pose+prop"),
    ("she is taking off her helmet with both hands and shaking her hair loose",
     "她双手摘头盔，甩了甩头发", "act"),
  ],
  "flirt": [
    ("she is pressed against his back on a deserted road, her hands sliding from his waist to his chest",
     "无人的路上她贴着他后背，双手从他腰滑到胸口", "inter"),
    ("they are parked in a dark underpass, she is perched on the tank facing him, holding his shoulders",
     "停在昏暗的桥洞下，她面朝他坐在油箱上，扶着他肩膀", "inter+pose"),
  ],
  "variants": [
    ("she is checking the tire pressure while he wipes the mirror",
     "她检查胎压，他擦后视镜", "act"),
    ("she is putting on gloves and tucking her scarf in so it will not flap",
     "她戴手套把围巾塞好，免得飘起来", "act+prop"),
  ],
},
}

def keys():
    return list(TRANSIT)

def info(k):
    return TRANSIT[k]["cn"], TRANSIT[k]["props"]

def pick(k, appearance, rng, flirt=False):
    t = TRANSIT[k]
    if flirt:
        pool = t["flirt"]
    else:
        pool = t["daily_1"] if appearance <= 1 else (t["daily_2"] if appearance == 2 else t["daily_3"])
    return rng.choice(pool)

def variants(k):
    return TRANSIT[k]["variants"]

if __name__ == "__main__":
    import random
    rng = random.Random(1)
    total = 0
    print(f"交通场景 {len(TRANSIT)} 个\n")
    for k, t in TRANSIT.items():
        n = sum(len(t[x]) for x in ("daily_1", "daily_2", "daily_3", "flirt", "variants"))
        total += n
        print(f"  {t['cn']:<8} 链 {len(t['daily_1'])}/{len(t['daily_2'])}/{len(t['daily_3'])}"
              f" + 走火 {len(t['flirt'])} + 变种 {len(t['variants'])} = {n} 条")
    print(f"\n  合计 {total} 条")
    print("\n【公交 · 第 1/2/3 次出现 + 走火 各抽一条】")
    for ap in (1, 2, 3):
        en, cn, slot = pick("bus", ap, rng)
        print(f"   第{ap}次 [{slot:<10}] {en[:70]}")
    en, cn, slot = pick("bus", 1, rng, flirt=True)
    print(f"   走火  [{slot:<10}] {en[:70]}")
    bad = [(k, x, i, e) for k, t in TRANSIT.items() for x in t for i, e in enumerate(t[x])
           if not (isinstance(e, tuple) and len(e) == 3 and e[2])]
    print(f"\n  格式校验（每条=英/中/槽位 且槽位非空）: {'✅ 全通过' if not bad else f'✗ {bad[:2]}'}")
