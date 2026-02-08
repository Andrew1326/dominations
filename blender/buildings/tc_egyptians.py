"""
Egyptian Town Center — culturally authentic architecture per age.

Stone:         Reed and mud-brick compound — circular mud walls, reed roof, fire pit, grain pit
Bronze:        Early dynasty mastaba complex — flat-topped tomb-palace, niched facade, obelisk
Iron:          Temple-palace with pylon gateway — massive tapered pylons, columned hall, sun disk
Classical:     Ptolemaic palace — Egyptian-Greek fusion, hypostyle hall, sphinx, obelisks
Medieval:      Islamic Cairo citadel — thick walls, towers, minaret, courtyard fountain
Gunpowder:     Mamluk palace — striped stonework, dome, minaret, mashrabiya windows
Enlightenment: Mohamed Ali mosque-palace — large dome, slim minarets, marble columns
Industrial:    Egyptian colonial building — colonnaded facade, clock tower, obelisk
Modern:        Cairo modernist — concrete with geometric patterns, pyramid skylight, palm court
Digital:       Neo-Egyptian high-tech — glass pyramid, gold wireframe, holographic eye, LED hieroglyphs
"""

import bpy
import bmesh
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# ============================================================
# STONE AGE — Reed and mud-brick compound
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Circular mud-brick enclosure wall ===
    wall_r = 2.3
    n_segs = 32
    wall_h = 1.0
    for i in range(n_segs):
        a0 = (2 * math.pi * i) / n_segs
        a1 = (2 * math.pi * (i + 1)) / n_segs
        # Skip a gap for entrance
        if 14 <= i <= 16:
            continue
        x0 = wall_r * math.cos(a0)
        y0 = wall_r * math.sin(a0)
        x1 = wall_r * math.cos(a1)
        y1 = wall_r * math.sin(a1)
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        seg_len = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
        angle = math.atan2(y1 - y0, x1 - x0)
        bm = bmesh.new()
        hw = seg_len / 2 + 0.02
        ht = 0.12
        hh = wall_h / 2
        v = [
            bm.verts.new((-hw, -ht, -hh)), bm.verts.new((hw, -ht, -hh)),
            bm.verts.new((hw, ht, -hh)), bm.verts.new((-hw, ht, -hh)),
            bm.verts.new((-hw, -ht, hh)), bm.verts.new((hw, -ht, hh)),
            bm.verts.new((hw, ht, hh)), bm.verts.new((-hw, ht, hh)),
        ]
        bm.faces.new([v[0], v[3], v[2], v[1]])
        bm.faces.new([v[4], v[5], v[6], v[7]])
        bm.faces.new([v[0], v[1], v[5], v[4]])
        bm.faces.new([v[2], v[3], v[7], v[6]])
        bm.faces.new([v[0], v[4], v[7], v[3]])
        bm.faces.new([v[1], v[2], v[6], v[5]])
        mesh = bpy.data.meshes.new(f"MudWall_{i}")
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(f"MudWall_{i}", mesh)
        bpy.context.collection.objects.link(obj)
        obj.location = (cx, cy, Z + wall_h / 2)
        obj.rotation_euler = (0, 0, angle)
        obj.data.materials.append(m['stone_dark'])

    # Gate posts
    gx = wall_r * math.cos(2 * math.pi * 15 / n_segs)
    gy_l = wall_r * math.sin(2 * math.pi * 14 / n_segs)
    gy_r = wall_r * math.sin(2 * math.pi * 17 / n_segs)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.10, depth=1.4,
                                        location=(gx - 0.1, gy_l, Z + 0.7))
    bpy.context.active_object.name = "GatePostL"
    bpy.context.active_object.data.materials.append(m['wood'])
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.10, depth=1.4,
                                        location=(gx - 0.1, gy_r, Z + 0.7))
    bpy.context.active_object.name = "GatePostR"
    bpy.context.active_object.data.materials.append(m['wood'])
    bmesh_box("GateLintel", (0.14, abs(gy_l - gy_r) + 0.2, 0.10),
              (gx - 0.1, (gy_l + gy_r) / 2, Z + 1.4), m['wood_dark'])

    # === Central great hut (reed roof) ===
    bmesh_prism("HutBase", 1.3, 0.15, 16, (0, 0, Z), m['stone_dark'])
    bmesh_prism("HutWall", 1.25, 1.6, 16, (0, 0, Z + 0.15), m['stone'])
    bmesh_cone("HutRoof", 1.7, 1.8, 16, (0, 0, Z + 1.75), m['roof'])
    # Smoke hole ring
    bmesh_prism("SmokeHole", 0.18, 0.12, 8, (0, 0, Z + 3.50), m['wood'])

    # Reed bundles supporting roof
    for i in range(8):
        a = (2 * math.pi * i) / 8
        px, py = 1.15 * math.cos(a), 1.15 * math.sin(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=1.8,
                                            location=(px, py, Z + 0.95))
        pole = bpy.context.active_object
        pole.name = f"ReedPole_{i}"
        pole.data.materials.append(m['wood'])

    # Door opening
    bmesh_box("Door", (0.10, 0.50, 0.95), (1.26, 0, Z + 0.62), m['door'])

    # === Grain storage pit (sunken circle) ===
    bmesh_prism("GrainPit", 0.55, 0.08, 12, (-1.3, -1.0, Z + 0.04), m['stone_dark'])
    bmesh_prism("GrainRim", 0.60, 0.12, 12, (-1.3, -1.0, Z), m['wood_dark'])
    # Cover (woven mat)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.50, depth=0.04,
                                        location=(-1.3, -1.0, Z + 0.14))
    bpy.context.active_object.name = "GrainCover"
    bpy.context.active_object.data.materials.append(m['roof'])

    # === Central fire pit ===
    bmesh_prism("FirePit", 0.40, 0.10, 10, (1.2, -0.9, Z + 0.05), m['stone_dark'])
    # Fire logs
    for angle_off in [0.2, -0.3, 0.7, -0.6]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.035, depth=0.4,
                                            location=(1.2, -0.9, Z + 0.12))
        log = bpy.context.active_object
        log.name = f"FireLog_{angle_off:.1f}"
        log.rotation_euler = (0.3, angle_off, 0)
        log.data.materials.append(m['wood_dark'])

    # === Secondary smaller hut ===
    bmesh_prism("Hut2Wall", 0.60, 0.9, 10, (1.0, 1.1, Z + 0.08), m['stone'])
    bmesh_cone("Hut2Roof", 0.80, 1.0, 12, (1.0, 1.1, Z + 0.98), m['roof'])

    # === Reed drying rack ===
    for dx in [-0.3, 0.3]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=1.2,
                                            location=(-1.5 + dx, 1.3, Z + 0.6))
        bpy.context.active_object.name = f"DryPole_{dx:.1f}"
        bpy.context.active_object.data.materials.append(m['wood'])
    bmesh_box("DryBar", (0.04, 0.70, 0.04), (-1.5, 1.3, Z + 1.2), m['wood'])

    # Hanging reed bundles
    for dy in [-0.15, 0.15]:
        bmesh_box(f"ReedBundle_{dy:.1f}", (0.08, 0.08, 0.35),
                  (-1.5, 1.3 + dy, Z + 0.85), m['roof_edge'])

    # Clay water jars near hut
    for i, (px, py) in enumerate([(0.7, -1.6), (-0.5, -1.7)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(px, py, Z + 0.08))
        jar = bpy.context.active_object
        jar.name = f"WaterJar_{i}"
        jar.scale = (1, 1, 1.2)
        jar.data.materials.append(m['roof'])


# ============================================================
# BRONZE AGE — Early dynasty mastaba complex
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Enclosure wall with niched facade ===
    hw = 2.2
    wall_h = 1.8
    wt = 0.18

    # Main walls
    bmesh_box("WallF", (wt, hw * 2, wall_h), (hw, 0, Z + wall_h / 2), m['stone'], bevel=0.02)
    bmesh_box("WallB", (wt, hw * 2, wall_h), (-hw, 0, Z + wall_h / 2), m['stone'], bevel=0.02)
    bmesh_box("WallR", (hw * 2, wt, wall_h), (0, -hw, Z + wall_h / 2), m['stone'], bevel=0.02)
    bmesh_box("WallL", (hw * 2, wt, wall_h), (0, hw, Z + wall_h / 2), m['stone'], bevel=0.02)

    # Niched facade (recessed panels on front wall)
    for i in range(8):
        y = -1.6 + i * 0.45
        bmesh_box(f"Niche_{i}", (0.06, 0.20, wall_h - 0.3),
                  (hw + wt / 2 + 0.02, y, Z + (wall_h - 0.3) / 2 + 0.15), m['stone_dark'])

    # Wall top capping
    bmesh_box("WallCapF", (0.24, hw * 2 + 0.06, 0.06), (hw, 0, Z + wall_h + 0.03), m['stone_trim'])
    bmesh_box("WallCapB", (0.24, hw * 2 + 0.06, 0.06), (-hw, 0, Z + wall_h + 0.03), m['stone_trim'])
    bmesh_box("WallCapR", (hw * 2 + 0.06, 0.24, 0.06), (0, -hw, Z + wall_h + 0.03), m['stone_trim'])
    bmesh_box("WallCapL", (hw * 2 + 0.06, 0.24, 0.06), (0, hw, Z + wall_h + 0.03), m['stone_trim'])

    # === Central mastaba (flat-topped rectangular structure) ===
    # Three stepped tiers (like early step pyramid precursor)
    bmesh_box("Mastaba1", (2.6, 2.2, 0.8), (0, 0, Z + 0.40), m['stone'], bevel=0.03)
    bmesh_box("Mastaba2", (2.2, 1.8, 0.7), (0, 0, Z + 0.80 + 0.35), m['stone'], bevel=0.02)
    bmesh_box("Mastaba3", (1.8, 1.4, 0.6), (0, 0, Z + 1.50 + 0.30), m['stone_upper'], bevel=0.02)
    # Flat top platform
    bmesh_box("MastabaTop", (1.9, 1.5, 0.06), (0, 0, Z + 2.13), m['stone_trim'])

    # === Entrance with sloped sides (battered walls) ===
    # Simplified trapezoidal entrance
    bmesh_box("EntranceFrame", (0.20, 0.70, 1.20), (hw + 0.08, 0, Z + 0.60), m['stone_dark'])
    bmesh_box("Door", (0.10, 0.50, 0.95), (hw + 0.10, 0, Z + 0.475), m['door'])

    # === Small obelisk (early form) ===
    ob_x, ob_y = 1.8, -1.8
    ob_h = 1.6
    # Tapered obelisk shaft
    v_ob = [
        (ob_x - 0.12, ob_y - 0.12, Z), (ob_x + 0.12, ob_y - 0.12, Z),
        (ob_x + 0.12, ob_y + 0.12, Z), (ob_x - 0.12, ob_y + 0.12, Z),
        (ob_x - 0.06, ob_y - 0.06, Z + ob_h), (ob_x + 0.06, ob_y - 0.06, Z + ob_h),
        (ob_x + 0.06, ob_y + 0.06, Z + ob_h), (ob_x - 0.06, ob_y + 0.06, Z + ob_h),
    ]
    f_ob = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7), (0, 3, 2, 1)]
    mesh_from_pydata("Obelisk", v_ob, f_ob, m['stone_light'])
    # Pyramidion (small pyramid on top)
    hw_p = 0.06
    pyr_v = [
        (ob_x - hw_p, ob_y - hw_p, Z + ob_h),
        (ob_x + hw_p, ob_y - hw_p, Z + ob_h),
        (ob_x + hw_p, ob_y + hw_p, Z + ob_h),
        (ob_x - hw_p, ob_y + hw_p, Z + ob_h),
        (ob_x, ob_y, Z + ob_h + 0.15),
    ]
    pyr_f = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (0, 1, 2, 3)]
    mesh_from_pydata("Pyramidion", pyr_v, pyr_f, m['gold'])

    # === Offering table ===
    bmesh_box("OfferTable", (0.50, 0.35, 0.08), (0, 1.4, Z + 0.55), m['stone_trim'])
    # Offerings (small objects)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0.1, 1.4, Z + 0.63))
    bpy.context.active_object.name = "Offering1"
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(-0.1, 1.4, Z + 0.62))
    bpy.context.active_object.name = "Offering2"
    bpy.context.active_object.data.materials.append(m['roof'])

    # === Seated statue (guardian) ===
    # Simple block figure
    bmesh_box("StatueBase", (0.30, 0.25, 0.10), (-1.6, 1.6, Z + 0.05), m['stone_dark'])
    bmesh_box("StatueBody", (0.20, 0.18, 0.50), (-1.6, 1.6, Z + 0.35), m['stone_light'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(-1.6, 1.6, Z + 0.70))
    bpy.context.active_object.name = "StatueHead"
    bpy.context.active_object.data.materials.append(m['stone_light'])

    # Steps to entrance
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.20, 1.0, 0.06),
                  (hw + 0.30 + i * 0.22, 0, Z - 0.03 - i * 0.06), m['stone_dark'])

    # Banner pole
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=1.0,
                                        location=(0, 0, Z + 2.66))
    bpy.context.active_object.data.materials.append(m['wood'])
    bv = [(0.04, 0, Z + 2.90), (0.45, 0.03, Z + 2.85),
          (0.45, 0.02, Z + 3.15), (0.04, 0, Z + 3.13)]
    mesh_from_pydata("Banner", bv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# IRON AGE — Temple-palace with pylon gateway
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation platform ===
    bmesh_box("Platform", (5.0, 4.6, 0.20), (0, 0, Z + 0.10), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.20

    # === Two massive pylon towers (tapered, flanking entrance) ===
    pylon_h = 3.5
    pylon_w_base = 1.2
    pylon_w_top = 0.9
    pylon_d = 0.6
    for side, sy in [("L", 0.9), ("R", -0.9)]:
        # Tapered pylon using mesh_from_pydata
        hb = pylon_w_base / 2
        ht = pylon_w_top / 2
        hd = pylon_d / 2
        px = 2.0
        v_pyl = [
            # Bottom face
            (px - hd, sy - hb, BZ), (px + hd, sy - hb, BZ),
            (px + hd, sy + hb, BZ), (px - hd, sy + hb, BZ),
            # Top face (narrower)
            (px - hd * 0.8, sy - ht, BZ + pylon_h), (px + hd * 0.8, sy - ht, BZ + pylon_h),
            (px + hd * 0.8, sy + ht, BZ + pylon_h), (px - hd * 0.8, sy + ht, BZ + pylon_h),
        ]
        f_pyl = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
                 (4, 5, 6, 7), (0, 3, 2, 1)]
        mesh_from_pydata(f"Pylon_{side}", v_pyl, f_pyl, m['stone'])

        # Cavetto cornice (curved top molding — simplified as slab)
        bmesh_box(f"PylonCornice_{side}", (pylon_d * 0.85, pylon_w_top + 0.06, 0.10),
                  (px, sy, BZ + pylon_h + 0.05), m['stone_trim'])

        # Torus molding below cornice
        bmesh_box(f"PylonMold_{side}", (pylon_d * 0.88, pylon_w_top + 0.08, 0.04),
                  (px, sy, BZ + pylon_h - 0.02), m['gold'])

        # Flag pole slots (tall poles on pylons)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=pylon_h + 1.5,
                                            location=(px + hd * 0.8 + 0.03, sy, BZ + (pylon_h + 1.5) / 2))
        bpy.context.active_object.name = f"FlagPole_{side}"
        bpy.context.active_object.data.materials.append(m['wood'])
        # Pennant
        fz = BZ + pylon_h + 0.8
        fv = [(px + hd * 0.8 + 0.06, sy, fz),
              (px + hd * 0.8 + 0.06 + 0.35, sy + 0.02, fz - 0.05),
              (px + hd * 0.8 + 0.06 + 0.35, sy + 0.01, fz + 0.25),
              (px + hd * 0.8 + 0.06, sy, fz + 0.22)]
        mesh_from_pydata(f"Pennant_{side}", fv, [(0, 1, 2, 3)], m['banner'])
        m['banner'].use_backface_culling = False

    # Gateway lintel between pylons
    bmesh_box("GateLintel", (0.55, 0.60, 0.15), (2.0, 0, BZ + 2.5), m['stone_trim'])
    # Gate door
    bmesh_box("GateDoor", (0.10, 0.50, 1.80), (2.25, 0, BZ + 0.90), m['door'])

    # === Columned hall (hypostyle, behind pylons) ===
    hall_w = 3.0
    hall_d = 2.4
    hall_h = 2.8
    # Hall walls
    bmesh_box("HallFloor", (hall_w, hall_d, 0.08), (0, 0, BZ + 0.04), m['stone_dark'])
    bmesh_box("HallWallB", (0.18, hall_d, hall_h), (-hall_w / 2, 0, BZ + hall_h / 2), m['stone'], bevel=0.02)
    bmesh_box("HallWallR", (hall_w, 0.18, hall_h), (0, -hall_d / 2, BZ + hall_h / 2), m['stone'], bevel=0.02)
    bmesh_box("HallWallL", (hall_w, 0.18, hall_h), (0, hall_d / 2, BZ + hall_h / 2), m['stone'], bevel=0.02)

    # Flat roof
    bmesh_box("HallRoof", (hall_w + 0.10, hall_d + 0.10, 0.10), (0, 0, BZ + hall_h + 0.05), m['stone_dark'])
    # Cavetto cornice on roof edge
    bmesh_box("HallCornice", (hall_w + 0.16, hall_d + 0.16, 0.08), (0, 0, BZ + hall_h + 0.14), m['stone_trim'])

    # Columns (papyrus bundle style — octagonal)
    col_h = 2.6
    col_r = 0.10
    col_positions = [
        (-0.8, -0.6), (-0.8, 0.6), (0.2, -0.6), (0.2, 0.6),
        (-0.8, 0), (0.2, 0),
    ]
    for i, (cx, cy) in enumerate(col_positions):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=col_r, depth=col_h,
                                            location=(cx, cy, BZ + col_h / 2))
        col = bpy.context.active_object
        col.name = f"Col_{i}"
        col.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        # Capital (flared top — wider disk)
        bmesh_prism(f"Capital_{i}", col_r + 0.06, 0.10, 8, (cx, cy, BZ + col_h), m['stone_trim'])
        # Base
        bmesh_prism(f"ColBase_{i}", col_r + 0.04, 0.06, 8, (cx, cy, BZ), m['stone_trim'])

    # === Obelisk (in front of pylons) ===
    ob_x, ob_y = 2.5, 0
    ob_h = 2.8
    v_ob = [
        (ob_x - 0.10, ob_y - 0.10, BZ), (ob_x + 0.10, ob_y - 0.10, BZ),
        (ob_x + 0.10, ob_y + 0.10, BZ), (ob_x - 0.10, ob_y + 0.10, BZ),
        (ob_x - 0.05, ob_y - 0.05, BZ + ob_h), (ob_x + 0.05, ob_y - 0.05, BZ + ob_h),
        (ob_x + 0.05, ob_y + 0.05, BZ + ob_h), (ob_x - 0.05, ob_y + 0.05, BZ + ob_h),
    ]
    f_ob = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7), (0, 3, 2, 1)]
    mesh_from_pydata("Obelisk", v_ob, f_ob, m['stone_light'])
    # Gold pyramidion
    hw_p = 0.05
    pv = [
        (ob_x - hw_p, ob_y - hw_p, BZ + ob_h),
        (ob_x + hw_p, ob_y - hw_p, BZ + ob_h),
        (ob_x + hw_p, ob_y + hw_p, BZ + ob_h),
        (ob_x - hw_p, ob_y + hw_p, BZ + ob_h),
        (ob_x, ob_y, BZ + ob_h + 0.18),
    ]
    pf = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (0, 1, 2, 3)]
    mesh_from_pydata("Pyramidion", pv, pf, m['gold'])

    # === Gold sun disk above gate ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.25, depth=0.04,
                                        location=(2.0, 0, BZ + 2.8))
    disk = bpy.context.active_object
    disk.name = "SunDisk"
    disk.rotation_euler = (math.radians(90), 0, 0)
    disk.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # Steps
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.22, 1.6, 0.06),
                  (2.50 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_dark'])


# ============================================================
# CLASSICAL AGE — Ptolemaic palace (Egyptian-Greek fusion)
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (6.0, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Grand stepped platform ===
    for i in range(4):
        w = 5.4 - i * 0.30
        d = 5.0 - i * 0.25
        bmesh_box(f"Plat_{i}", (w, d, 0.10), (0, 0, Z + 0.05 + i * 0.10), m['stone_light'], bevel=0.02)

    BZ = Z + 0.40

    # === Hypostyle hall (central, main structure) ===
    hall_w = 3.4
    hall_d = 2.8
    hall_h = 3.2
    bmesh_box("HallBase", (hall_w, hall_d, 0.15), (0, 0, BZ + 0.075), m['stone_dark'])
    bmesh_box("HallWallB", (0.20, hall_d, hall_h), (-hall_w / 2, 0, BZ + 0.15 + hall_h / 2), m['stone'], bevel=0.02)
    bmesh_box("HallWallR", (hall_w, 0.20, hall_h), (0, -hall_d / 2, BZ + 0.15 + hall_h / 2), m['stone'], bevel=0.02)
    bmesh_box("HallWallL", (hall_w, 0.20, hall_h), (0, hall_d / 2, BZ + 0.15 + hall_h / 2), m['stone'], bevel=0.02)

    # Flat roof with cornice
    roof_z = BZ + 0.15 + hall_h
    bmesh_box("HallRoof", (hall_w + 0.12, hall_d + 0.12, 0.10), (0, 0, roof_z + 0.05), m['stone_dark'])
    bmesh_box("HallCornice", (hall_w + 0.18, hall_d + 0.18, 0.08), (0, 0, roof_z + 0.14), m['stone_trim'])

    # Pyramid roof section on top (Egyptian motif on Greek building)
    hw_pr = 0.8
    pyr_base_z = roof_z + 0.18
    pyr_v = [
        (-hw_pr, -hw_pr, pyr_base_z), (hw_pr, -hw_pr, pyr_base_z),
        (hw_pr, hw_pr, pyr_base_z), (-hw_pr, hw_pr, pyr_base_z),
        (0, 0, pyr_base_z + 1.0),
    ]
    pyr_f = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (0, 1, 2, 3)]
    mesh_from_pydata("PyramidRoof", pyr_v, pyr_f, m['roof'])

    # === Tall lotus columns (3 rows of 3) ===
    col_h = 3.0
    col_r = 0.11
    for cx in [-0.8, 0.2, 1.2]:
        for cy in [-0.7, 0, 0.7]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=col_r, depth=col_h,
                                                location=(cx, cy, BZ + 0.15 + col_h / 2))
            col = bpy.context.active_object
            col.name = f"LotusCol_{cx:.1f}_{cy:.1f}"
            col.data.materials.append(m['stone_light'])
            bpy.ops.object.shade_smooth()
            # Lotus capital (flared shape — wider prism)
            bmesh_prism(f"LotusCap_{cx:.1f}_{cy:.1f}", col_r + 0.08, 0.14, 12,
                        (cx, cy, BZ + 0.15 + col_h), m['stone_trim'])
            # Column base
            bmesh_prism(f"ColBase_{cx:.1f}_{cy:.1f}", col_r + 0.04, 0.06, 12,
                        (cx, cy, BZ + 0.15), m['stone_trim'])

    # === Front colonnade (Greek-style, 5 columns) ===
    front_x = hall_w / 2 + 0.40
    for i, cy in enumerate([-1.1, -0.55, 0, 0.55, 1.1]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=col_r, depth=col_h,
                                            location=(front_x, cy, BZ + 0.15 + col_h / 2))
        col = bpy.context.active_object
        col.name = f"FrontCol_{i}"
        col.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        bmesh_box(f"FrontCap_{i}", (0.26, 0.26, 0.06), (front_x, cy, BZ + 0.15 + col_h + 0.03), m['stone_trim'])

    # Entablature over front columns
    bmesh_box("Entablature", (0.30, 2.8, 0.14), (front_x, 0, BZ + 0.15 + col_h + 0.13), m['stone_trim'], bevel=0.02)

    # Door
    bmesh_box("Door", (0.08, 0.60, 1.50), (hall_w / 2 + 0.01, 0, BZ + 0.15 + 0.75), m['door'])

    # === Obelisks (pair, flanking entrance) ===
    for side, oy in [("L", 1.6), ("R", -1.6)]:
        ob_h = 2.5
        ob_x = front_x + 0.5
        v_ob = [
            (ob_x - 0.08, oy - 0.08, BZ), (ob_x + 0.08, oy - 0.08, BZ),
            (ob_x + 0.08, oy + 0.08, BZ), (ob_x - 0.08, oy + 0.08, BZ),
            (ob_x - 0.04, oy - 0.04, BZ + ob_h), (ob_x + 0.04, oy - 0.04, BZ + ob_h),
            (ob_x + 0.04, oy + 0.04, BZ + ob_h), (ob_x - 0.04, oy + 0.04, BZ + ob_h),
        ]
        f_ob = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7), (0, 3, 2, 1)]
        mesh_from_pydata(f"Obelisk_{side}", v_ob, f_ob, m['stone_light'])
        # Gold pyramidion
        hp = 0.04
        pv = [
            (ob_x - hp, oy - hp, BZ + ob_h), (ob_x + hp, oy - hp, BZ + ob_h),
            (ob_x + hp, oy + hp, BZ + ob_h), (ob_x - hp, oy + hp, BZ + ob_h),
            (ob_x, oy, BZ + ob_h + 0.12),
        ]
        pf = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (0, 1, 2, 3)]
        mesh_from_pydata(f"Pyramidion_{side}", pv, pf, m['gold'])

    # === Sphinx statues (pair, flanking path) ===
    for side, oy in [("L", 2.0), ("R", -2.0)]:
        sx = front_x + 0.8
        # Body (elongated box)
        bmesh_box(f"SphinxBody_{side}", (0.65, 0.28, 0.25), (sx, oy, BZ + 0.125), m['stone_light'])
        # Head
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(sx + 0.25, oy, BZ + 0.38))
        bpy.context.active_object.name = f"SphinxHead_{side}"
        bpy.context.active_object.data.materials.append(m['stone_light'])
        # Headdress (flat top extension)
        bmesh_box(f"SphinxHdress_{side}", (0.08, 0.22, 0.08), (sx + 0.25, oy, BZ + 0.48), m['gold'])

    # Steps
    for i in range(6):
        bmesh_box(f"Step_{i}", (0.22, 2.4, 0.06),
                  (front_x + 0.70 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_light'])

    # Gold sun disk on roof
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.22, depth=0.04,
                                        location=(0, 0, pyr_base_z + 1.05))
    disk = bpy.context.active_object
    disk.name = "SunDisk"
    disk.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()


# ============================================================
# MEDIEVAL AGE — Islamic Cairo citadel
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Heavy foundation ===
    bmesh_box("Found", (5.2, 5.0, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.18
    WALL_H = 2.6
    hw = 2.1
    wt = 0.24

    # === Thick defensive walls ===
    bmesh_box("WallF", (wt, hw * 2 - 0.3, WALL_H), (hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallB", (wt, hw * 2 - 0.3, WALL_H), (-hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallR", (hw * 2 - 0.3, wt, WALL_H), (0, -hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallL", (hw * 2 - 0.3, wt, WALL_H), (0, hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)

    # Wall-top walkway
    walk_z = BZ + WALL_H
    bmesh_box("WalkF", (0.32, hw * 2, 0.06), (hw, 0, walk_z + 0.03), m['stone_trim'])
    bmesh_box("WalkB", (0.32, hw * 2, 0.06), (-hw, 0, walk_z + 0.03), m['stone_trim'])
    bmesh_box("WalkR", (hw * 2, 0.32, 0.06), (0, -hw, walk_z + 0.03), m['stone_trim'])
    bmesh_box("WalkL", (hw * 2, 0.32, 0.06), (0, hw, walk_z + 0.03), m['stone_trim'])

    # Battlements
    for i in range(10):
        y = -1.8 + i * 0.40
        bmesh_box(f"MF_{i}", (0.12, 0.16, 0.20), (hw + 0.06, y, walk_z + 0.16), m['stone_trim'], bevel=0.01)
        bmesh_box(f"MB_{i}", (0.12, 0.16, 0.20), (-hw - 0.06, y, walk_z + 0.16), m['stone_trim'], bevel=0.01)
    for i in range(10):
        x = -1.8 + i * 0.40
        bmesh_box(f"MR_{i}", (0.16, 0.12, 0.20), (x, -hw - 0.06, walk_z + 0.16), m['stone_trim'], bevel=0.01)
        bmesh_box(f"ML_{i}", (0.16, 0.12, 0.20), (x, hw + 0.06, walk_z + 0.16), m['stone_trim'], bevel=0.01)

    # === Corner towers (round, Islamic style) ===
    tower_r = 0.48
    tower_h = 3.6
    for xs, ys, label in [(-1, -1, "BL"), (-1, 1, "FL"), (1, -1, "BR"), (1, 1, "FR")]:
        tx, ty = xs * hw, ys * hw
        bmesh_prism(f"Tower_{label}", tower_r, tower_h, 12, (tx, ty, BZ), m['stone_upper'], bevel=0.02)
        # Tower bands
        for tz in [BZ + 1.2, BZ + 2.4, BZ + tower_h - 0.12]:
            bmesh_prism(f"TBand_{label}_{tz:.1f}", tower_r + 0.03, 0.06, 12, (tx, ty, tz), m['stone_trim'])
        # Parapet
        bmesh_prism(f"TTop_{label}", tower_r + 0.05, 0.10, 12, (tx, ty, BZ + tower_h), m['stone_trim'])
        # Merlons
        for i in range(6):
            a = (2 * math.pi * i) / 6
            bmesh_box(f"TM_{label}_{i}", (0.10, 0.10, 0.16),
                      (tx + (tower_r + 0.07) * math.cos(a), ty + (tower_r + 0.07) * math.sin(a),
                       BZ + tower_h + 0.18), m['stone_trim'], bevel=0.01)
        # Conical cap
        bmesh_cone(f"TCone_{label}", tower_r + 0.06, 0.8, 12, (tx, ty, BZ + tower_h + 0.26), m['roof'])

    # === Central palace with pointed arches ===
    palace_w = 2.2
    palace_d = 1.8
    palace_h = 3.0
    bmesh_box("Palace", (palace_w, palace_d, palace_h), (0, 0, BZ + palace_h / 2), m['stone'], bevel=0.03)
    bmesh_box("PalaceCornice", (palace_w + 0.06, palace_d + 0.06, 0.08), (0, 0, BZ + palace_h), m['stone_trim'], bevel=0.02)

    # Flat roof
    bmesh_box("PalaceRoof", (palace_w + 0.10, palace_d + 0.10, 0.06), (0, 0, BZ + palace_h + 0.07), m['stone_dark'])

    # Pointed arch windows (approximated with triangular tops)
    for y_off in [-0.50, 0, 0.50]:
        for z_off in [0.5, 1.6]:
            bmesh_box(f"PWin_{y_off:.1f}_{z_off:.1f}", (0.07, 0.18, 0.45),
                      (palace_w / 2 + 0.01, y_off, BZ + z_off + 0.20), m['window'])
            # Pointed arch top (triangle)
            wt_z = BZ + z_off + 0.425
            tv = [
                (palace_w / 2 + 0.02, y_off - 0.09, wt_z),
                (palace_w / 2 + 0.02, y_off + 0.09, wt_z),
                (palace_w / 2 + 0.02, y_off, wt_z + 0.12),
            ]
            mesh_from_pydata(f"PArch_{y_off:.1f}_{z_off:.1f}", tv, [(0, 1, 2)], m['stone_trim'])

    # Palace door with pointed arch
    bmesh_box("PalaceDoor", (0.08, 0.55, 1.30), (palace_w / 2 + 0.01, 0, BZ + 0.65), m['door'])
    dv = [
        (palace_w / 2 + 0.02, -0.275, BZ + 1.30),
        (palace_w / 2 + 0.02, 0.275, BZ + 1.30),
        (palace_w / 2 + 0.02, 0, BZ + 1.55),
    ]
    mesh_from_pydata("DoorArch", dv, [(0, 1, 2)], m['stone_trim'])

    # === Minaret tower (tallest element) ===
    min_x, min_y = -1.2, -1.5
    min_r = 0.22
    min_h = 4.5
    bmesh_prism("MinaretBase", min_r + 0.05, 0.4, 10, (min_x, min_y, BZ), m['stone_upper'])
    bmesh_prism("MinaretShaft", min_r, min_h, 10, (min_x, min_y, BZ + 0.4), m['stone_light'])
    # Balcony (gallery)
    bmesh_prism("MinaretBal", min_r + 0.12, 0.10, 10, (min_x, min_y, BZ + 0.4 + min_h * 0.7), m['stone_trim'])
    # Railing posts
    for i in range(8):
        a = (2 * math.pi * i) / 8
        bx = min_x + (min_r + 0.10) * math.cos(a)
        by = min_y + (min_r + 0.10) * math.sin(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.25,
                                            location=(bx, by, BZ + 0.4 + min_h * 0.7 + 0.22))
        bpy.context.active_object.name = f"BalRail_{i}"
        bpy.context.active_object.data.materials.append(m['stone_trim'])
    # Upper shaft
    bmesh_prism("MinaretUpper", min_r * 0.7, min_h * 0.25, 10,
                (min_x, min_y, BZ + 0.4 + min_h), m['stone_light'])
    # Pointed finial
    bmesh_cone("MinaretFinial", min_r * 0.5, 0.4, 8,
               (min_x, min_y, BZ + 0.4 + min_h + min_h * 0.25), m['gold'])

    # === Courtyard fountain ===
    bmesh_prism("FountainBase", 0.40, 0.08, 12, (0.8, 0.8, BZ + 0.04), m['stone_light'])
    bmesh_prism("FountainRim", 0.35, 0.12, 12, (0.8, 0.8, BZ + 0.08), m['stone_trim'])
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=0.5,
                                        location=(0.8, 0.8, BZ + 0.37))
    bpy.context.active_object.name = "FountainSpout"
    bpy.context.active_object.data.materials.append(m['stone_light'])

    # === Gatehouse ===
    gate_x = hw + wt / 2
    bmesh_box("Gatehouse", (0.55, 1.0, WALL_H + 0.6), (gate_x, 0, BZ + (WALL_H + 0.6) / 2), m['stone'], bevel=0.02)
    bmesh_box("GateDoor", (0.10, 0.60, 1.40), (gate_x + 0.25, 0, BZ + 0.70), m['door'])
    # Pointed arch over gate
    gv = [
        (gate_x + 0.26, -0.30, BZ + 1.40),
        (gate_x + 0.26, 0.30, BZ + 1.40),
        (gate_x + 0.26, 0, BZ + 1.70),
    ]
    mesh_from_pydata("GateArch", gv, [(0, 1, 2)], m['stone_trim'])

    # Steps
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.20, 1.2, 0.06),
                  (gate_x + 0.45 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_dark'])

    # Banner
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.8,
                                        location=(0, 0, BZ + palace_h + 0.47))
    bpy.context.active_object.data.materials.append(m['wood'])
    bvz = BZ + palace_h + 0.60
    bverts = [(0.04, 0, bvz), (0.45, 0.03, bvz - 0.05),
              (0.45, 0.02, bvz + 0.25), (0.04, 0, bvz + 0.22)]
    mesh_from_pydata("Banner", bverts, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# GUNPOWDER AGE — Mamluk palace
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (6.0, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation ===
    bmesh_box("Found", (5.4, 5.0, 0.22), (0, 0, Z + 0.11), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.22

    # === Main palace (Mamluk style) ===
    palace_w = 3.2
    palace_d = 2.6
    palace_h = 3.4
    bmesh_box("Palace", (palace_w, palace_d, palace_h), (0, 0, BZ + palace_h / 2), m['stone'], bevel=0.03)

    # Striped stonework bands (alternating light and dark — Mamluk ablaq)
    stripe_h = 0.18
    for i in range(9):
        z = BZ + 0.3 + i * (stripe_h * 2)
        mat = m['stone_light'] if i % 2 == 0 else m['stone_dark']
        bmesh_box(f"Stripe_{i}", (palace_w + 0.02, palace_d + 0.02, stripe_h),
                  (0, 0, z), mat)

    # Cornice with muqarnas suggestion (stepped brackets)
    bmesh_box("Cornice", (palace_w + 0.08, palace_d + 0.08, 0.10), (0, 0, BZ + palace_h), m['stone_trim'], bevel=0.02)
    bmesh_box("MuqStep1", (palace_w + 0.04, palace_d + 0.04, 0.06), (0, 0, BZ + palace_h - 0.08), m['stone_trim'])
    bmesh_box("MuqStep2", (palace_w + 0.02, palace_d + 0.02, 0.04), (0, 0, BZ + palace_h - 0.14), m['stone_upper'])

    # Flat roof
    bmesh_box("PalaceRoof", (palace_w + 0.12, palace_d + 0.12, 0.06), (0, 0, BZ + palace_h + 0.09), m['stone_dark'])

    # === Pointed arch windows with mashrabiya lattice ===
    for row, z_off in [(0, 0.6), (1, 1.8), (2, 2.8)]:
        for y in [-0.8, -0.3, 0.3, 0.8]:
            # Window opening
            bmesh_box(f"Win_{row}_{y:.1f}", (0.07, 0.20, 0.45),
                      (palace_w / 2 + 0.01, y, BZ + z_off), m['window'])
            # Pointed arch top
            wz = BZ + z_off + 0.225
            wv = [
                (palace_w / 2 + 0.02, y - 0.10, wz),
                (palace_w / 2 + 0.02, y + 0.10, wz),
                (palace_w / 2 + 0.02, y, wz + 0.10),
            ]
            mesh_from_pydata(f"WArch_{row}_{y:.1f}", wv, [(0, 1, 2)], m['stone_trim'])
            # Mashrabiya lattice (grid of thin bars)
            if row == 1:
                for dy in [-0.06, 0, 0.06]:
                    bmesh_box(f"MashH_{y:.1f}_{dy:.2f}", (0.02, 0.005, 0.40),
                              (palace_w / 2 + 0.03, y + dy, BZ + z_off), m['wood'])
                for dz in [-0.12, 0, 0.12]:
                    bmesh_box(f"MashV_{y:.1f}_{dz:.2f}", (0.02, 0.18, 0.005),
                              (palace_w / 2 + 0.03, y, BZ + z_off + dz), m['wood'])

    # Main entrance with pointed arch
    bmesh_box("Door", (0.10, 0.65, 1.50), (palace_w / 2 + 0.01, 0, BZ + 0.75), m['door'])
    dv = [
        (palace_w / 2 + 0.02, -0.325, BZ + 1.50),
        (palace_w / 2 + 0.02, 0.325, BZ + 1.50),
        (palace_w / 2 + 0.02, 0, BZ + 1.85),
    ]
    mesh_from_pydata("DoorArch", dv, [(0, 1, 2)], m['stone_trim'])
    # Recessed entrance niche
    bmesh_box("DoorNiche", (0.30, 0.80, 1.90), (palace_w / 2 + 0.15, 0, BZ + 0.95), m['stone_dark'])

    # === Central dome ===
    dome_z = BZ + palace_h + 0.09
    bmesh_prism("DomeDrum", 0.60, 0.5, 12, (0, 0, dome_z), m['stone_upper'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.65, location=(0, 0, dome_z + 0.50 + 0.15))
    dome = bpy.context.active_object
    dome.name = "Dome"
    dome.scale = (1, 1, 0.55)
    dome.data.materials.append(m['roof'])
    bpy.ops.object.shade_smooth()
    # Finial
    bmesh_cone("DomeFinial", 0.06, 0.20, 8, (0, 0, dome_z + 0.90), m['gold'])

    # === Minaret ===
    min_x, min_y = palace_w / 2 - 0.3, -palace_d / 2 + 0.3
    min_h = 5.0
    min_r = 0.20
    # Base (square)
    bmesh_box("MinBase", (0.50, 0.50, 0.6), (min_x, min_y, BZ + 0.30), m['stone_upper'])
    # Shaft
    bmesh_prism("MinShaft", min_r, min_h * 0.55, 10, (min_x, min_y, BZ + 0.6), m['stone_light'])
    # First balcony
    bal1_z = BZ + 0.6 + min_h * 0.55
    bmesh_prism("MinBal1", min_r + 0.10, 0.08, 10, (min_x, min_y, bal1_z), m['stone_trim'])
    # Upper octagonal shaft
    bmesh_prism("MinUpper", min_r * 0.75, min_h * 0.25, 8, (min_x, min_y, bal1_z + 0.08), m['stone_light'])
    # Second balcony
    bal2_z = bal1_z + 0.08 + min_h * 0.25
    bmesh_prism("MinBal2", min_r * 0.75 + 0.08, 0.06, 8, (min_x, min_y, bal2_z), m['stone_trim'])
    # Lantern
    bmesh_prism("MinLantern", min_r * 0.5, min_h * 0.12, 8, (min_x, min_y, bal2_z + 0.06), m['stone_light'])
    # Pointed cap
    bmesh_cone("MinCap", min_r * 0.4, 0.35, 8, (min_x, min_y, bal2_z + 0.06 + min_h * 0.12), m['gold'])

    # === Courtyard details ===
    # Fountain
    bmesh_prism("Fountain", 0.35, 0.10, 10, (-0.8, 0.8, BZ + 0.05), m['stone_light'])
    bmesh_prism("FountainRim", 0.30, 0.14, 10, (-0.8, 0.8, BZ + 0.07), m['stone_trim'])
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035, depth=0.45,
                                        location=(-0.8, 0.8, BZ + 0.34))
    bpy.context.active_object.name = "FountainJet"
    bpy.context.active_object.data.materials.append(m['stone_light'])

    # Steps
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.22, 1.4, 0.06),
                  (palace_w / 2 + 0.40 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_dark'])

    # Banner
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.8,
                                        location=(min_x, min_y, bal2_z + 0.06 + min_h * 0.12 + 0.75))
    bpy.context.active_object.data.materials.append(m['wood'])
    fz_top = bal2_z + 0.06 + min_h * 0.12 + 0.90
    fv = [(min_x + 0.04, min_y, fz_top), (min_x + 0.40, min_y + 0.03, fz_top - 0.05),
          (min_x + 0.40, min_y + 0.02, fz_top + 0.25), (min_x + 0.04, min_y, fz_top + 0.22)]
    mesh_from_pydata("Banner", fv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# ENLIGHTENMENT AGE — Mohamed Ali style mosque-palace
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (6.5, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.18
    bmesh_box("Found", (6.0, 5.2, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.05)

    # === Main palace-mosque body ===
    main_w = 3.4
    main_d = 2.8
    main_h = 3.2
    bmesh_box("Main", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone'], bevel=0.03)

    # Moldings
    bmesh_box("BaseMold", (main_w + 0.06, main_d + 0.06, 0.08), (0, 0, BZ + 0.04), m['stone_trim'], bevel=0.02)
    bmesh_box("MidMold", (main_w + 0.06, main_d + 0.06, 0.06), (0, 0, BZ + 1.4), m['stone_trim'], bevel=0.01)
    bmesh_box("Cornice", (main_w + 0.10, main_d + 0.10, 0.10), (0, 0, BZ + main_h), m['stone_trim'], bevel=0.03)

    # Balustrade on roof
    bmesh_box("Balustrade", (main_w + 0.06, main_d + 0.06, 0.22), (0, 0, BZ + main_h + 0.11), m['stone_light'])

    # === Large central dome (Mohamed Ali style) ===
    dome_z = BZ + main_h + 0.22
    # Drum
    bmesh_prism("Drum", 1.0, 0.8, 16, (0, 0, dome_z), m['stone'], bevel=0.02)
    # Windows on drum
    for i in range(8):
        a = (2 * math.pi * i) / 8
        wx = 1.01 * math.cos(a)
        wy = 1.01 * math.sin(a)
        bmesh_box(f"DrumWin_{i}", (0.05, 0.12, 0.45),
                  (wx, wy, dome_z + 0.25), m['window'])
    # Main dome
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.05, location=(0, 0, dome_z + 0.80 + 0.25))
    dome = bpy.context.active_object
    dome.name = "Dome"
    dome.scale = (1, 1, 0.50)
    dome.data.materials.append(m['roof'])
    bpy.ops.object.shade_smooth()
    # Lantern on dome
    bmesh_prism("Lantern", 0.16, 0.35, 8, (0, 0, dome_z + 1.30), m['stone_light'])
    bmesh_cone("LanternRoof", 0.20, 0.25, 8, (0, 0, dome_z + 1.65), m['gold'])
    # Crescent finial
    bpy.ops.mesh.primitive_torus_add(major_radius=0.08, minor_radius=0.015,
                                     location=(0, 0, dome_z + 1.95))
    crescent = bpy.context.active_object
    crescent.name = "Crescent"
    crescent.scale = (1, 0.3, 1)
    crescent.data.materials.append(m['gold'])

    # === Two slim minarets (pencil-style, Ottoman-Egyptian) ===
    for side, my in [("L", main_d / 2 + 0.3), ("R", -main_d / 2 - 0.3)]:
        mx = main_w / 2 - 0.5
        min_h = 5.8
        min_r = 0.14
        # Base (square)
        bmesh_box(f"MinBase_{side}", (0.36, 0.36, 0.5), (mx, my, BZ + 0.25), m['stone_upper'])
        # Main shaft
        bmesh_prism(f"MinShaft_{side}", min_r, min_h * 0.6, 10, (mx, my, BZ + 0.5), m['stone_light'])
        # Gallery
        gal_z = BZ + 0.5 + min_h * 0.6
        bmesh_prism(f"MinGal_{side}", min_r + 0.10, 0.08, 10, (mx, my, gal_z), m['stone_trim'])
        # Railing
        for i in range(8):
            a = (2 * math.pi * i) / 8
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=0.20,
                                                location=(mx + (min_r + 0.08) * math.cos(a),
                                                          my + (min_r + 0.08) * math.sin(a),
                                                          gal_z + 0.18))
            bpy.context.active_object.name = f"GalRail_{side}_{i}"
            bpy.context.active_object.data.materials.append(m['stone_trim'])
        # Upper shaft (thinner)
        bmesh_prism(f"MinUp_{side}", min_r * 0.7, min_h * 0.25, 10, (mx, my, gal_z + 0.08), m['stone_light'])
        # Pointed conical cap
        cap_z = gal_z + 0.08 + min_h * 0.25
        bmesh_cone(f"MinCap_{side}", min_r * 0.6, 0.60, 10, (mx, my, cap_z), m['roof'])
        # Gold finial
        bmesh_cone(f"MinFinial_{side}", 0.03, 0.15, 6, (mx, my, cap_z + 0.60), m['gold'])

    # === Marble columns (portico) ===
    col_h = 2.6
    for y in [-0.8, -0.3, 0.3, 0.8]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.10, depth=col_h,
                                            location=(main_w / 2 + 0.45, y, BZ + col_h / 2))
        col = bpy.context.active_object
        col.name = f"MarbleCol_{y:.1f}"
        col.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        bmesh_box(f"ColCap_{y:.1f}", (0.24, 0.24, 0.06), (main_w / 2 + 0.45, y, BZ + col_h + 0.03), m['stone_trim'])
        bmesh_box(f"ColBase_{y:.1f}", (0.22, 0.22, 0.06), (main_w / 2 + 0.45, y, BZ + 0.03), m['stone_trim'])

    # Portico roof
    bmesh_box("PorRoof", (0.50, 2.2, 0.08), (main_w / 2 + 0.45, 0, BZ + col_h + 0.10), m['stone_trim'])

    # Windows (arched, 2 rows)
    for row, z_off in [(0, 0.5), (1, 1.8)]:
        for y in [-1.0, -0.5, 0, 0.5, 1.0]:
            bmesh_box(f"Win_{row}_{y:.1f}", (0.07, 0.20, 0.55),
                      (main_w / 2 + 0.01, y, BZ + z_off), m['window'])
            bmesh_box(f"WinH_{row}_{y:.1f}", (0.08, 0.24, 0.04),
                      (main_w / 2 + 0.02, y, BZ + z_off + 0.30), m['stone_trim'])

    # Door
    bmesh_box("Door", (0.08, 0.60, 1.50), (main_w / 2 + 0.01, 0, BZ + 0.75), m['door'])

    # === Symmetrical wings ===
    wing_w = 1.4
    wing_d = 1.6
    wing_h = 2.2
    for ys, lbl in [(-2.2, "R"), (2.2, "L")]:
        bmesh_box(f"Wing_{lbl}", (wing_w, wing_d, wing_h), (0.2, ys, BZ + wing_h / 2), m['stone'], bevel=0.02)
        bmesh_box(f"WingCornice_{lbl}", (wing_w + 0.06, wing_d + 0.06, 0.08),
                  (0.2, ys, BZ + wing_h), m['stone_trim'], bevel=0.02)
        pyramid_roof(f"WingRoof_{lbl}", w=wing_w - 0.2, d=wing_d - 0.2, h=0.6, overhang=0.12,
                     origin=(0.2, ys, BZ + wing_h + 0.04), material=m['roof'])
        # Wing windows
        for wy in [-0.4, 0.4]:
            bmesh_box(f"WWin_{lbl}_{wy:.1f}", (0.07, 0.18, 0.50),
                      (0.2 + wing_w / 2 + 0.01, ys + wy, BZ + 1.0), m['window'])

    # Steps
    for i in range(7):
        bmesh_box(f"Step_{i}", (0.20, 2.2, 0.06),
                  (main_w / 2 + 0.65 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_light'])


# ============================================================
# INDUSTRIAL AGE — Egyptian colonial building
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (6.5, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.15
    bmesh_box("Found", (6.0, 5.0, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.04)

    # === Main building (grand colonnaded facade) ===
    main_w = 4.0
    main_d = 3.0
    main_h = 3.6
    bmesh_box("Main", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone'], bevel=0.02)

    # Egyptian motif bands on facade
    bmesh_box("BaseBand", (main_w + 0.04, main_d + 0.04, 0.10), (0, 0, BZ + 0.05), m['stone_trim'], bevel=0.02)
    bmesh_box("MidBand", (main_w + 0.04, main_d + 0.04, 0.08), (0, 0, BZ + 1.2), m['stone_trim'])
    bmesh_box("TopBand", (main_w + 0.04, main_d + 0.04, 0.08), (0, 0, BZ + 2.4), m['stone_trim'])
    bmesh_box("Cornice", (main_w + 0.08, main_d + 0.08, 0.12), (0, 0, BZ + main_h), m['stone_trim'], bevel=0.03)

    # Cavetto cornice (Egyptian style — simplified as tapered cap)
    bmesh_box("Cavetto", (main_w + 0.12, main_d + 0.12, 0.06), (0, 0, BZ + main_h + 0.09), m['stone_dark'])

    # Iron beams on facade
    for z in [BZ + 1.2, BZ + 2.4]:
        bmesh_box(f"IronH_{z:.1f}", (0.03, 3.0, 0.05), (main_w / 2 + 0.01, 0, z), m['iron'])

    # === Grand colonnade (palm capital columns — Egyptian style) ===
    col_h = 3.0
    col_r = 0.12
    for i, y in enumerate([-1.2, -0.6, 0, 0.6, 1.2]):
        cx = main_w / 2 + 0.50
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=col_r, depth=col_h,
                                            location=(cx, y, BZ + col_h / 2))
        col = bpy.context.active_object
        col.name = f"PalmCol_{i}"
        col.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        # Palm capital (wider disk with flare)
        bmesh_prism(f"PalmCap_{i}", col_r + 0.08, 0.12, 12, (cx, y, BZ + col_h), m['stone_trim'])
        # Abacus
        bmesh_box(f"PalmAbacus_{i}", (0.28, 0.28, 0.05), (cx, y, BZ + col_h + 0.14), m['stone_trim'])
        # Base
        bmesh_box(f"PalmBase_{i}", (0.26, 0.26, 0.06), (cx, y, BZ + 0.03), m['stone_trim'])

    # Entablature over columns
    bmesh_box("Entablature", (0.40, 3.0, 0.15), (main_w / 2 + 0.50, 0, BZ + col_h + 0.26), m['stone_trim'], bevel=0.02)

    # Windows (3 rows, 5 cols)
    for row, z_off in enumerate([0.4, 1.4, 2.5]):
        for y in [-1.0, -0.5, 0, 0.5, 1.0]:
            h = 0.50 if row < 2 else 0.40
            bmesh_box(f"Win_{row}_{y:.1f}", (0.07, 0.22, h),
                      (main_w / 2 + 0.01, y, BZ + z_off + 0.10), m['window'])
            bmesh_box(f"WinH_{row}_{y:.1f}", (0.08, 0.26, 0.04),
                      (main_w / 2 + 0.02, y, BZ + z_off + h / 2 + 0.12), m['stone_trim'])

    # Door
    bmesh_box("Door", (0.10, 0.80, 1.80), (main_w / 2 + 0.01, 0, BZ + 0.90), m['door'])
    bmesh_box("DoorFrame", (0.12, 0.95, 0.10), (main_w / 2 + 0.02, 0, BZ + 1.84), m['stone_trim'], bevel=0.02)

    # === Clock tower (with Egyptian motifs) ===
    TX, TY = main_w / 2 - 0.8, -main_d / 2 + 0.5
    tower_base_z = BZ + main_h + 0.09
    tower_w = 0.9
    tower_h = 3.2
    bmesh_box("Tower", (tower_w, tower_w, tower_h), (TX, TY, tower_base_z + tower_h / 2), m['stone'], bevel=0.03)
    bmesh_box("TCornice", (tower_w + 0.08, tower_w + 0.08, 0.08), (TX, TY, tower_base_z + tower_h), m['stone_trim'], bevel=0.02)

    # Clock faces
    for dx, dy, rot in [(tower_w / 2 + 0.01, 0, (0, math.radians(90), 0)),
                        (0, -tower_w / 2 - 0.01, (math.radians(90), 0, 0))]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.28, depth=0.04,
                                            location=(TX + dx, TY + dy, tower_base_z + 2.0))
        cl = bpy.context.active_object
        cl.name = f"Clock_{dx:.1f}_{dy:.1f}"
        cl.rotation_euler = rot
        cl.data.materials.append(m['gold'])

    # Pyramidal tower top (Egyptian touch)
    pyramid_roof("TowerRoof", w=tower_w - 0.1, d=tower_w - 0.1, h=1.2, overhang=0.08,
                 origin=(TX, TY, tower_base_z + tower_h + 0.04), material=m['roof'])

    # Gold spire
    bmesh_cone("Spire", 0.06, 0.4, 8, (TX, TY, tower_base_z + tower_h + 1.24), m['gold'])

    # === Obelisk (in front plaza) ===
    ob_x, ob_y = main_w / 2 + 1.5, 0
    ob_h = 2.5
    v_ob = [
        (ob_x - 0.09, ob_y - 0.09, Z), (ob_x + 0.09, ob_y - 0.09, Z),
        (ob_x + 0.09, ob_y + 0.09, Z), (ob_x - 0.09, ob_y + 0.09, Z),
        (ob_x - 0.045, ob_y - 0.045, Z + ob_h), (ob_x + 0.045, ob_y - 0.045, Z + ob_h),
        (ob_x + 0.045, ob_y + 0.045, Z + ob_h), (ob_x - 0.045, ob_y + 0.045, Z + ob_h),
    ]
    f_ob = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7), (0, 3, 2, 1)]
    mesh_from_pydata("Obelisk", v_ob, f_ob, m['stone_light'])
    # Pyramidion
    hp = 0.045
    pv = [(ob_x - hp, ob_y - hp, Z + ob_h), (ob_x + hp, ob_y - hp, Z + ob_h),
          (ob_x + hp, ob_y + hp, Z + ob_h), (ob_x - hp, ob_y + hp, Z + ob_h),
          (ob_x, ob_y, Z + ob_h + 0.14)]
    pf = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (0, 1, 2, 3)]
    mesh_from_pydata("Pyramidion", pv, pf, m['gold'])
    # Obelisk base
    bmesh_box("ObeliskBase", (0.30, 0.30, 0.10), (ob_x, ob_y, Z + 0.05), m['stone_dark'])

    # Iron fence
    for i in range(12):
        fy = -1.5 + i * 0.27
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.55,
                                            location=(main_w / 2 + 1.0, fy, BZ + 0.12))
        bpy.context.active_object.data.materials.append(m['iron'])

    # Steps
    for i in range(6):
        bmesh_box(f"Step_{i}", (0.22, 2.0, 0.06),
                  (main_w / 2 + 0.75 + i * 0.22, 0, BZ - 0.04 - i * 0.05), m['stone_dark'])


# ============================================================
# MODERN AGE — Cairo modernist
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (7.0, 6.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.10
    bmesh_box("Found", (6.5, 5.5, 0.10), (0, 0, Z + 0.05), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Main building (concrete brutalist with Egyptian geometric patterns) ===
    main_w = 3.6
    main_d = 2.8
    main_h = 4.5
    bmesh_box("Main", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone'], bevel=0.02)

    # Geometric pattern bands (sunken rectangles — Egyptian motif)
    for i in range(6):
        z = BZ + 0.5 + i * 0.65
        for y in [-1.0, -0.4, 0.4, 1.0]:
            bmesh_box(f"GeoPattern_{i}_{y:.1f}", (0.04, 0.22, 0.35),
                      (main_w / 2 + 0.01, y, z), m['stone_dark'])

    # Concrete frame grid
    for z in [BZ + 1.5, BZ + 3.0, BZ + main_h]:
        bmesh_box(f"ConcreteH_{z:.1f}", (main_w + 0.04, main_d + 0.04, 0.08), (0, 0, z), m['stone_trim'])

    # Flat roof
    bmesh_box("Roof", (main_w + 0.08, main_d + 0.08, 0.10), (0, 0, BZ + main_h + 0.05), m['stone_dark'])

    # === Pyramid-shaped skylight on roof ===
    pyr_hw = 0.8
    pyr_base_z = BZ + main_h + 0.10
    pyr_h = 1.2
    pyr_v = [
        (-pyr_hw, -pyr_hw, pyr_base_z), (pyr_hw, -pyr_hw, pyr_base_z),
        (pyr_hw, pyr_hw, pyr_base_z), (-pyr_hw, pyr_hw, pyr_base_z),
        (0, 0, pyr_base_z + pyr_h),
    ]
    pyr_f = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (0, 1, 2, 3)]
    mesh_from_pydata("PyramidSkylight", pyr_v, pyr_f, glass)

    # Metal frame on pyramid skylight
    for i in range(4):
        v0 = pyr_v[i]
        v1 = pyr_v[4]
        mid_x = (v0[0] + v1[0]) / 2
        mid_y = (v0[1] + v1[1]) / 2
        mid_z = (v0[2] + v1[2]) / 2
        edge_len = math.sqrt((v1[0] - v0[0]) ** 2 + (v1[1] - v0[1]) ** 2 + (v1[2] - v0[2]) ** 2)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=edge_len,
                                            location=(mid_x, mid_y, mid_z))
        obj = bpy.context.active_object
        obj.name = f"PyFrame_{i}"
        # Rotate to align with edge
        dx = v1[0] - v0[0]
        dy = v1[1] - v0[1]
        dz = v1[2] - v0[2]
        pitch = math.atan2(math.sqrt(dx * dx + dy * dy), dz)
        yaw = math.atan2(dy, dx)
        obj.rotation_euler = (pitch, 0, yaw)
        obj.data.materials.append(metal)

    # === Lower wing ===
    wing_w = 3.5
    wing_d = 2.2
    wing_h = 2.8
    bmesh_box("Wing", (wing_w, wing_d, wing_h), (1.2, 0, BZ + wing_h / 2), m['stone'], bevel=0.02)

    # Wing glass curtain wall
    bmesh_box("WGlass", (0.06, wing_d - 0.4, wing_h - 0.4),
              (1.2 + wing_w / 2 + 0.01, 0, BZ + wing_h / 2 + 0.1), glass)
    for z in [BZ + 1.0, BZ + 2.0]:
        bmesh_box(f"WBand_{z:.1f}", (0.08, wing_d - 0.3, 0.06),
                  (1.2 + wing_w / 2 + 0.02, 0, z), m['stone_trim'])

    # Wing flat roof
    bmesh_box("WRoof", (wing_w + 0.08, wing_d + 0.08, 0.08), (1.2, 0, BZ + wing_h + 0.04), m['stone_dark'])

    # === Palm court (open area with palm-column-shaped pillars) ===
    court_x = 1.2 + wing_w / 2 + 0.70
    for y in [-0.6, 0.6]:
        # Stylized palm column (concrete)
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.08, depth=2.2,
                                            location=(court_x, y, BZ + 1.1))
        col = bpy.context.active_object
        col.name = f"PalmPillar_{y:.1f}"
        col.data.materials.append(m['stone_light'])
        # Flared capital
        bmesh_prism(f"PalmFlare_{y:.1f}", 0.16, 0.10, 10, (court_x, y, BZ + 2.2), m['stone_trim'])

    # Canopy over court
    bmesh_box("CourtCanopy", (1.0, 2.0, 0.06), (court_x, 0, BZ + 2.3), metal)

    # Entrance
    bmesh_box("GlassDoor", (0.06, 1.2, 2.0),
              (1.2 + wing_w / 2 + 0.01, 0, BZ + 1.0), glass)
    bmesh_box("DoorFrame", (0.07, 1.3, 0.04),
              (1.2 + wing_w / 2 + 0.02, 0, BZ + 2.02), metal)

    # Side windows
    for x in [-0.5, 0.5, 1.5, 2.5]:
        bmesh_box(f"SWin_{x:.1f}", (0.24, 0.06, 0.70),
                  (x + 1.2, -wing_d / 2 - 0.01, BZ + 1.5), glass)

    # === Antenna / communications ===
    roof_z = BZ + main_h + 0.10
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035, depth=2.0,
                                        location=(0, 0, roof_z + pyr_h + 1.0))
    bpy.context.active_object.name = "Antenna"
    bpy.context.active_object.data.materials.append(metal)

    # HVAC on wing roof
    wing_rz = BZ + wing_h + 0.08
    bmesh_box("HVAC", (0.7, 0.5, 0.35), (1.5, 0.5, wing_rz + 0.175), m['stone_dark'])

    # Banner
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=1.2,
                                        location=(2.5, 1.0, wing_rz + 0.60))
    bpy.context.active_object.data.materials.append(metal)
    bvz = wing_rz + 0.95
    bv = [(2.53, 1.0, bvz), (3.0, 1.03, bvz - 0.05),
          (3.0, 1.02, bvz + 0.28), (2.53, 1.0, bvz + 0.25)]
    mesh_from_pydata("Banner", bv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False

    # Plaza planter
    bmesh_prism("Planter", 0.35, 0.15, 10, (court_x + 0.5, 0, Z + 0.075), m['stone_light'])


# ============================================================
# DIGITAL AGE — Neo-Egyptian high-tech
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (7.0, 6.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.08
    bmesh_box("Found", (6.5, 5.5, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Glass pyramid structure (main building) ===
    pyr_hw = 2.0
    pyr_h = 5.0
    pyr_v = [
        (-pyr_hw, -pyr_hw, BZ), (pyr_hw, -pyr_hw, BZ),
        (pyr_hw, pyr_hw, BZ), (-pyr_hw, pyr_hw, BZ),
        (0, 0, BZ + pyr_h),
    ]
    pyr_f = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (0, 1, 2, 3)]
    mesh_from_pydata("GlassPyramid", pyr_v, pyr_f, glass)

    # Gold wireframe edges on pyramid
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (1, 4), (2, 4), (3, 4)]
    for ei, (a, b) in enumerate(edges):
        va = pyr_v[a]
        vb = pyr_v[b]
        mx = (va[0] + vb[0]) / 2
        my = (va[1] + vb[1]) / 2
        mz = (va[2] + vb[2]) / 2
        edge_len = math.sqrt((vb[0] - va[0]) ** 2 + (vb[1] - va[1]) ** 2 + (vb[2] - va[2]) ** 2)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=edge_len,
                                            location=(mx, my, mz))
        obj = bpy.context.active_object
        obj.name = f"GoldWire_{ei}"
        dx = vb[0] - va[0]
        dy = vb[1] - va[1]
        dz = vb[2] - va[2]
        pitch = math.atan2(math.sqrt(dx * dx + dy * dy), dz)
        yaw = math.atan2(dy, dx)
        obj.rotation_euler = (pitch, 0, yaw)
        obj.data.materials.append(m['gold'])

    # Additional gold wireframe at mid-height
    mid_h_ratio = 0.5
    mid_hw = pyr_hw * (1 - mid_h_ratio)
    mid_z = BZ + pyr_h * mid_h_ratio
    mid_corners = [
        (-mid_hw, -mid_hw, mid_z), (mid_hw, -mid_hw, mid_z),
        (mid_hw, mid_hw, mid_z), (-mid_hw, mid_hw, mid_z),
    ]
    for i in range(4):
        va = mid_corners[i]
        vb = mid_corners[(i + 1) % 4]
        mx = (va[0] + vb[0]) / 2
        my = (va[1] + vb[1]) / 2
        mz = (va[2] + vb[2]) / 2
        seg_len = math.sqrt((vb[0] - va[0]) ** 2 + (vb[1] - va[1]) ** 2)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=seg_len,
                                            location=(mx, my, mz))
        obj = bpy.context.active_object
        obj.name = f"MidWire_{i}"
        yaw = math.atan2(vb[1] - va[1], vb[0] - va[0])
        obj.rotation_euler = (math.radians(90), 0, yaw)
        obj.data.materials.append(m['gold'])

    # === Holographic Eye of Horus (large disk with iris detail) ===
    eye_z = BZ + pyr_h * 0.55
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.50, depth=0.04,
                                        location=(pyr_hw * 0.4 + 0.3, 0, eye_z))
    eye_outer = bpy.context.active_object
    eye_outer.name = "HorusEyeOuter"
    eye_outer.rotation_euler = (0, math.radians(90), 0)
    eye_outer.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()
    # Inner iris
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.22, depth=0.06,
                                        location=(pyr_hw * 0.4 + 0.32, 0, eye_z))
    eye_inner = bpy.context.active_object
    eye_inner.name = "HorusEyeInner"
    eye_inner.rotation_euler = (0, math.radians(90), 0)
    eye_inner.data.materials.append(glass)
    bpy.ops.object.shade_smooth()
    # Tear line (vertical drop below eye)
    bmesh_box("HorusTear", (0.03, 0.06, 0.40), (pyr_hw * 0.4 + 0.31, 0, eye_z - 0.40), m['gold'])

    # === Floating obelisk (suspended by structure) ===
    ob_x, ob_y = -2.2, 0
    ob_h = 3.5
    float_z = BZ + 0.6  # floats above ground
    # Support frame underneath
    bmesh_box("ObeliskFrame", (0.40, 0.40, 0.04), (ob_x, ob_y, float_z - 0.02), metal)
    for dx, dy in [(-0.18, -0.18), (-0.18, 0.18), (0.18, -0.18), (0.18, 0.18)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=float_z - BZ,
                                            location=(ob_x + dx, ob_y + dy, BZ + (float_z - BZ) / 2))
        bpy.context.active_object.name = f"ObeliskLeg_{dx:.2f}_{dy:.2f}"
        bpy.context.active_object.data.materials.append(metal)
    # Obelisk body (tapered)
    v_ob = [
        (ob_x - 0.12, ob_y - 0.12, float_z), (ob_x + 0.12, ob_y - 0.12, float_z),
        (ob_x + 0.12, ob_y + 0.12, float_z), (ob_x - 0.12, ob_y + 0.12, float_z),
        (ob_x - 0.06, ob_y - 0.06, float_z + ob_h), (ob_x + 0.06, ob_y - 0.06, float_z + ob_h),
        (ob_x + 0.06, ob_y + 0.06, float_z + ob_h), (ob_x - 0.06, ob_y + 0.06, float_z + ob_h),
    ]
    f_ob = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7), (0, 3, 2, 1)]
    mesh_from_pydata("FloatingObelisk", v_ob, f_ob, m['stone_light'])
    # Gold pyramidion
    hp = 0.06
    ppv = [
        (ob_x - hp, ob_y - hp, float_z + ob_h), (ob_x + hp, ob_y - hp, float_z + ob_h),
        (ob_x + hp, ob_y + hp, float_z + ob_h), (ob_x - hp, ob_y + hp, float_z + ob_h),
        (ob_x, ob_y, float_z + ob_h + 0.20),
    ]
    ppf = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (0, 1, 2, 3)]
    mesh_from_pydata("ObeliskPyramidion", ppv, ppf, m['gold'])
    # LED glow strips on obelisk
    for z_off in [0.5, 1.2, 1.9, 2.6]:
        bmesh_box(f"ObeliskLED_{z_off:.1f}", (0.13, 0.005, 0.06),
                  (ob_x, ob_y + 0.12, float_z + z_off), m['gold'])
        bmesh_box(f"ObeliskLED2_{z_off:.1f}", (0.13, 0.005, 0.06),
                  (ob_x, ob_y - 0.12, float_z + z_off), m['gold'])

    # === LED hieroglyphs panel (on lower wing) ===
    wing_w = 3.8
    wing_d = 1.6
    wing_h = 2.5
    bmesh_box("Wing", (wing_w, wing_d, wing_h), (1.5, 0, BZ + wing_h / 2), glass)
    # Metal frame
    for z in [BZ + 0.8, BZ + 1.6, BZ + wing_h]:
        bmesh_box(f"WingH_{z:.1f}", (wing_w + 0.02, wing_d + 0.02, 0.04), (1.5, 0, z), metal)

    # Hieroglyph LED panel (front of wing)
    panel_x = 1.5 + wing_w / 2 + 0.01
    # Vertical LED columns (suggest hieroglyphic cartouches)
    for i, y in enumerate([-0.5, -0.2, 0.2, 0.5]):
        bmesh_box(f"HieroCol_{i}", (0.03, 0.08, 1.6), (panel_x, y, BZ + 1.2), m['gold'])
        # Small horizontal bars within each column (suggest glyphs)
        for dz in [-0.5, -0.15, 0.2, 0.55]:
            bmesh_box(f"HieroGlyph_{i}_{dz:.2f}", (0.035, 0.06, 0.10),
                      (panel_x + 0.005, y, BZ + 1.2 + dz), m['gold'])

    # Wing roof
    bmesh_box("WRoof", (wing_w + 0.06, wing_d + 0.06, 0.06), (1.5, 0, BZ + wing_h + 0.03), metal)

    # === Entrance atrium ===
    bmesh_box("Atrium", (0.8, 1.8, 2.2), (1.5 + wing_w / 2 + 0.40, 0, BZ + 1.10), glass)
    bmesh_box("AtrFrame", (0.82, 1.82, 0.04), (1.5 + wing_w / 2 + 0.40, 0, BZ + 2.22), metal)

    # === Communication spire on pyramid apex ===
    spire_z = BZ + pyr_h
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=2.0,
                                        location=(0, 0, spire_z + 1.0))
    bpy.context.active_object.name = "Spire"
    bpy.context.active_object.data.materials.append(metal)
    for z_off in [0.4, 0.8, 1.2, 1.6]:
        bmesh_box(f"SpireBar_{z_off:.1f}", (0.5, 0.02, 0.02), (0, 0, spire_z + z_off), metal)
        bmesh_box(f"SpireBar2_{z_off:.1f}", (0.02, 0.5, 0.02), (0, 0, spire_z + z_off), metal)

    # Gold LED accent strips
    bmesh_box("LED1", (0.06, wing_d + 0.02, 0.06), (1.5 + wing_w / 2, 0, BZ + wing_h - 0.10), m['gold'])
    bmesh_box("LED2", (wing_w + 0.02, 0.06, 0.06), (1.5, -wing_d / 2, BZ + wing_h - 0.10), m['gold'])

    # Solar panels on wing roof
    wing_rz = BZ + wing_h + 0.06
    for i in range(4):
        bmesh_box(f"Solar_{i}", (0.7, 0.4, 0.04), (0.5 + i * 0.8, 0, wing_rz + 0.06), glass)
        bmesh_box(f"SolarF_{i}", (0.72, 0.42, 0.02), (0.5 + i * 0.8, 0, wing_rz + 0.03), metal)

    # Landscaping hedges
    for y in [-1.6, 1.6]:
        bmesh_box(f"Hedge_{y:.1f}", (0.5, 0.3, 0.22),
                  (1.5 + wing_w / 2 + 0.80, y, Z + 0.11), m['ground'])


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


def build_town_center_egyptians(materials, age='medieval'):
    """Build an Egyptian Town Center with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
