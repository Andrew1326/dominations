"""
Nation-specific town center dispatch.
Each nation has unique architecture per age, not just color swaps.
"""

NATION_BUILDERS = {}

try:
    from buildings.tc_chinese import build_town_center_chinese
    NATION_BUILDERS['chinese'] = build_town_center_chinese
except ImportError:
    pass

try:
    from buildings.tc_japanese import build_town_center_japanese
    NATION_BUILDERS['japanese'] = build_town_center_japanese
except ImportError:
    pass

try:
    from buildings.tc_egyptians import build_town_center_egyptians
    NATION_BUILDERS['egyptians'] = build_town_center_egyptians
except ImportError:
    pass

try:
    from buildings.tc_vikings import build_town_center_vikings
    NATION_BUILDERS['vikings'] = build_town_center_vikings
except ImportError:
    pass

try:
    from buildings.tc_romans import build_town_center_romans
    NATION_BUILDERS['romans'] = build_town_center_romans
except ImportError:
    pass

try:
    from buildings.tc_greeks import build_town_center_greeks
    NATION_BUILDERS['greeks'] = build_town_center_greeks
except ImportError:
    pass

try:
    from buildings.tc_british import build_town_center_british
    NATION_BUILDERS['british'] = build_town_center_british
except ImportError:
    pass

try:
    from buildings.tc_persians import build_town_center_persians
    NATION_BUILDERS['persians'] = build_town_center_persians
except ImportError:
    pass
