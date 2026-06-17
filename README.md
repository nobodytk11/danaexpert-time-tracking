# Focus Time Tracking — Technical Assessment

A full-stack focus time-tracking app with productivity reporting, delivered in two
independent versions of the same product:


|                        | Stack                                                    | Architecture                                        | Tests           |
| ---------------------- | -------------------------------------------------------- | --------------------------------------------------- | --------------- |
| `**version-B-Manual**` | React (Vite) + FastAPI + SQLAlchemy + SQLite             | Layered: routers / services / repositories / models | 22 pytest tests |
| `**version-A-AI**`     | React (single HTML/CDN) + FastAPI (single file) + SQLite | Flat: logic inside route handlers                   | none            |


See `[Comparison.md](./Comparison.md)` for the side-by-side analysis and
`[PROMPT_HISTORY.md](./PROMPT_HISTORY.md)` for how the AI version was driven.
Design, plan and the code-review report live under
`[docs/superpowers/](./docs/superpowers)` (`specs/`, `plans/`, `reviews/`).

The database is SQLite for an easy demo. Because all access goes through SQLAlchemy,
switching to PostgreSQL is only a connection-string change.

---

## Demo both versions at once (4 ports)

Run everything from the repo root:

```bat
scripts\demo.bat
```

Stop all demo servers:

```bat
scripts\stop-demo.bat
```

| Service | URL |
|---|---|
| **Version A** — API | http://localhost:8100 |
| **Version A** — Frontend | http://localhost:5500 |
| **Version B** — API | http://localhost:8001 |
| **Version B** — Frontend | http://localhost:5173 |

API docs: [A /docs](http://localhost:8100/docs) · [B /docs](http://localhost:8001/docs)

The script creates `.venv` and runs `npm install` on first use if needed.

---

## Run `version-B-Manual`

### Backend (http://localhost:8001)

```bash
cd version-B-Manual/backend
python -m venv .venv
.venv\Scripts\activate            # Windows  (use: source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Run the tests:

```bash
pytest -q
```

Interactive API docs: http://localhost:8001/docs

### Frontend (http://localhost:5173)

```bash
cd version-B-Manual/frontend
npm install
npm run dev
```

The dev server proxies `/api` to the backend on port **8001**, so start the backend first.

---

## Run `version-A-AI`

### Backend (http://localhost:8100) — API only

```bash
cd version-A-AI/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8100
```

### Frontend (http://localhost:5500)

In a second terminal:

```bash
cd version-A-AI/frontend
python -m http.server 5500
```

Open **http://localhost:5500** in your browser (do not open `index.html` via `file://`).
The UI calls the API at **http://localhost:8100**.

---

## Features (both versions)

- Register / login (JWT)
- Create projects and tasks
- Start / stop a focus timer (one running timer per user)
- Productivity report: total time per project and per day
- (version B) Optional Slack notification when a session ends

