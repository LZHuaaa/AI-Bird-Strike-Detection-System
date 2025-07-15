
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Bird,
  Brain,
  Globe,
  Radar,
  Radio,
  Settings,
  Shield,
  TrendingUp
} from 'lucide-react';
import { useEffect, useState } from 'react';
import aviationHero from '../assets/aviation-hero.jpg';
import BehaviorAnalytics from '../components/BehaviorAnalytics';
import BirdTranslator from '../components/BirdTranslator';
import ControlCenter from '../components/ControlCenter';
import GlobalNetwork from '../components/GlobalNetwork';
import LiveAudioMonitor from '../components/LiveAudioMonitor';
import RiskAssessment from '../components/RiskAssessment';

const Index = () => {
  const [activeSystem, setActiveSystem] = useState('monitoring');
  const [systemStatus, setSystemStatus] = useState('active');
  const [currentBird, setCurrentBird] = useState('Seagull');
  const [geminiApiKey, setGeminiApiKey] = useState('');
  const [isConnected, setIsConnected] = useState(false);

  // Real-time system stats from backend
  const [systemStats, setSystemStats] = useState({
    total_alerts: 0,
    high_risk_alerts: 0,
    most_common_species: null,
    average_confidence: 0
  });
  const [riskLevel, setRiskLevel] = useState(0);

  // Fetch system stats from backend
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/stats');
        if (response.ok) {
          const stats = await response.json();
          setSystemStats(stats);
          // Optionally, set riskLevel based on stats (custom logic)
          setRiskLevel(
            stats.high_risk_alerts > 5 ? 90 :
            stats.high_risk_alerts > 2 ? 70 : 40
          );
        }
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // refresh every 30s
    return () => clearInterval(interval);
  }, []);

  // Load saved API key on component mount
  useEffect(() => {
    const savedApiKey = localStorage.getItem('geminiApiKey');
    if (savedApiKey) {
      setGeminiApiKey(savedApiKey);
      setIsConnected(true);
    }
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-blue-light to-primary-purple-light">
      {/* Hero Header */}
      <div className="relative h-48 overflow-hidden">
        <img 
          src={aviationHero} 
          alt="Aviation Command Center" 
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-black/80 to-black/60" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="flex items-center justify-center gap-3 mb-4">
              <Radar className="h-8 w-8 text-white animate-rotate" />
              <h1 className="text-4xl font-bold text-white drop-shadow-lg">Avian AI Sentinel</h1>
              <Bird className="h-8 w-8 text-white animate-pulse" />
            </div>
            <p className="text-lg text-gray-200 mb-6 drop-shadow-md">
              Advanced Bird Strike Warning & Communication System
            </p>
            <div className="flex items-center justify-center gap-4">
              <Badge className="bg-primary-blue text-white shadow-lg">AI-POWERED</Badge>
              <Badge className="bg-accent text-white shadow-lg">REAL-TIME</Badge>
              <Badge className="bg-warning text-white shadow-lg">PREDICTIVE</Badge>
            </div>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="bg-white/95 backdrop-blur-sm border-b border-border shadow-sm">
        <div className="container mx-auto px-6 py-2">
          <div className="flex items-center justify-between bg-white/60 backdrop-blur-sm rounded-lg p-4 border border-border/50">
            <div className="flex items-center space-x-8">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-success rounded-full"></div>
                <span className="text-sm font-medium text-foreground">System Online</span>
              </div>
              <div className="text-sm text-muted-foreground">
                Birds Detected: <span className="font-bold text-primary-blue">{systemStats.total_alerts} Active</span>
              </div>
              <div className="text-sm text-muted-foreground">
                Risk Level: <span className="font-bold text-warning">
                  {riskLevel > 80 ? 'High' : riskLevel > 60 ? 'Medium' : 'Low'}
                </span>
              </div>
              <div className="text-sm text-muted-foreground">
                Common Species: <span className="font-bold text-primary-blue">{systemStats.most_common_species || 'None'}</span>
              </div>
              <div className="text-sm text-muted-foreground">
                Network: <span className="font-bold text-primary-blue">47 Airports</span>
              </div>
            </div>
            <div className="text-sm text-muted-foreground">
              Last Update: {new Date().toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {/* Enhanced Dashboard Tabs */}
        <Tabs value={activeSystem} onValueChange={setActiveSystem} className="space-y-6">
          <TabsList className="grid w-full grid-cols-6 bg-white/80 backdrop-blur-sm border border-border shadow-lg rounded-xl p-1">
            <TabsTrigger value="monitoring" className="flex items-center space-x-2 data-[state=active]:bg-primary-blue data-[state=active]:text-white rounded-lg transition-all">
              <Radio className="w-4 h-4" />
              <span>Live Monitor</span>
            </TabsTrigger>
            <TabsTrigger value="translator" className="flex items-center space-x-2 data-[state=active]:bg-primary-blue data-[state=active]:text-white rounded-lg transition-all">
              <Brain className="w-4 h-4" />
              <span>Translator</span>
            </TabsTrigger>
            <TabsTrigger value="risk" className="flex items-center space-x-2 data-[state=active]:bg-primary-blue data-[state=active]:text-white rounded-lg transition-all">
              <Shield className="w-4 h-4" />
              <span>Risk Assessment</span>
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center space-x-2 data-[state=active]:bg-primary-blue data-[state=active]:text-white rounded-lg transition-all">
              <TrendingUp className="w-4 h-4" />
              <span>Analytics</span>
            </TabsTrigger>
            <TabsTrigger value="network" className="flex items-center space-x-2 data-[state=active]:bg-primary-blue data-[state=active]:text-white rounded-lg transition-all">
              <Globe className="w-4 h-4" />
              <span>Global Network</span>
            </TabsTrigger>
            <TabsTrigger value="control" className="flex items-center space-x-2 data-[state=active]:bg-primary-blue data-[state=active]:text-white rounded-lg transition-all">
              <Settings className="w-4 h-4" />
              <span>Control Center</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="monitoring">
            <LiveAudioMonitor />
          </TabsContent>

          <TabsContent value="translator">
            <BirdTranslator />
          </TabsContent>

          <TabsContent value="risk">
            <RiskAssessment />
          </TabsContent>

          <TabsContent value="analytics">
            <BehaviorAnalytics />
          </TabsContent>

          <TabsContent value="network">
            <GlobalNetwork />
          </TabsContent>

          <TabsContent value="control">
            <ControlCenter />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Index;
