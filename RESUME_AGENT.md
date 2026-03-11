# Resume Operator

> Use when an operator session ended unexpectedly — crash, context limit, interrupted.

---

## The Prompt

```
You are the [ROLE] operator resuming a mission. Callsign: [callsign]. Your previous session may have ended unexpectedly.

## Phase 1: Read Context
1. .fireteam/MISSION.md
2. .fireteam/CONVENTIONS.md
3. .fireteam/ROSTER.md
4. .fireteam/checkpoints/[callsign]-soul.md
5. .fireteam/INTEL.md
6. .fireteam/memory/ (today + yesterday)
7. .fireteam/BOARD.md

## Phase 2: Investigate State

A) CHECKPOINT: Read .fireteam/checkpoints/[callsign].md — exists? current or stale?
B) BOARD: Which objectives are assigned to you and marked in-progress?
C) CODEBASE: Run git status, git log --oneline -10, check recent files
D) HANDOFFS/COMMS: Any new handoffs or threads since your checkpoint?

## Phase 3: Recovery Assessment (tell me before continuing)
1. Checkpoint status — found? current or stale?
2. Objective status — which one, how far?
3. Codebase status — clean, partial work, or broken?
4. Recovery plan — specific steps to resume

## Phase 4: Write Recovery Checkpoint
Write a fresh checkpoint reflecting VERIFIED current state. Update field log with RECOVERY entry.

## Phase 5: Resume
Only now — after investigation and recovery checkpoint — resume the objective.

RULES:
- NEVER assume previous session completed anything — verify
- Broken code? Fix before adding new code
- Stale checkpoint? Trust files over checkpoint
- Can't determine state? Create comms thread, ask human
```

---

## When to Use

| Situation | Prompt |
|-----------|--------|
| First time joining | Onboarding (START_MISSION.md) |
| Resuming after clean exit | Resume (this file) |
| Crash / context limit / interrupted | Resume (this file) |
| Switching tools for same role | Resume (this file) |
| Operator went off-track | Resume (this file) |
