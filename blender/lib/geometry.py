"""
Geometry builders — bmesh box, prism, cone, pyramid roof, mesh_from_pydata.
Reusable across all building scripts.
"""

import bpy
import bmesh
import math


def mesh_from_pydata(name, vertices, faces, material=None):
    """Create a mesh object from raw vertex/face data."""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj


def bmesh_box(name, size, origin=(0, 0, 0), material=None, bevel=0.0):
    """Axis-aligned box via bmesh with optional bevel."""
    bm = bmesh.new()
    sx, sy, sz = size[0] / 2, size[1] / 2, size[2] / 2
    ox, oy, oz = origin
    v = [
        bm.verts.new((ox - sx, oy - sy, oz - sz)), bm.verts.new((ox + sx, oy - sy, oz - sz)),
        bm.verts.new((ox + sx, oy + sy, oz - sz)), bm.verts.new((ox - sx, oy + sy, oz - sz)),
        bm.verts.new((ox - sx, oy - sy, oz + sz)), bm.verts.new((ox + sx, oy - sy, oz + sz)),
        bm.verts.new((ox + sx, oy + sy, oz + sz)), bm.verts.new((ox - sx, oy + sy, oz + sz)),
    ]
    bm.faces.new([v[0], v[3], v[2], v[1]])
    bm.faces.new([v[4], v[5], v[6], v[7]])
    bm.faces.new([v[0], v[1], v[5], v[4]])
    bm.faces.new([v[2], v[3], v[7], v[6]])
    bm.faces.new([v[0], v[4], v[7], v[3]])
    bm.faces.new([v[1], v[2], v[6], v[5]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    if bevel > 0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = 'ANGLE'
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="Bevel")
    return obj


def bmesh_prism(name, radius, height, segments, origin=(0, 0, 0), material=None, bevel=0.0):
    """Polygonal prism (octagon, hexagon, etc) via bmesh."""
    bm = bmesh.new()
    ox, oy, oz = origin
    bot, top = [], []
    for i in range(segments):
        a = (2 * math.pi * i) / segments
        x, y = ox + radius * math.cos(a), oy + radius * math.sin(a)
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
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    if bevel > 0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 1
        mod.limit_method = 'ANGLE'
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="Bevel")
    return obj


def bmesh_cone(name, radius, height, segments, origin=(0, 0, 0), material=None, smooth=True):
    """Cone via bmesh."""
    bm = bmesh.new()
    ox, oy, oz = origin
    base = []
    for i in range(segments):
        a = (2 * math.pi * i) / segments
        base.append(bm.verts.new((ox + radius * math.cos(a), oy + radius * math.sin(a), oz)))
    apex = bm.verts.new((ox, oy, oz + height))
    bm.faces.new(base)
    for i in range(segments):
        bm.faces.new([base[i], base[(i + 1) % segments], apex])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def pyramid_roof(name, w, d, h, overhang=0.15, origin=(0, 0, 0), material=None):
    """Hipped roof with overhang using from_pydata."""
    ox, oy, oz = origin
    hw, hd = w / 2 + overhang, d / 2 + overhang
    tw, td = 0.12, 0.12  # top ridge size

    verts = [
        (ox - hw, oy - hd, oz), (ox + hw, oy - hd, oz),
        (ox + hw, oy + hd, oz), (ox - hw, oy + hd, oz),
        (ox - tw, oy - td, oz + h), (ox + tw, oy - td, oz + h),
        (ox + tw, oy + td, oz + h), (ox - tw, oy + td, oz + h),
    ]
    faces = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)]
    obj = mesh_from_pydata(name, verts, faces, material)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj
