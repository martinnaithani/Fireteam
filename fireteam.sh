#!/usr/bin/env bash
# ═══════════════════════════════════════════
# 🔥 FIRETEAM — Squad Coordination CLI
# ═══════════════════════════════════════════
set -euo pipefail

find_ft_dir() {
  local dir="$PWD"
  while [ "$dir" != "/" ]; do
    if [ -d "$dir/.fireteam" ]; then echo "$dir/.fireteam"; return 0; fi
    dir="$(dirname "$dir")"
  done
  echo "Error: .fireteam/ not found. Copy it from the Fireteam repo." >&2; exit 1
}

FT="$(find_ft_dir)"
TPL="$FT/templates"
TODAY="$(date +%Y-%m-%d)"
NOW="$(date +%H:%M)"

sedi() { if sed --version >/dev/null 2>&1; then sed -i "$@"; else sed -i '' "$@"; fi; }

next_id() {
  local dir="$1" pfx="$2" max=0 num
  for f in "$dir"/${pfx}-*.md; do
    [ -e "$f" ] || continue
    num="$(basename "$f" | sed "s/${pfx}-0*//" | sed 's/\.md$//')"; num="${num:-0}"
    [ "$num" -gt "$max" ] 2>/dev/null && max="$num"
  done
  printf "%03d" $((max + 1))
}

cmd_task() {
  local title="${1:?Usage: fireteam task \"Title\"}"
  local id; id="$(next_id "$FT/tasks" "OBJ")"
  local f="$FT/tasks/OBJ-${id}.md"
  cp "$TPL/TASK_TEMPLATE.md" "$f"
  sedi "s/OBJ-XXX/OBJ-${id}/g" "$f"; sedi "s/\[Title\]/${title}/g" "$f"; sedi "s/YYYY-MM-DD/${TODAY}/g" "$f"
  echo "Created $f"
}

cmd_handoff() {
  local from="${1:?Usage: fireteam handoff \"from\" \"to\"}" to="${2:?}"
  local id; id="$(next_id "$FT/handoffs" "HO")"
  local f="$FT/handoffs/HO-${id}.md"
  cp "$TPL/HANDOFF_TEMPLATE.md" "$f"
  sedi "s/HO-XXX/HO-${id}/g" "$f"; sedi "s/\[From\]/${from}/g" "$f"; sedi "s/\[To\]/${to}/g" "$f"; sedi "s/YYYY-MM-DD/${TODAY}/g" "$f"
  echo "Created $f"
}

cmd_thread() {
  local topic="${1:?Usage: fireteam thread \"Topic\"}"
  local id; id="$(next_id "$FT/comms" "THREAD")"
  local f="$FT/comms/THREAD-${id}.md"
  cp "$TPL/THREAD_TEMPLATE.md" "$f"
  sedi "s/THREAD-XXX/THREAD-${id}/g" "$f"; sedi "s/\[Topic\]/${topic}/g" "$f"; sedi "s/YYYY-MM-DD/${TODAY}/g" "$f"
  echo "Created $f"
}

cmd_decision() {
  local title="${1:?Usage: fireteam decision \"Title\"}"
  local id; id="$(next_id "$FT/decisions" "DEC")"
  local f="$FT/decisions/DEC-${id}.md"
  cp "$TPL/DECISION_TEMPLATE.md" "$f"
  sedi "s/DEC-XXX/DEC-${id}/g" "$f"; sedi "s/\[Title\]/${title}/g" "$f"; sedi "s/YYYY-MM-DD/${TODAY}/g" "$f"
  echo "Created $f"
}

cmd_log() {
  local cs="${1:?Usage: fireteam log \"callsign\"}"
  local f="$FT/memory/${TODAY}.md"
  if [ ! -f "$f" ]; then cp "$TPL/FIELDLOG_TEMPLATE.md" "$f"; sedi "s/YYYY-MM-DD/${TODAY}/g" "$f"; fi
  cat >> "$f" <<EOF

---

## Session: ${cs} — ${NOW}

### Actions Taken

-

### Decisions Made

-

### Blockers

-

### Handoffs

-
EOF
  echo "Added session for ${cs} to $f"
}

