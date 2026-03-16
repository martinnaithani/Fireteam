# 🔥 Fireteam

**Stop babysitting your AI agents.** Fireteam lets 2-6 AI agents coordinate on the same codebase through shared markdown files — mission, tasks, handoffs, crash recovery. No server. No database.

Works with Claude Code, Cursor, Aider, Windsurf — anything that reads files.

<!-- TODO: Replace with actual demo GIF -->
<!-- ![Fireteam Demo](assets/demo.gif) -->

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Claude Skill](https://img.shields.io/badge/Claude_Skill-Install-blue.svg)](#install)

---

## Install

**Download [`fireteam-skill.zip`](skill/) and upload to Claude:**

**Claude.ai:** Settings → Capabilities → Skills → Upload `fireteam-skill.zip`

**Claude Code:** Drop the `skill/fireteam/` folder into your skills directory

**Then just say:**

```
"Set up a fireteam for this project"
```

That's it. Claude knows the protocol. It detects your project state, sets everything up, and gives you onboarding prompts for each agent.

---

## What Happens When You Say "Set Up a Fireteam"

Claude automatically:

1. **Assesses your project** — empty directory? existing codebase? It adapts.
   - New project + PRD → plans forward from your requirements
   - Existing code → runs recon (scans stack, structure, patterns), then plans from reality
   - `.fireteam/` already exists → rejoins and picks up work

2. **Creates `.fireteam/`** in your project root:
   ```
   .fireteam/
   ├── MISSION.md          ← why we're here
   ├── BOARD.md            ← who's working on what
   ├── ROSTER.md           ← the squad and their roles
   ├── INTEL.md            ← stack, APIs, file paths, key facts
   ├── CONVENTIONS.md      ← rules every agent follows
   ├── tasks/OBJ-001.md    ← objectives with goal chains
   ├── handoffs/           ← context transfers between agents
   ├── checkpoints/        ← per-agent state + identity
   └── memory/             ← daily field logs
   ```

3. **Gives you onboarding prompts** — paste into new agent sessions. Each agent reads `.fireteam/`, finds its tasks, and starts working.

---

## How Agents Coordinate

```
Agent 1 (Team Lead) sets up the mission, tasks, roster
    ↓
Agent 2 (Backend) reads mission, claims OBJ-001, builds the API
    ↓
Agent 2 writes a handoff: endpoints, schemas, curl examples
    ↓
Agent 3 (Frontend) reads the handoff, integrates against the real API
    ↓
Each agent checkpoints every 15 min → crash-resistant
```

**The key insight:** Every AI agent can read and write files. Fireteam uses the file system as the coordination layer.

---

## Core Protocol

**Goal Chains** — Every task carries: Mission → Goal → Task → Why It Matters. Agents always see the "why."

**Atomic Checkout** — Tasks have a `checked_out_by` field. If another agent claimed it, you don't touch it.

**Progressive Checkpoints** — State saved every 15 min. Crashes lose minutes, not hours.

**Handoffs** — When Agent A finishes work Agent B needs: what was built, file locations, API contracts, next steps. A good handoff prevents re-work.

**Heartbeat** — Every session starts with: mission → intel → board → handoffs → "what's my highest priority?"

**Crash Recovery** — Agent dies? Say "resume my fireteam agent" — it investigates state, verifies what's done, then resumes.

---

## The Skill Handles All Entry Points

| Situation | What to say |
|-----------|------------|
| **New project** | "Set up a fireteam for this PRD" (paste your requirements) |
| **Existing codebase** | "Add fireteam to this project" (it scans your code first) |
| **New feature on existing project** | "Set up a fireteam for this feature" (paste spec + it reads code) |
| **Rejoin active fireteam** | "Continue my fireteam" (reads .fireteam/, picks up work) |
| **After a crash** | "Resume my fireteam agent" (investigates, recovers, resumes) |
| **Create a handoff** | "Write a handoff from backend to frontend" |
| **Save state** | "Write a checkpoint" |

---

## For Power Users: CLI + Live HQ

The repo includes a CLI and a live command center for autonomous agent orchestration. You don't need these to use Fireteam — the Skill handles everything — but they're here if you want them.

### CLI

```bash
./fireteam.sh task "Build auth API"         # Create objective
./fireteam.sh handoff "backend" "frontend"  # Create handoff
./fireteam.sh checkpoint "backend"          # Save agent state
./fireteam.sh recover "backend"             # Diagnose after crash
./fireteam.sh status                        # Terminal status
```

### Live Command Center

```bash
./fireteam.sh hq
# Opens http://localhost:4040
```

Web dashboard with auto-fire daemon — watches the board, builds a dependency graph, spawns Claude Code agents for ready tasks in parallel. Paste a PRD in the launch screen, watch agents deploy live.

```bash
./fireteam.sh hq                  # Auto-fire mode
./fireteam.sh hq --no-auto       # Manual — click FIRE on each task
```

Configure in `.fireteam/pro.yml`:

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

## Manual Setup (Without the Skill)

If you prefer manual control over the Skill:

```bash
# Clone and copy .fireteam/ into your project
git clone https://github.com/martinnaithani/fireteam.git
cp -r fireteam/.fireteam/ /path/to/your-project/.fireteam/

# Fill in the PRD
cp fireteam/PRD_TEMPLATE.md /path/to/your-project/PRD.md

# Paste START_MISSION.md prompt into your first AI agent + attach PRD
# That agent becomes Team Lead and sets up everything

# For subsequent agents: paste the onboarding prompt Team Lead generates
# For crash recovery: paste RESUME_AGENT.md prompt
```

---

## Tool Integrations

Fireteam works with any AI coding tool. The `integrate` command generates tool-specific config files that teach your tool the protocol:

```bash
./fireteam.sh integrate claude-code   # CLAUDE.md + hooks + .claude/settings.json
./fireteam.sh integrate cursor        # .cursor/rules/fireteam.mdc
./fireteam.sh integrate aider         # CONVENTIONS.md
./fireteam.sh integrate windsurf      # .windsurfrules
```

**Claude Code integration** includes lifecycle hooks that run automatically:
- **Session start** → prints a mission briefing (objectives, handoffs, open threads)
- **Session end** → reminds agent to checkpoint and update the field log

No manual heartbeat needed — the hooks handle situational awareness.

---

## Using with Everything Claude Code (ECC)

[Everything Claude Code](https://github.com/affaan-m/everything-claude-code) optimizes individual Claude Code sessions — skills, hooks, rules, agents. Fireteam coordinates BETWEEN sessions. They solve different problems and work well together.

**ECC makes each agent better.** Fireteam makes agents work together.

Use ECC in each terminal for single-session performance. Use `.fireteam/` for cross-session coordination. Run `./fireteam.sh integrate claude-code` to generate the CLAUDE.md and hooks that bridge them.

---

## Design Principles

- **Files are the protocol.** If it reads markdown, it's compatible. No server, no database.
- **Mission over tasks.** Everything traces to the mission. Agents know the *why*.
- **Crash-resistant.** Progressive checkpoints, recovery protocol. Sessions die — work survives.
- **Small teams.** 2-6 agents. If you need 20+, use [Paperclip](https://github.com/paperclipai/paperclip).

---

## Inspired By

- [Paperclip](https://github.com/paperclipai/paperclip) — goal ancestry, atomic checkout, heartbeats
- [OpenClaw](https://github.com/openclaw/openclaw) — two-tier memory, session management
- [Everything Claude Code](https://github.com/affaan-m/everything-claude-code) — hook lifecycle patterns, token budget awareness

## License

MIT © 2026 [Martin Naithani](https://martinnaithani.com) / [Innovation Theory](https://innovationtheory.com)
