/**
 * Game constants for OpenCivilizations
 */

import type {
  Age, Nation, NationDefinition, AgeDefinition,
  BuildingDefinition, BuildingType, NationBonusType,
  ResourceCost, Resources, UnitDefinition, UnitType,
} from './types';

// ============================================================
// Grid Configuration
// ============================================================

export const GRID_SIZE = 40; // 40x40 grid for more building space
export const TILE_WIDTH = 64;
export const TILE_HEIGHT = 32;
export const TILE_WIDTH_HALF = TILE_WIDTH / 2;
export const TILE_HEIGHT_HALF = TILE_HEIGHT / 2;

// Cost multiplier per level (e.g., level 2 costs 1.5x level 1)
export const UPGRADE_COST_MULTIPLIER = 1.5;

// ============================================================
// Age Definitions
// ============================================================

export const AGE_ORDER: Age[] = [
  'stone', 'bronze', 'iron', 'classical', 'medieval',
  'gunpowder', 'enlightenment', 'industrial', 'modern', 'digital',
];

export const AGES: Record<Age, AgeDefinition> = {
  stone: {
    id: 'stone',
    name: 'Stone Age',
    era: 'Ancient',
    order: 0,
    unlocksBuildings: ['townCenter', 'house', 'farm', 'storage', 'wall'],
    advanceCost: {},
    advanceTime: 0,
    resourceCapMultiplier: 1.0,
    buildingStatMultiplier: 1.0,
  },
  bronze: {
    id: 'bronze',
    name: 'Bronze Age',
    era: 'Ancient',
    order: 1,
    unlocksBuildings: ['goldMine', 'barracks', 'tower'],
    advanceCost: { food: 500, gold: 300 },
    advanceTime: 300,
    resourceCapMultiplier: 1.5,
    buildingStatMultiplier: 1.2,
  },
  iron: {
    id: 'iron',
    name: 'Iron Age',
    era: 'Ancient',
    order: 2,
    unlocksBuildings: ['blacksmith', 'temple'],
    advanceCost: { food: 1500, gold: 1000 },
    advanceTime: 900,
    resourceCapMultiplier: 2.0,
    buildingStatMultiplier: 1.5,
  },
  classical: {
    id: 'classical',
    name: 'Classical Age',
    era: 'Classical',
    order: 3,
    unlocksBuildings: ['library', 'market', 'stable'],
    advanceCost: { food: 4000, gold: 3000 },
    advanceTime: 1800,
    resourceCapMultiplier: 3.0,
    buildingStatMultiplier: 2.0,
  },
  medieval: {
    id: 'medieval',
    name: 'Medieval Age',
    era: 'Medieval',
    order: 4,
    unlocksBuildings: ['castle'],
    advanceCost: { food: 10000, gold: 8000 },
    advanceTime: 3600,
    resourceCapMultiplier: 4.0,
    buildingStatMultiplier: 3.0,
  },
  gunpowder: {
    id: 'gunpowder',
    name: 'Gunpowder Age',
    era: 'Early Modern',
    order: 5,
    unlocksBuildings: [],
    advanceCost: { food: 25000, gold: 20000 },
    advanceTime: 7200,
    resourceCapMultiplier: 5.5,
    buildingStatMultiplier: 4.0,
  },
  enlightenment: {
    id: 'enlightenment',
    name: 'Enlightenment Age',
    era: 'Early Modern',
    order: 6,
    unlocksBuildings: ['university'],
    advanceCost: { food: 50000, gold: 40000 },
    advanceTime: 14400,
    resourceCapMultiplier: 7.0,
    buildingStatMultiplier: 5.5,
  },
  industrial: {
    id: 'industrial',
    name: 'Industrial Age',
    era: 'Modern',
    order: 7,
    unlocksBuildings: ['oilWell', 'factory'],
    advanceCost: { food: 100000, gold: 80000 },
    advanceTime: 28800,
    resourceCapMultiplier: 10.0,
    buildingStatMultiplier: 7.0,
  },
  modern: {
    id: 'modern',
    name: 'Modern Age',
    era: 'Modern',
    order: 8,
    unlocksBuildings: ['airfield'],
    advanceCost: { food: 200000, gold: 150000, oil: 50000 },
    advanceTime: 57600,
    resourceCapMultiplier: 15.0,
    buildingStatMultiplier: 10.0,
  },
  digital: {
    id: 'digital',
    name: 'Digital Age',
    era: 'Contemporary',
    order: 9,
    unlocksBuildings: ['dataCentre'],
    advanceCost: { food: 500000, gold: 400000, oil: 200000 },
    advanceTime: 86400,
    resourceCapMultiplier: 20.0,
    buildingStatMultiplier: 14.0,
  },
};

