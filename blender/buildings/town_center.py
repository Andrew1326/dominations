"""
Town Center building — grand main structure per age, befitting the most
important building in the player's civilization.

Stone:         Chieftain's palisade compound with great hut and watchtower
Bronze:        Stepped mud-brick citadel with guard towers and palace
Iron:          Stone hillfort with great hall, round towers, heavy gate
Classical:     Grand acropolis — colonnade temple, stoa wings, ceremonial stairs
Medieval:      Castle keep with 4 corner towers, curtain walls, gatehouse
Gunpowder:     Star-fort palace with angular bastions and cannon tower
Enlightenment: Baroque palace with dome, symmetrical wings, clock tower
Industrial:    Grand Victorian civic hall with clock tower, iron framework
Modern:        Government complex — glass tower + lower wings, plaza
Digital:       High-tech campus — glass tower, connected wings, spire
"""

import bpy
import bmesh
import math
import random

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# ============================================================
# STONE AGE — Chieftain's palisade compound
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Palisade wall (ring of logs) ===
    pal_r = 2.2
    n_logs = 28
    for i in range(n_logs):
        a = (2 * math.pi * i) / n_logs
        px, py = pal_r * math.cos(a), pal_r * math.sin(a)
        h = 1.4 + 0.15 * math.sin(i * 3.7)  # uneven tops
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.08, depth=h,
                                            location=(px, py, Z + h / 2))
        log = bpy.context.active_object
        log.name = f"Palisade_{i}"
        log.data.materials.append(m['wood'])

    # Palisade gate opening (remove logs at front, add frame)
    bmesh_box("GatePostL", (0.12, 0.12, 1.6), (pal_r + 0.05, -0.30, Z + 0.8), m['wood_dark'])
    bmesh_box("GatePostR", (0.12, 0.12, 1.6), (pal_r + 0.05, 0.30, Z + 0.8), m['wood_dark'])
    bmesh_box("GateLintel", (0.12, 0.72, 0.10), (pal_r + 0.05, 0, Z + 1.65), m['wood_dark'])

    # === Great hut (large central structure) ===
    bmesh_prism("HutBase", 1.5, 0.20, 16, (0, 0, Z), m['stone_dark'])
    bmesh_prism("HutWall", 1.45, 1.8, 16, (0, 0, Z + 0.20), m['stone'])
    bmesh_cone("HutRoof", 2.0, 2.0, 20, (0, 0, Z + 2.0), m['roof'])
    bmesh_prism("SmokeHole", 0.20, 0.15, 8, (0, 0, Z + 3.95), m['wood'])

    # Support poles around great hut
    for i in range(8):
        a = (2 * math.pi * i) / 8
        px, py = 1.35 * math.cos(a), 1.35 * math.sin(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.06, depth=2.2,
                                            location=(px, py, Z + 1.1))
        pole = bpy.context.active_object
        pole.name = f"HutPole_{i}"
        pole.data.materials.append(m['wood'])

    # Door
    bmesh_box("Door", (0.12, 0.55, 1.10), (1.46, 0, Z + 0.75), m['door'])

    # === Secondary hut (smaller, side) ===
    bmesh_prism("Hut2Wall", 0.70, 1.0, 10, (-1.0, 1.0, Z + 0.10), m['stone'])
    bmesh_cone("Hut2Roof", 0.95, 1.1, 12, (-1.0, 1.0, Z + 1.10), m['roof'])

    # === Wooden watchtower ===
    TX, TY = -1.5, -1.2
    for cx, cy in [(TX - 0.25, TY - 0.25), (TX - 0.25, TY + 0.25),
                   (TX + 0.25, TY - 0.25), (TX + 0.25, TY + 0.25)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=3.0,
                                            location=(cx, cy, Z + 1.5))
        p = bpy.context.active_object
        p.name = f"TWPole_{cx:.1f}_{cy:.1f}"
        p.data.materials.append(m['wood'])
    bmesh_box("TWPlatform", (0.65, 0.65, 0.06), (TX, TY, Z + 2.6), m['wood'])
    bmesh_box("TWRail", (0.70, 0.70, 0.20), (TX, TY, Z + 2.75), m['wood_dark'])
    bmesh_cone("TWRoof", 0.55, 0.6, 8, (TX, TY, Z + 2.95), m['roof'])

    # === Fire pit (large, central gathering) ===
    bmesh_prism("FirePit", 0.45, 0.10, 10, (1.0, -0.8, Z + 0.05), m['stone_dark'])
    for angle in [0.2, -0.3, 0.8, -0.8]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.5,
                                            location=(1.0, -0.8, Z + 0.15))
        log = bpy.context.active_object
        log.name = f"FireLog_{angle:.1f}"
        log.rotation_euler = (0.3, angle, 0)
        log.data.materials.append(m['wood_dark'])

    # === Totem poles ===
    for tx, ty in [(1.8, 1.5), (-0.3, -1.8)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.09, depth=2.5,
                                            location=(tx, ty, Z + 1.25))
        t = bpy.context.active_object
        t.name = f"Totem_{tx:.1f}"
        t.data.materials.append(m['wood'])
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(tx, ty, Z + 2.60))
        h = bpy.context.active_object
        h.name = f"TotemHead_{tx:.1f}"
        h.data.materials.append(m['wood_dark'])

    # Skull decorations on gate
    for ys in [-0.20, 0.20]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(pal_r + 0.12, ys, Z + 1.35))
        sk = bpy.context.active_object
        sk.name = f"Skull_{ys:.1f}"
        sk.data.materials.append(m['stone_light'])

    # Animal skin over door
    sv = [(1.47, -0.35, Z + 1.55), (1.47, 0.35, Z + 1.55),
          (1.49, 0.30, Z + 0.85), (1.49, -0.30, Z + 0.90)]
    mesh_from_pydata("Skin", sv, [(0, 1, 2, 3)], m['roof_edge'])
    m['roof_edge'].use_backface_culling = False


