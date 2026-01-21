/**
 * Game constants for OpenCivilizations
 */

import type { BuildingDefinition, BuildingType, ResourceCost, Resources, UnitDefinition, UnitType } from './types';

// ============================================================
// Grid Configuration
// ============================================================

export const GRID_SIZE = 20; // 20x20 grid
export const TILE_WIDTH = 64;
export const TILE_HEIGHT = 32;
export const TILE_WIDTH_HALF = TILE_WIDTH / 2;
export const TILE_HEIGHT_HALF = TILE_HEIGHT / 2;

// ============================================================
// Building Definitions
// ============================================================

export const BUILDINGS: Record<BuildingType, BuildingDefinition> = {
  townCenter: {
    type: 'townCenter',
    name: 'Town Center',
    width: 3,
    height: 3,
    color: 0x8B4513, // Brown
    maxLevel: 10,
    buildTime: 60, // 1 minute for testing (would be longer in production)
    hp: 2000,
  },
  house: {
    type: 'house',
    name: 'House',
    width: 2,
    height: 2,
    color: 0x4169E1, // Blue
    maxLevel: 5,
    buildTime: 30,
    hp: 400,
  },
  farm: {
    type: 'farm',
    name: 'Farm',
    width: 2,
    height: 2,
    color: 0x228B22, // Green
    maxLevel: 10,
    buildTime: 45,
    hp: 500,
    produces: 'food',
    productionRate: 100, // 100 food per hour at level 1
  },
  goldMine: {
    type: 'goldMine',
    name: 'Gold Mine',
    width: 2,
    height: 2,
    color: 0xFFD700, // Gold
    maxLevel: 10,
    buildTime: 60,
    hp: 500,
    produces: 'gold',
    productionRate: 50, // 50 gold per hour at level 1
  },
  oilWell: {
    type: 'oilWell',
    name: 'Oil Well',
    width: 2,
    height: 2,
    color: 0x1C1C1C, // Dark gray
    maxLevel: 10,
    buildTime: 120,
    hp: 600,
    produces: 'oil',
    productionRate: 25, // 25 oil per hour at level 1
  },
};

// ============================================================
// Building Costs
// ============================================================

export const BUILDING_COSTS: Record<BuildingType, ResourceCost> = {
  townCenter: { gold: 1000, food: 500 },
  house: { gold: 100, food: 50 },
  farm: { gold: 150 },
  goldMine: { gold: 200, food: 100 },
  oilWell: { gold: 500, food: 200 },
};

// Cost multiplier per level (e.g., level 2 costs 1.5x level 1)
export const UPGRADE_COST_MULTIPLIER = 1.5;

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
