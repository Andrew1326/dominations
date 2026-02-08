"""
Vikings nation Town Center — Norse/Scandinavian architecture per age.

Stone:         Nordic longhouse with turf roof, central fire pit, antler decor
Bronze:        Improved longhouse with stone foundation, ship carving on gable
Iron:          Viking chieftain's hall with dragon prows, shield wall, runic stone
Classical:     Viking ring fortress (Trelleborg) with 4 longhouses, palisade
Medieval:      Stave church great hall with multi-tiered roofs, dragon finials
Gunpowder:     Scandinavian fortress (Kronborg style) with star ramparts, copper spire
Enlightenment: Nordic Baroque palace with copper roof, ornate tower
Industrial:    Scandinavian civic building with clean lines, copper spire
Modern:        Scandinavian modernist with grass roof, wood and glass
Digital:       Nordic futuristic with organic glass, LED runes, green roof
"""

import bpy
import bmesh
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# ----------------------------------------------------------------
# helpers
# ----------------------------------------------------------------
def _dragon_prow(name, origin, scale_x, mat, flip=False):
    """Curved dragon-head prow on a gable end via mesh_from_pydata.
    A stylised S-curve neck with head and open jaw."""
    ox, oy, oz = origin
    s = -1.0 if flip else 1.0
    verts = [
        # neck base (thick)
        (ox,            oy + s * 0.00, oz + 0.00),
        (ox + 0.08,     oy + s * 0.00, oz + 0.00),
        # neck mid
        (ox + 0.06,     oy + s * 0.10, oz + 0.30),
        (ox + 0.14,     oy + s * 0.10, oz + 0.30),
        # neck upper curve
        (ox + 0.04,     oy + s * 0.05, oz + 0.55),
        (ox + 0.12,     oy + s * 0.05, oz + 0.55),
        # head back
        (ox + 0.02,     oy - s * 0.04, oz + 0.70),
        (ox + 0.14,     oy - s * 0.04, oz + 0.70),
        # snout tip
        (ox + 0.08,     oy - s * 0.14, oz + 0.62),
        # jaw
        (ox + 0.08,     oy - s * 0.12, oz + 0.56),
    ]
    faces = [
        (0, 1, 3, 2),   # neck lower
        (2, 3, 5, 4),   # neck upper
        (4, 5, 7, 6),   # head back
        (6, 7, 8),      # head top
        (7, 5, 9),      # jaw side
        (6, 8, 9),      # jaw other
    ]
    mesh_from_pydata(name, verts, faces, mat)


def _shield_row(prefix, start, end, z, count, mat_a, mat_b, radius=0.10):
    """Row of round shields along a line from start to end."""
    sx, sy = start
    ex, ey = end
    for i in range(count):
        t = i / max(count - 1, 1)
        px = sx + (ex - sx) * t
        py = sy + (ey - sy) * t
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=0.04,
                                            location=(px, py, z))
        sh = bpy.context.active_object
        sh.name = f"{prefix}_{i}"
        sh.data.materials.append(mat_a if i % 2 == 0 else mat_b)
        # face the shield outward (rotate to face along the line direction)
        angle = math.atan2(ey - sy, ex - sx)
        sh.rotation_euler = (math.radians(90), 0, angle + math.radians(90))


def _runic_stone(name, pos, h, mat):
    """Tall runestone slab."""
    ox, oy, oz = pos
    verts = [
        (ox - 0.08, oy - 0.04, oz),
        (ox + 0.08, oy - 0.04, oz),
        (ox + 0.08, oy + 0.04, oz),
        (ox - 0.08, oy + 0.04, oz),
        (ox - 0.06, oy - 0.03, oz + h),
        (ox + 0.06, oy - 0.03, oz + h),
        (ox + 0.06, oy + 0.03, oz + h),
        (ox - 0.06, oy + 0.03, oz + h),
        (ox,        oy,        oz + h + 0.08),  # pointed top
    ]
    faces = [
        (0, 1, 2, 3),
        (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
        (4, 5, 8), (5, 6, 8), (6, 7, 8), (7, 4, 8),
    ]
    mesh_from_pydata(name, verts, faces, mat)


def _longhouse_roof(name, length, width, height, origin, mat):
    """Steep pitched roof typical of Viking longhouses."""
    ox, oy, oz = origin
    hl = length / 2 + 0.10
    hw = width / 2 + 0.12
    verts = [
        (ox - hl, oy - hw, oz),
        (ox + hl, oy - hw, oz),
        (ox + hl, oy + hw, oz),
        (ox - hl, oy + hw, oz),
        (ox - hl, oy, oz + height),
        (ox + hl, oy, oz + height),
    ]
    faces = [
        (0, 1, 5, 4),  # right slope
        (2, 3, 4, 5),  # left slope
        (0, 4, 3),     # gable back
        (1, 2, 5),     # gable front
    ]
    obj = mesh_from_pydata(name, verts, faces, mat)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


# ============================================================
# STONE AGE -- Nordic longhouse with turf roof
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Central longhouse (rectangular timber hall) ===
    # Low stone/earth foundation ring
    bmesh_box("LHFound", (3.0, 1.6, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.04)

    # Timber frame walls (wattle and daub)
    wall_h = 1.2
    bmesh_box("WallR", (2.8, 0.12, wall_h), (0, -0.70, Z + 0.15 + wall_h / 2), m['wood'])
    bmesh_box("WallL", (2.8, 0.12, wall_h), (0, 0.70, Z + 0.15 + wall_h / 2), m['wood'])
    bmesh_box("WallF", (0.12, 1.40, wall_h), (1.40, 0, Z + 0.15 + wall_h / 2), m['wood'])
    bmesh_box("WallB", (0.12, 1.40, wall_h), (-1.40, 0, Z + 0.15 + wall_h / 2), m['wood'])

    # Steep turf/thatch roof (green)
    roof_z = Z + 0.15 + wall_h
    _longhouse_roof("TurfRoof", 2.8, 1.4, 1.1, (0, 0, roof_z), m['ground'])

    # Smoke hole at ridge
    bmesh_box("SmokeHole", (0.30, 0.20, 0.08), (0, 0, roof_z + 1.10), m['wood_dark'])

    # Interior support posts (visible through door)
    for x in [-0.9, -0.3, 0.3, 0.9]:
        for y_off in [-0.40, 0.40]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=wall_h + 0.3,
                                                location=(x, y_off, Z + 0.15 + (wall_h + 0.3) / 2))
            p = bpy.context.active_object
            p.name = f"Post_{x:.1f}_{y_off:.1f}"
            p.data.materials.append(m['wood_dark'])

    # Door opening -- animal skin flap
    bmesh_box("DoorFrame", (0.08, 0.50, 0.90), (1.41, 0, Z + 0.15 + 0.45), m['wood_dark'])
    sv = [(1.43, -0.22, Z + 1.20), (1.43, 0.22, Z + 1.20),
          (1.45, 0.18, Z + 0.30), (1.45, -0.18, Z + 0.35)]
    mesh_from_pydata("SkinFlap", sv, [(0, 1, 2, 3)], m['roof_edge'])
    m['roof_edge'].use_backface_culling = False

    # === Central fire pit ===
    bmesh_prism("FirePit", 0.30, 0.08, 8, (0, 0, Z + 0.06), m['stone_dark'])
    for angle_off in [0.2, 1.0, 2.0, 3.0]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.03, depth=0.35,
                                            location=(0, 0, Z + 0.12))
        log = bpy.context.active_object
        log.name = f"FireLog_{angle_off:.1f}"
        log.rotation_euler = (0.4, angle_off, 0)
        log.data.materials.append(m['wood_dark'])

    # === Antler decoration on gable ===
    for side, xs in [("F", 1.42), ("B", -1.42)]:
        # Two antler prongs as simple angled cylinders
        for dy, rot_y in [(-0.15, 0.4), (0.15, -0.4)]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.02, depth=0.45,
                                                location=(xs, dy, roof_z + 0.90))
            ant = bpy.context.active_object
            ant.name = f"Antler_{side}_{dy:.2f}"
            ant.rotation_euler = (0, rot_y, 0)
            ant.data.materials.append(m['stone_light'])

    # === Small storage hut ===
    bmesh_box("StorageWall", (0.80, 0.60, 0.70), (-1.8, 1.5, Z + 0.15 + 0.35), m['wood'])
    _longhouse_roof("StorageRoof", 0.80, 0.60, 0.50, (-1.8, 1.5, Z + 0.85), m['ground'])

    # === Drying rack (fish/meat) ===
    for dy in [-0.30, 0.30]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.03, depth=1.0,
                                            location=(2.0, dy, Z + 0.50))
        bpy.context.active_object.name = f"Rack_{dy:.1f}"
        bpy.context.active_object.data.materials.append(m['wood'])
    bmesh_box("RackBar", (0.04, 0.65, 0.04), (2.0, 0, Z + 1.00), m['wood_dark'])

    # === Stone ring (gathering area) ===
    for i in range(8):
        a = (2 * math.pi * i) / 8
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08,
                                              location=(-1.8, -1.2 + 0.50 * math.cos(a),
                                                        Z + 0.06))
        st = bpy.context.active_object
        st.name = f"GatherStone_{i}"
        st.scale = (1.2, 1, 0.7)
        st.data.materials.append(m['stone'])


