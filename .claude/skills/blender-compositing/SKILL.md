---
name: blender-compositing
description: >-
  Automate Blender compositing and post-processing with Python. Use when the
  user wants to set up compositor nodes, add post-processing effects, color
  correct renders, combine render passes, apply blur or glare, key green
  screens, create node-based VFX pipelines, or script the Blender compositor.
license: Apache-2.0
compatibility: >-
  Requires Blender 3.0+. Run: blender --background --python script.py
metadata:
  author: terminal-skills
  version: "1.0.0"
  category: automation
  tags: ["blender", "compositing", "vfx", "post-processing", "nodes"]
---

# Blender Compositing

## Overview

Build node-based compositing pipelines in Blender using Python. Set up render passes, add post-processing effects (blur, glare, color correction), combine layers, key green screens, and output final composited images — all scriptable from the terminal.

## Instructions

### 1. Enable compositing and set up the node tree

```python
import bpy

scene = bpy.context.scene
scene.use_nodes = True

tree = scene.node_tree
nodes = tree.nodes
links = tree.links

# Clear default nodes
nodes.clear()

# Every compositor needs at minimum: Render Layers → Composite
rl_node = nodes.new('CompositorNodeRLayers')
rl_node.location = (0, 0)

comp_node = nodes.new('CompositorNodeComposite')
comp_node.location = (600, 0)

links.new(rl_node.outputs['Image'], comp_node.inputs['Image'])
```

### 2. Add a Viewer node for preview

```python
import bpy

tree = bpy.context.scene.node_tree
nodes = tree.nodes

viewer = nodes.new('CompositorNodeViewer')
viewer.location = (600, -200)

# Connect to see the result
rl = nodes.get('Render Layers') or nodes['Render Layers']
tree.links.new(rl.outputs['Image'], viewer.inputs['Image'])
```

### 3. Color correction nodes

```python
import bpy

tree = bpy.context.scene.node_tree
nodes = tree.nodes
links = tree.links

# Brightness/Contrast
bc = nodes.new('CompositorNodeBrightContrast')
bc.location = (300, 0)
bc.inputs['Bright'].default_value = 10
bc.inputs['Contrast'].default_value = 20

# Hue/Saturation/Value
hsv = nodes.new('CompositorNodeHueSat')
hsv.location = (300, -200)
hsv.inputs['Hue'].default_value = 0.5       # 0.5 = no change
hsv.inputs['Saturation'].default_value = 1.2
hsv.inputs['Value'].default_value = 1.0

# Color Balance (Lift/Gamma/Gain)
cb = nodes.new('CompositorNodeColorBalance')
cb.location = (300, -400)
cb.correction_method = 'LIFT_GAMMA_GAIN'
cb.lift = (0.95, 0.95, 1.0)    # cool shadows
cb.gamma = (1.0, 1.0, 1.0)
cb.gain = (1.1, 1.05, 1.0)     # warm highlights

# Color Curves
curves = nodes.new('CompositorNodeCurveRGB')
curves.location = (300, -600)
# Access curve data via curves.mapping

# Gamma
gamma = nodes.new('CompositorNodeGamma')
gamma.location = (300, -800)
gamma.inputs['Gamma'].default_value = 1.2
```

### 4. Filter and effect nodes

```python
import bpy

tree = bpy.context.scene.node_tree
nodes = tree.nodes

# Blur
blur = nodes.new('CompositorNodeBlur')
blur.location = (300, 0)
blur.filter_type = 'GAUSS'  # FLAT, TENT, QUAD, CUBIC, GAUSS, FAST_GAUSS, CATROM, MITCH
blur.size_x = 10
blur.size_y = 10
blur.use_relative = False

# Directional Blur
dblur = nodes.new('CompositorNodeDBlur')
dblur.location = (300, -200)
dblur.iterations = 3
dblur.angle = 0.0
dblur.zoom = 0.1

# Glare (bloom, streaks, fog glow)
glare = nodes.new('CompositorNodeGlare')
glare.location = (300, -400)
glare.glare_type = 'BLOOM'  # BLOOM, STREAKS, FOG_GLOW, SIMPLE_STAR, GHOSTS
glare.threshold = 0.8
glare.size = 6
glare.quality = 'HIGH'  # LOW, MEDIUM, HIGH

# Sharpen (via Filter node)
sharpen = nodes.new('CompositorNodeFilter')
sharpen.location = (300, -600)
sharpen.filter_type = 'SHARPEN'  # SOFTEN, SHARPEN, LAPLACE, SOBEL, PREWITT, KIRSCH, SHADOW

# Denoise
denoise = nodes.new('CompositorNodeDenoise')
denoise.location = (300, -800)
```

### 5. Combine render passes

