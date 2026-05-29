/**
 * Building Removal (Demolish) Tests
 *
 * Covers the two invariants behind demolishing a building on the base:
 *  1. Bounds hit-testing - a click inside a building's rendered bounds selects
 *     it (the sprite rises above its footprint, so we hit-test the visible
 *     bounds, not the footprint cell), and the frontmost building wins.
 *  2. Grid freeing - after a building is vacated, its cells become available
 *     again so a new building can be placed there.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { GridSystem } from '../src/game/systems/GridSystem';
import { BUILDINGS, TILE_WIDTH_HALF, TILE_HEIGHT_HALF } from '../../shared/constants';

interface HitBuilding {
  id: string;
  // footprint diamond center (world space) and footprint size in tiles
  cx: number;
  cy: number;
  w: number;
  h: number;
  // rendered sprite bounds (AABB, includes art above the footprint)
  bounds: { x: number; y: number; width: number; height: number };
  depth: number;
}

function pointInFootprint(b: HitBuilding, x: number, y: number): boolean {
  const halfW = ((b.w + b.h) * TILE_WIDTH_HALF) / 2;
  const halfH = ((b.w + b.h) * TILE_HEIGHT_HALF) / 2;
  return Math.abs(x - b.cx) / halfW + Math.abs(y - b.cy) / halfH <= 1;
}

function inBounds(b: HitBuilding, x: number, y: number): boolean {
  return (
    x >= b.bounds.x &&
    x <= b.bounds.x + b.bounds.width &&
    y >= b.bounds.y &&
    y <= b.bounds.y + b.bounds.height
  );
}

function topmost(buildings: HitBuilding[], pred: (b: HitBuilding) => boolean): HitBuilding | null {
  let best: HitBuilding | null = null;
  let bestDepth = -Infinity;
  for (const b of buildings) {
    if (pred(b) && b.depth >= bestDepth) {
      best = b;
      bestDepth = b.depth;
    }
  }
  return best;
}

/**
 * Mirror of MainMap.findBuildingAt - footprint diamond first (precise), then
 * sprite bounds (catches the raised art), frontmost match wins in each pass.
 */
function findBuildingAt(buildings: HitBuilding[], x: number, y: number): HitBuilding | null {
  return topmost(buildings, (b) => pointInFootprint(b, x, y)) ??
    topmost(buildings, (b) => inBounds(b, x, y));
}

describe('Building removal', () => {
  describe('hit-testing', () => {
    it('selects a building when the click is on its footprint', () => {
      const farm: HitBuilding = {
        id: 'farm', cx: 200, cy: 200, w: 2, h: 2,
        bounds: { x: 140, y: 130, width: 120, height: 120 }, depth: 5,
      };
      expect(findBuildingAt([farm], 200, 200)?.id).toBe('farm'); // footprint centre
    });

    it('returns null for clicks outside any building', () => {
      const farm: HitBuilding = {
        id: 'farm', cx: 200, cy: 200, w: 2, h: 2,
        bounds: { x: 140, y: 130, width: 120, height: 120 }, depth: 5,
      };
      expect(findBuildingAt([farm], 10, 10)).toBeNull();
      expect(findBuildingAt([], 200, 200)).toBeNull();
    });

    it('finds a 1x1 wall by its sprite when the click is on the raised art', () => {
      // Regression: a wall's sprite rises above its single footprint tile, so a
      // click on the visible wall lands above the footprint. The bounds pass
      // catches it.
      const wall: HitBuilding = {
        id: 'wall', cx: 300, cy: 300, w: 1, h: 1,
        bounds: { x: 284, y: 250, width: 32, height: 60 }, depth: 12,
      };
      // a point above the footprint centre, on the sprite, outside the footprint diamond
      expect(pointInFootprint(wall, 300, 260)).toBe(false);
      expect(findBuildingAt([wall], 300, 260)?.id).toBe('wall');
    });

    it('prefers the building under the footprint over a neighbour whose bounds overreach', () => {
      // A big house with a wide AABB (shadow/margin) overlapping a small wall's
      // footprint. Clicking the wall's footprint must select the WALL, not the
      // house — footprint precision beats bounds overreach.
      const house: HitBuilding = {
        id: 'house', cx: 400, cy: 400, w: 2, h: 2,
        bounds: { x: 280, y: 300, width: 240, height: 200 }, depth: 8, // wide bounds cover the wall
      };
      const wall: HitBuilding = {
        id: 'wall', cx: 320, cy: 360, w: 1, h: 1,
        bounds: { x: 304, y: 320, width: 32, height: 60 }, depth: 6,
      };
      // Click exactly on the wall's footprint centre (also inside the house bounds)
      expect(inBounds(house, 320, 360)).toBe(true); // house bounds overreach this point
      expect(findBuildingAt([house, wall], 320, 360)?.id).toBe('wall');
    });

    it('picks the frontmost (highest depth) building among footprint matches', () => {
      const back: HitBuilding = { id: 'back', cx: 100, cy: 100, w: 3, h: 3, bounds: { x: 0, y: 0, width: 1, height: 1 }, depth: 3 };
      const front: HitBuilding = { id: 'front', cx: 110, cy: 105, w: 3, h: 3, bounds: { x: 0, y: 0, width: 1, height: 1 }, depth: 9 };
      // A point inside both footprints -> frontmost wins
      expect(findBuildingAt([back, front], 105, 102)?.id).toBe('front');
    });
  });

  describe('grid freeing after removal', () => {
    let grid: GridSystem;

    beforeEach(() => {
      grid = new GridSystem(0, 0);
    });

    it('frees occupied cells so the same spot can be reused', () => {
      const def = BUILDINGS.townCenter; // 3x3
      grid.occupy(8, 8, def.width, def.height);
      expect(grid.canPlace(8, 8, def.width, def.height)).toBe(false);

      // Demolish -> vacate the footprint
      grid.vacate(8, 8, def.width, def.height);
      expect(grid.canPlace(8, 8, def.width, def.height)).toBe(true);
    });

    it('only frees the demolished building, leaving neighbours occupied', () => {
      const farm = BUILDINGS.farm; // 2x2
      grid.occupy(2, 2, farm.width, farm.height);
      grid.occupy(2, 5, farm.width, farm.height);

      // Remove the first farm only
      grid.vacate(2, 2, farm.width, farm.height);

      expect(grid.canPlace(2, 2, farm.width, farm.height)).toBe(true);
      expect(grid.canPlace(2, 5, farm.width, farm.height)).toBe(false);
    });
  });
});
