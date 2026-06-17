# Focus Time Tracking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans / subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Build a full-stack focus time-tracking app in two versions (clean manual + AI-style) with truthful comparison and interview-prep docs.

**Architecture:** React SPA -> FastAPI. version-B uses routers/services/repositories/models layers; version-A uses the flatter shape AI agents emit. SQLite via SQLAlchemy, Postgres-ready.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, passlib[bcrypt], python-jose, pytest; React (Vite).

---

## Phase 1 — version-B-Manual backend (TDD)

### Task 1: Project scaffold & config

**Files:** `version-B-Manual/backend/app/core/config.py`, `requirements.txt`, `app/main.py`

- [x] Create venv, install deps, freeze `requirements.txt`.
- [x] `config.py`: settings (DB URL, JWT secret, token expiry, SLACK_WEBHOOK_URL) via env with defaults.
- [x] `main.py`: FastAPI app + CORS + router includes.

### Task 2: Database & models

**Files:** `app/core/database.py`, `app/models/*.py`

- [x] `database.py`: SQLAlchemy engine/session, `Base`, `get_db` dependency.
- [x] Models: User, Project, Task, TimeEntry with relationships & FKs.

### Task 3: Security helpers (TDD)

**Files:** `app/core/security.py`, `tests/test_security.py`

- [x] RED: test password hash+verify round-trips; test JWT encode/decode returns subject.
- [x] GREEN: implement `hash_password`, `verify_password`, `create_access_token`, `decode_token`.

### Task 4: Auth service + endpoints (TDD)

**Files:** `app/services/auth_service.py`, `app/routers/auth.py`, `tests/test_auth.py`

- [x] RED: register creates user; duplicate email rejected; login returns token; bad password 401.
- [x] GREEN: implement service + repository + router.

### Task 5: Projects & tasks (TDD)

**Files:** `app/services/project_service.py`, `app/routers/projects.py`, `tests/test_projects.py`

- [x] RED: create/list projects scoped to user; create/list tasks; cannot see others' projects.
- [x] GREEN: implement.

### Task 6: Time entries (TDD)

**Files:** `app/services/time_entry_service.py`, `app/routers/time_entries.py`, `tests/test_time_entries.py`

- [x] RED: start creates running entry; cannot start second while one runs; stop sets duration; cannot stop already-stopped.
- [x] GREEN: implement, compute `duration_seconds` on stop.

### Task 7: Reporting (TDD)

**Files:** `app/services/report_service.py`, `app/routers/reports.py`, `tests/test_reports.py`

- [x] RED: summary groups total seconds by project and by day for the user only.
- [x] GREEN: implement aggregation query.

### Task 8: Slack notifier (TDD)

**Files:** `app/services/slack_notifier.py`, `tests/test_slack.py`

- [x] RED: no-op (returns False) when URL unset; posts payload when set (requests mocked).
- [x] GREEN: implement; call it from time-entry stop.

## Phase 2 — version-B-Manual frontend (React/Vite)

- [x] Vite React app, API client, auth (store token), pages: Login, Projects/Tasks, Timer, Report (with chart).

## Phase 3 — version-A-AI

- [x] Same features, single-file-ish FastAPI + a minimal React, AI-style (logic in handlers). Documented as such.

## Phase 4 — Docs

- [x] `Comparison.md` (truthful: time, quality, security, lessons).
- [x] `PROMPT_HISTORY.md` (truthful record of prompts used).
- [x] Root `README.md` with run instructions for both versions.

## Self-Review

- Spec coverage: auth, projects/tasks, time entries, reporting, Slack, two versions, docs — all mapped. ✓
- No placeholders: each task names files + behaviors. ✓
- Type consistency: `duration_seconds`, `stopped_at`, service names consistent across tasks. ✓

