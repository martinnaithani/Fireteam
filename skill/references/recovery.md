# Recovery Protocol

Use when an operator session ended unexpectedly — crash, context limit, interrupted, or went off-track.

## When to Use

| Situation | Action |
|-----------|--------|
| First time joining | Use onboarding prompt (see SKILL.md Phase 5) |
| Resuming after clean exit | Use this recovery protocol |
| Crash / context limit / interrupted | Use this recovery protocol |
| Switching tools for same role | Use this recovery protocol |
| Operator went off-track | Use this recovery protocol |

## The 5-Phase Recovery Sequence

### Phase 1: Read Context

Read these files in order:
1. `.fireteam/MISSION.md`
2. `.fireteam/CONVENTIONS.md`
3. `.fireteam/ROSTER.md`
4. `.fireteam/checkpoints/[callsign]-soul.md`
5. `.fireteam/INTEL.md`
6. `.fireteam/memory/` (today + yesterday)
7. `.fireteam/BOARD.md`

### Phase 2: Investigate State

Do NOT assume the previous session completed anything. Verify everything.

A) **CHECKPOINT:** Read `.fireteam/checkpoints/[callsign].md` — does it exist? Is it current or stale?
B) **BOARD:** Which objectives are assigned to you and marked in-progress?
C) **CODEBASE:** Run `git status`, `git log --oneline -10`, check recently modified files
D) **HANDOFFS/COMMS:** Any new handoffs or threads since your checkpoint?

### Phase 3: Recovery Assessment

Before doing any work, tell the user:
1. Checkpoint status — found? current or stale?
2. Objective status — which one, how far along?
3. Codebase status — clean, partial work, or broken?
4. Recovery plan — specific steps to resume

### Phase 4: Write Recovery Checkpoint

Write a fresh checkpoint reflecting the VERIFIED current state. Include `type: recovery` in the checkpoint. Update field log with a RECOVERY entry noting what was found.

### Phase 5: Resume

Only now — after investigation and recovery checkpoint — resume the objective.

## Critical Rules

- **NEVER** assume the previous session completed anything — verify by checking files
- **Broken code?** Fix before adding new code
- **Stale checkpoint?** Trust actual files over the checkpoint
- **Can't determine state?** Create a comms thread and ask the human
- **Conflicting state?** STOP. Create high-priority comms thread. Wait for resolution.
