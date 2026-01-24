import { useEffect, useState } from "react";

export type SystemVitals = {
  cpu: number;
  memory: number;
  load: number;
};

export function useSystemVitals() {
  const [data, setData] = useState<SystemVitals | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      setData({
        cpu: Math.floor(Math.random() * 50) + 20,
        memory: Math.floor(Math.random() * 8) + 2,
        load: parseFloat((Math.random() * 1.5).toFixed(2)),
      });
      setLoading(false);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return { data, loading };
}


