"""
Town Center — DomiNations-style isometric building (realistic version).
Cycles + procedural textures + detailed geometry.

Run: blender --background --python blender/town_center.py
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector


# ============================================================
# SCENE SETUP
# ============================================================
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)
    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)


def setup_scene():
    clear_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    # Cycles for realistic rendering
    scene.render.engine = 'CYCLES'
    cycles = scene.cycles
    cycles.samples = 256
    cycles.use_denoising = True
    cycles.denoiser = 'OPENIMAGEDENOISE'
    # Try GPU
    try:
        cycles.device = 'GPU'
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'CUDA'
        prefs.get_devices()
        for device in prefs.devices:
            device.use = True
    except:
        cycles.device = 'CPU'

    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.compression = 15
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    return scene


# ============================================================
# PROCEDURAL MATERIALS (shader nodes for realism)
# ============================================================
def _get_nodes(mat):
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    return nodes, links, bsdf


def mat_stone_wall(name, base_color=(0.62, 0.55, 0.43), scale=8.0):
    """Stone wall — brick pattern + noise color variation + bump."""
    mat = bpy.data.materials.new(name)
    nodes, links, bsdf = _get_nodes(mat)

    # Texture coordinate
    coord = nodes.new('ShaderNodeTexCoord')

    # Brick texture for stone block pattern
    brick = nodes.new('ShaderNodeTexBrick')
    brick.inputs['Scale'].default_value = scale
    brick.inputs['Mortar Size'].default_value = 0.015
    brick.inputs['Mortar Smooth'].default_value = 0.1
    brick.inputs['Bias'].default_value = 0.0
    brick.inputs['Brick Width'].default_value = 0.65
    brick.inputs['Row Height'].default_value = 0.35
    brick.inputs['Color1'].default_value = (*base_color, 1)
    r, g, b = base_color
    brick.inputs['Color2'].default_value = (r * 0.85, g * 0.85, b * 0.85, 1)
    brick.inputs['Mortar'].default_value = (r * 0.6, g * 0.6, b * 0.6, 1)
    links.new(coord.outputs['Object'], brick.inputs['Vector'])

    # Noise for color variation
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 20.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.7
    links.new(coord.outputs['Object'], noise.inputs['Vector'])

    # Mix brick color with noise for natural variation
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'OVERLAY'
    mix.inputs['Fac'].default_value = 0.15
    links.new(brick.outputs['Color'], mix.inputs['Color1'])
    links.new(noise.outputs['Color'], mix.inputs['Color2'])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.85

    # Bump from brick pattern + noise
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.4
    bump.inputs['Distance'].default_value = 0.02

    # Mix brick fac and noise for bump
    math_add = nodes.new('ShaderNodeMath')
    math_add.operation = 'ADD'
    links.new(brick.outputs['Fac'], math_add.inputs[0])
    links.new(noise.outputs['Fac'], math_add.inputs[1])
    links.new(math_add.outputs['Value'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


def mat_stone_dark(name, base_color=(0.40, 0.36, 0.30)):
    """Dark stone for foundation — noise texture + bump."""
    mat = bpy.data.materials.new(name)
    nodes, links, bsdf = _get_nodes(mat)

    coord = nodes.new('ShaderNodeTexCoord')

    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 12.0
    noise.inputs['Detail'].default_value = 8.0
    links.new(coord.outputs['Object'], noise.inputs['Vector'])

    # Color ramp for stone color
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*[c * 0.85 for c in base_color], 1)
    ramp.color_ramp.elements[1].color = (*[c * 1.1 for c in base_color], 1)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.90

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.5
    bump.inputs['Distance'].default_value = 0.015
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


def mat_roof_tiles(name, base_color=(0.55, 0.22, 0.08)):
    """Roof — wave texture for tile rows + noise variation + bump."""
    mat = bpy.data.materials.new(name)
    nodes, links, bsdf = _get_nodes(mat)

    coord = nodes.new('ShaderNodeTexCoord')

    # Wave texture for tile rows
    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'Y'
    wave.inputs['Scale'].default_value = 12.0
    wave.inputs['Distortion'].default_value = 2.0
    wave.inputs['Detail'].default_value = 4.0
    wave.inputs['Detail Scale'].default_value = 2.0
    links.new(coord.outputs['Object'], wave.inputs['Vector'])

    # Noise for color variation
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 25.0
    noise.inputs['Detail'].default_value = 5.0
    links.new(coord.outputs['Object'], noise.inputs['Vector'])

    # Color ramp for roof tile colors
    ramp = nodes.new('ShaderNodeValToRGB')
    r, g, b = base_color
    ramp.color_ramp.elements[0].color = (r * 0.8, g * 0.8, b * 0.8, 1)
    ramp.color_ramp.elements[1].color = (r * 1.15, g * 1.1, b * 1.0, 1)
    links.new(wave.outputs['Fac'], ramp.inputs['Fac'])

    # Overlay noise on tile color
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'OVERLAY'
    mix.inputs['Fac'].default_value = 0.2
    links.new(ramp.outputs['Color'], mix.inputs['Color1'])
    links.new(noise.outputs['Color'], mix.inputs['Color2'])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.75

    # Bump from wave (tile ridges)
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.6
    bump.inputs['Distance'].default_value = 0.02
    links.new(wave.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


def mat_wood(name, base_color=(0.42, 0.26, 0.13)):
    """Wood — wave texture for grain + bump."""
    mat = bpy.data.materials.new(name)
    nodes, links, bsdf = _get_nodes(mat)

    coord = nodes.new('ShaderNodeTexCoord')

    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'X'
    wave.inputs['Scale'].default_value = 6.0
    wave.inputs['Distortion'].default_value = 4.0
    wave.inputs['Detail'].default_value = 3.0
    links.new(coord.outputs['Object'], wave.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    r, g, b = base_color
    ramp.color_ramp.elements[0].color = (r * 0.7, g * 0.7, b * 0.7, 1)
    ramp.color_ramp.elements[1].color = (r * 1.2, g * 1.15, b * 1.1, 1)
    links.new(wave.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.70

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.35
    bump.inputs['Distance'].default_value = 0.01
    links.new(wave.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


def mat_ground(name, base_color=(0.48, 0.42, 0.30)):
    """Ground — noise texture for dirt/grass + bump."""
    mat = bpy.data.materials.new(name)
    nodes, links, bsdf = _get_nodes(mat)

    coord = nodes.new('ShaderNodeTexCoord')

    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.inputs['Scale'].default_value = 8.0
    noise1.inputs['Detail'].default_value = 10.0
    noise1.inputs['Roughness'].default_value = 0.8
    links.new(coord.outputs['Object'], noise1.inputs['Vector'])

    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.inputs['Scale'].default_value = 30.0
    noise2.inputs['Detail'].default_value = 4.0
    links.new(coord.outputs['Object'], noise2.inputs['Vector'])

    # Mix two noise scales
    ramp = nodes.new('ShaderNodeValToRGB')
    r, g, b = base_color
    ramp.color_ramp.elements[0].color = (r * 0.8, g * 0.85, b * 0.75, 1)
    ramp.color_ramp.elements[1].color = (r * 1.1, g * 1.05, b * 0.95, 1)
    links.new(noise1.outputs['Fac'], ramp.inputs['Fac'])

    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Fac'].default_value = 0.15
    links.new(ramp.outputs['Color'], mix.inputs['Color1'])
    links.new(noise2.outputs['Color'], mix.inputs['Color2'])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.95

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.6
    bump.inputs['Distance'].default_value = 0.025
    links.new(noise1.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


def mat_simple(name, color, roughness=0.5, metallic=0.0):
    """Simple PBR — for small details that don't need procedural textures."""
    mat = bpy.data.materials.new(name)
    nodes, links, bsdf = _get_nodes(mat)
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat


MATERIALS = {}

def init_materials():
    m = MATERIALS
    m['stone']       = mat_stone_wall("StoneWall", (0.65, 0.58, 0.45), scale=7.0)
    m['stone_upper'] = mat_stone_wall("StoneUpper", (0.60, 0.54, 0.42), scale=9.0)
    m['stone_dark']  = mat_stone_dark("StoneDark", (0.42, 0.38, 0.30))
    m['stone_trim']  = mat_stone_dark("StoneTrim", (0.55, 0.50, 0.40))
    m['stone_light'] = mat_stone_dark("StoneLight", (0.72, 0.66, 0.52))
    m['roof']        = mat_roof_tiles("RoofTiles", (0.55, 0.22, 0.08))
    m['roof_edge']   = mat_wood("RoofEdge", (0.45, 0.20, 0.08))
    m['wood']        = mat_wood("Wood", (0.42, 0.26, 0.13))
    m['wood_dark']   = mat_wood("WoodDark", (0.30, 0.18, 0.09))
    m['wood_beam']   = mat_wood("WoodBeam", (0.38, 0.24, 0.12))
    m['door']        = mat_wood("Door", (0.28, 0.16, 0.08))
    m['window']      = mat_simple("Window", (0.15, 0.20, 0.30), roughness=0.1)
    m['win_frame']   = mat_wood("WinFrame", (0.48, 0.38, 0.25))
    m['gold']        = mat_simple("Gold", (0.85, 0.68, 0.15), roughness=0.25, metallic=0.9)
    m['banner']      = mat_simple("Banner", (0.72, 0.10, 0.06), roughness=0.55)
    m['ground']      = mat_ground("Ground", (0.48, 0.42, 0.30))
    m['iron']        = mat_simple("Iron", (0.25, 0.25, 0.27), roughness=0.45, metallic=0.8)
    m['plaster']     = mat_stone_dark("Plaster", (0.78, 0.73, 0.65))
    return m


