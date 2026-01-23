import { useQuery } from "@tanstack/react-query";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

interface ContextData {
  context_id: string;
  observed_at: string;
  weather: {
    city: string;
    temp_c: number;
    condition: string;
  } | null;
  github: {
    owner: string;
    repo: string;
    open_issues: number;
    open_prs: number;
  } | null;
  news: Array<{
    title: string;
    url: string;
  }>;
  exchange: {
    base: string;
    rates: Record<string, number>;
  } | null;
  trending: Array<{
    title: string;
    url: string;
  }>;
  traffic: {
    origin: { lat: number; lon: number };
    destination: { lat: number; lon: number };
    eta_minutes: number;
  } | null;
  sources_ok: string[];
  sources_failed: Array<{ source: string; error: string }>;
  sources_skipped: Array<{ source: string; reason: string }>;
}

// GET /api/v1/context
export function useContextItems() {
  return useQuery({
    queryKey: ["context"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/v1/context?refresh=true`);
      if (!res.ok) throw new Error("Failed to fetch context");
      const json = await res.json();
      return json.data as ContextData;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });
}
