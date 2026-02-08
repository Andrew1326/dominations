"""
Storage building — resource storage structure per age, a sturdy functional
building for holding goods. 2x2 tile footprint (3.5x3.5 ground plane).

Stone:         Clay-lined pit with wooden frame cover, woven baskets, stacked pots
Bronze:        Mud-brick storehouse with flat roof, heavy wooden door, clay amphorae
Iron:          Stone granary with pitched thatch roof, ventilation gaps, wooden loading platform
Classical:     Roman horreum (granary) raised on stone pillars, tile roof, columns
Medieval:      Timber-framed warehouse with large barn doors, loading dock, barrels and crates
Gunpowder:     Stone warehouse with arched windows, wooden crane/hoist, heavy iron doors
Enlightenment: Brick warehouse with symmetrical design, clock, iron shutters, loading bay
Industrial:    Steel and brick warehouse with corrugated roof, rail platform, overhead crane
Modern:        Concrete storage facility with roll-up doors, loading dock, forklift area
Digital:       Automated warehouse — glass/metal cube with robotic arm, conveyor, LED indicators
"""

import bpy
import bmesh
import math

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# ============================================================
# STONE AGE — Clay-lined pit with wooden frame cover
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Sunken pit (clay-lined circular depression)
    bmesh_prism("PitRim", 1.2, 0.10, 12, (0, 0, Z), m['stone_dark'])
    bmesh_prism("PitInner", 1.05, 0.08, 12, (0, 0, Z), m['stone'])

    # Clay lining inside the pit (slightly recessed disc)
    bmesh_prism("ClayFloor", 1.0, 0.03, 12, (0, 0, Z - 0.02), m['stone'])

    # Wooden frame cover over the pit (rectangular lattice)
    bmesh_box("FrameBeamX1", (2.4, 0.08, 0.06), (0, -0.5, Z + 0.18), m['wood'])
    bmesh_box("FrameBeamX2", (2.4, 0.08, 0.06), (0, 0.0, Z + 0.18), m['wood'])
    bmesh_box("FrameBeamX3", (2.4, 0.08, 0.06), (0, 0.5, Z + 0.18), m['wood'])
    bmesh_box("FrameBeamY1", (0.08, 2.4, 0.06), (-0.6, 0, Z + 0.24), m['wood_dark'])
    bmesh_box("FrameBeamY2", (0.08, 2.4, 0.06), (0.0, 0, Z + 0.24), m['wood_dark'])
    bmesh_box("FrameBeamY3", (0.08, 2.4, 0.06), (0.6, 0, Z + 0.24), m['wood_dark'])

    # Corner support poles (4 tall poles holding up the cover frame)
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.50,
                                                location=(sx * 1.1, sy * 1.1, Z + 0.25))
            pole = bpy.context.active_object
            pole.name = f"SupportPole_{sx}_{sy}"
            pole.data.materials.append(m['wood'])

    # Thatched cover panel (angled, partially covering pit)
    cv = [(-1.1, -1.1, Z + 0.50), (1.1, -1.1, Z + 0.50),
          (1.1, 1.1, Z + 0.50), (-1.1, 1.1, Z + 0.50),
          (-0.9, -0.9, Z + 0.75), (0.9, -0.9, Z + 0.75),
          (0.9, 0.9, Z + 0.75), (-0.9, 0.9, Z + 0.75)]
    cf = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)]
    mesh_from_pydata("ThatchCover", cv, cf, m['roof'])

    # Woven baskets (cluster of 3)
    for i, (bx, by, br) in enumerate([(-0.6, -1.2, 0.14), (-0.3, -1.35, 0.12), (-0.8, -1.4, 0.10)]):
        bmesh_prism(f"Basket_{i}", br, br * 1.6, 8, (bx, by, Z), m['roof_edge'])

    # Stacked pots (cluster of clay pots)
    for i, (px, py, pr) in enumerate([(1.0, -1.0, 0.09), (1.2, -1.15, 0.08), (0.85, -1.25, 0.07)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=pr, location=(px, py, Z + pr * 0.8))
        pot = bpy.context.active_object
        pot.name = f"Pot_{i}"
        pot.scale = (1, 1, 0.75)
        pot.data.materials.append(m['stone'])

    # Large pot with narrow neck
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(1.1, 1.0, Z + 0.10))
    pot = bpy.context.active_object
    pot.name = "LargePot"
    pot.scale = (1, 1, 0.8)
    pot.data.materials.append(m['stone'])
    bmesh_prism("PotNeck", 0.06, 0.06, 8, (1.1, 1.0, Z + 0.18), m['stone_dark'])

    # Drying rack nearby
    for dy in [-0.15, 0.15]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.7,
                                            location=(-1.3, dy - 0.8, Z + 0.35))
        bpy.context.active_object.data.materials.append(m['wood'])
    bmesh_box("DryRackBar", (0.04, 0.35, 0.03), (-1.3, -0.8, Z + 0.68), m['wood_dark'])


