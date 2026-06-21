import type { RunState } from "@/types/simulation";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function createRun(name = "AI 南大默认模拟"): Promise<RunState> {
  const response = await fetch(`${API_BASE}/api/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!response.ok) throw new Error(`Failed to create run: ${response.status}`);
  return response.json();
}

export async function getRunState(runId: string): Promise<RunState> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}/state`);
  if (!response.ok) throw new Error(`Failed to load state: ${response.status}`);
  return response.json();
}