// ============================================================
// Nation Definitions
// ============================================================

export const NATIONS: Record<Nation, NationDefinition> = {
  romans: {
    id: 'romans',
    name: 'Romans',
    description: 'Masters of engineering and infrastructure.',
    colorPalette: { primary: '#8B0000', secondary: '#DAA520', accent: '#FFFFF0' },
    bonuses: [
      { type: 'buildSpeed', value: 15, description: '15% faster construction' },
      { type: 'buildingHp', value: 10, description: '10% more building HP' },
    ],
  },
  greeks: {
    id: 'greeks',
    name: 'Greeks',
    description: 'Scholars and strategists with cultural dominance.',
    colorPalette: { primary: '#1E90FF', secondary: '#FFFFFF', accent: '#FFD700' },
    bonuses: [
      { type: 'resourceProduction', value: 15, description: '15% more resource production' },
      { type: 'combatDamage', value: 5, description: '5% more troop damage' },
    ],
  },
  egyptians: {
    id: 'egyptians',
    name: 'Egyptians',
    description: 'Builders of wonders with vast resource stores.',
    colorPalette: { primary: '#C5A033', secondary: '#2E1A0E', accent: '#00CED1' },
    bonuses: [
      { type: 'storageCapacity', value: 20, description: '20% more resource storage' },
      { type: 'buildSpeed', value: 10, description: '10% faster construction' },
    ],
  },
  chinese: {
    id: 'chinese',
    name: 'Chinese',
    description: 'Innovative civilization with economic strength.',
    colorPalette: { primary: '#CC0000', secondary: '#FFD700', accent: '#1A1A1A' },
    bonuses: [
      { type: 'resourceProduction', value: 10, description: '10% more resource production' },
      { type: 'storageCapacity', value: 10, description: '10% more resource storage' },
    ],
  },
  japanese: {
    id: 'japanese',
    name: 'Japanese',
    description: 'Disciplined warriors with fast-training armies.',
    colorPalette: { primary: '#BC002D', secondary: '#FFFFFF', accent: '#1B1B1B' },
    bonuses: [
      { type: 'unitTraining', value: 15, description: '15% faster unit training' },
      { type: 'combatDamage', value: 10, description: '10% more troop damage' },
    ],
  },
  vikings: {
    id: 'vikings',
    name: 'Vikings',
    description: 'Fierce raiders who plunder enemy riches.',
    colorPalette: { primary: '#2F4F4F', secondary: '#8B4513', accent: '#C0C0C0' },
    bonuses: [
      { type: 'lootBonus', value: 20, description: '20% more loot from attacks' },
      { type: 'combatDamage', value: 8, description: '8% more troop damage' },
    ],
  },
  british: {
    id: 'british',
    name: 'British',
    description: 'A balanced empire with strong defenses.',
    colorPalette: { primary: '#00247D', secondary: '#CF142B', accent: '#FFFFFF' },
    bonuses: [
      { type: 'buildingHp', value: 15, description: '15% more building HP' },
      { type: 'resourceProduction', value: 5, description: '5% more resource production' },
    ],
  },
  persians: {
    id: 'persians',
    name: 'Persians',
    description: 'Wealthy empire with grand economic power.',
    colorPalette: { primary: '#4B0082', secondary: '#DAA520', accent: '#40E0D0' },
    bonuses: [
      { type: 'resourceProduction', value: 20, description: '20% more resource production' },
    ],
  },
};

