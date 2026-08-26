import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, Plant, SystemStatus } from "./api/client";

export function DashboardPage() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [plants, setPlants] = useState<Plant[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.status(), api.plants()])
      .then(([s, p]) => {
        setStatus(s);
        setPlants(p);
      })
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <section>
      <h2>Dashboard</h2>
      {error && <p className="err">{error}</p>}
      {status && (
        <p>
          System <strong>{status.status}</strong> · DB {status.database} · mode{" "}
          {status.mode}
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
