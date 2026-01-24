import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Filter, ArrowUpDown, Calendar, Zap, Clock } from "lucide-react";

export type FilterCategory = "all" | "work" | "health" | "learning" | "social" | "personal";
export type FilterPriority = "all" | "critical" | "high" | "normal" | "low";
export type FilterStatus = "all" | "planned" | "in_progress" | "completed" | "failed";
export type FilterDeadline = "all" | "today" | "tomorrow" | "week";
export type SortOption = "priority" | "deadline" | "energy";

interface FilterBarProps {
  category: FilterCategory;
  priority: FilterPriority;
  status: FilterStatus;
  deadline: FilterDeadline;
  sortBy: SortOption;
  onCategoryChange: (value: FilterCategory) => void;
  onPriorityChange: (value: FilterPriority) => void;
  onStatusChange: (value: FilterStatus) => void;
  onDeadlineChange: (value: FilterDeadline) => void;
  onSortChange: (value: SortOption) => void;
  onReset: () => void;
}

export function FilterBar({
  category,
  priority,
  status,
  deadline,
  sortBy,
  onCategoryChange,
  onPriorityChange,
  onStatusChange,
  onDeadlineChange,
  onSortChange,
  onReset,
}: FilterBarProps) {
  const hasActiveFilters =
    category !== "all" || priority !== "all" || status !== "all" || deadline !== "all";

  return (
    <div className="space-y-4 p-4 bg-black/40 rounded-lg border border-white/10 mb-6">
      {/* Filter Row */}
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2 text-sm font-mono text-muted-foreground">
          <Filter className="w-4 h-4" />
          FILTERS:
        </div>

        <Select value={category} onValueChange={(v) => onCategoryChange(v as FilterCategory)}>
          <SelectTrigger className="w-[140px] bg-white/5 border-white/10 text-white font-mono text-xs">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent className="bg-black border-white/20 text-white">
            <SelectItem value="all">All Categories</SelectItem>
            <SelectItem value="work">💼 Work</SelectItem>
            <SelectItem value="health">🏃 Health</SelectItem>
            <SelectItem value="learning">📚 Learning</SelectItem>
            <SelectItem value="social">👥 Social</SelectItem>
            <SelectItem value="personal">🏠 Personal</SelectItem>
          </SelectContent>
        </Select>

        <Select value={priority} onValueChange={(v) => onPriorityChange(v as FilterPriority)}>
          <SelectTrigger className="w-[140px] bg-white/5 border-white/10 text-white font-mono text-xs">
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent className="bg-black border-white/20 text-white">
            <SelectItem value="all">All Priorities</SelectItem>
            <SelectItem value="critical">🔴 Critical</SelectItem>
            <SelectItem value="high">🟠 High</SelectItem>
            <SelectItem value="normal">🟡 Normal</SelectItem>
            <SelectItem value="low">🟢 Low</SelectItem>
          </SelectContent>
        </Select>

        <Select value={status} onValueChange={(v) => onStatusChange(v as FilterStatus)}>
          <SelectTrigger className="w-[140px] bg-white/5 border-white/10 text-white font-mono text-xs">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent className="bg-black border-white/20 text-white">
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="planned">📋 Planned</SelectItem>
            <SelectItem value="in_progress">▶️ In Progress</SelectItem>
            <SelectItem value="completed">✅ Completed</SelectItem>
            <SelectItem value="failed">❌ Failed</SelectItem>
          </SelectContent>
        </Select>

        {/* Deadline Toggle Group */}
        <ToggleGroup type="single" value={deadline} onValueChange={(v) => v && onDeadlineChange(v as FilterDeadline)}>
          <ToggleGroupItem
            value="all"
            className="text-xs font-mono data-[state=on]:bg-primary/20 data-[state=on]:text-primary"
          >
            All
          </ToggleGroupItem>
          <ToggleGroupItem
            value="today"
            className="text-xs font-mono data-[state=on]:bg-primary/20 data-[state=on]:text-primary"
          >
            <Calendar className="w-3 h-3 mr-1" />
            Today
          </ToggleGroupItem>
          <ToggleGroupItem
            value="tomorrow"
            className="text-xs font-mono data-[state=on]:bg-primary/20 data-[state=on]:text-primary"
          >
            Tomorrow
          </ToggleGroupItem>
          <ToggleGroupItem
            value="week"
            className="text-xs font-mono data-[state=on]:bg-primary/20 data-[state=on]:text-primary"
          >
            This Week
          </ToggleGroupItem>
        </ToggleGroup>

        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onReset}
            className="text-xs text-muted-foreground hover:text-white font-mono"
          >
            Clear Filters
          </Button>
        )}
      </div>

      {/* Sort Row */}
      <div className="flex items-center gap-4 pt-2 border-t border-white/10">
        <div className="flex items-center gap-2 text-sm font-mono text-muted-foreground">
          <ArrowUpDown className="w-4 h-4" />
          SORT BY:
        </div>

        <ToggleGroup type="single" value={sortBy} onValueChange={(v) => v && onSortChange(v as SortOption)}>
          <ToggleGroupItem
            value="priority"
            className="text-xs font-mono data-[state=on]:bg-secondary/20 data-[state=on]:text-secondary"
          >
            <Zap className="w-3 h-3 mr-1" />
            Priority ↓
          </ToggleGroupItem>
          <ToggleGroupItem
            value="deadline"
            className="text-xs font-mono data-[state=on]:bg-secondary/20 data-[state=on]:text-secondary"
          >
            <Clock className="w-3 h-3 mr-1" />
            Deadline ↑
          </ToggleGroupItem>
          <ToggleGroupItem
            value="energy"
            className="text-xs font-mono data-[state=on]:bg-secondary/20 data-[state=on]:text-secondary"
          >
            ⚡ Energy ↑
          </ToggleGroupItem>
        </ToggleGroup>
      </div>
    </div>
  );
}
