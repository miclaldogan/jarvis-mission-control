import { Layout } from "@/components/Layout";
import { CyberCard } from "@/components/CyberCard";
import { useContextItems } from "@/hooks/use-context";
import { useSystemVitals } from "@/hooks/use-system-vitals";
import { useState, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { 
  CloudRain, 
  Github, 
  Newspaper, 
  Wind, 
  Thermometer, 
  TrendingUp,
  Navigation,
  ExternalLink,
  GitPullRequest,
  DollarSign,
  Car
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
  // City selector state (localStorage persistence)
  const [selectedCity, setSelectedCity] = useState<string>(() => {
    return localStorage.getItem('jarvis-selected-city') || 'Istanbul';
  });

  const queryClient = useQueryClient();
  const { data: context, isLoading, refetch } = useContextItems(selectedCity);
  const { data: vitals } = useSystemVitals();

  const displaySource = (source: string) => {
    // Avoid confusion with the "NETWORK TRAFFIC" chart (system vitals).
    if (source === 'traffic') return 'commute';
    return source;
  };

  const [nextRefreshAt, setNextRefreshAt] = useState<number>(() => Date.now() + 10 * 60 * 1000);
  const [secondsLeft, setSecondsLeft] = useState<number>(10 * 60);
  const [contextCache, setContextCache] = useState<string>("");

  const [networkSeries, setNetworkSeries] = useState<Array<{ name: string; uv: number; pv: number }>>([]);

  useEffect(() => {
    // Align countdown with the hook's 10-minute refetch cadence.
    setNextRefreshAt(Date.now() + 10 * 60 * 1000);
  }, [selectedCity]);

  useEffect(() => {
    const id = window.setInterval(() => {
      const left = Math.max(0, Math.floor((nextRefreshAt - Date.now()) / 1000));
      setSecondsLeft(left);
    }, 1000);
    return () => window.clearInterval(id);
  }, [nextRefreshAt]);

  const forceRefreshNow = async () => {
    const url = new URL(`/api/v1/context`, window.location.origin);
    url.searchParams.set("refresh", "true");
    url.searchParams.set("_ts", String(Date.now()));
    if (selectedCity) url.searchParams.set("city", selectedCity);

    const res = await fetch(url.toString(), { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to refresh context");

    const cache = res.headers.get("X-Cache") || "";
    setContextCache(cache);

    const json = await res.json();
    queryClient.setQueryData(["context", selectedCity], json.data);
    setNextRefreshAt(Date.now() + 10 * 60 * 1000);
  };

  useEffect(() => {
    // Capture cache header for normal (refresh=false) fetches as well.
    // We can't read headers from react-query's internal fetch result, so do a light HEAD-like fetch once per load.
    (async () => {
      try {
        const url = new URL(`/api/v1/context`, window.location.origin);
        url.searchParams.set("refresh", "false");
        if (selectedCity) url.searchParams.set("city", selectedCity);
        const res = await fetch(url.toString(), { cache: "no-store" });
        if (res.ok) setContextCache(res.headers.get("X-Cache") || "");
      } catch {
        // ignore
      }
    })();
  }, [selectedCity]);

  useEffect(() => {
    localStorage.setItem('jarvis-selected-city', selectedCity);
  }, [selectedCity]);

  const cities = ['Istanbul', 'Ankara', 'Izmir', 'Antalya'];

  // Real system vitals radar data
  const radarData = vitals ? [
    { subject: 'CPU', A: vitals.cpu_percent, fullMark: 100 },
    { subject: 'RAM', A: vitals.memory_percent, fullMark: 100 },
    { subject: 'DISK', A: vitals.disk_percent, fullMark: 100 },
    { subject: 'NET', A: Math.min(vitals.network_sent_mbps + vitals.network_recv_mbps, 100), fullMark: 100 },
  ] : [
    { subject: 'CPU', A: 0, fullMark: 100 },
    { subject: 'RAM', A: 0, fullMark: 100 },
    { subject: 'DISK', A: 0, fullMark: 100 },
    { subject: 'NET', A: 0, fullMark: 100 },
  ];

  useEffect(() => {
    if (!vitals) return;

    const ts = vitals.timestamp ? new Date(vitals.timestamp) : new Date();
    const label = ts.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });

    const inbound = Number(vitals.network_recv_mbps ?? 0);
    const outbound = Number(vitals.network_sent_mbps ?? 0);

    setNetworkSeries((prev) => {
      const next = [...prev, { name: label, uv: inbound, pv: outbound }];
      // Keep a short rolling window for readability.
      return next.slice(-30);
    });
  }, [vitals]);

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
                  <div className="text-5xl font-bold text-white">{context.weather.temp_c ?? '--'}°C</div>
                  <CloudRain className="w-16 h-16 text-primary opacity-80" />
               </div>
               <div className="grid grid-cols-2 gap-4 mt-4">
                 <div className="flex items-center gap-2 text-muted-foreground">
                   <Wind className="w-4 h-4" />
                   <span className="text-sm font-mono">{context.weather.condition ?? 'unknown'}</span>
                 </div>
                 <div className="flex items-center gap-2 text-muted-foreground">
                   <Thermometer className="w-4 h-4" />
                   <span className="text-sm font-mono">Feels like {context.weather.temp_c ?? '--'}°C</span>
                 </div>
               </div>
               {/* City Selector */}
               <div className="mt-4">
                 <label className="block text-xs font-mono text-primary/70 uppercase mb-2">Location</label>
                 <select
                   value={selectedCity}
                   onChange={(e) => setSelectedCity(e.target.value)}
                   className="w-full bg-black/80 border border-primary/50 text-primary font-mono text-sm px-3 py-2 rounded hover:border-primary/80 focus:border-primary focus:outline-none transition-all cursor-pointer"
                 >
                   {cities.map(city => (
                     <option key={city} value={city} className="bg-black text-primary">
                       ⚡ {city}
                     </option>
                   ))}
                 </select>
               </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground font-mono text-sm">
              {context?.sources_skipped?.find(s => s.source === 'weather') ? 'SKIPPED' : 'OFFLINE'}
            </div>
          )}
        </CyberCard>

        {/* System Vitals Radar */}
        <CyberCard title="SYSTEM VITALS" glowColor="secondary" className="h-64">
          <div className="h-full w-full -mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(188,19,254,0.2)" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: 'rgba(188,19,254,0.7)', fontSize: 10 }} />
                <PolarRadiusAxis angle={90} domain={[0, 150]} tick={{ fill: 'rgba(188,19,254,0.5)', fontSize: 10 }} />
                <Radar name="System Load" dataKey="A" stroke="#bc13fe" fill="#bc13fe" fillOpacity={0.3} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </CyberCard>

        {/* GitHub Activity */}
        <CyberCard title="REPOSITORY" glowColor="accent" className="h-64 flex flex-col">
          {context?.github ? (
            <div className="flex-1 flex flex-col justify-between">
              <div className="flex items-center gap-4">
                <Github className="w-12 h-12 text-accent opacity-80" />
                <div>
                  <a
                    className="font-mono text-white text-lg font-bold inline-flex items-center gap-2 hover:text-accent transition-colors"
                    href={`https://github.com/${context.github.owner}/${context.github.repo}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    title="Open on GitHub"
                  >
                    {context.github.owner}/{context.github.repo}
                    <ExternalLink className="w-4 h-4 opacity-80" />
                  </a>
                  <div className="text-xs text-muted-foreground">Repository Status</div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 mt-4">
                <div className="p-3 bg-white/5 rounded border border-accent/20">
                  <div className="text-2xl font-bold text-accent">{context.github.open_issues}</div>
                  <div className="text-xs text-muted-foreground font-mono uppercase">Open Issues</div>
                </div>
                <div className="p-3 bg-white/5 rounded border border-accent/20">
                  <div className="text-2xl font-bold text-accent">{context.github.open_prs}</div>
                  <div className="text-xs text-muted-foreground font-mono uppercase flex items-center gap-1">
                    <GitPullRequest className="w-3 h-3" />
                    Pull Requests
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground font-mono text-sm">
              {context?.sources_skipped?.find(s => s.source === 'github') ? 'SKIPPED' : 'OFFLINE'}
            </div>
          )}
        </CyberCard>
      </div>

      {/* News + Exchange + Traffic Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* News Ticker */}
        <div className="lg:col-span-2 h-[360px]">
          <CyberCard title="INTELLIGENCE FEED" glowColor="primary" className="h-full">
            <div className="flex items-center justify-between mb-3">
              <div className="text-xs font-mono text-muted-foreground">
                Next refresh in {String(Math.floor(secondsLeft / 60)).padStart(2, "0")}:{String(secondsLeft % 60).padStart(2, "0")}
                {contextCache ? ` • cache=${contextCache}` : ""}
                {context?.observed_at ? ` • observed=${new Date(context.observed_at).toLocaleTimeString()}` : ""}
              </div>
              <button
                onClick={() => {
                  forceRefreshNow().catch(() => {
                    // fall back to query refetch
                    refetch();
                    setNextRefreshAt(Date.now() + 10 * 60 * 1000);
                  });
                }}
                className="text-xs font-mono text-primary hover:text-white border border-primary/30 hover:border-primary/60 px-3 py-1 rounded"
              >
                Refresh now
              </button>
            </div>
            <div className="h-[300px] overflow-y-auto space-y-3 pr-2">
              {context?.news && context.news.length > 0 ? (
                context.news.map((news, i) => (
                  <a 
                    key={i} 
                    href={news.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="group flex gap-4 p-3 border border-white/5 bg-black/40 rounded hover:border-primary/30 transition-all"
                  >
                    <div className="shrink-0 flex flex-col items-center justify-center w-12 h-12 bg-white/5 rounded">
                      <Newspaper className="w-6 h-6 text-primary group-hover:text-white transition-colors" />
                    </div>
                    <div>
                      <h4 className="font-bold text-white text-sm group-hover:text-primary transition-colors line-clamp-2">{news.title}</h4>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-[10px] font-mono text-primary/50 uppercase">Hacker News</span>
                        <ExternalLink className="w-3 h-3 text-muted-foreground group-hover:text-white transition-colors" />
                      </div>
                    </div>
                  </a>
                ))
              ) : (
                <div className="flex items-center justify-center h-full text-muted-foreground font-mono text-sm">
                  NO NEWS AVAILABLE
                </div>
              )}
            </div>
          </CyberCard>
        </div>

        {/* Exchange + Traffic + Trending */}
        <div className="space-y-6 h-[360px] flex flex-col">
          {/* Exchange Rates */}
          <CyberCard title="EXCHANGE" glowColor="secondary" className="h-full">
            {context?.exchange ? (
              <div className="flex flex-col h-full">
                <div className="flex items-center gap-2 text-xs text-muted-foreground mb-3 flex-shrink-0">
                  <DollarSign className="w-4 h-4" />
                  <span className="font-mono">Base: {context.exchange.base}</span>
                </div>
                <div className="overflow-y-auto flex-1 space-y-2 pr-2 scrollbar-thin max-h-[240px]">
                  {Object.entries(context.exchange.rates).map(([currency, rate]) => (
                    <div key={currency} className="flex justify-between items-center">
                      <span className="font-mono text-sm text-white">{currency}</span>
                      <span className="font-mono text-sm text-secondary font-bold">{typeof rate === 'number' ? rate.toFixed(4) : rate}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-muted-foreground font-mono text-sm">
                OFFLINE
              </div>
            )}
          </CyberCard>

          {/* Traffic ETA */}
          {context?.traffic && (
            <CyberCard title="COMMUTE ETA" glowColor="accent" className="h-[140px]">
              <div className="flex items-center gap-4">
                <Car className="w-10 h-10 text-accent opacity-80" />
                <div>
                  <div className="text-3xl font-bold text-accent">{context.traffic.eta_minutes} min</div>
                  <div className="text-xs text-muted-foreground font-mono">Estimated Time</div>
                </div>
              </div>
              <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
                <Navigation className="w-3 h-3" />
                <span className="font-mono">Route calculated</span>
              </div>
            </CyberCard>
          )}
        </div>
      </div>

      {/* Trending (TMDB) */}
      {context?.trending && context.trending.length > 0 && (
        <CyberCard title="TRENDING MEDIA" glowColor="primary" className="mb-8">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {context.trending.slice(0, 5).map((item, i) => (
              <a 
                key={i} 
                href={item.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="group p-4 bg-white/5 rounded border border-white/10 hover:border-primary/50 transition-all"
              >
                <TrendingUp className="w-8 h-8 text-primary mb-2 group-hover:text-white transition-colors" />
                <div className="text-sm font-mono text-white line-clamp-2">{item.title}</div>
              </a>
            ))}
          </div>
        </CyberCard>
      )}

      {/* Network Traffic Chart */}
      <CyberCard title="NETWORK TRAFFIC ANALYSIS" subtitle="INBOUND / OUTBOUND PACKET VOLUME" glowColor="accent">
        <div className="h-[300px] w-full mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={networkSeries}>
              <defs>
                <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorPv" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#bc13fe" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#bc13fe" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" stroke="rgba(0,243,255,0.5)" style={{ fontSize: 10 }} />
              <YAxis stroke="rgba(0,243,255,0.5)" style={{ fontSize: 10 }} />
              <Tooltip
                contentStyle={{ 
                  backgroundColor: 'rgba(0,0,0,0.9)', 
                  border: '1px solid rgba(0,243,255,0.3)',
                  borderRadius: '4px',
                  fontSize: '12px'
                }}
              />
              <Area type="monotone" dataKey="uv" stroke="#22c55e" fillOpacity={1} fill="url(#colorUv)" />
              <Area type="monotone" dataKey="pv" stroke="#bc13fe" fillOpacity={1} fill="url(#colorPv)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CyberCard>

      {/* Source Status Footer */}
      {context && (
        <div className="mt-8 grid grid-cols-3 gap-4 text-xs font-mono">
          <div className="p-4 bg-accent/10 border border-accent/20 rounded">
            <div className="text-accent font-bold mb-2">SOURCES ONLINE: {context.sources_ok?.length || 0}</div>
            <div className="text-muted-foreground">
              {context.sources_ok?.map(displaySource).join(', ') || 'None'}
            </div>
          </div>
          <div className="p-4 bg-destructive/10 border border-destructive/20 rounded">
            <div className="text-destructive font-bold mb-2">SOURCES FAILED: {context.sources_failed?.length || 0}</div>
            <div className="text-muted-foreground">
              {context.sources_failed?.map(f => displaySource(f.source)).join(', ') || 'None'}
            </div>
          </div>
          <div className="p-4 bg-secondary/10 border border-secondary/20 rounded">
            <div className="text-secondary font-bold mb-2">SOURCES SKIPPED: {context.sources_skipped?.length || 0}</div>
            <div className="text-muted-foreground">
              {context.sources_skipped?.map(s => displaySource(s.source)).join(', ') || 'None'}
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
