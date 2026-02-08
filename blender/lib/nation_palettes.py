"""
Per-nation color palettes for material overrides.
When a nation is specified, the banner, trim, and accent colors
are swapped to match the nation's identity.
"""

# Each nation defines overrides applied on top of age materials.
# Keys match material dict keys from materials.init_materials().
NATION_PALETTES = {
    'romans': {
        'banner': (0.55, 0.00, 0.00),   # Deep red
        'gold':   (0.85, 0.68, 0.15),    # Standard gold
        'trim':   (0.85, 0.68, 0.15),    # Gold trim
    },
    'greeks': {
        'banner': (0.12, 0.56, 1.0),     # Blue
        'gold':   (0.90, 0.80, 0.30),    # Pale gold
        'trim':   (0.90, 0.90, 0.88),    # White marble trim
    },
    'egyptians': {
        'banner': (0.77, 0.63, 0.20),    # Gold-sand
        'gold':   (0.85, 0.70, 0.10),    # Rich gold
        'trim':   (0.18, 0.10, 0.05),    # Dark brown
    },
    'chinese': {
        'banner': (0.80, 0.00, 0.00),    # Red
        'gold':   (1.0, 0.84, 0.00),     # Bright gold
        'trim':   (0.10, 0.10, 0.10),    # Black lacquer
    },
    'japanese': {
        'banner': (0.74, 0.00, 0.18),    # Crimson
        'gold':   (0.85, 0.68, 0.15),    # Gold
        'trim':   (0.95, 0.95, 0.93),    # White
    },
    'vikings': {
        'banner': (0.18, 0.31, 0.31),    # Dark teal
        'gold':   (0.75, 0.75, 0.73),    # Silver
        'trim':   (0.55, 0.35, 0.15),    # Warm brown
    },
    'british': {
        'banner': (0.00, 0.14, 0.49),    # Navy blue
        'gold':   (0.85, 0.68, 0.15),    # Gold
        'trim':   (0.81, 0.08, 0.17),    # Red accent
    },
    'persians': {
        'banner': (0.29, 0.00, 0.51),    # Purple
        'gold':   (0.85, 0.65, 0.00),    # Deep gold
        'trim':   (0.25, 0.88, 0.82),    # Turquoise accent
    },
}


def apply_nation_palette(materials, nation):
    """
    Override banner, gold, and trim colors in the material dict
    based on the nation palette. Modifies materials in place.
    """
    if nation not in NATION_PALETTES:
        return

    palette = NATION_PALETTES[nation]

    # Update banner color
    if 'banner' in materials and 'banner' in palette:
        bsdf = materials['banner'].node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (*palette['banner'], 1)

    # Update gold/accent color
    if 'gold' in materials and 'gold' in palette:
        bsdf = materials['gold'].node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (*palette['gold'], 1)

    # Update stone trim to nation accent
    if 'stone_trim' in materials and 'trim' in palette:
        # For simple-ish tint, adjust the color ramp end color
        nodes = materials['stone_trim'].node_tree.nodes
        ramp = None
        for n in nodes:
            if n.type == 'VALTORGB':
                ramp = n
                break
        if ramp:
            tc = palette['trim']
            ramp.color_ramp.elements[1].color = (*tc, 1)
