"""
Scene setup utilities — clear, configure renderer, camera, lighting, compositing.
Designed for realistic isometric building renders with proper shadows,
ambient occlusion, and post-processing.
"""

import bpy
import math
from mathutils import Vector


def clear_scene():
    """Remove all objects and orphan data from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)
    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)
    for block in bpy.data.worlds:
        if block.users == 0:
            bpy.data.worlds.remove(block)


def setup_scene(resolution=512, samples=256):
    """Set up a clean scene with Cycles renderer and transparent background."""
    clear_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    # Cycles for realistic rendering
    scene.render.engine = 'CYCLES'
    cycles = scene.cycles
    cycles.samples = samples
    cycles.use_denoising = True
    cycles.denoiser = 'OPENIMAGEDENOISE'

    # Better light bounces for realism
    cycles.max_bounces = 8
    cycles.diffuse_bounces = 4
    cycles.glossy_bounces = 4
    cycles.transmission_bounces = 8
    cycles.transparent_max_bounces = 8

    # Try GPU
    try:
        cycles.device = 'GPU'
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'CUDA'
        prefs.get_devices()
        for device in prefs.devices:
            device.use = True
    except Exception:
        cycles.device = 'CPU'

    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.compression = 15
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100

    # Enable AO pass for compositing
    view_layer = bpy.context.view_layer
    view_layer.use_pass_ambient_occlusion = True

    return scene


def setup_camera(ortho_scale=12.0, target_z=2.2, elevation=30, azimuth=45, distance=20):
    """Set up an isometric orthographic camera with Track-To constraint."""
    scene = bpy.context.scene

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, target_z))
    target = bpy.context.active_object
    target.name = "CameraTarget"

    cam_data = bpy.data.cameras.new("IsoCamera")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = ortho_scale
    cam_data.clip_start = 0.1
    cam_data.clip_end = 100

    elev = math.radians(elevation)
    azim = math.radians(azimuth)
    cam = bpy.data.objects.new("IsoCamera", cam_data)
    cam.location = (
        distance * math.cos(elev) * math.cos(azim),
        -distance * math.cos(elev) * math.sin(azim),
        distance * math.sin(elev),
    )
    scene.collection.objects.link(cam)
    scene.camera = cam

    track = cam.constraints.new(type='TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'
    return cam


def setup_lighting():
    """Realistic outdoor lighting: Sun + key/fill/rim + Nishita sky environment."""

    # --- Sun light for crisp directional shadows ---
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    sun = bpy.context.active_object
    sun.name = "SunLight"
    sun.data.energy = 0.3
    sun.data.angle = 0.03  # Sharp sun disk
    sun.data.color = (1.0, 0.95, 0.85)  # Warm sunlight
    sun.rotation_euler = (math.radians(50), 0, math.radians(35))

    # --- Key light (large soft) — reduced since sky provides ambient ---
    bpy.ops.object.light_add(type='AREA', location=(6, -5, 7))
    key = bpy.context.active_object
    key.name = "KeyLight"
    key.data.energy = 2
    key.data.size = 6
    key.data.color = (1.0, 0.96, 0.88)
    key.rotation_euler = (math.radians(45), 0, math.radians(30))

    # --- Fill light (cool, softer) ---
    bpy.ops.object.light_add(type='AREA', location=(-5, -3, 5))
    fill = bpy.context.active_object
    fill.name = "FillLight"
    fill.data.energy = 0.5
    fill.data.size = 8
    fill.data.color = (0.82, 0.88, 1.0)  # Cool blue fill
    fill.rotation_euler = (math.radians(55), 0, math.radians(-120))

    # --- Rim/back light (warm highlight edge) ---
    bpy.ops.object.light_add(type='AREA', location=(0, 6, 6))
    rim = bpy.context.active_object
    rim.name = "RimLight"
    rim.data.energy = 1
    rim.data.size = 4
    rim.data.color = (1.0, 0.95, 0.85)
    rim.rotation_euler = (math.radians(40), 0, math.radians(200))

    # --- Nishita Sky — realistic environment lighting + reflections ---
    # With film_transparent, sky won't render as background but WILL
    # provide environment light, reflections on metal/glass, and color bounce.
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    # Clear default nodes
    for node in list(nodes):
        nodes.remove(node)

    sky = nodes.new('ShaderNodeTexSky')
    sky.sky_type = 'MULTIPLE_SCATTERING'
    sky.sun_elevation = math.radians(45)
    sky.sun_rotation = math.radians(35)
    sky.air_density = 1.0
    sky.aerosol_density = 0.5
    sky.ozone_density = 1.0
    sky.altitude = 0.0
    sky.location = (0, 0)

    bg = nodes.new('ShaderNodeBackground')
    bg.inputs['Strength'].default_value = 0.02
    bg.location = (200, 0)
    links.new(sky.outputs['Color'], bg.inputs['Color'])

    out = nodes.new('ShaderNodeOutputWorld')
    out.location = (400, 0)
    links.new(bg.outputs['Background'], out.inputs['Surface'])


def add_shadow_catcher():
    """Add an invisible ground plane that catches shadows.
    With Cycles + film_transparent, the shadow renders as semi-transparent
    darkening on the PNG — gives the building a grounded, realistic look."""
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    catcher = bpy.context.active_object
    catcher.name = "ShadowCatcher"
    catcher.is_shadow_catcher = True


def setup_compositing():
    """Set up compositor nodes for post-processing.
    Blender 5.0 uses compositing_node_group with NodeGroupOutput."""
    scene = bpy.context.scene
    scene.use_nodes = True

    # Blender 5.0: compositor uses node groups
    tree = bpy.data.node_groups.new('Compositing', 'CompositorNodeTree')
    scene.compositing_node_group = tree
    nodes = tree.nodes
    links = tree.links

    # --- Render Layers ---
    rl = nodes.new('CompositorNodeRLayers')
    rl.location = (0, 0)

    # --- Bloom (subtle glow on bright spots like gold, fire) ---
    # Blender 5.0: Glare settings are node inputs
    glare = nodes.new('CompositorNodeGlare')
    glare.location = (300, 0)
    glare.inputs['Type'].default_value = 'Bloom'
    glare.inputs['Quality'].default_value = 'High'
    glare.inputs['Threshold'].default_value = 0.82
    glare.inputs['Size'].default_value = 0.6
    glare.inputs['Strength'].default_value = 0.8
    links.new(rl.outputs['Image'], glare.inputs['Image'])

    # --- Brightness/Contrast for punch ---
    bc = nodes.new('CompositorNodeBrightContrast')
    bc.location = (550, 0)
    bc.inputs['Brightness'].default_value = -50
    bc.inputs['Contrast'].default_value = 25
    links.new(glare.outputs['Image'], bc.inputs['Image'])

    # --- Subtle warm tint via HueSat ---
    hsv = nodes.new('CompositorNodeHueSat')
    hsv.location = (800, 0)
    hsv.inputs['Hue'].default_value = 0.503      # Warm shift
    hsv.inputs['Saturation'].default_value = 1.22  # Strong saturation boost
    hsv.inputs['Value'].default_value = 0.55       # Darken overall
    links.new(bc.outputs['Image'], hsv.inputs['Image'])

    # --- Alpha: pass through from render ---
    set_alpha = nodes.new('CompositorNodeSetAlpha')
    set_alpha.location = (1050, 0)
    links.new(hsv.outputs['Image'], set_alpha.inputs['Image'])
    links.new(rl.outputs['Alpha'], set_alpha.inputs['Alpha'])

    # --- Output (Blender 5.0 uses NodeGroupOutput) ---
    out = nodes.new('NodeGroupOutput')
    out.location = (1300, 0)
    links.new(set_alpha.outputs['Image'], out.inputs[0])