# ============================================================
# BRONZE AGE -- Improved longhouse, stone foundation, ship gable
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Stone foundation platform ===
    bmesh_box("Platform", (4.0, 2.2, 0.20), (0, 0, Z + 0.10), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.20
    wall_h = 1.5

    # === Main longhouse -- wooden plank walls ===
    bmesh_box("WallR", (3.6, 0.14, wall_h), (0, -0.90, BZ + wall_h / 2), m['wood'])
    bmesh_box("WallL", (3.6, 0.14, wall_h), (0, 0.90, BZ + wall_h / 2), m['wood'])
    bmesh_box("WallF", (0.14, 1.80, wall_h), (1.80, 0, BZ + wall_h / 2), m['wood'])
    bmesh_box("WallB", (0.14, 1.80, wall_h), (-1.80, 0, BZ + wall_h / 2), m['wood'])

    # Wall plank detail (horizontal lines)
    for z_off in [0.3, 0.6, 0.9, 1.2]:
        bmesh_box(f"PlankR_{z_off:.1f}", (3.5, 0.02, 0.02), (0, -0.91, BZ + z_off), m['wood_dark'])
        bmesh_box(f"PlankL_{z_off:.1f}", (3.5, 0.02, 0.02), (0, 0.91, BZ + z_off), m['wood_dark'])

    # Stone foundation visible band
    bmesh_box("FoundBand", (3.7, 1.9, 0.08), (0, 0, BZ + 0.04), m['stone'], bevel=0.02)

    # Steep thatch roof
    roof_z = BZ + wall_h
    _longhouse_roof("ThatchRoof", 3.6, 1.8, 1.3, (0, 0, roof_z), m['roof'])

    # Ridge beam
    bmesh_box("Ridge", (3.8, 0.06, 0.06), (0, 0, roof_z + 1.30), m['wood_dark'])

    # === Bronze Age ship carving on front gable ===
    # Simplified ship shape carved on the gable end
    gx = 1.82
    sv = [
        (gx, -0.35, roof_z + 0.30),
        (gx, 0.35, roof_z + 0.30),
        (gx, 0.50, roof_z + 0.50),
        (gx, 0.20, roof_z + 0.65),
        (gx, -0.20, roof_z + 0.65),
        (gx, -0.50, roof_z + 0.50),
    ]
    mesh_from_pydata("ShipCarving", sv, [(0, 1, 2, 3, 4, 5)], m['gold'])

    # Gable cross beams
    for side in [1.82, -1.82]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=1.0,
                                            location=(side, 0, roof_z + 0.90))
        cb = bpy.context.active_object
        cb.name = f"GableBeam_{side:.1f}"
        cb.rotation_euler = (math.radians(90), 0, 0)
        cb.data.materials.append(m['wood_dark'])

    # === Support posts ===
    for x in [-1.2, -0.4, 0.4, 1.2]:
        for ys in [-0.55, 0.55]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.06, depth=wall_h + 0.4,
                                                location=(x, ys, BZ + (wall_h + 0.4) / 2))
            bpy.context.active_object.name = f"SPost_{x:.1f}_{ys:.1f}"
            bpy.context.active_object.data.materials.append(m['wood_dark'])

    # === Door ===
    bmesh_box("Door", (0.10, 0.55, 1.10), (1.81, 0, BZ + 0.55), m['door'])

    # === Storage pit (sunken) ===
    bmesh_prism("StoragePit", 0.35, 0.10, 8, (2.2, -1.2, Z + 0.05), m['stone_dark'])
    bmesh_box("PitCover", (0.55, 0.55, 0.04), (2.2, -1.2, Z + 0.12), m['wood'])

    # === Secondary shelter ===
    bmesh_box("Shelter", (1.0, 0.80, 0.90), (-2.2, 1.2, Z + 0.10 + 0.45), m['wood'])
    _longhouse_roof("ShelterRoof", 1.0, 0.80, 0.55, (-2.2, 1.2, Z + 1.00), m['roof'])

    # === Fire pit with stone ring ===
    bmesh_prism("FireRing", 0.25, 0.10, 10, (2.0, 1.0, Z + 0.05), m['stone'])

    # === Wooden fence section ===
    for i in range(6):
        bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.04, depth=0.80,
                                            location=(-2.5, -0.8 + i * 0.35, Z + 0.40))
        bpy.context.active_object.name = f"Fence_{i}"
        bpy.context.active_object.data.materials.append(m['wood'])
    bmesh_box("FenceRail", (0.04, 1.8, 0.04), (-2.5, -0.1, Z + 0.65), m['wood_dark'])


