#!/usr/bin/env python3
"""
Enhanced Database setup for Bird Strike Detection System with Additional Tables
Using SQLite for hackathon simplicity with SQLAlchemy ORM
"""

import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json
import os
import requests
import base64
from io import BytesIO
from PIL import Image

# Database configuration
DATABASE_URL = "sqlite:///bird_strike_detection.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Existing Database Models (keeping all your original models)
class BirdSpecies(Base):
    __tablename__ = "bird_species"
    
    id = Column(Integer, primary_key=True, index=True)
    scientific_name = Column(String, unique=True, index=True)
    common_name = Column(String, index=True)
    risk_level = Column(String)  # LOW, MEDIUM, HIGH
    size_category = Column(String)  # SMALL, MEDIUM, LARGE
    typical_behavior = Column(Text)
    migration_pattern = Column(String)
    
    # Image data
    image_url = Column(String)
    image_data = Column(Text)
    image_source = Column(String)
    image_fetched_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    detections = relationship("BirdDetection", back_populates="species")
    alerts = relationship("BirdAlert", back_populates="species")
    personalities = relationship("BirdPersonality", back_populates="species")
    migration_data = relationship("MigrationData", back_populates="species")

class BirdDetection(Base):
    __tablename__ = "bird_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    species_id = Column(Integer, ForeignKey("bird_species.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    confidence = Column(Float)
    
    # Audio characteristics
    frequency_range = Column(String)  # JSON: {"min": 100, "max": 8000}
    amplitude = Column(Float)
    duration = Column(Float)
    call_type = Column(String)  # TERRITORIAL, FEEDING, SOCIAL, WARNING, MATING
    
    # Location data
    location_x = Column(Float)
    location_y = Column(Float)
    distance_from_runway = Column(Float)
    direction = Column(String)  # N, NE, E, SE, S, SW, W, NW
    
    # Environmental context
    weather_conditions = Column(String)
    time_of_day = Column(String)
    season = Column(String)
    
    # AI Analysis
    emotional_state = Column(String)  # CALM, ALERT, AGITATED, FOCUSED, PANICKED
    behavioral_pattern = Column(String)
    group_behavior = Column(Boolean, default=False)
    
    # Location type
    location_type = Column(String, default="airport")

    # NEW: Audio segment filename for playback
    audio_segment_filename = Column(String, nullable=True)
    
    # NEW: Track if detection occurred during predator sound playback
    during_predator_sound = Column(Boolean, default=False)
    
    # Relationships
    species = relationship("BirdSpecies", back_populates="detections")
    alerts = relationship("BirdAlert", back_populates="detection")
    translations = relationship("BirdTranslation", back_populates="detection")

