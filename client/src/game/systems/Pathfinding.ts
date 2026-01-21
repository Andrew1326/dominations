/**
 * A* Pathfinding System
 *
 * Grid-based pathfinding for units navigating around buildings.
 * Uses the A* algorithm to find optimal paths.
 */

import { GRID_SIZE, BUILDINGS } from '../../../../shared/constants';
import type { BuildingData, BuildingType } from '../../../../shared/types';

// ============================================================
// Types
// ============================================================

interface GridNode {
  row: number;
  col: number;
  g: number;  // Cost from start
  h: number;  // Heuristic cost to goal
  f: number;  // Total cost (g + h)
  parent: GridNode | null;
  walkable: boolean;
}

export interface PathPoint {
  row: number;
  col: number;
}

// ============================================================
// Priority Queue (Min-Heap for A*)
// ============================================================

class PriorityQueue<T> {
  private items: { element: T; priority: number }[] = [];

  enqueue(element: T, priority: number): void {
    this.items.push({ element, priority });
    this.items.sort((a, b) => a.priority - b.priority);
  }

  dequeue(): T | undefined {
    return this.items.shift()?.element;
  }

  isEmpty(): boolean {
    return this.items.length === 0;
  }

  contains(predicate: (element: T) => boolean): boolean {
    return this.items.some((item) => predicate(item.element));
  }
}

// ============================================================
// Pathfinding Grid
// ============================================================

export class PathfindingGrid {
  private grid: GridNode[][] = [];
  private width: number;
  private height: number;

  constructor(width: number = GRID_SIZE, height: number = GRID_SIZE) {
    this.width = width;
    this.height = height;
    this.initializeGrid();
  }

  /**
   * Initialize empty grid
   */
  private initializeGrid(): void {
    this.grid = [];
    for (let row = 0; row < this.height; row++) {
      this.grid[row] = [];
      for (let col = 0; col < this.width; col++) {
        this.grid[row][col] = {
          row,
          col,
          g: 0,
          h: 0,
          f: 0,
          parent: null,
          walkable: true,
        };
      }
    }
  }

  /**
   * Reset grid costs for new pathfinding
   */
  private resetCosts(): void {
    for (let row = 0; row < this.height; row++) {
      for (let col = 0; col < this.width; col++) {
        this.grid[row][col].g = 0;
        this.grid[row][col].h = 0;
        this.grid[row][col].f = 0;
        this.grid[row][col].parent = null;
      }
    }
  }

  /**
   * Update grid with building obstacles
   */
  updateFromBuildings(buildings: BuildingData[]): void {
    // Reset all tiles to walkable
    for (let row = 0; row < this.height; row++) {
      for (let col = 0; col < this.width; col++) {
        this.grid[row][col].walkable = true;
      }
    }

    // Mark building tiles as unwalkable
    for (const building of buildings) {
      const def = BUILDINGS[building.type as BuildingType];
      if (!def) continue;

      for (let r = 0; r < def.height; r++) {
        for (let c = 0; c < def.width; c++) {
          const gridRow = building.row + r;
          const gridCol = building.col + c;
          if (this.isInBounds(gridRow, gridCol)) {
            this.grid[gridRow][gridCol].walkable = false;
          }
        }
      }
    }
  }

  /**
   * Check if position is within grid bounds
   */
  isInBounds(row: number, col: number): boolean {
    return row >= 0 && row < this.height && col >= 0 && col < this.width;
  }

  /**
   * Check if position is walkable
   */
  isWalkable(row: number, col: number): boolean {
    if (!this.isInBounds(row, col)) return false;
    return this.grid[row][col].walkable;
  }

  /**
   * Get node at position
   */
  getNode(row: number, col: number): GridNode | null {
    if (!this.isInBounds(row, col)) return null;
    return this.grid[row][col];
  }

  /**
   * Get walkable neighbors of a node
   */
  private getNeighbors(node: GridNode): GridNode[] {
    const neighbors: GridNode[] = [];
    const directions = [
      [-1, 0],  // Up
      [1, 0],   // Down
      [0, -1],  // Left
      [0, 1],   // Right
      [-1, -1], // Up-Left (diagonal)
      [-1, 1],  // Up-Right (diagonal)
      [1, -1],  // Down-Left (diagonal)
      [1, 1],   // Down-Right (diagonal)
    ];

    for (const [dr, dc] of directions) {
      const newRow = node.row + dr;
      const newCol = node.col + dc;

      if (this.isWalkable(newRow, newCol)) {
        // For diagonal movement, check that adjacent orthogonal tiles are also walkable
        // This prevents cutting corners through walls
        if (dr !== 0 && dc !== 0) {
          if (!this.isWalkable(node.row + dr, node.col) || !this.isWalkable(node.row, node.col + dc)) {
            continue;
          }
        }
        neighbors.push(this.grid[newRow][newCol]);
      }
    }

    return neighbors;
  }

  /**
   * Calculate heuristic (Euclidean distance)
   */
  private heuristic(a: GridNode, b: GridNode): number {
    const dx = Math.abs(a.col - b.col);
    const dy = Math.abs(a.row - b.row);
    return Math.sqrt(dx * dx + dy * dy);
  }

  /**
   * Find path using A* algorithm
   */
  findPath(startRow: number, startCol: number, endRow: number, endCol: number): PathPoint[] {
    // Validate inputs
    if (!this.isInBounds(startRow, startCol) || !this.isInBounds(endRow, endCol)) {
      return [];
    }

    // Reset costs from previous pathfinding
    this.resetCosts();

    const startNode = this.grid[Math.floor(startRow)][Math.floor(startCol)];
    const endNode = this.grid[Math.floor(endRow)][Math.floor(endCol)];

    // If start or end is not walkable, try to find nearest walkable
    if (!startNode.walkable || !endNode.walkable) {
      // For non-walkable end (building), find closest walkable tile
      if (!endNode.walkable) {
        const nearest = this.findNearestWalkable(endRow, endCol);
        if (!nearest) return [];
        return this.findPath(startRow, startCol, nearest.row, nearest.col);
      }
      return [];
    }

    const openSet = new PriorityQueue<GridNode>();
    const closedSet = new Set<string>();

    startNode.g = 0;
    startNode.h = this.heuristic(startNode, endNode);
    startNode.f = startNode.h;

    openSet.enqueue(startNode, startNode.f);

    while (!openSet.isEmpty()) {
      const current = openSet.dequeue()!;
      const currentKey = `${current.row},${current.col}`;

      // Found the goal
      if (current.row === endNode.row && current.col === endNode.col) {
        return this.reconstructPath(current);
      }

      closedSet.add(currentKey);

      for (const neighbor of this.getNeighbors(current)) {
        const neighborKey = `${neighbor.row},${neighbor.col}`;

        if (closedSet.has(neighborKey)) {
          continue;
        }

        // Cost to move to neighbor (1.0 for orthogonal, 1.414 for diagonal)
        const isDiagonal = current.row !== neighbor.row && current.col !== neighbor.col;
        const moveCost = isDiagonal ? 1.414 : 1.0;
        const tentativeG = current.g + moveCost;

        // Check if this path is better
        const inOpenSet = openSet.contains((n) => n.row === neighbor.row && n.col === neighbor.col);

        if (!inOpenSet || tentativeG < neighbor.g) {
          neighbor.parent = current;
          neighbor.g = tentativeG;
          neighbor.h = this.heuristic(neighbor, endNode);
          neighbor.f = neighbor.g + neighbor.h;

          if (!inOpenSet) {
            openSet.enqueue(neighbor, neighbor.f);
          }
        }
      }
    }

    // No path found
    return [];
  }

