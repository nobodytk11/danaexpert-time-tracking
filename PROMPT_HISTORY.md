# Prompt History (Version A — AI-generated workflow)

This document records the **orchestration prompts** used to drive the AI-assisted build,
following the [Superpowers](https://github.com/obra/superpowers) methodology
(brainstorm → spec → plan → test-driven development → review).

Per the assessment brief:
- **Version A** — maximise AI generation (prompts below).
- **Version B** — engineer-led architecture and business rules; AI used where the brief
  allows as an assist/lookup tool. Version B’s process is documented under
  `docs/superpowers/` (spec, plan, reviews), not as a line-by-line prompt log.

## Primary orchestration prompt

```
Use the Superpowers methodology and agent skills (https://github.com/obra/superpowers)
to build this project end-to-end: brainstorm the design, write a spec, break it into
a plan, implement with test-driven development, and run a code review before finishing.

PROJECT: A "Focus Time Tracking" web app with productivity reporting.
CORE FEATURES: JWT auth; projects & tasks; start/stop time entries; productivity
report (totals per project/day, with a chart); optional Slack webhook on session end.
TECH STACK: React (frontend), Python + FastAPI (backend), SQLAlchemy + SQLite
(relational, Postgres-portable).
DELIVERABLES: /version-A-AI (AI-built), /version-B-Manual (clean layered + tests),
Comparison.md, PROMPT_HISTORY.md. Apply clean architecture, YAGNI, DRY. Make both
versions run.
```

## Key follow-up prompts (paraphrased)

A realistic agentic workflow uses one high-level prompt plus targeted follow-ups:

1. "Confirm stack: React + FastAPI + SQLite; relational schema portable to PostgreSQL."
2. "Slack integration via incoming webhook — optional, no-op when not configured."
3. "Version B: test-first — failing test, then minimal code to pass (TDD)."
4. "Projects/tasks scoped per user; return 404 for other users' resources."
5. "Time entries: one running timer per user; compute duration on stop."
6. "Report: aggregate finished entries by project and by day."
7. "Version A: single-file backend + single-file frontend, AI-typical structure."
8. "Upgrade version A UI and add task mark-done / delete for a stronger AI baseline."
9. "Run Superpowers code-reviewer on version B; save report under docs/superpowers/reviews/."

## How AI was applied (summary)

| | Version A | Version B |
|---|---|---|
| **Goal** | Maximum AI autonomy | Engineer-specified structure |
| **Prompting** | Broad orchestration + UI/feature prompts | Spec/plan in `docs/superpowers/`; TDD tasks |
| **Structure** | Flat (logic in handlers) | Routers / services / repositories / models |
| **Verification** | Manual smoke test | 22 automated tests + code review |
| **Outcome** | Fast, polished, harder to extend safely | Slower to specify, easier to maintain and defend |

**Lesson for the Hybrid AI Workflow:** prompting quality determines whether AI output
stays a prototype (A) or becomes production-shaped code (B). The developer’s job is to
supply architecture, invariants, and tests — not to type every line by hand.
