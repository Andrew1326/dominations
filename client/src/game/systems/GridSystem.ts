/**
 * GridSystem - Handles isometric grid logic and coordinate conversions
 */

import type { GridPosition, ScreenPosition } from '@shared/types';
import {
  GRID_SIZE,
  TILE_WIDTH,
  TILE_HEIGHT,
  TILE_WIDTH_HALF,
  TILE_HEIGHT_HALF,
} from '@shared/constants';

export class GridSystem {
  private occupancyGrid: boolean[][];
  private originX: number;
  private originY: number;

  constructor(originX: number, originY: number) {
    this.originX = originX;
    this.originY = originY;

    // Initialize empty occupancy grid
    this.occupancyGrid = Array(GRID_SIZE)
      .fill(null)
      .map(() => Array(GRID_SIZE).fill(false));
  }

  /**
   * Convert grid (row, col) to screen (x, y) coordinates
   */
  gridToScreen(row: number, col: number): ScreenPosition {
    return {
      x: this.originX + (col - row) * TILE_WIDTH_HALF,
      y: this.originY + (col + row) * TILE_HEIGHT_HALF,
    };
  }

  /**
   * Convert screen (x, y) to grid (row, col) coordinates
   */
  screenToGrid(screenX: number, screenY: number): GridPosition {
    const relX = screenX - this.originX;
    const relY = screenY - this.originY;

    const col = (relX / TILE_WIDTH_HALF + relY / TILE_HEIGHT_HALF) / 2;
    const row = (relY / TILE_HEIGHT_HALF - relX / TILE_WIDTH_HALF) / 2;

    return {
      row: Math.floor(row),
      col: Math.floor(col),
    };
  }

  /**
   * Check if a grid position is within bounds
   */
  isInBounds(row: number, col: number): boolean {
    return row >= 0 && row < GRID_SIZE && col >= 0 && col < GRID_SIZE;
  }

  /**
   * Check if a rectangular area is available for building placement
   */
  canPlace(row: number, col: number, width: number, height: number): boolean {
    for (let r = row; r < row + height; r++) {
      for (let c = col; c < col + width; c++) {
        if (!this.isInBounds(r, c) || this.occupancyGrid[r][c]) {
          return false;
        }
      }
    }
    return true;
  }

  /**
   * Mark a rectangular area as occupied
   */
  occupy(row: number, col: number, width: number, height: number): void {
    for (let r = row; r < row + height; r++) {
      for (let c = col; c < col + width; c++) {
        if (this.isInBounds(r, c)) {
          this.occupancyGrid[r][c] = true;
        }
      }
    }
  }

  /**
   * Mark a rectangular area as unoccupied
   */
  vacate(row: number, col: number, width: number, height: number): void {
    for (let r = row; r < row + height; r++) {
      for (let c = col; c < col + width; c++) {
        if (this.isInBounds(r, c)) {
          this.occupancyGrid[r][c] = false;
        }
      }
    }
  }

  /**
   * Check if a specific tile is occupied
   */
  isOccupied(row: number, col: number): boolean {
    if (!this.isInBounds(row, col)) return true;
    return this.occupancyGrid[row][col];
  }

  /**
   * Clear all occupancy data
   */
  clearAll(): void {
    for (let r = 0; r < GRID_SIZE; r++) {
      for (let c = 0; c < GRID_SIZE; c++) {
        this.occupancyGrid[r][c] = false;
      }
    }
  }

  /**
   * Get the grid size
   */
  getSize(): number {
    return GRID_SIZE;
  }

  /**
   * Get tile dimensions
   */
  getTileDimensions(): { width: number; height: number } {
    return { width: TILE_WIDTH, height: TILE_HEIGHT };
  }

  /**
   * Get the origin point
   */
  getOrigin(): ScreenPosition {
    return { x: this.originX, y: this.originY };
  }
}
