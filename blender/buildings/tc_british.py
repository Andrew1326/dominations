"""
British nation Town Center -- British/English architecture per age.

Stone:         Neolithic stone circle settlement -- Skara Brae-style stone hut
               with corbelled walls, stone furniture, passage entrance
Bronze:        Round barrow hill fort -- circular ditched enclosure, thatched
               roundhouse with conical roof, palisade fence
Iron:          Celtic hill fort (oppidum) -- earth ramparts, wooden gatehouse,
               large roundhouse with wattle and daub walls
Classical:     Romano-British villa -- stone walls with red tile roof,
               hypocaust heating vents, small bathhouse wing, mosaic floor
Medieval:      Norman castle keep -- square stone tower with battlements
               (crenellations), narrow arrow slits, wooden drawbridge, bailey wall
Gunpowder:     Tudor manor house -- elaborate half-timber frame, tall brick
               chimneys, mullioned windows, gatehouse with coat of arms
Enlightenment: Georgian manor -- Palladian symmetry, central portico with
               columns, sash windows, stone balustrade, clock tower
Industrial:    Victorian civic hall -- Gothic Revival with pointed arches,
               clock tower (Big Ben inspired), ornate stonework, iron railings
Modern:        Brutalist/modern British -- concrete civic centre, angular
               geometry, glass curtain wall, roof garden
Digital:       Futuristic British -- glass and steel tower with holographic
               crown, neo-Gothic spires, transparent walls, LED heraldry
"""

import bpy
import bmesh
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# ----------------------------------------------------------------
# helpers -- distinctly British architectural elements
# ----------------------------------------------------------------
def _crenellations(prefix, cx, cy, cz, length, count, axis='x', mat=None):
    """Row of merlons (battlements) along one wall edge.
    axis='x' means merlons run along the x-axis, 'y' along y-axis."""
    spacing = length / count
    for i in range(count):
        if axis == 'x':
            px = cx - length / 2 + spacing * (i + 0.5)
            bmesh_box(f"{prefix}_{i}", (spacing * 0.45, 0.12, 0.18),
                      (px, cy, cz + 0.09), mat)
        else:
            py = cy - length / 2 + spacing * (i + 0.5)
            bmesh_box(f"{prefix}_{i}", (0.12, spacing * 0.45, 0.18),
                      (cx, py, cz + 0.09), mat)


def _arrow_slit(name, x, y, z, mat, face='x'):
    """Narrow cruciform arrow slit on a wall face."""
    if face == 'x':
        bmesh_box(f"{name}_v", (0.08, 0.04, 0.35), (x, y, z), mat)
        bmesh_box(f"{name}_h", (0.08, 0.14, 0.05), (x, y, z), mat)
    else:
        bmesh_box(f"{name}_v", (0.04, 0.08, 0.35), (x, y, z), mat)
        bmesh_box(f"{name}_h", (0.14, 0.08, 0.05), (x, y, z), mat)


def _tudor_timber_frame(prefix, x, y, z, w, h, mat_timber, mat_plaster, face='x'):
    """Half-timber frame pattern on a wall face -- horizontal, vertical, and
    diagonal timber beams over plaster infill."""
    if face == 'x':
        depth = 0.08
        # Plaster infill
        bmesh_box(f"{prefix}_plaster", (0.06, w, h), (x, y, z + h / 2), mat_plaster)
        # Horizontal beams
        for zh in [0, h * 0.33, h * 0.66, h]:
            bmesh_box(f"{prefix}_hbeam_{zh:.2f}", (depth, w + 0.02, 0.06),
                      (x, y, z + zh), mat_timber)
        # Vertical beams
        n_vert = max(2, int(w / 0.4))
        for i in range(n_vert + 1):
            py = y - w / 2 + (w / n_vert) * i
            bmesh_box(f"{prefix}_vbeam_{i}", (depth, 0.05, h),
                      (x, py, z + h / 2), mat_timber)
        # Diagonal braces (X pattern in each panel)
        panel_w = w / n_vert
        for i in range(n_vert):
            py_start = y - w / 2 + panel_w * i
            py_end = py_start + panel_w
            py_mid = (py_start + py_end) / 2
            # Rising diagonal
            verts = [
                (x + 0.04, py_start + 0.04, z + h * 0.05),
                (x + 0.04, py_start + 0.07, z + h * 0.05),
                (x + 0.04, py_end - 0.04, z + h * 0.30),
                (x + 0.04, py_end - 0.07, z + h * 0.30),
            ]
            mesh_from_pydata(f"{prefix}_diag_{i}", verts,
                             [(0, 1, 2, 3)], mat_timber)
    else:
        depth = 0.08
        bmesh_box(f"{prefix}_plaster", (w, 0.06, h), (x, y, z + h / 2), mat_plaster)
        for zh in [0, h * 0.33, h * 0.66, h]:
            bmesh_box(f"{prefix}_hbeam_{zh:.2f}", (w + 0.02, depth, 0.06),
                      (x, y, z + zh), mat_timber)
        n_vert = max(2, int(w / 0.4))
        for i in range(n_vert + 1):
            px = x - w / 2 + (w / n_vert) * i
            bmesh_box(f"{prefix}_vbeam_{i}", (0.05, depth, h),
                      (px, y, z + h / 2), mat_timber)


def _gothic_pointed_arch(name, x, y, z, width, height, depth, mat):
    """Pointed Gothic arch (lancet) built from mesh_from_pydata.
    The arch has two curved sections meeting at a point at the top."""
    hw = width / 2
    n_seg = 6
    verts = []
    faces = []
    # Left curve: arc from bottom-left up to apex
    for i in range(n_seg + 1):
        t = i / n_seg
        # Quadratic curve: x goes from -hw to 0, z goes from 0 to height
        px = -hw * (1 - t)
        pz = height * (2 * t - t * t)
        verts.append((x + depth / 2, y + px, z + pz))
        verts.append((x - depth / 2, y + px, z + pz))
    # Right curve: arc from apex down to bottom-right
    for i in range(1, n_seg + 1):
        t = i / n_seg
        px = hw * t
        pz = height * (1 - t * t)
        verts.append((x + depth / 2, y + px, z + pz))
        verts.append((x - depth / 2, y + px, z + pz))
    # Connect quads along the arch
    total_points = (n_seg + 1) + n_seg  # left curve + right curve (minus shared apex)
    for i in range(total_points - 1):
        i0 = i * 2
        i1 = i * 2 + 1
        i2 = (i + 1) * 2 + 1
        i3 = (i + 1) * 2
        faces.append((i0, i3, i2, i1))
    mesh_from_pydata(name, verts, faces, mat)


def _chimney_stack(name, x, y, z, height, mat_brick, mat_top):
    """Tall brick chimney with a slightly wider cap."""
    bmesh_box(f"{name}_shaft", (0.22, 0.22, height), (x, y, z + height / 2), mat_brick)
    # Chimney pot/cap
    bmesh_box(f"{name}_cap", (0.28, 0.28, 0.08), (x, y, z + height + 0.04), mat_top)
    bmesh_box(f"{name}_pot", (0.12, 0.12, 0.12), (x, y, z + height + 0.14), mat_brick)


def _corbelled_roof(name, cx, cy, cz, radius, height, segments, mat):
    """Corbelled stone dome (like Skara Brae) -- a squat cone with smooth shading."""
    obj = bmesh_cone(name, radius, height, segments, (cx, cy, cz), mat, smooth=True)
    return obj


