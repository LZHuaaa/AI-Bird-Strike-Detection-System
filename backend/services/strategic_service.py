#!/usr/bin/env python3
"""
Strategic Response Service - Integration layer for the strategic response system
Provides a clean interface between the main app and the strategic system
"""

import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
import json
from strategic_response import StrategicResponseSystem, NextActionPanel, NextActionRecommendation

logger = logging.getLogger(__name__)

class StrategicResponseService:
    """Service layer for strategic response system integration"""
    
    def __init__(self):
        self.strategic_system = None
        self.next_action_panel = None
        self.initialized = False
        self.current_recommendation = None
        self.active_responses = {}
        
    async def initialize(self):
        """Initialize the strategic response system"""
        try:
            # Initialize in a background thread to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._init_strategic_system)
            self.initialized = True
            logger.info("Strategic Response Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Strategic Response Service: {e}")
            self.initialized = False
    
    def _init_strategic_system(self):
        """Initialize the strategic system components"""
        self.strategic_system = StrategicResponseSystem()
        self.next_action_panel = NextActionPanel(self.strategic_system)
    
    async def process_bird_alert(self, alert_data: Dict) -> Optional[Dict]:
        """Process a bird alert and generate strategic response"""
        if not self.initialized:
            logger.warning("Strategic system not initialized")
            return None
        
        try:
            # Convert alert data to format expected by strategic system
            bird_data = self._convert_alert_to_bird_data(alert_data)
            
            # Generate strategic recommendation
            recommendation = await self._generate_recommendation(bird_data)
            
            # Store current recommendation
            self.current_recommendation = recommendation
            
            # Return simplified response for API
            return self._format_strategic_response(recommendation)
            
        except Exception as e:
            logger.error(f"Error processing strategic response: {e}")
            return None
    
    async def _generate_recommendation(self, bird_data: Dict) -> NextActionRecommendation:
        """Generate recommendation in background thread"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.next_action_panel.update_recommendation, 
            bird_data
        )
    
    def _convert_alert_to_bird_data(self, alert_data: Dict) -> Dict:
        """Convert API alert data to strategic system format"""
        return {
            "species": alert_data.get("species", {}),
            "alert_level": alert_data.get("alert_level", "LOW"),
            "risk_score": alert_data.get("risk_score", 0.0),
            "communication_analysis": alert_data.get("communication_analysis", {}),
            "behavioral_prediction": alert_data.get("behavioral_prediction", {}),
            "timestamp": alert_data.get("timestamp", datetime.now().isoformat())
        }
    
    def _format_strategic_response(self, recommendation: NextActionRecommendation) -> Dict:
        """Format strategic response for API consumption"""
        if not recommendation:
            return {}
        
        return {
            "strategic_recommendation": {
                "timestamp": recommendation.timestamp,
                "situation_analysis": recommendation.situation_analysis,
                "confidence_score": recommendation.confidence_score,
                "reasoning": recommendation.reasoning,
                "actions": [
                    {
                        "action_type": action.action_type.value,
                        "priority": action.priority,
                        "description": action.description,
                        "estimated_duration": action.estimated_duration,
                        "success_probability": action.success_probability,
                        "automated": action.automated,
                        "risk_assessment": action.risk_assessment
                    }
                    for action in recommendation.recommended_actions
                ],
                "risk_factors": recommendation.risk_factors,
                "success_metrics": recommendation.success_metrics
            }
        }
    
    async def get_current_recommendation(self) -> Optional[Dict]:
        """Get current strategic recommendation"""
        if not self.initialized or not self.current_recommendation:
            return None
        
        return self._format_strategic_response(self.current_recommendation)
    
    async def execute_manual_action(self, action_id: int) -> bool:
        """Execute a manual action"""
        if not self.initialized or not self.next_action_panel:
            return False
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.next_action_panel.execute_manual_action, 
                action_id
            )
            return result
        except Exception as e:
            logger.error(f"Error executing manual action: {e}")
            return False
    
    async def get_system_status(self) -> Dict:
        """Get strategic system status"""
        if not self.initialized:
            return {
                "status": "not_initialized",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            loop = asyncio.get_event_loop()
            status = await loop.run_in_executor(
                None, 
                self.strategic_system.get_system_status
            )
            
            # Add predator sounds information
            predator_sounds_status = {}
            if self.strategic_system and self.strategic_system.predator_sounds:
                predator_sounds = self.strategic_system.predator_sounds
                predator_sounds_status = {
                    "status": "active",
                    "sounds_loaded": len(predator_sounds.sound_cache),
                    "available_sounds": list(predator_sounds.sound_cache.keys()),
                    "current_sound": predator_sounds.get_current_sound_type()
                }
            
            return {
                "status": "active",
                "strategic_system": status,
                "predator_sounds": predator_sounds_status,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_predator_sounds_status(self) -> Dict:
        """Get predator sounds system status"""
        if not self.initialized or not self.strategic_system:
            return {"status": "not_initialized"}
        
        try:
            predator_sounds = self.strategic_system.predator_sounds
            return {
                "status": "active",
                "sounds_loaded": len(predator_sounds.sound_cache),
                "available_sounds": list(predator_sounds.sound_cache.keys()),
                "predator_mappings": predator_sounds.predator_mappings,
                "current_sound": predator_sounds.get_current_sound_type()
            }
        except Exception as e:
            logger.error(f"Error getting predator sounds status: {e}")
            return {"status": "error", "error": str(e)}

# Global service instance
strategic_service = StrategicResponseService()