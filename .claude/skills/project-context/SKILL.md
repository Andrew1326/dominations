---
name: project-context
description: OpenCivilizations project architecture, patterns, and conventions. Auto-applies for implementation tasks to ensure consistency.
allowed-tools: Read, Grep, Glob
---

# Project Context Skill

Architecture and conventions for OpenCivilizations (web-based MMORTS).

## Quick Reference

| Aspect | Standard |
|--------|----------|
| Language | TypeScript strict |
| Game Engine | Phaser 3 |
| UI Framework | React or Vue (overlays) |
| Backend | Node.js + Colyseus |
| Database | MongoDB |
| Caching | Redis |

## Key Documentation

- `docs/architecture.md` - System design
- `shared/constants.ts` - Game balance data
- `shared/types.ts` - Type definitions

## Domain Model

| Term | Meaning |
|------|---------|
| Base | Player's civilization layout |
| Building | Structure on the grid (TownCenter, Farm, Barracks) |
| Unit | Trainable troop with AI behavior |
| Resource | Food, Gold, Oil |
| Age | Technology era (Stone, Bronze, Iron, etc.) |
| Nation | Civilization with unique bonuses |

## Project Structure

```
client/src/
  assets/         # Sprites, tiles, audio
  game/
    scenes/       # Phaser scenes (MainMap, Battle, Loading)
    entities/     # Buildings, Units, Projectiles
    systems/      # Pathfinding, Grid, Input
  ui/             # React/Vue overlays (HUD, Menus)

server/src/
  rooms/          # Colyseus game rooms
  models/         # MongoDB schemas (User, Base, Clan)
  mechanics/      # Authoritative game logic

shared/
  constants.ts    # Building costs, Unit stats
  types.ts        # Shared interfaces
```

## Code Patterns

### Isometric Projection
```typescript
// Grid to Screen
function cartesianToIsometric(x: number, y: number) {
  return {
    x: (x - y) * TILE_WIDTH_HALF,
    y: (x + y) * TILE_HEIGHT_HALF
  };
}

// Screen to Grid
function isometricToCartesian(isoX: number, isoY: number) {
  return {
    x: (isoX / TILE_WIDTH_HALF + isoY / TILE_HEIGHT_HALF) / 2,
    y: (isoY / TILE_HEIGHT_HALF - isoX / TILE_WIDTH_HALF) / 2
  };
}
```

### Server Authority
```typescript
// Server calculates resources based on time
const elapsed = Date.now() - player.lastUpdate;
const produced = Math.floor(elapsed / 3600000) * farm.productionRate;
player.gold += produced;
```

### State Synchronization
```typescript
// Colyseus schema for synced state
class GameState extends Schema {
  @type([Building]) buildings = new ArraySchema<Building>();
  @type({ map: Player }) players = new MapSchema<Player>();
}
```

## Code Standards

1. **TypeScript strict** - No `any` without justification
2. **Server authoritative** - Never trust client input
3. **Client predicts** - Show optimistic updates, reconcile with server
4. **Colyseus for sync** - Use schemas for multiplayer state
5. **MongoDB for persistence** - Save base layouts, user data
6. **Redis for sessions** - Leaderboards, active sessions
