"""
Market building — 3x2 tile trading building, the commercial heart of every
civilization. Ground plane 5.0 x 3.5.

Stone:         Open-air trading post — wooden frame shelters, laid-out goods, campfire
Bronze:        Bazaar stalls with cloth awnings, merchant booth, weighing scale
Iron:          Covered market hall with wooden pillars, thatched roof, stall counters
Classical:     Roman forum/agora — columned portico, open courtyard, fountain
Medieval:      Timber-framed market hall, open sides, central well, guild signs
Gunpowder:     Stone market house with arcade arches, clock tower, covered stalls
Enlightenment: Elegant market hall with iron/glass roof, symmetrical wings
Industrial:    Steel and glass market pavilion, iron columns, clock, loading docks
Modern:        Shopping center — glass storefront, parking area, signage
Digital:       E-commerce hub — sleek glass building, drone pads, holographic displays
"""

import bpy
import bmesh
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# Ground plane dimensions for all ages (3x2 tile = 5.0 x 3.5)
GW = 5.0
GD = 3.5


# ============================================================
# STONE AGE — Open-air trading post with wooden frame shelters
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (GW, GD, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Dirt platform for the trading area
    bmesh_prism("DirtPlat", 1.8, 0.06, 12, (0, 0, Z), m['stone_dark'])

    # ------- Main shelter (wooden A-frame) -------
    # Two pairs of leaning poles forming an A-frame
    for side in [-1, 1]:
        for dy in [-0.6, 0.6]:
            sv = [(side * 0.8, dy - 0.03, Z + 0.06), (side * 0.8, dy + 0.03, Z + 0.06),
                  (0, dy + 0.03, Z + 1.5), (0, dy - 0.03, Z + 1.5)]
            mesh_from_pydata(f"APole_{side}_{dy:.1f}", sv, [(0, 1, 2, 3)], m['wood'])

    # Ridge pole along the top
    bmesh_box("Ridge", (0.05, 1.3, 0.05), (0, 0, Z + 1.50), m['wood_dark'])

    # Thatch covering draped over A-frame
    rv = [(-0.85, -0.65, Z + 0.30), (0.85, -0.65, Z + 0.30),
          (0.85, 0.65, Z + 0.30), (-0.85, 0.65, Z + 0.30),
          (-0.15, -0.65, Z + 1.45), (0.15, -0.65, Z + 1.45),
          (0.15, 0.65, Z + 1.45), (-0.15, 0.65, Z + 1.45)]
    rf = [(0, 3, 7, 4), (1, 2, 6, 5), (4, 5, 6, 7)]
    mesh_from_pydata("ThatchCover", rv, rf, m['roof'])

    # ------- Second smaller shelter (lean-to) -------
    # Poles
    for dy in [-0.4, 0.4]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=1.1,
                                            location=(-1.6, dy, Z + 0.55))
        bpy.context.active_object.name = f"LeanPole_{dy:.1f}"
        bpy.context.active_object.data.materials.append(m['wood'])

    # Lean-to roof (angled thatch)
    lv = [(-1.95, -0.50, Z + 0.75), (-1.25, -0.50, Z + 1.15),
          (-1.25, 0.50, Z + 1.15), (-1.95, 0.50, Z + 0.75)]
    mesh_from_pydata("LeanRoof", lv, [(0, 1, 2, 3)], m['roof'])

    # ------- Goods on the ground -------
    # Baskets (small cylinders)
    for pos in [(0.3, -0.3), (-0.2, 0.3), (0.5, 0.1)]:
        bmesh_prism(f"Basket_{pos[0]:.1f}_{pos[1]:.1f}", 0.10, 0.12, 8,
                    (pos[0], pos[1], Z + 0.06), m['wood_dark'])

    # Pots (small spheres)
    for pos in [(-0.4, -0.2), (0.1, 0.5)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(pos[0], pos[1], Z + 0.13))
        pot = bpy.context.active_object
        pot.name = f"Pot_{pos[0]:.1f}"
        pot.scale = (1, 1, 0.8)
        pot.data.materials.append(m['stone'])

    # Laid-out fur/hide for display
    bmesh_box("Hide", (0.6, 0.4, 0.02), (0.2, 0, Z + 0.07), m['roof_edge'])

    # ------- Campfire -------
    bmesh_prism("FireRing", 0.20, 0.08, 8, (1.2, -0.6, Z + 0.04), m['stone_dark'])
    # Fire logs
    for i, a in enumerate([0, 1.2, 2.4]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.30,
                                            location=(1.2, -0.6, Z + 0.12))
        log = bpy.context.active_object
        log.name = f"FireLog_{i}"
        log.rotation_euler = (math.radians(90), 0, a)
        log.data.materials.append(m['wood_dark'])

    # ------- Totem/trade marker -------
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=1.6,
                                        location=(1.6, 0.8, Z + 0.80))
    bpy.context.active_object.name = "Totem"
    bpy.context.active_object.data.materials.append(m['wood'])
    # Totem top decoration
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(1.6, 0.8, Z + 1.64))
    bpy.context.active_object.name = "TotemTop"
    bpy.context.active_object.data.materials.append(m['gold'])

    # Sitting logs for traders
    for px in [-1.0, 0.8]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=0.5,
                                            location=(px, -0.9, Z + 0.10))
        log = bpy.context.active_object
        log.name = f"SitLog_{px:.1f}"
        log.rotation_euler = (0, math.radians(90), math.radians(30))
        log.data.materials.append(m['wood_dark'])


