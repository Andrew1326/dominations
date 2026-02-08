"""
Tower (defense) building -- the tallest defensive structure per age.
1x1 tile footprint (2.0x2.0 ground) for Stone through Medieval,
2x2 tile footprint (3.5x3.5 ground) from Gunpowder onward.

Stone:         Wooden watchtower -- 4 tall log posts, raised platform, thatch roof, ladder
Bronze:        Square mud-brick tower with crenellations, arrow slits, small flag
Iron:          Round stone tower with bands, conical roof, archer platform, arrow slits
Classical:     Greek/Roman guard tower with columns at top, tiled roof, torch brackets
Medieval:      Tall round stone tower with machicolations, conical roof, arrow slits at 3 levels, banner
Gunpowder:     Square bastion tower with cannon embrasures, thicker walls, flag (2x2 ground)
Enlightenment: Brick watchtower with clock face, balcony, ornate spire (2x2 ground)
Industrial:    Steel-framed observation tower with searchlight platform, iron railings (2x2 ground)
Modern:        Concrete guard tower with bulletproof glass observation room, spotlight, antenna (2x2 ground)
Digital:       Automated defense turret -- sleek metal/glass pod on pedestal, sensor array, LED ring (2x2 ground)
"""

import bpy
import bmesh
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# ============================================================
# STONE AGE -- Wooden watchtower with 4 tall log posts,
# raised platform, thatch roof, ladder
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (2.0, 2.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Four tall corner log posts
    post_h = 3.0
    post_inset = 0.45
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            px, py = sx * post_inset, sy * post_inset
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.07, depth=post_h,
                                                location=(px, py, Z + post_h / 2))
            post = bpy.context.active_object
            post.name = f"Post_{sx}_{sy}"
            post.data.materials.append(m['wood_dark'])

    # Diagonal braces at bottom (X-pattern between posts)
    brace_z_lo = Z + 0.3
    brace_z_hi = Z + 1.0
    for sy in [-1, 1]:
        bv = [(-post_inset, sy * post_inset, brace_z_lo),
              (-post_inset + 0.04, sy * post_inset, brace_z_lo),
              (post_inset + 0.04, sy * post_inset, brace_z_hi),
              (post_inset, sy * post_inset, brace_z_hi)]
        mesh_from_pydata(f"BraceA_{sy}", bv, [(0, 1, 2, 3)], m['wood'])
    for sx in [-1, 1]:
        bv = [(sx * post_inset, -post_inset, brace_z_lo),
              (sx * post_inset, -post_inset + 0.04, brace_z_lo),
              (sx * post_inset, post_inset + 0.04, brace_z_hi),
              (sx * post_inset, post_inset, brace_z_hi)]
        mesh_from_pydata(f"BraceB_{sx}", bv, [(0, 1, 2, 3)], m['wood'])

    # Raised platform
    plat_z = Z + 2.0
    bmesh_box("Platform", (1.2, 1.2, 0.08), (0, 0, plat_z), m['wood'])

    # Platform railing (4 sides)
    rail_h = 0.35
    for sx in [-1, 1]:
        bmesh_box(f"RailX_{sx}", (0.04, 1.2, rail_h), (sx * 0.58, 0, plat_z + 0.04 + rail_h / 2), m['wood'])
    for sy in [-1, 1]:
        bmesh_box(f"RailY_{sy}", (1.2, 0.04, rail_h), (0, sy * 0.58, plat_z + 0.04 + rail_h / 2), m['wood'])

    # Railing vertical pickets
    for sx in [-1, 1]:
        for i in range(5):
            fy = -0.50 + i * 0.25
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=rail_h,
                                                location=(sx * 0.58, fy, plat_z + 0.04 + rail_h / 2))
            bpy.context.active_object.data.materials.append(m['wood_dark'])

    # Thatch roof (conical)
    bmesh_cone("Roof", 0.90, 0.9, 12, (0, 0, plat_z + 0.04 + rail_h), m['roof'])

    # Roof finial
    bmesh_prism("RoofKnob", 0.06, 0.10, 6, (0, 0, plat_z + 0.04 + rail_h + 0.9), m['wood_dark'])

    # Ladder (leaning against front)
    ladder_base_x = 0.65
    ladder_top_x = 0.20
    ladder_z_lo = Z + 0.0
    ladder_z_hi = plat_z + 0.04
    # Two ladder rails
    for dy in [-0.08, 0.08]:
        lv = [(ladder_base_x, dy, ladder_z_lo),
              (ladder_base_x + 0.03, dy, ladder_z_lo),
              (ladder_top_x + 0.03, dy, ladder_z_hi),
              (ladder_top_x, dy, ladder_z_hi)]
        mesh_from_pydata(f"LadderRail_{dy:.2f}", lv, [(0, 1, 2, 3)], m['wood_dark'])

    # Ladder rungs
    n_rungs = 8
    for i in range(n_rungs):
        t = (i + 0.5) / n_rungs
        rx = ladder_base_x + (ladder_top_x - ladder_base_x) * t
        rz = ladder_z_lo + (ladder_z_hi - ladder_z_lo) * t
        bmesh_box(f"Rung_{i}", (0.03, 0.20, 0.02), (rx, 0, rz), m['wood'])

    # Small fire basket on platform
    bmesh_prism("FireBasket", 0.08, 0.10, 6, (0.3, 0.3, plat_z + 0.04), m['iron'])


