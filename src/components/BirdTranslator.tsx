type AIStatistics = {
  communication_patterns_analyzed?: number;
  species_behavior_profiles?: number;
  ai_model_status?: string;
  active_monitoring_sessions?: number;
  average_risk_score?: number;
};

type SystemStats = {
  total_detections?: number;
  active_alerts?: number;
  species_count?: number;
  ai_statistics?: AIStatistics;
};

type SpeciesPattern = {
  intents?: Record<string, number>;
  communication_types?: Record<string, number>;
};

type CommunicationPatterns = Record<string, SpeciesPattern>;


import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    AlertTriangle,
    Brain,
    Heart,
    MessageSquare,
    Music,
    Pause,
    Play,
    TreePine,
    Volume2,
    Wifi,
    WifiOff
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

const AUDIO_API_BASE = "http://localhost:5000/api";

const BirdTranslator = () => {
  // Connection state
  const [isConnected, setIsConnected] = useState(false);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const wsRef = useRef(null);

  // Data state
  const [currentTranslation, setCurrentTranslation] = useState(null);
  const [recentTranslations, setRecentTranslations] = useState([]);
  const [birdPersonalities, setBirdPersonalities] = useState([]);
  const [communicationPatterns, setCommunicationPatterns] = useState<CommunicationPatterns>({});

  const [systemStats, setSystemStats] = useState<SystemStats>({});

  const [aiInsights, setAiInsights] = useState<any>({});
  const [audioSegments, setAudioSegments] = useState<any[]>([]);
  const [audioLoading, setAudioLoading] = useState(false);
  const [audioError, setAudioError] = useState<string | null>(null);

  // Backend API configuration
  const API_BASE = 'http://localhost:8000/api';
  const WS_URL = 'ws://localhost:8000/ws';

  // Initialize WebSocket connection
  useEffect(() => {
    connectWebSocket();
    fetchInitialData();
    fetchAudioSegments();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      wsRef.current = new WebSocket(WS_URL);
      
      wsRef.current.onopen = () => {
        setIsConnected(true);
        setConnectionError(null);
        console.log('WebSocket connected');
      };
      
      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      wsRef.current.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket disconnected');
        // Attempt to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
      
      wsRef.current.onerror = (error) => {
        setConnectionError('WebSocket connection failed');
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      setConnectionError('Failed to initialize WebSocket');
      console.error('WebSocket initialization error:', error);
    }
  };

  const handleWebSocketMessage = (data) => {
    if (data.type === 'heartbeat') {
      return; // Ignore heartbeat messages
    }

    // Handle real-time bird alerts
    if (data.timestamp && data.species) {
      const newTranslation = {
        species: data.species.common,
        originalCall: data.communication_analysis?.call_type || 'Unknown call',
        translation: data.ai_insights?.call_interpretation?.[0] || 'Processing...',
        emotion: data.communication_analysis?.emotional_state || 'Unknown',
        context: data.communication_analysis?.behavioral_context || 'Unknown',
        confidence: Math.round(((data.confidence ?? data.risk_score) || 0) * 100),
        timestamp: new Date(data.timestamp).toLocaleTimeString(),
        alertLevel: data.alert_level,
        riskScore: data.risk_score,
        behavioralPrediction: data.behavioral_prediction,
        aiInsights: data.ai_insights,
        imageData: data.image_data
      };

      setCurrentTranslation(newTranslation);
      
      // Add to recent translations
      setRecentTranslations(prev => [
        {
          species: newTranslation.species,
          call: newTranslation.originalCall,
          translation: newTranslation.translation,
          emotion: newTranslation.emotion,
          context: newTranslation.context,
          confidence: newTranslation.confidence,
          timestamp: newTranslation.timestamp,
          alertLevel: newTranslation.alertLevel,
          riskScore: newTranslation.riskScore
        },
        ...prev.slice(0, 9)
      ]);
    }
  };

  const fetchInitialData = async () => {
    try {
      // Fetch recent alerts
      const alertsResponse = await fetch(`${API_BASE}/alerts/recent`);
      if (alertsResponse.ok) {
        const alertsData = await alertsResponse.json();
        processAlertsData(alertsData.alerts);
      }

      // Fetch communication patterns
      const patternsResponse = await fetch(`${API_BASE}/communication-patterns`);
      if (patternsResponse.ok) {
        const patternsData = await patternsResponse.json();
        setCommunicationPatterns(patternsData.patterns);
      }

      // Fetch system stats
      const statsResponse = await fetch(`${API_BASE}/stats`);
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setSystemStats(statsData);
      }

      // Fetch AI insights
      const insightsResponse = await fetch(`${API_BASE}/ai-insights`);
      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json();
        setAiInsights(insightsData);
      }

    } catch (error) {
      console.error('Error fetching initial data:', error);
      setConnectionError('Failed to load initial data');
    }
  };

  const processAlertsData = (alerts) => {
    const processedTranslations = alerts.map(alert => ({
      species: alert.species?.common || 'Unknown',
      call: alert.communication_analysis?.call_type || 'Unknown call',
      translation: alert.ai_insights?.call_interpretation?.[0] || 'Processing...',
      emotion: alert.communication_analysis?.emotional_state || 'Unknown',
      context: alert.communication_analysis?.behavioral_context || 'Unknown',
      confidence: Math.round(((alert.confidence ?? alert.risk_score) || 0) * 100),
      timestamp: new Date(alert.timestamp).toLocaleTimeString(),
      alertLevel: alert.alert_level,
      riskScore: alert.risk_score,
      id: alert.id
    }));

    setRecentTranslations(processedTranslations);
    
    if (processedTranslations.length > 0) {
      const latest = processedTranslations[0];
      setCurrentTranslation({
        species: latest.species,
        originalCall: latest.call,
        translation: latest.translation,
        emotion: latest.emotion,
        context: latest.context,
        confidence: latest.confidence,
        timestamp: latest.timestamp
      });
    }
  };

  const triggerTestAlert = async () => {
    try {
      const response = await fetch(`${API_BASE}/test-alert`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        console.log('Test alert triggered successfully');
      }
    } catch (error) {
      console.error('Error triggering test alert:', error);
    }
  };

  const acknowledgeAlert = async (alertId) => {
    try {
      const response = await fetch(`${API_BASE}/acknowledge-alert/${alertId}`, {
        method: 'POST',
      });
      
      if (response.ok) {
        // Update the alert in the recent translations
        setRecentTranslations(prev => 
          prev.map(alert => 
            alert.id === alertId 
              ? { ...alert, acknowledged: true }
              : alert
          )
        );
      }
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  const toggleMonitoring = () => {
    setIsMonitoring(!isMonitoring);
  };

  const getEmotionColor = (emotion) => {
    switch (emotion?.toLowerCase()) {
      case 'confident': return 'bg-blue-500';
      case 'focused': return 'bg-purple-500';
      case 'excited': return 'bg-green-500';
      case 'agitated': 
      case 'alarmed': return 'bg-red-500';
      case 'calm': return 'bg-teal-500';
      default: return 'bg-gray-500';
    }
  };

  const getContextIcon = (context) => {
    switch (context?.toLowerCase()) {
      case 'territorial_defense':
      case 'territory_defense': return <TreePine className="w-4 h-4" />;
      case 'hunting_alert': return <AlertTriangle className="w-4 h-4" />;
      case 'feeding_call': return <Heart className="w-4 h-4" />;
      case 'predator_warning': return <AlertTriangle className="w-4 h-4" />;
      default: return <MessageSquare className="w-4 h-4" />;
    }
  };

  const getAlertLevelColor = (level) => {
    switch (level) {
      case 'HIGH': return 'bg-red-500';
      case 'MEDIUM': return 'bg-yellow-500';
      case 'LOW': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  // Fetch audio segments from Flask backend
  const fetchAudioSegments = async () => {
    setAudioLoading(true);
    setAudioError(null);
    try {
      const res = await fetch(`${AUDIO_API_BASE}/audio-segments`);
      const data = await res.json();
      if (data.success) {
        setAudioSegments(data.segments || []);
      } else {
        setAudioError(data.error || 'Failed to fetch audio segments');
      }
    } catch (err: any) {
      setAudioError(err.message || 'Failed to fetch audio segments');
    } finally {
      setAudioLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <Card className="border-l-4 border-l-blue-500">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {isConnected ? (
                <Wifi className="w-5 h-5 text-green-500" />
              ) : (
                <WifiOff className="w-5 h-5 text-red-500" />
              )}
              <div>
                <p className="font-medium">
                  {isConnected ? 'Connected to Backend' : 'Disconnected'}
                </p>
                <p className="text-sm text-slate-500">
                  {isConnected 
                    ? 'Real-time bird communication analysis active'
                    : 'Attempting to reconnect...'
                  }
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button 
                onClick={toggleMonitoring}
                variant={isMonitoring ? "default" : "outline"}
                size="sm"
              >
                {isMonitoring ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
                {isMonitoring ? 'Pause' : 'Start'} Monitoring
              </Button>
              <Button onClick={triggerTestAlert} variant="outline" size="sm">
                Test Alert
              </Button>
            </div>
          </div>
          
          {connectionError && (
            <Alert className="mt-4">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{connectionError}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Live Translation Display */}
      <Card className="border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50">
        <CardHeader>
          <CardTitle className="flex items-center text-xl">
            <Volume2 className="w-6 h-6 mr-3 text-blue-500" />
            Live Bird Language Translation
            <Badge className={`ml-3 ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}>
              {isConnected ? 'LIVE' : 'OFFLINE'}
            </Badge>
          </CardTitle>
          <CardDescription>
            Real-time decoding of avian communication patterns via AI backend
          </CardDescription>
        </CardHeader>
        <CardContent>
          {currentTranslation ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Original Call */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Original Bird Call</h3>
                  <Badge className="bg-green-500">{currentTranslation.confidence}% Confidence</Badge>
                </div>
                <div className="p-4 bg-white rounded-lg border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-blue-600">{currentTranslation.species}</span>
                    <span className="text-sm text-slate-500">{currentTranslation.timestamp}</span>
                  </div>
                  <div className="text-lg font-mono text-center py-4 bg-slate-50 rounded">
                    {/* Audio player if available, else fallback to text */}
                    {currentTranslation.audio_url ? (
                      <audio controls src={currentTranslation.audio_url} className="mx-auto">
                        Your browser does not support the audio element.
                      </audio>
                    ) : currentTranslation.audio_base64 ? (
                      <audio controls src={`data:audio/wav;base64,${currentTranslation.audio_base64}`} className="mx-auto">
                        Your browser does not support the audio element.
                      </audio>
                    ) : (
                      <>"{currentTranslation.originalCall}"</>
                    )}
                  </div>
                  <div className="flex items-center justify-between mt-3">
                    <div className="flex items-center space-x-2">
                      {getContextIcon(currentTranslation.context)}
                      <span className="text-sm">{currentTranslation.context.replace('_', ' ')}</span>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs text-white ${getEmotionColor(currentTranslation.emotion)}`}>
                      {currentTranslation.emotion}
                    </div>
                  </div>
                </div>
              </div>

              {/* Translation */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">AI Translation</h3>
                <div className="p-4 bg-white rounded-lg border">
                  <div className="flex items-center mb-3">
                    <Brain className="w-5 h-5 mr-2 text-purple-500" />
                    <span className="font-medium">AI Backend Analysis</span>
                  </div>
                  <blockquote className="text-lg italic text-slate-700 border-l-4 border-purple-500 pl-4">
                    "{currentTranslation.translation}"
                  </blockquote>
                  <div className="mt-4 p-3 bg-purple-50 rounded text-sm">
                    <strong>Context Analysis:</strong> This vocalization indicates {currentTranslation.context.replace('_', ' ')}, 
                    showing {currentTranslation.emotion} emotional state with behavioral patterns 
                    consistent with species-typical communication.
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500">
              <Volume2 className="w-16 h-16 mx-auto mb-4 text-slate-300" />
              <h3 className="text-lg font-medium mb-2">Waiting for Bird Communications</h3>
              <p>The AI system is listening for bird calls to translate...</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Analysis Tabs */}
      <Tabs defaultValue="recent" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="recent">Recent Calls</TabsTrigger>
          <TabsTrigger value="patterns">Communication Patterns</TabsTrigger>
          <TabsTrigger value="insights">AI Insights</TabsTrigger>
          <TabsTrigger value="stats">System Stats</TabsTrigger>
          <TabsTrigger value="audio">Audio Segments</TabsTrigger>
        </TabsList>

        <TabsContent value="recent">
          <Card>
            <CardHeader>
              <CardTitle>Recent Translations</CardTitle>
              <CardDescription>Latest decoded bird communications from backend</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {recentTranslations.length > 0 ? (
                  recentTranslations.map((translation, index) => (
                    <div key={index} className="p-4 border rounded-lg hover:bg-slate-50 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <span className="font-semibold text-blue-600">{translation.species}</span>
                            <div className={`px-2 py-1 rounded-full text-xs text-white ${getEmotionColor(translation.emotion)}`}>
                              {translation.emotion}
                            </div>
                            {translation.alertLevel && (
                              <div className={`px-2 py-1 rounded-full text-xs text-white ${getAlertLevelColor(translation.alertLevel)}`}>
                                {translation.alertLevel}
                              </div>
                            )}
                            <Badge variant="outline">{translation.confidence}%</Badge>
                            <span className="text-xs text-slate-500">{translation.timestamp}</span>
                          </div>
                          <div className="mb-2">
                            <span className="text-sm text-slate-600">Original: </span>
                            <span className="font-mono text-sm">"{translation.call}"</span>
                          </div>
                          <div className="text-slate-700">
                            <span className="text-sm text-slate-600">Translation: </span>
                            <span className="italic">"{translation.translation}"</span>
                          </div>
                          <div className="flex items-center mt-2 text-sm text-slate-500">
                            {getContextIcon(translation.context)}
                            <span className="ml-1">{translation.context.replace('_', ' ')}</span>
                            {translation.riskScore && (
                              <span className="ml-4">Risk: {Math.round(translation.riskScore * 100)}%</span>
                            )}
                          </div>
                        </div>
                        <div className="flex flex-col space-y-1">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => translation.id && acknowledgeAlert(translation.id)}
                          >
                            Acknowledge
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-slate-500">
                    <MessageSquare className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                    <p>No recent translations available</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="patterns">
          <Card>
            <CardHeader>
              <CardTitle>Communication Patterns</CardTitle>
              <CardDescription>Analysis from backend pattern recognition</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {Object.entries(communicationPatterns).length > 0 ? (
                  Object.entries(communicationPatterns).map(([species, patterns]) => (
                    <div key={species} className="p-4 border rounded-lg">
                      <h3 className="font-semibold mb-3">{species}</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h4 className="font-medium mb-2">Behavioral Intents</h4>
                          <div className="space-y-1">
                            {Object.entries(patterns.intents || {}).map(([intent, count]) => (
                              <div key={intent} className="flex justify-between text-sm">
                                <span>{intent.replace('_', ' ')}</span>
                                <span className="font-medium">{count}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                        <div>
                          <h4 className="font-medium mb-2">Communication Types</h4>
                          <div className="space-y-1">
                            {Object.entries(patterns.communication_types || {}).map(([type, count]) => (
                              <div key={type} className="flex justify-between text-sm">
                                <span>{type.replace('_', ' ')}</span>
                                <span className="font-medium">{count}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-slate-500">
                    <Music className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                    <p>No communication patterns data available</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights">
          <Card>
            <CardHeader>
              <CardTitle>AI Insights</CardTitle>
              <CardDescription>Machine learning analysis and insights</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-3">Recent Activity</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Total Communications</span>
                      <span className="font-medium">{aiInsights.total_communications_analyzed || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Recent Activity</span>
                      <span className="font-medium">{aiInsights.recent_activity || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Species Diversity</span>
                      <span className="font-medium">{aiInsights.species_diversity || 0}</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="font-medium mb-3">AI Performance</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Classification Accuracy</span>
                      <span className="font-medium">
                        {aiInsights.ai_model_performance?.classification_accuracy ? 
                          `${Math.round(aiInsights.ai_model_performance.classification_accuracy * 100)}%` : 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Prediction Confidence</span>
                      <span className="font-medium">
                        {aiInsights.ai_model_performance?.behavioral_prediction_confidence ? 
                          `${Math.round(aiInsights.ai_model_performance.behavioral_prediction_confidence * 100)}%` : 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Analysis Success Rate</span>
                      <span className="font-medium">
                        {aiInsights.ai_model_performance?.communication_analysis_success_rate ? 
                          `${Math.round(aiInsights.ai_model_performance.communication_analysis_success_rate * 100)}%` : 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stats">
          <Card>
            <CardHeader>
              <CardTitle>System Statistics</CardTitle>
              <CardDescription>Backend system performance and metrics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-800 mb-2">Detection Stats</h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span>Total Detections</span>
                      <span className="font-medium">{systemStats.total_detections || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Active Alerts</span>
                      <span className="font-medium">{systemStats.active_alerts || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Species Identified</span>
                      <span className="font-medium">{systemStats.species_count || 0}</span>
                    </div>
                  </div>
                </div>
                
                <div className="p-4 bg-purple-50 rounded-lg">
                  <h4 className="font-medium text-purple-800 mb-2">AI Statistics</h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span>Patterns Analyzed</span>
                      <span className="font-medium">{systemStats.ai_statistics?.communication_patterns_analyzed || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Behavior Profiles</span>
                      <span className="font-medium">{systemStats.ai_statistics?.species_behavior_profiles || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Model Status</span>
                      <span className="font-medium">{systemStats.ai_statistics?.ai_model_status || 'Unknown'}</span>
                    </div>
                  </div>
                </div>
                
                <div className="p-4 bg-green-50 rounded-lg">
                  <h4 className="font-medium text-green-800 mb-2">Connection Stats</h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span>Active Connections</span>
                      <span className="font-medium">{systemStats.ai_statistics?.active_monitoring_sessions || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Avg Risk Score</span>
                      <span className="font-medium">
                        {systemStats.ai_statistics?.average_risk_score ? 
                          `${Math.round(systemStats.ai_statistics.average_risk_score * 100)}%` : 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Status</span>
                      <span className={`font-medium ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
                        {isConnected ? 'Connected' : 'Disconnected'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audio">
          <Card>
            <CardHeader>
              <CardTitle>Detected Bird Call Audio Segments</CardTitle>
              <CardDescription>Playback and download detected bird call audio from the AI system (served by Flask backend)</CardDescription>
            </CardHeader>
            <CardContent>
              {audioLoading ? (
                <div>Loading audio segments...</div>
              ) : audioError ? (
                <div className="text-red-500">{audioError}</div>
              ) : audioSegments.length === 0 ? (
                <div>No audio segments available.</div>
              ) : (
                <ul className="space-y-4">
                  {audioSegments.map(segment => (
                    <li key={segment.segment_id} className="border p-3 rounded">
                      <div>
                        <strong>File:</strong> {segment.filename} <br />
                        <strong>Timestamp:</strong> {new Date(segment.timestamp).toLocaleString()} <br />
                        <strong>Duration:</strong> {segment.duration}s
                      </div>
                      <audio
                        controls
                        src={`${AUDIO_API_BASE}/audio-segment/${segment.segment_id}/play`}
                        className="mt-2"
                      />
                      <div className="mt-2">
                        <a
                          href={`${AUDIO_API_BASE}/audio-segment/${segment.segment_id}/download`}
                          className="text-blue-600 underline mr-4"
                          download
                        >
                          Download
                        </a>
                        <a
                          href={`${AUDIO_API_BASE}/audio-segment/${segment.segment_id}/base64`}
                          className="text-blue-600 underline"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          View Base64
                        </a>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default BirdTranslator;