/**
 * Wall autotiling — pick a wall's sprite orientation from its neighbours so a
 * run of walls reads as one continuous fence.
 *
 * Two rendered orientations exist (straight along each isometric grid axis).
 * A wall with neighbours along the row axis uses the row-axis sprite; along the
 * col axis, the col-axis sprite. Corners are approximated with the row-axis
 * sprite, and an isolated wall uses the default (row-axis) sprite.
 *
 * Pure (no Phaser), so it can be unit-tested.
 */

export type WallVariant = 'rowAxis' | 'colAxis' | 'isolated';

/** Key for a grid cell, used in the set of wall positions. */
export function cellKey(row: number, col: number): string {
  return `${row},${col}`;
}

/**
 * Choose the orientation for a wall at (row, col) given the set of all wall
 * cell keys.
 */
export function wallVariant(walls: Set<string>, row: number, col: number): WallVariant {
  const hasRow = walls.has(cellKey(row - 1, col)) || walls.has(cellKey(row + 1, col));
  const hasCol = walls.has(cellKey(row, col - 1)) || walls.has(cellKey(row, col + 1));

  if (hasCol && !hasRow) return 'colAxis';
  if (hasRow && !hasCol) return 'rowAxis';
  if (hasRow && hasCol) return 'rowAxis'; // corner — approximated as a row run
  return 'isolated';
}
