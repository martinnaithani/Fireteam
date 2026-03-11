#!/usr/bin/env bash
# Fireteam — Create .fireteam/ directory structure
# Usage: bash setup.sh [project-root]
# If project-root is omitted, uses current directory.

set -e
ROOT="${1:-.}"
FT="$ROOT/.fireteam"

if [ -d "$FT" ] && [ -f "$FT/MISSION.md" ]; then
  # Check if MISSION.md has content (not just template)
  if grep -q '^\w' "$FT/MISSION.md" 2>/dev/null; then
    echo ".fireteam/ already exists and has a populated MISSION.md."
    echo "Use the rejoin flow instead of setup."
    exit 0
  fi
fi

echo "Creating .fireteam/ in $ROOT"

mkdir -p "$FT/tasks"
mkdir -p "$FT/handoffs"
mkdir -p "$FT/comms"
mkdir -p "$FT/decisions"
mkdir -p "$FT/memory"
mkdir -p "$FT/checkpoints"

# Create .gitkeep files for empty directories
for d in tasks handoffs comms decisions memory checkpoints; do
  touch "$FT/$d/.gitkeep"
done

echo "Created .fireteam/ with: tasks/ handoffs/ comms/ decisions/ memory/ checkpoints/"
echo "Ready for Team Lead to populate MISSION.md, ROSTER.md, BOARD.md, INTEL.md"
