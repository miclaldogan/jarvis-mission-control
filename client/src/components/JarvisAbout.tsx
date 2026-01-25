import { CyberCard } from "@/components/CyberCard";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { motion } from "framer-motion";
import { 
  Brain, 
  Cpu, 
  Database, 
  Globe, 
  Layers, 
  Radio, 
  Shield, 
  Terminal, 
  Zap,
  Github,
  Server,
  Code2,
  Boxes,
  Activity
} from "lucide-react";

const techStack = {
  frontend: [
    { name: "React 18", icon: "⚛️", desc: "UI Framework" },
    { name: "TypeScript", icon: "📘", desc: "Type Safety" },
    { name: "Tailwind CSS", icon: "🎨", desc: "Styling" },
    { name: "Vite", icon: "⚡", desc: "Build Tool" },
    { name: "React Query", icon: "🔄", desc: "Data Fetching" },
    { name: "Framer Motion", icon: "🎬", desc: "Animations" },
  ],
  backend: [
    { name: "FastAPI", icon: "🚀", desc: "REST API Framework" },
    { name: "Python 3.11", icon: "🐍", desc: "Runtime" },
    { name: "SQLite", icon: "📦", desc: "Database" },
    { name: "Redis", icon: "⚡", desc: "Cache Layer" },
    { name: "Pydantic", icon: "✅", desc: "Validation" },
  ],
  infra: [
    { name: "Docker", icon: "🐳", desc: "Containerization" },
    { name: "Docker Compose", icon: "🔧", desc: "Orchestration" },
    { name: "Nginx", icon: "🌐", desc: "Reverse Proxy" },
  ],
};

const features = [
  {
    icon: Brain,
    title: "Autonomous Brain System",
    desc: "Signal Engine + Rule Engine + Orchestrator ile tam otonom görev üretimi",
    color: "text-purple-400",
  },
  {
    icon: Activity,
    title: "Real-time Monitoring",
    desc: "Sistem durumu, CPU, Memory, Network metrikleri anlık takip",
    color: "text-cyan-400",
  },
  {
    icon: Database,
    title: "Persistent Storage",
    desc: "SQLite + Redis hibrit storage, container restart sonrası veri korunur",
    color: "text-green-400",
  },
  {
    icon: Shield,
    title: "Explainable AI",
    desc: "Her görev için karar zinciri ve güven skoru",
    color: "text-yellow-400",
  },
  {
    icon: Zap,
    title: "High Performance",
    desc: "150+ concurrent user, 0% error rate, <50ms response time",
    color: "text-orange-400",
  },
  {
    icon: Layers,
    title: "State Machine",
    desc: "CALM → ACTIVE → OVERLOAD → RECOVERY dinamik sistem durumu",
    color: "text-pink-400",
  },
];

const tabs = [
  {
    name: "Mission Control",
    icon: Terminal,
    desc: "Ana görev yönetim paneli. Brain System'in ürettiği otomatik görevleri görüntüleyin, filtreleyin ve yönetin. Görevler öncelik skoruna göre sıralanır ve her görev için detaylı açıklama mevcuttur.",
  },
  {
    name: "Global Context",
    icon: Globe,
    desc: "Tüm veri kaynaklarının birleştirilmiş görünümü. Weather, GitHub, News, Exchange verileri anlık olarak toplanır ve görev üretimi için analiz edilir.",
  },
  {
    name: "Simulation Lab",
    icon: Radio,
    desc: "Test ve simülasyon ortamı. 1M veri üretebilir, load test yapabilir, cache performansını test edebilirsiniz. Sistemin dayanıklılığını ölçmek için idealdir.",
  },
];

