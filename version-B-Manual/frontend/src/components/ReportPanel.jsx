// Shows the productivity summary as simple bar charts. Reloads whenever
// `reloadKey` changes (i.e. after a timer is stopped).
import { useEffect, useState } from "react";
import { api } from "../api.js";

function formatHm(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return `${h}h ${m}m`;
}

function BarList({ items, labelKey }) {
  const max = Math.max(1, ...items.map((i) => i.total_seconds));
  return (
    <div className="bars">
      {items.map((item, idx) => (
        <div className="bar-row" key={idx}>
          <span className="bar-label">{item[labelKey]}</span>
          <span className="bar-track">
            <span
              className="bar-fill"
              style={{ width: `${(item.total_seconds / max) * 100}%` }}
            />
          </span>
          <span className="bar-value">{formatHm(item.total_seconds)}</span>
        </div>
      ))}
      {items.length === 0 && <p className="muted">No data yet</p>}
    </div>
  );
}

export default function ReportPanel({ reloadKey }) {
  const [summary, setSummary] = useState({ by_project: [], by_day: [] });

  useEffect(() => {
    api.summary().then(setSummary).catch(() => {});
  }, [reloadKey]);

  return (
    <div className="report">
      <div>
        <h3>By project</h3>
        <BarList items={summary.by_project} labelKey="project_name" />
      </div>
      <div>
        <h3>By day</h3>
        <BarList items={summary.by_day} labelKey="day" />
      </div>
    </div>
  );
}
