"""
Gold Mine building -- gold resource production structure per age, a 2x2 tile
building focused on mining, ore extraction, and gold production.

Stone:         Open pit mine with wooden supports, ore pile, primitive sluice
Bronze:        Mine entrance in hillside with timber frame, ore cart, smelting furnace
Iron:          Fortified mine head with stone walls, wooden headframe, ore buckets, slag pile
Classical:     Roman mine with columned entrance, aqueduct-style water channel, gold ingot stack
Medieval:      Mine shaft with wooden headframe/windlass, ore cart on rails, smelting shed, gold pile
Gunpowder:     Deeper mine with stone headhouse, mechanical windlass, blackpowder storage, ore processing
Enlightenment: Engineered mine with brick engine house, beam pump, chimney, ore wagons
Industrial:    Coal mine style headframe with winding gear, pithead buildings, rail tracks, conveyor
Modern:        Modern mining operation with steel headframe, processing plant, dump truck, conveyor belt
Digital:       Automated extraction - robotic drill rig, processing pod, drone transport, holographic display
"""

import bpy
import bmesh
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# ============================================================
# STONE AGE -- Open pit mine with wooden supports, ore pile, sluice
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Open pit (sunken circular area with stone rim)
    bmesh_prism("PitRim", 0.90, 0.15, 12, (0.0, 0.0, Z), m['stone_dark'])
    bmesh_prism("PitInner", 0.72, 0.08, 12, (0.0, 0.0, Z + 0.02), m['stone'])

    # Wooden support frame over pit (A-frame)
    # Left support beam
    fv_l = [(-0.65, 0.0, Z + 0.15), (-0.60, 0.0, Z + 0.15),
            (0.0, 0.0, Z + 1.10), (-0.03, 0.0, Z + 1.10)]
    mesh_from_pydata("SupportL", fv_l, [(0, 1, 2, 3)], m['wood'])
    # Right support beam
    fv_r = [(0.65, 0.0, Z + 0.15), (0.60, 0.0, Z + 0.15),
            (0.0, 0.0, Z + 1.10), (0.03, 0.0, Z + 1.10)]
    mesh_from_pydata("SupportR", fv_r, [(0, 1, 2, 3)], m['wood'])

    # Crossbeam at top
    bmesh_box("Crossbeam", (0.04, 0.80, 0.04), (0.0, 0.0, Z + 1.08), m['wood_dark'])

    # Vertical support poles around pit
    for i in range(4):
        a = math.pi * 0.25 + (2 * math.pi * i) / 4
        px, py = 0.70 * math.cos(a), 0.70 * math.sin(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.035, depth=0.90,
                                            location=(px, py, Z + 0.50))
        pole = bpy.context.active_object
        pole.name = f"PitPole_{i}"
        pole.data.materials.append(m['wood'])

    # Ore pile (gold-colored rocks near pit)
    for i, (ox, oy, r) in enumerate([
        (0.85, 0.60, 0.12), (1.00, 0.45, 0.10), (0.95, 0.70, 0.08),
        (0.80, 0.50, 0.09)
    ]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(ox, oy, Z + r * 0.7))
        nugget = bpy.context.active_object
        nugget.name = f"OreNugget_{i}"
        nugget.scale = (1.0, 0.9, 0.6)
        nugget.data.materials.append(m['gold'])

    # Primitive sluice (wooden trough for washing ore)
    # Trough base
    bmesh_box("SluiceBase", (0.80, 0.20, 0.04), (-0.80, -0.60, Z + 0.25), m['wood'])
    # Side walls of trough
    bmesh_box("SluiceSideL", (0.80, 0.03, 0.10), (-0.80, -0.70, Z + 0.30), m['wood'])
    bmesh_box("SluiceSideR", (0.80, 0.03, 0.10), (-0.80, -0.50, Z + 0.30), m['wood'])
    # Sluice support legs
    for sx in [-1.10, -0.50]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.30,
                                            location=(sx, -0.60, Z + 0.15))
        bpy.context.active_object.data.materials.append(m['wood_dark'])

    # Digging tools (picks leaning against pole)
    # Pick handle
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.50,
                                        location=(0.60, -0.75, Z + 0.30))
    pick = bpy.context.active_object
    pick.name = "PickHandle"
    pick.rotation_euler = (0.3, 0.0, 0.2)
    pick.data.materials.append(m['wood_dark'])
    # Pick head
    bmesh_box("PickHead", (0.18, 0.03, 0.04), (0.55, -0.70, Z + 0.52), m['stone_dark'])

    # Small fire pit for warmth
    bmesh_prism("FirePit", 0.18, 0.06, 8, (-0.90, 0.85, Z + 0.03), m['stone_dark'])

    # Woven basket for carrying ore
    bmesh_prism("OreBasket", 0.10, 0.16, 8, (1.10, -0.20, Z), m['roof_edge'])
    # Gold nuggets in basket
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(1.10, -0.20, Z + 0.18))
    bpy.context.active_object.name = "BasketGold"
    bpy.context.active_object.data.materials.append(m['gold'])


# ============================================================
# BRONZE AGE -- Mine entrance in hillside, ore cart, smelting furnace
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Hillside mound (the mine is cut into this)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(-0.4, 0.2, Z + 0.0))
    hill = bpy.context.active_object
    hill.name = "Hillside"
    hill.scale = (1.2, 1.0, 0.55)
    hill.data.materials.append(m['ground'])

    # Mine entrance (dark rectangular opening in hillside)
    bmesh_box("MineOpening", (0.08, 0.65, 0.80), (0.50, 0.2, Z + 0.40), m['stone_dark'])

    # Timber frame around entrance
    bmesh_box("TimberTop", (0.10, 0.75, 0.08), (0.52, 0.2, Z + 0.82), m['wood'])
    bmesh_box("TimberLeft", (0.10, 0.08, 0.80), (0.52, -0.12, Z + 0.40), m['wood'])
    bmesh_box("TimberRight", (0.10, 0.08, 0.80), (0.52, 0.52, Z + 0.40), m['wood'])

    # Stone reinforcement around entrance
    bmesh_box("StoneL", (0.12, 0.12, 0.85), (0.54, -0.22, Z + 0.42), m['stone'])
    bmesh_box("StoneR", (0.12, 0.12, 0.85), (0.54, 0.62, Z + 0.42), m['stone'])

    # Ore cart (wooden box on rollers)
    bmesh_box("CartBody", (0.30, 0.22, 0.15), (0.90, 0.2, Z + 0.18), m['wood_dark'])
    bmesh_box("CartFront", (0.03, 0.22, 0.20), (1.06, 0.2, Z + 0.20), m['wood'])
    bmesh_box("CartBack", (0.03, 0.22, 0.20), (0.74, 0.2, Z + 0.20), m['wood'])
    # Cart wheels (small cylinders)
    for dy in [-0.13, 0.13]:
        bmesh_prism(f"CartWheel_{dy:.2f}", 0.06, 0.03, 8, (0.90, 0.2 + dy, Z + 0.06), m['wood_dark'])

    # Gold ore in cart
    for i, (gx, gy) in enumerate([(0.85, 0.15), (0.95, 0.25), (0.88, 0.28)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(gx, gy, Z + 0.32))
        bpy.context.active_object.name = f"CartOre_{i}"
        bpy.context.active_object.scale = (1, 0.8, 0.7)
        bpy.context.active_object.data.materials.append(m['gold'])

    # Smelting furnace (beehive-shaped stone structure)
    bmesh_prism("FurnaceBase", 0.30, 0.60, 10, (1.0, -0.70, Z), m['stone_dark'])
    bmesh_cone("FurnaceTop", 0.30, 0.35, 10, (1.0, -0.70, Z + 0.60), m['stone'])
    # Furnace opening
    bmesh_box("FurnaceOpening", (0.06, 0.14, 0.18), (1.30, -0.70, Z + 0.15), m['door'])
    # Chimney hole at top
    bmesh_prism("FurnaceChimney", 0.08, 0.10, 6, (1.0, -0.70, Z + 0.92), m['stone_dark'])

    # Gold ingot mold / finished ingots near furnace
    for i, (ix, iy) in enumerate([(1.30, -0.40), (1.35, -0.50)]):
        bmesh_box(f"Ingot_{i}", (0.10, 0.06, 0.04), (ix, iy, Z + 0.02), m['gold'])

    # Firewood pile near furnace
    for j in range(3):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=0.35,
                                            location=(1.25, -1.00 + j * 0.08, Z + 0.03))
        log = bpy.context.active_object
        log.name = f"FuelLog_{j}"
        log.rotation_euler = (math.radians(90), 0, 0)
        log.data.materials.append(m['wood_dark'])

    # Water bucket (for quenching)
    bmesh_prism("Bucket", 0.08, 0.14, 8, (0.65, -0.50, Z), m['wood'])

    # Tool rack (picks and hammers)
    bmesh_box("ToolRack", (0.04, 0.40, 0.03), (0.55, -0.25, Z + 0.65), m['wood_dark'])
    for ty in [-0.35, -0.15]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=0.40,
                                            location=(0.55, ty, Z + 0.40))
        bpy.context.active_object.rotation_euler = (0.15, 0, 0)
        bpy.context.active_object.data.materials.append(m['wood'])


