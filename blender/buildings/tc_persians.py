"""
Persians Nation Town Center — Persian/Iranian architecture per age.

3x3 tile building, ground plane 5.5x5.5.

Stone:         Neolithic Zagros mountain settlement — rectangular mud-brick rooms,
               flat roof, small courtyard, grain storage pit
Bronze:        Elamite ziggurat complex — stepped pyramid (3 tiers), ramp entrance,
               bull guardians at gate, brick walls
Iron:          Median fortress — thick stone walls, columned hall (early apadana),
               corner towers, stone lion guardians
Classical:     Achaemenid Persepolis — grand apadana hall with tall fluted columns
               and bull capitals, Gate of Nations with lamassu, wide staircase
               with relief panels, stone platform
Medieval:      Sassanid/Islamic palace — iwan (tall arched portal), muqarnas
               (honeycomb vault), dome with geometric tile patterns, wind tower
               (badgir), courtyard with pool
Gunpowder:     Safavid Isfahan style — tall Ali Qapu palace, grand iwan entrance,
               blue tile mosaic dome, slender minarets, reflecting pool
Enlightenment: Qajar palace — mirrored hall, ornate tile work, windcatcher towers,
               Persian garden layout with central axis
Industrial:    Pahlavi-era modernized — Western-influenced with Persian motifs,
               grand columned entrance, Persepolis-inspired reliefs, wide steps
Modern:        Iranian modernist — geometric concrete with traditional muqarnas
               patterns, large arch entrance, integration of wind towers
Digital:       Futuristic Persian — glass iwan portal, holographic geometric
               patterns, floating garden platforms, energy dome with muqarnas
               fractal structure
"""

import bpy
import bmesh
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# -- helpers ---------------------------------------------------------

def _dome(name, radius, height, segments, origin, material, smooth=True):
    """
    Half-sphere dome built from latitude/longitude strips.
    Gives the characteristic Persian bulbous dome shape.
    """
    ox, oy, oz = origin
    verts = []
    faces = []
    rings = segments // 2

    # apex
    verts.append((ox, oy, oz + height))

    for r in range(1, rings + 1):
        phi = (math.pi / 2) * (r / rings)
        z = oz + height * math.cos(phi)
        ring_r = radius * math.sin(phi)
        for s in range(segments):
            theta = (2 * math.pi * s) / segments
            verts.append((ox + ring_r * math.cos(theta),
                          oy + ring_r * math.sin(theta), z))

    # faces from apex to first ring
    for s in range(segments):
        s_next = (s + 1) % segments
        faces.append((0, 1 + s, 1 + s_next))

    # faces between rings
    for r in range(rings - 1):
        base = 1 + r * segments
        for s in range(segments):
            s_next = (s + 1) % segments
            a = base + s
            b = base + s_next
            c = base + segments + s_next
            d = base + segments + s
            faces.append((a, b, c, d))

    # bottom face
    last_ring_start = 1 + (rings - 1) * segments
    bottom = list(range(last_ring_start, last_ring_start + segments))
    faces.append(tuple(reversed(bottom)))

    obj = mesh_from_pydata(name, verts, faces, material)
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def _iwan(name, width, depth, height, origin, wall_mat, arch_mat):
    """
    Persian iwan — a tall rectangular portal with a pointed arch opening.
    Creates the outer frame and the arch void filled with arch_mat.
    """
    ox, oy, oz = origin
    hw = width / 2
    hd = depth / 2

    # Side walls
    wall_t = 0.12
    bmesh_box(f"{name}_WallL", (wall_t, depth, height),
              (ox - hw + wall_t / 2, oy, oz + height / 2), wall_mat)
    bmesh_box(f"{name}_WallR", (wall_t, depth, height),
              (ox + hw - wall_t / 2, oy, oz + height / 2), wall_mat)
    # Top beam
    bmesh_box(f"{name}_Top", (width, depth, 0.10),
              (ox, oy, oz + height - 0.05), wall_mat)
    # Back wall (full)
    bmesh_box(f"{name}_Back", (width, wall_t, height),
              (ox, oy - hd + wall_t / 2, oz + height / 2), wall_mat)

    # Pointed arch face (simplified as triangular gable over rectangular opening)
    arch_w = width - wall_t * 2
    arch_h = height * 0.7
    peak_h = height * 0.9
    # Arch surround (decorative frame on the front face)
    front_y = oy + hd
    av = [
        (ox - arch_w / 2, front_y, oz),
        (ox + arch_w / 2, front_y, oz),
        (ox + arch_w / 2, front_y, oz + arch_h),
        (ox, front_y, oz + peak_h),
        (ox - arch_w / 2, front_y, oz + arch_h),
    ]
    af = [(0, 1, 2, 4), (2, 3, 4)]
    obj = mesh_from_pydata(f"{name}_Arch", av, af, arch_mat)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def _minaret(name, radius, height, origin, material, cap_mat, segments=12):
    """Slender Persian minaret with a small dome cap."""
    ox, oy, oz = origin
    # Shaft
    bmesh_prism(f"{name}_Shaft", radius, height, segments, (ox, oy, oz), material)
    # Balcony ring
    bmesh_prism(f"{name}_Balcony", radius * 1.5, 0.08, segments,
                (ox, oy, oz + height * 0.85), material)
    # Small dome cap
    _dome(f"{name}_Cap", radius * 1.3, radius * 1.8, segments,
          (ox, oy, oz + height), cap_mat)


def _windcatcher(name, width, height, origin, material, vent_mat):
    """
    Badgir (wind tower) — a tall rectangular tower with vent openings at top.
    """
    ox, oy, oz = origin
    hw = width / 2
    # Tower body
    bmesh_box(f"{name}_Body", (width, width, height),
              (ox, oy, oz + height / 2), material)
    # Vent openings on four sides (upper portion)
    vent_h = height * 0.3
    vent_z = oz + height - vent_h / 2 - 0.05
    for dx, dy, rot in [(hw + 0.01, 0, 0), (-hw - 0.01, 0, 0),
                         (0, hw + 0.01, 1), (0, -hw - 0.01, 1)]:
        if rot == 0:
            bmesh_box(f"{name}_Vent_{dx:.2f}", (0.04, width * 0.6, vent_h),
                      (ox + dx, oy + dy, vent_z), vent_mat)
        else:
            bmesh_box(f"{name}_Vent_{dy:.2f}", (width * 0.6, 0.04, vent_h),
                      (ox + dx, oy + dy, vent_z), vent_mat)
    # Cap
    pyramid_roof(f"{name}_Cap", width + 0.06, width + 0.06, 0.20,
                 overhang=0.04, origin=(ox, oy, oz + height), material=material)


def _muqarnas_band(name, cx, cy, z, width, depth, tiers, material):
    """
    Simplified muqarnas (honeycomb/stalactite corbelling) as a band of
    stepped, overlapping small boxes creating a cascading profile.
    """
    hw = width / 2
    for t in range(tiers):
        n_cells = 4 + t * 2
        cell_w = width / n_cells
        offset_z = z - t * 0.04
        inset = t * 0.02
        for i in range(n_cells):
            cx_i = cx - hw + inset + cell_w / 2 + i * (width - 2 * inset) / n_cells
            bmesh_box(f"{name}_T{t}_C{i}", (cell_w * 0.85, depth, 0.035),
                      (cx_i, cy, offset_z), material)


def _fluted_column(name, radius, height, origin, material, segments=12, flutes=8):
    """Fluted column reminiscent of Persepolis pillars."""
    ox, oy, oz = origin
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius, depth=height,
                                        location=(ox, oy, oz + height / 2))
    col = bpy.context.active_object
    col.name = name
    col.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    # Column base
    bmesh_prism(f"{name}_Base", radius * 1.3, 0.08, segments, (ox, oy, oz), material)
    # Column capital
    bmesh_box(f"{name}_Cap", (radius * 2.2, radius * 2.2, 0.10),
              (ox, oy, oz + height + 0.05), material)
    return col


