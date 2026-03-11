# Recon — Codebase Assessment Procedure

Run this when setting up Fireteam on an existing project (code already exists). The goal is to understand what's built, what stack is in use, and what patterns are established — so that tasks reference real files and real conventions.

## When to Run Recon

- `.fireteam/` does not exist AND the project directory contains source code
- `.fireteam/` does not exist AND user says "add fireteam to this project" or similar
- PRD + code both exist (Phase 2 of a project, new feature on existing codebase)

## The Recon Checklist

Scan these in order. Read at most ~20 files total. Must complete in under 30 seconds.

### 1. Project Identity
- [ ] `README.md` or `README` — what the project claims to be
- [ ] `LICENSE` — open source? proprietary?
- [ ] Any docs/ folder — existing documentation

### 2. Stack & Dependencies
- [ ] `package.json` → Node.js project, check scripts, dependencies, devDependencies
- [ ] `requirements.txt` or `pyproject.toml` or `Pipfile` → Python
- [ ] `Cargo.toml` → Rust
- [ ] `go.mod` → Go
- [ ] `Gemfile` → Ruby
- [ ] `pom.xml` or `build.gradle` → Java/Kotlin
- [ ] Check for multiple language files (monorepo indicator)

### 3. Project Structure
- [ ] Directory listing, 2 levels deep: `find . -maxdepth 2 -type d -not -path '*/node_modules/*' -not -path '*/.git/*'`
- [ ] Identify: src/, app/, lib/, pages/, routes/, api/, components/, public/, static/, tests/
- [ ] Note any unusual or project-specific directory conventions

### 4. Configuration
- [ ] `.env.example` or `.env.sample` → required environment variables, external services
- [ ] Config files: `next.config.*`, `vite.config.*`, `webpack.config.*`, `tsconfig.json`, `tailwind.config.*`
- [ ] CI/CD: `.github/workflows/`, `Dockerfile`, `docker-compose.yml`, `vercel.json`, `netlify.toml`
- [ ] Database: `prisma/schema.prisma`, `drizzle.config.*`, migrations folder, `knexfile.*`

### 5. Entry Points & API Surface
- [ ] Main entry: `index.*`, `main.*`, `app.*`, `server.*`
- [ ] Route definitions: scan for route/endpoint patterns
- [ ] API routes: `pages/api/` (Next.js), `routes/` (Express), `app/api/` (Next.js App Router)
- [ ] Note: how many endpoints exist? what do they do?

### 6. Database Schema
- [ ] ORM schema files (Prisma, Drizzle, Sequelize models)
- [ ] Migration files — how many? recent?
- [ ] Seed files

### 7. Recent Activity (if git repo)
- [ ] `git log --oneline -20` — what was worked on recently
- [ ] `git status` — uncommitted changes?
- [ ] `git branch -a` — active branches
- [ ] Who was the last committer? (indicates if AI or human was working)

### 8. Test Coverage
- [ ] Test directory: `tests/`, `__tests__/`, `spec/`, `test/`
- [ ] Test config: `jest.config.*`, `vitest.config.*`, `pytest.ini`
- [ ] Rough coverage: how many test files exist vs. source files?

### 9. Incomplete Work Markers
- [ ] Search for `TODO`, `FIXME`, `HACK`, `XXX` in source files
- [ ] Check for placeholder content: `lorem ipsum`, `example.com`, hardcoded test values
- [ ] Look for commented-out code blocks

### 10. External Services
- [ ] From `.env.example`: which APIs, databases, services does this connect to?
- [ ] Auth provider (Auth0, Clerk, NextAuth, Supabase Auth, etc.)
- [ ] Payment (Stripe, etc.)
- [ ] Email (SendGrid, Resend, etc.)
- [ ] Storage (S3, Cloudflare R2, etc.)

## Recon Output

After scanning, present findings to the user in this format:

```
## Recon Summary

**Project:** [name from README/package.json]
**Stack:** [e.g., Next.js 14, TypeScript, Tailwind, Prisma, SQLite]
**Structure:** [e.g., App Router, src/ directory, 12 API routes]
**Status:** [e.g., MVP ~60% complete, auth missing, no tests]

### What Exists
- [list of built features/endpoints/pages]

### What's Missing or Incomplete
- [list of TODOs, gaps, placeholder code]

### Key Files
| File | Purpose |
|------|---------|
| src/app/layout.tsx | Root layout |
| src/app/api/... | API routes |
| prisma/schema.prisma | Database schema |

### Conventions Detected
- [naming patterns, directory structure, import style]

### External Services Required
- [list from .env.example]
```

**Wait for user confirmation before proceeding to task creation.** If the user corrects anything, update the summary.

## Feeding Recon Into Fireteam Setup

After confirmation:

1. **INTEL.md** gets populated with: stack, key file paths, API routes, database schema, conventions, external services, environment variables
2. **Tasks** reference real files: not "build the API" but "add auth middleware to existing Express app in src/routes/, following the pattern in src/routes/users.ts"
3. **MISSION.md** respects what exists: mission is about what comes NEXT, not rebuilding what's already there
