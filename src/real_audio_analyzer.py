"""
Real Audio Analyzer using librosa for pitch detection
Simplified version without TensorFlow dependency (basic-pitch removed for Python 3.11 compatibility)
"""
import logging
import os
from typing import Dict, List, Any, Tuple
import numpy as np
import librosa
import soundfile as sf
import noisereduce as nr
import pretty_midi
import mido

logger = logging.getLogger(__name__)


class RealAudioAnalyzer:
    """Real audio analyzer using librosa for transcription (no TensorFlow dependency)"""
    
    def __init__(self):
        self.logger = logger
        self.sample_rate = 22050
        self.logger.info("Real Audio Analyzer initialized with librosa (TensorFlow-free)")
    
    def analyze(
        self,
        audio_path: str,
        instrument: str = 'piano',
        apply_noise_reduction: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze audio file using librosa for pitch detection
        
        Args:
            audio_path: Path to audio file
            instrument: Instrument type
            apply_noise_reduction: Apply noise reduction
            
        Returns:
            Comprehensive analysis with pitch detection
        """
        try:
            self.logger.info(f"Analyzing audio with librosa: {audio_path}")
            
            # Load and preprocess audio
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Apply noise reduction if requested
            if apply_noise_reduction:
                audio = self._reduce_noise(audio, sr)
            
            # Extract notes using librosa pitch detection
            notes = self._extract_notes_librosa(audio, sr)
            
            # Calculate tempo
            tempo = self._calculate_tempo_librosa(audio, sr)
            
            # Analyze dynamics
            dynamics = self._analyze_dynamics(audio, sr)
            
            # Analyze rhythm
            rhythm = self._analyze_rhythm(notes)
            
            # Calculate pitch range
            pitch_range = self._calculate_pitch_range(notes)
            
            # Analyze articulation
            articulation = self._analyze_articulation(notes)
            
            analysis = {
                'notes': notes,
                'tempo': tempo,
                'dynamics': dynamics,
                'rhythm': rhythm,
                'pitch_range': pitch_range,
                'articulation': articulation,
                'duration': len(audio) / sr,
                'instrument': instrument,
                'transcription_method': 'librosa pitch detection',
                'total_notes': len(notes),
                'sample_rate': sr,
                'has_real_transcription': True
            }
            
            self.logger.info(f"Analysis complete: {len(notes)} notes detected")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in audio analysis: {str(e)}")
            raise
    
    def _extract_notes_librosa(self, audio: np.ndarray, sr: int) -> List[Dict[str, Any]]:
        """Extract notes using librosa's pitch detection"""
        try:
            # Use librosa's piptrack for pitch detection
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
            
            # Get onset times
            onset_frames = librosa.onset.onset_detect(y=audio, sr=sr, units='frames')
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)
            
            notes = []
            for i, onset_time in enumerate(onset_times):
                # Get the frame index
                frame_idx = onset_frames[i]
                
                # Get pitch at this frame
                pitch_idx = magnitudes[:, frame_idx].argmax()
                pitch_hz = pitches[pitch_idx, frame_idx]
                
                if pitch_hz > 0:  # Valid pitch detected
                    # Convert Hz to MIDI note
                    midi_note = librosa.hz_to_midi(pitch_hz)
                    
                    # Estimate duration (time to next onset or end)
                    if i < len(onset_times) - 1:
                        duration = onset_times[i + 1] - onset_time
                    else:
                        duration = len(audio) / sr - onset_time
                    
                    # Estimate velocity from magnitude
                    velocity = int(np.clip(magnitudes[pitch_idx, frame_idx] * 127, 0, 127))
                    
                    notes.append({
                        'pitch': int(round(midi_note)),
                        'start': float(onset_time),
                        'end': float(onset_time + duration),
                        'duration': float(duration),
                        'velocity': velocity,
                        'frequency': float(pitch_hz)
                    })
            
            return notes
            
        except Exception as e:
            self.logger.warning(f"Error in note extraction: {str(e)}, returning empty note list")
            return []
    
    def _calculate_tempo_librosa(self, audio: np.ndarray, sr: int) -> float:
        """Calculate tempo using librosa"""
        try:
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
            return float(tempo)
        except:
            return 120.0  # Default tempo    
    def _reduce_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply noise reduction"""
        try:
            return nr.reduce_noise(y=audio, sr=sr)
        except:
            return audio
    
    def _analyze_dynamics(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analyze dynamics from audio"""
        rms = librosa.feature.rms(y=audio)[0]
        return {
            'average': float(np.mean(rms)),
            'min': float(np.min(rms)),
            'max': float(np.max(rms)),
            'variation': float(np.std(rms))
        }
    
    def _analyze_rhythm(self, notes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze rhythm patterns"""
        if not notes:
            return {'regularity': 0.0, 'pattern': 'unknown'}
        
        durations = [n['duration'] for n in notes]
        return {
            'regularity': float(1.0 - np.std(durations) / (np.mean(durations) + 0.001)),
            'average_duration': float(np.mean(durations)),
            'pattern': 'detected'
        }
    
    def _calculate_pitch_range(self, notes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate pitch range"""
        if not notes:
            return {'min': 0, 'max': 0, 'range': 0}
        
        pitches = [n['pitch'] for n in notes]
        return {
            'min': int(min(pitches)),
            'max': int(max(pitches)),
            'range': int(max(pitches) - min(pitches))
        }
    
    def _analyze_articulation(self, notes: List[Dict[str, Any]]) -> Dict[str, str]:
        """Analyze articulation"""
        if not notes:
            return {'style': 'unknown'}
        
        avg_duration = np.mean([n['duration'] for n in notes])
        
        if avg_duration < 0.3:
            style = 'staccato'
        elif avg_duration > 1.0:
            style = 'legato'
        else:
            style = 'normal'
        
        return {'style': style, 'average_note_length': float(avg_duration)}