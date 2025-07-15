import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, Calendar, Clock, AlertTriangle, Sun, Moon, Cloud, Thermometer, Wind, Bird, Eye } from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { format } from 'date-fns';

// API base URL
const API_BASE_URL = 'http://localhost:8000/api';

interface WeatherData {
  temperature: number;
  windSpeed: number;
  windDirection: string;
  visibility: number;
  precipitation: number;
  birdFavorability: number;
}

interface ForecastPoint {
  hour: number;
  risk: number;
  factors: string[];
  timeLabel: string;
}

const calculateRisk = (hour: number, weather: WeatherData): ForecastPoint => {
  let risk = weather.birdFavorability || 0;
  const factors: string[] = [];

  // Adjust temperature based on time of day (Malaysian climate patterns)
  let adjustedTemp = weather.temperature;
  if (hour >= 2 && hour < 6) { // Pre-dawn (coolest)
    adjustedTemp = weather.temperature - 4;
  } else if (hour >= 6 && hour < 10) { // Morning (warming)
    adjustedTemp = weather.temperature - 2;
  } else if (hour >= 10 && hour < 16) { // Afternoon (hottest)
    adjustedTemp = weather.temperature + 2;
  } else if (hour >= 16 && hour < 20) { // Evening (cooling)
    adjustedTemp = weather.temperature - 1;
  } else { // Night (cool)
    adjustedTemp = weather.temperature - 3;
  }

  // Time-based risk factors (aligned with backend scoring)
  if (hour >= 18 && hour < 19) { // Dusk peak (6-7pm)
    risk = Math.min(risk + 40, 100);
    factors.push("Peak evening activity");
  } else if (hour >= 6 && hour < 8) { // Dawn peak (6-8am)
    risk = Math.min(risk + 35, 100);
    factors.push("Peak morning activity");
  } else if (hour >= 8 && hour < 10) { // Early morning
    risk = Math.min(risk + 25, 100);
    factors.push("Active morning period");
  } else if (hour >= 16 && hour < 18) { // Late afternoon
    risk = Math.min(risk + 20, 100);
    factors.push("Increasing evening activity");
  } else if ((hour >= 20 && hour <= 23) || (hour >= 0 && hour < 4)) { // Night
    risk = Math.max(risk - 20, 20);
    factors.push("Minimal night activity");
  }

  // Weather-based risk factors with adjusted temperature
  if (adjustedTemp >= 25 && adjustedTemp <= 30) {
    risk = Math.min(risk + 10, 100);
    factors.push(`Optimal temperature (${adjustedTemp.toFixed(1)}°C)`);
  } else if (adjustedTemp > 30) {
    risk = Math.max(risk - 15, 20);
    factors.push(`High temperature (${adjustedTemp.toFixed(1)}°C) - reduced activity`);
  } else if (adjustedTemp < 25) {
    risk = Math.max(risk - 10, 20);
    factors.push(`Cool temperature (${adjustedTemp.toFixed(1)}°C) - moderate activity`);
  }

  if (weather.windSpeed < 10) {
    risk = Math.min(risk + 10, 100);
    factors.push(`Favorable wind conditions (${weather.windSpeed} km/h ${weather.windDirection})`);
  }

  if (weather.visibility > 8) {
    risk = Math.min(risk + 5, 100);
    factors.push(`Excellent visibility (${weather.visibility} km)`);
  }

  // Format time label
  const timeLabel = `${String(hour).padStart(2, '0')}:00`;

  return {
    hour,
    risk: Math.round(risk),
    factors,
    timeLabel
  };
};

const getRiskLevel = (risk: number) => {
  if (risk >= 60) return { label: 'High Risk', color: 'text-red-600 bg-red-100' };
  if (risk >= 40) return { label: 'Moderate Risk', color: 'text-yellow-600 bg-yellow-100' };
  return { label: 'Low Risk', color: 'text-green-600 bg-green-100' };
};

const getTimeOfDay = (hour: number) => {
  if (hour >= 5 && hour < 12) return { label: 'Morning', icon: Sun };
  if (hour >= 12 && hour < 17) return { label: 'Afternoon', icon: Sun };
  if (hour >= 17 && hour < 20) return { label: 'Evening', icon: Moon };
  return { label: 'Night', icon: Moon };
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border">
        <p className="font-semibold">{data.timeLabel}</p>
        <p className="text-sm text-slate-600">Risk Level: {data.risk}%</p>
        <div className="text-xs text-slate-500 mt-1">
          {data.factors.join(" • ")}
        </div>
      </div>
    );
  }
  return null;
};

const PeakActivityTimes = () => {
  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        <Clock className="w-5 h-5 mr-2 text-blue-500" />
        Peak Activity Times
      </h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Sun className="w-4 h-4 mr-2 text-orange-500" />
            <span>Dawn Peak</span>
          </div>
          <Badge variant="destructive">06:00 - 08:00</Badge>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Sun className="w-4 h-4 mr-2 text-yellow-500" />
            <span>Morning Activity</span>
          </div>
          <Badge variant="secondary">08:00 - 10:00</Badge>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Sun className="w-4 h-4 mr-2 text-orange-500" />
            <span>Dusk Peak</span>
          </div>
          <Badge variant="destructive">18:00 - 19:00</Badge>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Moon className="w-4 h-4 mr-2 text-slate-500" />
            <span>Night (Low Activity)</span>
          </div>
          <Badge variant="outline">20:00 - 04:00</Badge>
        </div>
      </div>
    </div>
  );
};

const PredictiveRiskForecast = () => {
  const [weatherData, setWeatherData] = useState<WeatherData>({
    temperature: 0,
    windSpeed: 0,
    windDirection: 'N/A',
    visibility: 0,
    precipitation: 0,
    birdFavorability: 0
  });
  const [hourlyForecast, setHourlyForecast] = useState<ForecastPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWeatherData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/risk-assessment/weather`);
        if (!response.ok) throw new Error('Failed to fetch weather data');
        const data = await response.json();
        
        setWeatherData({
          temperature: data.temperature || 0,
          windSpeed: data.windSpeed || 0,
          windDirection: data.windDirection || 'N/A',
          visibility: data.visibility || 0,
          precipitation: data.precipitation || 0,
          birdFavorability: data.birdFavorability || 0
        });

        // Get current hour in 24-hour format
        const now = new Date();
        const currentHour = now.getHours();
        const forecast: ForecastPoint[] = [];
        
        // Generate forecast for next 24 hours starting from current hour
        for (let i = 0; i < 24; i++) {
          const forecastHour = (currentHour + i) % 24;
          const forecastDate = new Date(now);
          forecastDate.setHours(forecastHour);
          
          // If hour is less than current hour, it's tomorrow
          if (forecastHour < currentHour) {
            forecastDate.setDate(forecastDate.getDate() + 1);
          }
          
          forecast.push({
            ...calculateRisk(forecastHour, data),
            timeLabel: forecastDate.toLocaleTimeString('en-US', { 
              hour: '2-digit', 
              minute: '2-digit', 
              hour12: false 
            })
          });
        }

        setHourlyForecast(forecast);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching weather data:', error);
        setLoading(false);
      }
    };

    fetchWeatherData();
    // Refresh data every 15 minutes
    const interval = setInterval(fetchWeatherData, 15 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // Find next peak risk period
  const nextPeakRisk = useMemo(() => {
    if (!hourlyForecast.length) return null;
    
    const now = new Date();
    const currentHour = now.getHours();
    
    // Look for the next highest risk period
    return hourlyForecast
      .filter(forecast => {
        const forecastHour = parseInt(forecast.timeLabel.split(':')[0]);
        return forecastHour > currentHour || (currentHour > 20 && forecastHour < 8); // Include early morning next day
      })
      .reduce((max, forecast) => 
        forecast.risk > max.risk ? forecast : max,
        hourlyForecast[0]
      );
  }, [hourlyForecast]);

  if (loading) {
    return (
      <Card>
        <CardContent className="py-6">
          <div className="text-center text-slate-500">Loading forecast data...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <TrendingUp className="w-5 h-5 mr-2 text-blue-500" />
          24-Hour Forecast
        </CardTitle>
        {nextPeakRisk && (
          <CardDescription>
            Next peak risk at {nextPeakRisk.timeLabel} ({nextPeakRisk.risk}% risk)
          </CardDescription>
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Current Period Analysis */}
          <div className="p-4 bg-slate-50 rounded-lg">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <Clock className="w-4 h-4 mr-2" />
              Current Period Analysis
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-slate-600 mb-1">Time of Day</div>
                <div className="flex items-center">
                  {React.createElement(getTimeOfDay(new Date().getHours()).icon, { className: "w-4 h-4 mr-2" })}
                  <span className="font-medium">{getTimeOfDay(new Date().getHours()).label}</span>
                </div>
              </div>
              <div>
                <div className="text-sm text-slate-600 mb-1">Next Peak Risk</div>
                <div className="flex items-center">
                  <AlertTriangle className="w-4 h-4 mr-2 text-orange-500" />
                  <span className="font-medium">{nextPeakRisk?.timeLabel} ({nextPeakRisk?.risk}% Risk)</span>
                </div>
              </div>
            </div>
          </div>

          {/* Chart */}
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={hourlyForecast}
                margin={{ top: 10, right: 145, left: 0, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="rgb(239 68 68)" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="rgb(96 165 250)" stopOpacity={0.1} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="hour"
                  tickFormatter={(hour) => format(new Date().setHours(hour), 'HH:mm')}
                  stroke="#64748b"
                  fontSize={12}
                />
                <YAxis
                  tickFormatter={(value) => `${value}%`}
                  stroke="#64748b"
                  fontSize={12}
                  domain={[0, 100]}
                  ticks={[0, 25, 50, 75, 100]}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-white p-2 shadow rounded border">
                          <p className="text-sm font-medium">
                            {format(new Date().setHours(data.hour), 'HH:mm')}
                          </p>
                          <p className="text-sm text-slate-600">
                            Risk Level: {data.risk}%
                          </p>
                          {data.factors.length > 0 && (
                            <ul className="text-xs text-slate-500 mt-1">
                              {data.factors.map((factor: string, i: number) => (
                                <li key={i}>• {factor}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <ReferenceLine
                  y={60}
                  label={{ value: "High Risk Threshold", position: "right", fill: "#dc2626" }}
                  stroke="#dc2626"
                  strokeDasharray="3 3"
                />
                <ReferenceLine
                  y={40}
                  label={{ value: "Moderate Risk", position: "right", fill: "#f97316" }}
                  stroke="#f97316"
                  strokeDasharray="3 3"
                />
                <Area
                  type="monotone"
                  dataKey="risk"
                  stroke="#3b82f6"
                  fill="url(#riskGradient)"
                  isAnimationActive={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Replace Weather Impact with Peak Activity Times */}
          <PeakActivityTimes />
        </div>
      </CardContent>
    </Card>
  );
};

export default PredictiveRiskForecast; 