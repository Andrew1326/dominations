"""
Farm building -- food production structure per age, a 2x2 tile building
focused on agriculture, storage, and food production.

Stone:         Small grain storage pit with wooden frame cover, drying rack, grinding stone
Bronze:        Irrigated field with mud-brick granary, water channel, grain baskets
Iron:          Wattle-and-daub barn with thatched roof, fenced animal pen, hay bales
Classical:     Roman villa rustica - columned portico over stone granary, olive press area
Medieval:      Timber barn with steep thatch roof, fenced yard, well, grain silo
Gunpowder:     Stone farmhouse with attached barn, windmill-style grain store, stone walls
Enlightenment: Brick farmhouse with separate barn, weather vane, organized plots
Industrial:    Steel-framed barn with corrugated roof, silo, mechanical equipment
Modern:        Agricultural facility with greenhouse section, metal grain silo, concrete
Digital:       Automated vertical farm - glass tower with LED growing levels, drone pad
"""

import bpy
import bmesh
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# ============================================================
# STONE AGE -- Grain storage pit with wooden frame, drying rack
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Circular storage pit (sunken with stone ring)
    bmesh_prism("PitRing", 0.75, 0.18, 12, (0.2, 0.2, Z), m['stone_dark'])
    bmesh_prism("PitInner", 0.60, 0.10, 12, (0.2, 0.2, Z + 0.02), m['stone'])

    # Wooden frame cover over pit (A-frame)
    # Two angled support beams
    fv = [(-0.55, -0.55 + 0.2, Z + 0.18), (-0.55 + 0.06, -0.55 + 0.2, Z + 0.18),
          (0.2, 0.2, Z + 1.05), (0.2 - 0.03, 0.2, Z + 1.05)]
    mesh_from_pydata("FrameL", fv, [(0, 1, 2, 3)], m['wood'])
    fv2 = [(0.95, -0.55 + 0.2, Z + 0.18), (0.95 - 0.06, -0.55 + 0.2, Z + 0.18),
           (0.2, 0.2, Z + 1.05), (0.2 + 0.03, 0.2, Z + 1.05)]
    mesh_from_pydata("FrameR", fv2, [(0, 1, 2, 3)], m['wood'])

    # Ridge pole
    bmesh_box("RidgePole", (0.04, 1.2, 0.04), (0.2, 0.2, Z + 1.05), m['wood_dark'])

    # Thatch cover draped over frame
    tv = [(-0.55, -0.35, Z + 0.20), (0.95, -0.35, Z + 0.20),
          (0.2, 0.2, Z + 1.10), (0.2, 0.2, Z + 1.10)]
    mesh_from_pydata("ThatchF", tv, [(0, 1, 2, 3)], m['roof'])
    tv2 = [(-0.55, 0.75, Z + 0.20), (0.95, 0.75, Z + 0.20),
           (0.2, 0.2, Z + 1.10), (0.2, 0.2, Z + 1.10)]
    mesh_from_pydata("ThatchB", tv2, [(0, 1, 2, 3)], m['roof'])

    # Support poles around frame
    for px, py in [(-0.50, -0.30), (0.90, -0.30), (-0.50, 0.70), (0.90, 0.70)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=0.90,
                                            location=(px, py, Z + 0.50))
        pole = bpy.context.active_object
        pole.name = f"FPole_{px:.1f}_{py:.1f}"
        pole.data.materials.append(m['wood'])

    # Drying rack with animal skins (right side)
    for dy in [-0.15, 0.15]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.90,
                                            location=(-1.0, dy - 0.6, Z + 0.45))
        bpy.context.active_object.data.materials.append(m['wood'])
    bmesh_box("RackBar", (0.04, 0.35, 0.03), (-1.0, -0.6, Z + 0.88), m['wood_dark'])

    # Skins hanging on rack
    sv = [(-1.01, -0.75, Z + 0.85), (-1.01, -0.45, Z + 0.85),
          (-1.03, -0.48, Z + 0.45), (-1.03, -0.72, Z + 0.50)]
    mesh_from_pydata("Skin", sv, [(0, 1, 2, 3)], m['roof_edge'])
    m['roof_edge'].use_backface_culling = False

    # Grinding stone (flat stone with round grinder)
    bmesh_box("GrindBase", (0.45, 0.35, 0.10), (1.0, -0.8, Z + 0.05), m['stone_dark'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(1.0, -0.8, Z + 0.18))
    grind = bpy.context.active_object
    grind.name = "Grinder"
    grind.scale = (1, 1, 0.5)
    grind.data.materials.append(m['stone'])

    # Small wooden pestle
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.25,
                                        location=(1.12, -0.72, Z + 0.25))
    pestle = bpy.context.active_object
    pestle.name = "Pestle"
    pestle.rotation_euler = (0.3, 0.2, 0)
    pestle.data.materials.append(m['wood_dark'])

    # Gathered grain bundles (small cone shapes)
    for i, (gx, gy) in enumerate([(0.9, 0.7), (1.1, 0.5), (0.7, 0.9)]):
        bmesh_cone(f"Grain_{i}", 0.08, 0.20, 6, (gx, gy, Z), m['roof_edge'])

    # Fire pit for cooking
    bmesh_prism("FirePit", 0.18, 0.06, 8, (-0.9, 0.9, Z + 0.03), m['stone_dark'])


