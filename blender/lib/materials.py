"""
Age-aware procedural material factory.
Every material has roughness variation, micro-bump, and surface imperfections
to avoid the "plastic" look. No flat-color materials.

Materials change appearance based on the civilization age:
  - Stone: rough noise, mud/thatch
  - Bronze/Iron: clay brick, early masonry
  - Classical: marble, columns
  - Medieval: half-timber + brick (current default)
  - Industrial+: clean brick, metal, glass
"""

import bpy


# ============================================================
# Shader node helpers
# ============================================================

def _get_nodes(mat):
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    return nodes, links, bsdf


def _add_roughness_variation(nodes, links, bsdf, base_roughness, variation=0.15, scale=15.0):
    """Add noise-driven roughness variation so surfaces don't look uniformly smooth/rough."""
    coord = None
    for n in nodes:
        if n.type == 'TEX_COORD':
            coord = n
            break
    if not coord:
        coord = nodes.new('ShaderNodeTexCoord')

    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = scale
    noise.inputs['Detail'].default_value = 4.0
    noise.inputs['Roughness'].default_value = 0.6
    links.new(coord.outputs['Object'], noise.inputs['Vector'])

    # Map noise (0-1) to roughness range
    ramp = nodes.new('ShaderNodeValToRGB')
    lo = max(0.0, base_roughness - variation)
    hi = min(1.0, base_roughness + variation)
    ramp.color_ramp.elements[0].color = (lo, lo, lo, 1)
    ramp.color_ramp.elements[1].color = (hi, hi, hi, 1)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Roughness'])
    return noise


