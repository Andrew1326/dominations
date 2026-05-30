/**
 * Grid line — the cells crossed by a straight line between two grid cells.
 *
 * Used for drag-to-paint walls: pointermove fires only every few pixels, so a
 * fast drag would skip cells. Interpolating the line between consecutive
 * samples keeps a dragged wall run continuous.
 *
 * Pure (no Phaser), so it can be unit-tested. Bresenham over integer cells,
 * inclusive of both endpoints.
 */

export interface GridCell {
  row: number;
  col: number;
}

export function gridLineCells(
  r0: number,
  c0: number,
  r1: number,
  c1: number
): GridCell[] {
  const cells: GridCell[] = [];
  let row = r0;
  let col = c0;
  const dRow = Math.abs(r1 - r0);
  const dCol = Math.abs(c1 - c0);
  const stepRow = r0 < r1 ? 1 : -1;
  const stepCol = c0 < c1 ? 1 : -1;
  let err = dRow - dCol;

  // Bounded iteration as a safety net (never loops forever on bad input).
  const maxSteps = dRow + dCol + 1;
  for (let i = 0; i <= maxSteps; i++) {
    cells.push({ row, col });
    if (row === r1 && col === c1) break;
    const e2 = 2 * err;
    if (e2 > -dCol) {
      err -= dCol;
      row += stepRow;
    }
    if (e2 < dRow) {
      err += dRow;
      col += stepCol;
    }
  }
  return cells;
}