# ============================================================
# BRONZE AGE -- Irrigated field with mud-brick granary
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Mud-brick granary (main structure)
    bmesh_box("GranaryFound", (1.8, 1.4, 0.10), (0.3, 0.3, Z + 0.05), m['stone_dark'], bevel=0.02)

    BZ = Z + 0.10
    wall_h = 1.3
    bmesh_box("Granary", (1.6, 1.2, wall_h), (0.3, 0.3, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Flat roof
    bmesh_box("GranaryRoof", (1.7, 1.3, 0.08), (0.3, 0.3, BZ + wall_h + 0.04), m['stone_trim'], bevel=0.02)

    # Low parapet
    for pos, size in [
        ((1.15, 0.3), (0.06, 1.3, 0.18)),
        ((-0.55, 0.3), (0.06, 1.3, 0.18)),
        ((0.3, 0.95), (1.7, 0.06, 0.18)),
        ((0.3, -0.35), (1.7, 0.06, 0.18)),
    ]:
        bmesh_box(f"Parapet_{pos[0]:.1f}_{pos[1]:.1f}", size,
                  (pos[0], pos[1], BZ + wall_h + 0.08 + 0.09), m['stone_trim'])

    # Door
    bmesh_box("Door", (0.06, 0.35, 0.75), (1.11, 0.3, BZ + 0.38), m['door'])
    bmesh_box("DoorFrame", (0.07, 0.42, 0.05), (1.12, 0.3, BZ + 0.77), m['wood'])

    # Small window
    bmesh_box("Win", (0.06, 0.14, 0.18), (1.11, -0.10, BZ + 0.90), m['window'])

    # Steps to granary
    for i in range(2):
        bmesh_box(f"Step_{i}", (0.14, 0.6, 0.04), (1.22 + i * 0.14, 0.3, BZ - 0.02 - i * 0.04), m['stone_dark'])

    # Water channel (irrigation ditch running across)
    bmesh_box("Channel", (0.18, 3.0, 0.08), (-0.8, 0, Z + 0.01), m['stone_dark'])
    # Water surface
    bmesh_box("Water", (0.12, 2.8, 0.02), (-0.8, 0, Z + 0.06), m['window'])

    # Perpendicular channel branch
    bmesh_box("ChannelBranch", (1.5, 0.14, 0.07), (0.0, -0.8, Z + 0.01), m['stone_dark'])
    bmesh_box("WaterBranch", (1.4, 0.08, 0.02), (0.0, -0.8, Z + 0.05), m['window'])

    # Irrigated field plots (raised beds)
    for px, py in [(-0.3, -0.7), (0.5, -0.7), (-0.3, -1.2), (0.5, -1.2)]:
        bmesh_box(f"Plot_{px:.1f}_{py:.1f}", (0.55, 0.35, 0.06), (px, py, Z + 0.03), m['ground'])

    # Grain baskets near granary entrance
    for i, (bx, by) in enumerate([(1.3, 0.65), (1.4, 0.1), (1.25, -0.15)]):
        bmesh_prism(f"Basket_{i}", 0.08, 0.14, 8, (bx, by, BZ), m['roof_edge'])

    # Large storage pot
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(1.35, 0.85, BZ + 0.08))
    pot = bpy.context.active_object
    pot.name = "Pot"
    pot.scale = (1, 1, 0.9)
    pot.data.materials.append(m['roof'])

    # Wooden shade structure over work area
    for px, py in [(0.8, -0.55), (0.8, -1.05), (1.35, -0.55), (1.35, -1.05)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.80,
                                            location=(px, py, Z + 0.40))
        bpy.context.active_object.data.materials.append(m['wood'])
    bmesh_box("ShadeRoof", (0.60, 0.55, 0.04), (1.07, -0.80, Z + 0.80), m['roof'])


# ============================================================
# IRON AGE -- Wattle-and-daub barn with thatched roof
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stone foundation for barn
    bmesh_box("Found", (2.4, 1.8, 0.12), (0, 0.15, Z + 0.06), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.12
    wall_h = 1.4

    # Wattle-and-daub walls (plaster-colored)
    bmesh_box("BarnWalls", (2.2, 1.6, wall_h), (0, 0.15, BZ + wall_h / 2), m['plaster'], bevel=0.02)

    # Timber frame on barn walls
    for y in [-0.55, 0.0, 0.55]:
        bmesh_box(f"VBeam_{y:.2f}", (0.05, 0.06, wall_h), (1.11, y + 0.15, BZ + wall_h / 2), m['wood_beam'])
    for z_off in [0.0, 0.7, wall_h]:
        bmesh_box(f"HBeam_{z_off:.1f}", (0.05, 1.6, 0.06), (1.11, 0.15, BZ + z_off + 0.03), m['wood_beam'])

    # Pitched thatch roof
    rv = [
        (-1.25, -0.85, BZ + wall_h), (1.25, -0.85, BZ + wall_h),
        (1.25, 1.15, BZ + wall_h), (-1.25, 1.15, BZ + wall_h),
        (0, -0.85, BZ + wall_h + 0.85), (0, 1.15, BZ + wall_h + 0.85),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("BarnRoof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Ridge beam
    bmesh_box("Ridge", (0.05, 2.04, 0.05), (0, 0.15, BZ + wall_h + 0.85), m['wood_dark'])

    # Barn door (large, for livestock)
    bmesh_box("BarnDoor", (0.07, 0.50, 0.90), (1.11, 0.15, BZ + 0.45), m['door'])
    bmesh_box("BarnDoorFrame", (0.08, 0.58, 0.05), (1.12, 0.15, BZ + 0.92), m['wood'])

    # Fenced animal pen (right side)
    fence_h = 0.45
    # Fence posts
    for i, (fx, fy) in enumerate([
        (0.5, -1.0), (1.0, -1.0), (1.5, -1.0),
        (1.5, -0.6), (1.5, -0.2),
        (0.5, -0.2)
    ]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=fence_h,
                                            location=(fx, fy, Z + fence_h / 2))
        post = bpy.context.active_object
        post.name = f"FPost_{i}"
        post.data.materials.append(m['wood'])

    # Fence rails
    bmesh_box("FRailF", (1.05, 0.03, 0.04), (1.0, -1.0, Z + 0.15), m['wood_dark'])
    bmesh_box("FRailF2", (1.05, 0.03, 0.04), (1.0, -1.0, Z + 0.35), m['wood_dark'])
    bmesh_box("FRailR", (0.03, 0.85, 0.04), (1.5, -0.60, Z + 0.15), m['wood_dark'])
    bmesh_box("FRailR2", (0.03, 0.85, 0.04), (1.5, -0.60, Z + 0.35), m['wood_dark'])
    bmesh_box("FRailL", (0.03, 0.85, 0.04), (0.5, -0.60, Z + 0.15), m['wood_dark'])
    bmesh_box("FRailL2", (0.03, 0.85, 0.04), (0.5, -0.60, Z + 0.35), m['wood_dark'])

    # Hay bales (stacked near barn)
    for i, (hx, hy, hz) in enumerate([
        (-1.2, 0.0, Z + 0.10), (-1.2, 0.35, Z + 0.10), (-1.2, -0.35, Z + 0.10),
        (-1.2, 0.0, Z + 0.30), (-1.2, 0.35, Z + 0.30)
    ]):
        bmesh_box(f"Hay_{i}", (0.25, 0.30, 0.18), (hx, hy, hz), m['roof_edge'])

    # Water trough in pen
    bmesh_box("Trough", (0.40, 0.14, 0.10), (1.0, -0.55, Z + 0.08), m['wood_dark'])

    # Small window on barn side
    bmesh_box("BarnWin", (0.14, 0.05, 0.20), (0.4, -0.66, BZ + 0.95), m['window'])

    # Woodpile
    for j in range(3):
        for k in range(2):
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.035, depth=0.40,
                                                location=(-1.2, 0.85 + j * 0.10, Z + 0.035 + k * 0.08))
            log = bpy.context.active_object
            log.name = f"Log_{j}_{k}"
            log.rotation_euler = (math.radians(90), 0, 0)
            log.data.materials.append(m['wood_dark'])


# ============================================================
# CLASSICAL AGE -- Roman villa rustica with portico, olive press
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stepped platform (2 tiers)
    for i in range(2):
        w = 2.8 - i * 0.15
        d = 2.4 - i * 0.10
        bmesh_box(f"Plat_{i}", (w, d, 0.06), (0, 0, Z + 0.03 + i * 0.06), m['stone_light'], bevel=0.01)

    BZ = Z + 0.12
    wall_h = 1.5

    # Stone granary building
    bmesh_box("Granary", (2.0, 1.6, wall_h), (0, 0.2, BZ + wall_h / 2), m['stone_light'], bevel=0.02)

    # Cornice
    bmesh_box("Cornice", (2.1, 1.7, 0.05), (0, 0.2, BZ + wall_h), m['stone_trim'], bevel=0.02)

    # Pitched tile roof
    rv = [
        (-1.10, -0.70, BZ + wall_h + 0.02), (1.10, -0.70, BZ + wall_h + 0.02),
        (1.10, 1.10, BZ + wall_h + 0.02), (-1.10, 1.10, BZ + wall_h + 0.02),
        (0, -0.70, BZ + wall_h + 0.65), (0, 1.10, BZ + wall_h + 0.65),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("Roof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Front columned portico (4 columns)
    col_h = 1.35
    for y in [-0.45, -0.15, 0.15, 0.45]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.055, depth=col_h,
                                            location=(1.15, y + 0.2, BZ + col_h / 2))
        c = bpy.context.active_object
        c.name = f"Col_{y:.2f}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        bmesh_box(f"Cap_{y:.2f}", (0.13, 0.13, 0.04), (1.15, y + 0.2, BZ + col_h + 0.02), m['stone_trim'])
        bmesh_box(f"Base_{y:.2f}", (0.12, 0.12, 0.03), (1.15, y + 0.2, BZ + 0.015), m['stone_trim'])

    # Portico roof slab
    bmesh_box("Portico", (0.35, 1.1, 0.04), (1.15, 0.2, BZ + col_h + 0.04), m['stone_trim'])

    # Door
    bmesh_box("Door", (0.06, 0.32, 0.80), (1.01, 0.2, BZ + 0.40), m['door'])

    # Windows
    for y in [-0.35, 0.75]:
        bmesh_box(f"Win_{y:.2f}", (0.05, 0.12, 0.30), (1.01, y, BZ + 1.00), m['window'])

    # Steps
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.14, 0.85, 0.04), (1.30 + i * 0.14, 0.2, BZ - 0.02 - i * 0.04), m['stone_light'])

    # Olive press area (stone basin + press arm)
    bmesh_prism("PressBasis", 0.30, 0.12, 10, (-0.8, -0.8, Z), m['stone_dark'])
    # Press stone (round)
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.22, depth=0.08,
                                        location=(-0.8, -0.8, Z + 0.16))
    press = bpy.context.active_object
    press.name = "PressStone"
    press.data.materials.append(m['stone'])
    # Press beam (wooden lever arm)
    bmesh_box("PressBeam", (0.60, 0.05, 0.04), (-0.55, -0.8, Z + 0.35), m['wood_dark'])
    # Press upright
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=0.40,
                                        location=(-0.80, -0.8, Z + 0.32))
    bpy.context.active_object.data.materials.append(m['wood'])

    # Storage amphorae (tall clay pots)
    for i, (ax, ay) in enumerate([(-0.9, 0.6), (-0.7, 0.8), (-1.05, 0.75)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(ax, ay, Z + 0.12))
        amp = bpy.context.active_object
        amp.name = f"Amphora_{i}"
        amp.scale = (0.7, 0.7, 1.5)
        amp.data.materials.append(m['roof'])

    # Low stone wall boundary (L-shaped)
    bmesh_box("BoundWall1", (0.08, 2.2, 0.35), (-1.3, -0.3, Z + 0.175), m['stone_dark'])
    bmesh_box("BoundWall2", (1.5, 0.08, 0.35), (-0.55, -1.35, Z + 0.175), m['stone_dark'])

    # Gold acroterion on roof peak
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(0, 0.2, BZ + wall_h + 0.68))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()


