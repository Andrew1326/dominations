"""
CLI entry point — render a unit's animation frames as a sprite sheet.

Renders each frame of a chosen animation (move/shoot) from a chosen direction,
then composites all frames into a horizontal sprite sheet PNG.

Usage:
  blender --background --python blender/render_unit.py -- --unit rangedShooter --anim move
  blender --background --python blender/render_unit.py -- --unit rangedShooter --anim shoot
  blender --background --python blender/render_unit.py -- --unit rangedShooter --anim move --directions 8
  blender --background --python blender/render_unit.py -- --unit rangedShooter --anim shoot --output /tmp/test_sheet.png

Output: A sprite sheet with rows = directions, columns = frames.
  Row 0 = South (toward camera), Row 1 = SW, Row 2 = West, ... (clockwise)

Also generates a JSON metadata file alongside the PNG.
"""

import sys
import os
import argparse
import json
import math

sys.path.insert(0, os.path.dirname(__file__))

import bpy
from lib.scene_setup import setup_scene, setup_camera, setup_lighting, setup_compositing, add_shadow_catcher

# Registry of unit builders
UNIT_BUILDERS = {}


def _load_builders():
    from units.ranged_shooter import build_ranged_shooter
    UNIT_BUILDERS['rangedShooter'] = build_ranged_shooter


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Render unit animation sprite sheet.")
    parser.add_argument("--unit", required=True, help="Unit type: rangedShooter")
    parser.add_argument("--anim", required=True, help="Animation: move, shoot")
    parser.add_argument("--directions", type=int, default=8,
                        help="Number of rotation directions (4 or 8). Default: 8")
    parser.add_argument("--frame-size", type=int, default=128,
                        help="Size of each frame in pixels (square). Default: 128")
    parser.add_argument("--samples", type=int, default=64,
                        help="Cycles samples per frame. Default: 64")
    parser.add_argument("--output", default=None,
                        help="Output path. Default: client/public/assets/units/{unit}_{anim}.png")
    parser.add_argument("--blend-output", default=None,
                        help="Save .blend file for inspection. Optional.")
    return parser.parse_args(argv)


ANIM_CONFIG = {
    'move': {
        'action_name': 'ArcherWalk',
        'frame_start': 1,
        'frame_end': 24,
        'frame_step': 3,  # every 3rd frame → 8 frames
    },
    'shoot': {
        'action_name': 'ArcherShoot',
        'frame_start': 1,
        'frame_end': 30,
        'frame_step': 3,  # every 3rd frame → 10 frames
    },
}


def _activate_animation(arm_obj, anim_name):
    """Activate the right NLA track for the chosen animation."""
    config = ANIM_CONFIG[anim_name]

    # Mute all NLA tracks
    for track in arm_obj.animation_data.nla_tracks:
        track.mute = True

    # Find and unmute the target track
    track_map = {'move': 'Walk', 'shoot': 'Shoot'}
    target_track = track_map[anim_name]
    for track in arm_obj.animation_data.nla_tracks:
        if track.name == target_track:
            track.mute = False
            break

    # Ensure no active action overrides NLA
    arm_obj.animation_data.action = None

    return config


def _render_frames(scene, arm_obj, config, direction_deg, frame_size, tmp_dir):
    """Render all frames for one direction. Returns list of frame file paths."""
    frames = []
    frame_range = range(config['frame_start'], config['frame_end'] + 1, config['frame_step'])

    for i, frame in enumerate(frame_range):
        scene.frame_set(frame)
        bpy.context.view_layer.update()

        filepath = os.path.join(tmp_dir, f"dir{direction_deg:03d}_f{i:03d}.png")
        scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)
        frames.append(filepath)

    return frames


def _composite_sprite_sheet(all_frames, num_directions, frames_per_dir, frame_size, output_path):
    """Stitch individual frame renders into a sprite sheet.

    Layout: rows = directions, columns = frames
    Uses Blender's compositor to load and combine images.
    """
    # We'll use Python + bpy.data.images to composite
    sheet_w = frames_per_dir * frame_size
    sheet_h = num_directions * frame_size

    # Create blank image for the sheet
    sheet = bpy.data.images.new("SpriteSheet", width=sheet_w, height=sheet_h, alpha=True)
    pixels = [0.0] * (sheet_w * sheet_h * 4)

    for dir_idx in range(num_directions):
        for frame_idx in range(frames_per_dir):
            filepath = all_frames[dir_idx][frame_idx]
            if not os.path.exists(filepath):
                continue

            frame_img = bpy.data.images.load(filepath)
            # Resize if needed
            if frame_img.size[0] != frame_size or frame_img.size[1] != frame_size:
                frame_img.scale(frame_size, frame_size)

            frame_pixels = list(frame_img.pixels)
            fw, fh = frame_img.size

            # Place in sheet: row = dir_idx (from bottom in Blender image coords)
            # Blender images are bottom-up, so row 0 = bottom
            # We want direction 0 (South) at top of sheet → flip y
            sheet_row = num_directions - 1 - dir_idx

            for py in range(fh):
                for px in range(fw):
                    src_idx = (py * fw + px) * 4
                    dst_x = frame_idx * frame_size + px
                    dst_y = sheet_row * frame_size + py
                    dst_idx = (dst_y * sheet_w + dst_x) * 4
                    if dst_idx + 3 < len(pixels) and src_idx + 3 < len(frame_pixels):
                        pixels[dst_idx]     = frame_pixels[src_idx]
                        pixels[dst_idx + 1] = frame_pixels[src_idx + 1]
                        pixels[dst_idx + 2] = frame_pixels[src_idx + 2]
                        pixels[dst_idx + 3] = frame_pixels[src_idx + 3]

            bpy.data.images.remove(frame_img)

    sheet.pixels = pixels
    sheet.filepath_raw = output_path
    sheet.file_format = 'PNG'
    sheet.save()
    bpy.data.images.remove(sheet)