```python
import bpy

scene = bpy.context.scene
scene.use_nodes = True
tree = scene.node_tree
nodes = tree.nodes
links = tree.links
nodes.clear()

# Enable render passes on the view layer
view_layer = bpy.context.view_layer
view_layer.use_pass_diffuse_color = True
view_layer.use_pass_glossy_direct = True
view_layer.use_pass_shadow = True
view_layer.use_pass_ambient_occlusion = True
view_layer.use_pass_emit = True
view_layer.use_pass_z = True

# Render Layers node exposes enabled passes
rl = nodes.new('CompositorNodeRLayers')
rl.location = (0, 0)

# Mix passes together
mix = nodes.new('CompositorNodeMixRGB')
mix.location = (400, 0)
mix.blend_type = 'MULTIPLY'
mix.inputs['Fac'].default_value = 0.5

links.new(rl.outputs['DiffCol'], mix.inputs[1])
links.new(rl.outputs['AO'], mix.inputs[2])

comp = nodes.new('CompositorNodeComposite')
comp.location = (700, 0)
links.new(mix.outputs['Image'], comp.inputs['Image'])
```

### 6. Alpha compositing and keying

```python
import bpy

tree = bpy.context.scene.node_tree
nodes = tree.nodes
links = tree.links

# Alpha Over — composite foreground over background
alpha_over = nodes.new('CompositorNodeAlphaOver')
alpha_over.location = (400, 0)
alpha_over.inputs['Fac'].default_value = 1.0
# Connect: background → input 1, foreground (with alpha) → input 2

# Keying node — green screen removal
keying = nodes.new('CompositorNodeKeying')
keying.location = (300, -300)
keying.inputs['Key Color'].default_value = (0, 1, 0, 1)  # green
keying.clip_black = 0.1
keying.clip_white = 0.9

# Color Spill — remove green fringing after keying
spill = nodes.new('CompositorNodeColorSpill')
spill.location = (500, -300)
spill.channel = 'G'
spill.limit_method = 'AVERAGE'

# Set Alpha node
set_alpha = nodes.new('CompositorNodeSetAlpha')
set_alpha.location = (400, -500)
set_alpha.mode = 'APPLY'  # APPLY, REPLACE_ALPHA
```

### 7. File output for multi-layer EXR

```python
import bpy

tree = bpy.context.scene.node_tree
nodes = tree.nodes
links = tree.links

# File Output node — save multiple passes to separate files
file_out = nodes.new('CompositorNodeOutputFile')
file_out.location = (800, -200)
file_out.base_path = "/tmp/comp_output/"
file_out.format.file_format = 'OPEN_EXR_MULTILAYER'

# Add input sockets for each pass
file_out.file_slots.new("Diffuse")
file_out.file_slots.new("AO")
file_out.file_slots.new("Shadow")

rl = nodes.get('Render Layers')
links.new(rl.outputs['DiffCol'], file_out.inputs['Diffuse'])
links.new(rl.outputs['AO'], file_out.inputs['AO'])
links.new(rl.outputs['Shadow'], file_out.inputs['Shadow'])

# For separate files per pass
file_out_separate = nodes.new('CompositorNodeOutputFile')
file_out_separate.location = (800, -500)
file_out_separate.base_path = "/tmp/passes/"
file_out_separate.format.file_format = 'PNG'
file_out_separate.file_slots[0].path = "beauty_"
file_out_separate.file_slots.new("depth_")
```

### 8. Depth-based effects (DOF, fog, mist)

```python
import bpy

scene = bpy.context.scene
scene.use_nodes = True
tree = scene.node_tree
nodes = tree.nodes
links = tree.links

# Enable Z pass
bpy.context.view_layer.use_pass_z = True

rl = nodes['Render Layers']

# Normalize the depth
normalize = nodes.new('CompositorNodeNormalize')
normalize.location = (300, -200)
links.new(rl.outputs['Depth'], normalize.inputs['Value'])

# Use depth as a factor for fog
mix = nodes.new('CompositorNodeMixRGB')
mix.location = (500, 0)
mix.blend_type = 'MIX'

# Fog color
fog_color = nodes.new('CompositorNodeRGB')
fog_color.location = (300, -400)
fog_color.outputs['RGBA'].default_value = (0.7, 0.75, 0.85, 1.0)

links.new(normalize.outputs['Value'], mix.inputs['Fac'])
links.new(rl.outputs['Image'], mix.inputs[1])
links.new(fog_color.outputs['RGBA'], mix.inputs[2])

comp = nodes['Composite']
links.new(mix.outputs['Image'], comp.inputs['Image'])
```

## Examples

### Example 1: Cinematic color grade pipeline

**User request:** "Add a cinematic look to my render — warm highlights, cool shadows, bloom, and vignette"

