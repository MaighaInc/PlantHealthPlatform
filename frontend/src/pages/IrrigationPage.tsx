import { useEffect, useState } from "react";
import { api, IrrigationEvent } from "../api/client";

export function IrrigationPage() {
  const [events, setEvents] = useState<IrrigationEvent[]>([]);
  useEffect(() => {
    api.irrigationEvents().then(setEvents).catch(() => setEvents([]));
  }, []);
  return (
    <section>
      <h2>Irrigation</h2>
      <ul>
        {events.map((e) => (
          <li key={e.id}>
            {e.water ? "ON" : "OFF"} — {e.reason} ({e.source})
          </li>
        ))}
      </ul>
    </section>
  );
}
