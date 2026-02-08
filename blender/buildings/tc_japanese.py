"""
Japanese Nation Town Center — culturally authentic Japanese architecture per age.

3x3 tile building, ground plane 5.5x5.5.

Stone:         Jomon pit dwelling compound — semi-underground thatched houses,
               center firepit, storage on stilts
Bronze:        Yayoi raised-floor granary village — raised platform buildings on
               wooden pillars, thatched roofs, watchtower
Iron:          Kofun period palace — wooden hall with curved roof, moat/ditch,
               keyhole-shaped mound suggestion
Classical:     Nara period temple-palace — graceful curved hip roof, red pillars,
               covered walkways, pagoda tower
Medieval:      Japanese castle (Himeji-style tenshu) — multi-tiered white tower
               with curved roofs, stone ishigaki, gold shachihoko
Gunpowder:     Azuchi-Momoyama castle — elaborate 5-story tenshu, gold leaf,
               stone walls, outer wall with gate
Enlightenment: Edo period shogun palace — wide elegant buildings with deep curved
               roofs, gardens, guardhouse, ornate gate
Industrial:    Meiji era — Western-Japanese fusion, brick base with Japanese roof,
               clock tower
Modern:        Post-war Japanese modernist — clean concrete, Japanese proportions,
               zen garden, glass wall
Digital:       Ultra-modern Japanese — sleek tower with floating curved roof tiers,
               cherry blossom hologram, LED torii gate
"""

import bpy
import bmesh
import math

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# ── helpers ────────────────────────────────────────────────────
def _curved_roof(name, w, d, h, origin, material, overhang=0.25,
                 curve_up=0.15, segments=8):
    """
    Japanese-style curved hip roof.  The eaves curve upward at the corners
    giving the distinctive East-Asian silhouette.

    w, d  — footprint (full width, depth)
    h     — peak height above origin
    overhang — eave overshoot beyond w/d
    curve_up — how much the corners lift
    """
    ox, oy, oz = origin
    hw = w / 2 + overhang
    hd = d / 2 + overhang

    verts = []
    faces = []

    # apex (single ridge point for a hip roof)
    apex_idx = 0
    verts.append((ox, oy, oz + h))

    # eave ring — 4 sides, each subdivided for curve
    ring_start = 1
    pts_per_side = segments

    # generate eave points around the perimeter with upward curve at corners
    eave = []
    # front edge (+x): from (+hw, -hd) to (+hw, +hd)
    for i in range(pts_per_side):
        t = i / (pts_per_side - 1)
        y = -hd + t * 2 * hd
        # corners curve up
        corner_dist = min(abs(t), abs(1 - t)) * 2  # 0 at corners, 1 at midpoint
        lift = curve_up * (1 - corner_dist)
        eave.append((ox + hw, oy + y, oz + lift))
    # right edge (-y): from (+hw, +hd) to (-hw, +hd)  — skip first (shared corner)
    for i in range(1, pts_per_side):
        t = i / (pts_per_side - 1)
        x = hw - t * 2 * hw
        corner_dist = min(abs(t), abs(1 - t)) * 2
        lift = curve_up * (1 - corner_dist)
        eave.append((ox + x, oy + hd, oz + lift))
    # back edge (-x): from (-hw, +hd) to (-hw, -hd)  — skip first
    for i in range(1, pts_per_side):
        t = i / (pts_per_side - 1)
        y = hd - t * 2 * hd
        corner_dist = min(abs(t), abs(1 - t)) * 2
        lift = curve_up * (1 - corner_dist)
        eave.append((ox - hw, oy + y, oz + lift))
    # left edge (+y): from (-hw, -hd) to (+hw, -hd)  — skip first
    for i in range(1, pts_per_side):
        t = i / (pts_per_side - 1)
        x = -hw + t * 2 * hw
        corner_dist = min(abs(t), abs(1 - t)) * 2
        lift = curve_up * (1 - corner_dist)
        eave.append((ox + x, oy - hd, oz + lift))

    for pt in eave:
        verts.append(pt)

    n_eave = len(eave)
    for i in range(n_eave):
        j = (i + 1) % n_eave
        faces.append((apex_idx, ring_start + i, ring_start + j))

    # bottom face (close eave ring)
    bottom = list(range(ring_start, ring_start + n_eave))
    faces.append(tuple(reversed(bottom)))

    obj = mesh_from_pydata(name, verts, faces, material)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def _torii_gate(prefix, cx, cy, z, h, w, mat_pillar, mat_beam):
    """Small torii gate."""
    # two pillars
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05, depth=h,
                                        location=(cx - w / 2, cy, z + h / 2))
    p1 = bpy.context.active_object
    p1.name = f"{prefix}_PillarL"
    p1.data.materials.append(mat_pillar)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05, depth=h,
                                        location=(cx + w / 2, cy, z + h / 2))
    p2 = bpy.context.active_object
    p2.name = f"{prefix}_PillarR"
    p2.data.materials.append(mat_pillar)
    # kasagi (top beam, slightly curved up at ends)
    top_z = z + h
    bv = [(cx - w / 2 - 0.12, cy - 0.04, top_z + 0.06),
          (cx + w / 2 + 0.12, cy - 0.04, top_z + 0.06),
          (cx + w / 2 + 0.12, cy + 0.04, top_z + 0.06),
          (cx - w / 2 - 0.12, cy + 0.04, top_z + 0.06),
          (cx - w / 2 - 0.15, cy - 0.04, top_z + 0.12),
          (cx + w / 2 + 0.15, cy - 0.04, top_z + 0.12),
          (cx + w / 2 + 0.15, cy + 0.04, top_z + 0.12),
          (cx - w / 2 - 0.15, cy + 0.04, top_z + 0.12)]
    mesh_from_pydata(f"{prefix}_Kasagi", bv,
                     [(0, 1, 2, 3), (4, 5, 6, 7),
                      (0, 1, 5, 4), (2, 3, 7, 6),
                      (0, 3, 7, 4), (1, 2, 6, 5)], mat_beam)
    # nuki (lower crossbeam)
    bmesh_box(f"{prefix}_Nuki", (w + 0.06, 0.06, 0.05),
              (cx, cy, top_z - 0.15), mat_beam)