# ============================================================
# BRONZE AGE — Mud-brick storehouse with flat roof
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Foundation step
    bmesh_box("Found", (2.8, 2.4, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.12
    wall_h = 1.8

    # Main mud-brick walls (thick for storage)
    bmesh_box("Main", (2.6, 2.2, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Flat roof slab (heavy)
    bmesh_box("Roof", (2.8, 2.4, 0.12), (0, 0, BZ + wall_h + 0.06), m['stone_trim'], bevel=0.02)

    # Parapet around roof
    for pos, size in [
        ((1.4, 0), (0.08, 2.4, 0.20)),
        ((-1.4, 0), (0.08, 2.4, 0.20)),
        ((0, 1.2), (2.8, 0.08, 0.20)),
        ((0, -1.2), (2.8, 0.08, 0.20)),
    ]:
        bmesh_box(f"Parapet_{pos[0]:.1f}_{pos[1]:.1f}", size,
                  (pos[0], pos[1], BZ + wall_h + 0.12 + 0.10), m['stone_trim'])

    # Heavy wooden door (wide, for loading)
    bmesh_box("Door", (0.10, 0.60, 1.10), (1.31, 0, BZ + 0.55), m['door'])
    bmesh_box("DoorFrame", (0.12, 0.70, 0.08), (1.32, 0, BZ + 1.14), m['wood'])
    # Door reinforcement bars
    for dz in [0.30, 0.60, 0.90]:
        bmesh_box(f"DoorBar_{dz:.1f}", (0.04, 0.58, 0.04), (1.35, 0, BZ + dz), m['wood_dark'])

    # Small ventilation slits
    for y in [-0.65, 0.65]:
        bmesh_box(f"Vent_{y:.1f}", (0.06, 0.08, 0.16), (1.31, y, BZ + 1.40), m['window'])

    # Side ventilation
    for x in [-0.5, 0.5]:
        bmesh_box(f"SVent_{x:.1f}", (0.08, 0.06, 0.16), (x, -1.11, BZ + 1.40), m['window'])

    # Clay amphorae (row along front wall)
    for i, ay in enumerate([-0.90, -0.60, -0.30]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(1.50, ay, BZ + 0.08))
        amp = bpy.context.active_object
        amp.name = f"Amphora_{i}"
        amp.scale = (0.7, 0.7, 1.2)
        amp.data.materials.append(m['roof'])
        # Neck
        bmesh_prism(f"AmpNeck_{i}", 0.04, 0.06, 8, (1.50, ay, BZ + 0.18), m['roof_edge'])

    # Loading stone platform at entrance
    bmesh_box("Platform", (0.60, 1.20, 0.10), (1.60, 0, BZ + 0.05), m['stone_dark'])

    # Steps to door
    for i in range(2):
        bmesh_box(f"Step_{i}", (0.18, 0.9, 0.05), (1.50 + i * 0.18, 0, BZ - 0.03 - i * 0.05), m['stone_dark'])

    # Grain sack
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(-1.2, -0.8, BZ + 0.08))
    sack = bpy.context.active_object
    sack.name = "Sack"
    sack.scale = (0.8, 0.6, 0.5)
    sack.data.materials.append(m['roof_edge'])


# ============================================================
# IRON AGE — Stone granary with pitched thatch roof
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stone foundation (raised for ventilation)
    bmesh_box("Found", (2.9, 2.3, 0.20), (0, 0, Z + 0.10), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.20
    wall_h = 1.8

    # Main stone walls (thick)
    bmesh_box("Main", (2.7, 2.1, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Stone band at base and top
    bmesh_box("BandLow", (2.74, 2.14, 0.06), (0, 0, BZ + 0.20), m['stone_trim'])
    bmesh_box("BandHigh", (2.74, 2.14, 0.06), (0, 0, BZ + wall_h - 0.06), m['stone_trim'])

    # Pitched thatch roof
    rv = [
        (-1.45, -1.15, BZ + wall_h), (1.45, -1.15, BZ + wall_h),
        (1.45, 1.15, BZ + wall_h), (-1.45, 1.15, BZ + wall_h),
        (0, -1.15, BZ + wall_h + 1.0), (0, 1.15, BZ + wall_h + 1.0),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("Roof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Ridge beam
    bmesh_box("Ridge", (0.06, 2.34, 0.06), (0, 0, BZ + wall_h + 1.0), m['wood_dark'])

    # Ventilation gaps (horizontal slits along upper walls)
    for y in [-0.70, -0.25, 0.25, 0.70]:
        bmesh_box(f"VentF_{y:.2f}", (0.06, 0.12, 0.05), (1.36, y, BZ + wall_h - 0.20), m['stone_dark'])
    for x in [-0.80, -0.30, 0.30, 0.80]:
        bmesh_box(f"VentS_{x:.2f}", (0.12, 0.06, 0.05), (x, -1.06, BZ + wall_h - 0.20), m['stone_dark'])

    # Wooden door (wide double door for grain)
    bmesh_box("DoorL", (0.08, 0.28, 1.0), (1.36, -0.18, BZ + 0.50), m['door'])
    bmesh_box("DoorR", (0.08, 0.28, 1.0), (1.36, 0.18, BZ + 0.50), m['door'])
    bmesh_box("DoorFrame", (0.10, 0.64, 0.08), (1.37, 0, BZ + 1.04), m['wood'])
    # Door vertical frame members
    for dy in [-0.32, 0.32]:
        bmesh_box(f"DoorPost_{dy:.2f}", (0.10, 0.06, 1.08), (1.37, dy, BZ + 0.54), m['wood'])

    # Wooden loading platform at front
    bmesh_box("Platform", (0.80, 1.60, 0.10), (1.65, 0, BZ + 0.05), m['wood'])
    # Platform support legs
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=0.15,
                                                location=(1.65 + sx * 0.30, sy * 0.60, Z + 0.075))
            bpy.context.active_object.data.materials.append(m['wood_dark'])

    # Steps from platform to door
    for i in range(2):
        bmesh_box(f"Step_{i}", (0.16, 0.80, 0.05), (1.45 + i * 0.18, 0, BZ - 0.03 - i * 0.05), m['stone_dark'])

    # Grain sacks by the platform
    for i, (sx, sy) in enumerate([(1.55, 0.90), (1.70, 0.80)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(sx, sy, BZ + 0.08))
        sack = bpy.context.active_object
        sack.name = f"Sack_{i}"
        sack.scale = (0.7, 0.6, 0.5)
        sack.data.materials.append(m['roof_edge'])

    # Wooden barrel by door
    bmesh_prism("Barrel", 0.10, 0.22, 8, (1.55, -0.80, BZ), m['wood_dark'])


# ============================================================
# CLASSICAL AGE — Roman horreum raised on stone pillars
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stepped platform (3 tiers)
    for i in range(3):
        w = 3.2 - i * 0.18
        d = 2.8 - i * 0.14
        bmesh_box(f"Plat_{i}", (w, d, 0.06), (0, 0, Z + 0.03 + i * 0.06), m['stone_light'], bevel=0.01)

    BZ = Z + 0.18

    # Raised stone pillars (the horreum floor is elevated for ventilation)
    pillar_h = 0.50
    for px in [-0.90, -0.30, 0.30, 0.90]:
        for py in [-0.70, 0, 0.70]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.07, depth=pillar_h,
                                                location=(px, py, BZ + pillar_h / 2))
            col = bpy.context.active_object
            col.name = f"Pillar_{px:.1f}_{py:.1f}"
            col.data.materials.append(m['stone_light'])
            bpy.ops.object.shade_smooth()
            # Pillar base
            bmesh_box(f"PilBase_{px:.1f}_{py:.1f}", (0.18, 0.18, 0.04),
                      (px, py, BZ + 0.02), m['stone_trim'])
            # Pillar cap
            bmesh_box(f"PilCap_{px:.1f}_{py:.1f}", (0.18, 0.18, 0.04),
                      (px, py, BZ + pillar_h - 0.02), m['stone_trim'])

    # Elevated floor slab
    floor_z = BZ + pillar_h
    bmesh_box("Floor", (2.6, 2.0, 0.10), (0, 0, floor_z + 0.05), m['stone_light'], bevel=0.02)

    FZ = floor_z + 0.10
    wall_h = 1.5

    # Main walls
    bmesh_box("Main", (2.4, 1.8, wall_h), (0, 0, FZ + wall_h / 2), m['stone_light'], bevel=0.02)

    # Cornice
    bmesh_box("Cornice", (2.5, 1.9, 0.06), (0, 0, FZ + wall_h), m['stone_trim'], bevel=0.02)

    # Tile roof (pitched)
    rv = [
        (-1.35, -1.05, FZ + wall_h + 0.03), (1.35, -1.05, FZ + wall_h + 0.03),
        (1.35, 1.05, FZ + wall_h + 0.03), (-1.35, 1.05, FZ + wall_h + 0.03),
        (0, -1.05, FZ + wall_h + 0.80), (0, 1.05, FZ + wall_h + 0.80),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("Roof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Ridge beam
    bmesh_box("Ridge", (0.06, 2.14, 0.06), (0, 0, FZ + wall_h + 0.80), m['wood_dark'])

    # Front entrance columns (flanking the door)
    col_h = 1.4
    for y in [-0.40, 0.40]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.065, depth=col_h,
                                            location=(1.35, y, FZ + col_h / 2))
        c = bpy.context.active_object
        c.name = f"Col_{y:.1f}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        bmesh_box(f"ColCap_{y:.1f}", (0.16, 0.16, 0.05), (1.35, y, FZ + col_h + 0.025), m['stone_trim'])
        bmesh_box(f"ColBase_{y:.1f}", (0.15, 0.15, 0.04), (1.35, y, FZ + 0.02), m['stone_trim'])

    # Portico lintel
    bmesh_box("Portico", (0.40, 1.0, 0.06), (1.35, 0, FZ + col_h + 0.05), m['stone_trim'])

    # Small pediment
    pv = [(1.38, -0.48, FZ + col_h + 0.08), (1.38, 0.48, FZ + col_h + 0.08),
          (1.38, 0, FZ + col_h + 0.35)]
    mesh_from_pydata("Pediment", pv, [(0, 1, 2)], m['stone_light'])

    # Wide door (double)
    bmesh_box("DoorL", (0.06, 0.24, 1.0), (1.21, -0.15, FZ + 0.50), m['door'])
    bmesh_box("DoorR", (0.06, 0.24, 1.0), (1.21, 0.15, FZ + 0.50), m['door'])

    # Side windows
    for x in [-0.50, 0.50]:
        bmesh_box(f"WinS_{x:.1f}", (0.14, 0.06, 0.35), (x, -0.91, FZ + 1.00), m['window'])

    # Loading ramp (wooden, going up to the elevated floor)
    rv2 = [(1.60, -0.50, Z + 0.10), (1.60, 0.50, Z + 0.10),
           (1.30, 0.50, FZ), (1.30, -0.50, FZ)]
    mesh_from_pydata("Ramp", rv2, [(0, 1, 2, 3)], m['wood'])

    # Ramp railings
    for dy in [-0.50, 0.50]:
        rv3 = [(1.60, dy, Z + 0.10), (1.60, dy, Z + 0.40),
               (1.30, dy, FZ + 0.30), (1.30, dy, FZ)]
        mesh_from_pydata(f"RampRail_{dy:.1f}", rv3, [(0, 1, 2, 3)], m['wood_dark'])

    # Gold acroterion on ridge
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(0, 0, FZ + wall_h + 0.83))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()


# ============================================================
# MEDIEVAL AGE — Timber-framed warehouse with barn doors
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stone foundation
    bmesh_box("Found", (2.8, 2.4, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.18
    wall_h = 2.0

    # Main walls (plaster infill)
    bmesh_box("Main", (2.6, 2.2, wall_h), (0, 0, BZ + wall_h / 2), m['plaster'], bevel=0.02)

    # Timber frame — vertical beams on front
    for y in [-0.95, -0.32, 0.32, 0.95]:
        bmesh_box(f"VBeamF_{y:.2f}", (0.07, 0.09, wall_h), (1.31, y, BZ + wall_h / 2), m['wood_beam'])
    # Horizontal beams on front
    for z_off in [0.0, 1.0, wall_h]:
        bmesh_box(f"HBeamF_{z_off:.1f}", (0.07, 2.2, 0.09), (1.31, 0, BZ + z_off + 0.04), m['wood_beam'])
    # Cross braces on front
    for y_start, y_end in [(-0.95, -0.32), (0.32, 0.95)]:
        dv = [(1.33, y_start, BZ + 1.08), (1.33, y_start + 0.04, BZ + 1.08),
              (1.33, y_end + 0.04, BZ + wall_h - 0.04), (1.33, y_end, BZ + wall_h - 0.04)]
        mesh_from_pydata(f"DiagF_{y_start:.2f}", dv, [(0, 1, 2, 3)], m['wood_beam'])

    # Side timber frame
    for x in [-0.85, 0, 0.85]:
        bmesh_box(f"VBeamS_{x:.1f}", (0.09, 0.07, wall_h), (x, -1.11, BZ + wall_h / 2), m['wood_beam'])
    for z_off in [0.0, 1.0, wall_h]:
        bmesh_box(f"HBeamS_{z_off:.1f}", (2.2, 0.07, 0.09), (0, -1.11, BZ + z_off + 0.04), m['wood_beam'])

    # Steep pitched roof
    rv = [
        (-1.50, -1.30, BZ + wall_h), (1.50, -1.30, BZ + wall_h),
        (1.50, 1.30, BZ + wall_h), (-1.50, 1.30, BZ + wall_h),
        (0, -1.30, BZ + wall_h + 1.3), (0, 1.30, BZ + wall_h + 1.3),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("Roof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Roof edge trim
    bmesh_box("RoofEdgeF", (0.06, 2.64, 0.06), (1.50, 0, BZ + wall_h + 0.03), m['wood_dark'])
    bmesh_box("RoofEdgeB", (0.06, 2.64, 0.06), (-1.50, 0, BZ + wall_h + 0.03), m['wood_dark'])
    # Ridge beam
    bmesh_box("Ridge", (0.06, 2.64, 0.06), (0, 0, BZ + wall_h + 1.30), m['wood_dark'])

    # Large barn doors (double, wide)
    bmesh_box("DoorL", (0.08, 0.38, 1.30), (1.31, -0.22, BZ + 0.65), m['door'])
    bmesh_box("DoorR", (0.08, 0.38, 1.30), (1.31, 0.22, BZ + 0.65), m['door'])
    bmesh_box("DoorFrame", (0.10, 0.88, 0.08), (1.32, 0, BZ + 1.34), m['wood_beam'])
    # Door frame posts
    for dy in [-0.44, 0.44]:
        bmesh_box(f"DoorPost_{dy:.2f}", (0.10, 0.07, 1.38), (1.32, dy, BZ + 0.69), m['wood_beam'])
    # Door cross-braces (Z-pattern)
    for door_y, flip in [(-0.22, 1), (0.22, -1)]:
        dv = [(1.35, door_y - 0.15, BZ + 0.10), (1.35, door_y - 0.15 + 0.04, BZ + 0.10),
              (1.35, door_y + 0.15 + 0.04, BZ + 1.20), (1.35, door_y + 0.15, BZ + 1.20)]
        mesh_from_pydata(f"DoorBrace_{door_y:.2f}", dv, [(0, 1, 2, 3)], m['wood_dark'])

    # Loading dock (raised wooden platform)
    bmesh_box("Dock", (0.80, 2.0, 0.18), (1.65, 0, BZ + 0.09), m['wood'])
    # Dock support posts
    for sy in [-0.70, 0, 0.70]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.035, depth=0.18,
                                            location=(1.90, sy, Z + 0.09))
        bpy.context.active_object.data.materials.append(m['wood_dark'])

    # Barrels on the dock
    for i, (bx, by) in enumerate([(1.50, -0.70), (1.65, -0.65), (1.55, 0.70)]):
        bmesh_prism(f"Barrel_{i}", 0.10, 0.22, 8, (bx, by, BZ + 0.18), m['wood_dark'])

    # Crates on the dock
    for i, (cx, cy) in enumerate([(1.65, 0.35), (1.80, 0.20)]):
        bmesh_box(f"Crate_{i}", (0.20, 0.20, 0.18), (cx, cy, BZ + 0.18 + 0.09), m['wood'])

    # Upper hoist beam (protruding from gable)
    bmesh_box("HoistBeam", (0.50, 0.08, 0.08), (1.50, 0, BZ + wall_h + 0.60), m['wood_dark'])
    # Hoist rope (thin cylinder)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=1.0,
                                        location=(1.70, 0, BZ + wall_h + 0.10))
    bpy.context.active_object.data.materials.append(m['roof_edge'])

    # Small window in gable
    bmesh_box("GableWin", (0.06, 0.16, 0.22), (1.31, 0, BZ + wall_h + 0.50), m['window'])


# ============================================================
# GUNPOWDER AGE — Stone warehouse with arched windows, crane
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stone foundation
    bmesh_box("Found", (3.0, 2.5, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.18
    wall_h = 2.2

    # Main stone walls
    bmesh_box("Main", (2.8, 2.3, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Stone quoin accents at corners
    for xs in [-1, 1]:
        for ys in [-1, 1]:
            for z_off in [0.15, 0.55, 0.95, 1.35, 1.75]:
                bmesh_box(f"Quoin_{xs}_{ys}_{z_off:.1f}", (0.06, 0.06, 0.14),
                          (xs * 1.41, ys * 1.16, BZ + z_off), m['stone_light'])

    # String course
    bmesh_box("StringCourse", (2.84, 2.34, 0.05), (0, 0, BZ + 1.1), m['stone_trim'], bevel=0.01)

    # Cornice
    bmesh_box("Cornice", (2.90, 2.38, 0.08), (0, 0, BZ + wall_h), m['stone_trim'], bevel=0.03)

    # Gabled roof
    top_z = BZ + wall_h
    rv = [
        (-1.55, -1.28, top_z), (1.55, -1.28, top_z),
        (1.55, 1.28, top_z), (-1.55, 1.28, top_z),
        (0, -1.28, top_z + 1.0), (0, 1.28, top_z + 1.0),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("Roof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Ridge beam
    bmesh_box("Ridge", (0.06, 2.60, 0.06), (0, 0, top_z + 1.0), m['wood_dark'])

    # Heavy iron doors (double)
    bmesh_box("DoorL", (0.10, 0.35, 1.30), (1.41, -0.20, BZ + 0.65), m['iron'])
    bmesh_box("DoorR", (0.10, 0.35, 1.30), (1.41, 0.20, BZ + 0.65), m['iron'])
    bmesh_box("DoorArch", (0.12, 0.80, 0.10), (1.42, 0, BZ + 1.35), m['stone_trim'])
    # Door frame posts
    for dy in [-0.40, 0.40]:
        bmesh_box(f"DoorPost_{dy:.2f}", (0.12, 0.08, 1.40), (1.42, dy, BZ + 0.70), m['stone_trim'])

    # Arched windows on front (simulated arches with rectangular window + arch top)
    for y in [-0.75, 0.75]:
        bmesh_box(f"Win_{y:.2f}", (0.06, 0.22, 0.40), (1.41, y, BZ + 1.50), m['window'])
        # Arch top (small triangular suggestion)
        av = [(1.42, y - 0.11, BZ + 1.70), (1.42, y + 0.11, BZ + 1.70),
              (1.42, y, BZ + 1.82)]
        mesh_from_pydata(f"WinArch_{y:.2f}", av, [(0, 1, 2)], m['window'])
        # Window frame
        bmesh_box(f"WinFrame_{y:.2f}", (0.07, 0.26, 0.04), (1.42, y, BZ + 1.72), m['stone_trim'])

    # Side arched windows
    for x in [-0.60, 0.30]:
        bmesh_box(f"SWin_{x:.1f}", (0.22, 0.06, 0.40), (x, -1.16, BZ + 1.50), m['window'])
        av = [(x - 0.11, -1.16, BZ + 1.70), (x + 0.11, -1.16, BZ + 1.70),
              (x, -1.16, BZ + 1.82)]
        mesh_from_pydata(f"SWinArch_{x:.1f}", av, [(0, 1, 2)], m['window'])

    # Wooden crane/hoist on the side
    crane_x, crane_y = -1.50, -0.80
    # Vertical mast
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=2.5,
                                        location=(crane_x, crane_y, BZ + 1.25))
    bpy.context.active_object.data.materials.append(m['wood_dark'])
    # Horizontal boom
    bmesh_box("CraneBoom", (0.06, 0.06, 1.4), (crane_x, crane_y, BZ + 2.50 + 0.10), m['wood'])
    bpy.context.active_object.rotation_euler = (0, math.radians(60), 0)
    # Diagonal brace
    bv = [(crane_x, crane_y - 0.03, BZ + 1.50), (crane_x, crane_y + 0.03, BZ + 1.50),
          (crane_x + 0.50, crane_y + 0.03, BZ + 2.40), (crane_x + 0.50, crane_y - 0.03, BZ + 2.40)]
    mesh_from_pydata("CraneBrace", bv, [(0, 1, 2, 3)], m['wood'])
    # Rope
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.010, depth=1.2,
                                        location=(crane_x + 0.40, crane_y, BZ + 1.90))
    bpy.context.active_object.data.materials.append(m['roof_edge'])

    # Loading platform
    bmesh_box("Platform", (0.60, 1.40, 0.12), (1.65, 0, BZ + 0.06), m['stone_dark'])

    # Steps
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.16, 0.90, 0.05), (1.50 + i * 0.16, 0, BZ - 0.03 - i * 0.05), m['stone_dark'])


# ============================================================
# ENLIGHTENMENT AGE — Brick warehouse, clock, iron shutters
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Foundation
    bmesh_box("Found", (3.0, 2.5, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.15
    wall_h = 2.6

    # Main brick walls
    bmesh_box("Main", (2.8, 2.3, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Quoins (decorative corner stones)
    for xs in [-1, 1]:
        for ys in [-1, 1]:
            for z_off in [0.15, 0.55, 0.95, 1.35, 1.75, 2.15]:
                bmesh_box(f"Quoin_{xs}_{ys}_{z_off:.1f}", (0.06, 0.06, 0.14),
                          (xs * 1.41, ys * 1.16, BZ + z_off), m['stone_light'])

    # String course between floors
    bmesh_box("StringCourse", (2.84, 2.34, 0.05), (0, 0, BZ + 1.3), m['stone_trim'], bevel=0.01)

    # Cornice
    bmesh_box("Cornice", (2.90, 2.38, 0.08), (0, 0, BZ + wall_h), m['stone_trim'], bevel=0.03)

    # Hipped roof
    pyramid_roof("Roof", w=2.6, d=2.1, h=0.8, overhang=0.15,
                 origin=(0, 0, BZ + wall_h + 0.04), material=m['roof'])

    # Clock face centered high on front wall
    bmesh_prism("ClockFace", 0.18, 0.04, 16, (1.42, 0, BZ + wall_h - 0.30), m['stone_light'])
    # Clock hands (simple lines)
    bmesh_box("ClockH1", (0.03, 0.01, 0.14), (1.44, 0, BZ + wall_h - 0.23), m['iron'])
    bmesh_box("ClockH2", (0.03, 0.10, 0.01), (1.44, 0.03, BZ + wall_h - 0.30), m['iron'])
    # Clock surround
    bmesh_prism("ClockRim", 0.20, 0.02, 16, (1.43, 0, BZ + wall_h - 0.31), m['stone_trim'])

    # Heavy double doors with iron fittings
    bmesh_box("DoorL", (0.08, 0.34, 1.20), (1.41, -0.20, BZ + 0.60), m['door'])
    bmesh_box("DoorR", (0.08, 0.34, 1.20), (1.41, 0.20, BZ + 0.60), m['door'])
    bmesh_box("DoorHead", (0.10, 0.80, 0.08), (1.42, 0, BZ + 1.24), m['stone_trim'])
    for dy in [-0.40, 0.40]:
        bmesh_box(f"DoorPost_{dy:.2f}", (0.10, 0.06, 1.28), (1.42, dy, BZ + 0.64), m['stone_trim'])

    # Ground floor windows with iron shutters
    for y in [-0.75, 0.75]:
        bmesh_box(f"GWin_{y:.2f}", (0.06, 0.24, 0.50), (1.41, y, BZ + 0.55), m['window'])
        bmesh_box(f"GWinHead_{y:.2f}", (0.07, 0.28, 0.04), (1.42, y, BZ + 0.82), m['stone_trim'])
        bmesh_box(f"GWinSill_{y:.2f}", (0.07, 0.28, 0.04), (1.42, y, BZ + 0.32), m['stone_trim'])
        # Iron shutters (closed on one side, open on other)
        bmesh_box(f"ShutterL_{y:.2f}", (0.04, 0.12, 0.48), (1.45, y - 0.14, BZ + 0.55), m['iron'])
        bmesh_box(f"ShutterR_{y:.2f}", (0.04, 0.12, 0.48), (1.45, y + 0.14, BZ + 0.55), m['iron'])

    # Upper floor windows (3 across)
    for y in [-0.65, 0, 0.65]:
        bmesh_box(f"UWin_{y:.2f}", (0.06, 0.22, 0.45), (1.41, y, BZ + 1.65), m['window'])
        bmesh_box(f"UWinHead_{y:.2f}", (0.07, 0.26, 0.04), (1.42, y, BZ + 1.90), m['stone_trim'])

    # Side windows
    for x in [-0.60, 0.40]:
        for z_off in [0.55, 1.65]:
            bmesh_box(f"SWin_{x:.1f}_{z_off:.1f}", (0.22, 0.06, 0.45), (x, -1.16, BZ + z_off), m['window'])

    # Loading bay (large opening on side wall)
    bmesh_box("LoadBay", (0.50, 0.06, 0.80), (-0.70, 1.16, BZ + 0.40), m['door'])
    bmesh_box("LoadBayFrame", (0.58, 0.07, 0.08), (-0.70, 1.17, BZ + 0.84), m['stone_trim'])

    # Loading bay platform outside
    bmesh_box("LoadPlat", (0.70, 0.50, 0.12), (-0.70, 1.40, BZ + 0.06), m['stone_dark'])

    # Iron railings at front
    for i in range(7):
        fy = -0.90 + i * 0.26
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=0.40,
                                            location=(1.55, fy, BZ + 0.10))
        bpy.context.active_object.data.materials.append(m['iron'])
    bmesh_box("FenceRail", (0.02, 1.60, 0.02), (1.55, 0, BZ + 0.28), m['iron'])

    # Steps
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.18, 1.0, 0.04), (1.55 + i * 0.18, 0, BZ - 0.02 - i * 0.04), m['stone_light'])


# ============================================================
# INDUSTRIAL AGE — Steel/brick warehouse, corrugated roof, rail
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Concrete foundation
    bmesh_box("Found", (3.2, 2.6, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.12
    wall_h = 2.8

    # Main brick walls
    bmesh_box("Main", (3.0, 2.4, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Iron structural beams on facade
    for z in [BZ + 1.0, BZ + 2.0]:
        bmesh_box(f"IronH_{z:.1f}", (0.03, 2.4, 0.05), (1.51, 0, z), m['iron'])
    for y in [-1.0, 0, 1.0]:
        bmesh_box(f"IronV_{y:.1f}", (0.03, 0.05, wall_h), (1.51, y, BZ + wall_h / 2), m['iron'])

    # Band between floors
    bmesh_box("Band", (3.04, 2.44, 0.05), (0, 0, BZ + 1.4), m['stone_trim'])

    # Cornice
    bmesh_box("Cornice", (3.08, 2.48, 0.06), (0, 0, BZ + wall_h), m['stone_trim'], bevel=0.02)

    # Corrugated roof (shallow pitch, represented as ridged surface)
    top_z = BZ + wall_h
    # Main roof planes
    rv = [
        (-1.60, -1.30, top_z), (1.60, -1.30, top_z),
        (1.60, 1.30, top_z), (-1.60, 1.30, top_z),
        (0, -1.30, top_z + 0.60), (0, 1.30, top_z + 0.60),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("Roof", rv, rf, m['iron'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Corrugation ridges on roof (visual detail)
    for i in range(8):
        cy = -1.10 + i * 0.31
        bmesh_box(f"Corrug_{i}", (1.60, 0.04, 0.02), (0.80, cy, top_z + 0.28 + 0.01), m['iron'])
        bmesh_box(f"CorругL_{i}", (1.60, 0.04, 0.02), (-0.80, cy, top_z + 0.28 + 0.01), m['iron'])

    # Ridge cap
    bmesh_box("RidgeCap", (0.10, 2.64, 0.04), (0, 0, top_z + 0.60), m['iron'])

    # Large rolling doors (industrial)
    bmesh_box("RollDoor", (0.08, 0.80, 1.60), (1.51, -0.30, BZ + 0.80), m['iron'])
    bmesh_box("RollDoorFrame", (0.10, 0.90, 0.08), (1.52, -0.30, BZ + 1.64), m['stone_trim'])
    for dy in [-0.45, 0.45]:
        bmesh_box(f"RollDoorPost_{dy:.2f}", (0.10, 0.06, 1.68), (1.52, -0.30 + dy, BZ + 0.84), m['stone_trim'])
    # Door horizontal slats (rolling door texture)
    for dz in [0.20, 0.50, 0.80, 1.10, 1.40]:
        bmesh_box(f"RollSlat_{dz:.1f}", (0.04, 0.78, 0.02), (1.55, -0.30, BZ + dz), m['stone_dark'])

    # Personnel door
    bmesh_box("SmallDoor", (0.06, 0.35, 1.10), (1.51, 0.70, BZ + 0.55), m['door'])

    # Windows (industrial style)
    for y in [-0.90, 0.70]:
        bmesh_box(f"Win_{y:.1f}", (0.06, 0.28, 0.45), (1.51, y, BZ + 2.20), m['window'])
        # Iron mullion cross
        bmesh_box(f"WinMullH_{y:.1f}", (0.04, 0.26, 0.02), (1.53, y, BZ + 2.20), m['iron'])
        bmesh_box(f"WinMullV_{y:.1f}", (0.04, 0.02, 0.43), (1.53, y, BZ + 2.20), m['iron'])

    # Side windows
    for x in [-0.80, 0.20]:
        bmesh_box(f"SWin_{x:.1f}", (0.28, 0.06, 0.45), (x, -1.21, BZ + 2.20), m['window'])

    # Rail platform (raised concrete platform along one side)
    bmesh_box("RailPlat", (3.0, 0.50, 0.20), (0, 1.45, BZ + 0.10), m['stone_dark'])
    # Rails (two parallel iron strips)
    for ry in [1.75, 1.85]:
        bmesh_box(f"Rail_{ry:.2f}", (3.2, 0.04, 0.04), (0, ry, Z + 0.06), m['iron'])
    # Rail ties
    for i in range(10):
        rx = -1.40 + i * 0.32
        bmesh_box(f"Tie_{i}", (0.06, 0.30, 0.03), (rx, 1.80, Z + 0.03), m['wood_dark'])

    # Overhead crane (steel beam spanning across the top)
    bmesh_box("CraneBeam", (3.0, 0.08, 0.08), (0, 0, top_z + 0.70), m['iron'])
    # Crane trolley
    bmesh_box("CraneTrolley", (0.20, 0.14, 0.10), (0.50, 0, top_z + 0.62), m['iron'])
    # Crane hoist (hanging)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.80,
                                        location=(0.50, 0, top_z + 0.20))
    bpy.context.active_object.data.materials.append(m['iron'])
    # Hook
    bmesh_box("Hook", (0.06, 0.04, 0.06), (0.50, 0, top_z - 0.18), m['iron'])

    # Chimney / vent stack
    bmesh_prism("VentStack", 0.10, 0.80, 8, (-1.20, 0.90, top_z + 0.10), m['iron'])


# ============================================================
# MODERN AGE — Concrete storage facility, roll-up doors
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.08
    bmesh_box("Found", (3.4, 2.8, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    wall_h = 2.4

    # Main concrete box
    bmesh_box("Main", (3.0, 2.4, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Flat roof with slight overhang
    bmesh_box("Roof", (3.2, 2.6, 0.10), (0, 0, BZ + wall_h + 0.05), m['stone_dark'])

    # Parapet (low wall around roof edge)
    for pos, size in [
        ((1.60, 0), (0.06, 2.6, 0.18)),
        ((-1.60, 0), (0.06, 2.6, 0.18)),
        ((0, 1.30), (3.2, 0.06, 0.18)),
        ((0, -1.30), (3.2, 0.06, 0.18)),
    ]:
        bmesh_box(f"Parapet_{pos[0]:.1f}_{pos[1]:.1f}", size,
                  (pos[0], pos[1], BZ + wall_h + 0.10 + 0.09), m['stone_dark'])

    # Roll-up doors (2 large bays)
    for i, dy in enumerate([-0.55, 0.55]):
        bmesh_box(f"RollDoor_{i}", (0.06, 0.70, 1.60), (1.51, dy, BZ + 0.80), metal)
        bmesh_box(f"RollFrame_{i}", (0.08, 0.78, 0.06), (1.52, dy, BZ + 1.63), metal)
        for ddy in [-0.39, 0.39]:
            bmesh_box(f"RollPost_{i}_{ddy:.2f}", (0.08, 0.04, 1.66), (1.52, dy + ddy, BZ + 0.83), metal)
        # Roll-up slats
        for j in range(6):
            bmesh_box(f"Slat_{i}_{j}", (0.04, 0.68, 0.02), (1.55, dy, BZ + 0.15 + j * 0.28), m['stone_dark'])

    # Personnel door
    bmesh_box("SmallDoor", (0.06, 0.40, 1.10), (1.51, -1.05, BZ + 0.55), m['door'])
    bmesh_box("SmallDoorFrame", (0.07, 0.44, 1.14), (1.52, -1.05, BZ + 0.57), metal)

    # Windows (high strip windows)
    bmesh_box("StripWin", (0.06, 2.0, 0.30), (1.51, 0, BZ + wall_h - 0.30), glass)
    # Window mullions
    for y in [-0.60, 0, 0.60]:
        bmesh_box(f"WinMull_{y:.1f}", (0.04, 0.03, 0.28), (1.53, y, BZ + wall_h - 0.30), metal)

    # Side windows
    for x in [-0.80, 0.40]:
        bmesh_box(f"SWin_{x:.1f}", (0.30, 0.06, 0.25), (x, -1.21, BZ + wall_h - 0.30), glass)

    # Loading dock (raised concrete platform)
    bmesh_box("Dock", (1.00, 2.4, 0.30), (1.65, 0, BZ + 0.15), m['stone_dark'])
    # Dock bumpers (rubber stops)
    for dy in [-0.55, 0.55]:
        bmesh_box(f"Bumper_{dy:.2f}", (0.06, 0.10, 0.20), (1.52, dy, BZ + 0.15), m['stone_dark'])

    # Forklift area — simplified forklift
    # Forklift body
    bmesh_box("ForkBody", (0.30, 0.20, 0.25), (0.80, -1.35, BZ + 0.30 + 0.125), m['gold'])
    # Forklift mast
    bmesh_box("ForkMast", (0.04, 0.18, 0.50), (0.95, -1.35, BZ + 0.50), metal)
    # Forks
    for fy in [-1.42, -1.28]:
        bmesh_box(f"Fork_{fy:.2f}", (0.25, 0.03, 0.02), (1.05, fy, BZ + 0.10), metal)
    # Forklift wheels
    for fx, fy in [(0.70, -1.42), (0.70, -1.28), (0.90, -1.42), (0.90, -1.28)]:
        bmesh_prism(f"ForkWheel_{fx:.2f}_{fy:.2f}", 0.05, 0.03, 8, (fx, fy, BZ + 0.05), m['stone_dark'])

    # Bollards (safety posts near dock)
    for i in range(3):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=0.35,
                                            location=(1.10 + i * 0.30, -1.10, BZ + 0.175))
        bpy.context.active_object.data.materials.append(m['gold'])

    # Address / signage panel
    bmesh_box("Sign", (0.06, 0.60, 0.20), (1.52, 0, BZ + wall_h - 0.65), m['stone_light'])


# ============================================================
# DIGITAL AGE — Automated warehouse, robotic arm, conveyor
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.06
    bmesh_box("Found", (3.4, 2.8, 0.06), (0, 0, Z + 0.03), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    wall_h = 2.6

    # Main cube structure (glass and metal)
    bmesh_box("Main", (3.0, 2.4, wall_h), (0, 0, BZ + wall_h / 2), metal, bevel=0.02)

    # Glass panels on front face
    bmesh_box("GlassFront", (0.06, 2.0, wall_h - 0.40), (1.51, 0, BZ + wall_h / 2 + 0.10), glass)
    # Structural mullions
    for y in [-0.80, -0.30, 0.30, 0.80]:
        bmesh_box(f"MullV_{y:.1f}", (0.04, 0.04, wall_h - 0.40), (1.53, y, BZ + wall_h / 2 + 0.10), metal)
    for z_off in [0.80, 1.60]:
        bmesh_box(f"MullH_{z_off:.1f}", (0.04, 2.0, 0.04), (1.53, 0, BZ + z_off), metal)

    # Glass panel on side
    bmesh_box("GlassSide", (1.50, 0.06, wall_h - 0.40), (-0.40, -1.21, BZ + wall_h / 2 + 0.10), glass)
    for x in [-0.90, -0.40, 0.10]:
        bmesh_box(f"SMullV_{x:.1f}", (0.04, 0.04, wall_h - 0.40), (x, -1.23, BZ + wall_h / 2 + 0.10), metal)

    # Flat roof with rooftop equipment
    bmesh_box("Roof", (3.2, 2.6, 0.10), (0, 0, BZ + wall_h + 0.05), metal)

    # HVAC units on roof
    bmesh_box("HVAC1", (0.40, 0.40, 0.25), (-0.80, 0.60, BZ + wall_h + 0.10 + 0.125), m['stone_dark'])
    bmesh_box("HVAC2", (0.30, 0.30, 0.20), (-0.80, -0.40, BZ + wall_h + 0.10 + 0.10), m['stone_dark'])

    # Automated roll-up door (single, large)
    bmesh_box("AutoDoor", (0.06, 0.90, 1.80), (1.51, 0, BZ + 0.90), m['stone_dark'])
    bmesh_box("AutoDoorFrame", (0.08, 1.00, 0.06), (1.52, 0, BZ + 1.83), metal)
    for dy in [-0.50, 0.50]:
        bmesh_box(f"AutoDoorPost_{dy:.2f}", (0.08, 0.04, 1.86), (1.52, dy, BZ + 0.93), metal)

    # LED indicator strips along door frame
    bmesh_box("LEDTop", (0.04, 0.96, 0.03), (1.54, 0, BZ + 1.86), m['gold'])
    for dy in [-0.50, 0.50]:
        bmesh_box(f"LEDSide_{dy:.2f}", (0.04, 0.03, 1.80), (1.54, dy, BZ + 0.93), m['gold'])

    # Robotic arm (inside, visible through glass)
    # Arm base
    bmesh_prism("ArmBase", 0.15, 0.10, 12, (0, 0.30, BZ), metal)
    # Arm segment 1 (vertical)
    bmesh_box("ArmSeg1", (0.08, 0.08, 0.80), (0, 0.30, BZ + 0.50), metal)
    # Arm joint
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0, 0.30, BZ + 0.90))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()
    # Arm segment 2 (angled outward)
    arm2_v = [(0.02, 0.26, BZ + 0.90), (-0.02, 0.26, BZ + 0.90),
              (0.35, 0.26, BZ + 1.30), (0.39, 0.26, BZ + 1.30)]
    mesh_from_pydata("ArmSeg2", arm2_v, [(0, 1, 2, 3)], metal)
    arm2_v2 = [(0.02, 0.34, BZ + 0.90), (-0.02, 0.34, BZ + 0.90),
               (0.35, 0.34, BZ + 1.30), (0.39, 0.34, BZ + 1.30)]
    mesh_from_pydata("ArmSeg2B", arm2_v2, [(0, 1, 2, 3)], metal)
    # Gripper
    bmesh_box("Gripper", (0.06, 0.10, 0.06), (0.37, 0.30, BZ + 1.30), m['iron'])

    # Conveyor belt (running from side to front)
    bmesh_box("ConveyorBed", (2.0, 0.30, 0.06), (0, -0.50, BZ + 0.40), m['stone_dark'])
    # Conveyor rollers
    for i in range(12):
        cx = -0.90 + i * 0.16
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=0.28,
                                            location=(cx, -0.50, BZ + 0.44))
        roller = bpy.context.active_object
        roller.name = f"Roller_{i}"
        roller.rotation_euler = (math.radians(90), 0, 0)
        roller.data.materials.append(metal)
    # Conveyor legs
    for cx in [-0.80, 0, 0.80]:
        for cy in [-0.62, -0.38]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.40,
                                                location=(cx, cy, BZ + 0.20))
            bpy.context.active_object.data.materials.append(metal)

    # Packages on conveyor
    for i, (px, c) in enumerate([(0.20, 0.16), (-0.30, 0.14), (-0.70, 0.12)]):
        bmesh_box(f"Package_{i}", (c, c, c * 0.8), (px, -0.50, BZ + 0.44 + c * 0.4), m['stone'])

    # LED status panel near door
    bmesh_box("StatusPanel", (0.06, 0.30, 0.18), (1.52, -0.70, BZ + 1.50), m['stone_dark'])
    # LED indicators (3 small colored lights)
    for i, dz in enumerate([0.04, 0.0, -0.04]):
        bmesh_box(f"LED_{i}", (0.04, 0.04, 0.03), (1.55, -0.70, BZ + 1.54 + dz), m['gold'])

    # Antenna / communications array on roof
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.50,
                                        location=(0.80, 0.80, BZ + wall_h + 0.35))
    bpy.context.active_object.data.materials.append(metal)
    # Dish
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0.80, 0.80, BZ + wall_h + 0.62))
    dish = bpy.context.active_object
    dish.name = "Dish"
    dish.scale = (1, 1, 0.3)
    dish.data.materials.append(metal)
    bpy.ops.object.shade_smooth()

    # Solar panels on roof
    for sx in [-0.40, 0.20]:
        bmesh_box(f"Solar_{sx:.1f}", (0.50, 0.60, 0.03), (sx, -0.20, BZ + wall_h + 0.14), glass)
        bmesh_box(f"SolarFrame_{sx:.1f}", (0.52, 0.62, 0.02), (sx, -0.20, BZ + wall_h + 0.12), metal)

    # Entrance path
    bmesh_box("Path", (0.50, 0.80, 0.03), (1.65, 0, BZ + 0.015), m['stone_light'])

    # LED accent ring around base
    bmesh_prism("LEDRing", 1.65, 0.03, 16, (0, 0, BZ + 0.02), m['gold'])


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


def build_storage(materials, age='medieval'):
    """Build a Storage building with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
