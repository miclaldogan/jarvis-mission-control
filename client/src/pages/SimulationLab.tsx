import { Layout } from "@/components/Layout";
import { CyberCard } from "@/components/CyberCard";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { Cloud, CloudRain, Sun, GitBranch, Calendar, Newspaper, Zap, ArrowRight, Plus, Minus } from "lucide-react";

interface ScenarioConfig {
  weather: 'sunny' | 'cloudy' | 'rainy';
  githubIssues: number;
  calendarEnabled: boolean;
  newsTopic: 'ai' | 'tech' | 'none';
}

interface Mission {
  id: string;
  title: string;
  priority: string;
  category: string;
  status: string;
}

export default function SimulationLab() {
  const { toast } = useToast();
  const [scenario, setScenario] = useState<ScenarioConfig>({
    weather: 'sunny',
    githubIssues: 2,
    calendarEnabled: true,
    newsTopic: 'none',
  });
  
  const [beforeMissions, setBeforeMissions] = useState<Mission[]>([]);
  const [afterMissions, setAfterMissions] = useState<Mission[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = async () => {
    setIsGenerating(true);
    
    try {
      // Generate "before" missions (default scenario)
      const beforeRes = await fetch('http://localhost:8000/api/v1/simulation/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          weather: 'sunny',
          github_issues: 2,
          calendar_busy: false,
          news_topic: null,
          limit: 5,
        }),
      });
      const beforeData = await beforeRes.json();
      setBeforeMissions(beforeData.data?.missions || []);

      // Generate "after" missions (custom scenario)
      const afterRes = await fetch('http://localhost:8000/api/v1/simulation/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          weather: scenario.weather,
          github_issues: scenario.githubIssues,
          calendar_busy: scenario.calendarEnabled,
          news_topic: scenario.newsTopic === 'none' ? null : scenario.newsTopic,
          limit: 5,
        }),
      });
      const afterData = await afterRes.json();
      setAfterMissions(afterData.data?.missions || []);

      toast({
        title: "SIMULATION COMPLETE",
        description: `Generated ${afterData.data?.missions?.length || 0} missions with custom scenario`,
        className: "bg-black border-accent text-accent",
      });
    } catch (error) {
      toast({
        title: "SIMULATION FAILED",
        description: "Failed to generate missions",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const getMissionDiff = () => {
    const beforeIds = new Set(beforeMissions.map(m => m.id));
    const afterIds = new Set(afterMissions.map(m => m.id));
    
    const added = afterMissions.filter(m => !beforeIds.has(m.id));
    const removed = beforeMissions.filter(m => !afterIds.has(m.id));
    const kept = afterMissions.filter(m => beforeIds.has(m.id));
    
    return { added, removed, kept };
  };

  const diff = beforeMissions.length > 0 ? getMissionDiff() : null;

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h2 className="text-4xl font-display font-bold text-white tracking-tighter mb-2 text-glow">
            SIMULATION LAB
          </h2>
          <p className="text-muted-foreground font-mono text-sm">
            Test how missions adapt to different context scenarios
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Scenario Controls */}
          <CyberCard className="lg:col-span-1" glowColor="primary">
            <h3 className="text-lg font-bold text-primary mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5" />
              SCENARIO CONFIG
            </h3>
            
            <div className="space-y-4">
              {/* Weather */}
              <div className="space-y-2">
                <Label className="text-xs text-muted-foreground uppercase">Weather Condition</Label>
                <Select value={scenario.weather} onValueChange={(v: any) => setScenario({...scenario, weather: v})}>
                  <SelectTrigger className="bg-white/5 border-primary/20">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-black border-primary/20">
                    <SelectItem value="sunny">
                      <div className="flex items-center gap-2">
                        <Sun className="w-4 h-4" />
                        Sunny ☀️
                      </div>
                    </SelectItem>
                    <SelectItem value="cloudy">
                      <div className="flex items-center gap-2">
                        <Cloud className="w-4 h-4" />
                        Cloudy ☁️
                      </div>
                    </SelectItem>
                    <SelectItem value="rainy">
                      <div className="flex items-center gap-2">
                        <CloudRain className="w-4 h-4" />
                        Rainy 🌧️
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* GitHub Issues */}
              <div className="space-y-2">
                <Label className="text-xs text-muted-foreground uppercase flex items-center gap-2">
                  <GitBranch className="w-3 h-3" />
                  Open GitHub Issues
                </Label>
                <div className="flex items-center gap-2">
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => setScenario({...scenario, githubIssues: Math.max(0, scenario.githubIssues - 5)})}
                    disabled={scenario.githubIssues <= 0}
                  >
                    <Minus className="w-3 h-3" />
                  </Button>
                  <span className="flex-1 text-center font-mono text-lg text-primary font-bold">
                    {scenario.githubIssues}
                  </span>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => setScenario({...scenario, githubIssues: Math.min(50, scenario.githubIssues + 5)})}
                    disabled={scenario.githubIssues >= 50}
                  >
                    <Plus className="w-3 h-3" />
                  </Button>
                </div>
              </div>

              {/* Calendar */}
              <div className="flex items-center justify-between">
                <Label className="text-xs text-muted-foreground uppercase flex items-center gap-2">
                  <Calendar className="w-3 h-3" />
                  Calendar Busy
                </Label>
                <Switch 
                  checked={scenario.calendarEnabled}
                  onCheckedChange={(checked) => setScenario({...scenario, calendarEnabled: checked})}
                />
              </div>

              {/* News Topic */}
              <div className="space-y-2">
                <Label className="text-xs text-muted-foreground uppercase flex items-center gap-2">
                  <Newspaper className="w-3 h-3" />
                  News Topic
                </Label>
                <Select value={scenario.newsTopic} onValueChange={(v: any) => setScenario({...scenario, newsTopic: v})}>
                  <SelectTrigger className="bg-white/5 border-primary/20">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-black border-primary/20">
                    <SelectItem value="none">None 📰</SelectItem>
                    <SelectItem value="ai">AI News 🤖</SelectItem>
                    <SelectItem value="tech">Tech News 💻</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Separator className="bg-primary/20" />

              <Button 
                onClick={handleGenerate} 
                disabled={isGenerating}
                className="w-full bg-primary/20 hover:bg-primary/40 text-primary border border-primary/50"
              >
                {isGenerating ? 'GENERATING...' : 'GENERATE MISSIONS'}
              </Button>
            </div>
          </CyberCard>

          {/* Results */}
          <div className="lg:col-span-2 space-y-4">
            {beforeMissions.length === 0 ? (
              <CyberCard className="text-center py-12">
                <p className="text-muted-foreground font-mono">
                  Configure scenario and click GENERATE to see mission comparison
                </p>
              </CyberCard>
            ) : (
              <>
                {/* Summary */}
                {diff && (
                  <div className="grid grid-cols-3 gap-3">
                    <CyberCard glowColor="accent" className="text-center py-3">
                      <div className="text-xs text-muted-foreground uppercase mb-1">Added</div>
                      <div className="text-2xl font-bold text-accent">{diff.added.length}</div>
                    </CyberCard>
                    <CyberCard glowColor="destructive" className="text-center py-3">
                      <div className="text-xs text-muted-foreground uppercase mb-1">Removed</div>
                      <div className="text-2xl font-bold text-destructive">{diff.removed.length}</div>
                    </CyberCard>
                    <CyberCard glowColor="primary" className="text-center py-3">
                      <div className="text-xs text-muted-foreground uppercase mb-1">Kept</div>
                      <div className="text-2xl font-bold text-primary">{diff.kept.length}</div>
                    </CyberCard>
                  </div>
                )}

                {/* Diff View */}
                <CyberCard>
                  <h3 className="text-sm font-bold text-primary uppercase mb-4">MISSION COMPARISON</h3>
                  
                  <div className="space-y-3">
                    {diff?.added.map(mission => (
                      <div key={mission.id} className="flex items-center gap-3 p-3 bg-accent/10 border border-accent/30 rounded">
                        <Plus className="w-4 h-4 text-accent" />
                        <div className="flex-1">
                          <div className="font-mono text-sm text-white">{mission.title}</div>
                          <div className="flex gap-2 mt-1">
                            <Badge className="text-xs">{mission.priority}</Badge>
                            <Badge variant="outline" className="text-xs">{mission.category}</Badge>
                          </div>
                        </div>
                        <Badge className="bg-accent/20 text-accent border-accent/50">NEW</Badge>
                      </div>
                    ))}
                    
                    {diff?.kept.map(mission => (
                      <div key={mission.id} className="flex items-center gap-3 p-3 bg-white/5 border border-white/10 rounded">
                        <ArrowRight className="w-4 h-4 text-muted-foreground" />
                        <div className="flex-1">
                          <div className="font-mono text-sm text-white/70">{mission.title}</div>
                          <div className="flex gap-2 mt-1">
                            <Badge className="text-xs opacity-70">{mission.priority}</Badge>
                            <Badge variant="outline" className="text-xs opacity-70">{mission.category}</Badge>
                          </div>
                        </div>
                      </div>
                    ))}
                    
                    {diff?.removed.map(mission => (
                      <div key={mission.id} className="flex items-center gap-3 p-3 bg-destructive/10 border border-destructive/30 rounded">
                        <Minus className="w-4 h-4 text-destructive" />
                        <div className="flex-1 opacity-50">
                          <div className="font-mono text-sm text-white line-through">{mission.title}</div>
                          <div className="flex gap-2 mt-1">
                            <Badge className="text-xs">{mission.priority}</Badge>
                            <Badge variant="outline" className="text-xs">{mission.category}</Badge>
                          </div>
                        </div>
                        <Badge className="bg-destructive/20 text-destructive border-destructive/50">REMOVED</Badge>
                      </div>
                    ))}
                  </div>
                </CyberCard>
              </>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
