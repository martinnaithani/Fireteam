---
name: fireteam
description: "Multi-agent coordination protocol for AI coding tools. Sets up a file-based system so 2-6 AI agents (Claude Code, Cursor, Aider, etc.) can work on the same codebase without conflicts. Use this skill whenever the user mentions coordinating agents, setting up a fireteam, multi-agent projects, splitting work across AI agents, adding coordination to an existing project, creating handoffs between agents, writing checkpoints, resuming after crashes, or managing a team of AI coding agents. Also use when the user says 'bootstrap from PRD', 'onboard agents', 'coordinate my agents', or 'set up agent coordination'. Do NOT use for single-agent coding tasks, general project management without AI agents, or questions about military fire teams."
---

# Fireteam — Multi-Agent Coordination Protocol

Fireteam is a file-system-native protocol that lets 2-6 AI agents coordinate on the same codebase. No server, no database — just structured markdown files in a `.fireteam/` folder that agents read at session start and write during work.

**Core mechanic:** Agents coordinate through files. Every agent can read and write files — that's the universal capability. Fireteam uses it as the message bus.

## When to Use This Skill

- User wants multiple AI agents working on the same project
- User says "set up a fireteam" or "coordinate my agents"
- User has a PRD and wants to split work across agents
- User has an existing codebase and wants to add multi-agent coordination
- User needs to create a handoff, write a checkpoint, or resume after a crash
- User wants to bootstrap a new project from a PRD with multiple agents

## Adaptive Entry Point

Fireteam uses ONE entry sequence that adapts to context. Never ask the user "are you bootstrapping or initializing?" — detect the state and act.

### Phase 1: Context Assessment

Before doing anything, assess the project state:

```
Does .fireteam/ exist and have a populated MISSION.md?
├─ YES → REJOIN: run heartbeat, read board, pick up work (skip to Phase 5)
├─ .fireteam/ exists but empty/stale → treat as new setup
└─ NO → new setup, continue to Phase 2
```

### Phase 2: Gather Inputs

Use everything available. Do NOT ask the user which flow to use.

| PRD provided? | Code exists? | Action |
|:---:|:---:|---|
| Yes | No | **Greenfield.** Plan forward from PRD. |
| No | Yes | **Existing project.** Run recon first (Phase 3), then ask user for goals. |
| Yes | Yes | **Phase 2 build.** Recon maps reality, PRD defines what's next. |
| No | No | **Interview.** Ask: "What are we building? What exists already?" |

### Phase 3: Recon (when code exists)

Only runs when there's existing code. Read the codebase structure to understand what's already built. See `references/recon.md` for the full procedure.

Quick version — scan these files:
- README / docs → what the project claims to be
- Package files (package.json, requirements.txt, Cargo.toml, go.mod) → stack
- Directory listing (2 levels deep) → code organization
- Config files (.env.example, config/, CI files) → deployment, services
- Entry points (main files, route definitions) → API surface
- Recent git log (if git, last 20 commits) → recent work

Present findings to the user for confirmation before creating tasks. Output goes into INTEL.md.

### Phase 4: Setup .fireteam/

Run `scripts/setup.sh` to create the directory structure. Then populate:

**Step 1 — MISSION.md:** Translate PRD goals (or recon findings + user goals) into mission statement, goals, scope, constraints. Use template from `assets/templates/mission.md`.

**Step 2 — ROSTER.md:** Propose operators based on work ahead. Reference `references/presets.md` for suggested team compositions. Use template from `assets/templates/roster.md`.

**Step 3 — SOUL files:** For EACH operator, create `checkpoints/[callsign]-soul.md` using template from `assets/templates/soul.md`. Must include: role, core duties, deliverables, success metrics, workflow pattern, boundaries, communication style.

**Step 4 — HEARTBEAT files:** For EACH operator, create `checkpoints/[callsign]-heartbeat.md` from `assets/templates/heartbeat.md`.

**Step 5 — Objectives:** Create task files in `tasks/OBJ-XXX.md` from `assets/templates/task.md`. Rules:
- Every objective MUST have a goal chain (Mission → Goal → Task → Why)
- Each objective is atomic: one deliverable, completable in one session
- Map dependencies between objectives
- For existing projects: tasks MUST reference real file paths and existing patterns from recon
- Assign to operator callsigns

**Step 6 — BOARD.md:** Populate with all objectives. Use template from `assets/templates/board.md`.

**Step 7 — INTEL.md:** Seed with key facts. For greenfield: stack, constraints, design direction from PRD. For existing projects: everything discovered in recon — file paths, API routes, database schema, conventions. Use template from `assets/templates/intel.md`.

**Step 8 — Field log:** Create today's `memory/YYYY-MM-DD.md`. Log setup actions.

