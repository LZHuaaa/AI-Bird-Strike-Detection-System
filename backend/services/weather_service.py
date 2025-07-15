import os
import requests
from datetime import datetime
import pytz  # for timezone handling
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY', '')
        self.base_url = 'https://api.openweathermap.org/data/2.5'
        # Kuala Lumpur coordinates
        self.lat = float(os.getenv('MALAYSIA_LAT', '3.1569'))  # KL latitude
        self.lon = float(os.getenv('MALAYSIA_LON', '101.7123'))  # KL longitude
        self.timezone = pytz.timezone('Asia/Kuala_Lumpur')

    def get_current_weather(self) -> Dict[str, Any]:
        """Fetch current weather data from OpenWeatherMap"""
        try:
            url = f"{self.base_url}/weather?lat={self.lat}&lon={self.lon}&appid={self.api_key}&units=metric"
            print(f"Attempting to fetch weather data with URL: {url}")
            
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
                
            data = response.json()

            # Get current time in Malaysia
            current_time = datetime.now(self.timezone)
            
            # Convert wind direction from degrees to cardinal direction
            wind_deg = data['wind'].get('deg', 0)
            wind_direction = self._degrees_to_cardinal(wind_deg)

            # Calculate bird favorability based on weather conditions and time
            bird_favorability = self._calculate_bird_favorability(data, current_time)

            return {
                "temperature": round(data['main']['temp']),  # Celsius
                "windSpeed": round(data['wind']['speed'] * 3.6),  # Convert m/s to km/h
                "windDirection": wind_direction,
                "precipitation": data.get('rain', {}).get('1h', 0),  # mm/hour
                "visibility": data['visibility'] / 1000,  # Convert m to km
                "birdFavorability": bird_favorability,
                "timestamp": current_time
            }
        except Exception as e:
            print(f"Error fetching weather data: {str(e)}")
            return None

    def _calculate_bird_favorability(self, weather_data: Dict, current_time: datetime) -> float:
        """Calculate bird activity favorability based on Malaysian weather patterns and bird behavior"""
        temp = weather_data['main']['temp']
        wind_speed = weather_data['wind']['speed'] * 3.6  # m/s to km/h
        visibility = weather_data['visibility'] / 1000  # m to km
        precipitation = weather_data.get('rain', {}).get('1h', 0)
        hour = current_time.hour

        print(f"Current time in Malaysia: {current_time}, Hour: {hour}")

        # Initialize scores
        weather_score = 0
        time_score = 0
        max_weather_score = 10  # Maximum possible weather score
        max_time_score = 10     # Maximum possible time score

        # Weather scoring (optimized for Malaysian tropical climate)
        
        # Temperature scoring - Malaysia's tropical climate
        if 25 <= temp <= 30:
            weather_score += 3  # Optimal temperature range for Malaysia
            print(f"Temperature {temp}°C is optimal (+3)")
        elif 22 <= temp <= 32:
            weather_score += 2  # Good temperature range
            print(f"Temperature {temp}°C is good (+2)")
        elif 20 <= temp <= 35:
            weather_score += 1  # Still acceptable
            print(f"Temperature {temp}°C is acceptable (+1)")
        else:
            print(f"Temperature {temp}°C is not ideal for bird activity")

        # Wind speed scoring - Malaysia's typical wind conditions
        # Convert m/s to km/h for easier understanding
        print(f"Wind speed: {wind_speed:.1f} km/h from {self._degrees_to_cardinal(weather_data['wind'].get('deg', 0))}")
        
        if 2 <= wind_speed <= 8:
            weather_score += 3  # Perfect conditions for most birds
            print(f"Wind speed {wind_speed:.1f} km/h is perfect for birds (+3)")
        elif 8 < wind_speed <= 15:
            weather_score += 2  # Good conditions
            print(f"Wind speed {wind_speed:.1f} km/h is good (+2)")
        elif wind_speed < 2:
            weather_score += 1  # Very light wind, still acceptable
            print(f"Wind speed {wind_speed:.1f} km/h is very light but acceptable (+1)")
        elif 15 < wind_speed <= 20:
            weather_score += 1  # Stronger but still manageable
            print(f"Wind speed {wind_speed:.1f} km/h is strong but manageable (+1)")
        elif 20 < wind_speed <= 25:
            weather_score -= 1  # Too strong for comfortable flight
            print(f"Wind speed {wind_speed:.1f} km/h is too strong for comfortable flight (-1)")
        else:  # > 25 km/h
            weather_score -= 2  # Dangerous for most birds
            print(f"Wind speed {wind_speed:.1f} km/h is dangerous for most birds (-2)")

        # Additional wind direction impact for Malaysia
        wind_direction = weather_data['wind'].get('deg', 0)
        # During monsoon seasons, certain wind directions are more significant
        if (45 <= wind_direction <= 90):  # NE to E winds (typical during Northeast monsoon)
            print("Northeast/East winds - typical monsoon pattern")

        # Visibility scoring
        if visibility > 8:
            weather_score += 2
            print(f"Visibility {visibility}km is excellent (+2)")
        elif visibility > 5:
            weather_score += 1
            print(f"Visibility {visibility}km is good (+1)")
        elif visibility < 2:
            weather_score -= 1
            print(f"Visibility {visibility}km is poor (-1)")

        # Precipitation scoring - heavily impacts bird activity in Malaysia
        if precipitation == 0:
            weather_score += 3
            print("No precipitation - excellent for birds (+3)")
        elif precipitation < 2:
            weather_score += 1
            print(f"Light precipitation {precipitation}mm - still okay (+1)")
        elif precipitation < 10:
            weather_score -= 1
            print(f"Moderate precipitation {precipitation}mm - reduced activity (-1)")
        else:
            weather_score -= 2
            print(f"Heavy precipitation {precipitation}mm - low activity (-2)")

        # Time of day scoring - based on Malaysian bird behavior patterns
        if 18 <= hour < 19:  # 6pm-7pm peak activity as specified
            time_score = 10
            print(f"Peak activity time - Evening (6-7pm) (+10)")
        elif 6 <= hour < 8:  # Dawn - second peak
            time_score = 9
            print(f"High activity time - Dawn (6-8am) (+9)")
        elif 8 <= hour < 10:  # Early morning - still active
            time_score = 7
            print(f"Good activity time - Early morning (8-10am) (+7)")
        elif 16 <= hour < 18:  # Late afternoon - preparing for evening
            time_score = 6
            print(f"Moderate activity time - Late afternoon (4-6pm) (+6)")
        elif 10 <= hour < 12:  # Mid-morning - moderate
            time_score = 5
            print(f"Moderate activity time - Mid-morning (10am-12pm) (+5)")
        elif 14 <= hour < 16:  # Early afternoon - some activity
            time_score = 4
            print(f"Low-moderate activity time - Early afternoon (2-4pm) (+4)")
        elif 12 <= hour < 14:  # Midday - hot, less active
            time_score = 3
            print(f"Low activity time - Midday (12-2pm) (+3)")
        elif 19 <= hour < 20:  # Early evening - winding down
            time_score = 3
            print(f"Low activity time - Early evening (7-8pm) (+3)")
        elif 20 <= hour or hour < 4:  # Night - minimal activity as specified
            time_score = 1
            print(f"Minimal activity time - Night (8pm-4am) (+1)")
        else:  # 4am-6am - early morning, low activity
            time_score = 2
            print(f"Low activity time - Early morning (4-6am) (+2)")

        print(f"Weather score: {weather_score}/{max_weather_score}")
        print(f"Time score: {time_score}/{max_time_score}")

        # Calculate final score with adjusted weights
        # Time of day: 70% weight (primary factor for bird activity)
        # Weather conditions: 30% weight
        weather_weight = 0.3
        time_weight = 0.7

        # Normalize scores to percentage
        weather_percentage = max(0, (weather_score / max_weather_score) * 100)
        time_percentage = (time_score / max_time_score) * 100

        print(f"Weather percentage: {weather_percentage}%")
        print(f"Time percentage: {time_percentage}%")

        final_score = (weather_percentage * weather_weight) + (time_percentage * time_weight)
        
        # Ensure score is between 0 and 100
        final_score = max(0, min(100, final_score))
        
        print(f"Final bird activity score: {final_score}%")
        
        return round(final_score, 2)

    def _degrees_to_cardinal(self, degrees: float) -> str:
        """Convert degrees to cardinal direction with full names"""
        if 348.75 <= degrees or degrees < 11.25:
            return "North"
        elif 11.25 <= degrees < 33.75:
            return "North-Northeast"
        elif 33.75 <= degrees < 56.25:
            return "Northeast"
        elif 56.25 <= degrees < 78.75:
            return "East-Northeast"
        elif 78.75 <= degrees < 101.25:
            return "East"
        elif 101.25 <= degrees < 123.75:
            return "East-Southeast"
        elif 123.75 <= degrees < 146.25:
            return "Southeast"
        elif 146.25 <= degrees < 168.75:
            return "South-Southeast"
        elif 168.75 <= degrees < 191.25:
            return "South"
        elif 191.25 <= degrees < 213.75:
            return "South-Southwest"
        elif 213.75 <= degrees < 236.25:
            return "Southwest"
        elif 236.25 <= degrees < 258.75:
            return "West-Southwest"
        elif 258.75 <= degrees < 281.25:
            return "West"
        elif 281.25 <= degrees < 303.75:
            return "West-Northwest"
        elif 303.75 <= degrees < 326.25:
            return "Northwest"
        else:  # 326.25 to 348.75
            return "North-Northwest"

    def get_bird_activity_summary(self) -> str:
        """Get a human-readable summary of current bird activity conditions"""
        weather_data = self.get_current_weather()
        if not weather_data:
            return "Unable to fetch weather data"
        
        score = weather_data['birdFavorability']
        hour = weather_data['timestamp'].hour
        temp = weather_data['temperature']
        precipitation = weather_data['precipitation']
        
        # Activity level classification
        if score >= 80:
            activity_level = "Excellent"
        elif score >= 60:
            activity_level = "Good"
        elif score >= 40:
            activity_level = "Moderate"
        elif score >= 20:
            activity_level = "Low"
        else:
            activity_level = "Very Low"
        
        # Generate summary
        summary = f"Bird Activity: {activity_level} ({score}%)\n"
        summary += f"Temperature: {temp}°C\n"
        summary += f"Wind: {weather_data['windSpeed']} km/h {weather_data['windDirection']}\n"
        
        if precipitation > 0:
            summary += f"Precipitation: {precipitation}mm/h (reducing bird activity)\n"
        else:
            summary += "No precipitation (good for birds)\n"
        
        # Time-based advice
        if 18 <= hour < 19:
            summary += "Peak time for bird watching (6-7pm)!"
        elif 6 <= hour < 8:
            summary += "Great time for early morning birding!"
        elif 20 <= hour or hour < 4:
            summary += "Night time - minimal bird activity expected"
        elif precipitation > 5:
            summary += "Rainy conditions - birds likely sheltering"
        
        return summary 