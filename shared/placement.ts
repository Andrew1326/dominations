/**
 * Shared building placement rules.
 *
 * Ordinary buildings must keep a gap of BUILDING_SPACING empty cells between
 * them — they can't be placed flush against each other. Fences (walls, marked
 * `allowAdjacent`) are exempt: they may touch anything, and each other, so a
 * continuous fence line can be built.
 *
 * Pure (no DOM/DB), so the client ghost preview and the authoritative server
 * share exactly the same rule.
 */

import type { BuildingType } from './types';
import { BUILDINGS } from './constants';

/** Empty cells required between two ordinary (non-fence) buildings. */
export const BUILDING_SPACING = 1;

/** A placed building's type and top-left grid position. */
export interface PlacedFootprint {
  type: BuildingType;
  row: number;
  col: number;
}

/** Fences may sit flush; every other building needs spacing around it. */
export function requiresSpacing(type: BuildingType): boolean {
  return !BUILDINGS[type].allowAdjacent;
}

/**
 * True when placing `type` at (row, col) would sit within `spacing` cells of
 * `other` (overlap counts as within spacing). If either building is a fence,
 * the spacing rule does not apply and this returns false.
 */
export function withinSpacing(
  type: BuildingType,
  row: number,
  col: number,
  other: PlacedFootprint,
  spacing: number = BUILDING_SPACING
): boolean {
  if (!requiresSpacing(type) || !requiresSpacing(other.type)) return false;

  const a = BUILDINGS[type];
  const b = BUILDINGS[other.type];

  // Expand the proposed footprint by `spacing` on every side, then test overlap
  // with the existing footprint (half-open ranges).
  const aR0 = row - spacing;
  const aR1 = row + a.height + spacing;
  const aC0 = col - spacing;
  const aC1 = col + a.width + spacing;

  const bR0 = other.row;
  const bR1 = other.row + b.height;
  const bC0 = other.col;
  const bC1 = other.col + b.width;

  const rowsOverlap = aR0 < bR1 && bR0 < aR1;
  const colsOverlap = aC0 < bC1 && bC0 < aC1;
  return rowsOverlap && colsOverlap;
}

/**
 * The first existing building that is too close to the proposed placement, or
 * null if the spacing rule is satisfied (or `type` is a fence).
 */
export function findSpacingConflict(
  type: BuildingType,
  row: number,
  col: number,
  existing: PlacedFootprint[],
  spacing: number = BUILDING_SPACING
): PlacedFootprint | null {
  if (!requiresSpacing(type)) return null;
  for (const other of existing) {
    if (withinSpacing(type, row, col, other, spacing)) return other;
  }
  return null;
}
