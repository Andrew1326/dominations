# Current Sprint

## Goal
Phase 3: The General (Combat & AI)

## In Progress
None

## TODO
None

## Done
- [x] Joined walls (autotiling) — added --rotate-z to render_building.py and rendered the wall in both isometric orientations (wall.png / wall_b.png). New pure wallTiling.ts picks each wall's orientation from its 4-neighbours (row-run / col-run / corner→row / isolated→default); MainMap.refreshWalls() preloads both textures and re-skins every wall on placement/removal/load so a run forms one continuous fence. Walls use WALL_FOOTPRINT_FACTOR=1.15 so a run abuts end-to-end. The ornate medieval wall didn't tile cleanly (discrete merlons/machicolation/3D front face looked crooked when joined), so added a purpose-built tileable wall: blender/buildings/wall.py build_simple_wall (registered as 'wallTile') — symmetric, exactly one tile long, evenly-spaced merlons (0.4) that continue across seams. Rendered to wall.png + wall_b.png (rotated). 6 autotiling unit tests; verified live (continuous, even, straight battlement along each run + clean corner).
- [x] Building spacing rule — ordinary buildings require a 1-cell gap (can't be placed flush); fences (walls, marked `allowAdjacent`) are exempt and can touch anything/each other. Added shared/placement.ts (pure: requiresSpacing/withinSpacing/findSpacingConflict), enforced in server validatePlacement (authoritative) and mirrored in the client ghost + placeBuilding guard. 16 new tests (shared rule + validatePlacement); verified live (ghost red on invalid, green flush against a wall).
- [x] Center building sprites on the footprint — the baked drop shadow was offsetting the cropped sprite (down-left), so buildings floated above/beside the green footprint. Added --no-shadow to render_building.py, re-rendered all 25 sprites building-only (no ground, no shadow) → content is now horizontally centred, and anchored the sprite's base (SPRITE_BASE_Y) at the footprint's front vertex so the base-centre sits on the tile centre. Verified live (ghost base sits on the green diamond).
- [x] Fix wall (and small building) demolish — sprites now rise above their footprint, so footprint-cell hit-testing missed the visible building. findBuildingAt now hit-tests the footprint diamond first (precise) then the sprite bounds (catches the raised art), frontmost match wins. Walls are removable again. Verified live (Demolishing Wall + refund) and with unit tests.
- [x] Dev: generous resources for playtesting — raised STARTING_RESOURCES to 1,000,000 each and BASE_RESOURCE_CAP to 10,000,000, and added a NODE_ENV!=='production' top-up in getOrCreateGuestUser so existing guests also get the money on reconnect. (Temporary; gated to non-production.)
- [x] Fix building/grid alignment — building renders baked in a 3.5×3.5 "Ground" plate + shadow that clashed with the grid. Added a --no-ground flag to render_building.py (strips the Ground mesh), re-rendered all 25 used (age, building) romans sprites building-only, re-cropped, and re-calibrated Building.ts to anchor the sprite bottom-centre at the footprint's front vertex (SPRITE_FOOTPRINT_FACTOR). Buildings now sit on the selected tiles. Verified via the placement ghost (green footprint diamond).
- [x] Render building sprites on the base canvas — Building/GhostBuilding now draw the rendered image (sprite) instead of a colored diamond, with the diamond kept as fallback for buildings without art. Added a generated image manifest (scripts/gen-building-manifest.mjs → src/game/ui/buildingImageManifest.ts), manifest-backed image resolution in buildingCatalog, and a Phaser texture preload in MainMap. Sprite scaled/anchored so its baked ground matches the footprint (GROUND_WIDTH_RATIO / GROUND_ORIGIN_Y) so the building lines up with the selected tiles.
- [x] Gold-only building economy — all building costs in BUILDING_COSTS_BY_AGE reduced to gold only (removed food/oil). Catalog menu and demolish refund follow automatically. Regression test guards it.
- [x] Tight-crop building sprites — added blender/crop_building_assets.py and ran it on the 25 served PNGs (512×512 → square content crop + uniform margin) so catalog thumbnails display large and consistently instead of small/uneven.
- [x] Promote building art into served assets — copied 15 rendered PNGs from blender/drafts into client/public/assets/buildings/<age>/romans/, and added age-fallback image resolution (getBuildingImageCandidates) so the catalog menu shows real images for all 10 modeled buildings. The 9 buildings without Blender models still show color swatches.
- [x] Building catalog menu — "Add Building" button opens a modal listing every building grouped by age, each with image (or color-swatch fallback), size and price; click a card to select it for placement. Affordability greys out cards you can't afford.
- [x] Building removal (demolish) on player base — Demolish button toggles demolish mode; click a building to remove it. Server-authoritative with 50% refund online; localStorage offline. Right-click/Esc cancels.
- [x] Implement Matchmaking System (see stories/matchmaking-system.story.md)
- [x] Implement Phase 3: Combat System (see stories/phase3-combat-system.story.md)
- [x] Implement Phase 2: Server Authoritative Economy (see stories/phase2-server-authoritative-economy.story.md)
- [x] Implement Phase 1: Base Building MVP (see stories/phase1-base-building-mvp.story.md)
- [x] Project structure setup
- [x] Claude Code configuration (agents, skills, commands)

## Blockers
None

## Notes
- Stories in `docs/planning/stories/` define acceptance criteria
- Use `/plan` command for Gemini-powered planning
- Server authority is critical - never trust client calculations
- Refer to README.md for implementation roadmap phases
