"""
Barracks building — military training and deployment structure per age.
3x3 tile footprint (same scale as Town Center).

Stone:         Warrior's longhouse with wooden palisade fence, weapon rack, training ground
Bronze:        Mud-brick garrison with courtyard, archery targets, watchtower
Iron:          Stone barracks hall with armory wing, training yard, straw dummies
Classical:     Roman castra — rectangular fort with colonnade, training field, eagle standard
Medieval:      Stone keep barracks with crenellated walls, training yard, armory tower, banner
Gunpowder:     Fortified military compound with thick walls, cannon storage, powder magazine
Enlightenment: Regimental barracks with parade ground, symmetrical wings, clock tower
Industrial:    Military depot with iron/brick construction, rail connection, munitions storage
Modern:        Military base with concrete bunkers, radar dish, vehicle bay, chain-link fence
Digital:       Cyber warfare center — high-tech facility with antenna arrays, holographic displays
"""

import bpy
import bmesh
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# ============================================================
# STONE AGE — Warrior's longhouse with palisade, weapon rack
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Palisade fence (partial ring around training area) ===
    pal_r = 2.3
    n_logs = 22
    for i in range(n_logs):
        a = (2 * math.pi * i) / n_logs
        # Leave a gap at the front (roughly i=0 area)
        if 0.3 < a < 5.9:
            px, py = pal_r * math.cos(a), pal_r * math.sin(a)
            h = 1.2 + 0.12 * math.sin(i * 4.1)
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.07, depth=h,
                                                location=(px, py, Z + h / 2))
            log = bpy.context.active_object
            log.name = f"Palisade_{i}"
            log.data.materials.append(m['wood'])

    # Gate posts at palisade opening
    bmesh_box("GatePostL", (0.10, 0.10, 1.5), (pal_r - 0.1, -0.35, Z + 0.75), m['wood_dark'])
    bmesh_box("GatePostR", (0.10, 0.10, 1.5), (pal_r - 0.1, 0.35, Z + 0.75), m['wood_dark'])
    bmesh_box("GateLintel", (0.10, 0.80, 0.08), (pal_r - 0.1, 0, Z + 1.54), m['wood_dark'])

    # === Warrior's longhouse (main structure) ===
    # Raised earth platform
    bmesh_box("LHPlatform", (2.8, 1.6, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.04)

    # Longhouse walls (rectangular)
    lh_w, lh_d, lh_h = 2.6, 1.4, 1.6
    bmesh_box("LHWall", (lh_w, lh_d, lh_h), (0, 0, Z + 0.15 + lh_h / 2), m['stone'])

    # Pitched thatch roof
    BZ = Z + 0.15
    rv = [
        (-lh_w / 2 - 0.15, -lh_d / 2 - 0.15, BZ + lh_h),
        (lh_w / 2 + 0.15, -lh_d / 2 - 0.15, BZ + lh_h),
        (lh_w / 2 + 0.15, lh_d / 2 + 0.15, BZ + lh_h),
        (-lh_w / 2 - 0.15, lh_d / 2 + 0.15, BZ + lh_h),
        (0, -lh_d / 2 - 0.15, BZ + lh_h + 1.0),
        (0, lh_d / 2 + 0.15, BZ + lh_h + 1.0),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("LHRoof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Ridge beam
    bmesh_box("Ridge", (0.06, lh_d + 0.34, 0.06), (0, 0, BZ + lh_h + 1.0), m['wood_dark'])

    # Smoke hole
    bmesh_prism("SmokeHole", 0.15, 0.12, 6, (0, 0, BZ + lh_h + 0.96), m['wood'])

    # Door
    bmesh_box("Door", (0.10, 0.50, 1.0), (lh_w / 2 + 0.01, 0, BZ + 0.50), m['door'])

    # Support poles inside (visible at entrance)
    for i in range(4):
        x = -0.9 + i * 0.6
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=lh_h + 0.3,
                                            location=(x, 0, BZ + (lh_h + 0.3) / 2))
        pole = bpy.context.active_object
        pole.name = f"LHPole_{i}"
        pole.data.materials.append(m['wood'])

    # Animal skin over doorway
    sv = [(lh_w / 2 + 0.02, -0.30, BZ + 1.25), (lh_w / 2 + 0.02, 0.30, BZ + 1.25),
          (lh_w / 2 + 0.04, 0.25, BZ + 0.60), (lh_w / 2 + 0.04, -0.25, BZ + 0.65)]
    mesh_from_pydata("DoorSkin", sv, [(0, 1, 2, 3)], m['roof_edge'])
    m['roof_edge'].use_backface_culling = False

    # === Weapon rack (spears) ===
    WRX, WRY = -1.5, -1.3
    # A-frame rack
    bmesh_box("RackPostL", (0.06, 0.06, 1.0), (WRX, WRY - 0.25, Z + 0.50), m['wood_dark'])
    bmesh_box("RackPostR", (0.06, 0.06, 1.0), (WRX, WRY + 0.25, Z + 0.50), m['wood_dark'])
    bmesh_box("RackBar", (0.04, 0.60, 0.04), (WRX, WRY, Z + 0.98), m['wood'])
    # Spears leaning against rack
    for j in range(4):
        sy = WRY - 0.18 + j * 0.12
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=1.6,
                                            location=(WRX + 0.05, sy, Z + 0.80))
        spear = bpy.context.active_object
        spear.name = f"Spear_{j}"
        spear.rotation_euler = (0, math.radians(12), 0)
        spear.data.materials.append(m['wood'])

    # === Training ground (flattened area with target post) ===
    bmesh_prism("TrainGround", 0.80, 0.04, 8, (1.2, -1.0, Z), m['stone_dark'])

    # Target post (wooden pole with animal hide target)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=1.5,
                                        location=(1.2, -1.0, Z + 0.75))
    bpy.context.active_object.name = "TargetPost"
    bpy.context.active_object.data.materials.append(m['wood'])
    # Target circle
    bmesh_prism("TargetCircle", 0.20, 0.04, 10, (1.23, -1.0, Z + 1.30), m['banner'])

    # === Fire pit (gathering spot) ===
    bmesh_prism("FirePit", 0.35, 0.08, 8, (0.8, 1.2, Z + 0.04), m['stone_dark'])
    for angle in [0.2, -0.4, 0.7]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=0.4,
                                            location=(0.8, 1.2, Z + 0.12))
        log = bpy.context.active_object
        log.name = f"FireLog_{angle:.1f}"
        log.rotation_euler = (0.3, angle, 0)
        log.data.materials.append(m['wood_dark'])

    # Skull totem near entrance
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06, depth=1.8,
                                        location=(1.8, 1.2, Z + 0.90))
    bpy.context.active_object.data.materials.append(m['wood'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(1.8, 1.2, Z + 1.90))
    bpy.context.active_object.name = "SkullTotem"
    bpy.context.active_object.data.materials.append(m['stone_light'])


# ============================================================
# BRONZE AGE — Mud-brick garrison with courtyard
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Stepped platform (2 tiers) ===
    bmesh_box("Plat_0", (4.8, 4.4, 0.20), (0, 0, Z + 0.10), m['stone_dark'], bevel=0.04)
    bmesh_box("Plat_1", (4.2, 3.8, 0.15), (0, 0, Z + 0.275), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.35

    # === Perimeter walls ===
    WALL_H = 1.8
    hw = 1.8
    bmesh_box("WallF", (0.18, hw * 2, WALL_H), (hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallB", (0.18, hw * 2, WALL_H), (-hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallR", (hw * 2, 0.18, WALL_H), (0, -hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallL", (hw * 2, 0.18, WALL_H), (0, hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)

    # Wall-top crenellations
    for i in range(8):
        y = -1.4 + i * 0.40
        bmesh_box(f"MF_{i}", (0.10, 0.14, 0.18), (hw + 0.05, y, BZ + WALL_H + 0.09), m['stone_trim'])
        bmesh_box(f"MB_{i}", (0.10, 0.14, 0.18), (-hw - 0.05, y, BZ + WALL_H + 0.09), m['stone_trim'])
    for i in range(8):
        x = -1.4 + i * 0.40
        bmesh_box(f"MR_{i}", (0.14, 0.10, 0.18), (x, -hw - 0.05, BZ + WALL_H + 0.09), m['stone_trim'])
        bmesh_box(f"ML_{i}", (0.14, 0.10, 0.18), (x, hw + 0.05, BZ + WALL_H + 0.09), m['stone_trim'])

    # === Main garrison building (inside courtyard) ===
    gar_w, gar_d, gar_h = 1.8, 1.4, 2.2
    bmesh_box("Garrison", (gar_w, gar_d, gar_h), (-0.3, 0, BZ + gar_h / 2), m['stone'], bevel=0.02)
    bmesh_box("GarTop", (gar_w + 0.08, gar_d + 0.08, 0.06), (-0.3, 0, BZ + gar_h + 0.03), m['stone_trim'])

    # Flat roof
    bmesh_box("GarRoof", (gar_w + 0.04, gar_d + 0.04, 0.08), (-0.3, 0, BZ + gar_h + 0.10), m['stone_dark'])

    # Garrison windows
    for y in [-0.40, 0.40]:
        bmesh_box(f"GWin_{y:.1f}", (0.06, 0.12, 0.30), (-0.3 + gar_w / 2 + 0.01, y, BZ + 1.5), m['window'])

    # Garrison door
    bmesh_box("GarDoor", (0.08, 0.45, 0.90), (-0.3 + gar_w / 2 + 0.01, 0, BZ + 0.45), m['door'])
    bmesh_box("GarDoorFrame", (0.09, 0.52, 0.06), (-0.3 + gar_w / 2 + 0.02, 0, BZ + 0.92), m['wood'])

    # === Watchtower (corner) ===
    TX, TY = -hw + 0.3, -hw + 0.3
    tower_h = 3.0
    bmesh_box("Tower", (0.50, 0.50, tower_h), (TX, TY, BZ + tower_h / 2), m['stone_upper'], bevel=0.02)
    bmesh_box("TowerTop", (0.58, 0.58, 0.08), (TX, TY, BZ + tower_h + 0.04), m['stone_trim'])
    # Tower merlons
    for dx, dy in [(-0.26, 0), (0.26, 0), (0, -0.26), (0, 0.26)]:
        bmesh_box(f"TM_{dx:.1f}_{dy:.1f}", (0.10, 0.10, 0.16),
                  (TX + dx, TY + dy, BZ + tower_h + 0.16), m['stone_trim'])
    bmesh_box("TowerCap", (0.46, 0.46, 0.04), (TX, TY, BZ + tower_h + 0.28), m['stone_dark'])

    # === Gate ===
    bmesh_box("Gate", (0.08, 0.55, 1.10), (hw + 0.01, 0, BZ + 0.55), m['door'])
    bmesh_box("GateFrame", (0.10, 0.65, 0.08), (hw + 0.02, 0, BZ + 1.14), m['wood'])

    # Steps
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.20, 1.0, 0.06), (hw + 0.30 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_dark'])

    # === Archery targets (in courtyard) ===
    for j, ty in enumerate([0.7, -0.7]):
        # Target post
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=1.2,
                                            location=(0.8, ty, BZ + 0.60))
        bpy.context.active_object.name = f"TargetPost_{j}"
        bpy.context.active_object.data.materials.append(m['wood'])
        # Target circle (straw)
        bmesh_prism(f"Target_{j}", 0.18, 0.06, 10, (0.84, ty, BZ + 0.90), m['roof'])
        # Bullseye
        bmesh_prism(f"Bullseye_{j}", 0.06, 0.07, 8, (0.85, ty, BZ + 0.90), m['banner'])

    # === Weapon storage rack ===
    bmesh_box("WeaponRack", (0.08, 0.80, 0.80), (-0.3 - gar_w / 2 - 0.02, 0, BZ + 0.40), m['wood_dark'])
    for j in range(4):
        wy = -0.30 + j * 0.20
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=1.0,
                                            location=(-0.3 - gar_w / 2 - 0.06, wy, BZ + 0.50))
        spear = bpy.context.active_object
        spear.name = f"WeaponSpear_{j}"
        spear.data.materials.append(m['wood'])

    # Clay pots
    for i, (px, py) in enumerate([(hw + 0.2, 0.6), (hw + 0.15, -0.7)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(px, py, BZ + 0.06))
        pot = bpy.context.active_object
        pot.name = f"Pot_{i}"
        pot.scale = (1, 1, 0.8)
        pot.data.materials.append(m['roof'])


# ============================================================
# IRON AGE — Stone barracks hall with armory wing
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Stone foundation ===
    bmesh_box("Mound", (5.0, 4.6, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.18

    # === Main barracks hall ===
    hall_w, hall_d, hall_h = 2.4, 1.8, 2.4
    bmesh_box("Hall", (hall_w, hall_d, hall_h), (-0.2, 0, BZ + hall_h / 2), m['stone'], bevel=0.03)

    # Stone band
    bmesh_box("HallBand", (hall_w + 0.04, hall_d + 0.04, 0.06), (-0.2, 0, BZ + 1.2), m['stone_trim'])
    bmesh_box("HallTop", (hall_w + 0.04, hall_d + 0.04, 0.06), (-0.2, 0, BZ + hall_h), m['stone_trim'])

    # Pitched roof on hall
    rv = [
        (-0.2 - hall_w / 2 - 0.12, -hall_d / 2 - 0.12, BZ + hall_h + 0.03),
        (-0.2 + hall_w / 2 + 0.12, -hall_d / 2 - 0.12, BZ + hall_h + 0.03),
        (-0.2 + hall_w / 2 + 0.12, hall_d / 2 + 0.12, BZ + hall_h + 0.03),
        (-0.2 - hall_w / 2 - 0.12, hall_d / 2 + 0.12, BZ + hall_h + 0.03),
        (-0.2, -hall_d / 2 - 0.12, BZ + hall_h + 1.0),
        (-0.2, hall_d / 2 + 0.12, BZ + hall_h + 1.0),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("HallRoof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Ridge beam
    bmesh_box("Ridge", (0.06, hall_d + 0.28, 0.06), (-0.2, 0, BZ + hall_h + 1.0), m['wood_dark'])

    # Hall windows
    for y in [-0.50, 0.50]:
        bmesh_box(f"HWin_{y:.1f}", (0.06, 0.14, 0.35), (-0.2 + hall_w / 2 + 0.01, y, BZ + 1.6), m['window'])
        bmesh_box(f"HWinF_{y:.1f}", (0.07, 0.18, 0.04), (-0.2 + hall_w / 2 + 0.02, y, BZ + 1.80), m['stone_trim'])

    # Hall door
    bmesh_box("HallDoor", (0.08, 0.50, 1.0), (-0.2 + hall_w / 2 + 0.01, 0, BZ + 0.50), m['door'])
    bmesh_box("HallDoorFrame", (0.10, 0.58, 0.06), (-0.2 + hall_w / 2 + 0.02, 0, BZ + 1.03), m['wood'])

    # === Armory wing (smaller, attached to side) ===
    arm_w, arm_d, arm_h = 1.2, 1.4, 1.8
    bmesh_box("Armory", (arm_w, arm_d, arm_h), (-0.2, -hall_d / 2 - arm_d / 2 + 0.1, BZ + arm_h / 2),
              m['stone'], bevel=0.02)
    bmesh_box("ArmoryTop", (arm_w + 0.04, arm_d + 0.04, 0.06),
              (-0.2, -hall_d / 2 - arm_d / 2 + 0.1, BZ + arm_h), m['stone_trim'])

    # Armory flat roof
    bmesh_box("ArmoryRoof", (arm_w + 0.08, arm_d + 0.08, 0.06),
              (-0.2, -hall_d / 2 - arm_d / 2 + 0.1, BZ + arm_h + 0.06), m['stone_dark'])

    # Armory door
    bmesh_box("ArmDoor", (0.06, 0.35, 0.75),
              (-0.2 + arm_w / 2 + 0.01, -hall_d / 2 - arm_d / 2 + 0.1, BZ + 0.38), m['door'])

    # === Iron weapon racks (outside armory) ===
    for j, rx in enumerate([-0.9, -0.5]):
        bmesh_box(f"IronRack_{j}", (0.06, 0.04, 1.0),
                  (rx, -hall_d / 2 - arm_d + 0.15, BZ + 0.50), m['iron'])
        bmesh_box(f"IronRackBar_{j}", (0.50, 0.04, 0.04),
                  (rx + 0.20, -hall_d / 2 - arm_d + 0.15, BZ + 0.95), m['iron'])
        # Swords on rack
        for k in range(3):
            sx = rx + 0.05 + k * 0.15
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.010, depth=0.70,
                                                location=(sx, -hall_d / 2 - arm_d + 0.12, BZ + 0.55))
            bpy.context.active_object.name = f"Sword_{j}_{k}"
            bpy.context.active_object.data.materials.append(m['iron'])

    # === Training yard with straw dummies ===
    # Flattened training area
    bmesh_box("TrainYard", (1.6, 1.4, 0.04), (1.2, 0, BZ + 0.02), m['stone_dark'])

    # Straw training dummies
    for j, (dx, dy) in enumerate([(0.8, 0.3), (1.4, -0.3), (1.6, 0.4)]):
        # Pole
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=1.3,
                                            location=(dx, dy, BZ + 0.65))
        bpy.context.active_object.name = f"DummyPole_{j}"
        bpy.context.active_object.data.materials.append(m['wood'])
        # Straw body
        bmesh_prism(f"DummyBody_{j}", 0.12, 0.50, 8, (dx, dy, BZ + 0.70), m['roof'])
        # Straw head
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(dx, dy, BZ + 1.25))
        bpy.context.active_object.name = f"DummyHead_{j}"
        bpy.context.active_object.data.materials.append(m['roof'])
        # Cross-arms
        bmesh_box(f"DummyArm_{j}", (0.04, 0.45, 0.04), (dx, dy, BZ + 1.0), m['wood'])

    # === Steps to hall ===
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.18, 0.9, 0.06),
                  (-0.2 + hall_w / 2 + 0.28 + i * 0.20, 0, BZ - 0.04 - i * 0.06), m['stone_dark'])

    # Woodpile near armory
    for j in range(3):
        for k in range(2):
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.5,
                                                location=(-1.6, -0.3 + j * 0.12, BZ + 0.04 + k * 0.09))
            log = bpy.context.active_object
            log.name = f"Log_{j}_{k}"
            log.rotation_euler = (math.radians(90), 0, 0)
            log.data.materials.append(m['wood_dark'])


# ============================================================
# CLASSICAL AGE — Roman castra with colonnade
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Grand stepped platform ===
    for i in range(3):
        w = 5.0 - i * 0.30
        d = 4.6 - i * 0.25
        bmesh_box(f"Plat_{i}", (w, d, 0.08), (0, 0, Z + 0.04 + i * 0.08), m['stone_light'], bevel=0.02)

    BZ = Z + 0.24

    # === Rectangular fort walls ===
    WALL_H = 2.0
    hw = 2.0
    wt = 0.18
    bmesh_box("WallF", (wt, hw * 2, WALL_H), (hw, 0, BZ + WALL_H / 2), m['stone_light'], bevel=0.02)
    bmesh_box("WallB", (wt, hw * 2, WALL_H), (-hw, 0, BZ + WALL_H / 2), m['stone_light'], bevel=0.02)
    bmesh_box("WallR", (hw * 2, wt, WALL_H), (0, -hw, BZ + WALL_H / 2), m['stone_light'], bevel=0.02)
    bmesh_box("WallL", (hw * 2, wt, WALL_H), (0, hw, BZ + WALL_H / 2), m['stone_light'], bevel=0.02)

    # Wall-top walkway
    for label, pos, size in [
        ("F", (hw, 0), (0.28, hw * 2, 0.06)),
        ("B", (-hw, 0), (0.28, hw * 2, 0.06)),
        ("R", (0, -hw), (hw * 2, 0.28, 0.06)),
        ("L", (0, hw), (hw * 2, 0.28, 0.06)),
    ]:
        bmesh_box(f"Walk_{label}", size, (*pos, BZ + WALL_H + 0.03), m['stone_trim'])

    # Battlements
    for i in range(9):
        y = -1.6 + i * 0.40
        bmesh_box(f"MF_{i}", (0.10, 0.14, 0.18), (hw + 0.05, y, BZ + WALL_H + 0.15), m['stone_trim'])
        bmesh_box(f"MB_{i}", (0.10, 0.14, 0.18), (-hw - 0.05, y, BZ + WALL_H + 0.15), m['stone_trim'])
    for i in range(9):
        x = -1.6 + i * 0.40
        bmesh_box(f"MR_{i}", (0.14, 0.10, 0.18), (x, -hw - 0.05, BZ + WALL_H + 0.15), m['stone_trim'])
        bmesh_box(f"ML_{i}", (0.14, 0.10, 0.18), (x, hw + 0.05, BZ + WALL_H + 0.15), m['stone_trim'])

    # === Corner towers (4, square with flat tops) ===
    tower_h = 2.8
    for xs, ys, label in [(-1, -1, "BL"), (-1, 1, "FL"), (1, -1, "BR"), (1, 1, "FR")]:
        tx, ty = xs * hw, ys * hw
        bmesh_box(f"Tower_{label}", (0.55, 0.55, tower_h), (tx, ty, BZ + tower_h / 2),
                  m['stone_light'], bevel=0.02)
        bmesh_box(f"TTop_{label}", (0.62, 0.62, 0.06), (tx, ty, BZ + tower_h + 0.03), m['stone_trim'])
        # Flat cap
        bmesh_box(f"TCap_{label}", (0.50, 0.50, 0.04), (tx, ty, BZ + tower_h + 0.08), m['stone_dark'])

    # === Main principia (headquarters) with colonnade ===
    princ_w, princ_d, princ_h = 2.0, 1.4, 2.4
    bmesh_box("Principia", (princ_w, princ_d, princ_h), (0, 0, BZ + princ_h / 2),
              m['stone_light'], bevel=0.02)

    # Cornice
    bmesh_box("PCornice", (princ_w + 0.06, princ_d + 0.06, 0.06), (0, 0, BZ + princ_h), m['stone_trim'])

    # Pitched roof
    rv = [
        (-princ_w / 2 - 0.10, -princ_d / 2 - 0.10, BZ + princ_h + 0.03),
        (princ_w / 2 + 0.10, -princ_d / 2 - 0.10, BZ + princ_h + 0.03),
        (princ_w / 2 + 0.10, princ_d / 2 + 0.10, BZ + princ_h + 0.03),
        (-princ_w / 2 - 0.10, princ_d / 2 + 0.10, BZ + princ_h + 0.03),
        (0, -princ_d / 2 - 0.10, BZ + princ_h + 0.80),
        (0, princ_d / 2 + 0.10, BZ + princ_h + 0.80),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("PrinRoof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Front colonnade (4 columns)
    col_h = 2.0
    for y in [-0.50, -0.17, 0.17, 0.50]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.07, depth=col_h,
                                            location=(princ_w / 2 + 0.30, y, BZ + col_h / 2))
        c = bpy.context.active_object
        c.name = f"Col_{y:.2f}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        bmesh_box(f"Cap_{y:.2f}", (0.16, 0.16, 0.05), (princ_w / 2 + 0.30, y, BZ + col_h + 0.025),
                  m['stone_trim'])
        bmesh_box(f"Base_{y:.2f}", (0.14, 0.14, 0.04), (princ_w / 2 + 0.30, y, BZ + 0.02),
                  m['stone_trim'])

    # Portico roof
    bmesh_box("Portico", (0.40, 1.20, 0.05), (princ_w / 2 + 0.30, 0, BZ + col_h + 0.075),
              m['stone_trim'])

    # Front pediment
    pv = [(princ_w / 2 + 0.35, -0.55, BZ + col_h + 0.10),
          (princ_w / 2 + 0.35, 0.55, BZ + col_h + 0.10),
          (princ_w / 2 + 0.35, 0, BZ + col_h + 0.45)]
    mesh_from_pydata("Pediment", pv, [(0, 1, 2)], m['stone_light'])

    # Door
    bmesh_box("Door", (0.06, 0.40, 1.10), (princ_w / 2 + 0.01, 0, BZ + 0.55), m['door'])

    # Gate (main entrance through wall)
    bmesh_box("Gate", (0.08, 0.60, 1.30), (hw + 0.01, 0, BZ + 0.65), m['door'])
    bmesh_box("GateFrame", (0.10, 0.70, 0.08), (hw + 0.02, 0, BZ + 1.34), m['stone_trim'])

    # Steps to gate
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.20, 1.2, 0.06), (hw + 0.35 + i * 0.22, 0, BZ - 0.04 - i * 0.06),
                  m['stone_light'])

    # === Training field (open area in courtyard) ===
    bmesh_box("TrainField", (1.4, 1.6, 0.04), (0, 0, BZ + 0.02), m['stone_dark'])

    # === Eagle standard (aquila) ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=2.5,
                                        location=(0, 0, BZ + princ_h + 0.80 + 1.25))
    pole = bpy.context.active_object
    pole.name = "EaglePole"
    pole.data.materials.append(m['wood'])

    # Eagle ornament at top
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0, 0, BZ + princ_h + 0.80 + 2.55))
    eagle = bpy.context.active_object
    eagle.name = "Eagle"
    eagle.scale = (1.2, 0.5, 0.8)
    eagle.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # Cross-bar on standard
    bmesh_box("StandardBar", (0.04, 0.40, 0.04), (0, 0, BZ + princ_h + 0.80 + 2.30), m['gold'])

    # Banner hanging from cross-bar
    bv = [(0.04, -0.18, BZ + princ_h + 3.06), (0.04, 0.18, BZ + princ_h + 3.06),
          (0.04, 0.15, BZ + princ_h + 2.65), (0.04, -0.15, BZ + princ_h + 2.70)]
    mesh_from_pydata("EagleBanner", bv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# MEDIEVAL AGE — Stone keep barracks with crenellated walls
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Heavy stone foundation ===
    bmesh_box("Found1", (5.0, 4.8, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.05)
    bmesh_box("Found2", (4.6, 4.4, 0.13), (0, 0, Z + 0.185), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.25

    # === Curtain walls ===
    WALL_H = 2.2
    wall_t = 0.20
    hw = 1.9

    bmesh_box("WallF", (wall_t, hw * 2 - 0.2, WALL_H), (hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallB", (wall_t, hw * 2 - 0.2, WALL_H), (-hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallR", (hw * 2 - 0.2, wall_t, WALL_H), (0, -hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallL", (hw * 2 - 0.2, wall_t, WALL_H), (0, hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)

    # Wall-walk ledge
    ledge_z = BZ + WALL_H
    bmesh_box("LedgeF", (0.32, hw * 2, 0.06), (hw, 0, ledge_z + 0.03), m['stone_trim'])
    bmesh_box("LedgeB", (0.32, hw * 2, 0.06), (-hw, 0, ledge_z + 0.03), m['stone_trim'])
    bmesh_box("LedgeR", (hw * 2, 0.32, 0.06), (0, -hw, ledge_z + 0.03), m['stone_trim'])
    bmesh_box("LedgeL", (hw * 2, 0.32, 0.06), (0, hw, ledge_z + 0.03), m['stone_trim'])

    # Crenellations
    merlon_z = ledge_z + 0.06
    for i in range(8):
        y = -1.4 + i * 0.38
        bmesh_box(f"MerlF_{i}", (0.10, 0.16, 0.20), (hw + 0.05, y, merlon_z + 0.10), m['stone_trim'], bevel=0.01)
        bmesh_box(f"MerlB_{i}", (0.10, 0.16, 0.20), (-hw - 0.05, y, merlon_z + 0.10), m['stone_trim'], bevel=0.01)
    for i in range(8):
        x = -1.4 + i * 0.38
        bmesh_box(f"MerlR_{i}", (0.16, 0.10, 0.20), (x, -hw - 0.05, merlon_z + 0.10), m['stone_trim'], bevel=0.01)
        bmesh_box(f"MerlL_{i}", (0.16, 0.10, 0.20), (x, hw + 0.05, merlon_z + 0.10), m['stone_trim'], bevel=0.01)

    # === Main barracks keep ===
    keep_w, keep_d, keep_h = 1.8, 1.5, 3.2
    bmesh_box("Keep", (keep_w, keep_d, keep_h), (-0.2, 0, BZ + keep_h / 2), m['stone'], bevel=0.03)

    # Keep stone bands
    for kz in [BZ + 0.8, BZ + 1.6, BZ + 2.4, BZ + keep_h]:
        bmesh_box(f"KeepBand_{kz:.1f}", (keep_w + 0.06, keep_d + 0.06, 0.06),
                  (-0.2, 0, kz), m['stone_trim'], bevel=0.02)

    # Keep battlements
    keep_top = BZ + keep_h + 0.04
    for i in range(5):
        y = -0.5 + i * 0.25
        bmesh_box(f"KMerlF_{i}", (0.10, 0.14, 0.18),
                  (-0.2 + keep_w / 2 + 0.05, y, keep_top + 0.09), m['stone_trim'], bevel=0.01)
        bmesh_box(f"KMerlB_{i}", (0.10, 0.14, 0.18),
                  (-0.2 - keep_w / 2 - 0.05, y, keep_top + 0.09), m['stone_trim'], bevel=0.01)
    for i in range(5):
        x = -0.2 - 0.5 + i * 0.25
        bmesh_box(f"KMerlR_{i}", (0.14, 0.10, 0.18),
                  (x, -keep_d / 2 - 0.05, keep_top + 0.09), m['stone_trim'], bevel=0.01)
        bmesh_box(f"KMerlL_{i}", (0.14, 0.10, 0.18),
                  (x, keep_d / 2 + 0.05, keep_top + 0.09), m['stone_trim'], bevel=0.01)

    # Keep pitched roof
    rv = [
        (-0.2 - keep_w / 2 - 0.10, -keep_d / 2 - 0.10, keep_top + 0.18),
        (-0.2 + keep_w / 2 + 0.10, -keep_d / 2 - 0.10, keep_top + 0.18),
        (-0.2 + keep_w / 2 + 0.10, keep_d / 2 + 0.10, keep_top + 0.18),
        (-0.2 - keep_w / 2 - 0.10, keep_d / 2 + 0.10, keep_top + 0.18),
        (-0.2, -keep_d / 2 - 0.10, keep_top + 1.2),
        (-0.2, keep_d / 2 + 0.10, keep_top + 1.2),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("KeepRoof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Keep windows (arrow slits + normal)
    for y in [-0.40, 0.40]:
        for kz in [BZ + 1.2, BZ + 2.4]:
            bmesh_box(f"KWin_{y:.1f}_{kz:.1f}", (0.07, 0.14, 0.40),
                      (-0.2 + keep_w / 2 + 0.01, y, kz), m['window'])

    # Keep door
    bmesh_box("KeepDoor", (0.08, 0.45, 1.10), (-0.2 + keep_w / 2 + 0.01, 0, BZ + 0.55), m['door'])
    # Iron bands on door
    for dz in [0.3, 0.6, 0.9]:
        bmesh_box(f"DoorBand_{dz:.1f}", (0.09, 0.50, 0.04),
                  (-0.2 + keep_w / 2 + 0.02, 0, BZ + dz), m['iron'])

    # === Armory tower (round, corner) ===
    TX, TY = hw - 0.2, hw - 0.2
    tower_r = 0.42
    tower_h = 3.6
    bmesh_prism("ArmoryTower", tower_r, tower_h, 10, (TX, TY, BZ), m['stone_upper'], bevel=0.02)
    for tz in [BZ + 1.2, BZ + 2.4, BZ + tower_h - 0.12]:
        bmesh_prism(f"ATBand_{tz:.1f}", tower_r + 0.03, 0.06, 10, (TX, TY, tz), m['stone_trim'])
    bmesh_prism("ATParapet", tower_r + 0.06, 0.10, 10, (TX, TY, BZ + tower_h), m['stone_trim'])
    # Tower merlons
    for i in range(6):
        a = (2 * math.pi * i) / 6
        bmesh_box(f"ATMerl_{i}", (0.10, 0.10, 0.14),
                  (TX + (tower_r + 0.08) * math.cos(a), TY + (tower_r + 0.08) * math.sin(a),
                   BZ + tower_h + 0.17), m['stone_trim'], bevel=0.01)
    bmesh_cone("ATRoof", tower_r + 0.08, 0.9, 10, (TX, TY, BZ + tower_h + 0.24), m['roof'])

    # Arrow slits on tower
    for az in [BZ + 1.0, BZ + 2.0, BZ + 3.0]:
        bmesh_box(f"ATSlit_{az:.1f}", (0.04, 0.08, 0.25),
                  (TX + tower_r * 0.7, TY + tower_r * 0.7, az), m['window'])

    # === Gatehouse ===
    gate_x = hw + wall_t / 2
    bmesh_box("Gatehouse", (0.50, 1.0, WALL_H + 0.6), (gate_x, 0, BZ + (WALL_H + 0.6) / 2),
              m['stone'], bevel=0.02)
    bmesh_box("GateArch", (0.08, 0.55, 1.20), (gate_x + 0.22, 0, BZ + 0.60), m['door'])
    # Portcullis bars
    for gy in [-0.20, -0.08, 0.04, 0.16]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=1.10,
                                            location=(gate_x + 0.24, gy, BZ + 0.55))
        bpy.context.active_object.name = f"Portcullis_{gy:.2f}"
        bpy.context.active_object.data.materials.append(m['iron'])
    # Horizontal bars
    for gz in [BZ + 0.25, BZ + 0.60, BZ + 0.95]:
        bmesh_box(f"PBar_{gz:.1f}", (0.03, 0.45, 0.02), (gate_x + 0.24, 0, gz), m['iron'])

    # Steps to gate
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.20, 1.2, 0.06), (gate_x + 0.40 + i * 0.22, 0, BZ - 0.04 - i * 0.06),
                  m['stone_dark'])

    # === Training yard (inside courtyard) ===
    bmesh_box("TrainYard", (1.2, 1.4, 0.04), (0.6, -0.4, BZ + 0.02), m['stone_dark'])

    # Straw training dummies
    for j, (dx, dy) in enumerate([(0.3, -0.8), (0.9, -0.2), (0.6, -0.6)]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=1.2,
                                            location=(dx, dy, BZ + 0.60))
        bpy.context.active_object.name = f"Dummy_{j}"
        bpy.context.active_object.data.materials.append(m['wood'])
        bmesh_prism(f"DBody_{j}", 0.10, 0.40, 8, (dx, dy, BZ + 0.65), m['roof'])
        bmesh_box(f"DArm_{j}", (0.04, 0.35, 0.04), (dx, dy, BZ + 0.95), m['wood'])
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(dx, dy, BZ + 1.15))
        bpy.context.active_object.name = f"DHead_{j}"
        bpy.context.active_object.data.materials.append(m['roof'])

    # === Banner on keep roof ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=1.0,
                                        location=(-0.2, 0, keep_top + 1.2 + 0.5))
    bpy.context.active_object.data.materials.append(m['wood'])
    fz = keep_top + 1.95
    fv = [(-0.17, 0, fz), (-0.17 + 0.50, 0.03, fz - 0.05),
          (-0.17 + 0.50, 0.02, fz + 0.25), (-0.17, 0, fz + 0.22)]
    mesh_from_pydata("Banner", fv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False

    # Gold finial
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(-0.2, 0, keep_top + 1.22))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # Torch holders on gatehouse
    for ys in [-0.35, 0.35]:
        bmesh_box(f"Torch_{ys:.1f}", (0.04, 0.04, 0.14), (gate_x + 0.26, ys, BZ + 1.3), m['iron'])


# ============================================================
# GUNPOWDER AGE — Fortified military compound
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Heavy foundation ===
    bmesh_box("Found", (5.2, 5.0, 0.22), (0, 0, Z + 0.11), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.22
    WALL_H = 2.6
    hw = 2.1

    # === Thick fortress walls ===
    wt = 0.25
    bmesh_box("WallF", (wt, hw * 2 - 0.3, WALL_H), (hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.03)
    bmesh_box("WallB", (wt, hw * 2 - 0.3, WALL_H), (-hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.03)
    bmesh_box("WallR", (hw * 2 - 0.3, wt, WALL_H), (0, -hw, BZ + WALL_H / 2), m['stone'], bevel=0.03)
    bmesh_box("WallL", (hw * 2 - 0.3, wt, WALL_H), (0, hw, BZ + WALL_H / 2), m['stone'], bevel=0.03)

    # Battlements on walls
    merlon_z = BZ + WALL_H + 0.06
    for i in range(9):
        y = -1.6 + i * 0.40
        bmesh_box(f"MF_{i}", (0.12, 0.14, 0.20), (hw + 0.07, y, merlon_z + 0.10), m['stone_trim'], bevel=0.01)
        bmesh_box(f"MB_{i}", (0.12, 0.14, 0.20), (-hw - 0.07, y, merlon_z + 0.10), m['stone_trim'], bevel=0.01)
    for i in range(9):
        x = -1.6 + i * 0.40
        bmesh_box(f"MR_{i}", (0.14, 0.12, 0.20), (x, -hw - 0.07, merlon_z + 0.10), m['stone_trim'], bevel=0.01)
        bmesh_box(f"ML_{i}", (0.14, 0.12, 0.20), (x, hw + 0.07, merlon_z + 0.10), m['stone_trim'], bevel=0.01)

    # === Angular bastions (4 corners) ===
    bastion_h = WALL_H + 0.3
    for xs, ys, label in [(-1, -1, "BL"), (-1, 1, "FL"), (1, -1, "BR"), (1, 1, "FR")]:
        bx, by = xs * hw, ys * hw
        bmesh_prism(f"Bastion_{label}", 0.50, bastion_h, 6, (bx, by, BZ), m['stone_upper'], bevel=0.02)
        bmesh_prism(f"BTop_{label}", 0.55, 0.08, 6, (bx, by, BZ + bastion_h), m['stone_trim'])
        # Cannon slit
        bmesh_box(f"CSlit_{label}", (0.04, 0.12, 0.08),
                  (bx + xs * 0.50, by + ys * 0.50, BZ + 1.0), m['window'])

    # === Main barracks building ===
    bar_w, bar_d, bar_h = 2.2, 1.8, 2.8
    bmesh_box("Barracks", (bar_w, bar_d, bar_h), (0, 0.2, BZ + bar_h / 2), m['stone'], bevel=0.03)
    for pz in [BZ + 1.0, BZ + 2.0, BZ + bar_h]:
        bmesh_box(f"BarBand_{pz:.1f}", (bar_w + 0.06, bar_d + 0.06, 0.06), (0, 0.2, pz),
                  m['stone_trim'], bevel=0.02)

    # Hipped roof
    pyramid_roof("BarRoof", w=bar_w - 0.2, d=bar_d - 0.2, h=1.2, overhang=0.18,
                 origin=(0, 0.2, BZ + bar_h + 0.04), material=m['roof'])

    # Barracks windows (2 rows)
    for row, z_off in [(0.4, 0), (1.5, 1)]:
        for y in [-0.4, 0.1, 0.6]:
            bmesh_box(f"BWin_{row}_{y:.1f}", (0.07, 0.18, 0.45),
                      (bar_w / 2 + 0.01, 0.2 + y, BZ + row + 0.10), m['window'])
            bmesh_box(f"BWinH_{row}_{y:.1f}", (0.08, 0.22, 0.04),
                      (bar_w / 2 + 0.02, 0.2 + y, BZ + row + 0.37), m['stone_trim'])

    # Barracks door
    bmesh_box("BarDoor", (0.08, 0.50, 1.20), (bar_w / 2 + 0.01, 0.2, BZ + 0.60), m['door'])
    bmesh_box("BarDoorFrame", (0.10, 0.58, 0.08), (bar_w / 2 + 0.02, 0.2, BZ + 1.24), m['stone_trim'])

    # === Cannon storage area ===
    # Low roofed shed
    cs_x, cs_y = -0.8, -1.0
    bmesh_box("CannonShed", (1.2, 0.8, 1.2), (cs_x, cs_y, BZ + 0.60), m['stone_dark'], bevel=0.02)
    bmesh_box("CSShedRoof", (1.3, 0.9, 0.06), (cs_x, cs_y, BZ + 1.23), m['stone_trim'])

    # Cannons in storage (2)
    for j, cy in enumerate([-1.15, -0.85]):
        # Barrel
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06, depth=0.60,
                                            location=(cs_x + 0.65, cy, BZ + 0.20))
        cannon = bpy.context.active_object
        cannon.name = f"Cannon_{j}"
        cannon.rotation_euler = (0, math.radians(90), 0)
        cannon.data.materials.append(m['iron'])
        # Wheels
        for side_y in [-0.10, 0.10]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.10, depth=0.03,
                                                location=(cs_x + 0.50, cy + side_y, BZ + 0.10))
            wheel = bpy.context.active_object
            wheel.name = f"CWheel_{j}_{side_y:.1f}"
            wheel.rotation_euler = (math.radians(90), 0, 0)
            wheel.data.materials.append(m['wood_dark'])

    # === Powder magazine (small, thick-walled building) ===
    pm_x, pm_y = 0.8, -1.0
    bmesh_box("Magazine", (0.8, 0.7, 1.0), (pm_x, pm_y, BZ + 0.50), m['stone_upper'], bevel=0.03)
    bmesh_box("MagRoof", (0.9, 0.8, 0.06), (pm_x, pm_y, BZ + 1.03), m['stone_trim'])
    # Heavy door
    bmesh_box("MagDoor", (0.06, 0.30, 0.60), (pm_x + 0.41, pm_y, BZ + 0.30), m['iron'])
    # Iron reinforcement bands
    for dz in [0.15, 0.35, 0.55]:
        bmesh_box(f"MagBand_{dz:.1f}", (0.07, 0.34, 0.03), (pm_x + 0.42, pm_y, BZ + dz), m['iron'])

    # === Grand gate ===
    gate_x = hw + wt / 2
    bmesh_box("Gatehouse", (0.60, 1.2, WALL_H + 0.8), (gate_x, 0, BZ + (WALL_H + 0.8) / 2),
              m['stone'], bevel=0.02)
    bmesh_box("GateArch", (0.08, 0.70, 1.40), (gate_x + 0.28, 0, BZ + 0.70), m['door'])
    bmesh_box("GateKeystone", (0.10, 0.80, 0.10), (gate_x + 0.29, 0, BZ + 1.44), m['stone_trim'], bevel=0.02)

    # Steps
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.20, 1.4, 0.06), (gate_x + 0.50 + i * 0.22, 0, BZ - 0.04 - i * 0.06),
                  m['stone_dark'])

    # Banner on barracks
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.8,
                                        location=(0, 0.2, BZ + bar_h + 1.2 + 0.4))
    bpy.context.active_object.data.materials.append(m['wood'])
    fz = BZ + bar_h + 1.85
    fv = [(0.03, 0.2, fz), (0.50, 0.23, fz - 0.05),
          (0.50, 0.22, fz + 0.25), (0.03, 0.2, fz + 0.22)]
    mesh_from_pydata("Banner", fv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# ENLIGHTENMENT AGE — Regimental barracks with parade ground
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.18
    bmesh_box("Found", (5.2, 5.0, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.04)

    # === Central block (main barracks) ===
    main_w, main_d, main_h = 2.2, 2.0, 2.8
    bmesh_box("Main", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone'], bevel=0.03)

    # Moldings
    bmesh_box("BaseMold", (main_w + 0.06, main_d + 0.06, 0.06), (0, 0, BZ + 0.03), m['stone_trim'], bevel=0.02)
    bmesh_box("MidMold", (main_w + 0.06, main_d + 0.06, 0.05), (0, 0, BZ + 1.0), m['stone_trim'], bevel=0.01)
    bmesh_box("Cornice", (main_w + 0.08, main_d + 0.08, 0.08), (0, 0, BZ + main_h), m['stone_trim'], bevel=0.03)

    # Balustrade
    bmesh_box("Balustrade", (main_w + 0.04, main_d + 0.04, 0.22), (0, 0, BZ + main_h + 0.11), m['stone_light'])

    # Main windows (3 cols x 2 rows on front)
    for row, (z_off, wh) in enumerate([(0.4, 0.50), (1.5, 0.55)]):
        for y in [-0.55, 0, 0.55]:
            bmesh_box(f"MWin_{row}_{y:.1f}", (0.07, 0.20, wh),
                      (main_w / 2 + 0.01, y, BZ + z_off), m['window'])
            bmesh_box(f"MWinH_{row}_{y:.1f}", (0.08, 0.24, 0.04),
                      (main_w / 2 + 0.02, y, BZ + z_off + wh / 2 + 0.02), m['stone_trim'])

    # Main door
    bmesh_box("Door", (0.08, 0.50, 1.20), (main_w / 2 + 0.01, 0, BZ + 0.60), m['door'])
    bmesh_box("DoorSurround", (0.10, 0.60, 1.30), (main_w / 2 + 0.02, 0, BZ + 0.65), m['stone_light'])

    # Front pediment
    pv = [(main_w / 2 + 0.04, -0.50, BZ + main_h + 0.01),
          (main_w / 2 + 0.04, 0.50, BZ + main_h + 0.01),
          (main_w / 2 + 0.04, 0, BZ + main_h + 0.40)]
    mesh_from_pydata("Pediment", pv, [(0, 1, 2)], m['stone_light'])

    # === Symmetrical wings ===
    wing_w, wing_d, wing_h = 1.4, 1.6, 2.2
    for ys, lbl in [(-1.7, "R"), (1.7, "L")]:
        bmesh_box(f"Wing_{lbl}", (wing_w, wing_d, wing_h), (0.2, ys, BZ + wing_h / 2),
                  m['stone'], bevel=0.02)
        bmesh_box(f"WingCornice_{lbl}", (wing_w + 0.06, wing_d + 0.06, 0.06),
                  (0.2, ys, BZ + wing_h), m['stone_trim'], bevel=0.02)
        # Wing hipped roof
        pyramid_roof(f"WingRoof_{lbl}", w=wing_w - 0.2, d=wing_d - 0.2, h=0.6, overhang=0.10,
                     origin=(0.2, ys, BZ + wing_h + 0.03), material=m['roof'])
        # Wing windows (2 rows, 2 cols)
        for row, z_off in [(0.4, 0), (1.3, 1)]:
            for wy in [-0.35, 0.35]:
                bmesh_box(f"WWin_{lbl}_{row}_{wy:.1f}", (0.06, 0.18, 0.45),
                          (0.2 + wing_w / 2 + 0.01, ys + wy, BZ + row + 0.08), m['window'])

    # Hipped roof on main block
    pyramid_roof("MainRoof", w=main_w - 0.2, d=main_d - 0.2, h=0.7, overhang=0.12,
                 origin=(0, 0, BZ + main_h + 0.22), material=m['roof'])

    # === Clock tower (on main building) ===
    ct_z = BZ + main_h + 0.22 + 0.7  # top of main roof
    bmesh_box("ClockTower", (0.6, 0.6, 1.6), (0, 0, ct_z + 0.80), m['stone'], bevel=0.02)
    bmesh_box("CTCornice", (0.7, 0.7, 0.06), (0, 0, ct_z + 1.60), m['stone_trim'], bevel=0.02)
    # Clock face (front)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.18, depth=0.04,
                                        location=(0.31, 0, ct_z + 1.15))
    clock = bpy.context.active_object
    clock.name = "Clock"
    clock.rotation_euler = (0, math.radians(90), 0)
    clock.data.materials.append(m['gold'])
    # Spire
    bmesh_cone("CTSpire", 0.22, 0.70, 8, (0, 0, ct_z + 1.63), m['roof'])

    # === Parade ground (in front) ===
    bmesh_box("ParadeGround", (2.0, 3.5, 0.04), (main_w / 2 + 1.2, 0, BZ + 0.02), m['stone_dark'])

    # Flagpole on parade ground
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=3.0,
                                        location=(main_w / 2 + 1.2, 0, BZ + 1.50))
    bpy.context.active_object.data.materials.append(m['iron'])
    fv = [(main_w / 2 + 1.23, 0, BZ + 2.80), (main_w / 2 + 1.23 + 0.50, 0.03, BZ + 2.75),
          (main_w / 2 + 1.23 + 0.50, 0.02, BZ + 3.05), (main_w / 2 + 1.23, 0, BZ + 3.02)]
    mesh_from_pydata("Flag", fv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False

    # Iron railings along parade ground
    for i in range(10):
        fy = -1.5 + i * 0.33
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=0.50,
                                            location=(main_w / 2 + 2.3, fy, BZ + 0.29))
        bpy.context.active_object.data.materials.append(m['iron'])
    # Fence rail
    bmesh_box("FenceRail", (0.02, 3.20, 0.02), (main_w / 2 + 2.3, 0, BZ + 0.50), m['iron'])

    # Steps to main entrance
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.18, 1.2, 0.05),
                  (main_w / 2 + 0.30 + i * 0.20, 0, BZ - 0.03 - i * 0.05), m['stone_light'])

    # Quoins on main block corners
    for xs in [-1, 1]:
        for ys in [-1, 1]:
            for z_off in [0.15, 0.55, 0.95, 1.35, 1.75, 2.15]:
                bmesh_box(f"Quoin_{xs}_{ys}_{z_off:.1f}", (0.06, 0.06, 0.12),
                          (xs * (main_w / 2 + 0.01), ys * (main_d / 2 + 0.01), BZ + z_off),
                          m['stone_light'])


