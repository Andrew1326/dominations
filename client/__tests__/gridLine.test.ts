/**
 * Grid line tests — cells crossed by a drag between two cells.
 */

import { describe, it, expect } from 'vitest';
import { gridLineCells } from '../src/game/systems/gridLine';

const keys = (cells: { row: number; col: number }[]) => cells.map((c) => `${c.row},${c.col}`);

describe('gridLineCells', () => {
  it('a single cell (no movement) returns just that cell', () => {
    expect(gridLineCells(5, 5, 5, 5)).toEqual([{ row: 5, col: 5 }]);
  });

  it('a horizontal run fills every column inclusively', () => {
    expect(keys(gridLineCells(3, 1, 3, 4))).toEqual(['3,1', '3,2', '3,3', '3,4']);
  });

  it('a vertical run fills every row inclusively', () => {
    expect(keys(gridLineCells(1, 7, 4, 7))).toEqual(['1,7', '2,7', '3,7', '4,7']);
  });

  it('endpoints are included and ordered from start to end', () => {
    const cells = gridLineCells(2, 2, 2, 6);
    expect(cells[0]).toEqual({ row: 2, col: 2 });
    expect(cells[cells.length - 1]).toEqual({ row: 2, col: 6 });
  });

  it('a diagonal run is continuous (no gaps) and has no duplicates', () => {
    const cells = gridLineCells(0, 0, 5, 5);
    const set = new Set(keys(cells));
    expect(set.size).toBe(cells.length); // no duplicates
    // each step moves at most one cell in each axis
    for (let i = 1; i < cells.length; i++) {
      expect(Math.abs(cells[i].row - cells[i - 1].row)).toBeLessThanOrEqual(1);
      expect(Math.abs(cells[i].col - cells[i - 1].col)).toBeLessThanOrEqual(1);
    }
  });

  it('works in the negative direction', () => {
    expect(keys(gridLineCells(4, 4, 4, 1))).toEqual(['4,4', '4,3', '4,2', '4,1']);
  });
});
