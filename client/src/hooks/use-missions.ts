import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Type definitions matching backend enums
type Priority = "CRITICAL" | "HIGH" | "NORMAL" | "LOW";
type Category = "SYSTEM" | "RECON" | "ENCRYPTION" | "DEFENSE";
type Status = "PENDING" | "IN_PROGRESS" | "COMPLETED" | "FAILED";

interface Mission {
  id: string | number;
  title: string;
  priority: Priority;
  category: Category;
  status: Status;
  isGlitched?: boolean;
  createdAt?: string;
  created_at?: string;
}

interface CreateMissionRequest {
  title: string;
  priority: Priority;
  category: Category;
  status?: Status;
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
      const res = await fetch(`${API_BASE}/api/v1/synthetic/tasks?n=100000&seed=42`);
      if (!res.ok) throw new Error("Failed to fetch missions");
      const json = await res.json();
      const tasks = json.data.sample as SyntheticTask[];
      
      // Transform synthetic tasks to match Mission interface
      return tasks.map((task, idx): Mission => {
        // Map synthetic priority to valid enum
        const priorityMap: Record<string, Priority> = {
          "P1": "CRITICAL",
          "P2": "HIGH",
          "P3": "NORMAL",
          "P4": "LOW"
        };
        
        // Cycle through categories
        const categories: Category[] = ["SYSTEM", "RECON", "ENCRYPTION", "DEFENSE"];
        const category = categories[idx % 4];
        
        // Map synthetic status to valid enum
        const statusMap: Record<string, Status> = {
          "open": "PENDING",
          "in_progress": "IN_PROGRESS",
          "done": "COMPLETED",
          "failed": "FAILED"
        };
        
        return {
          id: task.id,
          title: task.title,
          priority: priorityMap[task.priority] || "NORMAL",
          category,
          status: statusMap[task.status] || "PENDING",
          isGlitched: Math.random() > 0.9,
          createdAt: new Date().toISOString(),
        };
      });
    },
  });
}

// POST /api/v1/missions - Create single mission
export function useCreateMission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: CreateMissionRequest) => {
      const res = await fetch(`${API_BASE}/api/v1/missions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("Failed to create mission");
      const envelope = await res.json();
      return envelope.data as Mission;
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
