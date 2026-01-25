import { Link, useLocation } from "wouter";
import { 
  LayoutDashboard, 
  Globe, 
  FlaskConical, 
  Cpu, 
  Radio, 
  Menu,
  X
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { useSystemVitals } from "@/hooks/use-system-vitals";

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const [location] = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { data: vitals } = useSystemVitals();

  const cpu = Math.max(0, Math.min(100, Math.round(vitals?.cpu_percent ?? 0)));
  const mem = Math.max(0, Math.min(100, Math.round(vitals?.memory_percent ?? 0)));

  const navItems = [
    { href: "/dashboard", label: "MISSION CONTROL", icon: LayoutDashboard },
    { href: "/context", label: "GLOBAL CONTEXT", icon: Globe },
    { href: "/lab", label: "SIMULATION LAB", icon: FlaskConical },
  ];

  return (
    <div className="min-h-screen flex flex-col md:flex-row font-mono text-sm bg-background overflow-hidden scanline">
      {/* Mobile Header */}
      <div className="md:hidden flex items-center justify-between p-4 border-b border-primary/20 bg-black/80 backdrop-blur-lg sticky top-0 z-50">
        <div className="flex items-center gap-2 text-primary">
          <Cpu className="w-6 h-6 animate-pulse" />
          <span className="font-bold tracking-widest text-lg">JARVIS.OS</span>
        </div>
        <button 
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="text-primary hover:text-white transition-colors"
        >
          {isMobileMenuOpen ? <X /> : <Menu />}
        </button>
      </div>

      {/* Sidebar Navigation */}
      <aside className={cn(
        "fixed md:relative z-40 w-full md:w-64 h-[calc(100vh-65px)] md:h-screen bg-black/90 md:bg-black/40 border-r border-primary/20 backdrop-blur-xl transition-transform duration-300 ease-in-out transform",
        isMobileMenuOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
      )}>
        <div className="p-6 hidden md:flex items-center gap-3 border-b border-primary/10">
          <div className="relative">
            <div className="absolute inset-0 bg-primary/20 blur-lg rounded-full animate-pulse"></div>
            <Cpu className="w-8 h-8 text-primary relative z-10" />
          </div>
          <div>
            <h1 className="font-bold text-xl tracking-widest text-white">JARVIS</h1>
            <p className="text-xs text-primary/60">SYSTEM ONLINE</p>
          </div>
        </div>

        <nav className="p-4 space-y-2">
          {navItems.map((item) => {
            const isActive = location === item.href;
            return (
              <Link key={item.href} href={item.href}>
                <div 
                  className={cn(
                    "group flex items-center gap-3 px-4 py-3 rounded-none border-l-2 transition-all duration-200 cursor-pointer",
                    isActive 
                      ? "border-primary bg-primary/10 text-primary shadow-[0_0_15px_rgba(0,243,255,0.2)]" 
                      : "border-transparent text-muted-foreground hover:text-white hover:bg-white/5"
                  )}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <item.icon className={cn("w-5 h-5", isActive && "animate-pulse")} />
                  <span className="font-semibold tracking-wider">{item.label}</span>
                </div>
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-6 border-t border-primary/10">
          <div className="flex items-center justify-between text-xs text-primary/50 mb-2">
            <span>CPU</span>
            <span>{cpu}%</span>
          </div>
          <div className="h-1 bg-primary/10 w-full rounded-full overflow-hidden">
            <div className="h-full bg-primary/50 animate-pulse" style={{ width: `${cpu}%` }}></div>
          </div>
          
          <div className="flex items-center justify-between text-xs text-secondary/50 mt-4 mb-2">
            <span>MEM</span>
            <span>{mem}%</span>
          </div>
          <div className="h-1 bg-secondary/10 w-full rounded-full overflow-hidden">
            <div className="h-full bg-secondary/50 animate-pulse" style={{ width: `${mem}%` }}></div>
          </div>

          <div className="flex items-center gap-2 mt-6 text-xs text-accent">
            <Radio className="w-3 h-3 animate-ping" />
            <span>NETWORK SECURE</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto overflow-x-hidden relative">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary via-secondary to-primary opacity-50"></div>
        <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 min-h-screen pb-20">
          {children}
        </div>
      </main>
    </div>
  );
}