# ============================================================
# STONE AGE — Jomon pit dwelling compound
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Central large pit dwelling (tateana-jukyo) ===
    # Sunken pit
    bmesh_prism("PitRim", 1.6, 0.12, 12, (0, 0, Z), m['stone_dark'])
    bmesh_prism("PitInner", 1.45, 0.08, 12, (0, 0, Z - 0.04), m['stone'])

    # Thatched conical roof rising from ground level
    bmesh_cone("MainRoof", 1.9, 2.2, 16, (0, 0, Z + 0.08), m['roof'])
    # Smoke hole ring at top
    bmesh_prism("SmokeHole", 0.18, 0.12, 8, (0, 0, Z + 2.20), m['wood'])

    # Ridge poles visible under thatch
    for i in range(8):
        a = (2 * math.pi * i) / 8
        ex, ey = 1.7 * math.cos(a), 1.7 * math.sin(a)
        sv = [(ex, ey, Z + 0.10), (0, 0, Z + 2.25)]
        mesh_from_pydata(f"Ridge_{i}", sv, [], m['wood_dark'])

    # Entrance passage (low tunnel)
    bmesh_box("Entrance", (0.8, 0.55, 0.55), (1.7, 0, Z + 0.30), m['roof'])
    bmesh_box("EntrDoor", (0.06, 0.40, 0.50), (2.10, 0, Z + 0.28), m['door'])

    # Support posts around interior (visible through doorway)
    for i in range(6):
        a = (2 * math.pi * i) / 6
        px, py = 1.1 * math.cos(a), 1.1 * math.sin(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.06, depth=2.0,
                                            location=(px, py, Z + 1.0))
        pole = bpy.context.active_object
        pole.name = f"Post_{i}"
        pole.data.materials.append(m['wood'])

    # === Central firepit (outdoor gathering) ===
    bmesh_prism("FirePit", 0.35, 0.10, 10, (1.8, -1.2, Z + 0.02), m['stone_dark'])
    # Stones around pit
    for i in range(8):
        a = (2 * math.pi * i) / 8
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06,
                                              location=(1.8 + 0.30 * math.cos(a),
                                                        -1.2 + 0.30 * math.sin(a), Z + 0.06))
        st = bpy.context.active_object
        st.name = f"FStone_{i}"
        st.data.materials.append(m['stone'])

    # === Secondary pit dwelling (smaller) ===
    bmesh_prism("Pit2Rim", 0.85, 0.10, 10, (-1.5, 1.2, Z), m['stone_dark'])
    bmesh_cone("Hut2Roof", 1.1, 1.3, 12, (-1.5, 1.2, Z + 0.06), m['roof'])
    bmesh_prism("Smoke2", 0.12, 0.10, 6, (-1.5, 1.2, Z + 1.30), m['wood'])

    # === Storage building on stilts (takayuka-shiki) ===
    SX, SY = -1.6, -1.4
    stilt_h = 0.9
    # Four stilts
    for dx, dy in [(-0.35, -0.30), (-0.35, 0.30), (0.35, -0.30), (0.35, 0.30)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=stilt_h,
                                            location=(SX + dx, SY + dy, Z + stilt_h / 2))
        s = bpy.context.active_object
        s.name = f"Stilt_{dx:.1f}_{dy:.1f}"
        s.data.materials.append(m['wood'])

    # Platform
    bmesh_box("StorePlatform", (0.85, 0.75, 0.06), (SX, SY, Z + stilt_h + 0.03), m['wood'])
    # Walls
    bmesh_box("StoreWalls", (0.75, 0.65, 0.55), (SX, SY, Z + stilt_h + 0.06 + 0.275), m['wood_dark'])
    # Thatched roof
    bmesh_cone("StoreRoof", 0.60, 0.55, 8, (SX, SY, Z + stilt_h + 0.61), m['roof'])

    # Ladder to storage
    bmesh_box("Ladder", (0.06, 0.25, 1.0), (SX + 0.50, SY, Z + 0.50), m['wood'])
    for rz in [0.25, 0.45, 0.65, 0.85]:
        bmesh_box(f"Rung_{rz:.2f}", (0.04, 0.30, 0.03), (SX + 0.50, SY, Z + rz), m['wood_dark'])

    # === Drying rack ===
    for dy in [-0.30, 0.30]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=1.1,
                                            location=(1.8, 1.3 + dy, Z + 0.55))
        bpy.context.active_object.data.materials.append(m['wood'])
    bmesh_box("DryBeam", (0.04, 0.65, 0.04), (1.8, 1.3, Z + 1.10), m['wood'])

    # === Jomon pottery decoration ===
    for i, (px, py) in enumerate([(2.2, -0.5), (2.1, 0.5)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(px, py, Z + 0.10))
        pot = bpy.context.active_object
        pot.name = f"Pot_{i}"
        pot.scale = (1, 1, 0.85)
        pot.data.materials.append(m['roof_edge'])


# ============================================================
# BRONZE AGE — Yayoi raised-floor granary village
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Main raised-floor building (central, largest) ===
    stilt_h = 1.0
    # Heavy pillars
    pillar_positions = [(-0.70, -0.55), (-0.70, 0.55), (0.70, -0.55), (0.70, 0.55),
                        (0, -0.55), (0, 0.55)]
    for px, py in pillar_positions:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=stilt_h,
                                            location=(px, py, Z + stilt_h / 2))
        p = bpy.context.active_object
        p.name = f"MainPillar_{px:.1f}_{py:.1f}"
        p.data.materials.append(m['wood'])

    # Floor platform
    fl_z = Z + stilt_h
    bmesh_box("MainFloor", (1.8, 1.4, 0.08), (0, 0, fl_z + 0.04), m['wood'])

    # Walls (light wooden planks)
    wall_h = 1.4
    bmesh_box("MainWallF", (0.06, 1.30, wall_h), (0.85, 0, fl_z + 0.08 + wall_h / 2), m['wood_dark'])
    bmesh_box("MainWallB", (0.06, 1.30, wall_h), (-0.85, 0, fl_z + 0.08 + wall_h / 2), m['wood_dark'])
    bmesh_box("MainWallR", (1.60, 0.06, wall_h), (0, -0.65, fl_z + 0.08 + wall_h / 2), m['wood_dark'])
    bmesh_box("MainWallL", (1.60, 0.06, wall_h), (0, 0.65, fl_z + 0.08 + wall_h / 2), m['wood_dark'])

    # Distinctive thatched gable roof with extended ridge
    roof_base = fl_z + 0.08 + wall_h
    rv = [(-0.95, -0.75, roof_base), (0.95, -0.75, roof_base),
          (0.95, 0.75, roof_base), (-0.95, 0.75, roof_base),
          (-1.10, 0, roof_base + 1.1), (1.10, 0, roof_base + 1.1)]
    rf = [(0, 1, 5, 4), (2, 3, 4, 5), (0, 3, 4), (1, 2, 5)]
    r = mesh_from_pydata("MainRoof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Chigi (crossed ridge-end timbers, distinctive Yayoi/Shinto feature)
    ridge_z = roof_base + 1.1
    for xs, lbl in [(-1, "B"), (1, "F")]:
        for dy in [-0.06, 0.06]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=0.7,
                                                location=(xs * 1.10, dy, ridge_z + 0.15))
            ch = bpy.context.active_object
            ch.name = f"Chigi_{lbl}_{dy:.2f}"
            ch.rotation_euler = (0, math.radians(15 * xs), 0)
            ch.data.materials.append(m['wood'])

    # Katsuogi (log weights on ridge)
    for kx in [-0.6, -0.2, 0.2, 0.6]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.30,
                                            location=(kx, 0, ridge_z + 0.06))
        k = bpy.context.active_object
        k.name = f"Katsuogi_{kx:.1f}"
        k.rotation_euler = (math.radians(90), 0, 0)
        k.data.materials.append(m['wood_dark'])

    # Door opening
    bmesh_box("MainDoor", (0.06, 0.40, 0.80), (0.86, 0, fl_z + 0.48), m['door'])

    # Ladder
    bmesh_box("MainLadder", (0.06, 0.25, 1.2), (1.20, 0, Z + 0.60), m['wood'])
    for rz in [0.25, 0.45, 0.65, 0.85]:
        bmesh_box(f"MRung_{rz:.2f}", (0.04, 0.30, 0.03), (1.20, 0, Z + rz), m['wood_dark'])

    # === Secondary granary (smaller, to the side) ===
    GX, GY = -1.5, -1.0
    g_stilt_h = 0.8
    for dx, dy in [(-0.35, -0.30), (-0.35, 0.30), (0.35, -0.30), (0.35, 0.30)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06, depth=g_stilt_h,
                                            location=(GX + dx, GY + dy, Z + g_stilt_h / 2))
        bpy.context.active_object.data.materials.append(m['wood'])

    g_fl = Z + g_stilt_h
    bmesh_box("GranFloor", (0.85, 0.75, 0.06), (GX, GY, g_fl + 0.03), m['wood'])
    bmesh_box("GranWalls", (0.75, 0.65, 0.75), (GX, GY, g_fl + 0.06 + 0.375), m['wood_dark'])

    # Granary gable roof
    grz = g_fl + 0.06 + 0.75
    gv = [(GX - 0.48, GY - 0.40, grz), (GX + 0.48, GY - 0.40, grz),
          (GX + 0.48, GY + 0.40, grz), (GX - 0.48, GY + 0.40, grz),
          (GX - 0.55, GY, grz + 0.55), (GX + 0.55, GY, grz + 0.55)]
    gf = [(0, 1, 5, 4), (2, 3, 4, 5), (0, 3, 4), (1, 2, 5)]
    mesh_from_pydata("GranRoof", gv, gf, m['roof'])

    # Rat guards on stilts (nezumi-gaeshi)
    for dx, dy in [(-0.35, -0.30), (-0.35, 0.30), (0.35, -0.30), (0.35, 0.30)]:
        bmesh_box(f"RatGuard_{dx:.1f}_{dy:.1f}", (0.22, 0.22, 0.03),
                  (GX + dx, GY + dy, Z + g_stilt_h * 0.6), m['wood'])

    # === Watchtower (yagura) ===
    TX, TY = 1.5, 1.3
    t_h = 2.8
    # Four corner posts
    for dx, dy in [(-0.25, -0.25), (-0.25, 0.25), (0.25, -0.25), (0.25, 0.25)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=t_h,
                                            location=(TX + dx, TY + dy, Z + t_h / 2))
        bpy.context.active_object.data.materials.append(m['wood'])
    # Platform
    bmesh_box("WatchPlat", (0.65, 0.65, 0.06), (TX, TY, Z + t_h * 0.7), m['wood'])
    # Railing
    bmesh_box("WatchRailF", (0.06, 0.65, 0.20), (TX + 0.30, TY, Z + t_h * 0.7 + 0.13), m['wood_dark'])
    bmesh_box("WatchRailR", (0.65, 0.06, 0.20), (TX, TY - 0.30, Z + t_h * 0.7 + 0.13), m['wood_dark'])
    # Thatched roof
    bmesh_cone("WatchRoof", 0.50, 0.55, 8, (TX, TY, Z + t_h * 0.7 + 0.23), m['roof'])

    # === Wooden fence enclosure ===
    fence_r = 2.3
    n_posts = 22
    for i in range(n_posts):
        a = (2 * math.pi * i) / n_posts
        # leave gap at front
        if abs(a) < 0.25 or abs(a - 2 * math.pi) < 0.25:
            continue
        fx, fy = fence_r * math.cos(a), fence_r * math.sin(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.80,
                                            location=(fx, fy, Z + 0.40))
        bpy.context.active_object.data.materials.append(m['wood'])


# ============================================================
# IRON AGE — Kofun period palace
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Keyhole-shaped mound suggestion (kofun) ===
    # Circular part
    bmesh_prism("KofunCircle", 1.0, 0.18, 16, (-1.8, 0, Z), m['stone_dark'])
    # Rectangular part (the "key" extension)
    bmesh_box("KofunRect", (1.2, 1.2, 0.18), (-1.0, 0, Z + 0.09), m['stone_dark'], bevel=0.04)

    # === Surrounding ditch/moat ===
    # Ring of low walls suggesting a moat around the palace area
    moat_r = 2.0
    for i in range(24):
        a = (2 * math.pi * i) / 24
        mx, my = moat_r * math.cos(a), moat_r * math.sin(a)
        bmesh_box(f"Moat_{i}", (0.20, 0.20, 0.10), (mx, my, Z + 0.05), m['stone'])

    BZ = Z + 0.15

    # === Main palace hall (large wooden structure) ===
    # Raised platform
    bmesh_box("PalacePlat", (2.8, 2.2, 0.15), (0.3, 0, BZ + 0.075), m['stone_dark'], bevel=0.04)
    bmesh_box("PalacePlat2", (2.6, 2.0, 0.10), (0.3, 0, BZ + 0.20), m['stone'], bevel=0.03)

    fl_z = BZ + 0.25
    hall_h = 2.0

    # Pillars (wooden, red-tinted)
    pillar_xs = [-0.8, 0, 0.8]
    pillar_ys = [-0.75, 0, 0.75]
    for px in pillar_xs:
        for py in pillar_ys:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.07, depth=hall_h,
                                                location=(0.3 + px, py, fl_z + hall_h / 2))
            p = bpy.context.active_object
            p.name = f"Pillar_{px:.1f}_{py:.1f}"
            p.data.materials.append(m['wood'])

    # Walls between pillars (light wood panels)
    bmesh_box("HallWallB", (0.06, 1.60, hall_h * 0.7), (0.3 - 0.85, 0, fl_z + hall_h * 0.35), m['wood_dark'])
    bmesh_box("HallWallR", (1.80, 0.06, hall_h * 0.7), (0.3, -0.80, fl_z + hall_h * 0.35), m['wood_dark'])
    bmesh_box("HallWallL", (1.80, 0.06, hall_h * 0.7), (0.3, 0.80, fl_z + hall_h * 0.35), m['wood_dark'])

    # Door
    bmesh_box("HallDoor", (0.06, 0.50, 1.0), (0.3 + 0.85, 0, fl_z + 0.50), m['door'])

    # === Curved gable roof (early Japanese curve) ===
    roof_z = fl_z + hall_h
    # The roof has a gentle upward curve at the eave edges
    _curved_roof("HallRoof", 2.0, 1.8, 1.3, (0.3, 0, roof_z), m['roof'],
                 overhang=0.30, curve_up=0.12)

    # Ridge ornaments (chigi — forked finials)
    for xs in [-1, 1]:
        for dy in [-0.06, 0.06]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=0.50,
                                                location=(0.3 + xs * 1.15, dy, roof_z + 1.30 + 0.10))
            ch = bpy.context.active_object
            ch.name = f"Chigi_{xs}_{dy:.2f}"
            ch.rotation_euler = (0, math.radians(12 * xs), 0)
            ch.data.materials.append(m['wood_dark'])

    # Katsuogi (ridge weights)
    for kx in [-0.5, 0.0, 0.5]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.25,
                                            location=(0.3 + kx, 0, roof_z + 1.30))
        k = bpy.context.active_object
        k.name = f"Katsuogi_{kx:.1f}"
        k.rotation_euler = (math.radians(90), 0, 0)
        k.data.materials.append(m['wood'])

    # === Annex building (smaller, side) ===
    AX, AY = 0.3, -1.5
    bmesh_box("AnnexPlat", (1.2, 0.9, 0.10), (AX, AY, BZ + 0.05), m['stone_dark'])
    bmesh_box("AnnexWalls", (1.0, 0.7, 1.0), (AX, AY, BZ + 0.10 + 0.50), m['wood_dark'])
    _curved_roof("AnnexRoof", 1.1, 0.8, 0.65, (AX, AY, BZ + 1.10), m['roof'],
                 overhang=0.15, curve_up=0.08)

    # === Wooden palisade fence ===
    for i in range(16):
        a = (2 * math.pi * i) / 16
        if 0.15 < a < 0.55:
            continue  # gate opening
        fx = 2.3 * math.cos(a)
        fy = 2.3 * math.sin(a)
        h = 1.0 + 0.08 * math.sin(i * 2.7)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=h,
                                            location=(fx, fy, Z + h / 2))
        bpy.context.active_object.data.materials.append(m['wood'])

    # Gate posts
    bmesh_box("GatePostL", (0.10, 0.10, 1.3), (2.25, -0.25, Z + 0.65), m['wood_dark'])
    bmesh_box("GatePostR", (0.10, 0.10, 1.3), (2.25, 0.25, Z + 0.65), m['wood_dark'])
    bmesh_box("GateBeam", (0.10, 0.60, 0.08), (2.25, 0, Z + 1.30), m['wood_dark'])

    # === Haniwa figure (clay figurine) ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=0.40,
                                        location=(1.8, 1.5, Z + 0.20))
    bpy.context.active_object.data.materials.append(m['roof_edge'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(1.8, 1.5, Z + 0.48))
    bpy.context.active_object.data.materials.append(m['roof_edge'])


# ============================================================
# CLASSICAL AGE — Nara period temple-palace
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Stone platform (elaborate, multi-tier) ===
    bmesh_box("Plat1", (5.0, 4.6, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.04)
    bmesh_box("Plat2", (4.6, 4.2, 0.10), (0, 0, Z + 0.17), m['stone'], bevel=0.03)

    BZ = Z + 0.22

    # === Main hall (Kondo-style) ===
    hall_w, hall_d = 2.8, 2.2
    hall_h = 2.2

    # Red-painted pillars (iconic Nara style)
    for px in [-1.2, -0.6, 0, 0.6, 1.2]:
        for py in [-0.95, 0.95]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.08, depth=hall_h,
                                                location=(px, py, BZ + hall_h / 2))
            p = bpy.context.active_object
            p.name = f"RedPillar_{px:.1f}_{py:.1f}"
            p.data.materials.append(m['banner'])  # red material
            bpy.ops.object.shade_smooth()

    # White plaster walls
    bmesh_box("WallB", (0.06, 1.80, hall_h * 0.6), (-1.25, 0, BZ + hall_h * 0.3), m['stone_light'])
    bmesh_box("WallR", (2.40, 0.06, hall_h * 0.6), (0, -1.00, BZ + hall_h * 0.3), m['stone_light'])
    bmesh_box("WallL", (2.40, 0.06, hall_h * 0.6), (0, 1.00, BZ + hall_h * 0.3), m['stone_light'])

    # Dark timber framing on walls
    for py_sign in [-1, 1]:
        py_w = py_sign * 1.01
        bmesh_box(f"Frame_H_{py_sign}", (2.40, 0.04, 0.05), (0, py_w, BZ + hall_h * 0.6), m['wood_dark'])
        bmesh_box(f"Frame_B_{py_sign}", (2.40, 0.04, 0.05), (0, py_w, BZ + 0.02), m['wood_dark'])
        for fx in [-0.9, -0.3, 0.3, 0.9]:
            bmesh_box(f"Frame_V_{py_sign}_{fx:.1f}", (0.05, 0.04, hall_h * 0.6),
                      (fx, py_w, BZ + hall_h * 0.3), m['wood_dark'])

    # Door (central, front)
    bmesh_box("Door", (0.06, 0.55, 1.30), (1.26, 0, BZ + 0.65), m['door'])

    # === Graceful curved hip roof ===
    roof_z = BZ + hall_h
    _curved_roof("HallRoof", hall_w - 0.2, hall_d - 0.2, 1.4, (0, 0, roof_z), m['roof'],
                 overhang=0.35, curve_up=0.18)

    # Roof edge trim
    _curved_roof("RoofEdge", hall_w - 0.18, hall_d - 0.18, 1.35, (0, 0, roof_z - 0.02), m['roof_edge'],
                 overhang=0.38, curve_up=0.20)

    # Gold ornament at roof peak
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0, 0, roof_z + 1.40))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # === Covered walkway (kairo) around main hall ===
    for side_y, lbl in [(-1.5, "R"), (1.5, "L")]:
        bmesh_box(f"Kairo_{lbl}_Floor", (3.0, 0.45, 0.04), (0, side_y, BZ + 0.02), m['wood'])
        bmesh_box(f"Kairo_{lbl}_Rail", (3.0, 0.04, 0.35), (0, side_y - 0.20 * (-1 if side_y < 0 else 1), BZ + 0.20), m['banner'])
        # Walkway roof
        _curved_roof(f"KairoRoof_{lbl}", 3.0, 0.5, 0.45, (0, side_y, BZ + 1.2), m['roof'],
                     overhang=0.12, curve_up=0.06)
        # Walkway pillars
        for wx in [-1.2, -0.4, 0.4, 1.2]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=1.15,
                                                location=(wx, side_y, BZ + 0.60))
            bpy.context.active_object.data.materials.append(m['banner'])

    # === Five-story pagoda (iconic, side) ===
    PX, PY = -1.6, -1.2
    pag_z = BZ
    tier_sizes = [(0.70, 0.50), (0.58, 0.42), (0.46, 0.35), (0.36, 0.30), (0.28, 0.25)]

    for tier, (tw, th) in enumerate(tier_sizes):
        tz = pag_z + sum(s[1] + 0.10 for s in tier_sizes[:tier])
        # Tier body (white walls)
        bmesh_box(f"PagTier_{tier}", (tw, tw, th), (PX, PY, tz + th / 2), m['stone_light'])
        # Curved roof per tier
        _curved_roof(f"PagRoof_{tier}", tw + 0.05, tw + 0.05, 0.15,
                     (PX, PY, tz + th), m['roof'], overhang=0.12, curve_up=0.06)

    # Pagoda spire (sorin)
    spire_z = pag_z + sum(s[1] + 0.10 for s in tier_sizes)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.60,
                                        location=(PX, PY, spire_z + 0.30))
    bpy.context.active_object.data.materials.append(m['gold'])
    # Rings on spire
    for rz in [0.10, 0.20, 0.30, 0.40]:
        bmesh_prism(f"PagRing_{rz:.2f}", 0.06, 0.02, 8, (PX, PY, spire_z + rz), m['gold'])

    # === Steps to main hall ===
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.18, 1.2, 0.05), (1.40 + i * 0.20, 0, BZ - 0.03 - i * 0.04), m['stone'])

    # === Stone lantern ===
    LX, LY = 1.8, -1.6
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.06, depth=0.60,
                                        location=(LX, LY, Z + 0.30))
    bpy.context.active_object.data.materials.append(m['stone'])
    bmesh_box("LanternCap", (0.20, 0.20, 0.04), (LX, LY, Z + 0.62), m['stone'])
    bmesh_cone("LanternRoof", 0.16, 0.15, 4, (LX, LY, Z + 0.64), m['stone_dark'])


# ============================================================
# MEDIEVAL AGE — Himeji-style castle (tenshu)
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Stone foundation walls (ishigaki) with battered slope ===
    # The characteristic sloped stone base of Japanese castles
    # Built as a truncated pyramid using mesh_from_pydata
    base_w, base_d = 3.8, 3.4
    top_w, top_d = 3.2, 2.8
    ishi_h = 1.2
    bv = [
        (-base_w / 2, -base_d / 2, Z), (base_w / 2, -base_d / 2, Z),
        (base_w / 2, base_d / 2, Z), (-base_w / 2, base_d / 2, Z),
        (-top_w / 2, -top_d / 2, Z + ishi_h), (top_w / 2, -top_d / 2, Z + ishi_h),
        (top_w / 2, top_d / 2, Z + ishi_h), (-top_w / 2, top_d / 2, Z + ishi_h),
    ]
    bf = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    mesh_from_pydata("Ishigaki", bv, bf, m['stone_dark'])

    # Stone wall texture lines
    for i in range(4):
        lz = Z + 0.25 + i * 0.25
        t = lz / ishi_h
        lw = base_w + (top_w - base_w) * t
        ld = base_d + (top_d - base_d) * t
        bmesh_box(f"IshiLine_{i}", (lw + 0.02, ld + 0.02, 0.02), (0, 0, lz), m['stone'])

    BZ = Z + ishi_h

    # === Tier 1 (largest) — ground floor ===
    t1_w, t1_d, t1_h = 3.0, 2.5, 1.5
    bmesh_box("Tier1", (t1_w, t1_d, t1_h), (0, 0, BZ + t1_h / 2), m['stone_light'])

    # Dark timber frame on tier 1
    for py_s in [-1, 1]:
        py = py_s * t1_d / 2
        bmesh_box(f"T1FrameH_{py_s}", (t1_w, 0.04, 0.05), (0, py + py_s * 0.01, BZ + t1_h), m['wood_dark'])
        bmesh_box(f"T1FrameB_{py_s}", (t1_w, 0.04, 0.05), (0, py + py_s * 0.01, BZ + 0.02), m['wood_dark'])
        for fx in [-1.1, -0.4, 0.4, 1.1]:
            bmesh_box(f"T1FrameV_{py_s}_{fx:.1f}", (0.05, 0.04, t1_h),
                      (fx, py + py_s * 0.01, BZ + t1_h / 2), m['wood_dark'])
    for px_s in [-1, 1]:
        px = px_s * t1_w / 2
        bmesh_box(f"T1FrameH_X_{px_s}", (0.04, t1_d, 0.05), (px + px_s * 0.01, 0, BZ + t1_h), m['wood_dark'])
        bmesh_box(f"T1FrameB_X_{px_s}", (0.04, t1_d, 0.05), (px + px_s * 0.01, 0, BZ + 0.02), m['wood_dark'])

    # Windows (shoji-style, small rectangles)
    for y in [-0.8, -0.1, 0.6]:
        bmesh_box(f"T1WinF_{y:.1f}", (0.06, 0.25, 0.35), (t1_w / 2 + 0.01, y, BZ + 0.80), m['window'])
        bmesh_box(f"T1WinFr_{y:.1f}", (0.07, 0.27, 0.03), (t1_w / 2 + 0.02, y, BZ + 1.00), m['win_frame'])

    # Curved roof tier 1
    t1_roof_z = BZ + t1_h
    _curved_roof("Tier1Roof", t1_w, t1_d, 0.55, (0, 0, t1_roof_z), m['roof'],
                 overhang=0.40, curve_up=0.18)

    # === Tier 2 (medium) ===
    t2_w, t2_d, t2_h = 2.2, 1.8, 1.2
    t2_z = t1_roof_z + 0.55
    bmesh_box("Tier2", (t2_w, t2_d, t2_h), (0, 0, t2_z + t2_h / 2), m['stone_light'])

    # Timber framing tier 2
    for py_s in [-1, 1]:
        py = py_s * t2_d / 2
        bmesh_box(f"T2FrameH_{py_s}", (t2_w, 0.04, 0.04), (0, py + py_s * 0.01, t2_z + t2_h), m['wood_dark'])
        bmesh_box(f"T2FrameB_{py_s}", (t2_w, 0.04, 0.04), (0, py + py_s * 0.01, t2_z + 0.02), m['wood_dark'])
        for fx in [-0.7, 0, 0.7]:
            bmesh_box(f"T2FrameV_{py_s}_{fx:.1f}", (0.04, 0.04, t2_h),
                      (fx, py + py_s * 0.01, t2_z + t2_h / 2), m['wood_dark'])

    # Windows tier 2
    for y in [-0.5, 0.2]:
        bmesh_box(f"T2WinF_{y:.1f}", (0.06, 0.22, 0.30), (t2_w / 2 + 0.01, y, t2_z + 0.60), m['window'])
        bmesh_box(f"T2WinFr_{y:.1f}", (0.07, 0.24, 0.03), (t2_w / 2 + 0.02, y, t2_z + 0.78), m['win_frame'])

    # Curved roof tier 2
    t2_roof_z = t2_z + t2_h
    _curved_roof("Tier2Roof", t2_w, t2_d, 0.45, (0, 0, t2_roof_z), m['roof'],
                 overhang=0.35, curve_up=0.15)

    # === Tier 3 (smaller) ===
    t3_w, t3_d, t3_h = 1.5, 1.2, 1.0
    t3_z = t2_roof_z + 0.45
    bmesh_box("Tier3", (t3_w, t3_d, t3_h), (0, 0, t3_z + t3_h / 2), m['stone_light'])

    # Timber framing tier 3
    for py_s in [-1, 1]:
        py = py_s * t3_d / 2
        bmesh_box(f"T3FrameH_{py_s}", (t3_w, 0.03, 0.04), (0, py + py_s * 0.01, t3_z + t3_h), m['wood_dark'])
        bmesh_box(f"T3FrameB_{py_s}", (t3_w, 0.03, 0.04), (0, py + py_s * 0.01, t3_z + 0.02), m['wood_dark'])

    # Windows tier 3
    for y in [-0.3, 0.3]:
        bmesh_box(f"T3WinF_{y:.1f}", (0.05, 0.18, 0.25), (t3_w / 2 + 0.01, y, t3_z + 0.50), m['window'])

    # Curved roof tier 3
    t3_roof_z = t3_z + t3_h
    _curved_roof("Tier3Roof", t3_w, t3_d, 0.40, (0, 0, t3_roof_z), m['roof'],
                 overhang=0.30, curve_up=0.14)

    # === Top tier (smallest, lookout) ===
    t4_w, t4_d, t4_h = 0.9, 0.7, 0.8
    t4_z = t3_roof_z + 0.40
    bmesh_box("Tier4", (t4_w, t4_d, t4_h), (0, 0, t4_z + t4_h / 2), m['stone_light'])

    # Final curved roof
    t4_roof_z = t4_z + t4_h
    _curved_roof("Tier4Roof", t4_w, t4_d, 0.40, (0, 0, t4_roof_z), m['roof'],
                 overhang=0.22, curve_up=0.12)

    # === Gold shachihoko (fish ornaments on main roof peak) ===
    for dy in [-0.15, 0.15]:
        # Stylized fish — body + tail
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08,
                                              location=(0, dy, t4_roof_z + 0.42))
        sh = bpy.context.active_object
        sh.name = f"Shachi_{dy:.2f}"
        sh.scale = (1.2, 0.6, 1)
        sh.data.materials.append(m['gold'])
        bpy.ops.object.shade_smooth()
        # Tail fin
        tv = [(0, dy, t4_roof_z + 0.48),
              (0, dy + 0.08 * (-1 if dy < 0 else 1), t4_roof_z + 0.55),
              (0, dy, t4_roof_z + 0.55)]
        mesh_from_pydata(f"ShachiTail_{dy:.2f}", tv, [(0, 1, 2)], m['gold'])

    # === Gate in the ishigaki base ===
    bmesh_box("Gate", (0.08, 0.55, 0.90), (base_w / 2 + 0.01, 0, Z + 0.45), m['door'])
    bmesh_box("GateFrame", (0.10, 0.65, 0.06), (base_w / 2 + 0.02, 0, Z + 0.92), m['wood_dark'])

    # === Stone steps ===
    for i in range(6):
        bmesh_box(f"Step_{i}", (0.18, 1.0, 0.05), (base_w / 2 + 0.20 + i * 0.18, 0, Z - 0.03 + i * 0.03), m['stone'])

    # === Corner watchtower (small yagura) ===
    yx, yy = -1.3, -1.2
    bmesh_box("YaguraBase", (0.70, 0.60, 0.80), (yx, yy, BZ + 0.40), m['stone_light'])
    _curved_roof("YaguraRoof", 0.80, 0.70, 0.35, (yx, yy, BZ + 0.80), m['roof'],
                 overhang=0.15, curve_up=0.08)

    # === Banner ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.80,
                                        location=(0, 0, t4_roof_z + 0.80))
    bpy.context.active_object.data.materials.append(m['wood'])
    bv = [(0.03, 0, t4_roof_z + 1.00), (0.40, 0.03, t4_roof_z + 0.97),
          (0.40, 0.02, t4_roof_z + 1.22), (0.03, 0, t4_roof_z + 1.20)]
    mesh_from_pydata("Banner", bv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# GUNPOWDER AGE — Azuchi-Momoyama castle (5-story tenshu)
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Massive ishigaki (stone walls) with outer wall ===
    # Outer wall circuit
    ow_hw = 2.5
    ow_h = 1.0
    bmesh_box("OuterWallF", (0.15, ow_hw * 2, ow_h), (ow_hw, 0, Z + ow_h / 2), m['stone'], bevel=0.02)
    bmesh_box("OuterWallB", (0.15, ow_hw * 2, ow_h), (-ow_hw, 0, Z + ow_h / 2), m['stone'], bevel=0.02)
    bmesh_box("OuterWallR", (ow_hw * 2, 0.15, ow_h), (0, -ow_hw, Z + ow_h / 2), m['stone'], bevel=0.02)
    bmesh_box("OuterWallL", (ow_hw * 2, 0.15, ow_h), (0, ow_hw, Z + ow_h / 2), m['stone'], bevel=0.02)

    # Roof tiles on outer wall
    for pos, dims in [("F", (0.22, ow_hw * 2, 0.06)), ("B", (0.22, ow_hw * 2, 0.06)),
                      ("R", (ow_hw * 2, 0.22, 0.06)), ("L", (ow_hw * 2, 0.22, 0.06))]:
        if pos == "F":
            bmesh_box(f"OWRoof_{pos}", dims, (ow_hw, 0, Z + ow_h + 0.03), m['roof'])
        elif pos == "B":
            bmesh_box(f"OWRoof_{pos}", dims, (-ow_hw, 0, Z + ow_h + 0.03), m['roof'])
        elif pos == "R":
            bmesh_box(f"OWRoof_{pos}", dims, (0, -ow_hw, Z + ow_h + 0.03), m['roof'])
        else:
            bmesh_box(f"OWRoof_{pos}", dims, (0, ow_hw, Z + ow_h + 0.03), m['roof'])

    # Gatehouse (mon)
    bmesh_box("GatePillarL", (0.12, 0.12, 1.4), (ow_hw + 0.01, -0.35, Z + 0.70), m['wood_dark'])
    bmesh_box("GatePillarR", (0.12, 0.12, 1.4), (ow_hw + 0.01, 0.35, Z + 0.70), m['wood_dark'])
    _curved_roof("GateRoof", 0.40, 0.90, 0.30, (ow_hw + 0.01, 0, Z + 1.40), m['roof'],
                 overhang=0.15, curve_up=0.08)
    bmesh_box("GateDoor", (0.06, 0.50, 0.90), (ow_hw + 0.08, 0, Z + 0.45), m['door'])

    # === Main ishigaki base (battered stone, taller) ===
    base_w, base_d = 3.0, 2.6
    top_w, top_d = 2.4, 2.0
    ishi_h = 1.5
    bv = [
        (-base_w / 2, -base_d / 2, Z), (base_w / 2, -base_d / 2, Z),
        (base_w / 2, base_d / 2, Z), (-base_w / 2, base_d / 2, Z),
        (-top_w / 2, -top_d / 2, Z + ishi_h), (top_w / 2, -top_d / 2, Z + ishi_h),
        (top_w / 2, top_d / 2, Z + ishi_h), (-top_w / 2, top_d / 2, Z + ishi_h),
    ]
    bf = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    mesh_from_pydata("Ishigaki", bv, bf, m['stone_dark'])

    BZ = Z + ishi_h

    # === 5-story tenshu ===
    tier_specs = [
        # (width, depth, height)
        (2.3, 1.9, 1.2),   # Floor 1 (largest)
        (2.0, 1.6, 1.0),   # Floor 2
        (1.6, 1.3, 0.9),   # Floor 3
        (1.2, 1.0, 0.8),   # Floor 4
        (0.8, 0.7, 0.7),   # Floor 5 (smallest, top)
    ]

    cur_z = BZ
    for tier, (tw, td, th) in enumerate(tier_specs):
        # White plaster walls
        bmesh_box(f"Tier{tier}", (tw, td, th), (0, 0, cur_z + th / 2), m['stone_light'])

        # Dark timber frame
        for py_s in [-1, 1]:
            py = py_s * td / 2
            bmesh_box(f"T{tier}FH_{py_s}", (tw, 0.03, 0.04), (0, py + py_s * 0.01, cur_z + th), m['wood_dark'])
            bmesh_box(f"T{tier}FB_{py_s}", (tw, 0.03, 0.04), (0, py + py_s * 0.01, cur_z + 0.02), m['wood_dark'])
            n_verts = max(2, int(tw / 0.4))
            for vi in range(n_verts):
                vx = -tw / 2 + 0.2 + vi * (tw - 0.4) / max(1, n_verts - 1)
                bmesh_box(f"T{tier}FV_{py_s}_{vi}", (0.04, 0.03, th),
                          (vx, py + py_s * 0.01, cur_z + th / 2), m['wood_dark'])
        for px_s in [-1, 1]:
            px = px_s * tw / 2
            bmesh_box(f"T{tier}FHx_{px_s}", (0.03, td, 0.04), (px + px_s * 0.01, 0, cur_z + th), m['wood_dark'])

        # Windows
        if tier < 4:
            n_win = max(1, int(tw / 0.5))
            for wi in range(n_win):
                wy = -tw / 2 + 0.3 + wi * (tw - 0.6) / max(1, n_win - 1) if n_win > 1 else 0
                bmesh_box(f"T{tier}Win_{wi}", (0.05, 0.18, 0.22),
                          (tw / 2 + 0.01, wy, cur_z + th * 0.55), m['window'])

        # Curved roof
        _curved_roof(f"Tier{tier}Roof", tw, td, 0.35 + tier * 0.02,
                     (0, 0, cur_z + th), m['roof'],
                     overhang=0.30 - tier * 0.03, curve_up=0.14 - tier * 0.01)

        # Gold leaf accent line on upper tiers
        if tier >= 2:
            bmesh_box(f"T{tier}Gold", (tw + 0.02, td + 0.02, 0.03),
                      (0, 0, cur_z + th - 0.05), m['gold'])

        cur_z += th + 0.35 + tier * 0.02  # next tier starts above roof

    # === Gold shachihoko on top ===
    top_z = cur_z - 0.02
    for dy in [-0.12, 0.12]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10,
                                              location=(0, dy, top_z + 0.12))
        sh = bpy.context.active_object
        sh.name = f"Shachi_{dy:.2f}"
        sh.scale = (1.3, 0.6, 1.2)
        sh.data.materials.append(m['gold'])
        bpy.ops.object.shade_smooth()

    # === Corner turrets (attached to outer wall) ===
    for xs, ys, lbl in [(-1, -1, "BL"), (1, 1, "FR")]:
        tx, ty = xs * ow_hw, ys * ow_hw
        bmesh_box(f"Turret_{lbl}", (0.50, 0.50, 1.4), (tx, ty, Z + 0.70), m['stone_light'])
        _curved_roof(f"TurretRoof_{lbl}", 0.55, 0.55, 0.25,
                     (tx, ty, Z + 1.40), m['roof'], overhang=0.12, curve_up=0.06)

    # Steps
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.16, 0.80, 0.05),
                  (ow_hw + 0.25 + i * 0.18, 0, Z - 0.03 + i * 0.02), m['stone'])

    # Banner
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.70,
                                        location=(0, 0, top_z + 0.50))
    bpy.context.active_object.data.materials.append(m['wood'])
    bverts = [(0.03, 0, top_z + 0.65), (0.40, 0.03, top_z + 0.62),
              (0.40, 0.02, top_z + 0.90), (0.03, 0, top_z + 0.88)]
    mesh_from_pydata("Banner", bverts, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# ENLIGHTENMENT AGE — Edo period shogun palace
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Stone platform ===
    bmesh_box("Plat", (5.0, 4.8, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.15

    # === Main palace (shoin-zukuri style, wide and elegant) ===
    main_w, main_d = 3.6, 2.4
    main_h = 2.0

    # Raised wooden floor
    bmesh_box("MainFloor", (main_w + 0.10, main_d + 0.10, 0.08), (0, 0, BZ + 0.04), m['wood'])

    # White plaster walls with dark timber frame (shikkui + timber)
    bmesh_box("MainWallB", (0.08, main_d, main_h), (-main_w / 2, 0, BZ + 0.08 + main_h / 2), m['stone_light'])
    bmesh_box("MainWallR", (main_w, 0.08, main_h), (0, -main_d / 2, BZ + 0.08 + main_h / 2), m['stone_light'])
    bmesh_box("MainWallL", (main_w, 0.08, main_h), (0, main_d / 2, BZ + 0.08 + main_h / 2), m['stone_light'])

    # Dark timber grid on walls
    for py_s in [-1, 1]:
        py = py_s * main_d / 2 + py_s * 0.01
        for fz in [BZ + 0.10, BZ + 0.08 + main_h]:
            bmesh_box(f"MFH_{py_s}_{fz:.2f}", (main_w, 0.04, 0.05), (0, py, fz), m['wood_dark'])
        for fx in range(8):
            vx = -main_w / 2 + 0.25 + fx * (main_w - 0.50) / 7
            bmesh_box(f"MFV_{py_s}_{fx}", (0.04, 0.04, main_h),
                      (vx, py, BZ + 0.08 + main_h / 2), m['wood_dark'])

    # Front: shoji screen panels (translucent sliding doors)
    for wy in range(6):
        sy = -main_d / 2 + 0.25 + wy * (main_d - 0.50) / 5
        bmesh_box(f"Shoji_{wy}", (0.04, 0.30, 1.30),
                  (main_w / 2, sy, BZ + 0.08 + 0.65), m['plaster'])
        bmesh_box(f"ShojiFrame_{wy}", (0.05, 0.32, 0.03),
                  (main_w / 2 + 0.01, sy, BZ + 0.08 + 1.32), m['wood_dark'])

    # === Deep curved hip roof (characteristic Edo style) ===
    roof_z = BZ + 0.08 + main_h
    _curved_roof("MainRoof", main_w, main_d, 1.5, (0, 0, roof_z), m['roof'],
                 overhang=0.50, curve_up=0.22)
    _curved_roof("MainRoofEdge", main_w + 0.02, main_d + 0.02, 1.45, (0, 0, roof_z - 0.03), m['roof_edge'],
                 overhang=0.53, curve_up=0.24)

    # Gold ridge ornaments
    for dx in [-0.8, 0, 0.8]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(dx, 0, roof_z + 1.50))
        bpy.context.active_object.data.materials.append(m['gold'])
        bpy.ops.object.shade_smooth()

    # === Karahafu gable (ornate curved gable over entrance) ===
    gable_z = roof_z + 0.30
    gv = [(main_w / 2 + 0.50, -0.50, gable_z),
          (main_w / 2 + 0.50, 0.50, gable_z),
          (main_w / 2 + 0.55, 0, gable_z + 0.40)]
    mesh_from_pydata("Karahafu", gv, [(0, 1, 2)], m['roof'])

    # === Guardhouse (bansho) at the entrance ===
    GX, GY = 2.0, -1.2
    bmesh_box("GuardFloor", (0.90, 0.70, 0.06), (GX, GY, BZ + 0.03), m['wood'])
    bmesh_box("GuardWallB", (0.05, 0.60, 1.0), (GX - 0.40, GY, BZ + 0.06 + 0.50), m['stone_light'])
    bmesh_box("GuardWallR", (0.80, 0.05, 1.0), (GX, GY - 0.30, BZ + 0.06 + 0.50), m['stone_light'])
    bmesh_box("GuardWallL", (0.80, 0.05, 1.0), (GX, GY + 0.30, BZ + 0.06 + 0.50), m['stone_light'])
    _curved_roof("GuardRoof", 0.90, 0.70, 0.40, (GX, GY, BZ + 1.06), m['roof'],
                 overhang=0.15, curve_up=0.06)

    # === Ornate gate (mon) ===
    gate_x = 2.3
    bmesh_box("GatePillarL", (0.12, 0.12, 1.8), (gate_x, -0.50, BZ + 0.90), m['wood_dark'])
    bmesh_box("GatePillarR", (0.12, 0.12, 1.8), (gate_x, 0.50, BZ + 0.90), m['wood_dark'])
    _curved_roof("GateRoof", 0.50, 1.20, 0.35, (gate_x, 0, BZ + 1.80), m['roof'],
                 overhang=0.18, curve_up=0.10)
    bmesh_box("GateDoor", (0.06, 0.65, 1.30), (gate_x + 0.06, 0, BZ + 0.65), m['door'])

    # Gold gate ornament
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(gate_x, 0, BZ + 2.17))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # === Zen garden area ===
    bmesh_box("GardenBed", (1.2, 1.0, 0.04), (-1.8, 1.5, BZ + 0.02), m['stone_light'])
    # Raked gravel lines
    for gi in range(6):
        gy = 1.1 + gi * 0.15
        bmesh_box(f"Gravel_{gi}", (1.0, 0.02, 0.01), (-1.8, gy, BZ + 0.045), m['stone'])
    # Stones in garden
    for sx, sy, sr in [(-2.0, 1.3, 0.08), (-1.6, 1.6, 0.06), (-1.9, 1.8, 0.05)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=sr, location=(sx, sy, BZ + sr))
        bpy.context.active_object.data.materials.append(m['stone_dark'])

    # === Wing building (lower, connected) ===
    WX, WY = -0.5, -1.8
    bmesh_box("WingFloor", (2.0, 0.90, 0.06), (WX, WY, BZ + 0.03), m['wood'])
    bmesh_box("WingWall", (2.0, 0.06, 1.2), (WX, WY - 0.42, BZ + 0.06 + 0.60), m['stone_light'])
    bmesh_box("WingWallB", (0.06, 0.90, 1.2), (WX - 1.0, WY, BZ + 0.06 + 0.60), m['stone_light'])
    _curved_roof("WingRoof", 2.0, 0.90, 0.55, (WX, WY, BZ + 1.26), m['roof'],
                 overhang=0.20, curve_up=0.10)

    # Steps
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.16, 1.2, 0.04), (gate_x + 0.20 + i * 0.16, 0, BZ - 0.02 - i * 0.03), m['stone'])

    # Stone lanterns
    for lx, ly in [(2.2, 1.4), (-2.2, -0.8)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=0.50,
                                            location=(lx, ly, BZ + 0.25))
        bpy.context.active_object.data.materials.append(m['stone'])
        bmesh_box(f"LCap_{lx:.1f}", (0.16, 0.16, 0.03), (lx, ly, BZ + 0.52), m['stone'])
        bmesh_cone(f"LRoof_{lx:.1f}", 0.12, 0.10, 4, (lx, ly, BZ + 0.55), m['stone_dark'])


