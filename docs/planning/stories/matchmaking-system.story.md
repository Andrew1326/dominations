# Matchmaking System

## Overview
Enables players to find and attack other players' bases.

## Acceptance Criteria
- [x] AC1: Player can press a button in the UI to initiate a search for an opponent
- [x] AC2: The server finds a suitable opponent base from the database, excluding the searching player
- [x] AC3: The client receives the opponent's base layout and transitions to the battle scene to begin the attack

## Technical Notes

### Client Changes
- `client/src/ui/`: Add an "Attack" or "Find Match" button to the main UI overlay
- `client/src/services/NetworkService.ts`: Implement a method to send a matchmaking request to the GameRoom
- `client/src/game/scenes/MainMap.ts`: Handle the matchmaking response, and on success, transition to the Battle scene with the opponent's data
- `client/src/game/scenes/Battle.ts`: Modify to initialize with an opponent's base data, rendering their layout for the attack

### Server Changes
- `server/src/rooms/GameRoom.ts`: Add a message handler for `findMatch`. Use a new service to find an opponent and send their base data to the client
- `server/src/mechanics/MatchmakingService.ts`: (New file) Create a service to handle the logic of querying the MongoDB Base collection for a suitable opponent
- `server/src/models/Base.ts`: Add a `shieldUntil` timestamp to prevent players from being attacked too frequently
- `server/src/rooms/BattleRoom.ts`: Prepare to receive battle initiation state from the GameRoom or client

### Shared Changes
- `shared/types.ts`: Define interfaces for matchmaking messages (`FindMatchRequest`, `MatchFoundResponse`)

### Anti-Cheat
- Server must be the sole authority for selecting an opponent; the client cannot influence the choice
- Server must validate the player's eligibility to attack (e.g., has trained troops, is not currently shielded)
- Server must load the most current state of the opponent's base from the database for the battle

## Implementation Steps
- [x] Step 1: Define matchmaking request/response types in `shared/types.ts`
- [x] Step 2: Implement the core opponent-finding logic in new `server/src/mechanics/MatchmakingService.ts`
- [x] Step 3: Add shield field to Base model in `server/src/models/Base.ts`
- [x] Step 4: Add a `findMatch` message handler in `server/src/rooms/GameRoom.ts`
- [x] Step 5: Add "Attack" button to client UI that sends `findMatch` message via `NetworkService.ts`
- [x] Step 6: Implement client-side logic in `MainMap.ts` to handle server's response
- [x] Step 7: Update `Battle.ts` to dynamically render opponent's base from server data
- [x] Step 8: Write tests for MatchmakingService

## Test Scenarios
- Player clicks "Find Match" and is successfully presented with an opponent's base
- A player with an active shield cannot be found as an opponent in matchmaking
- A player cannot be matched against themself
- Player with no troops cannot initiate matchmaking (future: when troops implemented)
