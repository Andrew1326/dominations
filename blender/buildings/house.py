"""
House building — small residential structure per age, the most common
building in every player's civilization. 2x2 tile footprint.

Stone:         Round mud hut with conical thatch roof
Bronze:        Rectangular mud-brick house with flat roof, courtyard wall
Iron:          Stone cottage with pitched thatch roof, chimney
Classical:     Small Greek/Roman domus with red tile roof, entrance columns
Medieval:      Half-timber house with steep pitched roof, shuttered windows
Gunpowder:     Tudor-style house with timber frame, plastered walls
Enlightenment: Georgian brick townhouse, symmetrical windows, dormer roof
Industrial:    Victorian terraced house with chimney, bay window
Modern:        Mid-century modern house, flat roof, large windows
Digital:       Futuristic pod-house, curved glass, solar panels
"""

import bpy
import bmesh
import math

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# ============================================================
# STONE AGE — Round mud hut with conical thatch roof
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Circular base platform
    bmesh_prism("HutBase", 0.95, 0.12, 12, (0, 0, Z), m['stone_dark'])

    # Mud walls (cylindrical)
    bmesh_prism("HutWall", 0.90, 1.1, 12, (0, 0, Z + 0.12), m['stone'])

    # Conical thatch roof
    bmesh_cone("HutRoof", 1.25, 1.2, 14, (0, 0, Z + 1.22), m['roof'])

    # Roof finial (wooden knob)
    bmesh_prism("RoofKnob", 0.10, 0.12, 6, (0, 0, Z + 2.38), m['wood'])

    # Door
    bmesh_box("Door", (0.08, 0.35, 0.70), (0.91, 0, Z + 0.47), m['door'])

    # Support poles around hut
    for i in range(6):
        a = (2 * math.pi * i) / 6
        px, py = 0.82 * math.cos(a), 0.82 * math.sin(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.035, depth=1.2,
                                            location=(px, py, Z + 0.72))
        pole = bpy.context.active_object
        pole.name = f"Pole_{i}"
        pole.data.materials.append(m['wood'])

    # Small fire pit nearby
    bmesh_prism("FirePit", 0.22, 0.06, 8, (0.8, -0.7, Z + 0.03), m['stone_dark'])

    # Animal skin over doorway
    sv = [(0.92, -0.22, Z + 0.95), (0.92, 0.22, Z + 0.95),
          (0.94, 0.18, Z + 0.50), (0.94, -0.18, Z + 0.55)]
    mesh_from_pydata("Skin", sv, [(0, 1, 2, 3)], m['roof_edge'])
    m['roof_edge'].use_backface_culling = False

    # Drying rack (two poles + crossbar)
    for dy in [-0.15, 0.15]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.8,
                                            location=(-0.7, dy + 0.6, Z + 0.4))
        bpy.context.active_object.data.materials.append(m['wood'])
    bmesh_box("Crossbar", (0.04, 0.35, 0.03), (-0.7, 0.6, Z + 0.78), m['wood_dark'])


