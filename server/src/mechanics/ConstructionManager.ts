/**
 * ConstructionManager - Server-side construction logic
 *
 * Handles building placement validation, construction timers,
 * and resource cost verification.
 */

import type { BuildingType, Resources, ResourceCost } from '@shared/types';
import { IBuilding } from '../models/Base';
import {
  BUILDINGS,
  BUILDING_COSTS,
  GRID_SIZE,
  BUILD_TIME_MULTIPLIER,
  UPGRADE_COST_MULTIPLIER,
} from '@shared/constants';
import { canAfford, deductResources } from './ResourceCalculator';

export interface PlacementValidation {
  valid: boolean;
  error?: string;
}

export interface ConstructionResult {
  success: boolean;
  building?: IBuilding;
  newResources?: Resources;
  error?: string;
}

/**
 * Get the cost to build or upgrade a building
 */
export function getBuildingCost(buildingType: BuildingType, level: number = 1): ResourceCost {
  const baseCost = BUILDING_COSTS[buildingType];
  if (level === 1) {
    return { ...baseCost };
  }

  // Upgrade cost increases with level
  const multiplier = Math.pow(UPGRADE_COST_MULTIPLIER, level - 1);
  return {
    food: baseCost.food ? Math.floor(baseCost.food * multiplier) : undefined,
    gold: baseCost.gold ? Math.floor(baseCost.gold * multiplier) : undefined,
    oil: baseCost.oil ? Math.floor(baseCost.oil * multiplier) : undefined,
  };
}

/**
 * Get the construction time for a building at a given level (in seconds)
 */
export function getConstructionTime(buildingType: BuildingType, level: number = 1): number {
  const definition = BUILDINGS[buildingType];
  if (level === 1) {
    return definition.buildTime;
  }

  // Build time increases with level
  const multiplier = Math.pow(BUILD_TIME_MULTIPLIER, level - 1);
  return Math.floor(definition.buildTime * multiplier);
}

/**
 * Check if a position is within the grid bounds
 */
export function isWithinBounds(
  row: number,
  col: number,
  width: number,
  height: number
): boolean {
  return (
    row >= 0 &&
    col >= 0 &&
    row + height <= GRID_SIZE &&
    col + width <= GRID_SIZE
  );
}

/**
 * Check if a building placement overlaps with existing buildings
 */
export function checkOverlap(
  row: number,
  col: number,
  width: number,
  height: number,
  existingBuildings: IBuilding[]
): boolean {
  for (const building of existingBuildings) {
    const existingDef = BUILDINGS[building.type as BuildingType];
    if (!existingDef) continue;

    // Check for overlap using axis-aligned bounding box collision
    const noOverlap =
      row + height <= building.row ||           // New is above existing
      building.row + existingDef.height <= row || // New is below existing
      col + width <= building.col ||            // New is left of existing
      building.col + existingDef.width <= col;  // New is right of existing

    if (!noOverlap) {
      return true; // Overlap detected
    }
  }
  return false;
}

/**
 * Validate a building placement
 */
export function validatePlacement(
  buildingType: BuildingType,
  row: number,
  col: number,
  existingBuildings: IBuilding[]
): PlacementValidation {
  const definition = BUILDINGS[buildingType];
  if (!definition) {
    return { valid: false, error: 'Invalid building type' };
  }

  // Check bounds
  if (!isWithinBounds(row, col, definition.width, definition.height)) {
    return { valid: false, error: 'Position out of bounds' };
  }

  // Check overlap
  if (checkOverlap(row, col, definition.width, definition.height, existingBuildings)) {
    return { valid: false, error: 'Position overlaps with existing building' };
  }

  return { valid: true };
}

/**
 * Start construction of a new building
 */
export function startConstruction(
  buildingType: BuildingType,
  row: number,
  col: number,
  currentResources: Resources,
  existingBuildings: IBuilding[]
): ConstructionResult {
  // Validate placement
  const validation = validatePlacement(buildingType, row, col, existingBuildings);
  if (!validation.valid) {
    return { success: false, error: validation.error };
  }

  // Check resources
  const cost = getBuildingCost(buildingType);
  if (!canAfford(currentResources, cost)) {
    return { success: false, error: 'Insufficient resources' };
  }

  // Calculate construction end time
  const constructionTime = getConstructionTime(buildingType);
  const now = new Date();
  const endsAt = new Date(now.getTime() + constructionTime * 1000);

  // Create building
  const building: IBuilding = {
    id: `${buildingType}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    type: buildingType,
    row,
    col,
    level: 1,
    constructionStartedAt: now,
    constructionEndsAt: endsAt,
  };

  // Deduct resources
  const newResources = deductResources(currentResources, cost);

  return {
    success: true,
    building,
    newResources,
  };
}

/**
 * Check if a building's construction is complete
 */
export function isConstructionComplete(building: IBuilding, currentTime: Date = new Date()): boolean {
  if (!building.constructionEndsAt) {
    return true; // No construction timer = already complete
  }
  return currentTime >= building.constructionEndsAt;
}

/**
 * Complete a building's construction (remove construction timestamps)
 */
export function completeConstruction(building: IBuilding): IBuilding {
  return {
    ...building,
    constructionStartedAt: undefined,
    constructionEndsAt: undefined,
  };
}

/**
 * Get remaining construction time in seconds
 */
export function getRemainingConstructionTime(
  building: IBuilding,
  currentTime: Date = new Date()
): number {
  if (!building.constructionEndsAt) {
    return 0;
  }

  const remaining = building.constructionEndsAt.getTime() - currentTime.getTime();
  return Math.max(0, Math.ceil(remaining / 1000));
}

/**
 * Check and complete any finished constructions
 */
export function processCompletedConstructions(
  buildings: IBuilding[],
  currentTime: Date = new Date()
): { buildings: IBuilding[]; completedIds: string[] } {
  const completedIds: string[] = [];
  const updatedBuildings = buildings.map((building) => {
    if (building.constructionEndsAt && isConstructionComplete(building, currentTime)) {
      completedIds.push(building.id);
      return completeConstruction(building);
    }
    return building;
  });

  return { buildings: updatedBuildings, completedIds };
}
