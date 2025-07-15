#!/usr/bin/env python3
"""
Enhanced Bird Strike Warning System with AI Communication Analysis and Audio Serving
Uses multiple AI models for bird detection, communication analysis, and behavioral prediction
Includes audio segment saving and serving capabilities for frontend playback
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
import uuid
from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import threading
import shutil
from pathlib import Path
import base64
warnings.filterwarnings('ignore')
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedBirdCommunicationAnalyzer:
    def __init__(self):
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.RECORD_SECONDS = 3

        # Audio storage settings
        self.AUDIO_STORAGE_DIR = "detected_audio_segments"
        self.MAX_STORED_SEGMENTS = 100  # Maximum number of segments to store
        self.setup_audio_storage()

        # Initialize multiple AI models
        self.setup_ai_models()
        
        # Communication patterns database
        self.communication_patterns = {}
        self.behavioral_contexts = {}
        
        # Predator sound tracking
        self.predator_sounds = None  # Will be set by strategic system
        self.is_predator_playing = False
        self.predator_play_start = None
        self.predator_play_duration = 0
        
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
        self.stored_segments = []  # Track stored audio segments

    def setup_audio_storage(self):
        """Setup audio storage directory and management"""
        try:
            Path(self.AUDIO_STORAGE_DIR).mkdir(parents=True, exist_ok=True)
            print(f"📁 Audio storage directory created: {self.AUDIO_STORAGE_DIR}")
        except Exception as e:
            print(f"❌ Error setting up audio storage: {e}")

    def cleanup_old_segments(self):
        """Clean up old audio segments to maintain storage limits"""
        try:
            if len(self.stored_segments) > self.MAX_STORED_SEGMENTS:
                # Remove oldest segments
                segments_to_remove = self.stored_segments[:-self.MAX_STORED_SEGMENTS]
                for segment in segments_to_remove:
                    file_path = segment.get('file_path')
                    if file_path and os.path.exists(file_path):
                        os.remove(file_path)
                
                # Update stored segments list
                self.stored_segments = self.stored_segments[-self.MAX_STORED_SEGMENTS:]
                print(f"🧹 Cleaned up {len(segments_to_remove)} old audio segments")
        except Exception as e:
            print(f"❌ Error cleaning up segments: {e}")

    def save_audio_segment(self, audio_data, detection_info):
        """Save audio segment with detection metadata"""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            segment_id = str(uuid.uuid4())[:8]
            filename = f"bird_detection_{timestamp}_{segment_id}.wav"
            file_path = os.path.join(self.AUDIO_STORAGE_DIR, filename)
            
            # Save audio file
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(self.RATE)
                wf.writeframes(audio_data)
            
            # Create segment metadata
            segment_metadata = {
                'segment_id': segment_id,
                'filename': filename,
                'file_path': file_path,
                'timestamp': datetime.now().isoformat(),
                'detection_info': detection_info,
                'file_size': os.path.getsize(file_path),
                'duration': self.RECORD_SECONDS,
                'sample_rate': self.RATE,
                'channels': self.CHANNELS
            }
            
            # Add to stored segments
            self.stored_segments.append(segment_metadata)
            
            # Cleanup old segments if needed
            self.cleanup_old_segments()
            
            print(f"💾 Audio segment saved: {filename}")
            return segment_metadata
            
        except Exception as e:
            print(f"❌ Error saving audio segment: {e}")
            return None

    def get_audio_segment_info(self, segment_id):
        """Get metadata for a specific audio segment"""
        for segment in self.stored_segments:
            if segment['segment_id'] == segment_id:
                return segment
        return None

    def get_all_segments(self):
        """Get all stored audio segments metadata"""
        return self.stored_segments

    def delete_audio_segment(self, segment_id):
        """Delete a specific audio segment"""
        try:
            segment = self.get_audio_segment_info(segment_id)
            if segment:
                file_path = segment['file_path']
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # Remove from stored segments
                self.stored_segments = [s for s in self.stored_segments if s['segment_id'] != segment_id]
                return True
            return False
        except Exception as e:
            print(f"❌ Error deleting audio segment: {e}")
            return False

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
            # Skip analysis if predator sound is playing
            if self.is_predator_sound_active():
                logger.debug("Skipping audio analysis - predator sound is playing")
                return []

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
                # Save audio segment with detection info
                detection_summary = {
                    'total_detections': len(recording.detections),
                    'species_detected': [d['common_name'] for d in recording.detections],
                    'max_confidence': max(d['confidence'] for d in recording.detections),
                    'analysis_timestamp': datetime.now().isoformat()
                }
                
                segment_metadata = self.save_audio_segment(audio_data, detection_summary)
                
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
                        'audio_segment': segment_metadata,  # Include audio segment info
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
            print("💾 Audio segments will be saved for playback...")
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
                        if alert['audio_segment']:
                            print(f"   🎵 Audio saved: {alert['audio_segment']['filename']}")
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

    def set_predator_sounds(self, predator_sounds):
        """Set reference to predator sounds system"""
        self.predator_sounds = predator_sounds

    def update_predator_status(self, is_playing: bool, duration: float = 0):
        """Update predator sound playback status"""
        self.is_predator_playing = is_playing
        if is_playing:
            self.predator_play_start = time.time()
            self.predator_play_duration = duration
        else:
            self.predator_play_start = None
            self.predator_play_duration = 0

    def is_predator_sound_active(self) -> bool:
        """Check if predator sound is currently playing"""
        if not self.is_predator_playing or not self.predator_play_start:
            return False
        
        if self.predator_play_duration > 0:
            elapsed = time.time() - self.predator_play_start
            return elapsed < self.predator_play_duration
        
        return False


# Flask API for serving audio segments
app = Flask(__name__)
CORS(app)

# Global reference to the warning system
warning_system = None

@app.route('/api/audio-segments', methods=['GET'])
def get_audio_segments():
    """Get all stored audio segments metadata"""
    try:
        segments = warning_system.get_all_segments()
        return jsonify({
            'success': True,
            'segments': segments,
            'total_count': len(segments)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/audio-segment/<segment_id>', methods=['GET'])
def get_audio_segment(segment_id):
    """Get specific audio segment metadata"""
    try:
        segment = warning_system.get_audio_segment_info(segment_id)
        if segment:
            return jsonify({
                'success': True,
                'segment': segment
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Segment not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/audio-segment/<segment_id>/play', methods=['GET'])
def play_audio_segment(segment_id):
    """Serve audio file for playback"""
    try:
        segment = warning_system.get_audio_segment_info(segment_id)
        if segment and os.path.exists(segment['file_path']):
            return send_file(
                segment['file_path'],
                mimetype='audio/wav',
                as_attachment=False,
                download_name=segment['filename']
            )
        else:
            return jsonify({
                'success': False,
                'error': 'Audio file not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/audio-segment/<segment_id>/download', methods=['GET'])
def download_audio_segment(segment_id):
    """Download audio file"""
    try:
        segment = warning_system.get_audio_segment_info(segment_id)
        if segment and os.path.exists(segment['file_path']):
            return send_file(
                segment['file_path'],
                mimetype='audio/wav',
                as_attachment=True,
                download_name=segment['filename']
            )
        else:
            return jsonify({
                'success': False,
                'error': 'Audio file not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/audio-segment/<segment_id>', methods=['DELETE'])
def delete_audio_segment(segment_id):
    """Delete specific audio segment"""
    try:
        success = warning_system.delete_audio_segment(segment_id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Segment deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Segment not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/audio-segment/<segment_id>/base64', methods=['GET'])
def get_audio_segment_base64(segment_id):
    """Get audio segment as base64 encoded string"""
    try:
        segment = warning_system.get_audio_segment_info(segment_id)
        if segment and os.path.exists(segment['file_path']):
            with open(segment['file_path'], 'rb') as audio_file:
                audio_data = audio_file.read()
                base64_audio = base64.b64encode(audio_data).decode('utf-8')
                
            return jsonify({
                'success': True,
                'audio_base64': base64_audio,
                'segment_info': segment
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Audio file not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """Get system status"""
    return jsonify({
        'success': True,
        'status': 'running' if warning_system.is_running else 'stopped',
        'stored_segments': len(warning_system.stored_segments),
        'storage_directory': warning_system.AUDIO_STORAGE_DIR
    })

def start_flask_server():
    """Start Flask server in a separate thread"""
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)


# Enhanced alert handler with audio segment info
def enhanced_alert_handler(alert):
    """Handle enhanced bird strike alerts with AI insights and audio info"""
    print(f"\n🚨 ENHANCED BIRD STRIKE ALERT!")
    print(f"Species: {alert['species']['common']}")
    print(f"Risk Level: {alert['alert_level']} ({alert['risk_score']:.2f})")
    print(f"Predicted Behavior: {alert['behavioral_prediction']['primary_intent']}")
    print(f"Communication Type: {alert['communication_analysis']['call_type']}")
    print(f"Emotional State: {alert['communication_analysis']['emotional_state']}")
    print(f"Urgency Level: {alert['communication_analysis']['urgency_level']}")
    print(f"Action: {alert['recommended_action']}")
    
    # Audio segment info
    if alert['audio_segment']:
        print(f"🎵 Audio Segment: {alert['audio_segment']['filename']}")
        print(f"   • Segment ID: {alert['audio_segment']['segment_id']}")
        print(f"   • Duration: {alert['audio_segment']['duration']}s")
        print(f"   • File Size: {alert['audio_segment']['file_size']} bytes")
        print(f"   • Playback URL: http://localhost:5000/api/audio-segment/{alert['audio_segment']['segment_id']}/play")
    
    print("\n🧠 AI Insights:")
    for insight in alert['ai_insights']['call_interpretation']:
        print(f"   • {insight}")
    print("\n🔍 Monitoring Recommendations:")
    for rec in alert['ai_insights']['recommended_monitoring']:
        print(f"   • {rec}")
    print("-" * 60)


def main():
    """Main function to run the enhanced system with audio serving"""
    global warning_system
    
    print("🚀 Enhanced Bird Strike Warning System with AI Communication Analysis")
    print("🧠 Powered by Multiple AI Models for Behavior Prediction")
    print("🎵 Audio Segment Saving and Serving Enabled")
    print("🌐 API Server for Frontend Integration")
    print("=" * 80)
    
    # Initialize enhanced system
    warning_system = AdvancedBirdCommunicationAnalyzer()
    
    # Add enhanced alert handler
    warning_system.add_alert_callback(enhanced_alert_handler)
    
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=start_flask_server, daemon=True)
    flask_thread.start()
    
    print("🌐 API Server started on http://localhost:5000")
    print("\n📋 Available API Endpoints:")
    print("   • GET  /api/audio-segments - Get all stored segments")
    print("   • GET  /api/audio-segment/<id> - Get segment metadata")
    print("   • GET  /api/audio-segment/<id>/play - Play audio segment")
    print("   • GET  /api/audio-segment/<id>/download - Download audio file")
    print("   • GET  /api/audio-segment/<id>/base64 - Get base64 encoded audio")
    print("   • DELETE /api/audio-segment/<id> - Delete audio segment")
    print("   • GET  /api/status - Get system status")
    print("\n🎵 Audio segments will be stored in:", warning_system.AUDIO_STORAGE_DIR)
    
    # Start monitoring
    try:
        warning_system.start_monitoring()
    except KeyboardInterrupt:
        print("\n👋 Shutting down enhanced system...")
        warning_system.stop_monitoring()


if __name__ == "__main__":
    main()