"""
Wall building — single 1x1 wall segment, a defensive perimeter piece.
Runs along the Y axis (front-facing). Each segment connects at both ends.

Stone:         Wooden palisade — vertical logs, sharpened tops, rope lashing
Bronze:        Mud-brick wall with thick base, flat top walkway, crenellations
Iron:          Stone wall with mortar, wider base, battlements/merlons, walkway
Classical:     Dressed stone wall with decorative cornice, alternating merlons
Medieval:      Thick castle wall with walkway, merlons, machicolation, batter
Gunpowder:     Angled bastion wall, cannon embrasure, earthwork backing
Enlightenment: Brick wall with stone cap, iron spikes, buttresses
Industrial:    Reinforced brick wall with steel beams, barbed wire on top
Modern:        Concrete blast wall with steel reinforcement strips
Digital:       Energy barrier — metal posts with glowing energy strip
"""

import bpy
import bmesh
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.geometry import bmesh_box, bmesh_prism, bmesh_cone, pyramid_roof, mesh_from_pydata


# ============================================================
# STONE AGE — Wooden palisade with sharpened log tops
# ============================================================
def _build_stone(m):
    Z = 0.0

    bmesh_box("Ground", (2.0, 2.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Earthen mound base
    bmesh_box("EarthBase", (0.60, 1.8, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.12
    log_h = 1.1
    log_r = 0.055
    num_logs = 10
    spacing = 1.6 / (num_logs - 1)

    # Vertical logs forming the palisade
    for i in range(num_logs):
        ly = -0.8 + i * spacing
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=log_r, depth=log_h,
                                            location=(0, ly, BZ + log_h / 2))
        log = bpy.context.active_object
        log.name = f"Log_{i}"
        log.data.materials.append(m['wood'])

        # Sharpened top (cone)
        bmesh_cone(f"LogTip_{i}", log_r, 0.12, 6, (0, ly, BZ + log_h), m['wood_dark'], smooth=False)

    # Horizontal cross beam (lower)
    bmesh_box("BeamLow", (0.06, 1.7, 0.06), (0.08, 0, BZ + 0.25), m['wood_dark'])

    # Horizontal cross beam (upper)
    bmesh_box("BeamHigh", (0.06, 1.7, 0.06), (-0.08, 0, BZ + 0.75), m['wood_dark'])

    # Rope lashing at intersections (small blocks representing rope wraps)
    for beam_z in [BZ + 0.25, BZ + 0.75]:
        for i in range(0, num_logs, 2):
            ly = -0.8 + i * spacing
            bx = 0.08 if beam_z == BZ + 0.25 else -0.08
            bmesh_box(f"Rope_{beam_z:.2f}_{i}", (0.08, 0.05, 0.05),
                      (bx, ly, beam_z), m['roof_edge'])

    # Support stake on back side (angled braces)
    for sy in [-0.5, 0.5]:
        sv = [(-0.30, sy - 0.03, BZ), (-0.30, sy + 0.03, BZ),
              (-0.06, sy + 0.03, BZ + 0.6), (-0.06, sy - 0.03, BZ + 0.6)]
        mesh_from_pydata(f"Brace_{sy:.1f}", sv, [(0, 1, 2, 3)], m['wood_dark'])


# ============================================================
# BRONZE AGE — Mud-brick wall with flat top walkway and crenellations
# ============================================================
def _build_bronze(m):
    Z = 0.0

    bmesh_box("Ground", (2.0, 2.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Thick mud-brick base (tapered slightly)
    bmesh_box("WallBase", (0.65, 1.8, 0.15), (0, 0, Z + 0.075), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.15
    wall_h = 0.9

    # Main mud-brick body
    bmesh_box("WallBody", (0.55, 1.8, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Walkway slab on top
    bmesh_box("Walkway", (0.65, 1.8, 0.06), (0, 0, BZ + wall_h + 0.03), m['stone_trim'])

    # Crenellations (merlons along the front edge)
    merlon_w = 0.12
    merlon_h = 0.22
    merlon_d = 0.14
    num_merlons = 5
    merlon_spacing = 1.6 / (num_merlons - 1)
    for i in range(num_merlons):
        my = -0.8 + i * merlon_spacing
        bmesh_box(f"Merlon_{i}", (merlon_d, merlon_w, merlon_h),
                  (0.26, my, BZ + wall_h + 0.06 + merlon_h / 2), m['stone'])

    # Low parapet on inner side
    bmesh_box("InnerParapet", (0.08, 1.8, 0.12), (-0.29, 0, BZ + wall_h + 0.06 + 0.06), m['stone_dark'])

    # Decorative mud plaster band near top
    bmesh_box("PlasterBand", (0.57, 1.82, 0.04), (0, 0, BZ + wall_h - 0.10), m['stone_light'])

    # Drainage holes (small dark insets)
    for dy in [-0.5, 0.5]:
        bmesh_box(f"Drain_{dy:.1f}", (0.06, 0.06, 0.06),
                  (0.28, dy, BZ + 0.20), m['stone_dark'])

    # Steps on the inner side to reach walkway
    for i in range(3):
        step_w = 0.20
        bmesh_box(f"Step_{i}", (step_w, 0.35, 0.06),
                  (-0.33 - i * 0.12, -0.70, BZ + wall_h - i * 0.28), m['stone_dark'])


# ============================================================
# IRON AGE — Stone wall with mortar, wider base, battlements
# ============================================================
def _build_iron(m):
    Z = 0.0

    bmesh_box("Ground", (2.0, 2.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Wide stone foundation
    bmesh_box("Foundation", (0.75, 1.9, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.12
    wall_h = 1.05

    # Main wall body (slightly tapered via two stacked boxes)
    bmesh_box("WallLower", (0.65, 1.85, wall_h * 0.5), (0, 0, BZ + wall_h * 0.25), m['stone'], bevel=0.02)
    bmesh_box("WallUpper", (0.58, 1.85, wall_h * 0.5), (0, 0, BZ + wall_h * 0.75), m['stone'], bevel=0.02)

    # Mortar lines (horizontal bands)
    for z_off in [0.25, 0.50, 0.75]:
        bmesh_box(f"Mortar_{z_off:.2f}", (0.60, 1.86, 0.015),
                  (0, 0, BZ + z_off), m['stone_light'])

    # Walkway platform
    bmesh_box("Walkway", (0.70, 1.9, 0.06), (0, 0, BZ + wall_h + 0.03), m['stone_trim'])

    # Battlements with merlons and crenels
    merlon_h = 0.28
    merlon_d = 0.16
    merlon_w = 0.18
    gap_w = 0.14
    total = merlon_w + gap_w
    y_start = -0.80
    i = 0
    y = y_start
    while y < 0.85:
        bmesh_box(f"Merlon_{i}", (merlon_d, merlon_w, merlon_h),
                  (0.28, y + merlon_w / 2, BZ + wall_h + 0.06 + merlon_h / 2), m['stone'])
        y += total
        i += 1

    # Inner parapet wall
    bmesh_box("InnerWall", (0.08, 1.9, 0.18), (-0.32, 0, BZ + wall_h + 0.06 + 0.09), m['stone_dark'])

    # Arrow slits (narrow windows in merlons)
    for idx in [0, 2, 4]:
        if idx < i:
            my = y_start + idx * total + merlon_w / 2
            bmesh_box(f"ArrowSlit_{idx}", (0.18, 0.03, 0.14),
                      (0.28, my, BZ + wall_h + 0.06 + merlon_h / 2), m['stone_dark'])

    # Stone rubble at base (decorative blocks)
    for j, (rx, ry) in enumerate([(-0.40, -0.6), (-0.42, 0.3), (-0.38, 0.7)]):
        bmesh_box(f"Rubble_{j}", (0.10, 0.08, 0.06), (rx, ry, Z + 0.03), m['stone_dark'])


# ============================================================
# CLASSICAL AGE — Dressed stone wall with decorative cornice
# ============================================================
def _build_classical(m):
    Z = 0.0

    bmesh_box("Ground", (2.0, 2.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Stepped base (2 tiers)
    bmesh_box("BaseTier1", (0.80, 1.9, 0.06), (0, 0, Z + 0.03 + 0.03), m['stone_light'], bevel=0.01)
    bmesh_box("BaseTier2", (0.72, 1.88, 0.06), (0, 0, Z + 0.06 + 0.06), m['stone_light'], bevel=0.01)

    BZ = Z + 0.12
    wall_h = 1.0

    # Main dressed stone wall
    bmesh_box("WallBody", (0.55, 1.85, wall_h), (0, 0, BZ + wall_h / 2), m['stone_light'], bevel=0.02)

    # Decorative horizontal bands
    bmesh_box("BandLow", (0.57, 1.86, 0.03), (0, 0, BZ + 0.30), m['stone_trim'])
    bmesh_box("BandHigh", (0.57, 1.86, 0.03), (0, 0, BZ + 0.70), m['stone_trim'])

    # Decorative cornice at top
    bmesh_box("Cornice", (0.65, 1.92, 0.06), (0, 0, BZ + wall_h + 0.03), m['stone_trim'], bevel=0.02)
    bmesh_box("CorniceUpper", (0.60, 1.90, 0.04), (0, 0, BZ + wall_h + 0.08), m['stone_trim'], bevel=0.01)

    # Walkway
    bmesh_box("Walkway", (0.68, 1.92, 0.04), (0, 0, BZ + wall_h + 0.12), m['stone_light'])

    # Alternating merlon pattern (wider-narrow-wider)
    merlon_h = 0.25
    positions = [
        (-0.75, 0.22), (-0.40, 0.12), (-0.15, 0.22),
        (0.15, 0.12), (0.40, 0.22), (0.65, 0.12),
    ]
    for idx, (my, mw) in enumerate(positions):
        bmesh_box(f"Merlon_{idx}", (0.14, mw, merlon_h),
                  (0.28, my, BZ + wall_h + 0.14 + merlon_h / 2), m['stone_light'])

    # Pilaster accents on front face (shallow projecting columns)
    for py in [-0.80, 0, 0.80]:
        bmesh_box(f"Pilaster_{py:.1f}", (0.06, 0.10, wall_h),
                  (0.31, py, BZ + wall_h / 2), m['stone_trim'])
        # Small capital at top of pilaster
        bmesh_box(f"Capital_{py:.1f}", (0.08, 0.14, 0.04),
                  (0.31, py, BZ + wall_h - 0.02), m['stone_trim'])

    # Carved relief panel between pilasters (decorative slab)
    for py in [-0.40, 0.40]:
        bmesh_box(f"Relief_{py:.1f}", (0.04, 0.30, 0.15),
                  (0.29, py, BZ + 0.50), m['gold'])

    # Inner parapet
    bmesh_box("InnerParapet", (0.08, 1.85, 0.15), (-0.30, 0, BZ + wall_h + 0.14 + 0.075), m['stone_light'])


# ============================================================
# MEDIEVAL AGE — Thick castle wall with machicolation and batter
# ============================================================
def _build_medieval(m):
    Z = 0.0

    bmesh_box("Ground", (2.0, 2.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Battered (sloped) stone base — trapezoid cross-section via mesh_from_pydata
    batter_h = 0.30
    bv = [
        # bottom face (wider)
        (-0.45, -0.95, Z), (0.45, -0.95, Z),
        (0.45, 0.95, Z), (-0.45, 0.95, Z),
        # top face (narrower, shifted inward on front)
        (-0.38, -0.92, Z + batter_h), (0.35, -0.92, Z + batter_h),
        (0.35, 0.92, Z + batter_h), (-0.38, 0.92, Z + batter_h),
    ]
    bf = [(0, 1, 2, 3), (4, 7, 6, 5),
          (0, 1, 5, 4), (2, 3, 7, 6),
          (0, 3, 7, 4), (1, 2, 6, 5)]
    mesh_from_pydata("Batter", bv, bf, m['stone_dark'])

    BZ = Z + batter_h
    wall_h = 0.90

    # Main wall body
    bmesh_box("WallBody", (0.60, 1.84, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Stone course lines
    for z_off in [0.22, 0.45, 0.68]:
        bmesh_box(f"Course_{z_off:.2f}", (0.62, 1.85, 0.012),
                  (0, 0, BZ + z_off), m['stone_dark'])

    # Walkway slab
    bmesh_box("Walkway", (0.72, 1.90, 0.06), (0, 0, BZ + wall_h + 0.03), m['stone_trim'])

    # Machicolation corbels (projecting stone brackets on front)
    num_corbels = 6
    corbel_spacing = 1.6 / (num_corbels - 1)
    for i in range(num_corbels):
        cy = -0.8 + i * corbel_spacing
        # Corbel bracket (small triangular support)
        cv = [(0.31, cy - 0.04, BZ + wall_h - 0.10),
              (0.31, cy + 0.04, BZ + wall_h - 0.10),
              (0.42, cy + 0.04, BZ + wall_h + 0.03),
              (0.42, cy - 0.04, BZ + wall_h + 0.03)]
        mesh_from_pydata(f"Corbel_{i}", cv, [(0, 1, 2, 3)], m['stone_trim'])

    # Machicolation platform (extends beyond wall face)
    bmesh_box("MachPlatform", (0.22, 1.86, 0.05),
              (0.42, 0, BZ + wall_h + 0.055), m['stone_trim'])

    # Merlons on top of machicolation
    merlon_h = 0.26
    merlon_w = 0.16
    gap = 0.12
    total = merlon_w + gap
    y = -0.80
    i = 0
    while y < 0.85:
        bmesh_box(f"Merlon_{i}", (0.14, merlon_w, merlon_h),
                  (0.42, y + merlon_w / 2, BZ + wall_h + 0.08 + merlon_h / 2), m['stone'])
        y += total
        i += 1

    # Inner parapet (lower wall on walkway side)
    bmesh_box("InnerParapet", (0.08, 1.84, 0.20),
              (-0.33, 0, BZ + wall_h + 0.06 + 0.10), m['stone_dark'])

    # Murder holes (gaps in machicolation floor) — dark slots
    for dy in [-0.50, 0, 0.50]:
        bmesh_box(f"MurderHole_{dy:.1f}", (0.10, 0.08, 0.06),
                  (0.42, dy, BZ + wall_h + 0.03), m['stone_dark'])

    # Torch bracket on inner wall
    for dy in [-0.60, 0.60]:
        bmesh_box(f"TorchBracket_{dy:.1f}", (0.04, 0.04, 0.10),
                  (-0.28, dy, BZ + wall_h - 0.15), m['iron'])


# ============================================================
# GUNPOWDER AGE — Angled bastion wall with cannon embrasure
# ============================================================
def _build_gunpowder(m):
    Z = 0.0

    bmesh_box("Ground", (2.0, 2.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Thick angled/sloped wall face — trapezoidal cross-section
    # Much thicker than previous ages to absorb cannon fire
    slope_h = 1.0
    sv = [
        # bottom (very wide base)
        (-0.55, -0.92, Z), (0.55, -0.92, Z),
        (0.55, 0.92, Z), (-0.55, 0.92, Z),
        # top (narrower, front face slopes inward)
        (-0.40, -0.90, Z + slope_h), (0.30, -0.90, Z + slope_h),
        (0.30, 0.90, Z + slope_h), (-0.40, 0.90, Z + slope_h),
    ]
    sf = [(0, 1, 2, 3), (4, 7, 6, 5),
          (0, 1, 5, 4), (2, 3, 7, 6),
          (0, 3, 7, 4), (1, 2, 6, 5)]
    mesh_from_pydata("SlopeWall", sv, sf, m['stone'])

    BZ = Z + slope_h

    # Flat top / terreplein (walkway)
    bmesh_box("Walkway", (0.80, 1.88, 0.06), (0, 0, BZ + 0.03), m['stone_trim'])

    # Low parapet on the front
    bmesh_box("FrontParapet", (0.16, 1.88, 0.30),
              (0.30, 0, BZ + 0.06 + 0.15), m['stone'])

    # Cannon embrasure (wide opening in center of front parapet)
    # Cut the parapet and leave gap — represented by two parapet segments
    # with a splayed opening between them
    bmesh_box("ParapetLeft", (0.16, 0.60, 0.30),
              (0.30, -0.64, BZ + 0.06 + 0.15), m['stone'])
    bmesh_box("ParapetRight", (0.16, 0.60, 0.30),
              (0.30, 0.64, BZ + 0.06 + 0.15), m['stone'])

    # Embrasure splayed opening (wider outside, narrow inside)
    # Left splay
    elv = [(0.22, -0.34, BZ + 0.06), (0.38, -0.40, BZ + 0.06),
           (0.38, -0.40, BZ + 0.30), (0.22, -0.34, BZ + 0.30)]
    mesh_from_pydata("EmbrSplayL", elv, [(0, 1, 2, 3)], m['stone_dark'])
    # Right splay
    erv = [(0.22, 0.34, BZ + 0.06), (0.38, 0.40, BZ + 0.06),
           (0.38, 0.40, BZ + 0.30), (0.22, 0.34, BZ + 0.30)]
    mesh_from_pydata("EmbrSplayR", erv, [(0, 1, 2, 3)], m['stone_dark'])

    # Embrasure floor (flattened area for cannon)
    bmesh_box("EmbrFloor", (0.20, 0.50, 0.03), (0.30, 0, BZ + 0.07), m['stone_dark'])

    # Earthwork backing (sloped earth behind the wall)
    ev = [(-0.40, -0.88, Z), (-0.40, 0.88, Z),
          (-0.40, 0.88, BZ - 0.15), (-0.40, -0.88, BZ - 0.15),
          (-0.70, -0.88, Z), (-0.70, 0.88, Z)]
    ef = [(0, 1, 2, 3), (0, 4, 5, 1), (3, 2, 1, 5, 4, 0)]
    # Simpler earthwork: a wedge shape
    ev2 = [(-0.40, -0.85, Z + 0.05), (-0.40, 0.85, Z + 0.05),
           (-0.40, 0.85, BZ - 0.10), (-0.40, -0.85, BZ - 0.10),
           (-0.75, -0.85, Z + 0.05), (-0.75, 0.85, Z + 0.05)]
    ef2 = [(0, 1, 2, 3), (4, 5, 1, 0), (4, 0, 3), (5, 1, 2), (4, 5, 2, 3)]
    mesh_from_pydata("Earthwork", ev2, ef2, m['stone_dark'])

    # Inner parapet (low)
    bmesh_box("InnerParapet", (0.08, 1.86, 0.18),
              (-0.36, 0, BZ + 0.06 + 0.09), m['stone_dark'])

    # Stone cap trim along top edge of slope
    bmesh_box("SlopeCap", (0.70, 1.90, 0.04), (0, 0, BZ), m['stone_trim'])

    # Drainage channel
    bmesh_box("Drain", (0.04, 0.08, 0.15), (0.42, 0.70, Z + slope_h * 0.3), m['stone_dark'])


# ============================================================
# ENLIGHTENMENT AGE — Brick wall with stone cap, iron spikes, buttresses
# ============================================================
def _build_enlightenment(m):
    Z = 0.0

    bmesh_box("Ground", (2.0, 2.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Foundation
    bmesh_box("Foundation", (0.65, 1.9, 0.10), (0, 0, Z + 0.05), m['stone_dark'], bevel=0.02)

    BZ = Z + 0.10
    wall_h = 1.05

    # Main brick wall
    bmesh_box("WallBody", (0.50, 1.85, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Brick course lines (horizontal mortar joints)
    for z_off in [0.20, 0.40, 0.60, 0.80]:
        bmesh_box(f"MortarLine_{z_off:.2f}", (0.52, 1.86, 0.012),
                  (0, 0, BZ + z_off), m['stone_light'])

    # Stone cap (coping stones on top)
    bmesh_box("StoneCap", (0.60, 1.92, 0.07), (0, 0, BZ + wall_h + 0.035), m['stone_trim'], bevel=0.02)

    # Iron spikes along the top
    num_spikes = 12
    spike_spacing = 1.7 / (num_spikes - 1)
    for i in range(num_spikes):
        sy = -0.85 + i * spike_spacing
        bpy.ops.mesh.primitive_cylinder_add(vertices=4, radius=0.012, depth=0.20,
                                            location=(0, sy, BZ + wall_h + 0.07 + 0.10))
        spike = bpy.context.active_object
        spike.name = f"Spike_{i}"
        spike.data.materials.append(m['iron'])
        # Spike point
        bmesh_cone(f"SpikeTop_{i}", 0.018, 0.06, 4,
                   (0, sy, BZ + wall_h + 0.07 + 0.20), m['iron'], smooth=False)

    # Iron rail connecting spikes
    bmesh_box("SpikeRail", (0.02, 1.80, 0.02),
              (0, 0, BZ + wall_h + 0.07 + 0.12), m['iron'])

    # Buttresses (3 along the wall, on the back face)
    for by in [-0.65, 0, 0.65]:
        # Buttress body
        bmesh_box(f"Buttress_{by:.1f}", (0.25, 0.14, wall_h * 0.85),
                  (-0.37, by, BZ + wall_h * 0.85 / 2), m['stone'], bevel=0.02)
        # Buttress cap (sloped top via mesh)
        bv = [(-0.25, by - 0.07, BZ + wall_h * 0.85),
              (-0.25, by + 0.07, BZ + wall_h * 0.85),
              (-0.50, by + 0.08, BZ + wall_h * 0.85),
              (-0.50, by - 0.08, BZ + wall_h * 0.85),
              (-0.25, by - 0.05, BZ + wall_h),
              (-0.25, by + 0.05, BZ + wall_h)]
        bcf = [(0, 1, 4), (1, 5, 4), (0, 3, 2, 1), (0, 4, 5, 1), (2, 3, 0, 1)]
        # Simpler: just a sloped cap
        bv2 = [(-0.25, by - 0.08, BZ + wall_h * 0.85),
               (-0.25, by + 0.08, BZ + wall_h * 0.85),
               (-0.50, by + 0.08, BZ + wall_h * 0.55),
               (-0.50, by - 0.08, BZ + wall_h * 0.55)]
        mesh_from_pydata(f"ButtressCap_{by:.1f}", bv2, [(0, 1, 2, 3)], m['stone_trim'])

    # Decorative string course
    bmesh_box("StringCourse", (0.54, 1.87, 0.03),
              (0, 0, BZ + wall_h * 0.5), m['stone_trim'])

    # Plaque / date stone (decorative center element)
    bmesh_box("Plaque", (0.04, 0.20, 0.12),
              (0.27, 0, BZ + wall_h * 0.65), m['stone_light'])


# ============================================================
# INDUSTRIAL AGE — Reinforced brick wall with steel beams, barbed wire
# ============================================================
def _build_industrial(m):
    Z = 0.0

    bmesh_box("Ground", (2.0, 2.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    # Concrete foundation
    bmesh_box("Foundation", (0.70, 1.9, 0.12), (0, 0, Z + 0.06), m['stone_dark'], bevel=0.02)

    BZ = Z + 0.12
    wall_h = 1.10

    # Main brick wall
    bmesh_box("WallBody", (0.52, 1.85, wall_h), (0, 0, BZ + wall_h / 2), m['stone'], bevel=0.02)

    # Horizontal mortar bands
    for z_off in [0.22, 0.44, 0.66, 0.88]:
        bmesh_box(f"Mortar_{z_off:.2f}", (0.54, 1.86, 0.012),
                  (0, 0, BZ + z_off), m['stone_light'])

    # Steel I-beam reinforcement (vertical, embedded in wall)
    for sy in [-0.70, 0, 0.70]:
        # Flanges visible on front
        bmesh_box(f"BeamFlange_{sy:.1f}", (0.04, 0.10, wall_h),
                  (0.27, sy, BZ + wall_h / 2), m['iron'])
        # Web
        bmesh_box(f"BeamWeb_{sy:.1f}", (0.02, 0.04, wall_h),
                  (0.25, sy, BZ + wall_h / 2), m['iron'])

    # Steel cap plate on top
    bmesh_box("SteelCap", (0.56, 1.88, 0.04), (0, 0, BZ + wall_h + 0.02), m['iron'])

    # Barbed wire support posts
    num_posts = 6
    post_spacing = 1.6 / (num_posts - 1)
    post_h = 0.22
    for i in range(num_posts):
        py = -0.80 + i * post_spacing
        # Angled post (leaning outward)
        bpy.ops.mesh.primitive_cylinder_add(vertices=4, radius=0.012, depth=post_h,
                                            location=(0.12, py, BZ + wall_h + 0.04 + post_h / 2))
        post = bpy.context.active_object
        post.name = f"BWPost_{i}"
        post.rotation_euler = (0, math.radians(25), 0)
        post.data.materials.append(m['iron'])

    # Barbed wire lines (2 strands)
    for z_add in [0.12, 0.20]:
        x_off = 0.12 + math.sin(math.radians(25)) * z_add
        bmesh_box(f"BarbWire_{z_add:.2f}", (0.01, 1.70, 0.01),
                  (x_off, 0, BZ + wall_h + 0.04 + z_add), m['iron'])

    # Barbs (small crossing bits)
    for z_add in [0.12, 0.20]:
        x_off = 0.12 + math.sin(math.radians(25)) * z_add
        for j in range(8):
            by = -0.70 + j * 0.20
            bmesh_box(f"Barb_{z_add:.2f}_{j}", (0.025, 0.005, 0.025),
                      (x_off, by, BZ + wall_h + 0.04 + z_add), m['iron'])

    # Horizontal steel brace (tie rod)
    bmesh_box("TieRod", (0.02, 1.86, 0.02), (0, 0, BZ + wall_h * 0.5), m['iron'])

    # Buttress piers (brick)
    for by in [-0.75, 0.75]:
        bmesh_box(f"Pier_{by:.1f}", (0.20, 0.12, wall_h * 0.80),
                  (-0.36, by, BZ + wall_h * 0.80 / 2), m['stone'], bevel=0.01)

    # Riveted plate detail near base
    for ry in [-0.40, 0.40]:
        bmesh_box(f"Plate_{ry:.1f}", (0.04, 0.25, 0.12),
                  (0.27, ry, BZ + 0.10), m['iron'])


# ============================================================
# MODERN AGE — Concrete blast wall with steel reinforcement strips
# ============================================================
def _build_modern(m):
    Z = 0.0

    bmesh_box("Ground", (2.0, 2.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # Heavy concrete foundation
    bmesh_box("Foundation", (0.80, 1.9, 0.14), (0, 0, Z + 0.07), m['stone_dark'], bevel=0.03)

    BZ = Z + 0.14
    wall_h = 1.15

    # Main concrete wall (T-wall / blast wall profile)
    # Wider at base, slightly narrower at top
    base_w = 0.65
    top_w = 0.50
    # Lower thick section
    bmesh_box("WallLower", (base_w, 1.85, wall_h * 0.6),
              (0, 0, BZ + wall_h * 0.3), m['stone'], bevel=0.02)
    # Upper slightly thinner section
    bmesh_box("WallUpper", (top_w, 1.85, wall_h * 0.4),
              (0, 0, BZ + wall_h * 0.8), m['stone'], bevel=0.02)

    # Steel reinforcement strips (vertical channels on face)
    for sy in [-0.65, -0.22, 0.22, 0.65]:
        bmesh_box(f"ReinfStrip_{sy:.2f}", (0.03, 0.04, wall_h),
                  (0.26, sy, BZ + wall_h / 2), metal)

    # Horizontal steel band at transition
    bmesh_box("SteelBand", (0.52, 1.86, 0.03),
              (0, 0, BZ + wall_h * 0.6), metal)

    # Top cap (steel-edged concrete)
    bmesh_box("TopCap", (0.55, 1.88, 0.05), (0, 0, BZ + wall_h + 0.025), metal)

    # Anti-climb texture (angled ridges on front face)
    num_ridges = 6
    ridge_spacing = wall_h * 0.5 / num_ridges
    for i in range(num_ridges):
        rz = BZ + 0.35 + i * ridge_spacing
        bmesh_box(f"Ridge_{i}", (0.03, 1.80, 0.015),
                  (0.28, 0, rz), m['stone_dark'])

    # Blast deflection angle at base (concrete wedge)
    wv = [(0.33, -0.90, Z + 0.14), (0.33, 0.90, Z + 0.14),
          (0.50, 0.90, Z + 0.14), (0.50, -0.90, Z + 0.14),
          (0.33, -0.90, BZ + 0.15), (0.33, 0.90, BZ + 0.15)]
    wf = [(0, 1, 2, 3), (0, 4, 5, 1), (3, 2, 1, 5, 4, 0)]
    # Simpler wedge
    wv2 = [(0.33, -0.88, Z + 0.14), (0.33, 0.88, Z + 0.14),
           (0.55, 0.88, Z + 0.14), (0.55, -0.88, Z + 0.14),
           (0.33, -0.88, BZ + 0.20), (0.33, 0.88, BZ + 0.20)]
    wf2 = [(0, 1, 2, 3), (4, 5, 1, 0), (3, 2, 5, 4), (0, 3, 4), (2, 1, 5)]
    mesh_from_pydata("BlastWedge", wv2, wf2, m['stone_dark'])

    # Mounting brackets (for attaching equipment/wire)
    for by in [-0.50, 0.50]:
        bmesh_box(f"Bracket_{by:.1f}", (0.06, 0.06, 0.04),
                  (0.26, by, BZ + wall_h - 0.10), metal)

    # Drainage weep holes
    for dy in [-0.60, 0, 0.60]:
        bmesh_box(f"Weep_{dy:.1f}", (0.06, 0.04, 0.04),
                  (0.30, dy, BZ + 0.10), m['stone_dark'])


# ============================================================
# DIGITAL AGE — Energy barrier with metal posts and glowing strip
# ============================================================
def _build_digital(m):
    Z = 0.0

    bmesh_box("Ground", (2.0, 2.0, 0.06), (0, 0, Z + 0.03), m['ground'])

    glass = m.get('glass', m['window'])
    metal = m.get('metal', m['iron'])

    # Sleek metal base plate
    bmesh_box("BasePlate", (0.40, 1.9, 0.05), (0, 0, Z + 0.025), metal)

    BZ = Z + 0.05
    post_h = 1.10

    # Two main metal posts at each end of the segment
    for py in [-0.85, 0.85]:
        # Post body (octagonal prism)
        bmesh_prism(f"Post_{py:.1f}", 0.08, post_h, 8, (0, py, BZ), metal)

        # Post cap (small emitter dome)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06,
                                              location=(0, py, BZ + post_h + 0.03))
        cap = bpy.context.active_object
        cap.name = f"PostCap_{py:.1f}"
        cap.scale = (1, 1, 0.5)
        cap.data.materials.append(m['gold'])
        bpy.ops.object.shade_smooth()

        # Post base ring (accent)
        bmesh_prism(f"PostRing_{py:.1f}", 0.10, 0.04, 8, (0, py, BZ), m['gold'])

        # Indicator lights on post
        for lz in [0.30, 0.60, 0.90]:
            bmesh_box(f"Light_{py:.1f}_{lz:.1f}", (0.03, 0.03, 0.03),
                      (0.09, py, BZ + lz), m['gold'])

    # Energy barrier strips (glowing horizontal bands between posts)
    # Main energy strip (wide, gold/glowing)
    bmesh_box("EnergyMain", (0.02, 1.50, 0.30),
              (0, 0, BZ + post_h * 0.55), m['gold'])

    # Upper energy strip
    bmesh_box("EnergyUpper", (0.02, 1.50, 0.12),
              (0, 0, BZ + post_h * 0.82), m['gold'])

    # Lower energy strip
    bmesh_box("EnergyLower", (0.02, 1.50, 0.12),
              (0, 0, BZ + post_h * 0.28), m['gold'])

    # Faint energy field fill between strips (semi-transparent glass)
    bmesh_box("EnergyField", (0.01, 1.50, post_h * 0.70),
              (0, 0, BZ + post_h * 0.50), glass)

    # Horizontal frame rails connecting posts (structural, metal)
    for rz in [0.10, post_h - 0.05]:
        bmesh_box(f"Rail_{rz:.2f}", (0.04, 1.60, 0.03),
                  (0, 0, BZ + rz), metal)

    # Mid-span support node (floating metal hub)
    bmesh_prism("MidNode", 0.05, 0.06, 8, (0, 0, BZ + post_h * 0.55 - 0.03), metal)
    # Node accent ring
    bmesh_prism("NodeRing", 0.07, 0.02, 8, (0, 0, BZ + post_h * 0.55 - 0.01), m['gold'])

    # Base emitter strips (ground glow lines)
    for py_off in [-0.40, 0, 0.40]:
        bmesh_box(f"GlowLine_{py_off:.1f}", (0.30, 0.02, 0.02),
                  (0, py_off, Z + 0.04), m['gold'])

    # Conduit running along base (power feed)
    bmesh_box("Conduit", (0.03, 1.70, 0.03), (0.15, 0, BZ + 0.02), metal)


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


def build_wall(materials, age='medieval'):
    """Build a Wall segment with geometry appropriate for the given age."""
    builder = AGE_BUILDERS.get(age, _build_medieval)
    builder(materials)