# ============================================================
# INDUSTRIAL AGE — Meiji era Western-Japanese fusion
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation ===
    bmesh_box("Found", (5.2, 4.8, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.15

    # === Main building — brick base, Western proportions ===
    main_w, main_d = 3.4, 2.6
    main_h = 3.0

    # Brick lower section (Meiji Western influence)
    bmesh_box("BrickBase", (main_w, main_d, main_h * 0.4), (0, 0, BZ + main_h * 0.2), m['stone'], bevel=0.02)

    # Brick pattern lines
    for bz_i in range(4):
        lz = BZ + 0.15 + bz_i * 0.25
        bmesh_box(f"BrickLine_{bz_i}", (main_w + 0.02, main_d + 0.02, 0.02), (0, 0, lz), m['stone_trim'])

    # Upper section (plastered, lighter)
    bmesh_box("UpperWalls", (main_w, main_d, main_h * 0.6),
              (0, 0, BZ + main_h * 0.4 + main_h * 0.3), m['stone_light'])

    # Dark timber frame (Japanese influence on upper story)
    for py_s in [-1, 1]:
        py = py_s * main_d / 2 + py_s * 0.01
        bmesh_box(f"TimberH_{py_s}", (main_w, 0.04, 0.05), (0, py, BZ + main_h * 0.4), m['wood_dark'])
        bmesh_box(f"TimberT_{py_s}", (main_w, 0.04, 0.05), (0, py, BZ + main_h), m['wood_dark'])
        for fx in range(6):
            vx = -main_w / 2 + 0.35 + fx * (main_w - 0.70) / 5
            bmesh_box(f"TimberV_{py_s}_{fx}", (0.04, 0.04, main_h * 0.6),
                      (vx, py, BZ + main_h * 0.4 + main_h * 0.3), m['wood_dark'])

    # Windows (Western-style arched on brick, Japanese-style on upper)
    # Lower row — arched Western windows
    for y in [-0.9, -0.3, 0.3, 0.9]:
        bmesh_box(f"LowWin_{y:.1f}", (0.06, 0.22, 0.45),
                  (main_w / 2 + 0.01, y, BZ + 0.50), m['window'])
        bmesh_box(f"LowWinH_{y:.1f}", (0.07, 0.26, 0.04),
                  (main_w / 2 + 0.02, y, BZ + 0.75), m['stone_trim'])

    # Upper row — taller Japanese-proportion windows
    for y in [-0.9, -0.3, 0.3, 0.9]:
        bmesh_box(f"UpWin_{y:.1f}", (0.06, 0.20, 0.55),
                  (main_w / 2 + 0.01, y, BZ + main_h * 0.4 + 0.55), m['window'])
        bmesh_box(f"UpWinFr_{y:.1f}", (0.07, 0.22, 0.03),
                  (main_w / 2 + 0.02, y, BZ + main_h * 0.4 + 0.85), m['win_frame'])

    # Side windows
    for x in [-1.0, -0.2, 0.6]:
        bmesh_box(f"SideWin_{x:.1f}", (0.20, 0.06, 0.45),
                  (x, -main_d / 2 - 0.01, BZ + main_h * 0.4 + 0.55), m['window'])

    # === Japanese-style curved roof on Western building ===
    roof_z = BZ + main_h
    _curved_roof("MainRoof", main_w, main_d, 1.2, (0, 0, roof_z), m['roof'],
                 overhang=0.40, curve_up=0.18)

    # Ridge ornaments
    for dx in [-0.6, 0, 0.6]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(dx, 0, roof_z + 1.20))
        bpy.context.active_object.data.materials.append(m['gold'])
        bpy.ops.object.shade_smooth()

    # === Clock tower (yagura-style with Western clock) ===
    TX, TY = -0.8, -1.0
    ct_base = roof_z + 0.05
    ct_w = 0.75
    ct_h = 2.2
    bmesh_box("ClockTower", (ct_w, ct_w, ct_h), (TX, TY, ct_base + ct_h / 2), m['stone_light'])

    # Timber frame on clock tower
    for side in [-1, 1]:
        bmesh_box(f"CTFrame_{side}", (ct_w, 0.04, 0.04),
                  (TX, TY + side * ct_w / 2 + side * 0.01, ct_base + ct_h), m['wood_dark'])
        bmesh_box(f"CTFrameB_{side}", (ct_w, 0.04, 0.04),
                  (TX, TY + side * ct_w / 2 + side * 0.01, ct_base + 0.02), m['wood_dark'])

    # Clock face (Western element)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.22, depth=0.04,
                                        location=(TX + ct_w / 2 + 0.01, TY, ct_base + ct_h * 0.6))
    clock = bpy.context.active_object
    clock.name = "Clock"
    clock.rotation_euler = (0, math.radians(90), 0)
    clock.data.materials.append(m['gold'])

    # Japanese-style roof on clock tower
    _curved_roof("CTRoof", ct_w, ct_w, 0.45, (TX, TY, ct_base + ct_h), m['roof'],
                 overhang=0.15, curve_up=0.08)

    # Gold finial
    bmesh_cone("CTFinial", 0.06, 0.30, 8, (TX, TY, ct_base + ct_h + 0.45), m['gold'])

    # === Entrance portico (Western columns with Japanese roof) ===
    for dy in [-0.45, 0.45]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=2.0,
                                            location=(main_w / 2 + 0.45, dy, BZ + 1.0))
        c = bpy.context.active_object
        c.name = f"PorCol_{dy:.2f}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()

    # Portico roof (Japanese curve)
    _curved_roof("PorRoof", 0.50, 1.10, 0.25, (main_w / 2 + 0.45, 0, BZ + 2.05), m['roof'],
                 overhang=0.12, curve_up=0.06)

    # Door
    bmesh_box("Door", (0.08, 0.60, 1.50), (main_w / 2 + 0.01, 0, BZ + 0.75), m['door'])
    bmesh_box("DoorFrame", (0.10, 0.70, 0.06), (main_w / 2 + 0.02, 0, BZ + 1.53), m['wood_dark'])

    # === Iron fence (Western influence) ===
    for i in range(12):
        fy = -1.6 + i * 0.28
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.55,
                                            location=(main_w / 2 + 0.90, fy, BZ + 0.15))
        bpy.context.active_object.data.materials.append(m['iron'])

    # Steps
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.18, 1.6, 0.05),
                  (main_w / 2 + 0.65 + i * 0.20, 0, BZ - 0.03 - i * 0.04), m['stone'])

    # Chimney (brick)
    bmesh_box("Chimney", (0.25, 0.25, 1.5), (-main_w / 2 + 0.4, 0.8, roof_z + 0.75), m['stone'])
    bmesh_box("ChimTop", (0.30, 0.30, 0.06), (-main_w / 2 + 0.4, 0.8, roof_z + 1.53), m['stone_trim'])


