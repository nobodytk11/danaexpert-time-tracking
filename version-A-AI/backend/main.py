"""Focus Time Tracking API - Version A (AI-generated style).

This is the kind of single-file FastAPI app an AI coding assistant typically emits
when asked to "build the whole thing": everything (models, schemas, auth, business
logic and routes) lives in one module, with the logic written directly inside the
route handlers. It works, but it mixes concerns and has no automated tests.

Contrast this with version-B-Manual, which splits the same features into
routers / services / repositories / models layers and is built test-first.
"""
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    func,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# --- config / db ---
SECRET = "ai-version-secret"
ALGO = "HS256"
engine = create_engine(
    "sqlite:///./timetracking_a.db", connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer()


# --- models ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String)
    is_done = Column(Boolean, default=False)


class TimeEntry(Base):
    __tablename__ = "time_entries"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)


Base.metadata.create_all(engine)


# --- schemas ---
class RegisterIn(BaseModel):
    email: EmailStr
    password: str


class ProjectIn(BaseModel):
    name: str


class TaskIn(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str | None = None
    is_done: bool | None = None


class StartIn(BaseModel):
    task_id: int


app = FastAPI(title="Focus Time Tracking API (version A - AI)")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


def db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), s=Depends(db)):
    try:
        payload = jwt.decode(creds.credentials, SECRET, algorithms=[ALGO])
        uid = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(401, "Invalid token")
    user = s.query(User).get(uid)
    if not user:
        raise HTTPException(401, "Invalid token")
    return user


@app.post("/auth/register")
def register(data: RegisterIn, s=Depends(db)):
    if s.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already registered")
    u = User(email=data.email, password=pwd.hash(data.password))
    s.add(u)
    s.commit()
    return {"id": u.id, "email": u.email}


@app.post("/auth/login")
def login(data: RegisterIn, s=Depends(db)):
    u = s.query(User).filter(User.email == data.email).first()
    if not u or not pwd.verify(data.password, u.password):
        raise HTTPException(401, "Incorrect email or password")
    token = jwt.encode(
        {"sub": str(u.id), "exp": datetime.utcnow() + timedelta(days=1)}, SECRET, ALGO
    )
    return {"access_token": token, "token_type": "bearer"}


@app.get("/projects")
def list_projects(user=Depends(current_user), s=Depends(db)):
    rows = s.query(Project).filter(Project.owner_id == user.id).all()
    return [{"id": p.id, "name": p.name} for p in rows]


@app.post("/projects")
def create_project(data: ProjectIn, user=Depends(current_user), s=Depends(db)):
    p = Project(owner_id=user.id, name=data.name)
    s.add(p)
    s.commit()
    return {"id": p.id, "name": p.name}


@app.get("/projects/{pid}/tasks")
def list_tasks(pid: int, user=Depends(current_user), s=Depends(db)):
    p = s.query(Project).filter(Project.id == pid, Project.owner_id == user.id).first()
    if not p:
        raise HTTPException(404, "Project not found")
    rows = s.query(Task).filter(Task.project_id == pid).all()
    return [
        {"id": t.id, "title": t.title, "project_id": t.project_id, "is_done": t.is_done}
        for t in rows
    ]


@app.post("/projects/{pid}/tasks")
def add_task(pid: int, data: TaskIn, user=Depends(current_user), s=Depends(db)):
    p = s.query(Project).filter(Project.id == pid, Project.owner_id == user.id).first()
    if not p:
        raise HTTPException(404, "Project not found")
    t = Task(project_id=pid, title=data.title)
    s.add(t)
    s.commit()
    return {"id": t.id, "title": t.title, "project_id": t.project_id, "is_done": t.is_done}


def _owned_task(tid, user, s):
    t = (
        s.query(Task)
        .join(Project, Task.project_id == Project.id)
        .filter(Task.id == tid, Project.owner_id == user.id)
        .first()
    )
    if not t:
        raise HTTPException(404, "Task not found")
    return t


@app.patch("/tasks/{tid}")
def update_task(tid: int, data: TaskUpdate, user=Depends(current_user), s=Depends(db)):
    t = _owned_task(tid, user, s)
    if data.title is not None:
        t.title = data.title
    if data.is_done is not None:
        t.is_done = data.is_done
    s.commit()
    return {"id": t.id, "title": t.title, "project_id": t.project_id, "is_done": t.is_done}


