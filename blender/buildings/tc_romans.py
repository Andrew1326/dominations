"""
Romans Nation Town Center — Roman/Italian architecture per age.

3x3 tile building, ground plane ~4.5-6.5 depending on age.

Stone:         Primitive Latin hut (Casa Romuli style) — oval thatched hut
               with wattle walls, central hearth post, small walled yard
Bronze:        Etruscan-influenced temple-house — stone podium, terracotta roof,
               wide columns at entrance, small altar
Iron:          Early Republican villa — atrium with impluvium (rain pool),
               tiled roof, stone walls, small peristyle garden
Classical:     Grand Roman forum complex — marble temple with Corinthian columns,
               triumphal arch, basilica with apse, tiled forum floor
Medieval:      Byzantine/Romanesque palazzo — tall stone tower (campanile),
               rounded arches, mosaic-decorated facade, domed chapel
Gunpowder:     Renaissance palazzo — rusticated stone base, arched loggia,
               symmetrical facade, clock tower, courtyard
Enlightenment: Baroque Roman palazzo — curved facade, ornate pilasters,
               grand staircase, domed roof, fountain courtyard
Industrial:    Neoclassical Italian government building — tall columned portico,
               triangular pediment, dome, iron balconies
Modern:        Italian rationalist/Fascist architecture — stark white marble,
               massive columns, angular geometry, relief panels
Digital:       Futuristic Roman — glass and marble fusion, holographic columns,
               floating aqueduct arches, LED mosaics
"""

import bpy
import bmesh
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# ── helpers ────────────────────────────────────────────────────
def _roman_column(prefix, cx, cy, base_z, height, radius, material,
                  capital_mat=None, segments=12, fluted=False):
    """
    Classical Roman column with base torus, shaft, and capital.
    Returns the top z coordinate for stacking elements above.
    """
    cap_mat = capital_mat or material
    # Base disk
    bmesh_prism(f"{prefix}_Base", radius + 0.04, 0.06, segments,
                (cx, cy, base_z), cap_mat)
    # Shaft
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius,
                                        depth=height,
                                        location=(cx, cy, base_z + 0.06 + height / 2))
    shaft = bpy.context.active_object
    shaft.name = f"{prefix}_Shaft"
    shaft.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    # Capital (wider disk + abacus)
    cap_z = base_z + 0.06 + height
    bmesh_prism(f"{prefix}_CapRing", radius + 0.03, 0.05, segments,
                (cx, cy, cap_z), cap_mat)
    bmesh_box(f"{prefix}_Abacus", (radius * 2 + 0.10, radius * 2 + 0.10, 0.04),
              (cx, cy, cap_z + 0.07), cap_mat)
    return cap_z + 0.09


def _roman_arch(prefix, cx, cy, base_z, width, height, depth, material,
                keystone_mat=None, segments=12):
    """
    Roman semicircular arch.  Two pillars with a semicircular vault between them.
    """
    ks_mat = keystone_mat or material
    hw = width / 2
    hd = depth / 2
    pillar_h = height - hw  # height below the arch spring line

    # Two pillars
    bmesh_box(f"{prefix}_PillarL", (depth, 0.18, pillar_h),
              (cx, cy - hw, base_z + pillar_h / 2), material)
    bmesh_box(f"{prefix}_PillarR", (depth, 0.18, pillar_h),
              (cx, cy + hw, base_z + pillar_h / 2), material)

    # Arch curve (semicircular, built from wedge segments)
    spring_z = base_z + pillar_h
    arch_r = hw
    verts = []
    faces = []
    for i in range(segments + 1):
        a = math.pi * i / segments
        y_off = -arch_r * math.cos(a)
        z_off = arch_r * math.sin(a)
        # inner edge
        verts.append((cx - hd, cy + y_off, spring_z + z_off))
        # outer edge
        verts.append((cx + hd, cy + y_off, spring_z + z_off))
    for i in range(segments):
        i0 = i * 2
        faces.append((i0, i0 + 1, i0 + 3, i0 + 2))
    # close the underside and top
    obj = mesh_from_pydata(f"{prefix}_Arch", verts, faces, material)
    for p in obj.data.polygons:
        p.use_smooth = True

    # Keystone (decorative block at top of arch)
    bmesh_box(f"{prefix}_Keystone", (depth + 0.04, 0.12, 0.12),
              (cx, cy, spring_z + arch_r), ks_mat)

    return spring_z + arch_r


def _dome(prefix, cx, cy, base_z, radius, height, material, segments=16,
          rings=8):
    """
    Hemispherical dome built from rings of vertices.
    """
    verts = []
    faces = []
    # Bottom ring at base_z
    for i in range(segments):
        a = 2 * math.pi * i / segments
        verts.append((cx + radius * math.cos(a),
                      cy + radius * math.sin(a),
                      base_z))
    # Intermediate rings
    for r in range(1, rings):
        phi = (math.pi / 2) * r / rings
        ring_r = radius * math.cos(phi)
        ring_z = base_z + height * math.sin(phi)
        for i in range(segments):
            a = 2 * math.pi * i / segments
            verts.append((cx + ring_r * math.cos(a),
                          cy + ring_r * math.sin(a),
                          ring_z))
    # Apex
    apex_idx = len(verts)
    verts.append((cx, cy, base_z + height))

    # Faces between rings
    for r in range(rings - 1):
        for i in range(segments):
            j = (i + 1) % segments
            i0 = r * segments + i
            i1 = r * segments + j
            i2 = (r + 1) * segments + j
            i3 = (r + 1) * segments + i
            faces.append((i0, i1, i2, i3))
    # Top cap triangles
    last_ring = (rings - 1) * segments
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((last_ring + i, last_ring + j, apex_idx))
    # Bottom face
    bottom = list(range(segments))
    faces.append(tuple(reversed(bottom)))

    obj = mesh_from_pydata(f"{prefix}_Dome", verts, faces, material)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def _aqueduct_arch(prefix, cx, cy, base_z, width, height, thickness,
                   material, segments=10):
    """
    Repeating aqueduct-style arch segment — two piers and a rounded top.
    """
    hw = width / 2
    pier_w = thickness
    pier_h = height * 0.55

    # Piers
    bmesh_box(f"{prefix}_PierL", (thickness, pier_w, pier_h),
              (cx, cy - hw + pier_w / 2, base_z + pier_h / 2), material)
    bmesh_box(f"{prefix}_PierR", (thickness, pier_w, pier_h),
              (cx, cy + hw - pier_w / 2, base_z + pier_h / 2), material)

    # Arch span
    spring_z = base_z + pier_h
    span = width - 2 * pier_w
    arch_r = span / 2
    ht = thickness / 2
    verts = []
    faces = []
    for i in range(segments + 1):
        a = math.pi * i / segments
        y_off = -arch_r * math.cos(a)
        z_off = arch_r * math.sin(a)
        verts.append((cx - ht, cy + y_off, spring_z + z_off))
        verts.append((cx + ht, cy + y_off, spring_z + z_off))
    for i in range(segments):
        i0 = i * 2
        faces.append((i0, i0 + 1, i0 + 3, i0 + 2))
    obj = mesh_from_pydata(f"{prefix}_ArchSpan", verts, faces, material)
    for p in obj.data.polygons:
        p.use_smooth = True

    # Top walkway
    top_z = spring_z + arch_r
    bmesh_box(f"{prefix}_Top", (thickness + 0.04, width, 0.06),
              (cx, cy, top_z + 0.03), material)


def _pediment(prefix, cx, cy, base_z, width, depth, height, material):
    """
    Triangular pediment (tympanum) — classical Roman temple crown.
    """
    hw = width / 2
    hd = depth / 2
    verts = [
        (cx - hd, cy - hw, base_z), (cx + hd, cy - hw, base_z),
        (cx + hd, cy + hw, base_z), (cx - hd, cy + hw, base_z),
        (cx - hd, cy, base_z + height), (cx + hd, cy, base_z + height),
    ]
    faces = [
        (0, 1, 5, 4), (2, 3, 4, 5), (0, 3, 4), (1, 2, 5),
        (0, 1, 2, 3),
    ]
    obj = mesh_from_pydata(f"{prefix}_Pediment", verts, faces, material)
    return obj


