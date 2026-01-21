# Phase 2: Server Authoritative Economy

## Overview
Implements a server-authoritative backend for user accounts, resource generation, and building construction timers using Colyseus and MongoDB.

## Acceptance Criteria
- [ ] AC1: A player's game state (buildings, resources) is persisted in MongoDB and loaded upon connection
- [ ] AC2: Food, Gold, and Oil are generated on the server based on building types and elapsed time, and the client's UI reflects these values
- [ ] AC3: Initiating a building construction is a server request; the server manages the timer and updates the game state upon completion

## Technical Notes

### Client Changes
- `client/src/main.ts`: Connect to the Colyseus server and authenticate the player
- `client/src/game/scenes/MainMap.ts`: Send build/collect actions to the server instead of modifying local state. Listen for server state updates to render buildings and resources
- `client/src/ui/`: UI components will display resource totals and construction timers based on data received from the server's authoritative state

### Server Changes
- `server/src/rooms/GameRoom.ts`: The Colyseus room will manage player state, handle actions like 'build' and 'upgrade', and broadcast state changes
- `server/src/models/User.ts`: New MongoDB schema for player accounts and authentication
- `server/src/models/Base.ts`: New MongoDB schema to store player's buildings, resources, and timers
- `server/src/mechanics/ResourceCalculator.ts`: New file to calculate resource generation based on building levels and time
- `server/src/mechanics/ConstructionManager.ts`: New file to handle construction timers and resource validation

### Shared Changes
- `shared/types.ts`: Define interfaces for `Player`, `Building`, `Resources`, and network messages
- `shared/constants.ts`: Add build costs, timers, and resource generation rates

### Anti-Cheat Considerations
- The server must validate all build requests against the player's actual resources and game rules
- Resource generation is calculated exclusively on the server using its own clock
- Construction and upgrade completion times are managed authoritatively by the server

## Implementation Steps
- [x] Step 1: Set up the Colyseus server project with Express and MongoDB
- [x] Step 2: Define User and Base Mongoose schemas and create a simple authentication mechanism
- [x] Step 3: In the GameRoom, implement logic to load a player's base from MongoDB on join
- [x] Step 4: Implement the server-side ResourceCalculator to update resources periodically and on player login
- [x] Step 5: Add a 'startConstruction' message handler on the server that validates costs and starts a timer using ConstructionManager
- [x] Step 6: Refactor the client to send actions to the server and render state received from the server

## Test Scenarios
- A player with insufficient gold attempts to build a Town Center; the server must reject the request
- A player logs out for 10 minutes; upon logging back in, their resource totals are correctly updated by the server
- A player starts a 5-minute construction, disconnects, then reconnects after 5 minutes; the building must be complete
