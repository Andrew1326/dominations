/**
 * GridSystem Tests
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { GridSystem } from '../src/game/systems/GridSystem';
import { GRID_SIZE } from '../../shared/constants';

describe('GridSystem', () => {
  let gridSystem: GridSystem;
  const originX = 640;
  const originY = 100;

  beforeEach(() => {
    gridSystem = new GridSystem(originX, originY);
  });

  describe('coordinate conversion', () => {
    it('converts grid (0,0) to screen origin', () => {
      const screen = gridSystem.gridToScreen(0, 0);
      expect(screen.x).toBe(originX);
      expect(screen.y).toBe(originY);
    });

    it('converts screen origin to grid (0,0)', () => {
      const grid = gridSystem.screenToGrid(originX, originY);
      expect(grid.row).toBe(0);
      expect(grid.col).toBe(0);
    });

    it('roundtrips grid -> screen -> grid correctly', () => {
      const testCases = [
        { row: 0, col: 0 },
        { row: 5, col: 5 },
        { row: 10, col: 3 },
        { row: 3, col: 10 },
        { row: GRID_SIZE - 1, col: GRID_SIZE - 1 },
      ];

      testCases.forEach(({ row, col }) => {
        const screen = gridSystem.gridToScreen(row, col);
        // Add small offset to center of tile for accurate conversion
        const grid = gridSystem.screenToGrid(screen.x + 1, screen.y + 1);
        expect(grid.row).toBe(row);
        expect(grid.col).toBe(col);
      });
    });
  });

  describe('bounds checking', () => {
    it('returns true for valid positions', () => {
      expect(gridSystem.isInBounds(0, 0)).toBe(true);
      expect(gridSystem.isInBounds(10, 10)).toBe(true);
      expect(gridSystem.isInBounds(GRID_SIZE - 1, GRID_SIZE - 1)).toBe(true);
    });

    it('returns false for out-of-bounds positions', () => {
      expect(gridSystem.isInBounds(-1, 0)).toBe(false);
      expect(gridSystem.isInBounds(0, -1)).toBe(false);
      expect(gridSystem.isInBounds(GRID_SIZE, 0)).toBe(false);
      expect(gridSystem.isInBounds(0, GRID_SIZE)).toBe(false);
    });
  });

  describe('occupancy', () => {
    it('starts with all tiles unoccupied', () => {
      for (let r = 0; r < GRID_SIZE; r++) {
        for (let c = 0; c < GRID_SIZE; c++) {
          expect(gridSystem.isOccupied(r, c)).toBe(false);
        }
      }
    });

    it('marks single tile as occupied', () => {
      gridSystem.occupy(5, 5, 1, 1);
      expect(gridSystem.isOccupied(5, 5)).toBe(true);
      expect(gridSystem.isOccupied(4, 5)).toBe(false);
      expect(gridSystem.isOccupied(5, 4)).toBe(false);
    });

    it('marks rectangular area as occupied', () => {
      gridSystem.occupy(2, 3, 3, 2); // 3 wide, 2 tall starting at (2,3)

      // Check occupied tiles
      expect(gridSystem.isOccupied(2, 3)).toBe(true);
      expect(gridSystem.isOccupied(2, 4)).toBe(true);
      expect(gridSystem.isOccupied(2, 5)).toBe(true);
      expect(gridSystem.isOccupied(3, 3)).toBe(true);
      expect(gridSystem.isOccupied(3, 4)).toBe(true);
      expect(gridSystem.isOccupied(3, 5)).toBe(true);

      // Check adjacent unoccupied tiles
      expect(gridSystem.isOccupied(1, 3)).toBe(false);
      expect(gridSystem.isOccupied(2, 2)).toBe(false);
      expect(gridSystem.isOccupied(2, 6)).toBe(false);
      expect(gridSystem.isOccupied(4, 3)).toBe(false);
    });

    it('vacates occupied tiles', () => {
      gridSystem.occupy(5, 5, 2, 2);
      expect(gridSystem.isOccupied(5, 5)).toBe(true);

      gridSystem.vacate(5, 5, 2, 2);
      expect(gridSystem.isOccupied(5, 5)).toBe(false);
      expect(gridSystem.isOccupied(5, 6)).toBe(false);
      expect(gridSystem.isOccupied(6, 5)).toBe(false);
      expect(gridSystem.isOccupied(6, 6)).toBe(false);
    });

    it('clears all occupancy', () => {
      gridSystem.occupy(0, 0, 5, 5);
      gridSystem.occupy(10, 10, 3, 3);

      gridSystem.clearAll();

      expect(gridSystem.isOccupied(0, 0)).toBe(false);
      expect(gridSystem.isOccupied(10, 10)).toBe(false);
    });
  });

  describe('placement validation', () => {
    it('allows placement on empty tiles', () => {
      expect(gridSystem.canPlace(0, 0, 2, 2)).toBe(true);
      expect(gridSystem.canPlace(5, 5, 3, 3)).toBe(true);
    });

    it('denies placement on occupied tiles', () => {
      gridSystem.occupy(5, 5, 2, 2);

      // Direct overlap
      expect(gridSystem.canPlace(5, 5, 1, 1)).toBe(false);
      // Partial overlap
      expect(gridSystem.canPlace(4, 4, 2, 2)).toBe(false);
      expect(gridSystem.canPlace(6, 6, 2, 2)).toBe(false);
    });

    it('denies placement that extends out of bounds', () => {
      expect(gridSystem.canPlace(GRID_SIZE - 1, GRID_SIZE - 1, 2, 2)).toBe(false);
      expect(gridSystem.canPlace(-1, 0, 1, 1)).toBe(false);
      expect(gridSystem.canPlace(0, GRID_SIZE, 1, 1)).toBe(false);
    });

    it('allows placement adjacent to occupied tiles', () => {
      gridSystem.occupy(5, 5, 2, 2);

      // Adjacent but not overlapping
      expect(gridSystem.canPlace(5, 7, 2, 2)).toBe(true);
      expect(gridSystem.canPlace(7, 5, 2, 2)).toBe(true);
      expect(gridSystem.canPlace(3, 5, 2, 2)).toBe(true);
      expect(gridSystem.canPlace(5, 3, 2, 2)).toBe(true);
    });
  });
});
