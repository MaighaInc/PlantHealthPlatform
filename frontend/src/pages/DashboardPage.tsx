import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, Plant, SystemStatus } from "./api/client";

export function DashboardPage() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [plants, setPlants] = useState<Plant[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [liveSeq, setLiveSeq] = useState<number | null>(null);

  useEffect(() => {
    Promise.all([api.status(), api.plants()])
      .then(([s, p]) => {
        setStatus(s);
        setPlants(p);
      })
      .catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    const es = new EventSource("/api/stream/events");
    es.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data) as { seq?: number };
        if (typeof data.seq === "number") setLiveSeq(data.seq);
      } catch {
        /* ignore */
      }
    };
    es.onerror = () => {
      /* EventSource retries; keep last seq */
    };
    return () => es.close();
  }, []);

  return (
    <section>
      <h2>Dashboard</h2>
      {error && <p className="err">{error}</p>}
      {status && (
        <p>
          System <strong>{status.status}</strong> · DB {status.database} · mode{" "}
          {status.mode}
          {liveSeq !== null ? ` · live #${liveSeq}` : ""}
        </p>
      )}
      <ul>
        {plants.map((p) => (
          <li key={p.id}>
            <Link to={`/plants/${p.id}`}>{p.name}</Link>
            {p.variety ? ` (${p.variety})` : ""}
          </li>
        ))}
      </ul>
      {!plants.length && !error && <p>No plants yet — create via API.</p>}
    </section>
  );
}
