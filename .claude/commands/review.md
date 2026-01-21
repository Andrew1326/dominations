---
description: Perform thorough code review for bugs, security, and quality issues
allowed-tools: Bash, Read, Grep, Glob
argument-hint: [files or "staged" or "branch"]
---

# Code Review Workflow

Perform a thorough code review focused on real issues.

## Scope

$ARGUMENTS

- If "staged" -> Review staged changes: `git diff --cached`
- If "branch" -> Review branch changes: `git diff main...HEAD`
- If file paths -> Review those specific files
- If empty -> Review all uncommitted changes: `git diff`

## Step 1: Get Changes

```bash
# Choose based on scope
git diff --cached           # staged
git diff main...HEAD        # branch
git diff                    # uncommitted
```

## Step 2: Review for Issues

### Bug Detection (High Priority)
- Logic errors in game mechanics
- State synchronization issues
- Pathfinding edge cases
- Resource calculation errors
- Off-by-one in grid operations

### Security/Anti-Cheat (Critical)
- Client trust violations (trusting client-calculated values)
- Missing server validation
- Race conditions in state updates
- Exploitable timing windows
- Resource manipulation vulnerabilities

### Game-Specific Issues
- Depth sorting problems in isometric rendering
- Memory leaks (unit pooling, event listeners)
- Performance in hot paths (pathfinding, rendering loops)
- Missing collision checks
- Incorrect coordinate transformations

### Code Quality
- Missing error handling for network failures
- Code that will be difficult to maintain
- Performance issues at scale (100+ units)
- Missing validation at trust boundaries

## Step 3: Rate Confidence

For each issue found:
- **80-100%** confidence -> REPORT
- **50-79%** -> Only mention if significant
- **Below 50%** -> DO NOT REPORT

## Step 4: Output Report

```markdown
## Code Review Results

### Critical Issues
**[CRITICAL]** src/path/file.ts:123
Issue: <description>
Confidence: 95%
Category: Anti-Cheat
Fix: <specific suggestion>

### Important Issues
**[IMPORTANT]** src/path/file.ts:456
Issue: <description>
Confidence: 85%
Category: Bug
Fix: <specific suggestion>

### Summary
- Files reviewed: X
- Critical issues: Y
- Important issues: Z
- Recommendation: APPROVE / REQUEST CHANGES
```

## Step 5: Verify Build

```bash
npm run build    # Check for build errors
npm test         # Run tests
```

---

## Quality Over Quantity

Focus on real issues. 3 genuine problems are more valuable than 20 questionable nitpicks.
