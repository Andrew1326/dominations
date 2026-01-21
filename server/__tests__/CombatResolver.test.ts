/**
 * Tests for CombatResolver
 */

import { describe, it, expect, beforeEach } from 'vitest';
import type { BuildingData, UnitType, TroopSlot } from '@shared/types';
import { GRID_SIZE, DEPLOY_ZONE_DEPTH } from '@shared/constants';
import {
  calculateBuildingHp,
  initializeBattleBuildings,
  calculateTotalBuildingHp,
  createUnit,
  isValidDeployPosition,
  gridDistance,
  getBuildingCenter,
  findTarget,
  isInRange,
  moveUnitTowards,
  calculateDamage,
  processTick,
  calculateDestructionPercent,
  calculateStars,
  calculateLoot,
  isBattleOver,
  createSimulation,
  deployUnit,
  runFullSimulation,
  validateTroops,
  BattleBuilding,
  BattleSimulation,
} from '../src/mechanics/CombatResolver';

// Helper to create test buildings
function createBuilding(
  id: string,
  type: BuildingData['type'],
  row: number,
  col: number,
  level: number = 1
): BuildingData {
  return { id, type, row, col, level };
}

describe('CombatResolver', () => {
  describe('calculateBuildingHp', () => {
    it('returns base HP for level 1', () => {
      const hp = calculateBuildingHp('townCenter', 1);
      expect(hp).toBe(2000); // Base HP from constants
    });

    it('increases HP with level', () => {
      const hpL1 = calculateBuildingHp('farm', 1);
      const hpL2 = calculateBuildingHp('farm', 2);
      const hpL3 = calculateBuildingHp('farm', 3);

      expect(hpL2).toBeGreaterThan(hpL1);
      expect(hpL3).toBeGreaterThan(hpL2);
    });
  });

  describe('initializeBattleBuildings', () => {
    it('converts buildings to battle buildings with HP', () => {
      const buildings = [
        createBuilding('b1', 'farm', 5, 5),
        createBuilding('b2', 'house', 10, 10),
      ];

      const battleBuildings = initializeBattleBuildings(buildings);

      expect(battleBuildings).toHaveLength(2);
      expect(battleBuildings[0].hp).toBe(battleBuildings[0].maxHp);
      expect(battleBuildings[0].destroyed).toBe(false);
    });

    it('filters out buildings under construction', () => {
      const buildings: BuildingData[] = [
        createBuilding('b1', 'farm', 5, 5),
        { ...createBuilding('b2', 'house', 10, 10), constructionEndsAt: Date.now() + 60000 },
      ];

      const battleBuildings = initializeBattleBuildings(buildings);

      expect(battleBuildings).toHaveLength(1);
      expect(battleBuildings[0].id).toBe('b1');
    });
  });

  describe('calculateTotalBuildingHp', () => {
    it('sums all building HP', () => {
      const battleBuildings: BattleBuilding[] = [
        { ...createBuilding('b1', 'farm', 0, 0), hp: 500, maxHp: 500, destroyed: false },
        { ...createBuilding('b2', 'house', 5, 5), hp: 400, maxHp: 400, destroyed: false },
      ];

      const total = calculateTotalBuildingHp(battleBuildings);

      expect(total).toBe(900);
    });
  });

  describe('createUnit', () => {
    it('creates a unit with correct stats', () => {
      const unit = createUnit('warrior', 5, 5);

      expect(unit.type).toBe('warrior');
      expect(unit.hp).toBe(100); // Warrior base HP
      expect(unit.maxHp).toBe(100);
      expect(unit.state).toBe('idle');
      expect(unit.row).toBe(5);
      expect(unit.col).toBe(5);
    });
  });

  describe('isValidDeployPosition', () => {
    const battleBuildings: BattleBuilding[] = [
      { ...createBuilding('b1', 'farm', 5, 5), hp: 500, maxHp: 500, destroyed: false },
    ];

    it('allows deployment in deploy zone', () => {
      // Top edge
      expect(isValidDeployPosition(0, 10, battleBuildings)).toBe(true);
      // Bottom edge
      expect(isValidDeployPosition(GRID_SIZE - 1, 10, battleBuildings)).toBe(true);
      // Left edge
      expect(isValidDeployPosition(10, 0, battleBuildings)).toBe(true);
      // Right edge
      expect(isValidDeployPosition(10, GRID_SIZE - 1, battleBuildings)).toBe(true);
    });

    it('rejects deployment outside deploy zone', () => {
      const centerPos = Math.floor(GRID_SIZE / 2);
      expect(isValidDeployPosition(centerPos, centerPos, battleBuildings)).toBe(false);
    });

    it('rejects deployment on buildings', () => {
      expect(isValidDeployPosition(0, 5, [
        { ...createBuilding('b1', 'farm', 0, 5), hp: 500, maxHp: 500, destroyed: false },
      ])).toBe(false);
    });

    it('rejects deployment outside grid', () => {
      expect(isValidDeployPosition(-1, 0, [])).toBe(false);
      expect(isValidDeployPosition(0, -1, [])).toBe(false);
      expect(isValidDeployPosition(GRID_SIZE, 0, [])).toBe(false);
    });
  });

  describe('gridDistance', () => {
    it('calculates correct distance', () => {
      expect(gridDistance(0, 0, 3, 4)).toBe(5); // 3-4-5 triangle
      expect(gridDistance(5, 5, 5, 5)).toBe(0);
      expect(gridDistance(0, 0, 0, 10)).toBe(10);
    });
  });

  describe('getBuildingCenter', () => {
    it('returns center of building', () => {
      const building: BattleBuilding = {
        ...createBuilding('b1', 'townCenter', 5, 5), // 3x3 building
        hp: 2000,
        maxHp: 2000,
        destroyed: false,
      };

      const center = getBuildingCenter(building);

      expect(center.row).toBe(6.5); // 5 + 3/2
      expect(center.col).toBe(6.5);
    });
  });

  describe('findTarget', () => {
    it('finds closest building', () => {
      const buildings: BattleBuilding[] = [
        { ...createBuilding('far', 'farm', 15, 15), hp: 500, maxHp: 500, destroyed: false },
        { ...createBuilding('near', 'house', 5, 5), hp: 400, maxHp: 400, destroyed: false },
      ];

      const unit = createUnit('warrior', 0, 0);
      const target = findTarget(unit, buildings);

      expect(target?.id).toBe('near');
    });

    it('returns null when no buildings left', () => {
      const buildings: BattleBuilding[] = [
        { ...createBuilding('b1', 'farm', 5, 5), hp: 0, maxHp: 500, destroyed: true },
      ];

      const unit = createUnit('warrior', 0, 0);
      const target = findTarget(unit, buildings);

      expect(target).toBeNull();
    });
  });

  describe('isInRange', () => {
    it('returns true when unit is in range', () => {
      const unit = createUnit('warrior', 5, 5); // Range 1
      const building: BattleBuilding = {
        ...createBuilding('b1', 'farm', 5, 6), // Adjacent
        hp: 500,
        maxHp: 500,
        destroyed: false,
      };

      expect(isInRange(unit, building)).toBe(true);
    });

    it('returns false when unit is out of range', () => {
      const unit = createUnit('warrior', 0, 0); // Range 1
      const building: BattleBuilding = {
        ...createBuilding('b1', 'farm', 10, 10),
        hp: 500,
        maxHp: 500,
        destroyed: false,
      };

      expect(isInRange(unit, building)).toBe(false);
    });

    it('accounts for archer range', () => {
      const unit = createUnit('archer', 0, 0); // Range 4
      const building: BattleBuilding = {
        ...createBuilding('b1', 'farm', 3, 0),
        hp: 500,
        maxHp: 500,
        destroyed: false,
      };

      expect(isInRange(unit, building)).toBe(true);
    });
  });

  describe('moveUnitTowards', () => {
    it('moves unit towards target', () => {
      const unit = createUnit('warrior', 0, 0);
      const initialRow = unit.row;
      const initialCol = unit.col;

      moveUnitTowards(unit, 10, 10, 0.5);

      expect(unit.row).toBeGreaterThan(initialRow);
      expect(unit.col).toBeGreaterThan(initialCol);
    });

    it('does not overshoot target', () => {
      const unit = createUnit('warrior', 0, 0);

      moveUnitTowards(unit, 0.1, 0.1, 10); // Large deltaTime

      expect(unit.row).toBeCloseTo(0.1);
      expect(unit.col).toBeCloseTo(0.1);
    });
  });

  describe('calculateDamage', () => {
    it('calculates damage per tick', () => {
      const unit = createUnit('warrior', 0, 0); // 20 damage, 1 attack/sec
      const damage = calculateDamage(unit, 1); // 1 second

      expect(damage).toBe(20);
    });

    it('scales with deltaTime', () => {
      const unit = createUnit('warrior', 0, 0);
      const damage = calculateDamage(unit, 0.5);

      expect(damage).toBe(10);
    });
  });

  describe('processTick', () => {
    let simulation: BattleSimulation;

    beforeEach(() => {
      simulation = {
        buildings: [
          { ...createBuilding('b1', 'farm', 5, 5), hp: 500, maxHp: 500, destroyed: false },
        ],
        units: [createUnit('warrior', 5, 4)], // Adjacent to building
        tick: 0,
        totalBuildingHp: 500,
        destroyedBuildingHp: 0,
        loot: { food: 0, gold: 0, oil: 0 },
        attackerResources: { food: 1000, gold: 1000, oil: 100 },
      };
    });

    it('processes unit attacks', () => {
      const initialHp = simulation.buildings[0].hp;

      processTick(simulation, 1);

      expect(simulation.buildings[0].hp).toBeLessThan(initialHp);
      expect(simulation.units[0].state).toBe('attacking');
    });

    it('increments tick counter', () => {
      processTick(simulation, 1);
      expect(simulation.tick).toBe(1);
    });

    it('marks building as destroyed when HP reaches 0', () => {
      simulation.buildings[0].hp = 10; // Low HP

      processTick(simulation, 1); // Should destroy it

      expect(simulation.buildings[0].destroyed).toBe(true);
      expect(simulation.buildings[0].hp).toBe(0);
      expect(simulation.destroyedBuildingHp).toBe(500);
    });
  });

  describe('calculateDestructionPercent', () => {
    it('calculates correct percentage', () => {
      const simulation: BattleSimulation = {
        buildings: [],
        units: [],
        tick: 0,
        totalBuildingHp: 1000,
        destroyedBuildingHp: 500,
        loot: { food: 0, gold: 0, oil: 0 },
        attackerResources: { food: 0, gold: 0, oil: 0 },
      };

      expect(calculateDestructionPercent(simulation)).toBe(50);
    });

    it('returns 100 for empty base', () => {
      const simulation: BattleSimulation = {
        buildings: [],
        units: [],
        tick: 0,
        totalBuildingHp: 0,
        destroyedBuildingHp: 0,
        loot: { food: 0, gold: 0, oil: 0 },
        attackerResources: { food: 0, gold: 0, oil: 0 },
      };

      expect(calculateDestructionPercent(simulation)).toBe(100);
    });
  });

  describe('calculateStars', () => {
    it('returns correct stars', () => {
      expect(calculateStars(0)).toBe(0);
      expect(calculateStars(49)).toBe(0);
      expect(calculateStars(50)).toBe(1);
      expect(calculateStars(74)).toBe(1);
      expect(calculateStars(75)).toBe(2);
      expect(calculateStars(99)).toBe(2);
      expect(calculateStars(100)).toBe(3);
    });
  });

  describe('calculateLoot', () => {
    it('calculates loot based on destruction', () => {
      const resources = { food: 1000, gold: 1000, oil: 100 };
      const loot = calculateLoot(50, resources); // 50% destruction, 20% loot rate

      // 50% * 20% = 10% of resources
      expect(loot.food).toBe(100);
      expect(loot.gold).toBe(100);
      expect(loot.oil).toBe(10);
    });

    it('returns zero loot for zero destruction', () => {
      const resources = { food: 1000, gold: 1000, oil: 100 };
      const loot = calculateLoot(0, resources);

      expect(loot.food).toBe(0);
      expect(loot.gold).toBe(0);
      expect(loot.oil).toBe(0);
    });
  });

  describe('isBattleOver', () => {
    it('returns true when all buildings destroyed', () => {
      const simulation: BattleSimulation = {
        buildings: [
          { ...createBuilding('b1', 'farm', 5, 5), hp: 0, maxHp: 500, destroyed: true },
        ],
        units: [createUnit('warrior', 0, 0)],
        tick: 0,
        totalBuildingHp: 500,
        destroyedBuildingHp: 500,
        loot: { food: 0, gold: 0, oil: 0 },
        attackerResources: { food: 0, gold: 0, oil: 0 },
      };

      expect(isBattleOver(simulation)).toBe(true);
    });

    it('returns true when all units dead', () => {
      const simulation: BattleSimulation = {
        buildings: [
          { ...createBuilding('b1', 'farm', 5, 5), hp: 500, maxHp: 500, destroyed: false },
        ],
        units: [{ ...createUnit('warrior', 0, 0), state: 'dead', hp: 0 }],
        tick: 0,
        totalBuildingHp: 500,
        destroyedBuildingHp: 0,
        loot: { food: 0, gold: 0, oil: 0 },
        attackerResources: { food: 0, gold: 0, oil: 0 },
      };

      expect(isBattleOver(simulation)).toBe(true);
    });

    it('returns false when battle ongoing', () => {
      const simulation: BattleSimulation = {
        buildings: [
          { ...createBuilding('b1', 'farm', 5, 5), hp: 500, maxHp: 500, destroyed: false },
        ],
        units: [createUnit('warrior', 0, 0)],
        tick: 0,
        totalBuildingHp: 500,
        destroyedBuildingHp: 0,
        loot: { food: 0, gold: 0, oil: 0 },
        attackerResources: { food: 0, gold: 0, oil: 0 },
      };

      expect(isBattleOver(simulation)).toBe(false);
    });
  });

  describe('createSimulation', () => {
    it('creates simulation from defender data', () => {
      const buildings = [createBuilding('b1', 'farm', 5, 5)];
      const resources = { food: 1000, gold: 1000, oil: 100 };

      const simulation = createSimulation(buildings, resources);

      expect(simulation.buildings).toHaveLength(1);
      expect(simulation.units).toHaveLength(0);
      expect(simulation.tick).toBe(0);
      expect(simulation.totalBuildingHp).toBeGreaterThan(0);
      expect(simulation.attackerResources).toEqual(resources);
    });
  });

  describe('deployUnit', () => {
    it('deploys unit in valid position', () => {
      const simulation = createSimulation([], { food: 0, gold: 0, oil: 0 });

      const unit = deployUnit(simulation, 'warrior', 0, 0);

      expect(unit).not.toBeNull();
      expect(simulation.units).toHaveLength(1);
    });

    it('rejects invalid position', () => {
      const buildings = [createBuilding('b1', 'farm', 0, 0)];
      const simulation = createSimulation(buildings, { food: 0, gold: 0, oil: 0 });

      const unit = deployUnit(simulation, 'warrior', 0, 0);

      expect(unit).toBeNull();
      expect(simulation.units).toHaveLength(0);
    });
  });

  describe('validateTroops', () => {
    it('validates valid troop composition', () => {
      const troops: TroopSlot[] = [
        { type: 'warrior', count: 5 },
        { type: 'archer', count: 3 },
      ];

      const result = validateTroops(troops, 20);

      expect(result.valid).toBe(true);
    });

    it('rejects empty troops', () => {
      const result = validateTroops([], 20);

      expect(result.valid).toBe(false);
      expect(result.error).toBe('No troops selected');
    });

    it('rejects too many troops', () => {
      const troops: TroopSlot[] = [{ type: 'warrior', count: 25 }];

      const result = validateTroops(troops, 20);

      expect(result.valid).toBe(false);
      expect(result.error).toContain('Too many troops');
    });

    it('rejects invalid unit type', () => {
      const troops: TroopSlot[] = [{ type: 'invalid' as UnitType, count: 5 }];

      const result = validateTroops(troops, 20);

      expect(result.valid).toBe(false);
      expect(result.error).toContain('Invalid unit type');
    });
  });

  describe('runFullSimulation', () => {
    it('completes simulation and returns results', () => {
      const buildings = [createBuilding('b1', 'farm', 10, 10)];
      const resources = { food: 1000, gold: 1000, oil: 100 };
      const simulation = createSimulation(buildings, resources);

      // Deploy units near the building
      deployUnit(simulation, 'warrior', 0, 10);
      deployUnit(simulation, 'warrior', 0, 11);

      const result = runFullSimulation(simulation);

      expect(result.destructionPercent).toBeGreaterThanOrEqual(0);
      expect(result.destructionPercent).toBeLessThanOrEqual(100);
      expect(result.stars).toBeGreaterThanOrEqual(0);
      expect(result.stars).toBeLessThanOrEqual(3);
    });
  });
});
