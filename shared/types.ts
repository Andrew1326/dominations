/**
 * Shared type definitions for OpenCivilizations
 */

export type BuildingType = 'townCenter' | 'house' | 'farm';

export interface BuildingData {
  id: string;
  type: BuildingType;
  row: number;
  col: number;
}

export interface BaseLayout {
  buildings: BuildingData[];
  lastSaved: number;
}

export interface GridPosition {
  row: number;
  col: number;
}

export interface ScreenPosition {
  x: number;
  y: number;
}

export interface BuildingDefinition {
  type: BuildingType;
  name: string;
  width: number;  // Grid tiles wide
  height: number; // Grid tiles tall
  color: number;  // Placeholder color until sprites
}
