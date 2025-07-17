
import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

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
  Thermometer,
  CheckCircle,
  X,
  ZoomIn,
  ZoomOut,
  BarChart2,
  Eye,
  Bird
} from 'lucide-react';
import { MapContainer, TileLayer, Circle, Polygon, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { toast } from "@/components/ui/use-toast";
import { Toaster } from "@/components/ui/toaster";
import PredictiveRiskForecast from './PredictiveRiskForecast';

// API base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Types
interface AlertType {
  id: number;  // Now required
  level: string;
  message: string;
  time: string;
  runway: string;
  risk_score: number;
}

interface AlertResponseType {
  action_taken: string;
  notes: string;
  template_key?: string | null;
}

interface HistoricalDataPoint {
  date: string;
  risk_level: number;
  bird_count: number;
  incidents: number;
}

// Hardcoded map data for each runway
const HARDCODED_MAP_DATA = {
  "09L/27R": {
    runway: {
      length: 4000,
      width: 60,
      heading: 90,
      coordinates: { lat: 3.139, lon: 101.6869 }
    },
    bird_positions: [
      { lat: 3.140, lon: 101.688, species: "Crow", count: 3 },
      { lat: 3.138, lon: 101.685, species: "Pigeon", count: 5 },
      { lat: 3.141, lon: 101.687, species: "Eagle", count: 1 }
    ],
    risk_zones: [
      { level: "high", coordinates: [[3.139, 101.686], [3.140, 101.687], [3.138, 101.687]] },
      { level: "medium", coordinates: [[3.138, 101.685], [3.139, 101.686], [3.137, 101.686]] }
    ]
  },
  "09R/27L": {
    runway: {
      length: 4000,
      width: 60,
      heading: 90,
      coordinates: { lat: 3.135, lon: 101.6869 }
    },
    bird_positions: [
      { lat: 3.136, lon: 101.688, species: "Swallow", count: 8 },
      { lat: 3.134, lon: 101.685, species: "Sparrow", count: 4 }
    ],
    risk_zones: [
      { level: "medium", coordinates: [[3.135, 101.686], [3.136, 101.687], [3.134, 101.687]] }
    ]
  },
  "04L/22R": {
    runway: {
      length: 3800,
      width: 60,
      heading: 40,
      coordinates: { lat: 3.137, lon: 101.6850 }
    },
    bird_positions: [
      { lat: 3.138, lon: 101.686, species: "Kite", count: 2 },
      { lat: 3.136, lon: 101.684, species: "Mynah", count: 6 }
    ],
    risk_zones: [
      { level: "low", coordinates: [[3.137, 101.685], [3.138, 101.686], [3.136, 101.686]] }
    ]
  },
  "04R/22L": {
    runway: {
      length: 3800,
      width: 60,
      heading: 40,
      coordinates: { lat: 3.133, lon: 101.6850 }
    },
    bird_positions: [
      { lat: 3.134, lon: 101.686, species: "Heron", count: 1 },
      { lat: 3.132, lon: 101.684, species: "Dove", count: 7 }
    ],
    risk_zones: [
      { level: "medium", coordinates: [[3.133, 101.685], [3.134, 101.686], [3.132, 101.686]] }
    ]
  }
};

// Hardcoded historical data for each runway
const HARDCODED_HISTORY_DATA = {
  "09L/27R": [
    { date: "2024-03-14", risk_level: 8, bird_count: 15, incidents: 1 },
    { date: "2024-03-13", risk_level: 5, bird_count: 10, incidents: 0 },
    { date: "2024-03-12", risk_level: 7, bird_count: 12, incidents: 1 },
    { date: "2024-03-11", risk_level: 4, bird_count: 8, incidents: 0 },
    { date: "2024-03-10", risk_level: 6, bird_count: 11, incidents: 0 }
  ],
  "09R/27L": [
    { date: "2024-03-14", risk_level: 6, bird_count: 12, incidents: 0 },
    { date: "2024-03-13", risk_level: 4, bird_count: 8, incidents: 0 },
    { date: "2024-03-12", risk_level: 5, bird_count: 9, incidents: 1 },
    { date: "2024-03-11", risk_level: 3, bird_count: 6, incidents: 0 },
    { date: "2024-03-10", risk_level: 5, bird_count: 10, incidents: 0 }
  ],
  "04L/22R": [
    { date: "2024-03-14", risk_level: 4, bird_count: 8, incidents: 0 },
    { date: "2024-03-13", risk_level: 3, bird_count: 6, incidents: 0 },
    { date: "2024-03-12", risk_level: 5, bird_count: 10, incidents: 0 },
    { date: "2024-03-11", risk_level: 4, bird_count: 7, incidents: 1 },
    { date: "2024-03-10", risk_level: 3, bird_count: 5, incidents: 0 }
  ],
  "04R/22L": [
    { date: "2024-03-14", risk_level: 5, bird_count: 9, incidents: 0 },
    { date: "2024-03-13", risk_level: 6, bird_count: 11, incidents: 1 },
    { date: "2024-03-12", risk_level: 4, bird_count: 7, incidents: 0 },
    { date: "2024-03-11", risk_level: 3, bird_count: 5, incidents: 0 },
    { date: "2024-03-10", risk_level: 4, bird_count: 8, incidents: 0 }
  ]
};

// Custom bird icon for the map
const birdIcon = L.divIcon({
  className: 'bird-marker',
  html: `<div class="w-3 h-3 rounded-full animate-pulse bg-red-500"></div>`,
  iconSize: [12, 12],
});

// Add this utility function at the top level
const createUniqueAlertKey = (alert: AlertType): string => {
  // Create a unique string from all alert properties
  const uniqueString = `${alert.level}-${alert.message}-${alert.time}-${alert.runway}-${alert.risk_score}`;
  // Create a hash of the string
  let hash = 0;
  for (let i = 0; i < uniqueString.length; i++) {
    const char = uniqueString.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return `alert-${Math.abs(hash)}`;
};

const RiskAssessment = () => {
  const [overallRisk, setOverallRisk] = useState(0);
  const [alerts, setAlerts] = useState<AlertType[]>([]);
  const [riskFactors, setRiskFactors] = useState([]);
  const [runwayStatus, setRunwayStatus] = useState([]);
  const [weatherData, setWeatherData] = useState({
    temperature: 0,
    windSpeed: 0,
    windDirection: 'N/A',
    precipitation: 0,
    visibility: 0,
    birdFavorability: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Memoize the alert keys to prevent regeneration on every render
  const alertKeys = useMemo(() => {
    return alerts.map(alert => ({
      alert,
      key: createUniqueAlertKey(alert)
    }));
  }, [alerts]);

  // Alert response state
  const [selectedAlert, setSelectedAlert] = useState<AlertType | null>(null);
  const [responseDialogOpen, setResponseDialogOpen] = useState(false);
  const [responseData, setResponseData] = useState<AlertResponseType>({
    action_taken: '',
    notes: ''
  });
  const [responding, setResponding] = useState(false);
  const [responseError, setResponseError] = useState<string | null>(null);

  // Map and History dialog states
  const [selectedRunway, setSelectedRunway] = useState<any>(null);
  const [mapDialogOpen, setMapDialogOpen] = useState(false);
  const [historyDialogOpen, setHistoryDialogOpen] = useState(false);
  const [historicalData, setHistoricalData] = useState<HistoricalDataPoint[]>([]);
  const [mapZoom, setMapZoom] = useState(1);

  // Add predefined responses
  const quickResponses = {
    MONITOR: {
      action: "Area inspected, no threats detected",
      notes: "Completed routine perimeter check"
    },
    DETERRENT: {
      action: "Deployed deterrent measures",
      notes: "Activated sonic and visual deterrents"
    },
    SECURED: {
      action: "Area secured",
      notes: "Implemented standard operating procedures"
    },
    CLEAR: {
      action: "All clear - no threats",
      notes: "Situation resolved, no further action needed"
    }
  };

  // Add function to handle quick response selection
  const handleQuickResponse = (responseType) => {
    setResponseData({
      action_taken: quickResponses[responseType].action,
      notes: quickResponses[responseType].notes,
      template_key: responseType
    });
  };

  useEffect(() => {
    let mounted = true;
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch overall risk assessment
        const riskResponse = await fetch(`${API_BASE_URL}/risk-assessment/overall`);
        if (!riskResponse.ok) {
          throw new Error(`Risk assessment failed: ${riskResponse.statusText}`);
        }
        const riskData = await riskResponse.json();
        if (mounted) {
          setOverallRisk(riskData.overall_risk || 0);
          setRiskFactors(riskData.risk_factors || []);
        }

        // Fetch alerts
        const alertsResponse = await fetch(`${API_BASE_URL}/risk-assessment/alerts`);
        if (!alertsResponse.ok) {
          throw new Error(`Alerts fetch failed: ${alertsResponse.statusText}`);
        }
        const alertsData = await alertsResponse.json();
        if (mounted) {
          setAlerts(alertsData.alerts || []);
        }

        // Fetch weather data
        const weatherResponse = await fetch(`${API_BASE_URL}/risk-assessment/weather`);
        if (!weatherResponse.ok) {
          throw new Error(`Weather fetch failed: ${weatherResponse.statusText}`);
        }
        const weatherData = await weatherResponse.json();
        if (mounted) {
          setWeatherData(weatherData);
        }

        // Fetch runway status
        const runwayResponse = await fetch(`${API_BASE_URL}/risk-assessment/runways`);
        if (!runwayResponse.ok) {
          throw new Error(`Runway status fetch failed: ${runwayResponse.statusText}`);
        }
        const runwayData = await runwayResponse.json();
        if (mounted) {
          setRunwayStatus(runwayData.runways || []);
          setLoading(false);
        }

      } catch (err) {
        console.error('Error fetching risk assessment data:', err);
        if (mounted) {
          setError(err.message || 'Failed to load risk assessment data');
          setLoading(false);
        }
      }
    };

    fetchData();

    // Cleanup function
    return () => {
      mounted = false;
    };
  }, []); // Empty dependency array since we want to fetch only once on mount

  const getRiskColor = (risk: number) => {
    if (risk >= 30) return 'text-red-600 bg-red-100';
    if (risk >= 20) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const getAlertVariant = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'high': return 'destructive';
      case 'medium': return 'default';
      default: return 'default';
    }
  };

  const handleAlertResponse = async () => {
    if (!selectedAlert || !responseData.action_taken) return;

    try {
      setResponding(true);
      setResponseError(null);
      
      // Show success message using Alert component
      toast({
        title: "Response Saved",
        description: `Response recorded for alert at ${selectedAlert?.time}`,
        variant: "default",
        duration: 3000
      });

      // Remove only the responded alert from the list
      setAlerts(prevAlerts => 
        prevAlerts.filter(alert => 
          !(alert.id === selectedAlert.id && alert.time === selectedAlert.time)
        )
      );

      // Close dialog and reset form
      setResponseDialogOpen(false);
      setSelectedAlert(null);
      setResponseData({ action_taken: '', notes: '', template_key: null });

    } catch (err) {
      setResponseError(err.message || 'Failed to submit response');
    } finally {
      setResponding(false);
    }
  };

  const handleViewMap = async (runway) => {
    try {
      const runwayName = runway.name || runway.runway_name;
      const mapData = HARDCODED_MAP_DATA[runwayName];
      
      if (!mapData) {
        throw new Error(`No map data available for runway ${runwayName}`);
      }

      setSelectedRunway({
        ...runway,
        birdPositions: mapData.bird_positions,
        riskZones: mapData.risk_zones,
        dimensions: mapData.runway
      });
      setMapDialogOpen(true);
    } catch (err) {
      console.error('Error loading map data:', err);
    }
  };

  const handleViewHistory = async (runway) => {
    try {
      const runwayName = runway.name || runway.runway_name;
      const historyData = HARDCODED_HISTORY_DATA[runwayName];
      
      if (!historyData) {
        throw new Error(`No historical data available for runway ${runwayName}`);
      }

      setHistoricalData(historyData);
      setHistoryDialogOpen(true);
    } catch (err) {
      console.error('Error loading historical data:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-lg text-slate-600">Loading risk assessment data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert key="error-alert" variant="destructive">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

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
                  <div className="text-3xl font-bold text-slate-700">{Math.round(overallRisk)}%</div>
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
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Thermometer className="w-5 h-5 mr-2 text-orange-500" />
                  <span>Temperature</span>
                </div>
                <span className="font-medium">{weatherData.temperature}°C</span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Wind className="w-5 h-5 mr-2 text-blue-500" />
                  <span>Wind</span>
                </div>
                <span className="font-medium">{weatherData.windSpeed.toFixed(1)} km/h {weatherData.windDirection}</span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Bird className="w-5 h-5 mr-2 text-purple-500" />
                  <span>Bird Activity</span>
                </div>
                <div className="flex items-center">
                  <span className={`px-2 py-1 rounded-full text-sm font-medium ${
                    weatherData.birdFavorability >= 70 ? 'bg-red-100 text-red-700' :
                    weatherData.birdFavorability >= 40 ? 'bg-orange-100 text-orange-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {weatherData.birdFavorability.toFixed(1)}%
                  </span>
                </div>
              </div>

              {weatherData.visibility > 0 && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Eye className="w-5 h-5 mr-2 text-gray-500" />
                    <span>Visibility</span>
                  </div>
                  <span className="font-medium">{weatherData.visibility.toFixed(1)} km</span>
                </div>
              )}
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
              {alertKeys.map(({ alert, key }) => (
                <Alert 
                  key={key}
                  variant={getAlertVariant(alert.level)}
                >
                  <AlertDescription>
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="font-medium">{alert.message}</span>
                        <div className="text-sm mt-1">
                          {alert.runway} • {alert.time}
                        </div>
                      </div>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => {
                          setSelectedAlert(alert);
                          setResponseDialogOpen(true);
                        }}
                      >
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

      {/* Alert Response Dialog */}
      <Dialog open={responseDialogOpen} onOpenChange={setResponseDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Respond to Alert</DialogTitle>
            <DialogDescription asChild>
              <div>
                <p>{selectedAlert?.message}</p>
                <p className="text-sm text-slate-500 mt-1">
                  {selectedAlert?.runway} • {selectedAlert?.time}
                </p>
              </div>
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Quick Response Buttons */}
            <div className="grid grid-cols-2 gap-2 mb-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleQuickResponse('MONITOR')}
                className="w-full"
              >
                <Eye className="w-4 h-4 mr-1" />
                Monitor
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleQuickResponse('DETERRENT')}
                className="w-full"
              >
                <Zap className="w-4 h-4 mr-1" />
                Deterrent
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleQuickResponse('SECURED')}
                className="w-full"
              >
                <Shield className="w-4 h-4 mr-1" />
                Secured
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleQuickResponse('CLEAR')}
                className="w-full"
              >
                <CheckCircle className="w-4 h-4 mr-1" />
                Clear
              </Button>
            </div>

            <div className="space-y-2">
              <Label htmlFor="action">Action Taken</Label>
              <Input
                id="action"
                placeholder="Enter the action taken..."
                value={responseData.action_taken}
                onChange={(e) => setResponseData({ ...responseData, action_taken: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Additional Notes</Label>
              <Textarea
                id="notes"
                placeholder="Any additional information..."
                value={responseData.notes}
                onChange={(e) => setResponseData({ ...responseData, notes: e.target.value })}
              />
            </div>

            {responseError && (
              <Alert variant="destructive">
                <AlertDescription>{responseError}</AlertDescription>
              </Alert>
            )}
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setResponseDialogOpen(false);
                setSelectedAlert(null);
                setResponseData({ action_taken: '', notes: '' });
                setResponseError(null);
              }}
            >
              <X className="w-4 h-4 mr-1" />
              Cancel
            </Button>
            <Button
              onClick={handleAlertResponse}
              disabled={!responseData.action_taken || responding}
            >
              <CheckCircle className="w-4 h-4 mr-1" />
              {responding ? 'Submitting...' : 'Submit Response'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

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
                    <span className="font-medium">{Math.round(runway.risk)}%</span>
                  </div>
                  <Progress value={runway.risk} className="h-2" />
                  <div className="flex justify-between text-sm">
                    <span>Active Birds:</span>
                    <span className="font-medium">{runway.birdCount}</span>
                  </div>
                </div>
                
                <div className="mt-3 flex space-x-2">
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="flex-1"
                    onClick={() => handleViewMap(runway)}
                  >
                    <MapPin className="w-3 h-3 mr-1" />
                    View Map
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="flex-1"
                    onClick={() => handleViewHistory(runway)}
                  >
                    <Calendar className="w-3 h-3 mr-1" />
                    History
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Replace the old Predictive Analysis card with the new component */}
      <PredictiveRiskForecast />

      {/* Map Dialog */}
      <Dialog open={mapDialogOpen} onOpenChange={setMapDialogOpen}>
        <DialogContent className="max-w-5xl">
          <DialogHeader>
            <DialogTitle>Runway Map View - {selectedRunway?.name}</DialogTitle>
            <DialogDescription>
              Real-time bird activity and risk zones
            </DialogDescription>
          </DialogHeader>
          {/* Map Container */}
          <div className="bg-white rounded-lg shadow-sm">
            <h2 className="text-lg font-semibold p-4 border-b">Real-time bird activity and risk zones</h2>
            <div className="h-[400px] relative">
              {selectedRunway?.dimensions && (
                <MapContainer
                  center={[3.1390, 101.6869]}
                  zoom={15}
                  className="h-full w-full rounded-b-lg"
                  zoomControl={false}
                >
                  {/* Base map layer */}
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  />
                  
                  {/* Runway polygon */}
                  {selectedRunway.dimensions.coordinates && (
                    <Polygon
                      positions={[
                        [
                          [selectedRunway.dimensions.coordinates.lat - 0.001, selectedRunway.dimensions.coordinates.lon - 0.003],
                          [selectedRunway.dimensions.coordinates.lat - 0.001, selectedRunway.dimensions.coordinates.lon + 0.003],
                          [selectedRunway.dimensions.coordinates.lat + 0.001, selectedRunway.dimensions.coordinates.lon + 0.003],
                          [selectedRunway.dimensions.coordinates.lat + 0.001, selectedRunway.dimensions.coordinates.lon - 0.003],
                        ]
                      ]}
                      pathOptions={{ color: 'black', weight: 2, fillColor: '#666', fillOpacity: 0.8 }}
                    />
                  )}

                  {/* Risk zones */}
                  {selectedRunway.riskZones?.map((zone, index) => (
                    <Polygon
                      key={`risk-zone-${index}`}
                      positions={[zone.coordinates.map(coord => [coord[0], coord[1]])]}
                      pathOptions={{
                        color: zone.level === 'high' ? '#ef4444' : '#facc15',
                        fillColor: zone.level === 'high' ? '#fecaca' : '#fef9c3',
                        fillOpacity: 0.4,
                        weight: 1
                      }}
                    >
                      <Popup>
                        <div className="text-sm font-medium">
                          {zone.level === 'high' ? 'High Risk Zone' : 'Caution Zone'}
                        </div>
                      </Popup>
                    </Polygon>
                  ))}

                  {/* Bird positions */}
                  {selectedRunway.bird_positions?.map((bird, index) => (
                    <Marker
                      key={`bird-marker-${index}`}
                      position={[bird.lat, bird.lon]}
                      icon={birdIcon}
                    >
                      <Popup>
                        <div className="text-sm">
                          <div className="font-medium">{bird.species}</div>
                          <div>Count: {bird.count}</div>
                        </div>
                      </Popup>
                    </Marker>
                  ))}
                </MapContainer>
              )}

              {/* Legend */}
              <div className="absolute bottom-2 right-2 bg-white/90 p-2 rounded-lg shadow-sm text-xs">
                <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                    <span>Bird Activity</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-red-200" />
                    <span>High Risk Zone</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-yellow-200" />
                    <span>Caution Zone</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-slate-700" />
                    <span>Runway</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Stats below map */}
          <div className="mt-4 grid grid-cols-3 gap-4">
            <div className="p-4 bg-slate-50 rounded-lg">
              <div className="text-sm font-medium">Risk Level</div>
              <div className="text-2xl font-bold text-red-600">{Math.round(selectedRunway?.risk || 0)}%</div>
              <div className="text-xs text-slate-500 mt-1">Based on current conditions</div>
            </div>
            <div className="p-4 bg-slate-50 rounded-lg">
              <div className="text-sm font-medium">Active Birds</div>
              <div className="text-2xl font-bold text-blue-600">
                {selectedRunway?.bird_positions?.reduce((acc, bird) => acc + bird.count, 0) || 0}
              </div>
              <div className="text-xs text-slate-500 mt-1">Total birds in vicinity</div>
            </div>
            <div className="p-4 bg-slate-50 rounded-lg">
              <div className="text-sm font-medium">Species Count</div>
              <div className="text-2xl font-bold text-emerald-600">
                {selectedRunway?.bird_positions ? new Set(selectedRunway.bird_positions.map(bird => bird.species)).size : 0}
              </div>
              <div className="text-xs text-slate-500 mt-1">Unique bird species</div>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* History Dialog */}
      <Dialog open={historyDialogOpen} onOpenChange={setHistoryDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col">
          <DialogHeader className="flex-none">
            <DialogTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-blue-500" />
              Historical Data - {selectedRunway?.name}
            </DialogTitle>
            <DialogDescription>
              Past incidents and risk level trends
            </DialogDescription>
          </DialogHeader>
          <div className="flex-1 overflow-y-auto pr-6 space-y-6">
            {/* Historical stats */}
            <div className="grid grid-cols-3 gap-4 min-w-fit">
              <div className="p-4 bg-gradient-to-br from-orange-50 to-amber-50 rounded-lg border border-orange-100">
                <div className="text-sm font-medium text-orange-700">Average Risk</div>
                <div className="text-3xl font-bold text-orange-600">
                  {historicalData.length > 0
                    ? Math.round(
                        historicalData.reduce((acc, curr) => acc + curr.risk_level, 0) /
                        historicalData.length
                      )
                    : 0}%
                </div>
                <div className="text-xs text-orange-600 mt-1">Based on last 5 days</div>
              </div>
              <div className="p-4 bg-gradient-to-br from-red-50 to-rose-50 rounded-lg border border-red-100">
                <div className="text-sm font-medium text-red-700">Total Incidents</div>
                <div className="text-3xl font-bold text-red-600">
                  {historicalData.reduce((acc, curr) => acc + curr.incidents, 0)}
                </div>
                <div className="text-xs text-red-600 mt-1">Reported bird strikes</div>
              </div>
              <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-100">
                <div className="text-sm font-medium text-blue-700">Peak Bird Count</div>
                <div className="text-3xl font-bold text-blue-600">
                  {Math.max(...(historicalData.length ? historicalData.map(d => d.bird_count) : [0]))}
                </div>
                <div className="text-xs text-blue-600 mt-1">Maximum birds detected</div>
              </div>
            </div>

            {/* Risk Level Distribution */}
            <div className="p-4 bg-white rounded-lg border">
              <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-purple-500" />
                Risk Level Distribution
              </h3>
              <div className="grid grid-cols-4 gap-2">
                {['Low (0-25%)', 'Moderate (26-50%)', 'High (51-75%)', 'Critical (76-100%)'].map((level, i) => {
                  const count = historicalData.filter(d => {
                    const risk = d.risk_level;
                    return risk > i * 25 && risk <= (i + 1) * 25;
                  }).length;
                  return (
                    <div key={i} className="text-center p-2 bg-slate-50 rounded">
                      <div className="text-xs text-slate-600">{level}</div>
                      <div className="text-lg font-bold text-slate-700">{count}</div>
                      <div className="text-xs text-slate-500">days</div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Historical data table with enhanced design */}
            <div className="border rounded-lg overflow-hidden bg-white">
              <div className="p-3 bg-slate-50 border-b">
                <h3 className="font-semibold flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-slate-600" />
                  Daily Records
                </h3>
              </div>
              <table className="w-full">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-sm font-medium text-slate-600">Date</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-slate-600">Risk Level</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-slate-600">Bird Count</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-slate-600">Incidents</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-slate-600">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {historicalData.map((data, index) => (
                    <tr key={index} className="border-t hover:bg-slate-50 transition-colors">
                      <td className="px-4 py-3">
                        <div className="font-medium">{data.date}</div>
                        <div className="text-xs text-slate-500">
                          {index === 0 ? 'Today' : index === 1 ? 'Yesterday' : `${index} days ago`}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${
                            data.risk_level > 75 ? 'bg-red-500' :
                            data.risk_level > 50 ? 'bg-orange-500' :
                            data.risk_level > 25 ? 'bg-yellow-500' :
                            'bg-green-500'
                          }`} />
                          <Badge variant={
                            data.risk_level > 75 ? 'destructive' :
                            data.risk_level > 50 ? 'destructive' :
                            data.risk_level > 25 ? 'default' :
                            'secondary'
                          }>
                            {Math.round(data.risk_level)}%
                          </Badge>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <Bird className="w-4 h-4 text-blue-500" />
                          {data.bird_count}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        {data.incidents > 0 ? (
                          <Badge variant="destructive" className="flex items-center gap-1">
                            <AlertTriangle className="w-3 h-3" />
                            {data.incidents}
                          </Badge>
                        ) : (
                          <Badge variant="secondary" className="flex items-center gap-1">
                            <CheckCircle className="w-3 h-3" />
                            None
                          </Badge>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={
                          data.incidents > 0 ? 'destructive' :
                          data.risk_level > 50 ? 'default' :
                          'secondary'
                        }>
                          {data.incidents > 0 ? 'Incident Reported' :
                           data.risk_level > 50 ? 'High Risk Day' :
                           'Normal Operations'}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Trend Analysis */}
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-white rounded-lg border">
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-emerald-500" />
                  Risk Trend Analysis
                </h3>
                <div className="space-y-2">
                  {historicalData.length > 1 && (
                    <>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-slate-600">Current Trend</span>
                        <Badge variant={
                          historicalData[0].risk_level > historicalData[1].risk_level
                            ? 'destructive'
                            : 'default'
                        }>
                          {historicalData[0].risk_level > historicalData[1].risk_level
                            ? 'Increasing'
                            : 'Decreasing'}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-slate-600">5-Day Change</span>
                        <span className={`text-sm font-medium ${
                          historicalData[0].risk_level > historicalData[4].risk_level
                            ? 'text-red-600'
                            : 'text-green-600'
                        }`}>
                          {Math.abs(historicalData[0].risk_level - historicalData[4].risk_level)}%
                          {historicalData[0].risk_level > historicalData[4].risk_level
                            ? ' Increase'
                            : ' Decrease'}
                        </span>
                      </div>
                    </>
                  )}
                </div>
              </div>

              <div className="p-4 bg-white rounded-lg border">
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <Bird className="w-4 h-4 text-blue-500" />
                  Bird Activity Summary
                </h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600">Average Daily Count</span>
                    <span className="text-sm font-medium">
                      {historicalData && historicalData.length > 0
                        ? Math.round(
                            historicalData.reduce((acc, curr) => acc + (curr?.bird_count || 0), 0) /
                            historicalData.length
                          )
                        : 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600">Activity Pattern</span>
                    <Badge variant="outline">
                      {historicalData && historicalData.length > 1 && historicalData[0]?.bird_count && historicalData[1]?.bird_count
                        ? historicalData[0].bird_count > historicalData[1].bird_count
                          ? 'Increasing Activity'
                          : 'Decreasing Activity'
                        : 'No Data Available'}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Add Toaster */}
      <Toaster />
    </div>
  );
};

export default RiskAssessment;
