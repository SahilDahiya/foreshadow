import type { Scene, SceneSummary } from "../shared/scene";

// The playable scenes published by library/ (`library scenes`, then `library publish`).
const BASE = "/data/library/scenes";

export async function sceneCatalogue(): Promise<SceneSummary[]> {
  const response = await fetch(`${BASE}/index.json`);
  return response.ok ? ((await response.json()) as SceneSummary[]) : [];
}

export async function loadScene(id: string): Promise<Scene> {
  const response = await fetch(`${BASE}/${encodeURIComponent(id)}.json`);
  if (!response.ok) throw new Error(`scene ${id}: ${response.status}`);
  return (await response.json()) as Scene;
}
