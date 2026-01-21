/**
 * CombatResolver - Server-authoritative combat simulation
 *
 * Handles the entire battle simulation including:
 * - Unit movement and pathfinding
 * - Target acquisition
 * - Damage calculation
 * - Building destruction tracking
 */

import type {
  UnitData,
  UnitType,
  BuildingData,
  BuildingType,
  Resources,
  BattleResult,
  TroopSlot,
} from '@shared/types';
import {
  UNITS,
  BUILDINGS,
  BATTLE_TICK_RATE,
  BATTLE_MAX_DURATION,
  STAR_THRESHOLDS,
  LOOT_PERCENTAGE,
  BUILDING_HP_MULTIPLIER,
  GRID_SIZE,
  DEPLOY_ZONE_DEPTH,
} from '@shared/constants';

// Internal battle building type with HP tracking
export interface BattleBuilding extends BuildingData {
  hp: number;
  maxHp: number;
  destroyed: boolean;
}

// Battle simulation state
export interface BattleSimulation {
  buildings: BattleBuilding[];
  units: UnitData[];
  tick: number;
  totalBuildingHp: number;
  destroyedBuildingHp: number;
  loot: Resources;
  attackerResources: Resources;  // Resources available to loot
}

/**
 * Calculate building HP based on type and level
 */
export function calculateBuildingHp(type: BuildingType, level: number): number {
  const baseHp = BUILDINGS[type].hp;
  return Math.floor(baseHp * Math.pow(BUILDING_HP_MULTIPLIER, level - 1));
}

/**
 * Initialize battle buildings from defender's base
 */
export function initializeBattleBuildings(
  buildings: BuildingData[]
): BattleBuilding[] {
  return buildings
    .filter((b) => !b.constructionEndsAt) // Only completed buildings
    .map((b) => {
      const hp = calculateBuildingHp(b.type, b.level);
      return {
        ...b,
        hp,
        maxHp: hp,
        destroyed: false,
      };
    });
}

/**
 * Calculate total HP of all buildings (for destruction percentage)
 */
export function calculateTotalBuildingHp(buildings: BattleBuilding[]): number {
  return buildings.reduce((sum, b) => sum + b.maxHp, 0);
}

/**
 * Generate unique unit ID
 */
let unitIdCounter = 0;
export function generateUnitId(): string {
  return `unit_${Date.now()}_${unitIdCounter++}`;
}

/**
 * Create a new unit from troop deployment
 */
export function createUnit(
  type: UnitType,
  row: number,
  col: number
): UnitData {
  const def = UNITS[type];
  return {
    id: generateUnitId(),
    type,
    hp: def.hp,
    maxHp: def.hp,
    state: 'idle',
    row,
    col,
  };
}

/**
 * Validate unit deployment position
 */
export function isValidDeployPosition(
  row: number,
  col: number,
  buildings: BattleBuilding[]
): boolean {
  // Must be within grid
  if (row < 0 || row >= GRID_SIZE || col < 0 || col >= GRID_SIZE) {
    return false;
  }

  // Must be in deploy zone (edges of the grid)
  const inDeployZone =
    row < DEPLOY_ZONE_DEPTH ||
    row >= GRID_SIZE - DEPLOY_ZONE_DEPTH ||
    col < DEPLOY_ZONE_DEPTH ||
    col >= GRID_SIZE - DEPLOY_ZONE_DEPTH;

  if (!inDeployZone) {
    return false;
  }

  // Cannot deploy on buildings
  for (const building of buildings) {
    if (building.destroyed) continue;
    const bDef = BUILDINGS[building.type];
    if (
      row >= building.row &&
      row < building.row + bDef.height &&
      col >= building.col &&
      col < building.col + bDef.width
    ) {
      return false;
    }
  }

  return true;
}

/**
 * Calculate distance between two grid positions
 */
export function gridDistance(
  r1: number,
  c1: number,
  r2: number,
  c2: number
): number {
  return Math.sqrt((r2 - r1) ** 2 + (c2 - c1) ** 2);
}

/**
 * Find the closest building center to a position
 */
