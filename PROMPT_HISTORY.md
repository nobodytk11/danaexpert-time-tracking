# Prompt History

This document records how each version was driven. Per the assessment brief:

- **Version A** — maximise AI generation with minimal orchestration.
- **Version B** — engineer-led build following the [Superpowers](https://github.com/obra/superpowers)
  workflow end-to-end. Artifacts live under `docs/superpowers/`.

---

## Version A (`version-A-AI`) — minimal prompting

Version A was not built through the Superpowers loop. A small number of broad prompts
let the agent produce a working, polished app quickly — the typical “AI emits the whole
thing” shape (single-file backend, single HTML frontend, logic in route handlers, no
automated tests).

**Primary prompt (paraphrased):**

```
Build a Focus Time Tracking web app in /version-A-AI: JWT auth, projects & tasks,
start/stop timer (one running entry per user), productivity report. Use a single
FastAPI file + SQLite/SQLAlchemy and a single index.html with React + Babel from CDN.
Keep it flat — business logic inside route handlers.
```

**Follow-up (paraphrased):** polish the UI; add mark-done and delete for tasks/projects.

No separate spec, plan, TDD steps, or structured review. Outcome: fast and demo-ready;
harder to extend safely. See `Comparison.md` and
`docs/superpowers/reviews/2026-06-16-code-review-version-A.md`.

---

## Version B (`version-B-Manual`) — Superpowers workflow

Version B follows the standard Superpowers pipeline. Each step below is the
**orchestration prompt** used (or equivalent intent). Concrete outputs are linked.

### 1. `brainstorming` — design before code

```
Use the Superpowers brainstorming skill. I need a Focus Time Tracking web app for a
technical assessment: JWT auth, projects/tasks, start/stop time entries, productivity
report (totals per project and per day, with a chart), optional Slack webhook on
session end. Build TWO versions in one repo — version-A-AI (max AI) and version-B-Manual
(layered, testable, defensible). Stack: React + FastAPI + SQLAlchemy + SQLite
(Postgres-portable). Ask clarifying questions, explore alternatives, then write the
design in sections for my approval.
```

**Output:** `docs/superpowers/specs/2026-06-16-focus-time-tracking-design.md`

Key decisions captured: layered architecture for B (routers / services / repositories /
models), per-user scoping with 404 for others’ resources, one running timer per user,
Slack no-op when unconfigured, YAGNI on teams/billing.

---

### 2. `using-git-worktrees` — isolated workspace after design approval

```
Design approved. Use the Superpowers using-git-worktrees skill: create an isolated
worktree on a feature branch for version-B-Manual, run backend venv + pip install and
frontend npm install, then confirm pytest starts from a clean baseline before
implementation.
```

**Intent:** separate branch/worktree so B’s TDD work does not collide with A; verify
tooling before writing feature code.

---

### 3. `writing-plans` — bite-sized tasks with file paths

```
Use the Superpowers writing-plans skill. From the approved design spec, write an
implementation plan for version-B-Manual only. Break work into small tasks (2–5 minutes
each). Every task must name exact file paths, expected behaviour, and verification
steps. Order: backend scaffold → models → security (TDD) → auth → projects/tasks →
time entries → reporting → Slack → React/Vite frontend → docs. Use checkbox syntax.
```

**Output:** `docs/superpowers/plans/2026-06-16-focus-time-tracking.md`

---

### 4. `subagent-driven-development` / `executing-plans` — execute the plan

```
Use executing-plans (or subagent-driven-development). Implement the plan phase by phase.
One task at a time: read the task, implement, run its verification step, then move on.
Do not skip ahead. version-A-AI can be a lighter pass after B’s backend patterns are clear.
```

**Execution notes:** Phases 1–2 of the plan map 1:1 to `version-B-Manual/backend/` and
`version-B-Manual/frontend/`. Each backend slice was implemented in plan order (scaffold
→ security → auth → projects → time entries → reports → Slack → UI).

---

### 5. `test-driven-development` — RED → GREEN → REFACTOR per task

Used **during** plan execution, not after. Representative prompts per slice:

**Security (Task 3):**

```
TDD Task 3 from the plan. RED first: write failing tests in tests/test_security.py for
password hash/verify and JWT encode/decode. Run pytest — confirm FAIL. Then minimal
implementation in app/core/security.py until GREEN. No code before the failing test.
```

**Auth (Task 4):**

```
TDD Task 4. RED: tests/test_auth.py — register, duplicate email rejected, login returns
token, bad password 401. Watch them fail, then implement auth_service + user_repository
+ auth router until all pass.
```

**Time entries (Task 6) — business rules:**

```
TDD Task 6. RED: tests/test_time_entries.py — start creates running entry; cannot start
a second while one runs; stop sets duration_seconds; cannot stop twice. GREEN only after
tests fail for the right reason.
```

**Reporting & Slack (Tasks 7–8):** same pattern — failing aggregation tests, then
`report_service`; mocked webhook tests, then `slack_notifier` wired into stop.

**Result:** 22 pytest tests in `version-B-Manual/backend/tests/`.

---

### 6. `requesting-code-review` — review against plan before calling done

```
Use requesting-code-review / code-reviewer. Review version-B-Manual against the design
spec and implementation plan. Check architecture boundaries, security, test coverage of
invariants, and interview defensibility. Save the report under docs/superpowers/reviews/.
Also review version-A-AI separately for the Comparison.md contrast.
```

**Outputs:**

- `docs/superpowers/reviews/2026-06-16-code-review.md` (version B)
- `docs/superpowers/reviews/2026-06-16-code-review-version-A.md` (version A)

---

### 7. `finishing-a-development-branch` — verify and close the loop

```
Use finishing-a-development-branch. Run full verification: pytest -q, npm run build,
smoke both versions. Summarise deliverables vs assessment brief, list known follow-ups
from review, and document completion in docs/superpowers/.
```

**Output:** `docs/superpowers/2026-06-16-finishing-summary.md`

---

## Summary

| | Version A | Version B |
|---|---|---|
| **Workflow** | Ad-hoc broad prompts | Superpowers: brainstorm → worktree → plan → execute → TDD → review → finish |
| **Prompting** | ~2 prompts | ~8 orchestration prompts + per-task TDD prompts |
| **Artifacts** | Code only | Spec, plan, 22 tests, 2 review reports, finishing summary |
| **Developer role** | Steer features & UI | Supply architecture, invariants, tests; agent implements in bounded tasks |

**Lesson:** prompting quality and process determine whether AI output stays a prototype (A)
or becomes code you can trust, change, and defend in an interview (B).
