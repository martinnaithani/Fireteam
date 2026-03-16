# Getting Started with Fireteam

Every time you start a new AI coding session, the agent has amnesia. It doesn't know what you built yesterday, what decisions were made, or what's left to do. You spend the first 10 minutes re-explaining everything.

Fireteam gives your agent a memory that survives session restarts, context limits, and crashes. Here's how to set it up.

---

## The 2-Minute Setup (Claude Skill)

### Step 1: Install

Download `fireteam-skill.zip` from the [latest release](https://github.com/martinnaithani/fireteam/releases).

**Claude.ai:** Settings → Capabilities → Skills → Upload the zip.

**Claude Code:** Unzip and drop the `fireteam/` folder into your skills directory.

### Step 2: Start

Open Claude Code in your project. Say one of these:

**New project:**
```
Set up a fireteam for this project. Here's what I'm building: [describe it or paste a PRD]
```

**Existing codebase:**
```
Add fireteam to this project. I want to add auth and a dashboard.
```

### Step 3: Work

Claude creates a `.fireteam/` folder with your mission, tasks, and project intel. Then it starts working on the first task.

You don't need to do anything special. Just work normally. Claude checkpoints its progress every 15 minutes and writes structured notes between tasks.

### Step 4: Come Back Tomorrow

Next session, say:

```
Continue my fireteam
```

Claude reads `.fireteam/`, sees what's done, finds where it left off, and continues. No re-explaining. No wasted context.

### Step 5: When Things Break

Session crashed? Context window filled up? Say:

```
Resume my fireteam agent
```

Claude checks the files, verifies what's actually done (doesn't assume anything), and picks up from the last checkpoint.

**That's it.** You now have an AI agent with persistent memory.

---

## The 5-Minute Setup (Manual)

If you prefer to set things up yourself instead of using the Skill:

```bash
# 1. Clone Fireteam
git clone https://github.com/martinnaithani/fireteam.git

# 2. Copy .fireteam/ into your project
cp -r fireteam/.fireteam/ /path/to/your-project/.fireteam/

# 3. Write a quick PRD
cp fireteam/PRD_TEMPLATE.md /path/to/your-project/PRD.md
# Edit PRD.md — project name, what you're building, tech preferences

# 4. Open your AI tool, paste the prompt from START_MISSION.md, attach the PRD
# The agent sets up the mission, tasks, and board

# 5. Next session: paste the onboarding or resume prompt to continue
```

---

## What's Inside .fireteam/

You don't need to understand all of these to get started. Here's what each file does:

| File | What it is | Why it matters |
|------|-----------|---------------|
| `MISSION.md` | What you're building and why | Agent reads this first every session |
| `BOARD.md` | Task status board | Agent finds its next task here |
| `INTEL.md` | Key facts — stack, file paths, decisions | Context that never needs re-explaining |
| `tasks/OBJ-001.md` | Individual task with acceptance criteria | What to work on, how to know it's done |
| `handoffs/HO-001.md` | Notes between tasks | API contracts, file locations, what comes next |
| `checkpoints/` | Saved progress | Where the agent left off — survives crashes |
| `memory/2026-03-17.md` | What happened today | Session log for continuity |
| `CONVENTIONS.md` | Protocol rules | How the agent should behave |

---

## What Actually Happens Across Sessions

```
Session 1:
  Reads PRD → creates mission, 4 tasks, project intel
  Works on OBJ-001 (auth API) → checkpoints at 15, 30, 45 min
  Finishes OBJ-001 → writes notes: "API runs on :3001, 
    POST /auth/login returns JWT, see src/routes/auth.ts"
  Starts OBJ-002 (frontend) → context fills up at 40%
  Checkpoint saved: OBJ-002 at 40%, login form half-built

  ↓ session ends (context limit, crash, you close it, whatever)

Session 2:
  "Continue my fireteam"
  Reads MISSION.md → remembers the goal
  Reads INTEL.md → remembers the stack, file paths
  Reads checkpoint → OBJ-002 at 40%, login form
  Reads handoff from OBJ-001 → has the API contract
  Continues from exactly where it stopped
```

The agent doesn't re-read your entire codebase. It reads ~4K tokens of `.fireteam/` context and immediately knows what to do. That's 2% of a 200K context window — 98% left for actual work.

---

## Adding More Agents (Optional)

For bigger projects, you can run multiple agents in separate terminals. The same `.fireteam/` files coordinate between them:

```
Terminal 1: works on OBJ-001 (backend)
  → finishes, writes handoff with API contract

Terminal 2: reads handoff, works on OBJ-002 (frontend)
  → builds against the real API, no guessing

Terminal 3: waits for both, works on OBJ-003 (deploy)
```

Each agent claims tasks (so they don't duplicate work), writes checkpoints (crash-resistant), and communicates through handoff files (no copying context between terminals).

**You don't need to start with multiple agents.** Most projects work fine with one agent cycling through tasks. Add more terminals when a project is big enough that parallelism saves time.

---

## Hook Up Your Tool

For automatic session start briefings and end-of-session checkpoint reminders:

```bash
./fireteam.sh integrate claude-code   # Best — full hooks + CLAUDE.md
./fireteam.sh integrate cursor        # Cursor rules
./fireteam.sh integrate aider         # Aider conventions
./fireteam.sh integrate windsurf      # Windsurf rules
```

The Claude Code integration adds hooks that automatically brief the agent when you start and remind it to save when you stop. Zero manual steps.

---

## Useful Commands

```bash
./fireteam.sh status                        # What's happening in the project
./fireteam.sh task "Add payment form"       # Create a new task
./fireteam.sh checkpoint "backend"          # Save agent state
./fireteam.sh recover "backend"             # Diagnose after crash
```

---

## Common Questions

**Do I need multiple terminals?**
No. One agent cycling through tasks works for most projects. Multi-agent is optional for when you need parallelism.

**What happens when the context window fills up?**
The agent checkpoints every 15 minutes. When the session restarts, it reads the checkpoint and continues. That's the whole point.

**Does it work with existing code?**
Yes. The Skill scans your project structure and creates tasks based on what's actually there. Say "add fireteam to this project."

**How much context does .fireteam/ use?**
About 4K tokens at session start — mission, intel, checkpoint, current task. That's 2% of a 200K window.

**What if I don't use Claude Code?**
It works with any tool that reads files. Cursor, Aider, Windsurf, anything. Use `fireteam integrate` to generate tool-specific config.

**Is it safe?**
Agents can't read `.env` files, can't access other projects, can't install unspecified packages, can't copy credentials into `.fireteam/`. See CONVENTIONS.md Section 12.

**Can I see what's happening?**
Open `dashboard.html` in Chrome, select your `.fireteam/` folder. Live task board, handoffs, activity — no server needed.

---

## Next Steps

- Use `fireteam integrate claude-code` for automatic hooks
- Check the dashboard (`dashboard.html`) for a visual overview
- Read the [README](README.md) for multi-agent setup details
- Read `CONVENTIONS.md` for the full protocol rules

---

*Questions? [Open a discussion](https://github.com/martinnaithani/fireteam/discussions) on GitHub.*
