---
name: blender-render-automation
description: >-
  Automate Blender rendering from the command line. Use when the user wants to
  set up renders, batch render scenes, configure Cycles or EEVEE, set up
  cameras and lights, render animations, create materials and shaders, or
  build a render pipeline with Blender Python scripting.
license: Apache-2.0
compatibility: >-
  Requires Blender 3.0+. GPU rendering requires compatible CUDA, OptiX, or
  HIP device. Run: blender --background --python script.py
metadata:
  author: terminal-skills
  version: "1.0.0"
  category: automation
  tags: ["blender", "rendering", "cycles", "eevee", "3d"]
---

# Blender Render Automation

## Overview

Automate Blender's rendering pipeline from the terminal. Configure render engines (Cycles/EEVEE), set up cameras and lighting, create materials, and batch render scenes or animations — all headlessly via Python scripts.

## Instructions

### 1. Configure the render engine

```python
import bpy

scene = bpy.context.scene

# --- Cycles (ray-traced, production quality) ---
scene.render.engine = 'CYCLES'
cycles = scene.cycles
cycles.samples = 256
cycles.use_denoising = True
cycles.denoiser = 'OPENIMAGEDENOISE'

# GPU rendering
cycles.device = 'GPU'
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'CUDA'  # or 'OPTIX', 'HIP'
prefs.get_devices()
for device in prefs.devices:
    device.use = True

# --- EEVEE (fast, real-time) ---
scene.render.engine = 'BLENDER_EEVEE_NEXT'
eevee = scene.eevee
eevee.taa_render_samples = 64
```

### 2. Set output resolution and format

```python
import bpy

render = bpy.context.scene.render

# Resolution
render.resolution_x = 1920
render.resolution_y = 1080
render.resolution_percentage = 100

# Output format
render.image_settings.file_format = 'PNG'  # PNG, JPEG, OPEN_EXR, TIFF
render.image_settings.color_mode = 'RGBA'
render.image_settings.compression = 15

# For JPEG
# render.image_settings.file_format = 'JPEG'
# render.image_settings.quality = 90

# For EXR (linear, 32-bit)
# render.image_settings.file_format = 'OPEN_EXR'
# render.image_settings.color_depth = '32'

# Film settings
render.film_transparent = True  # transparent background
```

### 3. Set up cameras

```python
import bpy
from mathutils import Vector
import math

# Add a camera
bpy.ops.object.camera_add(location=(7, -6, 5))
camera = bpy.context.active_object
camera.name = "MainCamera"

# Point camera at a target
target = Vector((0, 0, 1))
direction = target - camera.location
rot_quat = direction.to_track_quat('-Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

# Camera settings
cam_data = camera.data
cam_data.lens = 50               # focal length in mm
cam_data.clip_start = 0.1
cam_data.clip_end = 1000
cam_data.sensor_width = 36       # full-frame sensor

# Depth of field
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = 5
cam_data.dof.aperture_fstop = 2.8

# Set as active camera
bpy.context.scene.camera = camera

# Track-to constraint (auto-aim at object)
track = camera.constraints.new(type='TRACK_TO')
track.target = bpy.data.objects["MySubject"]
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'
```

### 4. Set up lighting

```python
import bpy

# Point light
bpy.ops.object.light_add(type='POINT', location=(3, -3, 5))
point = bpy.context.active_object.data
point.energy = 1000      # watts
point.color = (1, 0.95, 0.9)
point.shadow_soft_size = 0.5

# Sun light
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
sun = bpy.context.active_object.data
sun.energy = 3
sun.angle = 0.05  # sun angular diameter (sharpness)

# Area light
bpy.ops.object.light_add(type='AREA', location=(0, -4, 3))
area = bpy.context.active_object
area.data.energy = 500
area.data.size = 2
area.data.shape = 'RECTANGLE'
area.data.size_y = 1

# HDRI environment lighting
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

bg = nodes.new('ShaderNodeBackground')
env = nodes.new('ShaderNodeTexEnvironment')
output = nodes.new('ShaderNodeOutputWorld')
env.image = bpy.data.images.load("/path/to/hdri.hdr")
links.new(env.outputs['Color'], bg.inputs['Color'])
links.new(bg.outputs['Background'], output.inputs['Surface'])
bg.inputs['Strength'].default_value = 1.0
```

### 5. Create materials and shaders

```python
import bpy

def create_pbr_material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")

    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat

def create_textured_material(name, texture_path):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")

    tex = nodes.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(texture_path)
    links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    return mat

# Glass material
def create_glass_material(name, color=(1, 1, 1), ior=1.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Transmission Weight'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.0
    bsdf.inputs['IOR'].default_value = ior
    return mat

# Assign material to object
obj = bpy.data.objects["MyCube"]
mat = create_pbr_material("BlueMetal", (0.1, 0.3, 0.8), metallic=1.0, roughness=0.2)
obj.data.materials.append(mat)
```

### 6. Render a single frame

```python
import bpy

scene = bpy.context.scene
scene.render.filepath = "/tmp/render_output.png"
bpy.ops.render.render(write_still=True)
print(f"Rendered to: {scene.render.filepath}")
```

