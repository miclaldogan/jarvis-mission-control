import { useQuery } from "@tanstack/react-query";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";


type EnvelopeOk<T> = {
  ok: true;
  data: T;
  meta: { request_id: string; ts: string };
};

type EnvelopeErr = {
  ok: false;
  data: null;
  meta: { request_id: string; ts: string };
  error: { code: string; message: string; details?: Record<string, unknown> };
};

type Envelope<T> = EnvelopeOk<T> | EnvelopeErr;

export type SystemVitalsData = {
  cpu: { percent: number; cores: number };
  memory: { percent: number; used_gb: number; total_gb: number };
  network: { bytes_sent: number; bytes_recv: number };
  disk: { percent: number; used_gb: number; total_gb: number };
};

export type SystemVitalsUI = {
  cpu: number;      // percent
  memory: number;   // percent
  disk: number;     // percent
  network: number;  // bytes_recv (UI’de tek sayı isteniyor diye)
  timestamp: string;
  raw: SystemVitalsData;
};

function toUI(data: SystemVitalsData, ts: string): SystemVitalsUI {
  return {
    cpu: data.cpu.percent,
    memory: data.memory.percent,
    disk: data.disk.percent,
    network: data.network.bytes_recv,
    timestamp: ts,
    raw: data,
  };
}

async function fetchSystemVitals(): Promise<SystemVitalsUI> {
  const res = await fetch(`${API_BASE}/api/v1/system/vitals`);

  // HTTP error -> throw (react-query isError)
  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    try {
      const body = (await res.json()) as Envelope<unknown>;
      if (!body.ok) msg = `${body.error.code}: ${body.error.message}`;
    } catch {
      // ignore parse errors
    }
    throw new Error(msg);
  }

  const json = (await res.json()) as Envelope<SystemVitalsData>;
  if (!json.ok) {
    throw new Error(`${json.error.code}: ${json.error.message}`);
  }

  return toUI(json.data, json.meta.ts);
}

export function useSystemVitals() {
  return useQuery({
    queryKey: ["system-vitals"],
    queryFn: fetchSystemVitals,
    refetchInterval: 2500,
    staleTime: 2000,
  });
}