export function JarvisAbout() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Hero Section */}
      <CyberCard className="p-6" glowColor="primary">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-lg bg-primary/10 border border-primary/30">
            <Brain className="w-8 h-8 text-primary" />
          </div>
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-primary tracking-wide mb-2">
              J.A.R.V.I.S. MISSION CONTROL
            </h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              <span className="text-primary font-semibold">Just A Rather Very Intelligent System</span> - 
              Akıllı görev yönetim ve otomasyon platformu. Çoklu veri kaynağından gerçek zamanlı 
              bilgi toplayarak, yapay zeka destekli kurallar ile otomatik görev oluşturur ve 
              önceliklendirir.
            </p>
          </div>
        </div>
      </CyberCard>

      {/* What is this project */}
      <CyberCard className="p-6">
        <h3 className="text-lg font-bold text-primary mb-4 flex items-center gap-2">
          <Code2 className="w-5 h-5" />
          PROJE HAKKINDA
        </h3>
        <div className="space-y-4 text-sm text-muted-foreground">
          <p>
            Bu proje, modern yazılım geliştirme pratiklerini sergileyen bir 
            <span className="text-white font-medium"> full stack demo projesidir</span>. 
            REST API mimarisi, gerçek zamanlı veri işleme, caching stratejileri ve 
            otonom karar verme sistemleri gibi ileri düzey konseptleri içerir.
          </p>
          <p>
            <span className="text-accent font-semibold">Signal Engine</span> çeşitli kaynaklardan 
            gelen verileri analiz eder ve anomalileri tespit eder. 
            <span className="text-secondary font-semibold"> Rule Engine</span> tanımlı kurallara 
            göre bu sinyalleri değerlendirir. 
            <span className="text-primary font-semibold"> Mission Orchestrator</span> ise görevleri 
            oluşturur, önceliklendirir ve sistem durumunu yönetir.
          </p>
        </div>
      </CyberCard>

      {/* Developers */}
      <CyberCard className="p-6">
        <h3 className="text-lg font-bold text-primary mb-4 flex items-center gap-2">
          <Github className="w-5 h-5" />
          GELİŞTİRİCİLER
        </h3>
        <div className="space-y-3 text-sm">
          <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-primary/10">
            <div className="text-white font-semibold">İclal Doğan</div>
            <Badge variant="outline" className="text-xs">Full-Stack Engineering</Badge>
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-primary/10">
            <div className="text-white font-semibold">Burcu Yıldırım</div>
            <Badge variant="outline" className="text-xs">Frontend Engineering</Badge>
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-primary/10">
            <div className="text-white font-semibold">Reyyan Erva Gökkaya</div>
            <Badge variant="outline" className="text-xs">Data Ingestion & Synthetic Data</Badge>
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-primary/10">
            <div className="text-white font-semibold">Merve Çaloğlu</div>
            <Badge variant="outline" className="text-xs">Data Ingestion & Synthetic Data</Badge>
          </div>
        </div>
      </CyberCard>

      {/* Core Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {features.map((feature, idx) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
          >
            <CyberCard className="p-4 h-full">
              <div className="flex items-start gap-3">
                <feature.icon className={`w-5 h-5 ${feature.color} flex-shrink-0`} />
                <div>
                  <h4 className="text-sm font-bold text-white mb-1">{feature.title}</h4>
                  <p className="text-xs text-muted-foreground">{feature.desc}</p>
                </div>
              </div>
            </CyberCard>
          </motion.div>
        ))}
      </div>

      {/* Tech Stack */}
      <CyberCard className="p-6">
        <h3 className="text-lg font-bold text-primary mb-4 flex items-center gap-2">
          <Boxes className="w-5 h-5" />
          TEKNOLOJİ STACK
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Frontend */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2 h-2 rounded-full bg-cyan-400" />
              <span className="text-sm font-semibold text-cyan-400 uppercase">Frontend</span>
            </div>
            <div className="space-y-2">
              {techStack.frontend.map((tech) => (
                <div key={tech.name} className="flex items-center gap-2 text-xs">
                  <span>{tech.icon}</span>
                  <span className="text-white font-medium">{tech.name}</span>
                  <span className="text-muted-foreground">- {tech.desc}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Backend */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2 h-2 rounded-full bg-green-400" />
              <span className="text-sm font-semibold text-green-400 uppercase">Backend</span>
            </div>
            <div className="space-y-2">
              {techStack.backend.map((tech) => (
                <div key={tech.name} className="flex items-center gap-2 text-xs">
                  <span>{tech.icon}</span>
                  <span className="text-white font-medium">{tech.name}</span>
                  <span className="text-muted-foreground">- {tech.desc}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Infrastructure */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2 h-2 rounded-full bg-orange-400" />
              <span className="text-sm font-semibold text-orange-400 uppercase">Infrastructure</span>
            </div>
            <div className="space-y-2">
              {techStack.infra.map((tech) => (
                <div key={tech.name} className="flex items-center gap-2 text-xs">
                  <span>{tech.icon}</span>
                  <span className="text-white font-medium">{tech.name}</span>
                  <span className="text-muted-foreground">- {tech.desc}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </CyberCard>

      {/* Tab Explanations */}
      <CyberCard className="p-6">
        <h3 className="text-lg font-bold text-primary mb-4 flex items-center gap-2">
          <Server className="w-5 h-5" />
          MODÜLLER
        </h3>
        <div className="space-y-4">
          {tabs.map((tab, idx) => (
            <div key={tab.name} className="flex items-start gap-4 p-3 rounded-lg bg-white/5 border border-primary/10">
              <div className="p-2 rounded bg-primary/10">
                <tab.icon className="w-5 h-5 text-primary" />
              </div>
              <div className="flex-1">
                <h4 className="text-sm font-bold text-white mb-1">{tab.name}</h4>
                <p className="text-xs text-muted-foreground">{tab.desc}</p>
              </div>
              <Badge variant="outline" className="text-xs">
                Tab {idx + 1}
              </Badge>
            </div>
          ))}
        </div>
      </CyberCard>

      {/* Architecture */}
      <CyberCard className="p-6">
        <h3 className="text-lg font-bold text-primary mb-4 flex items-center gap-2">
          <Cpu className="w-5 h-5" />
          SİSTEM MİMARİSİ
        </h3>
        <div className="font-mono text-xs bg-black/50 p-4 rounded-lg border border-primary/20 overflow-x-auto">
          <pre className="text-muted-foreground w-max mx-auto">
{`┌─────────────────────────────────────────────────────────────────┐
│                      JARVIS MISSION CONTROL                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│  │ Weather  │    │  GitHub  │    │   News   │    │ Exchange │   │
│  │   API    │    │   API    │    │   API    │    │   API    │   │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘   │
│       │               │               │               │          │
│       └───────────────┴───────┬───────┴───────────────┘          │
│                               ▼                                  │
│                    ┌─────────────────────┐                       │
│                    │   CONTEXT ENGINE    │                       │
│                    │  (Data Aggregation) │                       │
│                    └──────────┬──────────┘                       │
│                               ▼                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                     🧠 BRAIN SYSTEM                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐    │ │
│  │  │   SIGNAL    │  │    RULE     │  │    MISSION       │    │ │
│  │  │   ENGINE    │─▶│   ENGINE    │─▶│   ORCHESTRATOR   │    │ │
│  │  │  (Detect)   │  │  (Decide)   │  │   (Execute)      │    │ │
│  │  └─────────────┘  └─────────────┘  └──────────────────┘    │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                               │                                  │
│           ┌───────────────────┼───────────────────┐              │
│           ▼                   ▼                   ▼              │
│    ┌────────────┐     ┌────────────┐      ┌────────────┐        │
│    │   SQLite   │     │   Redis    │      │  REST API  │        │
│    │ (Persist)  │     │  (Cache)   │      │ (FastAPI)  │        │
│    └────────────┘     └────────────┘      └────────────┘        │
│                                                  │               │
│                                                  ▼               │
│                                    ┌────────────────────────┐   │
│                                    │   REACT FRONTEND       │   │
│                                    │  • Mission Control     │   │
│                                    │  • Global Context      │   │
│                                    │  • Simulation Lab      │   │
│                                    └────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘`}
          </pre>
        </div>
      </CyberCard>

      {/* API Endpoints Reference */}
      <CyberCard className="p-6">
        <h3 className="text-lg font-bold text-primary mb-4 flex items-center gap-2">
          <Terminal className="w-5 h-5" />
          API ENDPOINTS
        </h3>
        <div className="font-mono text-xs space-y-2">
          <div className="flex items-center gap-2 p-2 rounded bg-black/50">
            <Badge className="bg-green-500/20 text-green-400">GET</Badge>
            <span className="text-white">/api/v1/health</span>
            <span className="text-muted-foreground ml-auto">System health + Redis status</span>
          </div>
          <div className="flex items-center gap-2 p-2 rounded bg-black/50">
            <Badge className="bg-green-500/20 text-green-400">GET</Badge>
            <span className="text-white">/api/v1/context</span>
            <span className="text-muted-foreground ml-auto">Aggregated context data</span>
          </div>
          <div className="flex items-center gap-2 p-2 rounded bg-black/50">
            <Badge className="bg-green-500/20 text-green-400">GET</Badge>
            <span className="text-white">/api/v1/missions</span>
            <span className="text-muted-foreground ml-auto">All missions from DB</span>
          </div>
          <div className="flex items-center gap-2 p-2 rounded bg-black/50">
            <Badge className="bg-blue-500/20 text-blue-400">POST</Badge>
            <span className="text-white">/api/v1/brain/process</span>
            <span className="text-muted-foreground ml-auto">Process context → generate missions</span>
          </div>
          <div className="flex items-center gap-2 p-2 rounded bg-black/50">
            <Badge className="bg-green-500/20 text-green-400">GET</Badge>
            <span className="text-white">/api/v1/brain/status</span>
            <span className="text-muted-foreground ml-auto">Brain system status</span>
          </div>
          <div className="flex items-center gap-2 p-2 rounded bg-black/50">
            <Badge className="bg-green-500/20 text-green-400">GET</Badge>
            <span className="text-white">/api/v1/brain/state-machine</span>
            <span className="text-muted-foreground ml-auto">System state info</span>
          </div>
        </div>
      </CyberCard>
    </motion.div>
  );
}
