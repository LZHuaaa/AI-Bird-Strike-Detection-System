#!/usr/bin/env python3
"""
Strategic Response System with Next Action Panel and Automated Predator Sound Playback
Integrates with the main bird strike warning system to provide intelligent operational responses
"""

import asyncio
import json
import logging
import os
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import requests
import pygame
import threading
from pathlib import Path

# For AI-powered decision making
import openai
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ActionType(Enum):
    MONITOR = "MONITOR"
    DELAY = "DELAY"
    REDIRECT = "REDIRECT"
    EVACUATE = "EVACUATE"
    SOUND_DETERRENT = "SOUND_DETERRENT"
    EMERGENCY_STOP = "EMERGENCY_STOP"

@dataclass
class StrategicAction:
    action_type: ActionType
    priority: int
    description: str
    estimated_duration: int  # minutes
    resources_required: List[str]
    success_probability: float
    risk_assessment: str
    automated: bool = False

@dataclass
class NextActionRecommendation:
    timestamp: str
    situation_analysis: str
    recommended_actions: List[StrategicAction]
    risk_factors: List[str]
    success_metrics: Dict[str, float]
    confidence_score: float
    reasoning: str

class PredatorSoundLibrary:
    """Manages predator sound effects for bird deterrence"""

    def __init__(self, sounds_directory: str = None):
        if sounds_directory is None:
            # Use absolute path to backend/predator_sounds
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sounds_directory = os.path.join(current_dir, "predator_sounds")
        
        self.sounds_directory = Path(sounds_directory)
        if not self.sounds_directory.exists():
            logger.error(f"Predator sounds directory not found: {sounds_directory}")
            raise FileNotFoundError(f"Directory not found: {sounds_directory}")

        # Initialize pygame mixer for audio playback
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            logger.info("✅ Pygame mixer initialized successfully")
            
            # Test if mixer is working
            mixer_info = pygame.mixer.get_init()
            logger.info(f"🔊 Mixer info: {mixer_info}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize pygame mixer: {e}")
            raise

        # Predator sound mappings for different bird species
        self.predator_mappings = {
            "corvids": ["hawk_screech", "eagle_cry", "falcon_call"],
            "passerines": ["cat_meow", "snake_hiss", "hawk_screech"],
            "raptors": ["owl_hoot", "hawk_screech"],
            "waterfowl": ["fox_bark", "coyote_howl", "hawk_screech"],
            "default": ["hawk_screech", "eagle_cry", "owl_hoot"]
        }

        # Load sounds from directory
        self.sound_cache = {}
        self.initialize_sound_library()

        # Reference to communication analyzer
        self.communication_analyzer = None

        self._playback_thread = None
        self._stop_playback_event = threading.Event()

    def set_communication_analyzer(self, analyzer):
        """Set reference to communication analyzer"""
        self.communication_analyzer = analyzer

    def initialize_sound_library(self):
        """Initialize the predator sound library from local files"""
        try:
            logger.info(f"🔊 Initializing sound library from: {self.sounds_directory}")
            
            if not self.sounds_directory.exists():
                logger.error(f"❌ Sounds directory does not exist: {self.sounds_directory}")
                return
                
            # Load all MP3 files from the sounds directory
            sound_files = list(self.sounds_directory.glob("*.mp3"))
            logger.info(f"🔊 Found {len(sound_files)} MP3 files")
            
            for sound_file in sound_files:
                sound_name = sound_file.stem  # Get filename without extension
                logger.info(f"🔊 Loading sound: {sound_name} from {sound_file}")
                
                try:
                    sound = pygame.mixer.Sound(str(sound_file))
                    self.sound_cache[sound_name] = sound
                    logger.info(f"✅ Successfully loaded sound: {sound_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to load sound {sound_name}: {e}")
            
            logger.info(f"🔊 Sound library initialized with {len(self.sound_cache)} sounds")
            logger.info(f"🔊 Available sounds: {list(self.sound_cache.keys())}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize sound library: {e}")

    def get_effective_predator_sound(self, bird_species: str, bird_behavior: str) -> str:
        """Select the most effective predator sound for the given bird species"""
        bird_category = "default"
        bird_species_lower = bird_species.lower()

        if any(corvid in bird_species_lower for corvid in ["crow", "raven", "magpie", "jay"]):
            bird_category = "corvids"
        elif any(passerine in bird_species_lower for passerine in ["sparrow", "finch", "warbler", "robin"]):
            bird_category = "passerines"
        elif any(raptor in bird_species_lower for raptor in ["hawk", "eagle", "falcon", "kestrel"]):
            bird_category = "raptors"
        elif any(waterfowl in bird_species_lower for waterfowl in ["duck", "goose", "swan", "gull"]):
            bird_category = "waterfowl"

        # Get available sounds that match our mappings
        mapped_sounds = self.predator_mappings.get(bird_category, self.predator_mappings["default"])
        available_sounds = [s for s in mapped_sounds if s in self.sound_cache]

        # If no mapped sounds are available, use any available sound
        if not available_sounds:
            available_sounds = list(self.sound_cache.keys())

        # Filter by behavior - more aggressive sounds for territorial behavior
        if "territorial" in bird_behavior.lower() or "aggressive" in bird_behavior.lower():
            aggressive_sounds = ["hawk_screech", "eagle_cry", "falcon_call"]
            aggressive_available = [s for s in available_sounds if s in aggressive_sounds]
            if aggressive_available:
                available_sounds = aggressive_available

        # Return a random effective sound
        return random.choice(available_sounds) if available_sounds else list(self.sound_cache.keys())[0]

    def play_predator_sound(self, sound_name: str, volume: float = 0.8, repeat: int = 1):
        """Play a predator sound in a continuous loop until stopped"""
        logger.info(f"🔊 Attempting to play sound: {sound_name}")
        logger.info(f"🔊 Available sounds in cache: {list(self.sound_cache.keys())}")
        logger.info(f"🔊 Sound exists in cache: {sound_name in self.sound_cache}")

        # Stop any currently playing sound first
        self.stop_predator_sound()

        if sound_name in self.sound_cache:
            sound = self.sound_cache[sound_name]
            logger.info(f"🔊 Sound object retrieved: {sound}")
            sound.set_volume(volume)

            def playback_loop():
                try:
                    # Estimate duration for status tracking
                    duration = sound.get_length()
                    if self.communication_analyzer:
                        self.communication_analyzer.update_predator_status(True, 9999)  # Arbitrary long duration
                    while not self._stop_playback_event.is_set():
                        logger.info(f"🔊 Playing sound loop")
                        sound.play()
                        time.sleep(duration)
                except Exception as e:
                    logger.error(f"❌ Error in playback loop for {sound_name}: {e}")
                finally:
                    if self.communication_analyzer:
                        self.communication_analyzer.update_predator_status(False)
                    logger.info(f"🔊 Playback loop for {sound_name} stopped")

            self._stop_playback_event.clear()
            self._playback_thread = threading.Thread(target=playback_loop, daemon=True)
            self._playback_thread.start()
            logger.info(f"✅ Started continuous playback for predator sound: {sound_name}")
            return True
        else:
            logger.warning(f"❌ Predator sound not found in cache: {sound_name}")
            logger.info(f"🔊 Available sounds: {list(self.sound_cache.keys())}")
            return False

    def stop_predator_sound(self):
        """Stop any currently playing predator sound"""
        logger.info("🛑 Stopping predator sound playback (if any)")
        self._stop_playback_event.set()
        if self._playback_thread and self._playback_thread.is_alive():
            self._playback_thread.join(timeout=2)
        self._playback_thread = None
        # Also stop all pygame sounds immediately
        try:
            pygame.mixer.stop()
        except Exception as e:
            logger.error(f"❌ Error stopping pygame mixer: {e}")
        if self.communication_analyzer:
            self.communication_analyzer.update_predator_status(False)

