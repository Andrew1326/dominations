/**
 * Tests for the shared building spacing rules.
 */

import { describe, it, expect } from 'vitest';
import {
  BUILDING_SPACING,
  requiresSpacing,
  withinSpacing,
  findSpacingConflict,
  PlacedFootprint,
} from '@shared/placement';

describe('placement spacing rules', () => {
  describe('requiresSpacing', () => {
    it('ordinary buildings require spacing', () => {
      expect(requiresSpacing('farm')).toBe(true);
      expect(requiresSpacing('house')).toBe(true);
      expect(requiresSpacing('townCenter')).toBe(true);
    });

    it('walls (fences) are exempt', () => {
      expect(requiresSpacing('wall')).toBe(false);
    });
  });

  describe('withinSpacing', () => {
    // farm is 2x2: existing farm at (5,5) covers rows/cols 5-6
    const existingFarm: PlacedFootprint = { type: 'farm', row: 5, col: 5 };

    it('flags a building placed flush (no gap) against another', () => {
      // directly below (rows 7-8) -> 0-cell gap
      expect(withinSpacing('farm', 7, 5, existingFarm)).toBe(true);
      // directly right (cols 7-8) -> 0-cell gap
      expect(withinSpacing('farm', 5, 7, existingFarm)).toBe(true);
    });

    it('flags diagonal (corner) adjacency', () => {
      expect(withinSpacing('farm', 7, 7, existingFarm)).toBe(true);
    });

    it('allows a building with at least a 1-cell gap', () => {
      expect(withinSpacing('farm', 8, 5, existingFarm)).toBe(false); // one empty row between
      expect(withinSpacing('farm', 5, 8, existingFarm)).toBe(false); // one empty col between
      expect(withinSpacing('farm', 8, 8, existingFarm)).toBe(false); // diagonal with a gap
    });

    it('never applies when the placed building is a fence', () => {
      expect(withinSpacing('wall', 7, 5, existingFarm)).toBe(false);
      expect(withinSpacing('wall', 5, 5, existingFarm)).toBe(false); // even overlapping (handled elsewhere)
    });

    it('never applies when the existing building is a fence', () => {
      const existingWall: PlacedFootprint = { type: 'wall', row: 5, col: 5 };
      expect(withinSpacing('farm', 6, 5, existingWall)).toBe(false); // flush against a wall is fine
    });
  });

  describe('findSpacingConflict', () => {
    const existing: PlacedFootprint[] = [{ type: 'farm', row: 5, col: 5 }];

    it('returns the conflicting building when too close', () => {
      expect(findSpacingConflict('house', 5, 7, existing)).toEqual(existing[0]);
    });

    it('returns null when the gap is respected', () => {
      expect(findSpacingConflict('house', 5, 8, existing)).toBeNull();
    });

    it('returns null for fences regardless of neighbours', () => {
      expect(findSpacingConflict('wall', 5, 7, existing)).toBeNull();
    });

    it('uses a spacing of one cell by default', () => {
      expect(BUILDING_SPACING).toBe(1);
    });
  });
});
