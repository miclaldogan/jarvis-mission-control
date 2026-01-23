import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, buildUrl } from "@shared/routes";
import { type InsertMission, type Mission } from "@shared/schema";

// GET /api/missions
export function useMissions() {
  return useQuery({
    queryKey: [api.missions.list.path],
    queryFn: async () => {
      const res = await fetch(api.missions.list.path, { credentials: "include" });
      if (!res.ok) throw new Error('Failed to fetch missions');
      return api.missions.list.responses[200].parse(await res.json());
    },
  });
}

// POST /api/missions
export function useCreateMission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: InsertMission) => {
      const validated = api.missions.create.input.parse(data);
      const res = await fetch(api.missions.create.path, {
        method: api.missions.create.method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(validated),
        credentials: "include",
      });
      if (!res.ok) throw new Error('Failed to create mission');
      return api.missions.create.responses[201].parse(await res.json());
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [api.missions.list.path] }),
  });
}

// POST /api/missions/bulk
export function useBulkCreateMissions() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (count: number) => {
      const res = await fetch(api.missions.bulkCreate.path, {
        method: api.missions.bulkCreate.method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count }),
        credentials: "include",
      });
      if (!res.ok) throw new Error('Failed to bulk create missions');
      return api.missions.bulkCreate.responses[201].parse(await res.json());
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [api.missions.list.path] }),
  });
}
