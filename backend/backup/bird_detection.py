#!/usr/bin/env python3
"""
Enhanced Bird Strike Warning System with AI Communication Analysis
Uses multiple AI models for bird detection, communication analysis, and behavioral prediction
"""

import pyaudio
import numpy as np
import wave
import threading
import time
import os
import librosa
import torch
import tensorflow as tf
from datetime import datetime
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import json
import requests
import cv2
from transformers import pipeline, AutoFeatureExtractor, AutoModelForAudioClassification
import scipy.signal
try:
    from scipy.signal.windows import hann
    scipy.signal.hann = hann
except ImportError:
    pass  # hann is already available in older scipy versions
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pickle
import warnings
warnings.filterwarnings('ignore')


class AdvancedBirdCommunicationAnalyzer:
    def __init__(self):
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.RECORD_SECONDS = 3

        # Initialize multiple AI models
        self.setup_ai_models()
        
        # Communication patterns database
        self.communication_patterns = {}
        self.behavioral_contexts = {}
        
        # Malaysian airport high-risk species with extended behavioral data
        self.HIGH_RISK_SPECIES = {
            'Corvus splendens': {
                'common': 'House Crow', 
                'risk': 0.9,
                'flock_behavior': 'highly_social',
                'territorial_calls': ['caw', 'rattle', 'click'],
                'alarm_patterns': ['rapid_succession', 'pitch_variation'],
                'flight_patterns': 'erratic_when_alarmed'
            },
            'Corvus macrorhynchos': {
                'common': 'Large-billed Crow', 
                'risk': 0.8,
                'flock_behavior': 'family_groups',
                'territorial_calls': ['deep_caw', 'grunt', 'whistle'],
                'alarm_patterns': ['descending_pitch', 'repeated_calls'],
                'flight_patterns': 'coordinated_group_movement'
            },
            'Haliaeetus leucogaster': {
                'common': 'White-bellied Sea Eagle', 
                'risk': 0.95,
                'flock_behavior': 'solitary_pairs',
                'territorial_calls': ['harsh_bark', 'whistle', 'scream'],
                'alarm_patterns': ['extended_calls', 'circling_behavior'],
                'flight_patterns': 'soaring_thermal_riding'
            },
            'Acridotheres javanicus': {
                'common': 'Javan Myna', 
                'risk': 0.7,
                'flock_behavior': 'large_flocks',
                'territorial_calls': ['chatter', 'whistle', 'click'],
                'alarm_patterns': ['chorus_calling', 'synchronized_movement'],
                'flight_patterns': 'dense_group_formation'
            }
        }

        # System state
        self.is_running = False
        self.alert_callbacks = []
        self.communication_history = []

    def setup_ai_models(self):
        """Initialize multiple AI models for comprehensive analysis"""
        print("🤖 Loading AI models...")
        
        try:
            # 1. Audio classification model (Hugging Face)
            self.audio_classifier = pipeline(
                "audio-classification",
                model="MIT/ast-finetuned-audioset-10-10-0.4593",
                return_all_scores=True
            )
            
            # 2. Speech emotion recognition for communication context
            self.emotion_analyzer = pipeline(
                "audio-classification",
                model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
            )
            
            # 3. BirdNET for species identification
            self.birdnet_analyzer = Analyzer()
            
            print("✅ AI models loaded successfully")
            
        except Exception as e:
            print(f"⚠️  Warning: Some AI models failed to load: {e}")
            self.audio_classifier = None
            self.emotion_analyzer = None
            self.birdnet_analyzer = Analyzer()

    def extract_audio_features(self, audio_data, sample_rate=44100):
        """Extract comprehensive audio features for communication analysis"""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            audio_array = audio_array / 32768.0  # Normalize
            
            # Extract features using librosa
            features = {}
            
            # Spectral features
            features['mfcc'] = librosa.feature.mfcc(y=audio_array, sr=sample_rate, n_mfcc=13)
            features['spectral_centroid'] = librosa.feature.spectral_centroid(y=audio_array, sr=sample_rate)
            features['spectral_rolloff'] = librosa.feature.spectral_rolloff(y=audio_array, sr=sample_rate)
            features['zero_crossing_rate'] = librosa.feature.zero_crossing_rate(audio_array)
            features['chroma'] = librosa.feature.chroma_stft(y=audio_array, sr=sample_rate)
            
            # Rhythmic features
            features['tempo'], features['beat_frames'] = librosa.beat.beat_track(y=audio_array, sr=sample_rate)
            
            # Harmonic features
            features['harmonic'], features['percussive'] = librosa.effects.hpss(audio_array)
            
            # Frequency domain analysis
            stft = librosa.stft(audio_array)
            features['magnitude'] = np.abs(stft)
            features['phase'] = np.angle(stft)
            
            return features
            
        except Exception as e:
            print(f"❌ Error extracting features: {e}")
            return None

    def analyze_communication_patterns(self, audio_features, species_info):
        """Analyze communication patterns and decode behavioral context"""
        try:
            patterns = {
                'call_type': 'unknown',
                'emotional_state': 'neutral',
                'behavioral_context': 'normal',
                'urgency_level': 'low',
                'flock_communication': False,
                'territorial_behavior': False,
                'alarm_signal': False
            }
            
            if not audio_features:
                return patterns
            
            # Analyze spectral characteristics
            mfcc_mean = np.mean(audio_features['mfcc'], axis=1)
            spectral_centroid_mean = np.mean(audio_features['spectral_centroid'])
            
            # Determine call type based on spectral features
            if spectral_centroid_mean > 3000:
                patterns['call_type'] = 'high_frequency_alert'
                patterns['urgency_level'] = 'high'
            elif spectral_centroid_mean > 1500:
                patterns['call_type'] = 'territorial_call'
                patterns['territorial_behavior'] = True
            else:
                patterns['call_type'] = 'contact_call'
            
            # Analyze rhythmic patterns for flock communication
            tempo = audio_features.get('tempo', 0)
            if tempo > 150:
                patterns['flock_communication'] = True
                patterns['behavioral_context'] = 'group_coordination'
            
            # Check for alarm patterns
            zcr_variance = np.var(audio_features['zero_crossing_rate'])
            if zcr_variance > 0.01:
                patterns['alarm_signal'] = True
                patterns['emotional_state'] = 'alarmed'
                patterns['urgency_level'] = 'high'
            
            # Species-specific pattern analysis
            if species_info:
                species_data = self.HIGH_RISK_SPECIES.get(species_info.get('scientific', ''), {})
                alarm_patterns = species_data.get('alarm_patterns', [])
                
                if 'rapid_succession' in alarm_patterns and tempo > 180:
                    patterns['behavioral_context'] = 'immediate_threat_response'
                    patterns['urgency_level'] = 'critical'
                
                if 'pitch_variation' in alarm_patterns and zcr_variance > 0.015:
                    patterns['behavioral_context'] = 'predator_warning'
                    patterns['urgency_level'] = 'high'
            
            return patterns
            
        except Exception as e:
            print(f"❌ Error analyzing communication patterns: {e}")
            return patterns

    def predict_behavioral_intent(self, communication_patterns, historical_data):
        """Predict bird behavioral intent using AI analysis"""
        try:
            intent_scores = {
                'landing_approach': 0.0,
                'territory_defense': 0.0,
                'flock_gathering': 0.0,
                'predator_avoidance': 0.0,
                'normal_flight': 0.0
            }
            
            # Analyze current patterns
            if communication_patterns['alarm_signal']:
                intent_scores['predator_avoidance'] += 0.4
            
            if communication_patterns['territorial_behavior']:
                intent_scores['territory_defense'] += 0.3
            
            if communication_patterns['flock_communication']:
                intent_scores['flock_gathering'] += 0.4
            
            # Analyze historical context
            if len(historical_data) > 0:
                recent_patterns = historical_data[-5:]  # Last 5 detections
                
                # Check for pattern consistency
                alarm_frequency = sum(1 for p in recent_patterns if p.get('alarm_signal', False))
                if alarm_frequency > 2:
                    intent_scores['predator_avoidance'] += 0.3
                
                territorial_frequency = sum(1 for p in recent_patterns if p.get('territorial_behavior', False))
                if territorial_frequency > 1:
                    intent_scores['territory_defense'] += 0.2
            
            # Normalize scores
            total_score = sum(intent_scores.values())
            if total_score > 0:
                for key in intent_scores:
                    intent_scores[key] /= total_score
            else:
                intent_scores['normal_flight'] = 1.0
            
            # Determine primary intent
            primary_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[primary_intent]
            
            return {
                'primary_intent': primary_intent,
                'confidence': confidence,
                'all_scores': intent_scores
            }
            
        except Exception as e:
            print(f"❌ Error predicting behavioral intent: {e}")
            return {'primary_intent': 'unknown', 'confidence': 0.0, 'all_scores': {}}

    def calculate_enhanced_risk_score(self, species, confidence, communication_patterns, behavioral_intent):
        """Calculate enhanced risk score incorporating communication analysis"""
        base_risk = self.HIGH_RISK_SPECIES.get(species, {}).get('risk', 0.3)
        
        # Base score from species and confidence
        risk_score = base_risk * confidence
        
        # Communication pattern modifiers
        if communication_patterns['alarm_signal']:
            risk_score += 0.2
        
        if communication_patterns['urgency_level'] == 'critical':
            risk_score += 0.3
        elif communication_patterns['urgency_level'] == 'high':
            risk_score += 0.15
        
        if communication_patterns['flock_communication']:
            risk_score += 0.1  # Flocks are more dangerous
        
        # Behavioral intent modifiers
        intent_multipliers = {
            'landing_approach': 1.5,
            'territory_defense': 1.3,
            'flock_gathering': 1.2,
            'predator_avoidance': 0.8,  # Less likely to approach aircraft
            'normal_flight': 1.0
        }
        
        primary_intent = behavioral_intent.get('primary_intent', 'normal_flight')
        intent_confidence = behavioral_intent.get('confidence', 0.0)
        multiplier = intent_multipliers.get(primary_intent, 1.0)
        
        risk_score *= (1 + (multiplier - 1) * intent_confidence)
        
        return min(risk_score, 1.0)  # Cap at 1.0

    def analyze_audio_with_ai(self, audio_data):
        """Comprehensive AI analysis of audio data"""
        try:
            # Extract features
            audio_features = self.extract_audio_features(audio_data)
            
            # BirdNET species identification
            temp_file = f"temp_audio_{int(time.time())}.wav"
            
            # Save audio data
            with wave.open(temp_file, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(self.RATE)
                wf.writeframes(audio_data)
            
            # Analyze with BirdNET
            recording = Recording(
                self.birdnet_analyzer,
                temp_file,
                lat=3.1390,  # Johor Bahru
                lon=101.6869,
                min_conf=0.1
            )
            
            recording.analyze()
            
            alerts = []
            
            if recording.detections:
                for detection in recording.detections:
                    # Analyze communication patterns
                    species_info = {
                        'scientific': detection['scientific_name'],
                        'common': detection['common_name']
                    }
                    
                    communication_patterns = self.analyze_communication_patterns(
                        audio_features, species_info
                    )
                    
                    # Predict behavioral intent
                    behavioral_intent = self.predict_behavioral_intent(
                        communication_patterns, self.communication_history
                    )
                    
                    # Calculate enhanced risk score
                    risk_score = self.calculate_enhanced_risk_score(
                        detection['scientific_name'],
                        detection['confidence'],
                        communication_patterns,
                        behavioral_intent
                    )
                    
                    # Determine alert level with enhanced logic
                    if risk_score > 0.8:
                        alert_level = 'CRITICAL'
                        action = 'IMMEDIATE_RUNWAY_CLOSURE'
                    elif risk_score > 0.6:
                        alert_level = 'HIGH'
                        action = 'DELAY_TAKEOFF'
                    elif risk_score > 0.4:
                        alert_level = 'MEDIUM'
                        action = 'INCREASE_MONITORING'
                    else:
                        alert_level = 'LOW'
                        action = 'CONTINUE_NORMAL'
                    
                    # Create comprehensive alert
                    alert = {
                        'timestamp': datetime.now().isoformat(),
                        'species': species_info,
                        'confidence': detection['confidence'],
                        'risk_score': risk_score,
                        'alert_level': alert_level,
                        'recommended_action': action,
                        'communication_analysis': communication_patterns,
                        'behavioral_prediction': behavioral_intent,
                        'detection_time': {
                            'start': detection['start_time'],
                            'end': detection['end_time']
                        },
                        'ai_insights': {
                            'call_interpretation': self.interpret_call_meaning(communication_patterns),
                            'threat_assessment': self.assess_threat_level(communication_patterns, behavioral_intent),
                            'recommended_monitoring': self.get_monitoring_recommendations(behavioral_intent)
                        }
                    }
                    
                    # Store in communication history
                    self.communication_history.append(communication_patterns)
                    if len(self.communication_history) > 100:  # Keep last 100 patterns
                        self.communication_history = self.communication_history[-100:]
                    
                    alerts.append(alert)
                    
                    # Trigger callbacks
                    for callback in self.alert_callbacks:
                        callback(alert)
            
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return alerts
            
        except Exception as e:
            print(f"❌ Error in AI analysis: {e}")
            return []

    def interpret_call_meaning(self, communication_patterns):
        """Interpret the meaning of bird calls based on patterns"""
        interpretations = []
        
        if communication_patterns['alarm_signal']:
            interpretations.append("Alarm call - indicates perceived threat")
        
        if communication_patterns['territorial_behavior']:
            interpretations.append("Territorial call - defending area")
        
        if communication_patterns['flock_communication']:
            interpretations.append("Flock coordination - group movement")
        
        if communication_patterns['urgency_level'] == 'critical':
            interpretations.append("High urgency - immediate response needed")
        
        return interpretations if interpretations else ["Normal vocalization"]

    def assess_threat_level(self, communication_patterns, behavioral_intent):
        """Assess the threat level based on communication and behavior"""
        threat_factors = []
        
        if communication_patterns['alarm_signal']:
            threat_factors.append("Active alarm signals detected")
        
        if behavioral_intent['primary_intent'] == 'landing_approach':
            threat_factors.append("Potential landing approach behavior")
        
        if communication_patterns['flock_communication']:
            threat_factors.append("Flock coordination increases collision risk")
        
        if communication_patterns['urgency_level'] in ['high', 'critical']:
            threat_factors.append("High urgency vocalizations")
        
        return threat_factors if threat_factors else ["No significant threat indicators"]

    def get_monitoring_recommendations(self, behavioral_intent):
        """Get specific monitoring recommendations based on behavioral prediction"""
        recommendations = []
        
        primary_intent = behavioral_intent.get('primary_intent', 'unknown')
        confidence = behavioral_intent.get('confidence', 0.0)
        
        if primary_intent == 'landing_approach' and confidence > 0.5:
            recommendations.append("Increase visual monitoring of approach corridors")
            recommendations.append("Activate bird dispersal systems")
        
        elif primary_intent == 'flock_gathering' and confidence > 0.4:
            recommendations.append("Monitor for increasing flock size")
            recommendations.append("Prepare for potential mass movement")
        
        elif primary_intent == 'territory_defense' and confidence > 0.3:
            recommendations.append("Bird may remain in area - sustained monitoring needed")
        
        return recommendations if recommendations else ["Continue standard monitoring protocols"]

    def add_alert_callback(self, callback):
        """Add callback function for alerts"""
        self.alert_callbacks.append(callback)

    def start_monitoring(self):
        """Start real-time bird monitoring with AI analysis"""
        self.is_running = True
        
        p = pyaudio.PyAudio()
        
        try:
            stream = p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            print("🎤 Starting enhanced AI bird monitoring...")
            print("🧠 AI models ready for communication analysis...")
            print("🔍 Listening for bird sounds and analyzing behavior...")
            
            while self.is_running:
                # Record audio chunk
                frames = []
                for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                    data = stream.read(self.CHUNK)
                    frames.append(data)
                
                # Convert to audio data
                audio_data = b''.join(frames)
                
                # Analyze with AI
                alerts = self.analyze_audio_with_ai(audio_data)
                
                # Print results
                if alerts:
                    print(f"\n🚨 {len(alerts)} bird(s) detected with AI analysis!")
                    for alert in alerts:
                        print(f"   🐦 {alert['species']['common']}")
                        print(f"   📊 Risk: {alert['risk_score']:.2f} ({alert['alert_level']})")
                        print(f"   🧠 Behavior: {alert['behavioral_prediction']['primary_intent']}")
                        print(f"   💬 Communication: {alert['communication_analysis']['call_type']}")
                        print(f"   🎯 Action: {alert['recommended_action']}")
                        print(f"   💡 Insights: {', '.join(alert['ai_insights']['call_interpretation'])}")
                else:
                    print(".", end="", flush=True)
                
        except KeyboardInterrupt:
            print("\n⏹️  Stopping monitoring...")
        except Exception as e:
            print(f"❌ Error in monitoring: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_running = False


# Enhanced alert handler for CLI/demo use only
def enhanced_alert_handler(alert):
    """Handle enhanced bird strike alerts with AI insights"""
    print(f"\n🚨 ENHANCED BIRD STRIKE ALERT!")
    print(f"Species: {alert['species']['common']}")
    print(f"Risk Level: {alert['alert_level']} ({alert['risk_score']:.2f})")
    print(f"Predicted Behavior: {alert['behavioral_prediction']['primary_intent']}")
    print(f"Communication Type: {alert['communication_analysis']['call_type']}")
    print(f"Emotional State: {alert['communication_analysis']['emotional_state']}")
    print(f"Urgency Level: {alert['communication_analysis']['urgency_level']}")
    print(f"Action: {alert['recommended_action']}")
    print("\n🧠 AI Insights:")
    for insight in alert['ai_insights']['call_interpretation']:
        print(f"   • {insight}")
    print("\n🔍 Monitoring Recommendations:")
    for rec in alert['ai_insights']['recommended_monitoring']:
        print(f"   • {rec}")
    print("-" * 60)


def main():
    """Main function to run the enhanced system as CLI/demo"""
    print("🚀 Enhanced Bird Strike Warning System with AI Communication Analysis")
    print("🧠 Powered by Multiple AI Models for Behavior Prediction")
    print("=" * 80)
    
    # Initialize enhanced system
    warning_system = AdvancedBirdCommunicationAnalyzer()
    
    # Add enhanced alert handler
    warning_system.add_alert_callback(enhanced_alert_handler)
    
    # Start monitoring
    try:
        warning_system.start_monitoring()
    except KeyboardInterrupt:
        print("\n👋 Shutting down enhanced system...")
        warning_system.stop_monitoring()


if __name__ == "__main__":
    main()