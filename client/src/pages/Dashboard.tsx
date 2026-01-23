import { useMissions, useCreateMission } from "@/hooks/use-missions";
import { useMetrics } from "@/hooks/use-metrics";
import { CyberCard } from "@/components/CyberCard";
import { Layout } from "@/components/Layout";
import { 
  AlertCircle, 
  CheckCircle2, 
  Clock, 
  Database, 
  Plus, 
  Server, 
  ShieldCheck, 
  Terminal,
  Activity
} from "lucide-react";
import { format } from "date-fns";
import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { insertMissionSchema, type InsertMission } from "@shared/schema";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { motion } from "framer-motion";

export default function Dashboard() {
  const { data: missions, isLoading: loadingMissions } = useMissions();
  const { data: metrics } = useMetrics();
  const [isDialogOpen, setIsDialogOpen] = useState(false);

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

  return (
    <Layout>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 gap-4">
        <div>
          <h2 className="text-4xl font-display font-bold text-white tracking-tighter mb-2 text-glow">
            MISSION CONTROL
          </h2>
          <div className="flex items-center gap-2 text-primary font-mono text-sm">
            <span className="w-2 h-2 bg-primary rounded-full animate-pulse" />
            SYSTEM STATUS: ONLINE
            <span className="text-muted-foreground ml-2">
              {format(new Date(), "yyyy-MM-dd HH:mm:ss")}
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
        {/* Left Column: System Vitals */}
        <div className="space-y-6">
          <CyberCard title="System Vitals" subtitle="REAL-TIME MONITORING">
             <div className="space-y-6">
               <div className="space-y-2">
                 <div className="flex justify-between text-xs font-mono text-primary/80">
                   <span>Mainframe CPU</span>
                   <span>78%</span>
                 </div>
                 <div className="h-2 bg-primary/10 rounded-full overflow-hidden border border-primary/20">
                   <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: "78%" }}
                      transition={{ duration: 1, ease: "easeOut" }}
                      className="h-full bg-primary shadow-[0_0_10px_rgba(0,243,255,0.5)]" 
                   />
                 </div>
               </div>

               <div className="space-y-2">
                 <div className="flex justify-between text-xs font-mono text-secondary/80">
                   <span>Memory Usage</span>
                   <span>42%</span>
                 </div>
                 <div className="h-2 bg-secondary/10 rounded-full overflow-hidden border border-secondary/20">
                   <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: "42%" }}
                      transition={{ duration: 1, ease: "easeOut", delay: 0.2 }}
                      className="h-full bg-secondary shadow-[0_0_10px_rgba(188,19,254,0.5)]" 
                   />
                 </div>
               </div>

               <div className="space-y-2">
                 <div className="flex justify-between text-xs font-mono text-accent/80">
                   <span>Network Load</span>
                   <span>12%</span>
                 </div>
                 <div className="h-2 bg-accent/10 rounded-full overflow-hidden border border-accent/20">
                   <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: "12%" }}
                      transition={{ duration: 1, ease: "easeOut", delay: 0.4 }}
                      className="h-full bg-accent shadow-[0_0_10px_rgba(34,197,94,0.5)]" 
                   />
                 </div>
               </div>
             </div>

             <div className="mt-8 grid grid-cols-2 gap-4">
               <div className="text-center p-3 bg-white/5 rounded border border-white/10">
                 <ShieldCheck className="w-6 h-6 text-accent mx-auto mb-2" />
                 <div className="text-[10px] text-muted-foreground uppercase">Firewall</div>
                 <div className="text-accent text-xs font-bold">ACTIVE</div>
               </div>
               <div className="text-center p-3 bg-white/5 rounded border border-white/10">
                 <Database className="w-6 h-6 text-primary mx-auto mb-2" />
                 <div className="text-[10px] text-muted-foreground uppercase">DB Sync</div>
                 <div className="text-primary text-xs font-bold">SYNCED</div>
               </div>
             </div>
          </CyberCard>

          <CyberCard title="Active Protocols" glowColor="secondary">
             <ul className="space-y-3 font-mono text-xs">
               <li className="flex items-center justify-between text-muted-foreground">
                 <span>NET_SCAN_V4</span>
                 <span className="text-accent">RUNNING</span>
               </li>
               <li className="flex items-center justify-between text-muted-foreground">
                 <span>DATA_MINER_01</span>
                 <span className="text-accent">RUNNING</span>
               </li>
               <li className="flex items-center justify-between text-muted-foreground">
                 <span>ENCRYPTION_LAYER</span>
                 <span className="text-secondary">UPDATING</span>
               </li>
             </ul>
          </CyberCard>
        </div>

        {/* Right Column: Mission List */}
        <div className="lg:col-span-3 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <Terminal className="w-5 h-5 text-primary" />
              ACTIVE MISSIONS
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
            ) : missions?.length === 0 ? (
               <div className="text-muted-foreground font-mono p-8 border border-dashed border-white/10 rounded text-center">
                 NO ACTIVE MISSIONS DETECTED
               </div>
            ) : (
               missions?.map((mission) => (
                 <CyberCard 
                   key={mission.id} 
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
                       </div>
                     </div>
                   </div>

                   <div className="flex items-center gap-4">
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
                     
                     <Button size="sm" variant="outline" className="border-white/10 hover:bg-white/5 hover:text-white">
                       DETAILS
                     </Button>
                   </div>
                 </CyberCard>
               ))
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
