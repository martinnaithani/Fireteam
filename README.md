# 🔥 Fireteam

**Stop babysitting your AI agents.** Drop a `.fireteam/` folder into your project and 2-6 agents coordinate through files — shared mission, task assignments, handoffs, crash recovery. No server, no database. Just markdown.

Works with Claude Code, Cursor, Aider, Windsurf — anything that reads files.

<!-- TODO: Replace with actual demo GIF -->
<!-- ![Fireteam Demo](assets/demo.gif) -->
<!-- ↑ 30-second GIF: paste PRD → team lead bootstraps → agents coordinate → handoff works -->

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Claude Skill](https://img.shields.io/badge/Claude-Skill-blue.svg)](#install-the-claude-skill)

---

## Quickstart (60 seconds)

```bash
# 1. Clone
git clone https://github.com/martinnaithani/fireteam.git
cd fireteam

# 2. Copy .fireteam/ into your project
cp -r .fireteam/ /path/to/your-project/.fireteam/

# 3. Fill in the PRD template
cp PRD_TEMPLATE.md /path/to/your-project/PRD.md
# Edit PRD.md with your project details

# 4. Paste the prompt from START_MISSION.md into your first AI agent
# Attach your PRD. That agent becomes the Team Lead.
# It sets up everything: mission, tasks, roster, intel.

# 5. Team Lead gives you onboarding prompts for each operator.
# Paste into new sessions. Agents read .fireteam/ and start working.
```

**Or install the Claude Skill** — Claude learns the protocol natively. Just say "set up a fireteam for this project" and it handles setup automatically. See [Install the Claude Skill](#install-the-claude-skill).

---

## How It Works

```
You write a PRD
    ↓
Paste START_MISSION.md into Agent 1 → becomes Team Lead
    ↓
Team Lead reads PRD, creates:
  • MISSION.md (the "why")
  • Tasks with goal chains (the "what" + "why it matters")  
  • Roster with SOUL files (who does what)
  • INTEL.md (key facts every agent needs)
    ↓
You open Agent 2, Agent 3... paste onboarding prompt
    ↓
Each agent reads .fireteam/, claims a task, does the work
    ↓
When done → writes handoff for the next agent
    ↓
Next agent reads handoff → picks up seamlessly
```

**The key insight:** Every AI agent can read and write files. That's the universal capability. Fireteam uses the file system as the coordination layer.

---

## What's Inside `.fireteam/`

```
.fireteam/
├── MISSION.md          ← why we're here (agents read first)
├── BOARD.md            ← who's working on what
├── ROSTER.md           ← the squad and their roles
├── INTEL.md            ← curated facts: stack, APIs, file paths
├── CONVENTIONS.md      ← rules every agent follows
├── tasks/OBJ-001.md    ← objectives with goal chains
├── handoffs/HO-001.md  ← context transfers between agents
├── comms/              ← async discussions
├── decisions/          ← architecture decision records
├── memory/             ← daily field logs (append-only)
└── checkpoints/        ← per-agent state + identity files
```

---

## Core Concepts

**Goal Chains** — Every task carries: Mission → Goal → Task → Why It Matters. Agents always see the "why."

**Atomic Checkout** — Tasks have a `checked_out_by` field. If another agent claimed it, you don't touch it. Zero double-work.

**Progressive Checkpoints** — Agents save state every 15 min during work, not just at session end. Crashes lose minutes, not hours.

**Handoff Protocol** — When Agent A finishes work Agent B needs: what was built, file locations, API contracts, what to do next. A good handoff prevents re-work.

**Heartbeat** — Every session starts with a structured read: mission → intel → board → handoffs → comms → "what's my highest priority?"

**Crash Recovery** — Agent dies? Use `RESUME_AGENT.md`. It investigates state, verifies what's actually done, writes a recovery checkpoint, then resumes.

---

## Install the Claude Skill

The Skill teaches Claude the Fireteam protocol natively. No prompt pasting — just say "set up a fireteam" and it works.

```bash
# The skill is in the skill/ directory
cd skill/
zip -r fireteam.zip fireteam/
# Upload fireteam.zip to Claude.ai → Settings → Skills
# Or drop the fireteam/ folder into your Claude Code skills directory
```

**What the Skill does:**
- Detects project state automatically (greenfield vs existing code vs existing .fireteam/)
- Greenfield: bootstraps from your PRD
- Existing codebase: runs recon (scans structure, stack, patterns), then creates tasks that reference real files
- Handles recovery and onboarding without manual prompt pasting

---

## CLI

```bash
./fireteam.sh task "Build auth API"         # Create objective
./fireteam.sh handoff "backend" "frontend"  # Create handoff
./fireteam.sh checkpoint "backend"          # Save agent state
./fireteam.sh recover "backend"             # Diagnose after crash
./fireteam.sh status                        # Terminal status
./fireteam.sh hq                            # Launch live command center
```

---

## Pro Mode: Live Command Center

```bash
./fireteam.sh hq
# Opens http://localhost:4040
```

A live web dashboard that watches the board and auto-fires Claude Code agents:

- **Objectives Board** — tasks grouped by status, FIRE button on each
- **Auto-fire daemon** — builds dependency graph, spawns agents for ready tasks in parallel
- **Live comms** — event stream as agents deploy, complete, fail
- **PRD Launch Screen** — paste a PRD, click LAUNCH MISSION, watch the team lead bootstrap everything

```bash
./fireteam.sh hq                  # Auto-fire mode
./fireteam.sh hq --no-auto       # Manual — click FIRE on each task
./fireteam.sh hq --port 5050     # Custom port
```

Configure operators in `.fireteam/pro.yml`:

```yaml
team-lead:
  cli: claude
  model: opus

backend:
  cli: claude
  model: sonnet
```

Requires: Python 3.6+, `claude` CLI on PATH.

---

## Three Entry Points

| Situation | What to do |
|-----------|-----------|
| **New project** | Fill in `PRD_TEMPLATE.md`, paste `START_MISSION.md` prompt into your first agent |
| **Existing codebase** | Install the Claude Skill, say "add fireteam to this project" — it runs recon and sets up from reality |
| **After a crash** | Paste `RESUME_AGENT.md` prompt — agent investigates state before resuming |

---

## Design Principles

- **Files are the protocol.** No server, no database. If it reads markdown, it's compatible.
- **Mission over tasks.** Everything traces to the mission. Agents know the *why*.
- **Crash-resistant.** Progressive checkpoints, recovery protocol. Sessions die — work survives.
- **Zero config.** Copy folder, paste prompt, go. Under 60 seconds.
- **Small teams.** 2-6 agents. If you need 20+, use [Paperclip](https://github.com/paperclipai/paperclip).

---

## Inspired By

- [Paperclip](https://github.com/paperclipai/paperclip) — goal ancestry, atomic checkout, heartbeats
- [OpenClaw](https://github.com/openclaw/openclaw) — two-tier memory, session management

---

## License

MIT © 2026 [Martin Naithani](https://martinnaithani.com) / [Innovation Theory](https://innovationtheory.com)
