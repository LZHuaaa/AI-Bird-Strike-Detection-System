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
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import librosa
import numpy as np
import json
import asyncio
import threading
import uvicorn
import random
import numpy as np
from pydantic import BaseModel
import logging

# Import enhanced detection system and DB manager
from bird_communication_system import AdvancedBirdCommunicationAnalyzer
from db import DatabaseManager, BirdImageService, BirdAlert, BirdSpecies
from audio_analysis import classify_audio_segment
from gemini_utils import get_call_interpretation, get_bird_encyclopedia

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

        # Enhanced database storage with AI insights
        db_alert = db_manager.add_alert({
            "detection_id": None,
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
            'behavior': alert['behavioral_prediction']
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
        # Initialize the enhanced communication analyzer
        communication_analyzer = AdvancedBirdCommunicationAnalyzer()
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
        
        # Process through the enhanced handler
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
                "common": alert.species.common_name,
                "scientific": alert.species.scientific_name
            },
            "acknowledged": alert.acknowledged,
            "resolved": alert.resolved
        }
        
        # Add AI analysis if available
        if hasattr(alert, 'ai_analysis') and alert.ai_analysis:
            try:
                ai_data = json.loads(alert.ai_analysis)
                base_alert.update(ai_data)
            except (json.JSONDecodeError, AttributeError):
                pass
        
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


if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )