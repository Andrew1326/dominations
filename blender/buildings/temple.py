"""
Temple building -- grand cultural/religious structure per age, a 3x3 tile
prestige building with ornate details and gold accents.

Stone:         Sacred stone circle with menhir stones, central altar, fire pit, bone totems
Bronze:        Stepped ziggurat temple with ramp, altar platform, golden idol, torch stands
Iron:          Celtic/Norse temple -- stone pillars, wooden hall roof, sacred pool, carved totems
Classical:     Greek temple -- full peripteral colonnade, pediment with relief, gold statue, steps
Medieval:      Gothic cathedral -- pointed arches, rose window, bell tower, flying buttresses, cross
Gunpowder:     Renaissance church -- dome, bell tower, arched windows, ornate entrance, cross finial
Enlightenment: Neoclassical church -- grand portico with columns, dome, clock tower, symmetrical
Industrial:    Victorian cathedral -- tall spire, iron framework, large stained glass windows, iron gates
Modern:        Modernist worship center -- clean geometric forms, large glass wall, simple cross/symbol
Digital:       Meditation center -- floating geometric structure, holographic light features, zen garden
"""

import bpy
import bmesh
import math

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# ============================================================
# STONE AGE -- Sacred stone circle with menhir stones
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Raised earth mound platform ===
    bmesh_prism("Mound", 2.4, 0.15, 16, (0, 0, Z), m['stone_dark'])
    bmesh_prism("MoundInner", 1.8, 0.08, 12, (0, 0, Z + 0.15), m['stone_dark'])

    # === Menhir stone circle (12 standing stones) ===
    n_stones = 12
    circle_r = 2.0
    for i in range(n_stones):
        a = (2 * math.pi * i) / n_stones
        px, py = circle_r * math.cos(a), circle_r * math.sin(a)
        h = 1.6 + 0.3 * math.sin(i * 2.1)
        w = 0.22 + 0.06 * math.cos(i * 1.7)
        d = 0.12 + 0.04 * math.sin(i * 3.3)
        bmesh_box(f"Menhir_{i}", (w, d, h), (px, py, Z + h / 2 + 0.15), m['stone'])
        # Slight rotation for natural look
        obj = bpy.data.objects[f"Menhir_{i}"]
        obj.rotation_euler = (0.03 * math.sin(i), 0.03 * math.cos(i), a + math.radians(90))

    # === Lintel stones connecting pairs (like Stonehenge trilithons) ===
    for i in range(0, n_stones, 2):
        a1 = (2 * math.pi * i) / n_stones
        a2 = (2 * math.pi * (i + 1)) / n_stones
        x1, y1 = circle_r * math.cos(a1), circle_r * math.sin(a1)
        x2, y2 = circle_r * math.cos(a2), circle_r * math.sin(a2)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        h1 = 1.6 + 0.3 * math.sin(i * 2.1)
        h2 = 1.6 + 0.3 * math.sin((i + 1) * 2.1)
        lintel_z = Z + 0.15 + min(h1, h2) - 0.05
        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx * dx + dy * dy)
        angle = math.atan2(dy, dx)
        bmesh_box(f"Lintel_{i}", (length + 0.10, 0.16, 0.12), (mx, my, lintel_z), m['stone'])
        bpy.data.objects[f"Lintel_{i}"].rotation_euler = (0, 0, angle)

    # === Central altar (large flat stone on supports) ===
    bmesh_box("AltarBase1", (0.20, 0.20, 0.50), (-0.3, -0.25, Z + 0.40), m['stone_dark'])
    bmesh_box("AltarBase2", (0.20, 0.20, 0.50), (0.3, -0.25, Z + 0.40), m['stone_dark'])
    bmesh_box("AltarBase3", (0.20, 0.20, 0.50), (-0.3, 0.25, Z + 0.40), m['stone_dark'])
    bmesh_box("AltarBase4", (0.20, 0.20, 0.50), (0.3, 0.25, Z + 0.40), m['stone_dark'])
    bmesh_box("AltarSlab", (1.0, 0.8, 0.12), (0, 0, Z + 0.71), m['stone_light'])

    # Gold offering bowl on altar
    bmesh_prism("OfferingBowl", 0.15, 0.08, 10, (0, 0, Z + 0.77), m['gold'])

    # === Fire pit (stone ring with logs) ===
    FX, FY = 0.9, -1.0
    bmesh_prism("FireRing", 0.35, 0.12, 10, (FX, FY, Z + 0.15), m['stone_dark'])
    bmesh_prism("FireInner", 0.25, 0.06, 10, (FX, FY, Z + 0.15), m['stone'])
    for j, angle in enumerate([0.3, -0.4, 0.9, -0.7, 1.5]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=0.4,
                                            location=(FX, FY, Z + 0.22))
        log = bpy.context.active_object
        log.name = f"FireLog_{j}"
        log.rotation_euler = (0.4, angle, 0)
        log.data.materials.append(m['wood_dark'])

    # === Bone/skull totems (tall poles with skulls) ===
    for tx, ty in [(1.8, 1.5), (-1.5, 1.8), (-1.8, -1.0)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.06, depth=2.2,
                                            location=(tx, ty, Z + 1.25))
        t = bpy.context.active_object
        t.name = f"TotemPole_{tx:.1f}_{ty:.1f}"
        t.data.materials.append(m['wood'])
        # Skull at top
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(tx, ty, Z + 2.45))
        sk = bpy.context.active_object
        sk.name = f"Skull_{tx:.1f}_{ty:.1f}"
        sk.scale = (1, 0.8, 1.1)
        sk.data.materials.append(m['stone_light'])
        # Bone crosspiece
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.4,
                                            location=(tx, ty, Z + 2.0))
        bone = bpy.context.active_object
        bone.name = f"Bone_{tx:.1f}_{ty:.1f}"
        bone.rotation_euler = (0, math.radians(90), 0)
        bone.data.materials.append(m['stone_light'])

    # === Carved idol stone (central, taller) ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.14, depth=1.0,
                                        location=(0, -0.8, Z + 0.65))
    idol = bpy.context.active_object
    idol.name = "Idol"
    idol.data.materials.append(m['stone'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0, -0.8, Z + 1.25))
    head = bpy.context.active_object
    head.name = "IdolHead"
    head.scale = (1, 0.7, 1.2)
    head.data.materials.append(m['stone'])

    # Scattered small stones around the circle
    for sx, sy in [(-0.6, 1.5), (1.4, 0.5), (-1.3, -0.4), (0.5, 1.2)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(sx, sy, Z + 0.22))
        stone = bpy.context.active_object
        stone.name = f"SmallStone_{sx:.1f}_{sy:.1f}"
        stone.scale = (1.2, 0.9, 0.6)
        stone.data.materials.append(m['stone_dark'])


# ============================================================
# BRONZE AGE -- Stepped ziggurat temple with ramp
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Ziggurat tiers (5 stepped levels) ===
    tiers = [
        (4.8, 4.4, 0.45),
        (4.0, 3.6, 0.45),
        (3.2, 2.8, 0.45),
        (2.4, 2.0, 0.45),
        (1.6, 1.2, 0.45),
    ]
    tz = Z
    for i, (w, d, h) in enumerate(tiers):
        bmesh_box(f"Tier_{i}", (w, d, h), (0, 0, tz + h / 2), m['stone'], bevel=0.04)
        # Decorative band at top of each tier
        bmesh_box(f"TierBand_{i}", (w + 0.04, d + 0.04, 0.06), (0, 0, tz + h), m['stone_trim'], bevel=0.02)
        tz += h

    BZ = tz  # top of ziggurat

    # === Altar shrine on top ===
    bmesh_box("Shrine", (1.2, 0.8, 1.0), (0, 0, BZ + 0.50), m['stone_light'], bevel=0.03)
    bmesh_box("ShrineRoof", (1.4, 1.0, 0.08), (0, 0, BZ + 1.04), m['stone_trim'], bevel=0.02)

    # Shrine columns (4 at corners)
    for sx, sy in [(-0.5, -0.3), (-0.5, 0.3), (0.5, -0.3), (0.5, 0.3)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06, depth=1.0,
                                            location=(sx, sy, BZ + 0.50))
        col = bpy.context.active_object
        col.name = f"ShrCol_{sx:.1f}_{sy:.1f}"
        col.data.materials.append(m['stone_light'])

    # === Golden idol on altar ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=0.35,
                                        location=(0, 0, BZ + 0.175))
    pedestal = bpy.context.active_object
    pedestal.name = "IdolPedestal"
    pedestal.data.materials.append(m['stone_dark'])

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(0, 0, BZ + 0.50))
    idol_body = bpy.context.active_object
    idol_body.name = "IdolBody"
    idol_body.scale = (0.7, 0.7, 1.2)
    idol_body.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0, 0, BZ + 0.72))
    idol_head = bpy.context.active_object
    idol_head.name = "IdolHead"
    idol_head.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # === Central ramp (front approach) ===
    ramp_steps = 12
    for i in range(ramp_steps):
        step_z = Z + i * (BZ / ramp_steps)
        step_x = 2.4 + 0.18 * (ramp_steps - i)
        step_w = 0.20
        step_d = 1.2
        bmesh_box(f"Ramp_{i}", (step_w, step_d, BZ / ramp_steps + 0.02),
                  (step_x, 0, step_z + (BZ / ramp_steps) / 2), m['stone_dark'])

    # Ramp walls (low balustrades)
    for ys in [-0.65, 0.65]:
        for i in range(6):
            rx = 2.4 + 0.36 * (6 - i)
            rz = Z + i * (BZ / 6) + 0.15
            bmesh_box(f"RampWall_{ys:.1f}_{i}", (0.25, 0.10, 0.30),
                      (rx, ys, rz), m['stone_trim'])

    # === Torch stands (4 at top corners) ===
    for tx, ty in [(-0.7, -0.5), (-0.7, 0.5), (0.7, -0.5), (0.7, 0.5)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.8,
                                            location=(tx, ty, BZ + 0.40))
        torch = bpy.context.active_object
        torch.name = f"Torch_{tx:.1f}_{ty:.1f}"
        torch.data.materials.append(m['iron'])
        # Torch cup
        bmesh_prism(f"TorchCup_{tx:.1f}_{ty:.1f}", 0.07, 0.06, 8,
                    (tx, ty, BZ + 0.80), m['gold'])

    # === Decorative niches on tiers ===
    for tier_i in range(3):
        tier_z = Z + tier_i * 0.45
        tier_w = 4.8 - tier_i * 0.8
        for y in [-0.6, 0, 0.6]:
            bmesh_box(f"Niche_{tier_i}_{y:.1f}", (0.06, 0.14, 0.25),
                      (tier_w / 2 + 0.01, y, tier_z + 0.20), m['stone_dark'])

    # === Banner poles at top ===
    for ty in [-0.4, 0.4]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.8,
                                            location=(0, ty, BZ + 1.44))
        bpy.context.active_object.data.materials.append(m['wood'])
        fv = [(0.03, ty, BZ + 1.55), (0.35, ty + 0.03, BZ + 1.52),
              (0.35, ty + 0.02, BZ + 1.80), (0.03, ty, BZ + 1.78)]
        mesh_from_pydata(f"Banner_{ty:.1f}", fv, [(0, 1, 2, 3)], m['banner'])
    m['banner'].use_backface_culling = False


# ============================================================
# IRON AGE -- Celtic/Norse temple with sacred pool
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Raised stone platform ===
    bmesh_box("Platform", (4.8, 4.2, 0.20), (0, 0, Z + 0.10), m['stone_dark'], bevel=0.05)
    bmesh_box("Platform2", (4.4, 3.8, 0.12), (0, 0, Z + 0.26), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.32

    # === Main hall (long wooden structure with stone base) ===
    hall_w, hall_d = 3.0, 2.2
    hall_h = 2.2
    # Stone lower walls
    bmesh_box("HallBase", (hall_w, hall_d, 0.8), (0, 0, BZ + 0.40), m['stone'], bevel=0.02)
    # Wooden upper walls
    bmesh_box("HallUpper", (hall_w - 0.04, hall_d - 0.04, 1.4), (0, 0, BZ + 0.80 + 0.70), m['wood'], bevel=0.02)

    # === Stone pillar supports (6 per side) ===
    for i in range(6):
        x = -1.2 + i * 0.48
        for ys, lbl in [(-hall_d / 2 - 0.15, "R"), (hall_d / 2 + 0.15, "L")]:
            bmesh_box(f"Pillar_{lbl}_{i}", (0.18, 0.18, 2.4), (x, ys, BZ + 1.20), m['stone'], bevel=0.02)
            bmesh_box(f"PillarCap_{lbl}_{i}", (0.22, 0.22, 0.06), (x, ys, BZ + 2.44), m['stone_trim'])

    # === Grand pitched roof (steep, wooden) ===
    roof_z = BZ + hall_h
    rv = [
        (-hall_w / 2 - 0.20, -hall_d / 2 - 0.30, roof_z),
        (hall_w / 2 + 0.20, -hall_d / 2 - 0.30, roof_z),
        (hall_w / 2 + 0.20, hall_d / 2 + 0.30, roof_z),
        (-hall_w / 2 - 0.20, hall_d / 2 + 0.30, roof_z),
        (0, -hall_d / 2 - 0.30, roof_z + 1.8),
        (0, hall_d / 2 + 0.30, roof_z + 1.8),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("HallRoof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Ridge beam
    bmesh_box("Ridge", (0.08, hall_d + 0.64, 0.08), (0, 0, roof_z + 1.80), m['wood_dark'])

    # Roof edge trim
    bmesh_box("RoofEdgeF", (0.06, hall_d + 0.64, 0.06), (hall_w / 2 + 0.20, 0, roof_z + 0.03), m['wood_dark'])
    bmesh_box("RoofEdgeB", (0.06, hall_d + 0.64, 0.06), (-hall_w / 2 - 0.20, 0, roof_z + 0.03), m['wood_dark'])

    # === Gable end decorations (dragon head carvings) ===
    for ys, lbl in [(-1, "Front"), (1, "Back")]:
        dy = ys * (hall_d / 2 + 0.32)
        # Dragon/beast head at ridge end
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.12, radius2=0.04, depth=0.5,
                                        location=(0, dy, roof_z + 1.90))
        beast = bpy.context.active_object
        beast.name = f"Beast_{lbl}"
        beast.rotation_euler = (ys * math.radians(45), 0, 0)
        beast.data.materials.append(m['wood_dark'])

    # === Sacred pool (stone-lined shallow basin) ===
    PX, PY = 1.8, -1.2
    bmesh_prism("PoolOuter", 0.55, 0.15, 10, (PX, PY, BZ), m['stone'])
    bmesh_prism("PoolInner", 0.42, 0.08, 10, (PX, PY, BZ), m['stone_dark'])
    # Water surface
    bmesh_prism("Water", 0.40, 0.02, 10, (PX, PY, BZ + 0.05), m['window'])

    # === Carved totem poles (3) ===
    totems = [(-1.8, -1.5), (-1.8, 1.5), (1.8, 1.2)]
    for tx, ty in totems:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.10, depth=2.8,
                                            location=(tx, ty, BZ + 1.40))
        t = bpy.context.active_object
        t.name = f"Totem_{tx:.1f}_{ty:.1f}"
        t.data.materials.append(m['wood'])
        # Carved face rings
        for tz in [BZ + 0.7, BZ + 1.5, BZ + 2.3]:
            bmesh_prism(f"TotemRing_{tx:.1f}_{tz:.1f}", 0.13, 0.08, 8,
                        (tx, ty, tz), m['wood_dark'])
        # Top ornament
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(tx, ty, BZ + 2.90))
        head = bpy.context.active_object
        head.name = f"TotemHead_{tx:.1f}_{ty:.1f}"
        head.data.materials.append(m['wood_dark'])

    # === Door (heavy wooden with iron bands) ===
    bmesh_box("Door", (0.10, 0.60, 1.30), (hall_w / 2 + 0.01, 0, BZ + 0.65), m['door'])
    for z_off in [0.3, 0.7, 1.1]:
        bmesh_box(f"IronBand_{z_off:.1f}", (0.11, 0.65, 0.04), (hall_w / 2 + 0.02, 0, BZ + z_off), m['iron'])

    # === Gold offering plates at entrance ===
    for sy in [-0.5, 0.5]:
        bmesh_prism(f"Offering_{sy:.1f}", 0.10, 0.04, 10, (hall_w / 2 + 0.30, sy, BZ), m['gold'])

    # Steps
    for i in range(5):
        bmesh_box(f"Step_{i}", (0.22, 1.4, 0.06),
                  (hall_w / 2 + 0.40 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_dark'])


# ============================================================
# CLASSICAL AGE -- Greek temple with full peripteral colonnade
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Grand stepped platform (stylobate -- 5 steps) ===
    for i in range(5):
        w = 5.0 - i * 0.25
        d = 4.6 - i * 0.20
        bmesh_box(f"Stylobate_{i}", (w, d, 0.08), (0, 0, Z + 0.04 + i * 0.08), m['stone_light'], bevel=0.02)

    BZ = Z + 0.40
    col_h = 2.8
    col_r = 0.11

    # === Cella (inner temple room) ===
    cella_w, cella_d = 2.2, 1.8
    bmesh_box("Cella", (cella_w, cella_d, 2.4), (0, 0, BZ + 1.20), m['stone_light'], bevel=0.02)

    # === Full peripteral colonnade ===
    # Front colonnade (8 columns)
    front_x = 1.65
    for i in range(8):
        y = -1.75 + i * 0.50
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=col_r, depth=col_h,
                                            location=(front_x, y, BZ + col_h / 2))
        c = bpy.context.active_object
        c.name = f"ColF_{i}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        bmesh_box(f"CapF_{i}", (0.26, 0.26, 0.08), (front_x, y, BZ + col_h + 0.04), m['stone_trim'])
        bmesh_box(f"BaseF_{i}", (0.24, 0.24, 0.06), (front_x, y, BZ + 0.03), m['stone_trim'])

    # Back colonnade (8 columns)
    back_x = -1.65
    for i in range(8):
        y = -1.75 + i * 0.50
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=col_r, depth=col_h,
                                            location=(back_x, y, BZ + col_h / 2))
        c = bpy.context.active_object
        c.name = f"ColB_{i}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        bmesh_box(f"CapB_{i}", (0.26, 0.26, 0.08), (back_x, y, BZ + col_h + 0.04), m['stone_trim'])

    # Side columns (6 per side, excluding corners)
    for j in range(6):
        x = -1.1 + j * 0.44
        for ys, lbl in [(-1.75, "R"), (1.75, "L")]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=col_r, depth=col_h,
                                                location=(x, ys, BZ + col_h / 2))
            c = bpy.context.active_object
            c.name = f"Col{lbl}_{j}"
            c.data.materials.append(m['stone_light'])
            bpy.ops.object.shade_smooth()

    # === Entablature (architrave + frieze) ===
    bmesh_box("Entablature", (3.5, 3.7, 0.20), (0, 0, BZ + col_h + 0.10), m['stone_trim'], bevel=0.02)

    # Frieze band with triglyphs
    for i in range(12):
        y = -1.6 + i * 0.30
        bmesh_box(f"Triglyph_{i}", (0.04, 0.08, 0.12), (1.76, y, BZ + col_h + 0.06), m['stone'])

    # === Pediments (front + back) with relief ===
    for xs, name in [(1, "Front"), (-1, "Back")]:
        pv = [(xs * 1.76, -1.85, BZ + col_h + 0.20),
              (xs * 1.76, 1.85, BZ + col_h + 0.20),
              (xs * 1.76, 0, BZ + col_h + 1.10)]
        mesh_from_pydata(f"Pediment_{name}", pv, [(0, 1, 2)], m['stone_light'])

    # Relief sculpture in front pediment (simplified figures)
    bmesh_box("Relief1", (0.04, 0.20, 0.50), (1.74, -0.3, BZ + col_h + 0.45), m['stone'])
    bmesh_box("Relief2", (0.04, 0.16, 0.60), (1.74, 0.0, BZ + col_h + 0.50), m['stone'])
    bmesh_box("Relief3", (0.04, 0.20, 0.50), (1.74, 0.3, BZ + col_h + 0.45), m['stone'])

    # === Roof ===
    rv = [
        (-1.80, -1.90, BZ + col_h + 0.20), (1.80, -1.90, BZ + col_h + 0.20),
        (1.80, 1.90, BZ + col_h + 0.20), (-1.80, 1.90, BZ + col_h + 0.20),
        (0, -1.90, BZ + col_h + 1.15), (0, 1.90, BZ + col_h + 1.15),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("Roof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # === Gold statue (Athena-like figure on pedestal inside cella) ===
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.12, depth=0.30,
                                        location=(0, 0, BZ + 0.15))
    bpy.context.active_object.name = "StatuePedestal"
    bpy.context.active_object.data.materials.append(m['stone_dark'])

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.10, depth=1.4,
                                        location=(0, 0, BZ + 1.0))
    body = bpy.context.active_object
    body.name = "StatueBody"
    body.data.materials.append(m['gold'])

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(0, 0, BZ + 1.85))
    head = bpy.context.active_object
    head.name = "StatueHead"
    head.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # === Gold acroteria on roof peaks ===
    for sx, sy in [(0, -1.90), (0, 1.90), (0, 0)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(sx, sy, BZ + col_h + 1.20))
        orn = bpy.context.active_object
        orn.name = f"Acroterion_{sy:.1f}"
        orn.data.materials.append(m['gold'])
        bpy.ops.object.shade_smooth()

    # === Door ===
    bmesh_box("Door", (0.08, 0.55, 1.60), (cella_w / 2 + 0.01, 0, BZ + 0.80), m['door'])
    bmesh_box("DoorFrame", (0.10, 0.65, 0.08), (cella_w / 2 + 0.02, 0, BZ + 1.64), m['gold'])

    # === Wide ceremonial steps ===
    for i in range(7):
        bmesh_box(f"Step_{i}", (0.20, 3.2, 0.06),
                  (1.90 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_light'])


# ============================================================
# MEDIEVAL AGE -- Gothic cathedral with bell tower
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation ===
    bmesh_box("Found", (5.0, 4.4, 0.18), (0, 0, Z + 0.09), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.18

    # === Main nave ===
    nave_w, nave_d = 2.8, 2.0
    nave_h = 3.2
    bmesh_box("Nave", (nave_w, nave_d, nave_h), (0, 0, BZ + nave_h / 2), m['stone'], bevel=0.03)

    # Buttress bands
    for z in [BZ + 1.0, BZ + 2.0, BZ + nave_h]:
        bmesh_box(f"NaveBand_{z:.1f}", (nave_w + 0.06, nave_d + 0.06, 0.08), (0, 0, z), m['stone_trim'], bevel=0.02)

    # === Pointed arch roof (steep Gothic) ===
    roof_z = BZ + nave_h
    rv = [
        (-nave_w / 2 - 0.12, -nave_d / 2 - 0.12, roof_z),
        (nave_w / 2 + 0.12, -nave_d / 2 - 0.12, roof_z),
        (nave_w / 2 + 0.12, nave_d / 2 + 0.12, roof_z),
        (-nave_w / 2 - 0.12, nave_d / 2 + 0.12, roof_z),
        (0, -nave_d / 2 - 0.12, roof_z + 1.8),
        (0, nave_d / 2 + 0.12, roof_z + 1.8),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("NaveRoof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # Ridge cross
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.5,
                                        location=(0, 0, roof_z + 1.80 + 0.25))
    bpy.context.active_object.data.materials.append(m['gold'])
    bmesh_box("RidgeCrossH", (0.30, 0.03, 0.03), (0, 0, roof_z + 2.15), m['gold'])

    # === Flying buttresses (3 per side) ===
    for i in range(3):
        x = -0.8 + i * 0.8
        for ys, lbl in [(-1, "R"), (1, "L")]:
            # Buttress pier
            by = ys * (nave_d / 2 + 0.40)
            bmesh_box(f"ButtPier_{lbl}_{i}", (0.20, 0.20, 2.5), (x, by, BZ + 1.25), m['stone'], bevel=0.02)
            bmesh_box(f"ButtTop_{lbl}_{i}", (0.14, 0.14, 0.30), (x, by, BZ + 2.65), m['stone_trim'], bevel=0.01)
            # Flying arch (simplified as angled box)
            arch_v = [
                (x - 0.06, by, BZ + 2.2),
                (x + 0.06, by, BZ + 2.2),
                (x + 0.06, ys * nave_d / 2, BZ + nave_h - 0.3),
                (x - 0.06, ys * nave_d / 2, BZ + nave_h - 0.3),
            ]
            mesh_from_pydata(f"FlyArch_{lbl}_{i}", arch_v, [(0, 1, 2, 3)], m['stone_trim'])

    # === Pointed arch windows (tall, narrow) ===
    for i in range(4):
        y = -0.7 + i * 0.47
        for xs in [1, -1]:
            # Window opening
            bmesh_box(f"Win_{xs}_{i}", (0.08, 0.14, 0.80),
                      (xs * (nave_w / 2 + 0.01), y, BZ + 1.8), m['window'])
            # Pointed arch top
            bmesh_box(f"WinArch_{xs}_{i}", (0.09, 0.18, 0.06),
                      (xs * (nave_w / 2 + 0.02), y, BZ + 2.22), m['stone_trim'])

    # === Rose window (front face) ===
    RX = nave_w / 2 + 0.01
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.40, depth=0.06,
                                        location=(RX, 0, BZ + nave_h - 0.5))
    rose = bpy.context.active_object
    rose.name = "RoseWindow"
    rose.rotation_euler = (0, math.radians(90), 0)
    rose.data.materials.append(m['window'])
    # Rose window frame
    bpy.ops.mesh.primitive_torus_add(major_radius=0.42, minor_radius=0.03,
                                     location=(RX + 0.01, 0, BZ + nave_h - 0.5))
    frame = bpy.context.active_object
    frame.name = "RoseFrame"
    frame.rotation_euler = (0, math.radians(90), 0)
    frame.data.materials.append(m['stone_trim'])

    # Gold tracery spokes in rose window
    for i in range(8):
        a = (2 * math.pi * i) / 8
        sv = [(RX + 0.02, 0, BZ + nave_h - 0.5),
              (RX + 0.02, 0.38 * math.sin(a), BZ + nave_h - 0.5 + 0.38 * math.cos(a))]
        bpy.ops.mesh.primitive_cylinder_add(vertices=4, radius=0.015, depth=0.38,
                                            location=(RX + 0.02,
                                                      0.19 * math.sin(a),
                                                      BZ + nave_h - 0.5 + 0.19 * math.cos(a)))
        spoke = bpy.context.active_object
        spoke.name = f"RoseSpoke_{i}"
        spoke.rotation_euler = (a, 0, 0)
        spoke.data.materials.append(m['gold'])

    # === Bell tower (front-right, tallest structure) ===
    TX, TY = nave_w / 2 - 0.4, -nave_d / 2 - 0.5
    tower_w = 0.9
    tower_h = 5.0
    bmesh_box("BellTower", (tower_w, tower_w, tower_h), (TX, TY, BZ + tower_h / 2), m['stone'], bevel=0.03)

    # Tower bands
    for tz in [BZ + 1.5, BZ + 3.0, BZ + tower_h]:
        bmesh_box(f"TBand_{tz:.1f}", (tower_w + 0.06, tower_w + 0.06, 0.08), (TX, TY, tz), m['stone_trim'], bevel=0.02)

    # Belfry openings (pointed arches near top)
    for side_x, side_y in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        bx = TX + side_x * (tower_w / 2 + 0.01)
        by = TY + side_y * (tower_w / 2 + 0.01)
        bmesh_box(f"Belfry_{side_x}_{side_y}", (0.06, 0.20, 0.50) if side_x != 0 else (0.20, 0.06, 0.50),
                  (bx, by, BZ + tower_h - 0.8), m['window'])

    # Tower spire
    bmesh_cone("TowerSpire", tower_w / 2 + 0.05, 1.8, 8, (TX, TY, BZ + tower_h + 0.02), m['roof'])

    # Cross on spire top
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.4,
                                        location=(TX, TY, BZ + tower_h + 1.82 + 0.20))
    bpy.context.active_object.data.materials.append(m['gold'])
    bmesh_box("SpireCross", (0.25, 0.03, 0.03), (TX, TY, BZ + tower_h + 2.10), m['gold'])

    # === Main door (pointed arch) ===
    bmesh_box("Door", (0.10, 0.65, 1.50), (nave_w / 2 + 0.01, 0, BZ + 0.75), m['door'])
    # Pointed arch doorway
    bmesh_box("DoorArch", (0.12, 0.75, 0.08), (nave_w / 2 + 0.02, 0, BZ + 1.54), m['stone_trim'])
    # Tympanum (decorative panel above door)
    tv = [(nave_w / 2 + 0.03, -0.35, BZ + 1.50),
          (nave_w / 2 + 0.03, 0.35, BZ + 1.50),
          (nave_w / 2 + 0.03, 0, BZ + 1.85)]
    mesh_from_pydata("Tympanum", tv, [(0, 1, 2)], m['gold'])

    # === Steps ===
    for i in range(6):
        bmesh_box(f"Step_{i}", (0.22, 1.8, 0.06),
                  (nave_w / 2 + 0.40 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_dark'])


# ============================================================
# GUNPOWDER AGE -- Renaissance church with dome
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation ===
    bmesh_box("Found", (5.0, 4.6, 0.20), (0, 0, Z + 0.10), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.20

    # === Main nave body ===
    nave_w, nave_d = 3.0, 2.4
    nave_h = 3.0
    bmesh_box("Nave", (nave_w, nave_d, nave_h), (0, 0, BZ + nave_h / 2), m['stone'], bevel=0.03)

    # Cornice and string course
    bmesh_box("BaseMold", (nave_w + 0.06, nave_d + 0.06, 0.08), (0, 0, BZ + 0.04), m['stone_trim'], bevel=0.02)
    bmesh_box("MidMold", (nave_w + 0.06, nave_d + 0.06, 0.06), (0, 0, BZ + 1.5), m['stone_trim'], bevel=0.01)
    bmesh_box("Cornice", (nave_w + 0.08, nave_d + 0.08, 0.10), (0, 0, BZ + nave_h), m['stone_trim'], bevel=0.03)

    # Balustrade along roofline
    bmesh_box("Balustrade", (nave_w + 0.04, nave_d + 0.04, 0.20), (0, 0, BZ + nave_h + 0.10), m['stone_light'])

    # === Arched windows (2 rows, 3 per side on front) ===
    for row, z_off in [(0, 0.4), (1, 1.8)]:
        for y in [-0.7, 0, 0.7]:
            bmesh_box(f"Win_{row}_{y:.1f}", (0.08, 0.22, 0.55),
                      (nave_w / 2 + 0.01, y, BZ + z_off + 0.15), m['window'])
            # Arched top
            bmesh_box(f"WinArch_{row}_{y:.1f}", (0.09, 0.26, 0.06),
                      (nave_w / 2 + 0.02, y, BZ + z_off + 0.44), m['stone_trim'])
            # Window surround
            bmesh_box(f"WinSurr_{row}_{y:.1f}", (0.09, 0.26, 0.04),
                      (nave_w / 2 + 0.02, y, BZ + z_off + 0.13), m['stone_trim'])

    # Side windows
    for x in [-0.8, 0, 0.8]:
        for z_off in [0.5, 1.9]:
            bmesh_box(f"SWin_{x:.1f}_{z_off:.1f}", (0.22, 0.06, 0.50),
                      (x, -nave_d / 2 - 0.01, BZ + z_off), m['window'])

    # === Grand dome (central) ===
    dome_z = BZ + nave_h + 0.20
    # Drum (octagonal base)
    bmesh_prism("Drum", 0.85, 1.0, 16, (0, 0, dome_z), m['stone'], bevel=0.02)
    # Drum windows
    for i in range(8):
        a = (2 * math.pi * i) / 8
        wx = 0.86 * math.cos(a)
        wy = 0.86 * math.sin(a)
        bmesh_box(f"DrumWin_{i}", (0.04, 0.10, 0.35),
                  (wx, wy, dome_z + 0.50), m['window'])

    # Dome
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.90, location=(0, 0, dome_z + 1.0 + 0.25))
    dome = bpy.context.active_object
    dome.name = "Dome"
    dome.scale = (1, 1, 0.55)
    dome.data.materials.append(m['roof'])
    bpy.ops.object.shade_smooth()

    # Lantern on dome
    bmesh_prism("Lantern", 0.18, 0.50, 8, (0, 0, dome_z + 1.55), m['stone_light'])
    bmesh_cone("LanternRoof", 0.22, 0.30, 8, (0, 0, dome_z + 2.05), m['gold'])

    # Cross finial on lantern
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.35,
                                        location=(0, 0, dome_z + 2.35 + 0.175))
    bpy.context.active_object.data.materials.append(m['gold'])
    bmesh_box("DomeCrossH", (0.20, 0.03, 0.03), (0, 0, dome_z + 2.60), m['gold'])

    # === Bell tower (front-left) ===
    TX, TY = nave_w / 2 - 0.3, nave_d / 2 + 0.4
    tower_h = 4.5
    tower_w = 0.8
    bmesh_box("BellTower", (tower_w, tower_w, tower_h), (TX, TY, BZ + tower_h / 2), m['stone'], bevel=0.03)

    # Tower bands
    for tz in [BZ + 1.5, BZ + 3.0, BZ + tower_h]:
        bmesh_box(f"TBand_{tz:.1f}", (tower_w + 0.06, tower_w + 0.06, 0.08), (TX, TY, tz), m['stone_trim'], bevel=0.02)

    # Belfry arched openings
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        bx = TX + dx * (tower_w / 2 + 0.01)
        by = TY + dy * (tower_w / 2 + 0.01)
        if dx != 0:
            bmesh_box(f"Belfry_{dx}_{dy}", (0.06, 0.18, 0.45), (bx, by, BZ + tower_h - 0.7), m['window'])
        else:
            bmesh_box(f"Belfry_{dx}_{dy}", (0.18, 0.06, 0.45), (bx, by, BZ + tower_h - 0.7), m['window'])

    # Tower pyramidal cap
    pyramid_roof("TowerCap", w=tower_w - 0.1, d=tower_w - 0.1, h=1.2, overhang=0.08,
                 origin=(TX, TY, BZ + tower_h + 0.04), material=m['roof'])

    # Cross on tower
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.30,
                                        location=(TX, TY, BZ + tower_h + 1.24 + 0.15))
    bpy.context.active_object.data.materials.append(m['gold'])
    bmesh_box("TowerCross", (0.18, 0.03, 0.03), (TX, TY, BZ + tower_h + 1.45), m['gold'])

    # === Ornate entrance ===
    bmesh_box("Door", (0.10, 0.70, 1.60), (nave_w / 2 + 0.01, 0, BZ + 0.80), m['door'])
    # Entrance surround with pilasters
    for sy in [-0.45, 0.45]:
        bmesh_box(f"Pilaster_{sy:.1f}", (0.12, 0.10, 2.0), (nave_w / 2 + 0.06, sy, BZ + 1.0), m['stone_light'])
        bmesh_box(f"PilCap_{sy:.1f}", (0.16, 0.14, 0.06), (nave_w / 2 + 0.06, sy, BZ + 2.03), m['stone_trim'])

    # Entrance pediment
    pv = [(nave_w / 2 + 0.08, -0.55, BZ + 2.10),
          (nave_w / 2 + 0.08, 0.55, BZ + 2.10),
          (nave_w / 2 + 0.08, 0, BZ + 2.50)]
    mesh_from_pydata("EntrPediment", pv, [(0, 1, 2)], m['stone_light'])

    # Gold crest in pediment
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(nave_w / 2 + 0.10, 0, BZ + 2.25))
    bpy.context.active_object.name = "PedCrest"
    bpy.context.active_object.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # Steps
    for i in range(6):
        bmesh_box(f"Step_{i}", (0.22, 2.0, 0.06),
                  (nave_w / 2 + 0.40 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_dark'])


# ============================================================
# ENLIGHTENMENT AGE -- Neoclassical church with grand portico
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation ===
    bmesh_box("Found", (5.2, 4.8, 0.20), (0, 0, Z + 0.10), m['stone_dark'], bevel=0.05)

    BZ = Z + 0.20

    # === Main building body (symmetrical) ===
    main_w, main_d = 3.2, 2.6
    main_h = 3.2
    bmesh_box("Main", (main_w, main_d, main_h), (0, 0, BZ + main_h / 2), m['stone'], bevel=0.03)

    # Moldings
    bmesh_box("BaseMold", (main_w + 0.06, main_d + 0.06, 0.08), (0, 0, BZ + 0.04), m['stone_trim'], bevel=0.02)
    bmesh_box("MidMold", (main_w + 0.06, main_d + 0.06, 0.06), (0, 0, BZ + 1.6), m['stone_trim'], bevel=0.01)
    bmesh_box("Cornice", (main_w + 0.08, main_d + 0.08, 0.10), (0, 0, BZ + main_h), m['stone_trim'], bevel=0.03)

    # Balustrade
    bmesh_box("Balustrade", (main_w + 0.04, main_d + 0.04, 0.22), (0, 0, BZ + main_h + 0.11), m['stone_light'])

    # === Grand portico (6 large columns) ===
    portico_x = main_w / 2 + 0.50
    col_h = 2.8
    for i, y in enumerate([-1.0, -0.6, -0.2, 0.2, 0.6, 1.0]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.13, depth=col_h,
                                            location=(portico_x, y, BZ + col_h / 2))
        c = bpy.context.active_object
        c.name = f"PorCol_{i}"
        c.data.materials.append(m['stone_light'])
        bpy.ops.object.shade_smooth()
        bmesh_box(f"PorCap_{i}", (0.30, 0.30, 0.08), (portico_x, y, BZ + col_h + 0.04), m['stone_trim'])
        bmesh_box(f"PorBase_{i}", (0.28, 0.28, 0.06), (portico_x, y, BZ + 0.03), m['stone_trim'])

    # Portico entablature
    bmesh_box("PorEntab", (0.60, 2.4, 0.18), (portico_x, 0, BZ + col_h + 0.09), m['stone_trim'], bevel=0.02)

    # Grand pediment
    pv = [(portico_x + 0.02, -1.25, BZ + col_h + 0.18),
          (portico_x + 0.02, 1.25, BZ + col_h + 0.18),
          (portico_x + 0.02, 0, BZ + col_h + 0.95)]
    mesh_from_pydata("Pediment", pv, [(0, 1, 2)], m['stone_light'])

    # Relief in pediment
    bmesh_box("PedRelief", (0.04, 0.60, 0.35), (portico_x + 0.04, 0, BZ + col_h + 0.40), m['gold'])

    # Portico ceiling
    bmesh_box("PorCeiling", (0.55, 2.3, 0.06), (portico_x, 0, BZ + col_h - 0.03), m['stone_light'])

    # === Windows (symmetrical, front face, 2 rows x 4) ===
    for row, z_off in [(0, 0.4), (1, 2.0)]:
        for y in [-0.9, -0.3, 0.3, 0.9]:
            bmesh_box(f"Win_{row}_{y:.1f}", (0.07, 0.22, 0.55),
                      (main_w / 2 + 0.01, y, BZ + z_off + 0.15), m['window'])
            bmesh_box(f"WinH_{row}_{y:.1f}", (0.08, 0.26, 0.05),
                      (main_w / 2 + 0.02, y, BZ + z_off + 0.44), m['stone_trim'])

    # Side windows
    for x in [-1.0, -0.3, 0.3, 1.0]:
        for z_off in [0.5, 2.1]:
            bmesh_box(f"SWin_{x:.1f}_{z_off:.1f}", (0.22, 0.06, 0.50),
                      (x, -main_d / 2 - 0.01, BZ + z_off), m['window'])

    # === Central dome ===
    dome_z = BZ + main_h + 0.22
    bmesh_prism("Drum", 0.80, 0.90, 16, (0, 0, dome_z), m['stone'], bevel=0.02)

    # Drum windows
    for i in range(8):
        a = (2 * math.pi * i) / 8
        wx = 0.82 * math.cos(a)
        wy = 0.82 * math.sin(a)
        bmesh_box(f"DrumWin_{i}", (0.04, 0.08, 0.30), (wx, wy, dome_z + 0.45), m['window'])

    # Dome
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.85, location=(0, 0, dome_z + 0.90 + 0.25))
    dome = bpy.context.active_object
    dome.name = "Dome"
    dome.scale = (1, 1, 0.55)
    dome.data.materials.append(m['roof'])
    bpy.ops.object.shade_smooth()

    # Lantern
    bmesh_prism("Lantern", 0.16, 0.45, 8, (0, 0, dome_z + 1.40), m['stone_light'])
    bmesh_cone("LanternCap", 0.20, 0.30, 8, (0, 0, dome_z + 1.85), m['gold'])

    # Cross on dome
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.35,
                                        location=(0, 0, dome_z + 2.15 + 0.175))
    bpy.context.active_object.data.materials.append(m['gold'])
    bmesh_box("DomeCrossH", (0.22, 0.03, 0.03), (0, 0, dome_z + 2.40), m['gold'])

    # === Clock tower (front-left) ===
    TX, TY = main_w / 2 - 0.3, main_d / 2 + 0.4
    tower_h = 4.0
    tower_w = 0.80
    bmesh_box("ClockTower", (tower_w, tower_w, tower_h), (TX, TY, BZ + tower_h / 2), m['stone'], bevel=0.02)
    bmesh_box("CTCornice", (tower_w + 0.08, tower_w + 0.08, 0.08), (TX, TY, BZ + tower_h), m['stone_trim'], bevel=0.02)

    # Clock faces
    for dx, dy, rot in [(tower_w / 2 + 0.01, 0, (0, math.radians(90), 0)),
                        (0, tower_w / 2 + 0.01, (math.radians(90), 0, 0))]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.24, depth=0.04,
                                            location=(TX + dx, TY + dy, BZ + tower_h - 0.8))
        clock = bpy.context.active_object
        clock.name = f"Clock_{dx:.1f}_{dy:.1f}"
        clock.rotation_euler = rot
        clock.data.materials.append(m['gold'])

    # Tower spire
    bmesh_cone("CTSpire", tower_w / 2, 1.2, 8, (TX, TY, BZ + tower_h + 0.02), m['roof'])

    # Cross on tower
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.25,
                                        location=(TX, TY, BZ + tower_h + 1.22 + 0.125))
    bpy.context.active_object.data.materials.append(m['gold'])
    bmesh_box("TCrossH", (0.16, 0.03, 0.03), (TX, TY, BZ + tower_h + 1.40), m['gold'])

    # === Door ===
    bmesh_box("Door", (0.08, 0.65, 1.60), (main_w / 2 + 0.01, 0, BZ + 0.80), m['door'])

    # Steps (wide, ceremonial)
    for i in range(7):
        bmesh_box(f"Step_{i}", (0.22, 2.6, 0.06),
                  (portico_x + 0.40 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_light'])


# ============================================================
# INDUSTRIAL AGE -- Victorian cathedral with tall spire
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    # === Foundation ===
    bmesh_box("Found", (5.2, 4.6, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.04)

    BZ = Z + 0.15

    # === Main nave (wide, imposing) ===
    nave_w, nave_d = 3.4, 2.6
    nave_h = 3.5
    bmesh_box("Nave", (nave_w, nave_d, nave_h), (0, 0, BZ + nave_h / 2), m['stone'], bevel=0.02)

    # Iron beam grid on facade
    for z in [BZ + 1.0, BZ + 2.0, BZ + 3.0]:
        bmesh_box(f"IronH_{z:.1f}", (0.03, nave_d - 0.2, 0.06), (nave_w / 2 + 0.01, 0, z), m['iron'])
    for y in [-0.9, -0.3, 0.3, 0.9]:
        bmesh_box(f"IronV_{y:.1f}", (0.03, 0.06, nave_h), (nave_w / 2 + 0.01, y, BZ + nave_h / 2), m['iron'])

    # String courses
    for z in [BZ + 1.2, BZ + 2.4, BZ + nave_h]:
        bmesh_box(f"Band_{z:.1f}", (nave_w + 0.06, nave_d + 0.06, 0.08), (0, 0, z), m['stone_trim'], bevel=0.02)

    # === Steep pitched roof ===
    roof_z = BZ + nave_h
    rv = [
        (-nave_w / 2 - 0.15, -nave_d / 2 - 0.15, roof_z),
        (nave_w / 2 + 0.15, -nave_d / 2 - 0.15, roof_z),
        (nave_w / 2 + 0.15, nave_d / 2 + 0.15, roof_z),
        (-nave_w / 2 - 0.15, nave_d / 2 + 0.15, roof_z),
        (0, -nave_d / 2 - 0.15, roof_z + 1.5),
        (0, nave_d / 2 + 0.15, roof_z + 1.5),
    ]
    rf = [(0, 3, 5, 4), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5)]
    r = mesh_from_pydata("NaveRoof", rv, rf, m['roof'])
    for p in r.data.polygons:
        p.use_smooth = True

    # === Large stained glass windows (front) ===
    # Central large window
    bmesh_box("MainWindow", (0.08, 0.80, 1.60), (nave_w / 2 + 0.01, 0, BZ + 1.8), m['window'])
    bmesh_box("MainWinFrame", (0.10, 0.88, 0.08), (nave_w / 2 + 0.02, 0, BZ + 2.62), m['stone_trim'])
    bmesh_box("MainWinBase", (0.10, 0.88, 0.06), (nave_w / 2 + 0.02, 0, BZ + 1.02), m['stone_trim'])

    # Iron tracery in main window
    for y in [-0.2, 0.2]:
        bmesh_box(f"Tracery_V_{y:.1f}", (0.04, 0.02, 1.50), (nave_w / 2 + 0.02, y, BZ + 1.80), m['iron'])
    for z in [BZ + 1.5, BZ + 2.0, BZ + 2.5]:
        bmesh_box(f"Tracery_H_{z:.1f}", (0.04, 0.78, 0.02), (nave_w / 2 + 0.02, 0, z), m['iron'])

    # Side windows (tall, narrow stained glass)
    for i in range(4):
        x = -1.2 + i * 0.80
        for ys in [-1, 1]:
            bmesh_box(f"SideWin_{i}_{ys}", (0.20, 0.06, 1.20),
                      (x, ys * (nave_d / 2 + 0.01), BZ + 1.80), m['window'])
            # Iron frame
            bmesh_box(f"SideWinF_{i}_{ys}", (0.02, 0.06, 1.20),
                      (x, ys * (nave_d / 2 + 0.02), BZ + 1.80), m['iron'])

    # === Tall spire (front-right, Victorian Gothic) ===
    TX, TY = nave_w / 2 - 0.3, -nave_d / 2 - 0.4
    tower_w = 1.0
    tower_h = 5.0
    bmesh_box("SpireTower", (tower_w, tower_w, tower_h), (TX, TY, BZ + tower_h / 2), m['stone'], bevel=0.03)

    # Tower iron framework accents
    for z in [BZ + 1.2, BZ + 2.4, BZ + 3.6, BZ + tower_h]:
        bmesh_box(f"TIron_{z:.1f}", (tower_w + 0.04, tower_w + 0.04, 0.06), (TX, TY, z), m['iron'])

    # Tower windows
    for tz in [BZ + 1.5, BZ + 3.0]:
        for dx, dy in [(1, 0), (0, -1)]:
            wx = TX + dx * (tower_w / 2 + 0.01)
            wy = TY + dy * (tower_w / 2 + 0.01)
            if dx != 0:
                bmesh_box(f"TWin_{tz:.1f}_{dx}_{dy}", (0.06, 0.18, 0.50), (wx, wy, tz), m['window'])
            else:
                bmesh_box(f"TWin_{tz:.1f}_{dx}_{dy}", (0.18, 0.06, 0.50), (wx, wy, tz), m['window'])

    # Tall spire (very pointed)
    bmesh_cone("Spire", tower_w / 2 + 0.05, 3.0, 8, (TX, TY, BZ + tower_h + 0.02), m['roof'])

    # Gold cross on spire
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.40,
                                        location=(TX, TY, BZ + tower_h + 3.02 + 0.20))
    bpy.context.active_object.data.materials.append(m['gold'])
    bmesh_box("SpireCross", (0.25, 0.03, 0.03), (TX, TY, BZ + tower_h + 3.30), m['gold'])

    # === Iron gates at entrance ===
    gate_x = nave_w / 2 + 0.80
    for i in range(10):
        fy = -1.0 + i * 0.22
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=1.0,
                                            location=(gate_x, fy, BZ + 0.50))
        bar = bpy.context.active_object
        bar.name = f"GateBar_{i}"
        bar.data.materials.append(m['iron'])
    # Gate horizontal rails
    for gz in [BZ + 0.2, BZ + 0.6, BZ + 0.95]:
        bmesh_box(f"GateRail_{gz:.1f}", (0.02, 2.0, 0.02), (gate_x, 0, gz), m['iron'])

    # === Door ===
    bmesh_box("Door", (0.10, 0.80, 1.80), (nave_w / 2 + 0.01, 0, BZ + 0.90), m['door'])
    bmesh_box("DoorArch", (0.12, 0.90, 0.10), (nave_w / 2 + 0.02, 0, BZ + 1.84), m['stone_trim'], bevel=0.02)

    # Steps
    for i in range(6):
        bmesh_box(f"Step_{i}", (0.22, 2.2, 0.06),
                  (nave_w / 2 + 0.40 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_dark'])


# ============================================================
# MODERN AGE -- Modernist worship center
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.10
    bmesh_box("Found", (5.0, 4.6, 0.10), (0, 0, Z + 0.05), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Main worship hall (clean geometric box) ===
    hall_w, hall_d = 3.4, 2.8
    hall_h = 3.0
    bmesh_box("Hall", (hall_w, hall_d, hall_h), (0, 0, BZ + hall_h / 2), m['stone'], bevel=0.02)

    # Flat roof with slight overhang
    bmesh_box("Roof", (hall_w + 0.20, hall_d + 0.20, 0.10), (0, 0, BZ + hall_h + 0.05), m['stone_dark'])

    # === Large glass wall (entire front face) ===
    bmesh_box("GlassWall", (0.06, hall_d - 0.4, hall_h - 0.3),
              (hall_w / 2 + 0.01, 0, BZ + hall_h / 2 + 0.05), glass)

    # Vertical mullions (steel)
    for y in [-1.0, -0.5, 0, 0.5, 1.0]:
        bmesh_box(f"Mull_{y:.1f}", (0.04, 0.03, hall_h - 0.4),
                  (hall_w / 2 + 0.02, y, BZ + hall_h / 2 + 0.05), metal)

    # Horizontal mullions
    for z in [BZ + 1.0, BZ + 2.0]:
        bmesh_box(f"HMull_{z:.1f}", (0.04, hall_d - 0.5, 0.03),
                  (hall_w / 2 + 0.02, 0, z), metal)

    # === Side clerestory windows ===
    for ys in [-1, 1]:
        bmesh_box(f"Clere_{ys}", (2.4, 0.06, 0.60),
                  (0, ys * (hall_d / 2 + 0.01), BZ + hall_h - 0.50), glass)
        # Frame
        bmesh_box(f"ClereF_{ys}", (2.42, 0.07, 0.03),
                  (0, ys * (hall_d / 2 + 0.02), BZ + hall_h - 0.18), metal)

    # === Angled side wing (meditation room) ===
    wing_w, wing_d, wing_h = 1.8, 1.6, 2.2
    bmesh_box("Wing", (wing_w, wing_d, wing_h), (-1.2, -1.4, BZ + wing_h / 2), m['stone'], bevel=0.02)
    bmesh_box("WingRoof", (wing_w + 0.12, wing_d + 0.12, 0.08), (-1.2, -1.4, BZ + wing_h + 0.04), m['stone_dark'])

    # Wing window
    bmesh_box("WingWin", (0.06, 1.0, 0.80), (-1.2 + wing_w / 2 + 0.01, -1.4, BZ + 1.2), glass)

    # === Simple cross/symbol (clean, modern) ===
    cross_x = hall_w / 2 + 0.04
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=1.5,
                                        location=(cross_x, 0, BZ + hall_h / 2 + 0.3))
    vert_bar = bpy.context.active_object
    vert_bar.name = "CrossVert"
    vert_bar.rotation_euler = (0, math.radians(90), 0)
    vert_bar.data.materials.append(m['gold'])

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.8,
                                        location=(cross_x, 0, BZ + hall_h / 2 + 0.7))
    horiz_bar = bpy.context.active_object
    horiz_bar.name = "CrossHoriz"
    horiz_bar.rotation_euler = (math.radians(90), 0, math.radians(90))
    horiz_bar.data.materials.append(m['gold'])

    # === Entrance canopy (floating concrete slab) ===
    canopy_x = hall_w / 2 + 0.80
    bmesh_box("Canopy", (1.2, 2.4, 0.06), (canopy_x, 0, BZ + 2.0), m['stone'])
    # Support columns (thin, modern)
    for y in [-0.9, 0.9]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=1.9,
                                            location=(canopy_x + 0.30, y, BZ + 1.05))
        col = bpy.context.active_object
        col.name = f"CanopyCol_{y:.1f}"
        col.data.materials.append(metal)

    # Glass entrance doors
    bmesh_box("DoorL", (0.06, 0.50, 1.80), (hall_w / 2 + 0.01, -0.30, BZ + 0.90), glass)
    bmesh_box("DoorR", (0.06, 0.50, 1.80), (hall_w / 2 + 0.01, 0.30, BZ + 0.90), glass)
    bmesh_box("DoorFrame", (0.07, 1.10, 0.04), (hall_w / 2 + 0.02, 0, BZ + 1.82), metal)

    # === Reflecting pool ===
    bmesh_box("PoolOuter", (1.2, 2.0, 0.12), (hall_w / 2 + 1.2, 0, BZ + 0.06), m['stone_light'])
    bmesh_box("PoolInner", (1.0, 1.8, 0.04), (hall_w / 2 + 1.2, 0, BZ + 0.08), m['window'])

    # === Bell wall (freestanding, side) ===
    bmesh_box("BellWall", (0.15, 1.2, 2.5), (-hall_w / 2 - 0.6, 0, BZ + 1.25), m['stone'])
    # Bell opening
    bmesh_box("BellOpen", (0.16, 0.35, 0.40), (-hall_w / 2 - 0.6, 0, BZ + 2.20), m['window'])
    # Gold bell
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(-hall_w / 2 - 0.6, 0, BZ + 2.20))
    bell = bpy.context.active_object
    bell.name = "Bell"
    bell.scale = (1, 1, 1.3)
    bell.data.materials.append(m['gold'])
    bpy.ops.object.shade_smooth()

    # Steps
    for i in range(4):
        bmesh_box(f"Step_{i}", (0.22, 2.6, 0.06),
                  (canopy_x + 0.20 + i * 0.22, 0, BZ - 0.04 - i * 0.06), m['stone_dark'])


