# Code Review — version-B-Manual Backend

> Produced by the Superpowers `code-reviewer` step (read-only review of the
> carefully-engineered version against the spec and plan). Date: 2026-06-16.

**Scope:** `version-B-Manual/backend`
**Reviewed against:** `docs/superpowers/specs/2026-06-16-focus-time-tracking-design.md`,
`docs/superpowers/plans/2026-06-16-focus-time-tracking.md`

## Overall assessment

Clean, disciplined layered implementation that faithfully realizes the spec. Routers are
thin HTTP adapters, services own business rules, repositories own all SQL, `core/`
isolates config/security/db. Per-user scoping is consistent and "treat someone else's
resource as 404" is implemented correctly. **No Critical defects.** Headline items: an
insecure default JWT secret that fails open (H1), and the single-running-timer rule being
enforced only in app code (H2). Remaining items are Medium/Low polish and test-coverage
gaps around ownership/auth-failure paths.

Done well:
- Strict layering (no SQL in services/routers, no rules in repositories).
- Pydantic response models prevent leaking `hashed_password`.
- Ownership-as-404 avoids existence leakage.
- Slack notifier is a safe no-op when unconfigured and is invoked *after* the DB commit.

## High

- **H1 — Insecure default `jwt_secret` fails open** (`app/core/config.py`). If started
  without `JWT_SECRET`, the app signs tokens with a public default → anyone can forge
  tokens. Recommendation: fail closed outside dev (raise on startup if the default is
  used), or at least document loudly.
- **H2 — Single-timer rule: check-then-act race + latent 500**
  (`app/services/time_entry_service.py`, `app/repositories/time_entry_repository.py`).
  The check (`get_running_for_user`) and insert (`create`) aren't atomic, so two
  concurrent `start` requests can both succeed; afterward `scalar_one_or_none()` raises
  on every `start` (500). Recommendation: a partial unique index
  (`user_id WHERE stopped_at IS NULL`) and/or use `.first()` defensively.

## Medium

- **M1** — `int(subject)` in `app/api/deps.py` can raise 500 on a validly-signed token
  with a non-numeric `sub`; wrap and return 401 (defense-in-depth).
- **M2** — Slack `requests.post(timeout=5)` runs synchronously in `stop()`; use
  `BackgroundTasks` so the response isn't blocked.
- **M3** — Datetimes are serialized naive (no `Z`/offset); clients may parse as local
  time. Attach UTC marker on output or document the contract.
- **M4** — CORS is wildcard (`*`); tighten to known origins via config before non-demo use.
- **M5** — No password length policy; bcrypt truncates at 72 bytes. Add `min_length`/`max_length`.

## Low

- **L1** — Missing auth returns 403 (HTTPBearer default) but spec §6 says 401.
- **L2** — `_utcnow` duplicated in models and service; extract to one place.
- **L3** — `passlib 1.7.4` + `bcrypt 4.2.1` emits a noisy version-read warning; pin `bcrypt<4.1`.
- **L4** — Report query could also assert `Project.owner_id == user_id` (defense-in-depth).
- **L5** — Day buckets use `started_at`; sessions crossing midnight aren't split (document as intentional).

## Test coverage gaps

1. Stopping another user's entry → 404 (untested).
2. Starting a timer on another user's task → 404 (untested).
3. Invalid/malformed/expired bearer token → 401 (only missing-header is tested).
4. Reports scoped across users (user B excludes user A).
5. Duration accuracy (currently only `>= 0`; use `freezegun` to assert a concrete value).
6. Slack failure branch (`RequestException → False`).
7. Start-after-stop succeeds.
8. Invalid email format → 422.

## Priorities

Before any non-demo use: **H1** and **H2**, then the ownership/auth test gaps (#1–#3).
For the assessment, these findings are themselves evidence of a systematic AI-assisted
review step — they are documented here rather than all fixed, to keep the demo scope tight.
