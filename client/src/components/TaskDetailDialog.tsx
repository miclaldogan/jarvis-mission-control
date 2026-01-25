import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import { Clock, Target, Zap, Calendar, CheckCircle2, XCircle, AlertCircle } from "lucide-react";
import { format } from "date-fns";

type ScoreBreakdown = Record<string, number>;

interface Mission {
  id: string;
  title: string;
  priority: string;
  priority_score?: number;
  score_breakdown?: ScoreBreakdown;
  reasons?: string[];
  category: string;
  status: string;
  created_at?: string;
  generated_at?: string;
  due_at?: string;
  tags?: string[];
  why?: string;
  evidence?: {
    sources?: string[];
    confidence?: number;
  };
}

interface TaskDetailDialogProps {
  mission: Mission | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onStatusChange?: (missionId: string, newStatus: string) => void;
  onDelete?: (missionId: string) => void;
}

export function TaskDetailDialog({ mission, open, onOpenChange, onStatusChange, onDelete }: TaskDetailDialogProps) {
  if (!mission) return null;

  const priorityColors = {
    'P0': 'text-red-500 border-red-500/50 bg-red-500/10',
    'P1': 'text-orange-500 border-orange-500/50 bg-orange-500/10',
    'P2': 'text-yellow-500 border-yellow-500/50 bg-yellow-500/10',
    'P3': 'text-green-500 border-green-500/50 bg-green-500/10',
    'CRITICAL': 'text-red-500 border-red-500/50 bg-red-500/10',
    'HIGH': 'text-orange-500 border-orange-500/50 bg-orange-500/10',
    'NORMAL': 'text-yellow-500 border-yellow-500/50 bg-yellow-500/10',
    'LOW': 'text-green-500 border-green-500/50 bg-green-500/10',
  };

  const statusColors = {
    'open': 'text-primary border-primary/50 bg-primary/10',
    'PENDING': 'text-primary border-primary/50 bg-primary/10',
    'in_progress': 'text-secondary border-secondary/50 bg-secondary/10',
    'IN_PROGRESS': 'text-secondary border-secondary/50 bg-secondary/10',
    'completed': 'text-accent border-accent/50 bg-accent/10',
    'COMPLETED': 'text-accent border-accent/50 bg-accent/10',
    'failed': 'text-destructive border-destructive/50 bg-destructive/10',
    'FAILED': 'text-destructive border-destructive/50 bg-destructive/10',
  };

  const rawBreakdown = (mission.score_breakdown || {}) as Record<string, unknown>;
  const breakdown: Record<string, number> = Object.fromEntries(
    Object.entries(rawBreakdown)
      .filter(([, v]) => typeof v === "number" && Number.isFinite(v))
      .map(([k, v]) => [k, v as number])
  );

  const totalScore = Number(mission.priority_score) ||
    Object.values(breakdown).reduce((sum, v) => sum + v, 0) || 0;

  const breakdownLooksFractional = (() => {
    const values = Object.values(breakdown);
    if (values.length === 0) return true;
    return values.every((v) => v >= 0 && v <= 1.5);
  })();

  const scoreItems: Array<{ key: string; label: string; icon: any; color: string }> = [
    { key: "base", label: "Base Score", icon: Target, color: "text-primary" },
    { key: "deadline", label: "Deadline Urgency", icon: Clock, color: "text-red-400" },
    { key: "context", label: "Context Relevance", icon: Target, color: "text-blue-400" },
    { key: "energy", label: "Energy Level", icon: Zap, color: "text-yellow-400" },
    { key: "preference", label: "User Preference", icon: Calendar, color: "text-green-400" },
    { key: "routine", label: "Routine Match", icon: Zap, color: "text-secondary" },
  ];

  const handleStatusChange = (newStatus: string) => {
    if (onStatusChange) {
      onStatusChange(mission.id, newStatus);
    }
  };

  const handleDelete = () => {
    if (onDelete) {
      onDelete(mission.id);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-black/95 border-primary/20 text-white font-mono max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <DialogTitle className="text-2xl font-bold text-primary tracking-wide mb-2">
                {mission.title}
              </DialogTitle>
              <div className="flex items-center gap-2 flex-wrap">
                <Badge className={cn("font-mono text-xs", priorityColors[mission.priority as keyof typeof priorityColors] || priorityColors['NORMAL'])}>
                  {mission.priority}
                </Badge>
                <Badge className={cn("font-mono text-xs", statusColors[mission.status as keyof typeof statusColors] || statusColors['PENDING'])}>
                  {mission.status}
                </Badge>
                <Badge variant="outline" className="font-mono text-xs">
                  {mission.category}
                </Badge>
                <span className="text-xs text-muted-foreground">ID: {mission.id}</span>
              </div>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-6 mt-6">
          {/* Score Breakdown Section */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-primary uppercase tracking-wider flex items-center gap-2">
              <Target className="w-4 h-4" />
              Priority Score Breakdown
            </h3>
            <div className="bg-white/5 border border-primary/10 rounded-lg p-4 space-y-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-muted-foreground uppercase">Total Score</span>
                <span className="text-xl font-bold text-primary">{totalScore.toFixed(3)}</span>
              </div>
              
              <Separator className="bg-primary/20" />

              <div className="space-y-3">
                {scoreItems
                  .filter((item) => typeof breakdown[item.key] === "number")
                  .map((item) => (
                    <ScoreBar
                      key={item.key}
                      label={item.label}
                      icon={item.icon}
                      value={breakdown[item.key]}
                      total={totalScore}
                      fractional={breakdownLooksFractional}
                      color={item.color}
                    />
                  ))}
              </div>
            </div>
          </div>

          {/* Why This Task Section */}
          {(mission.why || mission.reasons) && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-primary uppercase tracking-wider">
                Why This Task?
              </h3>
              <div className="bg-white/5 border border-primary/10 rounded-lg p-4 space-y-2">
                {mission.why && (
                  <p className="text-sm text-white/80">{mission.why}</p>
                )}
                {mission.reasons && mission.reasons.length > 0 && (
                  <ul className="space-y-1 mt-2">
                    {mission.reasons.map((reason, idx) => (
                      <li key={idx} className="text-xs text-muted-foreground flex items-start gap-2">
                        <span className="text-primary">▸</span>
                        <span>{reason}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          )}

          {/* Task Details */}
          <div className="grid grid-cols-2 gap-4">
            {mission.generated_at && (
              <InfoCard 
                label="Generated At" 
                value={format(new Date(mission.generated_at), "MMM dd, yyyy HH:mm:ss")}
                icon={Clock}
              />
            )}
            {mission.due_at && (
              <InfoCard 
                label="Due Date" 
                value={format(new Date(mission.due_at), "MMM dd, yyyy HH:mm:ss")}
                icon={Calendar}
              />
            )}
          </div>

          {/* Evidence */}
          {mission.evidence && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-primary uppercase tracking-wider">
                Evidence
              </h3>
              <div className="bg-white/5 border border-primary/10 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs text-muted-foreground">Confidence Score</span>
                  <span className="text-sm font-bold text-accent">
                    {((mission.evidence.confidence || 0) * 100).toFixed(0)}%
                  </span>
                </div>
                {mission.evidence.sources && mission.evidence.sources.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {mission.evidence.sources.map((source, idx) => (
                      <Badge key={idx} variant="outline" className="text-xs">
                        {source}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Tags */}
          {mission.tags && mission.tags.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-primary uppercase tracking-wider">
                Tags
              </h3>
              <div className="flex flex-wrap gap-2">
                {mission.tags.map((tag, idx) => (
                  <Badge key={idx} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <Separator className="bg-primary/20" />
          <div className="flex items-center gap-3">
            <Button
              onClick={() => handleStatusChange('IN_PROGRESS')}
              disabled={mission.status === 'IN_PROGRESS'}
              className="bg-secondary/20 hover:bg-secondary/40 text-secondary border border-secondary/50"
            >
              <AlertCircle className="w-4 h-4 mr-2" />
              Start Task
            </Button>
            <Button
              onClick={() => handleStatusChange('COMPLETED')}
              disabled={mission.status === 'COMPLETED'}
              className="bg-accent/20 hover:bg-accent/40 text-accent border border-accent/50"
            >
              <CheckCircle2 className="w-4 h-4 mr-2" />
              Complete
            </Button>
            <Button
              onClick={() => handleStatusChange('FAILED')}
              disabled={mission.status === 'FAILED'}
              variant="outline"
              className="border-destructive/50 hover:bg-destructive/10 text-destructive"
            >
              <XCircle className="w-4 h-4 mr-2" />
              Mark Failed
            </Button>

            <div className="flex-1" />

            <Button
              onClick={handleDelete}
              variant="outline"
              className="border-destructive/50 hover:bg-destructive/10 text-destructive"
            >
              Delete
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

interface ScoreBarProps {
  label: string;
  icon: React.ElementType;
  value: number;
  total: number;
  fractional: boolean;
  color: string;
}

function ScoreBar({ label, icon: Icon, value, total, fractional, color }: ScoreBarProps) {
  // Safely handle undefined/NaN values
  const safeValue = typeof value === 'number' && !isNaN(value) ? value : 0;
  const pct = fractional
    ? safeValue * 100
    : (total > 0 ? (safeValue / total) * 100 : 0);
  const percentage = pct.toFixed(0);
  
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <Icon className={cn("w-3 h-3", color)} />
          <span className="text-muted-foreground">{label}</span>
        </div>
        <span className={cn("font-bold tabular-nums", color)}>
          {safeValue.toFixed(2)} ({percentage}%)
        </span>
      </div>
      <Progress 
        value={pct} 
        className="h-2 bg-white/5"
        indicatorClassName={cn("transition-all", color.replace('text-', 'bg-'))}
      />
    </div>
  );
}

interface InfoCardProps {
  label: string;
  value: string;
  icon: React.ElementType;
}

function InfoCard({ label, icon: Icon, value }: InfoCardProps) {
  return (
    <div className="bg-white/5 border border-primary/10 rounded-lg p-3">
      <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
        <Icon className="w-3 h-3" />
        {label}
      </div>
      <div className="text-sm font-mono text-white">{value}</div>
    </div>
  );
}
