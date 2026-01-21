# Phase 3: Combat System

## Overview
A server-authoritative combat system where players can attack enemy bases with AI-controlled units.

## Acceptance Criteria
- [ ] AC1: A player can select an enemy base, place their attacking units, and initiate a battle
- [ ] AC2: Units autonomously navigate the enemy base using A* pathfinding, avoiding obstacles like walls
- [ ] AC3: The server calculates the entire battle simulation, determining the final destruction percentage and resource loot

## Technical Notes

### Client Changes
- `client/src/game/entities/Unit.ts`: Implement the unit entity, including its Finite State Machine (Idle, Move, Attack, Die) and visual representation
- `client/src/game/scenes/Battle.ts`: Create a new Phaser scene to render the enemy base and the attacking units, visualizing the server-driven simulation
- `client/src/game/systems/Pathfinding.ts`: Implement a client-side A* pathfinding system for units to navigate the grid and predict movement

### Server Changes
- `server/src/mechanics/CombatResolver.ts`: Create a new service to run the core combat simulation loop, calculating pathfinding, target acquisition, damage, and unit states
- `server/src/rooms/BattleRoom.ts`: Add a new Colyseus room to manage the state of an individual combat session between two players
- `server/src/models/User.ts`: Update the user model to store available troops for attacks

### Shared Changes
- `shared/types.ts`: Add TypeScript interfaces for `Unit`, `Troop`, and `BattleState`
- `shared/constants.ts`: Define base stats for all combat units (HP, damage, range, speed)

### Anti-Cheat Considerations
- The server must be the sole authority for the entire combat simulation
- Server validates troop composition before the battle begins
- Server calculates all unit positions, damage dealt, and final results
- Client inputs are limited to initial troop placement

## Implementation Steps
- [x] Step 1: Define unit stats and types in `shared/constants.ts` and `shared/types.ts`
- [x] Step 2: Implement the core server-side combat logic in `CombatResolver.ts`
- [x] Step 3: Create the `BattleRoom.ts` on the server to manage combat state and player interaction
- [x] Step 4: Implement the client-side `Unit.ts` class with its FSM
- [x] Step 5: Build the `Battle.ts` scene to render the battle based on state updates from the `BattleRoom`
- [x] Step 6: Integrate A* pathfinding for unit movement around buildings and walls

## Test Scenarios
- A unit correctly pathfinds around a wall to attack a target
- The server correctly calculates total damage and resource loot after a battle
- A player disconnects mid-battle, and the server simulation continues to completion
