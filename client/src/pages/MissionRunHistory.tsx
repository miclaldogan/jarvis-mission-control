import { Layout } from "@/components/Layout";
import { CyberCard } from "@/components/CyberCard";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { Clock, Calendar, GitCompare, Eye, ChevronRight, TrendingUp } from "lucide-react";
import { useState, useEffect } from "react";
import { format } from "date-fns";

interface MissionRun {
  run_id: string;
  generated_at: string;
  context_id: string;
  mission_count: number;
  mission_ids: string[];
  preferences?: any;
  context_snapshot?: any;
}

export default function MissionRunHistory() {
  const [runs, setRuns] = useState<MissionRun[]>([]);
  const [selectedRun, setSelectedRun] = useState<MissionRun | null>(null);
  const [compareRun, setCompareRun] = useState<MissionRun | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadRuns();
  }, []);

  const loadRuns = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/missions/runs');
      const data = await res.json();
      setRuns(data.data?.runs || []);
    } catch (error) {
      toast({
        title: "FETCH FAILED",
        description: "Could not load mission runs",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const loadRunDetails = async (runId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/missions/runs/${runId}`);
      const data = await res.json();
      setSelectedRun(data.data);
    } catch (error) {
      toast({
        title: "ERROR",
        description: "Failed to load run details",
        variant: "destructive",
      });
    }
  };

  const handleCompare = (run: MissionRun) => {
    if (!selectedRun) {
      setSelectedRun(run);
      toast({
        title: "RUN SELECTED",
        description: "Select another run to compare",
        className: "bg-black border-primary text-primary",
      });
    } else if (selectedRun.run_id === run.run_id) {
      setSelectedRun(null);
      toast({
        title: "SELECTION CLEARED",
        className: "bg-black border-muted-foreground text-muted-foreground",
      });
    } else {
      setCompareRun(run);
      toast({
        title: "COMPARISON READY",
        description: `Comparing ${selectedRun.run_id} vs ${run.run_id}`,
        className: "bg-black border-accent text-accent",
      });
    }
  };

  const getComparison = () => {
    if (!selectedRun || !compareRun) return null;
    
    const set1 = new Set(selectedRun.mission_ids);
    const set2 = new Set(compareRun.mission_ids);
    
    const onlyIn1 = selectedRun.mission_ids.filter(id => !set2.has(id));
    const onlyIn2 = compareRun.mission_ids.filter(id => !set1.has(id));
    const inBoth = selectedRun.mission_ids.filter(id => set2.has(id));
    
    return { onlyIn1, onlyIn2, inBoth };
  };

  const comparison = compareRun ? getComparison() : null;

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-end justify-between">
          <div>
            <h2 className="text-4xl font-display font-bold text-white tracking-tighter mb-2 text-glow">
              MISSION RUN HISTORY
            </h2>
            <p className="text-muted-foreground font-mono text-sm">
              Track how missions evolved throughout the day
            </p>
          </div>
          <Button onClick={loadRuns} disabled={isLoading} variant="outline">
            {isLoading ? 'Loading...' : 'Refresh'}
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Run Timeline */}
          <div className="lg:col-span-1 space-y-3">
            <h3 className="text-sm font-bold text-primary uppercase flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Generation Timeline ({runs.length})
            </h3>
            
            {runs.length === 0 ? (
              <CyberCard className="text-center py-8">
                <p className="text-muted-foreground text-sm">No runs yet. Generate missions to see history.</p>
              </CyberCard>
            ) : (
              <div className="space-y-2">
                {runs.map((run, idx) => (
                  <CyberCard
                    key={run.run_id}
                    className={cn(
                      "cursor-pointer transition-all",
                      selectedRun?.run_id === run.run_id && "border-primary shadow-[0_0_20px_rgba(0,243,255,0.3)]",
                      compareRun?.run_id === run.run_id && "border-accent shadow-[0_0_20px_rgba(16,185,129,0.3)]"
                    )}
                    onClick={() => handleCompare(run)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant="outline" className="text-xs font-mono">
                            #{runs.length - idx}
                          </Badge>
                          {selectedRun?.run_id === run.run_id && (
                            <Badge className="bg-primary/20 text-primary border-primary/50 text-xs">A</Badge>
                          )}
                          {compareRun?.run_id === run.run_id && (
                            <Badge className="bg-accent/20 text-accent border-accent/50 text-xs">B</Badge>
                          )}
                        </div>
                        <div className="text-xs text-muted-foreground font-mono">
                          {format(new Date(run.generated_at), "MMM dd, HH:mm:ss")}
                        </div>
                        <div className="text-sm font-bold text-white mt-1">
                          {run.mission_count} missions
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-muted-foreground" />
                    </div>
                  </CyberCard>
                ))}
              </div>
            )}
          </div>

          {/* Details/Comparison View */}
          <div className="lg:col-span-2">
            {!selectedRun ? (
              <CyberCard className="text-center py-16">
                <GitCompare className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">
                  Click a run to view details, or select two runs to compare
                </p>
              </CyberCard>
            ) : !compareRun ? (
              <CyberCard>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-primary flex items-center gap-2">
                    <Eye className="w-5 h-5" />
                    RUN DETAILS
                  </h3>
                  <Badge className="font-mono">{selectedRun.run_id}</Badge>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="bg-white/5 p-3 rounded border border-white/10">
                    <div className="text-xs text-muted-foreground mb-1">Generated At</div>
                    <div className="text-sm font-mono text-white">
                      {format(new Date(selectedRun.generated_at), "MMM dd, yyyy HH:mm:ss")}
                    </div>
                  </div>
                  <div className="bg-white/5 p-3 rounded border border-white/10">
                    <div className="text-xs text-muted-foreground mb-1">Mission Count</div>
                    <div className="text-sm font-mono text-primary font-bold">
                      {selectedRun.mission_count}
                    </div>
                  </div>
                  <div className="bg-white/5 p-3 rounded border border-white/10 col-span-2">
                    <div className="text-xs text-muted-foreground mb-1">Context ID</div>
                    <div className="text-sm font-mono text-white">
                      {selectedRun.context_id}
                    </div>
                  </div>
                </div>

                <Separator className="my-4 bg-primary/20" />

                <h4 className="text-sm font-bold text-white uppercase mb-3">Mission IDs</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedRun.mission_ids.map(id => (
                    <Badge key={id} variant="outline" className="font-mono text-xs">
                      {id}
                    </Badge>
                  ))}
                </div>

                <div className="mt-4 p-3 bg-primary/5 border border-primary/20 rounded">
                  <p className="text-xs text-muted-foreground">
                    💡 Select another run to see how missions changed over time
                  </p>
                </div>
              </CyberCard>
            ) : (
              <CyberCard>
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-bold text-accent flex items-center gap-2">
                    <GitCompare className="w-5 h-5" />
                    RUN COMPARISON
                  </h3>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => {
                      setCompareRun(null);
                      setSelectedRun(null);
                    }}
                  >
                    Clear
                  </Button>
                </div>

                {comparison && (
                  <>
                    <div className="grid grid-cols-3 gap-3 mb-6">
                      <CyberCard glowColor="primary" className="text-center py-3">
                        <div className="text-xs text-muted-foreground uppercase mb-1">Only in A</div>
                        <div className="text-2xl font-bold text-primary">{comparison.onlyIn1.length}</div>
                      </CyberCard>
                      <CyberCard glowColor="accent" className="text-center py-3">
                        <div className="text-xs text-muted-foreground uppercase mb-1">In Both</div>
                        <div className="text-2xl font-bold text-accent">{comparison.inBoth.length}</div>
                      </CyberCard>
                      <CyberCard glowColor="secondary" className="text-center py-3">
                        <div className="text-xs text-muted-foreground uppercase mb-1">Only in B</div>
                        <div className="text-2xl font-bold text-secondary">{comparison.onlyIn2.length}</div>
                      </CyberCard>
                    </div>

                    <div className="space-y-4">
                      {comparison.onlyIn1.length > 0 && (
                        <div>
                          <h4 className="text-xs font-bold text-primary uppercase mb-2 flex items-center gap-2">
                            <TrendingUp className="w-3 h-3" />
                            Removed in Run B
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {comparison.onlyIn1.map(id => (
                              <Badge key={id} className="bg-primary/20 text-primary border-primary/50 font-mono text-xs">
                                {id}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      {comparison.inBoth.length > 0 && (
                        <div>
                          <h4 className="text-xs font-bold text-accent uppercase mb-2">Kept in Both</h4>
                          <div className="flex flex-wrap gap-2">
                            {comparison.inBoth.map(id => (
                              <Badge key={id} className="bg-accent/20 text-accent border-accent/50 font-mono text-xs">
                                {id}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      {comparison.onlyIn2.length > 0 && (
                        <div>
                          <h4 className="text-xs font-bold text-secondary uppercase mb-2 flex items-center gap-2">
                            <TrendingUp className="w-3 h-3" />
                            Added in Run B
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {comparison.onlyIn2.map(id => (
                              <Badge key={id} className="bg-secondary/20 text-secondary border-secondary/50 font-mono text-xs">
                                {id}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="mt-6 p-4 bg-accent/5 border border-accent/20 rounded">
                      <div className="flex items-start gap-3">
                        <Calendar className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                        <div>
                          <div className="text-sm font-bold text-accent mb-1">Run A</div>
                          <div className="text-xs text-muted-foreground">
                            {format(new Date(selectedRun.generated_at), "MMM dd, yyyy HH:mm:ss")} • {selectedRun.mission_count} missions
                          </div>
                        </div>
                      </div>
                      <Separator className="my-3 bg-accent/20" />
                      <div className="flex items-start gap-3">
                        <Calendar className="w-5 h-5 text-secondary flex-shrink-0 mt-0.5" />
                        <div>
                          <div className="text-sm font-bold text-secondary mb-1">Run B</div>
                          <div className="text-xs text-muted-foreground">
                            {format(new Date(compareRun.generated_at), "MMM dd, yyyy HH:mm:ss")} • {compareRun.mission_count} missions
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </CyberCard>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
