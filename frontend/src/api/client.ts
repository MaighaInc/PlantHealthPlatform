export type Plant = { id: number; name: string; variety: string | null };
export type SystemStatus = { status: string; database: string; mode: string };
export type IrrigationEvent = {
  id: number;
  plant_id: number | null;
  water: boolean;
  reason: string;
  source: string;
};
export type MlModel = {
  id: number;
  name: string;
  version: string;
  format: string;
  artifact: string;
};

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${path} → ${res.status}`);
  return res.json() as Promise<T>;
}

export const api = {
  status: () => getJson<SystemStatus>("/api/system/status"),
  plants: () => getJson<Plant[]>("/api/plants"),
  plant: (id: number) => getJson<Plant>(`/api/plants/${id}`),
  health: (id: number) =>
    getJson<{ status: string; confidence: number; model_version?: string }>(
      `/api/plants/${id}/health`
    ),
  irrigationEvents: () => getJson<IrrigationEvent[]>("/api/irrigation/events"),
  models: () => getJson<MlModel[]>("/api/models"),
};