# ============================================================
# BRONZE AGE -- Square mud-brick tower with crenellations,
# arrow slits, small flag
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (2.0, 2.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Foundation
    bmesh_box("Found", (1.5, 1.5, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.12
    wall_h = 3.2

    # Main tower body (square)
    bmesh_box("TowerBody", (1.3, 1.3, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Slight taper band at mid-height
    bmesh_box("Band", (1.34, 1.34, 0.06), (0, 0, BZ + wall_h * 0.5), m['stone_trim'])

    # Top cornice
    bmesh_box("Cornice", (1.38, 1.38, 0.06), (0, 0, BZ + wall_h), m['stone_trim'])

    # Crenellations (merlons around top)
    top_z = BZ + wall_h + 0.06
    merlon_w = 0.18
    merlon_h = 0.25
    merlon_d = 0.10
    # Front and back merlons
    for side_x in [-1, 1]:
        for i in range(4):
            my = -0.50 + i * 0.34
            bmesh_box(f"MerlonX_{side_x}_{i}",
                      (merlon_d, merlon_w, merlon_h),
                      (side_x * 0.65, my, top_z + merlon_h / 2), m['stone_trim'])
    # Left and right merlons
    for side_y in [-1, 1]:
        for i in range(4):
            mx = -0.50 + i * 0.34
            bmesh_box(f"MerlonY_{side_y}_{i}",
                      (merlon_w, merlon_d, merlon_h),
                      (mx, side_y * 0.65, top_z + merlon_h / 2), m['stone_trim'])

    # Arrow slits (narrow vertical openings) on two faces
    for z_off in [BZ + 1.2, BZ + 2.4]:
        bmesh_box(f"SlitF_{z_off:.1f}", (0.06, 0.06, 0.30), (0.66, 0, z_off), m['window'])
    for z_off in [BZ + 1.2, BZ + 2.4]:
        bmesh_box(f"SlitS_{z_off:.1f}", (0.06, 0.06, 0.30), (0, -0.66, z_off), m['window'])

    # Door at base
    bmesh_box("Door", (0.06, 0.30, 0.65), (0.66, 0, BZ + 0.32), m['door'])
    bmesh_box("DoorFrame", (0.07, 0.36, 0.06), (0.67, 0, BZ + 0.67), m['wood'])

    # Small flag on top
    flag_z = top_z + merlon_h
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.6,
                                        location=(0, 0, flag_z + 0.3))
    pole = bpy.context.active_object
    pole.name = "FlagPole"
    pole.data.materials.append(m['wood_dark'])

    # Flag banner
    fv = [(0, 0.02, flag_z + 0.55), (0, 0.02, flag_z + 0.38),
          (0, 0.22, flag_z + 0.40), (0, 0.22, flag_z + 0.52)]
    mesh_from_pydata("Flag", fv, [(0, 1, 2, 3)], m['banner'])

    # Steps at base
    for i in range(2):
        bmesh_box(f"Step_{i}", (0.14, 0.5, 0.04),
                  (0.78 + i * 0.14, 0, BZ - 0.02 - i * 0.04), m['stone_dark'])


# ============================================================
# IRON AGE -- Round stone tower with bands, conical roof,
# archer platform, arrow slits
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (2.0, 2.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Circular foundation
    bmesh_prism("Found", 0.80, 0.12, 16, (0, 0, Z), m['stone_dark'])

    BZ = Z + 0.12
    tower_h = 3.5
    tower_r = 0.65

    # Main cylindrical tower body
    bmesh_prism("TowerBody", tower_r, tower_h, 16, (0, 0, BZ), m['stone'])

    # Stone bands at intervals
    for z_off in [0.8, 1.6, 2.4, 3.2]:
        bmesh_prism(f"Band_{z_off:.1f}", tower_r + 0.04, 0.06, 16,
                    (0, 0, BZ + z_off), m['stone_trim'])

    # Top platform (slightly wider)
    plat_z = BZ + tower_h
    bmesh_prism("TopPlat", tower_r + 0.10, 0.10, 16, (0, 0, plat_z), m['stone_trim'])

    # Archer platform railing (crenellated ring)
    rail_z = plat_z + 0.10
    n_merlons = 10
    for i in range(n_merlons):
        a = (2 * math.pi * i) / n_merlons
        mx = (tower_r + 0.10) * math.cos(a)
        my = (tower_r + 0.10) * math.sin(a)
        if i % 2 == 0:
            bmesh_box(f"Merlon_{i}", (0.12, 0.12, 0.22),
                      (mx, my, rail_z + 0.11), m['stone_trim'])

    # Conical roof
    roof_z = rail_z + 0.22
    bmesh_cone("Roof", tower_r + 0.15, 1.2, 16, (0, 0, roof_z), m['roof'])

    # Roof finial
    bmesh_prism("RoofFinial", 0.06, 0.12, 6, (0, 0, roof_z + 1.2), m['gold'])

    # Arrow slits at 3 heights, alternating around circumference
    for level, z_off in enumerate([0.6, 1.4, 2.2]):
        n_slits = 4
        angle_offset = level * (math.pi / n_slits)
        for i in range(n_slits):
            a = angle_offset + (2 * math.pi * i) / n_slits
            sx = (tower_r + 0.01) * math.cos(a)
            sy = (tower_r + 0.01) * math.sin(a)
            bmesh_box(f"Slit_{level}_{i}", (0.05, 0.05, 0.25),
                      (sx, sy, BZ + z_off), m['window'])

    # Door
    bmesh_box("Door", (0.06, 0.30, 0.65), (tower_r + 0.01, 0, BZ + 0.32), m['door'])
    bmesh_box("DoorArch", (0.07, 0.36, 0.06), (tower_r + 0.02, 0, BZ + 0.67), m['stone_trim'])

    # Steps
    for i in range(2):
        bmesh_prism(f"Step_{i}", 0.85 + i * 0.10, 0.04, 16,
                    (0, 0, Z + 0.12 - (i + 1) * 0.04), m['stone_dark'])


# ============================================================
# CLASSICAL AGE -- Greek/Roman guard tower with columns at
# top, tiled roof, torch brackets
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (2.0, 2.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stepped platform (3 tiers)
    for i in range(3):
        w = 1.6 - i * 0.10
        bmesh_box(f"Plat_{i}", (w, w, 0.05), (0, 0, Z + 0.025 + i * 0.05),
                  m['stone_light'], bevel=0.01)

    BZ = Z + 0.15
    tower_h = 3.0

    # Square tower body
    body_w = 1.2
    bmesh_box("TowerBody", (body_w, body_w, tower_h), (0, 0, BZ + tower_h / 2),
              m['stone_light'], bevel=0.02)

    # Horizontal cornice at 2/3 height
    bmesh_box("MidCornice", (body_w + 0.06, body_w + 0.06, 0.05),
              (0, 0, BZ + tower_h * 0.66), m['stone_trim'])

    # Top cornice (wider, for column platform)
    col_plat_z = BZ + tower_h
    bmesh_box("TopCornice", (body_w + 0.16, body_w + 0.16, 0.08),
              (0, 0, col_plat_z + 0.04), m['stone_trim'], bevel=0.02)

    # Columns at top (4 corners)
    col_h = 1.0
    col_base_z = col_plat_z + 0.08
    col_inset = body_w / 2 + 0.02
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            cx, cy = sx * col_inset, sy * col_inset
            bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.055, depth=col_h,
                                                location=(cx, cy, col_base_z + col_h / 2))
            c = bpy.context.active_object
            c.name = f"Col_{sx}_{sy}"
            c.data.materials.append(m['stone_light'])
            bpy.ops.object.shade_smooth()
            # Column capital
            bmesh_box(f"Cap_{sx}_{sy}", (0.14, 0.14, 0.04),
                      (cx, cy, col_base_z + col_h + 0.02), m['stone_trim'])
            # Column base
            bmesh_box(f"CBase_{sx}_{sy}", (0.13, 0.13, 0.03),
                      (cx, cy, col_base_z + 0.015), m['stone_trim'])

    # Entablature (beam on top of columns)
    ent_z = col_base_z + col_h + 0.04
    bmesh_box("Entablature", (body_w + 0.22, body_w + 0.22, 0.06),
              (0, 0, ent_z + 0.03), m['stone_trim'])

    # Tiled pyramid roof
    roof_z = ent_z + 0.06
    pyramid_roof("Roof", w=body_w + 0.10, d=body_w + 0.10, h=0.7,
                 overhang=0.12, origin=(0, 0, roof_z), material=m['roof'])

    # Roof acroterion (gold ornament)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0, 0, roof_z + 0.73))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # Arrow slits on tower body
    for z_off in [BZ + 0.8, BZ + 1.6, BZ + 2.4]:
        bmesh_box(f"SlitF_{z_off:.1f}", (0.06, 0.05, 0.28),
                  (body_w / 2 + 0.01, 0, z_off), m['window'])
    for z_off in [BZ + 1.2, BZ + 2.0]:
        bmesh_box(f"SlitS_{z_off:.1f}", (0.05, 0.06, 0.28),
                  (0, -body_w / 2 - 0.01, z_off), m['window'])

    # Door
    bmesh_box("Door", (0.06, 0.32, 0.75), (body_w / 2 + 0.01, 0, BZ + 0.37), m['door'])

    # Torch brackets (one on each side of door)
    for dy in [-0.30, 0.30]:
        # Bracket arm
        bmesh_box(f"Torch_{dy:.2f}", (0.15, 0.04, 0.04),
                  (body_w / 2 + 0.08, dy, BZ + 0.85), m['iron'])
        # Torch cup
        bmesh_prism(f"TorchCup_{dy:.2f}", 0.04, 0.08, 6,
                    (body_w / 2 + 0.15, dy, BZ + 0.87), m['iron'])

    # Steps
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.14, 0.6, 0.04),
                  (body_w / 2 + 0.14 + i * 0.14, 0, BZ - 0.02 - i * 0.04), m['stone_light'])


# ============================================================
# MEDIEVAL AGE -- Tall round stone tower with machicolations,
# conical roof, arrow slits at 3 levels, banner
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (2.0, 2.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Circular stone foundation
    bmesh_prism("Found", 0.85, 0.15, 16, (0, 0, Z), m['stone_dark'], bevel=0.02)

    BZ = Z + 0.15
    tower_r = 0.60
    tower_h = 4.0

    # Main cylindrical tower body
    bmesh_prism("TowerBody", tower_r, tower_h, 16, (0, 0, BZ), m['stone'])

    # Stone bands
    for z_off in [0.7, 1.4, 2.1, 2.8, 3.5]:
        bmesh_prism(f"Band_{z_off:.1f}", tower_r + 0.03, 0.05, 16,
                    (0, 0, BZ + z_off), m['stone_trim'])

    # Machicolations (corbeled-out parapet supports at top)
    mach_z = BZ + tower_h
    n_mach = 12
    mach_r = tower_r + 0.15
    for i in range(n_mach):
        a = (2 * math.pi * i) / n_mach
        mx = mach_r * math.cos(a)
        my = mach_r * math.sin(a)
        # Corbel bracket
        bmesh_box(f"Corbel_{i}", (0.10, 0.10, 0.12),
                  (mx, my, mach_z + 0.06), m['stone_dark'])

    # Parapet wall (above machicolations)
    bmesh_prism("Parapet", mach_r + 0.02, 0.30, 16, (0, 0, mach_z + 0.12), m['stone'])

    # Crenellations on parapet
    cren_z = mach_z + 0.42
    n_cren = 8
    for i in range(n_cren):
        a = (2 * math.pi * i) / n_cren
        cx = (mach_r + 0.02) * math.cos(a)
        cy = (mach_r + 0.02) * math.sin(a)
        bmesh_box(f"Cren_{i}", (0.12, 0.12, 0.18),
                  (cx, cy, cren_z + 0.09), m['stone_trim'])

    # Conical roof
    roof_z = cren_z + 0.18
    bmesh_cone("Roof", tower_r + 0.20, 1.4, 16, (0, 0, roof_z), m['roof'])

    # Roof finial
    bmesh_prism("RoofFinial", 0.05, 0.14, 6, (0, 0, roof_z + 1.4), m['gold'])

    # Arrow slits at 3 levels, offset around circumference
    for level, z_off in enumerate([0.5, 1.5, 2.5]):
        n_slits = 4
        angle_off = level * (math.pi / 4)
        for i in range(n_slits):
            a = angle_off + (2 * math.pi * i) / n_slits
            sx = (tower_r + 0.01) * math.cos(a)
            sy = (tower_r + 0.01) * math.sin(a)
            bmesh_box(f"Slit_{level}_{i}", (0.05, 0.05, 0.28),
                      (sx, sy, BZ + z_off), m['window'])

    # Door
    bmesh_box("Door", (0.06, 0.30, 0.70), (tower_r + 0.01, 0, BZ + 0.35), m['door'])
    bmesh_box("DoorArch", (0.07, 0.36, 0.06), (tower_r + 0.02, 0, BZ + 0.72), m['stone_trim'])

    # Banner pole and banner
    banner_z = roof_z + 1.4
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.8,
                                        location=(0, 0, banner_z + 0.4))
    pole = bpy.context.active_object
    pole.name = "BannerPole"
    pole.data.materials.append(m['wood_dark'])

    bv = [(0, 0.02, banner_z + 0.75), (0, 0.02, banner_z + 0.45),
          (0, 0.30, banner_z + 0.48), (0, 0.30, banner_z + 0.72)]
    mesh_from_pydata("Banner", bv, [(0, 1, 2, 3)], m['banner'])

    # Steps
    for i in range(2):
        bmesh_prism(f"Step_{i}", 0.75 + i * 0.10, 0.04, 16,
                    (0, 0, Z + 0.15 - (i + 1) * 0.04), m['stone_dark'])


# ============================================================
# GUNPOWDER AGE -- Square bastion tower with cannon embrasures,
# thicker walls, flag (2x2 ground)
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Heavy stone foundation
    bmesh_box("Found", (2.6, 2.6, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.18
    tower_h = 4.5
    body_w = 2.2

    # Main tower body (square, thick walls)
    bmesh_box("TowerBody", (body_w, body_w, tower_h), (0, 0, BZ + tower_h / 2),
              m['stone'], bevel=0.03)

    # Battered base (sloped lower section for extra thickness)
    batter_h = 1.2
    bv = [
        # bottom ring (wider)
        (-body_w / 2 - 0.15, -body_w / 2 - 0.15, BZ),
        (body_w / 2 + 0.15, -body_w / 2 - 0.15, BZ),
        (body_w / 2 + 0.15, body_w / 2 + 0.15, BZ),
        (-body_w / 2 - 0.15, body_w / 2 + 0.15, BZ),
        # top ring (meets main body)
        (-body_w / 2, -body_w / 2, BZ + batter_h),
        (body_w / 2, -body_w / 2, BZ + batter_h),
        (body_w / 2, body_w / 2, BZ + batter_h),
        (-body_w / 2, body_w / 2, BZ + batter_h),
    ]
    bf = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    mesh_from_pydata("Batter", bv, bf, m['stone_dark'])

    # Stone bands
    for z_off in [1.5, 2.5, 3.5]:
        bmesh_box(f"Band_{z_off:.1f}", (body_w + 0.06, body_w + 0.06, 0.06),
                  (0, 0, BZ + z_off), m['stone_trim'])

    # Top cornice
    top_z = BZ + tower_h
    bmesh_box("Cornice", (body_w + 0.12, body_w + 0.12, 0.08),
              (0, 0, top_z + 0.04), m['stone_trim'], bevel=0.02)

    # Crenellated parapet
    parapet_z = top_z + 0.08
    for side in range(4):
        angle = side * math.pi / 2
        n_merlons = 5
        for i in range(n_merlons):
            t = -0.80 + i * 0.40
            if side == 0:
                mx, my = body_w / 2 + 0.06, t
                sw, sd = 0.10, 0.18
            elif side == 1:
                mx, my = t, body_w / 2 + 0.06
                sw, sd = 0.18, 0.10
            elif side == 2:
                mx, my = -body_w / 2 - 0.06, t
                sw, sd = 0.10, 0.18
            else:
                mx, my = t, -body_w / 2 - 0.06
                sw, sd = 0.18, 0.10
            bmesh_box(f"Merlon_{side}_{i}", (sw, sd, 0.30),
                      (mx, my, parapet_z + 0.15), m['stone_trim'])

    # Cannon embrasures (wider openings in walls at mid-height)
    emb_z = BZ + 2.2
    hw = body_w / 2 + 0.01
    # Front and back
    for sx in [-1, 1]:
        for dy in [-0.40, 0.40]:
            bmesh_box(f"EmbrX_{sx}_{dy:.1f}", (0.08, 0.30, 0.22),
                      (sx * hw, dy, emb_z), m['stone_dark'])
    # Left and right
    for sy in [-1, 1]:
        for dx in [-0.40, 0.40]:
            bmesh_box(f"EmbrY_{sy}_{dx:.1f}", (0.30, 0.08, 0.22),
                      (dx, sy * hw, emb_z), m['stone_dark'])

    # Arrow slits (narrow) at lower level
    slit_z = BZ + 1.0
    for face, coord in [(0, (hw, 0)), (1, (0, -hw))]:
        bmesh_box(f"Slit_{face}", (0.05, 0.05, 0.30),
                  (coord[0], coord[1], slit_z), m['window'])

    # Door (heavy, reinforced)
    bmesh_box("Door", (0.08, 0.50, 1.0), (hw, 0, BZ + 0.50), m['door'])
    bmesh_box("DoorArch", (0.10, 0.58, 0.08), (hw + 0.01, 0, BZ + 1.02), m['stone_trim'])

    # Flag pole and flag
    flag_z = parapet_z + 0.30
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=1.0,
                                        location=(0, 0, flag_z + 0.5))
    pole = bpy.context.active_object
    pole.name = "FlagPole"
    pole.data.materials.append(m['wood_dark'])

    fv = [(0, 0.025, flag_z + 0.95), (0, 0.025, flag_z + 0.65),
          (0, 0.35, flag_z + 0.68), (0, 0.35, flag_z + 0.92)]
    mesh_from_pydata("Flag", fv, [(0, 1, 2, 3)], m['banner'])

    # Steps to door
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.16, 0.8, 0.05),
                  (hw + 0.14 + i * 0.16, 0, BZ - 0.03 - i * 0.05), m['stone_dark'])


# ============================================================
# ENLIGHTENMENT AGE -- Brick watchtower with clock face,
# balcony, ornate spire (2x2 ground)
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Foundation
    bmesh_box("Found", (2.4, 2.4, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.15
    body_w = 1.8
    tower_h = 5.0

    # Main tower body (square brick)
    bmesh_box("TowerBody", (body_w, body_w, tower_h), (0, 0, BZ + tower_h / 2),
              m['stone'], bevel=0.02)

    # Quoins (decorative corner stones)
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            for z_off in [0.2, 0.7, 1.2, 1.7, 2.2, 2.7, 3.2, 3.7, 4.2, 4.7]:
                bmesh_box(f"Quoin_{sx}_{sy}_{z_off:.1f}", (0.06, 0.06, 0.18),
                          (sx * (body_w / 2 + 0.01), sy * (body_w / 2 + 0.01), BZ + z_off),
                          m['stone_light'])

    # String courses (horizontal bands)
    for z_off in [1.5, 3.0, tower_h]:
        bmesh_box(f"String_{z_off:.1f}", (body_w + 0.08, body_w + 0.08, 0.05),
                  (0, 0, BZ + z_off), m['stone_trim'], bevel=0.01)

    # Clock face (on front, near top)
    clock_z = BZ + 4.0
    hw = body_w / 2 + 0.01
    # Clock surround (circular approximation -- octagonal prism)
    bmesh_prism("ClockSurround", 0.30, 0.06, 16, (hw, 0, clock_z - 0.03), m['stone_trim'])
    # Rotate clock to face front
    bpy.context.view_layer.objects.active = bpy.data.objects["ClockSurround"]
    bpy.data.objects["ClockSurround"].rotation_euler = (0, math.radians(90), 0)
    # Clock face
    bmesh_box("ClockFace", (0.06, 0.44, 0.44), (hw + 0.02, 0, clock_z), m['stone_light'])
    # Clock hands (simplified as thin boxes)
    bmesh_box("ClockHandH", (0.04, 0.14, 0.02), (hw + 0.04, 0, clock_z + 0.04), m['iron'])
    bmesh_box("ClockHandM", (0.04, 0.02, 0.18), (hw + 0.04, 0, clock_z + 0.06), m['iron'])

    # Second clock face on side
    bmesh_box("ClockFaceS", (0.44, 0.06, 0.44), (0, -body_w / 2 - 0.02, clock_z), m['stone_light'])

    # Windows at various heights
    for z_off in [BZ + 0.8, BZ + 2.0, BZ + 3.2]:
        bmesh_box(f"WinF_{z_off:.1f}", (0.06, 0.18, 0.35),
                  (hw, 0, z_off), m['window'])
        bmesh_box(f"WinFH_{z_off:.1f}", (0.07, 0.22, 0.04),
                  (hw + 0.01, 0, z_off + 0.19), m['stone_trim'])
    # Side windows
    for z_off in [BZ + 1.2, BZ + 2.8]:
        bmesh_box(f"WinS_{z_off:.1f}", (0.18, 0.06, 0.35),
                  (0, -body_w / 2 - 0.01, z_off), m['window'])

    # Balcony (projecting platform below clock)
    bal_z = BZ + 3.5
    bmesh_box("BalconyFloor", (0.50, body_w * 0.6, 0.06),
              (hw + 0.25, 0, bal_z), m['stone_trim'])
    # Balcony brackets (corbels)
    for dy in [-0.25, 0.25]:
        bv = [(hw, dy - 0.04, bal_z - 0.30), (hw, dy + 0.04, bal_z - 0.30),
              (hw, dy + 0.04, bal_z - 0.03), (hw + 0.50, dy - 0.04, bal_z - 0.03),
              (hw + 0.50, dy + 0.04, bal_z - 0.03)]
        bf = [(0, 1, 2), (2, 4, 3), (0, 2, 3), (1, 2, 4)]
        mesh_from_pydata(f"BalBracket_{dy:.2f}", bv, bf, m['stone_dark'])
    # Balcony railing
    bmesh_box("BalRailF", (0.04, body_w * 0.6, 0.25),
              (hw + 0.48, 0, bal_z + 0.03 + 0.125), m['iron'])
    for i in range(5):
        fy = -body_w * 0.28 + i * (body_w * 0.56 / 4)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=0.25,
                                            location=(hw + 0.25, fy, bal_z + 0.03 + 0.125))
        bpy.context.active_object.data.materials.append(m['iron'])

    # Ornate spire on top
    top_z = BZ + tower_h
    # Transition base (octagonal)
    bmesh_prism("SpireBase", body_w / 2 * 0.9, 0.20, 8, (0, 0, top_z + 0.05), m['stone_trim'])
    # Spire cone
    bmesh_cone("Spire", body_w / 2 * 0.7, 1.8, 8, (0, 0, top_z + 0.25), m['roof'])
    # Spire finial (gold sphere and cross)
    finial_z = top_z + 0.25 + 1.8
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0, 0, finial_z + 0.06))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()
    # Cross
    bmesh_box("CrossV", (0.03, 0.03, 0.20), (0, 0, finial_z + 0.22), m['gold'])
    bmesh_box("CrossH", (0.03, 0.14, 0.03), (0, 0, finial_z + 0.26), m['gold'])

    # Door
    bmesh_box("Door", (0.08, 0.42, 1.0), (hw, 0, BZ + 0.50), m['door'])
    bmesh_box("DoorSurround", (0.10, 0.52, 1.10), (hw + 0.01, 0, BZ + 0.55), m['stone_light'])

    # Steps
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.16, 0.8, 0.04),
                  (hw + 0.16 + i * 0.16, 0, BZ - 0.02 - i * 0.04), m['stone_light'])


