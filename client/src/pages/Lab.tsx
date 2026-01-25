import { Layout } from "@/components/Layout";
import { CyberCard } from "@/components/CyberCard";
import { CacheBadge } from "@/components/CacheBadge";
import { useBulkCreateMissions } from "@/hooks/use-missions";
import { useMetrics } from "@/hooks/use-metrics";
import { useCacheTest } from "@/hooks/use-cache-test";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { 
  Beaker, 
  Cpu, 
  Zap, 
  PlayCircle, 
  BarChart4,
  Terminal,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Database,
  Activity,
  Server,
  HardDrive,
  Wifi
} from "lucide-react";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function Lab() {
  const bulkCreate = useBulkCreateMissions();
  const { data: metrics } = useMetrics();
  const cacheTest = useCacheTest();
  const [simulationRunning, setSimulationRunning] = useState(false);
  const [loadTestRunning, setLoadTestRunning] = useState(false);
  const [loadTestResults, setLoadTestResults] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const { toast } = useToast();

  const addLog = (msg: string) => {
    setLogs(prev => [...prev, `[${new Date().toISOString().split('T')[1].split('.')[0]}] ${msg}`].slice(-8));
  };

  const handleGenerateTasks = async () => {
    setSimulationRunning(true);
    addLog("Initializing task generation sequence...");
    addLog("Allocating virtual memory blocks...");
    
    // Simulate some delay before hitting API
    setTimeout(() => {
      addLog("Sending bulk create request...");
      bulkCreate.mutate(100000, { // create 100k tasks
        onSuccess: (data) => {
          addLog(`SUCCESS: ${data.message}`);
          addLog(`Generated ${data.count} new mission protocols.`);
          setSimulationRunning(false);
          toast({
            title: "SIMULATION COMPLETE",
            description: `Successfully generated ${data.count} tasks.`,
            className: "bg-black border-accent text-accent",
          });
        },
        onError: () => {
          addLog("ERROR: Simulation failed due to overload.");
          setSimulationRunning(false);
          toast({
            title: "SIMULATION FAILED",
            description: "System overload detected during task generation.",
            variant: "destructive",
            className: "bg-black border-destructive text-destructive",
          });
        }
      });
    }, 1500);
  };

  const handleRunReport = () => {
    addLog("Compiling performance metrics...");
    
    setTimeout(() => {
        addLog("Analyzing cache hit/miss ratios...");
        setTimeout(() => {
            addLog("Report generation complete.");
            toast({
                title: "REPORT GENERATED",
                description: "System diagnostics available in /logs/sys_latest.log",
                className: "bg-black border-primary text-primary",
            });
        }, 800);
    }, 800);
  };

  const handleCacheTest = async () => {
    addLog("Running cache performance test...");
    addLog(`→ GET /api/v1/synthetic/tasks?n=100000&seed=42`);
    try {
      const result = await cacheTest.runTest();
      addLog(`← Response: ${result.cacheStatus} (${result.computeTime}ms)`);
      toast({
        title: `CACHE ${result.cacheStatus}`,
        description: `Response time: ${result.computeTime}ms`,
        className: result.cacheStatus === "HIT" 
          ? "bg-black border-accent text-accent" 
          : "bg-black border-destructive text-destructive",
      });
    } catch (error) {
      addLog("ERROR: Cache test failed");
      toast({
        title: "TEST FAILED",
        description: "Unable to complete cache test",
        variant: "destructive",
      });
    }
  };

  // Load test function - simulates concurrent requests
  const handleLoadTest = async () => {
    setLoadTestRunning(true);
    setLoadTestResults(null);
    addLog("═══════════════════════════════════════════");
    addLog("🚀 LOAD TEST STARTING");
    addLog("═══════════════════════════════════════════");
    addLog(`Target: ${API_BASE}/api/v1/context`);
    addLog("Concurrent Users: 50");
    addLog("Duration: 10 seconds");
    addLog("");
    
    const startTime = Date.now();
    const results: { success: number; failed: number; times: number[] } = { success: 0, failed: 0, times: [] };
    const concurrency = 50;
    const duration = 10000; // 10 seconds
    let requestCount = 0;
    
    const makeRequest = async () => {
      const reqStart = performance.now();
      try {
        const res = await fetch(`${API_BASE}/api/v1/context`);
        const reqEnd = performance.now();
        results.times.push(reqEnd - reqStart);
        if (res.ok) {
          results.success++;
        } else {
          results.failed++;
        }
      } catch {
        results.failed++;
      }
      requestCount++;
    };
    
    // Progress updates
    const progressInterval = setInterval(() => {
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      const rps = (requestCount / parseFloat(elapsed)).toFixed(1);
      addLog(`[${elapsed}s] Requests: ${requestCount} | RPS: ${rps} | OK: ${results.success} | ERR: ${results.failed}`);
    }, 2000);
    
    // Run concurrent requests for duration
    const workers = Array(concurrency).fill(null).map(async () => {
      while (Date.now() - startTime < duration) {
        await makeRequest();
      }
    });
    
    await Promise.all(workers);
    clearInterval(progressInterval);
    
    const totalTime = (Date.now() - startTime) / 1000;
    const avgTime = results.times.length > 0 
      ? (results.times.reduce((a, b) => a + b, 0) / results.times.length).toFixed(2) 
      : 0;
    const errorRate = ((results.failed / (results.success + results.failed)) * 100).toFixed(2);
    const throughput = ((results.success + results.failed) / totalTime).toFixed(1);
    
    addLog("");
    addLog("═══════════════════════════════════════════");
    addLog("📊 LOAD TEST RESULTS");
    addLog("═══════════════════════════════════════════");
    addLog(`Total Requests: ${results.success + results.failed}`);
    addLog(`Success: ${results.success} | Failed: ${results.failed}`);
    addLog(`Error Rate: ${errorRate}%`);
    addLog(`Throughput: ${throughput} req/s`);
    addLog(`Avg Response Time: ${avgTime}ms`);
    addLog(`Duration: ${totalTime.toFixed(1)}s`);
    addLog("");
    addLog(parseFloat(errorRate) < 1 ? "✅ TEST PASSED" : "❌ TEST FAILED");
    
    setLoadTestResults({
      total: results.success + results.failed,
      success: results.success,
      failed: results.failed,
      errorRate: parseFloat(errorRate),
      throughput: parseFloat(throughput as string),
      avgTime: parseFloat(avgTime as string),
    });
    
    setLoadTestRunning(false);
    
    toast({
      title: parseFloat(errorRate) < 1 ? "✅ LOAD TEST PASSED" : "❌ LOAD TEST FAILED",
      description: `${throughput} req/s | ${errorRate}% error rate`,
      className: parseFloat(errorRate) < 1 
        ? "bg-black border-accent text-accent" 
        : "bg-black border-destructive text-destructive",
    });
  };

  return (
    <Layout>
      <div className="mb-8">
        <h2 className="text-4xl font-display font-bold text-white tracking-tighter mb-2 text-glow">
          SIMULATION LAB
        </h2>
        <p className="text-primary/60 font-mono text-sm max-w-2xl">
          Performance testing and system diagnostics. Generate up to 1M synthetic tasks, run load tests with 50 concurrent users, 
          and validate cache efficiency. All tests are logged in real-time below.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <CyberCard title="CONTROL PANEL" glowColor="secondary">
             <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
               <div className="p-4 bg-white/5 rounded border border-white/10 flex flex-col gap-4">
                 <div className="flex items-center gap-3 text-secondary">
                   <Zap className="w-6 h-6" />
                   <h4 className="font-bold">LOAD TEST</h4>
                 </div>
                 <p className="text-xs text-muted-foreground">
                   Generates high volume of mission protocols to test database write latency and UI rendering performance.
                 </p>
                 <Button 
                   onClick={handleGenerateTasks} 
                   disabled={simulationRunning}
                   className="w-full bg-secondary hover:bg-secondary/80 text-white font-bold tracking-wider relative overflow-hidden"
                 >
                   {simulationRunning && (
                     <motion.div 
                       className="absolute inset-0 bg-white/20"
                       initial={{ x: "-100%" }}
                       animate={{ x: "100%" }}
                       transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                     />
                   )}
                   {simulationRunning ? "GENERATING..." : "GENERATE 100K TASKS"}
                 </Button>
               </div>

               <div className="p-4 bg-white/5 rounded border border-white/10 flex flex-col gap-4">
                 <div className="flex items-center gap-3 text-accent">
                   <Activity className="w-6 h-6" />
                   <h4 className="font-bold">STRESS TEST</h4>
                 </div>
                 <p className="text-xs text-muted-foreground">
                   50 concurrent users for 10 seconds. Tests API throughput, response times, and error rates.
                 </p>
                 <Button 
                   onClick={handleLoadTest} 
                   disabled={loadTestRunning}
                   variant="outline" 
                   className="w-full border-accent text-accent hover:bg-accent hover:text-black font-bold tracking-wider"
                 >
                   {loadTestRunning ? (
                     <>
                       <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                       RUNNING...
                     </>
                   ) : (
                     "RUN LOAD TEST"
                   )}
                 </Button>
                 {loadTestResults && (
                   <div className="grid grid-cols-2 gap-2 mt-2">
                     <div className="p-2 bg-black/30 rounded text-center">
                       <div className="text-xs text-muted-foreground">Throughput</div>
                       <div className="text-sm font-bold text-accent">{loadTestResults.throughput} req/s</div>
                     </div>
                     <div className="p-2 bg-black/30 rounded text-center">
                       <div className="text-xs text-muted-foreground">Error Rate</div>
                       <div className={cn("text-sm font-bold", loadTestResults.errorRate < 1 ? "text-accent" : "text-destructive")}>
                         {loadTestResults.errorRate}%
                       </div>
                     </div>
                     <div className="p-2 bg-black/30 rounded text-center">
                       <div className="text-xs text-muted-foreground">Avg Time</div>
                       <div className="text-sm font-bold text-primary">{loadTestResults.avgTime}ms</div>
                     </div>
                     <div className="p-2 bg-black/30 rounded text-center">
                       <div className="text-xs text-muted-foreground">Total</div>
                       <div className="text-sm font-bold text-white">{loadTestResults.total}</div>
                     </div>
                   </div>
                 )}
               </div>

               <div className="p-4 bg-white/5 rounded border border-white/10 flex flex-col gap-4">
                 <div className="flex items-center gap-3 text-primary">
                   <Database className="w-6 h-6" />
                   <h4 className="font-bold">CACHE PROOF</h4>
                 </div>
                 <p className="text-xs text-muted-foreground">
                   Test cache performance: first call = MISS (slow), second call = HIT (fast). Demonstrates caching efficiency.
                 </p>
                 <Button 
                   onClick={handleCacheTest} 
                   disabled={cacheTest.loading}
                   variant="outline" 
                   className="w-full border-primary text-primary hover:bg-primary hover:text-black font-bold tracking-wider"
                 >
                   {cacheTest.loading ? (
                     <>
                       <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                       TESTING...
                     </>
                   ) : (
                     <>RUN CACHE TEST ({cacheTest.requestCount}/20)</>
                   )}
                 </Button>
                 {cacheTest.results.length > 0 && (
                   <div className="space-y-2 max-h-[120px] overflow-y-auto">
                     {cacheTest.results.map((result, i) => (
                       <div key={i} className="flex items-center justify-between p-2 bg-black/30 rounded border border-white/5">
                         <span className="text-xs text-muted-foreground">Test #{result.requestNumber}</span>
                         <CacheBadge 
                           status={result.cacheStatus as "HIT" | "MISS" | "BYPASS" | "UNKNOWN"} 
                           computeTime={result.computeTime}
                         />
                       </div>
                     ))}
                   </div>
                 )}
                 {cacheTest.requestCount > 0 && (
                   <Button 
                     onClick={cacheTest.reset} 
                     variant="ghost" 
                     size="sm"
                     className="text-xs text-muted-foreground hover:text-white"
                   >
                     Reset Tests
                   </Button>
                 )}
               </div>
             </div>
          </CyberCard>

          <CyberCard title="SIMULATION LOGS" glowColor="primary" className="font-mono text-xs h-[300px] overflow-hidden flex flex-col">
            <div className="flex-1 bg-black/50 p-4 rounded border border-white/5 overflow-y-auto space-y-2">
              <AnimatePresence initial={false}>
                {logs.length === 0 && <span className="text-muted-foreground opacity-50">Waiting for input...</span>}
                {logs.map((log, i) => (
                  <motion.div 
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="text-primary/80 border-l-2 border-primary/30 pl-2"
                  >
                    {log}
                  </motion.div>
                ))}
              </AnimatePresence>
              {simulationRunning && (
                <div className="flex items-center gap-2 text-secondary">
                   <RefreshCw className="w-3 h-3 animate-spin" />
                   PROCESSING...
                </div>
              )}
            </div>
          </CyberCard>
        </div>

        <div className="space-y-6">
          <CyberCard title="PERFORMANCE METRICS" glowColor="accent">
             <div className="space-y-4">
               {metrics?.map((metric) => (
                 <div key={metric.id} className="flex items-center justify-between p-3 bg-white/5 rounded border border-white/5 hover:border-accent/30 transition-all">
                   <div>
                     <div className="text-xs text-muted-foreground uppercase">{metric.name}</div>
                     <div className="font-mono font-bold text-white text-lg">{metric.value}</div>
                   </div>
                   <div className={
                     metric.status === 'CRITICAL' ? 'text-destructive' : 
                     metric.status === 'WARNING' ? 'text-yellow-500' : 'text-accent'
                   }>
                     <Beaker className="w-5 h-5" />
                   </div>
                 </div>
               ))}
             </div>
          </CyberCard>

          <CyberCard className="bg-gradient-to-br from-secondary/20 to-black border-secondary/30">
             <div className="flex flex-col items-center justify-center text-center py-6">
               <Cpu className="w-16 h-16 text-secondary mb-4 animate-pulse" />
               <h3 className="text-xl font-bold text-white">CORE STABLE</h3>
               <p className="text-secondary text-sm mt-1">Ready for overclocking</p>
             </div>
          </CyberCard>
        </div>
      </div>
    </Layout>
  );
}
