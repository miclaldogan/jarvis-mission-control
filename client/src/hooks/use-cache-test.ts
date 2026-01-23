import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

interface CacheTestResult {
  cacheStatus: string;
  computeTime: number;
  timestamp: Date;
  requestNumber: number;
}

export function useCacheTest() {
  const [results, setResults] = useState<CacheTestResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [requestCount, setRequestCount] = useState(0);

  const runTest = async (endpoint: string = "/api/v1/synthetic/tasks?n=100000&seed=42") => {
    setLoading(true);
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_BASE}${endpoint}`);
      const endTime = performance.now();
      const computeTime = Math.round(endTime - startTime);
      
      const cacheStatus = response.headers.get("X-Cache") || "UNKNOWN";
      const serverComputeTime = response.headers.get("X-Compute-Time-ms");
      
      const newResult: CacheTestResult = {
        cacheStatus,
        computeTime: serverComputeTime ? parseInt(serverComputeTime) : computeTime,
        timestamp: new Date(),
        requestNumber: requestCount + 1,
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
  };

  return {
    results,
    loading,
    requestCount,
    runTest,
    reset,
  };
}
