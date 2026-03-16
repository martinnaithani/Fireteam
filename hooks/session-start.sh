#!/usr/bin/env bash
# Fireteam — Session Start Hook
# Automatically reads .fireteam/ and prints a mission briefing.
# Designed for Claude Code's hook system (SessionStart event).
#
# Install: fireteam integrate claude-code
# Or manually add to .claude/settings.json:
#   "hooks": { "SessionStart": [{ "command": "bash .fireteam/hooks/session-start.sh" }] }

set -e

# Find .fireteam/
FT=""
for d in ".fireteam" "../.fireteam" "../../.fireteam"; do
  [ -d "$d" ] && FT="$d" && break
done

if [ -z "$FT" ]; then
  exit 0  # No .fireteam/ found — silently skip, don't break non-fireteam projects
fi

# Check if MISSION.md has content
if ! grep -q '^\w' "$FT/MISSION.md" 2>/dev/null; then
  exit 0  # Empty mission — not yet bootstrapped
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔥 FIRETEAM — Mission Briefing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Mission
MISSION=$(grep -A1 "^## Mission" "$FT/MISSION.md" 2>/dev/null | tail -1 | sed 's/^[[:space:]]*//')
if [ -n "$MISSION" ] && [ "$MISSION" != "<!--" ]; then
  echo "MISSION: $MISSION"
fi

# Status
STATUS=$(grep -o '\*\*Status:\*\*[[:space:]]*[A-Za-z]*' "$FT/MISSION.md" 2>/dev/null | head -1 | sed 's/.*\*\*[[:space:]]*//')
[ -n "$STATUS" ] && echo "STATUS:  $STATUS"

echo ""

# Board summary
if [ -f "$FT/BOARD.md" ]; then
  IP=0; BL=0; BK=0; RV=0; DN=0
  for f in "$FT/tasks/"OBJ-*.md; do
    [ -e "$f" ] || continue
    s=$(grep -o '\*\*Status:\*\*[[:space:]]*[a-z-]*' "$f" 2>/dev/null | head -1 | sed 's/.*\*\*[[:space:]]*//')
    case "$s" in
      in-progress) IP=$((IP+1)) ;;
      backlog)     BL=$((BL+1)) ;;
      blocked)     BK=$((BK+1)) ;;
      review)      RV=$((RV+1)) ;;
      done)        DN=$((DN+1)) ;;
    esac
  done
  TOTAL=$((IP+BL+BK+RV+DN))
  echo "BOARD: $TOTAL objectives | $IP active | $BL backlog | $BK blocked | $RV review | $DN done"
fi

# Recent handoffs
HO_COUNT=0
for f in "$FT/handoffs/"HO-*.md; do [ -e "$f" ] && HO_COUNT=$((HO_COUNT+1)); done
[ "$HO_COUNT" -gt 0 ] && echo "HANDOFFS: $HO_COUNT pending — check .fireteam/handoffs/"

# Open threads
TH_COUNT=0
for f in "$FT/comms/"THREAD-*.md; do
  [ -e "$f" ] && grep -q 'Status: open' "$f" 2>/dev/null && TH_COUNT=$((TH_COUNT+1))
done
[ "$TH_COUNT" -gt 0 ] && echo "THREADS: $TH_COUNT open — check .fireteam/comms/"

# Today's field log
TODAY=$(date +%Y-%m-%d)
if [ -f "$FT/memory/${TODAY}.md" ]; then
  SESSIONS=$(grep -c '^## Session:' "$FT/memory/${TODAY}.md" 2>/dev/null || echo 0)
  echo "FIELD LOG: $SESSIONS session(s) logged today"
fi

echo ""
echo "Read .fireteam/CONVENTIONS.md for rules of engagement."
echo "Run the heartbeat checklist before starting work."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
