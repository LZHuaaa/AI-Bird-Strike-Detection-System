#!/usr/bin/env python3
"""
Real-time Bird Strike Warning System using BirdNET
Captures audio from microphone and detects birds in real-time
"""

import pyaudio
import numpy as np
import wave
import threading
import time
import os
from datetime import datetime
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import json


class BirdStrikeWarningSystem:
    def __init__(self):
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.RECORD_SECONDS = 3  # Analyze every 3 seconds

        # Initialize BirdNET analyzer
        self.analyzer = Analyzer()

        # Malaysian airport high-risk species
        self.HIGH_RISK_SPECIES = {
            'Corvus splendens': {'common': 'House Crow', 'risk': 0.9},
            'Corvus macrorhynchos': {'common': 'Large-billed Crow', 'risk': 0.8},
            'Haliaeetus leucogaster': {'common': 'White-bellied Sea Eagle', 'risk': 0.95},
            'Acridotheres javanicus': {'common': 'Javan Myna', 'risk': 0.7},
            'Eudynamys scolopaceus': {'common': 'Asian Koel', 'risk': 0.6},
            'Hirundo rustica': {'common': 'Barn Swallow', 'risk': 0.5}
        }

        # System state
        self.is_running = False
        self.alert_callbacks = []

    def add_alert_callback(self, callback):
        """Add callback function for alerts"""
        self.alert_callbacks.append(callback)

    def calculate_risk_score(self, species, confidence):
        """Calculate risk score for detected bird"""
        base_risk = self.HIGH_RISK_SPECIES.get(species, {}).get('risk', 0.3)
        return base_risk * confidence

    def process_detection(self, detection):
        """Process bird detection and generate alerts"""
        species = detection['scientific_name']
        confidence = detection['confidence']

        # Calculate risk
        risk_score = self.calculate_risk_score(species, confidence)

        # Determine alert level
        if risk_score > 0.7:
            alert_level = 'HIGH'
            action = 'DELAY_TAKEOFF'
        elif risk_score > 0.5:
            alert_level = 'MEDIUM'
            action = 'INCREASE_MONITORING'
        else:
            alert_level = 'LOW'
            action = 'CONTINUE_NORMAL'

        # Create alert object
        alert = {
            'timestamp': datetime.now().isoformat(),
            'species': {
                'scientific': species,
                'common': detection['common_name']
            },
            'confidence': confidence,
            'risk_score': risk_score,
            'alert_level': alert_level,
            'recommended_action': action,
            'detection_time': {
                'start': detection['start_time'],
                'end': detection['end_time']
            }
        }

        # Trigger callbacks
        for callback in self.alert_callbacks:
            callback(alert)

        return alert

    def analyze_audio_chunk(self, audio_data):
        """Analyze audio chunk with BirdNET"""
        # Save audio chunk to temporary file
        temp_file = f"temp_audio_{int(time.time())}.wav"

        try:
            # Save audio data
            with wave.open(temp_file, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.RATE)
                wf.writeframes(audio_data)

            # Analyze with BirdNET - removed the 'week' parameter
            recording = Recording(
                self.analyzer,
                temp_file,
                lat=3.1390,  # Johor Bahru
                lon=101.6869,  # Johor Bahru
                min_conf=0.1  # Minimum confidence
            )

            recording.analyze()

            # Process detections
            alerts = []
            if recording.detections:
                for detection in recording.detections:
                    alert = self.process_detection(detection)
                    alerts.append(alert)

            return alerts

        except Exception as e:
            print(f"❌ Error analyzing audio: {e}")
            return []

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def start_monitoring(self):
        """Start real-time bird monitoring"""
        self.is_running = True

        # Initialize PyAudio
        p = pyaudio.PyAudio()

        try:
            # Open audio stream
            stream = p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )

            print("🎤 Starting real-time bird monitoring...")
            print("🔍 Listening for bird sounds...")

            while self.is_running:
                # Record audio chunk
                frames = []
                for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                    data = stream.read(self.CHUNK)
                    frames.append(data)

                # Convert to audio data
                audio_data = b''.join(frames)

                # Analyze audio
                alerts = self.analyze_audio_chunk(audio_data)

                # Print detection results
                if alerts:
                    print(f"\n🚨 {len(alerts)} bird(s) detected!")
                    for alert in alerts:
                        print(f"   🐦 {alert['species']['common']}")
                        print(f"   📊 Risk: {alert['risk_score']:.2f} ({alert['alert_level']})")
                        print(f"   🎯 Action: {alert['recommended_action']}")
                else:
                    print(".", end="", flush=True)  # Progress indicator

        except KeyboardInterrupt:
            print("\n⏹️  Stopping monitoring...")

        except Exception as e:
            print(f"❌ Error in monitoring: {e}")

        finally:
            # Clean up
            stream.stop_stream()
            stream.close()
            p.terminate()

    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_running = False


# Example usage and testing
def alert_handler(alert):
    """Handle bird strike alerts"""
    print(f"\n🚨 BIRD STRIKE ALERT!")
    print(f"Species: {alert['species']['common']}")
    print(f"Risk Level: {alert['alert_level']}")
    print(f"Action: {alert['recommended_action']}")
    print("-" * 40)


def main():
    """Main function to run the system"""
    print("🚀 Bird Strike Warning System")
    print("=" * 50)

    # Initialize system
    warning_system = BirdStrikeWarningSystem()

    # Add alert handler
    warning_system.add_alert_callback(alert_handler)

    # Start monitoring
    try:
        warning_system.start_monitoring()
    except KeyboardInterrupt:
        print("\n👋 Shutting down system...")
        warning_system.stop_monitoring()


if __name__ == "__main__":
    main()