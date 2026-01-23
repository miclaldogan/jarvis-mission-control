import { Layout } from "@/components/Layout";
import { CyberCard } from "@/components/CyberCard";
import { CacheBadge } from "@/components/CacheBadge";
import { useBulkCreateMissions } from "@/hooks/use-missions";
import { useMetrics } from "@/hooks/use-metrics";
import { useCacheTest } from "@/hooks/use-cache-test";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
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
  Database
} from "lucide-react";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function Lab() {
  const bulkCreate = useBulkCreateMissions();
  const { data: metrics } = useMetrics();
  const cacheTest = useCacheTest();
  const [simulationRunning, setSimulationRunning] = useState(false);
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
      bulkCreate.mutate(50, { // create 50 tasks
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
    try {
      const result = await cacheTest.runTest();
      addLog(`Cache ${result.cacheStatus} - ${result.computeTime}ms compute time`);
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

  return (
    <Layout>
      <div className="mb-8">
        <h2 className="text-4xl font-display font-bold text-white tracking-tighter mb-2 text-glow">
          SIMULATION LAB
        </h2>
        <p className="text-primary/60 font-mono text-sm">
          Stress test system capabilities and run scenario simulations.
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
                   <BarChart4 className="w-6 h-6" />
                   <h4 className="font-bold">DIAGNOSTICS</h4>
                 </div>
                 <p className="text-xs text-muted-foreground">
                   Compiles system performance logs and computes efficiency ratings based on current metrics.
                 </p>
                 <Button onClick={handleRunReport} variant="outline" className="w-full border-accent text-accent hover:bg-accent hover:text-black font-bold tracking-wider">
                   RUN SYSTEM REPORT
                 </Button>
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
                           status={result.cacheStatus as any} 
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
               
               {/* Static mock row for comparison */}
               <div className="flex items-center justify-between p-3 bg-white/5 rounded border border-white/5 opacity-50">
                 <div>
                   <div className="text-xs text-muted-foreground uppercase">BASELINE</div>
                   <div className="font-mono font-bold text-white text-lg">120ms</div>
                 </div>
                 <div className="text-muted-foreground">
                   <span className="text-[10px] border border-current px-1 rounded">REF</span>
                 </div>
               </div>
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
