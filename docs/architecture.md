# OpenCivilizations Architecture

Web-based MMORTS inspired by DomiNations.

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Phaser 3  │  │  React/Vue  │  │   Colyseus  │         │
│  │  (Rendering)│  │ (UI Overlay)│  │   (Client)  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                     WebSocket/HTTP
                            │
┌─────────────────────────────────────────────────────────────┐
│                        SERVER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Colyseus   │  │   Express   │  │  Mechanics  │         │
│  │   (Rooms)   │  │    (API)    │  │  (Logic)    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                            │                                 │
│  ┌─────────────┐  ┌─────────────┐                          │
│  │   MongoDB   │  │    Redis    │                          │
│  │ (Persistence)│  │  (Sessions) │                          │
│  └─────────────┘  └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

## Core Principle: Authoritative Server

**Never trust the client.**

- Client: Displays state, captures input, shows predictions
- Server: Validates actions, calculates state, persists data

```typescript
// BAD - Client calculates
client.resources.gold += 100;
sendToServer({ gold: client.resources.gold });

// GOOD - Server calculates
sendToServer({ action: 'collect', buildingId: 'farm1' });
// Server validates ownership, calculates time-based production, updates DB
```

## Directory Structure

```
client/
  src/
    assets/           # Sprites, tiles, audio
    game/
      scenes/         # Phaser scenes
        MainMap.ts    # Base building scene
        Battle.ts     # Combat scene
        Loading.ts    # Asset loading
      entities/       # Game objects
        Building.ts   # Base class for all buildings
        Unit.ts       # Base class for all units
      systems/        # Game systems
        GridSystem.ts # Isometric grid management
        Pathfinding.ts# A* pathfinding
        Input.ts      # Mouse/touch handling
    ui/               # React/Vue overlays
      components/     # Reusable UI components
      screens/        # Full-screen menus

server/
  src/
    rooms/            # Colyseus game rooms
      GameRoom.ts     # Main game room
      BattleRoom.ts   # Combat room
    models/           # MongoDB schemas
      User.ts         # Player account
      Base.ts         # Base layout
      Clan.ts         # Alliance data
    mechanics/        # Authoritative game logic
      ResourceCalculator.ts
      CombatResolver.ts
      ConstructionManager.ts

shared/
  constants.ts        # Game balance (costs, stats, timers)
  types.ts            # TypeScript interfaces
```

## Key Systems

### Isometric Grid

```typescript
const TILE_WIDTH = 64;
const TILE_HEIGHT = 32;

// Grid to Screen
function cartesianToIsometric(x: number, y: number) {
  return {
    x: (x - y) * (TILE_WIDTH / 2),
    y: (x + y) * (TILE_HEIGHT / 2)
  };
}

// Screen to Grid (for mouse input)
function isometricToCartesian(isoX: number, isoY: number) {
  return {
    x: (isoX / (TILE_WIDTH / 2) + isoY / (TILE_HEIGHT / 2)) / 2,
    y: (isoY / (TILE_HEIGHT / 2) - isoX / (TILE_WIDTH / 2)) / 2
  };
}
```

### State Synchronization (Colyseus)

```typescript
// Server: Define synced state
class GameState extends Schema {
  @type([Building]) buildings = new ArraySchema<Building>();
  @type({ map: Player }) players = new MapSchema<Player>();
  @type("number") serverTime: number = 0;
}

// Client: Listen for changes
room.state.buildings.onAdd((building) => {
  createBuildingSprite(building);
});
```

### Resource Calculation (Server-Side)

```typescript
// Server calculates resources based on time
function calculateOfflineProduction(player: Player): number {
  const elapsed = Date.now() - player.lastUpdate;
  const hours = elapsed / 3600000;

  let production = 0;
  for (const building of player.buildings) {
    if (building.type === 'farm') {
      production += building.productionRate * hours;
    }
  }

  return Math.min(production, player.storageCapacity - player.gold);
}
```

## Anti-Cheat Guidelines

1. **Action Validation**: Server validates every player action
2. **Time-Based Calculations**: Server calculates using its own clock
3. **Rate Limiting**: Prevent action spam
4. **State Authority**: Client state is always overwritten by server
5. **Replay Verification**: Battle replays can be verified server-side

## Performance Considerations

### Client
- Object pooling for units (avoid GC spikes)
- Texture atlases for sprites
- Depth sorting for isometric rendering
- Culling off-screen objects

### Server
- Batch database writes
- Redis for leaderboards and sessions
- Horizontal scaling with Colyseus presence

### Network
- Delta state updates (not full state)
- Interpolation for smooth movement
- Client-side prediction for responsiveness