# ============================================================
# GEOMETRY BUILDERS
# ============================================================
def mesh_from_pydata(name, vertices, faces, material=None):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj


def bmesh_box(name, size, origin=(0, 0, 0), material=None, bevel=0.0):
    bm = bmesh.new()
    sx, sy, sz = size[0]/2, size[1]/2, size[2]/2
    ox, oy, oz = origin
    v = [
        bm.verts.new((ox-sx, oy-sy, oz-sz)), bm.verts.new((ox+sx, oy-sy, oz-sz)),
        bm.verts.new((ox+sx, oy+sy, oz-sz)), bm.verts.new((ox-sx, oy+sy, oz-sz)),
        bm.verts.new((ox-sx, oy-sy, oz+sz)), bm.verts.new((ox+sx, oy-sy, oz+sz)),
        bm.verts.new((ox+sx, oy+sy, oz+sz)), bm.verts.new((ox-sx, oy+sy, oz+sz)),
    ]
    bm.faces.new([v[0], v[3], v[2], v[1]])
    bm.faces.new([v[4], v[5], v[6], v[7]])
    bm.faces.new([v[0], v[1], v[5], v[4]])
    bm.faces.new([v[2], v[3], v[7], v[6]])
    bm.faces.new([v[0], v[4], v[7], v[3]])
    bm.faces.new([v[1], v[2], v[6], v[5]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    if bevel > 0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = 'ANGLE'
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="Bevel")
    return obj


def bmesh_prism(name, radius, height, segments, origin=(0, 0, 0), material=None, bevel=0.0):
    """Polygonal prism (octagon, hexagon, etc) via bmesh."""
    bm = bmesh.new()
    ox, oy, oz = origin
    bot, top = [], []
    for i in range(segments):
        a = (2 * math.pi * i) / segments
        x, y = ox + radius * math.cos(a), oy + radius * math.sin(a)
        bot.append(bm.verts.new((x, y, oz)))
        top.append(bm.verts.new((x, y, oz + height)))
    bm.faces.new(bot)
    bm.faces.new(list(reversed(top)))
    for i in range(segments):
        j = (i + 1) % segments
        bm.faces.new([bot[i], bot[j], top[j], top[i]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    if bevel > 0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 1
        mod.limit_method = 'ANGLE'
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="Bevel")
    return obj


def bmesh_cone(name, radius, height, segments, origin=(0, 0, 0), material=None, smooth=True):
    """Cone via bmesh."""
    bm = bmesh.new()
    ox, oy, oz = origin
    base = []
    for i in range(segments):
        a = (2 * math.pi * i) / segments
        base.append(bm.verts.new((ox + radius * math.cos(a), oy + radius * math.sin(a), oz)))
    apex = bm.verts.new((ox, oy, oz + height))
    bm.faces.new(base)
    for i in range(segments):
        bm.faces.new([base[i], base[(i+1) % segments], apex])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def pyramid_roof(name, w, d, h, overhang=0.15, origin=(0, 0, 0), material=None):
    """Hipped roof with overhang using from_pydata."""
    ox, oy, oz = origin
    hw, hd = w/2 + overhang, d/2 + overhang
    tw, td = 0.12, 0.12  # top ridge size

    verts = [
        (ox-hw, oy-hd, oz), (ox+hw, oy-hd, oz),
        (ox+hw, oy+hd, oz), (ox-hw, oy+hd, oz),
        (ox-tw, oy-td, oz+h), (ox+tw, oy-td, oz+h),
        (ox+tw, oy+td, oz+h), (ox-tw, oy+td, oz+h),
    ]
    faces = [(0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7), (4,5,6,7)]
    obj = mesh_from_pydata(name, verts, faces, material)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


# ============================================================
# BUILD TOWN CENTER
# ============================================================
def build_town_center():
    m = MATERIALS

    Z = 0.0  # ground
    WALL_Z = 0.30
    WALL_H = 1.6
    ROOF_Z = WALL_Z + WALL_H + 0.04

    # ── GROUND ──
    bmesh_box("Ground", (4.2, 4.2, 0.06), (0, 0, Z + 0.03), m['ground'])

    # ── FOUNDATION (2-tier, beveled) ──
    bmesh_box("Found1", (3.7, 3.7, 0.14), (0, 0, Z + 0.13), m['stone_dark'], bevel=0.04)
    bmesh_box("Found2", (3.4, 3.4, 0.10), (0, 0, Z + 0.25), m['stone_dark'], bevel=0.03)

    # ── MAIN WALLS (brick-textured stone) ──
    wall_w = 2.7
    wall_d = 0.14

    # Four walls
    bmesh_box("WallFront", (wall_d, wall_w, WALL_H), ( 1.35, 0, WALL_Z+WALL_H/2), m['stone'], bevel=0.02)
    bmesh_box("WallBack",  (wall_d, wall_w, WALL_H), (-1.35, 0, WALL_Z+WALL_H/2), m['stone'], bevel=0.02)
    bmesh_box("WallRight", (wall_w, wall_d, WALL_H), (0, -1.35, WALL_Z+WALL_H/2), m['stone'], bevel=0.02)
    bmesh_box("WallLeft",  (wall_w, wall_d, WALL_H), (0,  1.35, WALL_Z+WALL_H/2), m['stone'], bevel=0.02)

    # ── HALF-TIMBER FRAME (medieval style) ──
    beam_d = 0.07
    beam_w = 0.06
    # Horizontal beams on front & right
    for z in [WALL_Z + 0.05, WALL_Z + 0.85, WALL_Z + WALL_H - 0.03]:
        bmesh_box(f"HBeamF_{z:.2f}", (beam_w, 2.5, beam_d), (1.37, 0, z), m['wood_beam'])
        bmesh_box(f"HBeamR_{z:.2f}", (2.5, beam_w, beam_d), (0, -1.37, z), m['wood_beam'])

    # Vertical beams (timber frame posts)
    for y in [-1.1, -0.4, 0.4, 1.1]:
        bmesh_box(f"VBeamF_{y:.1f}", (beam_w, beam_d, WALL_H-0.06), (1.37, y, WALL_Z+WALL_H/2), m['wood_beam'])
    for x in [-1.1, -0.4, 0.4, 1.1]:
        bmesh_box(f"VBeamR_{x:.1f}", (beam_d, beam_w, WALL_H-0.06), (x, -1.37, WALL_Z+WALL_H/2), m['wood_beam'])

    # Diagonal braces on front wall
    for y_off, rot in [(-0.75, 0.4), (0.75, -0.4)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(1.37, y_off, WALL_Z + 0.45))
        brace = bpy.context.active_object
        brace.name = f"Brace_{y_off:.1f}"
        brace.scale = (beam_w, 0.55, beam_d)
        brace.rotation_euler = (0, 0, rot)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        brace.data.materials.append(m['wood_beam'])

    # ── PLASTER INFILL between timbers (upper half) ──
    bmesh_box("PlasterFront", (0.01, 2.3, 0.65), (1.34, 0, WALL_Z + 1.22), m['plaster'])
    bmesh_box("PlasterRight", (2.3, 0.01, 0.65), (0, -1.34, WALL_Z + 1.22), m['plaster'])

    # ── STONE BANDS ──
    bmesh_box("BaseBand", (2.82, 2.82, 0.08), (0, 0, WALL_Z + 0.04), m['stone_trim'], bevel=0.01)
    bmesh_box("Cornice",  (2.86, 2.86, 0.06), (0, 0, WALL_Z + WALL_H + 0.01), m['stone_trim'], bevel=0.02)

    # ── CORNER PILASTERS ──
    for xs in [-1, 1]:
        for ys in [-1, 1]:
            bmesh_box(f"Pilaster_{xs}_{ys}", (0.16, 0.16, WALL_H+0.02),
                       (xs*1.32, ys*1.32, WALL_Z+WALL_H/2), m['stone_trim'], bevel=0.02)

    # ── WINDOWS (front: 2, right: 3, left: 3, back: 2) ──
    def add_window(pos, size_x, size_y):
        x, y, z = pos
        bmesh_box(f"WinG_{x:.1f}_{y:.1f}", (size_x + 0.01, size_y + 0.01, 0.42), (x, y, z), m['window'])
        # Frame
        bmesh_box(f"WinFT_{x:.1f}_{y:.1f}", (size_x + 0.02, size_y + 0.08, 0.04), (x, y, z + 0.23), m['win_frame'])
        bmesh_box(f"WinFB_{x:.1f}_{y:.1f}", (size_x + 0.03, size_y + 0.12, 0.05), (x, y, z - 0.23), m['win_frame'])
        bmesh_box(f"WinFL_{x:.1f}_{y:.1f}", (size_x + 0.02, 0.04, 0.48), (x, y - size_y/2 - 0.02, z), m['win_frame'])
        bmesh_box(f"WinFR_{x:.1f}_{y:.1f}", (size_x + 0.02, 0.04, 0.48), (x, y + size_y/2 + 0.02, z), m['win_frame'])
        # Cross bar
        bmesh_box(f"WinCH_{x:.1f}_{y:.1f}", (size_x + 0.02, size_y, 0.02), (x, y, z), m['win_frame'])
        bmesh_box(f"WinCV_{x:.1f}_{y:.1f}", (size_x + 0.02, 0.02, 0.42), (x, y, z), m['win_frame'])

    # Front
    for y in [-0.85, 0.85]:
        add_window((1.36, y, WALL_Z + 1.05), 0.15, 0.30)
    # Right
    for x in [-0.7, 0.0, 0.7]:
        add_window((x, -1.36, WALL_Z + 1.05), 0.30, 0.15)
    # Left
    for x in [-0.7, 0.0, 0.7]:
        add_window((x, 1.36, WALL_Z + 1.05), 0.30, 0.15)
    # Back
    for y in [-0.6, 0.6]:
        add_window((-1.36, y, WALL_Z + 1.05), 0.15, 0.30)

    # ── MAIN DOOR ──
    bmesh_box("DoorRecess", (0.07, 0.62, 1.00), (1.36, 0, WALL_Z + 0.50), m['door'])
    bmesh_box("DoorFrameL", (0.08, 0.06, 1.05), (1.37, -0.35, WALL_Z + 0.53), m['stone_light'])
    bmesh_box("DoorFrameR", (0.08, 0.06, 1.05), (1.37,  0.35, WALL_Z + 0.53), m['stone_light'])

    # Stone arch over door (from_pydata)
    arch_verts = []
    arch_faces = []
    segs = 10
    r_out, r_in = 0.38, 0.30
    for i in range(segs + 1):
        a = math.pi * i / segs
        arch_verts.append((1.38, -r_out * math.cos(a), WALL_Z + 1.05 + r_out * math.sin(a)))
        arch_verts.append((1.38, -r_in * math.cos(a),  WALL_Z + 1.05 + r_in * math.sin(a)))
    for i in range(segs):
        j = i * 2
        arch_faces.append((j, j+2, j+3, j+1))
    mesh_from_pydata("DoorArch", arch_verts, arch_faces, m['stone_light'])

    # Entrance steps
    for i in range(4):
        w = 0.90 - i * 0.03
        bmesh_box(f"Step_{i}", (0.18, w, 0.06), (1.48 + i*0.20, 0, WALL_Z - 0.06 - i*0.06), m['stone_dark'], bevel=0.008)

    # ── ROOF (hipped pyramid with tile texture) ──
    pyramid_roof("MainRoof", w=2.7, d=2.7, h=1.6, overhang=0.20, origin=(0, 0, ROOF_Z), material=m['roof'])

    # Eave fascia board
    bmesh_box("Eave", (3.15, 3.15, 0.05), (0, 0, ROOF_Z + 0.025), m['roof_edge'])

    # Roof ridge ornament
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0, 0, ROOF_Z + 1.63))
    cap = bpy.context.active_object
    cap.name = "RidgeCap"
    cap.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # ── CHIMNEY ──
    bmesh_box("Chimney", (0.28, 0.28, 0.8), (-0.6, 0.7, ROOF_Z + 0.7), m['stone'], bevel=0.02)
    bmesh_box("ChimneyTop", (0.34, 0.34, 0.06), (-0.6, 0.7, ROOF_Z + 1.12), m['stone_trim'], bevel=0.01)
    bmesh_box("ChimneyCap", (0.22, 0.22, 0.04), (-0.6, 0.7, ROOF_Z + 1.16), m['iron'])

    # ── WATCHTOWER (front-right, octagonal) ──
    TX, TY = 1.10, -1.10
    TZ = WALL_Z

    bmesh_prism("Tower", 0.46, 3.0, 8, (TX, TY, TZ), m['stone_upper'], bevel=0.02)

    # Tower stone bands
    for z in [TZ + 1.0, TZ + 2.0, TZ + 2.85]:
        bmesh_prism(f"TBand_{z:.1f}", 0.48, 0.05, 8, (TX, TY, z), m['stone_trim'])

    # Tower parapet + merlons
    bmesh_prism("TParapet", 0.52, 0.12, 8, (TX, TY, TZ + 2.90), m['stone_trim'])
    for i in range(8):
        a = (2 * math.pi * i) / 8
        mx, my = TX + 0.50 * math.cos(a), TY + 0.50 * math.sin(a)
        bmesh_box(f"Merlon_{i}", (0.10, 0.10, 0.14), (mx, my, TZ + 3.09), m['stone_trim'], bevel=0.01)

    # Tower roof
    bmesh_cone("TowerRoof", 0.58, 1.0, 8, (TX, TY, TZ + 3.15), m['roof'])

    # Tower windows
    for z in [TZ + 1.2, TZ + 2.2]:
        bmesh_box(f"TWin_{z:.1f}", (0.06, 0.10, 0.30), (TX + 0.46, TY, z), m['window'])
        bmesh_box(f"TWinF_{z:.1f}", (0.07, 0.14, 0.04), (TX + 0.46, TY, z + 0.17), m['win_frame'])
        bmesh_box(f"TWinS_{z:.1f}", (0.07, 0.14, 0.03), (TX + 0.46, TY, z - 0.17), m['win_frame'])

    # ── FLAG ──
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=1.0, location=(TX, TY, TZ + 4.15))
    pole = bpy.context.active_object
    pole.name = "FlagPole"
    pole.data.materials.append(m['wood'])

    # Banner with slight wave (from_pydata)
    bverts = [
        (TX+0.03, TY, TZ+4.45), (TX+0.55, TY+0.05, TZ+4.40),
        (TX+0.55, TY+0.03, TZ+4.72), (TX+0.03, TY, TZ+4.70),
    ]
    b = mesh_from_pydata("Banner", bverts, [(0,1,2,3)], m['banner'])
    m['banner'].use_backface_culling = False

    # Finial
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(TX, TY, TZ + 4.68))
    fin = bpy.context.active_object
    fin.name = "Finial"
    fin.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # ── TORCH SCONCES (iron brackets) ──
    for y in [-0.45, 0.45]:
        bmesh_box(f"Sconce_{y:.1f}", (0.08, 0.04, 0.04), (1.39, y, WALL_Z + 1.30), m['iron'])
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.14, location=(1.42, y, WALL_Z + 1.35))
        t = bpy.context.active_object
        t.name = f"Torch_{y:.1f}"
        t.data.materials.append(m['wood_dark'])

    # ── COBBLESTONE PATH ──
    import random
    random.seed(42)
    for ix in range(4):
        for iy in range(-3, 4):
            cx = 1.60 + ix * 0.20 + random.uniform(-0.03, 0.03)
            cy = iy * 0.20 + random.uniform(-0.03, 0.03)
            sz = 0.12 + random.uniform(-0.02, 0.02)
            bmesh_box(f"Cbl_{ix}_{iy}", (sz, sz, 0.04), (cx, cy, Z + 0.04), m['stone_dark'])


