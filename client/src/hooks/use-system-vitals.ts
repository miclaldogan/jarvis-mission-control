import { useQuery } from "@tanstack/react-query";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

type EnvelopeOk<T> = {
  ok: true;
  data: T;
  meta: { request_id: string; ts: string };
};

type EnvelopeErr = {
  ok: false;
  data: null;
  meta: { request_id: string; ts: string };
  error: { code: string; message: string; details: Record<string, unknown> };
};

type Envelope<T> = EnvelopeOk<T> | EnvelopeErr;

// UI-friendly shape (issue’deki basit interface)
export interface SystemVitals {
  cpu: number;
  cpu_percent: number;
  memory: number;
  memory_percent: number;
  disk: number;
  disk_percent: number;
  network: number;
  network_sent_mbps: number;
  network_recv_mbps: number;
  timestamp: string;
}

function toUiVitals(json: Envelope<any>): SystemVitals {
  if (!json.ok) {
    throw new Error(json.error?.message || "Failed to fetch system vitals");
  }

  const d = json.data;

  return {
    cpu: Number(d?.cpu ?? 0),
    cpu_percent: Number(d?.cpu ?? 0),
    memory: Number(d?.memory ?? 0),
    memory_percent: Number(d?.memory ?? 0),
    disk: Number(d?.disk ?? 0),
    disk_percent: Number(d?.disk ?? 0),
    network: Number(d?.network ?? 0),
    network_sent_mbps: Number(d?.network_mb_sent ?? 0),
    network_recv_mbps: Number(d?.network_mb_recv ?? 0),
    timestamp: d?.timestamp ?? json.meta?.ts ?? new Date().toISOString(),
  };
}

async function fetchSystemVitals(): Promise<SystemVitals> {
  const res = await fetch(`${API_BASE}/api/v1/system/vitals`);
  const json = (await res.json()) as Envelope<any>;

  if (!res.ok) {
    // Backend err envelope dönüyor olabilir
    const msg = (json as any)?.error?.message || `HTTP ${res.status}`;
    throw new Error(msg);
  }

  return toUiVitals(json);
}

export function useSystemVitals() {
  return useQuery({
    queryKey: ["system-vitals"],
    queryFn: fetchSystemVitals,
    refetchInterval: 2500,
    staleTime: 2000,
    retry: 1,
  });
}