# ============================================================
# DIGITAL AGE -- Meditation center with floating geometry
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (5.5, 5.5, 0.06), (0, 0, Z + 0.03), m['ground'])

    BZ = Z + 0.08
    bmesh_box("Found", (5.0, 4.6, 0.08), (0, 0, Z + 0.04), m['stone_dark'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # === Main structure (floating geometric form on pillars) ===
    main_w, main_d = 3.2, 2.6
    main_h = 2.8
    float_z = BZ + 0.60  # elevated above ground

    bmesh_box("MainBody", (main_w, main_d, main_h), (0, 0, float_z + main_h / 2), glass)

    # Steel frame grid
    for z in [float_z + 0.8, float_z + 1.6, float_z + 2.4]:
        bmesh_box(f"HFrame_{z:.1f}", (main_w + 0.02, main_d + 0.02, 0.04), (0, 0, z), metal)
    for x in [-1.2, 0, 1.2]:
        bmesh_box(f"VFrameF_{x:.1f}", (0.04, 0.04, main_h), (x, -main_d / 2 - 0.01, float_z + main_h / 2), metal)
        bmesh_box(f"VFrameB_{x:.1f}", (0.04, 0.04, main_h), (x, main_d / 2 + 0.01, float_z + main_h / 2), metal)
    for y in [-0.9, 0, 0.9]:
        bmesh_box(f"VFrameR_{y:.1f}", (0.04, 0.04, main_h), (main_w / 2 + 0.01, y, float_z + main_h / 2), metal)
        bmesh_box(f"VFrameL_{y:.1f}", (0.04, 0.04, main_h), (-main_w / 2 - 0.01, y, float_z + main_h / 2), metal)

    # === Support pillars (angled, dramatic) ===
    pillars = [(-1.0, -0.8), (-1.0, 0.8), (1.0, -0.8), (1.0, 0.8)]
    for px, py in pillars:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=float_z + 0.10,
                                            location=(px, py, BZ + (float_z - BZ) / 2))
        pil = bpy.context.active_object
        pil.name = f"Pillar_{px:.1f}_{py:.1f}"
        pil.data.materials.append(metal)

    # === Floating roof slab (extends beyond main body) ===
    roof_z = float_z + main_h
    bmesh_box("Roof", (main_w + 0.40, main_d + 0.40, 0.08), (0, 0, roof_z + 0.04), metal)

    # === Holographic light features (glowing geometric elements) ===
    # Central pyramid (inverted, floating above roof)
    pyr_z = roof_z + 0.30
    pyr_verts = [
        (-0.40, -0.40, pyr_z + 0.80),
        (0.40, -0.40, pyr_z + 0.80),
        (0.40, 0.40, pyr_z + 0.80),
        (-0.40, 0.40, pyr_z + 0.80),
        (0, 0, pyr_z),
    ]
    pyr_faces = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (0, 1, 2, 3)]
    pyr = mesh_from_pydata("HoloPyramid", pyr_verts, pyr_faces, m['gold'])
    for p in pyr.data.polygons:
        p.use_smooth = True

    # Floating light rings
    for i, rz in enumerate([roof_z + 0.50, roof_z + 1.0, roof_z + 1.50]):
        ring_r = 0.60 - i * 0.15
        n_seg = 12
        for j in range(n_seg):
            a = (2 * math.pi * j) / n_seg
            rx, ry = ring_r * math.cos(a), ring_r * math.sin(a)
            bmesh_box(f"LightSeg_{i}_{j}", (0.06, 0.06, 0.03), (rx, ry, rz), m['gold'])

    # === Zen garden (ground level, in front) ===
    garden_x = main_w / 2 + 0.80
    bmesh_box("ZenBase", (1.4, 2.4, 0.06), (garden_x, 0, BZ + 0.03), m['stone_light'])

    # Raked gravel pattern (concentric circles suggestion)
    for i in range(4):
        r = 0.25 + i * 0.15
        n_pts = 10
        for j in range(n_pts):
            a = (2 * math.pi * j) / n_pts
            gx = garden_x + r * math.cos(a)
            gy = r * math.sin(a)
            bmesh_box(f"Gravel_{i}_{j}", (0.04, 0.04, 0.02), (gx, gy, BZ + 0.07), m['stone_light'])

    # Zen stones (3 arranged stones)
    for sx, sy, sr in [(garden_x - 0.2, -0.3, 0.08), (garden_x + 0.1, 0.2, 0.06), (garden_x + 0.3, -0.1, 0.10)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=sr, location=(sx, sy, BZ + 0.08 + sr * 0.5))
        stone = bpy.context.active_object
        stone.name = f"ZenStone_{sx:.1f}_{sy:.1f}"
        stone.scale = (1, 0.8, 0.5)
        stone.data.materials.append(m['stone_dark'])

    # === Water feature (thin reflective strip) ===
    bmesh_box("WaterFeature", (0.10, 2.0, 0.04), (garden_x - 0.65, 0, BZ + 0.05), m['window'])

    # === Entrance bridge (glass walkway to floating structure) ===
    bmesh_box("Bridge", (1.5, 1.2, 0.06), (main_w / 2 + 0.40, 0, float_z - 0.03), glass)
    bmesh_box("BridgeFrame", (1.52, 1.22, 0.03), (main_w / 2 + 0.40, 0, float_z - 0.06), metal)

    # Bridge support
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06, depth=float_z - BZ,
                                        location=(main_w / 2 + 0.80, 0, BZ + (float_z - BZ) / 2))
    bpy.context.active_object.data.materials.append(metal)

    # === LED accent strips ===
    bmesh_box("LED1", (main_w + 0.02, 0.04, 0.06), (0, -main_d / 2 - 0.01, float_z - 0.05), m['gold'])
    bmesh_box("LED2", (main_w + 0.02, 0.04, 0.06), (0, main_d / 2 + 0.01, float_z - 0.05), m['gold'])
    bmesh_box("LED3", (0.04, main_d + 0.02, 0.06), (main_w / 2 + 0.01, 0, float_z - 0.05), m['gold'])
    bmesh_box("LED4", (0.04, main_d + 0.02, 0.06), (-main_w / 2 - 0.01, 0, float_z - 0.05), m['gold'])

    # Roof edge LEDs
    bmesh_box("LED_Roof1", (main_w + 0.42, 0.04, 0.04), (0, -main_d / 2 - 0.20, roof_z + 0.10), m['gold'])
    bmesh_box("LED_Roof2", (main_w + 0.42, 0.04, 0.04), (0, main_d / 2 + 0.20, roof_z + 0.10), m['gold'])

    # === Solar panels on roof ===
    for i in range(3):
        bmesh_box(f"Solar_{i}", (0.7, 0.5, 0.03), (-0.8 + i * 0.8, 0.8, roof_z + 0.12), glass)
        bmesh_box(f"SolarF_{i}", (0.72, 0.52, 0.02), (-0.8 + i * 0.8, 0.8, roof_z + 0.09), metal)

    # Antenna/communication spire
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=1.5,
                                        location=(0, 0, roof_z + 0.80))
    bpy.context.active_object.data.materials.append(metal)
    for z_off in [0.3, 0.6, 0.9, 1.2]:
        bmesh_box(f"SpireX_{z_off:.1f}", (0.4, 0.02, 0.02), (0, 0, roof_z + z_off), metal)
        bmesh_box(f"SpireY_{z_off:.1f}", (0.02, 0.4, 0.02), (0, 0, roof_z + z_off), metal)


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


def build_temple(materials, age='medieval'):
    """Build a Temple with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