# ============================================================
# IRON AGE -- Viking chieftain's hall, dragon prows, shield wall
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Raised earth mound foundation ===
    bmesh_box("Mound", (4.6, 2.8, 0.20), (0, 0, Z + 0.10), m['stone_dark'], bevel=0.06)
    bmesh_box("Mound2", (4.2, 2.4, 0.12), (0, 0, Z + 0.26), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.32
    wall_h = 1.8

    # === Grand mead hall (large longhouse) ===
    bmesh_box("HallWallR", (4.0, 0.16, wall_h), (0, -1.05, BZ + wall_h / 2), m['wood'])
    bmesh_box("HallWallL", (4.0, 0.16, wall_h), (0, 1.05, BZ + wall_h / 2), m['wood'])
    bmesh_box("HallWallF", (0.16, 2.10, wall_h), (2.00, 0, BZ + wall_h / 2), m['wood'])
    bmesh_box("HallWallB", (0.16, 2.10, wall_h), (-2.00, 0, BZ + wall_h / 2), m['wood'])

    # Heavy timber beam detail
    for z_off in [0.4, 0.8, 1.2, 1.6]:
        bmesh_box(f"BeamR_{z_off:.1f}", (3.9, 0.03, 0.05), (0, -1.06, BZ + z_off), m['wood_dark'])
        bmesh_box(f"BeamL_{z_off:.1f}", (3.9, 0.03, 0.05), (0, 1.06, BZ + z_off), m['wood_dark'])

    # Steep thatched roof
    roof_z = BZ + wall_h
    _longhouse_roof("HallRoof", 4.0, 2.1, 1.5, (0, 0, roof_z), m['roof'])

    # Ridge beam
    bmesh_box("Ridge", (4.2, 0.08, 0.08), (0, 0, roof_z + 1.50), m['wood_dark'])

    # === Dragon-head prow carvings on both gable ends ===
    _dragon_prow("DragonF", (2.05, 0, roof_z + 1.20), 1.0, m['wood_dark'], flip=False)
    _dragon_prow("DragonB", (-2.20, 0, roof_z + 1.20), 1.0, m['wood_dark'], flip=True)

    # === Shield wall along front (row of round shields) ===
    _shield_row("ShieldF", (2.01, -0.80), (2.01, 0.80), BZ + 1.20, 8,
                m['banner'], m['roof'], radius=0.10)

    # === Shield wall along right side ===
    _shield_row("ShieldR", (-1.50, -1.06), (1.50, -1.06), BZ + 1.20, 10,
                m['banner'], m['roof'], radius=0.09)

    # === Grand carved door ===
    bmesh_box("DoorFrame", (0.12, 0.70, 1.40), (2.01, 0, BZ + 0.70), m['wood_dark'])
    bmesh_box("Door", (0.08, 0.60, 1.30), (2.02, 0, BZ + 0.65), m['door'])
    # Carved border on door
    bmesh_box("DoorTrim_T", (0.09, 0.65, 0.05), (2.03, 0, BZ + 1.33), m['gold'])
    bmesh_box("DoorTrim_B", (0.09, 0.65, 0.05), (2.03, 0, BZ + 0.05), m['gold'])

    # Interior support pillars
    for x in [-1.3, -0.5, 0.5, 1.3]:
        for ys in [-0.60, 0.60]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.07, depth=wall_h + 0.5,
                                                location=(x, ys, BZ + (wall_h + 0.5) / 2))
            bpy.context.active_object.name = f"Pillar_{x:.1f}_{ys:.1f}"
            bpy.context.active_object.data.materials.append(m['wood_dark'])

    # === Runic stone ===
    _runic_stone("RuneStone", (2.5, -1.5, Z + 0.06), 0.60, m['stone'])

    # === Fire pit (central in hall) ===
    bmesh_prism("FirePit", 0.35, 0.10, 10, (0, 0, BZ + 0.05), m['stone'])

    # === Banner on ridge ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.80,
                                        location=(0, 0, roof_z + 1.50 + 0.40))
    bpy.context.active_object.data.materials.append(m['wood'])
    bv = [(0.04, 0, roof_z + 2.10), (0.50, 0.03, roof_z + 2.05),
          (0.50, 0.02, roof_z + 2.35), (0.04, 0, roof_z + 2.33)]
    mesh_from_pydata("Banner", bv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False

    # === Weapon rack ===
    bmesh_box("WeaponRack", (0.08, 0.60, 0.80), (-2.3, -1.0, Z + 0.10 + 0.40), m['wood'])
    for wy in [-0.20, 0.0, 0.20]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.02, depth=0.70,
                                            location=(-2.3, -1.0 + wy, Z + 0.80))
        bpy.context.active_object.name = f"Spear_{wy:.1f}"
        bpy.context.active_object.data.materials.append(m['iron'])


# ============================================================
# CLASSICAL AGE -- Viking ring fortress (Trelleborg style)
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Circular palisade wall ===
    pal_r = 2.3
    n_logs = 36
    for i in range(n_logs):
        a = (2 * math.pi * i) / n_logs
        # Leave gap for gate at angle ~0
        if 0.08 < (a % (2 * math.pi)) < 0.28:
            continue
        px, py = pal_r * math.cos(a), pal_r * math.sin(a)
        h = 1.6
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.07, depth=h,
                                            location=(px, py, Z + 0.06 + h / 2))
        log = bpy.context.active_object
        log.name = f"Pal_{i}"
        log.data.materials.append(m['wood'])

    # Gate posts and lintel
    gx = pal_r
    bmesh_box("GatePostL", (0.14, 0.14, 1.8), (gx + 0.05, -0.22, Z + 0.06 + 0.90), m['wood_dark'])
    bmesh_box("GatePostR", (0.14, 0.14, 1.8), (gx + 0.05, 0.22, Z + 0.06 + 0.90), m['wood_dark'])
    bmesh_box("GateLintel", (0.14, 0.58, 0.10), (gx + 0.05, 0, Z + 0.06 + 1.85), m['wood_dark'])

    # Circular earth rampart inside palisade
    bmesh_prism("Rampart", pal_r - 0.15, 0.12, 24, (0, 0, Z + 0.06), m['stone_dark'])

    BZ = Z + 0.18

    # === 4 longhouses arranged in a square inside the ring ===
    lh_positions = [
        (0.7, 0, 0),               # east (near gate)
        (-0.7, 0, 0),              # west
        (0, 0.7, math.radians(90)), # north
        (0, -0.7, math.radians(90)), # south
    ]
    for idx, (lx, ly, rot) in enumerate(lh_positions):
        lbl = ["E", "W", "N", "S"][idx]
        # Wall
        if rot == 0:
            bmesh_box(f"LH_{lbl}", (1.4, 0.70, 1.0), (lx, ly, BZ + 0.50), m['wood'])
            _longhouse_roof(f"LHRoof_{lbl}", 1.4, 0.70, 0.65, (lx, ly, BZ + 1.0), m['roof'])
        else:
            bmesh_box(f"LH_{lbl}", (0.70, 1.4, 1.0), (lx, ly, BZ + 0.50), m['wood'])
            # Rotated roof
            rv = [
                (lx - 0.47, ly - 0.82, BZ + 1.0),
                (lx + 0.47, ly - 0.82, BZ + 1.0),
                (lx + 0.47, ly + 0.82, BZ + 1.0),
                (lx - 0.47, ly + 0.82, BZ + 1.0),
                (lx, ly - 0.82, BZ + 1.65),
                (lx, ly + 0.82, BZ + 1.65),
            ]
            rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
            obj = mesh_from_pydata(f"LHRoof_{lbl}", rv, rf, m['roof'])
            for p in obj.data.polygons:
                p.use_smooth = True

        # Doors on longhouses (facing center)
        if lbl == "E":
            bmesh_box(f"LHDoor_{lbl}", (0.06, 0.35, 0.70), (lx - 0.71, ly, BZ + 0.35), m['door'])
        elif lbl == "W":
            bmesh_box(f"LHDoor_{lbl}", (0.06, 0.35, 0.70), (lx + 0.71, ly, BZ + 0.35), m['door'])
        elif lbl == "N":
            bmesh_box(f"LHDoor_{lbl}", (0.35, 0.06, 0.70), (lx, ly - 0.71, BZ + 0.35), m['door'])
        elif lbl == "S":
            bmesh_box(f"LHDoor_{lbl}", (0.35, 0.06, 0.70), (lx, ly + 0.71, BZ + 0.35), m['door'])

    # === Central flagpole ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=2.5,
                                        location=(0, 0, BZ + 1.25))
    bpy.context.active_object.name = "Flagpole"
    bpy.context.active_object.data.materials.append(m['wood_dark'])
    # Banner
    fv = [(0.05, 0, BZ + 2.30), (0.55, 0.03, BZ + 2.25),
          (0.55, 0.02, BZ + 2.55), (0.05, 0, BZ + 2.53)]
    mesh_from_pydata("Banner", fv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False

    # === Shield decorations on gate ===
    for ys in [-0.15, 0.15]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.10, depth=0.04,
                                            location=(gx + 0.07, ys, Z + 0.06 + 1.50))
        sh = bpy.context.active_object
        sh.name = f"GateShield_{ys:.1f}"
        sh.rotation_euler = (0, math.radians(90), 0)
        sh.data.materials.append(m['banner'])

    # === Runic stones at entrance ===
    _runic_stone("RuneL", (gx + 0.40, -0.50, Z + 0.06), 0.55, m['stone'])
    _runic_stone("RuneR", (gx + 0.40, 0.50, Z + 0.06), 0.55, m['stone'])

    # === Watchtower (wooden, near gate) ===
    TX, TY = gx - 0.30, -1.60
    for cx, cy in [(TX - 0.18, TY - 0.18), (TX - 0.18, TY + 0.18),
                   (TX + 0.18, TY - 0.18), (TX + 0.18, TY + 0.18)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=2.4,
                                            location=(cx, cy, Z + 0.06 + 1.20))
        bpy.context.active_object.name = f"TWPole_{cx:.2f}"
        bpy.context.active_object.data.materials.append(m['wood'])
    bmesh_box("TWPlat", (0.50, 0.50, 0.05), (TX, TY, Z + 0.06 + 2.20), m['wood'])
    bmesh_cone("TWRoof", 0.40, 0.50, 8, (TX, TY, Z + 0.06 + 2.25), m['roof'])