# ============================================================
# MEDIEVAL AGE -- Timber barn with steep thatch roof, well, silo
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stone foundation
    bmesh_box("Found", (2.6, 2.0, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.15
    wall_h = 1.6

    # Main barn walls (plaster with timber frame)
    bmesh_box("BarnWalls", (2.4, 1.8, wall_h), (0, 0, BZ + wall_h / 2), m['plaster'], bevel=0.02)

    # Timber frame on front face
    for y in [-0.70, -0.15, 0.40, 0.70]:
        bmesh_box(f"VBeamF_{y:.2f}", (0.05, 0.07, wall_h), (1.21, y, BZ + wall_h / 2), m['wood_beam'])
    for z_off in [0.0, 0.80, wall_h]:
        bmesh_box(f"HBeamF_{z_off:.1f}", (0.05, 1.8, 0.07), (1.21, 0, BZ + z_off + 0.035), m['wood_beam'])

    # Diagonal braces on front
    for y_s, y_e in [(-0.70, -0.15), (0.40, 0.70)]:
        dv = [(1.22, y_s, BZ + 0.07), (1.22, y_s + 0.04, BZ + 0.07),
              (1.22, y_e + 0.04, BZ + 0.80), (1.22, y_e, BZ + 0.80)]
        mesh_from_pydata(f"Diag_{y_s:.2f}", dv, [(0, 1, 2, 3)], m['wood_beam'])

    # Side timber frame
    for x in [-0.80, 0, 0.80]:
        bmesh_box(f"VBeamS_{x:.1f}", (0.07, 0.05, wall_h), (x, -0.91, BZ + wall_h / 2), m['wood_beam'])
    for z_off in [0.0, 0.80, wall_h]:
        bmesh_box(f"HBeamS_{z_off:.1f}", (1.8, 0.05, 0.07), (0, -0.91, BZ + z_off + 0.035), m['wood_beam'])

    # Steep pitched thatch roof
    rv = [
        (-1.35, -1.05, BZ + wall_h), (1.35, -1.05, BZ + wall_h),
        (1.35, 1.05, BZ + wall_h), (-1.35, 1.05, BZ + wall_h),
        (0, -1.05, BZ + wall_h + 1.1), (0, 1.05, BZ + wall_h + 1.1),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("BarnRoof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Roof edge trim
    bmesh_box("RoofEdgeF", (0.05, 2.14, 0.05), (1.35, 0, BZ + wall_h + 0.025), m['wood_dark'])
    bmesh_box("RoofEdgeB", (0.05, 2.14, 0.05), (-1.35, 0, BZ + wall_h + 0.025), m['wood_dark'])

    # Ridge beam
    bmesh_box("Ridge", (0.05, 2.14, 0.05), (0, 0, BZ + wall_h + 1.10), m['wood_dark'])

    # Large barn door
    bmesh_box("BarnDoor", (0.07, 0.50, 1.0), (1.21, 0.10, BZ + 0.50), m['door'])
    bmesh_box("BarnDoorFrame", (0.08, 0.58, 0.06), (1.22, 0.10, BZ + 1.02), m['wood_beam'])

    # Side window
    bmesh_box("BarnWin", (0.14, 0.05, 0.22), (0.3, -0.91, BZ + 1.10), m['window'])

    # Upper gable window
    bmesh_box("GableWin", (0.05, 0.12, 0.16), (1.21, 0.10, BZ + wall_h + 0.40), m['window'])

    # Fenced yard (front-right)
    fence_h = 0.40
    fence_posts = [(0.6, -1.1), (1.0, -1.1), (1.4, -1.1),
                   (1.4, -0.8), (1.4, -0.5),
                   (0.6, -0.5)]
    for i, (fx, fy) in enumerate(fence_posts):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.022, depth=fence_h,
                                            location=(fx, fy, Z + fence_h / 2))
        bpy.context.active_object.data.materials.append(m['wood'])
    # Fence rails
    bmesh_box("YardRailF", (0.85, 0.025, 0.03), (1.0, -1.1, Z + 0.13), m['wood_dark'])
    bmesh_box("YardRailF2", (0.85, 0.025, 0.03), (1.0, -1.1, Z + 0.33), m['wood_dark'])
    bmesh_box("YardRailR", (0.025, 0.65, 0.03), (1.4, -0.8, Z + 0.13), m['wood_dark'])
    bmesh_box("YardRailR2", (0.025, 0.65, 0.03), (1.4, -0.8, Z + 0.33), m['wood_dark'])
    bmesh_box("YardRailL", (0.025, 0.65, 0.03), (0.6, -0.8, Z + 0.13), m['wood_dark'])
    bmesh_box("YardRailL2", (0.025, 0.65, 0.03), (0.6, -0.8, Z + 0.33), m['wood_dark'])

    # Well (left side)
    bmesh_prism("WellBase", 0.20, 0.35, 8, (-1.1, -0.5, Z), m['stone'])
    # Well roof supports
    for dy in [-0.12, 0.12]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.55,
                                            location=(-1.1, -0.5 + dy, Z + 0.55))
        bpy.context.active_object.data.materials.append(m['wood'])
    # Well roof
    bmesh_box("WellRoof", (0.22, 0.30, 0.03), (-1.1, -0.5, Z + 0.80), m['roof'])
    # Crossbeam
    bmesh_box("WellBeam", (0.03, 0.28, 0.03), (-1.1, -0.5, Z + 0.70), m['wood_dark'])

    # Grain silo (cylindrical wooden storage)
    bmesh_prism("Silo", 0.22, 0.90, 10, (-1.05, 0.6, Z), m['wood'])
    bmesh_cone("SiloRoof", 0.28, 0.25, 10, (-1.05, 0.6, Z + 0.90), m['roof'])

    # Barrel
    bmesh_prism("Barrel", 0.09, 0.20, 8, (1.25, -0.40, Z), m['wood_dark'])

    # Steps to door
    for i in range(2):
        bmesh_box(f"Step_{i}", (0.14, 0.65, 0.04), (1.32 + i * 0.14, 0.10, BZ - 0.02 - i * 0.04), m['stone_dark'])


# ============================================================
# GUNPOWDER AGE -- Stone farmhouse with windmill grain store
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stone foundation
    bmesh_box("Found", (2.8, 2.2, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.15

    # Main farmhouse (stone lower half, plaster upper)
    gf_h = 0.85
    bmesh_box("GroundFloor", (2.0, 1.5, gf_h), (0.3, 0.2, BZ + gf_h / 2), m['stone'], bevel=0.02)
    uf_h = 0.90
    uf_z = BZ + gf_h
    bmesh_box("UpperFloor", (2.1, 1.6, uf_h), (0.3, 0.2, uf_z + uf_h / 2), m['plaster'], bevel=0.02)

    # Floor beam
    bmesh_box("FloorBeam", (2.12, 1.62, 0.05), (0.3, 0.2, uf_z + 0.025), m['wood_beam'])

    # Timber frame on upper floor
    for y in [-0.50, 0, 0.50]:
        bmesh_box(f"UVBeam_{y:.2f}", (0.05, 0.06, uf_h), (1.36, y + 0.2, uf_z + uf_h / 2), m['wood_beam'])
    for z_off in [0.05, uf_h - 0.04]:
        bmesh_box(f"UHBeam_{z_off:.2f}", (0.05, 1.6, 0.06), (1.36, 0.2, uf_z + z_off), m['wood_beam'])

    # Roof
    top_z = uf_z + uf_h
    rv = [
        (-0.80, -0.65, top_z), (1.40, -0.65, top_z),
        (1.40, 1.05, top_z), (-0.80, 1.05, top_z),
        (0.30, -0.65, top_z + 0.80), (0.30, 1.05, top_z + 0.80),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("HouseRoof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True
    bmesh_box("HouseRidge", (0.05, 1.74, 0.05), (0.30, 0.2, top_z + 0.80), m['wood_dark'])

    # Door
    bmesh_box("Door", (0.07, 0.36, 0.75), (1.31, 0.2, BZ + 0.38), m['door'])
    bmesh_box("DoorSurround", (0.08, 0.44, 0.05), (1.32, 0.2, BZ + 0.78), m['stone_trim'])

    # Ground floor windows
    for y in [-0.25, 0.65]:
        bmesh_box(f"GWin_{y:.2f}", (0.05, 0.14, 0.22), (1.31, y, BZ + 0.50), m['window'])

    # Upper floor windows
    for y in [-0.20, 0.60]:
        bmesh_box(f"UWin_{y:.2f}", (0.05, 0.16, 0.28), (1.36, y, uf_z + 0.42), m['window'])

    # Chimney
    bmesh_box("Chimney", (0.18, 0.18, 0.90), (-0.55, 0.75, top_z + 0.10), m['stone'], bevel=0.02)
    bmesh_box("ChimTop", (0.22, 0.22, 0.05), (-0.55, 0.75, top_z + 0.57), m['stone_trim'])

    # Steps
    for i in range(2):
        bmesh_box(f"Step_{i}", (0.14, 0.65, 0.04), (1.40 + i * 0.14, 0.2, BZ - 0.02 - i * 0.04), m['stone_dark'])

    # Windmill-style grain store (attached to side)
    # Cylindrical tower
    bmesh_prism("MillTower", 0.40, 1.80, 10, (-1.0, -0.4, BZ), m['stone'], bevel=0.02)
    bmesh_prism("MillBand", 0.42, 0.06, 10, (-1.0, -0.4, BZ + 0.90), m['stone_trim'])
    bmesh_cone("MillRoof", 0.50, 0.50, 10, (-1.0, -0.4, BZ + 1.80), m['roof'])

    # Windmill sails (simple cross)
    sail_z = BZ + 1.35
    for angle in [0, math.radians(90)]:
        sv = [(-1.0 + 0.45 * math.cos(angle), -0.4, sail_z + 0.45 * math.sin(angle)),
              (-1.0 + 0.48 * math.cos(angle), -0.4, sail_z + 0.48 * math.sin(angle)),
              (-1.0 - 0.48 * math.cos(angle), -0.4, sail_z - 0.48 * math.sin(angle)),
              (-1.0 - 0.45 * math.cos(angle), -0.4, sail_z - 0.45 * math.sin(angle))]
        mesh_from_pydata(f"Sail_{angle:.1f}", sv, [(0, 1, 2, 3)], m['wood'])

    # Sail hub
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=0.08,
                                        location=(-1.0, -0.42, sail_z))
    hub = bpy.context.active_object
    hub.name = "SailHub"
    hub.rotation_euler = (math.radians(90), 0, 0)
    hub.data.materials.append(m['iron'])

    # Mill door
    bmesh_box("MillDoor", (0.04, 0.05, 0.55), (-1.0, -0.80, BZ + 0.28), m['door'])

    # Stone boundary walls
    bmesh_box("StoneWall1", (0.10, 2.8, 0.50), (1.55, -0.25, Z + 0.25), m['stone_dark'])
    bmesh_box("StoneWall2", (1.8, 0.10, 0.50), (0.65, -1.35, Z + 0.25), m['stone_dark'])

    # Grain sacks near entrance
    for i, (sx, sy) in enumerate([(1.45, 0.55), (1.50, 0.80)]):
        bmesh_box(f"Sack_{i}", (0.12, 0.10, 0.16), (sx, sy, Z + 0.08), m['roof_edge'])


# ============================================================
# ENLIGHTENMENT AGE -- Brick farmhouse with barn, weather vane
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Foundation
    bmesh_box("Found", (2.6, 2.2, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.12

    # Main farmhouse (brick, two-story)
    wall_h = 2.0
    bmesh_box("Farmhouse", (1.6, 1.4, wall_h), (0.3, 0.2, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # String course
    bmesh_box("StringCourse", (1.64, 1.44, 0.04), (0.3, 0.2, BZ + 1.0), m['stone_trim'], bevel=0.01)

    # Cornice
    bmesh_box("Cornice", (1.68, 1.48, 0.06), (0.3, 0.2, BZ + wall_h), m['stone_trim'], bevel=0.02)

    # Quoins (corner decorations)
    for xs in [-1, 1]:
        for ys in [-1, 1]:
            for z_off in [0.12, 0.45, 0.78, 1.11, 1.44, 1.77]:
                bmesh_box(f"Quoin_{xs}_{ys}_{z_off:.2f}", (0.04, 0.04, 0.12),
                          (0.3 + xs * 0.81, 0.2 + ys * 0.71, BZ + z_off), m['stone_light'])

    # Hipped roof
    pyramid_roof("FarmRoof", w=1.4, d=1.2, h=0.65, overhang=0.12,
                 origin=(0.3, 0.2, BZ + wall_h + 0.03), material=m['roof'])

    # Door with fanlight
    bmesh_box("Door", (0.06, 0.34, 0.85), (1.11, 0.2, BZ + 0.43), m['door'])
    bmesh_box("DoorSurround", (0.07, 0.42, 0.92), (1.12, 0.2, BZ + 0.46), m['stone_light'])
    bmesh_box("Fanlight", (0.05, 0.34, 0.08), (1.11, 0.2, BZ + 0.88), m['window'])

    # Ground floor windows (symmetrical)
    for y in [-0.20, 0.60]:
        bmesh_box(f"GWin_{y:.2f}", (0.05, 0.16, 0.38), (1.11, y, BZ + 0.44), m['window'])
        bmesh_box(f"GWinH_{y:.2f}", (0.06, 0.20, 0.03), (1.12, y, BZ + 0.65), m['stone_trim'])
        bmesh_box(f"GWinS_{y:.2f}", (0.06, 0.20, 0.03), (1.12, y, BZ + 0.27), m['stone_trim'])

    # First floor windows
    for y in [-0.20, 0.20, 0.60]:
        bmesh_box(f"FWin_{y:.2f}", (0.05, 0.15, 0.35), (1.11, y, BZ + 1.30), m['window'])
        bmesh_box(f"FWinH_{y:.2f}", (0.06, 0.19, 0.03), (1.12, y, BZ + 1.50), m['stone_trim'])

    # Chimney
    bmesh_box("Chimney", (0.14, 0.14, 0.65), (-0.25, 0.70, BZ + wall_h + 0.42), m['stone'], bevel=0.02)
    bmesh_box("ChimTop", (0.18, 0.18, 0.04), (-0.25, 0.70, BZ + wall_h + 0.76), m['stone_trim'])

    # Steps
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.14, 0.75, 0.04), (1.22 + i * 0.14, 0.2, BZ - 0.02 - i * 0.04), m['stone_light'])

    # Separate barn (lower, wider)
    barn_h = 1.3
    bmesh_box("Barn", (1.4, 1.0, barn_h), (-0.9, -0.6, BZ + barn_h / 2), m['stone'], bevel=0.02)
    # Barn pitched roof
    brv = [
        (-1.65, -1.15, BZ + barn_h), (-0.15, -1.15, BZ + barn_h),
        (-0.15, -0.05, BZ + barn_h), (-1.65, -0.05, BZ + barn_h),
        (-0.9, -1.15, BZ + barn_h + 0.55), (-0.9, -0.05, BZ + barn_h + 0.55),
    ]
    brf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    br = mesh_from_pydata("BarnRoof", brv, brf, m['roof'])
    for p in br.data.polygons:
        p.use_smooth = True

    # Barn door
    bmesh_box("BarnDoor", (0.06, 0.40, 0.80), (-0.19, -0.6, BZ + 0.40), m['door'])

    # Weather vane on barn roof
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.40,
                                        location=(-0.9, -0.6, BZ + barn_h + 0.55 + 0.20))
    bpy.context.active_object.data.materials.append(m['iron'])
    # Arrow of weather vane
    wv_z = BZ + barn_h + 0.55 + 0.38
    wvv = [(-0.9 - 0.18, -0.6, wv_z), (-0.9 + 0.18, -0.6, wv_z),
           (-0.9 + 0.22, -0.6, wv_z + 0.04), (-0.9 - 0.14, -0.6, wv_z + 0.04)]
    mesh_from_pydata("WeatherVane", wvv, [(0, 1, 2, 3)], m['iron'])

    # Organized crop plots (neat rows)
    for row in range(3):
        for col in range(2):
            px = 0.5 + col * 0.50
            py = -0.5 - row * 0.35
            bmesh_box(f"CropPlot_{row}_{col}", (0.40, 0.28, 0.04), (px, py, Z + 0.02), m['ground'])

    # Iron fence along front
    for i in range(6):
        fy = -0.7 + i * 0.28
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.008, depth=0.30,
                                            location=(1.40, fy, BZ + 0.05))
        bpy.context.active_object.data.materials.append(m['iron'])


# ============================================================
# INDUSTRIAL AGE -- Steel-framed barn with silo, equipment
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Foundation
    bmesh_box("Found", (2.8, 2.2, 0.10), (0, 0, Z + 0.05), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.10

    # Main barn (steel-framed, brick lower, corrugated upper)
    wall_h = 2.0
    bmesh_box("BarnLower", (2.4, 1.8, 0.8), (0, 0, BZ + 0.4), m['stone'], bevel=0.02)
    bmesh_box("BarnUpper", (2.4, 1.8, wall_h - 0.8), (0, 0, BZ + 0.8 + (wall_h - 0.8) / 2), m['iron'], bevel=0.01)

    # Iron beam grid on facade
    for z in [BZ + 0.6, BZ + 1.2, BZ + 1.8]:
        bmesh_box(f"IronH_{z:.1f}", (0.03, 1.8, 0.04), (1.21, 0, z), m['iron'])
    for y in [-0.6, 0, 0.6]:
        bmesh_box(f"IronV_{y:.1f}", (0.03, 0.04, wall_h), (1.21, y, BZ + wall_h / 2), m['iron'])

    # Band between materials
    bmesh_box("Band", (2.44, 1.84, 0.04), (0, 0, BZ + 0.80), m['stone_trim'])

    # Gambrel (barn) roof
    half_w = 1.30
    rv = [
        (-half_w, -0.95, BZ + wall_h),
        (half_w, -0.95, BZ + wall_h),
        (half_w, 0.95, BZ + wall_h),
        (-half_w, 0.95, BZ + wall_h),
        (-0.55, -0.95, BZ + wall_h + 0.60),
        (0.55, -0.95, BZ + wall_h + 0.60),
        (0.55, 0.95, BZ + wall_h + 0.60),
        (-0.55, 0.95, BZ + wall_h + 0.60),
        (0, -0.95, BZ + wall_h + 0.85),
        (0, 0.95, BZ + wall_h + 0.85),
    ]
    rf = [
        (0, 3, 7, 4),       # left lower slope
        (1, 2, 6, 5),       # right lower slope
        (4, 7, 9, 8),       # left upper slope
        (5, 6, 9, 8),       # right upper slope
        (0, 1, 5, 4),       # front gable lower
        (4, 5, 8),          # front gable upper
        (2, 3, 7, 6),       # back gable lower
        (6, 7, 9),          # back gable upper
    ]
    r = mesh_from_pydata("BarnRoof", rv, rf, m['stone_dark'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Ridge
    bmesh_box("Ridge", (0.04, 1.94, 0.04), (0, 0, BZ + wall_h + 0.85), m['iron'])

    # Large barn doors (double)
    for y_off in [-0.18, 0.18]:
        bmesh_box(f"BarnDoor_{y_off:.2f}", (0.06, 0.30, 1.20), (1.21, y_off, BZ + 0.60), m['door'])
    bmesh_box("DoorFrame", (0.07, 0.70, 0.06), (1.22, 0, BZ + 1.23), m['iron'])

    # Windows
    for y in [-0.60, 0.60]:
        bmesh_box(f"Win_{y:.1f}", (0.05, 0.18, 0.30), (1.21, y, BZ + 1.40), m['window'])
        bmesh_box(f"WinH_{y:.1f}", (0.06, 0.22, 0.03), (1.22, y, BZ + 1.57), m['stone_trim'])

    # Side windows
    for x in [-0.50, 0.50]:
        bmesh_box(f"SWin_{x:.1f}", (0.18, 0.05, 0.30), (x, -0.91, BZ + 1.40), m['window'])

    # Cylindrical grain silo (tall, metal)
    silo_h = 2.8
    bmesh_prism("Silo", 0.35, silo_h, 12, (-1.2, -0.3, Z), m['iron'])
    bmesh_prism("SiloBand1", 0.37, 0.05, 12, (-1.2, -0.3, Z + 0.70), m['stone_trim'])
    bmesh_prism("SiloBand2", 0.37, 0.05, 12, (-1.2, -0.3, Z + 1.40), m['stone_trim'])
    bmesh_prism("SiloBand3", 0.37, 0.05, 12, (-1.2, -0.3, Z + 2.10), m['stone_trim'])
    bmesh_cone("SiloRoof", 0.40, 0.35, 12, (-1.2, -0.3, Z + silo_h), m['stone_dark'])

    # Silo access ladder
    for lz in range(8):
        bmesh_box(f"Rung_{lz}", (0.04, 0.14, 0.02), (-1.2 + 0.36, -0.3, Z + 0.35 * lz + 0.20), m['iron'])

    # Mechanical equipment (simple cart/plow suggestion)
    bmesh_box("CartBody", (0.50, 0.30, 0.15), (1.3, 0.80, Z + 0.18), m['wood_dark'])
    bmesh_box("CartHandle", (0.35, 0.04, 0.04), (1.55, 0.80, Z + 0.30), m['iron'])
    # Wheels
    for dy in [-0.17, 0.17]:
        bmesh_prism(f"Wheel_{dy:.2f}", 0.10, 0.03, 10, (1.3, 0.80 + dy, Z + 0.10), m['iron'])

    # Steps
    for i in range(2):
        bmesh_box(f"Step_{i}", (0.14, 0.80, 0.04), (1.32 + i * 0.14, 0, BZ - 0.02 - i * 0.04), m['stone_dark'])

    # Chimney (small, industrial)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06, depth=0.60,
                                        location=(-0.70, 0.60, BZ + wall_h + 0.85 + 0.30))
    bpy.context.active_object.data.materials.append(m['iron'])


# ============================================================
# MODERN AGE -- Agricultural facility with greenhouse, silo
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.08
    bmesh_box("Found", (3.2, 2.8, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # Main facility building (concrete/steel)
    main_h = 1.8
    bmesh_box("MainBuilding", (2.0, 1.6, main_h), (0.3, 0.3, BZ + main_h / 2), m['stone'], bevel=0.02)

    # Flat roof with overhang
    bmesh_box("MainRoof", (2.2, 1.8, 0.06), (0.3, 0.3, BZ + main_h + 0.03), m['stone_dark'])

    # Large front windows
    bmesh_box("FrontGlass", (0.05, 1.0, main_h - 0.4), (1.31, 0.3, BZ + main_h / 2 + 0.10), glass)
    # Mullions
    for y in [0.0, 0.3, 0.6]:
        bmesh_box(f"Mull_{y:.1f}", (0.03, 0.02, main_h - 0.4), (1.32, y, BZ + main_h / 2 + 0.10), metal)
    # Horizontal mullion
    bmesh_box("HMull", (0.03, 1.02, 0.02), (1.32, 0.3, BZ + main_h / 2), metal)

    # Front door
    bmesh_box("Door", (0.05, 0.40, 1.10), (1.31, -0.15, BZ + 0.55), glass)
    bmesh_box("DoorFrame", (0.06, 0.44, 1.14), (1.32, -0.15, BZ + 0.57), metal)

    # Side windows
    for x in [-0.20, 0.60]:
        bmesh_box(f"SWin_{x:.1f}", (0.28, 0.05, 0.50), (x, -0.41, BZ + 1.20), glass)

    # Greenhouse section (attached, glass with metal frame)
    gh_h = 1.5
    bmesh_box("GreenBase", (1.4, 1.2, 0.10), (-0.9, -0.5, BZ + 0.05), m['stone_dark'])

    # Glass walls
    bmesh_box("GHFront", (0.04, 1.2, gh_h - 0.2), (-0.19, -0.5, BZ + 0.10 + gh_h / 2 - 0.10), glass)
    bmesh_box("GHBack", (0.04, 1.2, gh_h - 0.2), (-1.61, -0.5, BZ + 0.10 + gh_h / 2 - 0.10), glass)
    bmesh_box("GHSide", (1.4, 0.04, gh_h - 0.2), (-0.9, -1.11, BZ + 0.10 + gh_h / 2 - 0.10), glass)
    bmesh_box("GHSide2", (1.4, 0.04, gh_h - 0.2), (-0.9, 0.11, BZ + 0.10 + gh_h / 2 - 0.10), glass)

    # Greenhouse metal frame
    for x in [-1.50, -0.90, -0.30]:
        bmesh_box(f"GHFrame_{x:.2f}", (0.03, 0.03, gh_h), (x, -1.10, BZ + 0.10 + gh_h / 2), metal)
        bmesh_box(f"GHFrame2_{x:.2f}", (0.03, 0.03, gh_h), (x, 0.10, BZ + 0.10 + gh_h / 2), metal)

    # Greenhouse roof (angled glass)
    grv = [(-1.62, -1.12, BZ + 0.10 + gh_h - 0.2),
           (-0.18, -1.12, BZ + 0.10 + gh_h - 0.2),
           (-0.18, 0.12, BZ + 0.10 + gh_h - 0.2),
           (-1.62, 0.12, BZ + 0.10 + gh_h - 0.2),
           (-0.90, -1.12, BZ + 0.10 + gh_h + 0.15),
           (-0.90, 0.12, BZ + 0.10 + gh_h + 0.15)]
    grf = [(0, 3, 5, 4), (1, 2, 5, 4)]
    mesh_from_pydata("GHRoof", grv, grf, glass)

    # Greenhouse roof frame
    bmesh_box("GHRoofRidge", (0.03, 1.28, 0.03), (-0.90, -0.5, BZ + 0.10 + gh_h + 0.15), metal)

    # Growing beds inside greenhouse suggestion
    for row in range(2):
        bmesh_box(f"GrowBed_{row}", (1.1, 0.35, 0.08), (-0.9, -0.2 - row * 0.55, BZ + 0.14), m['ground'])

    # Metal grain silo (large, cylindrical)
    silo_h = 2.5
    bmesh_prism("Silo", 0.40, silo_h, 14, (1.2, -0.9, Z), metal)
    bmesh_prism("SiloBand1", 0.42, 0.04, 14, (1.2, -0.9, Z + 0.60), m['stone_trim'])
    bmesh_prism("SiloBand2", 0.42, 0.04, 14, (1.2, -0.9, Z + 1.20), m['stone_trim'])
    bmesh_prism("SiloBand3", 0.42, 0.04, 14, (1.2, -0.9, Z + 1.80), m['stone_trim'])
    # Silo domed top
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.40, location=(1.2, -0.9, Z + silo_h))
    dome = bpy.context.active_object
    dome.name = "SiloDome"
    dome.scale = (1, 1, 0.35)
    dome.data.materials.append(metal)
    bpy.ops.object.shade_smooth()

    # Loading dock / concrete pad
    bmesh_box("LoadingDock", (1.0, 0.60, 0.12), (0.3, -1.2, Z + 0.06), m['stone_dark'])

    # Equipment (small tractor shape)
    bmesh_box("TractorBody", (0.35, 0.22, 0.18), (0.3, -1.2, Z + 0.20), m['stone_trim'])
    bmesh_box("TractorCab", (0.18, 0.20, 0.15), (0.22, -1.2, Z + 0.38 + 0.075), metal)

    # Patio / canopy over entrance
    bmesh_box("Canopy", (0.55, 0.80, 0.04), (1.55, 0.1, BZ + main_h - 0.3), metal)
    for y in [-0.25, 0.45]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=main_h - 0.3,
                                            location=(1.55, y, BZ + (main_h - 0.3) / 2))
        bpy.context.active_object.data.materials.append(metal)


# ============================================================
# DIGITAL AGE -- Automated vertical farm with LED levels, drone pad
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.06
    bmesh_box("Found", (3.0, 2.6, 0.06), (0, 0, Z + 0.03), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # Main vertical farm tower (glass with visible growing levels)
    tower_h = 3.5
    tower_w = 1.6
    tower_d = 1.4

    # Glass exterior
    bmesh_box("TowerGlass", (tower_w, tower_d, tower_h), (0, 0.1, BZ + tower_h / 2), glass)

    # Steel frame grid
    for z in [BZ + 0.70, BZ + 1.40, BZ + 2.10, BZ + 2.80, BZ + 3.45]:
        bmesh_box(f"HFrame_{z:.2f}", (tower_w + 0.02, tower_d + 0.02, 0.04), (0, 0.1, z), metal)
    for x in [-0.6, 0, 0.6]:
        bmesh_box(f"VFrameF_{x:.1f}", (0.03, 0.03, tower_h), (x, 0.1 - tower_d / 2 - 0.01, BZ + tower_h / 2), metal)
        bmesh_box(f"VFrameB_{x:.1f}", (0.03, 0.03, tower_h), (x, 0.1 + tower_d / 2 + 0.01, BZ + tower_h / 2), metal)
    for y in [-0.45, 0.10, 0.65]:
        bmesh_box(f"VFrameR_{y:.2f}", (0.03, 0.03, tower_h), (tower_w / 2 + 0.01, y, BZ + tower_h / 2), metal)
        bmesh_box(f"VFrameL_{y:.2f}", (0.03, 0.03, tower_h), (-tower_w / 2 - 0.01, y, BZ + tower_h / 2), metal)

    # LED growing levels (glowing strips inside tower, visible through glass)
    for level in range(5):
        lz = BZ + 0.40 + level * 0.70
        # LED strip (gold = glowing)
        bmesh_box(f"LED_{level}", (tower_w - 0.20, tower_d - 0.20, 0.03), (0, 0.1, lz), m['gold'])
        # Growing tray (green)
        bmesh_box(f"GrowTray_{level}", (tower_w - 0.30, tower_d - 0.30, 0.06), (0, 0.1, lz + 0.05), m['ground'])

    # Tower flat roof
    bmesh_box("TowerRoof", (tower_w + 0.08, tower_d + 0.08, 0.06), (0, 0.1, BZ + tower_h + 0.03), metal)

    # Communication antenna on roof
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.60,
                                        location=(0, 0.1, BZ + tower_h + 0.36))
    bpy.context.active_object.data.materials.append(metal)
    # Small dish on antenna
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0, 0.1, BZ + tower_h + 0.68))
    dish = bpy.context.active_object
    dish.name = "AntennaDish"
    dish.scale = (0.5, 1, 0.3)
    dish.data.materials.append(metal)
    bpy.ops.object.shade_smooth()

    # Entrance (glass door with metal frame)
    bmesh_box("EntranceFrame", (0.06, 0.45, 1.10), (tower_w / 2 + 0.01, 0.1, BZ + 0.58), metal)
    bmesh_box("EntranceGlass", (0.04, 0.40, 1.04), (tower_w / 2 + 0.02, 0.1, BZ + 0.58), glass)

    # Entrance path
    bmesh_box("Path", (0.40, 0.50, 0.02), (tower_w / 2 + 0.30, 0.1, BZ + 0.01), m['stone_light'])

    # LED accent strip around tower base
    bmesh_box("LEDBase1", (tower_w + 0.06, 0.04, 0.05), (0, 0.1 - tower_d / 2, BZ + 0.05), m['gold'])
    bmesh_box("LEDBase2", (tower_w + 0.06, 0.04, 0.05), (0, 0.1 + tower_d / 2, BZ + 0.05), m['gold'])
    bmesh_box("LEDBase3", (0.04, tower_d + 0.06, 0.05), (tower_w / 2, 0.1, BZ + 0.05), m['gold'])
    bmesh_box("LEDBase4", (0.04, tower_d + 0.06, 0.05), (-tower_w / 2, 0.1, BZ + 0.05), m['gold'])

    # Drone landing pad (hexagonal platform)
    bmesh_prism("DronePad", 0.45, 0.04, 6, (1.2, -0.9, Z + 0.02), m['stone_dark'])
    # Pad markings (concentric ring)
    bmesh_prism("PadRing", 0.35, 0.01, 6, (1.2, -0.9, Z + 0.05), m['gold'])
    bmesh_prism("PadCenter", 0.10, 0.01, 6, (1.2, -0.9, Z + 0.05), m['gold'])

    # Drone (small quadcopter suggestion)
    drone_z = Z + 0.30
    bmesh_box("DroneBody", (0.12, 0.12, 0.04), (1.2, -0.9, drone_z), metal)
    for dx, dy in [(-0.12, -0.12), (-0.12, 0.12), (0.12, -0.12), (0.12, 0.12)]:
        bmesh_box(f"DroneArm_{dx:.2f}_{dy:.2f}", (0.10, 0.02, 0.02),
                  (1.2 + dx, -0.9 + dy, drone_z), metal)
        bmesh_prism(f"Rotor_{dx:.2f}_{dy:.2f}", 0.06, 0.01, 8,
                    (1.2 + dx * 1.5, -0.9 + dy * 1.5, drone_z + 0.02), m['gold'])

    # Control terminal (small screen on pedestal)
    bmesh_box("Terminal", (0.08, 0.08, 0.55), (1.0, 0.75, Z + 0.275), metal)
    bmesh_box("Screen", (0.04, 0.14, 0.12), (1.04, 0.75, Z + 0.60), m['gold'])

    # Automated water tank (small cylinder)
    bmesh_prism("WaterTank", 0.25, 0.70, 10, (-1.1, -0.6, Z), metal)
    bmesh_prism("TankBand", 0.27, 0.03, 10, (-1.1, -0.6, Z + 0.35), m['stone_trim'])
    # Pipe from tank to tower
    bmesh_box("Pipe", (0.80, 0.04, 0.04), (-0.60, -0.3, Z + 0.55), metal)

    # Solar panels on ground
    for i in range(2):
        bmesh_box(f"Solar_{i}", (0.50, 0.35, 0.03), (-1.0, 0.5 + i * 0.45, Z + 0.22 + i * 0.02), glass)
        bmesh_box(f"SolarFrame_{i}", (0.52, 0.37, 0.02), (-1.0, 0.5 + i * 0.45, Z + 0.21 + i * 0.02), metal)
    # Solar panel stand
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.30,
                                        location=(-1.0, 0.72, Z + 0.10))
    bpy.context.active_object.data.materials.append(metal)

    # Landscaping (modern planters)
    for y in [-0.8, 0.8]:
        bmesh_box(f"Planter_{y:.1f}", (0.30, 0.15, 0.12), (tower_w / 2 + 0.30, y, Z + 0.06), m['stone_dark'])


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


def build_farm(materials, age='medieval'):
    """Build a Farm with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