From the command line:
```bash
blender scene.blend --background --python render.py
# Or render directly without a script:
blender scene.blend --background --render-output /tmp/frame_ --render-frame 1
```

### 7. Render an animation

```python
import bpy

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 250
scene.frame_step = 1
scene.render.fps = 24

# Output as image sequence
scene.render.filepath = "/tmp/anim/frame_"
scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(animation=True)

# Or output as video
scene.render.filepath = "/tmp/animation.mp4"
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
bpy.ops.render.render(animation=True)
```

From the command line:
```bash
blender scene.blend --background --render-output /tmp/anim/frame_ --render-anim
# Render specific frame range
blender scene.blend --background --frame-start 1 --frame-end 100 --render-anim
```

### 8. Batch render multiple scenes or cameras

```python
import bpy
import os

output_dir = "/tmp/renders"
os.makedirs(output_dir, exist_ok=True)

scene = bpy.context.scene
cameras = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']

for cam in cameras:
    scene.camera = cam
    filepath = os.path.join(output_dir, f"{cam.name}.png")
    scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {cam.name} -> {filepath}")
```

## Examples

### Example 1: Product shot render pipeline

**User request:** "Set up a clean studio render for a 3D product"

```python
import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import the product model
bpy.ops.wm.obj_import(filepath="/path/to/product.obj")
product = bpy.context.selected_objects[0]
product.location = (0, 0, 0)

# Studio backdrop (large curved plane)
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
backdrop = bpy.context.active_object
backdrop.name = "Backdrop"

# White backdrop material
mat_bg = bpy.data.materials.new("Backdrop")
mat_bg.use_nodes = True
bsdf = mat_bg.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.9, 0.9, 0.9, 1)
bsdf.inputs['Roughness'].default_value = 0.8
backdrop.data.materials.append(mat_bg)

# Three-point lighting
# Key light
bpy.ops.object.light_add(type='AREA', location=(4, -3, 5))
key = bpy.context.active_object
key.data.energy = 800
key.data.size = 3
key.rotation_euler = (math.radians(45), 0, math.radians(30))

# Fill light
bpy.ops.object.light_add(type='AREA', location=(-3, -2, 3))
fill = bpy.context.active_object
fill.data.energy = 300
fill.data.size = 4

# Rim light
bpy.ops.object.light_add(type='AREA', location=(0, 4, 4))
rim = bpy.context.active_object
rim.data.energy = 500
rim.data.size = 2

# Camera
bpy.ops.object.camera_add(location=(5, -5, 3))
cam = bpy.context.active_object
track = cam.constraints.new(type='TRACK_TO')
track.target = product

scene = bpy.context.scene
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.render.resolution_x = 2000
scene.render.resolution_y = 2000
scene.render.film_transparent = True
scene.render.filepath = "/tmp/product_render.png"
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'

bpy.ops.render.render(write_still=True)
```

### Example 2: Batch render turntable animation

**User request:** "Render a 360-degree turntable of my model — 36 frames"

```python
import bpy
import math
import os

output_dir = "/tmp/turntable"
os.makedirs(output_dir, exist_ok=True)

obj = bpy.data.objects["MyModel"]
frames = 36
scene = bpy.context.scene

# Set up camera on circular path
bpy.ops.object.camera_add(location=(5, 0, 2))
cam = bpy.context.active_object
scene.camera = cam
track = cam.constraints.new(type='TRACK_TO')
track.target = obj

scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.resolution_x = 1080
scene.render.resolution_y = 1080

for i in range(frames):
    angle = (2 * math.pi * i) / frames
    cam.location.x = 5 * math.cos(angle)
    cam.location.y = 5 * math.sin(angle)

    scene.render.filepath = os.path.join(output_dir, f"turn_{i:03d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"Frame {i+1}/{frames}")
```

Then combine to video: `ffmpeg -framerate 24 -i /tmp/turntable/turn_%03d.png -c:v libx264 -pix_fmt yuv420p turntable.mp4`

## Guidelines

- Always use `--background` for headless rendering. Without it, Blender opens the GUI.
- Cycles is physically accurate but slow. EEVEE is fast but approximate. Use EEVEE for previews, Cycles for final output.
- Enable denoising (`cycles.use_denoising = True`) to get clean results with fewer samples — 128-256 samples with denoising often matches 1000+ without.
- For GPU rendering, call `prefs.get_devices()` after setting `compute_device_type` — Blender won't detect GPUs otherwise.
- Render animations as image sequences (PNG), not directly to video. If a render crashes at frame 150, you keep frames 1-149. Composite to video afterwards with ffmpeg.
- Use `film_transparent = True` and RGBA color mode for renders that need transparent backgrounds (product shots, compositing).
- HDRI environment maps produce the most realistic lighting with minimal setup. Free HDRIs are available from Poly Haven.
- The Principled BSDF shader handles most materials — adjust Base Color, Metallic, Roughness, and Transmission for metals, plastics, glass, etc.
- For batch rendering across .blend files, loop with `bpy.ops.wm.open_mainfile()` and render each scene.
- Monitor render progress via terminal output — Blender prints per-tile/sample progress to stdout.