# ============================================================
# STONE AGE — Primitive Latin hut (Casa Romuli)
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (5.0, 5.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Oval wattle-and-daub main hut (Casa Romuli) ===
    # Low stone foundation ring (oval)
    bmesh_prism("HutFoundation", 1.5, 0.12, 16, (0, 0, Z), m['stone_dark'])

    # Wattle walls (oval approximated by stretched prism)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.4, depth=1.3,
                                        location=(0, 0, Z + 0.12 + 0.65))
    walls = bpy.context.active_object
    walls.name = "HutWalls"
    walls.scale = (1.2, 1.0, 1.0)
    walls.data.materials.append(m['stone'])

    # Thatched conical roof (tall, steep pitch)
    bmesh_cone("HutRoof", 2.0, 2.4, 16, (0, 0, Z + 1.42), m['roof'])

    # Smoke hole at apex
    bmesh_prism("SmokeHole", 0.15, 0.10, 8, (0, 0, Z + 3.78), m['wood'])

    # Ridge poles radiating from center
    for i in range(8):
        a = (2 * math.pi * i) / 8
        ex, ey = 1.85 * math.cos(a), 1.55 * math.sin(a)
        sv = [(ex, ey, Z + 1.42), (0, 0, Z + 3.85)]
        mesh_from_pydata(f"Ridge_{i}", sv, [], m['wood_dark'])

    # Central hearth post (thick pole in center)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.10, depth=3.5,
                                        location=(0, 0, Z + 1.75))
    post = bpy.context.active_object
    post.name = "HearthPost"
    post.data.materials.append(m['wood'])

    # Entrance (low doorway facing front)
    bmesh_box("Entrance", (0.65, 0.50, 0.55), (1.65, 0, Z + 0.40), m['roof'])
    bmesh_box("EntrDoor", (0.06, 0.38, 0.50), (1.98, 0, Z + 0.37), m['door'])

    # Support ring posts inside
    for i in range(6):
        a = (2 * math.pi * i) / 6 + 0.3
        px, py = 0.90 * math.cos(a), 0.75 * math.sin(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=1.3,
                                            location=(px, py, Z + 0.77))
        pole = bpy.context.active_object
        pole.name = f"IntPost_{i}"
        pole.data.materials.append(m['wood'])

    # === Stone hearth circle (outdoor) ===
    bmesh_prism("Hearth", 0.35, 0.08, 10, (1.8, -1.3, Z + 0.04), m['stone_dark'])
    for i in range(8):
        a = (2 * math.pi * i) / 8
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.06,
            location=(1.8 + 0.30 * math.cos(a), -1.3 + 0.30 * math.sin(a), Z + 0.06))
        st = bpy.context.active_object
        st.name = f"HearthStone_{i}"
        st.data.materials.append(m['stone'])

    # === Walled yard (low rough stone wall) ===
    # Front wall segments
    for i in range(6):
        y = -1.3 + i * 0.52
        bmesh_box(f"YardWall_{i}", (0.20, 0.48, 0.50),
                  (2.2, y, Z + 0.25), m['stone_dark'])

    # Side walls
    for i in range(5):
        x = 0.3 + i * 0.45
        bmesh_box(f"YardWallR_{i}", (0.42, 0.18, 0.45),
                  (x, -1.6, Z + 0.225), m['stone_dark'])
        bmesh_box(f"YardWallL_{i}", (0.42, 0.18, 0.45),
                  (x, 1.6, Z + 0.225), m['stone_dark'])

    # === Small secondary hut ===
    bmesh_prism("Hut2Base", 0.65, 0.10, 10, (-1.6, 1.1, Z), m['stone_dark'])
    bmesh_prism("Hut2Wall", 0.60, 0.85, 10, (-1.6, 1.1, Z + 0.10), m['stone'])
    bmesh_cone("Hut2Roof", 0.80, 1.0, 10, (-1.6, 1.1, Z + 0.95), m['roof'])

    # === Grain storage (clay pots) ===
    for i, (px, py) in enumerate([(-1.8, -0.8), (-1.9, -0.3), (-1.7, -1.3)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(px, py, Z + 0.10))
        jar = bpy.context.active_object
        jar.name = f"GrainJar_{i}"
        jar.scale = (1, 1, 1.3)
        jar.data.materials.append(m['roof_edge'])

    # Drying rack
    for dy in [-0.25, 0.25]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.035, depth=1.0,
                                            location=(-0.8, -1.6 + dy, Z + 0.50))
        bpy.context.active_object.name = f"DryPole_{dy:.2f}"
        bpy.context.active_object.data.materials.append(m['wood'])
    bmesh_box("DryBar", (0.04, 0.55, 0.04), (-0.8, -1.6, Z + 1.0), m['wood'])