# ============================================================
# STONE AGE -- Neolithic stone circle (Skara Brae)
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Sunken settlement mound ===
    bmesh_prism("SettleMound", 2.4, 0.20, 12, (0, 0, Z + 0.06), m['stone_dark'])

    BZ = Z + 0.26

    # === Main dwelling -- corbelled stone hut ===
    # Thick dry-stone walls (rectangular base with rounded interior)
    wall_h = 1.0
    bmesh_box("HutWallR", (1.6, 0.25, wall_h), (0, -0.65, BZ + wall_h / 2), m['stone'])
    bmesh_box("HutWallL", (1.6, 0.25, wall_h), (0, 0.65, BZ + wall_h / 2), m['stone'])
    bmesh_box("HutWallB", (0.25, 1.30, wall_h), (-0.80, 0, BZ + wall_h / 2), m['stone'])
    # Front wall with passage gap
    bmesh_box("HutWallF_L", (0.25, 0.40, wall_h), (0.80, -0.45, BZ + wall_h / 2), m['stone'])
    bmesh_box("HutWallF_R", (0.25, 0.40, wall_h), (0.80, 0.45, BZ + wall_h / 2), m['stone'])

    # Corbelled stone roof (dome shape)
    _corbelled_roof("HutRoof", 0, 0, BZ + wall_h, 1.05, 0.80, 12, m['stone_dark'])

    # Passage entrance (low tunnel)
    bmesh_box("PassageFloor", (0.70, 0.40, 0.06), (1.20, 0, BZ + 0.03), m['stone_dark'])
    bmesh_box("PassageWallL", (0.70, 0.08, 0.55), (1.20, -0.18, BZ + 0.275), m['stone'])
    bmesh_box("PassageWallR", (0.70, 0.08, 0.55), (1.20, 0.18, BZ + 0.275), m['stone'])
    bmesh_box("PassageLintel", (0.70, 0.40, 0.10), (1.20, 0, BZ + 0.60), m['stone'])

    # === Interior stone furniture ===
    # Stone bed platform (left)
    bmesh_box("StoneBedL", (0.55, 0.30, 0.20), (-0.35, 0.38, BZ + 0.10), m['stone_light'])
    # Stone bed platform (right)
    bmesh_box("StoneBedR", (0.55, 0.30, 0.20), (-0.35, -0.38, BZ + 0.10), m['stone_light'])
    # Stone dresser (back wall)
    bmesh_box("Dresser", (0.25, 0.60, 0.45), (-0.60, 0, BZ + 0.225), m['stone_light'])
    bmesh_box("DresserShelf", (0.22, 0.55, 0.04), (-0.60, 0, BZ + 0.30), m['stone'])

    # Central fire pit (stone-lined hearth)
    bmesh_prism("Hearth", 0.20, 0.08, 8, (0, 0, BZ + 0.04), m['stone_dark'])
    # Hearth stones
    for i in range(6):
        a = (2 * math.pi * i) / 6
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.06,
            location=(0.22 * math.cos(a), 0.22 * math.sin(a), BZ + 0.06))
        st = bpy.context.active_object
        st.name = f"HearthStone_{i}"
        st.scale = (1.2, 1, 0.6)
        st.data.materials.append(m['stone'])

    # === Secondary smaller hut ===
    bmesh_prism("Hut2Base", 0.55, wall_h * 0.7, 8, (-1.6, 1.2, BZ), m['stone'])
    _corbelled_roof("Hut2Roof", -1.6, 1.2, BZ + wall_h * 0.7, 0.65, 0.55, 10, m['stone_dark'])

    # === Stone circle (ritual/gathering area) ===
    circle_r = 1.8
    n_stones = 8
    for i in range(n_stones):
        a = (2 * math.pi * i) / n_stones + 0.3
        sx = circle_r * math.cos(a) - 0.5
        sy = circle_r * math.sin(a) - 0.5
        stone_h = 0.35 + 0.15 * (i % 3)
        verts = [
            (sx - 0.08, sy - 0.06, Z + 0.06),
            (sx + 0.08, sy - 0.06, Z + 0.06),
            (sx + 0.08, sy + 0.06, Z + 0.06),
            (sx - 0.08, sy + 0.06, Z + 0.06),
            (sx - 0.06, sy - 0.04, Z + 0.06 + stone_h),
            (sx + 0.06, sy - 0.04, Z + 0.06 + stone_h),
            (sx + 0.06, sy + 0.04, Z + 0.06 + stone_h),
            (sx - 0.06, sy + 0.04, Z + 0.06 + stone_h),
            (sx, sy, Z + 0.06 + stone_h + 0.06),
        ]
        faces = [
            (0, 1, 2, 3),
            (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
            (4, 5, 8), (5, 6, 8), (6, 7, 8), (7, 4, 8),
        ]
        mesh_from_pydata(f"StandingStone_{i}", verts, faces, m['stone'])

    # === Midden (refuse heap) ===
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(1.8, -1.3, Z + 0.10))
    midden = bpy.context.active_object
    midden.name = "Midden"
    midden.scale = (1.3, 1, 0.4)
    midden.data.materials.append(m['stone_dark'])

    # === Drying rack ===
    for dy in [-0.20, 0.20]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.03, depth=0.80,
                                            location=(1.8, 1.0 + dy, Z + 0.40))
        bpy.context.active_object.name = f"Rack_{dy:.1f}"
        bpy.context.active_object.data.materials.append(m['wood'])
    bmesh_box("RackBar", (0.04, 0.50, 0.04), (1.8, 1.0, Z + 0.80), m['wood_dark'])


# ============================================================
# BRONZE AGE -- Round barrow hill fort, thatched roundhouse
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Circular ditch and bank (hill fort enclosure) ===
    # Outer bank
    bmesh_prism("OuterBank", 2.5, 0.18, 20, (0, 0, Z + 0.06), m['stone_dark'])
    # Inner ditch (lower ring -- darker)
    bmesh_prism("InnerDitch", 2.2, 0.10, 20, (0, 0, Z + 0.05), m['ground'])
    # Raised inner platform
    bmesh_prism("InnerPlat", 2.0, 0.15, 16, (0, 0, Z + 0.06), m['stone_dark'])

    BZ = Z + 0.21

    # === Main roundhouse (large, central) ===
    rh_r = 1.1
    rh_h = 1.3
    # Wattle and daub wall (circular)
    bmesh_prism("RHWall", rh_r, rh_h, 16, (0, 0, BZ), m['wood'])
    # Stone foundation ring
    bmesh_prism("RHFound", rh_r + 0.08, 0.10, 16, (0, 0, BZ), m['stone_dark'])

    # Conical thatched roof
    bmesh_cone("RHRoof", rh_r + 0.20, 1.3, 16, (0, 0, BZ + rh_h), m['roof'], smooth=True)

    # Roof ridge pole extending beyond
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.50,
                                        location=(0, 0, BZ + rh_h + 1.30 + 0.10))
    bpy.context.active_object.name = "RidgePole"
    bpy.context.active_object.data.materials.append(m['wood_dark'])

    # Doorway (south-facing)
    bmesh_box("DoorFrame", (0.10, 0.50, 1.10), (rh_r + 0.01, 0, BZ + 0.55), m['wood_dark'])
    bmesh_box("Door", (0.06, 0.40, 0.95), (rh_r + 0.02, 0, BZ + 0.475), m['door'])

    # Interior central post
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.06, depth=rh_h + 0.8,
                                        location=(0, 0, BZ + (rh_h + 0.8) / 2))
    bpy.context.active_object.name = "CentralPost"
    bpy.context.active_object.data.materials.append(m['wood_dark'])

    # Ring of support posts
    for i in range(8):
        a = (2 * math.pi * i) / 8
        px = 0.65 * math.cos(a)
        py = 0.65 * math.sin(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=rh_h,
                                            location=(px, py, BZ + rh_h / 2))
        bpy.context.active_object.name = f"RingPost_{i}"
        bpy.context.active_object.data.materials.append(m['wood'])

    # === Secondary smaller roundhouse ===
    bmesh_prism("RH2Wall", 0.55, 0.90, 12, (-1.5, 1.0, BZ), m['wood'])
    bmesh_cone("RH2Roof", 0.65, 0.80, 12, (-1.5, 1.0, BZ + 0.90), m['roof'], smooth=True)

    # === Palisade fence (wooden stake perimeter) ===
    pal_r = 2.05
    n_stakes = 28
    for i in range(n_stakes):
        a = (2 * math.pi * i) / n_stakes
        # Gap for entrance
        if abs(a) < 0.15 or abs(a - 2 * math.pi) < 0.15:
            continue
        px = pal_r * math.cos(a)
        py = pal_r * math.sin(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.04, depth=0.90,
                                            location=(px, py, BZ + 0.45))
        stake = bpy.context.active_object
        stake.name = f"Stake_{i}"
        stake.data.materials.append(m['wood'])

    # Gate posts
    bmesh_box("GatePostL", (0.12, 0.12, 1.20), (pal_r + 0.05, -0.18, BZ + 0.60), m['wood_dark'])
    bmesh_box("GatePostR", (0.12, 0.12, 1.20), (pal_r + 0.05, 0.18, BZ + 0.60), m['wood_dark'])
    bmesh_box("GateLintel", (0.12, 0.48, 0.08), (pal_r + 0.05, 0, BZ + 1.24), m['wood_dark'])

    # === Round barrow (burial mound) ===
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.40, location=(1.6, -1.4, Z + 0.10))
    barrow = bpy.context.active_object
    barrow.name = "Barrow"
    barrow.scale = (1.2, 1.2, 0.4)
    barrow.data.materials.append(m['ground'])

    # === Fire pit ===
    bmesh_prism("FirePit", 0.22, 0.08, 8, (1.5, 0.8, Z + 0.06), m['stone_dark'])

    # === Storage pit with cover ===
    bmesh_prism("StoragePit", 0.30, 0.08, 8, (-1.8, -1.0, Z + 0.06), m['stone_dark'])
    bmesh_box("PitCover", (0.50, 0.50, 0.04), (-1.8, -1.0, Z + 0.16), m['wood'])