# ============================================================
# BRONZE AGE — Rectangular mud-brick house with flat roof
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Foundation step
    bmesh_box("Found", (2.6, 2.2, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.12
    wall_h = 1.5

    # Main walls
    bmesh_box("Main", (2.4, 2.0, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Flat roof slab
    bmesh_box("Roof", (2.6, 2.2, 0.10), (0, 0, BZ + wall_h + 0.05), m['stone_trim'], bevel=0.02)

    # Parapet (low wall around roof edge)
    for pos, size in [
        ((1.3, 0), (0.08, 2.2, 0.25)),
        ((-1.3, 0), (0.08, 2.2, 0.25)),
        ((0, 1.1), (2.6, 0.08, 0.25)),
        ((0, -1.1), (2.6, 0.08, 0.25)),
    ]:
        bmesh_box(f"Parapet_{pos[0]:.1f}_{pos[1]:.1f}", size,
                  (pos[0], pos[1], BZ + wall_h + 0.10 + 0.125), m['stone_trim'])

    # Door
    bmesh_box("Door", (0.08, 0.40, 0.90), (1.21, 0, BZ + 0.45), m['door'])
    bmesh_box("DoorFrame", (0.09, 0.48, 0.06), (1.22, 0, BZ + 0.92), m['wood'])

    # Windows (small rectangular openings)
    for y in [-0.50, 0.50]:
        bmesh_box(f"Win_{y:.1f}", (0.06, 0.18, 0.22), (1.21, y, BZ + 1.05), m['window'])

    # Side window
    bmesh_box("WinSide", (0.18, 0.06, 0.22), (0, -1.01, BZ + 1.05), m['window'])

    # Courtyard wall (low, L-shaped extension)
    bmesh_box("CourtWall1", (0.12, 1.2, 0.8), (1.5, -0.6, BZ + 0.40), m['stone_dark'])
    bmesh_box("CourtWall2", (1.0, 0.12, 0.8), (1.0, -1.2, BZ + 0.40), m['stone_dark'])

    # Steps to door
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.16, 0.8, 0.04), (1.35 + i * 0.18, 0, BZ - 0.02 - i * 0.04), m['stone_dark'])

    # Clay pot
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(1.4, 0.5, BZ + 0.06))
    pot = bpy.context.active_object
    pot.name = "Pot"
    pot.scale = (1, 1, 0.8)
    pot.data.materials.append(m['roof'])


# ============================================================
# IRON AGE — Stone cottage with pitched thatch roof, chimney
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stone foundation
    bmesh_box("Found", (2.8, 2.2, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.15
    wall_h = 1.6

    # Main walls
    bmesh_box("Main", (2.5, 2.0, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Stone band at mid-height
    bmesh_box("Band", (2.54, 2.04, 0.06), (0, 0, BZ + 0.8), m['stone_trim'])

    # Pitched roof
    rv = [
        (-1.35, -1.10, BZ + wall_h), (1.35, -1.10, BZ + wall_h),
        (1.35, 1.10, BZ + wall_h), (-1.35, 1.10, BZ + wall_h),
        (0, -1.10, BZ + wall_h + 0.9), (0, 1.10, BZ + wall_h + 0.9),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("Roof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Ridge beam
    bmesh_box("Ridge", (0.06, 2.24, 0.06), (0, 0, BZ + wall_h + 0.90), m['wood_dark'])

    # Door (arched suggestion)
    bmesh_box("Door", (0.08, 0.40, 0.85), (1.26, 0, BZ + 0.42), m['door'])
    bmesh_box("DoorFrame", (0.10, 0.48, 0.06), (1.27, 0, BZ + 0.87), m['wood'])

    # Windows
    for y in [-0.55, 0.55]:
        bmesh_box(f"Win_{y:.1f}", (0.06, 0.16, 0.28), (1.26, y, BZ + 1.10), m['window'])
        bmesh_box(f"WinF_{y:.1f}", (0.07, 0.20, 0.04), (1.27, y, BZ + 1.26), m['stone_trim'])

    # Side window
    bmesh_box("WinSide", (0.16, 0.06, 0.28), (0.3, -1.01, BZ + 1.10), m['window'])

    # Chimney
    bmesh_box("Chimney", (0.22, 0.22, 1.4), (-0.8, 0.80, BZ + wall_h + 0.2), m['stone_dark'], bevel=0.02)
    bmesh_box("ChimTop", (0.26, 0.26, 0.06), (-0.8, 0.80, BZ + wall_h + 0.9 + 0.03), m['stone_trim'])

    # Steps
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.18, 0.7, 0.05), (1.42 + i * 0.18, 0, BZ - 0.03 - i * 0.05), m['stone_dark'])

    # Woodpile next to house
    for j in range(3):
        for k in range(2):
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.5,
                                                location=(-1.3, -0.3 + j * 0.12, BZ + 0.04 + k * 0.09))
            log = bpy.context.active_object
            log.name = f"Log_{j}_{k}"
            log.rotation_euler = (math.radians(90), 0, 0)
            log.data.materials.append(m['wood_dark'])


# ============================================================
# CLASSICAL AGE — Small Greek/Roman domus
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stepped platform (3 tiers)
    for i in range(3):
        w = 3.0 - i * 0.20
        d = 2.6 - i * 0.15
        bmesh_box(f"Plat_{i}", (w, d, 0.06), (0, 0, Z + 0.03 + i * 0.06), m['stone_light'], bevel=0.01)

    BZ = Z + 0.18
    wall_h = 1.5

    # Main walls
    bmesh_box("Main", (2.4, 2.0, wall_h), (0, 0, BZ + wall_h / 2), m['stone_light'], bevel=0.02)

    # Cornice
    bmesh_box("Cornice", (2.5, 2.1, 0.06), (0, 0, BZ + wall_h), m['stone_trim'], bevel=0.02)

    # Pitched roof with tile texture
    rv = [
        (-1.30, -1.10, BZ + wall_h + 0.03), (1.30, -1.10, BZ + wall_h + 0.03),
        (1.30, 1.10, BZ + wall_h + 0.03), (-1.30, 1.10, BZ + wall_h + 0.03),
        (0, -1.10, BZ + wall_h + 0.75), (0, 1.10, BZ + wall_h + 0.75),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("Roof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Front entrance columns (2)
    col_h = 1.4
    for y in [-0.35, 0.35]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.07, depth=col_h,
                                            location=(1.35, y, BZ + col_h / 2))
        c = bpy.context.active_object
        c.name = f"Col_{y:.1f}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        bmesh_box(f"Cap_{y:.1f}", (0.17, 0.17, 0.05), (1.35, y, BZ + col_h + 0.025), m['stone_trim'])
        bmesh_box(f"Base_{y:.1f}", (0.16, 0.16, 0.04), (1.35, y, BZ + 0.02), m['stone_trim'])

    # Portico roof
    bmesh_box("Portico", (0.40, 0.85, 0.05), (1.35, 0, BZ + col_h + 0.05), m['stone_trim'])

    # Small pediment
    pv = [(1.38, -0.42, BZ + col_h + 0.08), (1.38, 0.42, BZ + col_h + 0.08),
          (1.38, 0, BZ + col_h + 0.35)]
    mesh_from_pydata("Pediment", pv, [(0, 1, 2)], m['stone_light'])

    # Door
    bmesh_box("Door", (0.06, 0.38, 0.90), (1.21, 0, BZ + 0.45), m['door'])

    # Windows (tall, narrow)
    for y in [-0.65, 0.65]:
        bmesh_box(f"Win_{y:.1f}", (0.06, 0.14, 0.40), (1.21, y, BZ + 0.95), m['window'])

    # Side windows
    for x in [-0.5, 0.5]:
        bmesh_box(f"WinS_{x:.1f}", (0.14, 0.06, 0.40), (x, -1.01, BZ + 0.95), m['window'])

    # Steps
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.16, 1.0, 0.04), (1.50 + i * 0.18, 0, BZ - 0.02 - i * 0.04), m['stone_light'])

    # Acroterion (small gold ornament)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0, 0, BZ + wall_h + 0.78))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()


# ============================================================
# MEDIEVAL AGE — Half-timber house with steep pitched roof
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stone foundation
    bmesh_box("Found", (2.6, 2.2, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.18
    wall_h = 1.7

    # Main walls (plaster/wattle infill)
    bmesh_box("Main", (2.4, 2.0, wall_h), (0, 0, BZ + wall_h / 2), m['plaster'], bevel=0.02)

    # Timber frame (half-timber effect)
    # Vertical beams
    for y in [-0.85, -0.28, 0.28, 0.85]:
        bmesh_box(f"VBeamF_{y:.2f}", (0.06, 0.08, wall_h), (1.22, y, BZ + wall_h / 2), m['wood_beam'])
    # Horizontal beams
    for z_off in [0.0, 0.85, wall_h]:
        bmesh_box(f"HBeamF_{z_off:.1f}", (0.06, 2.0, 0.08), (1.22, 0, BZ + z_off + 0.04), m['wood_beam'])
    # Diagonal braces
    for y_start, y_end in [(-0.85, -0.28), (0.28, 0.85)]:
        dv = [(1.23, y_start, BZ + 0.08), (1.23, y_start + 0.04, BZ + 0.08),
              (1.23, y_end + 0.04, BZ + 0.85), (1.23, y_end, BZ + 0.85)]
        mesh_from_pydata(f"Diag_{y_start:.2f}", dv, [(0, 1, 2, 3)], m['wood_beam'])

    # Side timber frame
    for x in [-0.80, 0, 0.80]:
        bmesh_box(f"VBeamS_{x:.1f}", (0.08, 0.06, wall_h), (x, -1.01, BZ + wall_h / 2), m['wood_beam'])
    for z_off in [0.0, 0.85, wall_h]:
        bmesh_box(f"HBeamS_{z_off:.1f}", (2.0, 0.06, 0.08), (0, -1.01, BZ + z_off + 0.04), m['wood_beam'])

    # Steep pitched roof (overhanging)
    rv = [
        (-1.40, -1.20, BZ + wall_h), (1.40, -1.20, BZ + wall_h),
        (1.40, 1.20, BZ + wall_h), (-1.40, 1.20, BZ + wall_h),
        (0, -1.20, BZ + wall_h + 1.2), (0, 1.20, BZ + wall_h + 1.2),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("Roof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Roof edge trim
    bmesh_box("RoofEdgeF", (0.06, 2.44, 0.06), (1.40, 0, BZ + wall_h + 0.03), m['wood_dark'])
    bmesh_box("RoofEdgeB", (0.06, 2.44, 0.06), (-1.40, 0, BZ + wall_h + 0.03), m['wood_dark'])

    # Ridge beam
    bmesh_box("Ridge", (0.06, 2.44, 0.06), (0, 0, BZ + wall_h + 1.20), m['wood_dark'])

    # Door
    bmesh_box("Door", (0.08, 0.38, 0.90), (1.21, 0, BZ + 0.45), m['door'])
    bmesh_box("DoorFrame", (0.10, 0.46, 0.06), (1.22, 0, BZ + 0.92), m['wood_beam'])

    # Windows with shutters
    for y in [-0.55, 0.55]:
        bmesh_box(f"Win_{y:.1f}", (0.06, 0.18, 0.30), (1.21, y, BZ + 1.15), m['window'])
        bmesh_box(f"WinFrame_{y:.1f}", (0.07, 0.22, 0.34), (1.22, y, BZ + 1.15), m['wood'])
        # Shutters (slightly open angle)
        for side, offset in [(-1, -0.13), (1, 0.13)]:
            bmesh_box(f"Shutter_{y:.1f}_{side}", (0.04, 0.10, 0.28),
                      (1.25, y + offset, BZ + 1.15), m['wood_dark'])

    # Upper story window (in gable)
    bmesh_box("GableWin", (0.06, 0.14, 0.20), (1.21, 0, BZ + wall_h + 0.45), m['window'])

    # Chimney
    bmesh_box("Chimney", (0.20, 0.20, 1.0), (-0.7, 0.85, BZ + wall_h + 0.3), m['stone'], bevel=0.02)
    bmesh_box("ChimTop", (0.24, 0.24, 0.05), (-0.7, 0.85, BZ + wall_h + 0.82), m['stone_trim'])

    # Steps
    for i in range(2):
        bmesh_box(f"Step_{i}", (0.16, 0.7, 0.05), (1.35 + i * 0.16, 0, BZ - 0.03 - i * 0.05), m['stone_dark'])

    # Barrel by the door
    bmesh_prism("Barrel", 0.10, 0.22, 8, (1.3, -0.55, BZ), m['wood_dark'])


# ============================================================
# GUNPOWDER AGE — Tudor-style house with timber frame
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stone foundation
    bmesh_box("Found", (2.8, 2.3, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.18

    # Ground floor (stone lower half)
    gf_h = 0.9
    bmesh_box("GroundFloor", (2.6, 2.1, gf_h), (0, 0, BZ + gf_h / 2), m['stone'], bevel=0.02)

    # Upper floor (jettied/overhanging, plaster with timber)
    uf_h = 1.2
    uf_z = BZ + gf_h
    bmesh_box("UpperFloor", (2.8, 2.3, uf_h), (0, 0, uf_z + uf_h / 2), m['plaster'], bevel=0.02)

    # Jetty floor beam
    bmesh_box("JettyBeam", (2.82, 2.32, 0.06), (0, 0, uf_z + 0.03), m['wood_beam'])

    # Upper floor timber frame
    for y in [-0.95, -0.32, 0.32, 0.95]:
        bmesh_box(f"UVBeam_{y:.2f}", (0.06, 0.08, uf_h), (1.41, y, uf_z + uf_h / 2), m['wood_beam'])
    for z_off in [0.06, uf_h - 0.04]:
        bmesh_box(f"UHBeam_{z_off:.2f}", (0.06, 2.3, 0.08), (1.41, 0, uf_z + z_off), m['wood_beam'])

    # Cross-bracing on upper floor
    for y_start, y_end in [(-0.95, -0.32), (0.32, 0.95)]:
        dv = [(1.42, y_start, uf_z + 0.10), (1.42, y_start + 0.04, uf_z + 0.10),
              (1.42, y_end + 0.04, uf_z + uf_h - 0.08), (1.42, y_end, uf_z + uf_h - 0.08)]
        mesh_from_pydata(f"UDiag_{y_start:.2f}", dv, [(0, 1, 2, 3)], m['wood_beam'])

    # Side timber frame
    for x in [-0.90, 0, 0.90]:
        bmesh_box(f"SVBeam_{x:.1f}", (0.08, 0.06, uf_h), (x, -1.16, uf_z + uf_h / 2), m['wood_beam'])
    for z_off in [0.06, uf_h - 0.04]:
        bmesh_box(f"SHBeam_{z_off:.2f}", (2.3, 0.06, 0.08), (0, -1.16, uf_z + z_off), m['wood_beam'])

    # Steep gabled roof
    top_z = uf_z + uf_h
    rv = [
        (-1.50, -1.25, top_z), (1.50, -1.25, top_z),
        (1.50, 1.25, top_z), (-1.50, 1.25, top_z),
        (0, -1.25, top_z + 1.1), (0, 1.25, top_z + 1.1),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("Roof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Ridge
    bmesh_box("Ridge", (0.06, 2.54, 0.06), (0, 0, top_z + 1.10), m['wood_dark'])

    # Ground floor door
    bmesh_box("Door", (0.08, 0.42, 0.80), (1.31, 0, BZ + 0.40), m['door'])
    bmesh_box("DoorSurround", (0.10, 0.50, 0.06), (1.32, 0, BZ + 0.82), m['stone_trim'])

    # Ground floor windows
    for y in [-0.60, 0.60]:
        bmesh_box(f"GWin_{y:.1f}", (0.06, 0.16, 0.25), (1.31, y, BZ + 0.55), m['window'])

    # Upper floor windows (larger, more ornate)
    for y in [-0.55, 0, 0.55]:
        bmesh_box(f"UWin_{y:.1f}", (0.06, 0.20, 0.35), (1.41, y, uf_z + 0.55), m['window'])
        bmesh_box(f"UWinH_{y:.1f}", (0.07, 0.24, 0.04), (1.42, y, uf_z + 0.74), m['wood'])

    # Chimney (tall, prominent)
    bmesh_box("Chimney", (0.24, 0.24, 1.6), (-0.9, 0.90, top_z + 0.3), m['stone'], bevel=0.02)
    bmesh_box("ChimTop", (0.28, 0.28, 0.06), (-0.9, 0.90, top_z + 1.13), m['stone_trim'])

    # Steps
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.16, 0.8, 0.05), (1.45 + i * 0.16, 0, BZ - 0.03 - i * 0.05), m['stone_dark'])


# ============================================================
# ENLIGHTENMENT AGE — Georgian brick townhouse
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Foundation
    bmesh_box("Found", (2.8, 2.3, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.15
    wall_h = 2.4

    # Main brick walls
    bmesh_box("Main", (2.6, 2.1, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Quoins (decorative corner stones)
    for xs in [-1, 1]:
        for ys in [-1, 1]:
            for z_off in [0.15, 0.55, 0.95, 1.35, 1.75, 2.15]:
                bmesh_box(f"Quoin_{xs}_{ys}_{z_off:.1f}", (0.06, 0.06, 0.14),
                          (xs * 1.31, ys * 1.06, BZ + z_off), m['stone_light'])

    # String course (horizontal band between floors)
    bmesh_box("StringCourse", (2.64, 2.14, 0.05), (0, 0, BZ + 1.2), m['stone_trim'], bevel=0.01)

    # Cornice
    bmesh_box("Cornice", (2.70, 2.18, 0.08), (0, 0, BZ + wall_h), m['stone_trim'], bevel=0.03)

    # Hipped roof with dormers
    pyramid_roof("Roof", w=2.4, d=1.9, h=0.8, overhang=0.15,
                 origin=(0, 0, BZ + wall_h + 0.04), material=m['roof'])

    # Dormer window (small gable protruding from roof)
    dz = BZ + wall_h + 0.30
    bmesh_box("Dormer", (0.30, 0.40, 0.40), (1.0, 0, dz + 0.20), m['stone'])
    bmesh_box("DormerWin", (0.06, 0.18, 0.25), (1.16, 0, dz + 0.18), m['window'])
    # Dormer roof
    drv = [(0.85, -0.22, dz + 0.40), (1.15, -0.22, dz + 0.40),
           (1.15, 0.22, dz + 0.40), (0.85, 0.22, dz + 0.40),
           (1.0, 0, dz + 0.62)]
    mesh_from_pydata("DormerRoof", drv, [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], m['roof'])

    # Front door with fanlight
    bmesh_box("Door", (0.08, 0.42, 1.0), (1.31, 0, BZ + 0.50), m['door'])
    bmesh_box("DoorSurround", (0.10, 0.54, 1.10), (1.32, 0, BZ + 0.55), m['stone_light'])
    # Fanlight (half-circle over door)
    bmesh_box("Fanlight", (0.06, 0.42, 0.10), (1.31, 0, BZ + 1.03), m['window'])

    # Ground floor windows (tall, symmetrical — 2 flanking door)
    for y in [-0.60, 0.60]:
        bmesh_box(f"GWin_{y:.1f}", (0.06, 0.22, 0.50), (1.31, y, BZ + 0.55), m['window'])
        bmesh_box(f"GWinH_{y:.1f}", (0.07, 0.26, 0.04), (1.32, y, BZ + 0.82), m['stone_trim'])
        bmesh_box(f"GWinS_{y:.1f}", (0.07, 0.26, 0.04), (1.32, y, BZ + 0.33), m['stone_trim'])

    # First floor windows (3 across)
    for y in [-0.55, 0, 0.55]:
        bmesh_box(f"FWin_{y:.1f}", (0.06, 0.20, 0.45), (1.31, y, BZ + 1.55), m['window'])
        bmesh_box(f"FWinH_{y:.1f}", (0.07, 0.24, 0.04), (1.32, y, BZ + 1.80), m['stone_trim'])

    # Side windows
    for x in [-0.5, 0.5]:
        for z_off in [0.55, 1.55]:
            bmesh_box(f"SWin_{x:.1f}_{z_off:.1f}", (0.20, 0.06, 0.45), (x, -1.06, BZ + z_off), m['window'])

    # Chimneys (2, symmetrical)
    for y in [-0.6, 0.6]:
        bmesh_box(f"Chimney_{y:.1f}", (0.18, 0.18, 0.8), (0, y, BZ + wall_h + 0.60), m['stone'], bevel=0.02)
        bmesh_box(f"ChimTop_{y:.1f}", (0.22, 0.22, 0.05), (0, y, BZ + wall_h + 1.02), m['stone_trim'])

    # Iron railings at front
    for i in range(8):
        fy = -0.85 + i * 0.24
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.01, depth=0.40,
                                            location=(1.45, fy, BZ + 0.10))
        bpy.context.active_object.data.materials.append(m['iron'])

    # Steps (wider, grander)
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.18, 1.0, 0.04), (1.45 + i * 0.18, 0, BZ - 0.02 - i * 0.04), m['stone_light'])


# ============================================================
# INDUSTRIAL AGE — Victorian terraced house
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Foundation
    bmesh_box("Found", (2.8, 2.3, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.12
    wall_h = 2.6

    # Main brick walls
    bmesh_box("Main", (2.6, 2.1, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Iron beam grid on facade
    for z in [BZ + 0.9, BZ + 1.8]:
        bmesh_box(f"IronH_{z:.1f}", (0.03, 2.1, 0.04), (1.31, 0, z), m['iron'])

    # Band between floors
    bmesh_box("Band", (2.64, 2.14, 0.05), (0, 0, BZ + 1.3), m['stone_trim'])

    # Cornice with dentils
    bmesh_box("Cornice", (2.68, 2.16, 0.08), (0, 0, BZ + wall_h), m['stone_trim'], bevel=0.02)

    # Flat roof with slight slope
    bmesh_box("Roof", (2.7, 2.2, 0.08), (0, 0, BZ + wall_h + 0.08 + 0.04), m['stone_dark'])
    bmesh_box("Parapet", (2.72, 2.22, 0.15), (0, 0, BZ + wall_h + 0.16 + 0.075), m['stone_trim'], bevel=0.01)

    # Front door (recessed)
    bmesh_box("DoorRecess", (0.15, 0.50, 1.10), (1.24, 0.30, BZ + 0.55), m['stone_dark'])
    bmesh_box("Door", (0.06, 0.38, 1.0), (1.31, 0.30, BZ + 0.50), m['door'])
    bmesh_box("DoorHead", (0.10, 0.52, 0.06), (1.25, 0.30, BZ + 1.07), m['stone_trim'])

    # Bay window (projecting, ground floor)
    bmesh_box("BayBase", (0.30, 0.70, 0.06), (1.45, -0.40, BZ + 0.38), m['stone_trim'])
    bmesh_box("BayFront", (0.06, 0.70, 0.65), (1.59, -0.40, BZ + 0.73), m['window'])
    bmesh_box("BaySideL", (0.30, 0.06, 0.65), (1.45, -0.75, BZ + 0.73), m['window'])
    bmesh_box("BaySideR", (0.30, 0.06, 0.65), (1.45, -0.05, BZ + 0.73), m['window'])
    bmesh_box("BayRoof", (0.34, 0.74, 0.05), (1.45, -0.40, BZ + 1.08), m['stone_trim'])
    # Bay mullions
    bmesh_box("BayMull1", (0.04, 0.02, 0.65), (1.59, -0.60, BZ + 0.73), m['iron'])
    bmesh_box("BayMull2", (0.04, 0.02, 0.65), (1.59, -0.20, BZ + 0.73), m['iron'])

    # First floor windows
    for y in [-0.40, 0.30]:
        bmesh_box(f"FWin_{y:.1f}", (0.06, 0.24, 0.50), (1.31, y, BZ + 1.70), m['window'])
        bmesh_box(f"FWinH_{y:.1f}", (0.07, 0.28, 0.04), (1.32, y, BZ + 1.97), m['stone_trim'])
        bmesh_box(f"FWinS_{y:.1f}", (0.07, 0.28, 0.04), (1.32, y, BZ + 1.48), m['stone_trim'])

    # Side windows
    for z_off in [0.65, 1.70]:
        bmesh_box(f"SWin_{z_off:.1f}", (0.22, 0.06, 0.45), (0, -1.06, BZ + z_off), m['window'])

    # Tall chimney
    bmesh_box("Chimney", (0.22, 0.22, 1.6), (-0.8, 0.80, BZ + wall_h + 0.5), m['stone'], bevel=0.02)
    bmesh_box("ChimTop", (0.26, 0.26, 0.06), (-0.8, 0.80, BZ + wall_h + 1.33), m['stone_trim'])
    # Chimney pots
    for dy in [-0.05, 0.05]:
        bmesh_prism(f"ChimPot_{dy:.2f}", 0.04, 0.10, 8,
                    (-0.8, 0.80 + dy, BZ + wall_h + 1.36), m['stone_dark'])

    # Iron fence
    for i in range(6):
        fy = -0.85 + i * 0.30
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=0.45,
                                            location=(1.50, fy, BZ + 0.10))
        bpy.context.active_object.data.materials.append(m['iron'])
    # Fence rail
    bmesh_box("FenceRail", (0.02, 1.55, 0.02), (1.50, -0.10, BZ + 0.30), m['iron'])

    # Steps
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.16, 0.8, 0.04), (1.42 + i * 0.16, 0.30, BZ - 0.02 - i * 0.04), m['stone_dark'])


# ============================================================
# MODERN AGE — Mid-century modern house
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (3.8, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.08
    bmesh_box("Found", (3.4, 2.8, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # Main box (lower portion)
    main_h = 1.8
    bmesh_box("Main", (2.8, 2.2, main_h), (0, 0, BZ + main_h / 2), m['stone'], bevel=0.02)

    # Flat roof with slight overhang
    bmesh_box("Roof", (3.0, 2.4, 0.08), (0, 0, BZ + main_h + 0.04), m['stone_dark'])

    # Large front window wall (floor-to-ceiling glass)
    bmesh_box("GlassWall", (0.06, 1.4, main_h - 0.3), (1.41, -0.15, BZ + main_h / 2 + 0.05), glass)
    # Mullions
    for y in [-0.60, -0.15, 0.30]:
        bmesh_box(f"Mull_{y:.1f}", (0.04, 0.03, main_h - 0.3), (1.42, y, BZ + main_h / 2 + 0.05), metal)
    # Horizontal mullion
    bmesh_box("HMull", (0.04, 1.42, 0.03), (1.42, -0.15, BZ + main_h / 2), metal)

    # Solid wall section (right of door)
    bmesh_box("SolidPanel", (0.06, 0.50, main_h - 0.3), (1.41, 0.80, BZ + main_h / 2 + 0.05), m['stone'])

    # Front door (glass)
    bmesh_box("Door", (0.06, 0.55, 1.20), (1.41, 0.55, BZ + 0.60), glass)
    bmesh_box("DoorFrame", (0.07, 0.58, 1.24), (1.42, 0.55, BZ + 0.62), metal)

    # Side windows
    for x in [-0.8, 0.3]:
        bmesh_box(f"SWin_{x:.1f}", (0.35, 0.06, 0.60), (x, -1.11, BZ + 1.20), glass)

    # Carport or patio extension
    bmesh_box("Patio", (1.2, 2.2, 0.05), (1.8, 0, BZ + main_h + 0.025), metal)
    # Patio support columns
    for y in [-0.8, 0.8]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=main_h,
                                            location=(2.3, y, BZ + main_h / 2))
        bpy.context.active_object.data.materials.append(metal)

    # Planter box
    bmesh_box("Planter", (0.5, 0.25, 0.20), (1.6, -0.90, BZ + 0.10), m['stone_dark'])

    # Address numbers / mailbox suggestion
    bmesh_box("Mailbox", (0.06, 0.10, 0.14), (1.60, 0.90, BZ + 0.50), metal)


# ============================================================
# DIGITAL AGE — Futuristic pod-house
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (3.8, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.06
    bmesh_box("Found", (3.2, 2.6, 0.06), (0, 0, Z + 0.03), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # Main pod body (rounded box — use a UV sphere scaled as pod)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.3, location=(0, 0, BZ + 1.2))
    pod = bpy.context.active_object
    pod.name = "Pod"
    pod.scale = (1.1, 0.85, 0.70)
    pod.data.materials.append(glass)
    bpy.ops.object.shade_smooth()

    # Steel frame ribs over the pod
    for i in range(5):
        a = -0.6 + i * 0.3
        for j in range(8):
            t = -0.7 + j * 0.2
            x = 1.1 * 1.3 * math.cos(t) * math.cos(a)
            y = 0.85 * 1.3 * math.cos(t) * math.sin(a)
            z = 0.70 * 1.3 * math.sin(t) + BZ + 1.2
            if z > BZ + 0.2:
                bmesh_box(f"Rib_{i}_{j}", (0.03, 0.03, 0.03), (x, y, z), metal)

    # Base platform (clean, geometric)
    bmesh_prism("BasePlat", 1.5, 0.10, 8, (0, 0, BZ), metal)

    # Front entrance (glass panel with metal frame)
    bmesh_box("EntranceFrame", (0.08, 0.60, 1.20), (1.30, 0, BZ + 0.70), metal)
    bmesh_box("EntranceGlass", (0.06, 0.54, 1.14), (1.31, 0, BZ + 0.70), glass)

    # Entrance path
    bmesh_box("Path", (0.6, 0.70, 0.03), (1.60, 0, BZ + 0.015), m['stone_light'])

    # Solar panel array on top
    for i in range(3):
        sx = -0.4 + i * 0.4
        bmesh_box(f"Solar_{i}", (0.35, 0.5, 0.03), (sx, 0, BZ + 2.0 + i * 0.02), glass)
        bmesh_box(f"SolarFrame_{i}", (0.37, 0.52, 0.02), (sx, 0, BZ + 1.99 + i * 0.02), metal)

    # LED accent strip around base
    bmesh_prism("LEDRing", 1.52, 0.04, 8, (0, 0, BZ + 0.10), m['gold'])

    # Vertical garden / green wall panel
    bmesh_box("GreenWall", (0.06, 0.8, 0.5), (-1.20, 0, BZ + 0.80), m['ground'])

    # Communication antenna (small)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.6,
                                        location=(0.3, 0.5, BZ + 2.10))
    bpy.context.active_object.data.materials.append(metal)

    # Smart mailbox
    bmesh_box("SmartBox", (0.12, 0.12, 0.18), (1.50, 0.50, BZ + 0.15), metal)
    bmesh_box("SmartScreen", (0.06, 0.08, 0.06), (1.56, 0.50, BZ + 0.20), m['gold'])


# ============================================================
# DISPATCHER
# ============================================================
AGE_BUILDERS = {
    'stone': _build_stone,
    'bronze': _build_bronze,
    'iron': _build_iron,
    'classical': _build_classical,
    'medieval': _build_medieval,
    'gunpowder': _build_gunpowder,
    'enlightenment': _build_enlightenment,
    'industrial': _build_industrial,
    'modern': _build_modern,
    'digital': _build_digital,
}


def build_house(materials, age='medieval'):
    """Build a House with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
