#!/usr/bin/env bash
# Fireteam — Session End Hook
# Reminds agent to checkpoint and update field log before closing.
# Designed for Claude Code's hook system (Stop event).
#
# Install: fireteam integrate claude-code
# Or manually add to .claude/settings.json:
#   "hooks": { "Stop": [{ "command": "bash .fireteam/hooks/session-end.sh" }] }

set -e

# Find .fireteam/
FT=""
for d in ".fireteam" "../.fireteam" "../../.fireteam"; do
  [ -d "$d" ] && FT="$d" && break
done

if [ -z "$FT" ]; then
  exit 0
fi

if ! grep -q '^\w' "$FT/MISSION.md" 2>/dev/null; then
  exit 0
fi

TODAY=$(date +%Y-%m-%d)

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔥 FIRETEAM — Session End Checklist"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Before this session ends:"
echo "  □ Update checkpoint    → .fireteam/checkpoints/[you].md"
echo "  □ Update field log     → .fireteam/memory/${TODAY}.md"
echo "  □ Update BOARD.md      → move your task status"
echo "  □ Create handoff       → .fireteam/handoffs/ (if work feeds another agent)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
