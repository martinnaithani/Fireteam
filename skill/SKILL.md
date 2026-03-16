---
name: fireteam
description: "Persistent memory and task coordination for AI coding sessions. Creates a .fireteam/ folder with mission context, task state, checkpoints, and handoff notes that survive session restarts, context limits, and crashes. Use this skill whenever the user wants to set up a fireteam, continue a fireteam, resume after a crash, add fireteam to a project, coordinate agents, split work across sessions, write checkpoints, create handoffs, or manage multi-session AI coding workflows. Also triggers on 'bootstrap from PRD', 'coordinate my agents', or 'pick up where I left off'. Do NOT use for single-turn coding questions, general project management without AI agents, or questions about military fire teams."
---

# Fireteam — Persistent Memory for AI Coding Sessions

Fireteam gives AI coding agents a memory that survives session restarts, context limits, and crashes. It uses a `.fireteam/` folder of structured markdown files — mission context, task state, progress checkpoints, and handoff notes — that the agent reads at session start and writes during work.

**Primary use case:** One agent working across multiple sessions on the same project. `.fireteam/` files carry context forward so the agent never starts from zero.

**Secondary use case:** 2-6 agents coordinating on the same codebase through shared `.fireteam/` files — task claims, handoffs, and conflict prevention.

**Core mechanic:** Every AI agent can read and write files. Fireteam uses the file system as the persistent memory layer.

## CRITICAL: Scope Boundaries

**Fireteam operates ONLY within the current working directory.** These rules are non-negotiable:

1. **NEVER navigate to, read, scan, or reference files outside the current working directory.** Not parent directories, not sibling directories, not the user's home folder, not other projects. The project boundary is the current working directory — period.

2. **NEVER search the filesystem for other projects.** If the current directory is empty and the user asked to set up a fireteam, set it up HERE. Do not go looking for code elsewhere.

3. **All `.fireteam/` files are created in the current working directory.** Not in a discovered project, not in a parent directory.

4. **Recon scans ONLY the current working directory.** If the directory is empty, recon finds nothing — that's correct. Proceed as greenfield.

5. **If the current directory seems wrong** (empty when user said "existing project"), ASK the user: "This directory appears empty. Would you like to set up a greenfield fireteam here, or should you navigate to your project first?" Do NOT go exploring.

## When to Use This Skill

**Session continuity (primary):**
- User wants their agent to remember context across sessions
- User says "continue my fireteam" or "pick up where I left off"
- User says "set up a fireteam" for a new or existing project
- User wants to save progress: "write a checkpoint"
- User is resuming after a crash or context limit

**Multi-agent coordination (secondary):**
- User wants multiple AI agents working on the same project
- User needs to create a handoff between agents
- User says "coordinate my agents" or "onboard agents"

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

Use everything available **within the current working directory.** Do NOT ask the user which flow to use.

| PRD provided? | Code exists in CWD? | Action |
|:---:|:---:|---|
| Yes | No | **Greenfield.** Plan forward from PRD. |
| No | Yes | **Existing project.** Run recon on CWD (Phase 3), then ask user for goals. |
| Yes | Yes | **Phase 2 build.** Recon maps CWD reality, PRD defines what's next. |
| No | No | **Empty directory.** Ask the user: "What are we building?" Do NOT search other directories. |

### Phase 3: Recon (when code exists in CWD)

Only runs when there's existing code **in the current working directory.** Read the codebase structure to understand what's already built. See `references/recon.md` for the full procedure.

**SCOPE: Scan ONLY the current working directory. Never traverse up or into sibling directories. If CWD is empty, skip recon entirely — proceed as greenfield.**

Quick version — scan these files:
- README / docs → what the project claims to be
- Package files (package.json, requirements.txt, Cargo.toml, go.mod) → stack
- Directory listing (2 levels deep) → code organization
- Config files (.env.example ONLY — never .env, config/, CI files) → deployment, services
- Entry points (main files, route definitions) → API surface
- Recent git log (if git, last 20 commits) → recent work

**SECURITY: Never read `.env` files, credential files, or SSH keys. Only read `.env.example`/`.env.sample`. Write variable names to INTEL.md, never values.** See `references/recon.md` for full credential safety rules.

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

**Step 7 — INTEL.md:** Seed with key facts. For greenfield: stack, constraints, design direction from PRD. For existing projects: everything discovered in recon — file paths, API routes, database schema, conventions. **NEVER write actual credential values — only variable names and service descriptions.** Use template from `assets/templates/intel.md`.

**Step 8 — Field log:** Create today's `memory/YYYY-MM-DD.md`. Log setup actions.

**Step 9 — Checkpoint:** Write `checkpoints/team-lead.md` with current state.

**Step 10 — Debrief:** Tell the user:
1. Operators proposed and why
2. Objective breakdown with dependencies
3. Which operator to deploy next
4. The onboarding prompt for that operator

### Phase 5: Execute & Continue

**Single agent (default):** After completing setup, begin working on the highest-priority task from the board. Work through tasks sequentially — when one finishes, write a handoff note (what was built, API contracts, file paths), update the board, and start the next ready task. Checkpoint every 15 minutes.

When the session ends (context limit, crash, user stops), everything is saved in `.fireteam/`. The next session reads the checkpoint, handoff notes, and board — picks up immediately.

**Multiple agents (when the user wants parallelism):** Generate onboarding prompts for each additional agent. The user pastes these into separate terminals. Each agent reads `.fireteam/`, claims its assigned tasks, and works independently. Handoffs transfer context between agents.

Onboarding prompt for additional agents:
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

## Fireteam Dashboard

The skill includes `assets/dashboard.html` — a visual status dashboard. After setting up `.fireteam/`, tell the user:

"Open `dashboard.html` in Chrome or Edge. Click 'Open .fireteam/ Folder' and select your project's `.fireteam/` directory. You'll see the task board, roster, handoffs, and activity in real-time."

The dashboard reads `.fireteam/` files directly via the browser's File System Access API. No server needed. Auto-refresh available (every 5 seconds). Chrome/Edge only — Firefox and Safari don't support the required API.

When setting up a fireteam, copy `assets/dashboard.html` into the project root so it's easy to find:
```bash
cp assets/dashboard.html [project-root]/fireteam-dashboard.html
```
