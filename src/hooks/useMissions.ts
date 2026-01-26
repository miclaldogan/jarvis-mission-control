import { useEffect, useState } from "react";

export type Mission = {
  id: string;
  title: string;
  priority: "low" | "medium" | "high";
  completed: boolean;
};

export function useMissions() {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // mock data — backend bağlanınca fetch olacak
    const timeout = setTimeout(() => {
      setMissions([
        {
          id: "1",
          title: "Analyze system vitals",
          priority: "high",
          completed: false,
        },
        {
          id: "2",
          title: "Generate daily report",
          priority: "medium",
          completed: true,
        },
        {
          id: "3",
          title: "Sync context data",
          priority: "low",
          completed: false,
        },
      ]);
      setLoading(false);
    }, 1200);

    return () => clearTimeout(timeout);
  }, []);

  return { missions, loading };
}
