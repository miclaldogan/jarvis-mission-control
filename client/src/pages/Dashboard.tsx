import { useState, useMemo } from "react";
import { useMissions, useCreateMission } from "@/hooks/use-missions";
import { useMetrics } from "@/hooks/use-metrics";
import { useSystemVitals } from "@/hooks/use-system-vitals";
import { CyberCard } from "@/components/CyberCard";
import { Layout } from "@/components/Layout";
import { TaskDetailDialog } from "@/components/TaskDetailDialog";
import { DashboardHeader } from "@/components/DashboardHeader";
import { FilterBar, FilterCategory, FilterPriority, FilterStatus, FilterDeadline, SortOption } from "@/components/FilterBar";
import { SystemHarmonics } from "@/components/SystemHarmonics";
import { cn } from "@/lib/utils";
import { 
  Clock, 
  Plus, 
  Terminal,
  Play,
  CheckCircle
} from "lucide-react";
import { format, isToday, isTomorrow, isThisWeek } from "date-fns";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { motion } from "framer-motion";

// Mission schema inline
const insertMissionSchema = z.object({
  title: z.string().min(1, "Title is required"),
  priority: z.enum(["CRITICAL", "HIGH", "NORMAL", "LOW"]),
  category: z.enum(["SYSTEM", "RECON", "ENCRYPTION", "DEFENSE"]),
  status: z.enum(["PENDING", "IN_PROGRESS", "COMPLETED", "FAILED"]).optional(),
  isGlitched: z.boolean().optional(),
});

type InsertMission = z.infer<typeof insertMissionSchema>;

// Mock data for demonstration
const mockSources = [
  { name: "Weather", icon: "🌤️", status: "online" as const, lastUpdated: new Date(Date.now() - 2 * 60000) },
  { name: "GitHub", icon: "💻", status: "online" as const, lastUpdated: new Date(Date.now() - 10 * 60000) },
  { name: "News", icon: "📰", status: "online" as const, lastUpdated: new Date(Date.now() - 1 * 60000) },
  { name: "Exchange", icon: "💱", status: "stale" as const, lastUpdated: new Date(Date.now() - 20 * 60000) },
];

const mockAnomalies = [
  { type: "warning" as const, icon: "⚠️", message: "GitHub issues spike: 15 → 23" },
  { type: "info" as const, icon: "🌧️", message: "Weather risk: Rain expected 14:00" },
];

const mockSummary = {
  riskLevel: "medium" as const,
  energyLevel: "high" as const,
  focusScore: 0.87,
};

