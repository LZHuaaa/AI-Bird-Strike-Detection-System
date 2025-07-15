
import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  AlertTriangle, 
  Shield, 
  Plane, 
  Cloud, 
  TrendingUp,
  Calendar,
  MapPin,
  Zap,
  Wind,
  Thermometer
} from 'lucide-react';

const RiskAssessment = () => {
  const [overallRisk] = useState(23);
  const [alerts] = useState([
    {
      level: 'medium',
      message: 'Increased bird activity detected in runway approach zone',
      time: '14:28',
      runway: 'Runway 09L'
    },
    {
      level: 'low',
      message: 'Weather conditions favorable for bird migration',
      time: '14:15',
      runway: 'All runways'
    }
  ]);

  const riskFactors = [
    {
      name: 'Bird Activity Level',
      value: 34,
      trend: 'up',
      description: 'Higher than normal feeding activity'
    },
    {
      name: 'Weather Impact',
      value: 18,
      trend: 'stable',
      description: 'Light winds, clear visibility'
    },
    {
      name: 'Seasonal Migration',
      value: 42,
      trend: 'up',
      description: 'Peak migration season for multiple species'
    },
    {
      name: 'Flight Schedule Density',
      value: 28,
      trend: 'down',
      description: 'Moderate traffic, decreasing'
    }
  ];

  const runwayStatus = [
    {
      name: 'Runway 09L/27R',
      risk: 23,
      status: 'caution',
      birdCount: 5,
      lastIncident: '2 hours ago'
    },
    {
      name: 'Runway 09R/27L',
      risk: 12,
      status: 'clear',
      birdCount: 1,
      lastIncident: '6 hours ago'
    },
    {
      name: 'Runway 04L/22R',
      risk: 8,
      status: 'clear',
      birdCount: 0,
      lastIncident: '1 day ago'
    },
    {
      name: 'Runway 04R/22L',
      risk: 15,
      status: 'clear',
      birdCount: 2,
      lastIncident: '4 hours ago'
    }
  ];

  const weatherData = {
    temperature: 72,
    windSpeed: 8,
    windDirection: 'SW',
    precipitation: 0,
    visibility: 10,
    birdFavorability: 'High'
  };

  const getRiskColor = (risk: number) => {
    if (risk >= 30) return 'text-red-600 bg-red-100';
    if (risk >= 20) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const getAlertVariant = (level: string) => {
    switch (level) {
      case 'high': return 'destructive';
      case 'medium': return 'default';
      default: return 'default';
    }
  };

  return (
    <div className="space-y-6">
      {/* Overall Risk Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Shield className="w-5 h-5 mr-2 text-blue-500" />
              Overall Risk Assessment
            </CardTitle>
            <CardDescription>Dynamic collision risk analysis</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-3xl font-bold text-slate-700">{overallRisk}%</div>
                  <div className="text-sm text-slate-600">Current Risk Level</div>
                </div>
                <div className={`px-4 py-2 rounded-lg ${getRiskColor(overallRisk)}`}>
                  {overallRisk >= 30 ? 'High Risk' : overallRisk >= 20 ? 'Moderate Risk' : 'Low Risk'}
                </div>
              </div>
              <Progress value={overallRisk} className="h-3" />
              <div className="text-xs text-slate-600">
                Risk calculation based on real-time bird activity, weather conditions, and flight schedules
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center text-lg">
              <Cloud className="w-5 h-5 mr-2 text-purple-500" />
              Weather Impact
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Thermometer className="w-4 h-4 mr-2 text-orange-500" />
                  <span className="text-sm">Temperature</span>
                </div>
                <span className="font-medium">{weatherData.temperature}°F</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Wind className="w-4 h-4 mr-2 text-blue-500" />
                  <span className="text-sm">Wind</span>
                </div>
                <span className="font-medium">{weatherData.windSpeed}mph {weatherData.windDirection}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Bird Activity</span>
                <Badge variant={weatherData.birdFavorability === 'High' ? 'destructive' : 'default'}>
                  {weatherData.birdFavorability}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Active Alerts */}
      {alerts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2 text-orange-500" />
              Active Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {alerts.map((alert, index) => (
                <Alert key={index} variant={getAlertVariant(alert.level)}>
                  <AlertDescription>
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="font-medium">{alert.message}</span>
                        <div className="text-sm mt-1">
                          {alert.runway} • {alert.time}
                        </div>
                      </div>
                      <Button size="sm" variant="outline">
                        <Zap className="w-3 h-3 mr-1" />
                        Respond
                      </Button>
                    </div>
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Risk Factors Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Risk Factor Analysis</CardTitle>
          <CardDescription>Detailed breakdown of contributing risk elements</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {riskFactors.map((factor, index) => (
              <div key={index} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{factor.name}</span>
                  <div className="flex items-center space-x-2">
                    <TrendingUp className={`w-4 h-4 ${
                      factor.trend === 'up' ? 'text-red-500' : 
                      factor.trend === 'down' ? 'text-green-500' : 'text-slate-500'
                    }`} />
                    <span className="font-bold">{factor.value}%</span>
                  </div>
                </div>
                <Progress value={factor.value} className="h-2 mb-2" />
                <p className="text-xs text-slate-600">{factor.description}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Runway Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Plane className="w-5 h-5 mr-2 text-blue-500" />
            Runway Risk Assessment
          </CardTitle>
          <CardDescription>Individual runway risk levels and bird activity</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {runwayStatus.map((runway, index) => (
              <div key={index} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <div className="font-semibold">{runway.name}</div>
                    <div className="text-sm text-slate-600">Last incident: {runway.lastIncident}</div>
                  </div>
                  <Badge variant={runway.status === 'clear' ? 'default' : 'secondary'}>
                    {runway.status}
                  </Badge>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Risk Level:</span>
                    <span className="font-medium">{runway.risk}%</span>
                  </div>
                  <Progress value={runway.risk} className="h-2" />
                  <div className="flex justify-between text-sm">
                    <span>Active Birds:</span>
                    <span className="font-medium">{runway.birdCount}</span>
                  </div>
                </div>
                
                <div className="mt-3 flex space-x-2">
                  <Button size="sm" variant="outline" className="flex-1">
                    <MapPin className="w-3 h-3 mr-1" />
                    View Map
                  </Button>
                  <Button size="sm" variant="outline" className="flex-1">
                    <Calendar className="w-3 h-3 mr-1" />
                    History
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Predictive Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Predictive Risk Forecast</CardTitle>
          <CardDescription>Next 24-hour risk projection</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-slate-500">
            <TrendingUp className="w-16 h-16 mx-auto mb-4 text-slate-300" />
            <h3 className="text-lg font-medium mb-2">Predictive Analytics</h3>
            <p>AI-powered risk forecasting coming soon...</p>
            <p className="text-sm mt-2">Based on historical patterns, weather forecasts, and seasonal behavior</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RiskAssessment;
