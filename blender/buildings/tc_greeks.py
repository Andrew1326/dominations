"""
Greeks nation Town Center — Greek/Hellenic architecture per age.

Stone:         Cycladic whitewashed hut — simple cubic white stone building, flat roof, small doorway, stone yard wall
Bronze:        Minoan palace fragment — red columns tapering downward (wider at top), light stone walls, bull horns on roof
Iron:          Mycenaean megaron — Lion Gate entrance, cyclopean stone walls, corbelled gallery, rectangular hall with hearth
Classical:     Grand Greek temple (Parthenon style) — peristyle of Doric columns, triangular pediment, stepped crepidoma, naos hall
Medieval:      Byzantine church — Greek cross plan, central dome on pendentives, round arched windows, bell tower, mosaic patterns
Gunpowder:     Venetian-Greek fortress — star-shaped walls, Venetian lion carvings, domed chapel, clock tower with arches
Enlightenment: Neoclassical Greek revival — tall Ionic columns, triangular pediment, symmetrical wings, acroterion ornaments
Industrial:    Greek neoclassical civic building — marble facade, tall arched windows, balustrade roofline, iron railings
Modern:        Greek modernist — white concrete, geometric forms, open terrace, blue accents (Cycladic influence), flat roofs
Digital:       Futuristic Greek — floating marble columns, holographic Parthenon outline, glass cella, energy beams between pillars
"""

import bpy
import bmesh
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# ----------------------------------------------------------------
# helpers — distinctly Greek architectural elements
# ----------------------------------------------------------------
def _doric_column(name, origin, radius, height, mat, segments=12, fluting=True):
    """Doric column: slight entasis (widening at 1/3), no base, simple capital.
    Creates shaft + abacus (flat cap block)."""
    ox, oy, oz = origin
    # Shaft
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius, depth=height,
                                        location=(ox, oy, oz + height / 2))
    shaft = bpy.context.active_object
    shaft.name = f"{name}_shaft"
    shaft.data.materials.append(mat)
    for p in shaft.data.polygons:
        p.use_smooth = True
    # Abacus (square cap)
    cap_size = radius * 2.4
    bmesh_box(f"{name}_cap", (cap_size, cap_size, radius * 0.4),
              (ox, oy, oz + height + radius * 0.2), mat)
    return shaft


def _ionic_column(name, origin, radius, height, mat, segments=14):
    """Ionic column: slender shaft with base torus and scroll capital."""
    ox, oy, oz = origin
    # Attic base (wider disc)
    bmesh_prism(f"{name}_base", radius * 1.4, radius * 0.3, segments,
                (ox, oy, oz), mat)
    # Shaft
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius, depth=height,
                                        location=(ox, oy, oz + radius * 0.3 + height / 2))
    shaft = bpy.context.active_object
    shaft.name = f"{name}_shaft"
    shaft.data.materials.append(mat)
    for p in shaft.data.polygons:
        p.use_smooth = True
    cap_z = oz + radius * 0.3 + height
    # Capital block
    bmesh_box(f"{name}_cap", (radius * 2.6, radius * 2.6, radius * 0.3),
              (ox, oy, cap_z + radius * 0.15), mat)
    # Volute scrolls (small cylinders on sides)
    for dy in [-radius * 1.2, radius * 1.2]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius * 0.35, depth=radius * 0.15,
                                            location=(ox, oy + dy, cap_z + radius * 0.15))
        vol = bpy.context.active_object
        vol.name = f"{name}_volute_{dy:.2f}"
        vol.data.materials.append(mat)
        for p in vol.data.polygons:
            p.use_smooth = True
    return shaft


def _pediment(name, width, height, depth, origin, mat):
    """Triangular pediment (gable front) for a Greek temple."""
    ox, oy, oz = origin
    hw = width / 2
    hd = depth / 2
    verts = [
        # front triangle
        (ox - hw, oy - hd, oz),
        (ox + hw, oy - hd, oz),
        (ox, oy - hd, oz + height),
        # back triangle
        (ox - hw, oy + hd, oz),
        (ox + hw, oy + hd, oz),
        (ox, oy + hd, oz + height),
    ]
    faces = [
        (0, 1, 2),        # front face
        (3, 5, 4),        # back face
        (0, 3, 5, 2),     # left slope
        (1, 2, 5, 4),     # right slope
        (0, 1, 4, 3),     # bottom
    ]
    return mesh_from_pydata(name, verts, faces, mat)


def _meander_strip(name, length, origin, mat, axis='x'):
    """Decorative meander (Greek key) strip — approximated as thin relief boxes
    in a zigzag pattern along the given axis."""
    ox, oy, oz = origin
    step = 0.12
    n = int(length / step)
    for i in range(n):
        t = -length / 2 + i * step
        h = 0.04 if i % 2 == 0 else 0.06
        if axis == 'x':
            bmesh_box(f"{name}_{i}", (step * 0.8, 0.04, h),
                      (ox + t + step / 2, oy, oz + h / 2), mat)
        else:
            bmesh_box(f"{name}_{i}", (0.04, step * 0.8, h),
                      (ox, oy + t + step / 2, oz + h / 2), mat)


def _acroterion(name, origin, height, mat):
    """Acroterion ornament — palmette-shaped finial on roof apex/corners."""
    ox, oy, oz = origin
    # Central palmette leaf (tall thin wedge)
    verts = [
        (ox - 0.03, oy, oz),
        (ox + 0.03, oy, oz),
        (ox + 0.02, oy, oz + height),
        (ox - 0.02, oy, oz + height),
        (ox, oy, oz + height + 0.06),  # tip
    ]
    faces = [
        (0, 1, 2, 3),
        (3, 2, 4),
    ]
    mesh_from_pydata(f"{name}_ctr", verts, faces, mat)
    # Side leaves (angled)
    for sx in [-1, 1]:
        lv = [
            (ox + sx * 0.03, oy, oz),
            (ox + sx * 0.06, oy, oz),
            (ox + sx * 0.08, oy, oz + height * 0.7),
            (ox + sx * 0.04, oy, oz + height * 0.8),
        ]
        mesh_from_pydata(f"{name}_{sx}", lv, [(0, 1, 2, 3)], mat)


def _dome(name, origin, radius, height, mat, segments=16, rings=8):
    """Half-sphere dome via mesh_from_pydata."""
    ox, oy, oz = origin
    verts = []
    faces = []
    # Generate vertices ring by ring from base to apex
    for r_idx in range(rings + 1):
        phi = (math.pi / 2) * (r_idx / rings)  # 0 at base to pi/2 at top
        ring_r = radius * math.cos(phi)
        ring_z = oz + height * math.sin(phi)
        for s_idx in range(segments):
            theta = (2 * math.pi * s_idx) / segments
            verts.append((ox + ring_r * math.cos(theta),
                          oy + ring_r * math.sin(theta),
                          ring_z))
    # Apex vertex
    apex_idx = len(verts)
    verts.append((ox, oy, oz + height))
    # Quad faces for rings
    for r_idx in range(rings - 1):
        for s_idx in range(segments):
            s_next = (s_idx + 1) % segments
            a = r_idx * segments + s_idx
            b = r_idx * segments + s_next
            c = (r_idx + 1) * segments + s_next
            d = (r_idx + 1) * segments + s_idx
            faces.append((a, b, c, d))
    # Top cap triangles
    last_ring = (rings - 1) * segments
    for s_idx in range(segments):
        s_next = (s_idx + 1) % segments
        faces.append((last_ring + s_idx, last_ring + s_next, apex_idx))
    # Base ring face (optional, close the bottom)
    base_ring = list(range(segments))
    faces.append(tuple(reversed(base_ring)))
    obj = mesh_from_pydata(name, verts, faces, mat)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def _bull_horns(name, origin, spread, height, mat):
    """Minoan sacred bull horns (horns of consecration)."""
    ox, oy, oz = origin
    verts = [
        # left horn
        (ox - spread, oy - 0.03, oz + height),
        (ox - spread, oy + 0.03, oz + height),
        (ox - spread * 0.3, oy + 0.04, oz),
        (ox - spread * 0.3, oy - 0.04, oz),
        # right horn
        (ox + spread, oy - 0.03, oz + height),
        (ox + spread, oy + 0.03, oz + height),
        (ox + spread * 0.3, oy + 0.04, oz),
        (ox + spread * 0.3, oy - 0.04, oz),
        # base connector
        (ox - spread * 0.3, oy - 0.04, oz),
        (ox - spread * 0.3, oy + 0.04, oz),
        (ox + spread * 0.3, oy + 0.04, oz),
        (ox + spread * 0.3, oy - 0.04, oz),
        # dip center
        (ox, oy - 0.03, oz + height * 0.25),
        (ox, oy + 0.03, oz + height * 0.25),
    ]
    faces = [
        (3, 2, 1, 0),      # left horn front
        (7, 6, 5, 4),      # right horn front  (note: reuses indices of right horn)
        (8, 9, 10, 11),    # base bottom
        (3, 12, 13, 2),    # left inner slope
        (11, 10, 13, 12),  # right inner slope
    ]
    obj = mesh_from_pydata(name, verts, faces, mat)
    return obj