export function getBuildingCenter(building: BattleBuilding): { row: number; col: number } {
  const def = BUILDINGS[building.type];
  return {
    row: building.row + def.height / 2,
    col: building.col + def.width / 2,
  };
}

/**
 * Find the best target for a unit based on its preferences
 */
export function findTarget(
  unit: UnitData,
  buildings: BattleBuilding[]
): BattleBuilding | null {
  const def = UNITS[unit.type];
  const aliveBuildings = buildings.filter((b) => !b.destroyed);

  if (aliveBuildings.length === 0) {
    return null;
  }

  // Filter by preference
  let candidates = aliveBuildings;
  if (def.preferredTarget === 'defensive') {
    const defensive = aliveBuildings.filter((b) => BUILDINGS[b.type].isDefensive);
    if (defensive.length > 0) {
      candidates = defensive;
    }
  }

  // Find closest target
  let closest: BattleBuilding | null = null;
  let closestDist = Infinity;

  for (const building of candidates) {
    const center = getBuildingCenter(building);
    const dist = gridDistance(unit.row, unit.col, center.row, center.col);
    if (dist < closestDist) {
      closestDist = dist;
      closest = building;
    }
  }

  return closest;
}

/**
 * Check if unit is in range to attack target building
 */
export function isInRange(unit: UnitData, building: BattleBuilding): boolean {
  const def = UNITS[unit.type];
  const bDef = BUILDINGS[building.type];

  // Check distance to closest edge of building
  const closestRow = Math.max(building.row, Math.min(unit.row, building.row + bDef.height - 1));
  const closestCol = Math.max(building.col, Math.min(unit.col, building.col + bDef.width - 1));
  const dist = gridDistance(unit.row, unit.col, closestRow, closestCol);

  return dist <= def.range;
}

/**
 * Move unit towards a target position
 */
export function moveUnitTowards(
  unit: UnitData,
  targetRow: number,
  targetCol: number,
  deltaTime: number
): void {
  const def = UNITS[unit.type];
  const speed = def.moveSpeed * deltaTime;

  const dx = targetCol - unit.col;
  const dy = targetRow - unit.row;
  const dist = Math.sqrt(dx * dx + dy * dy);

  if (dist <= speed) {
    unit.row = targetRow;
    unit.col = targetCol;
  } else {
    unit.col += (dx / dist) * speed;
    unit.row += (dy / dist) * speed;
  }
}

/**
 * Calculate damage dealt per tick
 */
export function calculateDamage(unit: UnitData, deltaTime: number): number {
  const def = UNITS[unit.type];
  return def.damage * def.attackSpeed * deltaTime;
}

/**
 * Process a single simulation tick
 */
export function processTick(
  simulation: BattleSimulation,
  deltaTime: number
): void {
  const aliveUnits = simulation.units.filter((u) => u.state !== 'dead');

  for (const unit of aliveUnits) {
    // Find or validate target
    let target = unit.targetId
      ? simulation.buildings.find((b) => b.id === unit.targetId && !b.destroyed)
      : null;

    if (!target) {
      target = findTarget(unit, simulation.buildings);
      if (target) {
        unit.targetId = target.id;
        const center = getBuildingCenter(target);
        unit.targetRow = center.row;
        unit.targetCol = center.col;
      }
    }

    if (!target) {
      // No targets left, unit becomes idle
      unit.state = 'idle';
      unit.targetId = undefined;
      unit.targetRow = undefined;
      unit.targetCol = undefined;
      continue;
    }

    // Check if in range
    if (isInRange(unit, target)) {
      // Attack
      unit.state = 'attacking';
      const damage = calculateDamage(unit, deltaTime);
      target.hp -= damage;

      if (target.hp <= 0) {
        target.hp = 0;
        target.destroyed = true;
        simulation.destroyedBuildingHp += target.maxHp;
        unit.targetId = undefined;
        unit.targetRow = undefined;
        unit.targetCol = undefined;
      }
    } else {
      // Move towards target
      unit.state = 'moving';
      const center = getBuildingCenter(target);
      moveUnitTowards(unit, center.row, center.col, deltaTime);
    }
  }

  simulation.tick++;
}

