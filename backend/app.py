#!/usr/bin/env python3
"""
Enhanced Bird Strike Warning API with AI Communication Analysis
Integrates multiple AI models for comprehensive bird behavior analysis
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import statistics
from pydantic import BaseModel

import librosa
import numpy as np
import json
import asyncio
import threading
import uvicorn
import random
from pydantic import BaseModel
import logging
import os


# Import enhanced detection system and DB manager
from bird_communication_system import AdvancedBirdCommunicationAnalyzer
from db import get_db,DatabaseManager, BirdImageService, BirdAlert, BirdSpecies, PredatorSoundEvent, RunwayRiskAssessment, WeatherData, BirdDetection, RiskPrediction, Runway
from utils.gemini_utils import get_call_interpretation, get_bird_encyclopedia
from services.strategic_service import strategic_service
from services.weather_service import WeatherService
from services.alert_templates import get_response_template
from fastapi.responses import FileResponse, JSONResponse


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enhanced Bird Strike Warning API",
    description="AI-powered bird communication analysis and strike prevention",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API responses
class CommunicationPattern(BaseModel):
    call_type: str
    emotional_state: str
    behavioral_context: str
    urgency_level: str
    flock_communication: bool
    territorial_behavior: bool
    alarm_signal: bool

class BehavioralPrediction(BaseModel):
    primary_intent: str
    confidence: float
    all_scores: Dict[str, float]

class AIInsights(BaseModel):
    call_interpretation: List[str]
    threat_assessment: List[str]
    recommended_monitoring: List[str]

class EnhancedAlert(BaseModel):
    id: Optional[int] = None
    timestamp: str
    species: Dict[str, str]
    confidence: float
    risk_score: float
    alert_level: str
    recommended_action: str
    communication_analysis: CommunicationPattern
    behavioral_prediction: BehavioralPrediction
    ai_insights: AIInsights
    acknowledged: bool = False
    resolved: bool = False
    strategic_recommendation: Optional[Dict] = None  # NEW: Strategic response

# Enhanced Connection Manager
class EnhancedConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_stats = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_stats[websocket] = {
            'connected_at': datetime.now(),
            'messages_sent': 0
        }
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.connection_stats.pop(websocket, None)
            logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
                self.connection_stats[connection]['messages_sent'] += 1
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

    async def send_to_connection(self, websocket: WebSocket, message: str):
        try:
            await websocket.send_text(message)
            self.connection_stats[websocket]['messages_sent'] += 1
        except Exception as e:
            logger.error(f"Error sending message to specific WebSocket: {e}")
            self.disconnect(websocket)

# Initialize components
manager = EnhancedConnectionManager()
db_manager = DatabaseManager()
warning_system = None
communication_analyzer = None

# Communication history storage
communication_history = []
behavioral_patterns = {}

def enhanced_websocket_alert_handler(alert: Dict):
    """Enhanced alert handler with AI communication analysis"""
    try:
        species = db_manager.get_species_by_name(alert['species']['common'])
        image_service = BirdImageService()

        if not species:
            # Auto-create new species with enhanced data
            image_data = image_service.fetch_bird_image(
                alert['species']['common'],
                alert['species']['scientific']
            )
            new_species = BirdSpecies(
                scientific_name=alert['species']['scientific'],
                common_name=alert['species']['common'],
                risk_level=alert['alert_level'],
                size_category='UNKNOWN',
                typical_behavior=alert['behavioral_prediction']['primary_intent'],
                migration_pattern='',
                image_url=image_data['image_url'],
                image_data=image_data['image_data'],
                image_source=image_data['image_source'],
                image_fetched_at=image_data['image_fetched_at']
            )
            db_manager.session.add(new_species)
            db_manager.session.commit()
            species = new_species
        
        elif not getattr(species, 'image_data', None):
            # Update existing species with image data
            image_data = image_service.fetch_bird_image(
                species.common_name,
                species.scientific_name
            )
            species.image_url = image_data['image_url']
            species.image_data = image_data['image_data']
            species.image_source = image_data['image_source']
            species.image_fetched_at = image_data['image_fetched_at']
            db_manager.session.commit()

        # Always attach image_data to alert
        alert['image_data'] = getattr(species, 'image_data', None)

        # --- NEW: Always save a detection before saving an alert ---
        audio_segment_filename = None
        if 'audio_segment' in alert and alert['audio_segment'] and 'filename' in alert['audio_segment']:
            audio_segment_filename = alert['audio_segment']['filename']
        detection_data = {
            'species_id': species.id,
            'timestamp': datetime.fromisoformat(alert['timestamp']),
            'confidence': alert.get('confidence'),
            'call_type': alert.get('communication_analysis', {}).get('call_type'),
            'emotional_state': alert.get('communication_analysis', {}).get('emotional_state'),
            'behavioral_pattern': alert.get('behavioral_prediction', {}).get('primary_intent'),
            # Optionals (None if not present):
            'duration': None,
            'frequency_range': None,
            'amplitude': None,
            'location_x': None,
            'location_y': None,
            'distance_from_runway': None,
            'direction': None,
            'weather_conditions': None,
            'time_of_day': None,
            'season': None,
            'group_behavior': alert.get('communication_analysis', {}).get('flock_communication'),
            'audio_segment_filename': audio_segment_filename
        }
        detection = db_manager.add_detection(detection_data)
        # --- END NEW ---
        
        # Process strategic response
        strategic_response = None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            strategic_response = loop.run_until_complete(
                strategic_service.process_bird_alert(alert)
            )
            loop.close()
            
            if strategic_response:
                alert['strategic_recommendation'] = strategic_response.get('strategic_recommendation')
                logger.info(f"Strategic response generated for {alert['species']['common']}")
        except Exception as e:
            logger.error(f"Error generating strategic response: {e}")

        # Enhanced database storage with AI insights and strategic response
        ai_analysis_data = {
            "communication_analysis": alert['communication_analysis'],
            "behavioral_prediction": alert['behavioral_prediction'],
            "ai_insights": alert['ai_insights']
        }
        
        # Add strategic response to stored data
        if strategic_response:
            ai_analysis_data["strategic_response"] = strategic_response
        
        # Enhanced database storage with AI insights
        db_alert = db_manager.add_alert({
            "detection_id": detection.id,  # Link to detection
            "species_id": species.id,
            "timestamp": datetime.fromisoformat(alert['timestamp']),
            "alert_level": alert['alert_level'],
            "risk_score": alert['risk_score'],
            "recommended_action": alert['recommended_action'],
            "proximity_to_runway": 0,
            "flight_path_intersection": False,
            "flock_size": 1,
            "acknowledged": False,
            "resolved": False,
            # Store AI analysis as JSON
            "ai_analysis": json.dumps({
                "communication_analysis": alert['communication_analysis'],
                "behavioral_prediction": alert['behavioral_prediction'],
                "ai_insights": alert['ai_insights']
            })
        })

        # Store communication patterns for analysis
        communication_history.append({
            'timestamp': alert['timestamp'],
            'species': alert['species']['scientific'],
            'patterns': alert['communication_analysis'],
            'behavior': alert['behavioral_prediction'],
            'strategic_response': strategic_response
        })

        # Keep only last 1000 entries
        if len(communication_history) > 1000:
            communication_history[:] = communication_history[-1000:]

        # Update behavioral patterns database
        species_key = alert['species']['scientific']
        if species_key not in behavioral_patterns:
            behavioral_patterns[species_key] = {
                'intents': {},
                'communication_types': {},
                'risk_factors': []
            }

        # Update pattern statistics
        intent = alert['behavioral_prediction']['primary_intent']
        behavioral_patterns[species_key]['intents'][intent] = (
            behavioral_patterns[species_key]['intents'].get(intent, 0) + 1
        )

        call_type = alert['communication_analysis']['call_type']
        behavioral_patterns[species_key]['communication_types'][call_type] = (
            behavioral_patterns[species_key]['communication_types'].get(call_type, 0) + 1
        )

        # Store risk factors
        if alert['risk_score'] > 0.7:
            behavioral_patterns[species_key]['risk_factors'].append({
                'timestamp': alert['timestamp'],
                'factors': alert['ai_insights']['threat_assessment'],
                'risk_score': alert['risk_score']
            })

        # Broadcast enhanced alert via WebSocket
        message = json.dumps(alert)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(manager.broadcast(message))
        loop.close()

        logger.info(f"Enhanced alert processed: {alert['species']['common']} - {alert['alert_level']}")

    except Exception as e:
        logger.error(f"Error processing enhanced alert: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize the enhanced system on startup"""
    global warning_system, communication_analyzer

    try:
        # Initialize strategic service first
        await strategic_service.initialize()
        logger.info("Strategic Response Service initialized")
        
        # Initialize the enhanced communication analyzer
        communication_analyzer = AdvancedBirdCommunicationAnalyzer()
        
        # Connect predator sounds system with analyzer
        if strategic_service.strategic_system and strategic_service.strategic_system.predator_sounds:
            predator_sounds = strategic_service.strategic_system.predator_sounds
            communication_analyzer.set_predator_sounds(predator_sounds)
            predator_sounds.set_communication_analyzer(communication_analyzer)
            logger.info("Predator sounds system connected to communication analyzer")
        
        communication_analyzer.add_alert_callback(enhanced_websocket_alert_handler)

        # For backward compatibility, also initialize the original system
        warning_system = communication_analyzer

        # Start background monitoring thread
        thread = threading.Thread(target=communication_analyzer.start_monitoring, daemon=True)
        thread.start()

        logger.info("Enhanced Bird Strike Warning System initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing system: {e}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Enhanced WebSocket endpoint with connection management"""
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic heartbeat
            await websocket.send_text(json.dumps({
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat()
            }))
            await asyncio.sleep(30)  # Heartbeat every 30 seconds
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# INTEGRATION POINT 4: New strategic response endpoints
@app.get("/api/strategic/status")
async def get_strategic_status():
    """Get strategic response system status"""
    try:
        status = await strategic_service.get_system_status()
        return {
            "strategic_system": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting strategic status: {e}")
        return {"error": str(e), "status": "error"}


@app.get("/api/strategic/current-recommendation")
async def get_current_strategic_recommendation():
    """Get current strategic recommendation"""
    try:
        recommendation = await strategic_service.get_current_recommendation()
        return {
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting current recommendation: {e}")
        return {"error": str(e)}


@app.post("/api/strategic/execute-action/{action_id}")
async def execute_strategic_action(action_id: int):
    """Execute a strategic action"""
    try:
        success = await strategic_service.execute_manual_action(action_id)
        return {
            "success": success,
            "action_id": action_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error executing strategic action: {e}")
        return {"error": str(e), "success": False}


@app.post("/api/strategic/stop-predator-sound")
async def stop_predator_sound():
    """Stop the currently playing predator sound"""
    try:
        if strategic_service.strategic_system and strategic_service.strategic_system.predator_sounds:
            predator_sounds = strategic_service.strategic_system.predator_sounds
            predator_sounds.stop_predator_sound()
            # Reset analyzer status
            if predator_sounds.communication_analyzer:
                predator_sounds.communication_analyzer.update_predator_status(False)
            return {"success": True, "message": "Predator sound stopped"}
        return {"success": False, "message": "Predator sound system not initialized"}
    except Exception as e:
        logger.error(f"Error stopping predator sound: {e}")
        return {"error": str(e), "success": False}


@app.post("/api/strategic/activate-predator-sound")
async def activate_predator_sound(sound_data: Dict):
    """Activate predator sound system and log the event"""
    try:
        if not strategic_service.strategic_system or not strategic_service.strategic_system.predator_sounds:
            return {"success": False, "message": "Predator sound system not initialized"}
        
        predator_sounds = strategic_service.strategic_system.predator_sounds
        sound_type = sound_data.get('sound_type', 'hawk_call')
        
        # Play the sound with default settings
        success = predator_sounds.play_predator_sound(
            sound_name=sound_type,
            volume=0.8,
            repeat=1
        )
        
        if success:
            # Log the event in the database
            event = PredatorSoundEvent(
                sound_type=sound_type,
                timestamp=datetime.now()
            )
            db_manager.session.add(event)
            db_manager.session.commit()
            return {"success": True, "message": f"Playing {sound_type}", "event_id": event.id, "event_time": event.timestamp.isoformat()}
        else:
            return {"success": False, "message": f"Failed to play {sound_type}"}
    except Exception as e:
        logger.error(f"Error activating predator sound: {e}")
        return {"error": str(e), "success": False}


@app.get("/api/strategic/predator-sounds")
async def get_predator_sounds_status():
    """Get predator sounds system status"""
    try:
        status = await strategic_service.get_predator_sounds_status()
        return {
            "predator_sounds": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting predator sounds status: {e}")
        return {"error": str(e)}


@app.get("/api/alerts")
async def get_all_alerts():
    """Return all alerts with enhanced AI analysis"""
    try:
        alerts = db_manager.get_active_alerts()
        enhanced_alerts = []
        
        for alert in alerts:
            serialized = serialize_enhanced_alert(alert)
            enhanced_alerts.append(serialized)
        
        return {
            "alerts": enhanced_alerts,
            "total_count": len(enhanced_alerts),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return {"alerts": [], "total_count": 0, "error": str(e)}


@app.get("/api/alerts/recent")
async def get_recent_alerts():
    """Return recent alerts with AI analysis"""
    try:
        alerts = db_manager.session.query(BirdAlert).order_by(
            BirdAlert.timestamp.desc()
        ).limit(10).all()
        
        enhanced_alerts = [serialize_enhanced_alert(alert) for alert in alerts]
        
        return {
            "alerts": enhanced_alerts,
            "count": len(enhanced_alerts),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting recent alerts: {e}")
        return {"alerts": [], "count": 0, "error": str(e)}


@app.get("/api/communication-patterns")
async def get_communication_patterns():
    """Get communication patterns analysis"""
    try:
        return {
            "patterns": behavioral_patterns,
            "history_count": len(communication_history),
            "analysis_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting communication patterns: {e}")
        return {"patterns": {}, "history_count": 0, "error": str(e)}


@app.get("/api/species/{species_name}/behavior")
async def get_species_behavior(species_name: str):
    """Get behavioral analysis for specific species"""
    try:
        species_patterns = behavioral_patterns.get(species_name, {})
        
        # Calculate behavior statistics
        total_detections = sum(species_patterns.get('intents', {}).values())
        intent_percentages = {}
        
        if total_detections > 0:
            for intent, count in species_patterns.get('intents', {}).items():
                intent_percentages[intent] = (count / total_detections) * 100
        
        return {
            "species": species_name,
            "total_detections": total_detections,
            "behavioral_intents": intent_percentages,
            "communication_types": species_patterns.get('communication_types', {}),
            "risk_factors": species_patterns.get('risk_factors', [])[-10:],  # Last 10 risk events
            "analysis_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting species behavior: {e}")
        return {"species": species_name, "error": str(e)}


@app.get("/api/ai-insights")
async def get_ai_insights():
    """Get AI system insights and statistics"""
    try:
        # Calculate insights from communication history
        recent_history = communication_history[-100:]  # Last 100 detections
        
        insights = {
            "total_communications_analyzed": len(communication_history),
            "recent_activity": len(recent_history),
            "species_diversity": len(set(h['species'] for h in recent_history)),
            "alert_level_distribution": {},
            "behavioral_intent_distribution": {},
            "communication_type_distribution": {},
            "risk_trends": [],
            "ai_model_performance": {
                "classification_accuracy": 0.85,  # Placeholder
                "behavioral_prediction_confidence": 0.78,  # Placeholder
                "communication_analysis_success_rate": 0.92  # Placeholder
            }
        }
        
        # Analyze recent patterns
        for item in recent_history:
            # Alert level distribution
            patterns = item.get('patterns', {})
            urgency = patterns.get('urgency_level', 'unknown')
            insights['alert_level_distribution'][urgency] = (
                insights['alert_level_distribution'].get(urgency, 0) + 1
            )
            
            # Behavioral intent distribution
            behavior = item.get('behavior', {})
            intent = behavior.get('primary_intent', 'unknown')
            insights['behavioral_intent_distribution'][intent] = (
                insights['behavioral_intent_distribution'].get(intent, 0) + 1
            )
            
            # Communication type distribution
            call_type = patterns.get('call_type', 'unknown')
            insights['communication_type_distribution'][call_type] = (
                insights['communication_type_distribution'].get(call_type, 0) + 1
            )
        
        return insights
        
    except Exception as e:
        logger.error(f"Error getting AI insights: {e}")
        return {"error": str(e)}


@app.get("/api/stats")
async def get_enhanced_stats():
    """Get enhanced statistics with AI analysis"""
    try:
        base_stats = db_manager.get_detection_stats()
        
        # Add AI-specific statistics
        ai_stats = {
            "communication_patterns_analyzed": len(communication_history),
            "species_behavior_profiles": len(behavioral_patterns),
            "active_monitoring_sessions": len(manager.active_connections),
            "ai_model_status": "active" if communication_analyzer else "inactive",
            "strategic_response_status": "active" if strategic_service.initialized else "inactive",
            "average_risk_score": 0.0,
            "behavioral_prediction_accuracy": 0.78  # Placeholder
        }
        
        # Calculate average risk score from recent history
        if communication_history:
            recent_risks = [
                h.get('behavior', {}).get('confidence', 0)
                for h in communication_history[-50:]
            ]
            ai_stats["average_risk_score"] = sum(recent_risks) / len(recent_risks)

        return {
            **base_stats,
            "ai_statistics": ai_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting enhanced stats: {e}")
        return {"error": str(e)}


@app.post("/api/test-alert")
async def test_enhanced_alert():
    """Generate a test alert with AI analysis"""
    try:
        now = datetime.now().isoformat()
        
        # Create realistic AI analysis data
        fake_alert = {
            "timestamp": now,
            "species": {
                "scientific": "Corvus splendens",
                "common": "House Crow"
            },
            "confidence": 0.88,
            "risk_score": 0.75,
            "alert_level": "HIGH",
            "recommended_action": "DELAY_TAKEOFF",
            "communication_analysis": {
                "call_type": "territorial_call",
                "emotional_state": "agitated",
                "behavioral_context": "territory_defense",
                "urgency_level": "high",
                "flock_communication": True,
                "territorial_behavior": True,
                "alarm_signal": True
            },
            "behavioral_prediction": {
                "primary_intent": "territory_defense",
                "confidence": 0.82,
                "all_scores": {
                    "landing_approach": 0.15,
                    "territory_defense": 0.82,
                    "flock_gathering": 0.23,
                    "predator_avoidance": 0.05,
                    "normal_flight": 0.10
                }
            },
            "ai_insights": {
                "call_interpretation": [
                    "Territorial call - defending area",
                    "Flock coordination - group movement",
                    "High urgency - immediate response needed"
                ],
                "threat_assessment": [
                    "Active alarm signals detected",
                    "Flock coordination increases collision risk",
                    "High urgency vocalizations"
                ],
                "recommended_monitoring": [
                    "Bird may remain in area - sustained monitoring needed",
                    "Prepare for potential mass movement"
                ]
            }
        }
        
        # --- NEW: Save detection for test alert ---
        species = db_manager.get_species_by_name(fake_alert['species']['common'])
        if not species:
            image_service = BirdImageService()
            image_data = image_service.fetch_bird_image(
                fake_alert['species']['common'],
                fake_alert['species']['scientific']
            )
            new_species = BirdSpecies(
                scientific_name=fake_alert['species']['scientific'],
                common_name=fake_alert['species']['common'],
                risk_level=fake_alert['alert_level'],
                size_category='UNKNOWN',
                typical_behavior=fake_alert['behavioral_prediction']['primary_intent'],
                migration_pattern='',
                image_url=image_data['image_url'],
                image_data=image_data['image_data'],
                image_source=image_data['image_source'],
                image_fetched_at=image_data['image_fetched_at']
            )
            db_manager.session.add(new_species)
            db_manager.session.commit()
            species = new_species
        
        detection_data = {
            'species_id': species.id,
            'timestamp': datetime.fromisoformat(fake_alert['timestamp']),
            'confidence': fake_alert.get('confidence'),
            'call_type': fake_alert.get('communication_analysis', {}).get('call_type'),
            'emotional_state': fake_alert.get('communication_analysis', {}).get('emotional_state'),
            'behavioral_pattern': fake_alert.get('behavioral_prediction', {}).get('primary_intent'),
            'duration': None,
            'frequency_range': None,
            'amplitude': None,
            'location_x': None,
            'location_y': None,
            'distance_from_runway': None,
            'direction': None,
            'weather_conditions': None,
            'time_of_day': None,
            'season': None,
            'group_behavior': fake_alert.get('communication_analysis', {}).get('flock_communication'),
        }
        detection = db_manager.add_detection(detection_data)
        # --- END NEW ---
        
        # Process through the enhanced handler
        fake_alert['detection_id'] = detection.id
        enhanced_websocket_alert_handler(fake_alert)
        
        return {
            "message": "Enhanced test alert triggered",
            "alert": fake_alert,
            "timestamp": now
        }
        
    except Exception as e:
        logger.error(f"Error generating test alert: {e}")
        return {"error": str(e)}


@app.get("/api/audio-config")
async def get_audio_config():
    """Get audio configuration for the AI system"""
    try:
        if communication_analyzer:
            return {
                "sample_rate": communication_analyzer.RATE,
                "channels": communication_analyzer.CHANNELS,
                "chunk_size": communication_analyzer.CHUNK,
                "analysis_window": f"{communication_analyzer.RECORD_SECONDS}s",
                "ai_models_loaded": True,
                "frequency_range": "20Hz - 22kHz",
                "features_extracted": [
                    "MFCC", "Spectral Centroid", "Spectral Rolloff",
                    "Zero Crossing Rate", "Chroma", "Tempo"
                ]
            }
        else:
            return {
                "sample_rate": 44100,
                "channels": 1,
                "ai_models_loaded": False,
                "status": "system_not_initialized"
            }
            
    except Exception as e:
        logger.error(f"Error getting audio config: {e}")
        return {"error": str(e)}


@app.post("/api/acknowledge-alert/{alert_id}")
async def acknowledge_alert(alert_id: int):
    """Acknowledge an alert"""
    try:
        alert = db_manager.session.query(BirdAlert).filter(
            BirdAlert.id == alert_id
        ).first()
        
        if alert:
            alert.acknowledged = True
            db_manager.session.commit()
            
            # Broadcast acknowledgment
            await manager.broadcast(json.dumps({
                "type": "alert_acknowledged",
                "alert_id": alert_id,
                "timestamp": datetime.now().isoformat()
            }))
            
            return {"message": "Alert acknowledged", "alert_id": alert_id}
        else:
            return {"error": "Alert not found"}, 404
            
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        return {"error": str(e)}


@app.post("/api/resolve-alert/{alert_id}")
async def resolve_alert(alert_id: int):
    """Resolve an alert"""
    try:
        alert = db_manager.session.query(BirdAlert).filter(
            BirdAlert.id == alert_id
        ).first()
        
        if alert:
            alert.resolved = True
            alert.acknowledged = True
            db_manager.session.commit()
            
            # Broadcast resolution
            await manager.broadcast(json.dumps({
                "type": "alert_resolved",
                "alert_id": alert_id,
                "timestamp": datetime.now().isoformat()
            }))
            
            return {"message": "Alert resolved", "alert_id": alert_id}
        else:
            return {"error": "Alert not found"}, 404
            
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        return {"error": str(e)}

def serialize_enhanced_alert(alert):
    """Serialize alert with AI analysis data"""
    try:
        base_alert = {
            "id": alert.id,
            "timestamp": alert.timestamp.isoformat(),
            "alert_level": alert.alert_level,
            "risk_score": alert.risk_score,
            "recommended_action": alert.recommended_action,
            "species": {
                "common": alert.species.common_name if alert.species else "Unknown",
                "scientific": alert.species.scientific_name if alert.species else "Unknown"
            },
            "acknowledged": alert.acknowledged,
            "resolved": alert.resolved,
            "image_data": alert.species.image_data if alert.species else None
        }
        
        # Add AI analysis if available
        ai_data = None
        if hasattr(alert, 'ai_analysis') and alert.ai_analysis:
            try:
                ai_data = json.loads(alert.ai_analysis)
                base_alert.update(ai_data)
            except (json.JSONDecodeError, AttributeError):
                pass
        
        # Try to extract audio_segment from ai_analysis or base_alert
        audio_segment = None
        if ai_data and isinstance(ai_data.get('audio_segment'), dict):
            audio_segment = ai_data['audio_segment']
        elif isinstance(base_alert.get('audio_segment'), dict):
            audio_segment = base_alert['audio_segment']
        # NEW: If detection has audio_segment_filename, add audio_url
        if hasattr(alert, 'detection') and alert.detection and getattr(alert.detection, 'audio_segment_filename', None):
            base_alert['audio_url'] = f"http://localhost:8000/api/audio-segment/{alert.detection.audio_segment_filename}/play"
        elif audio_segment and audio_segment.get('segment_id'):
            base_alert['audio_segment'] = audio_segment
            base_alert['audio_url'] = f"http://localhost:5000/api/audio-segment/{audio_segment['segment_id']}/play"
        return base_alert
           
    except Exception as e:
        logger.error(f"Error serializing alert: {e}")
        return {"error": "serialization_failed"}
    
    
@app.get("/api/bird-details/{bird_name}")
async def get_bird_details(bird_name: str):
    try:
        encyclopedia = get_bird_encyclopedia(bird_name)
        return JSONResponse(content={"details": encyclopedia})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/strategic/process-alert")
async def process_strategic_alert(bird_data: Dict):
    """Process a bird alert and generate strategic response"""
    try:
        response = await strategic_service.process_bird_alert(bird_data)
        if response:
            return {
                "success": True,
                "strategic_recommendation": response.get("strategic_recommendation"),
                "timestamp": datetime.now().isoformat()
            }
        return {
            "success": False,
            "error": "No recommendation generated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing strategic alert: {e}")
        return {"error": str(e), "success": False}

"""
@app.post("/api/analyze-audio")
async def analyze_audio(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        y, sr = librosa.load(librosa.util.buf_to_float(contents), sr=32000)
        intervals = librosa.effects.split(y, top_db=20)
        detections = []

        for i, (start, end) in enumerate(intervals):
            segment = y[start:end]
            bird_name, confidence = classify_audio_segment(segment, sr)
            if bird_name:
                interpretation = get_call_interpretation(bird_name)
                detections.append({
                    "id": i,
                    "bird_name": bird_name,
                    "confidence": f"{confidence:.2%}",
                    "timestamp": f"{start/sr:.2f}s - {end/sr:.2f}s",
                    "interpretation": interpretation
                })

        if not detections:
            return {"message": "No significant bird sounds detected"}
        return {"detections": detections}
    except Exception as e:
        return {"error": str(e)}
"""

@app.get("/api/strategic/recommended-sounds")
async def get_recommended_predator_sounds(species: str, behavior: str = ""):
    """Get recommended predator sounds for a given bird species and behavior (at least 3 if possible)"""
    try:
        if not strategic_service.strategic_system or not strategic_service.strategic_system.predator_sounds:
            return {"success": False, "message": "Predator sound system not initialized", "sounds": []}
        predator_sounds = strategic_service.strategic_system.predator_sounds
        # Use backend logic to get the best sounds
        bird_category = "default"
        species_lower = species.lower()
        if any(corvid in species_lower for corvid in ["crow", "raven", "magpie", "jay"]):
            bird_category = "corvids"
        elif any(passerine in species_lower for passerine in ["sparrow", "finch", "warbler", "robin"]):
            bird_category = "passerines"
        elif any(raptor in species_lower for raptor in ["hawk", "eagle", "falcon", "kestrel"]):
            bird_category = "raptors"
        elif any(waterfowl in species_lower for waterfowl in ["duck", "goose", "swan", "gull"]):
            bird_category = "waterfowl"
        mapped_sounds = predator_sounds.predator_mappings.get(bird_category, predator_sounds.predator_mappings["default"])
        available_sounds = [s for s in mapped_sounds if s in predator_sounds.sound_cache]
        # Filter by behavior for aggressive sounds
        if "territorial" in behavior.lower() or "aggressive" in behavior.lower():
            aggressive_sounds = ["hawk_screech", "eagle_cry", "falcon_call"]
            aggressive_available = [s for s in available_sounds if s in aggressive_sounds]
            if len(aggressive_available) >= 3:
                available_sounds = aggressive_available
        # Always return at least 3 if possible
        if len(available_sounds) < 3:
            # Fill with any available
            all_sounds = list(predator_sounds.sound_cache.keys())
            for s in all_sounds:
                if s not in available_sounds:
                    available_sounds.append(s)
                if len(available_sounds) >= 3:
                    break
        return {"success": True, "sounds": available_sounds[:3]}
    except Exception as e:
        logger.error(f"Error getting recommended predator sounds: {e}")
        return {"success": False, "message": str(e), "sounds": []}

@app.get("/api/strategic/predator-sound-effectiveness")
async def get_predator_sound_effectiveness(event_id: int, window_minutes: int = 5):
    """
    Calculate effectiveness as reduction in bird detections after sound played.
    event_id: ID of the PredatorSoundEvent
    window_minutes: time window before and after event (default 5 min)
    """
    try:
        event = db_manager.session.query(PredatorSoundEvent).filter_by(id=event_id).first()
        if not event:
            return {"success": False, "error": "Event not found"}
        event_dt = event.timestamp
        before_start = event_dt - timedelta(minutes=window_minutes)
        before_end = event_dt
        after_start = event_dt
        after_end = event_dt + timedelta(minutes=window_minutes)
        # Count detections
        before_count = db_manager.session.query(BirdAlert).filter(
            BirdAlert.timestamp >= before_start,
            BirdAlert.timestamp < before_end
        ).count()
        after_count = db_manager.session.query(BirdAlert).filter(
            BirdAlert.timestamp >= after_start,
            BirdAlert.timestamp < after_end
        ).count()
        if before_count == 0:
            effectiveness = 0.0
        else:
            effectiveness = max(0.0, min(1.0, (before_count - after_count) / before_count))
        # Optionally, store effectiveness in the event
        event.effectiveness = effectiveness * 100
        db_manager.session.commit()
        return {
            "success": True,
            "effectiveness": round(effectiveness * 100, 1),
            "before": before_count,
            "after": after_count,
            "event_id": event_id
        }
    except Exception as e:
        logger.error(f"Error calculating predator sound effectiveness: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/strategic/effectiveness-by-environment")
async def get_effectiveness_by_environment(location_type: str = 'airport'):
    """Get average deterrent effectiveness for a given environment/location_type."""
    try:
        result = db_manager.get_effectiveness_by_environment(location_type)
        return {"success": True, **result}
    except Exception as e:
        logger.error(f"Error getting effectiveness by environment: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/strategic/trigger-predator-sound")
async def trigger_predator_sound(alert_id: int = None, detection_id: int = None, sound_type: str = 'eagle_cry'):
    """Trigger predator sound for a specific alert or detection if high risk/critical."""
    try:
        alert = None
        if alert_id:
            alert = db_manager.session.query(BirdAlert).filter(BirdAlert.id == alert_id).first()
        elif detection_id:
            # Find alert by detection_id
            alert = db_manager.session.query(BirdAlert).filter(BirdAlert.detection_id == detection_id).first()
        if not alert:
            return {"success": False, "error": "Alert not found"}
        if alert.alert_level not in ['HIGH', 'CRITICAL']:
            return {"success": False, "error": "Alert is not high risk or critical"}
        if strategic_service.strategic_system and strategic_service.strategic_system.predator_sounds:
            predator_sounds = strategic_service.strategic_system.predator_sounds
            predator_sounds.play_predator_sound(
                sound_name=sound_type,
                volume=0.8,
                repeat=1
            )
            # Optionally log the event
            event = PredatorSoundEvent(
                sound_type=sound_type,
                timestamp=datetime.now(),
                location_type=getattr(alert, 'location_type', 'airport')
            )
            db_manager.session.add(event)
            db_manager.session.commit()
            return {"success": True, "message": f"Predator sound {sound_type} triggered."}
        return {"success": False, "error": "Predator sound system not initialized"}
    except Exception as e:
        logger.error(f"Error triggering predator sound: {e}")
        return {"success": False, "error": str(e)}
    


AUDIO_SEGMENTS_DIR = os.path.join(os.path.dirname(__file__), "..", "detected_audio_segments")

@app.get("/api/audio-segments")
async def get_audio_segments():
    """List all stored audio segments metadata."""
    try:
        segments = []
        for fname in os.listdir(AUDIO_SEGMENTS_DIR):
            if fname.endswith(".wav"):
                segments.append({
                    "filename": fname,
                    "segment_id": fname.split("_")[-1].replace(".wav", ""),
                    "file_path": os.path.join(AUDIO_SEGMENTS_DIR, fname)
                })
        return {"success": True, "segments": segments, "total_count": len(segments)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/audio-segment/{segment_id}/play")
async def play_audio_segment(segment_id: str):
    """Serve audio file for playback."""
    try:
        # Find the file by segment_id
        for fname in os.listdir(AUDIO_SEGMENTS_DIR):
            if fname.endswith(".wav") and segment_id in fname:
                file_path = os.path.join(AUDIO_SEGMENTS_DIR, fname)
                return FileResponse(file_path, media_type="audio/wav", filename=fname)
        return JSONResponse({"success": False, "error": "Audio file not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)   

@app.get("/api/audio-segment/{segment_id}/download")
async def download_audio_segment(segment_id: str):
    """Download audio file."""
    try:
        # Find the file by segment_id
        for fname in os.listdir(AUDIO_SEGMENTS_DIR):
            if fname.endswith(".wav") and segment_id in fname:
                file_path = os.path.join(AUDIO_SEGMENTS_DIR, fname)
                return FileResponse(
                    file_path,
                    media_type="audio/wav",
                    filename=fname,
                    headers={"Content-Disposition": f"attachment; filename={fname}"}
                )
        return JSONResponse({"success": False, "error": "Audio file not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

"""Risk assessment Part"""
# Initialize weather service
weather_service = WeatherService()

@app.get("/api/risk-assessment/overall")
def get_overall_risk(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get overall risk assessment including current risk level and contributing factors"""
    try:
        # Get latest risk assessments for all runways
        latest_assessments = (
            db.query(RunwayRiskAssessment)
            .order_by(RunwayRiskAssessment.timestamp.desc())
            .limit(10)
            .all()
        )
        
        if not latest_assessments:
            return {
                "overall_risk": 0,
                "risk_factors": [],
                "status": "No recent risk assessments available"
            }

        # Calculate overall risk as average of recent assessments
        risk_scores = [assessment.overall_risk_score for assessment in latest_assessments]
        overall_risk = int(statistics.mean(risk_scores))

        # Get risk factors with trends
        risk_factors = [
            {
                "name": "Bird Activity Level",
                "value": int(statistics.mean([a.bird_activity_risk for a in latest_assessments])),
                "trend": "up" if any(a.bird_activity_risk > 30 for a in latest_assessments) else "stable",
                "description": "Based on recent bird activity patterns"
            },
            {
                "name": "Weather Impact",
                "value": int(statistics.mean([a.weather_risk for a in latest_assessments])),
                "trend": "stable",
                "description": "Current weather conditions impact"
            },
            {
                "name": "Seasonal Migration",
                "value": int(statistics.mean([a.seasonal_risk for a in latest_assessments])),
                "trend": "up" if any(a.seasonal_risk > 40 for a in latest_assessments) else "stable",
                "description": "Migration season impact"
            },
            {
                "name": "Flight Schedule Density",
                "value": int(statistics.mean([a.traffic_density_risk for a in latest_assessments])),
                "trend": "down" if all(a.traffic_density_risk < 30 for a in latest_assessments) else "stable",
                "description": "Based on current flight schedule"
            }
        ]

        return {
            "overall_risk": overall_risk,
            "risk_factors": risk_factors,
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk-assessment/alerts")
def get_active_alerts(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get current active alerts"""
    try:
        # Get unresolved alerts from last 24 hours
        recent_alerts = (
            db.query(BirdAlert)
            .filter(
                BirdAlert.resolved == False,
                BirdAlert.timestamp >= datetime.utcnow() - timedelta(hours=24)
            )
            .order_by(BirdAlert.timestamp.desc())
            .all()
        )

        alerts = []
        for alert in recent_alerts:
            try:
                alerts.append({
                    "id": alert.id,  # Add the alert ID from the database
                    "level": alert.alert_level.lower() if alert.alert_level else "low",
                    "message": alert.recommended_action or "Monitor situation",
                    "time": alert.timestamp.strftime("%H:%M") if alert.timestamp else "N/A",
                    "runway": alert.detection.runway_name if alert.detection else "General Area",
                    "risk_score": alert.risk_score or 0
                })
            except Exception as e:
                print(f"Error processing alert {alert.id}: {str(e)}")
                continue

        return {"alerts": alerts}

    except Exception as e:
        print(f"Error in get_active_alerts: {str(e)}")
        # Return empty alerts instead of throwing error
        return {"alerts": []}

@app.get("/api/risk-assessment/weather")
def get_weather_impact(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get current weather conditions and impact"""
    try:
        # Get real-time weather data from OpenWeatherMap
        weather_data = weather_service.get_current_weather()
        
        if not weather_data:
            return {
                "temperature": 0,
                "windSpeed": 0,
                "windDirection": "N/A",
                "precipitation": 0,
                "visibility": 0,
                "birdFavorability": "Low"
            }

        # Store the weather data in our database for historical tracking
        db_weather = WeatherData(
            temperature=weather_data["temperature"],
            wind_speed=weather_data["windSpeed"],
            wind_direction=weather_data["windDirection"],
            precipitation=weather_data["precipitation"],
            visibility=weather_data["visibility"],
            bird_favorability_score=weather_data["birdFavorability"],
            timestamp=weather_data["timestamp"]
        )
        db.add(db_weather)
        db.commit()

        return weather_data

    except Exception as e:
        print(f"Error in get_weather_impact: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk-assessment/runways")
def get_runway_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get current status for all runways"""
    try:
        runways = db.query(Runway).filter(Runway.is_active == True).all()
        runway_status = []

        for runway in runways:
            # Get latest risk assessment
            latest_assessment = (
                db.query(RunwayRiskAssessment)
                .filter(RunwayRiskAssessment.runway_id == runway.id)
                .order_by(RunwayRiskAssessment.timestamp.desc())
                .first()
            )

            # Count active birds near runway
            active_birds = (
                db.query(BirdDetection)
                .filter(
                    BirdDetection.timestamp >= datetime.utcnow() - timedelta(hours=1),
                    BirdDetection.distance_from_runway <= runway.approach_zone_length
                )
                .count()
            )

            # Get latest incident
            latest_incident = (
                db.query(BirdAlert)
                .filter(
                    BirdAlert.detection.has(
                        BirdDetection.distance_from_runway <= runway.approach_zone_length
                    )
                )
                .order_by(BirdAlert.timestamp.desc())
                .first()
            )

            status = {
                "name": runway.runway_name,
                "risk": int(latest_assessment.overall_risk_score) if latest_assessment else 0,
                "status": "caution" if (latest_assessment and latest_assessment.overall_risk_score > 20) else "clear",
                "birdCount": active_birds,
                "lastIncident": "Never" if not latest_incident else _format_time_ago(latest_incident.timestamp)
            }
            runway_status.append(status)

        return {"runways": runway_status}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk-assessment/map/{runway_name}")
def get_runway_map_data(runway_name: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get detailed map data for a specific runway"""
    try:
        # Handle combined runway names (e.g., "09L/27R")
        runway = db.query(Runway).filter(Runway.runway_name == runway_name).first()
        if not runway:
            # If exact match not found, try matching the first part of the name
            runway_parts = runway_name.split('/')
            runway = db.query(Runway).filter(Runway.runway_name.like(f"%{runway_parts[0]}%")).first()
            
        if not runway:
            raise HTTPException(status_code=404, detail=f"Runway {runway_name} not found")

        # Get active birds near runway
        active_birds = (
            db.query(BirdDetection)
            .filter(
                BirdDetection.timestamp >= datetime.utcnow() - timedelta(hours=1),
                BirdDetection.distance_from_runway <= runway.approach_zone_length
            )
            .all()
        )

        # Get latest risk assessment
        latest_assessment = (
            db.query(RunwayRiskAssessment)
            .filter(RunwayRiskAssessment.runway_id == runway.id)
            .order_by(RunwayRiskAssessment.timestamp.desc())
            .first()
        )

        # Format bird positions for frontend
        bird_positions = []
        for bird in active_birds:
            # Scale bird positions to fit the map view
            scaled_x = bird.location_x * (runway.length / 2000) + runway.length / 2
            scaled_y = bird.location_y * (runway.width / 1000) + runway.width / 2
            
            bird_positions.append({
                "id": bird.id,
                "x": scaled_x,
                "y": scaled_y,
                "altitude": None,  # Not tracked in current schema
                "direction": bird.direction or "N/A",
                "risk_level": "HIGH" if bird.distance_from_runway < runway.side_clearance else "MEDIUM"
            })

        # Define risk zones based on latest assessment
        risk_zones = []
        if latest_assessment:
            # Create approach zone
            approach_zone = {
                "type": "high_risk",
                "coordinates": [
                    {"x": 0, "y": -runway.approach_zone_width/2},
                    {"x": runway.approach_zone_length, "y": -runway.approach_zone_width/2},
                    {"x": runway.approach_zone_length, "y": runway.approach_zone_width/2},
                    {"x": 0, "y": runway.approach_zone_width/2}
                ]
            }
            risk_zones.append(approach_zone)

            # Create runway zone
            runway_zone = {
                "type": "caution",
                "coordinates": [
                    {"x": 0, "y": -runway.width/2},
                    {"x": runway.length, "y": -runway.width/2},
                    {"x": runway.length, "y": runway.width/2},
                    {"x": 0, "y": runway.width/2}
                ]
            }
            risk_zones.append(runway_zone)

            # Add side clearance zones if risk is high
            if latest_assessment.overall_risk_score > 50:
                left_zone = {
                    "type": "caution",
                    "coordinates": [
                        {"x": 0, "y": -runway.width/2 - runway.side_clearance},
                        {"x": runway.length, "y": -runway.width/2 - runway.side_clearance},
                        {"x": runway.length, "y": -runway.width/2},
                        {"x": 0, "y": -runway.width/2}
                    ]
                }
                right_zone = {
                    "type": "caution",
                    "coordinates": [
                        {"x": 0, "y": runway.width/2},
                        {"x": runway.length, "y": runway.width/2},
                        {"x": runway.length, "y": runway.width/2 + runway.side_clearance},
                        {"x": 0, "y": runway.width/2 + runway.side_clearance}
                    ]
                }
                risk_zones.extend([left_zone, right_zone])

        return {
            "runway": {
                "name": runway.runway_name,
                "length": runway.length,
                "width": runway.width,
                "orientation": runway.orientation
            },
            "bird_positions": bird_positions,
            "risk_zones": risk_zones,
            "risk_level": latest_assessment.overall_risk_score if latest_assessment else 0
        }

    except Exception as e:
        print(f"Error in get_runway_map_data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk-assessment/history/{runway_name}")
def get_runway_history(
    runway_name: str, 
    days: int = 7, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get historical data for a specific runway"""
    try:
        runway = db.query(Runway).filter(Runway.runway_name == runway_name).first()
        if not runway:
            raise HTTPException(status_code=404, detail=f"Runway {runway_name} not found")

        # Get historical risk assessments
        start_date = datetime.utcnow() - timedelta(days=days)
        historical_assessments = (
            db.query(RunwayRiskAssessment)
            .filter(
                RunwayRiskAssessment.runway_id == runway.id,
                RunwayRiskAssessment.timestamp >= start_date
            )
            .order_by(RunwayRiskAssessment.timestamp.asc())
            .all()
        )

        # Get bird incidents
        incidents = (
            db.query(BirdAlert)
            .filter(
                BirdAlert.runway_id == runway.id,
                BirdAlert.timestamp >= start_date,
                BirdAlert.alert_level.in_(["HIGH", "CRITICAL"])
            )
            .all()
        )

        # Group data by date
        history = []
        current_date = start_date
        while current_date <= datetime.utcnow():
            day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            # Get assessments for this day
            day_assessments = [
                a for a in historical_assessments 
                if day_start <= a.timestamp < day_end
            ]
            
            # Get incidents for this day
            day_incidents = len([
                i for i in incidents 
                if day_start <= i.timestamp < day_end
            ])

            if day_assessments:
                avg_risk = statistics.mean([a.overall_risk_score for a in day_assessments])
                max_birds = max([a.bird_count or 0 for a in day_assessments])
                
                history.append({
                    "date": day_start.strftime("%Y-%m-%d"),
                    "risk_level": round(avg_risk),
                    "bird_count": max_birds,
                    "incidents": day_incidents
                })
            
            current_date += timedelta(days=1)

        return {
            "runway_name": runway_name,
            "history": history
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AlertResponse(BaseModel):
    alert_id: int
    action_taken: str
    notes: str = None
    template_key: Optional[str] = None

@app.post("/api/risk-assessment/alerts/{alert_id}/respond")
def respond_to_alert(alert_id: int, response: AlertResponse, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Handle response to an alert"""
    try:
        alert = db.query(BirdAlert).filter(BirdAlert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        # Get template if specified
        template_data = {}
        if response.template_key:
            template_data = get_response_template(response.template_key)
            if not template_data:
                raise HTTPException(status_code=400, detail=f"Invalid template key: {response.template_key}")

        # Update alert with response
        alert.acknowledged = True
        alert.acknowledged_at = datetime.utcnow()
        alert.action_taken = response.action_taken
        alert.resolved = True
        alert.resolved_at = datetime.utcnow()

        # Apply template-specific updates if available
        if template_data and "status_update" in template_data:
            status_update = template_data["status_update"]
            
            # Update alert level if specified
            if "alert_level" in status_update:
                alert.alert_level = status_update["alert_level"]
            
            # Adjust risk score if specified
            if "risk_score_adjustment" in status_update:
                new_risk_score = max(0, min(100, alert.risk_score + status_update["risk_score_adjustment"]))
                alert.risk_score = new_risk_score

            # Add template info to notes
            template_notes = template_data.get("notes", "")
            alert.notes = f"{response.notes}\n\nTemplate: {response.template_key}\n{template_notes}" if response.notes else template_notes

        db.commit()

        return {
            "status": "success",
            "message": "Alert response recorded successfully",
            "alert": {
                "id": alert.id,
                "level": alert.alert_level,
                "risk_score": alert.risk_score,
                "action_taken": alert.action_taken,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def _format_time_ago(timestamp: datetime) -> str:
    """Format time difference as human readable string"""
    now = datetime.utcnow()
    diff = now - timestamp

    if diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hours ago"
    else:
        minutes = diff.seconds // 60
        return f"{minutes} minutes ago"


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )