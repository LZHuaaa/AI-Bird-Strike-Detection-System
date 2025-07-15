
import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Globe, 
  MapPin, 
  TrendingUp, 
  Users,
  Thermometer,
  Wind,
  Calendar,
  Camera,
  Share2,
  Database
} from 'lucide-react';

const GlobalNetwork = () => {
  const connectedSites = [
    {
      name: 'JFK International Airport',
      location: 'New York, USA',
      status: 'Active',
      species: 23,
      sharedData: 1247,
      lastSync: '2 min ago'
    },
    {
      name: 'Heathrow Airport',
      location: 'London, UK',
      status: 'Active',
      species: 18,
      sharedData: 892,
      lastSync: '5 min ago'
    },
    {
      name: 'Changi Airport',
      location: 'Singapore',
      status: 'Active',
      species: 31,
      sharedData: 1566,
      lastSync: '3 min ago'
    },
    {
      name: 'Toronto Pearson',
      location: 'Toronto, Canada',
      status: 'Offline',
      species: 15,
      sharedData: 634,
      lastSync: '2 hours ago'
    }
  ];

  const globalInsights = [
    {
      title: 'Worldwide Migration Surge',
      description: 'Robin migration activity increased 34% globally this week',
      impact: 'High',
      affectedSites: 12,
      timeframe: 'This week'
    },
    {
      title: 'Climate Correlation Pattern',
      description: 'Unusual bird behavior linked to temperature anomalies across 3 continents',
      impact: 'Medium',
      affectedSites: 8,
      timeframe: 'Last month'
    },
    {
      title: 'Urban Adaptation Study',
      description: 'Cities showing 67% faster bird adaptation to human schedules',
      impact: 'Research',
      affectedSites: 15,
      timeframe: 'Ongoing'
    }
  ];

  const citizenScience = [
    {
      contributor: 'BirdWatcher_NYC',
      location: 'Central Park, NY',
      observations: 156,
      species: 'American Robin',
      note: 'Unusual territorial behavior near Bethesda Fountain',
      verified: true
    },
    {
      contributor: 'NatureLover_UK',
      location: 'Hyde Park, London',
      observations: 89,
      species: 'European Robin',
      note: 'Early morning singing patterns changed significantly',
      verified: true
    },
    {
      contributor: 'SkyWatcher_SG',
      location: 'Marina Bay, Singapore',
      observations: 234,
      species: 'Oriental Magpie-Robin',
      note: 'New nesting site discovered near terminals',
      verified: false
    }
  ];

  return (
    <div className="space-y-6">
      {/* Global Network Overview */}
      <Card className="bg-gradient-to-r from-blue-50 to-green-50 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center text-xl">
            <Globe className="w-6 h-6 mr-3 text-blue-500" />
            Global Bird Intelligence Network
          </CardTitle>
          <CardDescription>
            Connecting worldwide bird monitoring systems for global insights
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-white/60 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">47</div>
              <div className="text-sm text-slate-600">Connected Sites</div>
            </div>
            <div className="text-center p-4 bg-white/60 rounded-lg">
              <div className="text-2xl font-bold text-green-600">156</div>
              <div className="text-sm text-slate-600">Species Tracked</div>
            </div>
            <div className="text-center p-4 bg-white/60 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">2.3M</div>
              <div className="text-sm text-slate-600">Data Points</div>
            </div>
            <div className="text-center p-4 bg-white/60 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">89%</div>
              <div className="text-sm text-slate-600">Uptime</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Connected Sites */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <MapPin className="w-5 h-5 mr-2 text-green-500" />
            Connected Airport Systems
          </CardTitle>
          <CardDescription>Real-time data sharing with global bird monitoring networks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {connectedSites.map((site, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className={`w-3 h-3 rounded-full ${site.status === 'Active' ? 'bg-green-500' : 'bg-red-500'}`} />
                  <div>
                    <div className="font-semibold">{site.name}</div>
                    <div className="text-sm text-slate-600">{site.location}</div>
                  </div>
                </div>
                <div className="flex items-center space-x-6 text-sm">
                  <div className="text-center">
                    <div className="font-medium">{site.species}</div>
                    <div className="text-slate-600">Species</div>
                  </div>
                  <div className="text-center">
                    <div className="font-medium">{site.sharedData}</div>
                    <div className="text-slate-600">Data Points</div>
                  </div>
                  <div className="text-center">
                    <div className="font-medium">{site.lastSync}</div>
                    <div className="text-slate-600">Last Sync</div>
                  </div>
                  <Badge variant={site.status === 'Active' ? 'default' : 'secondary'}>
                    {site.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Global Insights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-purple-500" />
            Global Bird Behavior Insights
          </CardTitle>
          <CardDescription>Cross-continental patterns and correlations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {globalInsights.map((insight, index) => (
              <div key={index} className="p-4 border rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-slate-800">{insight.title}</h3>
                  <div className="flex items-center space-x-2">
                    <Badge variant={
                      insight.impact === 'High' ? 'destructive' :
                      insight.impact === 'Medium' ? 'default' : 'secondary'
                    }>
                      {insight.impact}
                    </Badge>
                    <span className="text-sm text-slate-500">{insight.timeframe}</span>
                  </div>
                </div>
                <p className="text-slate-700 mb-3">{insight.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">
                    Affecting {insight.affectedSites} sites worldwide
                  </span>
                  <Button size="sm" variant="outline">
                    <Share2 className="w-3 h-3 mr-1" />
                    View Details
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Climate Correlation */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Thermometer className="w-5 h-5 mr-2 text-orange-500" />
              Climate Impact Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm">Temperature Correlation</span>
                <Badge className="bg-orange-100 text-orange-800">Strong (87%)</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Precipitation Impact</span>
                <Badge className="bg-blue-100 text-blue-800">Moderate (62%)</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Wind Pattern Influence</span>
                <Badge className="bg-green-100 text-green-800">High (91%)</Badge>
              </div>
              <div className="mt-4 p-3 bg-slate-50 rounded text-sm">
                Birds show increased activity during 15-20°C temperatures with light winds under 10mph.
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Calendar className="w-5 h-5 mr-2 text-teal-500" />
              Seasonal Patterns
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-slate-500">
              <Calendar className="w-16 h-16 mx-auto mb-4 text-slate-300" />
              <p>Global seasonal pattern analysis</p>
              <p className="text-sm mt-1">Migration timing comparisons across regions</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Citizen Science Integration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Users className="w-5 h-5 mr-2 text-blue-500" />
            Citizen Science Contributions
          </CardTitle>
          <CardDescription>Community observations enhancing our understanding</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {citizenScience.map((contribution, index) => (
              <div key={index} className="p-4 border rounded-lg hover:bg-slate-50 transition-colors">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-green-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                      {contribution.contributor.charAt(0)}
                    </div>
                    <div>
                      <div className="font-medium">{contribution.contributor}</div>
                      <div className="text-sm text-slate-600">{contribution.location}</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {contribution.verified && (
                      <Badge className="bg-green-100 text-green-800">Verified</Badge>
                    )}
                    <span className="text-sm text-slate-500">{contribution.observations} obs.</span>
                  </div>
                </div>
                <div className="ml-13">
                  <div className="text-sm mb-1">
                    <span className="font-medium">{contribution.species}:</span> {contribution.note}
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 text-center">
            <Button variant="outline">
              <Camera className="w-4 h-4 mr-2" />
              Submit Observation
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GlobalNetwork;
