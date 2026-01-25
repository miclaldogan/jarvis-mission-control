import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

// Type definitions matching backend response
type Priority = "CRITICAL" | "HIGH" | "NORMAL" | "LOW" | "P1" | "P2" | "P3" | "P4";
type Category = "SYSTEM" | "RECON" | "ENCRYPTION" | "DEFENSE";
type Status = "PENDING" | "IN_PROGRESS" | "COMPLETED" | "FAILED" | "open" | "done" | "snoozed";

interface ScoreBreakdown {
  deadline: number;
  context: number;
  energy: number;
  preference: number;
}

interface Evidence {
  sources: string[];
  confidence: number;
}

export interface Mission {
  id: string | number;
  title: string;
  priority: Priority;
  priority_score?: number;
  score_breakdown?: ScoreBreakdown;
  reasons?: string[];
  category?: Category;
  status: Status;
  tags?: string[];
  why?: string;
  due_at?: string;
  dueAt?: string;
  evidence?: Evidence;
  actions?: Array<{ label: string; type: string; target: string }>;
  isGlitched?: boolean;
  createdAt?: string;
  created_at?: string;
  energyRequired?: number;
}

interface CreateMissionRequest {
  title: string;
  priority: Priority;
  category: Category;
  status?: Status;
}

// Store current run info
let currentRunId = 1;
let currentRunTimestamp = new Date();

export function getCurrentRun() {
  return { runId: currentRunId, timestamp: currentRunTimestamp };
}

export function incrementRun() {
  currentRunId++;
  currentRunTimestamp = new Date();
  return getCurrentRun();
}

// GET /api/v1/missions/today - Stable today's mission list (no regeneration on refresh)
export function useMissions() {
  return useQuery({
    queryKey: ["missions-today"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/v1/missions/today`);
      if (!res.ok) {
        // If no missions today, return empty array (will show "generate" prompt)
        if (res.status === 404) return [];
        throw new Error("Failed to fetch missions");
      }
      const json = await res.json();
      const missions = json.data?.missions || [];
      
      // Map backend response to frontend Mission interface
      return missions.map((m: any, idx: number): Mission => {
        const categories: Category[] = ["SYSTEM", "RECON", "ENCRYPTION", "DEFENSE"];
        return {
          id: m.id,
          title: m.title,
          priority: m.priority,
          priority_score: m.priority_score,
          score_breakdown: m.score_breakdown,
          reasons: m.reasons || m.score_breakdown?.reasons,
          category: m.category || categories[idx % 4],
          status: m.status || "open",
          tags: m.tags || [],
          why: m.why,
          due_at: m.due_at,
          dueAt: m.due_at,
          evidence: m.evidence,
          actions: m.actions,
          isGlitched: false,
          createdAt: m.created_at || new Date().toISOString(),
          energyRequired: Math.floor((m.priority_score || 0.5) * 100),
        };
      });
    },
    staleTime: 30000, // 30 seconds - don't refetch constantly
  });
}

// Generate new run with missions - saves to today's list
export function useGenerateRun() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (preferences?: { energy_level?: string }) => {
      // First generate missions
      const res = await fetch(`${API_BASE}/api/v1/missions/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          limit: 15,
          seed: Date.now(),
          preferences,
        }),
      });
      if (!res.ok) throw new Error("Failed to generate run");
      const json = await res.json();
      const missions = json.data?.missions || [];

      incrementRun();
      return {
        run: getCurrentRun(),
        missions,
        context: json.data?.context,
      };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["missions-today"] });
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
      queryClient.invalidateQueries({ queryKey: ["missions-today"] });
    },
  });
}

// POST /api/missions/bulk - Use synthetic tasks endpoint
export function useBulkCreateMissions() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (count: number) => {
      // Synthetic tasks endpoint only accepts 100000 or 1000000
      const validN = count >= 1000000 ? 1000000 : 100000;
      const res = await fetch(
        `${API_BASE}/api/v1/synthetic/tasks?n=${validN}&seed=${Date.now()}`
      );
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.error?.message || "Failed to bulk create missions");
      }
      const json = await res.json();
      return { message: `Generated ${json.data.sample.length} tasks from ${validN} total`, count: json.data.sample.length };
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["missions-today"] }),
  });
}