# ============================================================
# STONE AGE -- Neolithic Zagros mountain settlement
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Mud-brick perimeter wall (low, irregular) ===
    wall_r = 2.2
    n_segs = 28
    wall_h = 0.75
    for i in range(n_segs):
        a0 = (2 * math.pi * i) / n_segs
        a1 = (2 * math.pi * (i + 1)) / n_segs
        # Gate gap at front
        if 13 <= i <= 15:
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
        ht = 0.14
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
        mesh = bpy.data.meshes.new(f"Wall_{i}")
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(f"Wall_{i}", mesh)
        bpy.context.collection.objects.link(obj)
        obj.location = (cx, cy, Z + wall_h / 2)
        obj.rotation_euler = (0, 0, angle)
        obj.data.materials.append(m['stone_dark'])

    # Gate posts
    for dy in [-0.35, 0.35]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=1.0,
                                            location=(2.2, dy, Z + 0.50))
        bpy.context.active_object.name = f"GatePost_{dy:.2f}"
        bpy.context.active_object.data.materials.append(m['wood'])
    bmesh_box("GateLintel", (0.10, 0.80, 0.08), (2.2, 0, Z + 1.0), m['wood_dark'])

    # === Main rectangular room (largest, central) ===
    bmesh_box("MainRoom", (2.0, 1.6, 1.2), (0, 0, Z + 0.60), m['stone'])
    # Flat mud-brick roof
    bmesh_box("MainRoof", (2.2, 1.8, 0.10), (0, 0, Z + 1.25), m['stone_dark'])
    # Door
    bmesh_box("MainDoor", (0.06, 0.45, 0.80), (1.01, 0, Z + 0.40), m['door'])

    # Roof support beams (wooden, visible)
    for by in [-0.5, 0, 0.5]:
        bmesh_box(f"Beam_{by:.1f}", (2.1, 0.08, 0.06), (0, by, Z + 1.15), m['wood'])

    # === Secondary room (attached, smaller) ===
    bmesh_box("Room2", (1.2, 1.0, 0.95), (-1.3, -0.5, Z + 0.475), m['stone'])
    bmesh_box("Room2Roof", (1.35, 1.15, 0.08), (-1.3, -0.5, Z + 1.00), m['stone_dark'])
    bmesh_box("Room2Door", (0.06, 0.35, 0.65), (-0.69, -0.5, Z + 0.33), m['door'])

    # === Small courtyard (open area with packed earth) ===
    bmesh_box("Courtyard", (1.5, 1.5, 0.04), (0.8, -1.0, Z + 0.02), m['stone_light'])

    # === Grain storage pit ===
    bmesh_prism("GrainPit", 0.50, 0.08, 12, (-0.5, 1.2, Z + 0.04), m['stone_dark'])
    bmesh_prism("GrainRim", 0.55, 0.10, 12, (-0.5, 1.2, Z), m['wood_dark'])
    # Woven cover
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.45, depth=0.04,
                                        location=(-0.5, 1.2, Z + 0.14))
    bpy.context.active_object.name = "GrainCover"
    bpy.context.active_object.data.materials.append(m['roof'])

    # === Central fire pit ===
    bmesh_prism("FirePit", 0.30, 0.08, 10, (0.8, -1.0, Z + 0.04), m['stone_dark'])
    for i in range(6):
        a = (2 * math.pi * i) / 6
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05,
                                              location=(0.8 + 0.25 * math.cos(a),
                                                        -1.0 + 0.25 * math.sin(a), Z + 0.05))
        st = bpy.context.active_object
        st.name = f"FStone_{i}"
        st.data.materials.append(m['stone'])

    # === Storage room (rectangular, small) ===
    bmesh_box("StoreRoom", (0.80, 0.65, 0.80), (1.5, 1.0, Z + 0.40), m['stone'])
    bmesh_box("StoreRoof", (0.90, 0.75, 0.06), (1.5, 1.0, Z + 0.83), m['stone_dark'])

    # === Clay water jars ===
    for i, (px, py) in enumerate([(-1.6, 0.6), (0.3, 1.5)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(px, py, Z + 0.10))
        jar = bpy.context.active_object
        jar.name = f"Jar_{i}"
        jar.scale = (1, 1, 1.3)
        jar.data.materials.append(m['roof_edge'])

    # === Drying rack ===
    for dx in [-0.25, 0.25]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=1.0,
                                            location=(-1.8 + dx, -1.5, Z + 0.50))
        bpy.context.active_object.data.materials.append(m['wood'])
    bmesh_box("DryBar", (0.04, 0.55, 0.04), (-1.8, -1.5, Z + 1.0), m['wood'])


# ============================================================
# BRONZE AGE -- Elamite ziggurat complex
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Outer brick enclosure wall ===
    ow_hw = 2.4
    ow_h = 1.0
    bmesh_box("OuterWallF", (0.15, ow_hw * 2, ow_h), (ow_hw, 0, Z + ow_h / 2), m['stone'], bevel=0.02)
    bmesh_box("OuterWallB", (0.15, ow_hw * 2, ow_h), (-ow_hw, 0, Z + ow_h / 2), m['stone'], bevel=0.02)
    bmesh_box("OuterWallR", (ow_hw * 2, 0.15, ow_h), (0, -ow_hw, Z + ow_h / 2), m['stone'], bevel=0.02)
    bmesh_box("OuterWallL", (ow_hw * 2, 0.15, ow_h), (0, ow_hw, Z + ow_h / 2), m['stone'], bevel=0.02)

    # Wall crenellations
    for i in range(10):
        cx = -ow_hw + 0.30 + i * (ow_hw * 2 - 0.60) / 9
        bmesh_box(f"CrenF_{i}", (0.18, 0.18, 0.18),
                  (ow_hw, cx, Z + ow_h + 0.09), m['stone_dark'])
        bmesh_box(f"CrenB_{i}", (0.18, 0.18, 0.18),
                  (-ow_hw, cx, Z + ow_h + 0.09), m['stone_dark'])

    # === Gateway with bull guardians ===
    gate_x = ow_hw + 0.01
    bmesh_box("GatePillarL", (0.15, 0.15, 1.4), (gate_x, -0.40, Z + 0.70), m['stone_dark'])
    bmesh_box("GatePillarR", (0.15, 0.15, 1.4), (gate_x, 0.40, Z + 0.70), m['stone_dark'])
    bmesh_box("GateLintel", (0.20, 1.00, 0.12), (gate_x, 0, Z + 1.40), m['stone_dark'])
    bmesh_box("GateDoor", (0.06, 0.60, 1.0), (gate_x + 0.08, 0, Z + 0.50), m['door'])

    # Bull guardian figures (simplified as blocky shapes)
    for dy, lbl in [(-0.60, "L"), (0.60, "R")]:
        # Body
        bmesh_box(f"Bull_{lbl}_Body", (0.35, 0.18, 0.30),
                  (gate_x + 0.20, dy, Z + 0.15), m['stone_dark'])
        # Head
        bmesh_box(f"Bull_{lbl}_Head", (0.12, 0.12, 0.18),
                  (gate_x + 0.35, dy, Z + 0.35), m['stone_dark'])
        # Horns
        for hdy in [-0.08, 0.08]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.15,
                                                location=(gate_x + 0.38, dy + hdy, Z + 0.48))
            horn = bpy.context.active_object
            horn.name = f"BullHorn_{lbl}_{hdy:.2f}"
            horn.rotation_euler = (0, math.radians(30), 0)
            horn.data.materials.append(m['gold'])

    # === Three-tiered ziggurat (central) ===
    tiers = [
        (3.2, 3.2, 1.2),   # tier 1 base
        (2.4, 2.4, 1.0),   # tier 2
        (1.6, 1.6, 0.8),   # tier 3 top
    ]
    cur_z = Z + 0.02
    for t, (tw, td, th) in enumerate(tiers):
        bmesh_box(f"Zig_{t}", (tw, td, th), (0, 0, cur_z + th / 2), m['stone'])
        # Stepped edges (brick pattern)
        bmesh_box(f"ZigTrim_{t}", (tw + 0.04, td + 0.04, 0.06),
                  (0, 0, cur_z + th), m['stone_dark'])
        # Decorative niches on walls
        if t < 2:
            n_niches = 4 - t
            for ni in range(n_niches):
                nx = -tw / 2 + 0.30 + ni * (tw - 0.60) / max(1, n_niches - 1)
                bmesh_box(f"Niche_{t}_{ni}", (0.15, 0.06, 0.30),
                          (nx, td / 2 + 0.01, cur_z + th * 0.5), m['stone_dark'])
        cur_z += th

    # Small temple at ziggurat top
    bmesh_box("Temple", (0.90, 0.70, 0.60), (0, 0, cur_z + 0.30), m['stone_dark'])
    bmesh_box("TempleRoof", (1.0, 0.80, 0.06), (0, 0, cur_z + 0.63), m['stone_trim'])
    bmesh_box("TempleDoor", (0.05, 0.25, 0.45), (0.46, 0, cur_z + 0.23), m['door'])

    # === Ramp from ground to first tier ===
    ramp_verts = [
        (1.6, -0.40, Z), (2.5, -0.40, Z),
        (2.5, 0.40, Z), (1.6, 0.40, Z),
        (1.6, -0.35, Z + 1.2), (1.75, -0.35, Z + 1.2),
        (1.75, 0.35, Z + 1.2), (1.6, 0.35, Z + 1.2),
    ]
    ramp_faces = [(0, 1, 5, 4), (2, 3, 7, 6), (0, 3, 7, 4),
                  (1, 2, 6, 5), (4, 5, 6, 7), (0, 1, 2, 3)]
    mesh_from_pydata("Ramp", ramp_verts, ramp_faces, m['stone_dark'])

    # === Auxiliary building ===
    bmesh_box("AuxBuilding", (1.0, 0.80, 0.80), (-1.8, -1.5, Z + 0.40), m['stone'])
    pyramid_roof("AuxRoof", 1.0, 0.80, 0.30, overhang=0.08,
                 origin=(-1.8, -1.5, Z + 0.80), material=m['stone_dark'])

    # Flagpole
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=1.5,
                                        location=(0, 0, cur_z + 0.63 + 0.75))
    bpy.context.active_object.name = "Flagpole"
    bpy.context.active_object.data.materials.append(m['wood'])
    bv = [(0.04, 0, cur_z + 1.80), (0.45, 0.03, cur_z + 1.75),
          (0.45, 0.02, cur_z + 2.00), (0.04, 0, cur_z + 1.98)]
    mesh_from_pydata("Flag", bv, [(0, 1, 2, 3)], m['banner'])


