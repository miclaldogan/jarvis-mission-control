import { Layout } from "@/components/Layout";
import { CyberCard } from "@/components/CyberCard";
import { useContextItems } from "@/hooks/use-context";
import { 
  CloudRain, 
  Github, 
  Newspaper, 
  Wind, 
  Thermometer, 
  CalendarDays,
  ExternalLink,
  GitPullRequest
} from "lucide-react";
import { 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip
} from "recharts";

export default function Context() {
  const { data: context, isLoading } = useContextItems();

  // Mock data for charts since it's "Context" visualization
  const radarData = [
    { subject: 'CPU', A: 120, fullMark: 150 },
    { subject: 'RAM', A: 98, fullMark: 150 },
    { subject: 'DISK', A: 86, fullMark: 150 },
    { subject: 'NET', A: 99, fullMark: 150 },
    { subject: 'GPU', A: 85, fullMark: 150 },
    { subject: 'AI', A: 65, fullMark: 150 },
  ];

  const areaData = [
    { name: '00:00', uv: 4000, pv: 2400 },
    { name: '04:00', uv: 3000, pv: 1398 },
    { name: '08:00', uv: 2000, pv: 9800 },
    { name: '12:00', uv: 2780, pv: 3908 },
    { name: '16:00', uv: 1890, pv: 4800 },
    { name: '20:00', uv: 2390, pv: 3800 },
    { name: '23:59', uv: 3490, pv: 4300 },
  ];

  return (
    <Layout>
      <div className="mb-8">
        <h2 className="text-4xl font-display font-bold text-white tracking-tighter mb-2 text-glow">
          GLOBAL CONTEXT
        </h2>
        <p className="text-primary/60 font-mono text-sm max-w-2xl">
          Aggregating external data streams for situational awareness. Weather patterns, repository activity, and global news feeds synced.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Weather Card */}
        <CyberCard title="ENVIRONMENT" glowColor="primary" className="h-64 flex flex-col">
          {context?.weather ? (
            <div className="flex-1 flex flex-col justify-between">
               <div className="flex items-center justify-between">
                  <div className="text-5xl font-bold text-white">{context.weather.temp_c}°C</div>
                  <CloudRain className="w-16 h-16 text-primary opacity-80" />
               </div>
               <div className="grid grid-cols-2 gap-4 mt-4">
                 <div className="flex items-center gap-2 text-muted-foreground">
                   <Wind className="w-4 h-4" />
                   <span className="text-sm font-mono">{context.weather.condition}</span>
                 </div>
                 <div className="flex items-center gap-2 text-muted-foreground">
                   <Thermometer className="w-4 h-4" />
                   <span className="text-sm font-mono">City: {context.weather.city}</span>
                 </div>
               </div>
               <div className="mt-4 text-xs font-mono text-primary/70 uppercase">
                 Location: {context.weather.city}
               </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground font-mono text-sm">
              OFFLINE
            </div>
          )}
        </CyberCard>

        {/* System Balance Chart */}
        <CyberCard title="SYSTEM HARMONICS" glowColor="secondary" className="h-64">
          <div className="h-full w-full -mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                <PolarGrid stroke="#333" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#666', fontSize: 10 }} />
                <PolarRadiusAxis angle={30} domain={[0, 150]} tick={false} axisLine={false} />
                <Radar
                  name="System"
                  dataKey="A"
                  stroke="#bc13fe"
                  strokeWidth={2}
                  fill="#bc13fe"
                  fillOpacity={0.3}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </CyberCard>

        {/* Github Issues */}
        <CyberCard title="REPOSITORY SYNC" glowColor="accent" className="h-64 flex flex-col">
           <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
             {githubItems.map((item, i) => (
               <div key={i} className="flex gap-3 items-start p-2 rounded hover:bg-white/5 transition-colors border border-transparent hover:border-white/10">
                 <GitPullRequest className="w-4 h-4 text-accent mt-1 shrink-0" />
                 <div>
                   <div className="text-sm font-medium text-white line-clamp-1">{item.title}</div>
                   <div className="text-xs text-muted-foreground font-mono mt-0.5">{item.content}</div>
                 </div>
               </div>
             ))}
           </div>
        </CyberCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
         {/* News Ticker */}
         <div className="lg:col-span-2">
           <CyberCard title="INTELLIGENCE FEED" glowColor="primary">
              <div className="h-[200px] overflow-y-auto space-y-4 pr-2">
                {newsItems.map((news, i) => (
                  <div key={i} className="group flex gap-4 p-3 border border-white/5 bg-black/40 rounded hover:border-primary/30 transition-all">
                    <div className="shrink-0 flex flex-col items-center justify-center w-12 h-12 bg-white/5 rounded">
                      <Newspaper className="w-6 h-6 text-primary group-hover:text-white transition-colors" />
                    </div>
                    <div>
                      <h4 className="font-bold text-white text-sm group-hover:text-primary transition-colors">{news.title}</h4>
                      <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{news.content}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-[10px] font-mono text-primary/50 uppercase">{news.metadata?.source || 'UNKNOWN SOURCE'}</span>
                        <ExternalLink className="w-3 h-3 text-muted-foreground hover:text-white cursor-pointer" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
           </CyberCard>
         </div>

         {/* Calendar/Schedule */}
         <CyberCard title="SCHEDULE" glowColor="secondary">
            <div className="space-y-4">
              {calendarItems.map((item, i) => (
                <div key={i} className="flex gap-3">
                   <div className="flex flex-col items-center justify-center w-12 p-2 bg-secondary/10 rounded border border-secondary/20">
                      <span className="text-[10px] text-secondary font-bold uppercase">{item.metadata?.date ? format(new Date(item.metadata.date), 'MMM') : 'NOV'}</span>
                      <span className="text-lg font-bold text-white">{item.metadata?.date ? format(new Date(item.metadata.date), 'dd') : '14'}</span>
                   </div>
                   <div>
                     <div className="font-bold text-white text-sm">{item.title}</div>
                     <div className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                       <Clock className="w-3 h-3" />
                       {item.metadata?.time || '09:00 AM'}
                     </div>
                   </div>
                </div>
              ))}
            </div>
         </CyberCard>
      </div>
      
      {/* Network Traffic Chart */}
      <div className="mt-8">
        <CyberCard title="NETWORK TRAFFIC ANALYSIS" subtitle="INBOUND / OUTBOUND PACKET VOLUME" glowColor="accent">
          <div className="h-[300px] w-full mt-4">
             <ResponsiveContainer width="100%" height="100%">
               <AreaChart data={areaData}>
                 <defs>
                   <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
                     <stop offset="5%" stopColor="#00f3ff" stopOpacity={0.3}/>
                     <stop offset="95%" stopColor="#00f3ff" stopOpacity={0}/>
                   </linearGradient>
                   <linearGradient id="colorPv" x1="0" y1="0" x2="0" y2="1">
                     <stop offset="5%" stopColor="#bc13fe" stopOpacity={0.3}/>
                     <stop offset="95%" stopColor="#bc13fe" stopOpacity={0}/>
                   </linearGradient>
                 </defs>
                 <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
                 <XAxis dataKey="name" stroke="#666" tick={{fontSize: 12, fontFamily: 'monospace'}} />
                 <YAxis stroke="#666" tick={{fontSize: 12, fontFamily: 'monospace'}} />
                 <Tooltip 
                   contentStyle={{ backgroundColor: '#0a0a0f', borderColor: '#333', color: '#fff' }} 
                   itemStyle={{ fontFamily: 'monospace' }}
                 />
                 <Area type="monotone" dataKey="uv" stroke="#00f3ff" fillOpacity={1} fill="url(#colorUv)" />
                 <Area type="monotone" dataKey="pv" stroke="#bc13fe" fillOpacity={1} fill="url(#colorPv)" />
               </AreaChart>
             </ResponsiveContainer>
          </div>
        </CyberCard>
      </div>
    </Layout>
  );
}