# ============================================================
# IRON AGE -- Celtic hill fort (oppidum)
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Earth rampart defenses (double ring) ===
    bmesh_prism("OuterRampart", 2.6, 0.22, 20, (0, 0, Z + 0.06), m['stone_dark'])
    bmesh_prism("InnerRampart", 2.2, 0.30, 16, (0, 0, Z + 0.06), m['stone_dark'])

    BZ = Z + 0.36

    # === Large roundhouse (chieftain's hall) ===
    hall_r = 1.3
    hall_h = 1.6
    # Wattle and daub walls
    bmesh_prism("HallWall", hall_r, hall_h, 20, (0, 0, BZ), m['wood'])
    # Wattle texture lines (horizontal)
    for zh in [0.3, 0.6, 0.9, 1.2]:
        bmesh_prism(f"WattleBand_{zh:.1f}", hall_r + 0.02, 0.03, 20, (0, 0, BZ + zh), m['wood_dark'])

    # Stone plinth
    bmesh_prism("HallPlinth", hall_r + 0.10, 0.15, 20, (0, 0, BZ), m['stone'])

    # Conical thatch roof (steeper than Bronze)
    bmesh_cone("HallRoof", hall_r + 0.25, 1.8, 20, (0, 0, BZ + hall_h), m['roof'], smooth=True)

    # Ridge pole with smoke hole ring
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.40,
                                        location=(0, 0, BZ + hall_h + 1.80 + 0.10))
    bpy.context.active_object.name = "SmokePole"
    bpy.context.active_object.data.materials.append(m['wood_dark'])
    bmesh_prism("SmokeRing", 0.15, 0.06, 8, (0, 0, BZ + hall_h + 1.78), m['wood'])

    # Grand doorway
    bmesh_box("DoorFrame", (0.14, 0.65, 1.30), (hall_r + 0.02, 0, BZ + 0.65), m['wood_dark'])
    bmesh_box("Door", (0.08, 0.50, 1.15), (hall_r + 0.03, 0, BZ + 0.575), m['door'])

    # Porch overhang
    bmesh_box("PorchRoof", (0.50, 0.90, 0.06), (hall_r + 0.30, 0, BZ + 1.40), m['roof'])
    for py in [-0.35, 0.35]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=1.35,
                                            location=(hall_r + 0.30, py, BZ + 0.675))
        bpy.context.active_object.name = f"PorchPost_{py:.1f}"
        bpy.context.active_object.data.materials.append(m['wood'])

    # Interior ring of posts
    for i in range(10):
        a = (2 * math.pi * i) / 10
        px = 0.80 * math.cos(a)
        py = 0.80 * math.sin(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=hall_h + 0.5,
                                            location=(px, py, BZ + (hall_h + 0.5) / 2))
        bpy.context.active_object.name = f"HallPost_{i}"
        bpy.context.active_object.data.materials.append(m['wood_dark'])

    # === Wooden gatehouse at rampart entrance ===
    gx = 2.25
    bmesh_box("GatePostL", (0.15, 0.15, 1.80), (gx, -0.30, BZ + 0.90), m['wood_dark'])
    bmesh_box("GatePostR", (0.15, 0.15, 1.80), (gx, 0.30, BZ + 0.90), m['wood_dark'])
    bmesh_box("GateLintel", (0.20, 0.75, 0.12), (gx, 0, BZ + 1.85), m['wood_dark'])
    # Gate planks
    bmesh_box("GateDoor", (0.08, 0.55, 1.40), (gx + 0.01, 0, BZ + 0.70), m['wood'])
    # Watchtower platform above gate
    bmesh_box("GatePlatform", (0.60, 0.90, 0.06), (gx, 0, BZ + 1.90), m['wood'])
    # Palisade extensions from gatehouse
    for i in range(5):
        for side in [-1, 1]:
            py = side * (0.50 + i * 0.30)
            bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.04, depth=1.40,
                                                location=(gx, py, BZ + 0.70))
            bpy.context.active_object.name = f"GatePal_{side}_{i}"
            bpy.context.active_object.data.materials.append(m['wood'])

    # === Smaller roundhouse (storage/workshop) ===
    bmesh_prism("WorkWall", 0.60, 0.90, 12, (-1.5, -1.0, BZ), m['wood'])
    bmesh_cone("WorkRoof", 0.70, 0.70, 12, (-1.5, -1.0, BZ + 0.90), m['roof'], smooth=True)

    # === Chariot shed (lean-to) ===
    bmesh_box("ShedWall", (0.80, 0.50, 0.70), (-1.6, 1.2, BZ + 0.35), m['wood'])
    sv = [(-2.00, 0.95, BZ + 0.70), (-1.20, 0.95, BZ + 0.70),
          (-1.20, 1.45, BZ + 1.00), (-2.00, 1.45, BZ + 1.00)]
    mesh_from_pydata("ShedRoof", sv, [(0, 1, 2, 3)], m['roof'])

    # === Forge area ===
    bmesh_box("ForgeBase", (0.50, 0.50, 0.20), (1.5, 1.5, BZ + 0.10), m['stone'])
    bmesh_box("Anvil", (0.15, 0.10, 0.15), (1.5, 1.5, BZ + 0.275), m['iron'])