class BirdAlert(Base):
    __tablename__ = "bird_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, ForeignKey("bird_detections.id"))
    species_id = Column(Integer, ForeignKey("bird_species.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Alert details
    alert_level = Column(String)  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score = Column(Float)
    recommended_action = Column(String)  # MONITOR, DELAY_TAKEOFF, EMERGENCY_PROTOCOL
    
    # Strike risk factors
    proximity_to_runway = Column(Float)
    flight_path_intersection = Column(Boolean, default=False)
    flock_size = Column(Integer, default=1)
    
    # Response tracking
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String)
    acknowledged_at = Column(DateTime)
    action_taken = Column(String)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    ai_analysis = Column(Text, nullable=True)  # or String if you prefer
    
    # Location type
    location_type = Column(String, default="airport")
    
    # Relationships
    detection = relationship("BirdDetection", back_populates="alerts")
    species = relationship("BirdSpecies", back_populates="alerts")

class AudioSession(Base):
    __tablename__ = "audio_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    
    # Audio configuration
    sample_rate = Column(Integer, default=44100)
    channels = Column(Integer, default=16)
    bit_depth = Column(Integer, default=16)
    
    # Session statistics
    total_detections = Column(Integer, default=0)
    total_alerts = Column(Integer, default=0)
    avg_confidence = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # System performance
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    
    # Detection metrics
    detections_per_minute = Column(Float)
    false_positive_rate = Column(Float)
    system_uptime = Column(Float)
    
    # Audio system
    audio_level = Column(Float)
    microphone_status = Column(String)
    
    # Network
    connected_airports = Column(Integer)
    network_latency = Column(Float)

# NEW TABLES - Enhanced functionality

class Runway(Base):
    __tablename__ = "runways"
    
    id = Column(Integer, primary_key=True, index=True)
    runway_name = Column(String, unique=True, index=True)  # e.g., "09L/27R"
    airport_code = Column(String, index=True)  # e.g., "LAX"
    
    # Physical characteristics
    length = Column(Float)  # meters
    width = Column(Float)  # meters
    orientation = Column(Integer)  # degrees (0-360)
    
    # Operational status
    is_active = Column(Boolean, default=True)
    operational_hours = Column(String)  # JSON: {"start": "06:00", "end": "23:00"}
    
    # Risk zones around runway
    approach_zone_length = Column(Float, default=3000)  # meters
    departure_zone_length = Column(Float, default=1500)  # meters
    side_clearance = Column(Float, default=150)  # meters
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    risk_assessments = relationship("RunwayRiskAssessment", back_populates="runway")
    flight_schedules = relationship("FlightSchedule", back_populates="runway")

class RunwayRiskAssessment(Base):
    __tablename__ = "runway_risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    runway_id = Column(Integer, ForeignKey("runways.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Risk metrics
    overall_risk_score = Column(Float)  # 0-100
    bird_activity_risk = Column(Float)  # 0-100
    weather_risk = Column(Float)  # 0-100
    seasonal_risk = Column(Float)  # 0-100
    traffic_density_risk = Column(Float)  # 0-100
    
    # Current conditions
    active_bird_count = Column(Integer, default=0)
    high_risk_species_present = Column(Boolean, default=False)
    weather_conditions = Column(String)  # JSON weather data
    
    # Recommendations
    risk_level = Column(String)  # LOW, MODERATE, HIGH, CRITICAL
    recommended_action = Column(String)  # NORMAL, MONITOR, CAUTION, DELAY
    
    # Validity
    valid_until = Column(DateTime)
    
    # Relationships
    runway = relationship("Runway", back_populates="risk_assessments")

class WeatherData(Base):
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Basic weather
    temperature = Column(Float)  # Celsius
    humidity = Column(Float)  # percentage
    pressure = Column(Float)  # hPa
    
    # Wind data
    wind_speed = Column(Float)  # m/s
    wind_direction = Column(Integer)  # degrees
    wind_gust = Column(Float)  # m/s
    
    # Visibility and precipitation
    visibility = Column(Float)  # km
    precipitation = Column(Float)  # mm/h
    cloud_cover = Column(Float)  # percentage
    
    # Bird activity factors
    bird_favorability_score = Column(Float)  # 0-100
    migration_conditions = Column(String)  # POOR, FAIR, GOOD, EXCELLENT
    
    # Data source
    data_source = Column(String)  # API, MANUAL, SENSOR
    
    created_at = Column(DateTime, default=datetime.utcnow)

class FlightSchedule(Base):
    __tablename__ = "flight_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    runway_id = Column(Integer, ForeignKey("runways.id"))
    
    # Flight information
    flight_number = Column(String, index=True)
    airline = Column(String)
    aircraft_type = Column(String)
    
    # Schedule
    scheduled_time = Column(DateTime)
    actual_time = Column(DateTime)
    flight_type = Column(String)  # ARRIVAL, DEPARTURE
    
    # Status
    status = Column(String)  # SCHEDULED, DELAYED, CANCELLED, COMPLETED
    delay_reason = Column(String)
    bird_related_delay = Column(Boolean, default=False)
    
    # Risk assessment
    pre_flight_risk_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    runway = relationship("Runway", back_populates="flight_schedules")

class BirdStrikeIncident(Base):
    __tablename__ = "bird_strike_incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String, unique=True, index=True)
    
    # Basic incident information
    timestamp = Column(DateTime, default=datetime.utcnow)
    runway_id = Column(Integer, ForeignKey("runways.id"))
    flight_number = Column(String)
    aircraft_type = Column(String)
    
    # Strike details
    strike_location = Column(String)  # ENGINE, WINDSHIELD, WING, FUSELAGE
    bird_species_id = Column(Integer, ForeignKey("bird_species.id"))
    number_of_birds = Column(Integer, default=1)
    
    # Damage assessment
    damage_level = Column(String)  # NONE, MINOR, MODERATE, MAJOR, SUBSTANTIAL
    damage_cost = Column(Float)  # USD
    aircraft_damage_description = Column(Text)
    
    # Flight impact
    flight_phase = Column(String)  # TAXI, TAKEOFF, CLIMB, APPROACH, LANDING
    altitude = Column(Float)  # feet
    speed = Column(Float)  # knots
    
    # Response and outcome
    emergency_declared = Column(Boolean, default=False)
    return_to_airport = Column(Boolean, default=False)
    injuries = Column(Integer, default=0)
    fatalities = Column(Integer, default=0)
    
    # Investigation
    investigation_status = Column(String)  # OPEN, CLOSED, PENDING
    investigation_findings = Column(Text)
    
    # Prevention analysis
    could_have_been_prevented = Column(Boolean)
    prevention_recommendations = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class PredictiveModel(Base):
    __tablename__ = "predictive_models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, unique=True, index=True)
    model_type = Column(String)  # RISK_PREDICTION, SPECIES_DETECTION, BEHAVIOR_ANALYSIS
    
    # Model metadata
    version = Column(String)
    training_data_size = Column(Integer)
    accuracy_score = Column(Float)
    last_trained = Column(DateTime)
    
    # Model parameters
    parameters = Column(Text)  # JSON serialized parameters
    feature_importance = Column(Text)  # JSON serialized feature importance
    
    # Performance metrics
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    
    # Status
    is_active = Column(Boolean, default=True)
    deployment_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class RiskPrediction(Base):
    __tablename__ = "risk_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("predictive_models.id"))
    runway_id = Column(Integer, ForeignKey("runways.id"))
    
    # Prediction details
    prediction_timestamp = Column(DateTime, default=datetime.utcnow)
    forecast_timestamp = Column(DateTime)  # When the prediction is for
    
    # Risk scores
    predicted_risk_score = Column(Float)  # 0-100
    confidence_interval = Column(Float)  # 0-100
    
    # Contributing factors
    weather_contribution = Column(Float)
    seasonal_contribution = Column(Float)
    historical_contribution = Column(Float)
    bird_activity_contribution = Column(Float)
    
    # Prediction details
    prediction_horizon = Column(Integer)  # hours
    model_confidence = Column(Float)  # 0-100
    
    # Validation (if available)
    actual_risk_score = Column(Float)
    prediction_accuracy = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    username = Column(String)
    user_role = Column(String)  # OPERATOR, SUPERVISOR, ADMIN
    
    # Activity details
    activity_type = Column(String)  # LOGIN, ALERT_ACK, SYSTEM_CONFIG, REPORT_GENERATE
    activity_description = Column(Text)
    target_object = Column(String)  # What was acted upon
    
    # System interaction
    ip_address = Column(String)
    user_agent = Column(String)
    session_id = Column(String)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Result
    success = Column(Boolean, default=True)
    error_message = Column(String)

# NEW TABLES FOR BEHAVIOR ANALYTICS AND TRANSLATOR
class BirdPersonality(Base):
    __tablename__ = "bird_personalities"
    
    id = Column(Integer, primary_key=True, index=True)
    species_id = Column(Integer, ForeignKey("bird_species.id"))
    name = Column(String)  # e.g., "Alpha Robin #1"
    personality_type = Column(String)  # Assertive Leader, Community Coordinator
    territory = Column(String)  # Northwest Quadrant
    behavior_notes = Column(Text)
    social_rank = Column(String)  # Dominant, Facilitator
    stress_level = Column(String)  # Low, Medium, High
    learning_patterns = Column(Text)
    
    # Relationships
    species = relationship("BirdSpecies", back_populates="personalities")

class BirdTranslation(Base):
    __tablename__ = "bird_translations"
    
    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, ForeignKey("bird_detections.id"))
    original_call = Column(String)
    translation = Column(Text)
    emotion = Column(String)  # Confident, Focused, Excited
    context = Column(String)  # Territorial Defense, Hunting Alert
    confidence = Column(Float)
    
    # Relationships
    detection = relationship("BirdDetection", back_populates="translations")

