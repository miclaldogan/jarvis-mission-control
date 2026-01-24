import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Rocket, RefreshCw, Clock, Zap, CheckCircle, XCircle, AlertTriangle } from "lucide-react";
import { format, formatDistanceToNow } from "date-fns";

interface ContextSource {
  name: string;
  icon: string;
  status: "online" | "failed" | "stale";
  lastUpdated: Date | null;
}

interface DashboardHeaderProps {
  currentRunId: number | null;
  runTimestamp: Date | null;
  contextAge: Date | null;
  sources: ContextSource[];
  onIngestContext: () => void;
  onGenerateRun: () => void;
  isLoading?: boolean;
}

export function DashboardHeader({
  currentRunId,
  runTimestamp,
  contextAge,
  sources,
  onIngestContext,
  onGenerateRun,
  isLoading = false,
}: DashboardHeaderProps) {
  const [now, setNow] = useState(new Date());

  // Update "now" every 10 seconds for relative times
  useEffect(() => {
    const interval = setInterval(() => setNow(new Date()), 10000);
    return () => clearInterval(interval);
  }, []);

  const getContextAgeStatus = () => {
    if (!contextAge) return "unknown";
    const ageMinutes = (now.getTime() - contextAge.getTime()) / 60000;
    if (ageMinutes < 5) return "fresh";
    if (ageMinutes < 15) return "stale";
    return "expired";
  };

  const ageStatus = getContextAgeStatus();
  const onlineSources = sources.filter((s) => s.status === "online").length;

  return (
    <div className="flex flex-wrap items-center justify-between gap-4 mb-6 p-4 bg-black/40 rounded-lg border border-primary/20">
      {/* Run Badge */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-3 px-4 py-2 bg-primary/10 rounded-lg border border-primary/30">
          <Rocket className="w-5 h-5 text-primary" />
          <div>
            <div className="text-[10px] uppercase text-primary/60 font-mono">Current Run</div>
            <div className="text-lg font-bold text-primary font-mono">
              #{currentRunId?.toString().padStart(2, "0") || "--"}
            </div>
          </div>
          {runTimestamp && (
            <div className="text-xs text-muted-foreground font-mono border-l border-primary/20 pl-3">
              {format(runTimestamp, "HH:mm:ss")}
            </div>
          )}
        </div>

        {/* Context Age */}
        <div
          className={`flex items-center gap-3 px-4 py-2 rounded-lg border ${
            ageStatus === "fresh"
              ? "bg-accent/10 border-accent/30"
              : ageStatus === "stale"
              ? "bg-yellow-500/10 border-yellow-500/30"
              : "bg-destructive/10 border-destructive/30"
          }`}
        >
          <Clock
            className={`w-5 h-5 ${
              ageStatus === "fresh"
                ? "text-accent"
                : ageStatus === "stale"
                ? "text-yellow-500"
                : "text-destructive"
            }`}
          />
          <div>
            <div
              className={`text-[10px] uppercase font-mono ${
                ageStatus === "fresh"
                  ? "text-accent/60"
                  : ageStatus === "stale"
                  ? "text-yellow-500/60"
                  : "text-destructive/60"
              }`}
            >
              Context Age
            </div>
            <div
              className={`text-sm font-bold font-mono ${
                ageStatus === "fresh"
                  ? "text-accent"
                  : ageStatus === "stale"
                  ? "text-yellow-500"
                  : "text-destructive"
              }`}
            >
              {contextAge ? formatDistanceToNow(contextAge, { addSuffix: false }) : "Unknown"}
            </div>
          </div>
        </div>

        {/* Source Health Summary */}
        <div className="flex items-center gap-3 px-4 py-2 bg-white/5 rounded-lg border border-white/10">
          {onlineSources === sources.length ? (
            <CheckCircle className="w-5 h-5 text-accent" />
          ) : onlineSources >= sources.length / 2 ? (
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
          ) : (
            <XCircle className="w-5 h-5 text-destructive" />
          )}
          <div>
            <div className="text-[10px] uppercase text-muted-foreground font-mono">Sources</div>
            <div className="text-sm font-bold font-mono text-white">
              {onlineSources}/{sources.length} OK
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3">
        <Button
          variant="outline"
          size="sm"
          onClick={onIngestContext}
          disabled={isLoading}
          className="border-primary/50 text-primary hover:bg-primary/20 font-mono"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
          INGEST CONTEXT
        </Button>
        <Button
          size="sm"
          onClick={onGenerateRun}
          disabled={isLoading}
          className="bg-primary hover:bg-primary/80 text-black font-mono font-bold"
        >
          <Zap className="w-4 h-4 mr-2" />
          GENERATE RUN
        </Button>
      </div>
    </div>
  );
}
