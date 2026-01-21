/**
 * Tests for A* Pathfinding System
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { PathfindingGrid, PathFollower, PathPoint } from '../src/game/systems/Pathfinding';
import type { BuildingData } from '../../shared/types';

// Helper to create test buildings
function createBuilding(
  id: string,
  type: BuildingData['type'],
  row: number,
  col: number
): BuildingData {
  return { id, type, row, col, level: 1 };
}

describe('PathfindingGrid', () => {
  let grid: PathfindingGrid;

  beforeEach(() => {
    grid = new PathfindingGrid(10, 10); // Smaller grid for testing
  });

  describe('initialization', () => {
    it('creates a grid of the correct size', () => {
      expect(grid.isInBounds(0, 0)).toBe(true);
      expect(grid.isInBounds(9, 9)).toBe(true);
      expect(grid.isInBounds(10, 10)).toBe(false);
      expect(grid.isInBounds(-1, 0)).toBe(false);
    });

    it('starts with all tiles walkable', () => {
      for (let row = 0; row < 10; row++) {
        for (let col = 0; col < 10; col++) {
          expect(grid.isWalkable(row, col)).toBe(true);
        }
      }
    });
  });

  describe('updateFromBuildings', () => {
    it('marks building tiles as unwalkable', () => {
      const buildings = [
        createBuilding('b1', 'farm', 2, 2), // 2x2 building
      ];

      grid.updateFromBuildings(buildings);

      // Building tiles should not be walkable
      expect(grid.isWalkable(2, 2)).toBe(false);
      expect(grid.isWalkable(2, 3)).toBe(false);
      expect(grid.isWalkable(3, 2)).toBe(false);
      expect(grid.isWalkable(3, 3)).toBe(false);

      // Adjacent tiles should still be walkable
      expect(grid.isWalkable(1, 2)).toBe(true);
      expect(grid.isWalkable(4, 2)).toBe(true);
    });

    it('handles multiple buildings', () => {
      const buildings = [
        createBuilding('b1', 'farm', 0, 0),
        createBuilding('b2', 'farm', 5, 5),
      ];

      grid.updateFromBuildings(buildings);

      expect(grid.isWalkable(0, 0)).toBe(false);
      expect(grid.isWalkable(5, 5)).toBe(false);
      expect(grid.isWalkable(3, 3)).toBe(true);
    });
  });

  describe('findPath', () => {
    it('finds a direct path when no obstacles', () => {
      const path = grid.findPath(0, 0, 5, 5);

      expect(path.length).toBeGreaterThan(0);
      expect(path[0]).toEqual({ row: 0, col: 0 });
      expect(path[path.length - 1]).toEqual({ row: 5, col: 5 });
    });

    it('returns empty array for invalid start', () => {
      const path = grid.findPath(-1, 0, 5, 5);
      expect(path).toEqual([]);
    });

    it('returns empty array for invalid end', () => {
      const path = grid.findPath(0, 0, 15, 15);
      expect(path).toEqual([]);
    });

    it('finds path around obstacle', () => {
      // Create a wall of buildings blocking direct path
      const buildings = [
        createBuilding('b1', 'farm', 2, 2),
        createBuilding('b2', 'farm', 2, 4),
      ];
      grid.updateFromBuildings(buildings);

      const path = grid.findPath(0, 3, 5, 3);

      expect(path.length).toBeGreaterThan(0);
      expect(path[0]).toEqual({ row: 0, col: 3 });
      expect(path[path.length - 1]).toEqual({ row: 5, col: 3 });

      // Path should not go through buildings
      for (const point of path) {
        expect(grid.isWalkable(point.row, point.col)).toBe(true);
      }
    });

    it('finds path to building edge (nearest walkable)', () => {
      const buildings = [
        createBuilding('b1', 'farm', 5, 5),
      ];
      grid.updateFromBuildings(buildings);

      // Target is inside building, should path to nearest edge
      const path = grid.findPath(0, 0, 5, 5);

      expect(path.length).toBeGreaterThan(0);
      // End point should be walkable (near the building but not on it)
      const end = path[path.length - 1];
      expect(grid.isWalkable(end.row, end.col)).toBe(true);
    });

    it('uses diagonal movement when possible', () => {
      const path = grid.findPath(0, 0, 2, 2);

      // Diagonal path should be shorter than orthogonal
      expect(path.length).toBeLessThanOrEqual(3);
    });

    it('handles fractional start positions', () => {
      const path = grid.findPath(0.5, 0.5, 5, 5);

      expect(path.length).toBeGreaterThan(0);
      expect(path[0]).toEqual({ row: 0, col: 0 }); // Floors to integer
    });
  });

  describe('smoothPath', () => {
    it('removes unnecessary waypoints', () => {
      // Create a long straight path
      const longPath: PathPoint[] = [
        { row: 0, col: 0 },
        { row: 0, col: 1 },
        { row: 0, col: 2 },
        { row: 0, col: 3 },
        { row: 0, col: 4 },
      ];

      const smoothed = grid.smoothPath(longPath);

      // Should simplify to just start and end
      expect(smoothed.length).toBeLessThan(longPath.length);
      expect(smoothed[0]).toEqual({ row: 0, col: 0 });
      expect(smoothed[smoothed.length - 1]).toEqual({ row: 0, col: 4 });
    });

    it('keeps waypoints needed to avoid obstacles', () => {
      // Create obstacle
      const buildings = [
        createBuilding('b1', 'farm', 1, 2),
      ];
      grid.updateFromBuildings(buildings);

      // Path that goes around obstacle
      const path: PathPoint[] = [
        { row: 0, col: 0 },
        { row: 0, col: 1 },
        { row: 0, col: 2 }, // Turn point
        { row: 0, col: 3 },
        { row: 0, col: 4 },
        { row: 1, col: 4 },
        { row: 2, col: 4 },
      ];

      const smoothed = grid.smoothPath(path);

      // Should keep corner points
      expect(smoothed.length).toBeGreaterThanOrEqual(2);
    });

    it('handles empty path', () => {
      const smoothed = grid.smoothPath([]);
      expect(smoothed).toEqual([]);
    });

    it('handles single point path', () => {
      const smoothed = grid.smoothPath([{ row: 0, col: 0 }]);
      expect(smoothed).toEqual([{ row: 0, col: 0 }]);
    });
  });
});

describe('PathFollower', () => {
  let follower: PathFollower;

  beforeEach(() => {
    follower = new PathFollower(2); // 2 tiles per second
  });

  describe('path management', () => {
    it('starts with no path', () => {
      expect(follower.hasPath()).toBe(false);
      expect(follower.getCurrentTarget()).toBeNull();
    });

    it('sets and follows a path', () => {
      const path: PathPoint[] = [
        { row: 0, col: 0 },
        { row: 1, col: 1 },
        { row: 2, col: 2 },
      ];

      follower.setPath(path);

      expect(follower.hasPath()).toBe(true);
      expect(follower.getCurrentTarget()).toEqual({ row: 0, col: 0 });
    });

    it('clears the path', () => {
      follower.setPath([{ row: 0, col: 0 }, { row: 1, col: 1 }]);
      follower.clear();

      expect(follower.hasPath()).toBe(false);
    });
  });

  describe('movement', () => {
    it('moves towards target', () => {
      follower.setPath([
        { row: 0, col: 0 },
        { row: 0, col: 10 },
      ]);

      // First update reaches starting waypoint and advances to next
      follower.update(0, 0, 0.01);

      // Now current target should be the second waypoint
      expect(follower.getCurrentTarget()).toEqual({ row: 0, col: 10 });

      // Move towards second waypoint
      const newPos = follower.update(0, 0, 1); // 1 second at speed 2

      expect(newPos.col).toBeGreaterThan(0);
      expect(newPos.col).toBeLessThan(10);
    });

    it('advances to next waypoint when reaching target', () => {
      follower.setPath([
        { row: 0, col: 0 },
        { row: 0, col: 1 },
        { row: 0, col: 2 },
      ]);

      // Move past first waypoint
      const pos1 = follower.update(0, 0, 0.5);
      expect(pos1).toEqual({ row: 0, col: 0 }); // At first waypoint

      // Should now target second waypoint
      expect(follower.getCurrentTarget()).toEqual({ row: 0, col: 1 });
    });

    it('returns current position when no path', () => {
      const pos = follower.update(5, 5, 1);
      expect(pos).toEqual({ row: 5, col: 5 });
    });

    it('completes path when all waypoints reached', () => {
      follower.setPath([
        { row: 0, col: 0 },
        { row: 0, col: 1 },
      ]);

      // Reach all waypoints
      follower.update(0, 0, 0.5);
      follower.update(0, 1, 0.5);

      expect(follower.hasPath()).toBe(false);
    });
  });

  describe('getRemainingPath', () => {
    it('returns full path at start', () => {
      const path: PathPoint[] = [
        { row: 0, col: 0 },
        { row: 1, col: 1 },
        { row: 2, col: 2 },
      ];

      follower.setPath(path);

      expect(follower.getRemainingPath()).toEqual(path);
    });

    it('returns partial path after movement', () => {
      const path: PathPoint[] = [
        { row: 0, col: 0 },
        { row: 1, col: 1 },
        { row: 2, col: 2 },
      ];

      follower.setPath(path);
      follower.update(0, 0, 0.5); // Reach first waypoint

      const remaining = follower.getRemainingPath();
      expect(remaining.length).toBe(2);
      expect(remaining[0]).toEqual({ row: 1, col: 1 });
    });
  });
});
