ANGLES = [
    ("above", "from above, high angle"),
    ("below", "from below, low angle"),
    ("dutch", "dutch angle, tilted camera"),
    ("onepoint", "one point perspective"),
]
ANGLE_WEIGHTS = [34, 26, 28, 12]

SCALES = [
    ("full", "full body"),
    ("upper", "upper body"),
    ("closeup", "close-up, portrait"),
    ("cowboy", "cowboy shot, from head to thighs"),
]
SCALE_WEIGHTS = [40, 28, 22, 10]

POSITIONS = [
    ("center", "centered composition"),
    ("golden", "golden ratio composition, subject at the golden focal point"),
    ("framed", "framed composition, subject framed by the surrounding architecture"),
]
POSITION_WEIGHTS = [44, 30, 26]

LENSES = [
    ("none", ""),
    ("wide", "wide angle lens, 24mm, exaggerated perspective, strong depth"),
]
LENS_WEIGHTS = [60, 40]

FOREGROUND = ("a soft-focus tree branch entering from the upper corner, "
              "blurred leaves, bokeh foreground")
FG_CHANCE_GUOFENG = 1.0
FG_CHANCE_OTHER = 0.30

ANGLE_SCALE_MUTEX = {
    "below": ("full",),
    "above": ("cowboy",),
    "onepoint": ("closeup",),
}
POSITION_SCALE_MUTEX = {
    "framed": ("closeup",),
}
ANGLE_POSITION_MUTEX = {
    "dutch": ("center",),
}
