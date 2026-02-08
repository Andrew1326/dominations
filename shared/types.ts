/**
 * Shared type definitions for OpenCivilizations
 */

// ============================================================
// Building Types
// ============================================================

export type BuildingType =
  | 'townCenter' | 'house' | 'farm' | 'goldMine' | 'oilWell'
  | 'barracks' | 'wall' | 'tower' | 'storage'
  | 'blacksmith' | 'market' | 'temple' | 'library'
  | 'stable' | 'castle' | 'university' | 'factory'
  | 'airfield' | 'dataCentre';

// ============================================================
// Age & Nation Types
// ============================================================

export type Age =
  | 'stone' | 'bronze' | 'iron' | 'classical' | 'medieval'
  | 'gunpowder' | 'enlightenment' | 'industrial' | 'modern' | 'digital';

export type Nation =
  | 'romans' | 'greeks' | 'egyptians' | 'chinese'
  | 'japanese' | 'vikings' | 'british' | 'persians';

export type NationBonusType =
  | 'resourceProduction' | 'buildSpeed' | 'unitTraining'
  | 'combatDamage' | 'buildingHp' | 'lootBonus' | 'storageCapacity';

export interface NationBonus {
  type: NationBonusType;
  value: number;        // Percentage modifier (e.g., 10 = +10%)
  description: string;
}

export interface NationDefinition {
  id: Nation;
  name: string;
  description: string;
  colorPalette: {
    primary: string;    // Hex color
    secondary: string;
    accent: string;
  };
  bonuses: NationBonus[];
}

export interface AgeDefinition {
  id: Age;
  name: string;
  era: string;           // Display category (e.g., "Ancient", "Medieval", "Modern")
  order: number;         // 0-9 for sorting
  unlocksBuildings: BuildingType[];
  advanceCost: ResourceCost;
  advanceTime: number;   // Seconds to advance to this age
  resourceCapMultiplier: number;   // Multiplied against base resource cap
  buildingStatMultiplier: number;  // HP/damage scale factor for this age
}

export interface BuildingData {
  id: string;
  type: BuildingType;
  row: number;
  col: number;
  level: number;
  constructionStartedAt?: number;  // Timestamp when construction started
  constructionEndsAt?: number;     // Timestamp when construction completes
  hp?: number;                     // Current HP (used in combat)
  maxHp?: number;                  // Max HP (used in combat)
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
  hp: number;              // Base HP for combat
  produces?: ResourceType; // Resource this building produces
  productionRate?: number; // Units per hour at level 1
  isDefensive?: boolean;   // True for walls, towers, etc.
  availableFrom?: Age;     // First age this building is available (default: 'stone')
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

// ============================================================
// Unit & Combat Types
// ============================================================

export type UnitType = 'warrior' | 'archer' | 'cavalry' | 'catapult';

export type UnitState = 'idle' | 'moving' | 'attacking' | 'dead';

export interface UnitDefinition {
  type: UnitType;
  name: string;
  hp: number;              // Base health points
  damage: number;          // Base damage per attack
  attackSpeed: number;     // Attacks per second
  range: number;           // Attack range in grid tiles
  moveSpeed: number;       // Tiles per second
  trainingTime: number;    // Seconds to train
  preferredTarget?: 'building' | 'defensive' | 'any';  // AI targeting preference
  color: number;           // Placeholder color until sprites
}

export interface UnitData {
  id: string;
  type: UnitType;
  hp: number;              // Current HP
  maxHp: number;
  state: UnitState;
  row: number;             // Current grid position (fractional for smooth movement)
  col: number;
  targetId?: string;       // ID of building/unit being targeted
  targetRow?: number;      // Destination grid position
  targetCol?: number;
}

export interface TroopSlot {
  type: UnitType;
  count: number;
}

// ============================================================
// Battle Types
// ============================================================

export type BattlePhase = 'setup' | 'running' | 'ended';

export interface BattleState {
  id: string;
  phase: BattlePhase;
  attackerId: string;
  defenderId: string;
  defenderBase: BuildingData[];  // Snapshot of defender's base
  units: UnitData[];             // All active units
  tick: number;                  // Current simulation tick
  destructionPercent: number;    // 0-100%
  loot: Resources;               // Resources gained by attacker
  startTime: number;
  endTime?: number;
}

export interface BattleResult {
  battleId: string;
  attackerId: string;
  defenderId: string;
  destructionPercent: number;
  stars: number;                 // 0-3 stars based on destruction
  loot: Resources;
  duration: number;              // Battle duration in seconds
}

// ============================================================
// Battle Network Messages (Client -> Server)
// ============================================================

export interface StartBattleMessage {
  type: 'startBattle';
  defenderId: string;
  troops: TroopSlot[];
}

export interface DeployUnitMessage {
  type: 'deployUnit';
  unitType: UnitType;
  row: number;
  col: number;
}

export interface EndBattleMessage {
  type: 'endBattle';
}

export type BattleClientMessage =
  | StartBattleMessage
  | DeployUnitMessage
  | EndBattleMessage;

// ============================================================
// Battle Network Messages (Server -> Client)
// ============================================================

export interface BattleStartedMessage {
  type: 'battleStarted';
  battleId: string;
  defenderBase: BuildingData[];
  defenderUsername: string;
}

export interface BattleTickMessage {
  type: 'battleTick';
  tick: number;
  units: UnitData[];
  buildings: BuildingData[];     // Updated building HP
  destructionPercent: number;
}

export interface BattleEndedMessage {
  type: 'battleEnded';
  result: BattleResult;
}

export type BattleServerMessage =
  | BattleStartedMessage
  | BattleTickMessage
  | BattleEndedMessage
  | ErrorMessage;

// ============================================================
// Matchmaking Types
// ============================================================

export interface FindMatchMessage {
  type: 'findMatch';
}

export interface MatchFoundMessage {
  type: 'matchFound';
  attackerId: string;  // Current player's MongoDB ID (for BattleRoom)
  opponent: {
    odId: string;
    username: string;
    base: BuildingData[];
  };
}

export interface NoMatchFoundMessage {
  type: 'noMatchFound';
  reason: string;
}

export type MatchmakingClientMessage = FindMatchMessage;

export type MatchmakingServerMessage =
  | MatchFoundMessage
  | NoMatchFoundMessage
  | ErrorMessage;