cmd_checkpoint() {
  local cs="${1:?Usage: fireteam checkpoint \"callsign\"}"
  local f="$FT/checkpoints/${cs}.md"
  cp "$TPL/CHECKPOINT_TEMPLATE.md" "$f"
  sedi "s/YYYY-MM-DD HH:MM/${TODAY} ${NOW}/g" "$f"; sedi "s/\[callsign\]/${cs}/g" "$f"
  echo "Created checkpoint: $f"
}

cmd_heartbeat() {
  local cs="${1:?Usage: fireteam heartbeat \"callsign\"}"
  local f="$FT/checkpoints/${cs}-heartbeat.md"
  cp "$TPL/HEARTBEAT_TEMPLATE.md" "$f"
  sedi "s/\[callsign\]/${cs}/g" "$f"
  echo "Created heartbeat: $f"
}

cmd_soul() {
  local cs="${1:?Usage: fireteam soul \"callsign\"}"
  local f="$FT/checkpoints/${cs}-soul.md"
  cp "$TPL/SOUL_TEMPLATE.md" "$f"
  sedi "s/\[callsign\]/${cs}/g" "$f"
  echo "Created soul: $f"
}

cmd_recover() {
  local cs="${1:?Usage: fireteam recover \"callsign\"}"
  echo ""
  echo "RECOVERY REPORT — ${cs}"
  echo "═══════════════════════════════════"
  echo ""
  local ck="$FT/checkpoints/${cs}.md"
  if [ -f "$ck" ]; then
    local t; t="$(stat -c '%y' "$ck" 2>/dev/null | cut -d'.' -f1 || stat -f '%Sm' "$ck" 2>/dev/null || echo 'unknown')"
    echo "Checkpoint:  EXISTS ($t)"
    grep -m1 'Objective:' "$ck" 2>/dev/null | sed 's/^/  /' || true
    grep -m1 'Completion:' "$ck" 2>/dev/null | sed 's/^/  /' || true
  else echo "Checkpoint:  NOT FOUND (dirty exit)"; fi
  echo ""
  echo "Board entries:"
  grep -i "${cs}" "$FT/BOARD.md" 2>/dev/null | grep -v "^|--" | sed 's/^/  /' || echo "  (none)"
  echo ""
  local lg="$FT/memory/${TODAY}.md"
  if [ -f "$lg" ]; then echo "Field log:   EXISTS ($(grep -c '^## Session:' "$lg" 2>/dev/null || echo 0) sessions)"
  else echo "Field log:   NOT FOUND"; fi
  echo ""
  if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
    local d; d="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
    echo "Git:         $d uncommitted file(s)"
    [ "$d" -gt 0 ] && git status --porcelain 2>/dev/null | head -8 | sed 's/^/  /'
  else echo "Git:         not available"; fi
  echo ""
  echo "═══════════════════════════════════"
  echo "Next: paste RESUME_AGENT.md prompt"
  echo "with callsign=[${cs}]"
  echo ""
}

cmd_dashboard() {
  local sd; sd="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  local dp=""
  for c in "$sd/dashboard.py" "$(dirname "$FT")/dashboard.py"; do [ -f "$c" ] && dp="$c" && break; done
  if [ -z "$dp" ]; then echo "Error: dashboard.py not found." >&2; exit 1; fi
  local out="$(dirname "$FT")/dashboard.html"
  python3 "$dp" "$out"
  if command -v open >/dev/null 2>&1; then open "$out"
  elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$out"
  else echo "Open: $out"; fi
}