// ============================================================
// Age-Aware Building Definitions
// ============================================================

// Per-age building overrides. Buildings inherit from the most recent
// age that defines them (walk backward through AGE_ORDER).
export const BUILDING_DEFS_BY_AGE: Record<Age, Partial<Record<BuildingType, BuildingDefinition>>> = {
  stone: {
    townCenter: { type: 'townCenter', name: 'Town Center', width: 3, height: 3, color: 0x8B4513, maxLevel: 3, buildTime: 60, hp: 2000, availableFrom: 'stone' },
    house: { type: 'house', name: 'House', width: 2, height: 2, color: 0x4169E1, maxLevel: 3, buildTime: 30, hp: 400, availableFrom: 'stone' },
    farm: { type: 'farm', name: 'Farm', width: 2, height: 2, color: 0x228B22, maxLevel: 3, buildTime: 45, hp: 500, produces: 'food', productionRate: 100, availableFrom: 'stone' },
    storage: { type: 'storage', name: 'Storage Pit', width: 2, height: 2, color: 0x8B7355, maxLevel: 3, buildTime: 40, hp: 600, availableFrom: 'stone' },
    wall: { type: 'wall', name: 'Wall', width: 1, height: 1, color: 0x808080, maxLevel: 3, buildTime: 10, hp: 300, isDefensive: true, availableFrom: 'stone' },
  },
  bronze: {
    townCenter: { type: 'townCenter', name: 'Town Center', width: 3, height: 3, color: 0x8B4513, maxLevel: 5, buildTime: 120, hp: 3500, availableFrom: 'stone' },
    goldMine: { type: 'goldMine', name: 'Gold Mine', width: 2, height: 2, color: 0xFFD700, maxLevel: 5, buildTime: 60, hp: 500, produces: 'gold', productionRate: 50, availableFrom: 'bronze' },
    barracks: { type: 'barracks', name: 'Barracks', width: 3, height: 3, color: 0xB22222, maxLevel: 5, buildTime: 90, hp: 800, availableFrom: 'bronze' },
    tower: { type: 'tower', name: 'Watch Tower', width: 1, height: 1, color: 0x696969, maxLevel: 5, buildTime: 60, hp: 700, isDefensive: true, availableFrom: 'bronze' },
  },
  iron: {
    townCenter: { type: 'townCenter', name: 'Town Center', width: 3, height: 3, color: 0x8B4513, maxLevel: 6, buildTime: 180, hp: 5000, availableFrom: 'stone' },
    blacksmith: { type: 'blacksmith', name: 'Blacksmith', width: 2, height: 2, color: 0x4A4A4A, maxLevel: 5, buildTime: 120, hp: 600, availableFrom: 'iron' },
    temple: { type: 'temple', name: 'Temple', width: 3, height: 3, color: 0xDEB887, maxLevel: 5, buildTime: 180, hp: 1000, availableFrom: 'iron' },
  },
  classical: {
    townCenter: { type: 'townCenter', name: 'Town Center', width: 3, height: 3, color: 0x8B4513, maxLevel: 8, buildTime: 300, hp: 7000, availableFrom: 'stone' },
    library: { type: 'library', name: 'Library', width: 2, height: 3, color: 0xF5DEB3, maxLevel: 5, buildTime: 240, hp: 800, availableFrom: 'classical' },
    market: { type: 'market', name: 'Market', width: 3, height: 2, color: 0xDAA520, maxLevel: 5, buildTime: 150, hp: 600, availableFrom: 'classical' },
    stable: { type: 'stable', name: 'Stable', width: 3, height: 2, color: 0xA0522D, maxLevel: 5, buildTime: 120, hp: 700, availableFrom: 'classical' },
  },
  medieval: {
    townCenter: { type: 'townCenter', name: 'Town Center', width: 3, height: 3, color: 0x8B4513, maxLevel: 10, buildTime: 600, hp: 10000, availableFrom: 'stone' },
    castle: { type: 'castle', name: 'Castle', width: 4, height: 4, color: 0x708090, maxLevel: 5, buildTime: 900, hp: 5000, isDefensive: true, availableFrom: 'medieval' },
  },
  gunpowder: {
    townCenter: { type: 'townCenter', name: 'Town Center', width: 3, height: 3, color: 0x8B4513, maxLevel: 12, buildTime: 900, hp: 14000, availableFrom: 'stone' },
    tower: { type: 'tower', name: 'Cannon Tower', width: 2, height: 2, color: 0x696969, maxLevel: 8, buildTime: 300, hp: 2000, isDefensive: true, availableFrom: 'bronze' },
  },
  enlightenment: {
    townCenter: { type: 'townCenter', name: 'Town Center', width: 3, height: 3, color: 0x8B4513, maxLevel: 14, buildTime: 1200, hp: 18000, availableFrom: 'stone' },
    university: { type: 'university', name: 'University', width: 3, height: 3, color: 0x800020, maxLevel: 5, buildTime: 600, hp: 1200, availableFrom: 'enlightenment' },
  },
  industrial: {
    townCenter: { type: 'townCenter', name: 'Town Center', width: 3, height: 3, color: 0x8B4513, maxLevel: 16, buildTime: 1800, hp: 25000, availableFrom: 'stone' },
    oilWell: { type: 'oilWell', name: 'Oil Well', width: 2, height: 2, color: 0x1C1C1C, maxLevel: 10, buildTime: 120, hp: 600, produces: 'oil', productionRate: 25, availableFrom: 'industrial' },
    factory: { type: 'factory', name: 'Factory', width: 3, height: 3, color: 0x5C4033, maxLevel: 5, buildTime: 900, hp: 1500, availableFrom: 'industrial' },
  },
  modern: {
    townCenter: { type: 'townCenter', name: 'Town Center', width: 3, height: 3, color: 0x8B4513, maxLevel: 18, buildTime: 2700, hp: 35000, availableFrom: 'stone' },
    airfield: { type: 'airfield', name: 'Airfield', width: 4, height: 4, color: 0x4682B4, maxLevel: 5, buildTime: 1800, hp: 2000, availableFrom: 'modern' },
  },
  digital: {
    townCenter: { type: 'townCenter', name: 'Town Center', width: 3, height: 3, color: 0x8B4513, maxLevel: 20, buildTime: 3600, hp: 50000, availableFrom: 'stone' },
    dataCentre: { type: 'dataCentre', name: 'Data Centre', width: 3, height: 3, color: 0x00CED1, maxLevel: 5, buildTime: 2400, hp: 2500, availableFrom: 'digital' },
  },
};