# ============================================================
# IRON AGE -- Median fortress
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Thick stone fortress walls ===
    fw_hw = 2.3
    fw_h = 1.5
    wall_t = 0.25
    bmesh_box("FortWallF", (wall_t, fw_hw * 2, fw_h), (fw_hw, 0, Z + fw_h / 2), m['stone_dark'], bevel=0.03)
    bmesh_box("FortWallB", (wall_t, fw_hw * 2, fw_h), (-fw_hw, 0, Z + fw_h / 2), m['stone_dark'], bevel=0.03)
    bmesh_box("FortWallR", (fw_hw * 2, wall_t, fw_h), (0, -fw_hw, Z + fw_h / 2), m['stone_dark'], bevel=0.03)
    bmesh_box("FortWallL", (fw_hw * 2, wall_t, fw_h), (0, fw_hw, Z + fw_h / 2), m['stone_dark'], bevel=0.03)

    # Crenellations on all walls
    for wall_idx, (wx, wy, along_x) in enumerate([
        (fw_hw, 0, False), (-fw_hw, 0, False),
        (0, -fw_hw, True), (0, fw_hw, True),
    ]):
        for ci in range(9):
            offset = -fw_hw + 0.30 + ci * (fw_hw * 2 - 0.60) / 8
            if along_x:
                bmesh_box(f"Cren_{wall_idx}_{ci}", (0.20, 0.28, 0.20),
                          (offset, wy, Z + fw_h + 0.10), m['stone_dark'])
            else:
                bmesh_box(f"Cren_{wall_idx}_{ci}", (0.28, 0.20, 0.20),
                          (wx, offset, Z + fw_h + 0.10), m['stone_dark'])

    # === Corner towers (4) ===
    for tx, ty, lbl in [(fw_hw, fw_hw, "FL"), (fw_hw, -fw_hw, "FR"),
                        (-fw_hw, fw_hw, "BL"), (-fw_hw, -fw_hw, "BR")]:
        tower_h = 2.2
        bmesh_prism(f"Tower_{lbl}", 0.45, tower_h, 8, (tx, ty, Z), m['stone_dark'])
        # Tower cap (cone roof)
        bmesh_cone(f"TowerCap_{lbl}", 0.55, 0.45, 8, (tx, ty, Z + tower_h), m['roof'])
        # Arrow slits
        bmesh_box(f"Slit_{lbl}", (0.04, 0.08, 0.30),
                  (tx + 0.42 * (1 if tx > 0 else -1), ty, Z + tower_h * 0.6), m['stone'])

    # === Gatehouse ===
    gate_x = fw_hw + 0.01
    bmesh_box("GateFrame", (0.30, 1.0, 2.0), (gate_x, 0, Z + 1.0), m['stone_dark'])
    bmesh_box("GateOpen", (0.32, 0.65, 1.4), (gate_x, 0, Z + 0.70), m['door'])
    pyramid_roof("GateRoof", 0.50, 1.2, 0.30, overhang=0.08,
                 origin=(gate_x, 0, Z + 2.0), material=m['roof'])

    BZ = Z + 0.10

    # === Columned hall (early apadana) ===
    hall_w, hall_d = 2.6, 2.0
    hall_h = 2.5
    # Stone platform
    bmesh_box("HallPlat", (hall_w + 0.3, hall_d + 0.3, 0.15), (0, 0, BZ + 0.075), m['stone'], bevel=0.04)

    fl_z = BZ + 0.15
    # Columns (3x3 grid)
    col_xs = [-0.80, 0, 0.80]
    col_ys = [-0.65, 0, 0.65]
    for px in col_xs:
        for py in col_ys:
            bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.09, depth=hall_h,
                                                location=(px, py, fl_z + hall_h / 2))
            col = bpy.context.active_object
            col.name = f"ApadCol_{px:.1f}_{py:.1f}"
            col.data.materials.append(m['stone_light'])
            bpy.ops.object.shade_smooth()
            # Simple capital
            bmesh_box(f"ApadCap_{px:.1f}_{py:.1f}", (0.22, 0.22, 0.08),
                      (px, py, fl_z + hall_h + 0.04), m['stone_light'])

    # Walls (partial, between columns on back and sides)
    bmesh_box("HallWallB", (0.08, hall_d, hall_h * 0.6),
              (-hall_w / 2 + 0.04, 0, fl_z + hall_h * 0.3), m['stone'])
    bmesh_box("HallWallR", (hall_w, 0.08, hall_h * 0.6),
              (0, -hall_d / 2 + 0.04, fl_z + hall_h * 0.3), m['stone'])
    bmesh_box("HallWallL", (hall_w, 0.08, hall_h * 0.6),
              (0, hall_d / 2 - 0.04, fl_z + hall_h * 0.3), m['stone'])

    # Flat timber roof with stone trim
    bmesh_box("HallRoof", (hall_w + 0.2, hall_d + 0.2, 0.12),
              (0, 0, fl_z + hall_h + 0.06), m['wood_dark'])
    bmesh_box("HallRoofTrim", (hall_w + 0.25, hall_d + 0.25, 0.04),
              (0, 0, fl_z + hall_h + 0.14), m['stone_trim'])

    # Door
    bmesh_box("HallDoor", (0.06, 0.50, 1.20), (hall_w / 2 + 0.01, 0, fl_z + 0.60), m['door'])

    # === Stone lion guardians at hall entrance ===
    for dy, lbl in [(-0.55, "L"), (0.55, "R")]:
        # Lion body (blocky, stylized)
        bmesh_box(f"Lion_{lbl}_Body", (0.40, 0.18, 0.25),
                  (hall_w / 2 + 0.30, dy, fl_z + 0.125), m['stone_light'])
        # Lion head
        bmesh_box(f"Lion_{lbl}_Head", (0.15, 0.14, 0.18),
                  (hall_w / 2 + 0.50, dy, fl_z + 0.30), m['stone_light'])
        # Mane
        bmesh_prism(f"Lion_{lbl}_Mane", 0.10, 0.06, 8,
                    (hall_w / 2 + 0.45, dy, fl_z + 0.30), m['gold'])

    # Steps to hall
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.16, 1.4, 0.05),
                  (hall_w / 2 + 0.50 + i * 0.18, 0, fl_z - 0.03 - i * 0.04), m['stone'])


