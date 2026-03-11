# Changelog

All notable changes to Fireteam. For the full design narrative, see [HISTORY.md](HISTORY.md).

---

## [Unreleased] — Planned from Agency-Agents Analysis

**Source:** [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents/) (19.2k stars, 61 agents across 9 divisions)

### Planned: Rich SOUL Files
- Current SOUL_TEMPLATE is functional but generic (role, duties, boundaries)
- Agency-Agents proved personality-driven agents resonate: each has unique voice, communication style, quirks, concrete deliverables with code examples, and success metrics
- **Upgrade:** Rewrite SOUL_TEMPLATE with: personality traits, communication voice, example deliverables, success metrics, workflow patterns, and learning memory
- **Why:** An agent that says "Let me sketch the architecture before we write code" performs differently than one that just lists "Duties: API design"

### Planned: Mission-Type Presets
- Current presets are size-based: Solo (2), Duo (2), Squad (4), Platoon (6+)
- Agency-Agents organizes by division (Engineering, Design, Marketing, Product, Testing, Support) and shows scenario-based team compositions
- **Upgrade:** Add mission-type presets alongside size presets: "MVP Launch", "Marketing Campaign", "API Product", "Enterprise Feature", "Content Pipeline"
- Each preset pulls the right specialist operators with pre-written SOUL files

### Planned: Multi-Tool Integration
- Agency-Agents ships conversion scripts for Claude Code, Cursor (.mdc), Aider (CONVENTIONS.md), Windsurf (.windsurfrules), Gemini CLI, OpenCode
- **Upgrade:** `fireteam.sh integrate cursor|aider|windsurf` generates tool-specific config files that point agents to `.fireteam/`
- Cursor: `.cursor/rules/fireteam.mdc` with operator context
- Aider: merges protocol into `CONVENTIONS.md`
- Windsurf: generates `.windsurfrules`

### Planned: Scenario Examples
- 3-4 fully worked examples in `examples/` folder showing populated `.fireteam/` directories
- MVP build, marketing campaign, API product, full-stack app
- Each with filled MISSION.md, tasks with goal chains, handoffs, daily logs

### Planned: Agent Gallery in HQ
- Browse and assign pre-built operator personalities from the launch screen
- Select from personality library when configuring the roster
- Preview agent voice, deliverables, and metrics before deploying

### Not Adopting
- 61-agent library approach (we stay focused: 2-6 operators per mission)
- Complex multi-tool install scripts (we keep it to single config file generation)
- Standalone personality files without coordination (our strength is the protocol layer)

---

## [1.1.0] — 2026-03-09

### Added: Live Command Center (`hq.py`)
- Unified HTTP server + Pro Mode daemon + live dashboard in one file
- Serves web UI at `http://localhost:4040`
- Real-time objectives board with status grouping, progress bars, dependency tags
- Controls bar: START/STOP daemon, active/completed/failed counters
- Three side-panel tabs: Comms (live events), Roster (operator status), Logs (agent output)
- FIRE button on each backlog task for manual agent deployment
- Auto-polls every 3 seconds for live state updates

### Added: PRD Launch Screen
- Full-screen launch UI when no mission exists
- Paste PRD textarea with LOAD TEMPLATE button
- Model selector (Opus/Sonnet)
- Auto-fire checkbox
- LAUNCH MISSION button fires team-lead bootstrap
- Bootstrap overlay with spinner and live event stream
- Auto-transitions to dashboard when bootstrap completes
- Three-state UI: Launch Screen → Bootstrap Overlay → Dashboard

### Added: `/api/launch` endpoint
- POST with PRD text, model choice, auto-fire flag
- Saves PRD to `.fireteam/PRD.md`
- Extracts bootstrap prompt from `START_MISSION.md`
- Assembles full prompt (start mission + PRD + working directory)
- Spawns `claude -p` with team-lead's configured model
- 60-minute timeout for bootstrap operations
- Logs to `.fireteam/logs/BOOTSTRAP_*.log`

### Changed: `fireteam.sh` CLI
- Added `hq` command (launches live command center)
- `pro` is now alias for `hq`
- `dashboard` generates static HTML via `hq.py --generate`
- Removed standalone `pro.py` and `dashboard.py` — unified in `hq.py`

---

## [1.0.0] — 2026-03-08 — Fireteam Rebrand

### Added: Brand Identity
- Renamed from MACP to Fireteam
- Military/tactical naming: operators, callsigns, objectives, field logs, intel
- `.agents/` → `.fireteam/`, `PROJECT.md` → `MISSION.md`, `AGENTS.md` → `ROSTER.md`, `MEMORY.md` → `INTEL.md`
- Tasks renamed to objectives (`OBJ-XXX`)
- Product Lead → Team Lead

### Added: Goal Chains (from Paperclip)
- Every task template includes `## Goal Chain`: Mission → Goal → Task → Why It Matters
- Agents always see the "why", not just the "what"
- Team Lead fills goal chains during bootstrap

