import type {
  ConfigResponse,
  Digest,
  HistoryEntry,
  LogEntry,
  StatusResponse,
  WorkflowsResponse,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE_URL}/api${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store",
  });

  if (!resp.ok) {
    const body = await resp.text().catch(() => "");
    throw new ApiError(body || resp.statusText, resp.status);
  }
  return resp.json() as Promise<T>;
}

export const getToday = () => apiFetch<Digest>("/news/today");
export const getByDate = (date: string) => apiFetch<Digest>(`/news/date/${date}`);
export const getHistory = () => apiFetch<HistoryEntry[]>("/news/history");
export const getWorkflows = () => apiFetch<WorkflowsResponse>("/workflows");
export const getLogs = () => apiFetch<LogEntry[]>("/logs");
export const getStatus = () => apiFetch<StatusResponse>("/status");
export const getConfig = () => apiFetch<ConfigResponse>("/config");

export const runPipeline = (opts: { skip_send?: boolean; dry_run?: boolean }) =>
  apiFetch<{ status: string }>("/run", { method: "POST", body: JSON.stringify(opts) });

export const resendDigest = () => apiFetch<{ status: string }>("/send", { method: "POST" });