# ============================================================
# CLASSICAL AGE -- Achaemenid Persepolis
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Grand stone platform (multi-tier, Persepolis terrace) ===
    bmesh_box("Plat1", (5.2, 4.8, 0.20), (0, 0, Z + 0.10), m['stone_dark'], bevel=0.05)
    bmesh_box("Plat2", (4.8, 4.4, 0.15), (0, 0, Z + 0.275), m['stone'], bevel=0.04)

    BZ = Z + 0.35

    # === Wide staircase with relief panels ===
    stair_x = 2.4
    n_steps = 8
    for i in range(n_steps):
        bmesh_box(f"Step_{i}", (0.18, 2.0, 0.06),
                  (stair_x + i * 0.20, 0, BZ - 0.04 - i * 0.04), m['stone'])

    # Relief panels on staircase sides (simplified as textured slabs)
    for dy, lbl in [(-1.05, "L"), (1.05, "R")]:
        # Sloped relief panel
        panel_verts = [
            (stair_x, dy - 0.04, BZ - 0.04),
            (stair_x + n_steps * 0.20, dy - 0.04, BZ - 0.04 - n_steps * 0.04),
            (stair_x + n_steps * 0.20, dy + 0.04, BZ - 0.04 - n_steps * 0.04),
            (stair_x, dy + 0.04, BZ - 0.04),
            (stair_x, dy - 0.04, BZ + 0.40),
            (stair_x + n_steps * 0.20, dy - 0.04, BZ + 0.40 - n_steps * 0.04),
            (stair_x + n_steps * 0.20, dy + 0.04, BZ + 0.40 - n_steps * 0.04),
            (stair_x, dy + 0.04, BZ + 0.40),
        ]
        pf = [(0, 1, 5, 4), (2, 3, 7, 6), (0, 3, 7, 4), (1, 2, 6, 5),
              (4, 5, 6, 7), (0, 1, 2, 3)]
        mesh_from_pydata(f"Relief_{lbl}", panel_verts, pf, m['stone_trim'])

    # === Apadana hall (grand columned audience hall) ===
    hall_w, hall_d = 3.6, 3.0
    hall_h = 3.5

    # Tall fluted columns (4x4 grid)
    col_xs = [-1.2, -0.4, 0.4, 1.2]
    col_ys = [-1.0, -0.33, 0.33, 1.0]
    for px in col_xs:
        for py in col_ys:
            _fluted_column(f"ApadCol_{px:.1f}_{py:.1f}", 0.09, hall_h,
                           (px, py, BZ), m['stone_light'])

    # Bull capitals on corner columns (double bull heads)
    for px in [col_xs[0], col_xs[-1]]:
        for py in [col_ys[0], col_ys[-1]]:
            cap_z = BZ + hall_h + 0.10
            # Two bull heads facing outward
            for ddx, ddy in [(0.10, 0), (-0.10, 0)]:
                bmesh_box(f"BullCap_{px:.1f}_{py:.1f}_{ddx:.2f}",
                          (0.10, 0.08, 0.14), (px + ddx, py + ddy, cap_z + 0.07), m['stone_light'])
                # Horns
                for hd in [-0.05, 0.05]:
                    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=0.10,
                                                        location=(px + ddx + 0.06, py + ddy + hd, cap_z + 0.18))
                    horn = bpy.context.active_object
                    horn.name = f"BullHorn_{px:.1f}_{py:.1f}_{ddx:.2f}_{hd:.2f}"
                    horn.rotation_euler = (0, math.radians(25), 0)
                    horn.data.materials.append(m['gold'])

    # Roof beams (massive wooden)
    bmesh_box("RoofBeams", (hall_w + 0.3, hall_d + 0.3, 0.15),
              (0, 0, BZ + hall_h + 0.10 + 0.075), m['wood_dark'])
    bmesh_box("RoofSlab", (hall_w + 0.4, hall_d + 0.4, 0.08),
              (0, 0, BZ + hall_h + 0.32), m['stone_dark'])

    # Partial walls (back and sides, with windows)
    bmesh_box("WallB", (0.10, hall_d, hall_h * 0.5),
              (-hall_w / 2, 0, BZ + hall_h * 0.25), m['stone'])
    for py_s in [-1, 1]:
        py = py_s * hall_d / 2
        bmesh_box(f"WallS_{py_s}", (hall_w * 0.5, 0.10, hall_h * 0.5),
                  (-hall_w / 4, py, BZ + hall_h * 0.25), m['stone'])

    # === Gate of All Nations (smaller structure to the side) ===
    GX, GY = 1.8, -1.5
    gate_w, gate_d = 1.2, 0.80
    gate_h = 2.2
    bmesh_box("GateNations", (gate_w, gate_d, gate_h),
              (GX, GY, BZ + gate_h / 2), m['stone'])
    bmesh_box("GateNDoor", (0.06, 0.50, 1.40), (GX + gate_w / 2 + 0.01, GY, BZ + 0.70), m['door'])
    # Lamassu figures (winged bulls at gate entrance)
    for ddy, lbl in [(-0.40, "L"), (0.40, "R")]:
        # Winged bull body
        bmesh_box(f"Lamassu_{lbl}", (0.30, 0.15, 0.35),
                  (GX + gate_w / 2 + 0.20, GY + ddy, BZ + 0.175), m['stone_light'])
        # Head
        bmesh_box(f"LamHead_{lbl}", (0.12, 0.10, 0.15),
                  (GX + gate_w / 2 + 0.35, GY + ddy, BZ + 0.40), m['stone_light'])
        # Wing (simple triangular)
        wv = [
            (GX + gate_w / 2 + 0.12, GY + ddy, BZ + 0.30),
            (GX + gate_w / 2 + 0.20, GY + ddy + 0.08 * (1 if ddy > 0 else -1), BZ + 0.55),
            (GX + gate_w / 2 + 0.30, GY + ddy, BZ + 0.30),
        ]
        mesh_from_pydata(f"LamWing_{lbl}", wv, [(0, 1, 2)], m['gold'])
    # Gate roof
    bmesh_box("GateNRoof", (gate_w + 0.15, gate_d + 0.15, 0.10),
              (GX, GY, BZ + gate_h + 0.05), m['stone_dark'])

    # === Fire altar ===
    AX, AY = -1.8, 1.2
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.12, depth=0.60,
                                        location=(AX, AY, BZ + 0.30))
    bpy.context.active_object.name = "Altar"
    bpy.context.active_object.data.materials.append(m['stone'])
    bmesh_cone("AltarFlame", 0.08, 0.25, 8, (AX, AY, BZ + 0.60), m['gold'])

    # Gold ornament at roof peak
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0, 0, BZ + hall_h + 0.40))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()


