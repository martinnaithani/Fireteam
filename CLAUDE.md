# Agent Instructions for Maintaining Fireteam

> Read HISTORY.md first. It contains the full design evolution and WHY every decision was made.

## What This Repo Is

Fireteam is a file-system-native protocol for coordinating AI agent squads. No server, no database, no dependencies — just markdown files. This is the boilerplate repo that users copy into their projects.

## Critical Constraints

1. **ZERO DEPENDENCIES.** The `.fireteam/` folder works with a text editor. The CLI needs only bash. The dashboard needs only Python 3.6+ stdlib. Do not add npm, pip, or any package manager.

2. **PORTABLE BASH.** The CLI must work on macOS AND Linux. Use the `sedi()` wrapper for sed. Do not use `grep -P` (Perl regex), `readlink -f` (not on macOS), or GNU-specific flags.

3. **BACKWARD COMPATIBLE TEMPLATES.** Thousands of projects may use these templates. Adding fields is safe. Renaming or removing fields breaks existing projects.

4. **THE THREE PROMPTS ARE LOAD-BEARING.** `START_MISSION.md`, `RESUME_AGENT.md`, and the onboarding prompt each have a specific multi-step process. Every step exists for a reason documented in HISTORY.md. Do not simplify them without understanding the rationale.

## File Structure

```
fireteam/
├── README.md              ← GitHub landing page
├── HISTORY.md             ← Design evolution (READ THIS)
├── CLAUDE.md              ← You are here
├── PRD_TEMPLATE.md        ← User fills this to start
├── START_MISSION.md       ← Bootstrap prompt (creates Team Lead)
├── RESUME_AGENT.md        ← Recovery prompt (after crashes)
├── fireteam.sh            ← CLI tool (portable bash)
├── hq.py                 ← Live Command Center (HTTP server + daemon + dashboard)
├── LICENSE                ← MIT
├── .gitignore
└── .fireteam/             ← THE PROTOCOL (users copy this into projects)
    ├── MISSION.md         ← Why we're here
    ├── CONVENTIONS.md     ← Rules of engagement
    ├── ROSTER.md          ← Who's on the team
    ├── BOARD.md           ← Objective status
    ├── INTEL.md           ← Curated knowledge
    ├── README.md          ← Quick reference
    ├── tasks/             ← OBJ-XXX.md files
    ├── handoffs/          ← HO-XXX.md files
    ├── comms/             ← THREAD-XXX.md files
    ├── decisions/         ← DEC-XXX.md files
    ├── memory/            ← YYYY-MM-DD.md field logs
    ├── checkpoints/       ← [callsign].md + soul + heartbeat files
    ├── presets/           ← Team configurations (Solo, Duo, Squad, Platoon)
    ├── pro.yml            ← Pro Mode config (callsign → CLI mapping)
    └── templates/         ← 8 templates (task, handoff, thread, decision,
                              fieldlog, checkpoint, soul, heartbeat)
```

## Naming Conventions (Do Not Change)

| Type | Pattern | Prefix |
|------|---------|--------|
| Objectives | `OBJ-XXX.md` | OBJ |
| Handoffs | `HO-XXX.md` | HO |
| Threads | `THREAD-XXX.md` | THREAD |
| Decisions | `DEC-XXX.md` | DEC |
| Field Logs | `YYYY-MM-DD.md` | date |
| Checkpoints | `[callsign].md` | callsign |
| Souls | `[callsign]-soul.md` | callsign |
| Heartbeats | `[callsign]-heartbeat.md` | callsign |

## Terminology (Do Not Change)

| Term | Meaning |
|------|---------|
| Fireteam | The coordinated agent squad |
| Operator | An individual AI agent |
| Callsign | Agent identifier (e.g., `backend`, `frontend`) |
| Team Lead | The first agent; owns coordination |
| Objective | A task/work item (OBJ-XXX) |
| Field Log | Daily append-only activity record |
| Intel | Curated long-term project knowledge |
| Heartbeat | Session-start situational awareness checklist |
| Goal Chain | Mission → Goal → Task → Why traceability |

## How to Test Changes

1. Copy `.fireteam/` into a temp project directory
2. Run `./fireteam.sh task "Test"` — should create `OBJ-001.md`
3. Run `./fireteam.sh status` — should show stats
4. Run `./fireteam.sh soul "test-agent"` — should create soul file
5. Run `./fireteam.sh heartbeat "test-agent"` — should create heartbeat file
6. Run `python3 dashboard.py` — should generate `dashboard.html` without errors
7. Use the START_MISSION.md prompt with the test PRD in an AI agent — verify the full bootstrap works

## Key Design Decisions to Preserve

See HISTORY.md Section 12 (Architecture Principles) and Section 13 (What We Explicitly Rejected) for the full rationale. The short version:

- Files over databases
- Markdown over JSON
- Convention over enforcement
- Pull (read at start) over push (watch for changes)
- Explicit assignment over automatic routing
- Small teams (2-6) over large organizations
- Zero config over configuration wizards
