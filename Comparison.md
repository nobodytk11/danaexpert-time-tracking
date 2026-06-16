# Comparison: Version A (AI) vs Version B (Structured engineering)

Both versions implement the **same product** (auth, projects, tasks, start/stop time
tracking, productivity report) with the **same stack family** (FastAPI + SQLAlchemy +
SQLite, React frontend). They differ in *how the code is organised, verified, and how
AI was applied* — as required by the assessment brief.

> **Naming note:** `version-B-Manual` follows the assignment folder name (*Manual Coding*).
> In this submission it means **engineer-led structure and logic** (layered design, TDD,
> code review). Per the brief, AI may still be used as a lookup/assist tool; the contrast
> with version A is *how much architecture and verification the developer specifies*, not
> whether any AI was involved.

## 1. Completion time

| Version | Approx. effort | Notes |
|---|---|---|
| **A — AI-generated** | fast | One backend file + one HTML file, feature-rich UI. Minimal structural guidance in prompts — AI decides layout and mixes concerns. |
| **B — Structured** | slower up front | Time spent on **design decisions**: layer boundaries, business rules, test cases, and review. Implementation is faster with tooling; the effort is in **specification and verification**. |

The headline: **A optimises for AI autonomy and speed; B optimises for structure,
tests, and maintainability**. Both run the same features. Version A shows what strong
high-level prompting delivers; version B shows what happens when the developer **defines
architecture, rules, and test coverage** before and during implementation.

## 2. Code quality

### Cleanliness / structure
- **A**: feature-rich but everything lives in one module; business logic sits inside the
  route handlers and the whole UI is one HTML file. Fast and readable top-to-bottom for a
  small app, but concerns are mixed and it has no automated tests.
- **B**: clear separation —
  - `routers/` translate HTTP ↔ service calls,
  - `services/` hold business rules,
  - `repositories/` own all SQL,
  - `models/` / `schemas/` separate the DB shape from the API contract.
  Each file has one responsibility and is small enough to reason about.

### Maintainability
- **A**: changing one rule risks touching unrelated code in the same file; no tests means
  regressions are silent.
- **B**: rules are isolated in services and pinned by **22 automated tests**, so changes
  are safe and intent is documented by the tests.

### Security
- **Both**: passwords hashed with bcrypt; JWT bearer auth; every query scoped to the
  authenticated user; "not found" returned instead of "forbidden" so we don't leak
  the existence of other users' data.
- **A weaknesses**: hard-coded JWT secret in source; permissive CORS (`*`); no test
  coverage proving the access-control rules actually hold.
- **B improvements**: secret and config read from environment (`.env`), access-control
  rules are covered by tests (e.g. "a second user sees an empty project list",
  "cannot add a task to another user's project").

## 3. Lessons learned

**Where AI did well**
- Scaffolding boilerplate (models, CRUD endpoints, request/response shapes) extremely fast.
- Producing a working end-to-end slice from a single high-level prompt.
- Acting as a fast reference for framework syntax (SQLAlchemy queries, FastAPI deps).

**Where human judgement was required**
- **Architecture & boundaries**: deciding the routers/services/repositories split and
  keeping logic out of the handlers — AI defaults to the flat version unless told otherwise.
- **Test-first discipline**: defining the *behaviours and edge cases* to test
  (single running timer, can't stop twice, ownership checks) is a design activity, not
  something to delegate blindly.
- **Security hardening**: moving secrets to config, thinking about information leakage.
- **Knowing when to stop (YAGNI)**: keeping the scope tight instead of accepting every
  feature AI is happy to add.

**Takeaway:** AI accelerates implementation. The measurable gap between A and B is
**process**: spec → plan → TDD → review (Superpowers) and a layered codebase that can
be tested and extended — not raw typing speed alone.

## 4. Systematic review (Superpowers)

Version B additionally went through an AI-driven `code-reviewer` pass (see
[`docs/superpowers/reviews/2026-06-16-code-review.md`](./docs/superpowers/reviews/2026-06-16-code-review.md)).
It found no critical bugs, confirmed the layering, and surfaced concrete hardening items
(fail-closed JWT secret, a DB constraint for the single-timer rule, extra ownership/auth
tests). Running a structured review — not just generating code — is itself part of working
effectively with AI.
