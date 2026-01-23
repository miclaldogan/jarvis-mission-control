import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

interface SystemMetric {
  id?: number;
  name: string;
  value: string;
  status: "NOMINAL" | "WARNING" | "CRITICAL" | "HIT" | "MISS";
}

interface FastAPIMetrics {
  cache_hit_total: number;
  cache_miss_total: number;
  http_requests_total: number;
}

// GET /api/v1/metrics - Transform to SystemMetric format
export function useMetrics() {
  return useQuery({
    queryKey: ["metrics"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/v1/metrics`);
      if (!res.ok) throw new Error("Failed to fetch metrics");
      const text = await res.text();
      
      // Parse Prometheus metrics
      const metrics: SystemMetric[] = [];
      const lines = text.split("\n").filter((line) => !line.startsWith("#") && line.trim());
      
      let cacheHit = 0;
      let cacheMiss = 0;
      let computeTime = 0;
      
      for (const line of lines) {
        if (line.includes("cache_hit_total")) {
          cacheHit = parseFloat(line.split(" ")[1] || "0");
        } else if (line.includes("cache_miss_total")) {
          cacheMiss = parseFloat(line.split(" ")[1] || "0");
        } else if (line.includes("http_request_duration_seconds_sum")) {
          computeTime = parseFloat(line.split(" ")[1] || "0") * 1000; // to ms
        }
      }
      
      const total = cacheHit + cacheMiss;
      const hitRate = total > 0 ? ((cacheHit / total) * 100).toFixed(1) : "0.0";
      
      metrics.push({
        id: 1,
        name: "Cache Hit Rate",
        value: `${hitRate}%`,
        status: parseFloat(hitRate) > 80 ? "HIT" : "WARNING",
      });
      
      metrics.push({
        id: 2,
        name: "Compute Time",
        value: `${Math.round(computeTime)}ms`,
        status: computeTime < 100 ? "NOMINAL" : "WARNING",
      });
      
      metrics.push({
        id: 3,
        name: "Active Nodes",
        value: "12/16",
        status: "WARNING",
      });
      
      return metrics;
    },
    refetchInterval: 2000, // Poll metrics every 2 seconds
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
