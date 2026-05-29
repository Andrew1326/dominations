"""
Ranged Shooter (Archer) unit — procedural model, armature, and animations.

Builds a stylized low-poly archer with:
  - Chunky readable silhouette (DomiNations style)
  - Full armature: spine, chest, head, arms, legs
  - Bow mesh parented to hand bone
  - Quiver on back
  - Two NLA actions: "Move" (walk cycle) and "Shoot" (draw + release)
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler


# ── Helpers ──────────────────────────────────────────────────────────

def _clear_unit():
    """Remove previous unit objects (idempotent)."""
    for obj in list(bpy.data.objects):
        if obj.name.startswith("Archer"):
            bpy.data.objects.remove(obj, do_unlink=True)
    for arm in list(bpy.data.armatures):
        if arm.name.startswith("Archer"):
            bpy.data.armatures.remove(arm)
    for mesh in list(bpy.data.meshes):
        if mesh.name.startswith("Archer"):
            bpy.data.meshes.remove(mesh)


def _simple_mat(name, color, roughness=0.6, metallic=0.0):
    """Quick PBR material with a single color."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat


def _bmesh_box(name, size, origin=(0, 0, 0), material=None):
    """Axis-aligned box via bmesh."""
    bm = bmesh.new()
    sx, sy, sz = size[0] / 2, size[1] / 2, size[2] / 2
    ox, oy, oz = origin
    v = [
        bm.verts.new((ox - sx, oy - sy, oz)),
        bm.verts.new((ox + sx, oy - sy, oz)),
        bm.verts.new((ox + sx, oy + sy, oz)),
        bm.verts.new((ox - sx, oy + sy, oz)),
        bm.verts.new((ox - sx, oy - sy, oz + sz * 2)),
        bm.verts.new((ox + sx, oy - sy, oz + sz * 2)),
        bm.verts.new((ox + sx, oy + sy, oz + sz * 2)),
        bm.verts.new((ox - sx, oy + sy, oz + sz * 2)),
    ]
    bm.faces.new([v[0], v[3], v[2], v[1]])  # bottom
    bm.faces.new([v[4], v[5], v[6], v[7]])  # top
    bm.faces.new([v[0], v[1], v[5], v[4]])
    bm.faces.new([v[2], v[3], v[7], v[6]])
    bm.faces.new([v[0], v[4], v[7], v[3]])
    bm.faces.new([v[1], v[2], v[6], v[5]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj


def _bmesh_cylinder(name, radius, height, segments=12, origin=(0, 0, 0), material=None):
    """Simple cylinder via bmesh."""
    bm = bmesh.new()
    ox, oy, oz = origin
    bot, top = [], []
    for i in range(segments):
        a = (2 * math.pi * i) / segments
        x = ox + radius * math.cos(a)
        y = oy + radius * math.sin(a)
        bot.append(bm.verts.new((x, y, oz)))
        top.append(bm.verts.new((x, y, oz + height)))
    bm.faces.new(bot)
    bm.faces.new(list(reversed(top)))
    for i in range(segments):
        j = (i + 1) % segments
        bm.faces.new([bot[i], bot[j], top[j], top[i]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


# ── Materials ────────────────────────────────────────────────────────

def _create_materials():
    """Create the unit's material palette."""
    return {
        'skin':    _simple_mat("ArcherSkin",    (0.72, 0.55, 0.40), roughness=0.7),
        'tunic':   _simple_mat("ArcherTunic",   (0.22, 0.35, 0.18), roughness=0.75),
        'leather': _simple_mat("ArcherLeather", (0.35, 0.22, 0.10), roughness=0.8),
        'metal':   _simple_mat("ArcherMetal",   (0.45, 0.42, 0.40), roughness=0.35, metallic=0.85),
        'wood':    _simple_mat("ArcherWood",    (0.42, 0.26, 0.13), roughness=0.7),
        'hair':    _simple_mat("ArcherHair",    (0.15, 0.10, 0.06), roughness=0.85),
        'string':  _simple_mat("ArcherString",  (0.80, 0.75, 0.60), roughness=0.9),
        'boot':    _simple_mat("ArcherBoot",    (0.25, 0.16, 0.08), roughness=0.8),
        'pants':   _simple_mat("ArcherPants",   (0.30, 0.25, 0.18), roughness=0.75),
    }


# ── Body mesh builders ───────────────────────────────────────────────

def _build_body(mats):
    """Build the archer's body parts as separate meshes.
    Returns dict of body part objects."""
    parts = {}

    # Torso — slightly tapered box
    parts['torso'] = _bmesh_box("ArcherTorso", (0.50, 0.28, 0.45), (0, 0, 0.95), mats['tunic'])

    # Waist/belt
    parts['belt'] = _bmesh_box("ArcherBelt", (0.52, 0.30, 0.08), (0, 0, 0.92), mats['leather'])

    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, segments=16, ring_count=12, location=(0, 0, 1.72))
    head = bpy.context.active_object
    head.name = "ArcherHead"
    head.data.materials.append(mats['skin'])
    parts['head'] = head

    # Hair (slightly larger partial sphere on top)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.19, segments=12, ring_count=8, location=(0, 0.02, 1.76))
    hair = bpy.context.active_object
    hair.name = "ArcherHair"
    hair.scale = (1.0, 1.1, 0.8)
    hair.data.materials.append(mats['hair'])
    parts['hair'] = hair

    # Neck
    parts['neck'] = _bmesh_cylinder("ArcherNeck", 0.08, 0.12, 8, (0, 0, 1.52), mats['skin'])

    # Upper arms
    parts['upperarm_l'] = _bmesh_box("ArcherUpperArm.L", (0.14, 0.14, 0.28), (0.34, 0, 1.28), mats['tunic'])
    parts['upperarm_r'] = _bmesh_box("ArcherUpperArm.R", (0.14, 0.14, 0.28), (-0.34, 0, 1.28), mats['tunic'])

    # Forearms
    parts['forearm_l'] = _bmesh_box("ArcherForearm.L", (0.12, 0.12, 0.26), (0.34, 0, 0.96), mats['skin'])
    parts['forearm_r'] = _bmesh_box("ArcherForearm.R", (0.12, 0.12, 0.26), (-0.34, 0, 0.96), mats['skin'])

    # Hands
    parts['hand_l'] = _bmesh_box("ArcherHand.L", (0.10, 0.06, 0.12), (0.34, 0, 0.82), mats['skin'])
    parts['hand_r'] = _bmesh_box("ArcherHand.R", (0.10, 0.06, 0.12), (-0.34, 0, 0.82), mats['skin'])

    # Pants / upper legs
    parts['thigh_l'] = _bmesh_box("ArcherThigh.L", (0.17, 0.18, 0.32), (0.12, 0, 0.58), mats['pants'])
    parts['thigh_r'] = _bmesh_box("ArcherThigh.R", (0.17, 0.18, 0.32), (-0.12, 0, 0.58), mats['pants'])

    # Shins
    parts['shin_l'] = _bmesh_box("ArcherShin.L", (0.14, 0.14, 0.30), (0.12, 0, 0.22), mats['pants'])
    parts['shin_r'] = _bmesh_box("ArcherShin.R", (0.14, 0.14, 0.30), (-0.12, 0, 0.22), mats['pants'])

    # Boots
    parts['boot_l'] = _bmesh_box("ArcherBoot.L", (0.15, 0.20, 0.12), (0.12, 0.02, 0.0), mats['boot'])
    parts['boot_r'] = _bmesh_box("ArcherBoot.R", (0.15, 0.20, 0.12), (-0.12, 0.02, 0.0), mats['boot'])

    # Shoulder guards
    parts['shoulder_l'] = _bmesh_box("ArcherShoulder.L", (0.18, 0.18, 0.06), (0.34, 0, 1.44), mats['leather'])
    parts['shoulder_r'] = _bmesh_box("ArcherShoulder.R", (0.18, 0.18, 0.06), (-0.34, 0, 1.44), mats['leather'])

    return parts


def _build_bow(mats):
    """Build a simple bow mesh from a curve."""
    # Bow body — bezier curve extruded
    bpy.ops.curve.primitive_bezier_curve_add(location=(0.34, -0.15, 1.15))
    bow_curve = bpy.context.active_object
    bow_curve.name = "ArcherBowCurve"
    bow_curve.data.dimensions = '3D'
    bow_curve.data.bevel_depth = 0.02
    bow_curve.data.bevel_resolution = 3

    # Shape the bow arc
    points = bow_curve.data.splines[0].bezier_points
    points[0].co = (0, 0, -0.45)
    points[0].handle_left = (-0.25, 0, -0.50)
    points[0].handle_right = (0.25, 0, -0.40)
    points[1].co = (0, 0, 0.45)
    points[1].handle_left = (0.25, 0, 0.40)
    points[1].handle_right = (-0.25, 0, 0.50)

    bow_curve.data.materials.append(mats['wood'])

    # Bowstring — thin line between tips
    bpy.ops.curve.primitive_bezier_curve_add(location=(0.34, -0.15, 1.15))
    string = bpy.context.active_object
    string.name = "ArcherBowString"
    string.data.dimensions = '3D'
    string.data.bevel_depth = 0.005
    string.data.bevel_resolution = 1

    pts = string.data.splines[0].bezier_points
    pts[0].co = (0, 0, -0.45)
    pts[0].handle_left = (0, 0.02, -0.45)
    pts[0].handle_right = (0, -0.02, -0.45)
    pts[1].co = (0, 0, 0.45)
    pts[1].handle_left = (0, -0.02, 0.45)
    pts[1].handle_right = (0, 0.02, 0.45)

    string.data.materials.append(mats['string'])

    return bow_curve, string


def _build_quiver(mats):
    """Build a quiver with arrows on the back."""
    # Quiver body
    quiver = _bmesh_cylinder("ArcherQuiver", 0.06, 0.45, 8, (-0.18, 0.15, 1.05), mats['leather'])

    # Arrow shafts sticking out
    arrows = []
    for i, (dx, dy) in enumerate([(0.02, 0.01), (-0.02, 0.02), (0.0, -0.01)]):
        arrow = _bmesh_cylinder(f"ArcherArrow{i}", 0.008, 0.55, 6,
                                (-0.18 + dx, 0.15 + dy, 1.05), mats['wood'])
        arrows.append(arrow)

    # Arrow fletching tips (tiny cones)
    tips = []
    for i, (dx, dy) in enumerate([(0.02, 0.01), (-0.02, 0.02), (0.0, -0.01)]):
        bpy.ops.mesh.primitive_cone_add(radius1=0.015, radius2=0, depth=0.04,
                                        location=(-0.18 + dx, 0.15 + dy, 1.60))
        tip = bpy.context.active_object
        tip.name = f"ArcherArrowTip{i}"
        tip.data.materials.append(mats['metal'])
        tips.append(tip)

    return quiver, arrows, tips


# ── Armature ─────────────────────────────────────────────────────────

# Bone definitions: (name, head, tail, parent_name, connected)
BONE_DEFS = [
    ("Root",        (0, 0, 0.90),   (0, 0, 0.95),   None,           False),
    ("Spine",       (0, 0, 0.95),   (0, 0, 1.15),   "Root",         True),
    ("Chest",       (0, 0, 1.15),   (0, 0, 1.40),   "Spine",        True),
    ("Neck",        (0, 0, 1.40),   (0, 0, 1.55),   "Chest",        True),
    ("Head",        (0, 0, 1.55),   (0, 0, 1.80),   "Neck",         True),

    # Left arm
    ("Shoulder.L",  (0.25, 0, 1.38), (0.34, 0, 1.38), "Chest",       False),
    ("UpperArm.L",  (0.34, 0, 1.38), (0.34, 0, 1.10), "Shoulder.L",  True),
    ("Forearm.L",   (0.34, 0, 1.10), (0.34, 0, 0.85), "UpperArm.L",  True),
    ("Hand.L",      (0.34, 0, 0.85), (0.34, 0, 0.75), "Forearm.L",   True),

    # Right arm
    ("Shoulder.R",  (-0.25, 0, 1.38), (-0.34, 0, 1.38), "Chest",      False),
    ("UpperArm.R",  (-0.34, 0, 1.38), (-0.34, 0, 1.10), "Shoulder.R", True),
    ("Forearm.R",   (-0.34, 0, 1.10), (-0.34, 0, 0.85), "UpperArm.R", True),
    ("Hand.R",      (-0.34, 0, 0.85), (-0.34, 0, 0.75), "Forearm.R",  True),

    # Left leg
    ("Thigh.L",     (0.12, 0, 0.90), (0.12, 0, 0.52), "Root",         False),
    ("Shin.L",      (0.12, 0, 0.52), (0.12, 0, 0.12), "Thigh.L",     True),
    ("Foot.L",      (0.12, 0, 0.12), (0.12, 0.12, 0.0), "Shin.L",    True),

    # Right leg
    ("Thigh.R",     (-0.12, 0, 0.90), (-0.12, 0, 0.52), "Root",       False),
    ("Shin.R",      (-0.12, 0, 0.52), (-0.12, 0, 0.12), "Thigh.R",   True),
    ("Foot.R",      (-0.12, 0, 0.12), (-0.12, 0.12, 0.0), "Shin.R",  True),

    # Bow bone (attached to left hand)
    ("Bow",         (0.34, 0, 0.80), (0.34, -0.15, 0.80), "Hand.L",   False),
]


def _create_armature():
    """Create the archer armature with all bones."""
    arm_data = bpy.data.armatures.new("ArcherRig")
    arm_obj = bpy.data.objects.new("ArcherRig", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    for name, head, tail, parent_name, connected in BONE_DEFS:
        b = arm_data.edit_bones.new(name)
        b.head = head
        b.tail = tail
        if parent_name:
            b.parent = arm_data.edit_bones[parent_name]
            b.use_connect = connected

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj


def _parent_mesh_to_bone(arm_obj, mesh_obj, bone_name):
    """Parent a mesh to a specific bone with automatic weights."""
    mesh_obj.parent = arm_obj
    mesh_obj.parent_type = 'BONE'
    mesh_obj.parent_bone = bone_name
    # Offset to compensate for bone parenting
    bone = arm_obj.data.bones[bone_name]
    mesh_obj.matrix_parent_inverse = (arm_obj.matrix_world @ bone.matrix_local).inverted()


def _parent_all_parts(arm_obj, parts, bow_curve, bow_string, quiver, arrows, arrow_tips):
    """Parent all meshes to appropriate bones."""
    bone_map = {
        'torso': 'Spine',
        'belt': 'Spine',
        'neck': 'Neck',
        'head': 'Head',
        'hair': 'Head',
        'upperarm_l': 'UpperArm.L',
        'upperarm_r': 'UpperArm.R',
        'forearm_l': 'Forearm.L',
        'forearm_r': 'Forearm.R',
        'hand_l': 'Hand.L',
        'hand_r': 'Hand.R',
        'thigh_l': 'Thigh.L',
        'thigh_r': 'Thigh.R',
        'shin_l': 'Shin.L',
        'shin_r': 'Shin.R',
        'boot_l': 'Foot.L',
        'boot_r': 'Foot.R',
        'shoulder_l': 'Shoulder.L',
        'shoulder_r': 'Shoulder.R',
    }

    for part_name, bone_name in bone_map.items():
        if part_name in parts:
            _parent_mesh_to_bone(arm_obj, parts[part_name], bone_name)

    # Bow and string to bow bone
    _parent_mesh_to_bone(arm_obj, bow_curve, 'Bow')
    _parent_mesh_to_bone(arm_obj, bow_string, 'Bow')

    # Quiver and arrows to chest
    _parent_mesh_to_bone(arm_obj, quiver, 'Chest')
    for arrow in arrows:
        _parent_mesh_to_bone(arm_obj, arrow, 'Chest')
    for tip in arrow_tips:
        _parent_mesh_to_bone(arm_obj, tip, 'Chest')


# ── Animations ───────────────────────────────────────────────────────

def _create_walk_action(arm_obj):
    """Create a looping walk cycle action.

    24 frames, loopable. Arms swing opposite to legs.
    Subtle torso bob and head counter-rotation.
    """
    action = bpy.data.actions.new("ArcherWalk")
    action.use_fake_user = True

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')

    arm_obj.animation_data_create()
    arm_obj.animation_data.action = action

    # Walk cycle keyframes: frame → bone → (rx, ry, rz) in degrees
    # One full stride = 24 frames
    cycle = {
        # Left leg: forward at f1, back at f13, forward at f25(=f1)
        'Thigh.L':    [(1, (25, 0, 0)), (7, (10, 0, 0)), (13, (-25, 0, 0)), (19, (-10, 0, 0)), (25, (25, 0, 0))],
        'Shin.L':     [(1, (-10, 0, 0)), (7, (-45, 0, 0)), (13, (-5, 0, 0)), (19, (-20, 0, 0)), (25, (-10, 0, 0))],
        'Foot.L':     [(1, (10, 0, 0)), (7, (15, 0, 0)), (13, (-10, 0, 0)), (19, (5, 0, 0)), (25, (10, 0, 0))],

        # Right leg: opposite phase
        'Thigh.R':    [(1, (-25, 0, 0)), (7, (-10, 0, 0)), (13, (25, 0, 0)), (19, (10, 0, 0)), (25, (-25, 0, 0))],
        'Shin.R':     [(1, (-5, 0, 0)), (7, (-20, 0, 0)), (13, (-10, 0, 0)), (19, (-45, 0, 0)), (25, (-5, 0, 0))],
        'Foot.R':     [(1, (-10, 0, 0)), (7, (5, 0, 0)), (13, (10, 0, 0)), (19, (15, 0, 0)), (25, (-10, 0, 0))],

        # Arms: counter-swing (holding bow, so left arm stays more static)
        'UpperArm.L': [(1, (-8, 0, 5)), (13, (8, 0, 5)), (25, (-8, 0, 5))],
        'Forearm.L':  [(1, (-5, 0, 0)), (13, (5, 0, 0)), (25, (-5, 0, 0))],
        'UpperArm.R': [(1, (15, 0, -5)), (13, (-15, 0, -5)), (25, (15, 0, -5))],
        'Forearm.R':  [(1, (-10, 0, 0)), (13, (-5, 0, 0)), (25, (-10, 0, 0))],

        # Torso: subtle twist and bob
        'Spine':      [(1, (0, 0, 3)), (7, (2, 0, 0)), (13, (0, 0, -3)), (19, (2, 0, 0)), (25, (0, 0, 3))],
        'Chest':      [(1, (0, 0, -2)), (13, (0, 0, 2)), (25, (0, 0, -2))],

        # Head: slight counter
        'Head':       [(1, (0, 0, -1)), (13, (0, 0, 1)), (25, (0, 0, -1))],

        # Root: vertical bob
        'Root':       [(1, (0, 0, 0)), (7, (1, 0, 0)), (13, (0, 0, 0)), (19, (1, 0, 0)), (25, (0, 0, 0))],
    }

    for bone_name, keyframes in cycle.items():
        bone = arm_obj.pose.bones.get(bone_name)
        if not bone:
            continue
        bone.rotation_mode = 'XYZ'
        for frame, (rx, ry, rz) in keyframes:
            bone.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))
            bone.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Also keyframe root location for the vertical bob
    root = arm_obj.pose.bones.get("Root")
    if root:
        for frame, dz in [(1, 0), (7, 0.02), (13, 0), (19, 0.02), (25, 0)]:
            root.location = (0, 0, dz)
            root.keyframe_insert(data_path="location", frame=frame)

    # Set interpolation to bezier for smooth motion
    # Blender 5.0: fcurves are at action.layers[0].strips[0].channelbags[0].fcurves
    for layer in action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves:
                    for kp in fc.keyframe_points:
                        kp.interpolation = 'BEZIER'
                        kp.easing = 'AUTO'
                    # Add cycles modifier for looping
                    mod = fc.modifiers.new(type='CYCLES')
                    mod.mode_before = 'REPEAT'
                    mod.mode_after = 'REPEAT'

    bpy.ops.object.mode_set(mode='OBJECT')
    return action


def _create_shoot_action(arm_obj):
    """Create a shooting action.

    30 frames total:
      f1:     Rest pose
      f1-8:   Raise bow arm, begin draw
      f8-14:  Full draw + aim
      f14-17: Release arrow
      f17-30: Follow-through, return to rest

    Rotations kept small (max ~30°) since meshes are rigid boxes,
    not skinned. Large rotations cause parts to fly apart.
    """
    action = bpy.data.actions.new("ArcherShoot")
    action.use_fake_user = True

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')

    arm_obj.animation_data.action = action

    # Shooting keyframes — conservative rotations for rigid parenting
    shoot = {
        # Left arm (bow arm): raises forward to aim
        'UpperArm.L': [
            (1,  (0, 0, 0)),         # rest
            (5,  (15, 5, 8)),        # lifting bow
            (8,  (25, 8, 12)),       # bow raised
            (14, (25, 8, 12)),       # hold aim
            (17, (20, 5, 10)),       # release
            (22, (10, 3, 5)),        # lowering
            (30, (0, 0, 0)),         # rest
        ],
        'Forearm.L': [
            (1,  (0, 0, 0)),
            (5,  (-8, 0, 0)),
            (8,  (-15, 0, 0)),       # arm extended
            (14, (-15, 0, 0)),
            (17, (-10, 0, 0)),
            (30, (0, 0, 0)),
        ],

        # Right arm (draw arm): pulls string back
        'UpperArm.R': [
            (1,  (0, 0, 0)),         # rest
            (5,  (15, -5, -8)),      # reaching for string
            (8,  (20, -15, -10)),    # pulling back
            (12, (18, -25, -8)),     # fully drawn
            (14, (18, -25, -8)),     # hold
            (15, (10, -5, -5)),      # release snap
            (17, (5, 0, -3)),        # follow through
            (30, (0, 0, 0)),         # rest
        ],
        'Forearm.R': [
            (1,  (0, 0, 0)),
            (5,  (-10, 0, 0)),
            (8,  (-25, 0, 0)),       # pulling
            (12, (-30, 0, 0)),       # fully drawn
            (14, (-30, 0, 0)),       # hold
            (15, (-5, 0, 0)),        # snap forward
            (17, (-3, 0, 0)),
            (30, (0, 0, 0)),
        ],
        'Hand.R': [
            (1,  (0, 0, 0)),
            (12, (-5, 0, 0)),        # grip
            (15, (8, 0, 0)),         # release fingers
            (17, (3, 0, 0)),
            (30, (0, 0, 0)),
        ],

        # Torso: subtle lean into the shot
        'Spine': [
            (1,  (0, 0, 0)),
            (8,  (-2, 0, -3)),
            (14, (-3, 0, -4)),       # leaning into aim
            (17, (2, 0, 0)),         # recoil
            (30, (0, 0, 0)),
        ],
        'Chest': [
            (1,  (0, 0, 0)),
            (8,  (-2, 0, -2)),
            (14, (-2, 0, -3)),
            (17, (3, 0, 1)),         # recoil back
            (22, (1, 0, 0)),
            (30, (0, 0, 0)),
        ],

        # Head: tilt to aim
        'Head': [
            (1,  (0, 0, 0)),
            (8,  (-3, 0, -5)),
            (14, (-5, 0, -6)),       # looking at target
            (17, (-2, 0, -3)),
            (30, (0, 0, 0)),
        ],

        # Legs: widen stance slightly
        'Thigh.L': [
            (1,  (0, 0, 0)),
            (5,  (5, 0, 3)),         # step into stance
            (14, (8, 0, 4)),
            (22, (4, 0, 2)),
            (30, (0, 0, 0)),
        ],
        'Thigh.R': [
            (1,  (0, 0, 0)),
            (5,  (-5, 0, -3)),
            (14, (-6, 0, -3)),
            (22, (-3, 0, -1)),
            (30, (0, 0, 0)),
        ],
    }

    for bone_name, keyframes in shoot.items():
        bone = arm_obj.pose.bones.get(bone_name)
        if not bone:
            continue
        bone.rotation_mode = 'XYZ'
        for frame, (rx, ry, rz) in keyframes:
            bone.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))
            bone.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Bezier interpolation
    # Blender 5.0: fcurves are at action.layers[0].strips[0].channelbags[0].fcurves
    for layer in action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves:
                    for kp in fc.keyframe_points:
                        kp.interpolation = 'BEZIER'
                        kp.easing = 'AUTO'

    bpy.ops.object.mode_set(mode='OBJECT')
    return action


