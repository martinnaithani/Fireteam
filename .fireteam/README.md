# .fireteam/ — Squad Coordination Protocol

## Heartbeat (Every Session)

```
□ MISSION.md    → why we're here
□ CONVENTIONS   → rules of engagement
□ ROSTER.md     → your role
□ SOUL file     → your identity
□ INTEL.md      → key facts
□ Field log     → recent context
□ Checkpoint    → resume state
□ BOARD.md      → your objectives
□ Handoffs      → context from others
□ Comms         → open threads
□ ASSESS        → highest priority action?
```

## File Map

| Folder | Purpose | Who Writes |
|--------|---------|------------|
| tasks/ | Objectives with goal chains | Team Lead creates |
| handoffs/ | Context transfer | Completing operator |
| comms/ | Async threads | Any operator |
| decisions/ | Architecture records | Any operator |
| memory/ | Daily field logs | Every operator |
| checkpoints/ | Session state + soul + heartbeat | Each operator |
| presets/ | Team configurations | Reference only |

## Naming

| Type | Pattern | Example |
|------|---------|---------|
| Objectives | `OBJ-XXX.md` | `OBJ-001.md` |
| Handoffs | `HO-XXX.md` | `HO-001.md` |
| Threads | `THREAD-XXX.md` | `THREAD-001.md` |
| Decisions | `DEC-XXX.md` | `DEC-001.md` |
| Field Logs | `YYYY-MM-DD.md` | `2026-03-08.md` |
| Checkpoints | `[callsign].md` | `backend.md` |
| Souls | `[callsign]-soul.md` | `backend-soul.md` |
| Heartbeats | `[callsign]-heartbeat.md` | `backend-heartbeat.md` |
