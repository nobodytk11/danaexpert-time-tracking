import { useEffect, useState } from "react";
import { api } from "../api.js";
import { useAuth } from "../context/AuthContext.jsx";
import Timer from "../components/Timer.jsx";
import ReportPanel from "../components/ReportPanel.jsx";

export default function DashboardPage() {
  const { logout } = useAuth();
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [newProject, setNewProject] = useState("");
  const [newTask, setNewTask] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const [runningEntry, setRunningEntry] = useState(null);

  async function refreshRunning() {
    const entries = await api.listEntries().catch(() => []);
    setRunningEntry(entries.find((e) => e.stopped_at === null) || null);
  }

  useEffect(() => {
    api.listProjects().then(setProjects).catch(() => {});
    refreshRunning();
  }, []);

  async function onTimerChange() {
    await refreshRunning();
    setReloadKey((k) => k + 1);
  }

  useEffect(() => {
    if (selectedProject) {
      api.listTasks(selectedProject.id).then(setTasks).catch(() => setTasks([]));
    } else {
      setTasks([]);
    }
  }, [selectedProject]);

  async function addProject(e) {
    e.preventDefault();
    if (!newProject.trim()) return;
    const created = await api.createProject(newProject.trim());
    setProjects((prev) => [...prev, created]);
    setNewProject("");
  }

  async function addTask(e) {
    e.preventDefault();
    if (!newTask.trim() || !selectedProject) return;
    const created = await api.createTask(selectedProject.id, newTask.trim());
    setTasks((prev) => [...prev, created]);
    setNewTask("");
  }

  return (
    <div className="layout">
      <header className="topbar">
        <strong>Focus Time Tracking</strong>
        <button className="link" onClick={logout}>
          Log out
        </button>
      </header>

      <main className="grid">
        <section className="card">
          <h2>Projects</h2>
          <form className="row" onSubmit={addProject}>
            <input
              placeholder="New project"
              value={newProject}
              onChange={(e) => setNewProject(e.target.value)}
            />
            <button type="submit">Add</button>
          </form>
          <ul className="list">
            {projects.map((p) => (
              <li
                key={p.id}
                className={selectedProject?.id === p.id ? "active" : ""}
                onClick={() => setSelectedProject(p)}
              >
                {p.name}
              </li>
            ))}
            {projects.length === 0 && <li className="muted">No projects yet</li>}
          </ul>
        </section>

        <section className="card">
          <h2>{selectedProject ? `Tasks · ${selectedProject.name}` : "Tasks"}</h2>
          {!selectedProject && <p className="muted">Select a project</p>}
          {selectedProject && (
            <>
              <form className="row" onSubmit={addTask}>
                <input
                  placeholder="New task"
                  value={newTask}
                  onChange={(e) => setNewTask(e.target.value)}
                />
                <button type="submit">Add</button>
              </form>
              <ul className="list">
                {tasks.map((t) => (
                  <li key={t.id}>
                    <span>{t.title}</span>
                    <Timer
                      taskId={t.id}
                      runningEntry={runningEntry}
                      onChange={onTimerChange}
                    />
                  </li>
                ))}
                {tasks.length === 0 && <li className="muted">No tasks yet</li>}
              </ul>
            </>
          )}
        </section>

        <section className="card wide">
          <h2>Productivity report</h2>
          <ReportPanel reloadKey={reloadKey} />
        </section>
      </main>
    </div>
  );
}
