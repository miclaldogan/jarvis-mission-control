import { useQuery } from "@tanstack/react-query";
import { api } from "@shared/routes";

// GET /api/context
export function useContextItems() {
  return useQuery({
    queryKey: [api.context.list.path],
    queryFn: async () => {
      const res = await fetch(api.context.list.path, { credentials: "include" });
      if (!res.ok) throw new Error('Failed to fetch context items');
      return api.context.list.responses[200].parse(await res.json());
    },
  });
}