### Added: Atomic Checkout (from Paperclip)
- Task template has `checked_out_by` and `checkout_time` fields
- Convention: if another agent's ID is there, don't touch it
- Prevents double-work on the same task

### Added: HEARTBEAT.md (from Paperclip)
- New template: structured checklist operators run every session start
- Six sections: Mission Check, Situation Assessment, Comms Check, Prioritize, Execute, Debrief
- Replaces the previous prose-based startup sequence
- `fireteam.sh heartbeat "callsign"` CLI command

### Added: Mandatory SOUL Files (from Paperclip)
- SOUL_TEMPLATE upgraded from optional to required
- START_MISSION prompt requires Team Lead to create SOUL for every operator
- `fireteam.sh soul "callsign"` CLI command

### Added: Team Presets
- `.fireteam/presets/TEAMS.md` with four configurations: Solo, Duo, Squad, Platoon
- Drop-in roster blocks ready to copy

### Added: Pro Mode Daemon (`pro.py`)
- Python daemon polling `.fireteam/` for board changes
- Dependency graph builder — smart parallel execution
- Prompt assembly: soul + mission + intel + task + handoffs
- Spawns `claude -p` subprocesses
- Atomic checkout on task files before spawning
- `.fireteam/pro.yml` config maps callsigns to CLI commands and models
- Commands: `--once`, `--dry-run`, `--interval`, `--max-parallel`
- Logging to `.fireteam/logs/`

### Added: Project Documentation
- `HISTORY.md` — full design evolution (15 sections, 449 lines)
- `CLAUDE.md` — agent maintenance instructions

---

## [0.5.0] — 2026-03-08 — Crash Recovery

### Added: Progressive Checkpointing
- Agents update checkpoints during work, not just at session end
- Cadence: after meaningful units, before risky operations, every 15-20 min
- Checkpoint template upgraded with `type: progressive|session-end|recovery`

### Added: RESUME_AGENT.md
- Dedicated recovery prompt with 5 phases: read context, investigate state, assess, write recovery checkpoint, resume
- Separate from onboarding prompt — handles crashes, context limits, interrupted sessions

### Added: `recover` command in CLI
- Quick diagnostic: checkpoint age, in-progress tasks, daily log status, git uncommitted changes
- Run before pasting resume prompt to understand the state

### Changed: Three formalized entry points
- Start Mission (new project)
- Onboard Agent (joining active project)
- Resume Agent (recovering from interruption)

---

## [0.4.0] — 2026-03-08 — PRD Entry Point

### Added: PRD_TEMPLATE.md
- Minimum viable requirements document to start any project
- Sections: project name, problem, solution, features (prioritized), tech preferences, constraints, success criteria

### Added: START_PROJECT.md
- 10-step bootstrap prompt for the product lead
- Whoever receives this prompt becomes the Product Lead
- Generates: PROJECT.md, AGENTS.md, BOARD.md, MEMORY.md, all task files

### Added: agent-helper.sh CLI
- Portable bash script (macOS + Linux compatible)
- Commands: task, handoff, thread, decision, log, checkpoint, status
- Auto-incrementing IDs, portable `sedi()` wrapper

---

## [0.3.0] — 2026-03-08 — Example Validation

### Added: PriorityPing example project
- 3 agents, 5 tasks, 1 decision record, 1 thread, 1 handoff, daily log, checkpoints
- Validated: startup sequence is ~4k tokens (98% context window free)
- Validated: handoffs prevent re-work, daily logs create scannable history

---

## [0.2.0] — 2026-03-08 — OpenClaw Memory System

### Added: Two-tier memory (from OpenClaw)
- `MEMORY.md` — curated durable facts
- `memory/YYYY-MM-DD.md` — daily append-only logs
- Read today + yesterday at session start

### Added: Session checkpoints (from OpenClaw)
- CHECKPOINT_TEMPLATE.md with state capture
- Written before session end, read on resume

### Added: SOUL_TEMPLATE.md (from OpenClaw)
- Per-agent identity file defining role, capabilities, boundaries

---

## [0.1.0] — 2026-03-08 — Initial Protocol

### Added: Core protocol (MACP)
- `.agents/` folder structure with 5 communication layers
- PROJECT.md, CONVENTIONS.md, AGENTS.md, BOARD.md
- Templates: task, handoff, thread, decision
- File permissions system (who can modify what)
- Handoff protocol (the key coordination mechanism)
- Markdown-only, zero dependencies, agent-agnostic

---

## Versioning

This project uses date-based development with semantic versioning for releases:
- **Major (X.0.0):** Breaking changes to templates, file naming, or protocol structure
- **Minor (0.X.0):** New features, templates, or commands (backward compatible)
- **Patch (0.0.X):** Bug fixes, documentation, cosmetic changes
