import { useEffect, useState } from "react";
import { api, MlModel } from "../api/client";

export function MlPage() {
  const [models, setModels] = useState<MlModel[]>([]);
  useEffect(() => {
    api.models().then(setModels).catch(() => setModels([]));
  }, []);
  return (
    <section>
      <h2>ML Models</h2>
      <ul>
        {models.map((m) => (
          <li key={m.id}>
            {m.name} v{m.version} ({m.format}) — {m.artifact}
          </li>
        ))}
      </ul>
    </section>
  );
}
