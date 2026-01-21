---
description: Create or implement a story with acceptance criteria
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
argument-hint: <story name or "create" for new>
---

# Story Workflow

Work with story files for implementation and testing.

## Arguments

$ARGUMENTS

## Mode Detection

- If argument is "create" or "new" -> Create a new story
- If argument matches existing story -> Implement that story
- Otherwise -> Search for matching story

## Create New Story

### Step 1: Gather Requirements

Ask user for:
1. Feature name
2. Brief description
3. Key acceptance criteria

### Step 2: Create Story File

Create `docs/planning/stories/<feature-name>.story.md`:

```markdown
# <Feature Name>

## Overview
<Brief description of the feature>

## User Stories
- As a player, I want to <action> so that <benefit>

## Acceptance Criteria

### AC1: <Criterion Name>
- Given <precondition>
- When <action>
- Then <expected result>

### AC2: <Criterion Name>
- Given <precondition>
- When <action>
- Then <expected result>

## Technical Notes

### Client
- <Phaser scenes/entities affected>
- <UI components needed>

### Server
- <Colyseus room changes>
- <MongoDB schema changes>
- <Validation requirements>

### Anti-Cheat
- <What server must validate>
- <What client cannot be trusted with>

## Out of Scope
- <What this feature does NOT include>
```

## Implement Existing Story

### Step 1: Load Story

Read the story file from `docs/planning/stories/`

### Step 2: Review Acceptance Criteria

List all ACs and their status:
- [ ] AC1: ...
- [ ] AC2: ...

### Step 3: Implement

For each AC:
1. Write failing test
2. Implement the feature (client and/or server)
3. Verify test passes
4. Mark AC as done

### Step 4: Update Story

Mark completed ACs in the story file.

---

## Story Files Location

```
docs/planning/stories/
├── base-building.story.md
├── resource-system.story.md
├── combat-system.story.md
└── ...
```

## Related Tests

```
client/__tests__/
server/__tests__/
shared/__tests__/
```