**Step 9 — Checkpoint:** Write `checkpoints/team-lead.md` with current state.

**Step 10 — Debrief:** Tell the user:
1. Operators proposed and why
2. Objective breakdown with dependencies
3. Which operator to deploy next
4. The onboarding prompt for that operator

### Phase 5: Onboarding & Operations

**For the Team Lead (first agent):** You ARE the Team Lead after completing Phase 4.

**Onboarding prompt for subsequent operators:**
```
You are the [ROLE] operator. Callsign: [callsign].
Read these files in order:
1. .fireteam/MISSION.md
2. .fireteam/CONVENTIONS.md
3. .fireteam/ROSTER.md
4. .fireteam/checkpoints/[callsign]-soul.md
5. .fireteam/INTEL.md
6. .fireteam/memory/[today].md
7. .fireteam/checkpoints/[callsign].md (if resuming)
8. .fireteam/BOARD.md
9. .fireteam/handoffs/ (check for files addressed to you)
Run your heartbeat, then pick up your highest-priority objective.
```

**For recovery after crashes:** See `references/recovery.md` for the full 5-phase resume protocol.

## Core Protocol Rules

These rules govern all agent behavior within Fireteam. Full details in `references/conventions.md`.

### Goal Chains (mandatory)
Every task traces: Mission → Goal → Task → Why It Matters. No goal chain = don't start the task.

### Atomic Checkout
Before starting a task, check `checked_out_by`. If another agent's ID is there, don't touch it. Write your ID to claim it.

### Progressive Checkpointing
Don't wait for session end. Update `checkpoints/[you].md` after meaningful work, before risky operations, and every ~15 minutes.

### Heartbeat (every session start)
Read: MISSION → CONVENTIONS → ROSTER → SOUL → INTEL → field log → checkpoint → BOARD → handoffs → comms. Then assess: what is the highest-priority action?

### Handoffs (when your work feeds another agent)
Create `handoffs/HO-XXX.md`: what you built, file locations, decisions, API contracts, what the next agent needs to do. A good handoff prevents re-work.

### Session End Protocol
1. Update field log
2. Write checkpoint
3. Update BOARD.md
4. Create handoffs if needed

### File Permissions
- You MAY modify: your task files, BOARD.md (your rows), today's field log (append), your checkpoint, project code your task requires
- You MUST NOT modify: MISSION.md (Team Lead only), CONVENTIONS.md (Human only), ROSTER.md (Team Lead only), INTEL.md (Team Lead only), other agents' files

### Task Lifecycle
```
backlog → in-progress → review → done
              ↓
           blocked (create comms thread)
```

### Conflict Resolution
If you find conflicting work: STOP. Create high-priority comms thread. Wait for Team Lead or Human.

## .fireteam/ Directory Structure

```
.fireteam/
├── MISSION.md              ← why we're here (Team Lead owns)
├── CONVENTIONS.md          ← rules of engagement (Human owns)
├── ROSTER.md               ← who's on the team (Team Lead owns)
├── BOARD.md                ← objectives kanban (Team Lead owns rows, agents update theirs)
├── INTEL.md                ← curated knowledge (Team Lead owns)
├── tasks/OBJ-XXX.md        ← individual objectives with goal chains
├── handoffs/HO-XXX.md      ← context transfers between agents
├── comms/THREAD-XXX.md     ← async discussions
├── decisions/DEC-XXX.md    ← architecture/tech decision records
├── memory/YYYY-MM-DD.md    ← daily field logs (append-only)
└── checkpoints/
    ├── [callsign].md        ← progressive session state
    ├── [callsign]-soul.md   ← operator identity (mandatory)
    └── [callsign]-heartbeat.md ← session start checklist
```

## File References

Templates for all file types are in `assets/templates/`. Read the relevant template before creating any file.

| When creating... | Read template |
|---|---|
| A task | `assets/templates/task.md` |
| A handoff | `assets/templates/handoff.md` |
| A checkpoint | `assets/templates/checkpoint.md` |
| A SOUL file | `assets/templates/soul.md` |
| A heartbeat | `assets/templates/heartbeat.md` |
| A comms thread | `assets/templates/thread.md` |
| A decision record | `assets/templates/decision.md` |
| A field log entry | `assets/templates/fieldlog.md` |
| MISSION.md | `assets/templates/mission.md` |
| ROSTER.md | `assets/templates/roster.md` |
| BOARD.md | `assets/templates/board.md` |
| INTEL.md | `assets/templates/intel.md` |
| CONVENTIONS.md | `references/conventions.md` (copy as-is) |

For full protocol rules: `references/conventions.md`
For recovery after crashes: `references/recovery.md`
For codebase recon procedure: `references/recon.md`
For team composition presets: `references/presets.md`