cmd_status() {
  echo ""
  echo "🔥 FIRETEAM STATUS — ${TODAY}"
  echo "═══════════════════════════════════"
  echo ""
  local total=0 ip=0 blk=0 rev=0 dn=0
  for f in "$FT/tasks/"OBJ-*.md; do
    [ -e "$f" ] || continue; total=$((total+1))
    grep -q 'in-progress' "$f" 2>/dev/null && ip=$((ip+1))
    grep -q 'blocked' "$f" 2>/dev/null && blk=$((blk+1))
    grep -q 'review' "$f" 2>/dev/null && rev=$((rev+1))
    grep -q 'Status:.*done' "$f" 2>/dev/null && dn=$((dn+1))
  done
  echo "Objectives:  $total total | $ip active | $blk blocked | $rev review | $dn done"
  local ho=0 th=0 dec=0
  for f in "$FT/handoffs/"HO-*.md; do [ -e "$f" ] && ho=$((ho+1)); done
  for f in "$FT/comms/"THREAD-*.md; do [ -e "$f" ] && grep -q 'Status: open' "$f" 2>/dev/null && th=$((th+1)); done
  for f in "$FT/decisions/"DEC-*.md; do [ -e "$f" ] && dec=$((dec+1)); done
  echo "Handoffs:    $ho | Threads: $th open | Decisions: $dec"
  local logs=0 ckpts=0
  for f in "$FT/memory/"*.md; do [ -e "$f" ] && logs=$((logs+1)); done
  for f in "$FT/checkpoints/"*.md; do [ -e "$f" ] || continue; case "$f" in *-soul.md|*-heartbeat.md) ;; *) ckpts=$((ckpts+1));; esac; done
  echo "Field logs:  $logs | Checkpoints: $ckpts"
  echo ""
  if [ -f "$FT/memory/${TODAY}.md" ]; then
    echo "Today's ops:"
    grep '^## Session:' "$FT/memory/${TODAY}.md" 2>/dev/null | sed 's/## Session: /  /' || echo "  (quiet)"
  fi
  echo ""
}

cmd_hq() {
  local sd; sd="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  local hp=""
  for c in "$sd/hq.py" "$(dirname "$FT")/hq.py"; do [ -f "$c" ] && hp="$c" && break; done
  if [ -z "$hp" ]; then echo "Error: hq.py not found." >&2; exit 1; fi
  shift 2>/dev/null || true
  python3 "$hp" "$@"
}

cmd_pro() {
  # Legacy alias — just launches HQ
  cmd_hq "$@"
}

cmd_dashboard() {
  local sd; sd="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  local hp=""
  for c in "$sd/hq.py" "$(dirname "$FT")/hq.py"; do [ -f "$c" ] && hp="$c" && break; done
  if [ -z "$hp" ]; then echo "Error: hq.py not found." >&2; exit 1; fi
  python3 "$hp" --generate
}

cmd_help() {
  cat <<'EOF'

  🔥 FIRETEAM — Squad Coordination CLI

  fireteam task        "Title"            Create objective
  fireteam handoff     "from" "to"        Create handoff
  fireteam thread      "Topic"            Start thread
  fireteam decision    "Title"            Record decision
  fireteam log         "callsign"         Add to field log
  fireteam checkpoint  "callsign"         Save operator state
  fireteam heartbeat   "callsign"         Create heartbeat file
  fireteam soul        "callsign"         Create identity file
  fireteam recover     "callsign"         Diagnose after crash
  fireteam dashboard                      Generate visual HQ
  fireteam status                         Terminal status

  PRO MODE (auto-fire agents):
  fireteam hq                             Launch live command center (UI + daemon)
  fireteam hq --no-auto                   UI only, fire agents manually
  fireteam hq --port 5050                 Custom port
  fireteam pro                            Alias for fireteam hq
  fireteam dashboard                      Generate static dashboard.html

EOF
}

case "${1:-help}" in
  task)       shift; cmd_task "$@" ;;
  handoff)    shift; cmd_handoff "$@" ;;
  thread)     shift; cmd_thread "$@" ;;
  decision)   shift; cmd_decision "$@" ;;
  log)        shift; cmd_log "$@" ;;
  checkpoint) shift; cmd_checkpoint "$@" ;;
  heartbeat)  shift; cmd_heartbeat "$@" ;;
  soul)       shift; cmd_soul "$@" ;;
  recover)    shift; cmd_recover "$@" ;;
  hq)         cmd_hq "$@" ;;
  pro)        cmd_pro "$@" ;;
  dashboard)  cmd_dashboard ;;
  status)     cmd_status ;;
  help|--help|-h) cmd_help ;;
  *)          echo "Unknown: $1"; cmd_help; exit 1 ;;
esac
