import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

interface Mission {
  id: number;
  title: string;
  priority: "CRITICAL" | "HIGH" | "NORMAL" | "LOW";
  category: "SYSTEM" | "RECON" | "ENCRYPTION" | "DEFENSE";
  status?: "PENDING" | "IN_PROGRESS" | "COMPLETED" | "FAILED";
  isGlitched?: boolean;
  createdAt?: string;
}

interface SyntheticTask {
  id: number;
  title: string;
  priority: string;
  status: string;
}

// GET /api/v1/synthetic/tasks - Use synthetic tasks as missions
export function useMissions() {
  return useQuery({
    queryKey: ["missions"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/v1/synthetic/tasks?n=50&seed=42`);
      if (!res.ok) throw new Error("Failed to fetch missions");
      const json = await res.json();
      const tasks = json.data.tasks as SyntheticTask[];
      
      // Transform synthetic tasks to match Mission interface
      return tasks.map((task, idx) => ({
        id: task.id,
        title: task.title,
        priority: task.priority as any,
        category: (idx % 4 === 0 ? "SYSTEM" : idx % 4 === 1 ? "RECON" : idx % 4 === 2 ? "ENCRYPTION" : "DEFENSE") as any,
        status: task.status as any,
        isGlitched: Math.random() > 0.9,
        createdAt: new Date().toISOString(),
      })) as Mission[];
    },
  });
}

// POST /api/missions - Mock create (not supported by FastAPI yet)
export function useCreateMission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Omit<Mission, "id">) => {
      // Mock implementation - just add to local cache
      const newMission: Mission = {
        ...data,
        id: Date.now(),
        createdAt: new Date().toISOString(),
      };
      return newMission;
    },
    onSuccess: (newMission) => {
      queryClient.setQueryData(["missions"], (old: Mission[] = []) => [
        newMission,
        ...old,
      ]);
    },
  });
}

// POST /api/missions/bulk - Use synthetic tasks endpoint
export function useBulkCreateMissions() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (count: number) => {
      const res = await fetch(
        `${API_BASE}/api/v1/synthetic/tasks?n=${Math.min(count, 1000)}&seed=${Date.now()}`
      );
      if (!res.ok) throw new Error("Failed to bulk create missions");
      return { message: `Generated ${count} tasks`, count };
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["missions"] }),
  });
}