# ============================================================
# INDUSTRIAL AGE — Military depot with iron/brick, rail connection
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.12
    bmesh_box("Found", (5.2, 5.0, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.04)

    # === Main depot building (wide, industrial) ===
    dep_w, dep_d, dep_h = 3.0, 2.2, 3.0
    bmesh_box("Depot", (dep_w, dep_d, dep_h), (0, 0.2, BZ + dep_h / 2), m['stone'], bevel=0.02)

    # Iron beam grid on facade
    for z in [BZ + 0.8, BZ + 1.6, BZ + 2.4]:
        bmesh_box(f"IronH_{z:.1f}", (0.03, 2.2, 0.05), (dep_w / 2 + 0.01, 0.2, z), m['iron'])
    for y in [-0.60, 0, 0.60]:
        bmesh_box(f"IronV_{y:.1f}", (0.03, 0.05, dep_h), (dep_w / 2 + 0.01, 0.2 + y, BZ + dep_h / 2), m['iron'])

    # Windows (2 rows x 3 cols on front)
    for row, z_off in enumerate([0.4, 1.5]):
        for y in [-0.55, 0.2, 0.95]:
            h = 0.45 if row < 1 else 0.40
            bmesh_box(f"DWin_{row}_{y:.1f}", (0.07, 0.22, h),
                      (dep_w / 2 + 0.01, y, BZ + z_off + 0.10), m['window'])
            bmesh_box(f"DWinH_{row}_{y:.1f}", (0.08, 0.26, 0.04),
                      (dep_w / 2 + 0.02, y, BZ + z_off + h / 2 + 0.12), m['stone_trim'])

    # Band and cornice
    bmesh_box("Band", (dep_w + 0.04, dep_d + 0.04, 0.05), (0, 0.2, BZ + 1.2), m['stone_trim'])
    bmesh_box("Cornice", (dep_w + 0.08, dep_d + 0.08, 0.08), (0, 0.2, BZ + dep_h), m['stone_trim'], bevel=0.02)

    # Flat roof with parapet
    bmesh_box("Roof", (dep_w + 0.06, dep_d + 0.06, 0.08), (0, 0.2, BZ + dep_h + 0.04), m['stone_dark'])
    bmesh_box("Parapet", (dep_w + 0.10, dep_d + 0.10, 0.16), (0, 0.2, BZ + dep_h + 0.16), m['stone_trim'], bevel=0.02)

    # Main door
    bmesh_box("DepotDoor", (0.08, 0.80, 1.60), (dep_w / 2 + 0.01, 0.2, BZ + 0.80), m['door'])
    bmesh_box("DoorSurround", (0.10, 0.90, 0.10), (dep_w / 2 + 0.02, 0.2, BZ + 1.64), m['stone_trim'], bevel=0.02)

    # === Munitions storage building (smaller, reinforced) ===
    ms_x, ms_y = -0.8, -1.5
    ms_w, ms_d, ms_h = 1.4, 1.0, 1.6
    bmesh_box("Munitions", (ms_w, ms_d, ms_h), (ms_x, ms_y, BZ + ms_h / 2), m['stone_upper'], bevel=0.02)
    bmesh_box("MunCornice", (ms_w + 0.06, ms_d + 0.06, 0.06), (ms_x, ms_y, BZ + ms_h), m['stone_trim'])
    bmesh_box("MunRoof", (ms_w + 0.08, ms_d + 0.08, 0.06), (ms_x, ms_y, BZ + ms_h + 0.06), m['stone_dark'])

    # Heavy iron door on munitions
    bmesh_box("MunDoor", (0.06, 0.40, 0.90), (ms_x + ms_w / 2 + 0.01, ms_y, BZ + 0.45), m['iron'])
    for dz in [0.20, 0.50, 0.80]:
        bmesh_box(f"MunBand_{dz:.1f}", (0.07, 0.44, 0.03), (ms_x + ms_w / 2 + 0.02, ms_y, BZ + dz), m['iron'])

    # Munitions windows (small, barred)
    for y in [-0.25, 0.25]:
        bmesh_box(f"MunWin_{y:.1f}", (0.06, 0.12, 0.18),
                  (ms_x + ms_w / 2 + 0.01, ms_y + y, BZ + 1.1), m['window'])
        # Bars
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.008, depth=0.18,
                                            location=(ms_x + ms_w / 2 + 0.03, ms_y + y, BZ + 1.1))
        bpy.context.active_object.data.materials.append(m['iron'])

    # === Rail connection (track running along side) ===
    # Two rails
    for ry in [-1.95, -2.15]:
        bmesh_box("Rail_" + str(ry), (4.0, 0.04, 0.04), (0, ry, BZ + 0.02), m['iron'])
    # Ties (wooden sleepers)
    for i in range(12):
        rx = -1.8 + i * 0.33
        bmesh_box(f"Tie_{i}", (0.12, 0.35, 0.03), (rx, -2.05, BZ + 0.015), m['wood_dark'])

    # === Smokestack / chimney ===
    bmesh_box("Chimney", (0.28, 0.28, 2.0), (-dep_w / 2 + 0.3, 0.2 + dep_d / 2 - 0.3, BZ + dep_h + 0.5 + 0.5),
              m['stone'], bevel=0.02)
    bmesh_box("ChimTop", (0.34, 0.34, 0.08),
              (-dep_w / 2 + 0.3, 0.2 + dep_d / 2 - 0.3, BZ + dep_h + 2.04), m['stone_trim'])

    # Chimney pot
    bmesh_prism("ChimPot", 0.06, 0.12, 8,
                (-dep_w / 2 + 0.3, 0.2 + dep_d / 2 - 0.3, BZ + dep_h + 2.08), m['stone_dark'])

    # === Loading dock ===
    bmesh_box("LoadDock", (1.0, 0.6, 0.30), (dep_w / 2 + 0.50, 0.2, BZ + 0.15), m['stone_dark'])

    # Crates on loading dock
    for i, (cx, cy) in enumerate([(dep_w / 2 + 0.35, 0.0), (dep_w / 2 + 0.55, 0.4)]):
        bmesh_box(f"Crate_{i}", (0.25, 0.25, 0.25), (cx, cy, BZ + 0.30 + 0.125), m['wood_dark'])

    # Barrel
    bmesh_prism("Barrel", 0.10, 0.28, 8, (dep_w / 2 + 0.70, 0.2, BZ + 0.30), m['wood_dark'])

    # === Iron fence around perimeter ===
    for i in range(10):
        fy = -2.0 + i * 0.44
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=0.50,
                                            location=(dep_w / 2 + 1.1, fy, BZ + 0.15))
        bpy.context.active_object.data.materials.append(m['iron'])
    bmesh_box("FenceRail", (0.02, 4.20, 0.02), (dep_w / 2 + 1.1, -0.1, BZ + 0.38), m['iron'])

    # Steps
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.18, 1.2, 0.05),
                  (dep_w / 2 + 0.20 + i * 0.20, 0.2, BZ - 0.03 - i * 0.04), m['stone_dark'])