# ============================================================
# CLASSICAL AGE -- Romano-British villa
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Stone foundation platform ===
    bmesh_box("Platform", (4.5, 3.8, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.18

    # === Main villa building ===
    main_w, main_d = 3.2, 2.0
    wall_h = 2.0
    bmesh_box("VillaWalls", (main_w, main_d, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Red tile roof (hipped Roman style)
    pyramid_roof("VillaRoof", w=main_w - 0.2, d=main_d - 0.2, h=0.90, overhang=0.20,
                 origin=(0, 0, BZ + wall_h + 0.02), material=m['roof'])

    # Stone cornice
    bmesh_box("Cornice", (main_w + 0.06, main_d + 0.06, 0.08), (0, 0, BZ + wall_h), m['stone_trim'], bevel=0.02)

    # === Mosaic floor (visible through front colonnade) ===
    # Central decorative panel (gold inlay pattern)
    bmesh_box("MosaicBase", (2.0, 1.2, 0.04), (0, 0, BZ + 0.02), m['stone_light'])
    # Geometric border
    bmesh_box("MosaicBorderF", (2.1, 0.06, 0.05), (0, -0.60, BZ + 0.025), m['roof'])
    bmesh_box("MosaicBorderB", (2.1, 0.06, 0.05), (0, 0.60, BZ + 0.025), m['roof'])
    bmesh_box("MosaicBorderL", (0.06, 1.2, 0.05), (-1.05, 0, BZ + 0.025), m['roof'])
    bmesh_box("MosaicBorderR", (0.06, 1.2, 0.05), (1.05, 0, BZ + 0.025), m['roof'])
    # Central medallion
    bmesh_prism("MosaicMedallion", 0.25, 0.05, 12, (0, 0, BZ + 0.02), m['gold'])

    # === Front colonnade (covered walkway) ===
    col_x = main_w / 2 + 0.50
    for i, cy in enumerate([-0.70, -0.23, 0.23, 0.70]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=wall_h,
                                            location=(col_x, cy, BZ + wall_h / 2))
        col = bpy.context.active_object
        col.name = f"Column_{i}"
        col.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        # Column base
        bmesh_box(f"ColBase_{i}", (0.20, 0.20, 0.08), (col_x, cy, BZ + 0.04), m['stone_trim'])
        # Column capital
        bmesh_box(f"ColCap_{i}", (0.22, 0.22, 0.06), (col_x, cy, BZ + wall_h + 0.03), m['stone_trim'])

    # Colonnade roof extension
    bmesh_box("ColRoof", (0.60, 1.80, 0.08), (col_x, 0, BZ + wall_h + 0.04), m['stone_trim'])
    # Lean-to tile roof over colonnade
    cv = [(col_x + 0.30, -0.95, BZ + wall_h + 0.06),
          (col_x + 0.30, 0.95, BZ + wall_h + 0.06),
          (main_w / 2 + 0.01, 0.95, BZ + wall_h + 0.40),
          (main_w / 2 + 0.01, -0.95, BZ + wall_h + 0.40)]
    mesh_from_pydata("ColTileRoof", cv, [(0, 1, 2, 3)], m['roof'])

    # === Entrance door ===
    bmesh_box("Door", (0.08, 0.55, 1.40), (main_w / 2 + 0.01, 0, BZ + 0.70), m['door'])

    # === Windows (Roman arched style approximated) ===
    for y in [-0.60, 0.60]:
        bmesh_box(f"WinF_{y:.1f}", (0.07, 0.22, 0.50), (main_w / 2 + 0.01, y, BZ + 1.20), m['window'])
        bmesh_box(f"WinArch_{y:.1f}", (0.08, 0.26, 0.04), (main_w / 2 + 0.02, y, BZ + 1.47), m['stone_trim'])
    # Side windows
    for x in [-0.80, 0.0, 0.80]:
        bmesh_box(f"WinS_{x:.1f}", (0.22, 0.07, 0.45), (x, -main_d / 2 - 0.01, BZ + 1.20), m['window'])

    # === Hypocaust heating vents (visible on side) ===
    for x in [-1.0, -0.40, 0.20, 0.80]:
        bmesh_box(f"HypoVent_{x:.1f}", (0.12, 0.08, 0.12), (x, main_d / 2 + 0.01, BZ + 0.15), m['stone_dark'])

    # === Small bathhouse wing ===
    bath_w, bath_d, bath_h = 1.2, 1.0, 1.4
    bx, by = -main_w / 2 - bath_w / 2 + 0.10, 0
    bmesh_box("BathWalls", (bath_w, bath_d, bath_h), (bx, by, BZ + bath_h / 2), m['stone'])
    pyramid_roof("BathRoof", w=bath_w - 0.1, d=bath_d - 0.1, h=0.50, overhang=0.12,
                 origin=(bx, by, BZ + bath_h + 0.02), material=m['roof'])
    # Bath window
    bmesh_box("BathWin", (0.07, 0.18, 0.30), (bx - bath_w / 2 - 0.01, by, BZ + 0.90), m['window'])
    # Steam vent on roof
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.06, depth=0.20,
                                        location=(bx, by, BZ + bath_h + 0.50 + 0.10))
    bpy.context.active_object.name = "SteamVent"
    bpy.context.active_object.data.materials.append(m['stone_dark'])

    # === Garden courtyard wall ===
    bmesh_box("CourtyardWallR", (0.10, 2.5, 0.80), (main_w / 2 + 1.10, 0, BZ + 0.40), m['stone'])
    bmesh_box("CourtyardWallF", (1.10, 0.10, 0.80), (main_w / 2 + 0.55, -1.25, BZ + 0.40), m['stone'])
    bmesh_box("CourtyardWallB", (1.10, 0.10, 0.80), (main_w / 2 + 0.55, 1.25, BZ + 0.40), m['stone'])

    # === Steps to entrance ===
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.22, 1.40, 0.06),
                  (col_x + 0.40 + i * 0.22, 0, BZ - 0.04 - i * 0.05), m['stone_light'])


# ============================================================
# MEDIEVAL AGE -- Norman castle keep
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Motte (raised mound) ===
    bmesh_prism("Motte", 2.0, 0.40, 12, (0, 0, Z + 0.06), m['stone_dark'])
    bmesh_prism("MotteTop", 1.7, 0.15, 12, (0, 0, Z + 0.46), m['stone_dark'])

    BZ = Z + 0.61

    # === Square stone keep (main tower) ===
    keep_w = 2.2
    keep_h = 3.8
    bmesh_box("Keep", (keep_w, keep_w, keep_h), (0, 0, BZ + keep_h / 2), m['stone'], bevel=0.04)

    # Stone quoin detail at corners
    for cx, cy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        for kz in range(8):
            z_off = BZ + kz * 0.48
            bmesh_box(f"Quoin_{cx}_{cy}_{kz}", (0.14, 0.14, 0.20),
                      (cx * (keep_w / 2 + 0.01), cy * (keep_w / 2 + 0.01), z_off + 0.10),
                      m['stone_trim'])

    # === Crenellations (battlements) on all four sides ===
    cren_z = BZ + keep_h
    _crenellations("CrenF", 0, -keep_w / 2 - 0.06, cren_z, keep_w, 6, 'x', m['stone_trim'])
    _crenellations("CrenB", 0, keep_w / 2 + 0.06, cren_z, keep_w, 6, 'x', m['stone_trim'])
    _crenellations("CrenR", keep_w / 2 + 0.06, 0, cren_z, keep_w, 6, 'y', m['stone_trim'])
    _crenellations("CrenL", -keep_w / 2 - 0.06, 0, cren_z, keep_w, 6, 'y', m['stone_trim'])

    # Wall-walk parapet
    bmesh_box("ParapetF", (keep_w + 0.14, 0.10, 0.06), (0, -keep_w / 2 - 0.06, cren_z + 0.03), m['stone'])
    bmesh_box("ParapetB", (keep_w + 0.14, 0.10, 0.06), (0, keep_w / 2 + 0.06, cren_z + 0.03), m['stone'])
    bmesh_box("ParapetR", (0.10, keep_w + 0.14, 0.06), (keep_w / 2 + 0.06, 0, cren_z + 0.03), m['stone'])
    bmesh_box("ParapetL", (0.10, keep_w + 0.14, 0.06), (-keep_w / 2 - 0.06, 0, cren_z + 0.03), m['stone'])

    # === Arrow slits ===
    for z_off in [BZ + 1.0, BZ + 2.2, BZ + 3.2]:
        for y in [-0.50, 0.50]:
            _arrow_slit(f"SlitF_{z_off:.1f}_{y:.1f}", keep_w / 2 + 0.02, y, z_off, m['window'], face='x')
    for z_off in [BZ + 1.5, BZ + 2.8]:
        for x in [-0.50, 0.50]:
            _arrow_slit(f"SlitR_{z_off:.1f}_{x:.1f}", x, -keep_w / 2 - 0.02, z_off, m['window'], face='y')

    # === Main entrance with Norman arch ===
    door_x = keep_w / 2 + 0.01
    bmesh_box("DoorFrame", (0.14, 0.80, 1.60), (door_x, 0, BZ + 0.80), m['stone_trim'], bevel=0.02)
    bmesh_box("Door", (0.08, 0.65, 1.40), (door_x + 0.01, 0, BZ + 0.70), m['door'])
    # Arch stones above door
    bmesh_box("DoorArch", (0.16, 0.90, 0.10), (door_x + 0.01, 0, BZ + 1.63), m['stone_trim'], bevel=0.03)

    # === Forebuilding (stair tower to entrance) ===
    fb_w, fb_d, fb_h = 1.0, 0.80, 2.5
    bmesh_box("Forebuilding", (fb_w, fb_d, fb_h), (keep_w / 2 + fb_w / 2 + 0.01, 0, BZ + fb_h / 2), m['stone'], bevel=0.02)
    _crenellations("FBCren", keep_w / 2 + fb_w / 2 + 0.01, -fb_d / 2 - 0.05, BZ + fb_h, fb_w, 3, 'x', m['stone_trim'])

    # Steps up to forebuilding
    for i in range(8):
        bmesh_box(f"Step_{i}", (0.18, 0.85, 0.06),
                  (keep_w / 2 + fb_w + 0.20 + i * 0.18, 0, BZ - 0.04 - i * 0.07), m['stone_dark'])

    # === Wooden drawbridge ===
    bmesh_box("Drawbridge", (1.0, 0.70, 0.06), (keep_w / 2 + fb_w + 0.10, 0, BZ - 0.10), m['wood'])
    # Chains
    for dy in [-0.30, 0.30]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.015, depth=1.20,
                                            location=(keep_w / 2 + fb_w / 2 + 0.01, dy, BZ + 1.60))
        ch = bpy.context.active_object
        ch.name = f"Chain_{dy:.1f}"
        ch.rotation_euler = (0, math.radians(30), 0)
        ch.data.materials.append(m['iron'])

    # === Corner turrets ===
    for cx, cy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        tx = cx * (keep_w / 2 + 0.15)
        ty = cy * (keep_w / 2 + 0.15)
        turret_h = keep_h + 0.5
        bmesh_prism(f"Turret_{cx}_{cy}", 0.30, turret_h, 8, (tx, ty, BZ), m['stone'])
        # Turret cone roof
        bmesh_cone(f"TurretRoof_{cx}_{cy}", 0.35, 0.50, 8, (tx, ty, BZ + turret_h), m['roof'], smooth=True)

    # === Bailey wall (outer courtyard) ===
    bw = 2.8
    bmesh_box("BaileyF", (0.18, bw * 2, 1.4), (bw, 0, Z + 0.06 + 0.70), m['stone'])
    bmesh_box("BaileyR", (bw * 2, 0.18, 1.4), (0, -bw, Z + 0.06 + 0.70), m['stone'])
    # Bailey crenellations
    _crenellations("BaileyCrenF", bw + 0.08, 0, Z + 0.06 + 1.40, bw * 2, 10, 'y', m['stone_trim'])

    # === Keep roof (low-pitched) ===
    pyramid_roof("KeepRoof", w=keep_w - 0.3, d=keep_w - 0.3, h=0.40, overhang=0.08,
                 origin=(0, 0, cren_z + 0.18), material=m['roof'])

    # Banner
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.80,
                                        location=(0, 0, cren_z + 0.60 + 0.40))
    bpy.context.active_object.data.materials.append(m['wood'])
    fv = [(0.04, 0, cren_z + 1.20), (0.50, 0.03, cren_z + 1.15),
          (0.50, 0.02, cren_z + 1.45), (0.04, 0, cren_z + 1.43)]
    mesh_from_pydata("Banner", fv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# GUNPOWDER AGE -- Tudor manor house
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (6.0, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Stone foundation ===
    bmesh_box("Found", (5.0, 4.0, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.18

    # === Main hall (half-timbered upper, brick lower) ===
    main_w, main_d = 3.4, 2.4
    lower_h = 1.2
    upper_h = 1.6
    total_h = lower_h + upper_h

    # Brick ground floor
    bmesh_box("LowerWalls", (main_w, main_d, lower_h), (0, 0, BZ + lower_h / 2), m['stone'], bevel=0.02)

    # Half-timbered upper floor (jetted out slightly)
    jetty = 0.12
    bmesh_box("UpperWalls", (main_w + jetty * 2, main_d + jetty * 2, upper_h),
              (0, 0, BZ + lower_h + upper_h / 2), m['plaster'], bevel=0.02)

    # Jetty beam
    bmesh_box("JettyBeamF", (main_w + jetty * 2 + 0.06, 0.06, 0.06),
              (0, -(main_d / 2 + jetty), BZ + lower_h), m['wood_dark'])
    bmesh_box("JettyBeamB", (main_w + jetty * 2 + 0.06, 0.06, 0.06),
              (0, (main_d / 2 + jetty), BZ + lower_h), m['wood_dark'])

    # === Half-timber frame patterns on all upper walls ===
    _tudor_timber_frame("TFront", main_w / 2 + jetty + 0.01,
                        0, BZ + lower_h, main_d + jetty * 2 - 0.10, upper_h,
                        m['wood_dark'], m['plaster'], face='x')
    _tudor_timber_frame("TBack", -(main_w / 2 + jetty + 0.01),
                        0, BZ + lower_h, main_d + jetty * 2 - 0.10, upper_h,
                        m['wood_dark'], m['plaster'], face='x')
    _tudor_timber_frame("TRight", 0, -(main_d / 2 + jetty + 0.01),
                        BZ + lower_h, main_w + jetty * 2 - 0.10, upper_h,
                        m['wood_dark'], m['plaster'], face='y')

    # === Steep Tudor roof with gable ends ===
    roof_z = BZ + total_h
    hw = main_w / 2 + jetty + 0.15
    hd = main_d / 2 + jetty + 0.15
    ridge_h = 1.2
    rv = [
        (-hw, -hd, roof_z), (hw, -hd, roof_z),
        (hw, hd, roof_z), (-hw, hd, roof_z),
        (-hw, 0, roof_z + ridge_h), (hw, 0, roof_z + ridge_h),
    ]
    rf = [
        (0, 1, 5, 4),  # front slope
        (2, 3, 4, 5),  # back slope
        (0, 4, 3),     # left gable
        (1, 2, 5),     # right gable
    ]
    roof_obj = mesh_from_pydata("TudorRoof", rv, rf, m['roof'])
    for p in roof_obj.data.polygons:
        p.use_smooth = True

    # Ridge beam
    bmesh_box("Ridge", (main_w + jetty * 2 + 0.32, 0.06, 0.06),
              (0, 0, roof_z + ridge_h), m['wood_dark'])

    # === Tall brick chimneys (Tudor feature) ===
    _chimney_stack("ChimL", -main_w / 2 + 0.30, 0, BZ + total_h, 1.8, m['stone'], m['stone_trim'])
    _chimney_stack("ChimR", main_w / 2 - 0.30, 0, BZ + total_h, 1.8, m['stone'], m['stone_trim'])
    # Decorative chimney with spiral detail
    _chimney_stack("ChimCenter", 0, main_d / 2 + jetty - 0.10, BZ + total_h, 2.0, m['stone'], m['stone_trim'])

    # === Mullioned windows (stone frame, multiple lights) ===
    # Ground floor windows
    for y in [-0.70, 0.70]:
        # Window frame
        bmesh_box(f"WinGF_{y:.1f}", (0.08, 0.50, 0.50),
                  (main_w / 2 + 0.01, y, BZ + 0.60), m['win_frame'])
        # Glass panes (mullions divide into 3)
        for wy_off in [-0.14, 0, 0.14]:
            bmesh_box(f"WinGPane_{y:.1f}_{wy_off:.1f}", (0.07, 0.10, 0.42),
                      (main_w / 2 + 0.02, y + wy_off, BZ + 0.60), m['window'])
        # Mullion bars
        for wy_off in [-0.07, 0.07]:
            bmesh_box(f"WinGMull_{y:.1f}_{wy_off:.1f}", (0.08, 0.02, 0.50),
                      (main_w / 2 + 0.02, y + wy_off, BZ + 0.60), m['stone_trim'])
        bmesh_box(f"WinGTransom_{y:.1f}", (0.08, 0.50, 0.02),
                  (main_w / 2 + 0.02, y, BZ + 0.60), m['stone_trim'])

    # Upper floor windows (larger, oriel style)
    for y in [-0.70, 0.0, 0.70]:
        bmesh_box(f"WinUF_{y:.1f}", (0.10, 0.45, 0.55),
                  (main_w / 2 + jetty + 0.02, y, BZ + lower_h + 0.65), m['win_frame'])
        for wy_off in [-0.12, 0, 0.12]:
            bmesh_box(f"WinUPane_{y:.1f}_{wy_off:.1f}", (0.09, 0.10, 0.47),
                      (main_w / 2 + jetty + 0.03, y + wy_off, BZ + lower_h + 0.65), m['window'])

    # === Entrance with Tudor arch ===
    door_x = main_w / 2 + 0.01
    bmesh_box("DoorFrame", (0.12, 0.80, 1.60), (door_x, 0, BZ + 0.80), m['stone_trim'], bevel=0.02)
    bmesh_box("Door", (0.08, 0.60, 1.40), (door_x + 0.01, 0, BZ + 0.70), m['door'])
    # Tudor arch (four-centered arch)
    bmesh_box("TudorArch", (0.14, 0.85, 0.12), (door_x + 0.01, 0, BZ + 1.62), m['stone_trim'], bevel=0.04)

    # === Gatehouse wing ===
    gh_w, gh_d, gh_h = 1.2, 1.4, 2.8
    gx = main_w / 2 + gh_w / 2 + 0.10
    bmesh_box("Gatehouse", (gh_w, gh_d, gh_h), (gx, 0, BZ + gh_h / 2), m['stone'], bevel=0.02)
    # Gatehouse crenellations
    _crenellations("GHCrenF", gx, -gh_d / 2 - 0.05, BZ + gh_h, gh_w, 3, 'x', m['stone_trim'])
    _crenellations("GHCrenR", gx + gh_w / 2 + 0.05, 0, BZ + gh_h, gh_d, 4, 'y', m['stone_trim'])
    # Coat of arms (gold shield shape)
    shield_verts = [
        (gx + gh_w / 2 + 0.02, -0.18, BZ + 2.0),
        (gx + gh_w / 2 + 0.02, 0.18, BZ + 2.0),
        (gx + gh_w / 2 + 0.02, 0.18, BZ + 2.35),
        (gx + gh_w / 2 + 0.02, 0, BZ + 2.50),
        (gx + gh_w / 2 + 0.02, -0.18, BZ + 2.35),
    ]
    mesh_from_pydata("CoatOfArms", shield_verts, [(0, 1, 2, 3, 4)], m['gold'])

    # === Formal garden beds ===
    for gy in [-1.2, -0.4, 0.4, 1.2]:
        bmesh_box(f"GardenBed_{gy:.1f}", (0.50, 0.30, 0.12),
                  (main_w / 2 + gh_w + 0.60, gy, Z + 0.06), m['ground'])
        bmesh_box(f"GardenBorder_{gy:.1f}", (0.55, 0.35, 0.04),
                  (main_w / 2 + gh_w + 0.60, gy, Z + 0.02), m['stone_dark'])

    # Steps
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.22, 1.2, 0.06),
                  (gx + gh_w / 2 + 0.20 + i * 0.22, 0, BZ - 0.04 - i * 0.05), m['stone_dark'])


# ============================================================
# ENLIGHTENMENT AGE -- Georgian manor (Palladian)
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (6.5, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation ===
    bmesh_box("Found", (6.0, 5.0, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.18

    # === Main building (Palladian symmetry) ===
    main_w, main_d = 3.8, 2.6
    main_h = 3.4
    bmesh_box("Main", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone'], bevel=0.03)

    # === Elegant moldings ===
    bmesh_box("Plinth", (main_w + 0.08, main_d + 0.08, 0.12), (0, 0, BZ + 0.06), m['stone_trim'], bevel=0.03)
    bmesh_box("StringCourse", (main_w + 0.06, main_d + 0.06, 0.06), (0, 0, BZ + 1.2), m['stone_trim'], bevel=0.01)
    bmesh_box("Cornice", (main_w + 0.10, main_d + 0.10, 0.10), (0, 0, BZ + main_h), m['stone_trim'], bevel=0.04)

    # Dentil course under cornice
    for i in range(20):
        dy = -main_d / 2 + 0.05 + (main_d / 20) * i
        bmesh_box(f"Dentil_{i}", (main_w + 0.08, 0.06, 0.04),
                  (0, dy, BZ + main_h - 0.08), m['stone_light'])

    # === Hipped roof with balustrade ===
    pyramid_roof("GeorgianRoof", w=main_w - 0.2, d=main_d - 0.2, h=1.0, overhang=0.15,
                 origin=(0, 0, BZ + main_h + 0.02), material=m['roof'])

    # Stone balustrade along roofline
    for side_y, lbl in [(-main_d / 2 - 0.08, "F"), (main_d / 2 + 0.08, "B")]:
        bmesh_box(f"BalRail_{lbl}", (main_w + 0.10, 0.06, 0.04),
                  (0, side_y, BZ + main_h + 0.14), m['stone_light'])
        bmesh_box(f"BalBase_{lbl}", (main_w + 0.10, 0.08, 0.04),
                  (0, side_y, BZ + main_h + 0.02), m['stone_light'])
        # Balusters
        for i in range(12):
            bx = -main_w / 2 + 0.20 + (main_w - 0.40) / 11 * i
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.02, depth=0.10,
                                                location=(bx, side_y, BZ + main_h + 0.09))
            bpy.context.active_object.name = f"Baluster_{lbl}_{i}"
            bpy.context.active_object.data.materials.append(m['stone_light'])

    # === Sash windows (Georgian signature) ===
    # 5 columns x 3 rows (ground, piano nobile, upper)
    window_cols = [-1.30, -0.65, 0.0, 0.65, 1.30]
    for row, (wz, wh) in enumerate([(BZ + 0.35, 0.50), (BZ + 1.40, 0.65), (BZ + 2.50, 0.50)]):
        for ci, wy in enumerate(window_cols):
            if row == 1 and ci == 2:
                continue  # skip center for Venetian window
            bmesh_box(f"Win_{row}_{ci}", (0.07, 0.22, wh),
                      (main_w / 2 + 0.01, wy, wz + 0.10), m['window'])
            # Sash glazing bars
            bmesh_box(f"WinBar_{row}_{ci}", (0.08, 0.22, 0.02),
                      (main_w / 2 + 0.02, wy, wz + wh / 2 + 0.10), m['win_frame'])
            # Window lintel
            bmesh_box(f"WinLintel_{row}_{ci}", (0.08, 0.26, 0.04),
                      (main_w / 2 + 0.02, wy, wz + wh + 0.12), m['stone_trim'])
            # Window sill
            bmesh_box(f"WinSill_{row}_{ci}", (0.10, 0.26, 0.03),
                      (main_w / 2 + 0.03, wy, wz + 0.07), m['stone_trim'])

    # Venetian window (central, piano nobile) -- arched center with side lights
    vwz = BZ + 1.40
    bmesh_box("VenetianCenter", (0.08, 0.25, 0.70),
              (main_w / 2 + 0.02, 0, vwz + 0.10), m['window'])
    bmesh_box("VenetianArch", (0.09, 0.30, 0.06),
              (main_w / 2 + 0.02, 0, vwz + 0.82), m['stone_trim'], bevel=0.02)
    for vy in [-0.22, 0.22]:
        bmesh_box(f"VenetianSide_{vy:.1f}", (0.08, 0.12, 0.55),
                  (main_w / 2 + 0.02, vy, vwz + 0.10), m['window'])

    # === Central portico with columns (Palladian) ===
    portico_w = 1.8
    portico_d = 0.80
    n_cols = 4
    col_spacing = portico_w / (n_cols - 1)
    for i in range(n_cols):
        cy = -portico_w / 2 + col_spacing * i
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.10, depth=2.8,
                                            location=(main_w / 2 + portico_d, cy, BZ + 1.40))
        col = bpy.context.active_object
        col.name = f"PorCol_{i}"
        col.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        # Ionic capital
        bmesh_box(f"PorCap_{i}", (0.26, 0.26, 0.08),
                  (main_w / 2 + portico_d, cy, BZ + 2.84), m['stone_trim'])
        # Column base
        bmesh_box(f"PorBase_{i}", (0.24, 0.24, 0.06),
                  (main_w / 2 + portico_d, cy, BZ + 0.03), m['stone_trim'])

    # Pediment (triangular gable)
    px = main_w / 2 + portico_d + 0.02
    pediment_v = [
        (px, -portico_w / 2 - 0.10, BZ + 2.88),
        (px, portico_w / 2 + 0.10, BZ + 2.88),
        (px, 0, BZ + 3.30),
    ]
    mesh_from_pydata("Pediment", pediment_v, [(0, 1, 2)], m['stone_light'])
    # Entablature
    bmesh_box("Entablature", (portico_d + 0.10, portico_w + 0.25, 0.10),
              (main_w / 2 + portico_d, 0, BZ + 2.90), m['stone_trim'], bevel=0.02)
    # Portico ceiling
    bmesh_box("PorCeiling", (portico_d, portico_w + 0.10, 0.04),
              (main_w / 2 + portico_d, 0, BZ + 2.85), m['stone_light'])

    # Door
    bmesh_box("Door", (0.08, 0.60, 1.60), (main_w / 2 + 0.01, 0, BZ + 0.80), m['door'])
    # Fanlight above door (semicircle approximation)
    bmesh_prism("Fanlight", 0.30, 0.06, 12, (main_w / 2 + 0.02, 0, BZ + 1.62), m['window'])

    # === Clock tower (above roofline) ===
    tw = 0.70
    tower_h = 2.0
    tower_base = BZ + main_h + 0.10
    bmesh_box("ClockTower", (tw, tw, tower_h), (0, 0, tower_base + tower_h / 2), m['stone'], bevel=0.02)
    bmesh_box("TCornice", (tw + 0.08, tw + 0.08, 0.08), (0, 0, tower_base + tower_h), m['stone_trim'], bevel=0.02)

    # Clock face (front)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.20, depth=0.04,
                                        location=(tw / 2 + 0.01, 0, tower_base + 1.3))
    clock = bpy.context.active_object
    clock.name = "ClockFace"
    clock.rotation_euler = (0, math.radians(90), 0)
    clock.data.materials.append(m['gold'])

    # Cupola dome
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(0, 0, tower_base + tower_h + 0.10))
    dome = bpy.context.active_object
    dome.name = "Cupola"
    dome.scale = (1, 1, 0.6)
    dome.data.materials.append(m['roof'])
    bpy.ops.object.shade_smooth()

    # Finial
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0, 0, tower_base + tower_h + 0.35))
    bpy.context.active_object.name = "Finial"
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # === Symmetrical wings ===
    wing_w, wing_d, wing_h = 1.2, 2.0, 2.6
    for ys, lbl in [(-2.2, "R"), (2.2, "L")]:
        bmesh_box(f"Wing_{lbl}", (wing_w, wing_d, wing_h), (0, ys, BZ + wing_h / 2), m['stone'], bevel=0.02)
        pyramid_roof(f"WRoof_{lbl}", w=wing_w - 0.15, d=wing_d - 0.15, h=0.50, overhang=0.10,
                     origin=(0, ys, BZ + wing_h + 0.02), material=m['roof'])
        # Wing windows
        for row in range(2):
            for wx in [-0.25, 0.25]:
                bmesh_box(f"WWin_{lbl}_{row}_{wx:.1f}", (0.18, 0.07, 0.50),
                          (wx, ys - wing_d / 2 - 0.01, BZ + 0.40 + row * 1.10), m['window'])

    # Steps
    for i in range(6):
        bmesh_box(f"Step_{i}", (0.22, 2.0, 0.06),
                  (main_w / 2 + portico_d + 0.20 + i * 0.22, 0, BZ - 0.04 - i * 0.05), m['stone_light'])