# ============================================================
# INDUSTRIAL AGE -- Steel-framed observation tower with
# searchlight platform, iron railings (2x2 ground)
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Concrete pad
    bmesh_box("Pad", (2.4, 2.4, 0.10), (0, 0, Z + 0.05), m['stone_dark'], bevel=0.02)

    BZ = Z + 0.10
    tower_h = 5.5

    # Four main steel legs (tapered inward toward top)
    leg_base_spread = 0.90
    leg_top_spread = 0.40
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            bx, by = sx * leg_base_spread, sy * leg_base_spread
            tx, ty = sx * leg_top_spread, sy * leg_top_spread
            # Leg as a quad strip
            lv = [(bx - 0.04, by - 0.04, BZ), (bx + 0.04, by + 0.04, BZ),
                  (tx + 0.04, ty + 0.04, BZ + tower_h), (tx - 0.04, ty - 0.04, BZ + tower_h)]
            mesh_from_pydata(f"Leg_{sx}_{sy}_A", lv, [(0, 1, 2, 3)], m['iron'])
            lv2 = [(bx - 0.04, by + 0.04, BZ), (bx + 0.04, by - 0.04, BZ),
                   (tx + 0.04, ty - 0.04, BZ + tower_h), (tx - 0.04, ty + 0.04, BZ + tower_h)]
            mesh_from_pydata(f"Leg_{sx}_{sy}_B", lv2, [(0, 1, 2, 3)], m['iron'])

    # Horizontal cross-braces at intervals
    for level, z_off in enumerate([1.0, 2.2, 3.4, 4.6]):
        t = z_off / tower_h
        spread = leg_base_spread + (leg_top_spread - leg_base_spread) * t
        # X-direction braces
        for sy in [-1, 1]:
            y_pos = sy * spread
            bmesh_box(f"BraceX_{level}_{sy}", (spread * 2, 0.03, 0.03),
                      (0, y_pos, BZ + z_off), m['iron'])
        # Y-direction braces
        for sx in [-1, 1]:
            x_pos = sx * spread
            bmesh_box(f"BraceY_{level}_{sx}", (0.03, spread * 2, 0.03),
                      (x_pos, 0, BZ + z_off), m['iron'])

    # Diagonal cross-braces between levels
    for level in range(3):
        z_lo = BZ + 1.0 + level * 1.2
        z_hi = z_lo + 1.2
        t_lo = (z_lo - BZ) / tower_h
        t_hi = (z_hi - BZ) / tower_h
        spread_lo = leg_base_spread + (leg_top_spread - leg_base_spread) * t_lo
        spread_hi = leg_base_spread + (leg_top_spread - leg_base_spread) * t_hi
        # X-braces on front/back faces
        for sy in [-1, 1]:
            dv = [(-spread_lo, sy * spread_lo, z_lo),
                  (-spread_lo + 0.03, sy * spread_lo, z_lo),
                  (spread_hi + 0.03, sy * spread_hi, z_hi),
                  (spread_hi, sy * spread_hi, z_hi)]
            mesh_from_pydata(f"DiagX_{level}_{sy}", dv, [(0, 1, 2, 3)], m['iron'])

    # Observation platform at top
    plat_z = BZ + tower_h
    bmesh_box("Platform", (1.4, 1.4, 0.08), (0, 0, plat_z + 0.04), m['iron'])

    # Platform floor (wood)
    bmesh_box("PlatFloor", (1.30, 1.30, 0.04), (0, 0, plat_z + 0.10), m['wood'])

    # Iron railings around platform
    rail_h = 0.40
    for sx in [-1, 1]:
        bmesh_box(f"RailX_{sx}", (0.03, 1.4, rail_h),
                  (sx * 0.70, 0, plat_z + 0.12 + rail_h / 2), m['iron'])
    for sy in [-1, 1]:
        bmesh_box(f"RailY_{sy}", (1.4, 0.03, rail_h),
                  (0, sy * 0.70, plat_z + 0.12 + rail_h / 2), m['iron'])

    # Railing pickets
    for sx in [-1, 1]:
        for i in range(7):
            fy = -0.60 + i * 0.20
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=rail_h,
                                                location=(sx * 0.70, fy, plat_z + 0.12 + rail_h / 2))
            bpy.context.active_object.data.materials.append(m['iron'])

    # Searchlight on platform
    sl_z = plat_z + 0.12 + rail_h
    # Searchlight base
    bmesh_prism("SLBase", 0.12, 0.10, 8, (0, 0, sl_z), m['iron'])
    # Searchlight housing
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.15, depth=0.25,
                                        location=(0, 0, sl_z + 0.10 + 0.125))
    sl = bpy.context.active_object
    sl.name = "Searchlight"
    sl.rotation_euler = (math.radians(80), 0, math.radians(30))
    sl.data.materials.append(m['stone_light'])
    bpy.ops.object.shade_smooth()
    # Searchlight lens
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0.08, 0.05, sl_z + 0.28))
    lens = bpy.context.active_object
    lens.name = "SLLens"
    lens.scale = (0.6, 1, 1)
    lens.data.materials.append(m['window'])
    bpy.ops.object.shade_smooth()

    # Small roof/canopy over platform
    bmesh_box("Canopy", (1.5, 1.5, 0.04), (0, 0, sl_z + 0.50), m['stone_dark'])
    # Canopy supports (4 thin posts)
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.50,
                                                location=(sx * 0.60, sy * 0.60,
                                                          sl_z + 0.25))
            bpy.context.active_object.data.materials.append(m['iron'])

    # Ladder running up one leg
    ladder_leg_sx, ladder_leg_sy = 1, -1
    for i in range(18):
        t = (i + 0.5) / 18
        z_r = BZ + t * tower_h
        spread = leg_base_spread + (leg_top_spread - leg_base_spread) * t
        rx = ladder_leg_sx * spread
        ry = ladder_leg_sy * spread
        bmesh_box(f"LRung_{i}", (0.03, 0.18, 0.02), (rx + 0.10, ry, z_r), m['iron'])


