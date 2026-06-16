# Focus Time Tracking — Design Spec

> Status: Approved (brainstormed interactively, Superpowers `brainstorming` skill)
> Date: 2026-06-16

## 1. Goal

A full-stack web application for tracking focused work sessions and reporting
productivity. Built in **two independent versions** of the same product to compare
AI-generated vs. carefully-structured engineering:

- `/version-A-AI` — produced maximally with AI agents.
- `/version-B-Manual` — clean, layered architecture, fully understood and defensible.

## 2. Users & Core Use Cases

A single type of user (a worker) who wants to:

1. Register / log in.
2. Create projects, and tasks under a project.
3. Start a timer when they begin focused work, stop it when done (a *time entry*).
4. See a productivity report: total focused hours per project and per day, plus a chart.
5. (Optional) Get a Slack notification when a session is completed.

Out of scope (YAGNI): teams/org accounts, roles/permissions, billing/invoicing,
mobile app, real-time collaboration.

## 3. Architecture

Classic client/server split.

```
React SPA  ──HTTP/JSON──>  FastAPI  ──>  Service layer  ──>  Repository  ──>  SQLite (SQLAlchemy)
                              │
                              └── Slack notifier (optional, no-op if unconfigured)
```

**version-B-Manual** uses a deliberate layered structure so each unit has one job:

- `routers/` — HTTP endpoints, request/response validation (Pydantic schemas). No business logic.
- `services/` — business rules (e.g. "a user can only stop their own running entry").
- `repositories/` — all database access via SQLAlchemy. No business rules.
- `models/` — SQLAlchemy ORM tables.
- `schemas/` — Pydantic request/response models.
- `core/` — config, security (JWT, password hashing), database session.

**version-A-AI** implements the same features but in the flatter, faster shape an
AI agent typically emits (logic and DB access mixed into route handlers). This
contrast is the point of the exercise and is summarised in `Comparison.md`.

## 4. Data Model (relational)

- **User**: `id`, `email` (unique), `hashed_password`, `created_at`.
- **Project**: `id`, `owner_id` -> User, `name`, `created_at`.
- **Task**: `id`, `project_id` -> Project, `title`, `is_done`, `created_at`.
- **TimeEntry**: `id`, `user_id` -> User, `task_id` -> Task, `started_at`,
  `stopped_at` (nullable while running), `duration_seconds` (computed on stop).

Relationships: User 1—N Project, Project 1—N Task, Task 1—N TimeEntry,
User 1—N TimeEntry. Foreign keys + indexes on owner/user columns.

Schema is portable to PostgreSQL: only the connection string changes; ORM models
and queries stay identical.

## 5. API (REST)

Auth (JWT bearer):
- `POST /auth/register` — {email, password} -> user
- `POST /auth/login` — {email, password} -> {access_token}

Projects / tasks (auth required):
- `GET/POST /projects`
- `GET/POST /projects/{id}/tasks`

Time tracking:
- `POST /time-entries/start` — {task_id} -> running entry
- `POST /time-entries/{id}/stop` — -> entry with duration
- `GET /time-entries` — list current user's entries

Reporting:
- `GET /reports/summary` — total seconds grouped by project and by day.

## 6. Error Handling

- Validation errors -> 422 (FastAPI/Pydantic default).
- Auth failures -> 401; accessing another user's data -> 404 (don't leak existence).
- Business-rule violations (e.g. starting a second timer while one runs, stopping an
  already-stopped entry) -> 400 with a clear message.

## 7. Security

- Passwords hashed with bcrypt (`passlib`). Never stored or returned in plaintext.
- JWT access tokens (`python-jose`), short expiry, signed with a secret from env/config.
- Every data query is scoped to the authenticated user.
- Slack webhook URL read from env; absent -> notifier is a safe no-op.

## 8. Testing

`version-B-Manual` is built test-first (pytest):
- Service-layer unit tests (auth, time-entry rules, reporting math).
- API integration tests using FastAPI `TestClient` against an in-memory SQLite DB.

## 9. Third-party Integration

Slack Incoming Webhook. On session stop, post a short message
("Finished <task> — <duration>"). If `SLACK_WEBHOOK_URL` is unset, the notifier
returns immediately without error, so the app always runs.

## 10. Tech Stack

- Backend: Python 3.11, FastAPI, SQLAlchemy, Pydantic, passlib[bcrypt], python-jose, pytest.
- Frontend: React (Vite), fetch-based API client, a small chart for the report.
- DB: SQLite (dev/demo), Postgres-ready.