# ============================================================
# BRONZE AGE — Bazaar stalls with cloth awnings, weighing scale
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (GW, GD, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Raised platform
    bmesh_box("Platform", (4.2, 2.8, 0.10), (0, 0, Z + 0.05), m['stone_dark'], bevel=0.02)

    BZ = Z + 0.10

    # ------- Stall 1 (left) with cloth awning -------
    # Four poles
    for dx, dy in [(-1.7, -0.8), (-1.7, 0.8), (-0.5, -0.8), (-0.5, 0.8)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.035, depth=1.6,
                                            location=(dx, dy, BZ + 0.80))
        bpy.context.active_object.name = f"StallPole1_{dx:.1f}_{dy:.1f}"
        bpy.context.active_object.data.materials.append(m['wood'])

    # Awning cloth (angled slightly)
    av = [(-1.80, -0.90, BZ + 1.65), (-0.40, -0.90, BZ + 1.55),
          (-0.40, 0.90, BZ + 1.55), (-1.80, 0.90, BZ + 1.65)]
    aw = mesh_from_pydata("Awning1", av, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False

    # Counter
    bmesh_box("Counter1", (1.1, 1.4, 0.08), (-1.1, 0, BZ + 0.65), m['wood_dark'])
    # Counter legs
    for dx, dy in [(-1.6, -0.6), (-1.6, 0.6), (-0.6, -0.6), (-0.6, 0.6)]:
        bmesh_box(f"CntrLeg1_{dx:.1f}_{dy:.1f}", (0.06, 0.06, 0.55),
                  (dx, dy, BZ + 0.375), m['wood'])

    # Goods on counter
    for i, pos in enumerate([(-1.3, -0.3), (-1.0, 0.2), (-0.8, -0.1)]):
        bmesh_prism(f"Good1_{i}", 0.08, 0.10, 8, (pos[0], pos[1], BZ + 0.69), m['stone'])

    # ------- Stall 2 (right) with cloth awning -------
    for dx, dy in [(0.5, -0.8), (0.5, 0.8), (1.7, -0.8), (1.7, 0.8)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.035, depth=1.6,
                                            location=(dx, dy, BZ + 0.80))
        bpy.context.active_object.name = f"StallPole2_{dx:.1f}_{dy:.1f}"
        bpy.context.active_object.data.materials.append(m['wood'])

    # Awning cloth
    av2 = [(0.40, -0.90, BZ + 1.55), (1.80, -0.90, BZ + 1.65),
           (1.80, 0.90, BZ + 1.65), (0.40, 0.90, BZ + 1.55)]
    mesh_from_pydata("Awning2", av2, [(0, 1, 2, 3)], m['roof'])

    # Counter
    bmesh_box("Counter2", (1.1, 1.4, 0.08), (1.1, 0, BZ + 0.65), m['wood_dark'])
    for dx, dy in [(0.6, -0.6), (0.6, 0.6), (1.6, -0.6), (1.6, 0.6)]:
        bmesh_box(f"CntrLeg2_{dx:.1f}_{dy:.1f}", (0.06, 0.06, 0.55),
                  (dx, dy, BZ + 0.375), m['wood'])

    # Goods on counter 2
    for i, pos in enumerate([(0.8, 0.3), (1.2, -0.2), (1.4, 0.1)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(pos[0], pos[1], BZ + 0.75))
        bpy.context.active_object.name = f"Good2_{i}"
        bpy.context.active_object.data.materials.append(m['gold'])

    # ------- Merchant's booth (center back) -------
    bmesh_box("Booth", (0.8, 0.6, 1.0), (0, -1.0, BZ + 0.50), m['stone'], bevel=0.02)
    bmesh_box("BoothTop", (0.9, 0.7, 0.06), (0, -1.0, BZ + 1.03), m['wood_dark'])

    # ------- Weighing scale -------
    # Central pole
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=0.50,
                                        location=(0, 0.2, BZ + 0.90))
    bpy.context.active_object.name = "ScalePole"
    bpy.context.active_object.data.materials.append(m['gold'])
    # Crossbar
    bmesh_box("ScaleBar", (0.03, 0.40, 0.03), (0, 0.2, BZ + 1.14), m['gold'])
    # Pans (flat discs)
    for dy in [-0.18, 0.18]:
        bmesh_prism(f"ScalePan_{dy:.2f}", 0.07, 0.02, 10,
                    (0, 0.2 + dy, BZ + 1.02), m['gold'])

    # Scale base
    bmesh_box("ScaleBase", (0.12, 0.12, 0.04), (0, 0.2, BZ + 0.67), m['stone_dark'])

    # ------- Goods piles on ground -------
    # Sacks
    for pos in [(-0.3, 1.0), (0.4, 1.0), (-1.5, -1.1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10,
                                              location=(pos[0], pos[1], BZ + 0.12))
        sack = bpy.context.active_object
        sack.name = f"Sack_{pos[0]:.1f}"
        sack.scale = (1, 0.8, 0.6)
        sack.data.materials.append(m['roof_edge'])

    # Pottery jars
    for px in [1.8, -1.8]:
        bmesh_prism(f"Jar_{px:.1f}", 0.08, 0.22, 8, (px, 0, BZ), m['stone'])


# ============================================================
# IRON AGE — Covered market hall with wooden pillars, thatched roof
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (GW, GD, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stone foundation
    bmesh_box("Found", (4.4, 2.8, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.15
    wall_h = 1.8

    # ------- Main hall walls (partial height, open front/back) -------
    # Side walls (full)
    bmesh_box("WallLeft", (4.0, 0.15, wall_h), (0, -1.25, BZ + wall_h / 2), m['stone'], bevel=0.02)
    bmesh_box("WallRight", (4.0, 0.15, wall_h), (0, 1.25, BZ + wall_h / 2), m['stone'], bevel=0.02)
    # Back wall
    bmesh_box("WallBack", (0.15, 2.5, wall_h), (-2.0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # ------- Wooden pillars (open front and along sides) -------
    pillar_positions = [
        (2.0, -1.15), (2.0, 0), (2.0, 1.15),
        (0.7, -1.15), (0.7, 1.15),
        (-0.6, -1.15), (-0.6, 1.15),
    ]
    for px, py in pillar_positions:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=wall_h,
                                            location=(px, py, BZ + wall_h / 2))
        p = bpy.context.active_object
        p.name = f"Pillar_{px:.1f}_{py:.1f}"
        p.data.materials.append(m['wood'])
        # Pillar base
        bmesh_box(f"PBase_{px:.1f}_{py:.1f}", (0.20, 0.20, 0.06),
                  (px, py, BZ + 0.03), m['stone_dark'])

    # ------- Thatched roof (large gabled) -------
    rv = [
        (-2.30, -1.50, BZ + wall_h), (2.30, -1.50, BZ + wall_h),
        (2.30, 1.50, BZ + wall_h), (-2.30, 1.50, BZ + wall_h),
        (0, -1.50, BZ + wall_h + 1.1), (0, 1.50, BZ + wall_h + 1.1),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("Roof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Ridge beam
    bmesh_box("Ridge", (0.08, 3.04, 0.08), (0, 0, BZ + wall_h + 1.10), m['wood_dark'])

    # Roof edge trim
    bmesh_box("RoofEdgeF", (0.06, 3.04, 0.06), (2.30, 0, BZ + wall_h + 0.03), m['wood_dark'])
    bmesh_box("RoofEdgeB", (0.06, 3.04, 0.06), (-2.30, 0, BZ + wall_h + 0.03), m['wood_dark'])

    # ------- Stall counters inside -------
    # Left row of stalls
    for i, cx in enumerate([-1.3, -0.1, 1.1]):
        bmesh_box(f"StallCntr_{i}", (0.9, 0.5, 0.08), (cx, -0.7, BZ + 0.70), m['wood_dark'])
        # Legs
        for ldx in [-0.35, 0.35]:
            bmesh_box(f"StallLeg_{i}_{ldx:.1f}", (0.06, 0.06, 0.62),
                      (cx + ldx, -0.7, BZ + 0.37), m['wood'])
        # Goods on counter
        bmesh_prism(f"Goods_{i}", 0.08, 0.12, 8, (cx, -0.7, BZ + 0.74), m['stone'])

    # Right row of stalls
    for i, cx in enumerate([-1.3, -0.1, 1.1]):
        bmesh_box(f"StallCntrR_{i}", (0.9, 0.5, 0.08), (cx, 0.7, BZ + 0.70), m['wood_dark'])
        for ldx in [-0.35, 0.35]:
            bmesh_box(f"StallLegR_{i}_{ldx:.1f}", (0.06, 0.06, 0.62),
                      (cx + ldx, 0.7, BZ + 0.37), m['wood'])
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07,
                                              location=(cx + 0.1, 0.7, BZ + 0.81))
        bpy.context.active_object.name = f"GoodsR_{i}"
        bpy.context.active_object.data.materials.append(m['gold'])

    # ------- Goods storage at back -------
    # Crates
    for i, pos in enumerate([(-1.6, -0.3), (-1.6, 0.3)]):
        bmesh_box(f"Crate_{i}", (0.25, 0.25, 0.25), (pos[0], pos[1], BZ + 0.125), m['wood_dark'])

    # Barrels
    for py in [-0.8, 0.8]:
        bmesh_prism(f"Barrel_{py:.1f}", 0.10, 0.28, 8, (-1.7, py, BZ), m['wood_dark'])

    # ------- Stone band on side walls -------
    bmesh_box("BandL", (4.04, 0.16, 0.06), (0, -1.25, BZ + 0.9), m['stone_trim'])
    bmesh_box("BandR", (4.04, 0.16, 0.06), (0, 1.25, BZ + 0.9), m['stone_trim'])

    # ------- Steps at entrance -------
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.16, 1.6, 0.05),
                  (2.30 + i * 0.18, 0, BZ - 0.03 - i * 0.05), m['stone_dark'])


# ============================================================
# CLASSICAL AGE — Roman forum/agora with columned portico
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (GW, GD, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stepped platform (3 tiers)
    for i in range(3):
        w = 4.6 - i * 0.15
        d = 3.0 - i * 0.10
        bmesh_box(f"Plat_{i}", (w, d, 0.06), (0, 0, Z + 0.03 + i * 0.06), m['stone_light'], bevel=0.01)

    BZ = Z + 0.18
    wall_h = 1.8

    # ------- Back colonnade (portico) -------
    col_h = 1.7
    for py in [-1.0, -0.5, 0, 0.5, 1.0]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=col_h,
                                            location=(-1.6, py, BZ + col_h / 2))
        c = bpy.context.active_object
        c.name = f"ColBack_{py:.1f}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        # Capital
        bmesh_box(f"CapBack_{py:.1f}", (0.20, 0.20, 0.06), (-1.6, py, BZ + col_h + 0.03), m['stone_trim'])
        # Base
        bmesh_box(f"BaseBack_{py:.1f}", (0.18, 0.18, 0.04), (-1.6, py, BZ + 0.02), m['stone_trim'])

    # Portico entablature
    bmesh_box("Entablature", (0.30, 2.3, 0.12), (-1.6, 0, BZ + col_h + 0.12), m['stone_trim'], bevel=0.02)

    # Portico roof (flat slab)
    bmesh_box("PorticoRoof", (0.50, 2.5, 0.08), (-1.6, 0, BZ + col_h + 0.22), m['stone_light'])

    # ------- Front colonnade -------
    for py in [-1.0, -0.5, 0, 0.5, 1.0]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=col_h,
                                            location=(1.6, py, BZ + col_h / 2))
        c = bpy.context.active_object
        c.name = f"ColFront_{py:.1f}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        bmesh_box(f"CapFront_{py:.1f}", (0.20, 0.20, 0.06), (1.6, py, BZ + col_h + 0.03), m['stone_trim'])
        bmesh_box(f"BaseFront_{py:.1f}", (0.18, 0.18, 0.04), (1.6, py, BZ + 0.02), m['stone_trim'])

    bmesh_box("EntablatureF", (0.30, 2.3, 0.12), (1.6, 0, BZ + col_h + 0.12), m['stone_trim'], bevel=0.02)

    # ------- Side walls connecting colonnades -------
    bmesh_box("SideWallL", (3.0, 0.15, wall_h * 0.5), (0, -1.20, BZ + wall_h * 0.25), m['stone'], bevel=0.02)
    bmesh_box("SideWallR", (3.0, 0.15, wall_h * 0.5), (0, 1.20, BZ + wall_h * 0.25), m['stone'], bevel=0.02)

    # ------- Main pitched roof over the entire structure -------
    rv = [
        (-2.00, -1.40, BZ + wall_h), (2.00, -1.40, BZ + wall_h),
        (2.00, 1.40, BZ + wall_h), (-2.00, 1.40, BZ + wall_h),
        (0, -1.40, BZ + wall_h + 0.8), (0, 1.40, BZ + wall_h + 0.8),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("Roof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Front pediment
    pv = [(2.02, -1.20, BZ + wall_h), (2.02, 1.20, BZ + wall_h),
          (2.02, 0, BZ + wall_h + 0.75)]
    mesh_from_pydata("Pediment", pv, [(0, 1, 2)], m['stone_light'])

    # ------- Central fountain -------
    bmesh_prism("FountainBase", 0.35, 0.10, 12, (0, 0, BZ), m['stone_light'])
    bmesh_prism("FountainBowl", 0.30, 0.25, 12, (0, 0, BZ + 0.10), m['stone_trim'])
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05, depth=0.50,
                                        location=(0, 0, BZ + 0.50))
    bpy.context.active_object.name = "FountainSpout"
    bpy.context.active_object.data.materials.append(m['stone_light'])

    # Fountain top ornament
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0, 0, BZ + 0.78))
    bpy.context.active_object.name = "FountainOrn"
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # ------- Merchant stalls (stone benches along sides) -------
    for i, cx in enumerate([-0.7, 0.7]):
        for side in [-1, 1]:
            bmesh_box(f"Bench_{cx:.1f}_{side}", (0.6, 0.30, 0.35),
                      (cx, side * 0.80, BZ + 0.175), m['stone_light'])
            # Goods on benches
            bmesh_prism(f"BGoods_{cx:.1f}_{side}", 0.06, 0.10, 8,
                        (cx, side * 0.80, BZ + 0.35), m['gold'])

    # ------- Steps at front entrance -------
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.16, 2.0, 0.05),
                  (2.20 + i * 0.18, 0, BZ - 0.03 - i * 0.05), m['stone_light'])

    # Gold acroterion on pediment peak
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(2.02, 0, BZ + wall_h + 0.82))
    bpy.context.active_object.name = "Acroterion"
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()


# ============================================================
# MEDIEVAL AGE — Timber-framed market hall, open sides, central well
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (GW, GD, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stone foundation
    bmesh_box("Found", (4.4, 2.8, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.18
    wall_h = 2.0

    # ------- Timber pillars (open sides) -------
    pillar_pos = [
        (-1.8, -1.1), (-1.8, 0), (-1.8, 1.1),
        (-0.6, -1.1), (-0.6, 1.1),
        (0.6, -1.1), (0.6, 1.1),
        (1.8, -1.1), (1.8, 0), (1.8, 1.1),
    ]
    for px, py in pillar_pos:
        bmesh_box(f"Pillar_{px:.1f}_{py:.1f}", (0.14, 0.14, wall_h),
                  (px, py, BZ + wall_h / 2), m['wood_beam'])
        # Stone base pad
        bmesh_box(f"PilBase_{px:.1f}_{py:.1f}", (0.22, 0.22, 0.06),
                  (px, py, BZ + 0.03), m['stone_dark'])

    # ------- Horizontal beams connecting pillars -------
    # Top plate beams (long axis)
    for py in [-1.1, 1.1]:
        bmesh_box(f"TopPlate_{py:.1f}", (3.7, 0.10, 0.10),
                  (0, py, BZ + wall_h - 0.05), m['wood_beam'])
    # Cross beams
    for px in [-1.8, -0.6, 0.6, 1.8]:
        bmesh_box(f"CrossBeam_{px:.1f}", (0.10, 2.3, 0.10),
                  (px, 0, BZ + wall_h - 0.05), m['wood_beam'])

    # Knee braces at corners
    for px, py in [(-1.8, -1.1), (-1.8, 1.1), (1.8, -1.1), (1.8, 1.1)]:
        sx = 1 if px > 0 else -1
        sy = 1 if py > 0 else -1
        bv = [(px, py, BZ + wall_h - 0.15),
              (px, py, BZ + wall_h - 0.10),
              (px - sx * 0.40, py, BZ + wall_h - 0.10),
              (px - sx * 0.40, py, BZ + wall_h - 0.15)]
        mesh_from_pydata(f"KneeBrace_{px:.1f}_{py:.1f}", bv, [(0, 1, 2, 3)], m['wood_dark'])

    # ------- Steep pitched roof -------
    rv = [
        (-2.10, -1.35, BZ + wall_h), (2.10, -1.35, BZ + wall_h),
        (2.10, 1.35, BZ + wall_h), (-2.10, 1.35, BZ + wall_h),
        (0, -1.35, BZ + wall_h + 1.3), (0, 1.35, BZ + wall_h + 1.3),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("Roof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Ridge beam
    bmesh_box("Ridge", (0.08, 2.74, 0.08), (0, 0, BZ + wall_h + 1.30), m['wood_dark'])

    # Roof edge trim
    bmesh_box("RoofEdgeF", (0.06, 2.74, 0.06), (2.10, 0, BZ + wall_h + 0.03), m['wood_dark'])
    bmesh_box("RoofEdgeB", (0.06, 2.74, 0.06), (-2.10, 0, BZ + wall_h + 0.03), m['wood_dark'])

    # ------- Central well/fountain -------
    bmesh_prism("WellBase", 0.30, 0.35, 8, (0, 0, BZ), m['stone'])
    # Well rim
    bmesh_prism("WellRim", 0.35, 0.06, 8, (0, 0, BZ + 0.35), m['stone_trim'])
    # Well roof posts
    for dy in [-0.20, 0.20]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.70,
                                            location=(0, dy, BZ + 0.70))
        bpy.context.active_object.name = f"WellPost_{dy:.1f}"
        bpy.context.active_object.data.materials.append(m['wood'])
    # Well roof
    rv2 = [(-0.20, -0.25, BZ + 1.05), (0.20, -0.25, BZ + 1.05),
           (0.20, 0.25, BZ + 1.05), (-0.20, 0.25, BZ + 1.05),
           (0, 0, BZ + 1.25)]
    mesh_from_pydata("WellRoof", rv2, [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], m['roof'])

    # ------- Goods crates and barrels -------
    for i, pos in enumerate([(1.2, -0.6), (1.4, 0.4), (-1.2, 0.5)]):
        bmesh_box(f"Crate_{i}", (0.25, 0.25, 0.25), (pos[0], pos[1], BZ + 0.125), m['wood_dark'])

    for i, pos in enumerate([(-1.3, -0.6), (1.0, 0.8)]):
        bmesh_prism(f"Barrel_{i}", 0.10, 0.28, 8, (pos[0], pos[1], BZ), m['wood_dark'])

    # ------- Guild signs (hanging boards) -------
    # Sign post
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.80,
                                        location=(1.8, 0, BZ + wall_h + 0.40))
    bpy.context.active_object.name = "SignPost"
    bpy.context.active_object.data.materials.append(m['iron'])
    # Sign board
    bmesh_box("GuildSign", (0.30, 0.03, 0.20), (1.8, 0.10, BZ + wall_h + 0.15), m['wood'])
    # Sign bracket
    bmesh_box("SignBracket", (0.04, 0.12, 0.04), (1.8, 0.05, BZ + wall_h + 0.28), m['iron'])

    # Second guild sign
    bmesh_box("GuildSign2", (0.25, 0.03, 0.18), (-1.8, -0.10, BZ + wall_h + 0.10), m['banner'])

    # ------- Stall counters along sides -------
    for i, cx in enumerate([-1.2, 0, 1.2]):
        bmesh_box(f"StallL_{i}", (0.7, 0.35, 0.06), (cx, -0.85, BZ + 0.70), m['wood_dark'])
        bmesh_box(f"StallLLeg_{i}_a", (0.06, 0.06, 0.64), (cx - 0.25, -0.85, BZ + 0.38), m['wood'])
        bmesh_box(f"StallLLeg_{i}_b", (0.06, 0.06, 0.64), (cx + 0.25, -0.85, BZ + 0.38), m['wood'])

    for i, cx in enumerate([-1.2, 0, 1.2]):
        bmesh_box(f"StallR_{i}", (0.7, 0.35, 0.06), (cx, 0.85, BZ + 0.70), m['wood_dark'])
        bmesh_box(f"StallRLeg_{i}_a", (0.06, 0.06, 0.64), (cx - 0.25, 0.85, BZ + 0.38), m['wood'])
        bmesh_box(f"StallRLeg_{i}_b", (0.06, 0.06, 0.64), (cx + 0.25, 0.85, BZ + 0.38), m['wood'])

    # ------- Sacks of grain near stalls -------
    for pos in [(0.5, -0.5), (-0.5, 0.5), (0.3, 0.6)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, location=(pos[0], pos[1], BZ + 0.11))
        sack = bpy.context.active_object
        sack.name = f"Sack_{pos[0]:.1f}_{pos[1]:.1f}"
        sack.scale = (1, 0.7, 0.6)
        sack.data.materials.append(m['roof_edge'])


# ============================================================
# GUNPOWDER AGE — Stone market house with arcade arches, clock tower
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (GW, GD, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Foundation
    bmesh_box("Found", (4.6, 3.0, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.18

    # ------- Ground floor arcade (open arches) -------
    gf_h = 1.8
    # Arcade piers
    pier_xs = [-1.8, -0.6, 0.6, 1.8]
    for px in pier_xs:
        for py in [-1.2, 1.2]:
            bmesh_box(f"Pier_{px:.1f}_{py:.1f}", (0.20, 0.20, gf_h),
                      (px, py, BZ + gf_h / 2), m['stone'], bevel=0.02)

    # Arch tops (simplified as flat lintels with decorative keystones)
    for i in range(3):
        cx = -1.2 + i * 1.2
        for py in [-1.2, 1.2]:
            bmesh_box(f"Arch_{i}_{py:.1f}", (1.0, 0.20, 0.15),
                      (cx, py, BZ + gf_h - 0.075), m['stone_trim'])
            # Keystone
            bmesh_box(f"Key_{i}_{py:.1f}", (0.12, 0.22, 0.10),
                      (cx, py, BZ + gf_h + 0.02), m['stone_light'])

    # Floor slab between ground and upper floor
    bmesh_box("FloorSlab", (4.2, 2.6, 0.10), (0, 0, BZ + gf_h + 0.05), m['stone_trim'])

    # ------- Upper floor (enclosed) -------
    uf_z = BZ + gf_h + 0.10
    uf_h = 1.5
    bmesh_box("UpperMain", (4.0, 2.4, uf_h), (0, 0, uf_z + uf_h / 2), m['stone'], bevel=0.02)

    # Upper floor windows
    for i, cx in enumerate([-1.2, 0, 1.2]):
        for py_sign in [-1, 1]:
            bmesh_box(f"UWin_{i}_{py_sign}", (0.20, 0.06, 0.40),
                      (cx, py_sign * 1.21, uf_z + 0.60), m['window'])
            bmesh_box(f"UWinH_{i}_{py_sign}", (0.24, 0.07, 0.04),
                      (cx, py_sign * 1.22, uf_z + 0.82), m['stone_trim'])

    # Front windows
    for py in [-0.6, 0, 0.6]:
        bmesh_box(f"FWin_{py:.1f}", (0.06, 0.20, 0.40),
                  (2.01, py, uf_z + 0.60), m['window'])
        bmesh_box(f"FWinFrame_{py:.1f}", (0.07, 0.24, 0.04),
                  (2.02, py, uf_z + 0.82), m['stone_trim'])

    # ------- Cornice -------
    bmesh_box("Cornice", (4.1, 2.5, 0.08), (0, 0, uf_z + uf_h), m['stone_trim'], bevel=0.02)

    # ------- Main roof (hipped) -------
    pyramid_roof("Roof", w=3.8, d=2.2, h=0.9, overhang=0.20,
                 origin=(0, 0, uf_z + uf_h + 0.04), material=m['roof'])

    # ------- Clock tower (center, rising above roof) -------
    tw_z = uf_z + uf_h
    bmesh_box("Tower", (0.6, 0.6, 1.2), (0, 0, tw_z + 0.60), m['stone'], bevel=0.02)
    # Tower cornice
    bmesh_box("TowerCornice", (0.65, 0.65, 0.06), (0, 0, tw_z + 1.20), m['stone_trim'])

    # Clock faces (4 sides)
    for dx, dy, rx, ry in [(0.31, 0, 0.25, 0.06), (-0.31, 0, 0.25, 0.06),
                            (0, 0.31, 0.06, 0.25), (0, -0.31, 0.06, 0.25)]:
        bmesh_box(f"Clock_{dx:.1f}_{dy:.1f}", (rx, ry, 0.25),
                  (dx, dy, tw_z + 0.90), m['window'])

    # Clock frame
    for dx, dy, rx, ry in [(0.32, 0, 0.28, 0.07), (-0.32, 0, 0.28, 0.07),
                            (0, 0.32, 0.07, 0.28), (0, -0.32, 0.07, 0.28)]:
        bmesh_box(f"ClockFrame_{dx:.1f}_{dy:.1f}", (rx, ry, 0.28),
                  (dx, dy, tw_z + 0.90), m['gold'])

    # Tower spire
    bmesh_cone("Spire", 0.30, 0.70, 8, (0, 0, tw_z + 1.23), m['roof'])
    # Spire finial
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(0, 0, tw_z + 1.96))
    bpy.context.active_object.name = "Finial"
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # ------- Balcony on front -------
    bmesh_box("Balcony", (0.35, 1.6, 0.06), (2.15, 0, uf_z + 0.03), m['stone_trim'])
    # Balcony railing
    for i in range(10):
        fy = -0.70 + i * 0.16
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=0.40,
                                            location=(2.25, fy, uf_z + 0.26))
        bpy.context.active_object.name = f"BalRail_{i}"
        bpy.context.active_object.data.materials.append(m['iron'])
    # Rail top
    bmesh_box("RailTop", (0.04, 1.6, 0.03), (2.25, 0, uf_z + 0.48), m['iron'])

    # ------- Covered stalls in arcade -------
    for cx in [-1.2, 0, 1.2]:
        bmesh_box(f"Stall_{cx:.1f}", (0.8, 0.5, 0.06), (cx, 0, BZ + 0.65), m['wood_dark'])
        bmesh_box(f"StallLeg_{cx:.1f}_a", (0.06, 0.06, 0.59),
                  (cx - 0.30, 0, BZ + 0.36), m['wood'])
        bmesh_box(f"StallLeg_{cx:.1f}_b", (0.06, 0.06, 0.59),
                  (cx + 0.30, 0, BZ + 0.36), m['wood'])

    # ------- Steps -------
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.16, 2.0, 0.05),
                  (2.30 + i * 0.18, 0, BZ - 0.03 - i * 0.05), m['stone_dark'])


# ============================================================
# ENLIGHTENMENT AGE — Elegant market hall with iron/glass roof
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (GW, GD, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Foundation
    bmesh_box("Found", (4.6, 3.0, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.15
    wall_h = 2.4

    # ------- Main hall walls -------
    bmesh_box("Main", (4.2, 2.6, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Quoins on corners
    for xs in [-1, 1]:
        for ys in [-1, 1]:
            for z_off in [0.15, 0.55, 0.95, 1.35, 1.75, 2.15]:
                bmesh_box(f"Quoin_{xs}_{ys}_{z_off:.1f}", (0.06, 0.06, 0.14),
                          (xs * 2.11, ys * 1.31, BZ + z_off), m['stone_light'])

    # String courses
    bmesh_box("StringLow", (4.24, 2.64, 0.05), (0, 0, BZ + 0.8), m['stone_trim'], bevel=0.01)
    bmesh_box("StringHigh", (4.24, 2.64, 0.05), (0, 0, BZ + 1.6), m['stone_trim'], bevel=0.01)

    # Cornice
    bmesh_box("Cornice", (4.30, 2.68, 0.08), (0, 0, BZ + wall_h), m['stone_trim'], bevel=0.03)

    # ------- Iron and glass barrel-vault roof -------
    # Create a barrel vault with iron ribs
    vault_h = 1.0
    vault_base_z = BZ + wall_h
    segments = 10
    for i in range(segments + 1):
        angle = math.pi * i / segments
        vy = 1.30 * math.cos(angle)
        vz = vault_base_z + vault_h * math.sin(angle)
        # Iron rib running along the length
        bmesh_box(f"Rib_{i}", (4.0, 0.03, 0.03), (0, vy, vz), m['iron'])

    # Cross ribs
    for cx in [-1.5, -0.5, 0.5, 1.5]:
        for i in range(segments):
            a1 = math.pi * i / segments
            a2 = math.pi * (i + 1) / segments
            y1 = 1.30 * math.cos(a1)
            z1 = vault_base_z + vault_h * math.sin(a1)
            y2 = 1.30 * math.cos(a2)
            z2 = vault_base_z + vault_h * math.sin(a2)
            sv = [(cx - 0.015, y1, z1), (cx + 0.015, y1, z1),
                  (cx + 0.015, y2, z2), (cx - 0.015, y2, z2)]
            mesh_from_pydata(f"CrossRib_{cx:.1f}_{i}", sv, [(0, 1, 2, 3)], m['iron'])

    # Glass panels between ribs
    for i in range(segments):
        a1 = math.pi * i / segments
        a2 = math.pi * (i + 1) / segments
        y1 = 1.30 * math.cos(a1)
        z1 = vault_base_z + vault_h * math.sin(a1)
        y2 = 1.30 * math.cos(a2)
        z2 = vault_base_z + vault_h * math.sin(a2)
        gv = [(-2.0, y1, z1), (2.0, y1, z1), (2.0, y2, z2), (-2.0, y2, z2)]
        gp = mesh_from_pydata(f"GlassPanel_{i}", gv, [(0, 1, 2, 3)], m['window'])

    # ------- Symmetrical wings (lower extensions on each end) -------
    wing_h = 1.6
    for sx in [-1, 1]:
        wx = sx * 2.5
        bmesh_box(f"Wing_{sx}", (0.8, 2.2, wing_h), (wx, 0, BZ + wing_h / 2), m['stone'], bevel=0.02)
        bmesh_box(f"WingCornice_{sx}", (0.85, 2.24, 0.06), (wx, 0, BZ + wing_h), m['stone_trim'])
        # Wing roof
        pyramid_roof(f"WingRoof_{sx}", w=0.6, d=2.0, h=0.4, overhang=0.10,
                     origin=(wx, 0, BZ + wing_h + 0.02), material=m['roof'])
        # Wing windows
        for py in [-0.50, 0, 0.50]:
            bmesh_box(f"WWin_{sx}_{py:.1f}", (0.06, 0.20, 0.45),
                      (wx + sx * 0.41, py, BZ + 0.80), m['window'])
            bmesh_box(f"WWinH_{sx}_{py:.1f}", (0.07, 0.24, 0.04),
                      (wx + sx * 0.42, py, BZ + 1.05), m['stone_trim'])

    # ------- Front entrance (grand doorway) -------
    bmesh_box("DoorSurround", (0.12, 0.80, 1.40), (2.12, 0, BZ + 0.70), m['stone_light'])
    bmesh_box("Door", (0.06, 0.65, 1.30), (2.11, 0, BZ + 0.65), m['door'])
    # Fanlight
    bmesh_box("Fanlight", (0.06, 0.65, 0.12), (2.11, 0, BZ + 1.36), m['window'])

    # ------- Front windows (tall, symmetrical) -------
    for py in [-0.80, 0.80]:
        bmesh_box(f"FWin_{py:.1f}", (0.06, 0.24, 0.55), (2.11, py, BZ + 0.85), m['window'])
        bmesh_box(f"FWinH_{py:.1f}", (0.07, 0.28, 0.04), (2.12, py, BZ + 1.15), m['stone_trim'])
        bmesh_box(f"FWinS_{py:.1f}", (0.07, 0.28, 0.04), (2.12, py, BZ + 0.60), m['stone_trim'])

    # Upper front windows
    for py in [-0.60, 0, 0.60]:
        bmesh_box(f"UFWin_{py:.1f}", (0.06, 0.22, 0.45), (2.11, py, BZ + 1.85), m['window'])
        bmesh_box(f"UFWinH_{py:.1f}", (0.07, 0.26, 0.04), (2.12, py, BZ + 2.10), m['stone_trim'])

    # ------- Weighing house (small annex) -------
    bmesh_box("WeighHouse", (0.6, 0.6, 1.0), (-2.5, -1.2, BZ + 0.50), m['stone_light'], bevel=0.02)
    bmesh_box("WeighRoof", (0.7, 0.7, 0.06), (-2.5, -1.2, BZ + 1.03), m['stone_trim'])
    # Scale symbol
    bmesh_box("ScaleSymbol", (0.06, 0.15, 0.02), (-2.50, -1.2, BZ + 0.80), m['gold'])

    # ------- Steps -------
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.18, 1.8, 0.04),
                  (2.35 + i * 0.18, 0, BZ - 0.02 - i * 0.04), m['stone_light'])

    # ------- Iron railings at front -------
    for i in range(12):
        fy = -0.85 + i * 0.16
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=0.45,
                                            location=(2.50, fy, BZ + 0.12))
        bpy.context.active_object.name = f"Railing_{i}"
        bpy.context.active_object.data.materials.append(m['iron'])


# ============================================================
# INDUSTRIAL AGE — Steel and glass market pavilion
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (GW, GD, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Foundation
    bmesh_box("Found", (4.6, 3.0, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.12
    wall_h = 2.8

    # ------- Main pavilion walls (lower brick portion) -------
    brick_h = 1.2
    bmesh_box("BrickBase", (4.2, 2.6, brick_h), (0, 0, BZ + brick_h / 2), m['stone'], bevel=0.02)

    # Iron band above brick
    bmesh_box("IronBand", (4.24, 2.64, 0.05), (0, 0, BZ + brick_h), m['iron'])

    # ------- Glass upper portion (iron frame with glass panels) -------
    glass_h = wall_h - brick_h
    # Iron frame posts
    for px in [-1.8, -0.6, 0.6, 1.8]:
        for py in [-1.3, 1.3]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=glass_h,
                                                location=(px, py, BZ + brick_h + glass_h / 2))
            col = bpy.context.active_object
            col.name = f"IronCol_{px:.1f}_{py:.1f}"
            col.data.materials.append(m['iron'])

    # Glass walls (front and back)
    for py_sign in [-1, 1]:
        bmesh_box(f"GlassWall_{py_sign}", (4.0, 0.06, glass_h - 0.1),
                  (0, py_sign * 1.30, BZ + brick_h + glass_h / 2 + 0.05), m['window'])
        # Horizontal iron mullions
        for z_off in [0.4, 0.8]:
            bmesh_box(f"HMull_{py_sign}_{z_off:.1f}", (4.0, 0.04, 0.03),
                      (0, py_sign * 1.31, BZ + brick_h + z_off), m['iron'])

    # Glass front wall
    bmesh_box("GlassFront", (0.06, 2.4, glass_h - 0.1),
              (2.10, 0, BZ + brick_h + glass_h / 2 + 0.05), m['window'])
    for z_off in [0.4, 0.8]:
        bmesh_box(f"HMullF_{z_off:.1f}", (0.04, 2.4, 0.03),
                  (2.11, 0, BZ + brick_h + z_off), m['iron'])

    # ------- Barrel-vault glass roof -------
    vault_h = 0.8
    vault_base_z = BZ + wall_h
    segs = 8
    for i in range(segs):
        a1 = math.pi * i / segs
        a2 = math.pi * (i + 1) / segs
        y1 = 1.35 * math.cos(a1)
        z1 = vault_base_z + vault_h * math.sin(a1)
        y2 = 1.35 * math.cos(a2)
        z2 = vault_base_z + vault_h * math.sin(a2)
        gv = [(-2.1, y1, z1), (2.1, y1, z1), (2.1, y2, z2), (-2.1, y2, z2)]
        mesh_from_pydata(f"RoofGlass_{i}", gv, [(0, 1, 2, 3)], m['window'])
        # Iron rib
        bmesh_box(f"RoofRib_{i}", (4.2, 0.03, 0.03), (0, y1, z1), m['iron'])

    # Top rib
    bmesh_box("RoofTopRib", (4.2, 0.03, 0.03), (0, 0, vault_base_z + vault_h), m['iron'])

    # Cross ribs
    for cx in [-1.4, 0, 1.4]:
        for i in range(segs):
            a1 = math.pi * i / segs
            a2 = math.pi * (i + 1) / segs
            y1 = 1.35 * math.cos(a1)
            z1 = vault_base_z + vault_h * math.sin(a1)
            y2 = 1.35 * math.cos(a2)
            z2 = vault_base_z + vault_h * math.sin(a2)
            sv = [(cx - 0.015, y1, z1), (cx + 0.015, y1, z1),
                  (cx + 0.015, y2, z2), (cx - 0.015, y2, z2)]
            mesh_from_pydata(f"XRib_{cx:.1f}_{i}", sv, [(0, 1, 2, 3)], m['iron'])

    # ------- Clock (mounted on front facade) -------
    bmesh_prism("ClockFace", 0.20, 0.06, 12, (2.11, 0, BZ + brick_h - 0.30), m['window'])
    bmesh_prism("ClockRim", 0.22, 0.03, 12, (2.11, 0, BZ + brick_h - 0.30), m['gold'])
    # Clock hands (simplified as thin boxes)
    bmesh_box("ClockHand1", (0.02, 0.02, 0.14), (2.14, 0, BZ + brick_h - 0.23), m['iron'])
    bmesh_box("ClockHand2", (0.02, 0.10, 0.02), (2.14, 0.03, BZ + brick_h - 0.30), m['iron'])

    # ------- Iron columns inside -------
    for px in [-1.4, 0, 1.4]:
        for py in [-0.6, 0.6]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.06, depth=wall_h,
                                                location=(px, py, BZ + wall_h / 2))
            col = bpy.context.active_object
            col.name = f"IntCol_{px:.1f}_{py:.1f}"
            col.data.materials.append(m['iron'])
            bpy.ops.object.shade_smooth()
            # Capital
            bmesh_box(f"IntCap_{px:.1f}_{py:.1f}", (0.16, 0.16, 0.04),
                      (px, py, BZ + wall_h + 0.02), m['iron'])

    # ------- Loading dock (side extension) -------
    bmesh_box("Dock", (1.2, 0.6, 0.30), (0, -1.65, BZ + 0.15), m['stone_dark'])
    bmesh_box("DockEdge", (1.24, 0.04, 0.34), (0, -1.95, BZ + 0.17), m['iron'])

    # ------- Carts at loading dock -------
    # Cart body
    bmesh_box("CartBody", (0.5, 0.3, 0.15), (-0.3, -1.65, BZ + 0.42), m['wood_dark'])
    # Cart wheels
    for dy in [-0.20, 0.20]:
        bmesh_prism(f"CartWheel_{dy:.1f}", 0.08, 0.03, 10,
                    (-0.3, -1.65 + dy, BZ + 0.35), m['wood'])

    # Second cart
    bmesh_box("CartBody2", (0.4, 0.3, 0.12), (0.5, -1.65, BZ + 0.40), m['wood_dark'])

    # ------- Front entrance doors -------
    bmesh_box("DoorL", (0.06, 0.35, 1.10), (2.11, -0.25, BZ + 0.55), m['door'])
    bmesh_box("DoorR", (0.06, 0.35, 1.10), (2.11, 0.25, BZ + 0.55), m['door'])
    bmesh_box("DoorFrame", (0.08, 0.80, 0.06), (2.12, 0, BZ + 1.13), m['iron'])

    # ------- Brick windows on lower level -------
    for py in [-0.80, 0.80]:
        bmesh_box(f"BWin_{py:.1f}", (0.06, 0.22, 0.40), (2.11, py, BZ + 0.65), m['window'])
        bmesh_box(f"BWinH_{py:.1f}", (0.07, 0.26, 0.04), (2.12, py, BZ + 0.87), m['stone_trim'])

    # ------- Steps -------
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.16, 1.8, 0.04),
                  (2.30 + i * 0.16, 0, BZ - 0.02 - i * 0.04), m['stone_dark'])


# ============================================================
# MODERN AGE — Shopping center with glass storefront
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (GW, GD, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Concrete pad
    bmesh_box("Pad", (4.8, 3.2, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    BZ = Z + 0.08

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # ------- Main building (rectangular, modern) -------
    main_h = 2.6
    bmesh_box("Main", (3.8, 2.6, main_h), (-0.2, 0, BZ + main_h / 2), m['stone'], bevel=0.02)

    # ------- Flat roof -------
    bmesh_box("Roof", (4.0, 2.8, 0.08), (-0.2, 0, BZ + main_h + 0.04), m['stone_dark'])

    # Roof parapet
    bmesh_box("ParapetF", (0.06, 2.8, 0.20), (1.80, 0, BZ + main_h + 0.18), metal)
    bmesh_box("ParapetB", (0.06, 2.8, 0.20), (-2.20, 0, BZ + main_h + 0.18), metal)
    bmesh_box("ParapetL", (4.0, 0.06, 0.20), (-0.2, -1.40, BZ + main_h + 0.18), metal)
    bmesh_box("ParapetR", (4.0, 0.06, 0.20), (-0.2, 1.40, BZ + main_h + 0.18), metal)

    # ------- Glass storefront (entire front wall) -------
    bmesh_box("GlassFront", (0.06, 2.2, main_h - 0.3),
              (1.60, 0, BZ + main_h / 2 + 0.05), glass)
    # Vertical mullions
    for py in [-0.80, -0.30, 0.20, 0.70]:
        bmesh_box(f"VMull_{py:.1f}", (0.04, 0.03, main_h - 0.3),
                  (1.61, py, BZ + main_h / 2 + 0.05), metal)
    # Horizontal mullions
    for z_off in [1.0, 1.8]:
        bmesh_box(f"HMull_{z_off:.1f}", (0.04, 2.22, 0.03),
                  (1.61, 0, BZ + z_off), metal)

    # ------- Entrance (recessed, automated doors) -------
    bmesh_box("EntranceRecess", (0.30, 0.90, main_h - 0.2),
              (1.75, -0.55, BZ + main_h / 2 + 0.05), m['stone_dark'])
    # Sliding door panels
    bmesh_box("DoorL", (0.04, 0.35, 1.30), (1.89, -0.72, BZ + 0.65), glass)
    bmesh_box("DoorR", (0.04, 0.35, 1.30), (1.89, -0.38, BZ + 0.65), glass)
    # Door frame
    bmesh_box("DoorFrameTop", (0.06, 0.92, 0.06), (1.89, -0.55, BZ + 1.33), metal)
    bmesh_box("DoorFrameL", (0.06, 0.04, 1.30), (1.89, -0.92, BZ + 0.65), metal)
    bmesh_box("DoorFrameR", (0.06, 0.04, 1.30), (1.89, -0.18, BZ + 0.65), metal)

    # ------- Signage (above entrance) -------
    bmesh_box("SignBoard", (0.06, 1.6, 0.35), (1.62, 0, BZ + main_h - 0.25), m['banner'])
    # Sign backing light
    bmesh_box("SignLight", (0.04, 1.4, 0.06), (1.64, 0, BZ + main_h - 0.08), m['gold'])

    # ------- Side windows -------
    for x_off in [-1.2, -0.3, 0.6]:
        bmesh_box(f"SWin_{x_off:.1f}", (0.35, 0.06, 0.55),
                  (x_off - 0.2, -1.31, BZ + 1.60), glass)
        bmesh_box(f"SWinFrame_{x_off:.1f}", (0.39, 0.04, 0.03),
                  (x_off - 0.2, -1.32, BZ + 1.90), metal)

    # ------- Parking area (front) -------
    bmesh_box("ParkingLot", (1.6, 2.8, 0.04), (2.6, 0, BZ + 0.02), m['stone_dark'])
    # Parking lines
    for py in [-0.80, 0, 0.80]:
        bmesh_box(f"ParkLine_{py:.1f}", (1.0, 0.02, 0.01), (2.6, py, BZ + 0.045), m['stone_light'])

    # ------- Parked cars (simplified boxes) -------
    for i, (cx, cy) in enumerate([(2.3, -0.80), (2.3, 0.80)]):
        bmesh_box(f"Car_{i}", (0.55, 0.25, 0.15), (cx, cy, BZ + 0.12), metal)
        bmesh_box(f"CarTop_{i}", (0.30, 0.22, 0.10), (cx - 0.05, cy, BZ + 0.27), glass)
        # Wheels
        for wdx in [-0.18, 0.18]:
            bmesh_prism(f"Wheel_{i}_{wdx:.1f}", 0.05, 0.03, 8,
                        (cx + wdx, cy - 0.13, BZ + 0.05), m['stone_dark'])

    # ------- HVAC unit on roof -------
    bmesh_box("HVAC", (0.5, 0.4, 0.30), (-1.2, 0.6, BZ + main_h + 0.23), metal)
    bmesh_box("HVACFan", (0.25, 0.25, 0.04), (-1.2, 0.6, BZ + main_h + 0.40), m['stone_dark'])

    # ------- Shopping cart return (small shelter) -------
    bmesh_box("CartShelter", (0.5, 0.3, 0.50), (2.8, -0.40, BZ + 0.25), metal)
    bmesh_box("CartShelterRoof", (0.55, 0.35, 0.03), (2.8, -0.40, BZ + 0.52), metal)

    # ------- Sidewalk path to entrance -------
    bmesh_box("Sidewalk", (0.8, 0.60, 0.03), (2.2, -0.55, BZ + 0.015), m['stone_light'])


# ============================================================
# DIGITAL AGE — E-commerce hub with drone pads, holographic displays
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (GW, GD, 0.06), (0, 0, Z + 0.03), m['ground'])

    # High-tech platform
    bmesh_box("Pad", (4.8, 3.2, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    BZ = Z + 0.08

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # ------- Main building (sleek glass cube with chamfered edges) -------
    main_h = 3.0
    bmesh_box("MainFrame", (3.8, 2.6, main_h), (-0.2, 0, BZ + main_h / 2), metal, bevel=0.04)
    # Glass skin (slightly inset)
    bmesh_box("GlassSkin", (3.7, 2.5, main_h - 0.1), (-0.2, 0, BZ + main_h / 2 + 0.05), glass)

    # ------- Horizontal accent bands (LED strips) -------
    for z_off in [0.8, 1.6, 2.4]:
        bmesh_box(f"LEDStrip_{z_off:.1f}", (3.82, 2.62, 0.04),
                  (-0.2, 0, BZ + z_off), m['gold'])

    # ------- Flat roof -------
    bmesh_box("Roof", (4.0, 2.8, 0.06), (-0.2, 0, BZ + main_h + 0.03), metal)

    # ------- Entrance (futuristic sliding glass) -------
    bmesh_box("EntranceArch", (0.12, 1.0, 1.6), (1.60, 0, BZ + 0.80), metal)
    bmesh_box("EntranceGlass", (0.06, 0.90, 1.50), (1.61, 0, BZ + 0.78), glass)
    # Glowing entrance strip
    bmesh_box("EntranceGlow", (0.08, 0.95, 0.04), (1.61, 0, BZ + 0.03), m['gold'])

    # ------- Drone delivery pads (3 landing pads on roof) -------
    for i, (dx, dy) in enumerate([(-0.8, -0.7), (-0.8, 0.7), (0.4, 0)]):
        # Pad circle
        bmesh_prism(f"DronePad_{i}", 0.30, 0.03, 12,
                    (dx - 0.2, dy, BZ + main_h + 0.06), metal)
        # Landing H-mark
        bmesh_box(f"HMark_{i}_h", (0.20, 0.03, 0.01),
                  (dx - 0.2, dy, BZ + main_h + 0.095), m['gold'])
        bmesh_box(f"HMark_{i}_v1", (0.03, 0.15, 0.01),
                  (dx - 0.30, dy, BZ + main_h + 0.095), m['gold'])
        bmesh_box(f"HMark_{i}_v2", (0.03, 0.15, 0.01),
                  (dx - 0.10, dy, BZ + main_h + 0.095), m['gold'])

    # ------- Drone in flight (hovering near a pad) -------
    drone_x, drone_y, drone_z = 0.2, 0, BZ + main_h + 0.60
    bmesh_box("DroneBody", (0.15, 0.15, 0.05), (drone_x, drone_y, drone_z), metal)
    # Drone arms
    for adx, ady in [(-0.12, -0.12), (-0.12, 0.12), (0.12, -0.12), (0.12, 0.12)]:
        bmesh_box(f"DroneArm_{adx:.2f}_{ady:.2f}", (0.12, 0.02, 0.02),
                  (drone_x + adx, drone_y + ady, drone_z), metal)
        # Rotor discs
        bmesh_prism(f"Rotor_{adx:.2f}_{ady:.2f}", 0.06, 0.01, 8,
                    (drone_x + adx * 2, drone_y + ady * 2, drone_z + 0.03), m['gold'])

    # Package dangling from drone
    bmesh_box("Package", (0.08, 0.06, 0.06), (drone_x, drone_y, drone_z - 0.12), m['wood_dark'])

    # ------- Holographic displays (floating panels in front) -------
    for i, (hx, hy) in enumerate([(2.0, -0.70), (2.0, 0.70)]):
        # Display panel (slightly tilted, floating)
        bmesh_box(f"HoloPanel_{i}", (0.02, 0.40, 0.50), (hx, hy, BZ + 1.30), glass)
        # Glow base (projector)
        bmesh_prism(f"HoloBase_{i}", 0.08, 0.04, 8, (hx, hy, BZ + 0.80), m['gold'])
        # Hologram "beam" (thin glowing column)
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.015, depth=0.45,
                                            location=(hx, hy, BZ + 1.05))
        beam = bpy.context.active_object
        beam.name = f"HoloBeam_{i}"
        beam.data.materials.append(m['gold'])

    # ------- Server room annex (back of building) -------
    bmesh_box("ServerRoom", (1.0, 1.6, 2.0), (-2.0, 0, BZ + 1.0), metal, bevel=0.02)
    # Ventilation grilles
    for z_off in [0.5, 1.0, 1.5]:
        bmesh_box(f"Vent_{z_off:.1f}", (0.06, 0.30, 0.08),
                  (-2.51, 0, BZ + z_off), m['stone_dark'])
    # Server room status LED strip
    bmesh_box("ServerLED", (1.02, 0.04, 0.04), (-2.0, 0.81, BZ + 1.80), m['gold'])

    # Cooling fins on server room
    for i in range(5):
        bmesh_box(f"CoolFin_{i}", (0.04, 1.62, 0.02),
                  (-2.0, 0, BZ + 0.30 + i * 0.35), metal)

    # ------- Solar panel canopy -------
    # Support columns
    for dy in [-0.8, 0.8]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035, depth=2.2,
                                            location=(2.4, dy, BZ + 1.10))
        bpy.context.active_object.name = f"SolarCol_{dy:.1f}"
        bpy.context.active_object.data.materials.append(metal)
    # Canopy panel
    bmesh_box("SolarCanopy", (0.8, 1.8, 0.04), (2.4, 0, BZ + 2.22), glass)
    bmesh_box("SolarFrame", (0.82, 1.82, 0.02), (2.4, 0, BZ + 2.20), metal)

    # ------- Delivery robot (ground level) -------
    bmesh_box("RobotBody", (0.18, 0.14, 0.12), (1.8, -1.1, BZ + 0.10), metal)
    # Robot wheels
    for wdy in [-0.08, 0.08]:
        bmesh_prism(f"RobotWheel_{wdy:.2f}", 0.04, 0.02, 8,
                    (1.8, -1.1 + wdy, BZ + 0.04), m['stone_dark'])
    # Robot sensor
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(1.88, -1.1, BZ + 0.18))
    bpy.context.active_object.name = "RobotSensor"
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # ------- Lit pathway -------
    for i in range(5):
        px = 1.6 + i * 0.25
        bmesh_box(f"PathLight_{i}", (0.03, 0.03, 0.10),
                  (px, -1.3, BZ + 0.05), m['gold'])

    # ------- Digital signage panel on side -------
    bmesh_box("DigiSign", (0.04, 1.0, 0.60), (-0.2, -1.31, BZ + 1.80), glass)
    bmesh_box("DigiSignFrame", (0.06, 1.04, 0.64), (-0.2, -1.32, BZ + 1.80), metal)


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


def build_market(materials, age='medieval'):
    """Build a Market with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