# ============================================================
# MODERN AGE -- Concrete guard tower with bulletproof glass
# observation room, spotlight, antenna (2x2 ground)
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # Concrete foundation pad
    bmesh_box("Pad", (2.6, 2.6, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.12
    tower_h = 5.0
    body_w = 1.4

    # Main concrete shaft (square)
    bmesh_box("Shaft", (body_w, body_w, tower_h), (0, 0, BZ + tower_h / 2),
              m['stone'], bevel=0.02)

    # Concrete bands/reveals
    for z_off in [1.0, 2.0, 3.0, 4.0]:
        bmesh_box(f"Reveal_{z_off:.1f}", (body_w + 0.04, body_w + 0.04, 0.04),
                  (0, 0, BZ + z_off), m['stone_dark'])

    # Glass observation room at top (wider than shaft)
    obs_w = 2.0
    obs_h = 1.2
    obs_z = BZ + tower_h
    # Observation floor slab
    bmesh_box("ObsFloor", (obs_w + 0.10, obs_w + 0.10, 0.10),
              (0, 0, obs_z + 0.05), m['stone_dark'])
    # Glass walls (4 sides)
    hw = obs_w / 2
    bmesh_box("ObsGlassF", (0.06, obs_w, obs_h), (hw, 0, obs_z + 0.10 + obs_h / 2), glass)
    bmesh_box("ObsGlassB", (0.06, obs_w, obs_h), (-hw, 0, obs_z + 0.10 + obs_h / 2), glass)
    bmesh_box("ObsGlassL", (obs_w, 0.06, obs_h), (0, -hw, obs_z + 0.10 + obs_h / 2), glass)
    bmesh_box("ObsGlassR", (obs_w, 0.06, obs_h), (0, hw, obs_z + 0.10 + obs_h / 2), glass)
    # Glass mullions (metal frames)
    for dy in [-0.45, 0, 0.45]:
        bmesh_box(f"MullF_{dy:.2f}", (0.04, 0.03, obs_h),
                  (hw + 0.01, dy, obs_z + 0.10 + obs_h / 2), metal)
        bmesh_box(f"MullB_{dy:.2f}", (0.04, 0.03, obs_h),
                  (-hw - 0.01, dy, obs_z + 0.10 + obs_h / 2), metal)
    for dx in [-0.45, 0, 0.45]:
        bmesh_box(f"MullL_{dx:.2f}", (0.03, 0.04, obs_h),
                  (dx, -hw - 0.01, obs_z + 0.10 + obs_h / 2), metal)
        bmesh_box(f"MullR_{dx:.2f}", (0.03, 0.04, obs_h),
                  (dx, hw + 0.01, obs_z + 0.10 + obs_h / 2), metal)
    # Horizontal mullion band
    for face_hw_sign in [-1, 1]:
        bmesh_box(f"HMullX_{face_hw_sign}", (0.04, obs_w, 0.03),
                  (face_hw_sign * hw, 0, obs_z + 0.10 + obs_h / 2), metal)
    for face_hw_sign in [-1, 1]:
        bmesh_box(f"HMullY_{face_hw_sign}", (obs_w, 0.04, 0.03),
                  (0, face_hw_sign * hw, obs_z + 0.10 + obs_h / 2), metal)

    # Observation roof slab
    obs_top_z = obs_z + 0.10 + obs_h
    bmesh_box("ObsRoof", (obs_w + 0.16, obs_w + 0.16, 0.10),
              (0, 0, obs_top_z + 0.05), m['stone_dark'])

    # Spotlight on roof
    sl_z = obs_top_z + 0.10
    bmesh_prism("SLMount", 0.10, 0.08, 8, (0.50, 0, sl_z), metal)
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.12, depth=0.20,
                                        location=(0.50, 0, sl_z + 0.08 + 0.10))
    sl = bpy.context.active_object
    sl.name = "Spotlight"
    sl.rotation_euler = (math.radians(70), 0, 0)
    sl.data.materials.append(metal)
    bpy.ops.object.shade_smooth()

    # Antenna mast
    ant_z = obs_top_z + 0.10
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=1.2,
                                        location=(-0.30, 0.30, ant_z + 0.6))
    bpy.context.active_object.name = "Antenna"
    bpy.context.active_object.data.materials.append(metal)
    # Antenna cross-arms
    bmesh_box("AntArm1", (0.03, 0.30, 0.02), (-0.30, 0.30, ant_z + 0.9), metal)
    bmesh_box("AntArm2", (0.03, 0.20, 0.02), (-0.30, 0.30, ant_z + 1.1), metal)

    # Small windows in concrete shaft
    for z_off in [BZ + 1.5, BZ + 3.0]:
        bmesh_box(f"ShaftWinF_{z_off:.1f}", (0.06, 0.20, 0.12),
                  (body_w / 2 + 0.01, 0, z_off), glass)
    for z_off in [BZ + 2.2]:
        bmesh_box(f"ShaftWinS_{z_off:.1f}", (0.20, 0.06, 0.12),
                  (0, -body_w / 2 - 0.01, z_off), glass)

    # Door at base
    bmesh_box("Door", (0.08, 0.50, 1.10), (body_w / 2 + 0.01, 0, BZ + 0.55), metal)
    bmesh_box("DoorFrame", (0.10, 0.56, 1.14), (body_w / 2 + 0.02, 0, BZ + 0.57), m['stone_dark'])

    # Perimeter chain-link fence posts (simplified)
    fence_r = 1.4
    for i in range(8):
        a = (2 * math.pi * i) / 8
        fx, fy = fence_r * math.cos(a), fence_r * math.sin(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.8,
                                            location=(fx, fy, BZ + 0.4))
        bpy.context.active_object.data.materials.append(metal)
    # Fence rails
    for z_off in [0.2, 0.6]:
        for i in range(8):
            a1 = (2 * math.pi * i) / 8
            a2 = (2 * math.pi * ((i + 1) % 8)) / 8
            x1, y1 = fence_r * math.cos(a1), fence_r * math.sin(a1)
            x2, y2 = fence_r * math.cos(a2), fence_r * math.sin(a2)
            fv = [(x1, y1, BZ + z_off), (x2, y2, BZ + z_off),
                  (x2, y2, BZ + z_off + 0.02), (x1, y1, BZ + z_off + 0.02)]
            mesh_from_pydata(f"FRail_{z_off:.1f}_{i}", fv, [(0, 1, 2, 3)], metal)