def _add_micro_bump(nodes, links, bsdf, strength=0.15, scale=40.0):
    """Add fine micro-detail bump for surface imperfections."""
    coord = None
    for n in nodes:
        if n.type == 'TEX_COORD':
            coord = n
            break
    if not coord:
        coord = nodes.new('ShaderNodeTexCoord')

    micro = nodes.new('ShaderNodeTexNoise')
    micro.inputs['Scale'].default_value = scale
    micro.inputs['Detail'].default_value = 8.0
    micro.inputs['Roughness'].default_value = 0.9
    links.new(coord.outputs['Object'], micro.inputs['Vector'])

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = strength
    bump.inputs['Distance'].default_value = 0.005
    links.new(micro.outputs['Fac'], bump.inputs['Height'])

    # Chain with existing normal if one exists
    existing_normal = bsdf.inputs['Normal'].links
    if existing_normal:
        bump.inputs['Normal'].default_value = (0, 0, 0)
        links.new(existing_normal[0].from_socket, bump.inputs['Normal'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    else:
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return bump


def _add_dirt_layer(nodes, links, color_socket, dirt_color=(0.12, 0.10, 0.07), amount=0.12, scale=3.0):
    """Add a dirt/weathering overlay — darkens crevices and bottom edges."""
    coord = None
    for n in nodes:
        if n.type == 'TEX_COORD':
            coord = n
            break
    if not coord:
        coord = nodes.new('ShaderNodeTexCoord')

    # Low-frequency noise for dirt patches
    dirt_noise = nodes.new('ShaderNodeTexNoise')
    dirt_noise.inputs['Scale'].default_value = scale
    dirt_noise.inputs['Detail'].default_value = 3.0
    dirt_noise.inputs['Roughness'].default_value = 0.5
    links.new(coord.outputs['Object'], dirt_noise.inputs['Vector'])

    # Separate Z for height-based darkening (more dirt at bottom)
    sep = nodes.new('ShaderNodeSeparateXYZ')
    links.new(coord.outputs['Object'], sep.inputs['Vector'])

    # Invert Z so bottom = 1 (more dirt), top = 0
    invert_z = nodes.new('ShaderNodeMath')
    invert_z.operation = 'SUBTRACT'
    invert_z.inputs[0].default_value = 1.0
    links.new(sep.outputs['Z'], invert_z.inputs[1])

    # Combine noise and height factor
    combine = nodes.new('ShaderNodeMath')
    combine.operation = 'MULTIPLY'
    links.new(dirt_noise.outputs['Fac'], combine.inputs[0])
    links.new(invert_z.outputs['Value'], combine.inputs[1])

    # Clamp
    clamp = nodes.new('ShaderNodeClamp')
    clamp.inputs['Min'].default_value = 0.0
    clamp.inputs['Max'].default_value = 1.0
    links.new(combine.outputs['Value'], clamp.inputs['Value'])

    # Mix dirt color with base color
    dirt_mix = nodes.new('ShaderNodeMixRGB')
    dirt_mix.blend_type = 'MIX'
    links.new(clamp.outputs['Result'], dirt_mix.inputs['Fac'])

    # Rewire: disconnect current color from BSDF, route through dirt mix
    if color_socket.links:
        src = color_socket.links[0].from_socket
        links.new(src, dirt_mix.inputs['Color1'])
    dirt_mix.inputs['Color2'].default_value = (*dirt_color, 1)

    # Scale fac down
    scale_fac = nodes.new('ShaderNodeMath')
    scale_fac.operation = 'MULTIPLY'
    scale_fac.inputs[1].default_value = amount
    links.new(clamp.outputs['Result'], scale_fac.inputs[0])

    dirt_mix2 = nodes.new('ShaderNodeMixRGB')
    dirt_mix2.blend_type = 'MIX'
    links.new(scale_fac.outputs['Value'], dirt_mix2.inputs['Fac'])
    if color_socket.links:
        src = color_socket.links[0].from_socket
        links.new(src, dirt_mix2.inputs['Color1'])
    dirt_mix2.inputs['Color2'].default_value = (*dirt_color, 1)
    links.new(dirt_mix2.outputs['Color'], color_socket)

    return dirt_mix2


# ============================================================
# Base procedural materials (age-neutral)
# ============================================================

def mat_stone_wall(name, base_color=(0.62, 0.55, 0.43), scale=8.0):
    """Stone wall — Voronoi irregular blocks + mortar joints + noise variation + weathering."""
    mat = bpy.data.materials.new(name)
    nodes, links, bsdf = _get_nodes(mat)

    coord = nodes.new('ShaderNodeTexCoord')

    # --- Voronoi for irregular stone blocks (replaces Brick Texture) ---
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.voronoi_dimensions = '3D'
    voronoi.feature = 'DISTANCE_TO_EDGE'
    voronoi.inputs['Scale'].default_value = scale
    voronoi.inputs['Randomness'].default_value = 0.85
    links.new(coord.outputs['Object'], voronoi.inputs['Vector'])

    # Mortar mask: edges → mortar, center → stone
    mortar_ramp = nodes.new('ShaderNodeValToRGB')
    mortar_ramp.color_ramp.elements[0].position = 0.0
    mortar_ramp.color_ramp.elements[0].color = (1, 1, 1, 1)  # mortar
    mortar_ramp.color_ramp.elements[1].position = 0.06
    mortar_ramp.color_ramp.elements[1].color = (0, 0, 0, 1)  # stone
    links.new(voronoi.outputs['Distance'], mortar_ramp.inputs['Fac'])

    # --- Stone color with noise variation ---
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 20.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.7
    links.new(coord.outputs['Object'], noise.inputs['Vector'])

    # Large-scale stain/discoloration
    stain = nodes.new('ShaderNodeTexNoise')
    stain.inputs['Scale'].default_value = 2.5
    stain.inputs['Detail'].default_value = 3.0
    stain.inputs['Roughness'].default_value = 0.4
    links.new(coord.outputs['Object'], stain.inputs['Vector'])

    r, g, b = base_color
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.color_ramp.elements[0].color = (r * 0.76, g * 0.76, b * 0.68, 1)
    color_ramp.color_ramp.elements[1].color = (r * 1.22, g * 1.18, b * 1.10, 1)
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])

    # Add stain overlay
    stain_mix = nodes.new('ShaderNodeMixRGB')
    stain_mix.blend_type = 'MULTIPLY'
    stain_mix.inputs['Fac'].default_value = 0.12
    links.new(color_ramp.outputs['Color'], stain_mix.inputs['Color1'])
    links.new(stain.outputs['Color'], stain_mix.inputs['Color2'])

    # Mix stone color with mortar
    mortar_color = (r * 0.48, g * 0.48, b * 0.42)
    stone_mortar = nodes.new('ShaderNodeMixRGB')
    stone_mortar.blend_type = 'MIX'
    links.new(mortar_ramp.outputs['Color'], stone_mortar.inputs['Fac'])
    links.new(stain_mix.outputs['Color'], stone_mortar.inputs['Color1'])
    stone_mortar.inputs['Color2'].default_value = (*mortar_color, 1)
    links.new(stone_mortar.outputs['Color'], bsdf.inputs['Base Color'])

    # Roughness with variation
    _add_roughness_variation(nodes, links, bsdf, 0.82, variation=0.15, scale=14.0)

    # --- Multi-scale bump ---
    # Coarse: voronoi edges (stones raised above mortar)
    bump_coarse = nodes.new('ShaderNodeBump')
    bump_coarse.inputs['Strength'].default_value = 0.6
    bump_coarse.inputs['Distance'].default_value = 0.03
    links.new(voronoi.outputs['Distance'], bump_coarse.inputs['Height'])

    # Medium: surface noise
    bump_med = nodes.new('ShaderNodeBump')
    bump_med.inputs['Strength'].default_value = 0.3
    bump_med.inputs['Distance'].default_value = 0.015
    links.new(noise.outputs['Fac'], bump_med.inputs['Height'])
    links.new(bump_coarse.outputs['Normal'], bump_med.inputs['Normal'])

    # Fine: micro-detail
    fine_noise = nodes.new('ShaderNodeTexNoise')
    fine_noise.inputs['Scale'].default_value = 55.0
    fine_noise.inputs['Detail'].default_value = 10.0
    fine_noise.inputs['Roughness'].default_value = 0.9
    links.new(coord.outputs['Object'], fine_noise.inputs['Vector'])

    bump_fine = nodes.new('ShaderNodeBump')
    bump_fine.inputs['Strength'].default_value = 0.18
    bump_fine.inputs['Distance'].default_value = 0.007
    links.new(fine_noise.outputs['Fac'], bump_fine.inputs['Height'])
    links.new(bump_med.outputs['Normal'], bump_fine.inputs['Normal'])
    links.new(bump_fine.outputs['Normal'], bsdf.inputs['Normal'])

    # Dirt weathering
    _add_dirt_layer(nodes, links, bsdf.inputs['Base Color'],
                    dirt_color=(r * 0.28, g * 0.22, b * 0.15), amount=0.18, scale=2.5)

    return mat


