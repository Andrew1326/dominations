---
description: Check sprint status, get next task, or update progress
allowed-tools: Bash, Read, Write, Edit
argument-hint: [status|next|update|done <task>]
---

# Sprint Status Workflow

Manage sprint tasks and progress.

## Command

$ARGUMENTS

- `status` or empty -> Show current sprint status
- `next` -> Get next priority task
- `update` -> Update sprint file
- `done <task>` -> Mark task as done

## Show Status

Read and display `docs/planning/sprint.md`:

```bash
cat docs/planning/sprint.md
```

Present summary:
- Current phase/goal
- Tasks in progress
- Tasks remaining
- Any blockers

## Get Next Task

### Option A: Simple (read sprint.md)

Read `docs/planning/sprint.md` and find the first unchecked task.

### Option B: With Gemini Context

```bash
gemini "Read docs/planning/sprint.md and docs/architecture.md.
What's the next priority TODO? Give compact instructions:
1. What to do
2. Key requirements
3. Files to touch (client/server/shared)
4. Acceptance criteria
Under 200 words."
```

## Update Sprint

Modify `docs/planning/sprint.md`:
- Move tasks between sections
- Add new tasks
- Update blockers

## Mark Task Done

Edit `docs/planning/sprint.md`:
- Change `- [ ]` to `- [x]` for the completed task
- Move to Done section if appropriate

---

## Sprint File Format

```markdown
# Current Sprint

## Goal
<Sprint objective - current implementation phase>

## In Progress
- [ ] Task being worked on

## TODO
- [ ] Next task
- [ ] Another task

## Done
- [x] Completed task

## Blockers
- Any blocking issues

## Notes
- Important context
```

## Related Files

- `docs/planning/sprint.md` - Current sprint
- `docs/planning/backlog.md` - Future work
- `docs/planning/stories/` - Detailed story specs