# ============================================================
# MEDIEVAL AGE -- Stave church great hall, multi-tiered roofs
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Heavy stone foundation ===
    bmesh_box("Found", (4.2, 3.4, 0.20), (0, 0, Z + 0.10), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.20

    # === Main hall (stave construction -- vertical timber) ===
    hall_w, hall_d = 3.0, 2.2
    wall_h = 2.2
    bmesh_box("HallBase", (hall_w, hall_d, wall_h), (0, 0, BZ + wall_h / 2), m['wood'], bevel=0.02)

    # Vertical timber stave lines on walls
    for x in [-1.2, -0.8, -0.4, 0.0, 0.4, 0.8, 1.2]:
        bmesh_box(f"StaveF_{x:.1f}", (0.05, 0.03, wall_h), (x, -hall_d / 2 - 0.01, BZ + wall_h / 2), m['wood_dark'])
        bmesh_box(f"StaveB_{x:.1f}", (0.05, 0.03, wall_h), (x, hall_d / 2 + 0.01, BZ + wall_h / 2), m['wood_dark'])
    for y in [-0.7, -0.3, 0.3, 0.7]:
        bmesh_box(f"StaveR_{y:.1f}", (0.03, 0.05, wall_h), (hall_w / 2 + 0.01, y, BZ + wall_h / 2), m['wood_dark'])
        bmesh_box(f"StaveL_{y:.1f}", (0.03, 0.05, wall_h), (-hall_w / 2 - 0.01, y, BZ + wall_h / 2), m['wood_dark'])

    # === First tier roof (lowest, widest) ===
    r1_z = BZ + wall_h
    _longhouse_roof("Roof1", hall_w, hall_d, 1.2, (0, 0, r1_z), m['roof'])

    # === Second tier (narrower on top) ===
    t2_w, t2_d, t2_h = 2.0, 1.4, 1.0
    bmesh_box("Tier2", (t2_w, t2_d, t2_h), (0, 0, r1_z + 0.80 + t2_h / 2), m['wood'])
    r2_z = r1_z + 0.80 + t2_h
    _longhouse_roof("Roof2", t2_w, t2_d, 0.90, (0, 0, r2_z), m['roof'])

    # === Third tier (tower top) ===
    t3_w, t3_d, t3_h = 1.0, 0.8, 0.70
    bmesh_box("Tier3", (t3_w, t3_d, t3_h), (0, 0, r2_z + 0.60 + t3_h / 2), m['wood'])
    r3_z = r2_z + 0.60 + t3_h
    _longhouse_roof("Roof3", t3_w, t3_d, 0.70, (0, 0, r3_z), m['roof_edge'])

    # === Dragon finials on all roof ridges ===
    _dragon_prow("Dragon1F", (hall_w / 2 + 0.10, 0, r1_z + 0.90), 1.0, m['wood_dark'], flip=False)
    _dragon_prow("Dragon1B", (-hall_w / 2 - 0.25, 0, r1_z + 0.90), 1.0, m['wood_dark'], flip=True)
    _dragon_prow("Dragon2F", (t2_w / 2 + 0.10, 0, r2_z + 0.60), 1.0, m['wood_dark'], flip=False)
    _dragon_prow("Dragon2B", (-t2_w / 2 - 0.25, 0, r2_z + 0.60), 1.0, m['wood_dark'], flip=True)
    _dragon_prow("Dragon3F", (t3_w / 2 + 0.10, 0, r3_z + 0.40), 1.0, m['wood_dark'], flip=False)
    _dragon_prow("Dragon3B", (-t3_w / 2 - 0.25, 0, r3_z + 0.40), 1.0, m['wood_dark'], flip=True)

    # === Carved portal (front entrance) ===
    bmesh_box("PortalFrame", (0.14, 0.90, 1.70), (hall_w / 2 + 0.01, 0, BZ + 0.85), m['wood_dark'])
    bmesh_box("Door", (0.10, 0.70, 1.50), (hall_w / 2 + 0.02, 0, BZ + 0.75), m['door'])
    # Carved arch over door
    bmesh_box("PortalArch", (0.15, 0.95, 0.08), (hall_w / 2 + 0.02, 0, BZ + 1.72), m['gold'])
    # Side carvings (interlace suggestion)
    for ys in [-0.42, 0.42]:
        bmesh_box(f"PortalCarve_{ys:.1f}", (0.04, 0.06, 1.40), (hall_w / 2 + 0.03, ys, BZ + 0.90), m['gold'])

    # === Wooden tower (bell/lookout) ===
    TX, TY = -1.8, -1.4
    tower_h = 3.5
    bmesh_box("Tower", (0.80, 0.80, tower_h), (TX, TY, BZ + tower_h / 2), m['wood'], bevel=0.02)
    # Vertical staves on tower
    for dx in [-0.30, 0, 0.30]:
        bmesh_box(f"TStave_{dx:.1f}", (0.04, 0.03, tower_h), (TX + dx, TY - 0.41, BZ + tower_h / 2), m['wood_dark'])
    bmesh_cone("TowerRoof", 0.55, 1.0, 8, (TX, TY, BZ + tower_h), m['roof'])
    _dragon_prow("DragonTower", (TX, TY, BZ + tower_h + 0.70), 1.0, m['wood_dark'])

    # === Steps ===
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.22, 1.2, 0.06), (hall_w / 2 + 0.30 + i * 0.22, 0, BZ - 0.04 - i * 0.05), m['stone_dark'])

    # === Cross/interlace on gable (gold trim) ===
    bmesh_box("GableCross_V", (0.04, 0.04, 0.60), (hall_w / 2 + 0.02, 0, r1_z + 0.50), m['gold'])
    bmesh_box("GableCross_H", (0.04, 0.30, 0.04), (hall_w / 2 + 0.02, 0, r1_z + 0.60), m['gold'])

    # === Shield decoration on front wall ===
    _shield_row("ShieldFront", (hall_w / 2 + 0.02, -0.80), (hall_w / 2 + 0.02, 0.80), BZ + 1.80, 6,
                m['banner'], m['roof_edge'], radius=0.08)

    # === Banner ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.70,
                                        location=(0, 0, r3_z + 0.70 + 0.35))
    bpy.context.active_object.data.materials.append(m['wood'])
    fv = [(0.04, 0, r3_z + 1.25), (0.50, 0.03, r3_z + 1.20),
          (0.50, 0.02, r3_z + 1.50), (0.04, 0, r3_z + 1.48)]
    mesh_from_pydata("Banner", fv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# GUNPOWDER AGE -- Scandinavian fortress (Kronborg style)
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (6.0, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Star-shaped ramparts (earthwork) ===
    # Four diamond bastions at corners + connecting walls
    bmesh_box("RampartBase", (5.2, 5.2, 0.25), (0, 0, Z + 0.125), m['stone_dark'], bevel=0.06)

    BZ = Z + 0.25
    hw = 2.2
    WALL_H = 2.4
    wt = 0.24

    # Fortress walls
    bmesh_box("WallF", (wt, hw * 2 - 0.3, WALL_H), (hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallB", (wt, hw * 2 - 0.3, WALL_H), (-hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallR", (hw * 2 - 0.3, wt, WALL_H), (0, -hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallL", (hw * 2 - 0.3, wt, WALL_H), (0, hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)

    # Battlements
    for i in range(10):
        y = -1.8 + i * 0.40
        bmesh_box(f"MF_{i}", (0.10, 0.14, 0.20), (hw + 0.06, y, BZ + WALL_H + 0.10), m['stone_trim'], bevel=0.01)
        bmesh_box(f"MB_{i}", (0.10, 0.14, 0.20), (-hw - 0.06, y, BZ + WALL_H + 0.10), m['stone_trim'], bevel=0.01)
    for i in range(10):
        x = -1.8 + i * 0.40
        bmesh_box(f"MR_{i}", (0.14, 0.10, 0.20), (x, -hw - 0.06, BZ + WALL_H + 0.10), m['stone_trim'], bevel=0.01)
        bmesh_box(f"ML_{i}", (0.14, 0.10, 0.20), (x, hw + 0.06, BZ + WALL_H + 0.10), m['stone_trim'], bevel=0.01)

    # === Angular bastions (star fort) ===
    bastion_h = WALL_H + 0.3
    for xs, ys, lbl in [(-1, -1, "BL"), (-1, 1, "FL"), (1, -1, "BR"), (1, 1, "FR")]:
        bx, by = xs * hw, ys * hw
        bmesh_prism(f"Bastion_{lbl}", 0.50, bastion_h, 6, (bx, by, BZ), m['stone_upper'], bevel=0.02)
        bmesh_prism(f"BTop_{lbl}", 0.55, 0.08, 6, (bx, by, BZ + bastion_h), m['stone_trim'])
        # Cannon slit
        bmesh_box(f"CSlit_{lbl}", (0.04, 0.12, 0.08),
                  (bx + xs * 0.52, by + ys * 0.52, BZ + 1.0), m['window'])

    # === Cannon platforms on bastions ===
    for xs, ys, lbl in [(1, 1, "FR"), (1, -1, "BR")]:
        bx, by = xs * hw, ys * hw
        bmesh_box(f"CannonBase_{lbl}", (0.30, 0.15, 0.10), (bx + xs * 0.30, by + ys * 0.30, BZ + bastion_h + 0.05), m['iron'])
        # Cannon barrel
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=0.40,
                                            location=(bx + xs * 0.50, by + ys * 0.50, BZ + bastion_h + 0.15))
        cn = bpy.context.active_object
        cn.name = f"Cannon_{lbl}"
        cn.rotation_euler = (0, math.radians(80), math.atan2(ys, xs))
        cn.data.materials.append(m['iron'])

    # === Central stone tower with copper spire ===
    tower_w = 1.4
    tower_h = 4.0
    bmesh_box("Tower", (tower_w, tower_w, tower_h), (0, 0, BZ + tower_h / 2), m['stone'], bevel=0.03)

    # Stone bands
    for tz in [BZ + 1.0, BZ + 2.0, BZ + 3.0, BZ + tower_h]:
        bmesh_box(f"TBand_{tz:.1f}", (tower_w + 0.06, tower_w + 0.06, 0.08), (0, 0, tz), m['stone_trim'], bevel=0.02)

    # Tower windows (Kronborg style -- tall narrow)
    for y in [-0.35, 0.35]:
        for kz in [BZ + 1.3, BZ + 2.5, BZ + 3.5]:
            bmesh_box(f"TWin_{y:.1f}_{kz:.1f}", (0.07, 0.14, 0.45), (tower_w / 2 + 0.01, y, kz), m['window'])

    # Copper spire (green-tinted -- using roof_edge for patina)
    bmesh_cone("CopperSpire", 0.60, 2.0, 8, (0, 0, BZ + tower_h), m['roof_edge'])
    # Gold orb on top
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0, 0, BZ + tower_h + 2.00))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # === Palace wing (lower) ===
    wing_w, wing_d, wing_h = 2.0, 1.6, 2.0
    bmesh_box("Wing", (wing_w, wing_d, wing_h), (0, 0, BZ + wing_h / 2), m['stone'], bevel=0.02)
    pyramid_roof("WingRoof", w=wing_w - 0.2, d=wing_d - 0.2, h=0.6, overhang=0.12,
                 origin=(0, 0, BZ + wing_h + 0.04), material=m['roof'])

    # === Gate ===
    gate_x = hw + wt / 2
    bmesh_box("Gate", (0.10, 0.70, 1.50), (gate_x + 0.01, 0, BZ + 0.75), m['door'])
    bmesh_box("GateFrame", (0.14, 0.85, 0.10), (gate_x + 0.02, 0, BZ + 1.54), m['stone_trim'], bevel=0.02)

    # Steps
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.22, 1.4, 0.06), (gate_x + 0.40 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_dark'])

    # === Banner ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.80,
                                        location=(0, 0, BZ + tower_h + 2.10 + 0.40))
    bpy.context.active_object.data.materials.append(m['wood'])
    fv = [(0.04, 0, BZ + tower_h + 2.70), (0.50, 0.03, BZ + tower_h + 2.65),
          (0.50, 0.02, BZ + tower_h + 2.95), (0.04, 0, BZ + tower_h + 2.93)]
    mesh_from_pydata("Banner", fv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# ENLIGHTENMENT AGE -- Nordic Baroque palace
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (6.5, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation ===
    bmesh_box("Found", (6.0, 5.0, 0.20), (0, 0, Z + 0.10), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.20

    # === Symmetrical brick palace (main block) ===
    main_w, main_d = 3.4, 2.4
    main_h = 3.2
    bmesh_box("Main", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone'], bevel=0.03)

    # Moldings
    bmesh_box("BaseMold", (main_w + 0.06, main_d + 0.06, 0.10), (0, 0, BZ + 0.05), m['stone_trim'], bevel=0.02)
    bmesh_box("MidMold", (main_w + 0.06, main_d + 0.06, 0.06), (0, 0, BZ + 1.4), m['stone_trim'], bevel=0.01)
    bmesh_box("Cornice", (main_w + 0.08, main_d + 0.08, 0.10), (0, 0, BZ + main_h), m['stone_trim'], bevel=0.03)

    # === Copper roof (hipped, using roof_edge for patina) ===
    pyramid_roof("CopperRoof", w=main_w - 0.2, d=main_d - 0.2, h=1.2, overhang=0.15,
                 origin=(0, 0, BZ + main_h + 0.04), material=m['roof_edge'])

    # === Symmetrical wings ===
    wing_w, wing_d, wing_h = 1.4, 1.8, 2.6
    for ys, lbl in [(-2.0, "R"), (2.0, "L")]:
        bmesh_box(f"Wing_{lbl}", (wing_w, wing_d, wing_h), (0.2, ys, BZ + wing_h / 2), m['stone'], bevel=0.02)
        bmesh_box(f"WCornice_{lbl}", (wing_w + 0.06, wing_d + 0.06, 0.08), (0.2, ys, BZ + wing_h), m['stone_trim'], bevel=0.02)
        pyramid_roof(f"WRoof_{lbl}", w=wing_w - 0.2, d=wing_d - 0.2, h=0.60, overhang=0.10,
                     origin=(0.2, ys, BZ + wing_h + 0.04), material=m['roof_edge'])
        # Wing windows (2 rows x 3 cols)
        for row, z_off in [(0.4, 0), (1.4, 1)]:
            for wy in [-0.45, 0, 0.45]:
                bmesh_box(f"WWin_{lbl}_{row:.1f}_{wy:.1f}", (0.07, 0.18, 0.50),
                          (0.2 + wing_w / 2 + 0.01, ys + wy, BZ + row + 0.10), m['window'])

    # Main windows (5 cols x 2 rows)
    for i, y in enumerate([-0.80, -0.40, 0, 0.40, 0.80]):
        for z_off, h in [(0.5, 0.50), (1.8, 0.60)]:
            bmesh_box(f"MWin_{i}_{z_off}", (0.07, 0.20, h), (main_w / 2 + 0.01, y, BZ + z_off), m['window'])
            bmesh_box(f"MWinH_{i}_{z_off}", (0.08, 0.24, 0.04), (main_w / 2 + 0.02, y, BZ + z_off + h / 2 + 0.02), m['stone_trim'])

    # === Portico with columns ===
    for y in [-0.40, 0.40]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.10, depth=2.4,
                                            location=(main_w / 2 + 0.45, y, BZ + 1.20))
        c = bpy.context.active_object
        c.name = f"PorCol_{y:.1f}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        bmesh_box(f"PorCap_{y:.1f}", (0.24, 0.24, 0.06), (main_w / 2 + 0.45, y, BZ + 2.44), m['stone_trim'])

    # Pediment
    pv = [(main_w / 2 + 0.50, -0.55, BZ + 2.46), (main_w / 2 + 0.50, 0.55, BZ + 2.46),
          (main_w / 2 + 0.50, 0, BZ + 2.80)]
    mesh_from_pydata("Pediment", pv, [(0, 1, 2)], m['stone_light'])
    bmesh_box("PorRoof", (0.45, 1.2, 0.06), (main_w / 2 + 0.45, 0, BZ + 2.47), m['stone_trim'])

    # Door
    bmesh_box("Door", (0.08, 0.55, 1.40), (main_w / 2 + 0.01, 0, BZ + 0.70), m['door'])

    # === Ornate tower (central, taller) ===
    TX, TY = 0, 0
    tower_base = BZ + main_h + 0.10
    tower_w_t = 0.90
    tower_h = 2.5
    bmesh_box("Tower", (tower_w_t, tower_w_t, tower_h), (TX, TY, tower_base + tower_h / 2), m['stone'], bevel=0.02)
    bmesh_box("TCornice", (tower_w_t + 0.08, tower_w_t + 0.08, 0.08), (TX, TY, tower_base + tower_h), m['stone_trim'], bevel=0.02)

    # Tower windows
    for y_t in [-0.20, 0.20]:
        bmesh_box(f"TWin_{y_t:.1f}", (0.06, 0.14, 0.40), (TX + tower_w_t / 2 + 0.01, TY + y_t, tower_base + 1.2), m['window'])

    # Copper spire
    bmesh_cone("Spire", 0.40, 1.5, 8, (TX, TY, tower_base + tower_h), m['roof_edge'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(TX, TY, tower_base + tower_h + 1.50))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # === Formal garden suggestion (hedges) ===
    for gy in [-1.5, -0.5, 0.5, 1.5]:
        bmesh_box(f"Hedge_{gy:.1f}", (0.50, 0.25, 0.18), (main_w / 2 + 1.20, gy, Z + 0.09), m['ground'])

    # Steps
    for i in range(6):
        bmesh_box(f"Step_{i}", (0.20, 1.8, 0.06), (main_w / 2 + 0.65 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_light'])


# ============================================================
# INDUSTRIAL AGE -- Scandinavian brick civic building
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (6.5, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.15
    bmesh_box("Found", (6.0, 5.0, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.04)

    # === Main building (clean Scandinavian brick) ===
    main_w, main_d = 4.0, 3.0
    main_h = 3.5
    bmesh_box("Main", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone'], bevel=0.02)

    # Clean horizontal banding (brick courses)
    for z in [BZ + 0.8, BZ + 1.6, BZ + 2.4, BZ + 3.2]:
        bmesh_box(f"Band_{z:.1f}", (main_w + 0.02, main_d + 0.02, 0.04), (0, 0, z), m['stone_trim'])

    # === Large windows (functional design, tall) ===
    for row, z_off in enumerate([0.4, 1.3, 2.2]):
        for y in [-1.0, -0.50, 0, 0.50, 1.0]:
            h = 0.55 if row < 2 else 0.45
            bmesh_box(f"Win_{row}_{y:.1f}", (0.07, 0.22, h), (main_w / 2 + 0.01, y, BZ + z_off + 0.10), m['window'])
            bmesh_box(f"WinF_{row}_{y:.1f}", (0.08, 0.24, 0.03), (main_w / 2 + 0.02, y, BZ + z_off + h / 2 + 0.12), m['win_frame'])

    # Side windows
    for row in range(2):
        for x in [-1.2, -0.4, 0.4, 1.2]:
            bmesh_box(f"SWin_{row}_{x:.1f}", (0.22, 0.07, 0.50),
                      (x, -main_d / 2 - 0.01, BZ + 0.5 + row * 1.0), m['window'])

    # Flat roof with slight copper parapet
    bmesh_box("Roof", (main_w + 0.08, main_d + 0.08, 0.10), (0, 0, BZ + main_h + 0.05), m['stone_dark'])
    bmesh_box("Parapet", (main_w + 0.12, main_d + 0.12, 0.15), (0, 0, BZ + main_h + 0.175), m['roof_edge'])

    # === Copper spire tower (functional, clean) ===
    TX, TY = main_w / 2 - 0.6, -main_d / 2 + 0.5
    tower_base = BZ + main_h + 0.10
    tower_w = 0.80
    tower_h = 2.8
    bmesh_box("Tower", (tower_w, tower_w, tower_h), (TX, TY, tower_base + tower_h / 2), m['stone'], bevel=0.02)
    bmesh_box("TCornice", (tower_w + 0.08, tower_w + 0.08, 0.08), (TX, TY, tower_base + tower_h), m['stone_trim'], bevel=0.02)

    # Tower windows
    for yt in [-0.18, 0.18]:
        bmesh_box(f"TWin_{yt:.1f}", (0.06, 0.12, 0.40), (TX + tower_w / 2 + 0.01, TY + yt, tower_base + 1.5), m['window'])

    # Clock face
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.22, depth=0.04,
                                        location=(TX + tower_w / 2 + 0.02, TY, tower_base + 2.2))
    clock = bpy.context.active_object
    clock.name = "Clock"
    clock.rotation_euler = (0, math.radians(90), 0)
    clock.data.materials.append(m['gold'])

    # Copper spire
    bmesh_cone("CopperSpire", 0.30, 1.2, 8, (TX, TY, tower_base + tower_h), m['roof_edge'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(TX, TY, tower_base + tower_h + 1.20))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # === Entrance portico (clean lines) ===
    bmesh_box("Portico", (0.60, 1.8, 2.2), (main_w / 2 + 0.30, 0, BZ + 1.10), m['stone'], bevel=0.02)
    bmesh_box("PorTop", (0.65, 1.9, 0.08), (main_w / 2 + 0.30, 0, BZ + 2.24), m['stone_trim'], bevel=0.02)

    # Columns
    for y in [-0.55, 0.55]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=2.0,
                                            location=(main_w / 2 + 0.60, y, BZ + 1.10))
        c = bpy.context.active_object
        c.name = f"PorCol_{y:.1f}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()

    # Door
    bmesh_box("Door", (0.08, 0.80, 1.70), (main_w / 2 + 0.01, 0, BZ + 0.85), m['door'])

    # Steps
    for i in range(6):
        bmesh_box(f"Step_{i}", (0.22, 2.0, 0.06), (main_w / 2 + 0.75 + i * 0.22, 0, BZ - 0.04 - i * 0.05), m['stone_dark'])

    # === Chimneys (industrial) ===
    for cy in [-1.0, 1.0]:
        bmesh_box(f"Chimney_{cy:.1f}", (0.25, 0.25, 1.5), (-main_w / 2 + 0.4, cy, BZ + main_h + 0.75), m['stone'], bevel=0.01)
        bmesh_box(f"ChimTop_{cy:.1f}", (0.30, 0.30, 0.08), (-main_w / 2 + 0.4, cy, BZ + main_h + 1.54), m['stone_trim'])

    # === Iron fence ===
    for i in range(14):
        fy = -1.8 + i * 0.27
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.55,
                                            location=(main_w / 2 + 1.10, fy, BZ + 0.125))
        bpy.context.active_object.data.materials.append(m['iron'])


# ============================================================
# MODERN AGE -- Scandinavian modernist, grass roof, wood/glass
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (7.0, 6.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.10
    bmesh_box("Found", (6.5, 5.5, 0.10), (0, 0, Z + 0.05), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Main building (clean wood and glass) ===
    main_w, main_d = 3.6, 2.8
    main_h = 3.0
    # Wooden cladding
    bmesh_box("Main", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['wood'], bevel=0.02)

    # === Grass roof (green) -- living roof ===
    bmesh_box("GrassRoof", (main_w + 0.15, main_d + 0.15, 0.18), (0, 0, BZ + main_h + 0.09), m['ground'])
    # Slight slope on roof (front to back)
    rv = [
        (-main_w / 2 - 0.10, -main_d / 2 - 0.10, BZ + main_h + 0.18),
        (main_w / 2 + 0.10, -main_d / 2 - 0.10, BZ + main_h + 0.18),
        (main_w / 2 + 0.10, main_d / 2 + 0.10, BZ + main_h + 0.18),
        (-main_w / 2 - 0.10, main_d / 2 + 0.10, BZ + main_h + 0.18),
        (-main_w / 2 - 0.10, -main_d / 2 - 0.10, BZ + main_h + 0.35),
        (main_w / 2 + 0.10, -main_d / 2 - 0.10, BZ + main_h + 0.35),
    ]
    rf = [(0, 3, 2, 1), (0, 1, 5, 4), (4, 5, 2, 3)]
    mesh_from_pydata("GrassSlope", rv, rf, m['ground'])

    # === Large glass front wall ===
    bmesh_box("GlassFront", (0.06, main_d - 0.4, main_h - 0.3), (main_w / 2 + 0.01, 0, BZ + main_h / 2 + 0.1), glass)

    # Wood frame mullions
    for y in [-0.9, -0.3, 0.3, 0.9]:
        bmesh_box(f"Mull_{y:.1f}", (0.04, 0.04, main_h - 0.4), (main_w / 2 + 0.02, y, BZ + main_h / 2 + 0.1), m['wood_dark'])
    for z in [BZ + 1.0, BZ + 2.0]:
        bmesh_box(f"HMull_{z:.1f}", (0.04, main_d - 0.5, 0.04), (main_w / 2 + 0.02, 0, z), m['wood_dark'])

    # === Side windows (wood-framed) ===
    for x in [-1.2, -0.4, 0.4, 1.2]:
        bmesh_box(f"SWin_{x:.1f}", (0.30, 0.06, 0.80), (x, -main_d / 2 - 0.01, BZ + 1.8), glass)
        bmesh_box(f"SWinF_{x:.1f}", (0.32, 0.03, 0.04), (x, -main_d / 2 - 0.02, BZ + 2.22), m['wood_dark'])

    # === Wood-clad lower wing ===
    wing_w, wing_d, wing_h = 2.5, 2.0, 2.0
    bmesh_box("Wing", (wing_w, wing_d, wing_h), (1.5, 0, BZ + wing_h / 2), m['wood'])

    # Wing grass roof
    bmesh_box("WingGrass", (wing_w + 0.10, wing_d + 0.10, 0.15), (1.5, 0, BZ + wing_h + 0.075), m['ground'])

    # Wing glass wall
    bmesh_box("WGlass", (0.06, wing_d - 0.3, wing_h - 0.3), (1.5 + wing_w / 2 + 0.01, 0, BZ + wing_h / 2 + 0.1), glass)
    for wy in [-0.5, 0.0, 0.5]:
        bmesh_box(f"WMull_{wy:.1f}", (0.04, 0.04, wing_h - 0.4), (1.5 + wing_w / 2 + 0.02, wy, BZ + wing_h / 2 + 0.1), m['wood_dark'])

    # === Entrance (recessed, wood door) ===
    bmesh_box("Canopy", (0.80, 2.0, 0.06), (1.5 + wing_w / 2 + 0.40, 0, BZ + 2.30), m['wood_dark'])
    # Canopy supports
    for y in [-0.80, 0.80]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=2.20,
                                            location=(1.5 + wing_w / 2 + 0.40, y, BZ + 1.20))
        bpy.context.active_object.data.materials.append(m['wood_dark'])

    bmesh_box("Door", (0.06, 1.20, 2.10), (1.5 + wing_w / 2 + 0.01, 0, BZ + 1.05), m['door'])

    # === Nature integration -- planter boxes ===
    for gy in [-1.5, -0.5, 0.5, 1.5]:
        bmesh_box(f"Planter_{gy:.1f}", (0.40, 0.25, 0.25), (main_w / 2 + 0.80, gy, Z + 0.125), m['wood'])
        bmesh_box(f"Plant_{gy:.1f}", (0.35, 0.20, 0.10), (main_w / 2 + 0.80, gy, Z + 0.30), m['ground'])

    # === Wooden deck/pathway ===
    bmesh_box("Deck", (2.0, 3.0, 0.06), (main_w / 2 + 1.50, 0, Z + 0.08), m['wood'])

    # === Small birch trees suggestion ===
    for tx, ty in [(-2.5, -2.0), (-2.5, 2.0), (3.0, -2.2)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=1.5,
                                            location=(tx, ty, Z + 0.75))
        bpy.context.active_object.name = f"Trunk_{tx:.1f}_{ty:.1f}"
        bpy.context.active_object.data.materials.append(m['stone_light'])
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.30, location=(tx, ty, Z + 1.60))
        tree = bpy.context.active_object
        tree.name = f"Canopy_{tx:.1f}_{ty:.1f}"
        tree.scale = (1, 1, 0.7)
        tree.data.materials.append(m['ground'])

    # Flag
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=1.5,
                                        location=(2.0, 1.3, BZ + main_h + 0.35 + 0.75))
    bpy.context.active_object.data.materials.append(metal)
    fv = [(2.03, 1.3, BZ + main_h + 1.30), (2.50, 1.33, BZ + main_h + 1.25),
          (2.50, 1.32, BZ + main_h + 1.55), (2.03, 1.3, BZ + main_h + 1.58)]
    mesh_from_pydata("Banner", fv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# DIGITAL AGE -- Nordic futuristic, organic glass, LED runes
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (7.0, 6.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.08
    bmesh_box("Found", (6.5, 5.5, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Main organic curved building (approximated with tapered box) ===
    # Wide at base, narrowing toward top, slightly curved in plan
    main_h = 5.0
    # Lower section
    bmesh_box("BaseLower", (3.6, 2.8, 2.0), (0, 0, BZ + 1.0), glass)
    # Upper section (narrower -- organic taper)
    bmesh_box("BaseUpper", (3.0, 2.4, 2.0), (0, 0, BZ + 3.0), glass)
    # Top section (narrowest)
    bmesh_box("BaseTop", (2.4, 2.0, 1.0), (0, 0, BZ + 4.5), glass)

    # Steel frame structure
    for z in [BZ + 0.5, BZ + 1.5, BZ + 2.5, BZ + 3.5, BZ + 4.5]:
        w = 3.62 if z < BZ + 2.0 else (3.02 if z < BZ + 4.0 else 2.42)
        d = 2.82 if z < BZ + 2.0 else (2.42 if z < BZ + 4.0 else 2.02)
        bmesh_box(f"Frame_{z:.1f}", (w, d, 0.04), (0, 0, z), metal)

    # Vertical structural ribs (organic curves approximated)
    for y in [-1.0, 0, 1.0]:
        for xs in [-1, 1]:
            w_base = 1.80
            w_top = 1.20
            verts = [
                (xs * w_base, y - 0.02, BZ),
                (xs * w_base, y + 0.02, BZ),
                (xs * (w_base - 0.15), y + 0.02, BZ + 2.0),
                (xs * (w_base - 0.15), y - 0.02, BZ + 2.0),
                (xs * (w_top + 0.10), y + 0.02, BZ + 3.5),
                (xs * (w_top + 0.10), y - 0.02, BZ + 3.5),
                (xs * w_top, y + 0.02, BZ + main_h),
                (xs * w_top, y - 0.02, BZ + main_h),
            ]
            faces = [(0, 1, 2, 3), (3, 2, 4, 5), (5, 4, 6, 7)]
            mesh_from_pydata(f"Rib_{xs}_{y:.1f}", verts, faces, metal)

    # === LED rune patterns (glowing gold strips on facade) ===
    # Vertical rune-like patterns on front
    rx = 1.81
    rune_verts_1 = [
        (rx, -0.40, BZ + 0.5), (rx, -0.35, BZ + 0.5),
        (rx, -0.20, BZ + 1.5), (rx, -0.25, BZ + 1.5),
        (rx, -0.40, BZ + 2.0), (rx, -0.35, BZ + 2.0),
    ]
    rune_faces_1 = [(0, 1, 2, 3), (2, 3, 5, 4)]
    mesh_from_pydata("RuneLED_1", rune_verts_1, rune_faces_1, m['gold'])

    # Horizontal rune stroke
    bmesh_box("RuneLED_H1", (0.04, 0.50, 0.06), (rx, 0, BZ + 1.8), m['gold'])

    # Angular rune pattern
    rune_verts_2 = [
        (rx, 0.20, BZ + 0.6), (rx, 0.25, BZ + 0.6),
        (rx, 0.45, BZ + 1.2), (rx, 0.40, BZ + 1.2),
        (rx, 0.25, BZ + 1.8), (rx, 0.20, BZ + 1.8),
    ]
    rune_faces_2 = [(0, 1, 2, 3), (2, 3, 5, 4)]
    mesh_from_pydata("RuneLED_2", rune_verts_2, rune_faces_2, m['gold'])

    # Side rune patterns
    for x in [-0.6, 0.0, 0.6]:
        bmesh_box(f"RuneSide_{x:.1f}", (0.06, 0.04, 0.80), (x, -1.41, BZ + 2.0), m['gold'])
    bmesh_box("RuneSideH", (1.0, 0.04, 0.06), (0, -1.41, BZ + 2.4), m['gold'])

    # === Green roof technology (living roof on top) ===
    bmesh_box("GreenRoof", (2.5, 2.1, 0.15), (0, 0, BZ + main_h + 0.075), m['ground'])
    # Small vegetation patches
    for gx, gy in [(-0.6, -0.4), (0.3, 0.5), (-0.4, 0.3), (0.6, -0.3)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(gx, gy, BZ + main_h + 0.20))
        bush = bpy.context.active_object
        bush.name = f"Bush_{gx:.1f}_{gy:.1f}"
        bush.scale = (1, 1, 0.5)
        bush.data.materials.append(m['ground'])

    # === Wind turbine on roof ===
    WT_X, WT_Y = 0.8, 0.6
    wt_base = BZ + main_h + 0.15
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=1.5,
                                        location=(WT_X, WT_Y, wt_base + 0.75))
    bpy.context.active_object.name = "TurbinePole"
    bpy.context.active_object.data.materials.append(metal)
    # Hub
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(WT_X, WT_Y, wt_base + 1.50))
    bpy.context.active_object.name = "TurbineHub"
    bpy.context.active_object.data.materials.append(metal)
    # 3 blades
    for i in range(3):
        a = (2 * math.pi * i) / 3
        bx = WT_X + 0.45 * math.cos(a)
        bz = wt_base + 1.50 + 0.45 * math.sin(a)
        blade_v = [
            (WT_X, WT_Y, wt_base + 1.50),
            (WT_X + 0.03, WT_Y, wt_base + 1.50),
            (bx + 0.01, WT_Y, bz),
            (bx, WT_Y, bz),
        ]
        mesh_from_pydata(f"Blade_{i}", blade_v, [(0, 1, 2, 3)], m['stone_light'])

    # === Entrance -- sleek glass atrium ===
    bmesh_box("Atrium", (0.80, 2.2, 2.5), (1.82 + 0.40, 0, BZ + 1.25), glass)
    bmesh_box("AtrFrame", (0.82, 2.22, 0.04), (1.82 + 0.40, 0, BZ + 2.52), metal)

    # Glass sliding door
    bmesh_box("GlassDoor", (0.04, 1.2, 2.10), (1.82 + 0.81, 0, BZ + 1.05), glass)
    bmesh_box("DoorFrame", (0.05, 1.3, 0.04), (1.82 + 0.82, 0, BZ + 2.12), metal)

    # === LED accent lines around base ===
    bmesh_box("BaseLED_F", (3.62, 0.06, 0.06), (0, -1.42, BZ + 0.03), m['gold'])
    bmesh_box("BaseLED_R", (0.06, 2.82, 0.06), (1.82, 0, BZ + 0.03), m['gold'])
    bmesh_box("BaseLED_L", (0.06, 2.82, 0.06), (-1.82, 0, BZ + 0.03), m['gold'])

    # === Solar canopy walkway ===
    bmesh_box("SolarCanopy", (1.5, 3.0, 0.04), (2.80, 0, BZ + 1.80), glass)
    for sy in [-1.2, 1.2]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=1.70,
                                            location=(2.80, sy, BZ + 0.95))
        bpy.context.active_object.data.materials.append(metal)

    # === Communication spire ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=2.0,
                                        location=(0, 0, BZ + main_h + 0.15 + 1.0))
    bpy.context.active_object.name = "Spire"
    bpy.context.active_object.data.materials.append(metal)
    for z_off in [0.5, 1.0, 1.5]:
        bmesh_box(f"SpireBar_{z_off:.1f}", (0.60, 0.02, 0.02), (0, 0, BZ + main_h + 0.15 + z_off), metal)
        bmesh_box(f"SpireBarY_{z_off:.1f}", (0.02, 0.60, 0.02), (0, 0, BZ + main_h + 0.15 + z_off), metal)

    # LED ring on spire
    bmesh_prism("SpireLED", 0.12, 0.06, 12, (0, 0, BZ + main_h + 0.15 + 1.80), m['gold'])


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


def build_town_center_vikings(materials, age='medieval'):
    """Build a Vikings nation Town Center with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