# ── Main builder ─────────────────────────────────────────────────────

def build_ranged_shooter():
    """Build the complete ranged shooter: model, rig, and animations.

    Returns:
        arm_obj: The armature object (rig)
        walk_action: The walk cycle action
        shoot_action: The shoot action
    """
    _clear_unit()

    # Materials
    mats = _create_materials()

    # Build meshes
    parts = _build_body(mats)
    bow_curve, bow_string = _build_bow(mats)
    quiver, arrows, arrow_tips = _build_quiver(mats)

    # Create armature
    arm_obj = _create_armature()

    # Parent meshes to bones
    _parent_all_parts(arm_obj, parts, bow_curve, bow_string, quiver, arrows, arrow_tips)

    # Create animations
    walk_action = _create_walk_action(arm_obj)
    shoot_action = _create_shoot_action(arm_obj)

    # Set up NLA tracks so both actions are available
    bpy.context.view_layer.objects.active = arm_obj

    if not arm_obj.animation_data:
        arm_obj.animation_data_create()

    # Push walk as NLA track
    track_walk = arm_obj.animation_data.nla_tracks.new()
    track_walk.name = "Walk"
    strip_walk = track_walk.strips.new("Walk", start=1, action=walk_action)
    strip_walk.repeat = 1
    strip_walk.blend_type = 'REPLACE'
    track_walk.mute = True  # muted by default, render script activates as needed

    # Push shoot as NLA track
    track_shoot = arm_obj.animation_data.nla_tracks.new()
    track_shoot.name = "Shoot"
    strip_shoot = track_shoot.strips.new("Shoot", start=1, action=shoot_action)
    strip_shoot.repeat = 1
    strip_shoot.blend_type = 'REPLACE'
    track_shoot.mute = True

    # Clear active action so NLA can drive
    arm_obj.animation_data.action = None

    return arm_obj, walk_action, shoot_action
