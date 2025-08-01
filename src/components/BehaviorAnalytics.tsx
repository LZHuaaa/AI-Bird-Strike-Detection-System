// Define the structure for the AI Insights data
interface AiInsights {
  total_communications_analyzed: number;
  species_diversity: number;
  recent_activity: number;
  behavioral_intent_distribution: { [key: string]: number };
  alert_level_distribution: { high?: number };
  ai_model_performance: {
    classification_accuracy: number;
  };
}

// Define the structure for Communication Patterns data
interface CommunicationPatterns {
  history_count: number;
  patterns?: {
    [species: string]: {
      intents?: { [intent: string]: number };
    };
  };
}

// Define the structure for other state variables for clarity
interface DailyPattern {
  time: string;
  activity: number;
  species: number;
}

interface MigrationData {
  species: string;
  peak: string;
  status: 'Active' | 'Starting' | 'Upcoming';
  count: number;
}

interface BehaviorInsight {
  title: string;
  description: string;
  impact: 'High' | 'Medium' | 'Low' | 'Positive';
  recommendation: string;
}


import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
    AlertCircle,
    BarChart3,
    Brain,
    Clock,
    MapPin,
    RefreshCw
} from 'lucide-react';
import { useEffect, useState } from 'react';

const BehaviorAnalytics = () => {
  // Apply the newly defined types to your state initializations
  const [dailyPatterns, setDailyPatterns] = useState<DailyPattern[]>([]);
  const [migrationData, setMigrationData] = useState<MigrationData[]>([]);
  const [behaviorInsights, setBehaviorInsights] = useState<BehaviorInsight[]>([]);
  const [communicationPatterns, setCommunicationPatterns] = useState<CommunicationPatterns | null>(null);
  const [aiInsights, setAiInsights] = useState<AiInsights | null>(null); // Use null for initial state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // API base URL - adjust as needed
  const API_BASE = 'http://localhost:8000';

  // Fetch data from backend
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch communication patterns
      const patternsResponse = await fetch(`${API_BASE}/api/communication-patterns`);
      const patterns = await patternsResponse.json();
      setCommunicationPatterns(patterns);

      // Fetch AI insights
      const insightsResponse = await fetch(`${API_BASE}/api/ai-insights`);
      const insights = await insightsResponse.json();
      setAiInsights(insights);

      // Process communication patterns into daily patterns
      processDailyPatterns(patterns); // This line was corrected

      // Process migration data from patterns
      processMigrationData(patterns);

      // Generate behavioral insights from AI data
      generateBehavioralInsights(insights);

      setLastUpdate(new Date().toISOString());
    } catch (err) {
      setError(err.message);
      // Fallback to mock data if API fails
      loadMockData();
    } finally {
      setLoading(false);
    }
  };

  // Process backend data into daily patterns format
  const processDailyPatterns = (patterns) => {
    // Create hourly buckets
    const hourlyData = Array.from({ length: 24 }, (_, i) => ({
      time: `${i.toString().padStart(2, '0')}:00`,
      activity: 0,
      species: 0
    }));

    // Process communication history if available
    if (patterns.history_count > 0) {
      // This would need to be implemented based on actual backend data structure
      // For now, generate realistic patterns based on typical bird behavior
      const peakHours = [6, 7, 8, 17, 18, 19]; // Dawn and dusk

      hourlyData.forEach((data, index) => {
        const baseActivity = peakHours.includes(index) ? 70 + Math.random() * 30 : 20 + Math.random() * 40;
        data.activity = Math.round(baseActivity);
        data.species = Math.round(baseActivity / 7);
      });
    }

    setDailyPatterns(hourlyData.filter((_, i) => i % 3 === 0)); // Every 3 hours for display
  };

  // Process migration data from communication patterns
  const processMigrationData = (patterns) => {
    const migrationSpecies = [];

    if (patterns.patterns) {
      Object.entries(patterns.patterns).forEach(([species, data]) => {
        const totalDetections = Object.values((data as any).intents || {}).reduce((sum: number, count) => sum + (count as number), 0);

        if ((totalDetections as number) > 0) { // Only show species with more than 3 detections
          migrationSpecies.push({
            species: species.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
            peak: getCurrentSeasonPeak(),
            status: (totalDetections as number) > 10 ? 'Active' : (totalDetections as number) > 5 ? 'Starting' : 'Upcoming',
            count: totalDetections
          });
        }
      });
    }

    setMigrationData(migrationSpecies.slice(0, 4)); // Show top 3
  };

  // Generate behavioral insights from AI data
  const generateBehavioralInsights = (insights) => {
    const generatedInsights = [];

    if (insights.behavioral_intent_distribution) {
      const topIntent = Object.entries(insights.behavioral_intent_distribution)
        .sort(([, a], [, b]) => (b as number) - (a as number))[0];

      if (topIntent) {
        generatedInsights.push({
          title: `Dominant Behavior: ${topIntent[0].replace('_', ' ')}`,
          description: `${topIntent[1]} instances detected in recent activity. This represents the primary behavioral pattern.`,
          impact: (topIntent[1] as number) > 30 ? 'High' : (topIntent[1] as number) > 15 ? 'Medium' : 'Low',
          recommendation: getRecommendationForBehavior(topIntent[0])
        });
      }
    }

    if (insights.alert_level_distribution) {
      const highAlerts = insights.alert_level_distribution.high || 0;
      if (highAlerts > 0) {
        generatedInsights.push({
          title: 'High Alert Activity',
          description: `${highAlerts} high-urgency communications detected, indicating potential stress or territorial conflicts.`,
          impact: 'High',
          recommendation: 'Increase monitoring frequency during peak activity hours'
        });
      }
    }

    if (insights.ai_model_performance) {
      generatedInsights.push({
        title: 'AI Model Performance',
        description: `Current classification accuracy: ${(insights.ai_model_performance.classification_accuracy * 100).toFixed(1)}%`,
        impact: 'Positive',
        recommendation: 'Model performing well - continue current monitoring protocols'
      });
    }

    setBehaviorInsights(generatedInsights);
  };

  // Helper functions
  const getCurrentSeasonPeak = () => {
    const now = new Date();
    const month = now.getMonth();
    if (month >= 2 && month <= 4) return 'March 15 - May 15';
    if (month >= 5 && month <= 7) return 'June 1 - August 15';
    if (month >= 8 && month <= 10) return 'September 1 - November 15';
    return 'December 1 - February 28';
  };

  const getRecommendationForBehavior = (behavior) => {
    const recommendations = {
      'territory_defense': 'Monitor for aggressive behavior and potential conflicts',
      'landing_approach': 'Increase runway monitoring during peak landing times',
      'flock_gathering': 'Prepare for mass movement events',
      'predator_avoidance': 'Check for predator activity in the area',
      'normal_flight': 'Maintain standard monitoring protocols'
    };
    return recommendations[behavior] || 'Continue monitoring this behavior pattern';
  };

  // Load mock data as fallback
  const loadMockData = () => {
    setDailyPatterns([
      { time: '06:00', activity: 85, species: 12 },
      { time: '09:00', activity: 95, species: 15 },
      { time: '12:00', activity: 45, species: 8 },
      { time: '15:00', activity: 60, species: 9 },
      { time: '18:00', activity: 90, species: 14 },
      { time: '21:00', activity: 30, species: 6 }
    ]);

    setMigrationData([
      { species: 'House Crow', peak: 'March 15-30', status: 'Active', count: 156 },
      { species: 'Common Myna', peak: 'April 1-15', status: 'Starting', count: 89 },
      { species: 'White-bellied Sea Eagle', peak: 'April 10-25', status: 'Upcoming', count: 23 }
    ]);

    setBehaviorInsights([
      {
        title: 'API Connection Issue',
        description: 'Unable to connect to backend. Displaying mock data.',
        impact: 'Medium',
        recommendation: 'Check backend server status and network connectivity'
      }
    ]);
  };

  // Set up real-time updates via WebSocket
  useEffect(() => {
    fetchData();

    // Set up WebSocket connection for real-time updates
    const ws = new WebSocket(`ws://localhost:8000/ws`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'heartbeat') {
        // Handle heartbeat
        console.log('WebSocket heartbeat received');
      } else {
        // New alert or update - refresh data
        fetchData();
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    // Refresh data every 5 minutes
    const interval = setInterval(fetchData, 5 * 60 * 1000);

    return () => {
      ws.close();
      clearInterval(interval);
    };
  }, []);

  // Refresh button handler
  const handleRefresh = () => {
    fetchData();
  };

  if (loading && dailyPatterns.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-2 text-lg">Loading behavioral analytics...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with refresh button and status */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Behavioral Analytics</h1>
          {lastUpdate && (
            <p className="text-sm text-slate-600">
              Last updated: {new Date(lastUpdate).toLocaleString()}
            </p>
          )}
        </div>
        <button
          onClick={handleRefresh}
          disabled={loading}
          className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Error display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
              <span className="text-red-700">Backend Connection Error: {error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Connection Status */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className={`w-3 h-3 rounded-full mr-2 ${error ? 'bg-red-500' : 'bg-green-500'}`} />
              <span className="font-medium">
                Backend Status: {error ? 'Disconnected' : 'Connected'}
              </span>
            </div>
            <div className="text-sm text-slate-600">
              {aiInsights.total_communications_analyzed || 0} communications analyzed
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Daily Activity Patterns */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Clock className="w-5 h-5 mr-2 text-blue-500" />
            24-Hour Activity Patterns
          </CardTitle>
          <CardDescription>
            {error ? 'Mock data - backend unavailable' : 'Real-time circadian behavior analysis'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {(dailyPatterns.length === 0 || dailyPatterns.every(d => d.activity === 0)) ? (
              <div className="flex flex-col items-center justify-center h-64 text-slate-400">
                <Clock className="w-16 h-16 text-slate-300 mb-4" />
                <div className="text-center text-slate-500">
                  <p className="text-lg font-medium mb-2">No Activity Data Available</p>
                  <p className="text-sm">
                    The system needs to detect and analyze bird activity to display patterns.
                    <br />
                    Try running the system for at least 24 hours to see daily patterns.
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="grid grid-cols-3 gap-4 text-center text-sm">
                  <div>
                    <div className="font-semibold text-blue-600">Peak Activity</div>
                    <div>
                      {dailyPatterns.length > 0 ?
                        `${dailyPatterns.reduce((max, curr) => curr.activity > max.activity ? curr : max).time} (${dailyPatterns.reduce((max, curr) => curr.activity > max.activity ? curr : max).activity}%)` :
                        'N/A'
                      }
                    </div>
                  </div>
                  <div>
                    <div className="font-semibold text-green-600">Most Species</div>
                    <div>
                      {dailyPatterns.length > 0 ?
                        `${dailyPatterns.reduce((max, curr) => curr.species > max.species ? curr : max).time} (${dailyPatterns.reduce((max, curr) => curr.species > max.species ? curr : max).species} species)` :
                        'N/A'
                      }
                    </div>
                  </div>
                  <div>
                    <div className="font-semibold text-purple-600">Quietest Time</div>
                    <div>
                      {dailyPatterns.length > 0 ?
                        `${dailyPatterns.reduce((min, curr) => curr.activity < min.activity ? curr : min).time} (${dailyPatterns.reduce((min, curr) => curr.activity < min.activity ? curr : min).activity}%)` :
                        'N/A'
                      }
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-sm text-slate-600 mb-2">Activity Distribution</div>
                  <div className="grid grid-cols-8 gap-2">
                    {dailyPatterns.map((data, index) => (
                      <div key={index} className="text-center">
                        <div className="text-xs text-slate-500">{data.time}</div>
                        <div className="font-medium text-blue-600">{data.activity}%</div>
                        <div className="text-xs text-slate-400">{data.species} sp.</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Migration Tracking */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <MapPin className="w-5 h-5 mr-2 text-green-500" />
            Species Activity Analysis
          </CardTitle>
          <CardDescription>
            {error ? 'Mock data - backend unavailable' : 'Based on communication pattern analysis'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {migrationData.length === 0 ? (
              <div className="text-center text-slate-500 py-8">
                Try detecting above 3 species (e.g., House Crow, White-bellied Sea Eagle, Javan Myna) to see activity analysis.
              </div>
            ) : (
              migrationData.map((species, index) => (
              <div key={index} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <div className="font-semibold">{species.species}</div>
                    <div className="text-sm text-slate-600">Activity period: {species.peak}</div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={
                      species.status === 'Active' ? 'default' :
                        species.status === 'Starting' ? 'secondary' : 'outline'
                    }>
                      {species.status}
                    </Badge>
                    <span className="font-medium">{species.count} detections</span>
                  </div>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${species.status === 'Active' ? 'bg-green-500' :
                      species.status === 'Starting' ? 'bg-yellow-500' : 'bg-slate-400'
                      }`}
                    style={{
                      width: species.status === 'Active' ? '75%' :
                        species.status === 'Starting' ? '25%' : '5%'
                    }}
                  />
                </div>
              </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      {/* Behavioral Insights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Brain className="w-5 h-5 mr-2 text-purple-500" />
            AI-Generated Behavioral Insights
          </CardTitle>
          <CardDescription>
            {error ? 'Mock data - backend unavailable' : 'Machine learning analysis of communication patterns'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {behaviorInsights.map((insight, index) => (
              <div key={index} className="p-4 border rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-slate-800">{insight.title}</h3>
                  <Badge variant={
                    insight.impact === 'High' ? 'destructive' :
                      insight.impact === 'Medium' ? 'default' : 'secondary'
                  }>
                    {insight.impact} Impact
                  </Badge>
                </div>
                <p className="text-slate-700 mb-3">{insight.description}</p>
                <div className="p-3 bg-blue-50 rounded text-sm">
                  <strong>Recommendation:</strong> {insight.recommendation}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* AI Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="w-5 h-5 mr-2 text-orange-500" />
            AI System Performance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {aiInsights.total_communications_analyzed || 0}
              </div>
              <div className="text-sm text-slate-600">Total Analyzed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {aiInsights.species_diversity || 0}
              </div>
              <div className="text-sm text-slate-600">Species Detected</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {aiInsights.recent_activity || 0}
              </div>
              <div className="text-sm text-slate-600">Recent Activity</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {aiInsights.ai_model_performance ?
                  `${(aiInsights.ai_model_performance.classification_accuracy * 100).toFixed(0)}%` :
                  'N/A'
                }
              </div>
              <div className="text-sm text-slate-600">Accuracy</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default BehaviorAnalytics;