class DailyPattern(Base):
    __tablename__ = "daily_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    time_of_day = Column(String)  # e.g., "06:00"
    activity_level = Column(Integer)  # 0-100%
    species_count = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

class MigrationData(Base):
    __tablename__ = "migration_data"
    
    id = Column(Integer, primary_key=True, index=True)
    species_id = Column(Integer, ForeignKey("bird_species.id"))
    peak_period = Column(String)  # March 15-30
    status = Column(String)  # Active, Starting, Upcoming
    bird_count = Column(Integer)
    forecast_date = Column(DateTime)
    
    # Relationships
    species = relationship("BirdSpecies", back_populates="migration_data")

class BehaviorInsight(Base):
    __tablename__ = "behavior_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    impact_level = Column(String)  # High, Medium, Positive
    recommendation = Column(Text)
    generated_at = Column(DateTime, default=datetime.utcnow)

# NEW TABLE FOR PREDATOR SOUND EVENTS
class PredatorSoundEvent(Base):
    __tablename__ = "predator_sound_events"
    id = Column(Integer, primary_key=True, index=True)
    sound_type = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    effectiveness = Column(Float, nullable=True)
    location_type = Column(String, default="airport")
    target_species = Column(String)  # Add this field
    target_species_scientific = Column(String)  # Add this field