# ============================================================
# IRON AGE -- Fortified mine head, stone walls, wooden headframe
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stone foundation / fortified base
    bmesh_box("Found", (2.4, 2.0, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.15

    # Mine shaft opening (stone-lined square)
    bmesh_box("ShaftRim", (0.80, 0.80, 0.20), (0, 0, BZ + 0.10), m['stone'])
    bmesh_box("ShaftHole", (0.55, 0.55, 0.22), (0, 0, BZ + 0.09), m['stone_dark'])

    # Wooden headframe (A-frame over shaft)
    # Front legs
    for dy in [-0.35, 0.35]:
        fv = [(0.45, dy, BZ + 0.20), (0.40, dy, BZ + 0.20),
              (0.05, dy, BZ + 1.80), (0.0, dy, BZ + 1.80)]
        mesh_from_pydata(f"HFrameFront_{dy:.2f}", fv, [(0, 1, 2, 3)], m['wood'])
    # Back legs
    for dy in [-0.35, 0.35]:
        fv = [(-0.45, dy, BZ + 0.20), (-0.40, dy, BZ + 0.20),
              (-0.05, dy, BZ + 1.80), (0.0, dy, BZ + 1.80)]
        mesh_from_pydata(f"HFrameBack_{dy:.2f}", fv, [(0, 1, 2, 3)], m['wood'])

    # Top crossbar of headframe
    bmesh_box("HFrameTop", (0.06, 0.80, 0.06), (0.0, 0.0, BZ + 1.80), m['wood_dark'])

    # Horizontal braces on headframe
    bmesh_box("HFrameBrace", (0.60, 0.03, 0.04), (0.0, -0.35, BZ + 1.00), m['wood'])
    bmesh_box("HFrameBrace2", (0.60, 0.03, 0.04), (0.0, 0.35, BZ + 1.00), m['wood'])

    # Rope from headframe (going down into shaft)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=1.20,
                                        location=(0.0, 0.0, BZ + 1.00))
    rope = bpy.context.active_object
    rope.name = "Rope"
    rope.data.materials.append(m['roof_edge'])

    # Ore bucket (hanging from rope)
    bmesh_prism("OreBucket", 0.10, 0.14, 8, (0.0, 0.0, BZ + 0.35), m['wood_dark'])
    # Gold ore in bucket
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0.0, 0.0, BZ + 0.52))
    bpy.context.active_object.name = "BucketOre"
    bpy.context.active_object.data.materials.append(m['gold'])

    # Stone perimeter walls
    wall_h = 0.65
    bmesh_box("WallFront", (0.12, 2.0, wall_h), (1.15, 0.0, BZ + wall_h / 2), m['stone'], bevel=0.02)
    bmesh_box("WallBack", (0.12, 2.0, wall_h), (-1.15, 0.0, BZ + wall_h / 2), m['stone'], bevel=0.02)
    bmesh_box("WallLeft", (2.2, 0.12, wall_h), (0.0, -0.95, BZ + wall_h / 2), m['stone'], bevel=0.02)
    bmesh_box("WallRight", (2.2, 0.12, wall_h), (0.0, 0.95, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Gate opening in front wall
    bmesh_box("GateOpening", (0.14, 0.45, wall_h), (1.15, 0.0, BZ + wall_h / 2), m['stone_dark'])

    # Slag pile (waste rock, outside wall)
    for i, (sx, sy, sr) in enumerate([
        (1.35, -0.80, 0.10), (1.45, -0.70, 0.08), (1.30, -0.65, 0.09)
    ]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=sr, location=(sx, sy, Z + sr * 0.6))
        slag = bpy.context.active_object
        slag.name = f"Slag_{i}"
        slag.scale = (1.0, 1.0, 0.5)
        slag.data.materials.append(m['stone_dark'])

    # Gold ore pile inside compound
    for i, (gx, gy, gr) in enumerate([
        (0.70, -0.50, 0.08), (0.80, -0.45, 0.07), (0.75, -0.55, 0.06),
        (0.85, -0.55, 0.07)
    ]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=gr, location=(gx, gy, BZ + gr * 0.7))
        ore = bpy.context.active_object
        ore.name = f"GoldOre_{i}"
        ore.scale = (1, 0.9, 0.6)
        ore.data.materials.append(m['gold'])

    # Tool storage lean-to
    bmesh_box("LeanToBack", (0.06, 0.60, 0.70), (-0.85, -0.60, BZ + 0.35), m['wood'])
    # Angled roof
    ltv = [(-0.85, -0.90, BZ + 0.70), (-0.85, -0.30, BZ + 0.70),
           (-0.60, -0.30, BZ + 0.50), (-0.60, -0.90, BZ + 0.50)]
    mesh_from_pydata("LeanToRoof", ltv, [(0, 1, 2, 3)], m['roof'])


# ============================================================
# CLASSICAL AGE -- Roman mine with columned entrance, aqueduct channel
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stepped platform (2 tiers)
    for i in range(2):
        w = 2.8 - i * 0.15
        d = 2.4 - i * 0.10
        bmesh_box(f"Plat_{i}", (w, d, 0.06), (0, 0, Z + 0.03 + i * 0.06), m['stone_light'], bevel=0.01)

    BZ = Z + 0.12

    # Mine entrance building (stone, classical style)
    wall_h = 1.5
    bmesh_box("MineHouse", (1.8, 1.4, wall_h), (0.0, 0.2, BZ + wall_h / 2), m['stone_light'], bevel=0.02)

    # Cornice
    bmesh_box("Cornice", (1.9, 1.5, 0.05), (0.0, 0.2, BZ + wall_h), m['stone_trim'], bevel=0.02)

    # Pitched tile roof
    rv = [
        (-1.0, -0.60, BZ + wall_h + 0.02), (1.0, -0.60, BZ + wall_h + 0.02),
        (1.0, 1.00, BZ + wall_h + 0.02), (-1.0, 1.00, BZ + wall_h + 0.02),
        (0, -0.60, BZ + wall_h + 0.60), (0, 1.00, BZ + wall_h + 0.60),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("Roof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Columned entrance (4 columns across front)
    col_h = 1.35
    for y in [-0.30, -0.05, 0.20, 0.45]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.055, depth=col_h,
                                            location=(1.05, y + 0.1, BZ + col_h / 2))
        c = bpy.context.active_object
        c.name = f"Col_{y:.2f}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        bmesh_box(f"Cap_{y:.2f}", (0.13, 0.13, 0.04), (1.05, y + 0.1, BZ + col_h + 0.02), m['stone_trim'])
        bmesh_box(f"Base_{y:.2f}", (0.12, 0.12, 0.03), (1.05, y + 0.1, BZ + 0.015), m['stone_trim'])

    # Portico slab
    bmesh_box("Portico", (0.35, 1.0, 0.04), (1.05, 0.2, BZ + col_h + 0.04), m['stone_trim'])

    # Small pediment
    pv = [(1.08, -0.28, BZ + col_h + 0.06), (1.08, 0.68, BZ + col_h + 0.06),
          (1.08, 0.2, BZ + col_h + 0.30)]
    mesh_from_pydata("Pediment", pv, [(0, 1, 2)], m['stone_light'])

    # Mine entrance (dark opening)
    bmesh_box("MineEntrance", (0.06, 0.40, 0.80), (0.91, 0.2, BZ + 0.40), m['stone_dark'])

    # Steps to entrance
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.14, 0.85, 0.04), (1.20 + i * 0.14, 0.2, BZ - 0.02 - i * 0.04), m['stone_light'])

    # Aqueduct-style water channel (raised on small arches)
    # Channel base running along the side
    bmesh_box("Aqueduct", (3.0, 0.16, 0.06), (0.0, -0.85, Z + 0.45), m['stone_light'])
    # Water in channel
    bmesh_box("AqWater", (2.8, 0.10, 0.02), (0.0, -0.85, Z + 0.50), m['window'])
    # Support pillars for aqueduct
    for ax in [-1.10, -0.40, 0.30, 1.00]:
        bmesh_box(f"AqPillar_{ax:.2f}", (0.10, 0.12, 0.45), (ax, -0.85, Z + 0.22), m['stone_light'])
        # Small arch suggestion (horizontal band)
        bmesh_box(f"AqArch_{ax:.2f}", (0.06, 0.14, 0.04), (ax, -0.85, Z + 0.42), m['stone_trim'])

    # Gold ingot stack (neatly arranged Roman-style)
    for row in range(3):
        for col in range(2):
            bmesh_box(f"Ingot_{row}_{col}", (0.12, 0.07, 0.04),
                      (-0.70 + col * 0.14, 0.80 + row * 0.09, BZ + 0.02 + row * 0.045), m['gold'])

    # Acroterion (gold ornament on roof peak)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0, 0.2, BZ + wall_h + 0.63))
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()


# ============================================================
# MEDIEVAL AGE -- Mine shaft with headframe, windlass, ore cart, smelting shed
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stone foundation
    bmesh_box("Found", (2.6, 2.2, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.15

    # Mine shaft opening (stone-lined)
    bmesh_box("ShaftWall", (0.80, 0.80, 0.25), (0.15, 0.15, BZ + 0.125), m['stone'])
    bmesh_box("ShaftHole", (0.55, 0.55, 0.27), (0.15, 0.15, BZ + 0.115), m['stone_dark'])

    # Wooden headframe (tall A-frame with windlass)
    # Main legs (4 angled beams converging above shaft)
    for dx, dy in [(0.45, 0.45), (0.45, -0.15), (-0.15, 0.45), (-0.15, -0.15)]:
        fv = [(0.15 + dx, 0.15 + dy, BZ + 0.25), (0.15 + dx * 0.95, 0.15 + dy * 0.95, BZ + 0.25),
              (0.15 + dx * 0.10, 0.15 + dy * 0.10, BZ + 2.00), (0.15 + dx * 0.05, 0.15 + dy * 0.05, BZ + 2.00)]
        mesh_from_pydata(f"HFLeg_{dx:.2f}_{dy:.2f}", fv, [(0, 1, 2, 3)], m['wood_beam'])

    # Top platform / crossbeams
    bmesh_box("HFTopX", (0.06, 0.65, 0.06), (0.15, 0.15, BZ + 2.00), m['wood_dark'])
    bmesh_box("HFTopY", (0.65, 0.06, 0.06), (0.15, 0.15, BZ + 2.00), m['wood_dark'])

    # Horizontal braces at mid-height
    bmesh_box("HFBraceX", (0.04, 0.75, 0.04), (0.15, 0.15, BZ + 1.10), m['wood'])
    bmesh_box("HFBraceY", (0.75, 0.04, 0.04), (0.15, 0.15, BZ + 1.10), m['wood'])

    # Windlass (horizontal drum with rope)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06, depth=0.50,
                                        location=(0.15, 0.15, BZ + 1.80))
    windlass = bpy.context.active_object
    windlass.name = "Windlass"
    windlass.rotation_euler = (0, math.radians(90), 0)
    windlass.data.materials.append(m['wood_dark'])
    # Windlass handle
    bmesh_box("WHandle", (0.04, 0.04, 0.18), (0.42, 0.15, BZ + 1.80), m['iron'])

    # Rope from windlass
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=1.20,
                                        location=(0.15, 0.15, BZ + 1.00))
    bpy.context.active_object.name = "WRope"
    bpy.context.active_object.data.materials.append(m['roof_edge'])

    # Ore cart on rails (small cart with gold ore)
    # Rails
    for ry in [-0.08, 0.08]:
        bmesh_box(f"Rail_{ry:.2f}", (1.20, 0.03, 0.03), (0.90, 0.15 + ry, BZ + 0.015), m['iron'])
    # Cart body
    bmesh_box("CartBody", (0.35, 0.25, 0.12), (1.10, 0.15, BZ + 0.12), m['wood_dark'])
    bmesh_box("CartFront", (0.03, 0.25, 0.18), (1.28, 0.15, BZ + 0.15), m['wood'])
    bmesh_box("CartBack", (0.03, 0.25, 0.18), (0.92, 0.15, BZ + 0.15), m['wood'])
    # Cart wheels
    for dy in [-0.14, 0.14]:
        bmesh_prism(f"CWheel_{dy:.2f}", 0.05, 0.03, 8, (1.10, 0.15 + dy, BZ + 0.05), m['iron'])
    # Gold ore in cart
    for i, (gx, gy) in enumerate([(1.05, 0.10), (1.15, 0.20), (1.08, 0.18)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(gx, gy, BZ + 0.26))
        bpy.context.active_object.name = f"CartGold_{i}"
        bpy.context.active_object.data.materials.append(m['gold'])

    # Smelting shed (small covered workspace)
    shed_h = 1.2
    bmesh_box("ShedWalls", (1.0, 0.80, shed_h), (-0.85, -0.60, BZ + shed_h / 2), m['plaster'], bevel=0.02)
    # Shed pitched roof
    srv = [
        (-1.40, -1.05, BZ + shed_h), (-0.30, -1.05, BZ + shed_h),
        (-0.30, -0.15, BZ + shed_h), (-1.40, -0.15, BZ + shed_h),
        (-0.85, -1.05, BZ + shed_h + 0.50), (-0.85, -0.15, BZ + shed_h + 0.50),
    ]
    srf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    sr = mesh_from_pydata("ShedRoof", srv, srf, m['roof'])
    for p in sr.data.polygons:
        p.use_smooth = True
    # Shed door
    bmesh_box("ShedDoor", (0.06, 0.30, 0.65), (-0.34, -0.60, BZ + 0.33), m['door'])
    # Shed chimney (for smelting)
    bmesh_box("ShedChimney", (0.14, 0.14, 0.60), (-1.15, -0.30, BZ + shed_h + 0.30), m['stone'], bevel=0.02)

    # Gold pile (finished product near shed)
    for i, (gx, gy, gr) in enumerate([
        (-0.50, -1.10, 0.06), (-0.40, -1.15, 0.05), (-0.55, -1.20, 0.055),
        (-0.42, -1.05, 0.05)
    ]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=gr, location=(gx, gy, BZ + gr * 0.6))
        bpy.context.active_object.name = f"GoldPile_{i}"
        bpy.context.active_object.data.materials.append(m['gold'])

    # Gold ingots stacked near shed
    for row in range(2):
        for col in range(3):
            bmesh_box(f"Ingot_{row}_{col}", (0.10, 0.06, 0.035),
                      (-0.20 + col * 0.12, -1.10, BZ + 0.02 + row * 0.04), m['gold'])

    # Barrel
    bmesh_prism("Barrel", 0.09, 0.20, 8, (0.70, -0.70, BZ), m['wood_dark'])


# ============================================================
# GUNPOWDER AGE -- Stone headhouse, mechanical windlass, powder storage
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stone foundation
    bmesh_box("Found", (2.8, 2.2, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.15

    # Mine headhouse (stone building over shaft)
    hh_h = 1.8
    bmesh_box("Headhouse", (1.6, 1.4, hh_h), (0.2, 0.1, BZ + hh_h / 2), m['stone'], bevel=0.02)

    # Floor beam decoration
    bmesh_box("FloorBeam", (1.62, 1.42, 0.05), (0.2, 0.1, BZ + 0.90), m['wood_beam'])

    # Upper section with plaster
    bmesh_box("UpperWalls", (1.65, 1.45, 0.05), (0.2, 0.1, BZ + hh_h), m['stone_trim'])

    # Timber frame on upper floor
    for y in [-0.45, 0.0, 0.45]:
        bmesh_box(f"UVBeam_{y:.2f}", (0.05, 0.06, hh_h / 2), (1.01, y + 0.1, BZ + hh_h * 0.75), m['wood_beam'])
    for z_off in [0.90, hh_h - 0.04]:
        bmesh_box(f"UHBeam_{z_off:.2f}", (0.05, 1.4, 0.06), (1.01, 0.1, BZ + z_off), m['wood_beam'])

    # Pitched roof
    top_z = BZ + hh_h
    rv = [
        (-0.65, -0.65, top_z), (1.05, -0.65, top_z),
        (1.05, 0.85, top_z), (-0.65, 0.85, top_z),
        (0.20, -0.65, top_z + 0.80), (0.20, 0.85, top_z + 0.80),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("HeadRoof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True
    bmesh_box("HeadRidge", (0.05, 1.54, 0.05), (0.20, 0.1, top_z + 0.80), m['wood_dark'])

    # Large door (mine entrance)
    bmesh_box("Door", (0.07, 0.45, 1.0), (1.01, 0.1, BZ + 0.50), m['door'])
    bmesh_box("DoorSurround", (0.08, 0.53, 0.05), (1.02, 0.1, BZ + 1.02), m['stone_trim'])

    # Windows
    for y in [-0.30, 0.50]:
        bmesh_box(f"Win_{y:.2f}", (0.05, 0.14, 0.22), (1.01, y, BZ + 1.30), m['window'])

    # Mechanical windlass (large wooden drum with gears)
    # Windlass housing on roof
    bmesh_box("WindlassHouse", (0.40, 0.50, 0.30), (0.20, 0.1, top_z + 0.15), m['wood'])
    # Large drum
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.12, depth=0.40,
                                        location=(0.20, 0.1, top_z + 0.35))
    drum = bpy.context.active_object
    drum.name = "WindlassDrum"
    drum.rotation_euler = (0, math.radians(90), 0)
    drum.data.materials.append(m['wood_dark'])
    # Crank arm
    bmesh_box("Crank", (0.04, 0.04, 0.25), (0.42, 0.1, top_z + 0.35), m['iron'])

    # Steps
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.14, 0.80, 0.04), (1.14 + i * 0.14, 0.1, BZ - 0.02 - i * 0.04), m['stone_dark'])

    # Blackpowder storage (small reinforced shed, off to side)
    bmesh_box("PowderShed", (0.60, 0.50, 0.65), (-1.05, -0.70, BZ + 0.325), m['stone_dark'], bevel=0.02)
    bmesh_box("PowderRoof", (0.65, 0.55, 0.05), (-1.05, -0.70, BZ + 0.68), m['iron'])
    bmesh_box("PowderDoor", (0.05, 0.22, 0.40), (-0.74, -0.70, BZ + 0.20), m['door'])
    # Warning: small red/banner mark
    bmesh_box("PowderMark", (0.04, 0.10, 0.10), (-0.74, -0.70, BZ + 0.55), m['banner'])

    # Ore processing area (crushing stone)
    bmesh_box("CrushBase", (0.50, 0.40, 0.12), (1.10, -0.80, BZ + 0.06), m['stone_dark'])
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.16, depth=0.08,
                                        location=(1.10, -0.80, BZ + 0.16))
    bpy.context.active_object.name = "CrushStone"
    bpy.context.active_object.data.materials.append(m['stone'])

    # Gold ore pile near processing
    for i, (gx, gy) in enumerate([(1.35, -0.55), (1.40, -0.65), (1.30, -0.60)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=(gx, gy, BZ + 0.04))
        bpy.context.active_object.name = f"GoldOre_{i}"
        bpy.context.active_object.data.materials.append(m['gold'])

    # Finished gold ingots
    for col in range(3):
        bmesh_box(f"Ingot_{col}", (0.11, 0.06, 0.04),
                  (-0.90 + col * 0.13, 0.80, BZ + 0.02), m['gold'])

    # Stone boundary wall segment
    bmesh_box("BoundWall", (0.10, 2.8, 0.50), (1.45, -0.10, Z + 0.25), m['stone_dark'])


# ============================================================
# ENLIGHTENMENT AGE -- Brick engine house, beam pump, chimney
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Foundation
    bmesh_box("Found", (2.8, 2.3, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.12

    # Engine house (tall brick building housing beam pump)
    eh_h = 2.2
    bmesh_box("EngineHouse", (1.4, 1.2, eh_h), (0.3, 0.3, BZ + eh_h / 2), m['stone'], bevel=0.02)

    # Quoins (corner decorations)
    for xs in [-1, 1]:
        for ys in [-1, 1]:
            for z_off in [0.12, 0.50, 0.88, 1.26, 1.64, 2.02]:
                bmesh_box(f"Quoin_{xs}_{ys}_{z_off:.2f}", (0.04, 0.04, 0.14),
                          (0.3 + xs * 0.71, 0.3 + ys * 0.61, BZ + z_off), m['stone_light'])

    # String course
    bmesh_box("StringCourse", (1.44, 1.24, 0.04), (0.3, 0.3, BZ + 1.10), m['stone_trim'], bevel=0.01)

    # Cornice
    bmesh_box("Cornice", (1.48, 1.28, 0.06), (0.3, 0.3, BZ + eh_h), m['stone_trim'], bevel=0.02)

    # Hipped roof
    pyramid_roof("EngineRoof", w=1.2, d=1.0, h=0.55, overhang=0.12,
                 origin=(0.3, 0.3, BZ + eh_h + 0.03), material=m['roof'])

    # Door
    bmesh_box("Door", (0.06, 0.36, 0.90), (1.01, 0.3, BZ + 0.45), m['door'])
    bmesh_box("DoorSurround", (0.07, 0.44, 0.98), (1.02, 0.3, BZ + 0.49), m['stone_light'])
    bmesh_box("Fanlight", (0.05, 0.36, 0.08), (1.01, 0.3, BZ + 0.92), m['window'])

    # Ground floor windows
    for y in [-0.10, 0.70]:
        bmesh_box(f"GWin_{y:.2f}", (0.05, 0.18, 0.40), (1.01, y, BZ + 0.48), m['window'])
        bmesh_box(f"GWinH_{y:.2f}", (0.06, 0.22, 0.03), (1.02, y, BZ + 0.70), m['stone_trim'])

    # First floor windows
    for y in [-0.10, 0.30, 0.70]:
        bmesh_box(f"FWin_{y:.2f}", (0.05, 0.16, 0.35), (1.01, y, BZ + 1.45), m['window'])
        bmesh_box(f"FWinH_{y:.2f}", (0.06, 0.20, 0.03), (1.02, y, BZ + 1.65), m['stone_trim'])

    # Steps
    for i in range(3):
        bmesh_box(f"Step_{i}", (0.14, 0.75, 0.04), (1.12 + i * 0.14, 0.3, BZ - 0.02 - i * 0.04), m['stone_light'])

    # Tall chimney (prominent, brick)
    chimney_h = 3.0
    bmesh_prism("Chimney", 0.18, chimney_h, 8, (-0.60, 0.80, BZ), m['stone'], bevel=0.02)
    bmesh_prism("ChimBand1", 0.20, 0.06, 8, (-0.60, 0.80, BZ + 1.0), m['stone_trim'])
    bmesh_prism("ChimBand2", 0.20, 0.06, 8, (-0.60, 0.80, BZ + 2.0), m['stone_trim'])
    bmesh_prism("ChimTop", 0.22, 0.08, 8, (-0.60, 0.80, BZ + chimney_h - 0.08), m['stone_trim'])

    # Beam pump (extending from engine house)
    # Pivot point on engine house wall
    bmesh_box("PivotMount", (0.12, 0.20, 0.20), (0.3, -0.32, BZ + eh_h + 0.10), m['iron'])
    # Pump beam (long horizontal bar, slightly angled)
    bmesh_box("PumpBeam", (1.30, 0.06, 0.08), (0.3, -0.35, BZ + eh_h + 0.22), m['wood_dark'])
    # Pump rod (vertical, going down into shaft)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=1.80,
                                        location=(0.90, -0.35, BZ + 1.20))
    bpy.context.active_object.name = "PumpRod"
    bpy.context.active_object.data.materials.append(m['iron'])

    # Mine shaft opening
    bmesh_box("ShaftRim", (0.65, 0.65, 0.18), (0.90, -0.35, BZ + 0.09), m['stone'])
    bmesh_box("ShaftHole", (0.45, 0.45, 0.20), (0.90, -0.35, BZ + 0.08), m['stone_dark'])

    # Ore wagons (two small wooden wagons)
    for i, wx in enumerate([1.20, 1.55]):
        bmesh_box(f"Wagon_{i}", (0.28, 0.20, 0.10), (wx, -0.90, BZ + 0.10), m['wood_dark'])
        for dy in [-0.12, 0.12]:
            bmesh_prism(f"WWheel_{i}_{dy:.2f}", 0.05, 0.025, 8,
                        (wx, -0.90 + dy, BZ + 0.05), m['iron'])
        # Gold ore in wagons
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(wx, -0.90, BZ + 0.20))
        bpy.context.active_object.name = f"WagonOre_{i}"
        bpy.context.active_object.data.materials.append(m['gold'])

    # Gold ingot storage (stacked neatly)
    for row in range(2):
        for col in range(4):
            bmesh_box(f"Ingot_{row}_{col}", (0.10, 0.06, 0.035),
                      (-0.90 + col * 0.12, -0.60 + row * 0.08, BZ + 0.02 + row * 0.04), m['gold'])

    # Iron fence along front
    for i in range(7):
        fy = -0.60 + i * 0.24
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.008, depth=0.35,
                                            location=(1.40, fy, BZ + 0.075))
        bpy.context.active_object.data.materials.append(m['iron'])


# ============================================================
# INDUSTRIAL AGE -- Coal mine headframe, winding gear, pithead buildings
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Foundation
    bmesh_box("Found", (2.8, 2.3, 0.10), (0, 0, Z + 0.05), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.10

    # Steel headframe (tall lattice tower over shaft)
    hf_h = 3.0
    # Four main legs of headframe
    for dx, dy in [(0.30, 0.30), (0.30, -0.30), (-0.30, 0.30), (-0.30, -0.30)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.035, depth=hf_h,
                                            location=(dx, dy, BZ + hf_h / 2))
        leg = bpy.context.active_object
        leg.name = f"HFLeg_{dx:.2f}_{dy:.2f}"
        leg.data.materials.append(m['iron'])

    # Horizontal braces on headframe
    for hz in [BZ + 0.60, BZ + 1.20, BZ + 1.80, BZ + 2.40]:
        bmesh_box(f"HFBraceX_{hz:.2f}", (0.65, 0.03, 0.03), (0, 0, hz), m['iron'])
        bmesh_box(f"HFBraceY_{hz:.2f}", (0.03, 0.65, 0.03), (0, 0, hz), m['iron'])

    # Diagonal braces (X-pattern on sides)
    for dy in [-0.30, 0.30]:
        dv = [(0.30, dy, BZ + 0.60), (0.30, dy, BZ + 0.65),
              (-0.30, dy, BZ + 1.20), (-0.30, dy, BZ + 1.15)]
        mesh_from_pydata(f"HFDiagL_{dy:.2f}", dv, [(0, 1, 2, 3)], m['iron'])
        dv2 = [(-0.30, dy, BZ + 0.60), (-0.30, dy, BZ + 0.65),
               (0.30, dy, BZ + 1.20), (0.30, dy, BZ + 1.15)]
        mesh_from_pydata(f"HFDiagR_{dy:.2f}", dv2, [(0, 1, 2, 3)], m['iron'])

    # Top platform of headframe
    bmesh_box("HFPlatform", (0.70, 0.70, 0.05), (0, 0, BZ + hf_h + 0.025), m['iron'])

    # Winding wheel at top (large sheave)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.22, depth=0.06,
                                        location=(0, 0, BZ + hf_h + 0.08))
    wheel = bpy.context.active_object
    wheel.name = "WindingWheel"
    wheel.rotation_euler = (math.radians(90), 0, 0)
    wheel.data.materials.append(m['iron'])
    bpy.ops.object.shade_smooth()

    # Mine shaft opening
    bmesh_box("ShaftRim", (0.70, 0.70, 0.18), (0, 0, BZ + 0.09), m['stone'])
    bmesh_box("ShaftHole", (0.50, 0.50, 0.20), (0, 0, BZ + 0.08), m['stone_dark'])

    # Rope/cable from wheel to shaft
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=hf_h - 0.30,
                                        location=(0, 0, BZ + hf_h / 2 + 0.15))
    bpy.context.active_object.name = "Cable"
    bpy.context.active_object.data.materials.append(m['iron'])

    # Pithead building (winding engine house)
    ph_h = 1.6
    bmesh_box("PitHead", (1.2, 1.0, ph_h), (-1.0, 0.0, BZ + ph_h / 2), m['stone'], bevel=0.02)
    # Iron beam grid on facade
    for z in [BZ + 0.5, BZ + 1.0]:
        bmesh_box(f"PHIronH_{z:.1f}", (0.03, 1.0, 0.03), (-0.39, 0, z), m['iron'])
    bmesh_box("PHBand", (1.24, 1.04, 0.04), (-1.0, 0.0, BZ + 0.80), m['stone_trim'])

    # Pithead flat roof
    bmesh_box("PHRoof", (1.25, 1.05, 0.06), (-1.0, 0.0, BZ + ph_h + 0.03), m['stone_dark'])

    # Pithead door
    bmesh_box("PHDoor", (0.06, 0.35, 0.85), (-0.39, 0.0, BZ + 0.43), m['door'])

    # Pithead windows
    for y in [-0.30, 0.30]:
        bmesh_box(f"PHWin_{y:.2f}", (0.05, 0.16, 0.28), (-0.39, y, BZ + 1.10), m['window'])

    # Chimney on pithead building
    bmesh_box("PHChimney", (0.18, 0.18, 1.2), (-1.40, 0.35, BZ + ph_h + 0.20), m['stone'], bevel=0.02)
    bmesh_box("PHChimTop", (0.22, 0.22, 0.05), (-1.40, 0.35, BZ + ph_h + 0.82), m['stone_trim'])

    # Rail tracks (running from shaft to edge)
    for ry in [-0.08, 0.08]:
        bmesh_box(f"Track_{ry:.2f}", (2.20, 0.025, 0.025), (0.80, ry - 0.70, BZ + 0.012), m['iron'])
    # Sleepers / ties
    for tx in range(8):
        bmesh_box(f"Sleeper_{tx}", (0.04, 0.22, 0.02),
                  (-0.20 + tx * 0.30, -0.70, BZ + 0.01), m['wood_dark'])

    # Ore cart on tracks
    bmesh_box("OreCart", (0.35, 0.20, 0.15), (0.80, -0.70, BZ + 0.12), m['iron'])
    # Gold ore in cart
    for i, (gx, gy) in enumerate([(0.75, -0.75), (0.85, -0.65), (0.80, -0.70)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(gx, gy, BZ + 0.24))
        bpy.context.active_object.name = f"OreCartGold_{i}"
        bpy.context.active_object.data.materials.append(m['gold'])

    # Conveyor belt suggestion (angled ramp)
    bmesh_box("Conveyor", (0.80, 0.20, 0.04), (1.20, 0.80, BZ + 0.40), m['iron'])
    # Conveyor supports
    for cx in [0.90, 1.50]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.40,
                                            location=(cx, 0.80, BZ + 0.20))
        bpy.context.active_object.data.materials.append(m['iron'])

    # Gold ore stockpile
    for i, (gx, gy, gr) in enumerate([
        (1.10, 0.80, 0.07), (1.20, 0.85, 0.06), (1.15, 0.75, 0.065)
    ]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=gr, location=(gx, gy, BZ + 0.55))
        bpy.context.active_object.name = f"Stockpile_{i}"
        bpy.context.active_object.data.materials.append(m['gold'])


# ============================================================
# MODERN AGE -- Steel headframe, processing plant, dump truck, conveyor
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.08
    bmesh_box("Found", (3.2, 2.8, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # Steel headframe (modern lattice tower)
    hf_h = 3.2
    # Four main I-beam legs
    for dx, dy in [(0.25, 0.25), (0.25, -0.25), (-0.25, 0.25), (-0.25, -0.25)]:
        bmesh_box(f"HFLeg_{dx:.2f}_{dy:.2f}", (0.06, 0.06, hf_h),
                  (dx, dy, BZ + hf_h / 2), metal)

    # Horizontal braces
    for hz in [BZ + 0.60, BZ + 1.30, BZ + 2.00, BZ + 2.70]:
        bmesh_box(f"HFBraceX_{hz:.2f}", (0.55, 0.03, 0.03), (0, 0, hz), metal)
        bmesh_box(f"HFBraceY_{hz:.2f}", (0.03, 0.55, 0.03), (0, 0, hz), metal)

    # Top crane/sheave housing
    bmesh_box("SheaveHouse", (0.55, 0.55, 0.20), (0, 0, BZ + hf_h + 0.10), metal)
    # Sheave wheel
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.20, depth=0.05,
                                        location=(0, 0, BZ + hf_h + 0.25))
    sheave = bpy.context.active_object
    sheave.name = "Sheave"
    sheave.rotation_euler = (math.radians(90), 0, 0)
    sheave.data.materials.append(metal)
    bpy.ops.object.shade_smooth()

    # Mine shaft
    bmesh_box("ShaftRim", (0.60, 0.60, 0.15), (0, 0, BZ + 0.075), m['stone'])
    bmesh_box("ShaftHole", (0.42, 0.42, 0.17), (0, 0, BZ + 0.065), m['stone_dark'])

    # Processing plant (large building)
    pp_h = 1.8
    bmesh_box("ProcessPlant", (1.4, 1.2, pp_h), (-0.95, 0.0, BZ + pp_h / 2), m['stone'], bevel=0.02)
    bmesh_box("PPRoof", (1.5, 1.3, 0.06), (-0.95, 0.0, BZ + pp_h + 0.03), metal)

    # Large windows on processing plant
    bmesh_box("PPGlass", (0.05, 0.80, pp_h - 0.5), (-0.24, 0.0, BZ + pp_h / 2 + 0.15), glass)
    # Mullions
    for y in [-0.25, 0.0, 0.25]:
        bmesh_box(f"PPMull_{y:.2f}", (0.03, 0.02, pp_h - 0.5), (-0.24, y, BZ + pp_h / 2 + 0.15), metal)
    bmesh_box("PPHMull", (0.03, 0.82, 0.02), (-0.24, 0.0, BZ + pp_h / 2), metal)

    # Processing plant door
    bmesh_box("PPDoor", (0.05, 0.40, 1.10), (-0.24, -0.40, BZ + 0.55), metal)

    # Side windows
    for x in [-1.20, -0.70]:
        bmesh_box(f"PPSWin_{x:.2f}", (0.25, 0.05, 0.45), (x, -0.61, BZ + 1.15), glass)

    # Conveyor belt (angled, from shaft to processing)
    # Belt supports
    conv_verts = [(-0.25, -0.10, BZ + pp_h - 0.20), (0.35, -0.10, BZ + 0.50),
                  (0.35, 0.10, BZ + 0.50), (-0.25, 0.10, BZ + pp_h - 0.20)]
    mesh_from_pydata("ConveyorBelt", conv_verts, [(0, 1, 2, 3)], metal)
    # Conveyor frame
    bmesh_box("ConvFrame1", (0.04, 0.04, 0.60), (0.30, -0.10, BZ + 0.30), metal)
    bmesh_box("ConvFrame2", (0.04, 0.04, 0.60), (0.30, 0.10, BZ + 0.30), metal)
    bmesh_box("ConvFrame3", (0.04, 0.04, pp_h - 0.30), (-0.25, -0.10, BZ + (pp_h - 0.30) / 2), metal)
    bmesh_box("ConvFrame4", (0.04, 0.04, pp_h - 0.30), (-0.25, 0.10, BZ + (pp_h - 0.30) / 2), metal)

    # Gold ore on conveyor
    for i, (cx, cz) in enumerate([(0.15, BZ + 0.65), (0.0, BZ + 0.90), (-0.12, BZ + 1.10)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04, location=(cx, 0.0, cz + 0.06))
        bpy.context.active_object.name = f"ConvOre_{i}"
        bpy.context.active_object.data.materials.append(m['gold'])

    # Dump truck (simplified shape)
    # Truck body
    bmesh_box("TruckBed", (0.50, 0.30, 0.15), (1.15, -0.75, BZ + 0.20), m['stone_dark'])
    bmesh_box("TruckCab", (0.20, 0.28, 0.22), (1.45, -0.75, BZ + 0.28), metal)
    bmesh_box("TruckCabGlass", (0.05, 0.24, 0.12), (1.55, -0.75, BZ + 0.36), glass)
    # Truck wheels
    for dx in [-0.15, 0.15]:
        for dy in [-0.17, 0.17]:
            bmesh_prism(f"TruckWheel_{dx:.2f}_{dy:.2f}", 0.06, 0.03, 8,
                        (1.15 + dx, -0.75 + dy, BZ + 0.06), m['stone_dark'])
    # Gold in truck bed
    for i, (gx, gy) in enumerate([(1.10, -0.80), (1.20, -0.70), (1.15, -0.75)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(gx, gy, BZ + 0.35))
        bpy.context.active_object.name = f"TruckGold_{i}"
        bpy.context.active_object.data.materials.append(m['gold'])

    # Gold ore stockpile (large mound near plant)
    for i, (sx, sy, sr) in enumerate([
        (-0.95, -0.90, 0.10), (-0.85, -0.85, 0.08), (-1.05, -0.85, 0.09),
        (-0.90, -0.80, 0.07)
    ]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=sr, location=(sx, sy, BZ + sr * 0.5))
        bpy.context.active_object.name = f"StockGold_{i}"
        bpy.context.active_object.scale = (1, 1, 0.5)
        bpy.context.active_object.data.materials.append(m['gold'])

    # Safety railing around shaft
    for i in range(8):
        angle = (2 * math.pi * i) / 8
        rx, ry = 0.45 * math.cos(angle), 0.45 * math.sin(angle)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=0.50,
                                            location=(rx, ry, BZ + 0.40))
        bpy.context.active_object.data.materials.append(metal)


# ============================================================
# DIGITAL AGE -- Automated extraction, robotic drill, processing pod
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (3.5, 3.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.06
    bmesh_box("Found", (3.0, 2.6, 0.06), (0, 0, Z + 0.03), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # Base platform (clean hexagonal)
    bmesh_prism("BasePlat", 1.6, 0.08, 8, (0, 0, BZ), metal)

    # Robotic drill rig (central, tall mechanical arm)
    # Main drill column
    bmesh_prism("DrillColumn", 0.12, 2.80, 8, (0.0, 0.0, BZ + 0.08), metal)
    # Drill head (cone pointing down, at base)
    bmesh_cone("DrillHead", 0.18, 0.30, 10, (0.0, 0.0, BZ + 0.08), m['iron'])
    # Drill housing at top
    bmesh_prism("DrillHousing", 0.22, 0.30, 8, (0.0, 0.0, BZ + 2.58), metal)
    # Rotating motor section
    bmesh_prism("DrillMotor", 0.16, 0.15, 10, (0.0, 0.0, BZ + 2.88), m['stone_trim'])

    # Support arms (three radial stabilizers)
    for i in range(3):
        a = (2 * math.pi * i) / 3
        arm_x = 0.55 * math.cos(a)
        arm_y = 0.55 * math.sin(a)
        # Angled support from ground to drill column at mid-height
        sv = [(arm_x, arm_y, BZ + 0.10), (arm_x * 0.95, arm_y * 0.95, BZ + 0.10),
              (0.06 * math.cos(a), 0.06 * math.sin(a), BZ + 1.50),
              (0.03 * math.cos(a), 0.03 * math.sin(a), BZ + 1.50)]
        mesh_from_pydata(f"DrillArm_{i}", sv, [(0, 1, 2, 3)], metal)
        # Foot pad
        bmesh_prism(f"FootPad_{i}", 0.10, 0.04, 6, (arm_x, arm_y, BZ + 0.08), metal)

    # LED ring around drill base (indicating active drilling)
    bmesh_prism("DrillLED", 0.30, 0.03, 12, (0, 0, BZ + 0.08), m['gold'])

    # Processing pod (enclosed glass/metal structure)
    pod_h = 1.8
    # Pod body (rounded rectangle via sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.65, location=(-1.0, 0.0, BZ + pod_h / 2 + 0.20))
    pod = bpy.context.active_object
    pod.name = "ProcessPod"
    pod.scale = (0.9, 0.7, 1.0)
    pod.data.materials.append(glass)
    bpy.ops.object.shade_smooth()

    # Pod frame ribs
    for z_off in [0.40, 0.80, 1.20, 1.60]:
        bmesh_box(f"PodRib_{z_off:.2f}", (0.04, 0.94, 0.04), (-1.0, 0.0, BZ + z_off), metal)
    for y_off in [-0.35, 0.0, 0.35]:
        bmesh_box(f"PodVRib_{y_off:.2f}", (0.04, 0.04, pod_h - 0.30), (-1.0, y_off, BZ + pod_h / 2 + 0.15), metal)

    # Pod entrance
    bmesh_box("PodDoor", (0.06, 0.35, 0.90), (-0.42, 0.0, BZ + 0.55), metal)
    bmesh_box("PodDoorGlass", (0.04, 0.30, 0.80), (-0.41, 0.0, BZ + 0.55), glass)

    # Conveyor pipe from drill to processing pod
    bmesh_box("ConvPipe", (0.80, 0.12, 0.12), (-0.50, 0.0, BZ + 1.00), metal)
    # Gold ore visible in pipe section (transparent window)
    bmesh_box("PipeWindow", (0.20, 0.08, 0.08), (-0.30, 0.0, BZ + 1.00), glass)
    # Gold nuggets visible through window
    for i, px in enumerate([-0.35, -0.25]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.025, location=(px, 0.0, BZ + 1.00))
        bpy.context.active_object.name = f"PipeGold_{i}"
        bpy.context.active_object.data.materials.append(m['gold'])

    # Drone transport pad
    bmesh_prism("DronePad", 0.40, 0.04, 6, (1.15, -0.80, Z + 0.02), m['stone_dark'])
    bmesh_prism("PadRing", 0.30, 0.01, 6, (1.15, -0.80, Z + 0.05), m['gold'])
    bmesh_prism("PadCenter", 0.08, 0.01, 6, (1.15, -0.80, Z + 0.05), m['gold'])

    # Cargo drone (quadcopter with gold payload)
    drone_z = Z + 0.35
    bmesh_box("DroneBody", (0.14, 0.14, 0.05), (1.15, -0.80, drone_z), metal)
    for dx, dy in [(-0.13, -0.13), (-0.13, 0.13), (0.13, -0.13), (0.13, 0.13)]:
        bmesh_box(f"DroneArm_{dx:.2f}_{dy:.2f}", (0.10, 0.02, 0.02),
                  (1.15 + dx, -0.80 + dy, drone_z), metal)
        bmesh_prism(f"Rotor_{dx:.2f}_{dy:.2f}", 0.06, 0.01, 8,
                    (1.15 + dx * 1.5, -0.80 + dy * 1.5, drone_z + 0.02), m['gold'])
    # Gold payload under drone
    bmesh_box("DronePayload", (0.08, 0.08, 0.04), (1.15, -0.80, drone_z - 0.04), m['gold'])

    # Holographic display (floating screen near processing pod)
    # Display stand
    bmesh_box("HoloStand", (0.06, 0.06, 0.50), (0.80, 0.70, Z + 0.25), metal)
    # Holographic screen (semi-transparent, glowing)
    bmesh_box("HoloScreen", (0.30, 0.04, 0.22), (0.80, 0.72, Z + 0.65), glass)
    # Holographic data bars (floating indicators)
    for i in range(4):
        bar_h = 0.04 + i * 0.03
        bmesh_box(f"HoloBar_{i}", (0.04, 0.02, bar_h),
                  (0.70 + i * 0.07, 0.74, Z + 0.58 + bar_h / 2), m['gold'])

    # LED accent strips around base platform
    bmesh_prism("LEDRing", 1.62, 0.03, 8, (0, 0, BZ + 0.08), m['gold'])

    # Gold output storage (neat glowing containers)
    for i in range(3):
        bmesh_box(f"GoldCrate_{i}", (0.18, 0.14, 0.12),
                  (-0.50 + i * 0.22, -1.00, BZ + 0.06), metal)
        bmesh_box(f"GoldGlow_{i}", (0.14, 0.10, 0.04),
                  (-0.50 + i * 0.22, -1.00, BZ + 0.14), m['gold'])

    # Solar array nearby
    for i in range(2):
        bmesh_box(f"Solar_{i}", (0.45, 0.30, 0.02), (-0.60 + i * 0.55, 1.00, Z + 0.25 + i * 0.02), glass)
        bmesh_box(f"SolarFrame_{i}", (0.47, 0.32, 0.01), (-0.60 + i * 0.55, 1.00, Z + 0.24 + i * 0.02), metal)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.28,
                                        location=(-0.32, 1.00, Z + 0.12))
    bpy.context.active_object.data.materials.append(metal)


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


def build_gold_mine(materials, age='medieval'):
    """Build a Gold Mine with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
