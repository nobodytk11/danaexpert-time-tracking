// Single place that knows how to talk to the backend. Every call goes through
// `request`, which attaches the JWT (if present) and parses errors consistently.

const TOKEN_KEY = "tt_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function request(path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`/api${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `Request failed (${res.status})`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  register: (email, password) =>
    request("/auth/register", { method: "POST", body: { email, password } }),
  login: (email, password) =>
    request("/auth/login", { method: "POST", body: { email, password } }),

  listProjects: () => request("/projects"),
  createProject: (name) => request("/projects", { method: "POST", body: { name } }),

  listTasks: (projectId) => request(`/projects/${projectId}/tasks`),
  createTask: (projectId, title) =>
    request(`/projects/${projectId}/tasks`, { method: "POST", body: { title } }),

  startTimer: (taskId) =>
    request("/time-entries/start", { method: "POST", body: { task_id: taskId } }),
  stopTimer: (entryId) =>
    request(`/time-entries/${entryId}/stop`, { method: "POST" }),
  listEntries: () => request("/time-entries"),

  summary: () => request("/reports/summary"),
};