def mat_stone_dark(name, base_color=(0.40, 0.36, 0.30)):
    """Dark stone for foundation — noise texture + roughness variation + bump."""
    mat = bpy.data.materials.new(name)
    nodes, links, bsdf = _get_nodes(mat)

    coord = nodes.new('ShaderNodeTexCoord')

    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 12.0
    noise.inputs['Detail'].default_value = 10.0
    noise.inputs['Roughness'].default_value = 0.7
    links.new(coord.outputs['Object'], noise.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*[c * 0.80 for c in base_color], 1)
    ramp.color_ramp.elements[1].color = (*[c * 1.12 for c in base_color], 1)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    # Roughness variation
    _add_roughness_variation(nodes, links, bsdf, 0.88, variation=0.10, scale=10.0)

    # Multi-scale bump
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.55
    bump.inputs['Distance'].default_value = 0.018
    links.new(noise.outputs['Fac'], bump.inputs['Height'])

    # Fine detail
    fine = nodes.new('ShaderNodeTexNoise')
    fine.inputs['Scale'].default_value = 45.0
    fine.inputs['Detail'].default_value = 8.0
    links.new(coord.outputs['Object'], fine.inputs['Vector'])

    bump_fine = nodes.new('ShaderNodeBump')
    bump_fine.inputs['Strength'].default_value = 0.18
    bump_fine.inputs['Distance'].default_value = 0.006
    links.new(fine.outputs['Fac'], bump_fine.inputs['Height'])
    links.new(bump.outputs['Normal'], bump_fine.inputs['Normal'])
    links.new(bump_fine.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


def mat_roof_tiles(name, base_color=(0.55, 0.22, 0.08)):
    """Roof tiles — wave texture + noise variation + weathering + bump."""
    mat = bpy.data.materials.new(name)
    nodes, links, bsdf = _get_nodes(mat)

    coord = nodes.new('ShaderNodeTexCoord')

    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'Y'
    wave.inputs['Scale'].default_value = 12.0
    wave.inputs['Distortion'].default_value = 2.5
    wave.inputs['Detail'].default_value = 5.0
    wave.inputs['Detail Scale'].default_value = 2.5
    links.new(coord.outputs['Object'], wave.inputs['Vector'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 22.0
    noise.inputs['Detail'].default_value = 6.0
    links.new(coord.outputs['Object'], noise.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    r, g, b = base_color
    ramp.color_ramp.elements[0].color = (r * 0.65, g * 0.65, b * 0.58, 1)
    ramp.color_ramp.elements[1].color = (r * 1.30, g * 1.22, b * 1.10, 1)
    links.new(wave.outputs['Fac'], ramp.inputs['Fac'])

    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'OVERLAY'
    mix.inputs['Fac'].default_value = 0.25
    links.new(ramp.outputs['Color'], mix.inputs['Color1'])
    links.new(noise.outputs['Color'], mix.inputs['Color2'])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])

    # Roughness variation
    _add_roughness_variation(nodes, links, bsdf, 0.78, variation=0.14, scale=14.0)

    # Multi-scale bump
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.65
    bump.inputs['Distance'].default_value = 0.025
    links.new(wave.outputs['Fac'], bump.inputs['Height'])

    fine = nodes.new('ShaderNodeTexNoise')
    fine.inputs['Scale'].default_value = 55.0
    fine.inputs['Detail'].default_value = 6.0
    links.new(coord.outputs['Object'], fine.inputs['Vector'])

    bump_fine = nodes.new('ShaderNodeBump')
    bump_fine.inputs['Strength'].default_value = 0.15
    bump_fine.inputs['Distance'].default_value = 0.005
    links.new(fine.outputs['Fac'], bump_fine.inputs['Height'])
    links.new(bump.outputs['Normal'], bump_fine.inputs['Normal'])
    links.new(bump_fine.outputs['Normal'], bsdf.inputs['Normal'])

    # Weathering on roof
    _add_dirt_layer(nodes, links, bsdf.inputs['Base Color'],
                    dirt_color=(r * 0.3, g * 0.35, b * 0.25), amount=0.12, scale=2.0)

    return mat


def mat_wood(name, base_color=(0.42, 0.26, 0.13)):
    """Wood — wave grain + knot noise + roughness variation + bump."""
    mat = bpy.data.materials.new(name)
    nodes, links, bsdf = _get_nodes(mat)

    coord = nodes.new('ShaderNodeTexCoord')

    # Grain
    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'X'
    wave.inputs['Scale'].default_value = 6.0
    wave.inputs['Distortion'].default_value = 5.0
    wave.inputs['Detail'].default_value = 4.0
    links.new(coord.outputs['Object'], wave.inputs['Vector'])

    # Knots / variation
    knot_noise = nodes.new('ShaderNodeTexNoise')
    knot_noise.inputs['Scale'].default_value = 4.0
    knot_noise.inputs['Detail'].default_value = 6.0
    knot_noise.inputs['Roughness'].default_value = 0.6
    links.new(coord.outputs['Object'], knot_noise.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    r, g, b = base_color
    ramp.color_ramp.elements[0].color = (r * 0.55, g * 0.52, b * 0.45, 1)
    ramp.color_ramp.elements[1].color = (r * 1.38, g * 1.30, b * 1.20, 1)
    links.new(wave.outputs['Fac'], ramp.inputs['Fac'])

    # Overlay knots
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'OVERLAY'
    mix.inputs['Fac'].default_value = 0.15
    links.new(ramp.outputs['Color'], mix.inputs['Color1'])
    links.new(knot_noise.outputs['Color'], mix.inputs['Color2'])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])

    # Roughness variation
    _add_roughness_variation(nodes, links, bsdf, 0.72, variation=0.15, scale=8.0)

    # Multi-scale bump
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.40
    bump.inputs['Distance'].default_value = 0.012

    grain_add = nodes.new('ShaderNodeMath')
    grain_add.operation = 'ADD'
    links.new(wave.outputs['Fac'], grain_add.inputs[0])
    links.new(knot_noise.outputs['Fac'], grain_add.inputs[1])
    links.new(grain_add.outputs['Value'], bump.inputs['Height'])

    # Fine surface detail
    fine = nodes.new('ShaderNodeTexNoise')
    fine.inputs['Scale'].default_value = 60.0
    fine.inputs['Detail'].default_value = 8.0
    links.new(coord.outputs['Object'], fine.inputs['Vector'])

    bump_fine = nodes.new('ShaderNodeBump')
    bump_fine.inputs['Strength'].default_value = 0.12
    bump_fine.inputs['Distance'].default_value = 0.004
    links.new(fine.outputs['Fac'], bump_fine.inputs['Height'])
    links.new(bump.outputs['Normal'], bump_fine.inputs['Normal'])
    links.new(bump_fine.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


def mat_ground(name, base_color=(0.48, 0.42, 0.30)):
    """Ground — multi-noise dirt/grass + strong bump + roughness variation."""
    mat = bpy.data.materials.new(name)
    nodes, links, bsdf = _get_nodes(mat)

    coord = nodes.new('ShaderNodeTexCoord')

    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.inputs['Scale'].default_value = 6.0
    noise1.inputs['Detail'].default_value = 12.0
    noise1.inputs['Roughness'].default_value = 0.8
    links.new(coord.outputs['Object'], noise1.inputs['Vector'])

    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.inputs['Scale'].default_value = 25.0
    noise2.inputs['Detail'].default_value = 5.0
    links.new(coord.outputs['Object'], noise2.inputs['Vector'])

    # Pebble-scale noise
    noise3 = nodes.new('ShaderNodeTexNoise')
    noise3.inputs['Scale'].default_value = 60.0
    noise3.inputs['Detail'].default_value = 4.0
    links.new(coord.outputs['Object'], noise3.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    r, g, b = base_color
    ramp.color_ramp.elements[0].color = (r * 0.68, g * 0.75, b * 0.58, 1)
    ramp.color_ramp.elements[1].color = (r * 1.20, g * 1.15, b * 0.95, 1)
    links.new(noise1.outputs['Fac'], ramp.inputs['Fac'])

    mix1 = nodes.new('ShaderNodeMixRGB')
    mix1.blend_type = 'MULTIPLY'
    mix1.inputs['Fac'].default_value = 0.18
    links.new(ramp.outputs['Color'], mix1.inputs['Color1'])
    links.new(noise2.outputs['Color'], mix1.inputs['Color2'])

    mix2 = nodes.new('ShaderNodeMixRGB')
    mix2.blend_type = 'OVERLAY'
    mix2.inputs['Fac'].default_value = 0.08
    links.new(mix1.outputs['Color'], mix2.inputs['Color1'])
    links.new(noise3.outputs['Color'], mix2.inputs['Color2'])
    links.new(mix2.outputs['Color'], bsdf.inputs['Base Color'])

    # Roughness variation
    _add_roughness_variation(nodes, links, bsdf, 0.93, variation=0.06, scale=8.0)

    # Strong multi-scale bump for ground texture
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.7
    bump.inputs['Distance'].default_value = 0.03

    add_n = nodes.new('ShaderNodeMath')
    add_n.operation = 'ADD'
    links.new(noise1.outputs['Fac'], add_n.inputs[0])
    links.new(noise2.outputs['Fac'], add_n.inputs[1])
    links.new(add_n.outputs['Value'], bump.inputs['Height'])

    bump_fine = nodes.new('ShaderNodeBump')
    bump_fine.inputs['Strength'].default_value = 0.25
    bump_fine.inputs['Distance'].default_value = 0.008
    links.new(noise3.outputs['Fac'], bump_fine.inputs['Height'])
    links.new(bump.outputs['Normal'], bump_fine.inputs['Normal'])
    links.new(bump_fine.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


def mat_metal(name, color=(0.6, 0.6, 0.62), roughness=0.35, metallic=0.92):
    """Realistic metal — scratches, roughness variation, anisotropic look."""
    mat = bpy.data.materials.new(name)
    nodes, links, bsdf = _get_nodes(mat)

    coord = nodes.new('ShaderNodeTexCoord')

    # Base color with subtle noise variation
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 20.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.5
    links.new(coord.outputs['Object'], noise.inputs['Vector'])

    r, g, b = color
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (r * 0.88, g * 0.88, b * 0.88, 1)
    ramp.color_ramp.elements[1].color = (r * 1.08, g * 1.08, b * 1.08, 1)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Metallic'].default_value = metallic

    # Scratches via directional wave + noise for roughness
    scratches = nodes.new('ShaderNodeTexWave')
    scratches.wave_type = 'BANDS'
    scratches.bands_direction = 'X'
    scratches.inputs['Scale'].default_value = 30.0
    scratches.inputs['Distortion'].default_value = 8.0
    scratches.inputs['Detail'].default_value = 6.0
    links.new(coord.outputs['Object'], scratches.inputs['Vector'])

    roughness_noise = nodes.new('ShaderNodeTexNoise')
    roughness_noise.inputs['Scale'].default_value = 40.0
    roughness_noise.inputs['Detail'].default_value = 5.0
    links.new(coord.outputs['Object'], roughness_noise.inputs['Vector'])

    # Combine scratches with noise for roughness
    r_mix = nodes.new('ShaderNodeMath')
    r_mix.operation = 'ADD'
    links.new(scratches.outputs['Fac'], r_mix.inputs[0])
    links.new(roughness_noise.outputs['Fac'], r_mix.inputs[1])

    r_ramp = nodes.new('ShaderNodeValToRGB')
    lo = max(0.0, roughness - 0.12)
    hi = min(1.0, roughness + 0.18)
    r_ramp.color_ramp.elements[0].color = (lo, lo, lo, 1)
    r_ramp.color_ramp.elements[1].color = (hi, hi, hi, 1)
    links.new(r_mix.outputs['Value'], r_ramp.inputs['Fac'])
    links.new(r_ramp.outputs['Color'], bsdf.inputs['Roughness'])

    # Scratch bump
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.3
    bump.inputs['Distance'].default_value = 0.008
    links.new(scratches.outputs['Fac'], bump.inputs['Height'])

    # Micro imperfections
    micro = nodes.new('ShaderNodeTexNoise')
    micro.inputs['Scale'].default_value = 80.0
    micro.inputs['Detail'].default_value = 8.0
    links.new(coord.outputs['Object'], micro.inputs['Vector'])

    bump_micro = nodes.new('ShaderNodeBump')
    bump_micro.inputs['Strength'].default_value = 0.1
    bump_micro.inputs['Distance'].default_value = 0.003
    links.new(micro.outputs['Fac'], bump_micro.inputs['Height'])
    links.new(bump.outputs['Normal'], bump_micro.inputs['Normal'])
    links.new(bump_micro.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


def mat_glass(name, color=(0.82, 0.87, 0.92), ior=1.45, roughness=0.02):
    """Realistic glass with transmission, subtle imperfections."""
    mat = bpy.data.materials.new(name)
    nodes, links, bsdf = _get_nodes(mat)

    coord = nodes.new('ShaderNodeTexCoord')

    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Transmission Weight'].default_value = 0.85
    bsdf.inputs['IOR'].default_value = ior

    # Slight roughness variation for smudges/imperfections
    smudge = nodes.new('ShaderNodeTexNoise')
    smudge.inputs['Scale'].default_value = 25.0
    smudge.inputs['Detail'].default_value = 3.0
    links.new(coord.outputs['Object'], smudge.inputs['Vector'])

    r_ramp = nodes.new('ShaderNodeValToRGB')
    r_ramp.color_ramp.elements[0].color = (roughness, roughness, roughness, 1)
    r_ramp.color_ramp.elements[1].color = (roughness + 0.06, roughness + 0.06, roughness + 0.06, 1)
    links.new(smudge.outputs['Fac'], r_ramp.inputs['Fac'])
    links.new(r_ramp.outputs['Color'], bsdf.inputs['Roughness'])

    # Very subtle bump for surface texture
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.05
    bump.inputs['Distance'].default_value = 0.002

    micro = nodes.new('ShaderNodeTexNoise')
    micro.inputs['Scale'].default_value = 60.0
    micro.inputs['Detail'].default_value = 4.0
    links.new(coord.outputs['Object'], micro.inputs['Vector'])
    links.new(micro.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


def mat_fabric(name, color=(0.72, 0.10, 0.06), roughness=0.65):
    """Fabric/banner — woven texture + fuzz + roughness variation."""
    mat = bpy.data.materials.new(name)
    nodes, links, bsdf = _get_nodes(mat)

    coord = nodes.new('ShaderNodeTexCoord')

    # Weave pattern via two perpendicular waves
    wave1 = nodes.new('ShaderNodeTexWave')
    wave1.wave_type = 'BANDS'
    wave1.bands_direction = 'X'
    wave1.inputs['Scale'].default_value = 40.0
    wave1.inputs['Distortion'].default_value = 0.5
    wave1.inputs['Detail'].default_value = 2.0
    links.new(coord.outputs['Object'], wave1.inputs['Vector'])

    wave2 = nodes.new('ShaderNodeTexWave')
    wave2.wave_type = 'BANDS'
    wave2.bands_direction = 'Y'
    wave2.inputs['Scale'].default_value = 40.0
    wave2.inputs['Distortion'].default_value = 0.5
    wave2.inputs['Detail'].default_value = 2.0
    links.new(coord.outputs['Object'], wave2.inputs['Vector'])

    weave_mix = nodes.new('ShaderNodeMath')
    weave_mix.operation = 'ADD'
    links.new(wave1.outputs['Fac'], weave_mix.inputs[0])
    links.new(wave2.outputs['Fac'], weave_mix.inputs[1])

    # Color variation
    r, g, b = color
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (r * 0.72, g * 0.68, b * 0.62, 1)
    ramp.color_ramp.elements[1].color = (r * 1.22, g * 1.18, b * 1.12, 1)
    links.new(weave_mix.outputs['Value'], ramp.inputs['Fac'])

    # Fuzz noise
    fuzz = nodes.new('ShaderNodeTexNoise')
    fuzz.inputs['Scale'].default_value = 60.0
    fuzz.inputs['Detail'].default_value = 8.0
    fuzz.inputs['Roughness'].default_value = 0.8
    links.new(coord.outputs['Object'], fuzz.inputs['Vector'])

    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'OVERLAY'
    mix.inputs['Fac'].default_value = 0.10
    links.new(ramp.outputs['Color'], mix.inputs['Color1'])
    links.new(fuzz.outputs['Color'], mix.inputs['Color2'])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])

    # Roughness variation
    _add_roughness_variation(nodes, links, bsdf, roughness, variation=0.12, scale=30.0)

    # Weave bump
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.25
    bump.inputs['Distance'].default_value = 0.006
    links.new(weave_mix.outputs['Value'], bump.inputs['Height'])

    # Fuzz micro-bump
    bump_fuzz = nodes.new('ShaderNodeBump')
    bump_fuzz.inputs['Strength'].default_value = 0.08
    bump_fuzz.inputs['Distance'].default_value = 0.003
    links.new(fuzz.outputs['Fac'], bump_fuzz.inputs['Height'])
    links.new(bump.outputs['Normal'], bump_fuzz.inputs['Normal'])
    links.new(bump_fuzz.outputs['Normal'], bsdf.inputs['Normal'])

    # Slight sheen for fabric
    bsdf.inputs['Sheen Weight'].default_value = 0.3
    bsdf.inputs['Sheen Tint'].default_value = (*[min(1.0, c * 1.3) for c in color], 1)

    return mat


def mat_gold(name, color=(0.85, 0.68, 0.15)):
    """Gold — metallic with tarnish, scratches, and roughness variation."""
    mat = bpy.data.materials.new(name)
    nodes, links, bsdf = _get_nodes(mat)

    coord = nodes.new('ShaderNodeTexCoord')

    # Base gold with subtle color variation
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 15.0
    noise.inputs['Detail'].default_value = 5.0
    links.new(coord.outputs['Object'], noise.inputs['Vector'])

    r, g, b = color
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (r * 0.82, g * 0.78, b * 0.55, 1)
    ramp.color_ramp.elements[1].color = (r * 1.15, g * 1.12, b * 1.30, 1)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Metallic'].default_value = 0.95

    # Roughness: polished with tarnish patches
    tarnish = nodes.new('ShaderNodeTexNoise')
    tarnish.inputs['Scale'].default_value = 5.0
    tarnish.inputs['Detail'].default_value = 3.0
    tarnish.inputs['Roughness'].default_value = 0.4
    links.new(coord.outputs['Object'], tarnish.inputs['Vector'])

    scratches = nodes.new('ShaderNodeTexWave')
    scratches.wave_type = 'BANDS'
    scratches.inputs['Scale'].default_value = 50.0
    scratches.inputs['Distortion'].default_value = 10.0
    links.new(coord.outputs['Object'], scratches.inputs['Vector'])

    r_mix = nodes.new('ShaderNodeMath')
    r_mix.operation = 'ADD'
    links.new(tarnish.outputs['Fac'], r_mix.inputs[0])
    links.new(scratches.outputs['Fac'], r_mix.inputs[1])

    r_ramp = nodes.new('ShaderNodeValToRGB')
    r_ramp.color_ramp.elements[0].color = (0.15, 0.15, 0.15, 1)  # polished
    r_ramp.color_ramp.elements[1].color = (0.40, 0.40, 0.40, 1)  # tarnished
    links.new(r_mix.outputs['Value'], r_ramp.inputs['Fac'])
    links.new(r_ramp.outputs['Color'], bsdf.inputs['Roughness'])

    # Bump from scratches
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.15
    bump.inputs['Distance'].default_value = 0.004
    links.new(scratches.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


def mat_pbr(name, color, roughness=0.5, metallic=0.0):
    """PBR material with noise color variation, roughness variation, and micro-bump.
    Replaces the old mat_simple — nothing should look flat/plastic."""
    mat = bpy.data.materials.new(name)
    nodes, links, bsdf = _get_nodes(mat)

    coord = nodes.new('ShaderNodeTexCoord')

    # Color variation
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 18.0
    noise.inputs['Detail'].default_value = 5.0
    noise.inputs['Roughness'].default_value = 0.5
    links.new(coord.outputs['Object'], noise.inputs['Vector'])

    r, g, b = color
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (r * 0.82, g * 0.82, b * 0.78, 1)
    ramp.color_ramp.elements[1].color = (r * 1.14, g * 1.12, b * 1.10, 1)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Metallic'].default_value = metallic

    # Roughness variation
    _add_roughness_variation(nodes, links, bsdf, roughness, variation=0.10, scale=14.0)

    # Micro bump for surface imperfections
    _add_micro_bump(nodes, links, bsdf, strength=0.12, scale=45.0)

    return mat


# ============================================================
# Age-aware material palettes
# ============================================================

AGE_TINTS = {
    'stone':         {'wall': (0.62, 0.48, 0.28), 'roof': (0.55, 0.40, 0.18), 'roughness_add': 0.10},
    'bronze':        {'wall': (0.72, 0.55, 0.30), 'roof': (0.65, 0.35, 0.12), 'roughness_add': 0.05},
    'iron':          {'wall': (0.62, 0.52, 0.35), 'roof': (0.60, 0.28, 0.10), 'roughness_add': 0.03},
    'classical':     {'wall': (0.90, 0.85, 0.72), 'roof': (0.68, 0.30, 0.10), 'roughness_add': 0.0},
    'medieval':      {'wall': (0.72, 0.58, 0.38), 'roof': (0.68, 0.28, 0.08), 'roughness_add': 0.0},
    'gunpowder':     {'wall': (0.76, 0.62, 0.42), 'roof': (0.62, 0.25, 0.10), 'roughness_add': -0.02},
    'enlightenment': {'wall': (0.85, 0.78, 0.58), 'roof': (0.45, 0.35, 0.28), 'roughness_add': -0.05},
    'industrial':    {'wall': (0.72, 0.42, 0.28), 'roof': (0.38, 0.32, 0.26), 'roughness_add': -0.08},
    'modern':        {'wall': (0.76, 0.74, 0.70), 'roof': (0.30, 0.28, 0.32), 'roughness_add': -0.10},
    'digital':       {'wall': (0.82, 0.82, 0.86), 'roof': (0.22, 0.25, 0.32), 'roughness_add': -0.15},
}


def init_materials(age='medieval'):
    """Create a full material palette for the given age. Returns a dict."""
    tint = AGE_TINTS.get(age, AGE_TINTS['medieval'])
    wc = tint['wall']
    rc = tint['roof']

    m = {}
    m['stone']       = mat_stone_wall("StoneWall", wc, scale=7.0)
    m['stone_upper'] = mat_stone_wall("StoneUpper", (wc[0] - 0.05, wc[1] - 0.04, wc[2] - 0.03), scale=9.0)
    m['stone_dark']  = mat_stone_dark("StoneDark", (wc[0] - 0.23, wc[1] - 0.20, wc[2] - 0.15))
    m['stone_trim']  = mat_stone_dark("StoneTrim", (wc[0] - 0.10, wc[1] - 0.08, wc[2] - 0.05))
    m['stone_light'] = mat_stone_dark("StoneLight", (wc[0] + 0.07, wc[1] + 0.08, wc[2] + 0.07))
    m['roof']        = mat_roof_tiles("RoofTiles", rc)
    m['roof_edge']   = mat_wood("RoofEdge", (rc[0] - 0.10, rc[1] - 0.02, rc[2]))
    m['wood']        = mat_wood("Wood", (0.42, 0.26, 0.13))
    m['wood_dark']   = mat_wood("WoodDark", (0.30, 0.18, 0.09))
    m['wood_beam']   = mat_wood("WoodBeam", (0.38, 0.24, 0.12))
    m['door']        = mat_wood("Door", (0.28, 0.16, 0.08))
    m['window']      = mat_pbr("Window", (0.12, 0.18, 0.28), roughness=0.12)
    m['win_frame']   = mat_wood("WinFrame", (0.48, 0.38, 0.25))
    m['gold']        = mat_gold("Gold", (0.85, 0.68, 0.15))
    m['banner']      = mat_fabric("Banner", (0.72, 0.10, 0.06))
    m['ground']      = mat_ground("Ground", (0.48, 0.42, 0.30))
    m['iron']        = mat_metal("Iron", (0.25, 0.25, 0.27), roughness=0.45, metallic=0.85)
    m['plaster']     = mat_stone_dark("Plaster", (0.78, 0.73, 0.65))

    # Modern/digital ages get glass and metal materials
    if age in ('modern', 'digital'):
        m['glass'] = mat_glass("Glass", (0.82, 0.87, 0.92))
        m['metal'] = mat_metal("Metal", (0.6, 0.6, 0.62), roughness=0.30, metallic=0.92)

    return m