```python
import bpy

scene = bpy.context.scene
scene.use_nodes = True
tree = scene.node_tree
nodes = tree.nodes
links = tree.links
nodes.clear()

# Input
rl = nodes.new('CompositorNodeRLayers')
rl.location = (0, 0)

# Color Balance — warm highlights, cool shadows
cb = nodes.new('CompositorNodeColorBalance')
cb.location = (250, 0)
cb.correction_method = 'LIFT_GAMMA_GAIN'
cb.lift = (0.92, 0.93, 1.0)
cb.gamma = (1.0, 0.98, 0.95)
cb.gain = (1.15, 1.08, 0.95)
links.new(rl.outputs['Image'], cb.inputs['Image'])

# Bloom
glare = nodes.new('CompositorNodeGlare')
glare.location = (500, 0)
glare.glare_type = 'BLOOM'
glare.threshold = 0.7
glare.size = 7
glare.quality = 'HIGH'
links.new(cb.outputs['Image'], glare.inputs['Image'])

# Vignette using Ellipse Mask + Blur
ellipse = nodes.new('CompositorNodeEllipseMask')
ellipse.location = (300, -400)
ellipse.width = 0.85
ellipse.height = 0.85

blur_mask = nodes.new('CompositorNodeBlur')
blur_mask.location = (500, -400)
blur_mask.filter_type = 'GAUSS'
blur_mask.size_x = 200
blur_mask.size_y = 200
links.new(ellipse.outputs['Mask'], blur_mask.inputs['Image'])

mix_vig = nodes.new('CompositorNodeMixRGB')
mix_vig.location = (750, 0)
mix_vig.blend_type = 'MULTIPLY'
mix_vig.inputs['Fac'].default_value = 0.6
links.new(glare.outputs['Image'], mix_vig.inputs[1])
links.new(blur_mask.outputs['Image'], mix_vig.inputs[2])

# Output
comp = nodes.new('CompositorNodeComposite')
comp.location = (1000, 0)
links.new(mix_vig.outputs['Image'], comp.inputs['Image'])

viewer = nodes.new('CompositorNodeViewer')
viewer.location = (1000, -200)
links.new(mix_vig.outputs['Image'], viewer.inputs['Image'])
```

Run: `blender scene.blend --background --python grade.py --render-frame 1`

### Example 2: Green screen composite

**User request:** "Composite my 3D character over a photo background, with the render using a green background"

```python
import bpy

scene = bpy.context.scene
scene.use_nodes = True
tree = scene.node_tree
nodes = tree.nodes
links = tree.links
nodes.clear()

# 3D render input
rl = nodes.new('CompositorNodeRLayers')
rl.location = (0, 0)

# Background photo
bg_image = nodes.new('CompositorNodeImage')
bg_image.location = (0, -400)
bg_image.image = bpy.data.images.load("/path/to/background.jpg")

# Use film transparent instead of keying if possible
scene.render.film_transparent = True

# Alpha Over — place render on top of background
alpha_over = nodes.new('CompositorNodeAlphaOver')
alpha_over.location = (400, -100)
links.new(bg_image.outputs['Image'], alpha_over.inputs[1])
links.new(rl.outputs['Image'], alpha_over.inputs[2])

# Color match — adjust render to match background tone
hsv = nodes.new('CompositorNodeHueSat')
hsv.location = (600, -100)
hsv.inputs['Saturation'].default_value = 0.95
hsv.inputs['Value'].default_value = 0.9
links.new(alpha_over.outputs['Image'], hsv.inputs['Image'])

# Output
comp = nodes.new('CompositorNodeComposite')
comp.location = (850, -100)
links.new(hsv.outputs['Image'], comp.inputs['Image'])
```

## Guidelines

- Always set `scene.use_nodes = True` before accessing the compositor node tree.
- Node positions (`node.location`) are for visual layout only — they don't affect functionality but make the node tree readable if opened in the GUI.
- Connect Render Layers → Composite at minimum. Without a Composite node, nothing renders.
- Use `CompositorNodeOutputFile` to save multiple passes to disk in a single render. This avoids rendering the scene multiple times.
- Enable render passes on the View Layer before they appear as outputs on the Render Layers node.
- For green screen work, prefer `film_transparent = True` with Alpha Over instead of Keying when you control the 3D scene — it's cleaner than chroma keying.
- Chain color corrections in order: exposure/levels first, then color balance, then creative grading. This mirrors professional compositing workflows.
- The Denoise node works best when placed right after the Render Layers node, before any color adjustments.
- Use `OPEN_EXR_MULTILAYER` format on the File Output node to save all passes in a single file for later compositing.
- Compositor runs automatically on render. To force a compositor-only update without re-rendering, use `bpy.ops.render.render(write_still=True)` with cached render results.
