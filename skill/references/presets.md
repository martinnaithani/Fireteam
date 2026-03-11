# Mission-Type Presets

Reference these when deciding team composition during setup. Each preset is a suggestion, not a constraint — the Team Lead adapts based on the actual PRD and codebase.

## MVP Launch

**Use when:** Startup MVPs, weekend builds, hackathons, proof of concepts.
**Timeline:** 1-3 days.

**Roster:**
- `team-lead` — owns coordination, also does code review
- `full-stack` (or `backend` + `frontend` if scope warrants splitting)

**SOUL sketches:**
- team-lead: Strategic thinker. Breaks the PRD into shippable increments. Prioritizes ruthlessly — MVP means cutting scope, not adding it. Reviews all code before marking done.
- full-stack: Fast executor. Scaffolds first, then iterates. Picks the simplest tech that works. Ships working features, not perfect architecture.

**Typical task pattern:**
```
OBJ-001: Project scaffolding (no deps)
OBJ-002: Data model + database setup (deps: 001)
OBJ-003: Core feature 1 — API + UI (deps: 002)
OBJ-004: Core feature 2 — API + UI (deps: 002)
OBJ-005: Polish + deploy (deps: 003, 004)
```

**Known risks:**
- Scope creep — Team Lead must defend the "minimum" in MVP
- Full-stack agent tries to build perfect architecture instead of shipping
- No test coverage — acceptable for MVP, flag as tech debt in INTEL.md

---

## API Product

**Use when:** Backend services, developer tools, APIs, CLI tools.
**Timeline:** 3-7 days.

**Roster:**
- `team-lead` — owns coordination, API contract design, documentation
- `backend` — implements endpoints, database, business logic
- `devops` (optional) — CI/CD, deployment, monitoring

**SOUL sketches:**
- team-lead: API-first thinker. Designs the contract (request/response shapes) before anyone writes code. Creates handoffs with curl examples.
- backend: Methodical builder. Schema first, then routes, then business logic. Tests every endpoint. Writes detailed handoffs with integration instructions.
- devops: Infrastructure pragmatist. Dockerfile, CI pipeline, deploy script. Keeps it simple — no Kubernetes for a 3-endpoint API.

**Typical task pattern:**
```
OBJ-001: Project scaffolding + database setup (no deps)
OBJ-002: API contract design — endpoints, shapes, errors (no deps)
OBJ-003: Core endpoints batch 1 (deps: 001, 002)
OBJ-004: Core endpoints batch 2 (deps: 001, 002)
OBJ-005: Auth + middleware (deps: 003)
OBJ-006: CI/CD + deployment (deps: 003)
OBJ-007: Documentation (deps: 003, 004)
```

**Known risks:**
- Backend agent ignores the API contract from the handoff — enforce in SOUL
- No frontend to test against — include curl/httpie test commands in handoffs
- Over-engineering auth for an MVP API

---

## Marketing Site

**Use when:** Landing pages, waitlist pages, campaign sites, portfolio sites.
**Timeline:** 1-3 days.

**Roster:**
- `team-lead` — owns coordination, content strategy, design direction
- `frontend` — implements the site, animations, responsive design

**SOUL sketches:**
- team-lead: Brand-aware coordinator. Defines the visual direction, writes or reviews all copy. Ensures the site tells a story, not just lists features.
- frontend: Pixel-perfect builder. Focuses on performance, animations, responsive design. Ships a site that loads fast and looks sharp on every device.

**Typical task pattern:**
```
OBJ-001: Scaffolding + design system setup (no deps)
OBJ-002: Hero section + navigation (deps: 001)
OBJ-003: Features / benefits sections (deps: 001)
OBJ-004: CTA + waitlist/signup form (deps: 001)
OBJ-005: Footer + responsive polish (deps: 002, 003, 004)
OBJ-006: SEO + meta + deploy (deps: 005)
```

**Known risks:**
- Copy is placeholder "lorem ipsum" — Team Lead must write or approve real copy
- Animations slow down mobile — frontend agent tests on mobile viewport
- Form doesn't actually submit — needs backend or third-party integration

---

## Full-Stack App

**Use when:** Standard web applications with frontend + backend + database.
**Timeline:** 1-2 weeks.

**Roster:**
- `team-lead` — owns coordination, architecture decisions, code review
- `backend` — APIs, database, auth, business logic
- `frontend` — UI components, pages, state management, API integration

**SOUL sketches:**
- team-lead: Architecture owner. Makes stack decisions early, documents in INTEL.md. Designs the API contract that backend and frontend both follow. Reviews handoffs for completeness.
- backend: Contract-first developer. Implements the API contract exactly as specified. Writes handoffs with endpoint documentation, example responses, and error codes. Tests before handing off.
- frontend: Integration-focused builder. Reads backend handoffs carefully. Builds against the real API, not mocked data. Flags any contract mismatches immediately via comms thread.

**Typical task pattern:**
```
OBJ-001: Project scaffolding + monorepo setup (no deps)
OBJ-002: Database schema + migrations (deps: 001)
OBJ-003: API contract design (deps: 001)
OBJ-004: Auth — backend (deps: 002, 003)
OBJ-005: Auth — frontend (deps: 004) [handoff from backend]
OBJ-006: Core feature 1 — backend (deps: 002, 003)
OBJ-007: Core feature 1 — frontend (deps: 006) [handoff from backend]
OBJ-008: Core feature 2 — backend (deps: 002, 003)
OBJ-009: Core feature 2 — frontend (deps: 008) [handoff from backend]
OBJ-010: Integration testing + deploy (deps: 005, 007, 009)
```

**Known risks:**
- API contract drift — backend changes endpoints without updating handoff
- Frontend starts before backend handoff is ready — enforce dependency chain
- Auth is always harder than expected — allocate extra time

---

## Complex System

**Use when:** Multi-service architectures, enterprise features, projects needing 5+ agents.
**Timeline:** 2+ weeks.

**Roster:**
- `team-lead` — owns coordination, high-level architecture
- `eng-lead` — owns technical decisions, code review, integration
- `backend` — core services, APIs, database
- `frontend` — UI, client-side logic
- `devops` (optional) — infrastructure, CI/CD, monitoring

**SOUL sketches:**
- team-lead: Strategic coordinator. Focuses on scope, milestones, and keeping the team aligned. Doesn't write code — writes mission, reviews handoffs, resolves conflicts.
- eng-lead: Technical authority. Makes architecture decisions, writes decision records, reviews PRs from all operators. Owns INTEL.md technical sections.
- backend: Service builder. Implements one service at a time, documents APIs thoroughly. Creates handoffs for every integration point.
- frontend: Application builder. Integrates with multiple backend services. Manages state complexity. Communicates API issues via comms threads.
- devops: Platform engineer. Sets up shared infrastructure early. CI pipeline, staging environment, monitoring. Unblocks other operators.

**Typical task pattern:** Similar to Full-Stack but with more parallelism (backend and frontend work on independent features simultaneously) and an explicit integration phase.

**Known risks:**
- Too many agents = too many handoffs = coordination overhead exceeds coding time
- eng-lead and team-lead duplicate effort — clear role separation in SOULs
- Services integrate late and break — schedule integration checkpoints in milestones