# ============================================================
# INDUSTRIAL AGE -- Victorian civic hall (Gothic Revival)
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (6.5, 6.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation ===
    bmesh_box("Found", (6.0, 5.0, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.18

    # === Main hall (Gothic Revival civic building) ===
    main_w, main_d = 3.6, 2.8
    main_h = 3.8
    bmesh_box("Main", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone'], bevel=0.03)

    # Ornate stonework banding
    for z_off in [BZ + 0.30, BZ + 1.2, BZ + 2.2, BZ + 3.2]:
        bmesh_box(f"Band_{z_off:.1f}", (main_w + 0.04, main_d + 0.04, 0.06),
                  (0, 0, z_off), m['stone_trim'], bevel=0.01)

    # Parapet with Gothic tracery detail
    bmesh_box("Parapet", (main_w + 0.08, main_d + 0.08, 0.20),
              (0, 0, BZ + main_h + 0.10), m['stone_trim'], bevel=0.03)
    # Pinnacles along parapet
    for px in [-main_w / 2, -main_w / 4, 0, main_w / 4, main_w / 2]:
        bmesh_box(f"Pinnacle_F_{px:.1f}", (0.08, 0.08, 0.30),
                  (px, -main_d / 2 - 0.04, BZ + main_h + 0.35), m['stone_trim'])
        bmesh_cone(f"PinnTop_F_{px:.1f}", 0.06, 0.15, 6,
                   (px, -main_d / 2 - 0.04, BZ + main_h + 0.50), m['stone_trim'])

    # === Pointed arch windows (Gothic) ===
    for row, wz in enumerate([BZ + 0.50, BZ + 1.50, BZ + 2.60]):
        for ci, wy in enumerate([-1.0, -0.50, 0.0, 0.50, 1.0]):
            wh = 0.60 if row < 2 else 0.45
            if row == 1 and ci == 2:
                wh = 0.80  # Large central window
            bmesh_box(f"Win_{row}_{ci}", (0.07, 0.20, wh),
                      (main_w / 2 + 0.01, wy, wz + 0.05), m['window'])
            # Pointed arch top
            arch_v = [
                (main_w / 2 + 0.02, wy - 0.10, wz + wh + 0.05),
                (main_w / 2 + 0.02, wy + 0.10, wz + wh + 0.05),
                (main_w / 2 + 0.02, wy, wz + wh + 0.20),
            ]
            mesh_from_pydata(f"WinArch_{row}_{ci}", arch_v, [(0, 1, 2)], m['stone_trim'])
            # Gothic tracery bar (Y-shaped mullion)
            bmesh_box(f"WinMull_{row}_{ci}", (0.08, 0.02, wh),
                      (main_w / 2 + 0.02, wy, wz + wh / 2 + 0.05), m['stone_trim'])

    # Side pointed windows
    for x in [-1.0, -0.30, 0.40, 1.10]:
        bmesh_box(f"SWin_{x:.1f}", (0.20, 0.07, 0.70),
                  (x, -main_d / 2 - 0.01, BZ + 1.70), m['window'])
        sv = [
            (x - 0.10, -main_d / 2 - 0.02, BZ + 2.40),
            (x + 0.10, -main_d / 2 - 0.02, BZ + 2.40),
            (x, -main_d / 2 - 0.02, BZ + 2.55),
        ]
        mesh_from_pydata(f"SWinArch_{x:.1f}", sv, [(0, 1, 2)], m['stone_trim'])

    # === Steep Gothic roof ===
    hw = main_w / 2 + 0.15
    hd = main_d / 2 + 0.15
    ridge_h = 1.6
    rv = [
        (-hw, -hd, BZ + main_h + 0.20), (hw, -hd, BZ + main_h + 0.20),
        (hw, hd, BZ + main_h + 0.20), (-hw, hd, BZ + main_h + 0.20),
        (-hw, 0, BZ + main_h + 0.20 + ridge_h), (hw, 0, BZ + main_h + 0.20 + ridge_h),
    ]
    rf = [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5)]
    roof_obj = mesh_from_pydata("GothicRoof", rv, rf, m['roof'])
    for p in roof_obj.data.polygons:
        p.use_smooth = True

    # === Clock tower (Big Ben inspired) ===
    TX, TY = main_w / 2 - 0.60, -main_d / 2 + 0.60
    tower_w = 1.0
    tower_h = 5.5
    bmesh_box("ClockTower", (tower_w, tower_w, tower_h),
              (TX, TY, BZ + tower_h / 2), m['stone'], bevel=0.03)

    # Tower stone bands
    for tz in [BZ + 1.0, BZ + 2.0, BZ + 3.0, BZ + 4.0, BZ + tower_h]:
        bmesh_box(f"TBand_{tz:.1f}", (tower_w + 0.06, tower_w + 0.06, 0.08),
                  (TX, TY, tz), m['stone_trim'], bevel=0.02)

    # Tower pointed windows (3 levels)
    for tz in [BZ + 1.5, BZ + 2.8, BZ + 4.2]:
        for side_x, face_dir in [(TX + tower_w / 2 + 0.01, 'x'), (TX - tower_w / 2 - 0.01, 'x')]:
            bmesh_box(f"TWin_{tz:.1f}_{side_x:.1f}", (0.07, 0.14, 0.55),
                      (side_x, TY, tz), m['window'])

    # Clock faces (four sides)
    for dx, dy, rot in [(tower_w / 2 + 0.01, 0, (0, math.radians(90), 0)),
                        (-(tower_w / 2 + 0.01), 0, (0, math.radians(-90), 0)),
                        (0, tower_w / 2 + 0.01, (math.radians(90), 0, 0)),
                        (0, -(tower_w / 2 + 0.01), (math.radians(-90), 0, 0))]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.28, depth=0.04,
                                            location=(TX + dx, TY + dy, BZ + tower_h - 0.50))
        clk = bpy.context.active_object
        clk.name = f"Clock_{dx:.1f}_{dy:.1f}"
        clk.rotation_euler = rot
        clk.data.materials.append(m['gold'])

    # Tower spire (Gothic pointed)
    bmesh_cone("TowerSpire", 0.50, 2.0, 8,
               (TX, TY, BZ + tower_h), m['roof_edge'], smooth=True)

    # Gold orb and finial
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08,
                                          location=(TX, TY, BZ + tower_h + 2.00))
    bpy.context.active_object.name = "SpireOrb"
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # === Grand entrance ===
    # Gothic arched doorway
    door_x = main_w / 2 + 0.01
    bmesh_box("DoorFrame", (0.14, 1.0, 2.0), (door_x, 0, BZ + 1.0), m['stone_trim'], bevel=0.03)
    bmesh_box("Door", (0.08, 0.80, 1.80), (door_x + 0.01, 0, BZ + 0.90), m['door'])
    # Pointed arch over door
    dav = [
        (door_x + 0.02, -0.50, BZ + 2.00),
        (door_x + 0.02, 0.50, BZ + 2.00),
        (door_x + 0.02, 0, BZ + 2.40),
    ]
    mesh_from_pydata("DoorArch", dav, [(0, 1, 2)], m['stone_trim'])

    # === Iron railings ===
    for i in range(16):
        fy = -2.0 + i * 0.26
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.70,
                                            location=(main_w / 2 + 0.80, fy, BZ + 0.20))
        bpy.context.active_object.name = f"Railing_{i}"
        bpy.context.active_object.data.materials.append(m['iron'])
    # Railing top bar
    bmesh_box("RailTop", (0.04, 4.0, 0.03), (main_w / 2 + 0.80, 0, BZ + 0.58), m['iron'])
    # Railing bottom bar
    bmesh_box("RailBot", (0.04, 4.0, 0.03), (main_w / 2 + 0.80, 0, BZ + 0.08), m['iron'])

    # Steps
    for i in range(6):
        bmesh_box(f"Step_{i}", (0.22, 2.0, 0.06),
                  (main_w / 2 + 0.20 + i * 0.22, 0, BZ - 0.04 - i * 0.05), m['stone_dark'])


