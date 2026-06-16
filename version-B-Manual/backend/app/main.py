"""FastAPI application entry point: wires config, database and routers together."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.routers import auth, projects, reports, time_entries

# Create tables on startup. For a small app this is enough; a larger one would use
# Alembic migrations instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Focus Time Tracking API (version B - manual)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(time_entries.router)
app.include_router(reports.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