# ============================================================
# STONE AGE -- Cycladic whitewashed hut
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Stone yard wall (low perimeter) ===
    wall_r = 2.2
    wall_h = 0.45
    wt = 0.14
    # Front wall (with gap for entrance)
    bmesh_box("YardWallF_L", (0.80, wt, wall_h), (1.50, -0.90, Z + wall_h / 2), m['stone'])
    bmesh_box("YardWallF_R", (0.80, wt, wall_h), (1.50, 0.90, Z + wall_h / 2), m['stone'])
    bmesh_box("YardWallR", (wt, 3.8, wall_h), (2.10, 0, Z + wall_h / 2), m['stone'])
    bmesh_box("YardWallL", (wt, 3.8, wall_h), (-2.10, 0, Z + wall_h / 2), m['stone'])
    bmesh_box("YardWallB", (4.2, wt, wall_h), (0, 1.90, Z + wall_h / 2), m['stone'])
    bmesh_box("YardWallFr", (4.2, wt, wall_h), (0, -1.90, Z + wall_h / 2), m['stone'])

    BZ = Z + 0.06

    # === Main whitewashed cubic hut ===
    hut_w, hut_d, hut_h = 1.8, 1.6, 1.4
    bmesh_box("MainHut", (hut_w, hut_d, hut_h), (0, 0, BZ + hut_h / 2), m['stone_light'], bevel=0.03)

    # Flat roof slab (slightly overhanging)
    bmesh_box("Roof", (hut_w + 0.15, hut_d + 0.15, 0.10), (0, 0, BZ + hut_h + 0.05), m['stone_light'])

    # Small doorway (dark opening)
    bmesh_box("Door", (0.08, 0.50, 0.85), (0, -hut_d / 2 - 0.01, BZ + 0.425), m['door'])
    # Door lintel stone
    bmesh_box("DoorLintel", (0.10, 0.60, 0.08), (0, -hut_d / 2 - 0.02, BZ + 0.90), m['stone'])

    # Small window opening
    bmesh_box("Window", (0.06, 0.25, 0.25), (0.50, -hut_d / 2 - 0.01, BZ + 1.0), m['window'])

    # === Secondary smaller hut (storage) ===
    bmesh_box("StorageHut", (1.0, 0.9, 1.0), (-1.4, -0.8, BZ + 0.50), m['stone_light'], bevel=0.02)
    bmesh_box("StorageRoof", (1.1, 1.0, 0.08), (-1.4, -0.8, BZ + 1.04), m['stone_light'])

    # === Stone paved yard area ===
    bmesh_box("YardPaving", (3.0, 2.5, 0.04), (0, 0, Z + 0.04), m['stone_dark'])

    # === Clay pot cluster (storage vessels) ===
    for i, (px, py) in enumerate([(1.2, 0.5), (1.35, 0.8), (1.05, 0.75)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(px, py, BZ + 0.12))
        pot = bpy.context.active_object
        pot.name = f"ClayPot_{i}"
        pot.scale = (1, 1, 1.3)
        pot.data.materials.append(m['stone'])

    # === Low stone bench ===
    bmesh_box("Bench", (0.80, 0.25, 0.25), (-0.8, 1.2, Z + 0.125), m['stone_dark'])

    # === Stone steps to doorway ===
    bmesh_box("Step1", (0.50, 0.25, 0.06), (0, -hut_d / 2 - 0.20, Z + 0.06), m['stone_dark'])
    bmesh_box("Step2", (0.55, 0.25, 0.06), (0, -hut_d / 2 - 0.45, Z + 0.03), m['stone_dark'])

    # === Outdoor fire pit ===
    bmesh_prism("FirePit", 0.25, 0.08, 8, (1.0, -0.5, Z + 0.04), m['stone_dark'])

    # === Drying rack ===
    for dy in [-0.20, 0.20]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.025, depth=0.80,
                                            location=(-1.5, 0.6 + dy, Z + 0.40))
        bpy.context.active_object.name = f"Rack_{dy:.1f}"
        bpy.context.active_object.data.materials.append(m['wood'])
    bmesh_box("RackBar", (0.03, 0.50, 0.03), (-1.5, 0.6, Z + 0.80), m['wood'])


