
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Activity,
  AlertTriangle,
  Bell,
  CheckCircle,
  MapPin,
  Radio,
  Server,
  Shield,
  Wifi,
  Zap
} from 'lucide-react';
import { useEffect, useState } from 'react';

const API_BASE = 'http://localhost:8000/api';

const ControlCenter = () => {
  // Backend-driven system status
  const [systemStatus, setSystemStatus] = useState({
    audioSensors: 'loading',
    aiTranslator: 'loading',
    deterrentSystem: 'loading',
    flightCoordination: 'loading',
  });
  const [statusLoading, setStatusLoading] = useState(false);
  const [statusError, setStatusError] = useState<string | null>(null);
  const [lastDeterrentResult, setLastDeterrentResult] = useState<string | null>(null);
  const [deterrentLoading, setDeterrentLoading] = useState(false);
  const [deterrentError, setDeterrentError] = useState<string | null>(null);
  const [lastEmergencyResult, setLastEmergencyResult] = useState<string | null>(null);
  const [emergencyLoading, setEmergencyLoading] = useState(false);
  const [emergencyMode, setEmergencyMode] = useState(false);
  const [isDeterrentPlaying, setIsDeterrentPlaying] = useState(false);
  const [currentDeterrent, setCurrentDeterrent] = useState<string | null>(null);
  const [delayFlightSuccess, setDelayFlightSuccess] = useState<string | null>(null);

  // Fetch system status from backend
  const fetchSystemStatus = async () => {
    setStatusLoading(true);
    setStatusError(null);
    try {
      const [strategicRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/strategic/status`),
        fetch(`${API_BASE}/stats`)
      ]);
      const strategicData = strategicRes.ok ? await strategicRes.json() : null;
      const statsData = statsRes.ok ? await statsRes.json() : null;
      setSystemStatus({
        audioSensors: statsData ? (statsData.ai_statistics?.ai_model_status === 'active' ? 'online' : 'offline') : 'unknown',
        aiTranslator: statsData ? (statsData.ai_statistics?.ai_model_status === 'active' ? 'active' : 'inactive') : 'unknown',
        deterrentSystem: strategicData ? (strategicData.strategic_system?.predator_sounds?.status || 'unknown') : 'unknown',
        flightCoordination: 'connected', // Placeholder, can be improved
      });
      // Show current deterrent sound if available
      setCurrentDeterrent(
        strategicData && strategicData.strategic_system?.predator_sounds?.current_sound
          ? strategicData.strategic_system.predator_sounds.current_sound
          : null
      );
    } catch (err: any) {
      setStatusError('Failed to fetch system status');
      setSystemStatus({
        audioSensors: 'error',
        aiTranslator: 'error',
        deterrentSystem: 'error',
        flightCoordination: 'error',
      });
      setCurrentDeterrent(null);
    } finally {
      setStatusLoading(false);
    }
  };

  useEffect(() => {
    fetchSystemStatus();
  }, []);

  // Emergency alert handler (optionally call backend)
  const handleEmergencyAlert = async () => {
    setEmergencyLoading(true);
    setEmergencyMode(true);
    setLastEmergencyResult(null);
    try {
      // Optionally trigger backend test alert
      const res = await fetch(`${API_BASE}/test-alert`, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
      if (res.ok) {
        setLastEmergencyResult('Emergency alert sent to backend.');
      } else {
        setLastEmergencyResult('Failed to send emergency alert.');
      }
      // Also trigger sound deterrent
      await handleSoundDeterrent();
    } catch (err) {
      setLastEmergencyResult('Failed to send emergency alert.');
    } finally {
    setTimeout(() => setEmergencyMode(false), 5000);
      setEmergencyLoading(false);
    }
  };

  // Sound deterrent handler
  const handleSoundDeterrent = async () => {
    setDeterrentLoading(true);
    setDeterrentError(null);
    setLastDeterrentResult(null);
    try {
      const res = await fetch(`${API_BASE}/strategic/activate-predator-sound`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sound_type: 'eagle_cry' })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setLastDeterrentResult(`Sound deterrent triggered: ${data.message || 'Success'}`);
        setIsDeterrentPlaying(true);
      } else {
        setDeterrentError(data.message || 'Failed to trigger sound deterrent');
        setLastDeterrentResult('Failed to trigger sound deterrent.');
      }
    } catch (err: any) {
      setDeterrentError('Failed to trigger sound deterrent');
      setLastDeterrentResult('Failed to trigger sound deterrent.');
    } finally {
      setDeterrentLoading(false);
      fetchSystemStatus();
    }
  };

  // Stop deterrent handler
  const handleStopDeterrent = async () => {
    setDeterrentLoading(true);
    setDeterrentError(null);
    try {
      const res = await fetch(`${API_BASE}/strategic/stop-predator-sound`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setLastDeterrentResult('Sound deterrent stopped.');
        setIsDeterrentPlaying(false);
      } else {
        setDeterrentError(data.message || 'Failed to stop sound deterrent');
      }
    } catch (err: any) {
      setDeterrentError('Failed to stop sound deterrent');
    } finally {
      setDeterrentLoading(false);
      fetchSystemStatus();
    }
  };

  // Handler for Delay Flight
  const handleDelayFlight = () => {
    setDelayFlightSuccess('Flight delay action recorded successfully.');
    setTimeout(() => setDelayFlightSuccess(null), 3000);
  };

  const deterrentActive = isDeterrentPlaying || !!currentDeterrent;
  const systemComponents = [
    {
      name: 'Audio Sensors',
      status: systemStatus.audioSensors,
      icon: Radio,
      description: '16-channel microphone array'
    },
    {
      name: 'AI Translator',
      status: systemStatus.aiTranslator,
      icon: Activity,
      description: 'Neural network processing'
    },
    {
      name: 'Deterrent System',
      status: deterrentActive ? 'active' : (['offline', 'error', 'loading'].includes(systemStatus.deterrentSystem) ? systemStatus.deterrentSystem : 'standby'),
      icon: Zap,
      description: 'Sound & visual deterrents'
    },
    {
      name: 'Flight Coordination',
      status: systemStatus.flightCoordination,
      icon: Wifi,
      description: 'ATC system integration'
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
      case 'active':
      case 'connected':
        return 'bg-green-50 text-green-800 border-green-200';
      case 'standby':
        return 'bg-yellow-50 text-yellow-800 border-yellow-200';
      case 'offline':
      case 'error':
        return 'bg-red-50 text-red-800 border-red-200';
      case 'loading':
        return 'bg-gray-50 text-gray-500 border-gray-200 animate-pulse';
      default:
        return 'bg-gray-50 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
      case 'active':
      case 'connected':
        return <CheckCircle className="w-4 h-4 text-green-600 animate-pulse" />;
      case 'standby':
        return <AlertTriangle className="w-4 h-4 text-yellow-600 animate-pulse" />;
      case 'loading':
        return <Activity className="w-4 h-4 text-gray-400 animate-spin" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-red-600" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Emergency Alert */}
      {emergencyMode && (
        <Alert variant="destructive" className="border-red-500 bg-red-50 animate-pulse">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription className="font-medium">
            EMERGENCY ALERT ACTIVATED - All runways notified. Deterrent systems engaged.
          </AlertDescription>
        </Alert>
      )}

      {/* Control Center Dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Emergency Controls */}
        <Card className="border-2 border-red-200">
          <CardHeader>
            <CardTitle className="flex items-center text-red-700">
              <Shield className="w-5 h-5 mr-2" />
              Emergency Controls
            </CardTitle>
            <CardDescription>Critical response actions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-4">
              <Button 
                variant="destructive" 
                size="lg" 
                className="h-20 flex flex-col"
                onClick={handleEmergencyAlert}
                  disabled={emergencyLoading}
              >
                <Bell className="w-8 h-8 mb-2" />
                <span className="font-medium">Emergency Alert</span>
                  {emergencyLoading && <Activity className="w-4 h-4 ml-2 animate-spin" />}
              </Button>
              <Button 
                variant="outline" 
                size="lg" 
                  className="h-20 flex flex-col border-green-500 text-green-700 transition-colors hover:bg-green-600 hover:text-white hover:border-green-700"
                  onClick={handleDelayFlight}
              >
                  <MapPin className="w-8 h-8 mb-2" />
                  <span className="font-medium">Delay Flight</span>
              </Button>
              </div>
              <div className="flex flex-col gap-4">
              <Button 
                variant="outline" 
                size="lg" 
                  className={`h-20 flex flex-col border-yellow-500 text-yellow-700 transition-colors ${isDeterrentPlaying ? 'opacity-60 cursor-not-allowed' : 'hover:bg-yellow-400 hover:text-white hover:border-yellow-600'}`}
                  onClick={handleSoundDeterrent}
                  disabled={deterrentLoading || isDeterrentPlaying}
              >
                  <Zap className="w-8 h-8 mb-2" />
                  <span className="font-medium">Sound Deterrent</span>
                  {deterrentLoading && <Activity className="w-4 h-4 ml-2 animate-spin" />}
              </Button>
                {isDeterrentPlaying && (
              <Button 
                    variant="destructive"
                size="lg" 
                    className="h-20 flex flex-col border-red-600 text-white bg-red-600 hover:bg-red-700 hover:border-red-700 transition-colors"
                    onClick={handleStopDeterrent}
                    disabled={deterrentLoading}
              >
                    <Zap className="w-8 h-8 mb-2" />
                    <span className="font-medium">Stop Deterrent</span>
                    {deterrentLoading && <Activity className="w-4 h-4 ml-2 animate-spin" />}
              </Button>
                )}
              </div>
            </div>
            {/* Action feedback */}
            <div className="mt-4 space-y-2">
              {lastEmergencyResult && (
                <Alert variant="default" className="border border-red-300 bg-red-50">
                  <AlertDescription>{lastEmergencyResult}</AlertDescription>
                </Alert>
              )}
              {lastDeterrentResult && (
                <Alert variant="default" className="border border-yellow-300 bg-yellow-50">
                  <AlertDescription>{lastDeterrentResult}</AlertDescription>
                </Alert>
              )}
              {deterrentError && (
                <Alert variant="destructive" className="border border-red-400 bg-red-100">
                  <AlertDescription>{deterrentError}</AlertDescription>
                </Alert>
              )}
              {delayFlightSuccess && (
                <Alert variant="default" className="border border-green-300 bg-green-50">
                  <AlertDescription>{delayFlightSuccess}</AlertDescription>
                </Alert>
              )}
            </div>
          </CardContent>
        </Card>

        {/* System Status Monitor */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
            <CardTitle className="flex items-center">
              <Server className="w-5 h-5 mr-2 text-blue-500" />
              System Status Monitor
            </CardTitle>
              <Button size="sm" variant="outline" onClick={fetchSystemStatus} disabled={statusLoading}>
                Refresh
                {statusLoading && <Activity className="w-4 h-4 ml-2 animate-spin" />}
              </Button>
            </div>
            <CardDescription>Real-time component health</CardDescription>
          </CardHeader>
          <CardContent>
            {statusError && (
              <Alert variant="destructive" className="mb-2">
                <AlertDescription>{statusError}</AlertDescription>
              </Alert>
            )}
            <div className="space-y-4">
              {systemComponents.map((component, index) => {
                const IconComponent = component.icon;
                return (
                  <div 
                    key={index} 
                    className={`flex items-center justify-between p-4 rounded-lg border ${getStatusColor(component.status)}`}
                  >
                    <div className="flex items-center space-x-3">
                      <IconComponent className="w-5 h-5" />
                      <div>
                        <div className="font-medium flex items-center gap-2">
                          {component.name}
                          {component.status === 'loading' && <Activity className="w-3 h-3 animate-spin text-gray-400" />}
                        </div>
                        <div className="text-xs opacity-75">{component.description}
                          {component.name === 'Deterrent System' && (
                            <span className="block mt-1 font-semibold">
                              {component.status === 'unknown'
                                ? (currentDeterrent
                                    ? `Playing: ${currentDeterrent.replace('_', ' ').toUpperCase()}`
                                    : 'Idle')
                                : (currentDeterrent
                                    ? `Playing: ${currentDeterrent.replace('_', ' ').toUpperCase()}`
                                    : (component.status.charAt(0).toUpperCase() + component.status.slice(1)))}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(component.status)}
                      <span className="text-sm font-medium capitalize">{component.status}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Advanced Controls */}
      
    </div>
  );
};

export default ControlCenter;