/**
 * Calculate destruction percentage
 */
export function calculateDestructionPercent(simulation: BattleSimulation): number {
  if (simulation.totalBuildingHp === 0) return 100;
  return Math.floor((simulation.destroyedBuildingHp / simulation.totalBuildingHp) * 100);
}

/**
 * Calculate stars based on destruction percentage
 */
export function calculateStars(destructionPercent: number): number {
  if (destructionPercent >= STAR_THRESHOLDS.three) return 3;
  if (destructionPercent >= STAR_THRESHOLDS.two) return 2;
  if (destructionPercent >= STAR_THRESHOLDS.one) return 1;
  return 0;
}

/**
 * Calculate loot based on destruction and available resources
 */
export function calculateLoot(
  destructionPercent: number,
  defenderResources: Resources
): Resources {
  const lootFactor = (destructionPercent / 100) * LOOT_PERCENTAGE;
  return {
    food: Math.floor(defenderResources.food * lootFactor),
    gold: Math.floor(defenderResources.gold * lootFactor),
    oil: Math.floor(defenderResources.oil * lootFactor),
  };
}

/**
 * Check if battle is over
 */
export function isBattleOver(simulation: BattleSimulation): boolean {
  // All buildings destroyed
  const allDestroyed = simulation.buildings.every((b) => b.destroyed);
  if (allDestroyed) return true;

  // All units dead or no targets left
  const aliveUnits = simulation.units.filter((u) => u.state !== 'dead');
  if (aliveUnits.length === 0) return true;

  // Time limit reached
  const maxTicks = BATTLE_MAX_DURATION * BATTLE_TICK_RATE;
  if (simulation.tick >= maxTicks) return true;

  return false;
}

/**
 * Create initial simulation state
 */
export function createSimulation(
  defenderBuildings: BuildingData[],
  defenderResources: Resources
): BattleSimulation {
  const buildings = initializeBattleBuildings(defenderBuildings);
  return {
    buildings,
    units: [],
    tick: 0,
    totalBuildingHp: calculateTotalBuildingHp(buildings),
    destroyedBuildingHp: 0,
    loot: { food: 0, gold: 0, oil: 0 },
    attackerResources: defenderResources,
  };
}

/**
 * Deploy a unit into the simulation
 */
export function deployUnit(
  simulation: BattleSimulation,
  type: UnitType,
  row: number,
  col: number
): UnitData | null {
  if (!isValidDeployPosition(row, col, simulation.buildings)) {
    return null;
  }

  const unit = createUnit(type, row, col);
  simulation.units.push(unit);
  return unit;
}

/**
 * Run the full simulation and return the result
 */
export function runFullSimulation(
  simulation: BattleSimulation
): { destructionPercent: number; stars: number; loot: Resources } {
  const deltaTime = 1 / BATTLE_TICK_RATE;

  while (!isBattleOver(simulation)) {
    processTick(simulation, deltaTime);
  }

  const destructionPercent = calculateDestructionPercent(simulation);
  const stars = calculateStars(destructionPercent);
  const loot = calculateLoot(destructionPercent, simulation.attackerResources);

  return { destructionPercent, stars, loot };
}

/**
 * Validate troop composition for battle
 */
export function validateTroops(
  troops: TroopSlot[],
  maxTroops: number
): { valid: boolean; error?: string } {
  const totalTroops = troops.reduce((sum, slot) => sum + slot.count, 0);

  if (totalTroops === 0) {
    return { valid: false, error: 'No troops selected' };
  }

  if (totalTroops > maxTroops) {
    return { valid: false, error: `Too many troops: ${totalTroops}/${maxTroops}` };
  }

  for (const slot of troops) {
    if (!UNITS[slot.type]) {
      return { valid: false, error: `Invalid unit type: ${slot.type}` };
    }
    if (slot.count < 0) {
      return { valid: false, error: 'Invalid troop count' };
    }
  }

  return { valid: true };
}
