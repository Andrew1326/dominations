# Phase 1: Base Building MVP

## Overview
A client-only prototype for an isometric base builder, allowing users to place buildings on a grid and save the layout to local storage.

## User Stories
- As a player, I want to see an isometric grid so that I can plan my base layout
- As a player, I want to select and place buildings so that I can build my civilization
- As a player, I want my base to be saved so that I don't lose progress when I close the browser

## Acceptance Criteria

### AC1: Isometric Grid Rendering
- Given the application is loaded
- When the main scene initializes
- Then a visible isometric grid is rendered on the canvas

### AC2: Building Selection
- Given the game is running
- When the user selects a building type (Town Center, House, Farm) from UI
- Then that building type becomes the active selection for placement

### AC3: Building Preview with Snap
- Given a building type is selected
- When the user moves the mouse over the grid
- Then a preview building snaps to the nearest grid tile
- And shows green for valid placement, red for invalid

### AC4: Building Placement with Collision
- Given a valid placement location (unoccupied tile)
- When the user clicks
- Then the building is placed at that grid position
- And the tile is marked as occupied
- And clicking on occupied tiles does nothing

### AC5: LocalStorage Persistence
- Given buildings have been placed
- When the user refreshes the browser
- Then all buildings are restored in their correct positions

## Technical Notes

### Client Files to Create
- `client/index.html` - HTML host for Phaser canvas
- `client/src/main.ts` - Entry point, Phaser game config
- `client/src/game/scenes/MainMap.ts` - Primary game scene
- `client/src/game/systems/GridSystem.ts` - Isometric grid logic
- `client/src/game/entities/Building.ts` - Building base class and types
- `client/src/ui/` - React/simple HTML UI for building selection

### Shared Files to Create
- `shared/types.ts` - BuildingData, BaseLayout interfaces
- `shared/constants.ts` - Grid size, building definitions

### Assets Needed
- Placeholder sprites for grid tiles
- Placeholder sprites for Town Center, House, Farm

## Implementation Steps
- [x] Step 1: Setup Phaser 3 TypeScript project with build tooling
- [x] Step 2: Implement GridSystem with coordinate conversion functions
- [x] Step 3: Create MainMap scene with grid rendering
- [x] Step 4: Create Building entity classes
- [x] Step 5: Add mouse input and building preview (ghost building)
- [x] Step 6: Implement placement logic with collision detection
- [x] Step 7: Add building selection UI
- [x] Step 8: Implement localStorage save/load

## Test Scenarios
- Place a building and verify grid coordinates are correctly stored
- Attempt to place a building on occupied tile - action should be blocked
- Place multiple buildings, refresh browser, confirm all restored correctly
- Verify coordinate conversion: screen → grid → screen roundtrips correctly