# ============================================================
# BRONZE AGE -- Minoan palace fragment
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Stone platform base ===
    bmesh_box("Platform", (4.2, 3.6, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.18
    wall_h = 1.8

    # === Light stone palace walls ===
    bmesh_box("WallF", (3.6, 0.14, wall_h), (0, -1.50, BZ + wall_h / 2), m['stone_light'])
    bmesh_box("WallB", (3.6, 0.14, wall_h), (0, 1.50, BZ + wall_h / 2), m['stone_light'])
    bmesh_box("WallR", (0.14, 3.0, wall_h), (1.80, 0, BZ + wall_h / 2), m['stone_light'])
    bmesh_box("WallL", (0.14, 3.0, wall_h), (-1.80, 0, BZ + wall_h / 2), m['stone_light'])

    # Horizontal stone band detail
    for z_off in [0.5, 1.0, 1.5]:
        bmesh_box(f"BandF_{z_off:.1f}", (3.5, 0.02, 0.04), (0, -1.51, BZ + z_off), m['stone_trim'])
        bmesh_box(f"BandB_{z_off:.1f}", (3.5, 0.02, 0.04), (0, 1.51, BZ + z_off), m['stone_trim'])

    # === Flat roof slab ===
    bmesh_box("Roof", (3.8, 3.2, 0.12), (0, 0, BZ + wall_h + 0.06), m['stone_light'])

    # === Minoan red columns (tapering downward -- wider at top) ===
    # Characteristic Minoan inverted taper: top wider, base narrower
    col_positions = [(-1.0, -1.51), (-0.3, -1.51), (0.3, -1.51), (1.0, -1.51)]
    for i, (cx, cy) in enumerate(col_positions):
        # Build column as truncated cone (wider at top)
        base_r = 0.06
        top_r = 0.09
        col_h = wall_h - 0.10
        n_seg = 12
        verts = []
        faces = []
        n_rings = 2
        for ri in range(n_rings):
            t = ri / (n_rings - 1)
            r = base_r + (top_r - base_r) * t
            cz = BZ + 0.05 + col_h * t
            for si in range(n_seg):
                a = (2 * math.pi * si) / n_seg
                verts.append((cx + r * math.cos(a), cy - 0.08 + r * math.sin(a), cz))
        # Side faces
        for ri in range(n_rings - 1):
            for si in range(n_seg):
                sn = (si + 1) % n_seg
                a = ri * n_seg + si
                b = ri * n_seg + sn
                c = (ri + 1) * n_seg + sn
                d = (ri + 1) * n_seg + si
                faces.append((a, b, c, d))
        # Bottom and top caps
        faces.append(tuple(range(n_seg)))
        faces.append(tuple(range((n_rings - 1) * n_seg, n_rings * n_seg)))
        obj = mesh_from_pydata(f"MinoanCol_{i}", verts, faces, m['banner'])  # red
        for p in obj.data.polygons:
            p.use_smooth = True
        # Column cushion capital (wider disc)
        bmesh_prism(f"ColCap_{i}", top_r * 1.5, 0.06, n_seg,
                    (cx, cy - 0.08, BZ + 0.05 + col_h), m['banner'])

    # === Interior columns (two rows) ===
    for ix, iy in [(-0.5, -0.3), (-0.5, 0.5), (0.5, -0.3), (0.5, 0.5)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.07, depth=wall_h - 0.1,
                                            location=(ix, iy, BZ + wall_h / 2))
        col = bpy.context.active_object
        col.name = f"IntCol_{ix:.1f}_{iy:.1f}"
        col.data.materials.append(m['banner'])
        for p in col.data.polygons:
            p.use_smooth = True

    # === Bull horns of consecration on roof ===
    _bull_horns("BullHornsC", (0, 0, BZ + wall_h + 0.12), 0.25, 0.35, m['stone_light'])
    _bull_horns("BullHornsL", (-1.2, 0, BZ + wall_h + 0.12), 0.18, 0.25, m['stone_light'])
    _bull_horns("BullHornsR", (1.2, 0, BZ + wall_h + 0.12), 0.18, 0.25, m['stone_light'])

    # === Entrance doorway ===
    bmesh_box("Door", (0.08, 0.60, 1.30), (0, -1.51, BZ + 0.65), m['door'])
    bmesh_box("DoorLintel", (0.10, 0.70, 0.06), (0, -1.52, BZ + 1.33), m['stone_trim'])

    # === Fresco wall detail (painted band) ===
    bmesh_box("Fresco", (2.0, 0.03, 0.30), (0, -1.52, BZ + 1.10), m['gold'])

    # === Light well (central courtyard opening) ===
    bmesh_prism("LightWell", 0.40, 0.06, 8, (0, 0.3, BZ + 0.01), m['stone_dark'])

    # === Storage jars (pithoi) ===
    for i, (px, py) in enumerate([(1.4, 0.8), (1.5, 0.4), (1.3, 1.1)]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.10, depth=0.40,
                                            location=(px, py, BZ + 0.20))
        jar = bpy.context.active_object
        jar.name = f"Pithos_{i}"
        jar.data.materials.append(m['stone'])


# ============================================================
# IRON AGE -- Mycenaean megaron with Lion Gate
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Cyclopean stone wall enclosure (massive irregular blocks) ===
    wall_h = 1.6
    wt = 0.22
    bmesh_box("CycWallF", (4.0, wt, wall_h), (0, -1.80, Z + wall_h / 2), m['stone_dark'], bevel=0.06)
    bmesh_box("CycWallB", (4.0, wt, wall_h), (0, 1.80, Z + wall_h / 2), m['stone_dark'], bevel=0.06)
    bmesh_box("CycWallR", (wt, 3.6, wall_h), (2.00, 0, Z + wall_h / 2), m['stone_dark'], bevel=0.06)
    bmesh_box("CycWallL", (wt, 3.6, wall_h), (-2.00, 0, Z + wall_h / 2), m['stone_dark'], bevel=0.06)

    # Stone block texture (horizontal courses on walls)
    for z_off in [0.35, 0.70, 1.05, 1.40]:
        bmesh_box(f"CourseF_{z_off:.2f}", (3.9, 0.03, 0.04), (0, -1.81, Z + z_off), m['stone'])
        bmesh_box(f"CourseR_{z_off:.2f}", (0.03, 3.5, 0.04), (2.01, 0, Z + z_off), m['stone'])

    BZ = Z + 0.06

    # === Lion Gate entrance (iconic trapezoidal doorway) ===
    gate_x = 0
    gate_y = -1.80
    # Massive lintel stone
    bmesh_box("GateLintel", (0.30, 1.00, 0.18), (gate_x, gate_y - 0.01, Z + wall_h - 0.09), m['stone'], bevel=0.03)
    # Relieving triangle above lintel
    rv = [
        (gate_x - 0.40, gate_y - 0.06, Z + wall_h + 0.09),
        (gate_x + 0.40, gate_y - 0.06, Z + wall_h + 0.09),
        (gate_x, gate_y - 0.06, Z + wall_h + 0.45),
    ]
    mesh_from_pydata("RelievingTri", rv, [(0, 1, 2)], m['stone_light'])

    # Lion relief panel (simplified -- two opposing triangular shapes)
    for sx in [-1, 1]:
        lv = [
            (gate_x + sx * 0.05, gate_y - 0.07, Z + wall_h + 0.12),
            (gate_x + sx * 0.30, gate_y - 0.07, Z + wall_h + 0.12),
            (gate_x + sx * 0.20, gate_y - 0.07, Z + wall_h + 0.38),
            (gate_x + sx * 0.08, gate_y - 0.07, Z + wall_h + 0.35),
        ]
        mesh_from_pydata(f"Lion_{sx}", lv, [(0, 1, 2, 3)], m['gold'])

    # Central column in lion relief
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=0.28,
                                        location=(gate_x, gate_y - 0.07, Z + wall_h + 0.26))
    col_r = bpy.context.active_object
    col_r.name = "LionCol"
    col_r.data.materials.append(m['stone_trim'])

    # Gate opening
    bmesh_box("GateOpening", (0.08, 0.70, 1.40), (gate_x, gate_y - 0.01, Z + 0.70), m['door'])

    # === Main megaron hall ===
    hall_w, hall_d = 2.8, 2.4
    hall_h = 2.0
    bmesh_box("MegaronWalls", (hall_w, hall_d, hall_h), (0, 0.20, BZ + hall_h / 2), m['stone'], bevel=0.04)

    # === Porch with two columns (prostyle) ===
    for cy_off in [-0.50, 0.50]:
        _doric_column(f"PorchCol_{cy_off:.1f}", (0, -1.20 + cy_off * 0.6, BZ),
                      0.08, hall_h - 0.15, m['stone_light'], segments=8)

    # === Flat timber and clay roof ===
    bmesh_box("MegaronRoof", (hall_w + 0.12, hall_d + 0.30, 0.12),
              (0, 0.20, BZ + hall_h + 0.06), m['wood'])
    # Roof parapet
    bmesh_box("RoofParapet", (hall_w + 0.18, hall_d + 0.36, 0.08),
              (0, 0.20, BZ + hall_h + 0.16), m['stone'])

    # === Central hearth (round fire pit in megaron) ===
    bmesh_prism("Hearth", 0.35, 0.10, 10, (0, 0.20, BZ + 0.05), m['stone_dark'])
    bmesh_prism("HearthRing", 0.40, 0.06, 12, (0, 0.20, BZ + 0.03), m['stone'])

    # === Four interior columns around hearth ===
    for cx, cy in [(-0.50, -0.20), (0.50, -0.20), (-0.50, 0.60), (0.50, 0.60)]:
        _doric_column(f"IntCol_{cx:.1f}_{cy:.1f}", (cx, cy, BZ),
                      0.06, hall_h - 0.20, m['stone_light'], segments=8)

    # === Corbelled gallery (small side passage) ===
    gal_x = -1.60
    gal_h = 1.2
    bmesh_box("Gallery", (0.60, 1.2, gal_h), (gal_x, 0.8, BZ + gal_h / 2), m['stone_dark'], bevel=0.03)
    # Corbelled top (triangular profile)
    cv = [
        (gal_x - 0.30, 0.20, BZ + gal_h),
        (gal_x + 0.30, 0.20, BZ + gal_h),
        (gal_x + 0.15, 0.20, BZ + gal_h + 0.30),
        (gal_x - 0.15, 0.20, BZ + gal_h + 0.30),
        (gal_x - 0.30, 1.40, BZ + gal_h),
        (gal_x + 0.30, 1.40, BZ + gal_h),
        (gal_x + 0.15, 1.40, BZ + gal_h + 0.30),
        (gal_x - 0.15, 1.40, BZ + gal_h + 0.30),
    ]
    cf = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh_from_pydata("CorbelRoof", cv, cf, m['stone_dark'])

    # === Throne base (stone slab in megaron) ===
    bmesh_box("Throne", (0.35, 0.30, 0.30), (0, 1.10, BZ + 0.15), m['stone_light'])

    # === Steps at entrance ===
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.25, 1.0, 0.06),
                  (0, -1.80 - 0.25 * (i + 1), Z + wall_h * 0 + 0.03 - i * 0.01), m['stone'])

    # === Guard tower (corner) ===
    tw_x, tw_y = 2.00, -1.80
    bmesh_box("Tower", (0.70, 0.70, wall_h + 0.60), (tw_x, tw_y, Z + (wall_h + 0.60) / 2), m['stone_dark'], bevel=0.04)
    bmesh_box("TowerTop", (0.78, 0.78, 0.08), (tw_x, tw_y, Z + wall_h + 0.64), m['stone'])