// Age-aware building costs (per-age overrides; walk backward for fallback)
export const BUILDING_COSTS_BY_AGE: Record<Age, Partial<Record<BuildingType, ResourceCost>>> = {
  stone: {
    townCenter: { gold: 1000, food: 500 },
    house: { gold: 100, food: 50 },
    farm: { gold: 150 },
    storage: { gold: 200, food: 100 },
    wall: { gold: 50 },
  },
  bronze: {
    goldMine: { gold: 200, food: 100 },
    barracks: { gold: 400, food: 200 },
    tower: { gold: 300, food: 150 },
  },
  iron: {
    blacksmith: { gold: 500, food: 300 },
    temple: { gold: 800, food: 500 },
  },
  classical: {
    library: { gold: 1000, food: 600 },
    market: { gold: 600, food: 400 },
    stable: { gold: 700, food: 500 },
  },
  medieval: {
    castle: { gold: 5000, food: 3000 },
  },
  gunpowder: {},
  enlightenment: {
    university: { gold: 8000, food: 5000 },
  },
  industrial: {
    oilWell: { gold: 500, food: 200 },
    factory: { gold: 10000, food: 6000, oil: 2000 },
  },
  modern: {
    airfield: { gold: 20000, food: 10000, oil: 8000 },
  },
  digital: {
    dataCentre: { gold: 50000, food: 20000, oil: 15000 },
  },
};