class AIDecisionEngine:
    """AI-powered decision making for strategic responses"""
    
    def __init__(self):
        # Initialize Hugging Face models for decision making
        self.setup_ai_models()
        
        # Historical decision data for learning
        self.decision_history = []
        self.success_rates = {}
        
    def setup_ai_models(self):
        """Initialize AI models for decision making"""
        try:
            # Use a lightweight classification model for threat assessment
            self.threat_classifier = pipeline(
                "text-classification",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                return_all_scores=True
            )
            
            # Use a general-purpose model for strategic analysis
            self.strategy_analyzer = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-medium",
                max_length=100,
                temperature=0.7
            )
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
            # Fallback to rule-based system
            self.threat_classifier = None
            self.strategy_analyzer = None
    
    def analyze_situation(self, bird_data: Dict) -> Dict:
        """Analyze the current situation using AI"""
        
        # Prepare situation description
        situation_text = f"""
        Bird species: {bird_data.get('species', {}).get('common', 'Unknown')}
        Alert level: {bird_data.get('alert_level', 'UNKNOWN')}
        Risk score: {bird_data.get('risk_score', 0)}
        Communication pattern: {bird_data.get('communication_analysis', {}).get('call_type', 'unknown')}
        Behavioral intent: {bird_data.get('behavioral_prediction', {}).get('primary_intent', 'unknown')}
        Flock behavior: {bird_data.get('communication_analysis', {}).get('flock_communication', False)}
        """
        
        analysis = {
            "threat_level": self._assess_threat_level(bird_data),
            "urgency_score": self._calculate_urgency_score(bird_data),
            "complexity_factors": self._identify_complexity_factors(bird_data),
            "environmental_factors": self._assess_environmental_factors(bird_data),
            "historical_context": self._get_historical_context(bird_data)
        }
        
        return analysis
    
    def _assess_threat_level(self, bird_data: Dict) -> ThreatLevel:
        """Assess the threat level based on bird data"""
        risk_score = bird_data.get('risk_score', 0)
        alert_level = bird_data.get('alert_level', 'LOW')
        flock_behavior = bird_data.get('communication_analysis', {}).get('flock_communication', False)
        
        if risk_score > 0.8 or alert_level == 'CRITICAL':
            return ThreatLevel.CRITICAL
        elif risk_score > 0.6 or alert_level == 'HIGH' or flock_behavior:
            return ThreatLevel.HIGH
        elif risk_score > 0.4 or alert_level == 'MEDIUM':
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def _calculate_urgency_score(self, bird_data: Dict) -> float:
        """Calculate urgency score (0-1)"""
        base_score = bird_data.get('risk_score', 0)
        
        # Urgency modifiers
        urgency_level = bird_data.get('communication_analysis', {}).get('urgency_level', 'low')
        if urgency_level == 'high':
            base_score += 0.2
        elif urgency_level == 'medium':
            base_score += 0.1
        
        # Flock behavior increases urgency
        if bird_data.get('communication_analysis', {}).get('flock_communication', False):
            base_score += 0.15
        
        # Territorial behavior increases urgency
        if bird_data.get('communication_analysis', {}).get('territorial_behavior', False):
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _identify_complexity_factors(self, bird_data: Dict) -> List[str]:
        """Identify factors that complicate the situation"""
        factors = []
        
        if bird_data.get('communication_analysis', {}).get('flock_communication', False):
            factors.append("Flock coordination detected")
        
        if bird_data.get('communication_analysis', {}).get('territorial_behavior', False):
            factors.append("Territorial behavior - birds may return")
        
        if bird_data.get('communication_analysis', {}).get('alarm_signal', False):
            factors.append("Alarm signals - potential for mass movement")
        
        behavioral_intent = bird_data.get('behavioral_prediction', {}).get('primary_intent', '')
        if behavioral_intent == 'territory_defense':
            factors.append("Territory defense - persistent threat")
        elif behavioral_intent == 'flock_gathering':
            factors.append("Flock gathering - increasing numbers expected")
        
        return factors
    
    def _assess_environmental_factors(self, bird_data: Dict) -> Dict:
        """Assess environmental factors affecting the situation"""
        # This would integrate with weather data, time of day, etc.
        current_time = datetime.now()
        
        factors = {
            "time_of_day": "dawn" if 5 <= current_time.hour <= 7 else 
                           "dusk" if 17 <= current_time.hour <= 19 else "day",
            "migration_season": self._is_migration_season(current_time),
            "weather_impact": "clear",  # Would integrate with weather API
            "visibility": "good"  # Would integrate with visibility sensors
        }
        
        return factors
    
    def _is_migration_season(self, current_time: datetime) -> bool:
        """Check if it's migration season"""
        month = current_time.month
        return month in [3, 4, 5, 9, 10, 11]  # Spring and fall migration
    
    def _get_historical_context(self, bird_data: Dict) -> Dict:
        """Get historical context for similar situations"""
        species = bird_data.get('species', {}).get('scientific', 'unknown')
        
        # Look for similar past incidents
        similar_incidents = [
            incident for incident in self.decision_history
            if incident.get('species') == species
        ]
        
        if similar_incidents:
            avg_success_rate = sum(
                incident.get('success_rate', 0) for incident in similar_incidents
            ) / len(similar_incidents)
            
            common_actions = {}
            for incident in similar_incidents:
                action = incident.get('action_taken', 'unknown')
                common_actions[action] = common_actions.get(action, 0) + 1
            
            most_common_action = max(common_actions, key=common_actions.get) if common_actions else None
            
            return {
                "similar_incidents": len(similar_incidents),
                "average_success_rate": avg_success_rate,
                "most_successful_action": most_common_action,
                "recurrence_pattern": self._analyze_recurrence_pattern(similar_incidents)
            }
        
        return {
            "similar_incidents": 0,
            "average_success_rate": 0,
            "most_successful_action": None,
            "recurrence_pattern": "insufficient_data"
        }
    
    def _analyze_recurrence_pattern(self, incidents: List[Dict]) -> str:
        """Analyze if there's a recurrence pattern"""
        if len(incidents) < 2:
            return "insufficient_data"
        
        # Check for time-based patterns
        timestamps = [datetime.fromisoformat(i['timestamp']) for i in incidents if 'timestamp' in i]
        if len(timestamps) >= 2:
            # Check if incidents occur at similar times
            hours = [t.hour for t in timestamps]
            if len(set(hours)) <= 2:
                return "time_pattern_detected"
        
        return "no_clear_pattern"

