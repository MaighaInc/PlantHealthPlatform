import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";

export function PlantDetailPage() {
  const { id } = useParams();
  const plantId = Number(id);
  const [name, setName] = useState("");
  const [health, setHealth] = useState<{ status: string; confidence: number } | null>(
    null
  );

  useEffect(() => {
    if (!plantId) return;
    api.plant(plantId).then((p) => setName(p.name));
    api.health(plantId).then(setHealth);
  }, [plantId]);

  return (
    <section>
      <h2>Plant {name || plantId}</h2>
      {health && (
        <p>
          Health: <strong>{health.status}</strong> (confidence{" "}
          {health.confidence.toFixed(2)})
        </p>
      )}
    </section>
  );
}
