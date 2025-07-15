
import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Bell, 
  Zap, 
  Eye, 
  MapPin, 
  Settings, 
  Shield,
  AlertTriangle,
  CheckCircle,
  Activity,
  Radio,
  Wifi,
  Server
} from 'lucide-react';

const ControlCenter = () => {
  const [systemStatus, setSystemStatus] = useState({
    audioSensors: 'online',
    aiTranslator: 'active',
    deterrentSystem: 'standby',
    flightCoordination: 'connected'
  });

  const [emergencyMode, setEmergencyMode] = useState(false);

  const handleEmergencyAlert = () => {
    setEmergencyMode(true);
    // Simulate emergency alert
    setTimeout(() => setEmergencyMode(false), 5000);
  };

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
      status: systemStatus.deterrentSystem,
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
      default:
        return 'bg-gray-50 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
      case 'active':
      case 'connected':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'standby':
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-red-600" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Emergency Alert */}
      {emergencyMode && (
        <Alert variant="destructive" className="border-red-500 bg-red-50">
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
              <Button 
                variant="destructive" 
                size="lg" 
                className="h-20 flex flex-col"
                onClick={handleEmergencyAlert}
              >
                <Bell className="w-8 h-8 mb-2" />
                <span className="font-medium">Emergency Alert</span>
              </Button>
              <Button 
                variant="outline" 
                size="lg" 
                className="h-20 flex flex-col border-yellow-500 text-yellow-700 hover:bg-yellow-50"
              >
                <Zap className="w-8 h-8 mb-2" />
                <span className="font-medium">Sound Deterrent</span>
              </Button>
              <Button 
                variant="outline" 
                size="lg" 
                className="h-20 flex flex-col border-blue-500 text-blue-700 hover:bg-blue-50"
              >
                <Eye className="w-8 h-8 mb-2" />
                <span className="font-medium">Visual Deterrent</span>
              </Button>
              <Button 
                variant="outline" 
                size="lg" 
                className="h-20 flex flex-col border-green-500 text-green-700 hover:bg-green-50"
              >
                <MapPin className="w-8 h-8 mb-2" />
                <span className="font-medium">Delay Flight</span>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* System Status Monitor */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Server className="w-5 h-5 mr-2 text-blue-500" />
              System Status Monitor
            </CardTitle>
            <CardDescription>Real-time component health</CardDescription>
          </CardHeader>
          <CardContent>
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
                        <div className="font-medium">{component.name}</div>
                        <div className="text-xs opacity-75">{component.description}</div>
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
      <Card>
        <CardHeader>
          <CardTitle>Advanced System Controls</CardTitle>
          <CardDescription>Fine-tune system parameters and responses</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Detection Sensitivity */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Detection Sensitivity</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Audio Threshold</span>
                  <span>75%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: '75%' }}></div>
                </div>
              </div>
            </div>

            {/* Response Time */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Response Time</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Alert Delay</span>
                  <span>2.3s</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: '40%' }}></div>
                </div>
              </div>
            </div>

            {/* Risk Threshold */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Risk Threshold</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Alert Level</span>
                  <span>80%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-orange-500 h-2 rounded-full" style={{ width: '80%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 flex justify-between">
            <Button variant="outline">
              <Settings className="w-4 h-4 mr-2" />
              System Settings
            </Button>
            <Button>
              Save Configuration
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ControlCenter;
