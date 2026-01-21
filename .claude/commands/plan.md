---
description: Plan a feature using Gemini CLI for full-context strategic analysis
allowed-tools: Bash, Read, Write, Edit
argument-hint: <feature description>
---

# Plan Feature Workflow

**Feature:** $ARGUMENTS

## Step 1: Call Gemini

```bash
gemini "Read docs/architecture.md.

Task: Plan implementation for: $ARGUMENTS

Output EXACTLY this format:

FEATURE_NAME: <kebab-case-name>

SUMMARY: <one line description>

ACCEPTANCE_CRITERIA:
- AC1: <criterion>
- AC2: <criterion>
- AC3: <criterion>

CLIENT_CHANGES:
- <file path>: <what to change>

SERVER_CHANGES:
- <file path>: <what to change>

SHARED_CHANGES:
- <file path>: <what to change>

IMPLEMENTATION_STEPS:
1. <step>
2. <step>
3. <step>

ANTI_CHEAT_CONSIDERATIONS:
- <what server must validate>

TEST_SCENARIOS:
- <test scenario 1>
- <test scenario 2>

Keep under 400 words."
```

## Step 2: Create Story File

Parse Gemini output and create `docs/planning/stories/<FEATURE_NAME>.story.md`:

```markdown
# <Feature Title>

## Overview
<SUMMARY from Gemini>

## Acceptance Criteria
<ACCEPTANCE_CRITERIA from Gemini, formatted as checkboxes>
- [ ] AC1: ...
- [ ] AC2: ...

## Technical Notes
### Client Changes
<CLIENT_CHANGES>

### Server Changes
<SERVER_CHANGES>

### Shared Changes
<SHARED_CHANGES>

### Anti-Cheat
<ANTI_CHEAT_CONSIDERATIONS>

## Implementation Steps
<IMPLEMENTATION_STEPS as checkboxes>
- [ ] Step 1
- [ ] Step 2

## Test Scenarios
<TEST_SCENARIOS>
```

## Step 3: Update Sprint

Add to `docs/planning/sprint.md` under "In Progress":
```markdown
- [ ] Implement <feature name> (see stories/<feature-name>.story.md)
```

## Step 4: Start Implementation

Proceed with the mandatory workflow:
1. Implement first step
2. Write tests for it
3. Verify with build and test
4. Continue to next step

Mark items complete in the story file as you go.