# Enhanced Image Service
class BirdImageService:
    def __init__(self, unsplash_access_key=None):
        self.unsplash_key = 'Sso8qINdbjidG4RLXhNcJN1aGTefBQjnuvTSq6vKu1c'
        self.base_url = "https://api.unsplash.com/search/photos"
        
    def fetch_bird_image(self, bird_name, scientific_name=None):
        """Fetch bird image from Unsplash API"""
        if not self.unsplash_key:
            print("⚠️  No Unsplash API key provided. Using default images.")
            return self._get_default_image(bird_name)
        
        try:
            search_query = f"{bird_name} bird"
            params = {
                'query': search_query,
                'per_page': 1,
                'orientation': 'landscape'
            }
            
            headers = {
                'Authorization': f'Client-ID {self.unsplash_key}'
            }
            
            response = requests.get(self.base_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['results']:
                    image_info = data['results'][0]
                    image_url = image_info['urls']['regular']
                    
                    img_response = requests.get(image_url, timeout=10)
                    if img_response.status_code == 200:
                        image_data = base64.b64encode(img_response.content).decode('utf-8')
                        
                        return {
                            'image_url': image_url,
                            'image_data': image_data,
                            'image_source': 'unsplash',
                            'image_fetched_at': datetime.utcnow()
                        }
            
            return self._get_default_image(bird_name)
            
        except Exception as e:
            print(f"❌ Error fetching image for {bird_name}: {str(e)}")
            return self._get_default_image(bird_name)
    
    def _get_default_image(self, bird_name):
        """Generate default bird image based on category"""
        img = Image.new('RGB', (300, 200), color='lightblue')
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {
            'image_url': None,
            'image_data': image_data,
            'image_source': 'default',
            'image_fetched_at': datetime.utcnow()
        }

# Database initialization functions
def init_database():
    """Initialize database with tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def seed_runways():
    """Seed database with sample runway data"""
    session = SessionLocal()
    
    runway_data = [
        {
            "runway_name": "09L/27R",
            "airport_code": "LAX",
            "length": 3685,
            "width": 45,
            "orientation": 90,
            "operational_hours": '{"start": "06:00", "end": "23:00"}'
        },
        {
            "runway_name": "09R/27L",
            "airport_code": "LAX",
            "length": 3685,
            "width": 45,
            "orientation": 90,
            "operational_hours": '{"start": "06:00", "end": "23:00"}'
        },
        {
            "runway_name": "04L/22R",
            "airport_code": "LAX",
            "length": 3382,
            "width": 45,
            "orientation": 40,
            "operational_hours": '{"start": "06:00", "end": "23:00"}'
        },
        {
            "runway_name": "04R/22L",
            "airport_code": "LAX",
            "length": 3382,
            "width": 45,
            "orientation": 40,
            "operational_hours": '{"start": "06:00", "end": "23:00"}'
        }
    ]
    
    for runway_info in runway_data:
        existing = session.query(Runway).filter_by(
            runway_name=runway_info["runway_name"]
        ).first()
        
        if not existing:
            runway = Runway(**runway_info)
            session.add(runway)
            print(f"✅ Added runway {runway_info['runway_name']}")
    
    session.commit()
    session.close()
    print("✅ Runway data seeded successfully")

def seed_bird_species():
    """Seed database with common bird species"""
    session = SessionLocal()
    image_service = BirdImageService()
    
    species_data = [
        {
            "scientific_name": "Turdus migratorius",
            "common_name": "American Robin",
            "risk_level": "LOW",
            "size_category": "SMALL",
            "typical_behavior": "Ground foraging, territorial calls",
            "migration_pattern": "Partial migrant"
        },
        {
            "scientific_name": "Buteo jamaicensis",
            "common_name": "Red-tailed Hawk",
            "risk_level": "HIGH",
            "size_category": "LARGE",
            "typical_behavior": "Soaring, hunting calls",
            "migration_pattern": "Resident"
        },
        {
            "scientific_name": "Passer domesticus",
            "common_name": "House Sparrow",
            "risk_level": "LOW",
            "size_category": "SMALL",
            "typical_behavior": "Social chirping, ground feeding",
            "migration_pattern": "Resident"
        },
        {
            "scientific_name": "Corvus splendens",
            "common_name": "House Crow",
            "risk_level": "HIGH",
            "size_category": "MEDIUM",
            "typical_behavior": "Intelligent, territorial, scavenging",
            "migration_pattern": "Resident"
        },
        {
            "scientific_name": "Larus argentatus",
            "common_name": "Herring Gull",
            "risk_level": "CRITICAL",
            "size_category": "LARGE",
            "typical_behavior": "Flocking, aggressive feeding",
            "migration_pattern": "Seasonal migrant"
        },
        {
            "scientific_name": "Hirundo rustica",
            "common_name": "Barn Swallow",
            "risk_level": "MEDIUM",
            "size_category": "SMALL",
            "typical_behavior": "Aerial feeding, social calls",
            "migration_pattern": "Long-distance migrant"
        },
        {
            "scientific_name": "Falco tinnunculus",
            "common_name": "Common Kestrel",
            "risk_level": "HIGH",
            "size_category": "MEDIUM",
            "typical_behavior": "Hovering, sharp calls",
            "migration_pattern": "Partial migrant"
        },
        {
            "scientific_name": "Sturnus vulgaris",
            "common_name": "European Starling",
            "risk_level": "HIGH",
            "size_category": "SMALL",
            "typical_behavior": "Flocking, mimicry",
            "migration_pattern": "Resident"
        }
    ]
    
    for species_info in species_data:
        existing = session.query(BirdSpecies).filter_by(
            scientific_name=species_info["scientific_name"]
        ).first()
        
        if not existing:
            print(f"🔍 Fetching image for {species_info['common_name']}...")
            image_data = image_service.fetch_bird_image(
                species_info['common_name'],
                species_info['scientific_name']
            )
            
            species_info.update(image_data)
            
            species = BirdSpecies(**species_info)
            session.add(species)
            print(f"✅ Added {species_info['common_name']} with image")
        else:
            if existing.image_data is None:
                print(f"🔍 Fetching image for existing species: {existing.common_name}")
                image_data = image_service.fetch_bird_image(
                    existing.common_name,
                    existing.scientific_name
                )
                
                existing.image_url = image_data['image_url']
                existing.image_data = image_data['image_data']
                existing.image_source = image_data['image_source']
                existing.image_fetched_at = image_data['image_fetched_at']
                print(f"✅ Updated {existing.common_name} with image")
    
    session.commit()
    session.close()
    print("✅ Bird species seeded successfully")

def seed_behavior_data():
    """Seed database with behavior analytics data"""
    session = SessionLocal()
    
    # Daily patterns
    daily_patterns = [
        {"time_of_day": "06:00", "activity_level": 85, "species_count": 12},
        {"time_of_day": "08:00", "activity_level": 95, "species_count": 15},
        {"time_of_day": "10:00", "activity_level": 70, "species_count": 10},
        {"time_of_day": "12:00", "activity_level": 45, "species_count": 8},
        {"time_of_day": "14:00", "activity_level": 60, "species_count": 9},
        {"time_of_day": "16:00", "activity_level": 80, "species_count": 13},
        {"time_of_day": "18:00", "activity_level": 90, "species_count": 14},
        {"time_of_day": "20:00", "activity_level": 30, "species_count": 6}
    ]
    
    for pattern in daily_patterns:
        existing = session.query(DailyPattern).filter_by(
            time_of_day=pattern["time_of_day"]
        ).first()
        
        if not existing:
            daily = DailyPattern(**pattern)
            session.add(daily)
    
    # Migration data
    migration_data = [
        {"species_id": 1, "peak_period": "March 15-30", "status": "Active", "bird_count": 156},
        {"species_id": 2, "peak_period": "April 1-15", "status": "Starting", "bird_count": 89},
        {"species_id": 6, "peak_period": "April 10-25", "status": "Upcoming", "bird_count": 23},
    ]
    
    for migration in migration_data:
        existing = session.query(MigrationData).filter_by(
            species_id=migration["species_id"],
            peak_period=migration["peak_period"]
        ).first()
        
        if not existing:
            mig = MigrationData(**migration)
            session.add(mig)
    
    # Behavior insights
    insights = [
        {
            "title": "Morning Territorial Behavior",
            "description": "Peak territorial calling occurs between 6-8 AM, primarily from resident species",
            "impact_level": "High",
            "recommendation": "Schedule maintenance activities to avoid peak territorial hours"
        },
        {
            "title": "Weather-Driven Feeding Patterns",
            "description": "Bird activity increases 40% on overcast days due to optimal foraging conditions",
            "impact_level": "Medium",
            "recommendation": "Increase monitoring on cloudy days"
        },
        {
            "title": "Human Adaptation Learning",
            "description": "Birds show 67% faster adaptation to new airport schedules compared to last year",
            "impact_level": "Positive",
            "recommendation": "Continue consistent deterrent timing"
        }
    ]
    
    for insight in insights:
        existing = session.query(BehaviorInsight).filter_by(
            title=insight["title"]
        ).first()
        
        if not existing:
            behavior = BehaviorInsight(**insight)
            session.add(behavior)
    
    session.commit()
    session.close()
    print("✅ Behavior analytics data seeded successfully")

def seed_translator_data():
    """Seed database with bird translator data"""
    session = SessionLocal()
    
    # Bird personalities
    personalities = [
        {
            "species_id": 1,
            "name": "Alpha Robin #1",
            "personality_type": "Assertive Leader",
            "territory": "Northwest Quadrant",
            "behavior_notes": "Highly territorial, consistent morning vocalist, protective of nesting area",
            "social_rank": "Dominant",
            "stress_level": "Low",
            "learning_patterns": "Adapts quickly to human schedules"
        },
        {
            "species_id": 3,
            "name": "Social Sparrow #3",
            "personality_type": "Community Coordinator",
            "territory": "Central Food Area",
            "behavior_notes": "Excellent communicator, mediates disputes, organizes group feeding",
            "social_rank": "Facilitator",
            "stress_level": "Medium",
            "learning_patterns": "Teaches flock about human behavior patterns"
        }
    ]
    
    for personality in personalities:
        existing = session.query(BirdPersonality).filter_by(
            name=personality["name"]
        ).first()
        
        if not existing:
            bird_personality = BirdPersonality(**personality)
            session.add(bird_personality)
    
    session.commit()
    session.close()
    print("✅ Bird translator data seeded successfully")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Enhanced Database Manager
class DatabaseManager:
    def __init__(self):
        self.session = SessionLocal()
        self.image_service = BirdImageService()
    
    def add_detection(self, detection_data):
        """Add new bird detection to database"""
        if 'location_type' not in detection_data:
            detection_data['location_type'] = 'airport'
        detection = BirdDetection(**detection_data)
        self.session.add(detection)
        self.session.commit()
        return detection
    
    def add_alert(self, alert_data):
        """Add new alert to database"""
        if 'location_type' not in alert_data:
            alert_data['location_type'] = 'airport'
        alert = BirdAlert(**alert_data)
        self.session.add(alert)
        self.session.commit()
        return alert
    
    def add_runway_risk_assessment(self, runway_id, risk_data):
        """Add runway risk assessment"""
        risk_assessment = RunwayRiskAssessment(
            runway_id=runway_id,
            **risk_data
        )
        self.session.add(risk_assessment)
        self.session.commit()
        return risk_assessment
    
    def add_weather_data(self, weather_data):
        """Add weather data"""
        weather = WeatherData(**weather_data)
        self.session.add(weather)
        self.session.commit()
        return weather
    
    def add_bird_strike_incident(self, incident_data):
        """Add bird strike incident"""
        incident = BirdStrikeIncident(**incident_data)
        self.session.add(incident)
        self.session.commit()
        return incident
    
    def add_predator_sound_event(self, event_data):
        """Add predator sound event"""
        if 'location_type' not in event_data:
            event_data['location_type'] = 'airport'
        event = PredatorSoundEvent(**event_data)
        self.session.add(event)
        self.session.commit()
        return event
    
    def get_runway_current_risk(self, runway_name):
        """Get current risk assessment for a runway"""
        runway = self.session.query(Runway).filter_by(runway_name=runway_name).first()
        if not runway:
            return None
        
        current_risk = self.session.query(RunwayRiskAssessment).filter_by(
            runway_id=runway.id
        ).order_by(RunwayRiskAssessment.timestamp.desc()).first()
        
        return current_risk
    
    def get_recent_detections(self, limit=10):
        """Get recent bird detections with species images"""
        detections = self.session.query(BirdDetection).join(BirdSpecies).order_by(
            BirdDetection.timestamp.desc()
        ).limit(limit).all()
        
        for detection in detections:
            if not detection.species.image_data:
                self._fetch_species_image(detection.species)
        
        return detections
    
    def get_active_alerts(self):
        """Get unresolved alerts"""
        return self.session.query(BirdAlert).filter_by(
            resolved=False
        ).order_by(BirdAlert.timestamp.desc()).all()
    
    def get_species_by_name(self, common_name):
        """Get species by common name"""
        species = self.session.query(BirdSpecies).filter_by(
            common_name=common_name
        ).first()
        
        if species is not None and species.image_data is None:
            self._fetch_species_image(species)
        
        return species
    
    def _fetch_species_image(self, species):
        """Fetch and save image for a species"""
        try:
            print(f"🔍 Fetching image for {species.common_name}...")
            image_data = self.image_service.fetch_bird_image(
                species.common_name,
                species.scientific_name
            )
            
            species.image_url = image_data['image_url']
            species.image_data = image_data['image_data']
            species.image_source = image_data['image_source']
            species.image_fetched_at = image_data['image_fetched_at']
            
            self.session.commit()
            print(f"✅ Image fetched for {species.common_name}")
            
        except Exception as e:
            print(f"❌ Failed to fetch image for {species.common_name}: {str(e)}")
    
    def get_detection_stats(self):
        """Get detection statistics"""
        from sqlalchemy import func
        
        total_detections = self.session.query(BirdDetection).count()
        total_alerts = self.session.query(BirdAlert).count()
        high_risk_alerts = self.session.query(BirdAlert).filter(
            BirdAlert.alert_level.in_(['HIGH', 'CRITICAL'])
        ).count()
        
        most_common = self.session.query(
            BirdSpecies.common_name,
            func.count(BirdDetection.id).label('count')
        ).join(BirdDetection).group_by(BirdSpecies.common_name).order_by(
            func.count(BirdDetection.id).desc()
        ).first()
        
        avg_confidence = self.session.query(
            func.avg(BirdDetection.confidence)
        ).scalar() or 0.0

        # Add species count
        species_count = self.session.query(func.count(func.distinct(BirdDetection.species_id))).scalar() or 0
        
        # Add active (unresolved) alerts
        active_alerts = self.session.query(BirdAlert).filter(
            BirdAlert.resolved == False
        ).count()
        
        return {
            'total_detections': total_detections,
            'total_alerts': total_alerts,
            'high_risk_alerts': high_risk_alerts,
            'most_common_species': most_common[0] if most_common else None,
            'average_confidence': avg_confidence,
            'species_count': species_count,
            'active_alerts': active_alerts
        }
    
    # New methods for behavior analytics
    def get_daily_patterns(self):
        """Get daily activity patterns"""
        return self.session.query(DailyPattern).order_by(
            DailyPattern.time_of_day.asc()
        ).all()
    
    def get_migration_data(self):
        """Get migration patterns"""
        return self.session.query(MigrationData).join(BirdSpecies).all()
    
    def get_behavior_insights(self, limit=3):
        """Get AI-generated behavior insights"""
        return self.session.query(BehaviorInsight).order_by(
            BehaviorInsight.generated_at.desc()
        ).limit(limit).all()
    
    # New methods for bird translator
    def add_translation(self, translation_data):
        """Add bird call translation"""
        translation = BirdTranslation(**translation_data)
        self.session.add(translation)
        self.session.commit()
        return translation
    
    def get_recent_translations(self, limit=5):
        """Get recent bird translations"""
        return self.session.query(BirdTranslation).join(BirdDetection).order_by(
            BirdTranslation.id.desc()
        ).limit(limit).all()
    
    def get_bird_personalities(self):
        """Get bird personality profiles"""
        return self.session.query(BirdPersonality).join(BirdSpecies).all()
    
    def get_effectiveness_by_environment(self, location_type):
        """Get effectiveness by environment"""
        events = self.session.query(PredatorSoundEvent).filter_by(location_type=location_type).all()
        effectiveness_values = [e.effectiveness for e in events if e.effectiveness is not None]
        if effectiveness_values:
            avg_effectiveness = sum(effectiveness_values) / len(effectiveness_values)
        else:
            avg_effectiveness = None
        return {
            'location_type': location_type,
            'average_effectiveness': avg_effectiveness,
            'event_count': len(effectiveness_values)
        }
    
    def close(self):
        self.session.close()

# Database setup script
if __name__ == "__main__":
    print("🚀 Initializing Enhanced Bird Strike Detection Database...")
    
    # Create database and tables
    init_database()
    
    # Seed with data
    seed_runways()
    seed_bird_species()
    seed_behavior_data()
    seed_translator_data()
    
    # Test database connection
    db_manager = DatabaseManager()
    stats = db_manager.get_detection_stats()
    print(f"📊 Database initialized with enhanced schema")
    print(f"Total detections: {stats['total_detections']}")
    print(f"Total alerts: {stats['total_alerts']}")
    print(f"High risk alerts: {stats['high_risk_alerts']}")
    
    # Test new tables
    daily_patterns = db_manager.get_daily_patterns()
    print(f"📅 Daily patterns: {len(daily_patterns)} records")
    
    personalities = db_manager.get_bird_personalities()
    print(f"🐦 Bird personalities: {len(personalities)} records")
    
    db_manager.close()
    
    print("✅ Enhanced database setup complete!")