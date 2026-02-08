"""
Batch render — renders all registered buildings across all ages.
Optionally renders nation variants too.

Usage:
  blender --background --python blender/render_all.py
  blender --background --python blender/render_all.py -- --ages stone,medieval
  blender --background --python blender/render_all.py -- --with-nations
  blender --background --python blender/render_all.py -- --buildings townCenter --ages medieval --with-nations
"""

import sys
import os
import argparse
import subprocess

# Project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENDER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "render_building.py")

ALL_AGES = [
    'stone', 'bronze', 'iron', 'classical', 'medieval',
    'gunpowder', 'enlightenment', 'industrial', 'modern', 'digital',
]

ALL_NATIONS = [
    'romans', 'greeks', 'egyptians', 'chinese',
    'japanese', 'vikings', 'british', 'persians',
]

# Buildings available to render (must have a builder registered in render_building.py)
AVAILABLE_BUILDINGS = ['townCenter', 'house', 'farm', 'barracks', 'tower', 'wall', 'storage', 'goldMine', 'temple', 'market']


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Batch render buildings.")
    parser.add_argument("--ages", default=None, help="Comma-separated ages to render. Default: all")
    parser.add_argument("--buildings", default=None, help="Comma-separated buildings. Default: all available")
    parser.add_argument("--with-nations", action="store_true", help="Also render nation color variants")
    parser.add_argument("--resolution", type=int, default=512, help="Resolution. Default: 512")
    parser.add_argument("--samples", type=int, default=128, help="Cycles samples (lower for batch). Default: 128")
    return parser.parse_args(argv)


def main():
    args = parse_args()

    ages = args.ages.split(",") if args.ages else ALL_AGES
    buildings = args.buildings.split(",") if args.buildings else AVAILABLE_BUILDINGS

    nations = ALL_NATIONS if args.with_nations else [None]

    total = len(ages) * len(buildings) * len(nations)
    count = 0

    print(f"=== Batch render: {len(buildings)} buildings × {len(ages)} ages × {len(nations)} nation variants = {total} renders ===")

    for age in ages:
        for building in buildings:
            for nation in nations:
                count += 1
                nation_str = nation or "default"
                print(f"\n[{count}/{total}] {building} | age={age} | nation={nation_str}")

                cmd = [
                    "blender", "--background", "--python", RENDER_SCRIPT, "--",
                    "--age", age,
                    "--building", building,
                    "--resolution", str(args.resolution),
                    "--samples", str(args.samples),
                ]
                if nation:
                    cmd.extend(["--nation", nation])

                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"  ERROR: {result.stderr[-500:] if result.stderr else 'unknown error'}")
                else:
                    # Extract the "Done!" line from output
                    for line in result.stdout.split("\n"):
                        if "Done!" in line:
                            print(f"  {line.strip()}")

    print(f"\n=== Batch complete: {count} renders ===")


if __name__ == "__main__":
    main()