// ============================================================
// Age/Nation Helper Functions
// ============================================================

/** Resolve a building definition by walking backward through ages. */
export function getBuildingDefForAge(age: Age, type: BuildingType): BuildingDefinition | null {
  const idx = AGE_ORDER.indexOf(age);
  for (let i = idx; i >= 0; i--) {
    const def = BUILDING_DEFS_BY_AGE[AGE_ORDER[i]][type];
    if (def) return def;
  }
  return null;
}

/** Returns all building types available at a given age (cumulative). */
export function getAvailableBuildings(age: Age): BuildingType[] {
  const idx = AGE_ORDER.indexOf(age);
  const available = new Set<BuildingType>();
  for (let i = 0; i <= idx; i++) {
    for (const bt of AGES[AGE_ORDER[i]].unlocksBuildings) {
      available.add(bt);
    }
  }
  return Array.from(available);
}

/** Resolve building cost by walking backward through ages. */
export function getBuildingCostForAge(age: Age, type: BuildingType): ResourceCost | null {
  const idx = AGE_ORDER.indexOf(age);
  for (let i = idx; i >= 0; i--) {
    const cost = BUILDING_COSTS_BY_AGE[AGE_ORDER[i]][type];
    if (cost) return cost;
  }
  return null;
}

/** Apply a nation's percentage bonus to a base value. */
export function applyNationBonus(baseValue: number, nation: Nation, bonusType: NationBonusType): number {
  const bonuses = NATIONS[nation].bonuses.filter(b => b.type === bonusType);
  const totalPercent = bonuses.reduce((sum, b) => sum + b.value, 0);
  return Math.round(baseValue * (1 + totalPercent / 100));
}

// ============================================================
// Backward-Compatible Flat Records
// ============================================================

const ALL_BUILDING_TYPES: BuildingType[] = [
  'townCenter', 'house', 'farm', 'goldMine', 'oilWell',
  'barracks', 'wall', 'tower', 'storage',
  'blacksmith', 'market', 'temple', 'library',
  'stable', 'castle', 'university', 'factory',
  'airfield', 'dataCentre',
];

// Flat building definitions — each building resolves to its earliest-age definition.
export const BUILDINGS: Record<BuildingType, BuildingDefinition> = (() => {
  const result = {} as Record<BuildingType, BuildingDefinition>;
  for (const bt of ALL_BUILDING_TYPES) {
    for (const age of AGE_ORDER) {
      const def = BUILDING_DEFS_BY_AGE[age][bt];
      if (def) { result[bt] = def; break; }
    }
  }
  return result;
})();

// Flat building costs — each building resolves to its earliest-age cost.
export const BUILDING_COSTS: Record<BuildingType, ResourceCost> = (() => {
  const result = {} as Record<BuildingType, ResourceCost>;
  for (const bt of ALL_BUILDING_TYPES) {
    for (const age of AGE_ORDER) {
      const cost = BUILDING_COSTS_BY_AGE[age][bt];
      if (cost) { result[bt] = cost; break; }
    }
  }
  return result;
})();

// ============================================================
// Resource Configuration
// ============================================================

// Starting resources for new players
export const STARTING_RESOURCES: Resources = {
  food: 500,
  gold: 500,
  oil: 0,
};

// Maximum resource storage (can be increased by buildings)
export const BASE_RESOURCE_CAP: Resources = {
  food: 10000,
  gold: 10000,
  oil: 5000,
};

// Production rate multiplier per building level
export const PRODUCTION_RATE_MULTIPLIER = 1.2; // 20% increase per level

