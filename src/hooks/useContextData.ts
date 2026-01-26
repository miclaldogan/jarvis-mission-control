import { useEffect, useState } from "react";

export type ContextData = {
  weather: string;
  calendarEvents: number;
  unreadEmails: number;
};

export function useContextData() {
  const [data, setData] = useState<ContextData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // şimdilik mock — sonra API bağlanacak
    const timeout = setTimeout(() => {
      setData({
        weather: "Cloudy · 12°C",
        calendarEvents: Math.floor(Math.random() * 5),
        unreadEmails: Math.floor(Math.random() * 10),
      });
      setLoading(false);
    }, 1000);

    return () => clearTimeout(timeout);
  }, []);

  return { data, loading };
}