class StrategicResponseSystem:
    """Main strategic response system"""
    
    def __init__(self):
        self.ai_engine = AIDecisionEngine()
        self.predator_sounds = PredatorSoundLibrary()
        self.active_strategies = {}
        self.response_history = []
        
        # Strategy templates
        self.strategy_templates = {
            ThreatLevel.LOW: self._generate_low_threat_strategies,
            ThreatLevel.MEDIUM: self._generate_medium_threat_strategies,
            ThreatLevel.HIGH: self._generate_high_threat_strategies,
            ThreatLevel.CRITICAL: self._generate_critical_threat_strategies
        }
    
    def generate_next_action_recommendation(self, bird_data: Dict) -> NextActionRecommendation:
        """Generate next action recommendation based on current situation"""
        
        # Analyze the situation
        situation_analysis = self.ai_engine.analyze_situation(bird_data)
        threat_level = situation_analysis["threat_level"]
        
        # Generate appropriate strategies
        strategies = self.strategy_templates[threat_level](bird_data, situation_analysis)
        
        # Calculate overall confidence
        confidence_score = self._calculate_confidence_score(situation_analysis, strategies)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(bird_data, situation_analysis, strategies)
        
        recommendation = NextActionRecommendation(
            timestamp=datetime.now().isoformat(),
            situation_analysis=self._format_situation_analysis(situation_analysis),
            recommended_actions=strategies,
            risk_factors=situation_analysis["complexity_factors"],
            success_metrics=self._calculate_success_metrics(strategies),
            confidence_score=confidence_score,
            reasoning=reasoning
        )
        
        return recommendation
    
    def _generate_low_threat_strategies(self, bird_data: Dict, analysis: Dict) -> List[StrategicAction]:
        """Generate strategies for low threat situations"""
        return [
            StrategicAction(
                action_type=ActionType.MONITOR,
                priority=1,
                description="Continue passive monitoring with standard sensors",
                estimated_duration=15,
                resources_required=["audio_sensors", "visual_monitoring"],
                success_probability=0.9,
                risk_assessment="Minimal risk - routine monitoring sufficient",
                automated=True
            ),
            StrategicAction(
                action_type=ActionType.SOUND_DETERRENT,
                priority=2,
                description="Gentle sound deterrent if bird approaches critical zones",
                estimated_duration=2,
                resources_required=["speaker_system"],
                success_probability=0.7,
                risk_assessment="Low risk - gentle deterrent should be sufficient",
                automated=True
            )
        ]
    
    def _generate_medium_threat_strategies(self, bird_data: Dict, analysis: Dict) -> List[StrategicAction]:
        """Generate strategies for medium threat situations"""
        species = bird_data.get('species', {}).get('common', 'Unknown')
        behavior = bird_data.get('behavioral_prediction', {}).get('primary_intent', 'unknown')
        
        strategies = [
            StrategicAction(
                action_type=ActionType.SOUND_DETERRENT,
                priority=1,
                description=f"Deploy predator sound deterrent optimized for {species}",
                estimated_duration=5,
                resources_required=["speaker_system", "predator_sounds"],
                success_probability=0.8,
                risk_assessment="Medium risk - sound deterrent should be effective",
                automated=True
            ),
            StrategicAction(
                action_type=ActionType.MONITOR,
                priority=2,
                description="Enhanced monitoring with increased sensor sensitivity",
                estimated_duration=10,
                resources_required=["audio_sensors", "visual_monitoring", "radar"],
                success_probability=0.85,
                risk_assessment="Essential for tracking bird response to deterrent",
                automated=True
            )
        ]
        
        # Add delay if flock behavior detected
        if bird_data.get('communication_analysis', {}).get('flock_communication', False):
            strategies.append(
                StrategicAction(
                    action_type=ActionType.DELAY,
                    priority=3,
                    description="Consider brief operational delay if deterrent ineffective",
                    estimated_duration=3,
                    resources_required=["air_traffic_control"],
                    success_probability=0.95,
                    risk_assessment="Precautionary delay to prevent flock collision",
                    automated=False
                )
            )
        
        return strategies
    
    def _generate_high_threat_strategies(self, bird_data: Dict, analysis: Dict) -> List[StrategicAction]:
        """Generate strategies for high threat situations"""
        species = bird_data.get('species', {}).get('common', 'Unknown')
        
        return [
            StrategicAction(
                action_type=ActionType.SOUND_DETERRENT,
                priority=1,
                description=f"Immediate intensive predator sound deployment for {species}",
                estimated_duration=3,
                resources_required=["speaker_system", "predator_sounds"],
                success_probability=0.75,
                risk_assessment="High urgency - immediate deterrent required",
                automated=True
            ),
            StrategicAction(
                action_type=ActionType.DELAY,
                priority=2,
                description="Implement operational delay until threat clears",
                estimated_duration=10,
                resources_required=["air_traffic_control", "operations_team"],
                success_probability=0.9,
                risk_assessment="Necessary precaution for high-risk scenario",
                automated=False
            ),
            StrategicAction(
                action_type=ActionType.REDIRECT,
                priority=3,
                description="Prepare alternative routing if delay extends",
                estimated_duration=15,
                resources_required=["air_traffic_control", "flight_planning"],
                success_probability=0.8,
                risk_assessment="Contingency plan for extended bird presence",
                automated=False
            )
        ]
    
    def _generate_critical_threat_strategies(self, bird_data: Dict, analysis: Dict) -> List[StrategicAction]:
        """Generate strategies for critical threat situations"""
        return [
            StrategicAction(
                action_type=ActionType.EMERGENCY_STOP,
                priority=1,
                description="Immediate emergency stop of all runway operations",
                estimated_duration=1,
                resources_required=["emergency_protocols", "all_personnel"],
                success_probability=0.99,
                risk_assessment="Critical - immediate action required",
                automated=True
            ),
            StrategicAction(
                action_type=ActionType.SOUND_DETERRENT,
                priority=2,
                description="Maximum intensity predator sound deployment",
                estimated_duration=5,
                resources_required=["speaker_system", "predator_sounds"],
                success_probability=0.7,
                risk_assessment="Emergency deterrent - all available resources",
                automated=True
            ),
            StrategicAction(
                action_type=ActionType.EVACUATE,
                priority=3,
                description="Evacuate aircraft from immediate danger zone",
                estimated_duration=20,
                resources_required=["ground_crew", "emergency_vehicles"],
                success_probability=0.95,
                risk_assessment="Essential for preventing catastrophic collision",
                automated=False
            )
        ]
    
    def execute_automated_response(self, bird_data: Dict, recommendation: NextActionRecommendation):
        """Execute automated responses from the recommendation"""
        
        for action in recommendation.recommended_actions:
            if action.automated:
                # Skip sound deterrent actions - these should be manually triggered
                if action.action_type == ActionType.SOUND_DETERRENT:
                    continue
                    
                if action.action_type == ActionType.MONITOR:
                    self._execute_enhanced_monitoring(action)
                elif action.action_type == ActionType.EMERGENCY_STOP:
                    self._execute_emergency_stop(action)
                
                # Log the action
                self._log_action_execution(action, bird_data)
    
    def _execute_sound_deterrent(self, bird_data: Dict, action: StrategicAction):
        """Execute sound deterrent strategy"""
        species = bird_data.get('species', {}).get('common', 'Unknown')
        behavior = bird_data.get('behavioral_prediction', {}).get('primary_intent', 'unknown')
        
        # Select appropriate predator sound
        predator_sound = self.predator_sounds.get_effective_predator_sound(species, behavior)
        
        # Determine intensity based on threat level
        threat_level = bird_data.get('alert_level', 'LOW')
        repeat_count = 3 if threat_level == 'CRITICAL' else 2 if threat_level == 'HIGH' else 1
        volume = 0.9 if threat_level in ['CRITICAL', 'HIGH'] else 0.7
        
        # Execute sound playback
        success = self.predator_sounds.play_predator_sound(
            predator_sound, 
            volume=volume, 
            repeat=repeat_count
        )
        
        if success:
            logger.info(f"Sound deterrent executed: {predator_sound} for {species}")
        else:
            logger.error(f"Failed to execute sound deterrent for {species}")
    
    def _execute_enhanced_monitoring(self, action: StrategicAction):
        """Execute enhanced monitoring"""
        logger.info(f"Enhanced monitoring activated: {action.description}")
        # This would integrate with your existing monitoring systems
        
    def _execute_emergency_stop(self, action: StrategicAction):
        """Execute emergency stop"""
        logger.critical(f"EMERGENCY STOP ACTIVATED: {action.description}")
        # This would trigger emergency protocols
    
    def _log_action_execution(self, action: StrategicAction, bird_data: Dict):
        """Log action execution for learning"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action.action_type.value,
            "species": bird_data.get('species', {}).get('scientific', 'unknown'),
            "threat_level": bird_data.get('alert_level', 'UNKNOWN'),
            "success_probability": action.success_probability,
            "automated": action.automated
        }
        
        self.response_history.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.response_history) > 1000:
            self.response_history = self.response_history[-1000:]
    
    def _calculate_confidence_score(self, analysis: Dict, strategies: List[StrategicAction]) -> float:
        """Calculate confidence score for the recommendation"""
        base_confidence = 0.8
        
        # Reduce confidence for complex situations
        complexity_factors = len(analysis["complexity_factors"])
        confidence_reduction = min(complexity_factors * 0.1, 0.3)
        
        # Increase confidence if we have historical data
        historical_context = analysis["historical_context"]
        if historical_context["similar_incidents"] > 5:
            base_confidence += 0.1
        
        # Factor in strategy success probabilities
        avg_strategy_success = sum(s.success_probability for s in strategies) / len(strategies)
        combined_confidence = (base_confidence + avg_strategy_success) / 2
        
        return max(0.0, min(1.0, combined_confidence - confidence_reduction))
    
    def _generate_reasoning(self, bird_data: Dict, analysis: Dict, strategies: List[StrategicAction]) -> str:
        """Generate reasoning for the recommendation"""
        threat_level = analysis["threat_level"].value
        species = bird_data.get('species', {}).get('common', 'Unknown')
        urgency = analysis["urgency_score"]
        
        reasoning = f"Based on {species} detection with {threat_level} threat level "
        reasoning += f"and urgency score of {urgency:.2f}, "
        
        if analysis["complexity_factors"]:
            reasoning += f"complicated by: {', '.join(analysis['complexity_factors'][:2])}. "
        
        reasoning += f"Recommended {len(strategies)} strategic actions prioritizing "
        reasoning += f"{strategies[0].action_type.value.lower()} with "
        reasoning += f"{strategies[0].success_probability:.0%} success probability."
        
        return reasoning
    
    def _format_situation_analysis(self, analysis: Dict) -> str:
        """Format situation analysis for display"""
        return f"""
        Threat Level: {analysis['threat_level'].value}
        Urgency Score: {analysis['urgency_score']:.2f}
        Complexity Factors: {len(analysis['complexity_factors'])}
        Environmental Context: {analysis['environmental_factors']['time_of_day']}
        Historical Data: {analysis['historical_context']['similar_incidents']} similar incidents
        """
    
    def _calculate_success_metrics(self, strategies: List[StrategicAction]) -> Dict[str, float]:
        """Calculate success metrics for strategies"""
        return {
            "overall_success_probability": sum(s.success_probability for s in strategies) / len(strategies),
            "automation_coverage": sum(1 for s in strategies if s.automated) / len(strategies),
            "resource_efficiency": 1.0 - (sum(len(s.resources_required) for s in strategies) / (len(strategies) * 10)),
            "time_efficiency": max(0, 1.0 - (sum(s.estimated_duration for s in strategies) / 60))
        }
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            "ai_engine_status": "active" if self.ai_engine.threat_classifier else "fallback_mode",
            "predator_sounds_loaded": len(self.predator_sounds.sound_cache),
            "active_strategies": len(self.active_strategies),
            "response_history_entries": len(self.response_history),
            "system_timestamp": datetime.now().isoformat()
        }

# Integration class for the main system
class NextActionPanel:
    """Panel for displaying and managing next actions"""
    
    def __init__(self, strategic_system: StrategicResponseSystem):
        self.strategic_system = strategic_system
        self.current_recommendation = None
        self.action_callbacks = {}
    
    def update_recommendation(self, bird_data: Dict) -> NextActionRecommendation:
        """Update the next action recommendation"""
        self.current_recommendation = self.strategic_system.generate_next_action_recommendation(bird_data)
        
        # Execute automated responses
        self.strategic_system.execute_automated_response(bird_data, self.current_recommendation)
        
        return self.current_recommendation
    
    def get_current_recommendation(self) -> Optional[NextActionRecommendation]:
        """Get the current recommendation"""
        return self.current_recommendation
    
    def execute_manual_action(self, action_id: int) -> bool:
        """Execute a manual action from the recommendation"""
        if not self.current_recommendation:
            return False
        
        if 0 <= action_id < len(self.current_recommendation.recommended_actions):
            action = self.current_recommendation.recommended_actions[action_id]
            
            if not action.automated:
                logger.info(f"Manual action executed: {action.description}")
                # Here you would implement the actual action execution
                return True
        
        return False
    
    def to_dict(self) -> Dict:
        """Convert current state to dictionary for API responses"""
        if not self.current_recommendation:
            return {"status": "no_recommendation"}
        return asdict(self.current_recommendation)