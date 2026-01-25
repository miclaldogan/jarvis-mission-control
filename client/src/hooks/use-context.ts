import { useQuery } from "@tanstack/react-query";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

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

interface ContextHealthData {
  context_id: string;
  observed_at: string;
  freshness: Record<
    string,
    {
      last_updated: string;
      age_minutes: number;
      status: "fresh" | "stale" | "old";
    }
  >;
  anomalies: Array<{
    source: string;
    type: string;
    message: string;
    severity: "info" | "warning" | "critical";
  }>;
  anomaly_count: number;
  summary: {
    risk_level: "low" | "medium" | "high";
    energy_level: "low" | "medium" | "high";
    focus_score: number;
    overall_health: "good" | "fair" | "poor";
  };
  sources_status: {
    ok: string[];
    failed: string[];
    skipped: string[];
  };
}

// GET /api/v1/context
export function useContextItems(city?: string) {
  return useQuery({
    queryKey: ["context", city],
    queryFn: async () => {
      // When VITE_API_BASE_URL is empty (prod same-origin), new URL("/path") is invalid.
      // Use window.location.origin as base in that case.
      const base = API_BASE || window.location.origin;
      const makeUrl = (refresh: boolean) => {
        const url = new URL(`/api/v1/context`, base);
        url.searchParams.set("refresh", refresh ? "true" : "false");
        if (city) url.searchParams.set("city", city);
        return url;
      };

      // First try a cache-friendly read.
      // NOTE: We still benefit from server-side Redis caching (X-Cache HIT/MISS).
      // But we disable *browser* HTTP caching so a previous stale response (e.g.,
      // GitHub rate-limited showing 0) doesn't stick for max-age=600.
      const res = await fetch(makeUrl(false).toString(), { cache: "no-store" });
      if (!res.ok) throw new Error("Failed to fetch context");
      const json = await res.json();
      const data = json.data as ContextData;

      // If key sources are missing (e.g., GitHub), retry once with refresh=true.
      if (!data.github || !data.news || data.news.length === 0) {
        const res2 = await fetch(makeUrl(true).toString(), { cache: "no-store" });
        if (res2.ok) {
          const json2 = await res2.json();
          return json2.data as ContextData;
        }
      }

      return data;
    },
    refetchInterval: 10 * 60 * 1000, // Refresh every 10 minutes
  });
}

// GET /api/v1/context/health
export function useContextHealth() {
  return useQuery({
    queryKey: ["context-health"],
    queryFn: async () => {
      const base = API_BASE || window.location.origin;
      const url = new URL(`/api/v1/context/health`, base);
      const res = await fetch(url.toString());
      if (!res.ok) throw new Error("Failed to fetch context health");
      const json = await res.json();
      return json.data as ContextHealthData;
    },
    refetchInterval: 30 * 1000,
  });
}
