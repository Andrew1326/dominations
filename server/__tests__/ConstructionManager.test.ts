/**
 * Tests for ConstructionManager
 */

import { describe, it, expect } from 'vitest';
import type { BuildingType } from '@shared/types';
import { IBuilding } from '../src/models/Base';
import {
  getBuildingCost,
  getBuildingRefund,
  getConstructionTime,
  isWithinBounds,
  checkOverlap,
  validatePlacement,
  startConstruction,
  isConstructionComplete,
  completeConstruction,
  getRemainingConstructionTime,
  processCompletedConstructions,
} from '../src/mechanics/ConstructionManager';
import { GRID_SIZE, BUILDING_REFUND_RATE, BUILDING_COSTS, BASE_RESOURCE_CAP, STARTING_RESOURCES } from '@shared/constants';

// Helper to create test buildings
function createBuilding(
  type: BuildingType,
  row: number,
  col: number,
  level: number = 1
): IBuilding {
  return {
    id: `${type}_test`,
    type,
    row,
    col,
    level,
  };
}

describe('ConstructionManager', () => {
  describe('getBuildingCost', () => {
    it('returns base cost for level 1', () => {
      const cost = getBuildingCost('farm');
      expect(cost.gold).toBe(150);
      expect(cost.food).toBeUndefined();
    });

    it('increases cost with level', () => {
      const costL1 = getBuildingCost('farm', 1);
      const costL2 = getBuildingCost('farm', 2);
      const costL3 = getBuildingCost('farm', 3);

      // Cost increases by 50% per level
      expect(costL2.gold).toBe(Math.floor(150 * 1.5));
      expect(costL3.gold).toBe(Math.floor(150 * 1.5 * 1.5));
    });

    it('costs gold only (no food or oil)', () => {
      const cost = getBuildingCost('townCenter');
      expect(cost.gold).toBe(1000);
      expect(cost.food).toBeUndefined();
      expect(cost.oil).toBeUndefined();
    });

    it('every building costs gold only', () => {
      for (const [type, cost] of Object.entries(BUILDING_COSTS)) {
        expect(cost.gold, `${type} should have a gold cost`).toBeGreaterThan(0);
        expect(cost.food, `${type} should not cost food`).toBeUndefined();
        expect(cost.oil, `${type} should not cost oil`).toBeUndefined();
      }
    });

    it('resource cap is at least the starting grant (so generation never clamps below start)', () => {
      expect(BASE_RESOURCE_CAP.food).toBeGreaterThanOrEqual(STARTING_RESOURCES.food);
      expect(BASE_RESOURCE_CAP.gold).toBeGreaterThanOrEqual(STARTING_RESOURCES.gold);
      expect(BASE_RESOURCE_CAP.oil).toBeGreaterThanOrEqual(STARTING_RESOURCES.oil);
    });
  });

  describe('getBuildingRefund', () => {
    it('refunds the configured fraction of a level 1 cost', () => {
      const cost = getBuildingCost('farm', 1);
      const refund = getBuildingRefund('farm', 1);
      expect(refund.gold).toBe(Math.floor((cost.gold ?? 0) * BUILDING_REFUND_RATE));
      expect(refund.food).toBe(0);
      expect(refund.oil).toBe(0);
    });

    it('refunds all resource types a building cost', () => {
      const cost = getBuildingCost('townCenter', 1);
      const refund = getBuildingRefund('townCenter', 1);
      expect(refund.gold).toBe(Math.floor((cost.gold ?? 0) * BUILDING_REFUND_RATE));
      expect(refund.food).toBe(Math.floor((cost.food ?? 0) * BUILDING_REFUND_RATE));
    });

    it('refunds the cumulative cost across upgrade levels', () => {
      const cumulativeGold =
        (getBuildingCost('farm', 1).gold ?? 0) + (getBuildingCost('farm', 2).gold ?? 0);
      const refund = getBuildingRefund('farm', 2);
      expect(refund.gold).toBe(Math.floor(cumulativeGold * BUILDING_REFUND_RATE));
    });

    it('never refunds more than was spent', () => {
      const cost = getBuildingCost('house', 1);
      const refund = getBuildingRefund('house', 1);
      expect(refund.gold).toBeLessThanOrEqual(cost.gold ?? 0);
      expect(refund.food).toBeLessThanOrEqual(cost.food ?? Infinity);
    });
  });

  describe('getConstructionTime', () => {
    it('returns base time for level 1', () => {
      const time = getConstructionTime('farm');
      expect(time).toBe(45); // 45 seconds for farm
    });

    it('increases time with level', () => {
      const timeL1 = getConstructionTime('farm', 1);
      const timeL2 = getConstructionTime('farm', 2);
      const timeL3 = getConstructionTime('farm', 3);

      expect(timeL2).toBeGreaterThan(timeL1);
      expect(timeL3).toBeGreaterThan(timeL2);
    });
  });

  describe('isWithinBounds', () => {
    it('returns true for valid positions', () => {
      expect(isWithinBounds(0, 0, 2, 2)).toBe(true);
      expect(isWithinBounds(10, 10, 2, 2)).toBe(true);
      expect(isWithinBounds(GRID_SIZE - 2, GRID_SIZE - 2, 2, 2)).toBe(true);
    });

    it('returns false for positions out of bounds', () => {
      expect(isWithinBounds(-1, 0, 2, 2)).toBe(false);
      expect(isWithinBounds(0, -1, 2, 2)).toBe(false);
      expect(isWithinBounds(GRID_SIZE - 1, 0, 2, 2)).toBe(false);
      expect(isWithinBounds(0, GRID_SIZE - 1, 2, 2)).toBe(false);
    });
  });

  describe('checkOverlap', () => {
    it('returns false for no overlap', () => {
      const existing = [createBuilding('farm', 0, 0)]; // 2x2 at (0,0)
      expect(checkOverlap(5, 5, 2, 2, existing)).toBe(false);
    });

    it('returns true for direct overlap', () => {
      const existing = [createBuilding('farm', 5, 5)]; // 2x2 at (5,5)
      expect(checkOverlap(5, 5, 2, 2, existing)).toBe(true);
    });

    it('returns true for partial overlap', () => {
      const existing = [createBuilding('farm', 5, 5)]; // 2x2 at (5,5) covers 5-6,5-6
      expect(checkOverlap(6, 5, 2, 2, existing)).toBe(true); // Overlaps at (6,5)
      expect(checkOverlap(5, 6, 2, 2, existing)).toBe(true); // Overlaps at (5,6)
    });

    it('returns false for adjacent buildings', () => {
      const existing = [createBuilding('farm', 5, 5)]; // 2x2 at (5,5) covers 5-6,5-6
      expect(checkOverlap(7, 5, 2, 2, existing)).toBe(false); // Next to
      expect(checkOverlap(5, 7, 2, 2, existing)).toBe(false); // Below
    });
  });

  describe('validatePlacement', () => {
    it('validates correct placement', () => {
      const result = validatePlacement('farm', 5, 5, []);
      expect(result.valid).toBe(true);
    });

    it('rejects out of bounds placement', () => {
      const result = validatePlacement('townCenter', GRID_SIZE - 1, GRID_SIZE - 1, []);
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Position out of bounds');
    });

    it('rejects overlapping placement', () => {
      const existing = [createBuilding('farm', 5, 5)];
      const result = validatePlacement('farm', 5, 5, existing);
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Position overlaps with existing building');
    });

    it('rejects an ordinary building placed flush against another', () => {
      const existing = [createBuilding('farm', 5, 5)]; // covers 5-6, 5-6
      const result = validatePlacement('house', 5, 7, existing); // flush to the right
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Too close to another building');
    });

    it('allows an ordinary building with a 1-cell gap', () => {
      const existing = [createBuilding('farm', 5, 5)];
      expect(validatePlacement('house', 5, 8, existing).valid).toBe(true);
    });

    it('allows a wall flush against a building (fences are exempt)', () => {
      const existing = [createBuilding('farm', 5, 5)];
      expect(validatePlacement('wall', 5, 7, existing).valid).toBe(true); // flush right
      expect(validatePlacement('wall', 7, 5, existing).valid).toBe(true); // flush below
    });

    it('allows a building flush against a wall, and walls flush together', () => {
      const wall = [createBuilding('wall', 5, 5)];
      expect(validatePlacement('farm', 6, 5, wall).valid).toBe(true); // building touching a wall
      expect(validatePlacement('wall', 5, 6, wall).valid).toBe(true); // wall touching a wall (fence line)
    });
  });

  describe('startConstruction', () => {
    it('starts construction with sufficient resources', () => {
      const resources = { food: 500, gold: 500, oil: 0 };
      const result = startConstruction('farm', 5, 5, resources, []);

      expect(result.success).toBe(true);
      expect(result.building).toBeDefined();
      expect(result.building!.type).toBe('farm');
      expect(result.building!.row).toBe(5);
      expect(result.building!.col).toBe(5);
      expect(result.building!.constructionEndsAt).toBeDefined();
      expect(result.newResources!.gold).toBe(350); // 500 - 150
    });

    it('fails with insufficient resources', () => {
      const resources = { food: 0, gold: 50, oil: 0 };
      const result = startConstruction('farm', 5, 5, resources, []);

      expect(result.success).toBe(false);
      expect(result.error).toBe('Insufficient resources');
    });

    it('fails with invalid placement', () => {
      const resources = { food: 500, gold: 500, oil: 0 };
      const existing = [createBuilding('farm', 5, 5)];
      const result = startConstruction('farm', 5, 5, resources, existing);

      expect(result.success).toBe(false);
      expect(result.error).toBe('Position overlaps with existing building');
    });
  });

  describe('isConstructionComplete', () => {
    it('returns true for buildings without construction timer', () => {
      const building = createBuilding('farm', 0, 0);
      expect(isConstructionComplete(building)).toBe(true);
    });

    it('returns false for buildings still under construction', () => {
      const building: IBuilding = {
        ...createBuilding('farm', 0, 0),
        constructionEndsAt: new Date(Date.now() + 60000), // 1 minute in future
      };
      expect(isConstructionComplete(building)).toBe(false);
    });

    it('returns true for completed construction', () => {
      const building: IBuilding = {
        ...createBuilding('farm', 0, 0),
        constructionEndsAt: new Date(Date.now() - 1000), // 1 second in past
      };
      expect(isConstructionComplete(building)).toBe(true);
    });
  });

  describe('getRemainingConstructionTime', () => {
    it('returns 0 for completed buildings', () => {
      const building = createBuilding('farm', 0, 0);
      expect(getRemainingConstructionTime(building)).toBe(0);
    });

    it('returns correct remaining time', () => {
      const now = new Date();
      const building: IBuilding = {
        ...createBuilding('farm', 0, 0),
        constructionEndsAt: new Date(now.getTime() + 30000), // 30 seconds
      };
      const remaining = getRemainingConstructionTime(building, now);
      expect(remaining).toBe(30);
    });
  });

  describe('processCompletedConstructions', () => {
    it('completes finished buildings', () => {
      const buildings: IBuilding[] = [
        {
          ...createBuilding('farm', 0, 0),
          constructionStartedAt: new Date(Date.now() - 60000),
          constructionEndsAt: new Date(Date.now() - 1000),
        },
      ];

      const { buildings: updated, completedIds } = processCompletedConstructions(buildings);

      expect(completedIds).toContain(buildings[0].id);
      expect(updated[0].constructionEndsAt).toBeUndefined();
    });

    it('keeps unfinished buildings unchanged', () => {
      const buildings: IBuilding[] = [
        {
          ...createBuilding('farm', 0, 0),
          constructionStartedAt: new Date(),
          constructionEndsAt: new Date(Date.now() + 60000),
        },
      ];

      const { buildings: updated, completedIds } = processCompletedConstructions(buildings);

      expect(completedIds).toHaveLength(0);
      expect(updated[0].constructionEndsAt).toBeDefined();
    });
  });
});