# ============================================================
# MODERN AGE — Post-war Japanese modernist
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Foundation ===
    bmesh_box("Found", (5.2, 4.8, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    BZ = Z + 0.08

    # === Main building — clean concrete, Japanese proportions ===
    main_w, main_d = 3.2, 2.4
    main_h = 3.8
    bmesh_box("Main", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone'])

    # Clean horizontal lines (concrete bands, tatami-proportion rhythm)
    for bz_i in range(5):
        lz = BZ + 0.60 + bz_i * 0.70
        bmesh_box(f"Band_{bz_i}", (main_w + 0.04, main_d + 0.04, 0.04),
                  (0, 0, lz), m['stone_trim'])

    # Glass curtain wall on front (full height)
    bmesh_box("FrontGlass", (0.06, main_d - 0.5, main_h - 0.3),
              (main_w / 2 + 0.01, 0, BZ + main_h / 2 + 0.1), glass)

    # Vertical mullions (aluminum)
    for y in [-0.7, -0.2, 0.3, 0.8]:
        bmesh_box(f"Mullion_{y:.1f}", (0.04, 0.03, main_h - 0.4),
                  (main_w / 2 + 0.03, y, BZ + main_h / 2 + 0.1), metal)

    # Side windows (narrow horizontal bands — Japanese modernist style)
    for x in [-1.0, 0, 1.0]:
        for bz_i in range(3):
            wz = BZ + 1.0 + bz_i * 1.0
            bmesh_box(f"SideWin_{x:.1f}_{bz_i}", (0.50, 0.05, 0.25),
                      (x, -main_d / 2 - 0.01, wz), glass)

    # Flat roof with slight overhang (Japanese floating-roof effect)
    bmesh_box("RoofSlab", (main_w + 0.30, main_d + 0.30, 0.10),
              (0, 0, BZ + main_h + 0.05), m['stone_dark'])

    # === Lower wing ===
    wing_w, wing_d, wing_h = 2.0, 1.6, 2.2
    WX = 1.5
    bmesh_box("Wing", (wing_w, wing_d, wing_h), (WX, 0, BZ + wing_h / 2), m['stone'])
    bmesh_box("WingGlass", (0.05, wing_d - 0.4, wing_h - 0.4),
              (WX + wing_w / 2 + 0.01, 0, BZ + wing_h / 2 + 0.1), glass)
    bmesh_box("WingRoof", (wing_w + 0.20, wing_d + 0.20, 0.08),
              (WX, 0, BZ + wing_h + 0.04), m['stone_dark'])

    # Connection between main and wing
    bmesh_box("Connect", (0.6, 1.0, 2.0), (main_w / 2 + 0.30, 0, BZ + 1.0), glass)

    # === Zen garden (karesansui — dry landscape) ===
    bmesh_box("Garden", (1.8, 1.6, 0.03), (-1.8, 1.3, BZ + 0.015), m['stone_light'])
    # Raked gravel pattern (concentric lines around rocks)
    for gi in range(8):
        gy = 0.65 + gi * 0.18
        bmesh_box(f"Gravel_{gi}", (1.5, 0.015, 0.008), (-1.8, gy, BZ + 0.035), m['stone'])
    # Garden rocks
    for rx, ry, rr in [(-2.1, 1.1, 0.10), (-1.5, 1.4, 0.07), (-2.0, 1.6, 0.06)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=rr, location=(rx, ry, BZ + rr))
        bpy.context.active_object.data.materials.append(m['stone_dark'])

    # === Entrance canopy (floating slab) ===
    bmesh_box("Canopy", (1.0, 2.0, 0.06),
              (main_w / 2 + 0.55, 0, BZ + 1.60), metal)
    # Single column support
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=1.50,
                                        location=(main_w / 2 + 0.55, -0.80, BZ + 0.83))
    bpy.context.active_object.data.materials.append(metal)

    # Glass door
    bmesh_box("GlassDoor", (0.05, 1.2, 1.80),
              (main_w / 2 + 0.01, 0, BZ + 0.90), glass)

    # === Small water feature ===
    bmesh_box("WaterBasin", (0.30, 0.30, 0.20),
              (-2.2, -1.5, BZ + 0.10), m['stone'])
    # Bamboo spout
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.35,
                                        location=(-2.2, -1.5 - 0.18, BZ + 0.35))
    bc = bpy.context.active_object
    bc.name = "BambooSpout"
    bc.rotation_euler = (math.radians(30), 0, 0)
    bc.data.materials.append(m['wood'])

    # Steps
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.16, 1.4, 0.04),
                  (main_w / 2 + 0.75 + i * 0.18, 0, BZ - 0.02 - i * 0.02), m['stone'])

    # Antenna / communication mast
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=1.5,
                                        location=(0, 0, BZ + main_h + 0.85))
    bpy.context.active_object.data.materials.append(metal)


