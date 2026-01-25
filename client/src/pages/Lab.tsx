import { Layout } from "@/components/Layout";
import { CyberCard } from "@/components/CyberCard";
import { CacheBadge } from "@/components/CacheBadge";
import { useBulkCreateMissions } from "@/hooks/use-missions";
import { useMetrics } from "@/hooks/use-metrics";
import { useCacheTest } from "@/hooks/use-cache-test";
import { useSystemVitals } from "@/hooks/use-system-vitals";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
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
  Wifi,
  ChevronDown,
  Flame,
  Gauge
} from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

type TaskCount = 100000 | 1000000;

export default function Lab() {
  const bulkCreate = useBulkCreateMissions();
  const { data: metrics } = useMetrics();
  const { data: vitals } = useSystemVitals();
  const cacheTest = useCacheTest();
  const [simulationRunning, setSimulationRunning] = useState(false);
  const [loadTestRunning, setLoadTestRunning] = useState(false);
  const [loadTestResults, setLoadTestResults] = useState<any>(null);
  const [terminalLogs, setTerminalLogs] = useState<string[]>([]);
  const [taskCount, setTaskCount] = useState<TaskCount>(100000);
  const [showTaskDropdown, setShowTaskDropdown] = useState(false);
  const terminalRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // Auto scroll terminal
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [terminalLogs]);

  const addLog = (msg: string, type: 'info' | 'success' | 'error' | 'header' | 'data' = 'info') => {
    const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
    const prefix = {
      info: '│',
      success: '✓',
      error: '✗',
      header: '═',
      data: '→',
    }[type];
    setTerminalLogs(prev => [...prev, `[${timestamp}] ${prefix} ${msg}`].slice(-50));
  };

  const clearTerminal = () => {
    setTerminalLogs([]);
  };

  const handleGenerateTasks = async () => {
    setSimulationRunning(true);
    clearTerminal();
    
    const countLabel = taskCount === 1000000 ? "1M" : "100K";
    
    addLog("═══════════════════════════════════════════════", "header");
    addLog(`🗄️  TASK GENERATION PROTOCOL - ${countLabel} TASKS`, "header");
    addLog("═══════════════════════════════════════════════", "header");
    addLog("");
    addLog(`Target Count: ${taskCount.toLocaleString()} synthetic tasks`);
    addLog(`Endpoint: POST /api/v1/missions/bulk`);
    addLog("");
    addLog("Initializing virtual memory allocation...");
    
    await new Promise(r => setTimeout(r, 500));
    addLog("Allocating task buffer pools...", "data");
    
    await new Promise(r => setTimeout(r, 500));
    addLog("Preparing database transaction...", "data");
    
    await new Promise(r => setTimeout(r, 500));
    addLog("Sending bulk create request...", "data");
    addLog("");
    
    bulkCreate.mutate(taskCount, {
      onSuccess: (data) => {
        addLog("");
        addLog("═══════════════════════════════════════════════", "header");
        addLog("📊 GENERATION COMPLETE", "header");
        addLog("═══════════════════════════════════════════════", "header");
        addLog(`Tasks Created: ${data.count?.toLocaleString() || taskCount.toLocaleString()}`, "success");
        addLog(`Status: ${data.message || "SUCCESS"}`, "success");
        addLog(`Timestamp: ${new Date().toISOString()}`, "data");
        addLog("");
        addLog("✅ SIMULATION COMPLETE", "success");
        setSimulationRunning(false);
        toast({
          title: "SIMULATION COMPLETE",
          description: `Successfully generated ${data.count?.toLocaleString() || taskCount.toLocaleString()} tasks.`,
          className: "bg-black border-accent text-accent",
        });
      },
      onError: (err) => {
        addLog("");
        addLog("═══════════════════════════════════════════════", "header");
        addLog("❌ GENERATION FAILED", "error");
        addLog("═══════════════════════════════════════════════", "header");
        addLog(`Error: ${err instanceof Error ? err.message : "Unknown error"}`, "error");
        addLog("");
        setSimulationRunning(false);
        toast({
          title: "SIMULATION FAILED",
          description: "System overload detected during task generation.",
          variant: "destructive",
          className: "bg-black border-destructive text-destructive",
        });
      }
    });
  };

  const handleRunReport = () => {
    addLog("Compiling performance metrics...");
    
    setTimeout(() => {
        addLog("Analyzing cache hit/miss ratios...", "data");
        setTimeout(() => {
            addLog("Report generation complete.", "success");
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
    addLog(`→ GET /api/v1/synthetic/tasks?n=100000&seed=42`, "data");
    try {
      const result = await cacheTest.runTest();
      addLog(`← Response: ${result.cacheStatus} (${result.computeTime}ms)`, result.cacheStatus === "HIT" ? "success" : "info");
      toast({
        title: `CACHE ${result.cacheStatus}`,
        description: `Response time: ${result.computeTime}ms`,
        className: result.cacheStatus === "HIT" 
          ? "bg-black border-accent text-accent" 
          : "bg-black border-destructive text-destructive",
      });
    } catch (error) {
      addLog("ERROR: Cache test failed", "error");
      toast({
        title: "TEST FAILED",
        description: "Unable to complete cache test",
        variant: "destructive",
      });
    }
  };

  // Stress Test - simulates concurrent requests
  const handleStressTest = async () => {
    setLoadTestRunning(true);
    setLoadTestResults(null);
    clearTerminal();
    
    addLog("═══════════════════════════════════════════════", "header");
    addLog("🔥 STRESS TEST INITIALIZING", "header");
    addLog("═══════════════════════════════════════════════", "header");
    addLog("");
    addLog(`Target Endpoint: ${API_BASE}/api/v1/context`);
    addLog("Concurrent Workers: 50");
    addLog("Test Duration: 10 seconds");
    addLog("Request Type: GET (API Throughput Test)");
    addLog("");
    addLog("Starting worker threads...", "data");
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
      const successRate = requestCount > 0 ? ((results.success / requestCount) * 100).toFixed(1) : "0.0";
      addLog(`[${elapsed}s] Reqs: ${requestCount} | RPS: ${rps} | OK: ${results.success} | ERR: ${results.failed} | Rate: ${successRate}%`, "data");
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
    const minTime = results.times.length > 0 ? Math.min(...results.times).toFixed(2) : 0;
    const maxTime = results.times.length > 0 ? Math.max(...results.times).toFixed(2) : 0;
    const p95Time = results.times.length > 0 
      ? results.times.sort((a, b) => a - b)[Math.floor(results.times.length * 0.95)]?.toFixed(2) || 0
      : 0;
    const errorRate = ((results.failed / (results.success + results.failed)) * 100).toFixed(2);
    const throughput = ((results.success + results.failed) / totalTime).toFixed(1);
    
    addLog("");
    addLog("═══════════════════════════════════════════════", "header");
    addLog("📊 STRESS TEST RESULTS", "header");
    addLog("═══════════════════════════════════════════════", "header");
    addLog(`Total Requests: ${(results.success + results.failed).toLocaleString()}`, "data");
    addLog(`Successful: ${results.success.toLocaleString()}`, "success");
    addLog(`Failed: ${results.failed.toLocaleString()}`, results.failed > 0 ? "error" : "data");
    addLog("");
    addLog("Performance Metrics:", "header");
    addLog(`  Throughput: ${throughput} req/s`, "data");
    addLog(`  Error Rate: ${errorRate}%`, parseFloat(errorRate) > 1 ? "error" : "success");
    addLog(`  Avg Response: ${avgTime}ms`, "data");
    addLog(`  Min Response: ${minTime}ms`, "data");
    addLog(`  Max Response: ${maxTime}ms`, "data");
    addLog(`  P95 Response: ${p95Time}ms`, "data");
    addLog(`  Duration: ${totalTime.toFixed(1)}s`, "data");
    addLog("");
    addLog(parseFloat(errorRate) < 1 ? "✅ STRESS TEST PASSED" : "❌ STRESS TEST FAILED", parseFloat(errorRate) < 1 ? "success" : "error");
    
    setLoadTestResults({
      total: results.success + results.failed,
      success: results.success,
      failed: results.failed,
      errorRate: parseFloat(errorRate),
      throughput: parseFloat(throughput as string),
      avgTime: parseFloat(avgTime as string),
      minTime: parseFloat(minTime as string),
      maxTime: parseFloat(maxTime as string),
      p95Time: parseFloat(p95Time as string),
      duration: totalTime,
    });
    
    setLoadTestRunning(false);
    
    toast({
      title: parseFloat(errorRate) < 1 ? "✅ STRESS TEST PASSED" : "❌ STRESS TEST FAILED",
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
               {/* TASK GENERATOR Card */}
               <div className="p-4 bg-white/5 rounded border border-white/10 flex flex-col gap-4">
                 <div className="flex items-center gap-3 text-secondary">
                   <Database className="w-6 h-6" />
                   <h4 className="font-bold">TASK GENERATOR</h4>
                 </div>
                 <p className="text-xs text-muted-foreground">
                   Generates synthetic mission protocols to test database write latency and UI rendering performance.
                 </p>
                 
                 {/* Task Count Selector */}
                 <div className="relative">
                   <Button
                     variant="outline"
                     onClick={() => setShowTaskDropdown(!showTaskDropdown)}
                     className="w-full justify-between border-white/20 text-white hover:bg-white/10"
                   >
                     <span className="font-mono">
                       {taskCount === 1000000 ? "1,000,000 (1M)" : "100,000 (100K)"} Tasks
                     </span>
                     <ChevronDown className={cn("w-4 h-4 transition-transform", showTaskDropdown && "rotate-180")} />
                   </Button>
                   {showTaskDropdown && (
                     <div className="absolute top-full left-0 right-0 mt-1 bg-black border border-white/20 rounded z-10">
                       <button
                         onClick={() => { setTaskCount(100000); setShowTaskDropdown(false); }}
                         className={cn(
                           "w-full px-4 py-2 text-left font-mono text-sm hover:bg-white/10 transition-colors",
                           taskCount === 100000 ? "text-secondary" : "text-white"
                         )}
                       >
                         100,000 (100K) Tasks
                       </button>
                       <button
                         onClick={() => { setTaskCount(1000000); setShowTaskDropdown(false); }}
                         className={cn(
                           "w-full px-4 py-2 text-left font-mono text-sm hover:bg-white/10 transition-colors",
                           taskCount === 1000000 ? "text-secondary" : "text-white"
                         )}
                       >
                         1,000,000 (1M) Tasks
                       </button>
                     </div>
                   )}
                 </div>
                 
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
                   {simulationRunning ? "GENERATING..." : `GENERATE ${taskCount === 1000000 ? "1M" : "100K"} TASKS`}
                 </Button>
               </div>

               {/* STRESS TEST Card */}
               <div className="p-4 bg-white/5 rounded border border-white/10 flex flex-col gap-4">
                 <div className="flex items-center gap-3 text-destructive">
                   <Flame className="w-6 h-6" />
                   <h4 className="font-bold">STRESS TEST</h4>
                 </div>
                 <p className="text-xs text-muted-foreground">
                   50 concurrent users for 10 seconds. Tests API throughput, response times, and error rates under load.
                 </p>
                 <Button 
                   onClick={handleStressTest} 
                   disabled={loadTestRunning}
                   variant="outline" 
                   className="w-full border-destructive text-destructive hover:bg-destructive hover:text-white font-bold tracking-wider"
                 >
                   {loadTestRunning ? (
                     <>
                       <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                       TESTING...
                     </>
                   ) : (
                     "RUN STRESS TEST"
                   )}
                 </Button>
                 
                 {/* Real-time metrics from stress test */}
                 {loadTestResults && (
                   <div className="grid grid-cols-2 gap-2 mt-2">
                     <div className="p-2 bg-black/30 rounded text-center border border-white/5">
                       <div className="text-[10px] text-muted-foreground uppercase">Throughput</div>
                       <div className="text-sm font-bold text-accent font-mono">{loadTestResults.throughput} req/s</div>
                     </div>
                     <div className="p-2 bg-black/30 rounded text-center border border-white/5">
                       <div className="text-[10px] text-muted-foreground uppercase">Error Rate</div>
                       <div className={cn("text-sm font-bold font-mono", loadTestResults.errorRate < 1 ? "text-accent" : "text-destructive")}>
                         {loadTestResults.errorRate}%
                       </div>
                     </div>
                     <div className="p-2 bg-black/30 rounded text-center border border-white/5">
                       <div className="text-[10px] text-muted-foreground uppercase">Avg Time</div>
                       <div className="text-sm font-bold text-primary font-mono">{loadTestResults.avgTime}ms</div>
                     </div>
                     <div className="p-2 bg-black/30 rounded text-center border border-white/5">
                       <div className="text-[10px] text-muted-foreground uppercase">P95 Time</div>
                       <div className="text-sm font-bold text-secondary font-mono">{loadTestResults.p95Time}ms</div>
                     </div>
                     <div className="p-2 bg-black/30 rounded text-center border border-white/5">
                       <div className="text-[10px] text-muted-foreground uppercase">Total Reqs</div>
                       <div className="text-sm font-bold text-white font-mono">{loadTestResults.total.toLocaleString()}</div>
                     </div>
                     <div className="p-2 bg-black/30 rounded text-center border border-white/5">
                       <div className="text-[10px] text-muted-foreground uppercase">Duration</div>
                       <div className="text-sm font-bold text-white font-mono">{loadTestResults.duration.toFixed(1)}s</div>
                     </div>
                   </div>
                 )}
               </div>

               {/* CACHE PROOF Card - Full Width */}
               <div className="p-4 bg-white/5 rounded border border-white/10 flex flex-col gap-4 md:col-span-2">
                 <div className="flex items-center gap-3 text-primary">
                   <Gauge className="w-6 h-6" />
                   <h4 className="font-bold">CACHE PROOF</h4>
                 </div>
                 <p className="text-xs text-muted-foreground">
                   Test cache performance: first call = MISS (slow), second call = HIT (fast). Demonstrates Redis caching efficiency.
                 </p>
                 <div className="flex gap-2">
                   <Button 
                     onClick={handleCacheTest} 
                     disabled={cacheTest.loading}
                     variant="outline" 
                     className="flex-1 border-primary text-primary hover:bg-primary hover:text-black font-bold tracking-wider"
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
                   {cacheTest.requestCount > 0 && (
                     <Button 
                       onClick={cacheTest.reset} 
                       variant="ghost" 
                       size="sm"
                       className="text-xs text-muted-foreground hover:text-white"
                     >
                       Reset
                     </Button>
                   )}
                 </div>
                 {cacheTest.results.length > 0 && (
                   <div className="grid grid-cols-2 md:grid-cols-4 gap-2 max-h-[120px] overflow-y-auto">
                     {cacheTest.results.map((result, i) => (
                       <div key={i} className="flex items-center justify-between p-2 bg-black/30 rounded border border-white/5">
                         <span className="text-xs text-muted-foreground">#{result.requestNumber}</span>
                         <CacheBadge 
                           status={result.cacheStatus as "HIT" | "MISS" | "BYPASS" | "UNKNOWN"} 
                           computeTime={result.computeTime}
                         />
                       </div>
                     ))}
                   </div>
                 )}
               </div>
             </div>
          </CyberCard>

          {/* Terminal Output - Enhanced Aesthetic */}
          <CyberCard title="SYSTEM TERMINAL" glowColor="primary" className="font-mono text-xs">
            <div 
              ref={terminalRef}
              className="h-[350px] bg-black/80 p-4 rounded border border-primary/20 overflow-y-auto space-y-1 scroll-smooth"
              style={{ fontFamily: "'JetBrains Mono', 'Fira Code', monospace" }}
            >
              {terminalLogs.length === 0 && (
                <div className="text-muted-foreground/50 flex items-center gap-2">
                  <span className="animate-pulse">▌</span>
                  <span>Awaiting command input...</span>
                </div>
              )}
              <AnimatePresence initial={false}>
                {terminalLogs.map((log, i) => {
                  const isHeader = log.includes("═══") || log.includes("Performance Metrics:");
                  const isSuccess = log.includes("✓") || log.includes("✅");
                  const isError = log.includes("✗") || log.includes("❌");
                  const isData = log.includes("→");
                  
                  return (
                    <motion.div 
                      key={i}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.15 }}
                      className={cn(
                        "whitespace-pre",
                        isHeader && "text-primary font-bold",
                        isSuccess && "text-accent",
                        isError && "text-destructive",
                        isData && "text-secondary",
                        !isHeader && !isSuccess && !isError && !isData && "text-primary/70"
                      )}
                    >
                      {log}
                    </motion.div>
                  );
                })}
              </AnimatePresence>
              {(simulationRunning || loadTestRunning) && (
                <motion.div 
                  className="flex items-center gap-2 text-secondary mt-2"
                  animate={{ opacity: [1, 0.5, 1] }}
                  transition={{ repeat: Infinity, duration: 1 }}
                >
                  <RefreshCw className="w-3 h-3 animate-spin" />
                  <span>Processing...</span>
                </motion.div>
              )}
            </div>
            <div className="flex justify-end mt-2">
              <Button 
                onClick={clearTerminal} 
                variant="ghost" 
                size="sm"
                className="text-xs text-muted-foreground hover:text-white"
              >
                Clear Terminal
              </Button>
            </div>
          </CyberCard>
        </div>

        {/* Right Sidebar - System Vitals */}
        <div className="space-y-6">
          <CyberCard title="SYSTEM VITALS" glowColor="accent">
             <div className="space-y-4">
               {/* CPU */}
               <div className="p-3 bg-white/5 rounded border border-white/5">
                 <div className="flex items-center justify-between mb-2">
                   <div className="flex items-center gap-2">
                     <Cpu className="w-4 h-4 text-primary" />
                     <span className="text-xs text-muted-foreground uppercase">CPU Usage</span>
                   </div>
                   <span className={cn(
                     "font-mono font-bold text-lg",
                     (vitals?.cpu || 0) > 80 ? "text-destructive" : 
                     (vitals?.cpu || 0) > 50 ? "text-yellow-500" : "text-accent"
                   )}>
                     {vitals?.cpu?.toFixed(1) || "0.0"}%
                   </span>
                 </div>
                 <Progress 
                   value={vitals?.cpu || 0} 
                   className="h-2 bg-white/10"
                   indicatorClassName={cn(
                     (vitals?.cpu || 0) > 80 ? "bg-destructive" : 
                     (vitals?.cpu || 0) > 50 ? "bg-yellow-500" : "bg-accent"
                   )}
                 />
               </div>
               
               {/* Memory */}
               <div className="p-3 bg-white/5 rounded border border-white/5">
                 <div className="flex items-center justify-between mb-2">
                   <div className="flex items-center gap-2">
                     <Server className="w-4 h-4 text-secondary" />
                     <span className="text-xs text-muted-foreground uppercase">Memory</span>
                   </div>
                   <span className={cn(
                     "font-mono font-bold text-lg",
                     (vitals?.memory || 0) > 85 ? "text-destructive" : 
                     (vitals?.memory || 0) > 70 ? "text-yellow-500" : "text-secondary"
                   )}>
                     {vitals?.memory?.toFixed(1) || "0.0"}%
                   </span>
                 </div>
                 <Progress 
                   value={vitals?.memory || 0} 
                   className="h-2 bg-white/10"
                   indicatorClassName={cn(
                     (vitals?.memory || 0) > 85 ? "bg-destructive" : 
                     (vitals?.memory || 0) > 70 ? "bg-yellow-500" : "bg-secondary"
                   )}
                 />
               </div>
               
               {/* Disk */}
               <div className="p-3 bg-white/5 rounded border border-white/5">
                 <div className="flex items-center justify-between mb-2">
                   <div className="flex items-center gap-2">
                     <HardDrive className="w-4 h-4 text-primary" />
                     <span className="text-xs text-muted-foreground uppercase">Disk</span>
                   </div>
                   <span className={cn(
                     "font-mono font-bold text-lg",
                     (vitals?.disk || 0) > 90 ? "text-destructive" : 
                     (vitals?.disk || 0) > 75 ? "text-yellow-500" : "text-primary"
                   )}>
                     {vitals?.disk?.toFixed(1) || "0.0"}%
                   </span>
                 </div>
                 <Progress 
                   value={vitals?.disk || 0} 
                   className="h-2 bg-white/10"
                   indicatorClassName={cn(
                     (vitals?.disk || 0) > 90 ? "bg-destructive" : 
                     (vitals?.disk || 0) > 75 ? "bg-yellow-500" : "bg-primary"
                   )}
                 />
               </div>
               
               {/* Network */}
               <div className="p-3 bg-white/5 rounded border border-white/5">
                 <div className="flex items-center justify-between mb-2">
                   <div className="flex items-center gap-2">
                     <Wifi className="w-4 h-4 text-accent" />
                     <span className="text-xs text-muted-foreground uppercase">Network I/O</span>
                   </div>
                 </div>
                 <div className="grid grid-cols-2 gap-2 text-xs">
                   <div className="flex justify-between">
                     <span className="text-muted-foreground">↑ Sent</span>
                     <span className="font-mono text-accent">{vitals?.network_sent_mbps?.toFixed(1) || "0.0"} MB</span>
                   </div>
                   <div className="flex justify-between">
                     <span className="text-muted-foreground">↓ Recv</span>
                     <span className="font-mono text-accent">{vitals?.network_recv_mbps?.toFixed(1) || "0.0"} MB</span>
                   </div>
                 </div>
               </div>
             </div>
          </CyberCard>

          {/* Performance Metrics from API */}
          <CyberCard title="API METRICS" glowColor="secondary">
             <div className="space-y-3">
               {metrics?.map((metric) => (
                 <div key={metric.id} className="flex items-center justify-between p-2 bg-white/5 rounded border border-white/5 hover:border-secondary/30 transition-all">
                   <div>
                     <div className="text-[10px] text-muted-foreground uppercase">{metric.name}</div>
                     <div className="font-mono font-bold text-white">{metric.value}</div>
                   </div>
                   <div className={cn(
                     "w-2 h-2 rounded-full",
                     metric.status === 'CRITICAL' ? 'bg-destructive' : 
                     metric.status === 'WARNING' ? 'bg-yellow-500' : 'bg-accent'
                   )} />
                 </div>
               ))}
             </div>
          </CyberCard>

          <CyberCard className="bg-gradient-to-br from-accent/10 to-black border-accent/30">
             <div className="flex flex-col items-center justify-center text-center py-6">
               <div className="relative">
                 <Cpu className="w-16 h-16 text-accent mb-4" />
                 <motion.div
                   className="absolute inset-0 bg-accent/20 rounded-full blur-xl"
                   animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
                   transition={{ repeat: Infinity, duration: 2 }}
                 />
               </div>
               <h3 className="text-xl font-bold text-white">CORE STABLE</h3>
               <p className="text-accent text-sm mt-1">System operational</p>
               <div className="text-[10px] text-muted-foreground mt-2 font-mono">
                 Last Update: {vitals?.timestamp ? new Date(vitals.timestamp).toLocaleTimeString() : "--:--:--"}
               </div>
             </div>
          </CyberCard>
        </div>
      </div>
    </Layout>
  );
}
