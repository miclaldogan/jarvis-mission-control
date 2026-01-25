import { useState } from "react";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

interface CacheTestResult {
  cacheStatus: string;
  cacheKey: string;
  computeTime: number;
  timestamp: Date;
  requestNumber: number;
  seed: number;
}

export function useCacheTest() {
  const [results, setResults] = useState<CacheTestResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [requestCount, setRequestCount] = useState(0);
  const [seed, setSeed] = useState<number>(() => Date.now());

  const runTest = async (forceRefresh: boolean = false) => {
    setLoading(true);
    const startTime = performance.now();

    // Use a stable seed per session: first call is usually MISS, next calls HIT.
    // If forceRefresh is requested, rotate the seed for a new cache key.
    const usedSeed = forceRefresh ? Date.now() : seed;
    if (forceRefresh) setSeed(usedSeed);
    const endpoint = `/api/v1/synthetic/tasks?n=100000&seed=${usedSeed}`;
    
    try {
      // Important: disable browser HTTP caching; otherwise it may replay the first
      // MISS response (due to Cache-Control) and you'll never observe a HIT.
      const response = await fetch(`${API_BASE}${endpoint}`, { cache: "no-store" });
      const endTime = performance.now();
      const computeTime = Math.round(endTime - startTime);
      
      const cacheStatus = response.headers.get("X-Cache") || "UNKNOWN";
      const cacheKey = response.headers.get("X-Cache-Key") || "";
      const serverComputeTime = response.headers.get("X-Compute-Time-ms");
      
      const newResult: CacheTestResult = {
        cacheStatus,
        cacheKey,
        computeTime: serverComputeTime ? parseInt(serverComputeTime) : computeTime,
        timestamp: new Date(),
        requestNumber: requestCount + 1,
        seed: usedSeed,
      };
      
      setResults(prev => [...prev, newResult]);
      setRequestCount(prev => prev + 1);
      
      return newResult;
    } catch (error) {
      console.error("Cache test failed:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResults([]);
    setRequestCount(0);
    setSeed(Date.now());
  };

  return {
    results,
    loading,
    requestCount,
    runTest,
    reset,
  };
}
