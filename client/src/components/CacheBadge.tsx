import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Clock, Database } from "lucide-react";

interface CacheBadgeProps {
  status: "HIT" | "MISS" | "BYPASS" | "UNKNOWN";
  computeTime?: number;
  className?: string;
}

export function CacheBadge({ status, computeTime, className }: CacheBadgeProps) {
  const statusColors = {
    HIT: "bg-accent/20 text-accent border-accent",
    MISS: "bg-destructive/20 text-destructive border-destructive",
    BYPASS: "bg-yellow-500/20 text-yellow-500 border-yellow-500",
    UNKNOWN: "bg-muted text-muted-foreground border-muted-foreground",
  };

  return (
    <div className={cn("flex items-center gap-2 flex-wrap", className)}>
      <Badge variant="outline" className={cn("font-mono text-xs", statusColors[status])}>
        <Database className="w-3 h-3 mr-1" />
        {status}
      </Badge>
      {computeTime !== undefined && (
        <Badge variant="outline" className="font-mono text-xs text-primary border-primary/50">
          <Clock className="w-3 h-3 mr-1" />
          {computeTime}ms
        </Badge>
      )}
    </div>
  );
}
