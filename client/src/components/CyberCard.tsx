import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface CyberCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  subtitle?: string;
  glowColor?: "primary" | "secondary" | "accent" | "destructive";
  interactive?: boolean;
}

export function CyberCard({ 
  children, 
  className, 
  title, 
  subtitle,
  glowColor = "primary",
  interactive = false,
  ...props 
}: CyberCardProps) {
  const glowStyles = {
    primary: "border-primary/30 hover:border-primary/60 shadow-[0_0_20px_rgba(0,243,255,0.05)]",
    secondary: "border-secondary/30 hover:border-secondary/60 shadow-[0_0_20px_rgba(188,19,254,0.05)]",
    accent: "border-accent/30 hover:border-accent/60 shadow-[0_0_20px_rgba(34,197,94,0.05)]",
    destructive: "border-destructive/30 hover:border-destructive/60 shadow-[0_0_20px_rgba(239,68,68,0.05)]",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn(
        "relative bg-black/60 backdrop-blur-md border rounded-sm p-5 overflow-hidden group transition-all duration-300",
        glowStyles[glowColor],
        interactive && "cursor-pointer hover:-translate-y-1 hover:shadow-lg",
        className
      )}
      {...props}
    >
      {/* Decorative corner markers */}
      <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-current opacity-50 group-hover:opacity-100 transition-opacity" style={{ color: `var(--${glowColor})` }} />
      <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-current opacity-50 group-hover:opacity-100 transition-opacity" style={{ color: `var(--${glowColor})` }} />
      <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-current opacity-50 group-hover:opacity-100 transition-opacity" style={{ color: `var(--${glowColor})` }} />
      <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-current opacity-50 group-hover:opacity-100 transition-opacity" style={{ color: `var(--${glowColor})` }} />

      {(title || subtitle) && (
        <div className="mb-4 flex justify-between items-start border-b border-white/5 pb-2">
          <div>
            {title && <h3 className="text-lg font-bold tracking-widest text-white uppercase">{title}</h3>}
            {subtitle && <p className="text-xs text-muted-foreground font-mono mt-1">{subtitle}</p>}
          </div>
          <div className={cn("w-2 h-2 rounded-full animate-pulse", 
            glowColor === 'primary' ? 'bg-primary' : 
            glowColor === 'secondary' ? 'bg-secondary' : 
            glowColor === 'accent' ? 'bg-accent' : 'bg-destructive'
          )} />
        </div>
      )}
      
      <div className="relative z-10">
        {children}
      </div>
    </motion.div>
  );
}
