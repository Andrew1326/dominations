/**
 * Shared type definitions for OpenCivilizations
 */

// ============================================================
// Building Types
// ============================================================

export type BuildingType = 'townCenter' | 'house' | 'farm' | 'goldMine' | 'oilWell';

export interface BuildingData {
  id: string;
  type: BuildingType;
  row: number;
  col: number;
  level: number;
  constructionStartedAt?: number;  // Timestamp when construction started
  constructionEndsAt?: number;     // Timestamp when construction completes
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
  width: number;           // Grid tiles wide
  height: number;          // Grid tiles tall
  color: number;           // Placeholder color until sprites
  maxLevel: number;        // Maximum upgrade level
  buildTime: number;       // Base construction time in seconds
  produces?: ResourceType; // Resource this building produces
  productionRate?: number; // Units per hour at level 1
}

// ============================================================
// Resource Types
// ============================================================

export type ResourceType = 'food' | 'gold' | 'oil';

export interface Resources {
  food: number;
  gold: number;
  oil: number;
}

export interface ResourceCost {
  food?: number;
  gold?: number;
  oil?: number;
}

// ============================================================
// Player Types
// ============================================================

export interface PlayerData {
  id: string;
  username: string;
  resources: Resources;
  resourcesLastUpdated: number;  // Timestamp for offline resource calculation
  buildings: BuildingData[];
  createdAt: number;
}

// ============================================================
// Network Messages (Client -> Server)
// ============================================================

export interface PlaceBuildingMessage {
  type: 'placeBuilding';
  buildingType: BuildingType;
  row: number;
  col: number;
}

export interface CollectResourcesMessage {
  type: 'collectResources';
}

export interface CancelConstructionMessage {
  type: 'cancelConstruction';
  buildingId: string;
}

export type ClientMessage =
  | PlaceBuildingMessage
  | CollectResourcesMessage
  | CancelConstructionMessage;

// ============================================================
// Network Messages (Server -> Client)
// ============================================================

export interface StateUpdateMessage {
  type: 'stateUpdate';
  resources: Resources;
  buildings: BuildingData[];
}

export interface ErrorMessage {
  type: 'error';
  code: string;
  message: string;
}

export interface BuildingPlacedMessage {
  type: 'buildingPlaced';
  building: BuildingData;
}

export interface ConstructionCompleteMessage {
  type: 'constructionComplete';
  buildingId: string;
}

export type ServerMessage =
  | StateUpdateMessage
  | ErrorMessage
  | BuildingPlacedMessage
  | ConstructionCompleteMessage;
