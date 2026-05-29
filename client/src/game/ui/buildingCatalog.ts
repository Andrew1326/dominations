/**
 * Building Catalog - pure helpers describing every placeable building.
 *
 * Used by the "Add Building" menu to render all buildings with their image,
 * size and price. Kept free of DOM/Phaser so it can be unit-tested.
 */

import type { Age, BuildingType, ResourceCost } from '@shared/types';
import { BUILDINGS, BUILDING_COSTS, AGES, AGE_ORDER } from '@shared/constants';
import { BUILDING_IMAGE_AGES } from './buildingImageManifest';

export interface CatalogEntry {
  type: BuildingType;
  name: string;
  width: number;
  height: number;
  cost: ResourceCost;
  age: Age;
  ageName: string;
  /** Resolved sprite URL, or undefined when no render exists for this building. */
  imageUrl?: string;
  /** CSS hex color used as a fallback swatch when no image is available. */
  color: string;
}

/** Phaser texture key used for a building's canvas sprite. */
export interface BuildingTexture {
  key: string;
  url: string;
}

/**
 * The age whose render set is most complete; used as the primary fallback when
 * a building has no art at its own unlock age.
 */
const FALLBACK_ART_AGE: Age = 'medieval';

/** The age a building first becomes available (defaults to the earliest age). */
function buildingAge(type: BuildingType): Age {
  return BUILDINGS[type].availableFrom ?? AGE_ORDER[0];
}

/** Convert a Phaser numeric color (0xRRGGBB) to a CSS hex string. */
export function colorToHex(color: number): string {
  return `#${color.toString(16).padStart(6, '0')}`;
}

/** Build the sprite path for a building at a specific age and nation. */
function imagePath(age: Age, type: BuildingType, nation: string): string {
  return `assets/buildings/${age}/${nation}/${type}.png`;
}

/**
 * Pick the age whose render best represents a building: prefer its own unlock
 * age, then the most complete fallback set, then any other age that has art.
 * Returns undefined when no render exists (per the generated manifest).
 */
function resolveImageAge(type: BuildingType): Age | undefined {
  const available = BUILDING_IMAGE_AGES[type];
  if (!available || available.length === 0) return undefined;

  const preference: Age[] = [buildingAge(type), FALLBACK_ART_AGE, ...AGE_ORDER];
  for (const age of preference) {
    if (available.includes(age)) return age;
  }
  return available[0];
}

/** True when a rendered sprite exists for this building. */
export function hasBuildingImage(type: BuildingType): boolean {
  return resolveImageAge(type) !== undefined;
}

/**
 * Resolve the best sprite URL for a building, or undefined if it has no render.
 * Backed by the generated manifest, so it never points at a missing file.
 */
export function getBuildingImageUrl(type: BuildingType, nation: string = 'romans'): string | undefined {
  const age = resolveImageAge(type);
  return age ? imagePath(age, type, nation) : undefined;
}

/**
 * Phaser texture key + URL for a building's canvas sprite, or undefined when
 * the building has no render.
 */
export function getBuildingTexture(type: BuildingType, nation: string = 'romans'): BuildingTexture | undefined {
  const url = getBuildingImageUrl(type, nation);
  return url ? { key: `building-${type}`, url } : undefined;
}

/**
 * Build the full catalog, sorted by age progression then by name so the
 * menu reads as a natural tech tree.
 */
export function getBuildingCatalog(nation: string = 'romans'): CatalogEntry[] {
  const types = Object.keys(BUILDINGS) as BuildingType[];

  return types
    .map((type): CatalogEntry => {
      const def = BUILDINGS[type];
      const age = buildingAge(type);
      return {
        type,
        name: def.name,
        width: def.width,
        height: def.height,
        cost: BUILDING_COSTS[type] ?? {},
        age,
        ageName: AGES[age].name,
        imageUrl: getBuildingImageUrl(type, nation),
        color: colorToHex(def.color),
      };
    })
    .sort((a, b) => {
      const ageDiff = AGE_ORDER.indexOf(a.age) - AGE_ORDER.indexOf(b.age);
      return ageDiff !== 0 ? ageDiff : a.name.localeCompare(b.name);
    });
}

/** Format a cost as a compact emoji string, e.g. "💰150 🍖50". */
export function formatCost(cost: ResourceCost): string {
  const parts: string[] = [];
  if (cost.gold) parts.push(`💰${cost.gold}`);
  if (cost.food) parts.push(`🍖${cost.food}`);
  if (cost.oil) parts.push(`🛢️${cost.oil}`);
  return parts.length > 0 ? parts.join('  ') : 'Free';
}