export default function Dashboard() {
  const { data: missions, isLoading: loadingMissions } = useMissions();
  const { data: metrics } = useMetrics();
  const { data: vitals } = useSystemVitals();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedMission, setSelectedMission] = useState<any>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  
  // Filter state
  const [category, setCategory] = useState<FilterCategory>("all");
  const [priority, setPriority] = useState<FilterPriority>("all");
  const [status, setStatus] = useState<FilterStatus>("all");
  const [deadline, setDeadline] = useState<FilterDeadline>("all");
  const [sortBy, setSortBy] = useState<SortOption>("priority");

  // Run state (mock)
  const [currentRunId, setCurrentRunId] = useState(15);
  const [runTimestamp, setRunTimestamp] = useState(new Date());
  const [contextAge, setContextAge] = useState(new Date(Date.now() - 3 * 60000));
  const [isLoading, setIsLoading] = useState(false);

  // Helper to find metric value by name
  const getMetric = (name: string) => metrics?.find(m => m.name === name);
  const cacheMetric = getMetric("Cache Hit Rate");
  const computeMetric = getMetric("Compute Time");

  const form = useForm<InsertMission>({
    resolver: zodResolver(insertMissionSchema),
    defaultValues: {
      title: "",
      priority: "NORMAL",
      category: "SYSTEM",
      status: "PENDING",
      isGlitched: false,
    },
  });

  const createMission = useCreateMission();

  const onSubmit = (data: InsertMission) => {
    createMission.mutate(data, {
      onSuccess: () => {
        setIsDialogOpen(false);
        form.reset();
      }
    });
  };

  // Filter and sort missions
  const filteredMissions = useMemo(() => {
    if (!missions) return [];
    
    let result = [...missions];

    // Apply filters
    if (category !== "all") {
      result = result.filter(m => m.category?.toLowerCase() === category);
    }
    if (priority !== "all") {
      result = result.filter(m => m.priority?.toLowerCase() === priority);
    }
    if (status !== "all") {
      const statusMap: Record<FilterStatus, string> = {
        all: "",
        planned: "PENDING",
        in_progress: "IN_PROGRESS",
        completed: "COMPLETED",
        failed: "FAILED",
      };
      result = result.filter(m => m.status === statusMap[status]);
    }
    if (deadline !== "all") {
      result = result.filter(m => {
        if (!m.dueAt) return deadline === "all";
        const dueDate = new Date(m.dueAt);
        switch (deadline) {
          case "today": return isToday(dueDate);
          case "tomorrow": return isTomorrow(dueDate);
          case "week": return isThisWeek(dueDate);
          default: return true;
        }
      });
    }

    // Apply sorting
    const priorityOrder = { CRITICAL: 0, HIGH: 1, NORMAL: 2, LOW: 3 };
    result.sort((a, b) => {
      switch (sortBy) {
        case "priority":
          return (priorityOrder[a.priority as keyof typeof priorityOrder] || 2) - 
                 (priorityOrder[b.priority as keyof typeof priorityOrder] || 2);
        case "deadline":
          if (!a.dueAt && !b.dueAt) return 0;
          if (!a.dueAt) return 1;
          if (!b.dueAt) return -1;
          return new Date(a.dueAt).getTime() - new Date(b.dueAt).getTime();
        case "energy":
          return (a.energyRequired || 50) - (b.energyRequired || 50);
        default:
          return 0;
      }
    });

    return result;
  }, [missions, category, priority, status, deadline, sortBy]);

  const resetFilters = () => {
    setCategory("all");
    setPriority("all");
    setStatus("all");
    setDeadline("all");
  };

  const handleIngestContext = async () => {
    setIsLoading(true);
    // Simulate API call
    await new Promise(r => setTimeout(r, 1000));
    setContextAge(new Date());
    setIsLoading(false);
  };

  const handleGenerateRun = async () => {
    setIsLoading(true);
    // Simulate API call
    await new Promise(r => setTimeout(r, 1500));
    setCurrentRunId(prev => prev + 1);
    setRunTimestamp(new Date());
    setIsLoading(false);
  };

  const handleStartMission = (mission: any) => {
    // TODO: Call API to update mission status
    console.log("Starting mission:", mission.id);
  };

  const handleCompleteMission = (mission: any) => {
    // TODO: Call API to update mission status
    console.log("Completing mission:", mission.id);
  };

  return (
    <Layout>
      {/* Dashboard Header with Run Badge & Context Age */}
      <DashboardHeader
        currentRunId={currentRunId}
        runTimestamp={runTimestamp}
        contextAge={contextAge}
        sources={mockSources}
        onIngestContext={handleIngestContext}
        onGenerateRun={handleGenerateRun}
        isLoading={isLoading}
      />

      <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-6 gap-4">
        <div>
          <h2 className="text-4xl font-display font-bold text-white tracking-tighter mb-2 text-glow">
            TODAY'S MISSIONS
          </h2>
          <div className="flex items-center gap-2 text-primary font-mono text-sm">
            <span className="w-2 h-2 bg-primary rounded-full animate-pulse" />
            {filteredMissions.length} missions active
            <span className="text-muted-foreground ml-2">
              {format(new Date(), "yyyy-MM-dd")}
            </span>
          </div>
        </div>

        <div className="flex gap-4">
          <CyberCard className="py-2 px-4 min-w-[140px]" glowColor="secondary">
            <div className="text-xs text-muted-foreground mb-1 font-mono uppercase">Compute Time</div>
            <div className="text-2xl font-mono text-secondary font-bold tabular-nums">
              {computeMetric?.value || "0ms"}
            </div>
          </CyberCard>
          
          <CyberCard className="py-2 px-4 min-w-[140px]" glowColor={cacheMetric?.status === 'HIT' ? 'accent' : 'destructive'}>
             <div className="text-xs text-muted-foreground mb-1 font-mono uppercase">Cache Status</div>
             <div className="flex items-center gap-2">
               <div className={`w-3 h-3 rounded-full ${cacheMetric?.status === 'HIT' ? 'bg-accent animate-pulse' : 'bg-destructive'}`} />
               <span className={`text-2xl font-mono font-bold ${cacheMetric?.status === 'HIT' ? 'text-accent' : 'text-destructive'}`}>
                 {cacheMetric?.status || "Checking..."}
               </span>
             </div>
          </CyberCard>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Column: System Harmonics */}
        <div className="space-y-6">
          <SystemHarmonics
            sources={mockSources}
            anomalies={mockAnomalies}
            summary={mockSummary}
          />
        </div>

        {/* Right Column: Mission List with Filters */}
        <div className="lg:col-span-3 space-y-4">
          {/* Filter Bar */}
          <FilterBar
            category={category}
            priority={priority}
            status={status}
            deadline={deadline}
            sortBy={sortBy}
            onCategoryChange={setCategory}
            onPriorityChange={setPriority}
            onStatusChange={setStatus}
            onDeadlineChange={setDeadline}
            onSortChange={setSortBy}
            onReset={resetFilters}
          />

          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <Terminal className="w-5 h-5 text-primary" />
              ACTIVE MISSIONS
              <span className="text-sm font-normal text-muted-foreground ml-2">
                ({filteredMissions.length} shown)
              </span>
            </h3>
            
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-primary/20 hover:bg-primary/40 text-primary border border-primary/50 font-mono">
                  <Plus className="w-4 h-4 mr-2" />
                  NEW MISSION
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-black/95 border-primary/20 text-white font-mono">
                <DialogHeader>
                  <DialogTitle className="text-primary tracking-widest">INITIALIZE NEW MISSION</DialogTitle>
                </DialogHeader>
                <Form {...form}>
                  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    <FormField
                      control={form.control}
                      name="title"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>MISSION DESIGNATION</FormLabel>
                          <FormControl>
                            <Input {...field} className="bg-white/5 border-primary/20 text-primary focus:border-primary" placeholder="ENTER TITLE..." />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <div className="grid grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="priority"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>PRIORITY LEVEL</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger className="bg-white/5 border-primary/20 text-white">
                                  <SelectValue placeholder="Select priority" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent className="bg-black border-primary/20 text-white">
                                <SelectItem value="LOW">LOW</SelectItem>
                                <SelectItem value="NORMAL">NORMAL</SelectItem>
                                <SelectItem value="HIGH">HIGH</SelectItem>
                                <SelectItem value="CRITICAL">CRITICAL</SelectItem>
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="category"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>CATEGORY</FormLabel>
                            <FormControl>
                              <Input {...field} className="bg-white/5 border-primary/20 text-white" />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                    <Button type="submit" disabled={createMission.isPending} className="w-full bg-primary hover:bg-primary/80 text-black font-bold">
                      {createMission.isPending ? "INITIALIZING..." : "INITIATE MISSION"}
                    </Button>
                  </form>
                </Form>
              </DialogContent>
            </Dialog>
          </div>

          <div className="grid gap-4">
            {loadingMissions ? (
               <div className="text-primary/50 font-mono animate-pulse">Scanning database for active missions...</div>
            ) : filteredMissions.length === 0 ? (
               <div className="text-muted-foreground font-mono p-8 border border-dashed border-white/10 rounded text-center">
                 {missions?.length === 0 ? "NO ACTIVE MISSIONS DETECTED" : "NO MISSIONS MATCH CURRENT FILTERS"}
               </div>
            ) : (
               filteredMissions.map((mission) => (
                 <motion.div
                   key={mission.id}
                   initial={{ opacity: 0, y: 10 }}
                   animate={{ opacity: 1, y: 0 }}
                   transition={{ duration: 0.2 }}
                 >
                   <CyberCard 
                     className={cn(
                       "flex flex-col md:flex-row md:items-center justify-between gap-4 p-4",
                       mission.isGlitched && "animate-pulse border-red-500/50"
                     )}
                     glowColor={
                       mission.priority === 'CRITICAL' ? 'destructive' : 
                       mission.priority === 'HIGH' ? 'secondary' : 'primary'
                     }
                   >
                     <div className="flex items-center gap-4">
                       <div className={cn(
                         "w-1 h-16 rounded-full",
                         mission.priority === 'CRITICAL' ? 'bg-destructive shadow-[0_0_10px_rgba(239,68,68,0.8)]' : 
                         mission.priority === 'HIGH' ? 'bg-secondary shadow-[0_0_10px_rgba(188,19,254,0.8)]' : 
                         'bg-primary shadow-[0_0_10px_rgba(0,243,255,0.8)]'
                       )} />
                       
                       <div>
                         <div className="flex items-center gap-2 mb-1">
                           <span className="text-xs font-bold px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-muted-foreground">
                             {mission.category}
                           </span>
                           {mission.isGlitched && (
                             <span className="text-xs font-bold px-1.5 py-0.5 rounded bg-red-500/20 text-red-500 border border-red-500/50 animate-pulse">
                               GLITCH DETECTED
                             </span>
                           )}
                         </div>
                         <h4 className="text-lg font-bold text-white tracking-wide">{mission.title}</h4>
                         <div className="flex items-center gap-4 text-xs font-mono text-muted-foreground mt-1">
                           <span className="flex items-center gap-1">
                             <Clock className="w-3 h-3" />
                             {mission.createdAt ? format(new Date(mission.createdAt), "HH:mm:ss") : 'Unknown'}
                           </span>
                           <span>ID: #{mission.id.toString().padStart(4, '0')}</span>
                           {mission.score && (
                             <span className="text-primary">Score: {(mission.score * 100).toFixed(0)}</span>
                           )}
                         </div>
                       </div>
                     </div>

                     <div className="flex items-center gap-3">
                       <div className="text-right hidden md:block">
                         <div className="text-[10px] uppercase text-muted-foreground">Status</div>
                         <div className={cn(
                           "font-bold font-mono",
                           mission.status === 'COMPLETED' ? 'text-accent' : 
                           mission.status === 'IN_PROGRESS' ? 'text-secondary' : 'text-primary'
                         )}>
                           {mission.status}
                         </div>
                       </div>
                       
                       {/* Quick Actions */}
                       {mission.status === 'PENDING' && (
                         <Button 
                           size="sm" 
                           variant="outline" 
                           className="border-accent/50 text-accent hover:bg-accent/20"
                           onClick={() => handleStartMission(mission)}
                         >
                           <Play className="w-3 h-3 mr-1" />
                           START
                         </Button>
                       )}
                       {mission.status === 'IN_PROGRESS' && (
                         <Button 
                           size="sm" 
                           variant="outline" 
                           className="border-accent/50 text-accent hover:bg-accent/20"
                           onClick={() => handleCompleteMission(mission)}
                         >
                           <CheckCircle className="w-3 h-3 mr-1" />
                           DONE
                         </Button>
                       )}
                       
                       <Button 
                         size="sm" 
                         variant="outline" 
                         className="border-white/10 hover:bg-white/5 hover:text-white"
                         onClick={() => {
                           setSelectedMission(mission);
                           setIsDetailOpen(true);
                         }}
                       >
                         DETAILS
                       </Button>
                     </div>
                   </CyberCard>
                 </motion.div>
               ))
            )}
          </div>
        </div>
      </div>

      <TaskDetailDialog
        mission={selectedMission}
        open={isDetailOpen}
        onOpenChange={setIsDetailOpen}
      />
    </Layout>
  );
}
