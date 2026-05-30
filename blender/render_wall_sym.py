"""
Render the tileable wall with LEFT-RIGHT SYMMETRIC lighting.

The wall is drawn as one sprite per tile and the perpendicular (col-axis)
orientation is the same sprite mirrored (flipX). A directional key light bakes a
left/right brightness gradient into the art, so the mirrored copy disagrees with
its neighbour at every seam — the run "staircases". Lighting that is symmetric
about the screen-vertical (i.e. about the world X=Y plane, the camera azimuth)
makes the mirror identical, so a run reads as one continuous, even wall.

Usage:
  blender --background --python blender/render_wall_sym.py -- --output /tmp/wall.png
"""

import sys, os, math, argparse
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from lib.scene_setup import setup_scene, setup_camera, setup_compositing
from lib.materials import init_materials
from lib.nation_palettes import apply_nation_palette
from buildings.wall import build_simple_wall, build_corner_tower

BUILDERS = {'wallTile': build_simple_wall, 'wallCorner': build_corner_tower}


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--age", default="medieval")
    p.add_argument("--nation", default="romans")
    p.add_argument("--building", default="wallTile", choices=list(BUILDERS.keys()))
    p.add_argument("--output", required=True)
    p.add_argument("--resolution", type=int, default=512)
    p.add_argument("--samples", type=int, default=256)
    return p.parse_args(argv)


def setup_symmetric_lighting():
    """Lighting symmetric about the camera azimuth (world X=Y plane), so the
    sprite looks identical when mirrored left-right."""
    # Top-down sun: hits the top/merlons evenly, no left/right bias.
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 12))
    top = bpy.context.active_object
    top.name = "TopSun"
    top.data.energy = 1.4
    top.data.angle = 0.05
    top.data.color = (1.0, 0.97, 0.9)
    top.rotation_euler = (0, 0, 0)  # straight down

    # Front key from the camera azimuth (equal +X, -Y) — symmetric under X<->Y,
    # so it lights both long faces (the one seen at 0 deg and at 90 deg) equally.
    bpy.ops.object.light_add(type='AREA', location=(6, -6, 6))
    key = bpy.context.active_object
    key.name = "FrontKey"
    key.data.energy = 2.2
    key.data.size = 10
    key.data.color = (1.0, 0.96, 0.9)
    # point at origin from (6,-6,6): symmetric about X=Y
    key.rotation_euler = (math.radians(48), 0, math.radians(45))

    # Soft ambient sky for fill
    world = bpy.data.worlds['World'] if 'World' in bpy.data.worlds else bpy.data.worlds.new('World')
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs[0].default_value = (0.55, 0.6, 0.7, 1.0)
        bg.inputs[1].default_value = 0.6


def main():
    args = parse_args()
    scene = setup_scene(resolution=args.resolution, samples=args.samples)
    materials = init_materials(age=args.age)
    if args.nation:
        apply_nation_palette(materials, args.nation)
    BUILDERS[args.building](materials, age=args.age)

    # building-only: strip ground
    for obj in [o for o in bpy.data.objects if o.name == "Ground" or o.name.startswith("Ground.")]:
        bpy.data.objects.remove(obj, do_unlink=True)

    setup_symmetric_lighting()
    setup_camera()
    setup_compositing()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    scene.render.filepath = args.output
    bpy.ops.render.render(write_still=True)
    print(f"Done! {args.output}")


if __name__ == "__main__":
    main()