// ============================================================
// Time Configuration
// ============================================================

// Build time multiplier per level
export const BUILD_TIME_MULTIPLIER = 1.3; // 30% increase per level

// Resource update interval on server (milliseconds)
export const RESOURCE_UPDATE_INTERVAL = 60000; // 1 minute

// ============================================================
// Colors
// ============================================================

export const GRID_LINE_COLOR = 0x444444;
export const VALID_PLACEMENT_COLOR = 0x00FF00;
export const INVALID_PLACEMENT_COLOR = 0xFF0000;
export const GRID_FILL_COLOR = 0x1a1a2e;
export const CONSTRUCTION_COLOR = 0xFFFF00; // Yellow for buildings under construction

// ============================================================
// Storage Keys (Client-side)
// ============================================================

export const STORAGE_KEY = 'opencivilizations_base_layout';
export const AUTH_TOKEN_KEY = 'opencivilizations_auth_token';

// ============================================================
// Server Configuration
// ============================================================

export const DEFAULT_SERVER_PORT = 2567;
export const DEFAULT_SERVER_URL = 'ws://localhost:2567';

// ============================================================
// Unit Definitions
// ============================================================

export const UNITS: Record<UnitType, UnitDefinition> = {
  warrior: {
    type: 'warrior',
    name: 'Warrior',
    hp: 100,
    damage: 20,
    attackSpeed: 1,        // 1 attack per second
    range: 1,              // Melee range
    moveSpeed: 2,          // 2 tiles per second
    trainingTime: 30,
    preferredTarget: 'any',
    color: 0xCC3300,       // Red-brown
  },
  archer: {
    type: 'archer',
    name: 'Archer',
    hp: 60,
    damage: 15,
    attackSpeed: 1.5,      // 1.5 attacks per second
    range: 4,              // Ranged
    moveSpeed: 2.5,
    trainingTime: 45,
    preferredTarget: 'any',
    color: 0x00CC66,       // Green
  },
  cavalry: {
    type: 'cavalry',
    name: 'Cavalry',
    hp: 150,
    damage: 30,
    attackSpeed: 0.8,      // Slower attack
    range: 1,
    moveSpeed: 4,          // Fast movement
    trainingTime: 60,
    preferredTarget: 'building',
    color: 0x6633CC,       // Purple
  },
  catapult: {
    type: 'catapult',
    name: 'Catapult',
    hp: 80,
    damage: 100,           // High damage
    attackSpeed: 0.3,      // Very slow attack
    range: 6,              // Long range
    moveSpeed: 1,          // Slow movement
    trainingTime: 120,
    preferredTarget: 'defensive',
    color: 0x996633,       // Brown
  },
};

// ============================================================
// Unit Training Costs
// ============================================================

export const UNIT_COSTS: Record<UnitType, ResourceCost> = {
  warrior: { food: 50, gold: 25 },
  archer: { food: 40, gold: 40 },
  cavalry: { food: 80, gold: 60 },
  catapult: { food: 100, gold: 150, oil: 20 },
};

// ============================================================
// Combat Configuration
// ============================================================

// Battle simulation tick rate (ticks per second)
export const BATTLE_TICK_RATE = 20;

// Battle duration limit (seconds)
export const BATTLE_MAX_DURATION = 180; // 3 minutes

// Star thresholds based on destruction percentage
export const STAR_THRESHOLDS = {
  one: 50,      // 50% destruction = 1 star
  two: 75,      // 75% destruction = 2 stars
  three: 100,   // 100% destruction = 3 stars
};

// Loot percentage (how much of defender's resources attacker gets)
export const LOOT_PERCENTAGE = 0.2; // 20% of available resources

// HP multiplier per building level
export const BUILDING_HP_MULTIPLIER = 1.25; // 25% more HP per level

// Unit deploy zone (rows from edge where units can be deployed)
export const DEPLOY_ZONE_DEPTH = 2;
