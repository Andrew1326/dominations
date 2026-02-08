"""
Chinese Nation Town Center — culturally authentic Chinese architecture per age.

Stone:         Neolithic Banpo-style village — semi-underground round houses,
               rammed earth walls, thatched roofs, village center post
Bronze:        Shang dynasty palace — rammed earth platform, timber-frame hall
               with wide overhanging roof, bronze vessels, oracle bone tower
Iron:          Zhou dynasty palace — walled compound, main hall with hip-and-gable
               roof, watchtower, ceremonial gate with pillars
Classical:     Han dynasty palace — large multi-tiered hall on raised platform,
               que (pillar gates), curved roof with upturned eaves, courtyard walls
Medieval:      Tang/Song dynasty palace — grand multi-story pagoda-style main
               hall, curved roofs with gold ridge ornaments, gate tower, dragon finials
Gunpowder:     Ming dynasty Forbidden City style — grand hall on marble platform,
               double-eaved hip roof, red walls, gold roof ridge, corner towers
Enlightenment: Qing dynasty imperial hall — ornate multi-tier structure, yellow
               glazed tile roofs, elaborate bracket sets (dougong), marble balustrades
Industrial:    Late Qing/Republic era — blend of Chinese roofs with Western brick,
               clock tower, grand staircase, hybrid architecture
Modern:        Chinese modernist — Great Hall of the People style, wide columned
               facade, flat roof with Chinese-style cornice, red star
Digital:       Futuristic Chinese — glass pagoda tower with LED-lit curved roof
               tiers, holographic dragon, floating garden platforms
"""

import bpy
import bmesh
import math

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# -----------------------------------------------------------------
# Helper: curved Chinese roof via mesh_from_pydata
# -----------------------------------------------------------------
def _chinese_roof(name, half_w, half_d, ridge_h, eave_overhang, eave_lift,
                  origin, material, ridge_w=0.0):
    """
    Build a hip roof whose four corners curve upward (upturned eaves).
    *ridge_w* lets the ridge be a short line instead of a point
    (set 0 for a true hip, >0 for a hip-and-gable look).
    """
    ox, oy, oz = origin
    hw = half_w + eave_overhang
    hd = half_d + eave_overhang

    # Mid-eave control points stay at oz; corners lift up
    verts = [
        # 0-3  eave corners (lifted)
        (ox - hw, oy - hd, oz + eave_lift),
        (ox + hw, oy - hd, oz + eave_lift),
        (ox + hw, oy + hd, oz + eave_lift),
        (ox - hw, oy + hd, oz + eave_lift),
        # 4-7  eave midpoints (at oz, making the curve)
        (ox,      oy - hd, oz),
        (ox + hw, oy,      oz),
        (ox,      oy + hd, oz),
        (ox - hw, oy,      oz),
        # 8-9  ridge endpoints
        (ox - ridge_w, oy, oz + ridge_h),
        (ox + ridge_w, oy, oz + ridge_h),
    ]
    faces = [
        (0, 4, 9, 8),   # front-left slope
        (4, 1, 9),       # front-right triangle
        (1, 5, 9),       # right-front slope
        (5, 2, 9, 8) if ridge_w == 0 else (5, 2, 9),  # right-back
        (2, 6, 8) if ridge_w == 0 else (2, 6, 8, 9),  # back-right
        (6, 3, 8),       # back-left triangle
        (3, 7, 8),       # left-back slope
        (7, 0, 8),       # left-front slope
    ]
    # Simpler tessellation: 4 quad faces (front, right, back, left)
    faces = [
        (0, 4, 9, 8),   # front-left
        (4, 1, 9),       # front-right
        (1, 5, 9),       # right-front
        (5, 2, 8, 9),   # right-back
        (2, 6, 8),       # back-right
        (6, 3, 8),       # back-left
        (3, 7, 8),       # left-back
        (7, 0, 9, 8),   # left-front
    ]
    # Even simpler: 4 main faces for a hip roof
    faces = [
        (0, 1, 9, 8),   # front face
        (1, 2, 8, 9),   # right face
        (2, 3, 8),       # back face  (triangle if ridge_w==0)
        (3, 0, 8),       # left face
    ]
    if ridge_w > 0:
        faces = [
            (0, 1, 9, 8),   # front
            (1, 2, 9),       # right-front
            (2, 3, 8, 9),   # back
            (3, 0, 8),       # left-back
        ]

    # Full curved hip roof with 8 triangular/quad sections
    # Using 4 corner verts + 4 edge-midpoint verts + ridge
    verts = [
        # 0-3 corners (lifted for upturned eaves)
        (ox - hw, oy - hd, oz + eave_lift),
        (ox + hw, oy - hd, oz + eave_lift),
        (ox + hw, oy + hd, oz + eave_lift),
        (ox - hw, oy + hd, oz + eave_lift),
        # 4-7 edge midpoints (drooping slightly for curve)
        (ox,      oy - hd, oz - 0.02),
        (ox + hw, oy,      oz - 0.02),
        (ox,      oy + hd, oz - 0.02),
        (ox - hw, oy,      oz - 0.02),
        # 8-9 ridge
        (ox - ridge_w, oy, oz + ridge_h),
        (ox + ridge_w, oy, oz + ridge_h),
    ]

    if ridge_w > 0:
        faces = [
            (0, 4, 9, 8),   # front-left
            (4, 1, 9),       # front-right
            (1, 5, 9),       # right-front
            (5, 2, 8, 9),   # right-back
            (2, 6, 8),       # back-right
            (6, 3, 8),       # back-left
            (3, 7, 8),       # left-back
            (7, 0, 9, 8),   # left-front
        ]
    else:
        # single apex
        apex = 8
        faces = [
            (0, 4, apex),
            (4, 1, apex),
            (1, 5, apex),
            (5, 2, apex),
            (2, 6, apex),
            (6, 3, apex),
            (3, 7, apex),
            (7, 0, apex),
        ]
        # remove vert 9 — not needed
        verts = verts[:9]

    obj = mesh_from_pydata(name, verts, faces, material)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def _dougong_bracket(name, x, y, z, material):
    """Small stepped bracket set (dougong) for under eaves."""
    bmesh_box(name + "_b0", (0.12, 0.12, 0.06), (x, y, z), material)
    bmesh_box(name + "_b1", (0.18, 0.08, 0.04), (x, y, z + 0.05), material)
    bmesh_box(name + "_b2", (0.08, 0.18, 0.04), (x, y, z + 0.09), material)


# ============================================================
# STONE AGE — Neolithic Banpo-style village
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Central village post (totem/marker) ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.10, depth=2.8,
                                        location=(0, 0, Z + 1.4))
    post = bpy.context.active_object
    post.name = "CenterPost"
    post.data.materials.append(m['wood_dark'])

    # Carved head on top of post
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0, 0, Z + 2.90))
    head = bpy.context.active_object
    head.name = "PostHead"
    head.data.materials.append(m['wood'])

    # === Main semi-underground round house ===
    # Sunken pit
    bmesh_prism("Pit1", 1.6, 0.10, 16, (1.0, 0.5, Z - 0.05), m['stone_dark'])
    # Rammed earth walls (low ring)
    bmesh_prism("HouseWall1", 1.5, 0.9, 16, (1.0, 0.5, Z), m['stone'])
    # Thatched conical roof
    bmesh_cone("HouseRoof1", 2.0, 1.8, 16, (1.0, 0.5, Z + 0.9), m['roof'])
    # Smoke hole ring at top
    bmesh_prism("Smoke1", 0.18, 0.12, 8, (1.0, 0.5, Z + 2.65), m['wood'])
    # Door opening
    bmesh_box("Door1", (0.10, 0.50, 0.70), (1.0 + 1.50, 0.5, Z + 0.35), m['door'])

    # Support poles around main house
    for i in range(6):
        a = (2 * math.pi * i) / 6
        px = 1.0 + 1.35 * math.cos(a)
        py = 0.5 + 1.35 * math.sin(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=1.8,
                                            location=(px, py, Z + 0.9))
        pole = bpy.context.active_object
        pole.name = f"Pole1_{i}"
        pole.data.materials.append(m['wood'])

    # === Second smaller round house ===
    bmesh_prism("Pit2", 1.0, 0.08, 12, (-1.2, -0.8, Z - 0.04), m['stone_dark'])
    bmesh_prism("HouseWall2", 0.95, 0.7, 12, (-1.2, -0.8, Z), m['stone'])
    bmesh_cone("HouseRoof2", 1.3, 1.3, 12, (-1.2, -0.8, Z + 0.7), m['roof'])
    bmesh_box("Door2", (0.08, 0.40, 0.55), (-1.2 + 0.95, -0.8, Z + 0.28), m['door'])

    # === Third smallest house ===
    bmesh_prism("Pit3", 0.70, 0.06, 10, (-0.8, 1.5, Z - 0.03), m['stone_dark'])
    bmesh_prism("HouseWall3", 0.65, 0.55, 10, (-0.8, 1.5, Z), m['stone'])
    bmesh_cone("HouseRoof3", 0.90, 1.0, 10, (-0.8, 1.5, Z + 0.55), m['roof'])

    # === Storage pit (covered) ===
    bmesh_prism("StoragePit", 0.50, 0.06, 10, (1.8, -1.4, Z - 0.03), m['stone_dark'])
    bmesh_cone("StorageCover", 0.65, 0.5, 8, (1.8, -1.4, Z + 0.03), m['roof'])

    # === Fire pit (communal hearth) ===
    bmesh_prism("FirePit", 0.40, 0.08, 10, (-0.2, -0.3, Z + 0.04), m['stone_dark'])
    for i, angle in enumerate([0.3, -0.5, 0.7, -0.2]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.45,
                                            location=(-0.2, -0.3, Z + 0.12))
        log = bpy.context.active_object
        log.name = f"FireLog_{i}"
        log.rotation_euler = (0.3, angle, i * 0.8)
        log.data.materials.append(m['wood_dark'])

    # === Drying rack (wooden A-frame) ===
    for dy in [-0.25, 0.25]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=1.5,
                                            location=(-2.0, dy, Z + 0.75))
        rack = bpy.context.active_object
        rack.name = f"Rack_{dy:.1f}"
        rack.data.materials.append(m['wood'])
    bmesh_box("RackBar", (0.04, 0.60, 0.04), (-2.0, 0, Z + 1.45), m['wood'])

    # Animal skin hanging
    sv = [(-2.0, -0.20, Z + 1.40), (-2.0, 0.20, Z + 1.40),
          (-2.0, 0.18, Z + 0.80), (-2.0, -0.18, Z + 0.85)]
    mesh_from_pydata("HangingSkin", sv, [(0, 1, 2, 3)], m['roof_edge'])
    m['roof_edge'].use_backface_culling = False

    # === Low fence (wattle fence around village) ===
    fence_r = 2.4
    n_stakes = 20
    for i in range(n_stakes):
        a = (2 * math.pi * i) / n_stakes
        fx, fy = fence_r * math.cos(a), fence_r * math.sin(a)
        h = 0.6 + 0.08 * math.sin(i * 2.3)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=h,
                                            location=(fx, fy, Z + h / 2))
        stake = bpy.context.active_object
        stake.name = f"Fence_{i}"
        stake.data.materials.append(m['wood'])