# ============================================================
# MEDIEVAL AGE -- Sassanid/Islamic palace
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Stone platform ===
    bmesh_box("Plat", (5.0, 4.8, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.12

    # === Main palace body ===
    main_w, main_d = 3.2, 2.8
    main_h = 2.5
    bmesh_box("PalaceBody", (main_w, main_d, main_h),
              (0, 0, BZ + main_h / 2), m['stone'])

    # Decorative tile trim bands
    for bz_i in range(3):
        lz = BZ + 0.60 + bz_i * 0.80
        bmesh_box(f"TileBand_{bz_i}", (main_w + 0.04, main_d + 0.04, 0.06),
                  (0, 0, lz), m['stone_trim'])

    # === Grand iwan (tall arched portal, front face) ===
    iwan_w = 1.6
    iwan_h = main_h + 0.5
    _iwan("MainIwan", iwan_w, 0.60, iwan_h, (0, main_d / 2, BZ), m['stone_dark'], m['gold'])

    # Iwan decorative spandrels (geometric patterns - simplified as panels)
    for dx in [-0.55, 0.55]:
        bmesh_box(f"Spandrel_{dx:.2f}", (0.35, 0.04, 0.35),
                  (dx, main_d / 2 + 0.02, BZ + iwan_h - 0.50), m['stone_trim'])

    # === Central dome ===
    dome_r = 1.0
    dome_h = 1.2
    dome_base = BZ + main_h
    # Drum (octagonal base for dome)
    bmesh_prism("DomeDrum", dome_r + 0.05, 0.30, 8, (0, 0, dome_base), m['stone'])
    # Dome
    _dome("MainDome", dome_r, dome_h, 16, (0, 0, dome_base + 0.30), m['roof'])

    # Dome finial (gold crescent)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06,
                                          location=(0, 0, dome_base + 0.30 + dome_h + 0.06))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # === Muqarnas cornice under dome ===
    _muqarnas_band("DomeMuq", 0, 0, dome_base + 0.05, 2.2, 0.10, 3, m['stone_trim'])

    # === Courtyard with pool ===
    CX, CY = 0, -1.6
    bmesh_box("Courtyard", (2.0, 1.4, 0.04), (CX, CY, BZ + 0.02), m['stone_light'])
    # Reflecting pool
    bmesh_box("Pool", (1.2, 0.60, 0.08), (CX, CY, BZ + 0.04), m['window'])
    # Pool border
    bmesh_box("PoolBorderF", (1.30, 0.06, 0.10), (CX, CY - 0.33, BZ + 0.05), m['stone'])
    bmesh_box("PoolBorderB", (1.30, 0.06, 0.10), (CX, CY + 0.33, BZ + 0.05), m['stone'])
    bmesh_box("PoolBorderL", (0.06, 0.60, 0.10), (CX - 0.65, CY, BZ + 0.05), m['stone'])
    bmesh_box("PoolBorderR", (0.06, 0.60, 0.10), (CX + 0.65, CY, BZ + 0.05), m['stone'])

    # === Wind tower (badgir) ===
    _windcatcher("Badgir", 0.55, 2.8, (-1.2, 0.8, BZ), m['stone'], m['wood_dark'])

    # === Side arched gallery (arcade) ===
    for i in range(4):
        ax = -1.2 + i * 0.70
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.06, depth=1.5,
                                            location=(ax, -main_d / 2 - 0.30, BZ + 0.75))
        col = bpy.context.active_object
        col.name = f"ArcadeCol_{i}"
        col.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()

    # Arcade beam
    bmesh_box("ArcadeBeam", (3.0, 0.10, 0.10),
              (-0.05, -main_d / 2 - 0.30, BZ + 1.55), m['stone'])
    # Arcade roof
    bmesh_box("ArcadeRoof", (3.0, 0.50, 0.06),
              (-0.05, -main_d / 2 - 0.30, BZ + 1.65), m['stone_dark'])

    # === Windows with geometric screens ===
    for y in [-0.7, 0.0, 0.7]:
        bmesh_box(f"Win_{y:.1f}", (0.06, 0.28, 0.45),
                  (main_w / 2 + 0.01, y, BZ + 1.30), m['window'])
        bmesh_box(f"WinFrame_{y:.1f}", (0.07, 0.30, 0.04),
                  (main_w / 2 + 0.02, y, BZ + 1.55), m['win_frame'])
        # Geometric screen pattern (simple cross)
        bmesh_box(f"WinScreenH_{y:.1f}", (0.02, 0.24, 0.02),
                  (main_w / 2 + 0.04, y, BZ + 1.30), m['wood'])
        bmesh_box(f"WinScreenV_{y:.1f}", (0.02, 0.02, 0.40),
                  (main_w / 2 + 0.04, y, BZ + 1.30), m['wood'])

    # Door
    bmesh_box("Door", (0.08, 0.55, 1.40), (0, main_d / 2 + 0.31, BZ + 0.70), m['door'])

    # Steps
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.16, 1.6, 0.05),
                  (0, main_d / 2 + 0.55 + i * 0.18, BZ - 0.03 - i * 0.03), m['stone'])

    # Gold accents on iwan
    bmesh_box("IwanGold", (iwan_w + 0.10, 0.06, 0.06),
              (0, main_d / 2 + 0.02, BZ + iwan_h - 0.03), m['gold'])


# ============================================================
# GUNPOWDER AGE -- Safavid Isfahan style
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation platform ===
    bmesh_box("Plat", (5.2, 5.0, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.15

    # === Main palace body (Ali Qapu inspired, tall) ===
    main_w, main_d = 2.8, 2.4
    main_h = 4.0
    bmesh_box("Palace", (main_w, main_d, main_h),
              (0, 0, BZ + main_h / 2), m['stone'])

    # Decorative tile bands (blue/gold geometric patterns)
    for bz_i in range(5):
        lz = BZ + 0.50 + bz_i * 0.70
        bmesh_box(f"TileBand_{bz_i}", (main_w + 0.04, main_d + 0.04, 0.05),
                  (0, 0, lz), m['stone_trim'])

    # Upper gallery (open columned balcony, Ali Qapu signature)
    gallery_z = BZ + main_h * 0.65
    gallery_h = main_h * 0.35
    for i in range(6):
        gx = -main_w / 2 + 0.25 + i * (main_w - 0.50) / 5
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.05, depth=gallery_h,
                                            location=(gx, main_d / 2 + 0.01, gallery_z + gallery_h / 2))
        col = bpy.context.active_object
        col.name = f"GalCol_{i}"
        col.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()

    # Gallery floor
    bmesh_box("GalFloor", (main_w + 0.30, 0.40, 0.06),
              (0, main_d / 2 + 0.20, gallery_z), m['wood'])
    # Gallery roof/overhang
    bmesh_box("GalRoof", (main_w + 0.40, 0.50, 0.06),
              (0, main_d / 2 + 0.20, gallery_z + gallery_h + 0.03), m['wood_dark'])

    # Windows (tall arched, Safavid style)
    for y in [-0.6, 0.0, 0.6]:
        for wz_off in [0.8, 2.0]:
            bmesh_box(f"Win_{y:.1f}_{wz_off:.1f}", (0.06, 0.25, 0.50),
                      (main_w / 2 + 0.01, y, BZ + wz_off), m['window'])
            bmesh_box(f"WinFr_{y:.1f}_{wz_off:.1f}", (0.07, 0.27, 0.04),
                      (main_w / 2 + 0.02, y, BZ + wz_off + 0.27), m['win_frame'])

    # === Grand iwan entrance ===
    iwan_w = 1.8
    iwan_h = 3.5
    _iwan("GrandIwan", iwan_w, 0.70, iwan_h, (0, main_d / 2, BZ), m['stone_dark'], m['gold'])

    # Muqarnas in the iwan vault
    _muqarnas_band("IwanMuq", 0, main_d / 2 + 0.15, BZ + iwan_h - 0.10, iwan_w - 0.30, 0.12, 4, m['stone_trim'])

    # === Blue tile mosaic dome ===
    dome_r = 1.1
    dome_h = 1.5
    dome_base = BZ + main_h
    # Drum
    bmesh_prism("DomeDrum", dome_r + 0.08, 0.40, 12, (0, 0, dome_base), m['stone_trim'])
    # Dome (using roof material for blue tiles)
    _dome("BlueDome", dome_r, dome_h, 20, (0, 0, dome_base + 0.40), m['roof'])
    # Dome geometric tile pattern lines (meridians)
    for i in range(8):
        a = (2 * math.pi * i) / 8
        for seg in range(5):
            phi = (math.pi / 2) * (seg / 5)
            sz = dome_base + 0.40 + dome_h * math.cos(phi)
            sr = dome_r * math.sin(phi) * 1.01
            bpy.ops.mesh.primitive_cylinder_add(vertices=4, radius=0.015, depth=0.04,
                                                location=(sr * math.cos(a), sr * math.sin(a), sz))
            bpy.context.active_object.data.materials.append(m['gold'])

    # Finial
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06,
                                          location=(0, 0, dome_base + 0.40 + dome_h + 0.06))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # === Slender minarets (2) ===
    for dy, lbl in [(-1.5, "L"), (1.5, "R")]:
        _minaret(f"Min_{lbl}", 0.12, 4.5, (main_w / 2 - 0.10, dy, BZ), m['stone_trim'], m['roof'])

    # === Reflecting pool ===
    PX, PY = 0, 2.0
    bmesh_box("ReflPool", (2.0, 0.80, 0.08), (PX, PY, BZ + 0.04), m['window'])
    bmesh_box("PoolBorderF", (2.10, 0.06, 0.10), (PX, PY - 0.43, BZ + 0.05), m['stone_light'])
    bmesh_box("PoolBorderB", (2.10, 0.06, 0.10), (PX, PY + 0.43, BZ + 0.05), m['stone_light'])
    bmesh_box("PoolBorderL", (0.06, 0.80, 0.10), (PX - 1.05, PY, BZ + 0.05), m['stone_light'])
    bmesh_box("PoolBorderR", (0.06, 0.80, 0.10), (PX + 1.05, PY, BZ + 0.05), m['stone_light'])

    # Door
    bmesh_box("Door", (0.08, 0.60, 1.60), (0, main_d / 2 + 0.71, BZ + 0.80), m['door'])

    # Steps
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.16, 2.0, 0.05),
                  (0, main_d / 2 + 0.85 + i * 0.18, BZ - 0.03 - i * 0.04), m['stone'])