def _write_metadata(output_path, unit_name, anim_name, num_directions, frames_per_dir, frame_size):
    """Write a JSON metadata file alongside the sprite sheet."""
    meta = {
        'unit': unit_name,
        'animation': anim_name,
        'frameWidth': frame_size,
        'frameHeight': frame_size,
        'framesPerDirection': frames_per_dir,
        'directions': num_directions,
        'directionOrder': _direction_labels(num_directions),
        'sheetWidth': frames_per_dir * frame_size,
        'sheetHeight': num_directions * frame_size,
    }
    meta_path = output_path.replace('.png', '.json')
    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)
    print(f"Metadata: {meta_path}")


def _direction_labels(n):
    """Return direction labels for n directions (clockwise from South)."""
    if n == 8:
        return ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']
    elif n == 4:
        return ['S', 'W', 'N', 'E']
    else:
        return [f"{int(i * 360 / n)}deg" for i in range(n)]


def main():
    args = parse_args()
    _load_builders()

    if args.unit not in UNIT_BUILDERS:
        print(f"ERROR: Unknown unit '{args.unit}'. Available: {', '.join(UNIT_BUILDERS.keys())}")
        sys.exit(1)

    if args.anim not in ANIM_CONFIG:
        print(f"ERROR: Unknown anim '{args.anim}'. Available: {', '.join(ANIM_CONFIG.keys())}")
        sys.exit(1)

    # Output path
    if args.output:
        output = args.output
    else:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output = os.path.join(project_root, "client", "public", "assets", "units",
                              f"{args.unit}_{args.anim}.png")
    os.makedirs(os.path.dirname(output), exist_ok=True)

    print(f"=== Rendering {args.unit} | anim={args.anim} | dirs={args.directions} | frame={args.frame_size}px ===")

    # Setup scene
    scene = setup_scene(resolution=args.frame_size, samples=args.samples)

    # Build unit
    print("Building unit model and rig...")
    builder = UNIT_BUILDERS[args.unit]
    arm_obj, walk_action, shoot_action = builder()

    # Activate animation
    config = _activate_animation(arm_obj, args.anim)
    frame_range = range(config['frame_start'], config['frame_end'] + 1, config['frame_step'])
    frames_per_dir = len(list(frame_range))

    # Setup rendering environment
    setup_lighting()
    add_shadow_catcher()

    # Camera setup for units — closer, smaller ortho scale
    setup_camera(ortho_scale=3.5, target_z=0.9, elevation=30, azimuth=45, distance=20)

    setup_compositing()

    # Temp directory for individual frames
    import tempfile
    tmp_dir = tempfile.mkdtemp(prefix="unit_render_")

    # Render each direction
    all_frames = []
    dir_step = 360.0 / args.directions

    for dir_idx in range(args.directions):
        direction_deg = int(dir_idx * dir_step)
        print(f"\n  Direction {dir_idx + 1}/{args.directions}: {direction_deg}° ...")

        # Rotate the armature for this direction
        arm_obj.rotation_euler = (0, 0, math.radians(direction_deg))
        bpy.context.view_layer.update()

        dir_frames = _render_frames(scene, arm_obj, config, direction_deg, args.frame_size, tmp_dir)
        all_frames.append(dir_frames)
        print(f"    Rendered {len(dir_frames)} frames")

    # Composite sprite sheet
    print(f"\nCompositing sprite sheet ({frames_per_dir} frames × {args.directions} directions)...")
    _composite_sprite_sheet(all_frames, args.directions, frames_per_dir, args.frame_size, output)

    # Write metadata
    _write_metadata(output, args.unit, args.anim, args.directions, frames_per_dir, args.frame_size)

    # Cleanup temp frames
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)

    # Optionally save blend file
    if args.blend_output:
        bpy.ops.wm.save_as_mainfile(filepath=args.blend_output)
        print(f"Blend file: {args.blend_output}")

    print(f"\nDone! Sprite sheet: {output}")
    print(f"  {frames_per_dir} frames × {args.directions} directions = {frames_per_dir * args.directions} cells")
    print(f"  Sheet size: {frames_per_dir * args.frame_size} × {args.directions * args.frame_size} px")


if __name__ == "__main__":
    main()
