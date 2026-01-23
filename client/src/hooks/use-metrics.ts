import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@shared/routes";
import { type InsertSystemMetric, type SystemMetric } from "@shared/schema";

// GET /api/metrics
export function useMetrics() {
  return useQuery({
    queryKey: [api.metrics.list.path],
    queryFn: async () => {
      const res = await fetch(api.metrics.list.path, { credentials: "include" });
      if (!res.ok) throw new Error('Failed to fetch metrics');
      return api.metrics.list.responses[200].parse(await res.json());
    },
    // Poll metrics every 2 seconds for that "live dashboard" feel
    refetchInterval: 2000, 
  });
}

// POST /api/metrics
export function useUpdateMetric() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: InsertSystemMetric) => {
      const validated = api.metrics.update.input.parse(data);
      const res = await fetch(api.metrics.update.path, {
        method: api.metrics.update.method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(validated),
        credentials: "include",
      });
      if (!res.ok) throw new Error('Failed to update metric');
      return api.metrics.update.responses[200].parse(await res.json());
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [api.metrics.list.path] }),
  });
}