# ============================================================
# ENLIGHTENMENT AGE -- Qajar palace
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation ===
    bmesh_box("Plat", (5.2, 5.0, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.12

    # === Persian garden layout (chahar bagh: four-quarter garden) ===
    # Central axis path
    bmesh_box("AxisPathY", (0.35, 5.0, 0.04), (0, 0, BZ + 0.02), m['stone_light'])
    bmesh_box("AxisPathX", (5.0, 0.35, 0.04), (0, 0, BZ + 0.02), m['stone_light'])

    # Garden beds in the four quarters
    for qx, qy in [(1.2, 1.2), (1.2, -1.2), (-1.2, 1.2), (-1.2, -1.2)]:
        bmesh_box(f"Garden_{qx:.1f}_{qy:.1f}", (1.5, 1.5, 0.03),
                  (qx, qy, BZ + 0.015), m['ground'])
        # Small tree (trunk + sphere canopy)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=0.5,
                                            location=(qx, qy, BZ + 0.28))
        bpy.context.active_object.data.materials.append(m['wood'])
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(qx, qy, BZ + 0.60))
        bpy.context.active_object.data.materials.append(m['ground'])

    # Central fountain/pool (at axis intersection)
    bmesh_prism("CenterPool", 0.45, 0.06, 8, (0, 0, BZ + 0.03), m['window'])
    bmesh_prism("PoolRim", 0.50, 0.10, 8, (0, 0, BZ), m['stone'])

    # === Main palace (mirrored hall, ornate) ===
    pal_w, pal_d = 3.0, 2.0
    pal_h = 3.0
    PX = 0
    # Palace body
    bmesh_box("Palace", (pal_w, pal_d, pal_h),
              (PX, 0, BZ + 0.04 + pal_h / 2), m['stone'])

    # Ornate tile work (horizontal bands)
    for bz_i in range(4):
        lz = BZ + 0.04 + 0.50 + bz_i * 0.65
        bmesh_box(f"TileBand_{bz_i}", (pal_w + 0.04, pal_d + 0.04, 0.04),
                  (PX, 0, lz), m['stone_trim'])

    # Mirrored hall windows (tall, ornate, reflective)
    for y in [-0.6, 0.0, 0.6]:
        # Tall window
        bmesh_box(f"MirrorWin_{y:.1f}", (0.05, 0.30, 0.80),
                  (PX + pal_w / 2 + 0.01, y, BZ + 0.04 + pal_h * 0.45), m['window'])
        # Ornate frame
        bmesh_box(f"MirrorFrame_{y:.1f}", (0.06, 0.34, 0.04),
                  (PX + pal_w / 2 + 0.02, y, BZ + 0.04 + pal_h * 0.45 + 0.42), m['gold'])
        bmesh_box(f"MirrorFrameB_{y:.1f}", (0.06, 0.34, 0.04),
                  (PX + pal_w / 2 + 0.02, y, BZ + 0.04 + pal_h * 0.45 - 0.42), m['gold'])

    # Side windows
    for x in [-0.8, 0, 0.8]:
        bmesh_box(f"SideWin_{x:.1f}", (0.25, 0.05, 0.55),
                  (PX + x, pal_d / 2 + 0.01, BZ + 0.04 + pal_h * 0.45), m['window'])

    # Door (front, ornate)
    bmesh_box("Door", (0.08, 0.60, 1.50),
              (PX + pal_w / 2 + 0.01, 0, BZ + 0.04 + 0.75), m['door'])
    # Door frame with gold
    bmesh_box("DoorFrameT", (0.10, 0.70, 0.06),
              (PX + pal_w / 2 + 0.02, 0, BZ + 0.04 + 1.53), m['gold'])

    # === Roof with decorative parapet ===
    roof_z = BZ + 0.04 + pal_h
    bmesh_box("PalRoof", (pal_w + 0.20, pal_d + 0.20, 0.10),
              (PX, 0, roof_z + 0.05), m['stone_dark'])
    # Parapet with decorative crenellations
    for i in range(8):
        cx = PX - pal_w / 2 + 0.25 + i * (pal_w - 0.50) / 7
        bmesh_box(f"Parapet_{i}", (0.12, pal_d + 0.22, 0.15),
                  (cx, 0, roof_z + 0.175), m['stone_trim'])

    # Small dome accent
    _dome("PalDome", 0.55, 0.65, 12, (PX, 0, roof_z + 0.10), m['roof'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04,
                                          location=(PX, 0, roof_z + 0.10 + 0.65 + 0.04))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # === Windcatcher towers (two, flanking) ===
    for dx, lbl in [(-1.2, "L"), (1.2, "R")]:
        _windcatcher(f"Badgir_{lbl}", 0.45, 3.5, (PX + dx, -0.7, BZ), m['stone'], m['wood_dark'])

    # === Steps ===
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.16, 1.8, 0.05),
                  (PX + pal_w / 2 + 0.30 + i * 0.18, 0, BZ - 0.02 - i * 0.03), m['stone'])


# ============================================================
# INDUSTRIAL AGE -- Pahlavi-era modernized
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation ===
    bmesh_box("Found", (5.2, 4.8, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.15

    # === Wide stone steps (grand entrance, Persepolis-inspired) ===
    for i in range(8):
        step_w = 2.8 - i * 0.05
        bmesh_box(f"Step_{i}", (0.18, step_w, 0.06),
                  (2.2 + i * 0.20, 0, BZ - 0.04 - i * 0.04), m['stone'])

    # === Main building (Western style with Persian motifs) ===
    main_w, main_d = 3.6, 2.8
    main_h = 3.5
    # Stone base (lower third, heavier)
    bmesh_box("Base", (main_w, main_d, main_h * 0.35),
              (0, 0, BZ + main_h * 0.175), m['stone'], bevel=0.02)
    # Upper section (lighter plaster)
    bmesh_box("Upper", (main_w, main_d, main_h * 0.65),
              (0, 0, BZ + main_h * 0.35 + main_h * 0.325), m['stone_light'])

    # Cornice trim between base and upper
    bmesh_box("Cornice", (main_w + 0.08, main_d + 0.08, 0.08),
              (0, 0, BZ + main_h * 0.35), m['stone_trim'])

    # Persepolis-inspired relief band (decorative strip with figures)
    bmesh_box("ReliefBand", (main_w + 0.02, main_d + 0.02, 0.15),
              (0, 0, BZ + main_h * 0.35 + 0.20), m['stone_trim'])

    # === Grand columned entrance (Persepolis-inspired columns) ===
    col_h = main_h * 0.8
    for dy in [-0.80, -0.27, 0.27, 0.80]:
        _fluted_column(f"EntCol_{dy:.2f}", 0.10, col_h,
                       (main_w / 2 + 0.40, dy, BZ), m['stone_light'])

    # Entablature above columns
    bmesh_box("Entab", (0.50, 2.0, 0.15),
              (main_w / 2 + 0.40, 0, BZ + col_h + 0.075), m['stone'])

    # Pediment (triangular, classical influence)
    ped_verts = [
        (main_w / 2 + 0.15, -1.0, BZ + col_h + 0.15),
        (main_w / 2 + 0.15, 1.0, BZ + col_h + 0.15),
        (main_w / 2 + 0.15, 0, BZ + col_h + 0.70),
        (main_w / 2 + 0.65, -1.0, BZ + col_h + 0.15),
        (main_w / 2 + 0.65, 1.0, BZ + col_h + 0.15),
        (main_w / 2 + 0.65, 0, BZ + col_h + 0.70),
    ]
    ped_faces = [(0, 1, 2), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (0, 2, 5, 3)]
    mesh_from_pydata("Pediment", ped_verts, ped_faces, m['stone'])

    # Windows (Western-style with Persian proportions)
    for y in [-0.9, -0.3, 0.3, 0.9]:
        # Lower row
        bmesh_box(f"LowWin_{y:.1f}", (0.06, 0.22, 0.50),
                  (main_w / 2 + 0.01, y, BZ + 0.55), m['window'])
        bmesh_box(f"LowWinH_{y:.1f}", (0.07, 0.26, 0.04),
                  (main_w / 2 + 0.02, y, BZ + 0.82), m['stone_trim'])
        # Upper row
        bmesh_box(f"UpWin_{y:.1f}", (0.06, 0.22, 0.60),
                  (main_w / 2 + 0.01, y, BZ + main_h * 0.35 + 0.65), m['window'])
        bmesh_box(f"UpWinH_{y:.1f}", (0.07, 0.26, 0.04),
                  (main_w / 2 + 0.02, y, BZ + main_h * 0.35 + 0.98), m['stone_trim'])

    # Side windows
    for x in [-1.0, -0.2, 0.6]:
        bmesh_box(f"SideWin_{x:.1f}", (0.22, 0.06, 0.50),
                  (x, -main_d / 2 - 0.01, BZ + main_h * 0.35 + 0.65), m['window'])

    # Door
    bmesh_box("Door", (0.08, 0.70, 1.80),
              (main_w / 2 + 0.01, 0, BZ + 0.90), m['door'])
    bmesh_box("DoorFrame", (0.10, 0.80, 0.08),
              (main_w / 2 + 0.02, 0, BZ + 1.83), m['stone_trim'])

    # === Flat roof with parapet ===
    roof_z = BZ + main_h
    bmesh_box("Roof", (main_w + 0.15, main_d + 0.15, 0.10),
              (0, 0, roof_z + 0.05), m['stone_dark'])
    # Parapet
    for py_s in [-1, 1]:
        py = py_s * (main_d / 2 + 0.10)
        bmesh_box(f"Parapet_{py_s}", (main_w + 0.15, 0.08, 0.30),
                  (0, py, roof_z + 0.25), m['stone'])

    # Persepolis-style winged disk ornament above entrance
    orn_z = BZ + main_h - 0.20
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.15, depth=0.04,
                                        location=(main_w / 2 + 0.02, 0, orn_z))
    disk = bpy.context.active_object
    disk.name = "WingedDisk"
    disk.rotation_euler = (0, math.radians(90), 0)
    disk.data.materials.append(m['gold'])
    # Wings (flat triangles)
    for dy_s in [-1, 1]:
        wv = [
            (main_w / 2 + 0.02, 0, orn_z),
            (main_w / 2 + 0.02, dy_s * 0.55, orn_z + 0.08),
            (main_w / 2 + 0.02, dy_s * 0.45, orn_z - 0.08),
        ]
        mesh_from_pydata(f"Wing_{dy_s}", wv, [(0, 1, 2)], m['gold'])

    # === Side wing (lower) ===
    wing_w, wing_d, wing_h = 1.6, 1.8, 2.2
    WX = -1.2
    bmesh_box("Wing", (wing_w, wing_d, wing_h), (WX, -0.5, BZ + wing_h / 2), m['stone_light'])
    bmesh_box("WingRoof", (wing_w + 0.10, wing_d + 0.10, 0.08),
              (WX, -0.5, BZ + wing_h + 0.04), m['stone_dark'])

    # Iron fence
    for i in range(10):
        fy = -1.4 + i * 0.28
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.50,
                                            location=(main_w / 2 + 1.0, fy, BZ + 0.25))
        bpy.context.active_object.data.materials.append(m['iron'])