# ============================================================
# BRONZE AGE — Shang dynasty palace
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Large rammed earth platform (hangtu) ===
    bmesh_box("Platform1", (5.0, 4.6, 0.20), (0, 0, Z + 0.10), m['stone_dark'], bevel=0.05)
    bmesh_box("Platform2", (4.4, 4.0, 0.18), (0, 0, Z + 0.29), m['stone_dark'], bevel=0.04)
    bmesh_box("Platform3", (3.8, 3.4, 0.15), (0, 0, Z + 0.45), m['stone'], bevel=0.03)

    BZ = Z + 0.53

    # === Main timber-frame hall ===
    hall_w, hall_d = 2.8, 2.2
    hall_h = 2.0

    # Timber columns (grid of pillars)
    col_positions = []
    for cx in [-1.2, -0.4, 0.4, 1.2]:
        for cy in [-0.9, 0, 0.9]:
            col_positions.append((cx, cy))
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=hall_h,
                                                location=(cx, cy, BZ + hall_h / 2))
            col = bpy.context.active_object
            col.name = f"Col_{cx:.1f}_{cy:.1f}"
            col.data.materials.append(m['wood_dark'])

    # Rammed-earth infill walls
    bmesh_box("WallF", (0.12, hall_d, hall_h * 0.7), (hall_w / 2 - 0.06, 0, BZ + hall_h * 0.35), m['stone'])
    bmesh_box("WallB", (0.12, hall_d, hall_h * 0.7), (-hall_w / 2 + 0.06, 0, BZ + hall_h * 0.35), m['stone'])
    bmesh_box("WallR", (hall_w, 0.12, hall_h * 0.7), (0, -hall_d / 2 + 0.06, BZ + hall_h * 0.35), m['stone'])
    bmesh_box("WallL", (hall_w, 0.12, hall_h * 0.7), (0, hall_d / 2 - 0.06, BZ + hall_h * 0.35), m['stone'])

    # Beam structure at top of walls
    bmesh_box("BeamF", (hall_w + 0.3, 0.10, 0.10), (0, -hall_d / 2, BZ + hall_h), m['wood_beam'])
    bmesh_box("BeamB", (hall_w + 0.3, 0.10, 0.10), (0, hall_d / 2, BZ + hall_h), m['wood_beam'])
    bmesh_box("BeamR", (0.10, hall_d + 0.3, 0.10), (hall_w / 2, 0, BZ + hall_h), m['wood_beam'])
    bmesh_box("BeamL", (0.10, hall_d + 0.3, 0.10), (-hall_w / 2, 0, BZ + hall_h), m['wood_beam'])

    # Wide overhanging thatched roof
    _chinese_roof("HallRoof", hall_w / 2, hall_d / 2, 1.4, 0.45, 0.25,
                  (0, 0, BZ + hall_h + 0.05), m['roof'], ridge_w=0.6)

    # Door
    bmesh_box("Door", (0.08, 0.55, 1.20), (hall_w / 2 - 0.01, 0, BZ + 0.60), m['door'])

    # === Oracle bone tower (tall narrow structure) ===
    TX, TY = -1.6, -1.4
    tower_h = 3.0
    bmesh_box("OracleTower", (0.6, 0.6, tower_h), (TX, TY, BZ + tower_h / 2), m['wood_dark'], bevel=0.02)
    bmesh_box("OTBand1", (0.66, 0.66, 0.06), (TX, TY, BZ + 1.0), m['wood_beam'])
    bmesh_box("OTBand2", (0.66, 0.66, 0.06), (TX, TY, BZ + 2.0), m['wood_beam'])
    _chinese_roof("OTRoof", 0.3, 0.3, 0.7, 0.25, 0.15,
                  (TX, TY, BZ + tower_h + 0.02), m['roof'], ridge_w=0.0)

    # === Bronze vessels (ritual ding tripods) ===
    for i, (vx, vy) in enumerate([(1.8, 1.2), (1.8, -1.2), (1.5, 0)]):
        # Vessel body
        bmesh_prism(f"Ding_{i}", 0.15, 0.20, 8, (vx, vy, BZ + 0.10), m['gold'])
        # Tripod legs
        for la in range(3):
            ang = (2 * math.pi * la) / 3
            lx = vx + 0.12 * math.cos(ang)
            ly = vy + 0.12 * math.sin(ang)
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.10,
                                                location=(lx, ly, BZ + 0.05))
            leg = bpy.context.active_object
            leg.name = f"DingLeg_{i}_{la}"
            leg.data.materials.append(m['gold'])

    # === Steps to platform (front) ===
    for i in range(6):
        bmesh_box(f"Step_{i}", (0.20, 1.4, 0.06),
                  (hall_w / 2 + 0.40 + i * 0.22, 0, BZ - 0.04 - i * 0.09), m['stone_dark'])

    # Banner pole
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=1.0,
                                        location=(0, 0, BZ + hall_h + 1.4 + 0.5))
    bpy.context.active_object.data.materials.append(m['wood'])
    bv = [(0.04, 0, BZ + hall_h + 2.15), (0.50, 0.03, BZ + hall_h + 2.10),
          (0.50, 0.02, BZ + hall_h + 2.40), (0.04, 0, BZ + hall_h + 2.38)]
    mesh_from_pydata("Banner", bv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# IRON AGE — Zhou dynasty palace
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Raised earth platform ===
    bmesh_box("Platform", (5.0, 4.6, 0.22), (0, 0, Z + 0.11), m['stone_dark'], bevel=0.05)
    bmesh_box("Platform2", (4.4, 4.0, 0.16), (0, 0, Z + 0.30), m['stone'], bevel=0.04)

    BZ = Z + 0.38

    # === Compound walls ===
    WALL_H = 1.8
    hw = 2.0
    wt = 0.18
    bmesh_box("WallF", (wt, hw * 2, WALL_H), (hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallB", (wt, hw * 2, WALL_H), (-hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallR", (hw * 2, wt, WALL_H), (0, -hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallL", (hw * 2, wt, WALL_H), (0, hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)

    # Wall caps
    for label, pos, sz in [
        ("F", (hw, 0), (wt + 0.06, hw * 2 + 0.06, 0.06)),
        ("B", (-hw, 0), (wt + 0.06, hw * 2 + 0.06, 0.06)),
        ("R", (0, -hw), (hw * 2 + 0.06, wt + 0.06, 0.06)),
        ("L", (0, hw), (hw * 2 + 0.06, wt + 0.06, 0.06)),
    ]:
        bmesh_box(f"WallCap_{label}", sz, (*pos, BZ + WALL_H + 0.03), m['stone_trim'])

    # === Ceremonial gate with pillars ===
    gate_x = hw + wt / 2
    # Gate pillars
    for gy in [-0.45, 0.45]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.10, depth=2.2,
                                            location=(gate_x, gy, BZ + 1.1))
        gp = bpy.context.active_object
        gp.name = f"GatePillar_{gy:.1f}"
        gp.data.materials.append(m['wood_dark'])

    # Gate lintel beam
    bmesh_box("GateLintel", (0.14, 1.1, 0.12), (gate_x, 0, BZ + 2.25), m['wood_beam'])

    # Small gate roof
    _chinese_roof("GateRoof", 0.35, 0.55, 0.5, 0.20, 0.12,
                  (gate_x, 0, BZ + 2.37), m['roof'], ridge_w=0.15)

    # Gate door
    bmesh_box("GateDoor", (0.08, 0.60, 1.30), (gate_x + 0.01, 0, BZ + 0.65), m['door'])

    # === Main hall (hip-and-gable roof) ===
    hall_w, hall_d, hall_h = 2.2, 1.8, 2.4

    # Timber columns
    for cx in [-0.8, 0, 0.8]:
        for cy in [-0.7, 0, 0.7]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=hall_h,
                                                location=(cx, cy, BZ + hall_h / 2))
            col = bpy.context.active_object
            col.name = f"HallCol_{cx:.1f}_{cy:.1f}"
            col.data.materials.append(m['wood_dark'])

    # Hall walls (infill between columns)
    bmesh_box("HallWallF", (0.10, hall_d, hall_h * 0.75), (hall_w / 2 - 0.05, 0, BZ + hall_h * 0.375), m['stone'])
    bmesh_box("HallWallB", (0.10, hall_d, hall_h * 0.75), (-hall_w / 2 + 0.05, 0, BZ + hall_h * 0.375), m['stone'])
    bmesh_box("HallWallR", (hall_w, 0.10, hall_h * 0.75), (0, -hall_d / 2 + 0.05, BZ + hall_h * 0.375), m['stone'])
    bmesh_box("HallWallL", (hall_w, 0.10, hall_h * 0.75), (0, hall_d / 2 - 0.05, BZ + hall_h * 0.375), m['stone'])

    # Beam structure
    bmesh_box("HallBeamTop", (hall_w + 0.20, hall_d + 0.20, 0.10), (0, 0, BZ + hall_h), m['wood_beam'])

    # Hip-and-gable roof
    _chinese_roof("HallRoof", hall_w / 2, hall_d / 2, 1.3, 0.40, 0.20,
                  (0, 0, BZ + hall_h + 0.05), m['roof'], ridge_w=0.5)

    # Hall door
    bmesh_box("HallDoor", (0.08, 0.50, 1.15), (hall_w / 2, 0, BZ + 0.58), m['door'])

    # Hall windows
    for y in [-0.55, 0.55]:
        bmesh_box(f"HallWin_{y:.1f}", (0.06, 0.18, 0.40), (hall_w / 2, y, BZ + 1.4), m['window'])

    # === Watchtower (corner) ===
    TX, TY = -1.6, -1.6
    tower_h = 3.6
    # Square base
    bmesh_box("WatchBase", (0.65, 0.65, tower_h * 0.6), (TX, TY, BZ + tower_h * 0.3), m['wood_dark'], bevel=0.02)
    # Upper tier
    bmesh_box("WatchUpper", (0.55, 0.55, tower_h * 0.4), (TX, TY, BZ + tower_h * 0.6 + tower_h * 0.2), m['wood'], bevel=0.02)
    # Intermediate roof
    _chinese_roof("WatchRoof1", 0.28, 0.28, 0.15, 0.20, 0.10,
                  (TX, TY, BZ + tower_h * 0.6), m['roof'], ridge_w=0.0)
    # Top roof
    _chinese_roof("WatchRoof2", 0.28, 0.28, 0.5, 0.22, 0.12,
                  (TX, TY, BZ + tower_h + 0.02), m['roof'], ridge_w=0.0)

    # === Steps ===
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.20, 1.2, 0.06),
                  (hw + 0.35 + i * 0.22, 0, BZ - 0.04 - i * 0.08), m['stone_dark'])

    # Banner
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.8,
                                        location=(TX, TY, BZ + tower_h + 0.5 + 0.4))
    bpy.context.active_object.data.materials.append(m['wood'])
    fz = BZ + tower_h + 0.9 + 0.15
    fv = [(TX + 0.03, TY, fz), (TX + 0.42, TY + 0.03, fz - 0.04),
          (TX + 0.42, TY + 0.02, fz + 0.22), (TX + 0.03, TY, fz + 0.20)]
    mesh_from_pydata("Banner", fv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# CLASSICAL AGE — Han dynasty palace
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Grand raised platform (3 tiers with stairs) ===
    bmesh_box("Plat1", (5.2, 4.8, 0.18), (0, 0, Z + 0.09), m['stone_light'], bevel=0.04)
    bmesh_box("Plat2", (4.6, 4.2, 0.16), (0, 0, Z + 0.26), m['stone_light'], bevel=0.03)
    bmesh_box("Plat3", (4.0, 3.6, 0.14), (0, 0, Z + 0.41), m['stone'], bevel=0.03)

    BZ = Z + 0.48

    # === Courtyard walls ===
    WALL_H = 1.5
    cw = 1.9
    wt = 0.14
    bmesh_box("CWallR", (cw * 2, wt, WALL_H), (0, -cw, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("CWallL", (cw * 2, wt, WALL_H), (0, cw, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("CWallB", (wt, cw * 2, WALL_H), (-cw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    # Wall caps
    for label, pos, sz in [
        ("R", (0, -cw), (cw * 2 + 0.08, wt + 0.06, 0.06)),
        ("L", (0, cw), (cw * 2 + 0.08, wt + 0.06, 0.06)),
        ("B", (-cw, 0), (wt + 0.06, cw * 2 + 0.08, 0.06)),
    ]:
        bmesh_box(f"CWallCap_{label}", sz, (*pos, BZ + WALL_H + 0.03), m['stone_trim'])

    # === Que (pillar gates) at entrance ===
    for gy in [-1.0, 1.0]:
        # Pillar base
        bmesh_box(f"QueBase_{gy:.1f}", (0.30, 0.30, 0.20), (cw + 0.4, gy, BZ + 0.10), m['stone_light'])
        # Pillar shaft
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.10, depth=2.0,
                                            location=(cw + 0.4, gy, BZ + 1.20))
        qp = bpy.context.active_object
        qp.name = f"QuePillar_{gy:.1f}"
        qp.data.materials.append(m['stone_light'])
        # Que cap with small roof
        bmesh_box(f"QueCap_{gy:.1f}", (0.35, 0.35, 0.08), (cw + 0.4, gy, BZ + 2.24), m['stone_trim'])
        _chinese_roof(f"QueRoof_{gy:.1f}", 0.18, 0.18, 0.30, 0.12, 0.08,
                      (cw + 0.4, gy, BZ + 2.32), m['roof'], ridge_w=0.0)

    # === Main hall — multi-tiered ===
    # Lower tier
    hall_w, hall_d = 2.4, 2.0
    hall_h1 = 2.2
    # Timber columns (4x3 grid)
    for cx in [-0.9, -0.3, 0.3, 0.9]:
        for cy in [-0.75, 0, 0.75]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.08, depth=hall_h1,
                                                location=(cx, cy, BZ + hall_h1 / 2))
            col = bpy.context.active_object
            col.name = f"HallCol_{cx:.1f}_{cy:.1f}"
            col.data.materials.append(m['wood_dark'])

    # Lower walls
    bmesh_box("LWallF", (0.10, hall_d - 0.2, hall_h1 * 0.65), (hall_w / 2 - 0.05, 0, BZ + hall_h1 * 0.325), m['stone'])
    bmesh_box("LWallB", (0.10, hall_d - 0.2, hall_h1 * 0.65), (-hall_w / 2 + 0.05, 0, BZ + hall_h1 * 0.325), m['stone'])
    bmesh_box("LWallR", (hall_w - 0.2, 0.10, hall_h1 * 0.65), (0, -hall_d / 2 + 0.05, BZ + hall_h1 * 0.325), m['stone'])
    bmesh_box("LWallL", (hall_w - 0.2, 0.10, hall_h1 * 0.65), (0, hall_d / 2 - 0.05, BZ + hall_h1 * 0.325), m['stone'])

    # Beam at top
    bmesh_box("LowerBeam", (hall_w + 0.20, hall_d + 0.20, 0.10), (0, 0, BZ + hall_h1), m['wood_beam'])

    # Lower curved roof with upturned eaves
    _chinese_roof("LowerRoof", hall_w / 2, hall_d / 2, 1.2, 0.50, 0.30,
                  (0, 0, BZ + hall_h1 + 0.05), m['roof'], ridge_w=0.5)

    # Upper tier
    hall_h2 = 1.6
    upper_w, upper_d = 1.6, 1.3
    upper_z = BZ + hall_h1 + 1.2 + 0.05

    bmesh_box("UpperHall", (upper_w, upper_d, hall_h2),
              (0, 0, upper_z + hall_h2 / 2), m['stone'], bevel=0.02)
    bmesh_box("UpperBeam", (upper_w + 0.14, upper_d + 0.14, 0.08),
              (0, 0, upper_z + hall_h2), m['wood_beam'])

    # Upper roof
    _chinese_roof("UpperRoof", upper_w / 2, upper_d / 2, 0.9, 0.35, 0.22,
                  (0, 0, upper_z + hall_h2 + 0.03), m['roof'], ridge_w=0.3)

    # Windows on lower hall
    for y in [-0.60, 0, 0.60]:
        bmesh_box(f"LWin_{y:.1f}", (0.06, 0.16, 0.45), (hall_w / 2, y, BZ + 1.3), m['window'])

    # Door
    bmesh_box("Door", (0.08, 0.55, 1.30), (hall_w / 2, 0, BZ + 0.65), m['door'])

    # === Ceremonial steps (wide, central) ===
    for i in range(7):
        bmesh_box(f"Step_{i}", (0.22, 2.2, 0.06),
                  (cw + 0.70 + i * 0.22, 0, BZ - 0.04 - i * 0.07), m['stone_light'])

    # Gold ridge ornament on upper roof
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10,
                                          location=(0, 0, upper_z + hall_h2 + 0.93))
    ornament = bpy.context.active_object
    ornament.name = "RidgeOrnament"
    ornament.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()


# ============================================================
# MEDIEVAL AGE — Tang/Song dynasty palace
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Grand marble platform ===
    bmesh_box("Plat1", (5.2, 4.8, 0.15), (0, 0, Z + 0.075), m['stone_light'], bevel=0.04)
    bmesh_box("Plat2", (4.6, 4.2, 0.14), (0, 0, Z + 0.22), m['stone_light'], bevel=0.03)
    bmesh_box("Plat3", (4.0, 3.6, 0.12), (0, 0, Z + 0.35), m['stone'], bevel=0.03)

    BZ = Z + 0.41

    # === Courtyard walls (low, decorative) ===
    cw = 2.0
    wt = 0.12
    WALL_H = 1.2
    bmesh_box("CWallR", (cw * 2, wt, WALL_H), (0, -cw, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("CWallL", (cw * 2, wt, WALL_H), (0, cw, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("CWallB", (wt, cw * 2, WALL_H), (-cw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)

    # Wall cap tiles
    for label, pos, sz in [
        ("R", (0, -cw), (cw * 2 + 0.06, wt + 0.08, 0.05)),
        ("L", (0, cw), (cw * 2 + 0.06, wt + 0.08, 0.05)),
        ("B", (-cw, 0), (wt + 0.08, cw * 2 + 0.06, 0.05)),
    ]:
        bmesh_box(f"WCap_{label}", sz, (*pos, BZ + WALL_H + 0.025), m['roof'])

    # === Gate tower (front entrance) ===
    gate_x = cw + 0.15
    gate_w, gate_d, gate_h = 0.8, 1.3, 2.5
    bmesh_box("GateTower", (gate_w, gate_d, gate_h), (gate_x, 0, BZ + gate_h / 2), m['stone'], bevel=0.02)
    bmesh_box("GateBeam", (gate_w + 0.15, gate_d + 0.15, 0.08), (gate_x, 0, BZ + gate_h), m['wood_beam'])

    # Gate tower curved roof
    _chinese_roof("GateRoof", gate_w / 2, gate_d / 2, 0.7, 0.30, 0.18,
                  (gate_x, 0, BZ + gate_h + 0.04), m['roof'], ridge_w=0.20)

    # Gate opening
    bmesh_box("GateDoor", (0.08, 0.65, 1.40), (gate_x + gate_w / 2 + 0.01, 0, BZ + 0.70), m['door'])

    # === Grand multi-story main hall (pagoda style) ===
    # First floor
    hall_w, hall_d = 2.6, 2.2
    f1_h = 2.4

    # Red-painted columns (5x4 grid)
    for cx in [-1.0, -0.5, 0, 0.5, 1.0]:
        for cy in [-0.85, -0.28, 0.28, 0.85]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.07, depth=f1_h,
                                                location=(cx, cy, BZ + f1_h / 2))
            col = bpy.context.active_object
            col.name = f"Col1_{cx:.1f}_{cy:.1f}"
            col.data.materials.append(m['wood_dark'])

    # First floor walls
    bmesh_box("F1WallF", (0.10, hall_d, f1_h * 0.7), (hall_w / 2 - 0.05, 0, BZ + f1_h * 0.35), m['stone'])
    bmesh_box("F1WallB", (0.10, hall_d, f1_h * 0.7), (-hall_w / 2 + 0.05, 0, BZ + f1_h * 0.35), m['stone'])
    bmesh_box("F1WallR", (hall_w, 0.10, f1_h * 0.7), (0, -hall_d / 2 + 0.05, BZ + f1_h * 0.35), m['stone'])
    bmesh_box("F1WallL", (hall_w, 0.10, f1_h * 0.7), (0, hall_d / 2 - 0.05, BZ + f1_h * 0.35), m['stone'])

    # First floor beam
    bmesh_box("F1Beam", (hall_w + 0.20, hall_d + 0.20, 0.10), (0, 0, BZ + f1_h), m['wood_beam'])

    # First floor curved roof (wide eaves)
    roof1_z = BZ + f1_h + 0.05
    _chinese_roof("Roof1", hall_w / 2, hall_d / 2, 1.2, 0.55, 0.30,
                  (0, 0, roof1_z), m['roof'], ridge_w=0.5)

    # Second floor
    f2_w, f2_d = 1.8, 1.5
    f2_h = 1.8
    f2_z = roof1_z + 1.2  # above first roof ridge

    bmesh_box("F2Hall", (f2_w, f2_d, f2_h), (0, 0, f2_z + f2_h / 2), m['stone'], bevel=0.02)
    bmesh_box("F2Beam", (f2_w + 0.14, f2_d + 0.14, 0.08), (0, 0, f2_z + f2_h), m['wood_beam'])

    # Second floor curved roof
    roof2_z = f2_z + f2_h + 0.03
    _chinese_roof("Roof2", f2_w / 2, f2_d / 2, 0.9, 0.40, 0.22,
                  (0, 0, roof2_z), m['roof'], ridge_w=0.3)

    # Second floor windows
    for y in [-0.45, 0, 0.45]:
        bmesh_box(f"F2Win_{y:.1f}", (0.06, 0.14, 0.40), (f2_w / 2 + 0.01, y, f2_z + 0.9), m['window'])

    # First floor windows
    for y in [-0.7, -0.25, 0.25, 0.7]:
        bmesh_box(f"F1Win_{y:.1f}", (0.06, 0.16, 0.50), (hall_w / 2, y, BZ + 1.4), m['window'])

    # Door
    bmesh_box("Door", (0.08, 0.55, 1.30), (hall_w / 2, 0, BZ + 0.65), m['door'])

    # === Gold ridge ornaments ===
    # Ridge finials (dragon-like accents)
    for rz, rw in [(roof1_z + 1.2, 0.5), (roof2_z + 0.9, 0.3)]:
        for dx in [-1, 1]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(dx * rw, 0, rz + 0.05))
            fin = bpy.context.active_object
            fin.name = f"RidgeFin_{rz:.1f}_{dx}"
            fin.data.materials.append(m['gold'])
            bpy.ops.object.shade_smooth()

    # Top ornament (golden finial)
    top_z = roof2_z + 0.9
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, 0, top_z + 0.05))
    bpy.context.active_object.name = "TopOrnament"
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # Dragon finials on first roof corners
    for cx, cy in [(hall_w / 2 + 0.55, -hall_d / 2 - 0.55),
                   (hall_w / 2 + 0.55, hall_d / 2 + 0.55),
                   (-hall_w / 2 - 0.55, -hall_d / 2 - 0.55),
                   (-hall_w / 2 - 0.55, hall_d / 2 + 0.55)]:
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.06, radius2=0.02, depth=0.20,
                                         location=(cx, cy, roof1_z + 0.35))
        dragon = bpy.context.active_object
        dragon.name = f"DragonFin_{cx:.1f}_{cy:.1f}"
        dragon.rotation_euler = (0.3, 0.3, math.atan2(cy, cx))
        dragon.data.materials.append(m['gold'])

    # === Steps ===
    for i in range(7):
        bmesh_box(f"Step_{i}", (0.20, 2.0, 0.06),
                  (cw + 0.55 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_light'])


# ============================================================
# GUNPOWDER AGE — Ming dynasty Forbidden City style
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (6.0, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Triple-tier marble platform (Forbidden City style) ===
    bmesh_box("MarblePlat1", (5.6, 5.2, 0.20), (0, 0, Z + 0.10), m['stone_light'], bevel=0.05)
    bmesh_box("MarblePlat2", (5.0, 4.6, 0.18), (0, 0, Z + 0.29), m['stone_light'], bevel=0.04)
    bmesh_box("MarblePlat3", (4.4, 4.0, 0.16), (0, 0, Z + 0.46), m['stone'], bevel=0.03)

    BZ = Z + 0.54

    # Marble balustrade on platform edge (simplified posts)
    for i in range(12):
        bx = -2.1 + i * 0.40
        for by in [-1.95, 1.95]:
            bmesh_box(f"Baluster_{i}_{by:.1f}", (0.06, 0.06, 0.25),
                      (bx, by, Z + 0.46 + 0.125), m['stone_light'])
    for j in range(10):
        by = -1.75 + j * 0.39
        for bx in [-2.15, 2.15]:
            bmesh_box(f"BalusterS_{j}_{bx:.1f}", (0.06, 0.06, 0.25),
                      (bx, by, Z + 0.46 + 0.125), m['stone_light'])

    # === Red walls (enclosure) ===
    WALL_H = 2.4
    hw = 2.0
    wt = 0.20
    # Red-painted walls
    bmesh_box("RWallF", (wt, hw * 2 - 0.2, WALL_H), (hw, 0, BZ + WALL_H / 2), m['banner'], bevel=0.02)
    bmesh_box("RWallB", (wt, hw * 2 - 0.2, WALL_H), (-hw, 0, BZ + WALL_H / 2), m['banner'], bevel=0.02)
    bmesh_box("RWallR", (hw * 2 - 0.2, wt, WALL_H), (0, -hw, BZ + WALL_H / 2), m['banner'], bevel=0.02)
    bmesh_box("RWallL", (hw * 2 - 0.2, wt, WALL_H), (0, hw, BZ + WALL_H / 2), m['banner'], bevel=0.02)

    # Wall-top roof tiles
    for label, pos, sz in [
        ("F", (hw, 0), (wt + 0.10, hw * 2, 0.06)),
        ("B", (-hw, 0), (wt + 0.10, hw * 2, 0.06)),
        ("R", (0, -hw), (hw * 2, wt + 0.10, 0.06)),
        ("L", (0, hw), (hw * 2, wt + 0.10, 0.06)),
    ]:
        bmesh_box(f"WTile_{label}", sz, (*pos, BZ + WALL_H + 0.03), m['roof'])

    # === Corner towers ===
    tower_h = 3.0
    for xs, ys, label in [(-1, -1, "BL"), (-1, 1, "FL"), (1, -1, "BR"), (1, 1, "FR")]:
        tx, ty = xs * hw, ys * hw
        bmesh_box(f"CTower_{label}", (0.55, 0.55, tower_h),
                  (tx, ty, BZ + tower_h / 2), m['banner'], bevel=0.02)
        bmesh_box(f"CTBeam_{label}", (0.62, 0.62, 0.06),
                  (tx, ty, BZ + tower_h), m['wood_beam'])
        _chinese_roof(f"CTRoof_{label}", 0.28, 0.28, 0.5, 0.22, 0.12,
                      (tx, ty, BZ + tower_h + 0.03), m['roof'], ridge_w=0.0)

    # === Ceremonial gate (Meridian Gate style) ===
    gate_x = hw + wt / 2 + 0.10
    bmesh_box("GateBase", (0.8, 1.6, 0.30), (gate_x, 0, BZ + 0.15), m['stone_light'])
    bmesh_box("GateHall", (0.7, 1.4, 2.0), (gate_x, 0, BZ + 0.30 + 1.0), m['banner'], bevel=0.02)
    bmesh_box("GateBeam", (0.80, 1.55, 0.08), (gate_x, 0, BZ + 2.30), m['wood_beam'])
    _chinese_roof("GateRoof", 0.35, 0.7, 0.6, 0.28, 0.15,
                  (gate_x, 0, BZ + 2.38), m['roof'], ridge_w=0.20)

    # Gate opening
    bmesh_box("GateDoor", (0.10, 0.60, 1.40), (gate_x + 0.36, 0, BZ + 1.0), m['door'])

    # Gold door studs
    for gz in [BZ + 0.6, BZ + 1.0, BZ + 1.4]:
        for gy in [-0.15, 0.15]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03,
                                                  location=(gate_x + 0.42, gy, gz))
            bpy.context.active_object.name = f"DoorStud_{gz:.1f}_{gy:.1f}"
            bpy.context.active_object.data.materials.append(m['gold'])

    # === Grand hall (Hall of Supreme Harmony style) ===
    hall_w, hall_d = 3.0, 2.4
    hall_h = 2.8

    # Timber columns (6x4)
    for cx in [-1.2, -0.6, 0, 0.6, 1.2]:
        for cy in [-0.9, -0.3, 0.3, 0.9]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.07, depth=hall_h,
                                                location=(cx, cy, BZ + hall_h / 2))
            col = bpy.context.active_object
            col.name = f"HCol_{cx:.1f}_{cy:.1f}"
            col.data.materials.append(m['wood_dark'])

    # Red walls
    bmesh_box("HWallF", (0.10, hall_d, hall_h * 0.7), (hall_w / 2 - 0.05, 0, BZ + hall_h * 0.35), m['banner'])
    bmesh_box("HWallB", (0.10, hall_d, hall_h * 0.7), (-hall_w / 2 + 0.05, 0, BZ + hall_h * 0.35), m['banner'])
    bmesh_box("HWallR", (hall_w, 0.10, hall_h * 0.7), (0, -hall_d / 2 + 0.05, BZ + hall_h * 0.35), m['banner'])
    bmesh_box("HWallL", (hall_w, 0.10, hall_h * 0.7), (0, hall_d / 2 - 0.05, BZ + hall_h * 0.35), m['banner'])

    # Beam structure
    bmesh_box("HallBeam", (hall_w + 0.20, hall_d + 0.20, 0.10), (0, 0, BZ + hall_h), m['wood_beam'])

    # Double-eaved hip roof (lower eave)
    lower_roof_z = BZ + hall_h + 0.05
    _chinese_roof("LowerEave", hall_w / 2, hall_d / 2, 0.6, 0.55, 0.28,
                  (0, 0, lower_roof_z), m['roof'], ridge_w=0.6)

    # Upper roof (sits above lower, steeper)
    upper_roof_z = lower_roof_z + 0.6
    _chinese_roof("UpperEave", hall_w / 2 - 0.3, hall_d / 2 - 0.25, 1.2, 0.45, 0.25,
                  (0, 0, upper_roof_z), m['roof'], ridge_w=0.4)

    # Gold roof ridge ornaments
    ridge_z = upper_roof_z + 1.2
    bmesh_box("GoldRidge", (0.80, 0.06, 0.08), (0, 0, ridge_z), m['gold'])
    for dx in [-0.45, 0.45]:
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.06, radius2=0.02, depth=0.15,
                                         location=(dx, 0, ridge_z + 0.10))
        bpy.context.active_object.name = f"RidgeEnd_{dx:.1f}"
        bpy.context.active_object.data.materials.append(m['gold'])

    # Chiwen (owl-tail ridge beasts) at ridge ends
    for dx in [-0.50, 0.50]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(dx, 0, ridge_z + 0.12))
        bpy.context.active_object.name = f"Chiwen_{dx:.1f}"
        bpy.context.active_object.scale = (0.6, 1.0, 1.2)
        bpy.context.active_object.data.materials.append(m['gold'])

    # Hall windows
    for y in [-0.7, -0.25, 0.25, 0.7]:
        bmesh_box(f"HWin_{y:.1f}", (0.06, 0.18, 0.55), (hall_w / 2, y, BZ + 1.5), m['window'])
        bmesh_box(f"HWinF_{y:.1f}", (0.07, 0.22, 0.04), (hall_w / 2 + 0.01, y, BZ + 1.80), m['wood_beam'])

    # Main door
    bmesh_box("HallDoor", (0.08, 0.60, 1.40), (hall_w / 2, 0, BZ + 0.70), m['door'])

    # === Grand staircase (central spirit way) ===
    for i in range(8):
        bmesh_box(f"Step_{i}", (0.22, 2.6, 0.06),
                  (gate_x + 0.65 + i * 0.22, 0, BZ - 0.04 - i * 0.07), m['stone_light'])

    # Dragon carved ramp (spirit way between stairs)
    sv = [(gate_x + 0.10, -0.30, BZ), (gate_x + 0.10, 0.30, BZ),
          (gate_x + 2.30, 0.30, Z + 0.06), (gate_x + 2.30, -0.30, Z + 0.06)]
    mesh_from_pydata("SpiritWay", sv, [(0, 1, 2, 3)], m['stone_trim'])


# ============================================================
# ENLIGHTENMENT AGE — Qing dynasty imperial hall
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (6.0, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Triple marble platform with balustrades ===
    for i, (pw, pd, ph) in enumerate([(5.8, 5.4, 0.18), (5.2, 4.8, 0.16), (4.6, 4.2, 0.14)]):
        z_base = Z + sum([0.18, 0.16, 0.14][:i]) + ph / 2
        bmesh_box(f"MPlat_{i}", (pw, pd, ph), (0, 0, z_base), m['stone_light'], bevel=0.04)

    plat_top = Z + 0.48

    # Marble balustrade posts on each tier
    for tier, (tw, td, tz) in enumerate([
        (5.8, 5.4, Z + 0.18),
        (5.2, 4.8, Z + 0.34),
        (4.6, 4.2, Z + 0.48),
    ]):
        for i in range(int(tw / 0.45)):
            bx = -tw / 2 + 0.2 + i * 0.45
            for by in [-td / 2, td / 2]:
                bmesh_box(f"Bal_{tier}_{i}_{by:.1f}", (0.05, 0.05, 0.18),
                          (bx, by, tz + 0.09), m['stone_light'])

    BZ = plat_top

    # === Ornate multi-tier main structure ===
    # First tier: base hall
    hall_w, hall_d = 3.2, 2.6
    f1_h = 2.6

    # Dragon pillars (red columns with decorative bases)
    for cx in [-1.2, -0.6, 0, 0.6, 1.2]:
        for cy in [-1.0, -0.33, 0.33, 1.0]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=f1_h,
                                                location=(cx, cy, BZ + f1_h / 2))
            col = bpy.context.active_object
            col.name = f"DPillar_{cx:.1f}_{cy:.1f}"
            col.data.materials.append(m['wood_dark'])
            # Column base
            bmesh_box(f"PBase_{cx:.1f}_{cy:.1f}", (0.20, 0.20, 0.08),
                      (cx, cy, BZ + 0.04), m['stone_light'])

    # Red walls
    bmesh_box("F1WallF", (0.10, hall_d, f1_h * 0.65), (hall_w / 2 - 0.05, 0, BZ + f1_h * 0.325), m['banner'])
    bmesh_box("F1WallB", (0.10, hall_d, f1_h * 0.65), (-hall_w / 2 + 0.05, 0, BZ + f1_h * 0.325), m['banner'])
    bmesh_box("F1WallR", (hall_w, 0.10, f1_h * 0.65), (0, -hall_d / 2 + 0.05, BZ + f1_h * 0.325), m['banner'])
    bmesh_box("F1WallL", (hall_w, 0.10, f1_h * 0.65), (0, hall_d / 2 - 0.05, BZ + f1_h * 0.325), m['banner'])

    # Dougong bracket sets under eaves
    for cx in [-1.3, -0.65, 0, 0.65, 1.3]:
        _dougong_bracket(f"DG_F_{cx:.1f}", cx, -hall_d / 2 - 0.02, BZ + f1_h - 0.12, m['wood_beam'])
        _dougong_bracket(f"DG_B_{cx:.1f}", cx, hall_d / 2 + 0.02, BZ + f1_h - 0.12, m['wood_beam'])
    for cy in [-0.9, -0.3, 0.3, 0.9]:
        _dougong_bracket(f"DG_R_{cy:.1f}", hall_w / 2 + 0.02, cy, BZ + f1_h - 0.12, m['wood_beam'])
        _dougong_bracket(f"DG_L_{cy:.1f}", -hall_w / 2 - 0.02, cy, BZ + f1_h - 0.12, m['wood_beam'])

    # Beam
    bmesh_box("F1Beam", (hall_w + 0.24, hall_d + 0.24, 0.10), (0, 0, BZ + f1_h), m['wood_beam'])

    # First tier roof — yellow glazed tiles (using gold material)
    roof1_z = BZ + f1_h + 0.05
    _chinese_roof("Roof1", hall_w / 2, hall_d / 2, 0.7, 0.55, 0.30,
                  (0, 0, roof1_z), m['gold'], ridge_w=0.6)

    # Second tier
    f2_w, f2_d = 2.2, 1.8
    f2_h = 2.0
    f2_z = roof1_z + 0.7

    bmesh_box("F2Hall", (f2_w, f2_d, f2_h), (0, 0, f2_z + f2_h / 2), m['banner'], bevel=0.02)

    # Dougong on second tier
    for cx in [-0.8, 0, 0.8]:
        _dougong_bracket(f"DG2_F_{cx:.1f}", cx, -f2_d / 2 - 0.02, f2_z + f2_h - 0.12, m['wood_beam'])
        _dougong_bracket(f"DG2_B_{cx:.1f}", cx, f2_d / 2 + 0.02, f2_z + f2_h - 0.12, m['wood_beam'])

    bmesh_box("F2Beam", (f2_w + 0.16, f2_d + 0.16, 0.08), (0, 0, f2_z + f2_h), m['wood_beam'])

    # Second tier roof — yellow glazed
    roof2_z = f2_z + f2_h + 0.03
    _chinese_roof("Roof2", f2_w / 2, f2_d / 2, 0.6, 0.40, 0.22,
                  (0, 0, roof2_z), m['gold'], ridge_w=0.4)

    # Third tier (small crown)
    f3_w, f3_d = 1.2, 1.0
    f3_h = 1.2
    f3_z = roof2_z + 0.6

    bmesh_box("F3Hall", (f3_w, f3_d, f3_h), (0, 0, f3_z + f3_h / 2), m['banner'], bevel=0.02)
    bmesh_box("F3Beam", (f3_w + 0.12, f3_d + 0.12, 0.06), (0, 0, f3_z + f3_h), m['wood_beam'])

    roof3_z = f3_z + f3_h + 0.02
    _chinese_roof("Roof3", f3_w / 2, f3_d / 2, 0.5, 0.30, 0.18,
                  (0, 0, roof3_z), m['gold'], ridge_w=0.0)

    # Golden roof finial (baoding)
    finial_z = roof3_z + 0.5
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0, 0, finial_z))
    bpy.context.active_object.name = "Baoding"
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.05, radius2=0.02, depth=0.15,
                                     location=(0, 0, finial_z + 0.15))
    bpy.context.active_object.name = "BaodingSpire"
    bpy.context.active_object.data.materials.append(m['gold'])

    # Windows on first tier
    for y in [-0.8, -0.3, 0.3, 0.8]:
        bmesh_box(f"F1Win_{y:.1f}", (0.06, 0.18, 0.55), (hall_w / 2, y, BZ + 1.5), m['window'])
        bmesh_box(f"F1WinF_{y:.1f}", (0.07, 0.22, 0.04), (hall_w / 2 + 0.01, y, BZ + 1.80), m['wood_beam'])

    # Grand door with lattice pattern
    bmesh_box("Door", (0.08, 0.65, 1.50), (hall_w / 2, 0, BZ + 0.75), m['door'])
    bmesh_box("DoorFrame", (0.09, 0.75, 0.06), (hall_w / 2 + 0.01, 0, BZ + 1.52), m['wood_beam'])
    # Lattice bars on door
    for gy in [-0.20, 0, 0.20]:
        bmesh_box(f"Lattice_V_{gy:.1f}", (0.09, 0.02, 1.20), (hall_w / 2 + 0.01, gy, BZ + 0.90), m['wood_beam'])
    for gz in [BZ + 0.50, BZ + 0.80, BZ + 1.10, BZ + 1.40]:
        bmesh_box(f"Lattice_H_{gz:.1f}", (0.09, 0.60, 0.02), (hall_w / 2 + 0.01, 0, gz), m['wood_beam'])

    # === Grand stairs with dragon-carved spirit way ===
    stair_x = hall_w / 2 + 0.25
    for i in range(8):
        bmesh_box(f"Step_{i}", (0.22, 2.8, 0.06),
                  (stair_x + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_light'])

    # Spirit way dragon carving
    sw = [(stair_x, -0.30, BZ), (stair_x, 0.30, BZ),
          (stair_x + 1.76, 0.30, Z + 0.06), (stair_x + 1.76, -0.30, Z + 0.06)]
    mesh_from_pydata("SpiritWay", sw, [(0, 1, 2, 3)], m['stone_trim'])


# ============================================================
# INDUSTRIAL AGE — Late Qing/Republic hybrid
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (6.5, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.15
    bmesh_box("Found", (6.0, 5.0, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.04)

    # === Main building — Western brick with Chinese roof ===
    main_w, main_d = 3.6, 2.8
    main_h = 3.2
    bmesh_box("MainHall", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone'], bevel=0.03)

    # Brick coursing bands
    for bz in [BZ + 0.8, BZ + 1.6, BZ + 2.4]:
        bmesh_box(f"BrickBand_{bz:.1f}", (main_w + 0.04, main_d + 0.04, 0.06),
                  (0, 0, bz), m['stone_trim'], bevel=0.01)

    # Cornice molding (Western style)
    bmesh_box("Cornice", (main_w + 0.10, main_d + 0.10, 0.12), (0, 0, BZ + main_h), m['stone_trim'], bevel=0.03)

    # Chinese hip roof on top (glazed tiles)
    _chinese_roof("MainRoof", main_w / 2, main_d / 2, 1.3, 0.50, 0.25,
                  (0, 0, BZ + main_h + 0.06), m['roof'], ridge_w=0.5)

    # Gold ridge ornaments
    ridge_z = BZ + main_h + 1.36
    bmesh_box("GoldRidge", (1.0, 0.06, 0.06), (0, 0, ridge_z), m['gold'])
    for dx in [-0.55, 0.55]:
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.05, radius2=0.02, depth=0.12,
                                         location=(dx, 0, ridge_z + 0.08))
        bpy.context.active_object.name = f"RidgeEnd_{dx:.1f}"
        bpy.context.active_object.data.materials.append(m['gold'])

    # Windows (Western arched style, 3 rows x 4 cols)
    for row, z_off in enumerate([0.3, 1.2, 2.1]):
        for y in [-0.9, -0.3, 0.3, 0.9]:
            h = 0.55 if row < 2 else 0.45
            bmesh_box(f"Win_{row}_{y:.1f}", (0.07, 0.22, h),
                      (main_w / 2 + 0.01, y, BZ + z_off + 0.10), m['window'])
            # Arched top (small semicircle suggestion)
            bmesh_box(f"WinArch_{row}_{y:.1f}", (0.08, 0.26, 0.04),
                      (main_w / 2 + 0.02, y, BZ + z_off + h / 2 + 0.12), m['stone_trim'])

    # === Grand entrance with Chinese arch ===
    entrance_x = main_w / 2
    # Western columns
    for gy in [-0.50, 0.50]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.10, depth=2.5,
                                            location=(entrance_x + 0.45, gy, BZ + 1.25))
        col = bpy.context.active_object
        col.name = f"EntCol_{gy:.1f}"
        col.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()

    # Portico roof — Chinese curved
    bmesh_box("PorticoBeam", (0.50, 1.2, 0.08), (entrance_x + 0.45, 0, BZ + 2.54), m['wood_beam'])
    _chinese_roof("PorticoRoof", 0.25, 0.60, 0.45, 0.20, 0.12,
                  (entrance_x + 0.45, 0, BZ + 2.62), m['roof'], ridge_w=0.10)

    # Door
    bmesh_box("Door", (0.10, 0.80, 1.70), (entrance_x + 0.01, 0, BZ + 0.85), m['door'])

    # === Clock tower (Western style but with Chinese cap) ===
    TX, TY = -main_w / 2 + 0.5, -main_d / 2 + 0.5
    ct_base_z = BZ + main_h + 0.12
    tower_w = 0.9
    tower_h = 3.0
    bmesh_box("ClockTower", (tower_w, tower_w, tower_h),
              (TX, TY, ct_base_z + tower_h / 2), m['stone'], bevel=0.03)
    bmesh_box("CTCornice", (tower_w + 0.08, tower_w + 0.08, 0.08),
              (TX, TY, ct_base_z + tower_h), m['stone_trim'], bevel=0.02)

    # Clock face
    for dx, dy, rot in [(tower_w / 2 + 0.01, 0, (0, math.radians(90), 0)),
                        (0, -tower_w / 2 - 0.01, (math.radians(90), 0, 0))]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.25, depth=0.04,
                                            location=(TX + dx, TY + dy, ct_base_z + tower_h * 0.65))
        cl = bpy.context.active_object
        cl.name = f"Clock_{dx:.1f}_{dy:.1f}"
        cl.rotation_euler = rot
        cl.data.materials.append(m['gold'])

    # Chinese-style cap on clock tower
    _chinese_roof("CTRoof", tower_w / 2 - 0.05, tower_w / 2 - 0.05, 0.6, 0.25, 0.15,
                  (TX, TY, ct_base_z + tower_h + 0.04), m['roof'], ridge_w=0.0)

    # === Grand staircase ===
    for i in range(7):
        bmesh_box(f"Step_{i}", (0.22, 2.0, 0.06),
                  (entrance_x + 0.70 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_dark'])

    # === Side wing (offices/administration) ===
    wing_w, wing_d, wing_h = 1.4, 1.6, 2.2
    for ys, lbl in [(-2.0, "R"), (2.0, "L")]:
        bmesh_box(f"Wing_{lbl}", (wing_w, wing_d, wing_h),
                  (0.3, ys, BZ + wing_h / 2), m['stone'], bevel=0.02)
        bmesh_box(f"WingCornice_{lbl}", (wing_w + 0.06, wing_d + 0.06, 0.06),
                  (0.3, ys, BZ + wing_h), m['stone_trim'], bevel=0.02)
        # Chinese hip roof on wing
        _chinese_roof(f"WingRoof_{lbl}", wing_w / 2, wing_d / 2, 0.6, 0.25, 0.15,
                      (0.3, ys, BZ + wing_h + 0.03), m['roof'], ridge_w=0.2)
        # Wing windows
        for wy in [-0.45, 0, 0.45]:
            actual_y = ys + wy
            bmesh_box(f"WWin_{lbl}_{wy:.1f}", (0.07, 0.18, 0.50),
                      (0.3 + wing_w / 2 + 0.01, actual_y, BZ + 1.2), m['window'])

    # Iron fence along front
    for i in range(14):
        fy = -1.8 + i * 0.27
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.6,
                                            location=(entrance_x + 1.2, fy, BZ + 0.15))
        bpy.context.active_object.data.materials.append(m['iron'])


# ============================================================
# MODERN AGE — Great Hall of the People style
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (7.0, 6.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.12
    bmesh_box("Found", (6.5, 5.8, 0.12), (0, 0, Z + 0.06), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Grand platform ===
    bmesh_box("Platform", (6.2, 5.4, 0.20), (0, 0, BZ + 0.10), m['stone_light'], bevel=0.05)

    BZ = BZ + 0.20

    # === Main building (wide, monumental) ===
    main_w, main_d = 5.0, 3.5
    main_h = 3.8
    bmesh_box("MainHall", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone'], bevel=0.02)

    # Flat roof with Chinese-style cornice (overhanging eave-like cap)
    bmesh_box("RoofSlab", (main_w + 0.15, main_d + 0.15, 0.15), (0, 0, BZ + main_h + 0.075), m['stone_dark'])
    # Chinese cornice overhang
    bmesh_box("CorniceFront", (0.12, main_d + 0.20, 0.25), (main_w / 2 + 0.10, 0, BZ + main_h + 0.15 + 0.125), m['stone_trim'], bevel=0.02)
    bmesh_box("CorniceBack", (0.12, main_d + 0.20, 0.25), (-main_w / 2 - 0.10, 0, BZ + main_h + 0.15 + 0.125), m['stone_trim'], bevel=0.02)
    bmesh_box("CorniceR", (main_w + 0.30, 0.12, 0.25), (0, -main_d / 2 - 0.10, BZ + main_h + 0.15 + 0.125), m['stone_trim'], bevel=0.02)
    bmesh_box("CorniceL", (main_w + 0.30, 0.12, 0.25), (0, main_d / 2 + 0.10, BZ + main_h + 0.15 + 0.125), m['stone_trim'], bevel=0.02)

    # === Grand columned facade (Great Hall style) ===
    n_cols = 10
    col_start_y = -2.2
    col_step = 0.49
    col_h = 3.4
    for i in range(n_cols):
        cy = col_start_y + i * col_step
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.10, depth=col_h,
                                            location=(main_w / 2 + 0.30, cy, BZ + col_h / 2 + 0.20))
        col = bpy.context.active_object
        col.name = f"FacadeCol_{i}"
        col.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        # Column base
        bmesh_box(f"ColBase_{i}", (0.24, 0.24, 0.10),
                  (main_w / 2 + 0.30, cy, BZ + 0.25), m['stone_light'])
        # Column capital
        bmesh_box(f"ColCap_{i}", (0.24, 0.24, 0.08),
                  (main_w / 2 + 0.30, cy, BZ + col_h + 0.24), m['stone_trim'])

    # Entablature above columns
    bmesh_box("Entablature", (0.40, main_d + 0.40, 0.20),
              (main_w / 2 + 0.30, 0, BZ + col_h + 0.32), m['stone_trim'], bevel=0.02)

    # Portico ceiling
    bmesh_box("PorticoCeiling", (0.55, main_d + 0.20, 0.06),
              (main_w / 2 + 0.28, 0, BZ + main_h - 0.03), m['stone_light'])

    # === Red star emblem (above entrance) ===
    star_z = BZ + main_h + 0.55
    star_x = main_w / 2 + 0.30
    # Star as a simple 5-pointed shape approximated by a sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.20, location=(star_x, 0, star_z))
    star = bpy.context.active_object
    star.name = "RedStar"
    star.scale = (0.15, 1.0, 1.0)
    star.data.materials.append(m['banner'])
    bpy.ops.object.shade_smooth()

    # Chinese national emblem (simplified gold circle)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.25, depth=0.04,
                                        location=(star_x, 0, BZ + main_h - 0.50))
    emblem = bpy.context.active_object
    emblem.name = "Emblem"
    emblem.rotation_euler = (0, math.radians(90), 0)
    emblem.data.materials.append(m['gold'])

    # === Main entrance doors ===
    for dy in [-0.35, 0.35]:
        bmesh_box(f"Door_{dy:.1f}", (0.08, 0.55, 2.20),
                  (main_w / 2 + 0.01, dy, BZ + 1.30), m['door'])

    # Side windows (recessed)
    for y in [-1.5, -0.8, 0.8, 1.5]:
        bmesh_box(f"SWin_{y:.1f}", (0.07, 0.30, 1.50),
                  (main_w / 2 + 0.01, y, BZ + 2.0), glass)

    # === Wide ceremonial stairs ===
    for i in range(8):
        bmesh_box(f"Step_{i}", (0.22, 4.0, 0.06),
                  (main_w / 2 + 0.55 + i * 0.22, 0, BZ - 0.04 - i * 0.04), m['stone_light'])

    # === Flag poles ===
    for fy in [-2.5, 2.5]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=3.5,
                                            location=(main_w / 2 + 1.5, fy, BZ + 1.75))
        pole = bpy.context.active_object
        pole.name = f"FlagPole_{fy:.1f}"
        pole.data.materials.append(metal)
        # Flag
        fz_base = BZ + 3.20
        fv = [(main_w / 2 + 1.53, fy, fz_base), (main_w / 2 + 2.10, fy + 0.03, fz_base - 0.05),
              (main_w / 2 + 2.10, fy + 0.02, fz_base + 0.30), (main_w / 2 + 1.53, fy, fz_base + 0.28)]
        mesh_from_pydata(f"Flag_{fy:.1f}", fv, [(0, 1, 2, 3)], m['banner'])
        m['banner'].use_backface_culling = False

    # === Plaza with garden beds ===
    for gx, gy in [(main_w / 2 + 1.8, -1.0), (main_w / 2 + 1.8, 1.0)]:
        bmesh_box(f"Garden_{gx:.1f}_{gy:.1f}", (0.6, 0.6, 0.12),
                  (gx, gy, BZ + 0.06), m['ground'])

    # Roof HVAC (simplified)
    bmesh_box("HVAC", (0.8, 0.6, 0.35), (-1.5, 0, BZ + main_h + 0.15 + 0.175), m['stone_dark'])


# ============================================================
# DIGITAL AGE — Futuristic Chinese glass pagoda
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (7.0, 6.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.08
    bmesh_box("Found", (6.5, 5.5, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Floating garden platforms (3 elliptical tiers) ===
    for i, (gr, gz) in enumerate([(1.8, BZ + 0.05), (1.2, BZ + 2.5), (0.8, BZ + 5.0)]):
        bmesh_prism(f"GardenPlat_{i}", gr, 0.06, 16, (-2.0, 1.5, gz), m['ground'])
        # Support struts from below
        if i > 0:
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=gz - BZ,
                                                location=(-2.0, 1.5, BZ + (gz - BZ) / 2))
            strut = bpy.context.active_object
            strut.name = f"GardenStrut_{i}"
            strut.data.materials.append(metal)
    # Small trees/plants on garden platforms
    for gx, gy, gz in [(-2.4, 1.8, BZ + 0.11), (-1.6, 1.2, BZ + 0.11),
                        (-2.0, 1.5, BZ + 2.56)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(gx, gy, gz + 0.15))
        tree = bpy.context.active_object
        tree.name = f"TreeCanopy_{gx:.1f}_{gy:.1f}"
        tree.scale = (1.0, 1.0, 0.8)
        tree.data.materials.append(m['ground'])

    # === Main glass pagoda tower ===
    # 5 tiers, each smaller than the last, with LED-lit curved roofs
    tiers = [
        # (width, depth, height, roof_overhang, eave_lift)
        (2.4, 2.0, 1.8, 0.50, 0.25),
        (2.0, 1.6, 1.5, 0.42, 0.22),
        (1.6, 1.3, 1.3, 0.35, 0.20),
        (1.2, 1.0, 1.1, 0.28, 0.18),
        (0.8, 0.7, 0.9, 0.22, 0.15),
    ]

    tier_z = BZ
    for ti, (tw, td, th, t_ovh, t_lift) in enumerate(tiers):
        # Glass walls for each tier
        bmesh_box(f"Tier_{ti}", (tw, td, th), (0, 0, tier_z + th / 2), glass)

        # Steel frame on each tier
        bmesh_box(f"TFrame_top_{ti}", (tw + 0.02, td + 0.02, 0.04), (0, 0, tier_z + th), metal)
        bmesh_box(f"TFrame_bot_{ti}", (tw + 0.02, td + 0.02, 0.04), (0, 0, tier_z), metal)
        # Vertical mullions
        for mx in [-tw / 2, 0, tw / 2]:
            bmesh_box(f"TMullF_{ti}_{mx:.1f}", (0.03, 0.03, th), (mx, -td / 2, tier_z + th / 2), metal)
            bmesh_box(f"TMullB_{ti}_{mx:.1f}", (0.03, 0.03, th), (mx, td / 2, tier_z + th / 2), metal)
        for my in [-td / 2, 0, td / 2]:
            bmesh_box(f"TMullR_{ti}_{my:.1f}", (0.03, 0.03, th), (tw / 2, my, tier_z + th / 2), metal)
            bmesh_box(f"TMullL_{ti}_{my:.1f}", (0.03, 0.03, th), (-tw / 2, my, tier_z + th / 2), metal)

        # LED-lit curved roof tier
        roof_z = tier_z + th + 0.02
        _chinese_roof(f"TierRoof_{ti}", tw / 2, td / 2, 0.35, t_ovh, t_lift,
                      (0, 0, roof_z), glass, ridge_w=tw * 0.15)

        # LED accent strips on roof edges (glowing gold)
        led_z = roof_z - 0.02
        bmesh_box(f"LED_F_{ti}", (tw + t_ovh * 2, 0.04, 0.04),
                  (0, -td / 2 - t_ovh, led_z + t_lift), m['gold'])
        bmesh_box(f"LED_B_{ti}", (tw + t_ovh * 2, 0.04, 0.04),
                  (0, td / 2 + t_ovh, led_z + t_lift), m['gold'])
        bmesh_box(f"LED_R_{ti}", (0.04, td + t_ovh * 2, 0.04),
                  (tw / 2 + t_ovh, 0, led_z + t_lift), m['gold'])
        bmesh_box(f"LED_L_{ti}", (0.04, td + t_ovh * 2, 0.04),
                  (-tw / 2 - t_ovh, 0, led_z + t_lift), m['gold'])

        tier_z = roof_z + 0.35 + 0.05  # next tier base

    # === Holographic dragon ===
    # Represent as a sinuous line of semi-transparent spheres spiraling up
    dragon_h_start = BZ + 2.0
    dragon_radius = 1.8
    n_segments = 18
    for i in range(n_segments):
        t = i / n_segments
        angle = t * math.pi * 3  # 1.5 full spirals
        dz = dragon_h_start + t * 4.5
        dx = dragon_radius * math.cos(angle) * (1.0 - t * 0.4)
        dy = dragon_radius * math.sin(angle) * (1.0 - t * 0.4)
        sphere_r = 0.10 - t * 0.04  # taper toward tail
        bpy.ops.mesh.primitive_uv_sphere_add(radius=sphere_r, location=(dx, dy, dz))
        seg = bpy.context.active_object
        seg.name = f"Dragon_{i}"
        seg.data.materials.append(m['gold'])
        bpy.ops.object.shade_smooth()

    # Dragon head (larger sphere with cone horns)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(dragon_radius * 0.6, 0, BZ + 2.0))
    dhead = bpy.context.active_object
    dhead.name = "DragonHead"
    dhead.scale = (1.3, 0.8, 0.9)
    dhead.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()
    # Horns
    for dy in [-0.08, 0.08]:
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.04, radius2=0.01, depth=0.20,
                                         location=(dragon_radius * 0.6 + 0.05, dy, BZ + 2.20))
        horn = bpy.context.active_object
        horn.name = f"DragonHorn_{dy:.2f}"
        horn.rotation_euler = (0, -0.4, 0)
        horn.data.materials.append(m['gold'])

    # === Communication spire on top ===
    spire_z = tier_z - 0.05
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=2.0,
                                        location=(0, 0, spire_z + 1.0))
    bpy.context.active_object.name = "Spire"
    bpy.context.active_object.data.materials.append(metal)
    # Cross bars
    for sz in [0.4, 0.8, 1.2, 1.6]:
        bmesh_box(f"SpireX_{sz:.1f}", (0.5, 0.02, 0.02), (0, 0, spire_z + sz), metal)
        bmesh_box(f"SpireY_{sz:.1f}", (0.02, 0.5, 0.02), (0, 0, spire_z + sz), metal)

    # === Glass entrance atrium ===
    bmesh_box("Atrium", (1.0, 2.2, 2.2), (1.8, 0, BZ + 1.1), glass)
    bmesh_box("AtrFrame", (1.02, 2.22, 0.04), (1.8, 0, BZ + 2.22), metal)
    bmesh_box("AtrDoor", (0.06, 1.0, 1.8), (2.31, 0, BZ + 0.9), glass)
    bmesh_box("DoorFrame", (0.07, 1.1, 0.04), (2.32, 0, BZ + 1.82), metal)

    # LED path lights along entrance
    for i in range(5):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.25,
                                            location=(2.5 + i * 0.30, -0.6, BZ + 0.125))
        light = bpy.context.active_object
        light.name = f"PathLight_{i}"
        light.data.materials.append(m['gold'])


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


def build_town_center_chinese(materials, age='medieval'):
    """Build a Chinese Nation Town Center with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