  /**
   * Find nearest walkable tile to a position
   */
  private findNearestWalkable(row: number, col: number): GridNode | null {
    const maxRadius = 5;

    for (let radius = 1; radius <= maxRadius; radius++) {
      for (let dr = -radius; dr <= radius; dr++) {
        for (let dc = -radius; dc <= radius; dc++) {
          if (Math.abs(dr) === radius || Math.abs(dc) === radius) {
            const testRow = Math.floor(row) + dr;
            const testCol = Math.floor(col) + dc;
            if (this.isWalkable(testRow, testCol)) {
              return this.grid[testRow][testCol];
            }
          }
        }
      }
    }

    return null;
  }

  /**
   * Reconstruct path from goal to start
   */
  private reconstructPath(endNode: GridNode): PathPoint[] {
    const path: PathPoint[] = [];
    let current: GridNode | null = endNode;

    while (current) {
      path.unshift({ row: current.row, col: current.col });
      current = current.parent;
    }

    return path;
  }

  /**
   * Smooth a path by removing unnecessary waypoints
   */
  smoothPath(path: PathPoint[]): PathPoint[] {
    if (path.length <= 2) return path;

    const smoothed: PathPoint[] = [path[0]];
    let current = 0;

    while (current < path.length - 1) {
      // Find the furthest visible point
      let furthest = current + 1;

      for (let i = path.length - 1; i > current + 1; i--) {
        if (this.hasLineOfSight(path[current], path[i])) {
          furthest = i;
          break;
        }
      }

      smoothed.push(path[furthest]);
      current = furthest;
    }

    return smoothed;
  }

  /**
   * Check if there's a clear line of sight between two points
   */
  private hasLineOfSight(a: PathPoint, b: PathPoint): boolean {
    const dx = b.col - a.col;
    const dy = b.row - a.row;
    const steps = Math.max(Math.abs(dx), Math.abs(dy));

    if (steps === 0) return true;

    const stepX = dx / steps;
    const stepY = dy / steps;

    for (let i = 1; i < steps; i++) {
      const col = Math.round(a.col + stepX * i);
      const row = Math.round(a.row + stepY * i);

      if (!this.isWalkable(row, col)) {
        return false;
      }
    }

    return true;
  }
}

// ============================================================
// Path Follower for Units
// ============================================================

export class PathFollower {
  private path: PathPoint[] = [];
  private currentIndex: number = 0;
  private speed: number;

  constructor(speed: number) {
    this.speed = speed;
  }

  /**
   * Set a new path to follow
   */
  setPath(path: PathPoint[]): void {
    this.path = path;
    this.currentIndex = 0;
  }

  /**
   * Check if currently following a path
   */
  hasPath(): boolean {
    return this.path.length > 0 && this.currentIndex < this.path.length;
  }

  /**
   * Get current target waypoint
   */
  getCurrentTarget(): PathPoint | null {
    if (!this.hasPath()) return null;
    return this.path[this.currentIndex];
  }

  /**
   * Get remaining path
   */
  getRemainingPath(): PathPoint[] {
    return this.path.slice(this.currentIndex);
  }

  /**
   * Update position along path
   * Returns new position
   */
  update(currentRow: number, currentCol: number, deltaTime: number): { row: number; col: number } {
    if (!this.hasPath()) {
      return { row: currentRow, col: currentCol };
    }

    const target = this.path[this.currentIndex];
    const dx = target.col - currentCol;
    const dy = target.row - currentRow;
    const dist = Math.sqrt(dx * dx + dy * dy);

    const moveAmount = this.speed * deltaTime;

    if (dist <= moveAmount) {
      // Reached waypoint, move to next
      this.currentIndex++;
      return { row: target.row, col: target.col };
    }

    // Move towards target
    return {
      row: currentRow + (dy / dist) * moveAmount,
      col: currentCol + (dx / dist) * moveAmount,
    };
  }

  /**
   * Clear the current path
   */
  clear(): void {
    this.path = [];
    this.currentIndex = 0;
  }
}
