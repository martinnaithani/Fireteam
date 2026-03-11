# 🔥 Fireteam

**Your Seal Team 6 for building products.** A file-system protocol that turns a squad of AI agents into a coordinated strike team.

No server. No database. No dependencies. Just markdown files that agents read and write.

Works with Claude Code, Cursor, Aider, Windsurf, Codex — anything that can read a file.

---

## The Problem

You have AI agents that can build. But they can't coordinate. You open 5 terminals, each agent works in isolation, they make conflicting decisions, duplicate work, and forget everything between sessions. You're the bottleneck — manually copying context between tools.

## The Solution

A `.fireteam/` folder in your project root. Structured markdown files that give your agents shared memory, task assignments, handoffs, and a chain of command. Every agent reads the mission at session start. Every agent knows *what* to do, *who else* is doing what, and *why* it matters.

**If Paperclip is a company, Fireteam is a platoon.** Light. Fast. No infrastructure. Drop it in any project and go.

```
your-project/
├── .fireteam/             ← shared brain
│   ├── MISSION.md         ← why we're here (every agent reads first)
│   ├── CONVENTIONS.md     ← rules of engagement
│   ├── ROSTER.md          ← who's on the team
│   ├── BOARD.md           ← mission objectives status
│   ├── INTEL.md           ← curated long-term knowledge
│   ├── tasks/             ← mission objectives with goal chains
│   ├── handoffs/          ← structured context transfer
│   ├── comms/             ← async discussion threads
│   ├── decisions/         ← architecture decision records
│   ├── memory/            ← daily field logs
│   ├── checkpoints/       ← per-agent session state
│   └── templates/         ← templates for everything
├── fireteam.sh            ← CLI tool
├── hq.py                 ← Live command center (server + daemon + UI)
└── dashboard.py           ← (generated) static dashboard
```

## Three Entry Points

| Situation | File |
|-----------|------|
| **Start a new project** — first agent becomes team lead | [`START_MISSION.md`](START_MISSION.md) + [`PRD_TEMPLATE.md`](PRD_TEMPLATE.md) |
| **Join an active project** — new agent onboarding | Onboarding prompt at bottom of `START_MISSION.md` |
| **Resume after crash/interruption** — recovery protocol | [`RESUME_AGENT.md`](RESUME_AGENT.md) |

## How It Works

### 1. Write a PRD
Fill in [`PRD_TEMPLATE.md`](PRD_TEMPLATE.md). Minimum viable requirements: problem, solution, features, constraints.

### 2. Start the Mission
Paste the prompt from [`START_MISSION.md`](START_MISSION.md) into your first AI agent. Attach the PRD. That agent becomes the **Team Lead** — it reads your PRD and sets up the entire `.fireteam/` folder: mission brief, task breakdown, roster, and intel.

### 3. Deploy the Squad
The team lead generates onboarding prompts for each role. Open a new session in any tool, paste the prompt. The agent reads `.fireteam/`, sees the mission, finds its assigned objectives, and starts executing.

### 4. Agents Coordinate via Files
Every task carries a **goal chain** — a direct line from the task back to the mission. Agents always know the *why*, not just the *what*. Handoffs transfer context between agents. Checkpoints save state progressively so crashes don't lose work.

### 5. Resume After Interruptions
Agents crash. Context windows fill up. Use [`RESUME_AGENT.md`](RESUME_AGENT.md) — the agent investigates state, verifies what's actually done, writes a recovery checkpoint, then resumes.

## What's Different About Fireteam

**Borrowed from Paperclip, adapted for zero infrastructure:**

| Concept | How It Works |
|---------|-------------|
| **Goal Chains** | Every task carries the full chain: Mission → Goal → Task. Agents always see the *why*. |
| **Atomic Checkout** | Tasks have a `checked_out_by` field. If another agent has it, don't touch it. No double-work. |
| **Heartbeat Protocol** | Each agent gets a `HEARTBEAT.md` — a repeatable checklist they run every session: check board, check comms, assess blockers, prioritize. |
| **Mandatory SOUL** | Every agent gets an identity file defining who they are, what they can do, and their boundaries. Not optional. |
| **Progressive Checkpoints** | Agents save state every 15-20 min during work, not just at session end. Crashes lose minutes, not hours. |
| **Two-Tier Memory** | `INTEL.md` for curated durable facts + `memory/YYYY-MM-DD.md` for daily field logs. |
| **Team Presets** | Pre-built squad configurations: Solo, Duo, Squad (4), Platoon (6+). |

## CLI

```bash
./fireteam.sh task "Build auth API"              # Create objective
./fireteam.sh handoff "backend" "frontend"       # Create handoff
./fireteam.sh thread "API contract question"     # Start discussion
./fireteam.sh decision "Database choice"         # Record decision
./fireteam.sh log "backend-lead"                 # Add to field log
./fireteam.sh checkpoint "backend-lead"          # Save agent state
./fireteam.sh heartbeat "backend-lead"           # Run heartbeat check
./fireteam.sh recover "backend-lead"             # Diagnose after crash
./fireteam.sh dashboard                          # Generate visual HQ
./fireteam.sh status                             # Terminal status
```

## Pro Mode — Live Command Center

One command launches everything:

```bash
./fireteam.sh hq
```

Open `http://localhost:4040`:

