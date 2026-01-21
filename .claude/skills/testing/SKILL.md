---
name: testing
description: Testing patterns for game client and server. Auto-applies when working with tests or implementing features that need testing.
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# Testing Skill

Testing patterns for OpenCivilizations game.

## Test Structure

```
client/
  __tests__/        # Client-side tests
    game/           # Game logic tests
    ui/             # UI component tests

server/
  __tests__/        # Server-side tests
    rooms/          # Room logic tests
    mechanics/      # Game mechanics tests

shared/
  __tests__/        # Shared utility tests
```

## Running Tests

```bash
# All tests
npm test

# Client tests only
npm run test:client

# Server tests only
npm run test:server

# Watch mode
npm run test:watch

# Specific test file
npm test -- path/to/test.spec.ts
```

## Test Patterns

### Game Mechanics (Server)
```typescript
import { calculateResources } from '../mechanics/resources';

describe('Resource Calculation', () => {
  it('calculates gold production based on time elapsed', () => {
    const player = { gold: 0, lastUpdate: Date.now() - 3600000 };
    const farms = [{ productionRate: 10 }];

    const result = calculateResources(player, farms);

    expect(result.gold).toBe(10); // 1 hour * 10/hour
  });
});
```

### Colyseus Room (Server)
```typescript
import { ColyseusTestServer } from '@colyseus/testing';
import { GameRoom } from '../rooms/GameRoom';

describe('GameRoom', () => {
  let colyseus: ColyseusTestServer;

  beforeAll(async () => {
    colyseus = new ColyseusTestServer();
    await colyseus.listen(2567);
  });

  afterAll(() => colyseus.shutdown());

  it('creates building when player has resources', async () => {
    const room = await colyseus.createRoom('game', {});
    const client = await colyseus.connectTo(room);

    client.send('build', { type: 'farm', x: 5, y: 5 });

    await room.waitForNextPatch();
    expect(room.state.buildings.length).toBe(1);
  });
});
```

### Pathfinding (Client)
```typescript
import { findPath } from '../systems/pathfinding';

describe('Pathfinding', () => {
  it('finds path around obstacles', () => {
    const grid = createGrid(10, 10);
    grid[5][5].walkable = false; // obstacle

    const path = findPath(grid, { x: 0, y: 0 }, { x: 9, y: 9 });

    expect(path).not.toContain({ x: 5, y: 5 });
    expect(path[path.length - 1]).toEqual({ x: 9, y: 9 });
  });
});
```

### Isometric Conversion (Shared)
```typescript
import { cartesianToIsometric, isometricToCartesian } from '../utils/isometric';

describe('Isometric Conversion', () => {
  it('converts cartesian to isometric and back', () => {
    const cart = { x: 5, y: 3 };
    const iso = cartesianToIsometric(cart.x, cart.y);
    const result = isometricToCartesian(iso.x, iso.y);

    expect(Math.round(result.x)).toBe(cart.x);
    expect(Math.round(result.y)).toBe(cart.y);
  });
});
```

## Stories Reference

Test scenarios come from story files:
- Location: `docs/planning/stories/*.story.md`
- Each story has acceptance criteria (AC1, AC2, etc.)
- Tests should map to specific ACs

## Best Practices

1. **Test server logic extensively** - Most game logic is server-side
2. **Mock Colyseus for unit tests** - Use @colyseus/testing for integration
3. **Test pathfinding edge cases** - Blocked paths, unreachable targets
4. **Test resource calculations** - Time-based, overflow, negative
5. **Test state sync** - Client receives correct updates
6. **Use descriptive names** - `it('denies build when insufficient gold')`