# ============================================================
# CLASSICAL AGE -- Grand Greek temple (Parthenon style)
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (6.0, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Stepped crepidoma (three steps platform) ===
    for i in range(3):
        step_w = 4.8 - i * 0.18
        step_d = 3.4 - i * 0.14
        step_h = 0.12
        bmesh_box(f"Crepidoma_{i}", (step_w, step_d, step_h),
                  (0, 0, Z + 0.06 + i * step_h + step_h / 2), m['stone_light'], bevel=0.02)

    BZ = Z + 0.06 + 3 * 0.12  # top of crepidoma

    # === Stylobate (floor) ===
    sty_w, sty_d = 4.2, 2.8
    bmesh_box("Stylobate", (sty_w, sty_d, 0.08), (0, 0, BZ + 0.04), m['stone_light'])

    BZ += 0.08

    # === Peristyle of Doric columns ===
    col_h = 2.0
    col_r = 0.08
    # Front row (8 columns)
    n_front = 8
    for i in range(n_front):
        cx = -sty_w / 2 + 0.25 + i * (sty_w - 0.50) / (n_front - 1)
        _doric_column(f"ColF_{i}", (cx, -sty_d / 2 + 0.20, BZ), col_r, col_h, m['stone_light'])
    # Back row (8 columns)
    for i in range(n_front):
        cx = -sty_w / 2 + 0.25 + i * (sty_w - 0.50) / (n_front - 1)
        _doric_column(f"ColB_{i}", (cx, sty_d / 2 - 0.20, BZ), col_r, col_h, m['stone_light'])
    # Side rows (6 columns each side, excluding corners already placed)
    n_side = 4
    for i in range(n_side):
        cy = -sty_d / 2 + 0.55 + i * (sty_d - 1.10) / max(n_side - 1, 1)
        _doric_column(f"ColR_{i}", (-sty_w / 2 + 0.20, cy, BZ), col_r, col_h, m['stone_light'])
        _doric_column(f"ColL_{i}", (sty_w / 2 - 0.20, cy, BZ), col_r, col_h, m['stone_light'])

    # === Entablature (architrave + frieze + cornice) ===
    ent_z = BZ + col_h + col_r * 0.4  # just above column capitals
    # Architrave
    bmesh_box("Architrave", (sty_w + 0.10, sty_d + 0.10, 0.12),
              (0, 0, ent_z + 0.06), m['stone_light'])
    # Triglyphs and metopes (frieze band with alternating panels)
    frieze_z = ent_z + 0.12
    bmesh_box("Frieze", (sty_w + 0.10, sty_d + 0.10, 0.16),
              (0, 0, frieze_z + 0.08), m['stone'])
    # Triglyph details (vertical grooves on front frieze)
    for i in range(12):
        tx = -sty_w / 2 + 0.20 + i * (sty_w - 0.40) / 11
        bmesh_box(f"Triglyph_{i}", (0.10, 0.03, 0.14),
                  (tx, -sty_d / 2 - 0.05, frieze_z + 0.08), m['stone_trim'])
    # Cornice
    bmesh_box("Cornice", (sty_w + 0.20, sty_d + 0.20, 0.08),
              (0, 0, frieze_z + 0.20), m['stone_light'], bevel=0.02)

    # === Triangular pediments (front and back) ===
    ped_z = frieze_z + 0.24
    _pediment("PedimentF", sty_w + 0.10, 0.70, 0.10, (0, -sty_d / 2 - 0.02, ped_z), m['stone_light'])
    _pediment("PedimentB", sty_w + 0.10, 0.70, 0.10, (0, sty_d / 2 + 0.02, ped_z), m['stone_light'])

    # === Pediment sculpture reliefs (simplified figures) ===
    for sx in [-0.80, -0.40, 0, 0.40, 0.80]:
        fig_h = 0.40 - abs(sx) * 0.20
        bmesh_box(f"PedFig_{sx:.1f}", (0.10, 0.04, fig_h),
                  (sx, -sty_d / 2 - 0.06, ped_z + fig_h / 2 + 0.02), m['gold'])

    # === Acroteria on pediment ===
    _acroterion("AcroApex", (0, -sty_d / 2 - 0.02, ped_z + 0.70), 0.15, m['gold'])
    _acroterion("AcroL", (-sty_w / 2, -sty_d / 2 - 0.02, ped_z), 0.12, m['gold'])
    _acroterion("AcroR", (sty_w / 2, -sty_d / 2 - 0.02, ped_z), 0.12, m['gold'])

    # === Roof (low-pitched, covering the temple) ===
    roof_z = ped_z - 0.02
    rv = [
        (-sty_w / 2 - 0.10, -sty_d / 2 - 0.10, roof_z),
        (sty_w / 2 + 0.10, -sty_d / 2 - 0.10, roof_z),
        (sty_w / 2 + 0.10, sty_d / 2 + 0.10, roof_z),
        (-sty_w / 2 - 0.10, sty_d / 2 + 0.10, roof_z),
        (0, -sty_d / 2 - 0.10, roof_z + 0.70),
        (0, sty_d / 2 + 0.10, roof_z + 0.70),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    obj = mesh_from_pydata("TempleRoof", rv, rf, m['roof'])
    for p in obj.data.polygons:
        p.use_smooth = True

    # === Naos (inner cella hall) ===
    naos_w, naos_d, naos_h = 2.4, 1.6, 1.8
    bmesh_box("Naos", (naos_w, naos_d, naos_h), (0, 0, BZ + naos_h / 2), m['stone'], bevel=0.02)
    # Naos door
    bmesh_box("NaosDoor", (0.06, 0.50, 1.30), (0, -naos_d / 2 - 0.01, BZ + 0.65), m['door'])

    # === Meander strip at base of naos ===
    _meander_strip("MeanderF", naos_w, (0, -naos_d / 2 - 0.02, BZ), m['gold'], axis='x')

    # === Altar in front ===
    bmesh_box("Altar", (0.40, 0.30, 0.50), (0, -sty_d / 2 - 0.60, Z + 0.25), m['stone_light'])
    bmesh_box("AltarTop", (0.44, 0.34, 0.04), (0, -sty_d / 2 - 0.60, Z + 0.52), m['stone_trim'])


# ============================================================
# MEDIEVAL AGE -- Byzantine church
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation ===
    bmesh_box("Found", (4.5, 4.5, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.15

    # === Greek cross plan body ===
    # Central square
    ctr_w = 2.0
    wall_h = 2.4
    bmesh_box("CenterBody", (ctr_w, ctr_w, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.03)

    # Four arms of the cross
    arm_len = 1.2
    arm_w = 1.4
    arm_h = 2.0
    bmesh_box("ArmN", (arm_w, arm_len, arm_h), (0, ctr_w / 2 + arm_len / 2 - 0.10, BZ + arm_h / 2), m['stone'], bevel=0.02)
    bmesh_box("ArmS", (arm_w, arm_len, arm_h), (0, -ctr_w / 2 - arm_len / 2 + 0.10, BZ + arm_h / 2), m['stone'], bevel=0.02)
    bmesh_box("ArmE", (arm_len, arm_w, arm_h), (ctr_w / 2 + arm_len / 2 - 0.10, 0, BZ + arm_h / 2), m['stone'], bevel=0.02)
    bmesh_box("ArmW", (arm_len, arm_w, arm_h), (-ctr_w / 2 - arm_len / 2 + 0.10, 0, BZ + arm_h / 2), m['stone'], bevel=0.02)

    # === Arm pitched roofs ===
    for lbl, ox, oy, is_x in [("N", 0, ctr_w / 2 + arm_len / 2 - 0.10, False),
                                ("S", 0, -ctr_w / 2 - arm_len / 2 + 0.10, False),
                                ("E", ctr_w / 2 + arm_len / 2 - 0.10, 0, True),
                                ("W", -ctr_w / 2 - arm_len / 2 + 0.10, 0, True)]:
        if is_x:
            pyramid_roof(f"ArmRoof_{lbl}", w=arm_len - 0.10, d=arm_w - 0.10, h=0.50,
                         overhang=0.08, origin=(ox, oy, BZ + arm_h + 0.02), material=m['roof'])
        else:
            pyramid_roof(f"ArmRoof_{lbl}", w=arm_w - 0.10, d=arm_len - 0.10, h=0.50,
                         overhang=0.08, origin=(ox, oy, BZ + arm_h + 0.02), material=m['roof'])

    # === Central dome on drum ===
    drum_r = 0.75
    drum_h = 0.60
    bmesh_prism("Drum", drum_r, drum_h, 16, (0, 0, BZ + wall_h), m['stone_trim'])
    # Drum windows (round arched)
    n_drum_win = 8
    for i in range(n_drum_win):
        a = (2 * math.pi * i) / n_drum_win
        wx = drum_r * 0.98 * math.cos(a)
        wy = drum_r * 0.98 * math.sin(a)
        bmesh_box(f"DrumWin_{i}", (0.10, 0.06, 0.30),
                  (wx, wy, BZ + wall_h + drum_h / 2 + 0.05), m['window'])
    # Dome
    dome_z = BZ + wall_h + drum_h
    _dome("MainDome", (0, 0, dome_z), drum_r - 0.05, 0.65, m['roof'])
    # Cross on top of dome
    cross_z = dome_z + 0.65
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.30,
                                        location=(0, 0, cross_z + 0.15))
    bpy.context.active_object.name = "CrossV"
    bpy.context.active_object.data.materials.append(m['gold'])
    bmesh_box("CrossH", (0.20, 0.03, 0.03), (0, 0, cross_z + 0.25), m['gold'])

    # === Round arched windows on arms ===
    # South arm front (main facade)
    for wx in [-0.35, 0.35]:
        bmesh_box(f"WinS_{wx:.1f}", (0.12, 0.06, 0.50),
                  (wx, -ctr_w / 2 - arm_len + 0.11, BZ + arm_h / 2 + 0.20), m['window'])
        # Arched top
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.06, depth=0.06,
                                            location=(wx, -ctr_w / 2 - arm_len + 0.10,
                                                      BZ + arm_h / 2 + 0.45))
        arch = bpy.context.active_object
        arch.name = f"WinArch_{wx:.1f}"
        arch.rotation_euler = (math.radians(90), 0, 0)
        arch.data.materials.append(m['stone_trim'])

    # East and west arm windows
    for arm_dir, ay, rot in [("E", ctr_w / 2 + arm_len / 2, 0),
                              ("W", -ctr_w / 2 - arm_len / 2, 0)]:
        for wy in [-0.30, 0.30]:
            bmesh_box(f"Win{arm_dir}_{wy:.1f}", (0.06, 0.12, 0.45),
                      (ay, wy, BZ + arm_h / 2 + 0.20), m['window'])

    # === Bell tower (campanile) ===
    tw_x, tw_y = -1.80, -1.60
    tower_h = 3.8
    bmesh_box("BellTower", (0.70, 0.70, tower_h), (tw_x, tw_y, BZ + tower_h / 2), m['stone'], bevel=0.02)
    # Arched openings at top (belfry)
    for side_x, side_y, face in [(tw_x - 0.36, tw_y, 'x'), (tw_x + 0.36, tw_y, 'x'),
                                  (tw_x, tw_y - 0.36, 'y'), (tw_x, tw_y + 0.36, 'y')]:
        bmesh_box(f"Belfry_{side_x:.1f}_{side_y:.1f}", (0.05 if face == 'x' else 0.20,
                                                          0.20 if face == 'x' else 0.05,
                                                          0.35),
                  (side_x, side_y, BZ + tower_h - 0.40), m['window'])
    # Tower dome
    _dome(f"TowerDome", (tw_x, tw_y, BZ + tower_h), 0.30, 0.35, m['roof'], segments=10, rings=6)
    # Tower cross
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.20,
                                        location=(tw_x, tw_y, BZ + tower_h + 0.35 + 0.10))
    bpy.context.active_object.data.materials.append(m['gold'])
    bmesh_box("TwCrossH", (0.12, 0.02, 0.02), (tw_x, tw_y, BZ + tower_h + 0.50), m['gold'])

    # === Mosaic/decorative band ===
    _meander_strip("MosaicS", 1.2, (0, -ctr_w / 2 - arm_len + 0.10, BZ + arm_h - 0.10), m['gold'], axis='x')

    # === Entrance portal ===
    bmesh_box("Portal", (0.70, 0.10, 1.50), (0, -ctr_w / 2 - arm_len + 0.10, BZ + 0.75), m['door'])
    bmesh_box("PortalFrame", (0.80, 0.12, 0.08), (0, -ctr_w / 2 - arm_len + 0.09, BZ + 1.53), m['stone_trim'])

    # === Steps ===
    for i in range(4):
        bmesh_box(f"Step_{i}", (1.0, 0.22, 0.06),
                  (0, -ctr_w / 2 - arm_len - 0.05 - i * 0.22, BZ - 0.02 - i * 0.04), m['stone_dark'])

    # === Small apse (semicircular bump on north arm) ===
    bmesh_prism("Apse", 0.50, arm_h, 8, (0, ctr_w / 2 + arm_len - 0.10, BZ), m['stone'])
    _dome("ApseDome", (0, ctr_w / 2 + arm_len - 0.10, BZ + arm_h), 0.45, 0.30, m['roof'],
          segments=10, rings=5)


# ============================================================
# GUNPOWDER AGE -- Venetian-Greek fortress
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (6.0, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Star-shaped fortress walls ===
    bmesh_box("RampartBase", (5.4, 5.4, 0.22), (0, 0, Z + 0.11), m['stone_dark'], bevel=0.06)

    BZ = Z + 0.22
    hw = 2.2
    WALL_H = 2.2
    wt = 0.22

    # Fortress walls
    bmesh_box("WallF", (wt, hw * 2 - 0.20, WALL_H), (hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallB", (wt, hw * 2 - 0.20, WALL_H), (-hw, 0, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallR", (hw * 2 - 0.20, wt, WALL_H), (0, -hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)
    bmesh_box("WallL", (hw * 2 - 0.20, wt, WALL_H), (0, hw, BZ + WALL_H / 2), m['stone'], bevel=0.02)

    # Battlements
    for i in range(10):
        y = -1.8 + i * 0.40
        bmesh_box(f"MF_{i}", (0.10, 0.14, 0.18), (hw + 0.06, y, BZ + WALL_H + 0.09), m['stone_trim'], bevel=0.01)
        bmesh_box(f"MB_{i}", (0.10, 0.14, 0.18), (-hw - 0.06, y, BZ + WALL_H + 0.09), m['stone_trim'], bevel=0.01)
    for i in range(10):
        x = -1.8 + i * 0.40
        bmesh_box(f"MR_{i}", (0.14, 0.10, 0.18), (x, -hw - 0.06, BZ + WALL_H + 0.09), m['stone_trim'], bevel=0.01)
        bmesh_box(f"ML_{i}", (0.14, 0.10, 0.18), (x, hw + 0.06, BZ + WALL_H + 0.09), m['stone_trim'], bevel=0.01)

    # === Angular bastions (star fort points) ===
    bastion_h = WALL_H + 0.25
    for xs, ys, lbl in [(-1, -1, "BL"), (-1, 1, "FL"), (1, -1, "BR"), (1, 1, "FR")]:
        bx, by = xs * hw, ys * hw
        # Diamond bastion shape
        bv = [
            (bx, by + ys * 0.70, BZ),
            (bx + xs * 0.70, by, BZ),
            (bx, by - ys * 0.30, BZ),
            (bx - xs * 0.30, by, BZ),
            (bx, by + ys * 0.70, BZ + bastion_h),
            (bx + xs * 0.70, by, BZ + bastion_h),
            (bx, by - ys * 0.30, BZ + bastion_h),
            (bx - xs * 0.30, by, BZ + bastion_h),
        ]
        bf = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        mesh_from_pydata(f"Bastion_{lbl}", bv, bf, m['stone_upper'])
        # Cannon slit
        bmesh_box(f"CSlit_{lbl}", (0.04, 0.12, 0.08),
                  (bx + xs * 0.50, by + ys * 0.50, BZ + 1.0), m['window'])

    # === Venetian lion relief on gate ===
    lion_y = -hw - wt / 2
    lv = [
        (0.25, lion_y - 0.02, BZ + WALL_H - 0.60),
        (-0.25, lion_y - 0.02, BZ + WALL_H - 0.60),
        (-0.20, lion_y - 0.02, BZ + WALL_H - 0.20),
        (0.20, lion_y - 0.02, BZ + WALL_H - 0.20),
    ]
    mesh_from_pydata("VenetianLion", lv, [(0, 1, 2, 3)], m['gold'])

    # === Gate entrance ===
    bmesh_box("Gate", (0.60, 0.10, 1.50), (0, -hw - wt / 2 - 0.01, BZ + 0.75), m['door'])
    # Arched gate top
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.30, depth=wt + 0.04,
                                        location=(0, -hw, BZ + 1.50))
    arch = bpy.context.active_object
    arch.name = "GateArch"
    arch.rotation_euler = (math.radians(90), 0, 0)
    arch.data.materials.append(m['stone_trim'])

    # === Domed chapel inside fortress ===
    chapel_x, chapel_y = 0.6, 0.6
    chapel_w, chapel_h = 1.2, 1.8
    bmesh_box("Chapel", (chapel_w, chapel_w, chapel_h), (chapel_x, chapel_y, BZ + chapel_h / 2), m['stone_light'], bevel=0.02)
    # Chapel dome
    _dome("ChapelDome", (chapel_x, chapel_y, BZ + chapel_h), 0.55, 0.50, m['roof'])
    # Cross on dome
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.20,
                                        location=(chapel_x, chapel_y, BZ + chapel_h + 0.50 + 0.10))
    bpy.context.active_object.data.materials.append(m['gold'])
    bmesh_box("ChapelCrossH", (0.10, 0.02, 0.02), (chapel_x, chapel_y, BZ + chapel_h + 0.65), m['gold'])

    # Chapel windows
    for cy_off in [-0.35, 0.35]:
        bmesh_box(f"ChapelWin_{cy_off:.1f}", (0.06, 0.10, 0.35),
                  (chapel_x + chapel_w / 2 + 0.01, chapel_y + cy_off, BZ + chapel_h / 2 + 0.20), m['window'])

    # === Clock tower with arched openings ===
    tw_x, tw_y = -0.8, -0.6
    tower_h = 4.0
    bmesh_box("ClockTower", (0.80, 0.80, tower_h), (tw_x, tw_y, BZ + tower_h / 2), m['stone'], bevel=0.02)

    # Stone bands on tower
    for tz in [BZ + 1.0, BZ + 2.0, BZ + 3.0, BZ + tower_h]:
        bmesh_box(f"TBand_{tz:.1f}", (0.86, 0.86, 0.06), (tw_x, tw_y, tz), m['stone_trim'], bevel=0.01)

    # Arched windows on tower
    for tz in [BZ + 1.3, BZ + 2.5]:
        for face_x, face_y in [(tw_x + 0.41, tw_y), (tw_x - 0.41, tw_y)]:
            bmesh_box(f"TWin_{tz:.1f}_{face_x:.1f}", (0.05, 0.14, 0.40),
                      (face_x, face_y, tz), m['window'])

    # Clock face
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.22, depth=0.04,
                                        location=(tw_x + 0.41, tw_y, BZ + 3.4))
    clock = bpy.context.active_object
    clock.name = "Clock"
    clock.rotation_euler = (0, math.radians(90), 0)
    clock.data.materials.append(m['gold'])

    # Tower pointed roof
    bmesh_cone("TowerRoof", 0.50, 1.0, 8, (tw_x, tw_y, BZ + tower_h), m['roof'])

    # === Steps to gate ===
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.22, 1.2, 0.06),
                  (0, -hw - wt / 2 - 0.30 - i * 0.22, BZ - 0.04 - i * 0.05), m['stone_dark'])

    # === Cannons on walls ===
    for cx, cy, rot in [(hw + 0.10, -1.0, 0), (hw + 0.10, 1.0, 0), (-1.0, -hw - 0.10, math.radians(90))]:
        bmesh_box(f"CanBase_{cx:.1f}_{cy:.1f}", (0.25, 0.12, 0.08),
                  (cx, cy, BZ + WALL_H + 0.04), m['iron'])
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035, depth=0.35,
                                            location=(cx + 0.15 * math.cos(rot), cy + 0.15 * math.sin(rot),
                                                      BZ + WALL_H + 0.12))
        cn = bpy.context.active_object
        cn.name = f"Cannon_{cx:.1f}"
        cn.rotation_euler = (0, math.radians(80), rot)
        cn.data.materials.append(m['iron'])


