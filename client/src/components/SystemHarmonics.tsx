import { CyberCard } from "@/components/CyberCard";
import { Badge } from "@/components/ui/badge";
import { formatDistanceToNow } from "date-fns";
import { Activity, AlertTriangle, CloudRain, TrendingUp, CheckCircle, XCircle, Clock } from "lucide-react";

interface ContextSource {
  name: string;
  icon: string;
  status: "online" | "failed" | "stale";
  lastUpdated: Date | null;
}

interface Anomaly {
  type: "warning" | "info" | "error";
  icon: string;
  message: string;
}

interface ContextSummary {
  riskLevel: "low" | "medium" | "high";
  energyLevel: "low" | "medium" | "high";
  focusScore: number;
}

interface SystemHarmonicsProps {
  sources: ContextSource[];
  anomalies: Anomaly[];
  summary: ContextSummary;
}

export function SystemHarmonics({ sources, anomalies, summary }: SystemHarmonicsProps) {
  const getStatusColor = (status: ContextSource["status"]) => {
    switch (status) {
      case "online":
        return "text-accent";
      case "failed":
        return "text-destructive";
      case "stale":
        return "text-yellow-500";
    }
  };

  const getStatusIcon = (status: ContextSource["status"]) => {
    switch (status) {
      case "online":
        return <CheckCircle className="w-4 h-4 text-accent" />;
      case "failed":
        return <XCircle className="w-4 h-4 text-destructive" />;
      case "stale":
        return <Clock className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case "low":
        return "bg-accent/20 text-accent border-accent/30";
      case "medium":
        return "bg-yellow-500/20 text-yellow-500 border-yellow-500/30";
      case "high":
        return "bg-destructive/20 text-destructive border-destructive/30";
      default:
        return "bg-white/10 text-white border-white/20";
    }
  };

  const getEnergyColor = (level: string) => {
    switch (level) {
      case "low":
        return "bg-blue-500/20 text-blue-400 border-blue-500/30";
      case "medium":
        return "bg-primary/20 text-primary border-primary/30";
      case "high":
        return "bg-secondary/20 text-secondary border-secondary/30";
      default:
        return "bg-white/10 text-white border-white/20";
    }
  };

  return (
    <CyberCard title="System Harmonics" subtitle="CONTEXT HEALTH MONITORING" glowColor="accent">
      {/* Freshness Matrix */}
      <div className="space-y-3 mb-6">
        <h4 className="text-xs font-mono text-muted-foreground uppercase flex items-center gap-2">
          <Activity className="w-3 h-3" />
          Freshness Matrix
        </h4>
        <div className="space-y-2">
          {sources.map((source) => (
            <div
              key={source.name}
              className="flex items-center justify-between p-2 bg-white/5 rounded border border-white/10"
            >
              <div className="flex items-center gap-3">
                <span className="text-lg">{source.icon}</span>
                <span className="text-sm font-mono text-white">{source.name}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs font-mono text-muted-foreground">
                  {source.lastUpdated
                    ? formatDistanceToNow(source.lastUpdated, { addSuffix: true })
                    : "Never"}
                </span>
                {getStatusIcon(source.status)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Anomaly Alerts */}
      {anomalies.length > 0 && (
        <div className="space-y-3 mb-6">
          <h4 className="text-xs font-mono text-muted-foreground uppercase flex items-center gap-2">
            <AlertTriangle className="w-3 h-3" />
            Anomaly Alerts
          </h4>
          <div className="space-y-2">
            {anomalies.map((anomaly, idx) => (
              <div
                key={idx}
                className={`flex items-center gap-3 p-2 rounded border ${
                  anomaly.type === "error"
                    ? "bg-destructive/10 border-destructive/30"
                    : anomaly.type === "warning"
                    ? "bg-yellow-500/10 border-yellow-500/30"
                    : "bg-primary/10 border-primary/30"
                }`}
              >
                <span className="text-lg">{anomaly.icon}</span>
                <span
                  className={`text-xs font-mono ${
                    anomaly.type === "error"
                      ? "text-destructive"
                      : anomaly.type === "warning"
                      ? "text-yellow-500"
                      : "text-primary"
                  }`}
                >
                  {anomaly.message}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Context Summary */}
      <div className="space-y-3">
        <h4 className="text-xs font-mono text-muted-foreground uppercase flex items-center gap-2">
          <TrendingUp className="w-3 h-3" />
          Context Summary
        </h4>
        <div className="flex flex-wrap gap-2">
          <Badge variant="outline" className={`font-mono text-xs ${getRiskColor(summary.riskLevel)}`}>
            Risk: {summary.riskLevel.toUpperCase()}
          </Badge>
          <Badge variant="outline" className={`font-mono text-xs ${getEnergyColor(summary.energyLevel)}`}>
            Energy: {summary.energyLevel.toUpperCase()}
          </Badge>
          <Badge variant="outline" className="font-mono text-xs bg-white/10 text-white border-white/20">
            Focus: {(summary.focusScore * 100).toFixed(0)}%
          </Badge>
        </div>
      </div>
    </CyberCard>
  );
}
