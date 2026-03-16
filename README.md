# 🔥 Fireteam

![Fireteam Demo](assets/Fireteam_poster.gif)

**Your AI agent forgets everything when the session ends. Fireteam fixes that.**

A `.fireteam/` folder in your project gives your AI agent persistent memory — mission context, task state, progress checkpoints, and structured notes that survive session restarts, context limits, and crashes. No server. No database. Just markdown files.

Works with Claude Code, Codex, Antigravity, Cursor, Aider, Windsurf — anything that reads files.

<!-- TODO: Replace with actual demo GIF -->


[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Claude Skill](https://img.shields.io/badge/Claude_Skill-Install-blue.svg)](#install)

**New here?** Read the [Getting Started Guide](GETTING_STARTED.md) — zero jargon, step-by-step.

---

## Install

**Download [Download the Claude Skill](https://github.com/martinnaithani/fireteam/releases/latest/download/fireteam-skill.zip) and upload to Claude:**

**Claude.ai:** Settings → Capabilities → Skills → Upload `fireteam-skill.zip`

**Claude Code:** Drop the `skill/fireteam/` folder into your skills directory

**Then just say:**

```
"Set up a fireteam for this project"
```

That's it. Claude sets up the mission, breaks work into tasks, and starts executing. When the session ends or crashes, everything is saved. Next session picks up where you left off.

---

## Why Fireteam Exists

Every AI coding session starts from zero. The agent doesn't know what you built yesterday, what decisions were made, or what's left to do. You spend the first 10 minutes re-explaining context every single time.

Fireteam gives your agent a persistent project brain:

```
.fireteam/
├── MISSION.md        ← what we're building and why
├── BOARD.md          ← tasks and their status
├── INTEL.md          ← stack, file paths, API contracts, key decisions
├── tasks/OBJ-001.md  ← each task with goal chain and acceptance criteria
├── handoffs/         ← structured notes between tasks
├── checkpoints/      ← saved session state (every 15 min)
└── memory/           ← daily log of what happened
```

Your agent reads these at session start. It knows the mission, sees what's done, finds the next task, and continues. No re-explaining.

---

## How It Works

```
Session 1:
  Agent reads PRD → creates mission, tasks, board
  Works on OBJ-001 → builds API, checkpoints progress
  Finishes OBJ-001 → writes handoff notes, marks done
  Starts OBJ-002 → context window fills up, session ends
  Last checkpoint saved: OBJ-002 at 60%

Session 2 (new session, fresh context):
  Agent reads .fireteam/ → knows the mission, sees OBJ-001 is done
  Reads checkpoint → OBJ-002 at 60%, picks up from there
  Reads handoff from OBJ-001 → has the API contract
  Finishes OBJ-002 → writes handoff, starts OBJ-003
  ...continues until everything is done
```

**The key insight:** Your agent already reads and writes files. Fireteam uses the file system as the memory layer that persists across sessions.

---

## What the Skill Does

The Claude Skill teaches Claude the full protocol. It adapts to your project automatically:

| Situation | What to say |
|-----------|------------|
| **New project** | "Set up a fireteam for this PRD" (paste your requirements) |
| **Existing codebase** | "Add fireteam to this project" (it scans your code first) |
| **Continue working** | "Continue my fireteam" (reads .fireteam/, picks up work) |
| **After a crash** | "Resume my fireteam agent" (investigates state, then resumes) |
| **Save progress** | "Write a checkpoint" |
| **New feature on existing project** | "Set up a fireteam for this feature" (paste spec + it reads code) |

---

## Core Protocol

**Progressive Checkpoints** — State saved every 15 min during work. Sessions die — work survives. Crashes lose minutes, not hours.

**Handoffs** — Structured notes between tasks: what was built, file locations, API contracts, what comes next. When the agent starts the next task (even in a new session), it reads the handoff and has full context.

**Goal Chains** — Every task carries: Mission → Goal → Task → Why It Matters. The agent always knows *why* it's doing something, not just *what*.

**Heartbeat** — Every session starts with: mission → intel → board → checkpoints → handoffs → "what's my highest priority?" Consistent orientation in under 10 seconds.

**Crash Recovery** — Say "resume my fireteam agent." It checks files, git status, and checkpoints to verify what's actually done before continuing. Never assumes the previous session completed anything.

---

## Multiple Agents (When You Need Them)

For larger projects, Fireteam scales to 2-6 agents working in parallel across separate terminals. The same `.fireteam/` files coordinate between them:

```
Terminal 1 (Backend): reads mission, claims OBJ-001, builds API
    ↓ writes handoff with API contract
Terminal 2 (Frontend): reads handoff, claims OBJ-002, builds against real API
    ↓ both checkpoint independently
Terminal 3 (Deploy): waits for deps, claims OBJ-003, ships it
```

Each agent has a SOUL file (role identity), claims tasks with atomic checkout (no double-work), and communicates through handoffs and comms threads. The protocol handles coordination — you don't copy context between terminals.

**Most projects don't need this.** One agent cycling through tasks with checkpoints handles 80% of cases. Multi-agent is there when you genuinely need parallelism.

---

## Tool Integrations

```bash
./fireteam.sh integrate claude-code   # CLAUDE.md + auto-hooks + settings
./fireteam.sh integrate cursor        # .cursor/rules/fireteam.mdc
./fireteam.sh integrate aider         # CONVENTIONS.md
./fireteam.sh integrate windsurf      # .windsurfrules
```

**Claude Code integration** includes lifecycle hooks:
- **Session start** → automatic mission briefing (objectives, handoffs, status)
- **Session end** → checkpoint reminder

No manual heartbeat needed — the hooks handle it.

---

## CLI

```bash
./fireteam.sh task "Build auth API"         # Create objective
./fireteam.sh handoff "backend" "frontend"  # Create handoff
./fireteam.sh checkpoint "backend"          # Save agent state
./fireteam.sh recover "backend"             # Diagnose after crash
./fireteam.sh status                        # See what's going on
./fireteam.sh integrate claude-code         # Set up tool integration
```

---

## Dashboard

Open `dashboard.html` in Chrome/Edge. Click "Open .fireteam/ Folder." See the task board, roster, handoffs, and activity log — all read live from your `.fireteam/` files. No server needed.

---

## Manual Setup (Without the Skill)

```bash
git clone https://github.com/martinnaithani/fireteam.git
cp -r fireteam/.fireteam/ /path/to/your-project/.fireteam/
cp fireteam/PRD_TEMPLATE.md /path/to/your-project/PRD.md
# Edit PRD.md, paste START_MISSION.md prompt into your agent + attach PRD
```

---

## Design Principles

- **Files are the memory.** If it reads markdown, it works. No server, no database.
- **Sessions die, work survives.** Progressive checkpoints + handoffs = crash-resistant by default.
- **Mission over tasks.** Everything traces to the mission. The agent knows the *why*.
- **One agent or many.** Same protocol works for solo use and multi-agent coordination.
- **Zero config.** Say one sentence and it works. Under 60 seconds to first task.

---

## Using with Everything Claude Code (ECC)

[Everything Claude Code](https://github.com/affaan-m/everything-claude-code) optimizes individual Claude Code sessions. Fireteam adds persistent memory across sessions. They're complementary — use both.

---

## Inspired By

- [Paperclip](https://github.com/paperclipai/paperclip) — goal ancestry, atomic checkout, heartbeats
- [OpenClaw](https://github.com/openclaw/openclaw) — two-tier memory, session management
- [Everything Claude Code](https://github.com/affaan-m/everything-claude-code) — hook lifecycle patterns

## License

MIT © 2026 [Martin Naithani](https://martinnaithani.com) / [Innovation Theory](https://innovationtheory.com)