# ============================================================
# BRONZE AGE — Stepped mud-brick citadel
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Stepped platform (ziggurat-style, 3 tiers) ===
    for i, (w, d, h) in enumerate([(4.8, 4.4, 0.25), (4.0, 3.6, 0.25), (3.2, 2.8, 0.25)]):
        bmesh_box(f"Plat_{i}", (w, d, h), (0, 0, Z + h / 2 + i * 0.25), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.75  # base of walls

    # === Perimeter walls ===
    WALL_H = 2.0
    hw = 1.8
    bmesh_box("WallF", (0.20, hw * 2, WALL_H), (hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallB", (0.20, hw * 2, WALL_H), (-hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallR", (hw * 2, 0.20, WALL_H), (0, -hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallL", (hw * 2, 0.20, WALL_H), (0, hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)

    # Wall-top walkway
    for label, pos in [("F", (hw, 0)), ("B", (-hw, 0)), ("R", (0, -hw)), ("L", (0, hw))]:
        if label in ("F", "B"):
            bmesh_box(f"Walk_{label}", (0.30, hw * 2, 0.06), (*pos, BZ + WALL_H + 0.03), m['stone_trim'])
        else:
            bmesh_box(f"Walk_{label}", (hw * 2, 0.30, 0.06), (*pos, BZ + WALL_H + 0.03), m['stone_trim'])

    # Battlements
    for i in range(8):
        y = -1.4 + i * 0.40
        bmesh_box(f"MF_{i}", (0.10, 0.16, 0.20), (hw + 0.05, y, BZ + WALL_H + 0.16), m['stone_trim'])
        bmesh_box(f"MB_{i}", (0.10, 0.16, 0.20), (-hw - 0.05, y, BZ + WALL_H + 0.16), m['stone_trim'])
    for i in range(8):
        x = -1.4 + i * 0.40
        bmesh_box(f"MR_{i}", (0.16, 0.10, 0.20), (x, -hw - 0.05, BZ + WALL_H + 0.16), m['stone_trim'])
        bmesh_box(f"ML_{i}", (0.16, 0.10, 0.20), (x, hw + 0.05, BZ + WALL_H + 0.16), m['stone_trim'])

    # === 4 Square guard towers ===
    tower_h = 3.0
    for xs, ys, label in [(-1, -1, "BL"), (-1, 1, "FL"), (1, -1, "BR"), (1, 1, "FR")]:
        tx, ty = xs * hw, ys * hw
        bmesh_box(f"Tower_{label}", (0.55, 0.55, tower_h), (tx, ty, BZ + tower_h / 2), m['stone_upper'], bevel=0.02)
        bmesh_box(f"TTop_{label}", (0.62, 0.62, 0.08), (tx, ty, BZ + tower_h + 0.04), m['stone_trim'])
        # Tower merlons
        for dx, dy in [(-0.28, 0), (0.28, 0), (0, -0.28), (0, 0.28)]:
            bmesh_box(f"TM_{label}_{dx:.1f}_{dy:.1f}", (0.12, 0.12, 0.18),
                      (tx + dx, ty + dy, BZ + tower_h + 0.17), m['stone_trim'])
        # Flat mud-brick cap
        bmesh_box(f"TCap_{label}", (0.50, 0.50, 0.04), (tx, ty, BZ + tower_h + 0.30), m['stone_dark'])

    # === Central palace (taller inner building) ===
    palace_h = 2.8
    bmesh_box("Palace", (1.6, 1.3, palace_h), (0, 0, BZ + palace_h / 2), m['stone'], bevel=0.03)
    bmesh_box("PalaceTop", (1.7, 1.4, 0.08), (0, 0, BZ + palace_h + 0.04), m['stone_trim'], bevel=0.02)

    # Palace second tier
    bmesh_box("Palace2", (1.0, 0.8, 1.2), (0, 0, BZ + palace_h + 0.08 + 0.6), m['stone'], bevel=0.02)
    bmesh_box("Palace2Top", (1.1, 0.9, 0.06), (0, 0, BZ + palace_h + 1.32), m['stone_trim'])

    # Gate
    bmesh_box("Gate", (0.10, 0.60, 1.20), (hw + 0.01, 0, BZ + 0.60), m['door'])
    bmesh_box("GateFrame", (0.12, 0.72, 0.08), (hw + 0.02, 0, BZ + 1.24), m['wood'])

    # Windows
    for y in [-0.6, 0.6]:
        bmesh_box(f"PWin_{y:.1f}", (0.06, 0.14, 0.35), (0.81, y, BZ + palace_h - 0.6), m['window'])
    for x in [-0.4, 0.4]:
        bmesh_box(f"PWinS_{x:.1f}", (0.14, 0.06, 0.35), (x, -0.66, BZ + palace_h - 0.6), m['window'])

    # Steps
    for i in range(6):
        bmesh_box(f"Step_{i}", (0.22, 1.2, 0.06), (hw + 0.40 + i * 0.24, 0, BZ - 0.04 - i * 0.06), m['stone_dark'])

    # Banner
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=1.0,
                                        location=(0, 0, BZ + palace_h + 1.85))
    bpy.context.active_object.data.materials.append(m['wood'])
    bv = [(0.04, 0, BZ + palace_h + 2.10), (0.50, 0.03, BZ + palace_h + 2.05),
          (0.50, 0.02, BZ + palace_h + 2.35), (0.04, 0, BZ + palace_h + 2.33)]
    mesh_from_pydata("Banner", bv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False

    # Clay pots near entrance
    for i, (px, py) in enumerate([(hw + 0.3, 0.7), (hw + 0.4, -0.6), (hw + 0.2, -0.8)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(px, py, BZ + 0.08))
        pot = bpy.context.active_object
        pot.name = f"Pot_{i}"
        pot.scale = (1, 1, 0.8)
        pot.data.materials.append(m['roof'])


# ============================================================
# IRON AGE — Stone hillfort with great hall
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Stone foundation (raised mound) ===
    bmesh_box("Mound", (5.0, 4.6, 0.20), (0, 0, Z + 0.10), m['stone_dark'], bevel=0.06)
    bmesh_box("Mound2", (4.6, 4.2, 0.15), (0, 0, Z + 0.28), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.35
    WALL_H = 2.6
    hw = 2.0

    # === Thick fortress walls ===
    wt = 0.25
    bmesh_box("WallF", (wt, hw * 2, WALL_H), (hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallB", (wt, hw * 2, WALL_H), (-hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallR", (hw * 2, wt, WALL_H), (0, -hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallL", (hw * 2, wt, WALL_H), (0, hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)

    # Battlements
    merlon_z = BZ + WALL_H + 0.06
    for i in range(9):
        y = -1.6 + i * 0.40
        bmesh_box(f"MF_{i}", (0.12, 0.16, 0.22), (hw + 0.06, y, merlon_z + 0.11), m['stone_trim'], bevel=0.01)
        bmesh_box(f"MB_{i}", (0.12, 0.16, 0.22), (-hw - 0.06, y, merlon_z + 0.11), m['stone_trim'], bevel=0.01)
    for i in range(9):
        x = -1.6 + i * 0.40
        bmesh_box(f"MR_{i}", (0.16, 0.12, 0.22), (x, -hw - 0.06, merlon_z + 0.11), m['stone_trim'], bevel=0.01)
        bmesh_box(f"ML_{i}", (0.16, 0.12, 0.22), (x, hw + 0.06, merlon_z + 0.11), m['stone_trim'], bevel=0.01)

    # === 4 Round towers ===
    tower_r = 0.50
    tower_h = 3.8
    for xs, ys, label in [(-1, -1, "BL"), (-1, 1, "FL"), (1, -1, "BR"), (1, 1, "FR")]:
        tx, ty = xs * hw, ys * hw
        bmesh_prism(f"Tower_{label}", tower_r, tower_h, 10, (tx, ty, BZ), m['stone_upper'], bevel=0.02)
        for tz in [BZ + 1.3, BZ + 2.6, BZ + tower_h - 0.12]:
            bmesh_prism(f"TB_{label}_{tz:.1f}", tower_r + 0.03, 0.06, 10, (tx, ty, tz), m['stone_trim'])
        bmesh_prism(f"TP_{label}", tower_r + 0.06, 0.12, 10, (tx, ty, BZ + tower_h), m['stone_trim'])
        # Merlons
        for i in range(6):
            a = (2 * math.pi * i) / 6
            bmesh_box(f"TM_{label}_{i}", (0.10, 0.10, 0.16),
                      (tx + (tower_r + 0.08) * math.cos(a), ty + (tower_r + 0.08) * math.sin(a),
                       BZ + tower_h + 0.20), m['stone_trim'], bevel=0.01)
        bmesh_cone(f"TR_{label}", tower_r + 0.08, 1.0, 10, (tx, ty, BZ + tower_h + 0.28), m['roof'])

    # === Great hall (central, large) ===
    hall_w, hall_d, hall_h = 2.2, 1.8, 2.8
    bmesh_box("Hall", (hall_w, hall_d, hall_h), (0, 0, BZ + hall_h / 2), m['stone'], bevel=0.03)
    bmesh_box("HallBand", (hall_w + 0.04, hall_d + 0.04, 0.08), (0, 0, BZ + hall_h), m['stone_trim'], bevel=0.02)

    # Pitched roof on great hall
    rv = [
        (-hall_w / 2 - 0.12, -hall_d / 2 - 0.12, BZ + hall_h + 0.04),
        (hall_w / 2 + 0.12, -hall_d / 2 - 0.12, BZ + hall_h + 0.04),
        (hall_w / 2 + 0.12, hall_d / 2 + 0.12, BZ + hall_h + 0.04),
        (-hall_w / 2 - 0.12, hall_d / 2 + 0.12, BZ + hall_h + 0.04),
        (0, -hall_d / 2 - 0.12, BZ + hall_h + 1.3),
        (0, hall_d / 2 + 0.12, BZ + hall_h + 1.3),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("HallRoof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Hall windows
    for y in [-0.55, 0.55]:
        for kz in [BZ + 1.2, BZ + 2.2]:
            bmesh_box(f"HWin_{y:.1f}_{kz:.1f}", (0.07, 0.12, 0.40), (hall_w / 2 + 0.01, y, kz), m['window'])
    for x in [-0.6, 0, 0.6]:
        bmesh_box(f"HWinS_{x:.1f}", (0.12, 0.07, 0.40), (x, -hall_d / 2 - 0.01, BZ + 1.8), m['window'])

    # Heavy door with iron bands
    bmesh_box("Door", (0.10, 0.65, 1.30), (hw + 0.01, 0, BZ + 0.65), m['door'])
    for z_off in [0.3, 0.7, 1.1]:
        bmesh_box(f"IronBand_{z_off:.1f}", (0.11, 0.70, 0.04), (hw + 0.02, 0, BZ + z_off), m['iron'])

    # Steps
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.22, 1.2, 0.07), (hw + 0.40 + i * 0.24, 0, BZ - 0.04 - i * 0.07), m['stone_dark'])

    # Banner on front-right tower
    TX, TY = hw, -hw
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.8,
                                        location=(TX, TY, BZ + tower_h + 1.28 + 0.4))
    bpy.context.active_object.data.materials.append(m['wood'])
    fz = BZ + tower_h + 1.68 + 0.15
    fv = [(TX + 0.03, TY, fz), (TX + 0.45, TY + 0.03, fz - 0.05),
          (TX + 0.45, TY + 0.02, fz + 0.25), (TX + 0.03, TY, fz + 0.22)]
    mesh_from_pydata("Banner", fv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# CLASSICAL AGE — Grand acropolis temple complex
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (6.0, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Grand stepped platform (5 tiers) ===
    for i in range(5):
        w = 5.2 - i * 0.30
        d = 4.8 - i * 0.25
        bmesh_box(f"Plat_{i}", (w, d, 0.10), (0, 0, Z + 0.05 + i * 0.10), m['stone_light'], bevel=0.02)

    BZ = Z + 0.50
    col_h = 2.5
    col_r = 0.12

    # === Main temple (cella) ===
    bmesh_box("Cella", (2.4, 2.0, 2.2), (0, 0, BZ + 1.1), m['stone_light'], bevel=0.02)

    # === Front colonnade (6 columns) ===
    for i, y in enumerate([-1.2, -0.72, -0.24, 0.24, 0.72, 1.2]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=col_r, depth=col_h,
                                            location=(1.65, y, BZ + col_h / 2))
        c = bpy.context.active_object
        c.name = f"ColF_{i}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        bmesh_box(f"CapF_{i}", (0.28, 0.28, 0.08), (1.65, y, BZ + col_h + 0.04), m['stone_trim'])
        bmesh_box(f"BaseF_{i}", (0.26, 0.26, 0.06), (1.65, y, BZ + 0.03), m['stone_trim'])

    # Back colonnade (6 columns)
    for i, y in enumerate([-1.2, -0.72, -0.24, 0.24, 0.72, 1.2]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=col_r, depth=col_h,
                                            location=(-1.65, y, BZ + col_h / 2))
        c = bpy.context.active_object
        c.name = f"ColB_{i}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        bmesh_box(f"CapB_{i}", (0.28, 0.28, 0.08), (-1.65, y, BZ + col_h + 0.04), m['stone_trim'])

    # Side columns (4 per side)
    for x in [-0.9, -0.3, 0.3, 0.9]:
        for ys, lbl in [(-1.35, "R"), (1.35, "L")]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=col_r, depth=col_h,
                                                location=(x, ys, BZ + col_h / 2))
            c = bpy.context.active_object
            c.name = f"Col{lbl}_{x:.1f}"
            c.data.materials.append(m['stone_light'])
            bpy.ops.object.shade_smooth()

    # Entablature
    bmesh_box("Entablature", (3.5, 2.9, 0.18), (0, 0, BZ + col_h + 0.09), m['stone_trim'], bevel=0.02)

    # Pediments (front + back)
    for xs, name in [(1, "Front"), (-1, "Back")]:
        pv = [(xs * 1.75, -1.45, BZ + col_h + 0.18),
              (xs * 1.75, 1.45, BZ + col_h + 0.18),
              (xs * 1.75, 0, BZ + col_h + 0.95)]
        mesh_from_pydata(f"Ped{name}", pv, [(0, 1, 2)], m['stone_light'])

    # Roof
    rv = [
        (-1.8, -1.5, BZ + col_h + 0.18), (1.8, -1.5, BZ + col_h + 0.18),
        (1.8, 1.5, BZ + col_h + 0.18), (-1.8, 1.5, BZ + col_h + 0.18),
        (0, -1.5, BZ + col_h + 1.0), (0, 1.5, BZ + col_h + 1.0),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("Roof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # === Stoa wings (covered walkways on sides) ===
    for ys, lbl in [(-2.0, "R"), (2.0, "L")]:
        bmesh_box(f"Stoa_{lbl}", (2.8, 0.6, 1.6), (0, ys, BZ + 0.8), m['stone_light'], bevel=0.02)
        bmesh_box(f"StoaRoof_{lbl}", (3.0, 0.7, 0.06), (0, ys, BZ + 1.64), m['stone_trim'])
        # Stoa columns
        for x in [-1.1, -0.4, 0.4, 1.1]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=1.5,
                                                location=(x, ys - 0.25 * (-1 if ys < 0 else 1), BZ + 0.75))
            sc = bpy.context.active_object
            sc.name = f"StoaCol_{lbl}_{x:.1f}"
            sc.data.materials.append(m['stone_light'])
            bpy.ops.object.shade_smooth()

    # Acroterion (gold ornament on roof peak)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(0, 0, BZ + col_h + 1.05))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # Door
    bmesh_box("Door", (0.08, 0.60, 1.40), (1.21, 0, BZ + 0.70), m['door'])

    # Wide ceremonial steps
    for i in range(7):
        bmesh_box(f"Step_{i}", (0.22, 2.5, 0.06), (1.85 + i * 0.24, 0, BZ - 0.04 - i * 0.07), m['stone_light'])

    # Statue on platform
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=1.2,
                                        location=(2.2, -1.5, BZ + 0.6))
    bpy.context.active_object.data.materials.append(m['stone_light'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(2.2, -1.5, BZ + 1.30))
    bpy.context.active_object.data.materials.append(m['stone_light'])


# ============================================================
# MEDIEVAL AGE — Castle keep with 4 corner towers, gatehouse, battlements
# ============================================================
def _build_medieval(m):
    Z = 0.0
    BZ = Z + 0.25  # base of walls (on foundation)

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Heavy stone foundation ===
    bmesh_box("Found1", (5.0, 5.0, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.05)
    bmesh_box("Found2", (4.6, 4.6, 0.13), (0, 0, Z + 0.19), m['stone_dark'], bevel=0.04)

    # === Curtain walls (thick castle walls) ===
    WALL_H = 2.4
    wall_t = 0.22  # wall thickness
    hw = 2.0       # half-width of inner courtyard

    bmesh_box("WallF", (wall_t, hw * 2 - 0.2, WALL_H), (hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallB", (wall_t, hw * 2 - 0.2, WALL_H), (-hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallR", (hw * 2 - 0.2, wall_t, WALL_H), (0, -hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallL", (hw * 2 - 0.2, wall_t, WALL_H), (0, hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)

    # === Wall-walk ledge (walkway along top of walls) ===
    ledge_z = BZ + WALL_H
    bmesh_box("LedgeF", (0.35, hw * 2, 0.08), (hw, 0, ledge_z + 0.04), m['stone_trim'], bevel=0.01)
    bmesh_box("LedgeB", (0.35, hw * 2, 0.08), (-hw, 0, ledge_z + 0.04), m['stone_trim'], bevel=0.01)
    bmesh_box("LedgeR", (hw * 2, 0.35, 0.08), (0, -hw, ledge_z + 0.04), m['stone_trim'], bevel=0.01)
    bmesh_box("LedgeL", (hw * 2, 0.35, 0.08), (0, hw, ledge_z + 0.04), m['stone_trim'], bevel=0.01)

    # === Battlements / crenellations on walls ===
    merlon_h, merlon_w = 0.22, 0.18
    merlon_z = ledge_z + 0.08
    for i in range(9):
        y = -1.6 + i * 0.40
        bmesh_box(f"MerlF_{i}", (0.12, merlon_w, merlon_h), (hw + 0.06, y, merlon_z + merlon_h / 2), m['stone_trim'], bevel=0.01)
        bmesh_box(f"MerlB_{i}", (0.12, merlon_w, merlon_h), (-hw - 0.06, y, merlon_z + merlon_h / 2), m['stone_trim'], bevel=0.01)
    for i in range(9):
        x = -1.6 + i * 0.40
        bmesh_box(f"MerlR_{i}", (merlon_w, 0.12, merlon_h), (x, -hw - 0.06, merlon_z + merlon_h / 2), m['stone_trim'], bevel=0.01)
        bmesh_box(f"MerlL_{i}", (merlon_w, 0.12, merlon_h), (x, hw + 0.06, merlon_z + merlon_h / 2), m['stone_trim'], bevel=0.01)

    # === 4 Corner towers (round, taller than walls) ===
    tower_r = 0.52
    tower_h = 3.6
    for xs, ys, label in [(-1, -1, "BL"), (-1, 1, "FL"), (1, -1, "BR"), (1, 1, "FR")]:
        tx, ty = xs * hw, ys * hw
        bmesh_prism(f"Tower_{label}", tower_r, tower_h, 12, (tx, ty, BZ), m['stone_upper'], bevel=0.02)
        # Tower bands
        for tz in [BZ + 1.2, BZ + 2.4, BZ + tower_h - 0.15]:
            bmesh_prism(f"TBand_{label}_{tz:.1f}", tower_r + 0.03, 0.06, 12, (tx, ty, tz), m['stone_trim'])
        # Tower parapet
        bmesh_prism(f"TParapet_{label}", tower_r + 0.06, 0.12, 12, (tx, ty, BZ + tower_h), m['stone_trim'])
        # Tower merlons
        for i in range(8):
            a = (2 * math.pi * i) / 8
            mx = tx + (tower_r + 0.08) * math.cos(a)
            my = ty + (tower_r + 0.08) * math.sin(a)
            bmesh_box(f"TMerl_{label}_{i}", (0.10, 0.10, 0.16),
                      (mx, my, BZ + tower_h + 0.20), m['stone_trim'], bevel=0.01)
        # Conical tower roof
        bmesh_cone(f"TRoof_{label}", tower_r + 0.10, 1.1, 12, (tx, ty, BZ + tower_h + 0.28), m['roof'])
        # Arrow slits on towers
        for az in [BZ + 1.0, BZ + 2.0, BZ + 3.0]:
            sx = tx + (tower_r + 0.01) * xs * 0.7
            sy = ty + (tower_r + 0.01) * ys * 0.7
            bmesh_box(f"Slit_{label}_{az:.1f}", (0.04, 0.08, 0.30), (sx, sy, az), m['window'])

    # === Central keep (main tower — tallest structure) ===
    keep_w, keep_d = 1.8, 1.6
    keep_h = 4.2
    bmesh_box("Keep", (keep_w, keep_d, keep_h), (0, 0, BZ + keep_h / 2), m['stone'], bevel=0.03)

    # Keep stone bands
    for kz in [BZ + 1.0, BZ + 2.0, BZ + 3.0, BZ + keep_h]:
        bmesh_box(f"KeepBand_{kz:.1f}", (keep_w + 0.06, keep_d + 0.06, 0.08), (0, 0, kz), m['stone_trim'], bevel=0.02)

    # Keep battlements
    keep_top = BZ + keep_h + 0.04
    for i in range(6):
        y = -0.6 + i * 0.24
        bmesh_box(f"KMerlF_{i}", (0.10, 0.14, 0.20), (keep_w / 2 + 0.05, y, keep_top + 0.10), m['stone_trim'], bevel=0.01)
        bmesh_box(f"KMerlB_{i}", (0.10, 0.14, 0.20), (-keep_w / 2 - 0.05, y, keep_top + 0.10), m['stone_trim'], bevel=0.01)
    for i in range(5):
        x = -0.5 + i * 0.25
        bmesh_box(f"KMerlR_{i}", (0.14, 0.10, 0.20), (x, -keep_d / 2 - 0.05, keep_top + 0.10), m['stone_trim'], bevel=0.01)
        bmesh_box(f"KMerlL_{i}", (0.14, 0.10, 0.20), (x, keep_d / 2 + 0.05, keep_top + 0.10), m['stone_trim'], bevel=0.01)

    # Keep pitched roof
    roof_verts = [
        (-keep_w / 2 - 0.10, -keep_d / 2 - 0.10, keep_top + 0.20),
        (keep_w / 2 + 0.10, -keep_d / 2 - 0.10, keep_top + 0.20),
        (keep_w / 2 + 0.10, keep_d / 2 + 0.10, keep_top + 0.20),
        (-keep_w / 2 - 0.10, keep_d / 2 + 0.10, keep_top + 0.20),
        (0, -keep_d / 2 - 0.10, keep_top + 1.4),
        (0, keep_d / 2 + 0.10, keep_top + 1.4),
    ]
    roof_faces = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("KeepRoof", roof_verts, roof_faces, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Keep windows (arched)
    for y in [-0.45, 0.45]:
        for kz in [BZ + 1.5, BZ + 2.8]:
            bmesh_box(f"KWin_{y:.1f}_{kz:.1f}", (0.08, 0.18, 0.45), (keep_w / 2 + 0.01, y, kz), m['window'])
    for x in [-0.5, 0.0, 0.5]:
        for kz in [BZ + 1.5, BZ + 2.8]:
            bmesh_box(f"KWinS_{x:.1f}_{kz:.1f}", (0.18, 0.08, 0.45), (x, -keep_d / 2 - 0.01, kz), m['window'])

    # === Gatehouse (front entrance) ===
    gate_x = hw + wall_t / 2
    bmesh_box("Gatehouse", (0.6, 1.2, WALL_H + 0.8), (gate_x, 0, BZ + (WALL_H + 0.8) / 2), m['stone'], bevel=0.02)
    bmesh_box("GateArch", (0.08, 0.70, 1.40), (gate_x + 0.28, 0, BZ + 0.70), m['door'])
    # Portcullis suggestion (iron grate)
    for gy in [-0.25, -0.12, 0, 0.12, 0.25]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=1.30,
                                            location=(gate_x + 0.30, gy, BZ + 0.65))
        bar = bpy.context.active_object
        bar.name = f"Portcullis_{gy:.2f}"
        bar.data.materials.append(m['iron'])
    # Horizontal bars
    for gz in [BZ + 0.3, BZ + 0.7, BZ + 1.1]:
        bmesh_box(f"PBar_{gz:.1f}", (0.03, 0.60, 0.025), (gate_x + 0.30, 0, gz), m['iron'])
    # Gatehouse battlements
    for i in range(4):
        y = -0.4 + i * 0.27
        bmesh_box(f"GMerl_{i}", (0.10, 0.14, 0.18), (gate_x + 0.08, y, BZ + WALL_H + 0.8 + 0.09), m['stone_trim'], bevel=0.01)

    # === Steps to gate ===
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.22, 1.4, 0.06), (gate_x + 0.50 + i * 0.24, 0, BZ - 0.04 - i * 0.06), m['stone_dark'])

    # === Main banner on keep ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=1.2,
                                        location=(0, 0, keep_top + 1.4 + 0.6))
    bpy.context.active_object.data.materials.append(m['wood'])
    bverts = [(0.04, 0, keep_top + 2.30), (0.65, 0.04, keep_top + 2.25),
              (0.65, 0.02, keep_top + 2.60), (0.04, 0, keep_top + 2.58)]
    mesh_from_pydata("Banner", bverts, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False

    # === Gold finial on keep roof ===
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0, 0, keep_top + 1.42))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # === Small flags on front corner towers ===
    for ys, label in [(-1, "R"), (1, "L")]:
        tx, ty = hw, ys * hw
        fz = BZ + tower_h + 1.38 + 0.4
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.6,
                                            location=(tx, ty, fz))
        bpy.context.active_object.data.materials.append(m['wood'])
        fv = [(tx + 0.03, ty, fz + 0.15), (tx + 0.38, ty + 0.03, fz + 0.12),
              (tx + 0.38, ty + 0.02, fz + 0.35), (tx + 0.03, ty, fz + 0.33)]
        mesh_from_pydata(f"Flag_{label}", fv, [(0, 1, 2, 3)], m['banner'])

    # === Torch holders on gatehouse ===
    for ys in [-0.4, 0.4]:
        bmesh_box(f"Torch_{ys:.1f}", (0.04, 0.04, 0.15), (gate_x + 0.32, ys, BZ + 1.5), m['iron'])


# ============================================================
# GUNPOWDER AGE — Star-fort palace with bastions
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (6.0, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Heavy foundation ===
    bmesh_box("Found", (5.2, 5.0, 0.25), (0, 0, Z + 0.125), m['stone_dark'], bevel=0.06)

    BZ = Z + 0.25
    WALL_H = 2.8
    hw = 2.2

    # === Thick fortress walls ===
    wt = 0.28
    bmesh_box("WallF", (wt, hw * 2 - 0.3, WALL_H), (hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.03)
    bmesh_box("WallB", (wt, hw * 2 - 0.3, WALL_H), (-hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.03)
    bmesh_box("WallR", (hw * 2 - 0.3, wt, WALL_H), (0, -hw, BZ + WALL_H / 2), m['stone'], bevel=0.03)
    bmesh_box("WallL", (hw * 2 - 0.3, wt, WALL_H), (0, hw, BZ + WALL_H / 2), m['stone'], bevel=0.03)

    # Battlements
    merlon_z = BZ + WALL_H + 0.06
    for i in range(10):
        y = -1.8 + i * 0.40
        bmesh_box(f"MF_{i}", (0.12, 0.16, 0.22), (hw + 0.08, y, merlon_z + 0.11), m['stone_trim'], bevel=0.01)
        bmesh_box(f"MB_{i}", (0.12, 0.16, 0.22), (-hw - 0.08, y, merlon_z + 0.11), m['stone_trim'], bevel=0.01)
    for i in range(10):
        x = -1.8 + i * 0.40
        bmesh_box(f"MR_{i}", (0.16, 0.12, 0.22), (x, -hw - 0.08, merlon_z + 0.11), m['stone_trim'], bevel=0.01)
        bmesh_box(f"ML_{i}", (0.16, 0.12, 0.22), (x, hw + 0.08, merlon_z + 0.11), m['stone_trim'], bevel=0.01)

    # === Angular bastions (star fort corners) ===
    bastion_h = WALL_H + 0.4
    for xs, ys, label in [(-1, -1, "BL"), (-1, 1, "FL"), (1, -1, "BR"), (1, 1, "FR")]:
        bx, by = xs * hw, ys * hw
        # Diamond-shaped bastion
        bmesh_prism(f"Bastion_{label}", 0.55, bastion_h, 6, (bx, by, BZ), m['stone_upper'], bevel=0.02)
        bmesh_prism(f"BTop_{label}", 0.60, 0.10, 6, (bx, by, BZ + bastion_h), m['stone_trim'])
        # Merlons on bastion
        for i in range(6):
            a = (2 * math.pi * i) / 6
            bmesh_box(f"BM_{label}_{i}", (0.10, 0.10, 0.18),
                      (bx + 0.58 * math.cos(a), by + 0.58 * math.sin(a),
                       BZ + bastion_h + 0.19), m['stone_trim'], bevel=0.01)
        # Cannon slit
        bmesh_box(f"CSlit_{label}", (0.04, 0.14, 0.08),
                  (bx + xs * 0.56, by + ys * 0.56, BZ + 1.2), m['window'])

    # === Central palace (grand, multi-story) ===
    palace_w, palace_d = 2.4, 2.0
    palace_h = 3.6
    bmesh_box("Palace", (palace_w, palace_d, palace_h), (0, 0, BZ + palace_h / 2), m['stone'], bevel=0.03)
    for pz in [BZ + 1.2, BZ + 2.4, BZ + palace_h]:
        bmesh_box(f"PBand_{pz:.1f}", (palace_w + 0.06, palace_d + 0.06, 0.08), (0, 0, pz), m['stone_trim'], bevel=0.02)

    # Hipped roof on palace
    pyramid_roof("PalaceRoof", w=palace_w - 0.2, d=palace_d - 0.2, h=1.5, overhang=0.20,
                 origin=(0, 0, BZ + palace_h + 0.04), material=m['roof'])

    # Palace windows (3 rows)
    for row, z_off in enumerate([0.5, 1.6, 2.7]):
        for y in [-0.6, 0, 0.6]:
            bmesh_box(f"PWin_{row}_{y:.1f}", (0.08, 0.22, 0.50), (palace_w / 2 + 0.01, y, BZ + z_off + 0.10), m['window'])
            bmesh_box(f"PWinH_{row}_{y:.1f}", (0.09, 0.26, 0.04), (palace_w / 2 + 0.02, y, BZ + z_off + 0.37), m['stone_trim'])

    # === Cannon tower (front-right, tallest) ===
    TX, TY = hw - 0.3, -hw + 0.3
    ct_h = 4.8
    bmesh_prism("CannonTower", 0.60, ct_h, 10, (TX, TY, BZ), m['stone'], bevel=0.02)
    bmesh_prism("CTTop", 0.65, 0.12, 10, (TX, TY, BZ + ct_h), m['stone_trim'])
    for i in range(8):
        a = (2 * math.pi * i) / 8
        bmesh_box(f"CTM_{i}", (0.10, 0.10, 0.18),
                  (TX + 0.68 * math.cos(a), TY + 0.68 * math.sin(a), BZ + ct_h + 0.21), m['stone_trim'], bevel=0.01)
    bmesh_cone("CTRoof", 0.70, 1.3, 10, (TX, TY, BZ + ct_h + 0.30), m['roof'])

    # === Grand gate ===
    gate_x = hw + wt / 2
    bmesh_box("Gatehouse", (0.7, 1.4, WALL_H + 1.0), (gate_x, 0, BZ + (WALL_H + 1.0) / 2), m['stone'], bevel=0.02)
    bmesh_box("GateArch", (0.10, 0.80, 1.60), (gate_x + 0.32, 0, BZ + 0.80), m['door'])
    bmesh_box("GateKeystone", (0.12, 0.90, 0.12), (gate_x + 0.33, 0, BZ + 1.64), m['stone_trim'], bevel=0.02)

    # Steps
    for i in range(6):
        bmesh_box(f"Step_{i}", (0.22, 1.6, 0.07), (gate_x + 0.55 + i * 0.24, 0, BZ - 0.04 - i * 0.06), m['stone_dark'])

    # Banner
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=1.0,
                                        location=(TX, TY, BZ + ct_h + 1.6 + 0.5))
    bpy.context.active_object.data.materials.append(m['wood'])
    fz = BZ + ct_h + 2.40
    fv = [(TX + 0.04, TY, fz), (TX + 0.55, TY + 0.04, fz - 0.05),
          (TX + 0.55, TY + 0.02, fz + 0.30), (TX + 0.04, TY, fz + 0.28)]
    mesh_from_pydata("Banner", fv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# ENLIGHTENMENT AGE — Baroque palace with dome and wings
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (6.5, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.20
    bmesh_box("Found", (6.0, 5.0, 0.20), (0, 0, Z + 0.10), m['stone_dark'], bevel=0.05)

    # === Central block ===
    main_w, main_d = 2.8, 2.4
    main_h = 3.0
    bmesh_box("Main", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone'], bevel=0.03)

    # Moldings
    bmesh_box("BaseMold", (main_w + 0.06, main_d + 0.06, 0.08), (0, 0, BZ + 0.04), m['stone_trim'], bevel=0.02)
    bmesh_box("MidMold", (main_w + 0.06, main_d + 0.06, 0.06), (0, 0, BZ + 1.2), m['stone_trim'], bevel=0.01)
    bmesh_box("Cornice", (main_w + 0.08, main_d + 0.08, 0.10), (0, 0, BZ + main_h), m['stone_trim'], bevel=0.03)

    # Balustrade
    bmesh_box("Balustrade", (main_w + 0.04, main_d + 0.04, 0.25), (0, 0, BZ + main_h + 0.12), m['stone_light'])

    # === Symmetrical wings ===
    wing_w, wing_d, wing_h = 1.6, 1.8, 2.4
    for ys, lbl in [(-2.0, "R"), (2.0, "L")]:
        bmesh_box(f"Wing_{lbl}", (wing_w, wing_d, wing_h), (0.3, ys, BZ + wing_h / 2), m['stone'], bevel=0.02)
        bmesh_box(f"WingCornice_{lbl}", (wing_w + 0.06, wing_d + 0.06, 0.08), (0.3, ys, BZ + wing_h), m['stone_trim'], bevel=0.02)
        # Wing hipped roof
        pyramid_roof(f"WingRoof_{lbl}", w=wing_w - 0.2, d=wing_d - 0.2, h=0.7, overhang=0.12,
                     origin=(0.3, ys, BZ + wing_h + 0.04), material=m['roof'])
        # Wing windows (2 rows, 3 cols)
        for row, z_off in [(0.5, 0), (1.5, 1)]:
            for wy in [-0.5, 0, 0.5]:
                actual_y = ys + wy
                bmesh_box(f"WWin_{lbl}_{row}_{wy:.1f}", (0.07, 0.20, 0.55),
                          (0.3 + wing_w / 2 + 0.01, actual_y, BZ + row + 0.10), m['window'])

    # Main windows (5 cols × 2 rows on front)
    for i, y in enumerate([-0.9, -0.45, 0, 0.45, 0.9]):
        for z_off, h in [(0.5, 0.55), (1.7, 0.65)]:
            bmesh_box(f"MWin_{i}_{z_off}", (0.07, 0.22, h), (main_w / 2 + 0.01, y, BZ + z_off), m['window'])
            bmesh_box(f"MWinH_{i}_{z_off}", (0.08, 0.26, 0.04), (main_w / 2 + 0.02, y, BZ + z_off + h / 2 + 0.02), m['stone_trim'])

    # === Portico with columns ===
    for y in [-0.50, 0.50]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.11, depth=2.2,
                                            location=(main_w / 2 + 0.50, y, BZ + 1.10))
        c = bpy.context.active_object
        c.name = f"PorCol_{y:.1f}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        bmesh_box(f"PorCap_{y:.1f}", (0.26, 0.26, 0.06), (main_w / 2 + 0.50, y, BZ + 2.24), m['stone_trim'])

    # Portico pediment
    pv = [(main_w / 2 + 0.55, -0.65, BZ + 2.26), (main_w / 2 + 0.55, 0.65, BZ + 2.26),
          (main_w / 2 + 0.55, 0, BZ + 2.65)]
    mesh_from_pydata("Pediment", pv, [(0, 1, 2)], m['stone_light'])
    bmesh_box("PorRoof", (0.55, 1.4, 0.06), (main_w / 2 + 0.50, 0, BZ + 2.27), m['stone_trim'])

    # Door
    bmesh_box("Door", (0.08, 0.60, 1.40), (main_w / 2 + 0.01, 0, BZ + 0.70), m['door'])

    # === Central dome ===
    dome_z = BZ + main_h + 0.25
    # Drum (cylindrical base for dome)
    bmesh_prism("Drum", 0.70, 0.8, 16, (0, 0, dome_z), m['stone'], bevel=0.02)
    # Dome
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.75, location=(0, 0, dome_z + 0.80 + 0.20))
    dome = bpy.context.active_object
    dome.name = "Dome"
    dome.scale = (1, 1, 0.55)
    dome.data.materials.append(m['roof'])
    bpy.ops.object.shade_smooth()
    # Lantern on dome
    bmesh_prism("Lantern", 0.15, 0.4, 8, (0, 0, dome_z + 1.20), m['stone_light'])
    bmesh_cone("LanternRoof", 0.20, 0.25, 8, (0, 0, dome_z + 1.60), m['gold'])

    # === Clock tower (side) ===
    TX, TY = -0.8, -2.0
    ct_z = BZ + wing_h + 0.04
    bmesh_box("ClockTower", (0.7, 0.7, 2.0), (TX, TY, ct_z + 1.0), m['stone'], bevel=0.02)
    bmesh_box("CTCornice", (0.8, 0.8, 0.08), (TX, TY, ct_z + 2.0), m['stone_trim'], bevel=0.02)
    # Clock face
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.22, depth=0.04,
                                        location=(TX + 0.36, TY, ct_z + 1.40))
    clock = bpy.context.active_object
    clock.name = "Clock"
    clock.rotation_euler = (0, math.radians(90), 0)
    clock.data.materials.append(m['gold'])
    # Spire
    bmesh_cone("CTSpire", 0.25, 0.8, 8, (TX, TY, ct_z + 2.05), m['roof'])

    # Steps
    for i in range(7):
        bmesh_box(f"Step_{i}", (0.20, 2.0, 0.06), (main_w / 2 + 0.70 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_light'])


# ============================================================
# INDUSTRIAL AGE — Grand Victorian civic hall with clock tower
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (6.5, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.15
    bmesh_box("Found", (6.0, 5.0, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.04)

    # === Main building (wide, imposing) ===
    main_w, main_d = 4.2, 3.2
    main_h = 3.5
    bmesh_box("Main", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone'], bevel=0.02)

    # Iron beam grid on facade
    for z in [BZ + 0.9, BZ + 1.8, BZ + 2.7]:
        bmesh_box(f"IronH_{z:.1f}", (0.03, 3.3, 0.06), (main_w / 2 + 0.01, 0, z), m['iron'])
    for y in [-1.3, -0.6, 0, 0.6, 1.3]:
        bmesh_box(f"IronV_{y:.1f}", (0.03, 0.06, main_h), (main_w / 2 + 0.01, y, BZ + main_h / 2), m['iron'])

    # Windows (3 rows × 5 cols on front)
    for row, z_off in enumerate([0.4, 1.3, 2.2]):
        for y in [-1.1, -0.55, 0, 0.55, 1.1]:
            h = 0.50 if row < 2 else 0.40
            bmesh_box(f"Win_{row}_{y:.1f}", (0.08, 0.24, h), (main_w / 2 + 0.01, y, BZ + z_off + 0.10), m['window'])
            bmesh_box(f"WinH_{row}_{y:.1f}", (0.09, 0.28, 0.04), (main_w / 2 + 0.02, y, BZ + z_off + h / 2 + 0.12), m['stone_trim'])

    # Flat roof with parapet
    bmesh_box("Roof", (main_w + 0.1, main_d + 0.1, 0.12), (0, 0, BZ + main_h + 0.06), m['stone_dark'])
    bmesh_box("Parapet", (main_w + 0.2, main_d + 0.2, 0.20), (0, 0, BZ + main_h + 0.22), m['stone_trim'], bevel=0.02)

    # === Grand entrance portico ===
    bmesh_box("Portico", (0.8, 2.0, 2.0), (main_w / 2 + 0.40, 0, BZ + 1.0), m['stone'], bevel=0.02)
    bmesh_box("PorTop", (0.9, 2.1, 0.10), (main_w / 2 + 0.40, 0, BZ + 2.04), m['stone_trim'], bevel=0.02)
    # Portico columns
    for y in [-0.6, 0.6]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.10, depth=1.9,
                                            location=(main_w / 2 + 0.80, y, BZ + 0.95))
        c = bpy.context.active_object
        c.name = f"PorCol_{y:.1f}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()

    # Door
    bmesh_box("Door", (0.10, 0.90, 1.80), (main_w / 2 + 0.01, 0, BZ + 0.90), m['door'])
    bmesh_box("DoorSurround", (0.12, 1.1, 0.12), (main_w / 2 + 0.02, 0, BZ + 1.84), m['stone_trim'], bevel=0.02)

    # === Clock tower (prominent, like Big Ben style) ===
    TX, TY = main_w / 2 - 0.8, -main_d / 2 + 0.5
    tower_base_z = BZ + main_h + 0.12
    tower_w = 1.0
    tower_h = 3.5
    bmesh_box("Tower", (tower_w, tower_w, tower_h), (TX, TY, tower_base_z + tower_h / 2), m['stone'], bevel=0.03)
    bmesh_box("TCornice", (tower_w + 0.1, tower_w + 0.1, 0.10), (TX, TY, tower_base_z + tower_h), m['stone_trim'], bevel=0.02)

    # Clock faces (front + side)
    for dx, dy, rot in [(tower_w / 2 + 0.01, 0, (0, math.radians(90), 0)),
                        (0, -tower_w / 2 - 0.01, (math.radians(90), 0, 0))]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.30, depth=0.04,
                                            location=(TX + dx, TY + dy, tower_base_z + 2.2))
        cl = bpy.context.active_object
        cl.name = f"Clock_{dx:.1f}_{dy:.1f}"
        cl.rotation_euler = rot
        cl.data.materials.append(m['gold'])

    # Tower pointed roof
    pyramid_roof("TowerRoof", w=tower_w - 0.1, d=tower_w - 0.1, h=1.5, overhang=0.10,
                 origin=(TX, TY, tower_base_z + tower_h + 0.05), material=m['roof'])

    # Gold spire on tower
    bmesh_cone("Spire", 0.06, 0.5, 8, (TX, TY, tower_base_z + tower_h + 1.55), m['gold'])

    # === Two chimneys ===
    for y_off in [-1.2, 1.2]:
        bmesh_box(f"Chimney_{y_off:.1f}", (0.30, 0.30, 2.0), (-main_w / 2 + 0.5, y_off, BZ + main_h + 1.0), m['stone'], bevel=0.02)
        bmesh_box(f"ChimTop_{y_off:.1f}", (0.36, 0.36, 0.10), (-main_w / 2 + 0.5, y_off, BZ + main_h + 2.05), m['stone_trim'])

    # === Iron fence ===
    for i in range(14):
        fy = -1.8 + i * 0.27
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.6,
                                            location=(main_w / 2 + 1.2, fy, BZ + 0.15))
        bpy.context.active_object.data.materials.append(m['iron'])

    # Steps
    for i in range(6):
        bmesh_box(f"Step_{i}", (0.22, 2.2, 0.06), (main_w / 2 + 0.95 + i * 0.22, 0, BZ - 0.04 - i * 0.05), m['stone_dark'])


# ============================================================
# MODERN AGE — Government complex with glass tower
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (7.0, 6.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.10
    bmesh_box("Found", (6.5, 5.5, 0.10), (0, 0, Z + 0.05), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Main tower (tallest) ===
    tower_w, tower_d = 2.0, 1.8
    tower_h = 5.5
    bmesh_box("Tower", (tower_w, tower_d, tower_h), (-0.5, 0, BZ + tower_h / 2), m['stone'], bevel=0.02)

    # Glass curtain wall on tower front
    bmesh_box("TGlass", (0.06, tower_d - 0.3, tower_h - 0.4), (-0.5 + tower_w / 2 + 0.01, 0, BZ + tower_h / 2 + 0.1), glass)
    # Horizontal bands
    for z in [BZ + 1.2, BZ + 2.4, BZ + 3.6, BZ + 4.8]:
        bmesh_box(f"TBand_{z:.1f}", (0.08, tower_d - 0.2, 0.10), (-0.5 + tower_w / 2 + 0.02, 0, z), m['stone_trim'])
    # Vertical mullions
    for y in [-0.5, 0, 0.5]:
        bmesh_box(f"TMull_{y:.1f}", (0.05, 0.03, tower_h - 0.5), (-0.5 + tower_w / 2 + 0.03, y, BZ + tower_h / 2 + 0.1), metal)

    # Tower flat roof
    bmesh_box("TRoof", (tower_w + 0.1, tower_d + 0.1, 0.12), (-0.5, 0, BZ + tower_h + 0.06), m['stone_dark'])

    # === Lower wing (wide, connected) ===
    wing_w, wing_d, wing_h = 4.0, 2.5, 2.8
    bmesh_box("Wing", (wing_w, wing_d, wing_h), (1.0, 0, BZ + wing_h / 2), m['stone'], bevel=0.02)

    # Wing glass wall
    bmesh_box("WGlass", (0.06, wing_d - 0.4, wing_h - 0.4), (1.0 + wing_w / 2 + 0.01, 0, BZ + wing_h / 2 + 0.1), glass)
    for z in [BZ + 1.0, BZ + 2.0]:
        bmesh_box(f"WBand_{z:.1f}", (0.08, wing_d - 0.3, 0.08), (1.0 + wing_w / 2 + 0.02, 0, z), m['stone_trim'])
    for y in [-0.8, -0.2, 0.4, 1.0]:
        bmesh_box(f"WMull_{y:.1f}", (0.05, 0.03, wing_h - 0.5), (1.0 + wing_w / 2 + 0.03, y, BZ + wing_h / 2), metal)

    # Wing flat roof
    bmesh_box("WRoof", (wing_w + 0.1, wing_d + 0.1, 0.10), (1.0, 0, BZ + wing_h + 0.05), m['stone_dark'])

    # Side windows on wing
    for x in [-0.5, 0.5, 1.5, 2.5]:
        bmesh_box(f"SWin_{x:.1f}", (0.25, 0.06, 0.80), (x + 1.0, -wing_d / 2 - 0.01, BZ + 1.6), glass)

    # === Entrance canopy ===
    bmesh_box("Canopy", (1.2, 2.5, 0.06), (1.0 + wing_w / 2 + 0.60, 0, BZ + 1.8), metal)
    for y in [-0.9, 0.9]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=1.7,
                                            location=(1.0 + wing_w / 2 + 0.60, y, BZ + 0.95))
        bpy.context.active_object.data.materials.append(metal)

    # Glass entrance
    bmesh_box("GlassDoor", (0.06, 1.4, 2.0), (1.0 + wing_w / 2 + 0.01, 0, BZ + 1.0), glass)
    bmesh_box("DoorFrame", (0.07, 1.5, 0.04), (1.0 + wing_w / 2 + 0.02, 0, BZ + 2.02), metal)

    # === Antenna on tower roof ===
    roof_z = BZ + tower_h + 0.12
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=2.5,
                                        location=(-0.5, 0, roof_z + 1.25))
    bpy.context.active_object.data.materials.append(metal)
    for z_off in [0.5, 1.0, 1.5, 2.0]:
        bmesh_box(f"AntBar_{z_off:.1f}", (0.02, 0.6, 0.02), (-0.5, 0, roof_z + z_off), metal)

    # HVAC units on wing roof
    wing_roof_z = BZ + wing_h + 0.10
    bmesh_box("HVAC1", (0.8, 0.6, 0.4), (1.5, 0.6, wing_roof_z + 0.20), m['stone_dark'])
    bmesh_box("HVAC2", (0.6, 0.5, 0.3), (0.5, -0.5, wing_roof_z + 0.15), m['stone_dark'])

    # Flag
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=1.5,
                                        location=(2.0, 1.0, wing_roof_z + 0.75))
    bpy.context.active_object.data.materials.append(metal)
    bv = [(2.03, 1.0, wing_roof_z + 1.20), (2.55, 1.03, wing_roof_z + 1.15),
          (2.55, 1.02, wing_roof_z + 1.45), (2.03, 1.0, wing_roof_z + 1.48)]
    mesh_from_pydata("Banner", bv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False

    # Plaza fountain
    bmesh_prism("Fountain", 0.40, 0.15, 12, (3.5, 0, Z + 0.075), m['stone_light'])


# ============================================================
# DIGITAL AGE — High-tech campus with glass tower and spire
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (7.0, 6.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.08
    bmesh_box("Found", (6.5, 5.5, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Main glass tower (tallest) ===
    tower_h = 6.5
    bmesh_box("Tower", (2.4, 2.0, tower_h), (0, 0, BZ + tower_h / 2), glass)

    # Steel frame grid on tower
    for z in [BZ + 1.2, BZ + 2.4, BZ + 3.6, BZ + 4.8, BZ + 6.0]:
        bmesh_box(f"HFrame_{z:.1f}", (2.42, 2.02, 0.05), (0, 0, z), metal)
    for x in [-1.0, 0, 1.0]:
        bmesh_box(f"VFrameF_{x:.1f}", (0.04, 0.04, tower_h), (x, -1.01, BZ + tower_h / 2), metal)
        bmesh_box(f"VFrameB_{x:.1f}", (0.04, 0.04, tower_h), (x, 1.01, BZ + tower_h / 2), metal)
    for y in [-0.8, 0, 0.8]:
        bmesh_box(f"VFrameR_{y:.1f}", (0.04, 0.04, tower_h), (1.21, y, BZ + tower_h / 2), metal)
        bmesh_box(f"VFrameL_{y:.1f}", (0.04, 0.04, tower_h), (-1.21, y, BZ + tower_h / 2), metal)

    # === Lower wing (connected) ===
    wing_h = 3.0
    bmesh_box("Wing", (4.0, 1.8, wing_h), (1.0, 0, BZ + wing_h / 2), glass)
    for z in [BZ + 1.0, BZ + 2.0]:
        bmesh_box(f"WingH_{z:.1f}", (4.02, 1.82, 0.04), (1.0, 0, z), metal)

    # === Entrance atrium ===
    bmesh_box("Atrium", (1.0, 2.0, 2.5), (3.30, 0, BZ + 1.25), glass)
    bmesh_box("AtrFrame", (1.02, 2.02, 0.04), (3.30, 0, BZ + 2.52), metal)

    # Tower flat roof
    roof_z = BZ + tower_h
    bmesh_box("TRoof", (2.5, 2.1, 0.08), (0, 0, roof_z + 0.04), metal)

    # === Communication spire ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05, depth=3.0,
                                        location=(0, 0, roof_z + 1.50))
    bpy.context.active_object.data.materials.append(metal)
    for z_off in [0.5, 1.0, 1.5, 2.0, 2.5]:
        bmesh_box(f"SpireX_{z_off:.1f}", (0.7, 0.02, 0.02), (0, 0, roof_z + z_off), metal)
        bmesh_box(f"SpireY_{z_off:.1f}", (0.02, 0.7, 0.02), (0, 0, roof_z + z_off), metal)

    # === Satellite dish ===
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, location=(0.6, 0.5, roof_z + 0.35))
    dish = bpy.context.active_object
    dish.name = "Dish"
    dish.scale = (1, 1, 0.3)
    dish.data.materials.append(metal)
    bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.5,
                                        location=(0.6, 0.5, roof_z + 0.60))
    bpy.context.active_object.data.materials.append(metal)

    # LED accent strips
    bmesh_box("LED1", (2.42, 0.06, 0.08), (0, -1.02, roof_z - 0.2), m['gold'])
    bmesh_box("LED2", (0.06, 2.02, 0.08), (1.22, 0, roof_z - 0.2), m['gold'])
    bmesh_box("LED3", (4.02, 0.06, 0.06), (1.0, -0.91, BZ + wing_h - 0.15), m['gold'])

    # Solar panels on wing roof
    wing_roof_z = BZ + wing_h
    for i in range(4):
        bmesh_box(f"Solar_{i}", (0.8, 0.5, 0.04), (0.2 + i * 0.9, 0, wing_roof_z + 0.08), m['window'])
        bmesh_box(f"SolarF_{i}", (0.82, 0.52, 0.02), (0.2 + i * 0.9, 0, wing_roof_z + 0.05), metal)

    # Landscaping hedges
    for y in [-1.8, 1.8]:
        bmesh_box(f"Hedge_{y:.1f}", (0.6, 0.3, 0.25), (3.8, y, Z + 0.125), m['ground'])

    # Holographic display suggestion (glowing box)
    bmesh_box("HoloDisplay", (0.3, 0.5, 0.6), (3.32, 0, BZ + 0.30), m['gold'])


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


def build_town_center(materials, age='medieval'):
    """Build a Town Center with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