**If no mission exists** — you see the Launch Screen:
1. Paste your PRD into the text area (or click LOAD TEMPLATE for the blank PRD structure)
2. Pick a model (Opus for strategic planning, Sonnet for speed)
3. Check "Auto-fire agents after bootstrap" if you want full autonomy
4. Hit **LAUNCH MISSION**

The team lead agent reads your PRD, creates the mission brief, builds the roster, writes tasks with goal chains, sets up the board — everything. You watch the progress live in a bootstrap overlay with streaming events. Takes 2-5 minutes.

**Once bootstrapped** — the dashboard takes over:

- **Objectives Board** — all tasks grouped by status, with live running indicators, dependency tags, progress bars, and a FIRE button on each backlog task
- **Controls Bar** — START/STOP daemon, active count, completed, failed, poll interval
- **Comms Tab** — live event stream (agent deployed, completed, failed, blocked)
- **Roster Tab** — all operators with live status dots (green = running, red = idle), current model, and what they're working on
- **Logs Tab** — click any log file to view the full agent output inline

```bash
./fireteam.sh hq                 # Launch HQ (daemon + UI at localhost:4040)
./fireteam.sh hq --no-auto       # UI only — fire agents manually via FIRE buttons
./fireteam.sh hq --port 5050     # Custom port
./fireteam.sh hq --interval 15   # Poll every 15s
./fireteam.sh dashboard          # Generate static dashboard.html (no server)
```

**How auto-fire works:**

```
Daemon polls .fireteam/ every 30s
  ├─ Parses all OBJ-*.md + builds dependency graph
  ├─ Finds READY tasks (backlog + all deps done + not running)
  ├─ For each: assembles prompt (soul + mission + intel + task + handoffs)
  ├─ Spawns `claude -p "<prompt>"` in project directory
  ├─ Independent tasks → parallel (up to 4)
  ├─ Dependent tasks → wait for predecessors
  └─ Loops until stopped
```

**Or fire manually:** Turn off auto-fire (`--no-auto`), then click the FIRE button on any task in the UI. Full control, zero babysitting.

**The full flow (zero to running agents):**

```
1. ./fireteam.sh hq                    ← starts server at localhost:4040
2. Open browser → see Launch Screen
3. Paste PRD → click LAUNCH MISSION
4. Team Lead bootstraps (2-5 min)      ← watch live progress
5. Dashboard appears with tasks
6. Agents auto-fire based on board     ← or click FIRE manually
7. Watch agents deploy, complete, handoff
8. Ctrl+C when done
```

**Configure operators** in `.fireteam/pro.yml`:

```yaml
team-lead:
  cli: claude
  model: opus

backend:
  cli: claude
  model: sonnet

frontend:
  cli: claude
  model: sonnet
```

**Requirements:** Python 3.6+, `claude` CLI on PATH.

## Team Presets

Drop-in squad configurations in `.fireteam/presets/`:

| Preset | Agents | Best For |
|--------|--------|----------|
| **Solo** | team-lead (you + 1 dev agent) | Quick builds, prototypes |
| **Duo** | team-lead + full-stack | Landing pages, MVPs |
| **Squad** | team-lead + backend + frontend + design | Standard web apps |
| **Platoon** | team-lead + eng-lead + backend + frontend + devops + QA | Complex systems |

## The Heartbeat

Every session, agents run their heartbeat — a structured self-check:

```
1. Read MISSION.md     → remember why we're here
2. Read INTEL.md       → recall key facts
3. Run HEARTBEAT.md    → structured checklist:
   □ Check BOARD.md for my objectives
   □ Check comms/ for open threads involving me
   □ Check handoffs/ for context addressed to me
   □ Check my checkpoint — am I resuming?
   □ Assess: what's the highest-priority thing I should do right now?
4. Execute              → pick up the work
5. Checkpoint          → save state progressively
```

## The Goal Chain

Every task answers "why does this matter?"

```
MISSION: Build PriorityPing into the #1 spam-resistant communication protocol
  └─ GOAL: Launch waitlist to capture 1,000 early adopters
      └─ TASK-003: Build signup form with email + wallet fields
          └─ WHY: This form is the primary conversion point for early adopters
```

The full chain is embedded in every task file. An agent never has to wonder what they're building toward.

## Design Principles

- **Files are the protocol.** No server, no database, no runtime. If an agent can read markdown, it's compatible.
- **Mission over tasks.** Everything traces back to the mission. Agents don't just do work — they understand *why*.
- **Small teams, big output.** Fireteam is built for 2-6 agents. If you need 20+, look at [Paperclip](https://github.com/paperclipai/paperclip).
- **Crash-resistant by default.** Progressive checkpoints, recovery protocol, dirty exit handling. Sessions die — work survives.
- **Zero config.** Copy the folder, paste the prompt, start building. Under 60 seconds to first agent.

## Inspired By

- [Paperclip](https://github.com/paperclipai/paperclip) — goal ancestry, atomic checkout, heartbeats, SOUL.md
- [OpenClaw](https://github.com/openclaw/openclaw) — two-tier memory, workspace isolation, session management
- [Star Office UI](https://github.com/ringhyacinth/Star-Office-UI) — pixel art dashboard visualization

## License

MIT © 2026 Martin Naithani / Innovation Theory
