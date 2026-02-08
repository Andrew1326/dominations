"""
CLI entry point — render a single building for a given age and optional nation.

Usage:
  blender --background --python blender/render_building.py -- --age stone --building townCenter
  blender --background --python blender/render_building.py -- --age medieval --building townCenter --nation romans
  blender --background --python blender/render_building.py -- --age medieval --building townCenter --output /tmp/test.png
"""

import sys
import os
import argparse

# Ensure blender/ is on the path so lib/ imports work
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from lib.scene_setup import setup_scene, setup_camera, setup_lighting, setup_compositing, add_shadow_catcher
from lib.materials import init_materials
from lib.nation_palettes import apply_nation_palette

# Registry of building builder functions
# Key: "buildingName" for generic, "buildingName:nation" for nation-specific
BUILDING_BUILDERS = {}


def _load_builders():
    """Lazily import all building modules."""
    from buildings.town_center import build_town_center
    BUILDING_BUILDERS['townCenter'] = build_town_center

    # Nation-specific town centers with unique architecture
    from buildings import town_center_nations
    for nation, builder in town_center_nations.NATION_BUILDERS.items():
        BUILDING_BUILDERS[f'townCenter:{nation}'] = builder

    from buildings.house import build_house
    BUILDING_BUILDERS['house'] = build_house
    from buildings.farm import build_farm
    BUILDING_BUILDERS['farm'] = build_farm
    from buildings.barracks import build_barracks
    BUILDING_BUILDERS['barracks'] = build_barracks
    from buildings.tower import build_tower
    BUILDING_BUILDERS['tower'] = build_tower
    from buildings.wall import build_wall
    BUILDING_BUILDERS['wall'] = build_wall
    from buildings.storage import build_storage
    BUILDING_BUILDERS['storage'] = build_storage
    from buildings.gold_mine import build_gold_mine
    BUILDING_BUILDERS['goldMine'] = build_gold_mine
    from buildings.temple import build_temple
    BUILDING_BUILDERS['temple'] = build_temple
    from buildings.market import build_market
    BUILDING_BUILDERS['market'] = build_market


def parse_args():
    # Everything after "--" in blender's argv
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Render a building sprite.")
    parser.add_argument("--age", default="medieval",
                        help="Age: stone, bronze, iron, classical, medieval, gunpowder, enlightenment, industrial, modern, digital")
    parser.add_argument("--building", required=True,
                        help="Building type (camelCase): townCenter, house, farm, etc.")
    parser.add_argument("--nation", default=None,
                        help="Nation for color palette: romans, greeks, egyptians, chinese, japanese, vikings, british, persians")
    parser.add_argument("--output", default=None,
                        help="Output path. Default: client/public/assets/buildings/{age}/{building}.png")
    parser.add_argument("--resolution", type=int, default=1024,
                        help="Image resolution (square). Default: 1024")
    parser.add_argument("--samples", type=int, default=512,
                        help="Cycles samples. Default: 512")
    return parser.parse_args(argv)


def main():
    args = parse_args()
    _load_builders()

    if args.building not in BUILDING_BUILDERS:
        available = ", ".join(BUILDING_BUILDERS.keys())
        print(f"ERROR: Unknown building '{args.building}'. Available: {available}")
        sys.exit(1)

    # Determine output path
    if args.output:
        output = args.output
    else:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if args.nation:
            output = os.path.join(project_root, "client", "public", "assets", "buildings",
                                  args.age, args.nation, f"{args.building}.png")
        else:
            output = os.path.join(project_root, "client", "public", "assets", "buildings",
                                  args.age, f"{args.building}.png")
    os.makedirs(os.path.dirname(output), exist_ok=True)

    print(f"=== Rendering {args.building} | age={args.age} | nation={args.nation or 'default'} ===")

    # Setup
    scene = setup_scene(resolution=args.resolution, samples=args.samples)
    materials = init_materials(age=args.age)

    # Build — check for nation-specific builder first, fall back to generic + palette
    print("Building geometry...")
    nation_key = f"{args.building}:{args.nation}" if args.nation else None
    if nation_key and nation_key in BUILDING_BUILDERS:
        # Nation-specific builder with unique architecture
        apply_nation_palette(materials, args.nation)
        builder = BUILDING_BUILDERS[nation_key]
        builder(materials, age=args.age)
    else:
        # Generic builder with optional palette swap
        if args.nation:
            apply_nation_palette(materials, args.nation)
        builder = BUILDING_BUILDERS[args.building]
        builder(materials, age=args.age)

    # Camera, lighting & post-processing
    print("Setting up camera, lights, and compositing...")
    setup_lighting()
    add_shadow_catcher()
    setup_camera()
    setup_compositing()

    # Render
    scene.render.filepath = output
    print(f"Rendering (Cycles {scene.cycles.samples} samples)...")
    bpy.ops.render.render(write_still=True)
    print(f"Done! {output}")


if __name__ == "__main__":
    main()
