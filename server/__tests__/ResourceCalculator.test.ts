/**
 * Tests for ResourceCalculator
 */

import { describe, it, expect } from 'vitest';
import type { BuildingType } from '@shared/types';
import { IBuilding } from '../src/models/Base';
import {
  getBuildingProductionRate,
  getTotalProductionRate,
  calculateResourcesGenerated,
  updateResources,
  canAfford,
  deductResources,
} from '../src/mechanics/ResourceCalculator';

// Helper to create test buildings
function createBuilding(
  type: BuildingType,
  level: number = 1,
  underConstruction: boolean = false
): IBuilding {
  const now = new Date();
  return {
    id: `${type}_test`,
    type,
    row: 0,
    col: 0,
    level,
    constructionStartedAt: underConstruction ? now : undefined,
    constructionEndsAt: underConstruction ? new Date(now.getTime() + 60000) : undefined,
  };
}

describe('ResourceCalculator', () => {
  describe('getBuildingProductionRate', () => {
    it('returns zero for non-producing buildings', () => {
      const townCenter = createBuilding('townCenter');
      const rate = getBuildingProductionRate(townCenter);

      expect(rate.food).toBe(0);
      expect(rate.gold).toBe(0);
      expect(rate.oil).toBe(0);
    });

    it('returns correct rate for farm at level 1', () => {
      const farm = createBuilding('farm', 1);
      const rate = getBuildingProductionRate(farm);

      expect(rate.food).toBe(100); // 100 food/hour at level 1
      expect(rate.gold).toBe(0);
      expect(rate.oil).toBe(0);
    });

    it('returns correct rate for gold mine at level 1', () => {
      const goldMine = createBuilding('goldMine', 1);
      const rate = getBuildingProductionRate(goldMine);

      expect(rate.food).toBe(0);
      expect(rate.gold).toBe(50); // 50 gold/hour at level 1
      expect(rate.oil).toBe(0);
    });

    it('returns correct rate for oil well at level 1', () => {
      const oilWell = createBuilding('oilWell', 1);
      const rate = getBuildingProductionRate(oilWell);

      expect(rate.food).toBe(0);
      expect(rate.gold).toBe(0);
      expect(rate.oil).toBe(25); // 25 oil/hour at level 1
    });

    it('increases rate with building level', () => {
      const farmL1 = createBuilding('farm', 1);
      const farmL2 = createBuilding('farm', 2);
      const farmL3 = createBuilding('farm', 3);

      const rateL1 = getBuildingProductionRate(farmL1);
      const rateL2 = getBuildingProductionRate(farmL2);
      const rateL3 = getBuildingProductionRate(farmL3);

      // Each level should increase production by 20% (multiplier = 1.2)
      expect(rateL2.food).toBeCloseTo(100 * 1.2, 1);
      expect(rateL3.food).toBeCloseTo(100 * 1.2 * 1.2, 1);
      expect(rateL1.food).toBeLessThan(rateL2.food);
      expect(rateL2.food).toBeLessThan(rateL3.food);
    });

    it('returns zero for buildings under construction', () => {
      const farm = createBuilding('farm', 1, true);
      const rate = getBuildingProductionRate(farm);

      expect(rate.food).toBe(0);
    });
  });

  describe('getTotalProductionRate', () => {
    it('returns zero for empty building list', () => {
      const rate = getTotalProductionRate([]);

      expect(rate.food).toBe(0);
      expect(rate.gold).toBe(0);
      expect(rate.oil).toBe(0);
    });

    it('sums production from multiple buildings', () => {
      const buildings = [
        createBuilding('farm', 1),
        createBuilding('farm', 1),
        createBuilding('goldMine', 1),
      ];

      const rate = getTotalProductionRate(buildings);

      expect(rate.food).toBe(200); // 2 farms * 100
      expect(rate.gold).toBe(50);  // 1 gold mine * 50
      expect(rate.oil).toBe(0);
    });

    it('excludes buildings under construction', () => {
      const buildings = [
        createBuilding('farm', 1, false),
        createBuilding('farm', 1, true), // Under construction
      ];

      const rate = getTotalProductionRate(buildings);

      expect(rate.food).toBe(100); // Only 1 active farm
    });
  });

  describe('calculateResourcesGenerated', () => {
    it('calculates resources for 1 hour', () => {
      const buildings = [createBuilding('farm', 1)];
      const oneHourMs = 60 * 60 * 1000;

      const generated = calculateResourcesGenerated(buildings, oneHourMs);

      expect(generated.food).toBe(100);
    });

    it('calculates resources for 30 minutes', () => {
      const buildings = [createBuilding('farm', 1)];
      const thirtyMinutesMs = 30 * 60 * 1000;

      const generated = calculateResourcesGenerated(buildings, thirtyMinutesMs);

      expect(generated.food).toBe(50);
    });

    it('calculates resources for multiple buildings over time', () => {
      const buildings = [
        createBuilding('farm', 1),
        createBuilding('goldMine', 1),
        createBuilding('oilWell', 1),
      ];
      const twoHoursMs = 2 * 60 * 60 * 1000;

      const generated = calculateResourcesGenerated(buildings, twoHoursMs);

      expect(generated.food).toBe(200);  // 100/hr * 2hrs
      expect(generated.gold).toBe(100);  // 50/hr * 2hrs
      expect(generated.oil).toBe(50);    // 25/hr * 2hrs
    });
  });

  describe('updateResources', () => {
    it('adds generated resources to current resources', () => {
      const current = { food: 100, gold: 100, oil: 0 };
      const buildings = [createBuilding('farm', 1)];
      const lastUpdated = new Date(Date.now() - 60 * 60 * 1000); // 1 hour ago

      const updated = updateResources(current, buildings, lastUpdated);

      expect(updated.food).toBe(200); // 100 + 100
      expect(updated.gold).toBe(100); // No change
      expect(updated.oil).toBe(0);    // No change
    });

    it('caps resources at maximum', () => {
      const current = { food: 9950, gold: 100, oil: 0 };
      const buildings = [createBuilding('farm', 1)];
      const lastUpdated = new Date(Date.now() - 60 * 60 * 1000); // 1 hour ago

      const updated = updateResources(current, buildings, lastUpdated);

      expect(updated.food).toBe(10000); // Capped at max
    });

    it('handles no time elapsed', () => {
      const current = { food: 100, gold: 100, oil: 0 };
      const buildings = [createBuilding('farm', 1)];
      const now = new Date();

      const updated = updateResources(current, buildings, now, now);

      expect(updated.food).toBe(100); // No change
    });

    it('handles negative time gracefully', () => {
      const current = { food: 100, gold: 100, oil: 0 };
      const buildings = [createBuilding('farm', 1)];
      const futureTime = new Date(Date.now() + 60000);

      const updated = updateResources(current, buildings, futureTime);

      expect(updated.food).toBe(100); // No change
    });
  });

  describe('canAfford', () => {
    it('returns true when player has enough resources', () => {
      const resources = { food: 500, gold: 500, oil: 100 };
      const cost = { food: 100, gold: 200 };

      expect(canAfford(resources, cost)).toBe(true);
    });

    it('returns false when player lacks food', () => {
      const resources = { food: 50, gold: 500, oil: 100 };
      const cost = { food: 100, gold: 200 };

      expect(canAfford(resources, cost)).toBe(false);
    });

    it('returns false when player lacks gold', () => {
      const resources = { food: 500, gold: 100, oil: 100 };
      const cost = { food: 100, gold: 200 };

      expect(canAfford(resources, cost)).toBe(false);
    });

    it('returns true for zero cost', () => {
      const resources = { food: 0, gold: 0, oil: 0 };
      const cost = {};

      expect(canAfford(resources, cost)).toBe(true);
    });
  });

  describe('deductResources', () => {
    it('deducts correct amounts', () => {
      const resources = { food: 500, gold: 500, oil: 100 };
      const cost = { food: 100, gold: 200 };

      const result = deductResources(resources, cost);

      expect(result.food).toBe(400);
      expect(result.gold).toBe(300);
      expect(result.oil).toBe(100); // Unchanged
    });

    it('handles partial costs', () => {
      const resources = { food: 500, gold: 500, oil: 100 };
      const cost = { gold: 50 };

      const result = deductResources(resources, cost);

      expect(result.food).toBe(500);
      expect(result.gold).toBe(450);
      expect(result.oil).toBe(100);
    });
  });
});