# ============================================================
# ENLIGHTENMENT AGE -- Neoclassical Greek revival
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (6.5, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation ===
    bmesh_box("Found", (6.0, 5.0, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.18

    # === Central main block ===
    main_w, main_d = 2.8, 2.2
    main_h = 3.4
    bmesh_box("Main", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone_light'], bevel=0.03)

    # Moldings
    bmesh_box("BaseMold", (main_w + 0.06, main_d + 0.06, 0.08), (0, 0, BZ + 0.04), m['stone_trim'], bevel=0.02)
    bmesh_box("Cornice", (main_w + 0.10, main_d + 0.10, 0.10), (0, 0, BZ + main_h), m['stone_trim'], bevel=0.03)

    # === Tall Ionic colonnade across the front ===
    col_h = 2.8
    n_cols = 6
    col_spacing = (main_w - 0.40) / (n_cols - 1)
    for i in range(n_cols):
        cx = -main_w / 2 + 0.20 + i * col_spacing
        _ionic_column(f"Col_{i}", (cx, -main_d / 2 - 0.45, BZ),
                      0.08, col_h, m['stone_light'])

    # === Portico roof (flat slab held by columns) ===
    portico_z = BZ + col_h + 0.08 * 0.3 + 0.08 * 2.6 * 0.5  # above capitals
    bmesh_box("PorticoRoof", (main_w + 0.10, 0.70, 0.12),
              (0, -main_d / 2 - 0.45, BZ + col_h + 0.30), m['stone_light'])

    # === Triangular pediment ===
    ped_z = BZ + col_h + 0.36
    _pediment("Pediment", main_w + 0.10, 0.80, 0.12,
              (0, -main_d / 2 - 0.45, ped_z), m['stone_light'])

    # Pediment sculpture relief
    for sx in [-0.60, -0.20, 0.20, 0.60]:
        fig_h = 0.45 - abs(sx) * 0.25
        bmesh_box(f"PedFig_{sx:.1f}", (0.10, 0.04, fig_h),
                  (sx, -main_d / 2 - 0.50, ped_z + fig_h / 2 + 0.03), m['gold'])

    # === Acroteria ===
    _acroterion("AcroApex", (0, -main_d / 2 - 0.45, ped_z + 0.80), 0.18, m['gold'])
    _acroterion("AcroL", (-main_w / 2 - 0.05, -main_d / 2 - 0.45, ped_z), 0.14, m['gold'])
    _acroterion("AcroR", (main_w / 2 + 0.05, -main_d / 2 - 0.45, ped_z), 0.14, m['gold'])

    # === Symmetrical wings ===
    wing_w, wing_d, wing_h = 1.4, 1.8, 2.8
    for ys, lbl in [(-2.2, "R"), (2.2, "L")]:
        bmesh_box(f"Wing_{lbl}", (wing_w, wing_d, wing_h), (0, ys, BZ + wing_h / 2), m['stone_light'], bevel=0.02)
        bmesh_box(f"WCornice_{lbl}", (wing_w + 0.06, wing_d + 0.06, 0.08),
                  (0, ys, BZ + wing_h), m['stone_trim'], bevel=0.02)
        # Wing hip roof
        pyramid_roof(f"WRoof_{lbl}", w=wing_w - 0.15, d=wing_d - 0.15, h=0.55,
                     overhang=0.10, origin=(0, ys, BZ + wing_h + 0.04), material=m['roof'])
        # Wing windows (tall, 2 rows)
        for row, z_off in [(0.5, 0), (1.6, 1)]:
            for wy in [-0.50, 0, 0.50]:
                bmesh_box(f"WWin_{lbl}_{row:.1f}_{wy:.1f}", (0.06, 0.16, 0.55),
                          (wing_w / 2 + 0.01, ys + wy, BZ + row + 0.10), m['window'])
                # Window pediment (small triangular header)
                wv = [
                    (wing_w / 2 + 0.02, ys + wy - 0.10, BZ + row + 0.68),
                    (wing_w / 2 + 0.02, ys + wy + 0.10, BZ + row + 0.68),
                    (wing_w / 2 + 0.02, ys + wy, BZ + row + 0.78),
                ]
                mesh_from_pydata(f"WinPed_{lbl}_{row:.1f}_{wy:.1f}", wv, [(0, 1, 2)], m['stone_trim'])

    # === Main building windows (front facade) ===
    for i, y in enumerate([-0.70, -0.25, 0.25, 0.70]):
        for z_off, h in [(0.6, 0.60), (1.8, 0.70)]:
            bmesh_box(f"MWin_{i}_{z_off}", (0.06, 0.18, h),
                      (-main_w / 2 - 0.01, y, BZ + z_off), m['window'])

    # === Hip roof on main block ===
    pyramid_roof("MainRoof", w=main_w - 0.15, d=main_d - 0.15, h=0.70,
                 overhang=0.12, origin=(0, 0, BZ + main_h + 0.04), material=m['roof'])

    # === Entrance door ===
    bmesh_box("Door", (0.08, 0.65, 1.60), (0, -main_d / 2 - 0.45, BZ + 0.80), m['door'])

    # === Steps (grand staircase) ===
    for i in range(6):
        bmesh_box(f"Step_{i}", (0.22, main_w + 0.20, 0.06),
                  (0, -main_d / 2 - 0.70 - i * 0.22, BZ - 0.04 - i * 0.05), m['stone_light'])

    # === Meander decorative strip above colonnade ===
    _meander_strip("MeanderFront", main_w, (0, -main_d / 2 - 0.46, BZ + col_h + 0.20), m['gold'], axis='x')

    # === Formal garden hedges ===
    for gy in [-1.5, -0.5, 0.5, 1.5]:
        bmesh_box(f"Hedge_{gy:.1f}", (0.45, 0.22, 0.16),
                  (-main_d / 2 - 1.40, gy, Z + 0.08), m['ground'])


# ============================================================
# INDUSTRIAL AGE -- Greek neoclassical civic building
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (6.5, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.15
    bmesh_box("Found", (6.0, 5.0, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.04)

    # === Main marble building ===
    main_w, main_d = 4.0, 3.0
    main_h = 3.5
    bmesh_box("Main", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone_light'], bevel=0.02)

    # Horizontal bands (marble courses)
    for z in [BZ + 0.8, BZ + 1.6, BZ + 2.4, BZ + 3.2]:
        bmesh_box(f"Band_{z:.1f}", (main_w + 0.02, main_d + 0.02, 0.04), (0, 0, z), m['stone_trim'])

    # === Tall arched windows (3 rows x 5 cols on front) ===
    for row, z_off in enumerate([0.4, 1.3, 2.3]):
        for y in [-1.0, -0.50, 0, 0.50, 1.0]:
            h = 0.55 if row < 2 else 0.45
            bmesh_box(f"Win_{row}_{y:.1f}", (0.06, 0.20, h),
                      (main_w / 2 + 0.01, y, BZ + z_off + 0.10), m['window'])
            bmesh_box(f"WinF_{row}_{y:.1f}", (0.07, 0.22, 0.03),
                      (main_w / 2 + 0.02, y, BZ + z_off + h / 2 + 0.12), m['win_frame'])
            # Arched window top
            if row == 1:  # main floor gets arches
                bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.10, depth=0.06,
                                                    location=(main_w / 2 + 0.02, y, BZ + z_off + h + 0.10))
                wa = bpy.context.active_object
                wa.name = f"WinArch_{row}_{y:.1f}"
                wa.rotation_euler = (math.radians(90), 0, 0)
                wa.data.materials.append(m['stone_trim'])

    # Side windows
    for row in range(2):
        for x in [-1.2, -0.4, 0.4, 1.2]:
            bmesh_box(f"SWin_{row}_{x:.1f}", (0.20, 0.06, 0.50),
                      (x, -main_d / 2 - 0.01, BZ + 0.5 + row * 1.0), m['window'])

    # === Balustrade roofline ===
    bmesh_box("RoofSlab", (main_w + 0.08, main_d + 0.08, 0.10), (0, 0, BZ + main_h + 0.05), m['stone_light'])
    # Balustrade posts along front
    n_posts = 16
    for i in range(n_posts):
        py = -main_d / 2 + 0.15 + i * (main_d - 0.30) / (n_posts - 1)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.25,
                                            location=(main_w / 2 + 0.04, py, BZ + main_h + 0.225))
        bal = bpy.context.active_object
        bal.name = f"Baluster_{i}"
        bal.data.materials.append(m['stone_light'])
    # Balustrade rail
    bmesh_box("BalRail", (0.06, main_d - 0.10, 0.04),
              (main_w / 2 + 0.04, 0, BZ + main_h + 0.36), m['stone_light'])
    # Side balustrade
    for i in range(12):
        px = -main_w / 2 + 0.25 + i * (main_w - 0.50) / 11
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.25,
                                            location=(px, -main_d / 2 - 0.04, BZ + main_h + 0.225))
        bal = bpy.context.active_object
        bal.name = f"SBaluster_{i}"
        bal.data.materials.append(m['stone_light'])
    bmesh_box("SBalRail", (main_w - 0.20, 0.06, 0.04),
              (0, -main_d / 2 - 0.04, BZ + main_h + 0.36), m['stone_light'])

    # === Entrance portico with Ionic columns ===
    col_h = 2.6
    for y in [-0.60, -0.20, 0.20, 0.60]:
        _ionic_column(f"PorCol_{y:.1f}", (main_w / 2 + 0.50, y, BZ),
                      0.07, col_h, m['stone_light'])

    # Portico entablature
    bmesh_box("PorEnta", (0.50, 1.60, 0.12),
              (main_w / 2 + 0.50, 0, BZ + col_h + 0.25), m['stone_light'])

    # Pediment
    _pediment("PorPediment", 1.60, 0.50, 0.10,
              (main_w / 2 + 0.50, 0, BZ + col_h + 0.37), m['stone_light'])

    # Door
    bmesh_box("Door", (0.08, 0.80, 1.80), (main_w / 2 + 0.01, 0, BZ + 0.90), m['door'])

    # === Iron railings (fence in front) ===
    for i in range(16):
        fy = -2.0 + i * 0.26
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.60,
                                            location=(main_w / 2 + 1.20, fy, BZ + 0.15))
        bpy.context.active_object.name = f"IronRail_{i}"
        bpy.context.active_object.data.materials.append(m['iron'])
    # Rail bars
    bmesh_box("IronBarTop", (0.03, 4.0, 0.03), (main_w / 2 + 1.20, 0, BZ + 0.42), m['iron'])
    bmesh_box("IronBarBot", (0.03, 4.0, 0.03), (main_w / 2 + 1.20, 0, BZ + 0.10), m['iron'])

    # === Steps (grand) ===
    for i in range(7):
        bmesh_box(f"Step_{i}", (0.22, 2.0, 0.06),
                  (main_w / 2 + 0.75 + i * 0.22, 0, BZ - 0.04 - i * 0.05), m['stone_light'])

    # === Meander decorative band on facade ===
    _meander_strip("MeanderFacade", main_w - 0.20,
                   (0, -main_d / 2 - 0.02, BZ + main_h - 0.15), m['gold'], axis='x')

    # === Flag on roofline ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=1.0,
                                        location=(0, 0, BZ + main_h + 0.36 + 0.50))
    bpy.context.active_object.data.materials.append(m['iron'])
    fv = [(0.03, 0, BZ + main_h + 1.05), (0.45, 0.02, BZ + main_h + 1.00),
          (0.45, 0.01, BZ + main_h + 1.28), (0.03, 0, BZ + main_h + 1.30)]
    mesh_from_pydata("Banner", fv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# MODERN AGE -- Greek modernist (Cycladic influence)
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (7.0, 6.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.10
    bmesh_box("Found", (6.5, 5.5, 0.10), (0, 0, Z + 0.05), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Main white concrete volume (Cycladic cubic forms) ===
    main_w, main_d = 3.0, 2.4
    main_h = 2.8
    bmesh_box("MainBlock", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone_light'], bevel=0.02)

    # Flat roof
    bmesh_box("Roof", (main_w + 0.08, main_d + 0.08, 0.08), (0, 0, BZ + main_h + 0.04), m['stone_light'])

    # === Secondary geometric volume (offset, taller) ===
    sec_w, sec_d, sec_h = 1.8, 1.6, 3.4
    bmesh_box("SecBlock", (sec_w, sec_d, sec_h), (-1.2, 0.8, BZ + sec_h / 2), m['stone_light'], bevel=0.02)
    bmesh_box("SecRoof", (sec_w + 0.06, sec_d + 0.06, 0.06), (-1.2, 0.8, BZ + sec_h + 0.03), m['stone_light'])

    # === Tertiary lower volume (ground level) ===
    ter_w, ter_d, ter_h = 2.2, 1.4, 1.8
    bmesh_box("TerBlock", (ter_w, ter_d, ter_h), (1.5, -0.8, BZ + ter_h / 2), m['stone_light'], bevel=0.02)
    bmesh_box("TerRoof", (ter_w + 0.06, ter_d + 0.06, 0.06), (1.5, -0.8, BZ + ter_h + 0.03), m['stone_light'])

    # === Blue accents (Cycladic doors and window frames) ===
    # Large front windows with blue frames
    for y in [-0.60, 0.0, 0.60]:
        bmesh_box(f"FWin_{y:.1f}", (0.06, 0.35, 0.80),
                  (main_w / 2 + 0.01, y, BZ + main_h / 2 + 0.30), glass)
        # Blue frame
        bmesh_box(f"FWinFrame_{y:.1f}_T", (0.07, 0.38, 0.04),
                  (main_w / 2 + 0.02, y, BZ + main_h / 2 + 0.72), m['banner'])  # blue
        bmesh_box(f"FWinFrame_{y:.1f}_B", (0.07, 0.38, 0.04),
                  (main_w / 2 + 0.02, y, BZ + main_h / 2 - 0.12), m['banner'])
        bmesh_box(f"FWinFrame_{y:.1f}_L", (0.07, 0.04, 0.84),
                  (main_w / 2 + 0.02, y - 0.17, BZ + main_h / 2 + 0.30), m['banner'])
        bmesh_box(f"FWinFrame_{y:.1f}_R", (0.07, 0.04, 0.84),
                  (main_w / 2 + 0.02, y + 0.17, BZ + main_h / 2 + 0.30), m['banner'])

    # Secondary block windows
    for wy in [0.30, 0.80, 1.30]:
        bmesh_box(f"SWin_{wy:.1f}", (0.06, 0.28, 0.50),
                  (-1.2 - sec_w / 2 - 0.01, wy, BZ + sec_h / 2 + 0.40), glass)

    # Tertiary block large glass wall
    bmesh_box("TGlass", (0.06, ter_d - 0.30, ter_h - 0.30),
              (1.5 + ter_w / 2 + 0.01, -0.8, BZ + ter_h / 2 + 0.10), glass)

    # === Open terrace on main roof ===
    # Terrace railing (blue accented)
    for i in range(8):
        py = -main_d / 2 + 0.15 + i * (main_d - 0.30) / 7
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.35,
                                            location=(main_w / 2 + 0.02, py, BZ + main_h + 0.08 + 0.175))
        bpy.context.active_object.name = f"TerRail_{i}"
        bpy.context.active_object.data.materials.append(m['banner'])  # blue
    bmesh_box("TerRailBar", (0.04, main_d - 0.10, 0.03),
              (main_w / 2 + 0.02, 0, BZ + main_h + 0.40), m['banner'])

    # === Blue dome accent (small rooftop feature) ===
    _dome("BlueDome", (-1.2, 0.8, BZ + sec_h + 0.03), 0.30, 0.25, m['banner'],
          segments=12, rings=6)

    # === Blue door ===
    bmesh_box("Door", (0.06, 0.70, 1.80), (main_w / 2 + 0.01, 0, BZ + 0.90), m['banner'])

    # === Geometric forms -- pergola/shade structure ===
    pergola_x = main_w / 2 + 0.80
    for py in [-0.80, 0, 0.80]:
        # Slim metal posts
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=2.0,
                                            location=(pergola_x, py, BZ + 1.0))
        bpy.context.active_object.name = f"PergolaPost_{py:.1f}"
        bpy.context.active_object.data.materials.append(metal)
    # Horizontal beams
    bmesh_box("PergolaBeam1", (0.04, 2.0, 0.04), (pergola_x, 0, BZ + 2.0), metal)
    bmesh_box("PergolaBeam2", (0.60, 0.04, 0.04), (pergola_x, -0.40, BZ + 2.0), metal)
    bmesh_box("PergolaBeam3", (0.60, 0.04, 0.04), (pergola_x, 0.40, BZ + 2.0), metal)

    # === Planter boxes with bougainvillea suggestion ===
    for px, py in [(main_w / 2 + 0.50, -1.2), (main_w / 2 + 0.50, 1.2)]:
        bmesh_box(f"Planter_{py:.1f}", (0.35, 0.30, 0.30), (px, py, Z + 0.15), m['stone_light'])
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(px, py, Z + 0.40))
        plant = bpy.context.active_object
        plant.name = f"Plant_{py:.1f}"
        plant.scale = (1.2, 1, 0.7)
        plant.data.materials.append(m['banner'])  # purple/blue flowers

    # === Steps ===
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.22, 1.2, 0.06),
                  (main_w / 2 + 0.30 + i * 0.22, 0, BZ - 0.02 - i * 0.04), m['stone_light'])

    # === Paved courtyard ===
    bmesh_box("Court", (2.5, 4.0, 0.04), (main_w / 2 + 1.00, 0, Z + 0.06), m['stone_dark'])


# ============================================================
# DIGITAL AGE -- Futuristic Greek
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (7.0, 6.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.08
    bmesh_box("Found", (6.5, 5.5, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Stepped crepidoma platform (futuristic marble with LED edges) ===
    for i in range(3):
        step_w = 5.0 - i * 0.25
        step_d = 3.6 - i * 0.18
        bmesh_box(f"Crep_{i}", (step_w, step_d, 0.10),
                  (0, 0, BZ + i * 0.10 + 0.05), m['stone_light'], bevel=0.02)
        # LED edge on each step
        bmesh_box(f"CrepLED_{i}", (step_w + 0.02, step_d + 0.02, 0.02),
                  (0, 0, BZ + i * 0.10 + 0.10), m['gold'])

    PZ = BZ + 0.30  # platform top

    # === Glass cella (transparent inner sanctum) ===
    cella_w, cella_d, cella_h = 2.4, 1.6, 2.8
    bmesh_box("Cella", (cella_w, cella_d, cella_h), (0, 0, PZ + cella_h / 2), glass)
    # Metal frame structure
    for z in [PZ + 0.5, PZ + 1.4, PZ + 2.3]:
        bmesh_box(f"CellaFrame_{z:.1f}", (cella_w + 0.02, cella_d + 0.02, 0.04), (0, 0, z), metal)
    # Vertical frame edges
    for cx, cy in [(-cella_w / 2, -cella_d / 2), (cella_w / 2, -cella_d / 2),
                   (-cella_w / 2, cella_d / 2), (cella_w / 2, cella_d / 2)]:
        bmesh_box(f"CellaVert_{cx:.1f}_{cy:.1f}", (0.04, 0.04, cella_h), (cx, cy, PZ + cella_h / 2), metal)

    # === Floating marble columns (hovering above platform) ===
    # Columns don't touch the ground -- a 0.15 gap underneath
    float_gap = 0.15
    col_h = 2.2
    col_r = 0.08
    n_front = 8
    sty_w = 4.2
    sty_d = 2.8
    for i in range(n_front):
        cx = -sty_w / 2 + 0.30 + i * (sty_w - 0.60) / (n_front - 1)
        # Front row
        col_z = PZ + float_gap
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=col_r, depth=col_h,
                                            location=(cx, -sty_d / 2 + 0.20, col_z + col_h / 2))
        shaft = bpy.context.active_object
        shaft.name = f"FCol_{i}"
        shaft.data.materials.append(m['stone_light'])
        for p in shaft.data.polygons:
            p.use_smooth = True
        # Glowing base ring
        bmesh_prism(f"FColGlow_{i}", col_r + 0.03, 0.03, 14,
                    (cx, -sty_d / 2 + 0.20, col_z - 0.015), m['gold'])
        # Back row
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=col_r, depth=col_h,
                                            location=(cx, sty_d / 2 - 0.20, col_z + col_h / 2))
        shaft2 = bpy.context.active_object
        shaft2.name = f"BCol_{i}"
        shaft2.data.materials.append(m['stone_light'])
        for p in shaft2.data.polygons:
            p.use_smooth = True
        bmesh_prism(f"BColGlow_{i}", col_r + 0.03, 0.03, 14,
                    (cx, sty_d / 2 - 0.20, col_z - 0.015), m['gold'])

    # Side columns
    n_side = 4
    for i in range(n_side):
        cy = -sty_d / 2 + 0.55 + i * (sty_d - 1.10) / max(n_side - 1, 1)
        for sx, lbl in [(-sty_w / 2 + 0.20, "L"), (sty_w / 2 - 0.20, "R")]:
            col_z = PZ + float_gap
            bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=col_r, depth=col_h,
                                                location=(sx, cy, col_z + col_h / 2))
            shaft = bpy.context.active_object
            shaft.name = f"{lbl}Col_{i}"
            shaft.data.materials.append(m['stone_light'])
            for p in shaft.data.polygons:
                p.use_smooth = True
            bmesh_prism(f"{lbl}ColGlow_{i}", col_r + 0.03, 0.03, 14,
                        (sx, cy, col_z - 0.015), m['gold'])

    # === Holographic Parthenon outline (wireframe entablature) ===
    ent_z = PZ + float_gap + col_h + 0.05
    # Thin glowing gold wireframe around the entablature
    # Top frame
    bmesh_box("HoloEntF", (sty_w + 0.10, 0.03, 0.03), (0, -sty_d / 2 + 0.10, ent_z), m['gold'])
    bmesh_box("HoloEntB", (sty_w + 0.10, 0.03, 0.03), (0, sty_d / 2 - 0.10, ent_z), m['gold'])
    bmesh_box("HoloEntL", (0.03, sty_d - 0.10, 0.03), (-sty_w / 2 + 0.10, 0, ent_z), m['gold'])
    bmesh_box("HoloEntR", (0.03, sty_d - 0.10, 0.03), (sty_w / 2 - 0.10, 0, ent_z), m['gold'])

    # Holographic pediment outline (front)
    ped_z = ent_z + 0.05
    pv = [
        (-sty_w / 2, -sty_d / 2 + 0.08, ped_z),
        (sty_w / 2, -sty_d / 2 + 0.08, ped_z),
        (0, -sty_d / 2 + 0.08, ped_z + 0.80),
    ]
    mesh_from_pydata("HoloPedF", pv, [(0, 1, 2)], m['gold'])
    # Back pediment
    pvb = [
        (-sty_w / 2, sty_d / 2 - 0.08, ped_z),
        (sty_w / 2, sty_d / 2 - 0.08, ped_z),
        (0, sty_d / 2 - 0.08, ped_z + 0.80),
    ]
    mesh_from_pydata("HoloPedB", pvb, [(0, 1, 2)], m['gold'])

    # Ridge line (holographic)
    bmesh_box("HoloRidge", (0.02, sty_d - 0.20, 0.02), (0, 0, ped_z + 0.80), m['gold'])

    # === Energy beams between pillars (vertical light shafts) ===
    beam_positions = [(-sty_w / 2 + 0.20, -sty_d / 2 + 0.20),
                      (sty_w / 2 - 0.20, -sty_d / 2 + 0.20),
                      (-sty_w / 2 + 0.20, sty_d / 2 - 0.20),
                      (sty_w / 2 - 0.20, sty_d / 2 - 0.20)]
    for i, (bx, by) in enumerate(beam_positions):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.015, depth=col_h + 0.30,
                                            location=(bx, by, PZ + float_gap + col_h / 2))
        beam = bpy.context.active_object
        beam.name = f"EBeam_{i}"
        beam.data.materials.append(m['gold'])

    # Horizontal energy beams connecting corner columns at mid-height
    beam_h = PZ + float_gap + col_h / 2
    bmesh_box("HBeamF", (sty_w - 0.30, 0.02, 0.02), (0, -sty_d / 2 + 0.20, beam_h), m['gold'])
    bmesh_box("HBeamB", (sty_w - 0.30, 0.02, 0.02), (0, sty_d / 2 - 0.20, beam_h), m['gold'])
    bmesh_box("HBeamL", (0.02, sty_d - 0.30, 0.02), (-sty_w / 2 + 0.20, 0, beam_h), m['gold'])
    bmesh_box("HBeamR", (0.02, sty_d - 0.30, 0.02), (sty_w / 2 - 0.20, 0, beam_h), m['gold'])

    # === LED accent strips at platform base ===
    bmesh_box("BaseLED_F", (5.02, 0.04, 0.04), (0, -1.81, BZ + 0.02), m['gold'])
    bmesh_box("BaseLED_B", (5.02, 0.04, 0.04), (0, 1.81, BZ + 0.02), m['gold'])
    bmesh_box("BaseLED_L", (0.04, 3.62, 0.04), (-2.51, 0, BZ + 0.02), m['gold'])
    bmesh_box("BaseLED_R", (0.04, 3.62, 0.04), (2.51, 0, BZ + 0.02), m['gold'])

    # === Floating glass roof canopy ===
    canopy_z = ped_z + 0.90
    bmesh_box("GlassCanopy", (sty_w - 0.50, sty_d - 0.50, 0.04), (0, 0, canopy_z), glass)
    bmesh_box("CanopyFrame", (sty_w - 0.48, sty_d - 0.48, 0.02), (0, 0, canopy_z + 0.03), metal)

    # === Communication spire (modern antenna) ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=1.8,
                                        location=(0, 0, canopy_z + 0.04 + 0.90))
    bpy.context.active_object.name = "Spire"
    bpy.context.active_object.data.materials.append(metal)
    # LED rings on spire
    for z_off in [0.4, 0.9, 1.4]:
        bmesh_prism(f"SpireLED_{z_off:.1f}", 0.08, 0.04, 12,
                    (0, 0, canopy_z + 0.04 + z_off), m['gold'])

    # === Holographic meander pattern at base of cella ===
    _meander_strip("HoloMeander", cella_w, (0, -cella_d / 2 - 0.02, PZ), m['gold'], axis='x')

    # === Entrance ===
    bmesh_box("GlassDoor", (0.04, 0.80, 2.10), (cella_w / 2 + 0.01, 0, PZ + 1.05), glass)
    bmesh_box("DoorFrame", (0.05, 0.85, 0.04), (cella_w / 2 + 0.02, 0, PZ + 2.12), metal)


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


def build_town_center_greeks(materials, age='medieval'):
    """Build a Greeks nation Town Center with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
