// Start/Stop control for a single task.
// `runningEntry` is the user's currently running entry (or null), lifted to the
// dashboard so all timers agree on the single-timer-at-a-time rule.
import { useState } from "react";
import { api } from "../api.js";

export default function Timer({ taskId, runningEntry, onChange }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const isRunningThisTask = runningEntry && runningEntry.task_id === taskId;
  const anotherRunning = runningEntry && runningEntry.task_id !== taskId;

  async function start() {
    setBusy(true);
    setError("");
    try {
      await api.startTimer(taskId);
      await onChange();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function stop() {
    setBusy(true);
    setError("");
    try {
      await api.stopTimer(runningEntry.id);
      await onChange();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <span className="timer">
      {isRunningThisTask ? (
        <button className="stop" disabled={busy} onClick={stop}>
          Stop
        </button>
      ) : (
        <button disabled={busy || anotherRunning} onClick={start}>
          Start
        </button>
      )}
      {error && <span className="error small">{error}</span>}
    </span>
  );
}