@app.delete("/tasks/{tid}")
def delete_task(tid: int, user=Depends(current_user), s=Depends(db)):
    t = _owned_task(tid, user, s)
    s.query(TimeEntry).filter(TimeEntry.task_id == tid).delete()
    s.delete(t)
    s.commit()
    return {"ok": True}


@app.delete("/projects/{pid}")
def delete_project(pid: int, user=Depends(current_user), s=Depends(db)):
    p = s.query(Project).filter(Project.id == pid, Project.owner_id == user.id).first()
    if not p:
        raise HTTPException(404, "Project not found")
    task_ids = [t.id for t in s.query(Task).filter(Task.project_id == pid).all()]
    if task_ids:
        s.query(TimeEntry).filter(TimeEntry.task_id.in_(task_ids)).delete(synchronize_session=False)
    s.query(Task).filter(Task.project_id == pid).delete()
    s.delete(p)
    s.commit()
    return {"ok": True}


@app.post("/time-entries/start")
def start(data: StartIn, user=Depends(current_user), s=Depends(db)):
    task = (
        s.query(Task)
        .join(Project, Task.project_id == Project.id)
        .filter(Task.id == data.task_id, Project.owner_id == user.id)
        .first()
    )
    if not task:
        raise HTTPException(404, "Task not found")
    running = (
        s.query(TimeEntry)
        .filter(TimeEntry.user_id == user.id, TimeEntry.stopped_at.is_(None))
        .first()
    )
    if running:
        raise HTTPException(400, "A timer is already running")
    e = TimeEntry(user_id=user.id, task_id=data.task_id)
    s.add(e)
    s.commit()
    return {"id": e.id, "task_id": e.task_id, "stopped_at": None, "duration_seconds": None}


@app.post("/time-entries/{eid}/stop")
def stop(eid: int, user=Depends(current_user), s=Depends(db)):
    e = s.query(TimeEntry).filter(TimeEntry.id == eid, TimeEntry.user_id == user.id).first()
    if not e:
        raise HTTPException(404, "Entry not found")
    if e.stopped_at is not None:
        raise HTTPException(400, "Entry already stopped")
    e.stopped_at = datetime.utcnow()
    e.duration_seconds = int((e.stopped_at - e.started_at).total_seconds())
    s.commit()
    return {
        "id": e.id,
        "task_id": e.task_id,
        "stopped_at": e.stopped_at.isoformat(),
        "duration_seconds": e.duration_seconds,
    }


@app.get("/time-entries")
def entries(user=Depends(current_user), s=Depends(db)):
    rows = (
        s.query(TimeEntry)
        .filter(TimeEntry.user_id == user.id)
        .order_by(TimeEntry.started_at.desc())
        .all()
    )
    return [
        {
            "id": e.id,
            "task_id": e.task_id,
            "stopped_at": e.stopped_at.isoformat() if e.stopped_at else None,
            "duration_seconds": e.duration_seconds,
        }
        for e in rows
    ]


@app.get("/reports/summary")
def summary(user=Depends(current_user), s=Depends(db)):
    by_project = (
        s.query(Project.id, Project.name, func.coalesce(func.sum(TimeEntry.duration_seconds), 0))
        .join(Task, Task.project_id == Project.id)
        .join(TimeEntry, TimeEntry.task_id == Task.id)
        .filter(TimeEntry.user_id == user.id, TimeEntry.duration_seconds.isnot(None))
        .group_by(Project.id, Project.name)
        .all()
    )
    day = func.date(TimeEntry.started_at)
    by_day = (
        s.query(day, func.coalesce(func.sum(TimeEntry.duration_seconds), 0))
        .filter(TimeEntry.user_id == user.id, TimeEntry.duration_seconds.isnot(None))
        .group_by(day)
        .all()
    )
    return {
        "by_project": [
            {"project_id": r[0], "project_name": r[1], "total_seconds": int(r[2])}
            for r in by_project
        ],
        "by_day": [{"day": str(r[0]), "total_seconds": int(r[1])} for r in by_day],
    }


@app.get("/")
def root():
    return {"app": "Focus Time Tracking API (version A - AI)", "docs": "/docs"}
