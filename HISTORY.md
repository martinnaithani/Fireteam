# Fireteam — Project History & Design Decisions

> This document captures the complete evolution of Fireteam from initial concept to v1.0.
> It exists so any agent maintaining this repo understands WHY every decision was made,
> not just WHAT the code does. Read this before making significant changes.

---

## Table of Contents

1. [Genesis — The Problem](#1-genesis--the-problem)
2. [v0.1 — First Protocol Draft (MACP)](#2-v01--first-protocol-draft-macp)
3. [v0.2 — OpenClaw Inspiration](#3-v02--openclaw-inspiration)
4. [v0.3 — Example Project Validation](#4-v03--example-project-validation)
5. [v0.4 — GitHub-Ready with PRD Entry Point](#5-v04--github-ready-with-prd-entry-point)
6. [v0.5 — Crash Recovery & Progressive Checkpoints](#6-v05--crash-recovery--progressive-checkpoints)
7. [v0.6 — Visual Dashboard (Dream Lab)](#7-v06--visual-dashboard-dream-lab)
8. [v0.7 — Isometric Office View](#8-v07--isometric-office-view)
9. [v0.8 — Pixel Art Rewrite](#9-v08--pixel-art-rewrite)
10. [v0.9 — Contra / Strike Team Theme](#10-v09--contra--strike-team-theme)
11. [v1.0 — Paperclip Analysis & Fireteam Rebrand](#11-v10--paperclip-analysis--fireteam-rebrand)
12. [Architecture Principles](#12-architecture-principles)
13. [What We Explicitly Rejected](#13-what-we-explicitly-rejected)
14. [Maintenance Guidelines](#14-maintenance-guidelines)
15. [Future Roadmap](#15-future-roadmap)

---

## 1. Genesis — The Problem

**Date:** March 2026
**Creator:** Martin Naithani (Innov8or), founder of Innovation Theory — a UX/UI and product design agency focused on Web3, AI, blockchain, and mixed reality.

**The problem Martin articulated:**

When building products with AI agents, he used multiple tools — Claude Code for backend, Cursor for frontend, Aider for quick fixes. Each agent worked fine in isolation, but they had no way to coordinate. They made conflicting decisions, duplicated work, and lost all context between sessions. Martin was the bottleneck, manually copying context between tools.

**The core insight:** Every AI agent, regardless of platform, can read and write files. The file system is the only universal capability. Therefore, the coordination protocol should be file-system-native — no server, no database, no runtime dependencies.

**The vision:** A shared folder in the project root where agents read context at session start and write state before session end. Like a real office where people leave notes on each other's desks.

**Key design decision:** Martin wanted this to work as a **boilerplate** — something he could drop into any new project. Not a framework to install, not a service to run. Just copy a folder, paste a prompt, and go.

---

## 2. v0.1 — First Protocol Draft (MACP)

**Name:** Multi-Agent Communication Protocol (MACP)

**What was built:**

The initial protocol had five communication layers:
1. **Shared Context** (PROJECT.md, CONVENTIONS.md) — read by all agents
2. **Task Board** (BOARD.md) — kanban-style status tracking
3. **Task Files** (tasks/TASK-XXX.md) — individual work orders with frontmatter
4. **Handoffs** (handoffs/HO-XXX.md) — structured context transfer between agents
5. **Communication Threads** (comms/THREAD-XXX.md) — async Q&A

**Folder structure:**
```
.agents/
├── PROJECT.md
├── CONVENTIONS.md
├── AGENTS.md
├── BOARD.md
├── tasks/
├── handoffs/
├── comms/
├── decisions/
└── templates/
```

**Key decisions made:**
- **Markdown only.** No JSON, no YAML, no database. Human-readable, git-trackable, every agent can parse it.
- **Templates for everything.** Every file type has a template with commented instructions. Agents don't need to invent the format.
- **Explicit file permissions.** CONVENTIONS.md specifies which agent can modify which files, preventing conflicts.
- **The handoff is the key file.** We identified early that the most critical communication is when Agent A finishes work that Agent B needs. The handoff template forces agents to document: what was built, where files are, decisions made, API contracts, and exactly what the next agent should do.

**What was missing:** No memory between sessions. No crash recovery. No "why" behind tasks.

---

## 3. v0.2 — OpenClaw Inspiration

**Source:** https://docs.openclaw.ai/concepts/memory

**What we learned from OpenClaw:**

We studied OpenClaw's memory architecture and identified six patterns to adapt:

1. **Two-tier memory** — OpenClaw uses `memory/YYYY-MM-DD.md` (daily, append-only) and `MEMORY.md` (curated, durable). We had neither. Added both.

2. **Pre-compaction memory flush** — Before OpenClaw compacts a session, it triggers a silent turn to write durable state. We adapted this as the session-end checkpoint protocol.

3. **Context checkpoints** — OpenClaw's `.context-checkpoint.md` survives compaction. We created the CHECKPOINT_TEMPLATE with exact state: what's done, what's not, files modified, next steps.

4. **Post-compaction context loss** — A real GitHub issue (#17727) showed that agents lose awareness of AGENTS.md and SOUL.md after compaction. Our solution: checkpoints are separate from session history, and agents re-read identity files every session.

5. **Deterministic routing** — One developer found that LLM-decided routing caused silent failures. File-system assignment is deterministic by design — tasks are assigned explicitly, not guessed.

6. **Agent identity (SOUL.md)** — OpenClaw gives each agent a personality file. We created the SOUL_TEMPLATE.

**Structural additions:**
- `MEMORY.md` — curated long-term knowledge
- `memory/` — daily logs (append-only)
- `checkpoints/` — per-agent session state
- SOUL_TEMPLATE.md in templates

**Key insight adopted:** "Daily logs are noisy and ephemeral — they capture the stream of work. MEMORY.md is curated and durable — it captures what matters long-term." This two-tier approach means an agent at session start reads ~4k tokens of context and is fully oriented.

---

## 4. v0.3 — Example Project Validation

**Built a fully populated example** using PriorityPing (Martin's actual Web3 communication protocol project) as the test case.

**What the example contained:**
- 3 agents: product-lead, backend-lead, frontend-lead
- 5 tasks with a realistic dependency chain
- 1 architecture decision (DEC-001: src/ directory structure)
- 1 communication thread (API contract discussion, resolved)
- 1 handoff (HO-001: backend → frontend with full API contract)
- 1 daily log with 3 session entries
- 2 checkpoints (one mid-work, one complete)
- Populated MEMORY.md with API contracts, file locations, gotchas

**What this validated:**
- The startup sequence (~3,000 words / ~4k tokens) leaves 98% of a 200k context window free
- Handoffs genuinely prevent re-work — the frontend agent could start integrating immediately
- Daily logs create a timeline that any new agent can scan
- The protocol is learnable by any AI agent in one prompt

---

## 5. v0.4 — GitHub-Ready with PRD Entry Point

**Critical design change:** The project must start with a PRD, and whoever starts it becomes the Product Lead.

**Why this matters:** Previous versions required manually filling in PROJECT.md and AGENTS.md. This was friction. The new flow: fill in a simple PRD template, paste a prompt, and the AI agent does all the setup — creating tasks, assigning roles, seeding memory.

**Files added:**
- `PRD_TEMPLATE.md` — minimum viable requirements document
- `START_PROJECT.md` — the bootstrap prompt (10-step process for the product lead)
- Onboarding prompt for subsequent agents (at bottom of START_PROJECT.md)

**PRD design:** Intentionally minimal — project name, problem, solution, features with priority, tech preferences, constraints, success criteria. Nothing more. The product lead agent extracts everything it needs from this.

**Agent helper script:** `agent-helper.sh` — a portable bash CLI for creating tasks, handoffs, threads, daily logs, checkpoints. Uses `sedi()` wrapper for macOS/Linux compatibility. Auto-increments IDs.

---

## 6. v0.5 — Crash Recovery & Progressive Checkpoints

**The problem:** Checkpoints only work if the agent gets a clean exit. But agents crash (context limits, user closes terminal, network errors). What happens then?

**Three changes made:**

1. **Progressive checkpointing** — Agents no longer wait until session end. They update their checkpoint after every meaningful unit of work, before risky operations, and roughly every 15-20 minutes. If the session dies, the checkpoint is at most minutes stale, not hours.

2. **RESUME_AGENT.md** — A dedicated recovery prompt with 5 phases:
   - Phase 1: Read context files
   - Phase 2: Investigate state (check checkpoint, task files, git status, recent file changes)
   - Phase 3: Write recovery assessment (tell the human what you found)
   - Phase 4: Write recovery checkpoint (verified current state)
   - Phase 5: Only then resume work

3. **`recover` command in CLI** — `./agent-helper.sh recover "agent-id"` runs a quick diagnostic: checkpoint exists? how old? what's in-progress on the board? uncommitted git changes? Gives the human a status report before they even paste the resume prompt.

**Key principle established:** "Investigate first, act second." A recovering agent must NEVER assume the previous session completed anything — it verifies by checking actual files.

**Three entry points formalized:**
- Start Project (new project)
- Onboard Agent (joining active project)
- Resume Agent (recovering from interruption)

---

## 7. v0.6 — Visual Dashboard (Dream Lab)

**Inspiration:** Star Office UI (https://github.com/ringhyacinth/Star-Office-UI) — a pixel art office where AI agents appear as characters moving between zones based on their state.

**Approach:** A Python script (`dashboard.py`) reads every file in `.agents/` (agents, board, tasks, checkpoints, daily logs, handoffs, threads) and generates a self-contained HTML file with all data embedded as JSON. No server needed — just open the file in a browser.

**First version — "Dream Lab":**
- Dark space environment with canvas starfield
- Six glowing workstations: Coding, Review, Planning, Break Room, Blocked, Done
- CSS-drawn character figures with state-based animations (typing, thinking, wobbling, bobbing)
- Hover for speech bubble (checkpoint focus), click for detail panel
- Stats bar, task list with progress bars, activity feed from daily logs
- Ambient floating orbs, backdrop particle effects

**Technical decisions:**
- Pure HTML/CSS/JS — no build step, no dependencies, no CDN requirements
- Data embedded as JSON literal in the HTML (replaced via `__STATE_JSON__` placeholder)
- Character animations via CSS keyframes
- Canvas for starfield (performant particle system)

---

## 8. v0.7 — Isometric Office View

**Request:** Add a switchable isometric office layout alongside Dream Lab.

**Implementation:** Dual-view with toggle button in the header. Both views rendered from the same data.

**Isometric view details:**
- CSS 3D transforms: `rotateX(58deg) rotateZ(45deg)` for isometric perspective
- Furniture: desks with monitors (glow when occupied), whiteboard, couch, bug jar, trophy shelf
- Floor: perspective grid with zone markings
- Characters: same figures adapted for isometric space with `rotateZ(-45deg) rotateX(-58deg)` counter-rotation
- Labels float above zones in screen-space

**Both views share:** stats bar, task list, activity feed, and the agent detail slide panel.

---

## 9. v0.8 — Pixel Art Rewrite

**Direction change:** Full pixel art, front-view room with slight top-down angle, 16-bit SNES-era aesthetic.

**Technical approach:**
- Native 400×240 canvas rendered at true pixel resolution
- Scaled up with `image-rendering: pixelated` for crisp pixels
- ~8 FPS for authentic retro feel (setTimeout, not requestAnimationFrame)
- Every element drawn rect-by-rect — no images, no sprites, no external assets

**Room design:**
- Back wall with brick pattern, three windows showing dark sky
- Wood plank floor with grain lines
- Zones: Coding (3 desks with monitors), Planning (whiteboard + desk), Review (conference table), Break Room (couch + coffee machine), Blocked (warning sign + bug), Trophy Shelf (medals)
- Plants, lamp, bookshelves for atmosphere

**Character sprites:** 11×20 pixel figures with hair, skin-tone face, eyes that blink, colored body/arms/legs. State animations: typing arms, wobble, vertical bob, thinking.

**Interaction:** Hit-detection on canvas coordinates for click/hover. Tooltip on hover, detail panel on click.

---

## 10. v0.9 — Contra / Strike Team Theme

**Concept evolution:** "You're assembling your Seal Team 6, but for product building." Contra game heroes whose weapons are laptops and whiteboards.

**Complete visual redesign:**
- Military command center: riveted metal walls, hazard stripe baseboard, concrete floor
- Tactical zones: Deploy Zone (3 consoles), War Room (giant screen + war table), Intel Desk (data readouts), Barracks (bunk beds + locker), Minefield (sandbags + barbed wire), Decorated (medal display)
- Environment details: radar dish with sweeping line, radio equipment with blinking signal light, ammo crates labeled "CODE" and "BUGS", ceiling strip lights that flicker

**Contra-style characters (14×34 pixel soldiers):**
- Wide shoulders, thick arms (muscular Contra silhouette)
- Colored headband with fluttering tail — the signature Contra element
- Spiky hair above headband
- Tactical harness with cross-straps
- Belt with buckle, heavy boots
- Squad callsigns: ALPHA, BRAVO, CHARLIE, DELTA, ECHO, FOXTROT
- Each agent gets a unique headband color (red, blue, orange, purple, gold, teal)

**State animations:**
- Active: Arms pump typing, green sparks from hands, radio comms dots
- Blocked: Body sways, fist pumps in frustration, red anger symbols
- Review: Hand on chin, thought bubble floating above
- Idle: Gentle bob, relaxed stance
- Product lead gets a gold rank chevron

**UI chrome:**
- Military terminal green-on-black aesthetic
- CRT scanlines overlay + vignette
- "Press Start 2P" font throughout
- Renamed: Missions, Operatives, Deployed, Stuck, Field Log, Callsign, SITREP

---

## 11. v1.0 — Paperclip Analysis & Fireteam Rebrand

**Source studied:** https://github.com/paperclipai/paperclip — "Open-source orchestration for zero-human companies"

**What Paperclip is:** A full Node.js + Postgres + React server that orchestrates AI agents into a company with org charts, budgets, governance, goal alignment, heartbeats, and cost controls. Heavy infrastructure. Server-dependent.

**What we are:** File-system-native, zero infrastructure, zero dependencies. Different tier entirely.

**Six concepts borrowed and adapted:**

### 1. Goal Chains (Goal Ancestry)
Paperclip's strongest idea. Every task carries the full chain: Company Mission → Project Goals → Agent Goals → Tasks. The agent always sees the "why."

**Our adaptation:** Added `## Goal Chain` section to the task template with Mission → Goal → Task → Why It Matters. Team Lead fills this during bootstrap. An agent never has to wonder what they're building toward.

### 2. Atomic Task Checkout
Paperclip uses database-level atomic checkout — when an agent grabs a task, it's locked. No double-work.

**Our adaptation:** Added `checked_out_by` and `checkout_time` fields to the task template. Convention: if another agent's ID is there, don't touch it. Not database-atomic, but enforced by convention and AI agent compliance.

### 3. HEARTBEAT.md
Paperclip agents have a heartbeat — a scheduled self-check that runs periodically: check tasks, review work, delegate, report.

**Our adaptation:** New HEARTBEAT_TEMPLATE.md — a structured checklist operators run at every session start. Six sections: Mission Check, Situation Assessment, Comms Check, Prioritize, Execute, Debrief. Replaces the old prose-based startup sequence with a concrete checklist.

### 4. Mandatory SOUL.md
Paperclip's per-agent AGENTS.md references SOUL.md and TOOLS.md as essential files.

**Our adaptation:** SOUL_TEMPLATE.md upgraded from optional to mandatory. The START_MISSION prompt now requires the Team Lead to create a SOUL file for every operator during bootstrap. CLI has `fireteam soul "callsign"` command.

### 5. Goal-Aware Context
Paperclip injects goal context into every task. Agents don't discover it — it's handed to them.

**Our adaptation:** MISSION.md is goal-first (mission statement → goals → scope). Every task file embeds the goal chain inline. An agent reading their task file sees the full mission context without opening another file.

### 6. Team Presets (inspired by Clipmart)
Paperclip is building a marketplace for company templates.

**Our adaptation:** `.fireteam/presets/TEAMS.md` with four drop-in squad configurations: Solo (2 agents), Duo (2), Squad (4), Platoon (6+). Copy the roster block into ROSTER.md.

### Brand Evolution

**Why "Fireteam":**
A fire team is the military's smallest coordinated combat element — typically 4 people. That maps exactly to our use case: 2-6 AI agents coordinated on a mission. The name works as a CLI (`./fireteam.sh task "Build API"`), as a repo name, and as a concept.

**Full rename map:**

| Old (MACP) | New (Fireteam) |
|---|---|
| `.agents/` | `.fireteam/` |
| `PROJECT.md` | `MISSION.md` |
| `AGENTS.md` | `ROSTER.md` |
| `MEMORY.md` | `INTEL.md` |
| Tasks: `TASK-XXX` | Objectives: `OBJ-XXX` |
| Product Lead | Team Lead |
| Agents | Operators |
| Agent ID | Callsign |
| Daily logs | Field logs |
| `agent-helper.sh` | `fireteam.sh` |
| `START_PROJECT.md` | `START_MISSION.md` |

---

## v1.1 — Pro Mode (Autonomous Orchestration)

**The leap:** Going from passive protocol (human pastes prompts) to active orchestrator (Fireteam spawns agents automatically).

**Implementation:** `pro.py` — a Python daemon (stdlib only) that:

1. **Polls** `.fireteam/` every 30 seconds (configurable) using MD5 hash of board + task files to detect changes
2. **Parses** all OBJ-*.md task files and builds a dependency DAG
3. **Identifies ready tasks** — those in backlog with all dependencies satisfied and not already running
4. **Assembles prompts** — for each ready task, builds a full prompt combining the operator's soul file, MISSION.md, INTEL.md, today's field log, checkpoint (if resuming), relevant handoffs, and the task itself with execution instructions
5. **Spawns Claude Code** — fires `claude -p "<prompt>"` in the project directory as a subprocess
6. **Smart parallel execution** — independent tasks run simultaneously (up to configurable max), dependent tasks wait for predecessors
7. **Logs everything** — each agent session is logged to `.fireteam/logs/`
8. **Marks atomic checkout** — updates task file with `checked_out_by` and status before spawning

**Configuration via `.fireteam/pro.yml`:**
Simple key-value format (no YAML parser dependency) mapping callsigns to CLI commands and models. Default: all operators use `claude -p` with model from config.

**Key design decisions:**
- **Python stdlib only** — no watchdog, no asyncio, no third-party packages. Just subprocess, threading, and hashlib.
- **Polling over inotify** — filesystem watchers are platform-dependent. Polling at 30s is simple and portable.
- **Claude Code `-p` flag** — pipe mode, non-interactive. Agent receives the full prompt and runs to completion.
- **30-minute timeout** — prevents runaway agents. Logged as failure if exceeded.
- **Dry run mode** — `--dry-run` shows what would fire without executing. Essential for testing.
- **Graceful shutdown** — SIGINT/SIGTERM handler. Running agents finish in background.

**CLI integration:**
- `fireteam pro` — start daemon
- `fireteam pro --once` — single pass
- `fireteam pro --dry-run` — show plan
- `fireteam pro --interval 15` — custom poll
- `fireteam pro --max-parallel 2` — limit concurrency

---

## 12. Architecture Principles

These are the non-negotiable design constraints that should survive any future changes:

1. **Files are the protocol.** No server, no database, no runtime. If an agent can read markdown, it's compatible. This is the core differentiator.

2. **Zero dependencies.** The protocol works with a text editor. The CLI needs only bash. The dashboard needs only Python 3.6+ stdlib. Nothing to install.

3. **Mission over tasks.** Everything traces back to the mission through goal chains. Tasks without a "why" are not valid.

4. **Crash-resistant by default.** Progressive checkpoints, recovery protocol, dirty exit handling. Sessions die — work survives.

5. **Under 60 seconds to first agent.** Copy folder, paste prompt, go. No configuration, no setup wizard.

6. **Small teams.** Optimized for 2-6 agents. If you need 20+, use Paperclip. We're the platoon, not the company.

7. **Agent-agnostic.** No assumptions about which tool runs the agent. Works with Claude Code, Cursor, Aider, Windsurf, Copilot, or anything that reads files.

8. **Human-readable.** Everything is markdown. A human can read every file and understand the project state without any tool.

---

## 13. What We Explicitly Rejected

Decisions that came up during development and were deliberately NOT implemented:

1. **JSON over Markdown.** JSON is easier to parse but harder for agents and humans to read/write. Markdown is universally understood.

2. **SQLite for state.** Would solve atomic checkout properly but adds a dependency. Convention-based checkout is good enough for 2-6 agents.

3. **Watcher script / live updates.** A filesystem watcher that triggers actions when files change. Adds complexity and a running process. The pull model (agents read at session start) is simpler.

4. **Vector search over memory.** OpenClaw does this. For our scale (weeks of daily logs, not years), scanning markdown is fast enough.

5. **Server-based dashboard.** The dashboard is generated as a static HTML file. A live-updating server would be nicer but violates the zero-infrastructure principle.

6. **Agent-to-agent messaging.** Paperclip has agent-to-agent heartbeats. We use files (handoffs, threads). Asynchronous file-based communication is simpler and doesn't require agents to be running simultaneously.

7. **Budget tracking.** Paperclip tracks cost per agent per task. Useful but requires API-level integration with LLM providers. Out of scope for a file-based protocol.

8. **Automatic task assignment.** We use explicit assignment by the Team Lead. LLM-decided routing causes silent failures (validated by the OpenClaw community).

---

## 14. Maintenance Guidelines

For any agent maintaining this repository:

### What to change carefully:
- **Templates** — these are the interface agents interact with. Changes affect every project using Fireteam. Always maintain backward compatibility.
- **CONVENTIONS.md** — the rules all agents follow. Changes here change agent behavior across all projects.
- **CLI commands** — maintain the existing interface. Add new commands, don't rename old ones.

### What to change freely:
- **README.md** — improve copy, add examples, update badges.
- **Dashboard visual style** — the dashboard is cosmetic. Change the theme, add views.
- **Presets** — add new team presets for different project types.
- **Documentation** — more examples, better guides, translations.

### File naming conventions (do not change):
- Objectives: `OBJ-XXX.md` (zero-padded 3 digits)
- Handoffs: `HO-XXX.md`
- Threads: `THREAD-XXX.md`
- Decisions: `DEC-XXX.md`
- Field logs: `YYYY-MM-DD.md`
- Checkpoints: `[callsign].md`
- Souls: `[callsign]-soul.md`
- Heartbeats: `[callsign]-heartbeat.md`

### The three prompts (critical files):
- `START_MISSION.md` — bootstrap prompt. The 11-step process is load-bearing. Each step exists for a reason.
- `RESUME_AGENT.md` — recovery prompt. The 5-phase process prevents data loss. Don't simplify.
- Onboarding prompt (bottom of START_MISSION.md) — the minimal startup for subsequent agents.

### Testing changes:
1. Create a test project with the example PriorityPing PRD
2. Run the Start Mission prompt with an AI agent
3. Verify: MISSION.md populated, ROSTER.md has agents, BOARD.md has objectives, every task has a goal chain, every agent has a SOUL file
4. Run `./fireteam.sh status` to verify CLI works
5. Run `python3 dashboard.py` to verify dashboard generates

---

## 15. Future Roadmap

Ideas discussed but not yet implemented:

### High Priority
- **Walking animations in dashboard** — characters move between zones when state changes (requires state diffing between dashboard generations)
- **Handoff connection lines** — visual lines between agents who have active handoffs
- **`fireteam init`** — a setup command that copies `.fireteam/` into the current directory (like `git init`)

### Medium Priority
- **CLAUDE.md / .cursorrules auto-generation** — generate tool-specific config files that auto-load the Fireteam protocol so agents don't need manual prompt pasting
- **Multi-project support** — one human coordinating Fireteam across multiple repos
- **Retrospective template** — end-of-project review: what worked, what didn't, lessons for INTEL.md

### Low Priority / Exploratory
- **Budget tracking** — optional cost tracking per agent (would need LLM provider integration)
- **GitHub Actions integration** — auto-generate dashboard on push
- **Paperclip bridge** — export Fireteam state to Paperclip for teams that outgrow the file-based model
- **npm package** — `npx fireteam init` for zero-copy setup

---

## Acknowledgments

- **Paperclip** (https://github.com/paperclipai/paperclip) — goal ancestry, atomic checkout, heartbeats, SOUL.md, team templates
- **OpenClaw** (https://github.com/openclaw/openclaw) — two-tier memory, workspace isolation, pre-compaction flush, session management
- **Star Office UI** (https://github.com/ringhyacinth/Star-Office-UI) — pixel art dashboard concept, zone-based agent visualization

---

*This document was written on March 9, 2026, covering the development from initial concept through Fireteam v1.0.*
*Last updated: 2026-03-09*