# ============================================================
# BRONZE AGE — Etruscan-influenced temple-house
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (5.0, 5.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Raised stone podium (high platform, Etruscan style) ===
    bmesh_box("Podium", (3.2, 2.8, 0.55), (0, 0, Z + 0.275), m['stone_dark'], bevel=0.04)
    bmesh_box("PodiumTop", (3.3, 2.9, 0.06), (0, 0, Z + 0.58), m['stone_trim'])

    BZ = Z + 0.55

    # === Front steps (wide, ceremonial) ===
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.18, 2.2, 0.08),
                  (1.60 + 0.20 + i * 0.20, 0, BZ - 0.04 - i * 0.10), m['stone'])

    # === Main temple-house (cella) ===
    cella_w = 2.4
    cella_d = 2.0
    cella_h = 2.2
    # Walls
    bmesh_box("CellaWallB", (0.18, cella_d, cella_h),
              (-cella_w / 2, 0, BZ + cella_h / 2), m['stone'], bevel=0.02)
    bmesh_box("CellaWallR", (cella_w, 0.18, cella_h),
              (0, -cella_d / 2, BZ + cella_h / 2), m['stone'], bevel=0.02)
    bmesh_box("CellaWallL", (cella_w, 0.18, cella_h),
              (0, cella_d / 2, BZ + cella_h / 2), m['stone'], bevel=0.02)

    # === Front colonnade (wide Tuscan columns — Etruscan style) ===
    col_h = 2.0
    col_r = 0.10
    for i, cy in enumerate([-0.70, 0, 0.70]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=col_r, depth=col_h,
                                            location=(0.90, cy, BZ + col_h / 2))
        col = bpy.context.active_object
        col.name = f"FrontCol_{i}"
        col.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        # Capitals (wide, cushion-like)
        bmesh_prism(f"FrontCap_{i}", col_r + 0.06, 0.08, 10,
                    (0.90, cy, BZ + col_h), m['stone_trim'])
        # Base
        bmesh_prism(f"FrontBase_{i}", col_r + 0.04, 0.06, 10,
                    (0.90, cy, BZ), m['stone_trim'])

    # Entablature (beam above columns)
    bmesh_box("Entablature", (0.22, cella_d + 0.20, 0.14),
              (0.90, 0, BZ + col_h + 0.15), m['wood_dark'])

    # === Terracotta hip roof ===
    pyramid_roof("Roof", w=cella_w + 0.30, d=cella_d + 0.30, h=1.2,
                 overhang=0.25, origin=(0, 0, BZ + cella_h), material=m['roof'])
    # Ridge decoration
    bmesh_box("Ridge", (cella_w * 0.3, 0.06, 0.06),
              (0, 0, BZ + cella_h + 1.18), m['roof_edge'])

    # Acroterion (decorative finial at peak)
    bmesh_cone("Acroterion", 0.08, 0.25, 8, (0, 0, BZ + cella_h + 1.20), m['gold'])

    # === Small altar in front ===
    alt_x = 1.80
    bmesh_box("AltarBase", (0.45, 0.35, 0.10), (alt_x, 0, Z + 0.05), m['stone_dark'])
    bmesh_box("AltarBody", (0.35, 0.28, 0.55), (alt_x, 0, Z + 0.375), m['stone'])
    bmesh_box("AltarTop", (0.40, 0.32, 0.06), (alt_x, 0, Z + 0.68), m['stone_trim'])
    # Offering bowl
    bmesh_prism("OfferBowl", 0.08, 0.05, 8, (alt_x, 0, Z + 0.71), m['gold'])

    # === Side walls forming enclosed temenos (sacred precinct) ===
    for y_sign, label in [(-1, "R"), (1, "L")]:
        bmesh_box(f"Temenos_{label}", (2.8, 0.14, 0.70),
                  (0.3, y_sign * 2.0, Z + 0.35), m['stone_dark'])

    # Gate posts at temenos entrance
    for y_sign in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.07, depth=1.2,
                                            location=(1.75, y_sign * 2.0, Z + 0.60))
        bpy.context.active_object.name = f"GatePost_{y_sign}"
        bpy.context.active_object.data.materials.append(m['wood'])

    # === Terracotta antefixes along roofline ===
    for i in range(5):
        y = -0.8 + i * 0.4
        bmesh_box(f"Antefix_{i}", (0.06, 0.08, 0.12),
                  (cella_w / 2 + 0.15, y, BZ + cella_h + 0.06), m['roof_edge'])

    # Banner pole
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.8,
                                        location=(0, 0, BZ + cella_h + 1.50))
    bpy.context.active_object.data.materials.append(m['wood'])
    bvz = BZ + cella_h + 1.60
    bv = [(0.04, 0, bvz), (0.40, 0.03, bvz - 0.04),
          (0.40, 0.02, bvz + 0.22), (0.04, 0, bvz + 0.20)]
    mesh_from_pydata("Banner", bv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# IRON AGE — Early Republican villa with atrium
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation (raised stone platform) ===
    bmesh_box("Foundation", (5.0, 4.4, 0.20), (0, 0, Z + 0.10), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.20

    # === Main building — solid rectangular domus ===
    main_w = 3.6
    main_d = 3.2
    wall_h = 2.6
    bmesh_box("MainBody", (main_w, main_d, wall_h),
              (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.03)

    # === Proper pitched roof (hipped, complete coverage) ===
    roof_z = BZ + wall_h
    pyramid_roof("MainRoof", w=main_w, d=main_d, h=1.0, overhang=0.25,
                 origin=(0, 0, roof_z), material=m['roof'])
    # Roof edge trim
    bmesh_box("RoofEdgeF", (0.06, main_d + 0.50, 0.08),
              (main_w / 2 + 0.25, 0, roof_z + 0.04), m['roof_edge'])
    bmesh_box("RoofEdgeB", (0.06, main_d + 0.50, 0.08),
              (-main_w / 2 - 0.25, 0, roof_z + 0.04), m['roof_edge'])
    bmesh_box("RoofEdgeL", (main_w + 0.50, 0.06, 0.08),
              (0, main_d / 2 + 0.25, roof_z + 0.04), m['roof_edge'])
    bmesh_box("RoofEdgeR", (main_w + 0.50, 0.06, 0.08),
              (0, -main_d / 2 - 0.25, roof_z + 0.04), m['roof_edge'])

    # === Front entrance portico with columns ===
    portico_x = main_w / 2
    portico_depth = 0.8
    col_h = 2.4
    col_r = 0.07
    # Portico roof (flat slab extending from main roof)
    bmesh_box("PorticoRoof", (portico_depth + 0.10, 2.0, 0.10),
              (portico_x + portico_depth / 2, 0, BZ + col_h + 0.05), m['roof'])
    bmesh_box("PorticoBeam", (portico_depth + 0.12, 2.02, 0.06),
              (portico_x + portico_depth / 2, 0, BZ + col_h), m['stone_trim'])

    # Four Tuscan columns at entrance
    for i, cy in enumerate([-0.70, -0.25, 0.25, 0.70]):
        _roman_column(f"PortCol_{i}", portico_x + portico_depth, cy,
                      BZ, col_h, col_r, m['stone_light'], m['stone_trim'])

    # === Entrance door ===
    bmesh_box("Door", (0.08, 0.60, 1.70),
              (main_w / 2 + 0.01, 0, BZ + 0.85), m['door'])
    bmesh_box("DoorFrameT", (0.10, 0.70, 0.08),
              (main_w / 2 + 0.02, 0, BZ + 1.74), m['stone_trim'])
    bmesh_box("DoorFrameL", (0.10, 0.06, 1.70),
              (main_w / 2 + 0.02, -0.33, BZ + 0.85), m['stone_trim'])
    bmesh_box("DoorFrameR", (0.10, 0.06, 1.70),
              (main_w / 2 + 0.02, 0.33, BZ + 0.85), m['stone_trim'])

    # === Windows on front facade ===
    for cy in [-1.10, 1.10]:
        bmesh_box(f"FWin_{cy:.1f}", (0.06, 0.30, 0.50),
                  (main_w / 2 + 0.02, cy, BZ + 1.50), m['window'])
        bmesh_box(f"FWinFrame_{cy:.1f}", (0.07, 0.34, 0.06),
                  (main_w / 2 + 0.03, cy, BZ + 1.77), m['stone_trim'])

    # === Side windows ===
    for i in range(3):
        wx = -1.0 + i * 1.0
        bmesh_box(f"SWin_{i}", (0.30, 0.06, 0.45),
                  (wx, -main_d / 2 - 0.02, BZ + 1.55), m['window'])
        bmesh_box(f"SWinFrame_{i}", (0.34, 0.07, 0.05),
                  (wx, -main_d / 2 - 0.03, BZ + 1.80), m['stone_trim'])

    # === Decorative cornice band ===
    bmesh_box("CorniceF", (0.06, main_d + 0.04, 0.10),
              (main_w / 2 + 0.01, 0, BZ + wall_h - 0.05), m['stone_trim'])
    bmesh_box("CorniceB", (0.06, main_d + 0.04, 0.10),
              (-main_w / 2 - 0.01, 0, BZ + wall_h - 0.05), m['stone_trim'])
    bmesh_box("CorniceL", (main_w + 0.04, 0.06, 0.10),
              (0, main_d / 2 + 0.01, BZ + wall_h - 0.05), m['stone_trim'])
    bmesh_box("CorniceR", (main_w + 0.04, 0.06, 0.10),
              (0, -main_d / 2 - 0.01, BZ + wall_h - 0.05), m['stone_trim'])

    # === Side wing (lower, peristyle garden) ===
    wing_w = 1.8
    wing_d = 2.4
    wing_h = 1.8
    WX = -main_w / 2 - wing_w / 2 + 0.10
    bmesh_box("Wing", (wing_w, wing_d, wing_h),
              (WX, 0, BZ + wing_h / 2), m['stone'], bevel=0.02)
    pyramid_roof("WingRoof", w=wing_w, d=wing_d, h=0.6, overhang=0.15,
                 origin=(WX, 0, BZ + wing_h), material=m['roof'])

    # Wing colonnade (front face)
    for i in range(3):
        cy = -0.70 + i * 0.70
        _roman_column(f"WingCol_{i}", WX + wing_w / 2 + 0.01, cy,
                      BZ, wing_h - 0.10, 0.05, m['stone_light'], m['stone_trim'])

    # Wing door
    bmesh_box("WingDoor", (0.06, 0.40, 1.20),
              (WX + wing_w / 2 + 0.01, 0, BZ + 0.60), m['door'])

    # === Courtyard wall (connecting main to wing) ===
    yard_front_x = main_w / 2 + 0.10
    bmesh_box("YardWallF", (0.12, 0.12, 1.2),
              (yard_front_x, -main_d / 2 + 0.10, BZ + 0.60), m['stone'])
    bmesh_box("YardWallSide", (main_w + wing_w - 0.20, 0.12, 1.2),
              (-0.40, -main_d / 2 - 0.30, BZ + 0.60), m['stone'])

    # === Impluvium basin (visible in courtyard, decorative) ===
    bmesh_prism("ImpluviumRim", 0.30, 0.10, 10,
                (WX, 0, BZ + 0.05), m['stone_trim'])
    bmesh_prism("ImpluviumPool", 0.24, 0.04, 10,
                (WX, 0, BZ + 0.02), m['stone_dark'])

    # === Steps at main entrance ===
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.18, 1.6, 0.06),
                  (portico_x + portico_depth + 0.15 + i * 0.20, 0, BZ - 0.04 - i * 0.06),
                  m['stone'])

    # === Banner ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.8,
                                        location=(0, 0, roof_z + 1.05 + 0.40))
    bpy.context.active_object.data.materials.append(m['wood'])
    bvz = roof_z + 1.05 + 0.55
    bv = [(0.04, 0, bvz), (0.45, 0.03, bvz - 0.04),
          (0.45, 0.02, bvz + 0.22), (0.04, 0, bvz + 0.20)]
    mesh_from_pydata("Banner", bv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# CLASSICAL AGE — Grand Roman forum complex
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (6.0, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Forum floor (tiled stone plaza) ===
    bmesh_box("ForumFloor", (5.5, 5.2, 0.12), (0, 0, Z + 0.06), m['stone'], bevel=0.03)
    # Tile grid lines
    for i in range(8):
        x = -2.4 + i * 0.70
        bmesh_box(f"GridX_{i}", (0.02, 5.2, 0.02), (x, 0, Z + 0.13), m['stone_dark'])
    for j in range(7):
        y = -2.2 + j * 0.73
        bmesh_box(f"GridY_{j}", (5.5, 0.02, 0.02), (0, y, Z + 0.13), m['stone_dark'])

    BZ = Z + 0.12

    # === Main Temple (marble, with Corinthian columns) ===
    # High podium
    tmpl_x = -0.8
    bmesh_box("TemplePodium", (2.4, 2.2, 0.45), (tmpl_x, 0, BZ + 0.225), m['stone_light'], bevel=0.04)
    bmesh_box("PodiumMold", (2.5, 2.3, 0.06), (tmpl_x, 0, BZ + 0.48), m['stone_trim'])

    TZ = BZ + 0.45
    temple_h = 3.0

    # Cella (inner sanctum) walls
    bmesh_box("CellaBack", (0.18, 1.8, temple_h), (tmpl_x - 1.0, 0, TZ + temple_h / 2), m['stone_light'])
    bmesh_box("CellaR", (1.6, 0.16, temple_h), (tmpl_x - 0.20, -0.90, TZ + temple_h / 2), m['stone_light'])
    bmesh_box("CellaL", (1.6, 0.16, temple_h), (tmpl_x - 0.20, 0.90, TZ + temple_h / 2), m['stone_light'])

    # Front colonnade (6 Corinthian columns)
    col_positions = [-0.75, -0.45, -0.15, 0.15, 0.45, 0.75]
    for i, cy in enumerate(col_positions):
        _roman_column(f"TempleCol_{i}", tmpl_x + 0.90, cy, TZ,
                      height=2.6, radius=0.08, material=m['stone_light'],
                      capital_mat=m['stone_trim'])

    # Entablature
    bmesh_box("Entablature", (0.30, 2.2, 0.18),
              (tmpl_x + 0.90, 0, TZ + 2.78), m['stone_trim'])

    # Triangular pediment
    _pediment("Temple", tmpl_x + 0.90, 0, TZ + 2.96, 2.2, 0.30, 0.65, m['stone_light'])

    # Pediment decoration (small relief in center)
    bmesh_box("PedRelief", (0.06, 0.40, 0.25),
              (tmpl_x + 0.92, 0, TZ + 3.15), m['gold'])

    # Temple roof behind pediment
    pyramid_roof("TempleRoof", w=2.0, d=2.0, h=0.70, overhang=0.15,
                 origin=(tmpl_x, 0, TZ + temple_h), material=m['roof'])

    # Temple steps
    for i in range(6):
        bmesh_box(f"TempleStep_{i}", (0.16, 2.0, 0.06),
                  (tmpl_x + 1.20 + i * 0.18, 0, TZ - 0.04 - i * 0.07), m['stone'])

    # === Triumphal Arch ===
    arch_x = 2.2
    _roman_arch("TriumphArch", arch_x, 0, BZ, width=1.4, height=3.2,
                depth=0.55, material=m['stone_light'], keystone_mat=m['gold'])

    # Attic (inscription block above arch)
    arch_top = BZ + 3.2
    bmesh_box("ArchAttic", (0.60, 1.6, 0.50), (arch_x, 0, arch_top + 0.25), m['stone_light'])
    bmesh_box("ArchInscr", (0.04, 1.0, 0.25), (arch_x + 0.31, 0, arch_top + 0.25), m['stone_trim'])

    # Decorative reliefs on arch piers
    for y_sign in [-1, 1]:
        bmesh_box(f"ArchRelief_{y_sign}", (0.04, 0.20, 0.60),
                  (arch_x + 0.28, y_sign * 0.55, BZ + 0.90), m['gold'])

    # === Basilica with apse (side building) ===
    bas_y = -1.8
    bas_w = 2.0
    bas_d = 1.2
    bas_h = 2.6
    bmesh_box("BasilicaBody", (bas_w, bas_d, bas_h),
              (0, bas_y, BZ + bas_h / 2), m['stone'], bevel=0.02)

    # Apse (semicircular end)
    bmesh_prism("Apse", bas_d / 2, bas_h, 12,
                (-bas_w / 2 - 0.01, bas_y, BZ), m['stone'])
    # Cut appearance — roof over apse
    bmesh_prism("ApseRoof", bas_d / 2 + 0.10, 0.08, 12,
                (-bas_w / 2 - 0.01, bas_y, BZ + bas_h), m['roof'])

    # Basilica roof
    bmesh_box("BasilicaRoof", (bas_w + 0.10, bas_d + 0.10, 0.08),
              (0, bas_y, BZ + bas_h + 0.04), m['roof'])

    # Basilica columns (along front face)
    for i in range(4):
        cx = -0.65 + i * 0.44
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.06, depth=2.2,
                                            location=(cx, bas_y + bas_d / 2 + 0.01, BZ + 1.1))
        col = bpy.context.active_object
        col.name = f"BasCol_{i}"
        col.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()

    # === Decorative statue on plinth ===
    stat_x, stat_y = 1.5, 1.5
    bmesh_box("StatuePlinth", (0.30, 0.30, 0.60), (stat_x, stat_y, BZ + 0.30), m['stone_dark'])
    bmesh_box("StatueBody", (0.16, 0.14, 0.55), (stat_x, stat_y, BZ + 0.875), m['gold'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(stat_x, stat_y, BZ + 1.20))
    bpy.context.active_object.name = "StatueHead"
    bpy.context.active_object.data.materials.append(m['gold'])

    # === Forum fountain ===
    bmesh_prism("Fountain", 0.35, 0.12, 12, (1.5, -0.8, BZ + 0.06), m['stone_light'])
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=0.45,
                                        location=(1.5, -0.8, BZ + 0.35))
    bpy.context.active_object.name = "FountainSpout"
    bpy.context.active_object.data.materials.append(m['stone_trim'])

    # Banner on temple
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.9,
                                        location=(tmpl_x, 0, TZ + temple_h + 0.70 + 0.45))
    bpy.context.active_object.data.materials.append(m['wood'])
    bvz = TZ + temple_h + 1.20
    bv = [(tmpl_x + 0.04, 0, bvz), (tmpl_x + 0.45, 0.03, bvz - 0.04),
          (tmpl_x + 0.45, 0.02, bvz + 0.25), (tmpl_x + 0.04, 0, bvz + 0.22)]
    mesh_from_pydata("Banner", bv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# MEDIEVAL AGE — Byzantine/Romanesque palazzo
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation ===
    bmesh_box("Foundation", (5.0, 4.8, 0.20), (0, 0, Z + 0.10), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.20

    # === Main palazzo building ===
    palazzo_w = 3.0
    palazzo_d = 2.4
    palazzo_h = 3.2
    bmesh_box("Palazzo", (palazzo_w, palazzo_d, palazzo_h),
              (0, 0, BZ + palazzo_h / 2), m['stone'], bevel=0.03)

    # === Rounded arches along front facade (Romanesque arcade) ===
    for i in range(4):
        y = -0.90 + i * 0.60
        _roman_arch(f"FacadeArch_{i}", palazzo_w / 2 + 0.02, y, BZ,
                    width=0.45, height=1.5, depth=0.12,
                    material=m['stone_light'], keystone_mat=m['stone_trim'],
                    segments=8)

    # Window arches on upper level
    for i in range(4):
        y = -0.90 + i * 0.60
        _roman_arch(f"UpperArch_{i}", palazzo_w / 2 + 0.02, y, BZ + 1.8,
                    width=0.35, height=1.0, depth=0.08,
                    material=m['stone_light'], keystone_mat=m['stone_trim'],
                    segments=8)
        # Window glass
        bmesh_box(f"Window_{i}", (0.04, 0.28, 0.50),
                  (palazzo_w / 2 + 0.03, y, BZ + 2.15), m['window'])

    # Mosaic-decorated band (colored strip along facade)
    bmesh_box("MosaicBand", (palazzo_w + 0.04, 0.04, 0.15),
              (0, -palazzo_d / 2 - 0.01, BZ + palazzo_h - 0.40), m['gold'])
    bmesh_box("MosaicBand2", (0.04, palazzo_d + 0.04, 0.15),
              (palazzo_w / 2 + 0.01, 0, BZ + palazzo_h - 0.40), m['gold'])

    # Cornice
    bmesh_box("Cornice", (palazzo_w + 0.10, palazzo_d + 0.10, 0.08),
              (0, 0, BZ + palazzo_h + 0.04), m['stone_trim'])

    # === Campanile (tall bell tower) ===
    tower_x, tower_y = -1.8, -1.5
    tower_w = 0.80
    tower_h = 5.5
    bmesh_box("TowerBase", (tower_w + 0.10, tower_w + 0.10, 0.15),
              (tower_x, tower_y, BZ + 0.075), m['stone_dark'])
    bmesh_box("Tower", (tower_w, tower_w, tower_h),
              (tower_x, tower_y, BZ + tower_h / 2), m['stone'], bevel=0.02)

    # Tower levels (horizontal bands)
    for i in range(5):
        z = BZ + 1.0 + i * 1.0
        bmesh_box(f"TowerBand_{i}", (tower_w + 0.04, tower_w + 0.04, 0.05),
                  (tower_x, tower_y, z), m['stone_trim'])

    # Belfry openings (arched windows at top)
    for side_dx, side_dy, rot in [(tower_w / 2 + 0.01, 0, 0),
                                   (0, tower_w / 2 + 0.01, 1)]:
        belf_z = BZ + tower_h - 1.0
        bmesh_box(f"Belfry_{side_dx:.1f}_{side_dy:.1f}",
                  (0.04, 0.25, 0.50),
                  (tower_x + side_dx, tower_y + side_dy, belf_z), m['stone_dark'])

    # Tower pyramidal roof
    pyramid_roof("TowerRoof", w=tower_w, d=tower_w, h=1.0, overhang=0.08,
                 origin=(tower_x, tower_y, BZ + tower_h), material=m['roof'])

    # Cross finial
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.30,
                                        location=(tower_x, tower_y, BZ + tower_h + 1.15))
    bpy.context.active_object.name = "CrossPole"
    bpy.context.active_object.data.materials.append(m['gold'])
    bmesh_box("CrossH", (0.20, 0.03, 0.03), (tower_x, tower_y, BZ + tower_h + 1.25), m['gold'])
    bmesh_box("CrossV", (0.03, 0.03, 0.22), (tower_x, tower_y, BZ + tower_h + 1.20), m['gold'])

    # === Domed chapel ===
    chapel_x, chapel_y = 1.0, 1.4
    chapel_r = 0.70
    chapel_h = 2.0
    # Drum (cylinder base for dome)
    bmesh_prism("ChapelDrum", chapel_r, chapel_h, 12,
                (chapel_x, chapel_y, BZ), m['stone'])
    # Dome
    _dome("Chapel", chapel_x, chapel_y, BZ + chapel_h,
          radius=chapel_r, height=0.65, material=m['roof'])

    # Dome cross
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.20,
                                        location=(chapel_x, chapel_y, BZ + chapel_h + 0.75))
    bpy.context.active_object.data.materials.append(m['gold'])
    bmesh_box("DomeCrossH", (0.14, 0.02, 0.02),
              (chapel_x, chapel_y, BZ + chapel_h + 0.82), m['gold'])

    # Chapel arched windows
    for i in range(4):
        a = math.pi / 4 + (2 * math.pi * i) / 4
        wx = chapel_x + (chapel_r + 0.01) * math.cos(a)
        wy = chapel_y + (chapel_r + 0.01) * math.sin(a)
        bmesh_box(f"ChapelWin_{i}", (0.12, 0.06, 0.45),
                  (wx, wy, BZ + chapel_h / 2 + 0.30), m['window'])

    # === Courtyard cloister (covered walkway) ===
    for i in range(5):
        y = -0.8 + i * 0.40
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=1.5,
                                            location=(palazzo_w / 2 + 0.50, y, BZ + 0.75))
        col = bpy.context.active_object
        col.name = f"CloisterCol_{i}"
        col.data.materials.append(m['stone_light'])
    bmesh_box("CloisterRoof", (0.35, 2.0, 0.06),
              (palazzo_w / 2 + 0.50, -0.4, BZ + 1.53), m['roof'])

    # === Main entrance door ===
    bmesh_box("MainDoor", (0.08, 0.60, 1.6),
              (palazzo_w / 2 + 0.01, 0, BZ + 0.80), m['door'])

    # Steps
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.20, 1.5, 0.06),
                  (palazzo_w / 2 + 0.50 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_dark'])

    # Banner
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.8,
                                        location=(tower_x, tower_y, BZ + tower_h + 1.60))
    bpy.context.active_object.data.materials.append(m['wood'])
    bvz = BZ + tower_h + 1.70
    bv = [(tower_x + 0.04, tower_y, bvz),
          (tower_x + 0.45, tower_y + 0.03, bvz - 0.04),
          (tower_x + 0.45, tower_y + 0.02, bvz + 0.25),
          (tower_x + 0.04, tower_y, bvz + 0.22)]
    mesh_from_pydata("Banner", bv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# GUNPOWDER AGE — Renaissance palazzo
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (6.0, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation ===
    bmesh_box("Foundation", (5.5, 5.0, 0.22), (0, 0, Z + 0.11), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.22

    # === Main palazzo body ===
    palazzo_w = 3.6
    palazzo_d = 3.0
    palazzo_h = 3.8

    # Rusticated stone base (ground floor — rough-cut blocks)
    base_h = 1.3
    bmesh_box("RusticBase", (palazzo_w, palazzo_d, base_h),
              (0, 0, BZ + base_h / 2), m['stone_dark'], bevel=0.03)

    # Rustication texture (raised block courses)
    for i in range(5):
        z = BZ + 0.15 + i * 0.24
        for j in range(6):
            y = -1.2 + j * 0.48
            bmesh_box(f"Rustic_{i}_{j}", (0.04, 0.40, 0.18),
                      (palazzo_w / 2 + 0.01, y, z), m['stone'])

    # Upper stories (smooth plaster)
    upper_h = palazzo_h - base_h
    bmesh_box("UpperFloors", (palazzo_w, palazzo_d, upper_h),
              (0, 0, BZ + base_h + upper_h / 2), m['plaster'], bevel=0.02)

    # String courses (horizontal bands between stories)
    bmesh_box("StringCourse1", (palazzo_w + 0.06, palazzo_d + 0.06, 0.06),
              (0, 0, BZ + base_h), m['stone_trim'])
    bmesh_box("StringCourse2", (palazzo_w + 0.06, palazzo_d + 0.06, 0.06),
              (0, 0, BZ + base_h + upper_h * 0.55), m['stone_trim'])

    # Heavy cornice at top
    bmesh_box("Cornice", (palazzo_w + 0.14, palazzo_d + 0.14, 0.10),
              (0, 0, BZ + palazzo_h + 0.05), m['stone_trim'], bevel=0.02)
    bmesh_box("CorniceUnder", (palazzo_w + 0.10, palazzo_d + 0.10, 0.06),
              (0, 0, BZ + palazzo_h - 0.03), m['stone_dark'])

    # Palazzo flat roof
    bmesh_box("Roof", (palazzo_w + 0.08, palazzo_d + 0.08, 0.06),
              (0, 0, BZ + palazzo_h + 0.13), m['roof'])

    # === Arched loggia (ground floor front) ===
    for i in range(5):
        y = -1.0 + i * 0.50
        _roman_arch(f"LoggiaArch_{i}", palazzo_w / 2 + 0.03, y, BZ,
                    width=0.40, height=1.15, depth=0.10,
                    material=m['stone'], keystone_mat=m['stone_trim'],
                    segments=8)

    # === Upper floor windows (rectangular with pediments) ===
    for floor_z in [BZ + base_h + 0.30, BZ + base_h + upper_h * 0.55 + 0.20]:
        for i in range(5):
            y = -1.0 + i * 0.50
            # Window opening
            bmesh_box(f"Win_{floor_z:.1f}_{i}", (0.04, 0.28, 0.55),
                      (palazzo_w / 2 + 0.02, y, floor_z + 0.30), m['window'])
            # Window frame
            bmesh_box(f"WinFrame_{floor_z:.1f}_{i}", (0.05, 0.32, 0.04),
                      (palazzo_w / 2 + 0.02, y, floor_z + 0.59), m['stone_trim'])
            # Small triangular pediment above window
            hw_p = 0.18
            pv = [(palazzo_w / 2 + 0.03, y - hw_p, floor_z + 0.62),
                  (palazzo_w / 2 + 0.03, y + hw_p, floor_z + 0.62),
                  (palazzo_w / 2 + 0.03, y, floor_z + 0.72)]
            mesh_from_pydata(f"WinPed_{floor_z:.1f}_{i}", pv, [(0, 1, 2)], m['stone_trim'])

    # === Clock tower (attached to one corner) ===
    ct_x, ct_y = -1.2, -1.8
    ct_w = 0.85
    ct_h = 5.5
    bmesh_box("ClockTower", (ct_w, ct_w, ct_h),
              (ct_x, ct_y, BZ + ct_h / 2), m['stone'], bevel=0.02)

    # Tower level bands
    for i in range(5):
        z = BZ + 1.0 + i * 1.0
        bmesh_box(f"CTBand_{i}", (ct_w + 0.04, ct_w + 0.04, 0.04),
                  (ct_x, ct_y, z), m['stone_trim'])

    # Clock face (on two visible sides)
    for dx, dy, rot in [(ct_w / 2 + 0.01, 0, (0, math.radians(90), 0)),
                        (0, -ct_w / 2 - 0.01, (math.radians(90), 0, 0))]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.22, depth=0.04,
                                            location=(ct_x + dx, ct_y + dy, BZ + ct_h - 1.0))
        cl = bpy.context.active_object
        cl.name = f"Clock_{dx:.1f}_{dy:.1f}"
        cl.rotation_euler = rot
        cl.data.materials.append(m['gold'])

    # Tower roof (pyramidal)
    pyramid_roof("CTRoof", w=ct_w, d=ct_w, h=1.0, overhang=0.06,
                 origin=(ct_x, ct_y, BZ + ct_h), material=m['roof'])

    # Spire
    bmesh_cone("CTSpire", 0.06, 0.35, 8, (ct_x, ct_y, BZ + ct_h + 1.0), m['gold'])

    # === Inner courtyard ===
    bmesh_box("Courtyard", (1.8, 1.8, 0.04), (0, 0, BZ - 0.02), m['stone_light'])

    # Courtyard columns (arcade around yard)
    for cx, cy in [(-0.6, -0.6), (-0.6, 0.6), (0.6, -0.6), (0.6, 0.6)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.05, depth=1.2,
                                            location=(cx, cy, BZ + 0.60))
        col = bpy.context.active_object
        col.name = f"CourtCol_{cx:.1f}_{cy:.1f}"
        col.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()

    # === Main entrance ===
    bmesh_box("MainDoor", (0.08, 0.65, 1.80),
              (palazzo_w / 2 + 0.01, 0, BZ + 0.90), m['door'])

    # Steps
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.20, 1.6, 0.06),
                  (palazzo_w / 2 + 0.50 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone'])

    # Banner
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.8,
                                        location=(ct_x, ct_y, BZ + ct_h + 1.70))
    bpy.context.active_object.data.materials.append(m['wood'])
    bvz = BZ + ct_h + 1.80
    bv = [(ct_x + 0.04, ct_y, bvz),
          (ct_x + 0.45, ct_y + 0.03, bvz - 0.04),
          (ct_x + 0.45, ct_y + 0.02, bvz + 0.25),
          (ct_x + 0.04, ct_y, bvz + 0.22)]
    mesh_from_pydata("Banner", bv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# ENLIGHTENMENT AGE — Baroque Roman palazzo
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (6.5, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation ===
    bmesh_box("Foundation", (6.0, 5.5, 0.22), (0, 0, Z + 0.11), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.22

    # === Main palazzo body (Baroque — curved facade) ===
    palazzo_w = 4.0
    palazzo_d = 3.2
    palazzo_h = 4.0

    # Main body
    bmesh_box("PalazzoBody", (palazzo_w, palazzo_d, palazzo_h),
              (0, 0, BZ + palazzo_h / 2), m['plaster'], bevel=0.03)

    # === Curved facade (convex front wall overlaid) ===
    # Represented by a series of angled panels suggesting a curve
    curve_segs = 8
    facade_x = palazzo_w / 2
    for i in range(curve_segs):
        t = i / (curve_segs - 1)
        y = -palazzo_d / 2 + t * palazzo_d
        # subtle outward bulge
        bulge = 0.12 * math.sin(math.pi * t)
        bmesh_box(f"CurveFacade_{i}", (0.06, palazzo_d / curve_segs + 0.02, palazzo_h),
                  (facade_x + bulge, y, BZ + palazzo_h / 2), m['stone_light'])

    # === Ornate pilasters (shallow columns on facade) ===
    pilaster_positions = [-1.2, -0.4, 0.4, 1.2]
    for i, py in enumerate(pilaster_positions):
        # Pilaster shaft
        bmesh_box(f"Pilaster_{i}", (0.10, 0.14, palazzo_h - 0.40),
                  (facade_x + 0.08, py, BZ + palazzo_h / 2), m['stone_light'])
        # Capital
        bmesh_box(f"PilCap_{i}", (0.12, 0.18, 0.10),
                  (facade_x + 0.08, py, BZ + palazzo_h - 0.15), m['stone_trim'])
        # Base
        bmesh_box(f"PilBase_{i}", (0.12, 0.18, 0.08),
                  (facade_x + 0.08, py, BZ + 0.04), m['stone_trim'])

    # === Grand staircase (double flight) ===
    stair_x = palazzo_w / 2 + 0.30
    # Left flight
    for i in range(7):
        bmesh_box(f"StairL_{i}", (0.18, 0.60, 0.06),
                  (stair_x + i * 0.20, -0.55, BZ - 0.04 - i * 0.06), m['stone'])
    # Right flight
    for i in range(7):
        bmesh_box(f"StairR_{i}", (0.18, 0.60, 0.06),
                  (stair_x + i * 0.20, 0.55, BZ - 0.04 - i * 0.06), m['stone'])
    # Landing platform
    bmesh_box("StairLanding", (0.30, 1.4, 0.08),
              (stair_x - 0.05, 0, BZ + 0.04), m['stone_trim'])

    # Balustrade (railing pillars along stairs)
    for side_y in [-0.90, 0.90]:
        for i in range(4):
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.35,
                                                location=(stair_x + 0.20 + i * 0.35,
                                                          side_y,
                                                          BZ - i * 0.10 + 0.10))
            bpy.context.active_object.name = f"Baluster_{side_y:.1f}_{i}"
            bpy.context.active_object.data.materials.append(m['stone_light'])

    # === Cornice (elaborate) ===
    bmesh_box("Cornice1", (palazzo_w + 0.16, palazzo_d + 0.16, 0.08),
              (0, 0, BZ + palazzo_h + 0.04), m['stone_trim'], bevel=0.02)
    bmesh_box("Cornice2", (palazzo_w + 0.12, palazzo_d + 0.12, 0.06),
              (0, 0, BZ + palazzo_h - 0.04), m['stone_trim'])

    # === Windows with baroque surrounds ===
    for floor_i in range(2):
        fz = BZ + 0.60 + floor_i * 1.60
        for i in range(5):
            y = -1.2 + i * 0.60
            # Window
            bmesh_box(f"Win_{floor_i}_{i}", (0.04, 0.30, 0.65),
                      (facade_x + 0.12, y, fz + 0.35), m['window'])
            # Ornate frame
            bmesh_box(f"WinFrameT_{floor_i}_{i}", (0.06, 0.36, 0.05),
                      (facade_x + 0.12, y, fz + 0.70), m['stone_trim'])
            bmesh_box(f"WinFrameB_{floor_i}_{i}", (0.06, 0.36, 0.04),
                      (facade_x + 0.12, y, fz + 0.03), m['stone_trim'])
            # Scroll bracket under window
            if floor_i == 1:
                bmesh_box(f"Scroll_{i}", (0.06, 0.10, 0.12),
                          (facade_x + 0.12, y - 0.12, fz - 0.02), m['stone_dark'])
                bmesh_box(f"Scroll2_{i}", (0.06, 0.10, 0.12),
                          (facade_x + 0.12, y + 0.12, fz - 0.02), m['stone_dark'])

    # === Domed roof (central dome rising above palazzo) ===
    dome_base = BZ + palazzo_h + 0.10
    # Drum
    bmesh_prism("DomeDrum", 0.80, 0.60, 16, (0, 0, dome_base), m['stone_light'])
    # Dome
    _dome("Main", 0, 0, dome_base + 0.60, radius=0.80, height=0.70,
          material=m['roof'])
    # Lantern atop dome
    bmesh_prism("Lantern", 0.20, 0.35, 8, (0, 0, dome_base + 1.30), m['stone_light'])
    bmesh_cone("LanternRoof", 0.22, 0.25, 8, (0, 0, dome_base + 1.65), m['gold'])
    # Cross
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.20,
                                        location=(0, 0, dome_base + 2.00))
    bpy.context.active_object.data.materials.append(m['gold'])
    bmesh_box("DomeCross", (0.12, 0.02, 0.02), (0, 0, dome_base + 2.08), m['gold'])

    # === Fountain courtyard ===
    court_x = -1.5
    bmesh_box("Courtyard", (2.0, 2.0, 0.04), (court_x, 0, BZ - 0.02), m['stone_light'])

    # Fountain (ornate Baroque style)
    bmesh_prism("FountainPool", 0.50, 0.08, 16, (court_x, 0, BZ + 0.04), m['stone_light'])
    bmesh_prism("FountainRim", 0.55, 0.04, 16, (court_x, 0, BZ + 0.10), m['stone_trim'])
    # Central column
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.06, depth=0.70,
                                        location=(court_x, 0, BZ + 0.49))
    bpy.context.active_object.name = "FountainCol"
    bpy.context.active_object.data.materials.append(m['stone_light'])
    bpy.ops.object.shade_smooth()
    # Upper bowl
    bmesh_prism("FountainBowl", 0.20, 0.06, 10, (court_x, 0, BZ + 0.84), m['stone_trim'])
    # Spout
    bmesh_cone("FountainSpout", 0.04, 0.15, 6, (court_x, 0, BZ + 0.90), m['gold'])

    # Main entrance
    bmesh_box("MainDoor", (0.08, 0.70, 2.0),
              (facade_x + 0.14, 0, BZ + 1.00), m['door'])

    # Banner
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.8,
                                        location=(0, 0, dome_base + 2.40))
    bpy.context.active_object.data.materials.append(m['wood'])
    bvz = dome_base + 2.50
    bv = [(0.04, 0, bvz), (0.45, 0.03, bvz - 0.04),
          (0.45, 0.02, bvz + 0.25), (0.04, 0, bvz + 0.22)]
    mesh_from_pydata("Banner", bv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# INDUSTRIAL AGE — Neoclassical Italian government building
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (7.0, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Grand foundation platform ===
    bmesh_box("Foundation", (6.5, 5.5, 0.25), (0, 0, Z + 0.125), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.25

    # === Main building body ===
    main_w = 4.5
    main_d = 3.2
    main_h = 4.0
    bmesh_box("MainBody", (main_w, main_d, main_h),
              (0, 0, BZ + main_h / 2), m['stone'], bevel=0.02)

    # Horizontal band courses
    for i, z in enumerate([BZ + 1.5, BZ + 3.0, BZ + main_h]):
        bmesh_box(f"BandCourse_{i}", (main_w + 0.06, main_d + 0.06, 0.06),
                  (0, 0, z), m['stone_trim'])

    # === Tall columned portico (front, monumental) ===
    portico_x = main_w / 2 + 0.20
    col_h = 3.4
    n_cols = 8
    col_spacing = main_d / (n_cols - 1)
    for i in range(n_cols):
        cy = -main_d / 2 + i * col_spacing
        _roman_column(f"PorticoCol_{i}", portico_x, cy, BZ,
                      height=col_h, radius=0.10, material=m['stone_light'],
                      capital_mat=m['stone_trim'])

    # Portico entablature
    bmesh_box("PorticoEnt", (0.30, main_d + 0.20, 0.18),
              (portico_x, 0, BZ + col_h + 0.18), m['stone_trim'])

    # === Triangular pediment ===
    _pediment("Portico", portico_x, 0, BZ + col_h + 0.36,
              main_d + 0.20, 0.30, 0.80, m['stone_light'])

    # Pediment relief (decorative shield)
    bmesh_box("PedRelief", (0.06, 0.50, 0.30),
              (portico_x + 0.16, 0, BZ + col_h + 0.65), m['gold'])

    # Portico ceiling
    bmesh_box("PorticoCeiling", (0.80, main_d + 0.10, 0.06),
              (portico_x - 0.20, 0, BZ + col_h + 0.06), m['stone_dark'])

    # === Central dome ===
    dome_base = BZ + main_h + 0.06
    # Drum with windows
    drum_r = 1.0
    drum_h = 0.80
    bmesh_prism("DomeDrum", drum_r, drum_h, 16, (0, 0, dome_base), m['stone_light'])
    # Drum pilasters
    for i in range(8):
        a = (2 * math.pi * i) / 8
        px = (drum_r + 0.02) * math.cos(a)
        py = (drum_r + 0.02) * math.sin(a)
        bmesh_box(f"DrumPil_{i}", (0.08, 0.06, drum_h),
                  (px, py, dome_base + drum_h / 2), m['stone_trim'])

    # Dome
    _dome("Main", 0, 0, dome_base + drum_h, radius=drum_r, height=0.90,
          material=m['roof'])

    # Lantern
    bmesh_prism("Lantern", 0.25, 0.40, 8, (0, 0, dome_base + drum_h + 0.90), m['stone_light'])
    bmesh_cone("LanternCap", 0.28, 0.30, 8, (0, 0, dome_base + drum_h + 1.30), m['gold'])

    # === Windows (regularly spaced, with frames) ===
    for floor_z in [BZ + 0.40, BZ + 2.00]:
        for i in range(6):
            y = -1.2 + i * 0.48
            # Side windows (both visible sides)
            bmesh_box(f"WinF_{floor_z:.1f}_{i}", (0.04, 0.28, 0.60),
                      (main_w / 2 + 0.01, y, floor_z + 0.30), m['window'])
            bmesh_box(f"WinFrT_{floor_z:.1f}_{i}", (0.05, 0.32, 0.04),
                      (main_w / 2 + 0.02, y, floor_z + 0.62), m['stone_trim'])

    # === Iron balconies on upper floor ===
    for i in range(5):
        y = -1.0 + i * 0.50
        bmesh_box(f"Balcony_{i}", (0.25, 0.35, 0.03),
                  (main_w / 2 + 0.13, y, BZ + 2.00), m['iron'])
        # Railing
        bmesh_box(f"BalRail_{i}", (0.02, 0.35, 0.18),
                  (main_w / 2 + 0.25, y, BZ + 2.12), m['iron'])

    # === Side wing (lower extension) ===
    wing_x = -main_w / 2 - 0.60
    wing_w = 1.4
    wing_h = 2.8
    bmesh_box("SideWing", (wing_w, main_d - 0.40, wing_h),
              (wing_x, 0, BZ + wing_h / 2), m['stone'], bevel=0.02)
    bmesh_box("WingRoof", (wing_w + 0.10, main_d - 0.30, 0.08),
              (wing_x, 0, BZ + wing_h + 0.04), m['roof'])

    # === Grand entrance door ===
    bmesh_box("MainDoor", (0.08, 0.80, 2.2),
              (portico_x + 0.35, 0, BZ + 1.10), m['door'])
    # Door surround
    bmesh_box("DoorSurT", (0.10, 0.90, 0.08),
              (portico_x + 0.35, 0, BZ + 2.24), m['stone_trim'])

    # Steps (monumental staircase)
    for i in range(8):
        bmesh_box(f"Step_{i}", (0.18, 2.4, 0.06),
                  (portico_x + 0.70 + i * 0.20, 0, BZ - 0.04 - i * 0.04), m['stone'])

    # Iron fence at base of steps
    for i in range(14):
        fy = -1.6 + i * 0.23
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.50,
                                            location=(portico_x + 2.40, fy, BZ - 0.20))
        bpy.context.active_object.name = f"Fence_{i}"
        bpy.context.active_object.data.materials.append(m['iron'])

    # Banner
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.8,
                                        location=(0, 0, dome_base + drum_h + 1.90))
    bpy.context.active_object.data.materials.append(m['iron'])
    bvz = dome_base + drum_h + 2.00
    bv = [(0.04, 0, bvz), (0.45, 0.03, bvz - 0.04),
          (0.45, 0.02, bvz + 0.25), (0.04, 0, bvz + 0.22)]
    mesh_from_pydata("Banner", bv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# MODERN AGE — Italian Rationalist/Fascist architecture
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (7.0, 6.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.10
    bmesh_box("Foundation", (6.5, 5.8, 0.10), (0, 0, Z + 0.05), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Main building (stark white marble, angular) ===
    main_w = 4.2
    main_d = 3.4
    main_h = 4.5
    bmesh_box("MainBlock", (main_w, main_d, main_h),
              (0, 0, BZ + main_h / 2), m['stone_light'], bevel=0.02)

    # === Massive front columns (square, oversized — Rationalist style) ===
    col_h = 4.0
    for i in range(6):
        cy = -1.3 + i * 0.52
        # Square columns (not round — intentionally brutalist)
        bmesh_box(f"MassCol_{i}", (0.22, 0.22, col_h),
                  (main_w / 2 + 0.30, cy, BZ + col_h / 2), m['stone_light'])

    # Monumental lintel across columns
    bmesh_box("Lintel", (0.30, main_d + 0.20, 0.25),
              (main_w / 2 + 0.30, 0, BZ + col_h + 0.12), m['stone_light'])

    # "ITALIA" inscription band (simplified as relief block)
    bmesh_box("InscripBand", (0.06, 2.0, 0.30),
              (main_w / 2 + 0.46, 0, BZ + col_h + 0.35), m['stone_trim'])

    # === Angular geometry — stepped facade ===
    # Recessed upper section
    step_w = main_w - 0.60
    step_h = 1.0
    bmesh_box("UpperStep", (step_w, main_d - 0.40, step_h),
              (0, 0, BZ + main_h + step_h / 2), m['stone_light'])

    # Flat overhanging roof
    bmesh_box("Roof", (main_w + 0.30, main_d + 0.30, 0.10),
              (0, 0, BZ + main_h + step_h + 0.05), m['stone_dark'])

    # === Relief panels (stylized human figures / eagles) ===
    for i in range(4):
        y = -0.90 + i * 0.60
        bmesh_box(f"Relief_{i}", (0.04, 0.40, 0.80),
                  (main_w / 2 + 0.02, y, BZ + 1.50), m['stone_trim'])

    # === Regular window grid (deep-set) ===
    for floor_i in range(3):
        fz = BZ + 0.60 + floor_i * 1.30
        for i in range(5):
            y = -1.1 + i * 0.55
            # Deep window reveal
            bmesh_box(f"WinReveal_{floor_i}_{i}", (0.15, 0.35, 0.70),
                      (main_w / 2 + 0.01, y, fz + 0.35), m['stone_dark'])
            # Glass
            bmesh_box(f"WinGlass_{floor_i}_{i}", (0.04, 0.30, 0.65),
                      (main_w / 2 + 0.06, y, fz + 0.35), glass)

    # === Side windows ===
    for floor_i in range(3):
        fz = BZ + 0.60 + floor_i * 1.30
        for i in range(4):
            y = -1.0 + i * 0.66
            bmesh_box(f"SideWin_{floor_i}_{i}", (0.04, 0.30, 0.65),
                      (0, -main_d / 2 - 0.01, fz + 0.35), glass)

    # === Monumental entrance ===
    bmesh_box("EntranceVoid", (0.15, 1.2, 3.0),
              (main_w / 2 + 0.30, 0, BZ + 1.50), m['stone_dark'])
    bmesh_box("Door", (0.06, 1.0, 2.8),
              (main_w / 2 + 0.35, 0, BZ + 1.40), m['door'])

    # === Eagle relief above entrance ===
    bmesh_box("EagleRelief", (0.08, 0.60, 0.40),
              (main_w / 2 + 0.32, 0, BZ + 3.20), m['gold'])

    # === Flanking lower wings ===
    for y_sign in [-1, 1]:
        wy = y_sign * 2.2
        bmesh_box(f"Wing_{y_sign}", (2.0, 1.2, 2.5),
                  (0.5, wy, BZ + 1.25), m['stone_light'], bevel=0.02)
        bmesh_box(f"WingRoof_{y_sign}", (2.1, 1.3, 0.06),
                  (0.5, wy, BZ + 2.54), m['stone_dark'])
        # Wing windows
        for i in range(3):
            wx = -0.4 + i * 0.55
            bmesh_box(f"WingWin_{y_sign}_{i}", (0.04, 0.30, 0.50),
                      (wx + 0.5, wy + y_sign * 0.61, BZ + 1.00), glass)

    # === Formal plaza (travertine paving) ===
    bmesh_box("Plaza", (2.0, 3.5, 0.04),
              (main_w / 2 + 1.50, 0, Z + 0.02), m['stone_light'])

    # Lamp posts
    for y in [-1.2, 1.2]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=2.0,
                                            location=(main_w / 2 + 1.50, y, BZ + 1.0))
        bpy.context.active_object.name = f"Lamp_{y:.1f}"
        bpy.context.active_object.data.materials.append(metal)
        # Lamp head
        bmesh_box(f"LampHead_{y:.1f}", (0.15, 0.10, 0.08),
                  (main_w / 2 + 1.50, y, BZ + 2.04), m['gold'])

    # Steps
    for i in range(6):
        bmesh_box(f"Step_{i}", (0.18, 2.5, 0.06),
                  (main_w / 2 + 0.80 + i * 0.20, 0, BZ - 0.04 - i * 0.04), m['stone'])

    # Banner
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=1.0,
                                        location=(0, 0, BZ + main_h + step_h + 0.60))
    bpy.context.active_object.data.materials.append(metal)
    bvz = BZ + main_h + step_h + 0.85
    bv = [(0.04, 0, bvz), (0.45, 0.03, bvz - 0.04),
          (0.45, 0.02, bvz + 0.28), (0.04, 0, bvz + 0.25)]
    mesh_from_pydata("Banner", bv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# DIGITAL AGE — Futuristic Roman
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (7.0, 6.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.08
    bmesh_box("Foundation", (6.5, 5.8, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Main structure — glass and marble fusion ===
    main_w = 4.0
    main_d = 3.2
    main_h = 4.5

    # Marble core
    bmesh_box("MarbleCore", (main_w * 0.6, main_d * 0.6, main_h),
              (0, 0, BZ + main_h / 2), m['stone_light'], bevel=0.03)

    # Glass curtain walls (wrap around marble core)
    bmesh_box("GlassWallF", (0.06, main_d, main_h - 0.30),
              (main_w / 2, 0, BZ + main_h / 2), glass)
    bmesh_box("GlassWallR", (main_w, 0.06, main_h - 0.30),
              (0, -main_d / 2, BZ + main_h / 2), glass)
    bmesh_box("GlassWallL", (main_w, 0.06, main_h - 0.30),
              (0, main_d / 2, BZ + main_h / 2), glass)

    # Metal frame grid on glass
    for i in range(5):
        z = BZ + 0.6 + i * 0.90
        bmesh_box(f"FrameH_{i}", (main_w + 0.04, main_d + 0.04, 0.03),
                  (0, 0, z), metal)
    for i in range(5):
        y = -1.2 + i * 0.60
        bmesh_box(f"FrameVF_{i}", (0.03, 0.03, main_h),
                  (main_w / 2 + 0.01, y, BZ + main_h / 2), metal)

    # === Holographic columns (translucent, glowing pillars) ===
    # Represented by thin glass cylinders with gold accents
    holo_cols = [
        (main_w / 2 + 0.50, -1.2), (main_w / 2 + 0.50, -0.4),
        (main_w / 2 + 0.50, 0.4), (main_w / 2 + 0.50, 1.2),
    ]
    for i, (hx, hy) in enumerate(holo_cols):
        # Glass shaft
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.08, depth=3.5,
                                            location=(hx, hy, BZ + 1.75))
        shaft = bpy.context.active_object
        shaft.name = f"HoloCol_{i}"
        shaft.data.materials.append(glass)
        bpy.ops.object.shade_smooth()
        # Gold ring accents (floating)
        for j, rz in enumerate([0.5, 1.5, 2.5]):
            bmesh_prism(f"HoloRing_{i}_{j}", 0.12, 0.04, 12,
                        (hx, hy, BZ + rz), m['gold'])
        # Capital glow disc
        bmesh_prism(f"HoloCap_{i}", 0.14, 0.03, 12,
                    (hx, hy, BZ + 3.50), m['gold'])

    # === Floating aqueduct arches (signature Roman element, reimagined) ===
    for i in range(3):
        ay = -1.5 + i * 1.5
        arch_base = BZ + main_h + 0.30
        _aqueduct_arch(f"FloatArch_{i}", 0, ay, arch_base,
                       width=1.4, height=1.2, thickness=0.12, material=glass,
                       segments=10)
        # Metal trim on top
        bmesh_box(f"ArchTrim_{i}", (0.16, 1.4, 0.03),
                  (0, ay, arch_base + 1.2 + 0.05), metal)

    # === LED mosaic panels (on marble core faces) ===
    core_hw = main_w * 0.3
    core_hd = main_d * 0.3
    # Front face mosaic
    for row in range(4):
        for col in range(3):
            z = BZ + 0.80 + row * 0.80
            y = -0.40 + col * 0.40
            # Alternating gold and glass for mosaic effect
            mat = m['gold'] if (row + col) % 2 == 0 else glass
            bmesh_box(f"Mosaic_F_{row}_{col}", (0.03, 0.30, 0.60),
                      (core_hw + 0.01, y, z), mat)
    # Side face mosaic
    for row in range(4):
        for col in range(3):
            z = BZ + 0.80 + row * 0.80
            x = -0.40 + col * 0.40
            mat = m['gold'] if (row + col) % 2 == 0 else glass
            bmesh_box(f"Mosaic_S_{row}_{col}", (0.30, 0.03, 0.60),
                      (x, -core_hd - 0.01, z), mat)

    # === Domed roof with glass panels ===
    dome_base = BZ + main_h
    bmesh_box("DomeRing", (main_w + 0.10, main_d + 0.10, 0.06),
              (0, 0, dome_base + 0.03), metal)
    _dome("Tech", 0, 0, dome_base + 0.06, radius=1.2, height=0.80,
          material=glass)
    # Metal ribs on dome
    for i in range(8):
        a = (2 * math.pi * i) / 8
        rx = 1.0 * math.cos(a)
        ry = 1.0 * math.sin(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=1.4,
                                            location=(rx * 0.5, ry * 0.5, dome_base + 0.60))
        rib = bpy.context.active_object
        rib.name = f"DomeRib_{i}"
        rib.rotation_euler = (math.atan2(ry, rx) + math.pi / 2, math.radians(35), 0)
        rib.data.materials.append(metal)

    # Dome spire (antenna with glowing tip)
    spire_z = dome_base + 0.86
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=1.5,
                                        location=(0, 0, spire_z + 0.75))
    bpy.context.active_object.name = "Spire"
    bpy.context.active_object.data.materials.append(metal)
    # Glowing orb at top
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0, 0, spire_z + 1.55))
    bpy.context.active_object.name = "SpireOrb"
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # === LED accent strips ===
    bmesh_box("LED_Front", (0.04, main_d + 0.04, 0.04),
              (main_w / 2 + 0.01, 0, BZ + main_h - 0.10), m['gold'])
    bmesh_box("LED_Side", (main_w + 0.04, 0.04, 0.04),
              (0, -main_d / 2 - 0.01, BZ + main_h - 0.10), m['gold'])
    bmesh_box("LED_Base", (0.04, main_d + 0.04, 0.04),
              (main_w / 2 + 0.01, 0, BZ + 0.15), m['gold'])

    # === Entrance (sliding glass portal) ===
    bmesh_box("EntrGlass", (0.06, 1.4, 2.8),
              (main_w / 2 + 0.01, 0, BZ + 1.40), glass)
    bmesh_box("EntrFrame", (0.07, 1.5, 0.04),
              (main_w / 2 + 0.02, 0, BZ + 2.82), metal)
    bmesh_box("EntrFrameB", (0.07, 1.5, 0.04),
              (main_w / 2 + 0.02, 0, BZ + 0.02), metal)

    # === Solar panels on floating arches ===
    for i in range(3):
        ay = -1.5 + i * 1.5
        solar_z = BZ + main_h + 1.53
        bmesh_box(f"Solar_{i}", (0.70, 0.40, 0.04), (0, ay, solar_z), glass)
        bmesh_box(f"SolarF_{i}", (0.72, 0.42, 0.02), (0, ay, solar_z - 0.03), metal)

    # Floating steps (minimal, tech style)
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.20, 1.8, 0.04),
                  (main_w / 2 + 0.60 + i * 0.25, 0, BZ - 0.02 - i * 0.02), metal)

    # Planters
    for y in [-1.8, 1.8]:
        bmesh_prism(f"Planter_{y:.1f}", 0.30, 0.12, 10,
                    (main_w / 2 + 1.0, y, Z + 0.06), m['stone_light'])


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


def build_town_center_romans(materials, age='medieval'):
    """Build a Roman Town Center with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