# ============================================================
# MODERN AGE -- Iranian modernist
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Foundation ===
    bmesh_box("Found", (5.2, 4.8, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    BZ = Z + 0.08

    # === Main building (geometric concrete with muqarnas patterns) ===
    main_w, main_d = 3.0, 2.6
    main_h = 4.0
    bmesh_box("Main", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone'])

    # Concrete horizontal bands (modernist rhythm)
    for bz_i in range(5):
        lz = BZ + 0.60 + bz_i * 0.70
        bmesh_box(f"Band_{bz_i}", (main_w + 0.06, main_d + 0.06, 0.05),
                  (0, 0, lz), m['stone_trim'])

    # === Large arch entrance (modern Persian arch) ===
    arch_w = 1.4
    arch_h = 3.2
    arch_y = main_d / 2
    # Arch frame (parabolic shape, simplified as pointed arch)
    arch_verts = [
        (-arch_w / 2, arch_y + 0.01, BZ),
        (arch_w / 2, arch_y + 0.01, BZ),
        (arch_w / 2, arch_y + 0.01, BZ + arch_h * 0.7),
        (0, arch_y + 0.01, BZ + arch_h),
        (-arch_w / 2, arch_y + 0.01, BZ + arch_h * 0.7),
    ]
    arch_faces = [(0, 1, 2, 4), (2, 3, 4)]
    obj = mesh_from_pydata("ModernArch", arch_verts, arch_faces, m['stone_dark'])
    for p in obj.data.polygons:
        p.use_smooth = True

    # Arch inset (recessed, different material)
    for dx in [-arch_w / 2 - 0.06, arch_w / 2 + 0.06]:
        bmesh_box(f"ArchPillar_{dx:.2f}", (0.12, 0.20, arch_h),
                  (dx, arch_y + 0.10, BZ + arch_h / 2), m['stone_dark'])

    # Glass infill in arch
    bmesh_box("ArchGlass", (arch_w - 0.20, 0.04, arch_h * 0.6),
              (0, arch_y + 0.05, BZ + arch_h * 0.3), glass)

    # === Muqarnas-patterned facade panels (geometric concrete screen) ===
    # Simplified as a grid of small recessed boxes on the front facade
    for row in range(4):
        for col in range(6):
            px = -main_w / 2 + 0.35 + col * (main_w - 0.70) / 5
            pz = BZ + 0.80 + row * 0.70
            # Skip where the arch is
            if abs(px) < arch_w / 2 + 0.10 and pz < BZ + arch_h + 0.20:
                continue
            bmesh_box(f"MuqPanel_{row}_{col}", (0.18, 0.04, 0.18),
                      (px, main_d / 2 + 0.02, pz), m['stone_dark'])

    # === Glass curtain wall on side ===
    bmesh_box("SideGlass", (0.05, main_d - 0.5, main_h - 0.4),
              (main_w / 2 + 0.01, -0.25, BZ + main_h / 2 + 0.1), glass)
    # Mullions
    for y in [-0.8, -0.3, 0.2]:
        bmesh_box(f"Mullion_{y:.1f}", (0.04, 0.03, main_h - 0.5),
                  (main_w / 2 + 0.03, y, BZ + main_h / 2 + 0.1), metal)

    # === Integrated wind tower (modern interpretation) ===
    WT_X, WT_Y = -1.0, -0.8
    wt_h = 4.5
    bmesh_box("WindTower", (0.60, 0.60, wt_h),
              (WT_X, WT_Y, BZ + wt_h / 2), m['stone'])
    # Modern wind scoops (angled panels at top)
    for rot_i in range(4):
        a = math.radians(45 + rot_i * 90)
        sx = WT_X + 0.35 * math.cos(a)
        sy = WT_Y + 0.35 * math.sin(a)
        bmesh_box(f"WindScoop_{rot_i}", (0.30, 0.04, 0.60),
                  (sx, sy, BZ + wt_h - 0.30), m['stone_dark'])
    # Wind tower cap
    bmesh_box("WTCap", (0.70, 0.70, 0.06), (WT_X, WT_Y, BZ + wt_h + 0.03), metal)

    # === Flat roof with overhang ===
    roof_z = BZ + main_h
    bmesh_box("RoofSlab", (main_w + 0.40, main_d + 0.40, 0.12),
              (0, 0, roof_z + 0.06), m['stone_dark'])

    # === Lower wing ===
    wing_w, wing_d, wing_h = 2.2, 1.4, 2.5
    WX = 1.0
    bmesh_box("Wing", (wing_w, wing_d, wing_h),
              (WX, -0.6, BZ + wing_h / 2), m['stone'])
    bmesh_box("WingGlass", (0.05, wing_d - 0.3, wing_h - 0.4),
              (WX + wing_w / 2 + 0.01, -0.6, BZ + wing_h / 2 + 0.1), glass)
    bmesh_box("WingRoof", (wing_w + 0.20, wing_d + 0.20, 0.08),
              (WX, -0.6, BZ + wing_h + 0.04), m['stone_dark'])

    # Connection
    bmesh_box("Connect", (0.6, 0.8, 2.0), (main_w / 2 + 0.10, -0.6, BZ + 1.0), glass)

    # Door
    bmesh_box("Door", (0.08, 0.80, 2.0),
              (0, main_d / 2 + 0.01, BZ + 1.0), glass)
    bmesh_box("DoorFrame", (0.10, 0.90, 0.06), (0, main_d / 2 + 0.02, BZ + 2.03), metal)

    # Steps
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.16, 2.0, 0.05),
                  (0, main_d / 2 + 0.40 + i * 0.18, BZ - 0.02 - i * 0.02), m['stone'])

    # Concrete planter
    bmesh_box("Planter", (1.0, 0.40, 0.25), (2.0, 1.5, BZ + 0.125), m['stone'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.20, location=(2.0, 1.5, BZ + 0.45))
    bpy.context.active_object.data.materials.append(m['ground'])


# ============================================================
# DIGITAL AGE -- Futuristic Persian
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Foundation (minimal, tech platform) ===
    bmesh_box("Found", (5.0, 4.6, 0.06), (0, 0, Z + 0.03), m['stone_dark'])

    BZ = Z + 0.06

    # === Glass iwan portal (main entrance, futuristic) ===
    iwan_w = 2.0
    iwan_h = 4.5
    iwan_y = 2.0
    # Glass arch frame
    iv = [
        (-iwan_w / 2, iwan_y, BZ),
        (iwan_w / 2, iwan_y, BZ),
        (iwan_w / 2, iwan_y, BZ + iwan_h * 0.75),
        (0, iwan_y, BZ + iwan_h),
        (-iwan_w / 2, iwan_y, BZ + iwan_h * 0.75),
    ]
    ivf = [(0, 1, 2, 4), (2, 3, 4)]
    obj = mesh_from_pydata("GlassIwan", iv, ivf, glass)
    for p in obj.data.polygons:
        p.use_smooth = True

    # Iwan frame (metal edges)
    for dx in [-iwan_w / 2 - 0.04, iwan_w / 2 + 0.04]:
        bmesh_box(f"IwanFrame_{dx:.2f}", (0.08, 0.08, iwan_h),
                  (dx, iwan_y, BZ + iwan_h / 2), metal)
    # Top frame
    bmesh_box("IwanFrameTop", (iwan_w + 0.20, 0.08, 0.06),
              (0, iwan_y, BZ + iwan_h + 0.03), metal)

    # === Main structure (glass and metal tower) ===
    tower_w, tower_d = 2.4, 2.0
    tower_h = 5.0
    bmesh_box("Tower", (tower_w, tower_d, tower_h),
              (0, 0, BZ + tower_h / 2), glass)

    # Steel frame grid
    for tz in range(6):
        hz = BZ + 0.7 + tz * 0.80
        bmesh_box(f"TFrame_{tz}", (tower_w + 0.02, tower_d + 0.02, 0.04),
                  (0, 0, hz), metal)
    for y in [-0.6, 0, 0.6]:
        bmesh_box(f"TVert_{y:.1f}", (0.03, 0.03, tower_h),
                  (tower_w / 2 + 0.01, y, BZ + tower_h / 2), metal)
        bmesh_box(f"TVert2_{y:.1f}", (0.03, 0.03, tower_h),
                  (-tower_w / 2 - 0.01, y, BZ + tower_h / 2), metal)

    # === Holographic geometric patterns (gold wireframe panels) ===
    # Floating geometric panels around the tower
    for i in range(6):
        a = (2 * math.pi * i) / 6
        px = 1.8 * math.cos(a)
        py = 1.8 * math.sin(a)
        pz = BZ + 1.5 + i * 0.4
        # Small diamond-shaped panel
        dv = [
            (px, py, pz),
            (px + 0.20, py + 0.05, pz + 0.20),
            (px, py + 0.10, pz + 0.40),
            (px - 0.20, py + 0.05, pz + 0.20),
        ]
        panel = mesh_from_pydata(f"HoloPanel_{i}", dv, [(0, 1, 2, 3)], m['gold'])
        panel.data.materials[0].use_backface_culling = False

    # === Energy dome with muqarnas fractal structure ===
    dome_base = BZ + tower_h
    dome_r = 1.5
    dome_h = 1.8
    # Main dome (glass/energy)
    _dome("EnergyDome", dome_r, dome_h, 20, (0, 0, dome_base), glass)

    # Muqarnas fractal structure inside dome (cascading tiers of small prisms)
    for tier in range(4):
        n_cells = 6 + tier * 3
        t_r = dome_r * (0.3 + tier * 0.15)
        t_z = dome_base + dome_h * 0.3 - tier * 0.12
        for ci in range(n_cells):
            ca = (2 * math.pi * ci) / n_cells
            cx = t_r * math.cos(ca)
            cy = t_r * math.sin(ca)
            bmesh_prism(f"FracMuq_{tier}_{ci}", 0.06, 0.08, 6,
                        (cx, cy, t_z), m['gold'])

    # Dome finial (energy spire)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=1.0,
                                        location=(0, 0, dome_base + dome_h + 0.50))
    bpy.context.active_object.data.materials.append(m['gold'])
    # Spire tip sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08,
                                          location=(0, 0, dome_base + dome_h + 1.05))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # === Floating garden platforms ===
    garden_positions = [(-1.5, 1.2, BZ + 1.0), (1.5, -1.2, BZ + 1.5),
                        (-1.8, -1.0, BZ + 2.0), (1.8, 1.0, BZ + 2.5)]
    for gi, (gx, gy, gz) in enumerate(garden_positions):
        # Platform
        bmesh_box(f"GardenPlat_{gi}", (0.80, 0.80, 0.06), (gx, gy, gz), metal)
        # Garden surface (green)
        bmesh_box(f"GardenGreen_{gi}", (0.70, 0.70, 0.03), (gx, gy, gz + 0.045), m['ground'])
        # Thin support pillar
        pillar_h = gz - BZ
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=pillar_h,
                                            location=(gx, gy, BZ + pillar_h / 2))
        bpy.context.active_object.name = f"GardenPillar_{gi}"
        bpy.context.active_object.data.materials.append(metal)
        # Small tree on platform
        if gi < 3:
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.35,
                                                location=(gx, gy, gz + 0.22))
            bpy.context.active_object.data.materials.append(m['wood'])
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(gx, gy, gz + 0.48))
            bpy.context.active_object.data.materials.append(m['ground'])

    # === LED accent strips ===
    bmesh_box("LED_Base", (5.0, 0.04, 0.04), (0, -2.3, BZ + 0.02), m['gold'])
    bmesh_box("LED_Tower1", (tower_w + 0.04, 0.04, 0.04),
              (0, -tower_d / 2 - 0.01, BZ + tower_h - 0.10), m['gold'])
    bmesh_box("LED_Tower2", (0.04, tower_d + 0.04, 0.04),
              (tower_w / 2 + 0.01, 0, BZ + tower_h - 0.10), m['gold'])

    # === Lower connected wing (glass) ===
    wing_w, wing_d, wing_h = 2.0, 1.2, 2.8
    WX = 0.8
    WY = -0.8
    bmesh_box("Wing", (wing_w, wing_d, wing_h), (WX, WY, BZ + wing_h / 2), glass)
    for wz in range(3):
        hz = BZ + 0.8 + wz * 0.9
        bmesh_box(f"WingFrame_{wz}", (wing_w + 0.02, wing_d + 0.02, 0.03),
                  (WX, WY, hz), metal)
    bmesh_box("WingRoof", (wing_w + 0.15, wing_d + 0.15, 0.06),
              (WX, WY, BZ + wing_h + 0.03), metal)

    # === Entrance glass bridge ===
    bmesh_box("Bridge", (0.60, 1.5, 0.06), (0, tower_d / 2 + 0.75, BZ + 0.40), glass)
    bmesh_box("BridgeRail_L", (0.03, 1.5, 0.25), (-0.30, tower_d / 2 + 0.75, BZ + 0.55), metal)
    bmesh_box("BridgeRail_R", (0.03, 1.5, 0.25), (0.30, tower_d / 2 + 0.75, BZ + 0.55), metal)

    # Steps
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.60, 0.16, 0.04),
                  (0, iwan_y + 0.20 + i * 0.18, BZ - 0.02 - i * 0.02), metal)

    # Solar/tech panels on wing roof
    for i in range(3):
        bmesh_box(f"Solar_{i}", (0.55, 0.35, 0.03),
                  (WX - 0.5 + i * 0.6, WY, BZ + wing_h + 0.09), glass)
        bmesh_box(f"SolarF_{i}", (0.57, 0.37, 0.02),
                  (WX - 0.5 + i * 0.6, WY, BZ + wing_h + 0.065), metal)


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


def build_town_center_persians(materials, age='medieval'):
    """Build a Persian Town Center with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