# ============================================================
# MODERN AGE — Military base with bunkers, radar dish, vehicle bay
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.08
    bmesh_box("Found", (5.2, 5.0, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Main command building ===
    cmd_w, cmd_d, cmd_h = 2.4, 2.0, 2.4
    bmesh_box("Command", (cmd_w, cmd_d, cmd_h), (0, 0.3, BZ + cmd_h / 2), m['stone'], bevel=0.02)

    # Flat roof
    bmesh_box("CmdRoof", (cmd_w + 0.08, cmd_d + 0.08, 0.08), (0, 0.3, BZ + cmd_h + 0.04), m['stone_dark'])

    # Front glass wall
    bmesh_box("CmdGlass", (0.06, cmd_d - 0.4, cmd_h - 0.4),
              (cmd_w / 2 + 0.01, 0.3, BZ + cmd_h / 2 + 0.1), glass)
    # Horizontal bands
    for z in [BZ + 0.8, BZ + 1.6]:
        bmesh_box(f"CmdBand_{z:.1f}", (0.07, cmd_d - 0.3, 0.08),
                  (cmd_w / 2 + 0.02, 0.3, z), m['stone_trim'])
    # Vertical mullions
    for y in [-0.40, 0, 0.40]:
        bmesh_box(f"CmdMull_{y:.1f}", (0.05, 0.03, cmd_h - 0.5),
                  (cmd_w / 2 + 0.03, 0.3 + y, BZ + cmd_h / 2 + 0.1), metal)

    # Side windows
    for x in [-0.6, 0.3]:
        bmesh_box(f"CmdSWin_{x:.1f}", (0.30, 0.06, 0.60),
                  (x, 0.3 - cmd_d / 2 - 0.01, BZ + 1.4), glass)

    # Front door
    bmesh_box("CmdDoor", (0.06, 0.60, 1.40), (cmd_w / 2 + 0.01, 0.3, BZ + 0.70), glass)
    bmesh_box("CmdDoorFrame", (0.07, 0.64, 1.44), (cmd_w / 2 + 0.02, 0.3, BZ + 0.72), metal)

    # === Concrete bunkers (2, low and reinforced) ===
    for j, (bx, by) in enumerate([(-1.2, -1.0), (1.0, -1.2)]):
        bk_w, bk_d, bk_h = 1.0, 0.8, 0.9
        bmesh_box(f"Bunker_{j}", (bk_w, bk_d, bk_h), (bx, by, BZ + bk_h / 2),
                  m['stone_dark'], bevel=0.04)
        bmesh_box(f"BunkRoof_{j}", (bk_w + 0.06, bk_d + 0.06, 0.06),
                  (bx, by, BZ + bk_h + 0.03), m['stone_dark'])
        # Slit window
        bmesh_box(f"BunkSlit_{j}", (0.04, 0.30, 0.08),
                  (bx + bk_w / 2 + 0.01, by, BZ + bk_h - 0.15), m['window'])
        # Door
        bmesh_box(f"BunkDoor_{j}", (0.06, 0.35, 0.65),
                  (bx + bk_w / 2 + 0.01, by, BZ + 0.33), m['iron'])

    # === Radar dish (on roof of command building) ===
    roof_z = BZ + cmd_h + 0.12
    # Dish support pole
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=1.2,
                                        location=(0, 0.3, roof_z + 0.60))
    bpy.context.active_object.data.materials.append(metal)
    # Dish (half-sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.40, location=(0, 0.3, roof_z + 1.25))
    dish = bpy.context.active_object
    dish.name = "RadarDish"
    dish.scale = (1, 1, 0.35)
    dish.data.materials.append(metal)
    bpy.ops.object.shade_smooth()
    # Dish feed
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.35,
                                        location=(0, 0.3, roof_z + 1.45))
    bpy.context.active_object.data.materials.append(metal)

    # === Vehicle bay (open-fronted garage) ===
    vb_x, vb_y = -0.5, 1.5
    vb_w, vb_d, vb_h = 2.0, 1.2, 1.6
    # Back and side walls
    bmesh_box("VBBack", (vb_w, 0.15, vb_h), (vb_x, vb_y + vb_d / 2, BZ + vb_h / 2), m['stone'], bevel=0.02)
    bmesh_box("VBSideL", (0.15, vb_d, vb_h), (vb_x - vb_w / 2, vb_y, BZ + vb_h / 2), m['stone'], bevel=0.02)
    bmesh_box("VBSideR", (0.15, vb_d, vb_h), (vb_x + vb_w / 2, vb_y, BZ + vb_h / 2), m['stone'], bevel=0.02)
    # Roof
    bmesh_box("VBRoof", (vb_w + 0.10, vb_d + 0.10, 0.08), (vb_x, vb_y, BZ + vb_h + 0.04), m['stone_dark'])

    # Vehicle inside (simplified military truck shape)
    bmesh_box("Truck", (0.8, 0.5, 0.4), (vb_x, vb_y - 0.1, BZ + 0.30), m['stone_dark'])
    bmesh_box("TruckCab", (0.3, 0.5, 0.35), (vb_x + 0.55, vb_y - 0.1, BZ + 0.28), m['stone_dark'])
    # Wheels
    for wx in [-0.2, 0.2, 0.55]:
        for wy in [-0.30, 0.10]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=0.04,
                                                location=(vb_x + wx, vb_y - 0.1 + wy, BZ + 0.08))
            wheel = bpy.context.active_object
            wheel.name = f"TruckWheel_{wx:.1f}_{wy:.1f}"
            wheel.rotation_euler = (math.radians(90), 0, 0)
            wheel.data.materials.append(m['iron'])

    # === Chain-link fence (perimeter) ===
    # Fence posts
    fence_positions = []
    for i in range(12):
        fy = -2.3 + i * 0.42
        fence_positions.append((2.4, fy))
    for pos in fence_positions:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=1.0,
                                            location=(pos[0], pos[1], BZ + 0.50))
        bpy.context.active_object.data.materials.append(metal)
    # Fence wire (horizontal bars representing chain link)
    for z_off in [0.30, 0.55, 0.80, 1.00]:
        bmesh_box(f"FenceWire_{z_off:.2f}", (0.02, 4.80, 0.015),
                  (2.4, -0.2, BZ + z_off), metal)

    # Top rail
    bmesh_box("FenceTopRail", (0.02, 4.80, 0.02), (2.4, -0.2, BZ + 1.02), metal)

    # Entrance canopy
    bmesh_box("Canopy", (0.8, 1.2, 0.05), (cmd_w / 2 + 0.50, 0.3, BZ + 1.60), metal)
    for y in [-0.40, 0.40]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=1.5,
                                            location=(cmd_w / 2 + 0.50, 0.3 + y, BZ + 0.83))
        bpy.context.active_object.data.materials.append(metal)

    # Flag
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=2.0,
                                        location=(cmd_w / 2 + 0.50, 0.3 + 0.8, BZ + 1.0))
    bpy.context.active_object.data.materials.append(metal)
    fv = [(cmd_w / 2 + 0.53, 0.3 + 0.8, BZ + 1.80),
          (cmd_w / 2 + 0.53 + 0.45, 0.3 + 0.83, BZ + 1.75),
          (cmd_w / 2 + 0.53 + 0.45, 0.3 + 0.82, BZ + 2.05),
          (cmd_w / 2 + 0.53, 0.3 + 0.8, BZ + 2.02)]
    mesh_from_pydata("Flag", fv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False

    # Sandbags near bunkers
    for i, (sx, sy) in enumerate([(-1.7, -0.6), (-0.8, -1.5)]):
        for k in range(3):
            bmesh_box(f"Sandbag_{i}_{k}", (0.20, 0.10, 0.08),
                      (sx + k * 0.08, sy, BZ + 0.04 + k * 0.08), m['stone_dark'])


# ============================================================
# DIGITAL AGE — Cyber warfare center, high-tech facility
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.06
    bmesh_box("Found", (5.2, 5.0, 0.06), (0, 0, Z + 0.03), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Main cyber warfare building (angular, modern) ===
    main_w, main_d, main_h = 2.6, 2.2, 3.0
    bmesh_box("CyberMain", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), glass)

    # Steel frame grid
    for z in [BZ + 0.8, BZ + 1.6, BZ + 2.4]:
        bmesh_box(f"HFrame_{z:.1f}", (main_w + 0.02, main_d + 0.02, 0.04), (0, 0, z), metal)
    for x in [-1.0, 0, 1.0]:
        bmesh_box(f"VFrameF_{x:.1f}", (0.04, 0.04, main_h), (x, -main_d / 2 - 0.01, BZ + main_h / 2), metal)
        bmesh_box(f"VFrameB_{x:.1f}", (0.04, 0.04, main_h), (x, main_d / 2 + 0.01, BZ + main_h / 2), metal)
    for y in [-0.7, 0, 0.7]:
        bmesh_box(f"VFrameR_{y:.1f}", (0.04, 0.04, main_h), (main_w / 2 + 0.01, y, BZ + main_h / 2), metal)
        bmesh_box(f"VFrameL_{y:.1f}", (0.04, 0.04, main_h), (-main_w / 2 - 0.01, y, BZ + main_h / 2), metal)

    # Flat roof
    roof_z = BZ + main_h
    bmesh_box("MainRoof", (main_w + 0.08, main_d + 0.08, 0.06), (0, 0, roof_z + 0.03), metal)

    # LED accent strips
    bmesh_box("LED1", (main_w + 0.04, 0.06, 0.06), (0, -main_d / 2 - 0.02, roof_z - 0.15), m['gold'])
    bmesh_box("LED2", (0.06, main_d + 0.04, 0.06), (main_w / 2 + 0.02, 0, roof_z - 0.15), m['gold'])
    bmesh_box("LED3", (main_w + 0.04, 0.06, 0.06), (0, main_d / 2 + 0.02, BZ + 0.15), m['gold'])

    # === Lower tech wing (connected) ===
    wing_w, wing_d, wing_h = 1.8, 1.4, 2.0
    bmesh_box("TechWing", (wing_w, wing_d, wing_h), (1.5, -0.8, BZ + wing_h / 2), glass)
    for z in [BZ + 0.7, BZ + 1.4]:
        bmesh_box(f"WingH_{z:.1f}", (wing_w + 0.02, wing_d + 0.02, 0.04), (1.5, -0.8, z), metal)
    bmesh_box("WingRoof", (wing_w + 0.06, wing_d + 0.06, 0.05), (1.5, -0.8, BZ + wing_h + 0.025), metal)

    # Wing LED accent
    bmesh_box("WingLED", (wing_w + 0.02, 0.05, 0.05), (1.5, -0.8 - wing_d / 2 - 0.01, BZ + wing_h - 0.12), m['gold'])

    # === Entrance atrium ===
    bmesh_box("Atrium", (0.8, 1.6, 2.2), (main_w / 2 + 0.40, 0, BZ + 1.10), glass)
    bmesh_box("AtrFrame", (0.82, 1.62, 0.04), (main_w / 2 + 0.40, 0, BZ + 2.22), metal)

    # Entrance path
    bmesh_box("Path", (0.8, 1.0, 0.03), (main_w / 2 + 0.80, 0, BZ + 0.015), m['stone_light'])

    # === Antenna arrays (3, on roof) ===
    for i, (ax, ay) in enumerate([(-0.6, -0.5), (0.5, 0.4), (-0.3, 0.6)]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=2.0,
                                            location=(ax, ay, roof_z + 1.0))
        ant = bpy.context.active_object
        ant.name = f"Antenna_{i}"
        ant.data.materials.append(metal)
        # Cross-arms on antenna
        for z_off in [0.4, 0.8, 1.2, 1.6]:
            bmesh_box(f"AntArm_{i}_{z_off:.1f}", (0.50, 0.02, 0.02), (ax, ay, roof_z + z_off), metal)
            bmesh_box(f"AntArmY_{i}_{z_off:.1f}", (0.02, 0.50, 0.02), (ax, ay, roof_z + z_off), metal)

    # === Satellite dish (large, on wing roof) ===
    wing_roof_z = BZ + wing_h + 0.05
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.40, location=(1.5, -0.8, wing_roof_z + 0.30))
    dish = bpy.context.active_object
    dish.name = "SatDish"
    dish.scale = (1, 1, 0.30)
    dish.data.materials.append(metal)
    bpy.ops.object.shade_smooth()
    # Dish feed
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.40,
                                        location=(1.5, -0.8, wing_roof_z + 0.50))
    bpy.context.active_object.data.materials.append(metal)

    # === Holographic displays (glowing panels around entrance) ===
    for j, (hx, hy) in enumerate([(main_w / 2 + 0.42, -0.60), (main_w / 2 + 0.42, 0.60)]):
        bmesh_box(f"HoloFrame_{j}", (0.06, 0.40, 0.60), (hx, hy, BZ + 1.20), metal)
        bmesh_box(f"HoloScreen_{j}", (0.04, 0.36, 0.54), (hx + 0.01, hy, BZ + 1.20), m['gold'])

    # Indoor holographic table (visible through glass)
    bmesh_box("HoloTable", (0.6, 0.4, 0.05), (0, 0, BZ + 0.80), metal)
    bmesh_box("HoloProjection", (0.40, 0.30, 0.35), (0, 0, BZ + 1.00), m['gold'])

    # === Server racks (visible through glass side) ===
    for i in range(3):
        sx = -0.6 + i * 0.45
        bmesh_box(f"Server_{i}", (0.30, 0.15, 1.20), (sx, main_d / 2 - 0.20, BZ + 0.60), m['iron'])
        # Blinking lights (small gold dots)
        for k in range(4):
            bmesh_box(f"SrvLight_{i}_{k}", (0.04, 0.02, 0.04),
                      (sx, main_d / 2 - 0.11, BZ + 0.30 + k * 0.25), m['gold'])

    # === Solar panels on main roof ===
    for i in range(3):
        bmesh_box(f"Solar_{i}", (0.70, 0.45, 0.03), (-0.8 + i * 0.80, 0, roof_z + 0.06), glass)
        bmesh_box(f"SolarFrame_{i}", (0.72, 0.47, 0.02), (-0.8 + i * 0.80, 0, roof_z + 0.04), metal)

    # === Perimeter security (modern fence with sensors) ===
    for i in range(10):
        fy = -2.2 + i * 0.48
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=1.2,
                                            location=(2.5, fy, BZ + 0.60))
        bpy.context.active_object.data.materials.append(metal)
    # Fence wires
    for z_off in [0.35, 0.60, 0.85, 1.10]:
        bmesh_box(f"SecWire_{z_off:.2f}", (0.02, 4.60, 0.012), (2.5, -0.3, BZ + z_off), metal)

    # Security sensors (on top of fence posts)
    for pos_y in [-2.2, 0, 2.2]:
        bmesh_box(f"Sensor_{pos_y:.1f}", (0.06, 0.06, 0.06), (2.5, pos_y, BZ + 1.25), m['gold'])

    # Landscaping hedges
    for y in [-1.8, 1.8]:
        bmesh_box(f"Hedge_{y:.1f}", (0.5, 0.25, 0.20), (main_w / 2 + 0.80, y, BZ + 0.10), m['ground'])


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


def build_barracks(materials, age='medieval'):
    """Build a Barracks with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
