/**
 * Wall autotiling tests — orientation chosen from neighbours.
 */

import { describe, it, expect } from 'vitest';
import { cellKey, wallVariant, shouldMirrorWall, WallVariant } from '../src/game/systems/wallTiling';

function wallsAt(cells: Array<[number, number]>): Set<string> {
  return new Set(cells.map(([r, c]) => cellKey(r, c)));
}

describe('wallTiling', () => {
  it('an isolated wall has no run orientation', () => {
    const walls = wallsAt([[5, 5]]);
    expect(wallVariant(walls, 5, 5)).toBe<WallVariant>('isolated');
  });

  it('a wall in a row-axis run uses the row-axis sprite', () => {
    const walls = wallsAt([[5, 5], [6, 5], [7, 5]]);
    expect(wallVariant(walls, 6, 5)).toBe('rowAxis'); // middle
    expect(wallVariant(walls, 5, 5)).toBe('rowAxis'); // endpoint
  });

  it('a wall in a col-axis run uses the col-axis sprite', () => {
    const walls = wallsAt([[5, 5], [5, 6], [5, 7]]);
    expect(wallVariant(walls, 5, 6)).toBe('colAxis'); // middle
    expect(wallVariant(walls, 5, 7)).toBe('colAxis'); // endpoint
  });

  it('a corner (neighbours on both axes) uses the corner tower', () => {
    // L-shape: (5,5) has neighbours at (6,5) [row] and (5,6) [col]
    const walls = wallsAt([[5, 5], [6, 5], [5, 6]]);
    expect(wallVariant(walls, 5, 5)).toBe('corner');
  });

  it('diagonal-only neighbours do not connect (not 4-adjacent)', () => {
    const walls = wallsAt([[5, 5], [6, 6]]);
    expect(wallVariant(walls, 5, 5)).toBe('isolated');
  });

  it('cellKey is stable and unique per cell', () => {
    expect(cellKey(3, 7)).toBe('3,7');
    expect(cellKey(3, 7)).not.toBe(cellKey(7, 3));
  });

  it('only the col-axis orientation is mirrored (the two iso orientations are one mirrored sprite)', () => {
    expect(shouldMirrorWall('colAxis')).toBe(true);
    expect(shouldMirrorWall('rowAxis')).toBe(false);
    expect(shouldMirrorWall('corner')).toBe(false);
    expect(shouldMirrorWall('isolated')).toBe(false);
  });
});
