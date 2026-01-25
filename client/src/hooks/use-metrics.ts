import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

interface SystemMetric {
  id?: number;
  name: string;
  value: string;
  status: "NOMINAL" | "WARNING" | "CRITICAL" | "HIT" | "MISS";
  raw?: number; // Raw numeric value for calculations
}

interface FastAPIMetrics {
  cache_hit_total: number;
  cache_miss_total: number;
  http_requests_total: number;
}

// GET /metrics - Transform to SystemMetric format
export function useMetrics() {
  return useQuery({
    queryKey: ["metrics"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/metrics`);
      if (!res.ok) throw new Error("Failed to fetch metrics");
      const text = await res.text();
      
      // Parse Prometheus metrics
      const metrics: SystemMetric[] = [];
      const lines = text.split("\n").filter((line) => !line.startsWith("#") && line.trim());
      
      let cacheHit = 0;
      let cacheMiss = 0;
      let computeTime = 0;
      let requestCount = 0;
      
      for (const line of lines) {
        if (line.includes("cache_hits_total")) {
          cacheHit = parseFloat(line.split(" ")[1] || "0");
        } else if (line.includes("cache_misses_total")) {
          cacheMiss = parseFloat(line.split(" ")[1] || "0");
        } else if (line.includes("http_request_duration_seconds_sum")) {
          computeTime = parseFloat(line.split(" ")[1] || "0") * 1000; // to ms
        } else if (line.includes("http_requests_total")) {
          requestCount = parseFloat(line.split(" ")[1] || "0");
        }
      }
      
      const total = cacheHit + cacheMiss;
      const hitRate = total > 0 ? ((cacheHit / total) * 100).toFixed(1) : "0.0";
      const cacheStatus = total === 0 ? "MISS" : (parseFloat(hitRate) > 70 ? "HIT" : "MISS");
      
      metrics.push({
        id: 1,
        name: "Cache Hit Rate",
        value: `${hitRate}%`,
        status: cacheStatus,
        raw: parseFloat(hitRate),
      });
      
      metrics.push({
        id: 2,
        name: "Compute Time",
        value: `${Math.round(computeTime)}ms`,
        status: computeTime < 100 ? "NOMINAL" : computeTime < 500 ? "WARNING" : "CRITICAL",
        raw: computeTime,
      });
      
      metrics.push({
        id: 3,
        name: "Request Count",
        value: `${requestCount}`,
        status: "NOMINAL",
        raw: requestCount,
      });
      
      metrics.push({
        id: 4,
        name: "Cache Hits",
        value: `${cacheHit}`,
        status: "NOMINAL",
        raw: cacheHit,
      });
      
      metrics.push({
        id: 5,
        name: "Cache Misses",
        value: `${cacheMiss}`,
        status: cacheMiss > 0 ? "WARNING" : "NOMINAL",
        raw: cacheMiss,
      });
      
      return metrics;
    },
    refetchInterval: 2000, // Poll metrics every 2 seconds
  });
}

// Check Redis health
export function useRedisHealth() {
  return useQuery({
    queryKey: ["redis-health"],
    queryFn: async () => {
      try {
        const res = await fetch(`${API_BASE}/health`);
        const data = await res.json();
        return {
          connected: data.data?.redis === "connected" || false,
          status: data.data?.redis || "unknown",
        };
      } catch {
        return { connected: false, status: "error" };
      }
    },
    refetchInterval: 5000,
  });
}

// POST /api/metrics - Mock update (not supported by FastAPI)
export function useUpdateMetric() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: SystemMetric) => {
      // Mock implementation - just update local cache
      return data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["metrics"] }),
  });
}
