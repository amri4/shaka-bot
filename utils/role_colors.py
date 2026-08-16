# =========================================
# ROLE COLORS
# =========================================

ROLE_COLORS = {

    # Basic
    "red": 0xFF0000,
    "orange": 0xFFA500,
    "yellow": 0xFFFF00,
    "green": 0x00FF00,
    "lime": 0x32CD32,
    "cyan": 0x00FFFF,
    "blue": 0x0000FF,
    "navy": 0x000080,
    "purple": 0x800080,
    "violet": 0xEE82EE,
    "pink": 0xFFC0CB,
    "magenta": 0xFF00FF,
    "white": 0xFFFFFF,
    "black": 0x000000,
    "gray": 0x808080,

    # Reds
    "crimson": 0xDC143C,
    "scarlet": 0xFF2400,
    "ruby": 0xE0115F,
    "darkred": 0x8B0000,
    "firebrick": 0xB22222,
    "maroon": 0x800000,
    "salmon": 0xFA8072,
    "coral": 0xFF7F50,
    "tomato": 0xFF6347,

    # Oranges / yellows
    "darkorange": 0xFF8C00,
    "gold": 0xFFD700,
    "amber": 0xFFBF00,
    "lemon": 0xFFF44F,
    "khaki": 0xF0E68C,
    "peach": 0xFFE5B4,

    # Greens
    "darkgreen": 0x006400,
    "forest": 0x228B22,
    "emerald": 0x50C878,
    "mint": 0x98FF98,
    "spring": 0x00FF7F,
    "olive": 0x808000,
    "seafoam": 0x9FE2BF,

    # Blues
    "darkblue": 0x00008B,
    "royalblue": 0x4169E1,
    "sky": 0x87CEEB,
    "azure": 0x007FFF,
    "steelblue": 0x4682B4,
    "midnight": 0x191970,
    "ocean": 0x0077BE,

    # Cyan / teal
    "teal": 0x008080,
    "darkcyan": 0x008B8B,
    "turquoise": 0x40E0D0,
    "aqua": 0x00FFFF,
    "aquamarine": 0x7FFFD4,

    # Purples
    "darkpurple": 0x4B0082,
    "darkviolet": 0x9400D3,
    "indigo": 0x4B0082,
    "lavender": 0xE6E6FA,
    "plum": 0xDDA0DD,
    "grape": 0x6F2DA8,
    "amethyst": 0x9966CC,

    # Pinks
    "darkpink": 0xC71585,
    "hotpink": 0xFF69B4,
    "rose": 0xFF007F,
    "blush": 0xDE5D83,
    "bubblegum": 0xFFC1CC,

    # Browns
    "brown": 0xA52A2A,
    "darkbrown": 0x5C4033,
    "chocolate": 0xD2691E,
    "tan": 0xD2B48C,
    "beige": 0xF5F5DC,
    "coffee": 0x6F4E37,

    # Grays
    "darkgray": 0x555555,
    "lightgray": 0xD3D3D3,
    "silver": 0xC0C0C0,
    "slate": 0x708090,
    "charcoal": 0x36454F,
}


def parse_role_color(value):

    value = value.lower().strip()

    # Named color
    if value in ROLE_COLORS:
        return ROLE_COLORS[value]

    # Hex color
    if value.startswith("#"):
        value = value[1:]

    if len(value) == 6:

        try:
            return int(value, 16)

        except ValueError:
            pass

    return None
