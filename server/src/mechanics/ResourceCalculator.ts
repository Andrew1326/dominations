/**
 * ResourceCalculator - Server-side resource generation logic
 *
 * Calculates resource production based on buildings and elapsed time.
 * This is the authoritative source for resource calculations.
 */

import type { Resources, BuildingType } from '@shared/types';
import { IBuilding } from '../models/Base';
import {
  BUILDINGS,
  PRODUCTION_RATE_MULTIPLIER,
  BASE_RESOURCE_CAP,
} from '@shared/constants';

export interface ResourceProduction {
  food: number;
  gold: number;
  oil: number;
}

/**
 * Calculate production rate for a single building (per hour)
 */
export function getBuildingProductionRate(building: IBuilding): ResourceProduction {
  const production: ResourceProduction = { food: 0, gold: 0, oil: 0 };

  // Skip buildings under construction
  if (building.constructionEndsAt && building.constructionEndsAt > new Date()) {
    return production;
  }

  const definition = BUILDINGS[building.type as BuildingType];
  if (!definition || !definition.produces || !definition.productionRate) {
    return production;
  }

  // Calculate production with level multiplier
  // Rate = baseRate * (multiplier ^ (level - 1))
  const levelMultiplier = Math.pow(PRODUCTION_RATE_MULTIPLIER, building.level - 1);
  const rate = definition.productionRate * levelMultiplier;

  production[definition.produces] = rate;
  return production;
}

/**
 * Calculate total production rate for all buildings (per hour)
 */
export function getTotalProductionRate(buildings: IBuilding[]): ResourceProduction {
  const total: ResourceProduction = { food: 0, gold: 0, oil: 0 };

  for (const building of buildings) {
    const rate = getBuildingProductionRate(building);
    total.food += rate.food;
    total.gold += rate.gold;
    total.oil += rate.oil;
  }

  return total;
}

/**
 * Calculate resources generated over a time period
 *
 * @param buildings - List of buildings
 * @param elapsedMs - Time elapsed in milliseconds
 * @returns Resources generated during the period
 */
export function calculateResourcesGenerated(
  buildings: IBuilding[],
  elapsedMs: number
): ResourceProduction {
  const hourlyRate = getTotalProductionRate(buildings);
  const hours = elapsedMs / (1000 * 60 * 60);

  return {
    food: Math.floor(hourlyRate.food * hours),
    gold: Math.floor(hourlyRate.gold * hours),
    oil: Math.floor(hourlyRate.oil * hours),
  };
}

/**
 * Update resources based on time elapsed since last update
 *
 * @param currentResources - Current resource amounts
 * @param buildings - List of buildings
 * @param lastUpdated - Timestamp of last resource update
 * @param currentTime - Current timestamp (defaults to now)
 * @returns Updated resources (capped at maximum)
 */
export function updateResources(
  currentResources: Resources,
  buildings: IBuilding[],
  lastUpdated: Date,
  currentTime: Date = new Date()
): Resources {
  const elapsedMs = currentTime.getTime() - lastUpdated.getTime();

  // Don't generate negative resources (in case of time issues)
  if (elapsedMs <= 0) {
    return { ...currentResources };
  }

  const generated = calculateResourcesGenerated(buildings, elapsedMs);

  // Add generated resources and cap at maximum
  return {
    food: Math.min(currentResources.food + generated.food, BASE_RESOURCE_CAP.food),
    gold: Math.min(currentResources.gold + generated.gold, BASE_RESOURCE_CAP.gold),
    oil: Math.min(currentResources.oil + generated.oil, BASE_RESOURCE_CAP.oil),
  };
}

/**
 * Check if player can afford a resource cost
 */
export function canAfford(resources: Resources, cost: Partial<Resources>): boolean {
  if (cost.food && resources.food < cost.food) return false;
  if (cost.gold && resources.gold < cost.gold) return false;
  if (cost.oil && resources.oil < cost.oil) return false;
  return true;
}

/**
 * Deduct resources from player (returns new resource object)
 */
export function deductResources(
  resources: Resources,
  cost: Partial<Resources>
): Resources {
  return {
    food: resources.food - (cost.food || 0),
    gold: resources.gold - (cost.gold || 0),
    oil: resources.oil - (cost.oil || 0),
  };
}