# ============================================================
# MODERN AGE -- Brutalist / modern British civic centre
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (7.0, 6.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.10
    bmesh_box("Found", (6.5, 5.5, 0.10), (0, 0, Z + 0.05), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Main concrete block (brutalist angular geometry) ===
    main_w, main_d = 3.8, 2.8
    main_h = 3.5
    bmesh_box("MainBlock", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone'], bevel=0.02)

    # Exposed concrete texture bands
    for z_off in [BZ + 0.80, BZ + 1.60, BZ + 2.40, BZ + 3.20]:
        bmesh_box(f"ConcBand_{z_off:.1f}", (main_w + 0.02, main_d + 0.02, 0.04),
                  (0, 0, z_off), m['stone_dark'])

    # === Angular cantilevered upper section ===
    cant_w, cant_d, cant_h = 4.2, 3.2, 1.5
    bmesh_box("CantSection", (cant_w, cant_d, cant_h),
              (0.20, 0, BZ + main_h - cant_h / 2), m['stone'], bevel=0.01)

    # === Glass curtain wall (front face) ===
    bmesh_box("GlassCurtain", (0.06, main_d - 0.30, main_h - 0.50),
              (main_w / 2 + 0.01, 0, BZ + main_h / 2 + 0.2), glass)

    # Concrete mullion grid
    for y in [-0.90, -0.30, 0.30, 0.90]:
        bmesh_box(f"CMull_{y:.1f}", (0.05, 0.06, main_h - 0.60),
                  (main_w / 2 + 0.02, y, BZ + main_h / 2 + 0.2), m['stone'])
    for z_off in [BZ + 1.0, BZ + 2.0, BZ + 3.0]:
        bmesh_box(f"CHMull_{z_off:.1f}", (0.05, main_d - 0.40, 0.05),
                  (main_w / 2 + 0.02, 0, z_off), m['stone'])

    # === Side glass ribbon windows ===
    for z_off in [BZ + 1.0, BZ + 2.2]:
        bmesh_box(f"RibWin_{z_off:.1f}", (main_w - 0.50, 0.06, 0.60),
                  (0, -main_d / 2 - 0.01, z_off), glass)
        bmesh_box(f"RibFrame_{z_off:.1f}", (main_w - 0.50, 0.04, 0.04),
                  (0, -main_d / 2 - 0.02, z_off + 0.32), m['stone'])

    # === Flat roof with garden ===
    bmesh_box("FlatRoof", (cant_w + 0.10, cant_d + 0.10, 0.12),
              (0.20, 0, BZ + main_h + 0.06), m['stone_dark'])

    # Roof garden planters
    for gx, gy in [(-1.2, -0.8), (-1.2, 0.8), (0.4, -0.8), (0.4, 0.8), (1.2, 0)]:
        bmesh_box(f"Planter_{gx:.1f}_{gy:.1f}", (0.50, 0.40, 0.20),
                  (gx + 0.20, gy, BZ + main_h + 0.22), m['stone'])
        bmesh_box(f"Plant_{gx:.1f}_{gy:.1f}", (0.45, 0.35, 0.08),
                  (gx + 0.20, gy, BZ + main_h + 0.36), m['ground'])

    # === Brutalist entrance canopy (cantilevered concrete slab) ===
    bmesh_box("Canopy", (1.2, 2.4, 0.10), (main_w / 2 + 0.60, 0, BZ + 2.60), m['stone'])
    # Support pillars (concrete, angular)
    for py in [-0.90, 0.90]:
        bmesh_box(f"CanopyPillar_{py:.1f}", (0.15, 0.15, 2.50),
                  (main_w / 2 + 1.10, py, BZ + 1.30), m['stone'])

    # Glass entrance doors
    bmesh_box("GlassDoor", (0.06, 1.60, 2.30), (main_w / 2 + 0.01, 0, BZ + 1.15), glass)
    bmesh_box("DoorFrame", (0.07, 1.70, 0.05), (main_w / 2 + 0.02, 0, BZ + 2.32), metal)

    # === Staircase tower (angular concrete) ===
    st_w, st_h = 0.80, 4.5
    bmesh_box("StairTower", (st_w, st_w, st_h),
              (-main_w / 2 - st_w / 2 + 0.10, -main_d / 2 + st_w / 2, BZ + st_h / 2), m['stone'])
    # Stair tower slit window
    bmesh_box("StairWin", (0.06, 0.12, st_h - 0.50),
              (-main_w / 2 - st_w + 0.11, -main_d / 2 + st_w / 2, BZ + st_h / 2), glass)

    # === Covered walkway (concrete colonnade) ===
    for i in range(6):
        py = -2.0 + i * 0.80
        bmesh_box(f"WalkPillar_{i}", (0.12, 0.12, 2.40),
                  (main_w / 2 + 0.60, py, BZ + 1.20), m['stone'])
    bmesh_box("WalkRoof", (0.60, 4.2, 0.08), (main_w / 2 + 0.60, -0.10, BZ + 2.45), m['stone'])

    # === Public art sculpture (abstract) ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.08, depth=1.2,
                                        location=(main_w / 2 + 1.80, 0, BZ + 0.60))
    bpy.context.active_object.name = "Sculpture_Base"
    bpy.context.active_object.data.materials.append(metal)
    # Angular top piece
    sv = [
        (main_w / 2 + 1.70, -0.15, BZ + 1.20),
        (main_w / 2 + 1.90, -0.15, BZ + 1.20),
        (main_w / 2 + 1.95, 0.10, BZ + 1.70),
        (main_w / 2 + 1.65, 0.10, BZ + 1.70),
    ]
    mesh_from_pydata("Sculpture_Top", sv, [(0, 1, 2, 3)], metal)

    # Flag
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=1.5,
                                        location=(1.0, 1.2, BZ + main_h + 0.12 + 0.75))
    bpy.context.active_object.data.materials.append(metal)
    fv = [(1.03, 1.2, BZ + main_h + 1.10), (1.50, 1.23, BZ + main_h + 1.05),
          (1.50, 1.22, BZ + main_h + 1.35), (1.03, 1.2, BZ + main_h + 1.38)]
    mesh_from_pydata("Banner", fv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# DIGITAL AGE -- Futuristic British (glass/steel, neo-Gothic)
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (7.0, 6.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.08
    bmesh_box("Found", (6.5, 5.5, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Main glass tower (tapered, neo-Gothic silhouette) ===
    # Lower wide section
    lower_h = 2.5
    bmesh_box("TowerLower", (3.2, 2.6, lower_h), (0, 0, BZ + lower_h / 2), glass)
    # Middle section (narrower)
    mid_h = 2.0
    bmesh_box("TowerMid", (2.6, 2.2, mid_h), (0, 0, BZ + lower_h + mid_h / 2), glass)
    # Upper section (crown level)
    upper_h = 1.5
    bmesh_box("TowerUpper", (2.0, 1.8, upper_h), (0, 0, BZ + lower_h + mid_h + upper_h / 2), glass)

    # Steel structural frame
    for z in [BZ + 0.8, BZ + 1.8, BZ + 2.5, BZ + 3.5, BZ + 4.5, BZ + 5.5]:
        if z < BZ + lower_h:
            fw, fd = 3.22, 2.62
        elif z < BZ + lower_h + mid_h:
            fw, fd = 2.62, 2.22
        else:
            fw, fd = 2.02, 1.82
        bmesh_box(f"Frame_{z:.1f}", (fw, fd, 0.04), (0, 0, z), metal)

    # Vertical steel ribs (Gothic rib vault inspired)
    for y in [-0.80, 0.0, 0.80]:
        for xs in [-1, 1]:
            verts = [
                (xs * 1.60, y - 0.02, BZ),
                (xs * 1.60, y + 0.02, BZ),
                (xs * 1.30, y + 0.02, BZ + lower_h),
                (xs * 1.30, y - 0.02, BZ + lower_h),
                (xs * 1.10, y + 0.02, BZ + lower_h + mid_h),
                (xs * 1.10, y - 0.02, BZ + lower_h + mid_h),
                (xs * 1.00, y + 0.02, BZ + lower_h + mid_h + upper_h),
                (xs * 1.00, y - 0.02, BZ + lower_h + mid_h + upper_h),
            ]
            faces = [(0, 1, 2, 3), (3, 2, 4, 5), (5, 4, 6, 7)]
            mesh_from_pydata(f"Rib_{xs}_{y:.1f}", verts, faces, metal)

    # === Holographic crown (LED-lit crown shape on top) ===
    crown_z = BZ + lower_h + mid_h + upper_h
    crown_r = 1.10
    n_points = 8
    crown_verts = []
    crown_faces = []
    # Inner ring (base)
    for i in range(n_points):
        a = (2 * math.pi * i) / n_points
        crown_verts.append((crown_r * 0.85 * math.cos(a),
                           crown_r * 0.85 * math.sin(a),
                           crown_z))
    # Outer ring with alternating peaks (crown shape)
    for i in range(n_points):
        a = (2 * math.pi * i) / n_points
        peak = 0.55 if i % 2 == 0 else 0.25
        crown_verts.append((crown_r * math.cos(a),
                           crown_r * math.sin(a),
                           crown_z + peak))
    # Connect inner to outer
    for i in range(n_points):
        j = (i + 1) % n_points
        crown_faces.append((i, j, n_points + j, n_points + i))
    # Top cap (connecting peaks)
    for i in range(n_points):
        j = (i + 1) % n_points
        crown_faces.append((n_points + i, n_points + j, 2 * n_points))
    crown_verts.append((0, 0, crown_z + 0.40))  # apex
    crown_obj = mesh_from_pydata("HoloCrown", crown_verts, crown_faces, m['gold'])
    for p in crown_obj.data.polygons:
        p.use_smooth = True

    # Crown jewels (orb on top)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0, 0, crown_z + 0.60))
    orb = bpy.context.active_object
    orb.name = "CrownOrb"
    orb.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # Cross on orb
    bmesh_box("CrossV", (0.03, 0.03, 0.25), (0, 0, crown_z + 0.82), m['gold'])
    bmesh_box("CrossH", (0.03, 0.18, 0.03), (0, 0, crown_z + 0.88), m['gold'])

    # === Neo-Gothic spires at corners ===
    for cx, cy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        sx = cx * 1.10
        sy = cy * 0.95
        spire_base = crown_z - 0.50
        bmesh_box(f"SpireBase_{cx}_{cy}", (0.20, 0.20, 0.80),
                  (sx, sy, spire_base + 0.40), metal)
        bmesh_cone(f"Spire_{cx}_{cy}", 0.15, 0.80, 6,
                   (sx, sy, spire_base + 0.80), metal, smooth=True)
        # LED accent on spire
        bmesh_prism(f"SpireLED_{cx}_{cy}", 0.08, 0.06, 8,
                    (sx, sy, spire_base + 0.60), m['gold'])

    # === LED heraldry panels (three lions, stylized) ===
    # Front facade LED panel
    panel_x = 1.61
    bmesh_box("HeraldryPanel", (0.06, 1.2, 0.80), (panel_x, 0, BZ + 1.50), m['gold'])
    # Shield outline
    shv = [
        (panel_x + 0.01, -0.30, BZ + 1.20),
        (panel_x + 0.01, 0.30, BZ + 1.20),
        (panel_x + 0.01, 0.30, BZ + 1.70),
        (panel_x + 0.01, 0, BZ + 1.85),
        (panel_x + 0.01, -0.30, BZ + 1.70),
    ]
    mesh_from_pydata("LEDShield", shv, [(0, 1, 2, 3, 4)], m['banner'])

    # Horizontal LED heraldry bars (lion passant suggestion)
    for hz in [BZ + 1.35, BZ + 1.50, BZ + 1.65]:
        bmesh_box(f"LEDBar_{hz:.2f}", (0.07, 0.20, 0.04), (panel_x + 0.01, 0, hz), m['gold'])

    # Side LED rose pattern (Tudor rose)
    for side_y in [-1.31, 1.31]:
        bmesh_prism(f"LEDRose_{side_y:.1f}", 0.18, 0.05, 8,
                    (0, side_y, BZ + 2.0), m['gold'])
        bmesh_prism(f"LEDRoseInner_{side_y:.1f}", 0.10, 0.06, 8,
                    (0, side_y, BZ + 2.01), m['banner'])

    # === Transparent walls with LED accent lines ===
    # Base LED ring
    for side in ['F', 'B', 'R', 'L']:
        if side == 'F':
            bmesh_box(f"BaseLED_{side}", (3.22, 0.06, 0.06), (0, -1.32, BZ + 0.03), m['gold'])
        elif side == 'B':
            bmesh_box(f"BaseLED_{side}", (3.22, 0.06, 0.06), (0, 1.32, BZ + 0.03), m['gold'])
        elif side == 'R':
            bmesh_box(f"BaseLED_{side}", (0.06, 2.62, 0.06), (1.62, 0, BZ + 0.03), m['gold'])
        else:
            bmesh_box(f"BaseLED_{side}", (0.06, 2.62, 0.06), (-1.62, 0, BZ + 0.03), m['gold'])

    # Vertical LED accent strips on corners
    for cx, cy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        vx = cx * 1.61
        vy = cy * 1.31
        total = lower_h + mid_h + upper_h
        bmesh_box(f"CornerLED_{cx}_{cy}", (0.05, 0.05, total),
                  (vx, vy, BZ + total / 2), m['gold'])

    # === Glass entrance atrium ===
    bmesh_box("Atrium", (1.0, 2.4, 2.8), (1.62 + 0.50, 0, BZ + 1.40), glass)
    bmesh_box("AtrFrame", (1.02, 2.42, 0.04), (1.62 + 0.50, 0, BZ + 2.82), metal)
    # Sliding glass doors
    bmesh_box("GlassDoor", (0.04, 1.40, 2.40), (1.62 + 1.01, 0, BZ + 1.20), glass)
    bmesh_box("DoorFrameT", (0.05, 1.50, 0.04), (1.62 + 1.02, 0, BZ + 2.42), metal)

    # === Communication spire (central, above crown) ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=1.5,
                                        location=(0, 0, crown_z + 1.20))
    bpy.context.active_object.name = "CommSpire"
    bpy.context.active_object.data.materials.append(metal)
    # Antenna dishes
    for z_off in [0.4, 0.9, 1.3]:
        bmesh_box(f"Antenna_{z_off:.1f}", (0.50, 0.02, 0.02),
                  (0, 0, crown_z + 0.60 + z_off), metal)
        bmesh_box(f"AntennaY_{z_off:.1f}", (0.02, 0.50, 0.02),
                  (0, 0, crown_z + 0.60 + z_off), metal)

    # LED ring on comm spire
    bmesh_prism("CommLED", 0.10, 0.05, 12, (0, 0, crown_z + 1.85), m['gold'])

    # === Solar panel canopy walkway ===
    bmesh_box("SolarWalk", (1.5, 3.0, 0.04), (2.80, 0, BZ + 2.00), glass)
    for sy in [-1.2, 1.2]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=1.90,
                                            location=(2.80, sy, BZ + 1.05))
        bpy.context.active_object.data.materials.append(metal)

    # === Landscaped approach ===
    for gy in [-1.5, -0.5, 0.5, 1.5]:
        bmesh_box(f"Planter_{gy:.1f}", (0.45, 0.25, 0.20),
                  (2.80, gy, Z + 0.10), m['stone'])
        bmesh_box(f"PlantGreen_{gy:.1f}", (0.40, 0.20, 0.08),
                  (2.80, gy, Z + 0.24), m['ground'])


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


def build_town_center_british(materials, age='medieval'):
    """Build a British nation Town Center with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
