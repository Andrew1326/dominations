/**
 * Game constants for OpenCivilizations
 */

import type { BuildingDefinition, BuildingType } from './types';

// Grid configuration
export const GRID_SIZE = 20; // 20x20 grid
export const TILE_WIDTH = 64;
export const TILE_HEIGHT = 32;
export const TILE_WIDTH_HALF = TILE_WIDTH / 2;
export const TILE_HEIGHT_HALF = TILE_HEIGHT / 2;

// Building definitions
export const BUILDINGS: Record<BuildingType, BuildingDefinition> = {
  townCenter: {
    type: 'townCenter',
    name: 'Town Center',
    width: 3,
    height: 3,
    color: 0x8B4513, // Brown
  },
  house: {
    type: 'house',
    name: 'House',
    width: 2,
    height: 2,
    color: 0x4169E1, // Blue
  },
  farm: {
    type: 'farm',
    name: 'Farm',
    width: 2,
    height: 2,
    color: 0x228B22, // Green
  },
};

// Colors
export const GRID_LINE_COLOR = 0x444444;
export const VALID_PLACEMENT_COLOR = 0x00FF00;
export const INVALID_PLACEMENT_COLOR = 0xFF0000;
export const GRID_FILL_COLOR = 0x1a1a2e;

// LocalStorage key
export const STORAGE_KEY = 'opencivilizations_base_layout';
