# Focus Time Tracking — Technical Assessment

A full-stack focus time-tracking app with productivity reporting, delivered in two
independent versions of the same product:

| | Stack | Architecture | Tests |
|---|---|---|---|
| **`version-B-Manual`** | React (Vite) + FastAPI + SQLAlchemy + SQLite | Layered: routers / services / repositories / models | 22 pytest tests |
| **`version-A-AI`** | React (single HTML/CDN) + FastAPI (single file) + SQLite | Flat: logic inside route handlers | none |

See [`Comparison.md`](./Comparison.md) for the side-by-side analysis and
[`PROMPT_HISTORY.md`](./PROMPT_HISTORY.md) for how the AI version was driven.
Design, plan and the code-review report live under
[`docs/superpowers/`](./docs/superpowers) (`specs/`, `plans/`, `reviews/`).

The database is SQLite for an easy demo. Because all access goes through SQLAlchemy,
switching to PostgreSQL is only a connection-string change.

---

## Run `version-B-Manual`

### Backend (http://localhost:8000)

```bash
cd version-B-Manual/backend
python -m venv .venv
.venv\Scripts\activate            # Windows  (use: source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run the tests:

```bash
pytest -q
```

Interactive API docs: http://localhost:8000/docs

### Frontend (http://localhost:5173)

```bash
cd version-B-Manual/frontend
npm install
npm run dev
```

The dev server proxies `/api` to the backend, so start the backend first.

---

## Run `version-A-AI`

### Backend (http://localhost:8000)

```bash
cd version-A-AI/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

Open `version-A-AI/frontend/index.html` in a browser (it calls the backend at
`http://localhost:8000` directly). Run only one backend at a time, or change the port.

---

## Features (both versions)

- Register / login (JWT)
- Create projects and tasks
- Start / stop a focus timer (one running timer per user)
- Productivity report: total time per project and per day
- (version B) Optional Slack notification when a session ends
