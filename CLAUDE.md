# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

OpenCivilizations - browser-based MMORTS inspired by DomiNations.

## Mandatory Workflow

**Every implementation task follows this sequence:**

```
1. PLAN     → Complex? Gemini + create story + add to sprint.md (In Progress)
            → Simple? Brief plan + add to sprint.md (In Progress)
2. IMPLEMENT → Write the code (client and/or server)
3. TEST      → Write tests (MANDATORY)
4. VERIFY    → npm run build && npm test (must PASS)
5. REVIEW    → Self-check + Gemini review for complex changes
6. DONE      → Move task to Done in sprint.md
```

**Sprint Tracking (REQUIRED):**
- Start: Add task to `docs/planning/sprint.md` under "In Progress"
- Finish: Move task to "Done" section
- Complex tasks: Create story in `docs/planning/stories/<name>.story.md`

### When to Use Gemini

**Call Gemini first:**
```bash
gemini "Read docs/architecture.md. Plan: [TASK]"
```
- New game systems affecting 3+ files
- Architecture decisions (client-server split)
- Cross-cutting concerns

**Work directly:** Bug fixes, small edits, single component changes

### Slash Commands

| Command | Purpose |
|---------|---------|
| `/plan <feature>` | Strategic planning with Gemini |
| `/story <name>` | Create or implement a story |
| `/review [scope]` | Code review for bugs/security |
| `/sprint-status` | Check or update sprint progress |
| `/commit-push` | Commit and push changes |

### Native Agents

| Agent | When to Use |
|-------|-------------|
| `dev` | Implementation, bug fixes, tests |
| `architect` | System design, client-server split |
| `reviewer` | Thorough code review, anti-cheat audit |
| `strategist` | Full-context planning with Gemini |

## Project Structure

```
client/
  src/
    assets/         # Sprites, tiles, audio
    game/
      scenes/       # Phaser scenes (MainMap, Battle, Loading)
      entities/     # Buildings, Units, Projectiles
      systems/      # Pathfinding, Grid, Input
    ui/             # React/Vue overlays

server/
  src/
    rooms/          # Colyseus game rooms
    models/         # MongoDB schemas
    mechanics/      # Authoritative game logic

shared/
  constants.ts      # Building costs, unit stats
  types.ts          # Shared interfaces

docs/
  architecture.md   # System architecture
  planning/
    sprint.md       # Current sprint tasks
    backlog.md      # Future work
    stories/        # Feature specifications

.claude/
  agents/           # Native Claude agents
  skills/           # Auto-applied knowledge
  commands/         # Slash commands
  hooks/            # Event triggers
```

## Key Documents

| Document | Location |
|----------|----------|
| Architecture | `docs/architecture.md` |
| Sprint Tasks | `docs/planning/sprint.md` |
| Backlog | `docs/planning/backlog.md` |
| Stories | `docs/planning/stories/*.md` |
| Game Constants | `shared/constants.ts` |

## Technology Stack

| Component | Technology |
|-----------|------------|
| Game Engine | Phaser 3 |
| UI Framework | React or Vue |
| Backend | Node.js + Colyseus |
| Database | MongoDB |
| Cache | Redis |
| Language | TypeScript (strict) |

## Core Principle: Authoritative Server

**Never trust the client.**

```typescript
// BAD - Client calculates
client.resources.gold += 100;

// GOOD - Server calculates
sendToServer({ action: 'collect', buildingId: 'farm1' });
// Server validates, calculates, updates DB
```

## Code Standards

- TypeScript strict mode
- Server validates all player actions
- Client displays state, captures input
- Colyseus for state synchronization
- MongoDB for persistence

## Isometric Grid

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

## Domain Terms

| Term | Meaning |
|------|---------|
| Base | Player's civilization layout |
| Building | Structure on the grid |
| Unit | Trainable troop with AI |
| Resource | Food, Gold, Oil |
| Age | Technology era (Stone → Space) |
| Nation | Civilization with unique bonuses |

## Git Guidelines

**Only commit application logic.**

**Never commit:**
- `node_modules/`
- `dist/`, `build/`
- `.idea/`
- `.env*`
- `.claude/reflections/`

**Commit format:**
```bash
git commit -m "$(cat <<'EOF'
type: short description

- Detail
EOF
)"
```

No footers, no Co-Authored-By.

## Implementation Roadmap

1. **Phase 1: The Architect** - Base building, grid system, placement
2. **Phase 2: The Economist** - Resources, timers, server backend
3. **Phase 3: The General** - Combat, pathfinding, units
4. **Phase 4: The Emperor** - Multiplayer, matchmaking, polish

See `docs/planning/backlog.md` for detailed task breakdown.
