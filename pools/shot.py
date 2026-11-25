ANGLES = [
    ("eye_level",     "eye-level shot",           40),
    ("slightly_above", "slightly high angle",      12),
    ("slightly_below", "slightly low angle",       12),
    ("above",         "from above, high angle",    10),
    ("below",         "from below, low angle",     10),
    ("dutch",         "dutch angle, tilted frame",  8),
    ("onepoint",      "one-point perspective",      8),
]
ANGLE_WEIGHTS = [w for _, _, w in ANGLES]
ANGLE_DISTANCE_MUTEX = {
    "above": {"extreme_closeup"},
    "below": {"extreme_closeup"},
}

DISTANCES = [
    ("extreme_closeup", "extreme close-up",                        6),
    ("closeup",         "close-up, portrait",                     14),
    ("upper",           "upper body",                             20),
    ("cowboy",          "cowboy shot, from head to mid-thigh",     8),
    ("full",            "full body",                              22),
    ("none",            "",                                       30),
]
DISTANCE_WEIGHTS = [w for _, _, w in DISTANCES]

POSITIONS = [
    ("center",  "centered composition",                                34),
    ("golden",  "golden ratio composition",                            18),
    ("framed",  "framed composition",                                  14),
    ("",        "",                                                    10),
]

LENSES = [
    ("none", "none_lens",  50),
    ("wide", "wide angle lens, exaggerated perspective", 30),
]

FOREGROUND = "a soft-focus foreground element framing the shot"

FACING = [
    ("front",       "facing the viewer, front view",                    34),
    ("threequarter", "three-quarter view, facing slightly to the side", 26),
    ("side",        "profile view, facing to the side",                 16),
    ("back",        "facing away from the viewer, back turned",         24),
]
FACING_WEIGHTS = [w for _, _, w in FACING]

FACING_GAZE_MUTEX = {
    "back": {
        "looking at viewer", "looking at camera", "eye contact",
        "gentle soft gaze", "cool confident look", "looking up at viewer",
    },
    "side": {"looking at viewer", "looking at camera", "eye contact"},
    "front": {"looking over her shoulder"},
}
FACING_BODY_MUTEX = {
    "back": {
        "nipples fully visible", "nipples visible", "nipple fully visible",
        "nipples showing through the fabric", "breasts exposed", "both breasts exposed",
        "bare breasts", "bare breasts with hard nipples", "hard nipples",
        "one breast out of her clothing", "top pulled up over her breasts",
        "bra pulled down completely", "clothing pulled open",
        "cleavage visible", "cleavage spilling out", "underboob", "sideboob",
        "close-up on face", "close-up on breasts", "close-up on chest",
        "soft bare stomach",
    },
    "front": {
        "bare buttocks", "anus visible", "pussy visible from the rear",
        "back and buttocks visible", "buttocks partially visible",
        "rear focus", "facing away from the viewer", "back turned",
        "clothing riding up", "panty line visible",
    },
}

FRAMING_PARTS = {
    "full":     ("body", "head", "hand", "leg"),
    "upper":    ("head", "hand"),
    "closeup":  ("head",),
    "extreme":  (),
}

FRAMING_LENS_OK = {
    "full":     ("none", "wide"),
    "upper":    ("none",),
    "closeup":  ("none",),
    "extreme":  ("none",),
}

FRAMING_ANGLE_BAN = {
    "full": (),
    "upper": ("above", "below"),
    "closeup": ("above", "below"),
    "extreme": (),
}

FRAMING_BY_TIER = {
    "fashion": {"full": 88, "upper": 0, "closeup": 12, "extreme": 0},
    "tease":   {"full": 30, "upper": 70, "closeup": 0, "extreme": 0},
    "exposed": {"full": 35, "upper": 35, "closeup": 0, "extreme": 30},
    "sex":     {"full": 40, "upper": 35, "closeup": 0, "extreme": 25},
}

CLOSEUP_TIERS = ("fashion",)

FRAMING_TO_VIS = {
    "full":     ("full",),
    "upper":    ("upper",),
    "closeup":  ("closeup",),
    "extreme":  ("xchest", "xpussy"),
}

FRAMING_SLOTS = {
    "closeup":  ("head", "ears", "neck", "upper"),
    "upper":    ("head", "ears", "neck", "upper", "wrist", "hands", "waist"),
    "full":     ("head", "ears", "neck", "upper", "lower", "waist",
                 "legs", "feet", "wrist", "hands"),
    "extreme":  ("head",),
}

FRAMING_HIDDEN_KW = {
    "closeup": ("thigh", "leg", "knee", "calf", "ankle", "foot", "feet", "toe",
                "hip", "waist", "skirt", "shorts", "pants"),
    "upper":   ("thigh", "knee", "calf", "ankle", "foot", "feet", "toe"),
    "full":    (),
    "extreme": ("thigh", "leg", "knee", "calf", "ankle", "foot", "feet", "toe", "hip"),
}

def slot_visible(slot, framing):
    return slot in FRAMING_SLOTS.get(framing, FRAMING_SLOTS["full"])