# ============================================================
# DIGITAL AGE -- Automated defense turret: sleek metal/glass
# pod on pedestal, sensor array, LED ring (2x2 ground)
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # Clean geometric base pad
    bmesh_prism("BasePad", 1.4, 0.06, 8, (0, 0, Z + 0.06), m['stone_dark'])

    BZ = Z + 0.12

    # LED accent ring at base
    bmesh_prism("LEDRingBase", 1.42, 0.04, 16, (0, 0, Z + 0.06), m['gold'])

    # Pedestal (tapered hexagonal column)
    ped_h = 4.0
    ped_r_bot = 0.55
    ped_r_top = 0.35
    n_seg = 6
    # Build pedestal as from_pydata with tapered sides
    bot_verts = []
    top_verts = []
    pv = []
    pf = []
    for i in range(n_seg):
        a = (2 * math.pi * i) / n_seg
        bx = ped_r_bot * math.cos(a)
        by = ped_r_bot * math.sin(a)
        tx = ped_r_top * math.cos(a)
        ty = ped_r_top * math.sin(a)
        pv.append((bx, by, BZ))
        pv.append((tx, ty, BZ + ped_h))
    # Bottom face
    pf.append(tuple(range(0, n_seg * 2, 2)))
    # Top face
    pf.append(tuple(reversed(range(1, n_seg * 2, 2))))
    # Side faces
    for i in range(n_seg):
        j = (i + 1) % n_seg
        b0 = i * 2
        t0 = i * 2 + 1
        b1 = j * 2
        t1 = j * 2 + 1
        pf.append((b0, b1, t1, t0))
    ped = mesh_from_pydata("Pedestal", pv, pf, metal)

    # Pedestal accent rings
    for z_off in [0.8, 1.6, 2.4, 3.2]:
        t = z_off / ped_h
        r = ped_r_bot + (ped_r_top - ped_r_bot) * t
        bmesh_prism(f"PedRing_{z_off:.1f}", r + 0.04, 0.04, n_seg, (0, 0, BZ + z_off), m['gold'])

    # Transition platform at top of pedestal
    pod_base_z = BZ + ped_h
    bmesh_prism("TransPlat", 0.60, 0.08, 8, (0, 0, pod_base_z), metal)

    # LED ring at pod base
    bmesh_prism("LEDRingPod", 0.62, 0.04, 16, (0, 0, pod_base_z + 0.08), m['gold'])

    # Turret pod (dome-like glass/metal structure)
    pod_z = pod_base_z + 0.12
    pod_r = 0.55
    pod_h = 0.80

    # Pod lower shell (cylinder)
    bmesh_prism("PodShell", pod_r, pod_h * 0.5, 16, (0, 0, pod_z), metal)

    # Pod upper dome (half sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=pod_r, location=(0, 0, pod_z + pod_h * 0.5))
    dome = bpy.context.active_object
    dome.name = "PodDome"
    dome.scale = (1.0, 1.0, 0.65)
    dome.data.materials.append(glass)
    bpy.ops.object.shade_smooth()

    # Pod metal frame ribs (meridian lines)
    for i in range(6):
        a = (2 * math.pi * i) / 6
        for j in range(6):
            t = 0.1 + j * 0.14
            rx = pod_r * math.cos(t * math.pi) * math.cos(a) * 1.01
            ry = pod_r * math.cos(t * math.pi) * math.sin(a) * 1.01
            rz = pod_r * 0.65 * math.sin(t * math.pi) + pod_z + pod_h * 0.5
            if rz > pod_z + 0.15:
                bmesh_box(f"Rib_{i}_{j}", (0.02, 0.02, 0.02), (rx, ry, rz), metal)

    # Sensor array on top of dome
    sensor_z = pod_z + pod_h * 0.5 + pod_r * 0.65
    # Sensor stalk
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=0.30,
                                        location=(0, 0, sensor_z + 0.15))
    bpy.context.active_object.name = "SensorStalk"
    bpy.context.active_object.data.materials.append(metal)

    # Sensor dish (small rotating radar)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.18, depth=0.04,
                                        location=(0, 0, sensor_z + 0.32))
    dish = bpy.context.active_object
    dish.name = "SensorDish"
    dish.data.materials.append(metal)
    bpy.ops.object.shade_smooth()

    # Sensor antenna array (3 small rods)
    for i in range(3):
        a = (2 * math.pi * i) / 3
        ax = 0.10 * math.cos(a)
        ay = 0.10 * math.sin(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.01, depth=0.20,
                                            location=(ax, ay, sensor_z + 0.44))
        bpy.context.active_object.data.materials.append(metal)

    # Weapon barrels (2 small tubes protruding from pod front)
    for dy in [-0.12, 0.12]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.35,
                                            location=(pod_r + 0.10, dy, pod_z + pod_h * 0.25))
        barrel = bpy.context.active_object
        barrel.name = f"Barrel_{dy:.2f}"
        barrel.rotation_euler = (0, math.radians(90), 0)
        barrel.data.materials.append(metal)

    # Status light indicators on pod shell
    for i in range(8):
        a = (2 * math.pi * i) / 8
        lx = (pod_r + 0.01) * math.cos(a)
        ly = (pod_r + 0.01) * math.sin(a)
        bmesh_box(f"StatusLight_{i}", (0.03, 0.03, 0.03),
                  (lx, ly, pod_z + 0.10), m['gold'])

    # Ground-level perimeter sensor posts
    for i in range(4):
        a = math.pi / 4 + (2 * math.pi * i) / 4
        px = 1.20 * math.cos(a)
        py = 1.20 * math.sin(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.40,
                                            location=(px, py, Z + 0.06 + 0.20))
        bpy.context.active_object.data.materials.append(metal)
        # Sensor tip light
        bmesh_box(f"SensorTip_{i}", (0.04, 0.04, 0.03),
                  (px, py, Z + 0.06 + 0.42), m['gold'])


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


def build_tower(materials, age='medieval'):
    """Build a Tower (defense) with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
