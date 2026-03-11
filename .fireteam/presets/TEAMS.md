# Team Presets

Drop-in squad configurations. Copy the roster block into your ROSTER.md.

---

## Solo

Best for: quick builds, prototypes, 1-2 day projects.

```
### Team Lead
- **Callsign:** `team-lead`
- **Duties:** Planning, architecture, code review, all coordination
- **Clearance:** All .fireteam/ files

### Dev
- **Callsign:** `dev`
- **Duties:** All implementation — frontend, backend, database, deployment
- **Clearance:** Assigned tasks, codebase
```

---

## Duo

Best for: landing pages, MVPs, 3-5 day projects.

```
### Team Lead
- **Callsign:** `team-lead`
- **Duties:** Planning, architecture, copy, coordination, design direction
- **Clearance:** All .fireteam/ files

### Full Stack
- **Callsign:** `full-stack`
- **Duties:** Frontend + backend implementation, database, API design
- **Clearance:** Assigned tasks, full codebase
```

---

## Squad

Best for: standard web apps, 1-2 week projects.

```
### Team Lead
- **Callsign:** `team-lead`
- **Duties:** Planning, architecture, scope management, copy, review
- **Clearance:** All .fireteam/ files

### Backend Lead
- **Callsign:** `backend`
- **Duties:** APIs, database, server logic, integrations
- **Clearance:** Assigned tasks, src/api/, src/lib/, db/

### Frontend Lead
- **Callsign:** `frontend`
- **Duties:** UI components, styling, client-side state, UX
- **Clearance:** Assigned tasks, src/components/, src/app/

### Design Lead
- **Callsign:** `design`
- **Duties:** Design system, component specs, visual QA, assets
- **Clearance:** Assigned tasks, design files, public/
```

---

## Platoon

Best for: complex systems, 2+ week projects, multiple workstreams.

```
### Team Lead
- **Callsign:** `team-lead`
- **Duties:** Strategy, scope, stakeholder management, coordination
- **Clearance:** All .fireteam/ files

### Engineering Lead
- **Callsign:** `eng-lead`
- **Duties:** Architecture decisions, technical review, task breakdown
- **Clearance:** decisions/, assigned tasks, full codebase

### Backend Lead
- **Callsign:** `backend`
- **Duties:** APIs, database, server logic, integrations, performance
- **Clearance:** Assigned tasks, server-side code

### Frontend Lead
- **Callsign:** `frontend`
- **Duties:** UI/UX implementation, responsive design, client-side state
- **Clearance:** Assigned tasks, client-side code

### DevOps Lead
- **Callsign:** `devops`
- **Duties:** CI/CD, deployment, infrastructure, monitoring, security
- **Clearance:** Assigned tasks, config files, infrastructure

### QA Lead
- **Callsign:** `qa`
- **Duties:** Test strategy, test cases, bug tracking, regression testing
- **Clearance:** Assigned tasks, test files
```