# ============================================================
# DIGITAL AGE — Ultra-modern Japanese
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Foundation (minimal, floating effect) ===
    bmesh_box("Found", (5.0, 4.6, 0.06), (0, 0, Z + 0.03), m['stone_dark'])

    BZ = Z + 0.06

    # === Sleek glass tower (main structure) ===
    tower_w, tower_d = 2.2, 1.8
    tower_h = 5.5
    bmesh_box("Tower", (tower_w, tower_d, tower_h), (0, 0, BZ + tower_h / 2), glass)

    # Steel frame
    for tz in range(6):
        hz = BZ + 0.8 + tz * 0.85
        bmesh_box(f"TFrame_{tz}", (tower_w + 0.02, tower_d + 0.02, 0.04), (0, 0, hz), metal)
    for y in [-0.6, 0, 0.6]:
        bmesh_box(f"TVF_{y:.1f}", (0.03, 0.03, tower_h), (tower_w / 2 + 0.01, y, BZ + tower_h / 2), metal)
        bmesh_box(f"TVB_{y:.1f}", (0.03, 0.03, tower_h), (-tower_w / 2 - 0.01, y, BZ + tower_h / 2), metal)

    # === Floating curved roof tiers (signature feature) ===
    # Three floating Japanese-style curved roofs at different heights
    # They are detached, supported on thin pillars, giving a futuristic look
    float_tiers = [
        (2.6, 2.2, BZ + 2.0, 0.50),   # lowest, largest
        (2.0, 1.6, BZ + 3.8, 0.40),   # middle
        (1.4, 1.0, BZ + tower_h + 0.15, 0.35),  # top
    ]

    for ti, (fw, fd, fz, fh) in enumerate(float_tiers):
        _curved_roof(f"FloatRoof_{ti}", fw, fd, fh, (0, 0, fz), m['roof'],
                     overhang=0.30, curve_up=0.15)
        # Thin support columns for floating roofs
        for dx, dy in [(-fw / 4, -fd / 4), (fw / 4, fd / 4)]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=0.30,
                                                location=(dx, dy, fz - 0.15))
            bpy.context.active_object.data.materials.append(metal)

    # Gold accent on top floating roof
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08,
                                          location=(0, 0, float_tiers[2][2] + float_tiers[2][3] + 0.05))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # === LED torii gate (modern interpretation) ===
    TX, TY = 2.2, 0
    torii_h = 2.0
    torii_w = 1.0
    # Pillars (thin metal)
    for dy in [-torii_w / 2, torii_w / 2]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=torii_h,
                                            location=(TX, TY + dy, BZ + torii_h / 2))
        bpy.context.active_object.data.materials.append(metal)

    # Kasagi (top beam) — LED-lit
    bmesh_box("ToriiKasagi", (0.08, torii_w + 0.30, 0.06),
              (TX, TY, BZ + torii_h + 0.03), m['gold'])
    # Nuki (lower beam) — LED-lit
    bmesh_box("ToriiNuki", (0.06, torii_w + 0.10, 0.04),
              (TX, TY, BZ + torii_h - 0.25), m['gold'])
    # LED strips on torii
    bmesh_box("ToriiLED_L", (0.02, 0.02, torii_h),
              (TX + 0.03, TY - torii_w / 2, BZ + torii_h / 2), m['gold'])
    bmesh_box("ToriiLED_R", (0.02, 0.02, torii_h),
              (TX + 0.03, TY + torii_w / 2, BZ + torii_h / 2), m['gold'])

    # === Cherry blossom hologram (glowing pink sphere cluster) ===
    # Represented as a cluster of small glowing spheres
    holo_x, holo_y, holo_z = -1.8, 1.2, BZ + 1.5
    # Hologram projector base
    bmesh_prism("HoloProjBase", 0.20, 0.15, 8, (holo_x, holo_y, BZ), metal)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.5,
                                        location=(holo_x, holo_y, BZ + 0.40))
    bpy.context.active_object.data.materials.append(metal)

    # Cherry blossom hologram cluster (gold/banner material for pink glow)
    blossom_offsets = [(0, 0, 0), (0.15, 0.10, 0.08), (-0.12, 0.08, 0.05),
                       (0.05, -0.12, 0.12), (-0.08, -0.06, -0.05),
                       (0.10, -0.05, -0.08), (-0.15, 0.02, 0.10),
                       (0.02, 0.15, -0.03)]
    for bi, (bx, by, bbz) in enumerate(blossom_offsets):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06,
                                              location=(holo_x + bx, holo_y + by, holo_z + bbz))
        bl = bpy.context.active_object
        bl.name = f"Blossom_{bi}"
        bl.data.materials.append(m['banner'])  # pink/red glow
        bpy.ops.object.shade_smooth()

    # === Lower connected wing ===
    wing_w, wing_d, wing_h = 2.4, 1.4, 2.5
    WX = 0.8
    bmesh_box("Wing", (wing_w, wing_d, wing_h), (WX, -0.8, BZ + wing_h / 2), glass)
    for wz in range(3):
        hz = BZ + 0.7 + wz * 0.8
        bmesh_box(f"WingFrame_{wz}", (wing_w + 0.02, wing_d + 0.02, 0.03),
                  (WX, -0.8, hz), metal)

    # Wing floating roof
    _curved_roof("WingFloatRoof", wing_w + 0.2, wing_d + 0.2, 0.30,
                 (WX, -0.8, BZ + wing_h + 0.20), m['roof'],
                 overhang=0.20, curve_up=0.10)

    # === Entrance glass atrium ===
    bmesh_box("Atrium", (0.8, 1.6, 2.0), (tower_w / 2 + 0.40, 0, BZ + 1.0), glass)
    bmesh_box("AtriumFrame", (0.82, 1.62, 0.03), (tower_w / 2 + 0.40, 0, BZ + 2.02), metal)

    # === LED accent strips ===
    bmesh_box("LED_Base", (5.0, 0.04, 0.04), (0, -2.3, BZ + 0.02), m['gold'])
    bmesh_box("LED_Tower1", (tower_w + 0.04, 0.04, 0.04), (0, -tower_d / 2 - 0.01, BZ + tower_h - 0.10), m['gold'])
    bmesh_box("LED_Tower2", (0.04, tower_d + 0.04, 0.04), (tower_w / 2 + 0.01, 0, BZ + tower_h - 0.10), m['gold'])

    # === Solar/tech panels on wing roof ===
    wing_roof_z = BZ + wing_h + 0.25
    for i in range(3):
        bmesh_box(f"Solar_{i}", (0.6, 0.4, 0.03),
                  (WX - 0.6 + i * 0.7, -0.8, wing_roof_z + 0.10), glass)
        bmesh_box(f"SolarF_{i}", (0.62, 0.42, 0.02),
                  (WX - 0.6 + i * 0.7, -0.8, wing_roof_z + 0.07), metal)

    # === Communication spire ===
    spire_z = BZ + tower_h + float_tiers[2][3] + 0.15
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=1.5,
                                        location=(0, 0, spire_z + 0.75))
    bpy.context.active_object.data.materials.append(metal)
    for sz in [0.3, 0.6, 0.9, 1.2]:
        bmesh_box(f"SpireBar_{sz:.1f}", (0.5, 0.02, 0.02), (0, 0, spire_z + sz), metal)

    # Steps (minimal, floating)
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.20, 1.8, 0.04),
                  (tower_w / 2 + 0.80 + i * 0.22, 0, BZ - 0.02 - i * 0.02), metal)


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


def build_town_center_japanese(materials, age='medieval'):
    """Build a Japanese Town Center with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