# ============================================================
# LIGHTING (three-point area lights)
# ============================================================
def setup_lighting():
    # Key light
    bpy.ops.object.light_add(type='AREA', location=(6, -5, 7))
    key = bpy.context.active_object
    key.name = "KeyLight"
    key.data.energy = 150
    key.data.size = 5
    key.data.color = (1.0, 0.95, 0.85)
    key.rotation_euler = (math.radians(45), 0, math.radians(30))

    # Fill
    bpy.ops.object.light_add(type='AREA', location=(-5, -3, 5))
    fill = bpy.context.active_object
    fill.name = "FillLight"
    fill.data.energy = 60
    fill.data.size = 6
    fill.data.color = (0.85, 0.90, 1.0)
    fill.rotation_euler = (math.radians(55), 0, math.radians(-120))

    # Rim
    bpy.ops.object.light_add(type='AREA', location=(0, 6, 6))
    rim = bpy.context.active_object
    rim.name = "RimLight"
    rim.data.energy = 70
    rim.data.size = 3
    rim.data.color = (1.0, 0.98, 0.90)
    rim.rotation_euler = (math.radians(40), 0, math.radians(200))

    # Ambient
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.30, 0.32, 0.38, 1.0)
        bg.inputs["Strength"].default_value = 0.6


# ============================================================
# CAMERA (Track-To)
# ============================================================
def setup_camera():
    scene = bpy.context.scene

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 1.6))
    target = bpy.context.active_object
    target.name = "CameraTarget"

    cam_data = bpy.data.cameras.new("IsoCamera")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 8.5
    cam_data.clip_start = 0.1
    cam_data.clip_end = 100

    dist = 20
    elev, azim = math.radians(30), math.radians(45)
    cam = bpy.data.objects.new("IsoCamera", cam_data)
    cam.location = (
        dist * math.cos(elev) * math.cos(azim),
        -dist * math.cos(elev) * math.sin(azim),
        dist * math.sin(elev),
    )
    scene.collection.objects.link(cam)
    scene.camera = cam

    track = cam.constraints.new(type='TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'


# ============================================================
# MAIN
# ============================================================
def main():
    scene = setup_scene()
    init_materials()
    print("Building geometry...")
    build_town_center()
    print("Lighting...")
    setup_lighting()
    print("Camera...")
    setup_camera()

    output = os.path.expanduser("~/Desktop/dominations/client/public/assets/buildings/town_center.png")
    os.makedirs(os.path.dirname(output), exist_ok=True)
    scene.render.filepath = output

    print(f"Rendering (Cycles {scene.cycles.samples} samples)...")
    bpy.ops.render.render(write_still=True)
    print(f"Done! {output}")


if __name__ == "__main__":
    main()
