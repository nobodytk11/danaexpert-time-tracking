# Code Review — version-A-AI (the AI-generated version)

> Produced by the Superpowers `code-reviewer` step. Read-only review — no files changed.
> Date: 2026-06-16. This review intentionally characterizes the weaknesses of the
> "100% AI, minimal intervention" version, as input for `Comparison.md`.

**Scope:** `version-A-AI/backend/main.py`, `version-A-AI/frontend/index.html`

## Overall assessment

Version A is **functional and visually polished** — it implements the full feature set
(JWT auth, projects/tasks CRUD, mark-done, delete, start/stop timer, productivity report)
and the UI looks good. Credit where due: per-user query scoping is applied consistently,
and it correctly returns **404 (not 403)** for other users' resources to avoid leaking
their existence.

The gap versus a layered, tested version is not "it doesn't work" — it's that **nothing is
structurally enforced or verified**. This is exactly the "runs" vs. "trusted & defensible"
contrast the assessment targets.

## Critical

- **C1 — Hardcoded JWT secret** (`main.py`, `SECRET = "ai-version-secret"`). Anyone with
  access to the source can forge a valid token for any user id, silently defeating the
  otherwise-correct per-user scoping. (Version B reads the secret from env/config.)

## High

- **H1 — No automated tests.** The invariants (single timer, ownership, stop-once) are
  asserted in code but never proven. Any future change can regress silently.
  (Version B has 22 tests covering these rules.)
- **H2 — All business logic inlined in route handlers.** Auth, rules, and SQL are mixed
  in each endpoint. Readable for a small app, but hard to reuse/test/change.
  (Version B separates routers / services / repositories.)
- **H3 — Wide-open CORS** (`allow_origins=["*"]`).
- **H4 — Single-timer rule enforced only in app code** (check-then-act race, no DB
  constraint), plus minor schema drift from the spec.

## Medium / Frontend

- **M1** — Unhandled `IntegrityError` and similar DB errors surface as 500s.
- **M2** — Deprecated `datetime.utcnow()` and `Query.get()` used.
- **M3** — Frontend loads React + Babel from a CDN and transpiles JSX in the browser —
  fine for a demo, not for production (slow, no build-time checks).
- **M4** — UI swallows some errors silently / via `alert`.
- **M5** — JWT stored in `localStorage` (XSS-exposed); acceptable for a demo, worth noting.

## A vs. a layered/tested version (for Comparison.md)

| Aspect | Version A (AI) | Version B (layered + TDD) |
|---|---|---|
| Works / looks good | ✅ | ✅ |
| Separation of concerns | ❌ logic in handlers | ✅ routers/services/repos |
| Automated tests | ❌ none | ✅ 22 tests |
| Secret management | ❌ hardcoded | ✅ env/config |
| Invariants enforced | app code only | app code (+ recommended DB constraint) |
| Defensible in interview | harder | easier (small, explained units) |

## Conclusion

Version A demonstrates that good prompting yields a polished, working app quickly. What it
lacks — and what version B supplies — is **structure, automated verification, and security
hardening**: the engineering judgement that turns "it runs" into "I can trust, change, and
defend it."
