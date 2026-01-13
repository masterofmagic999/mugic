"""
Audio Analyzer - Analyzes recorded audio performance with noise reduction
"""
import logging
import numpy as np
import librosa
import soundfile as sf
import noisereduce as nr
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """Analyzes recorded audio and extracts musical features"""
    
    def __init__(self):
        """Initialize the audio analyzer"""
        self.logger = logger
        self.sample_rate = 22050  # Standard sample rate for music analysis
    
    def analyze(
        self,
        audio_path: str,
        instrument: str = 'piano',
        apply_noise_reduction: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze an audio recording
        
        Args:
            audio_path: Path to the audio file
            instrument: Type of instrument being played
            apply_noise_reduction: Whether to apply noise reduction
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            self.logger.info(f"Starting audio analysis of {audio_path}")
            
            # Load audio file
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Apply noise reduction if requested
            if apply_noise_reduction:
                audio = self._reduce_noise(audio, sr)
            
            # Extract musical features
            pitches = self._extract_pitches(audio, sr)
            onsets = self._detect_note_onsets(audio, sr)
            tempo = self._estimate_tempo(audio, sr)
            dynamics = self._analyze_dynamics(audio, sr)
            rhythm = self._analyze_rhythm(audio, sr, onsets)
            
            # Match notes with instrument characteristics
            notes = self._extract_notes(audio, sr, pitches, onsets, instrument)
            
            analysis = {
                'notes': notes,
                'tempo': tempo,
                'dynamics': dynamics,
                'rhythm': rhythm,
                'pitches': pitches,
                'onsets': onsets,
                'duration': len(audio) / sr,
                'instrument': instrument
            }
            
            self.logger.info(f"Audio analysis complete: {len(notes)} notes detected")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing audio: {str(e)}")
            raise
    
    def _reduce_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply noise reduction to audio signal"""
        try:
            # Use stationary noise reduction
            # Estimate noise from the first 0.5 seconds (assuming silence or ambient noise)
            reduced_audio = nr.reduce_noise(
                y=audio,
                sr=sr,
                stationary=True,
                prop_decrease=0.8
            )
            
            self.logger.info("Noise reduction applied successfully")
            return reduced_audio
            
        except Exception as e:
            self.logger.warning(f"Error during noise reduction: {str(e)}, using original audio")
            return audio
    
    def _extract_pitches(self, audio: np.ndarray, sr: int) -> List[Dict]:
        """Extract pitch information from audio"""
        # Use pYIN algorithm for pitch tracking
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'),
            sr=sr
        )
        
        pitches = []
        hop_length = 512
        times = librosa.frames_to_time(range(len(f0)), sr=sr, hop_length=hop_length)
        
        for i, (time, freq, voiced, prob) in enumerate(zip(times, f0, voiced_flag, voiced_probs)):
            if voiced and not np.isnan(freq) and prob > 0.5:
                # Convert frequency to note name
                note = librosa.hz_to_note(freq)
                pitches.append({
                    'time': float(time),
                    'frequency': float(freq),
                    'note': note,
                    'confidence': float(prob)
                })
        
        return pitches
    
    def _detect_note_onsets(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Detect note onset times"""
        # Detect onsets using spectral flux
        onset_frames = librosa.onset.onset_detect(
            y=audio,
            sr=sr,
            units='frames',
            backtrack=True
        )
        
        # Convert frames to time
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        
        return onset_times
    
    def _estimate_tempo(self, audio: np.ndarray, sr: int) -> float:
        """Estimate the tempo of the performance"""
        tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
        return float(tempo)
    
    def _analyze_dynamics(self, audio: np.ndarray, sr: int) -> List[Dict]:
        """Analyze dynamic levels (volume) over time"""
        # Calculate RMS energy
        rms = librosa.feature.rms(y=audio)[0]
        
        # Convert to dB scale
        rms_db = librosa.amplitude_to_db(rms, ref=np.max)
        
        hop_length = 512
        times = librosa.frames_to_time(range(len(rms)), sr=sr, hop_length=hop_length)
        
        dynamics = []
        for time, db in zip(times, rms_db):
            # Classify dynamic level
            if db > -10:
                level = 'ff'  # fortissimo
            elif db > -20:
                level = 'f'   # forte
            elif db > -30:
                level = 'mf'  # mezzo-forte
            elif db > -40:
                level = 'mp'  # mezzo-piano
            elif db > -50:
                level = 'p'   # piano
            else:
                level = 'pp'  # pianissimo
            
            dynamics.append({
                'time': float(time),
                'db': float(db),
                'level': level
            })
        
        return dynamics
    
    def _analyze_rhythm(
        self,
        audio: np.ndarray,
        sr: int,
        onsets: np.ndarray
    ) -> Dict[str, Any]:
        """Analyze rhythmic accuracy"""
        if len(onsets) < 2:
            return {'inter_onset_intervals': [], 'mean_ioi': 0, 'std_ioi': 0}
        
        # Calculate inter-onset intervals
        iois = np.diff(onsets)
        
        return {
            'inter_onset_intervals': iois.tolist(),
            'mean_ioi': float(np.mean(iois)),
            'std_ioi': float(np.std(iois)),
            'num_notes': len(onsets)
        }
    
    def _extract_notes(
        self,
        audio: np.ndarray,
        sr: int,
        pitches: List[Dict],
        onsets: np.ndarray,
        instrument: str
    ) -> List[Dict]:
        """Extract individual notes from audio"""
        notes = []
        
        if len(onsets) == 0:
            return notes
        
        # For each onset, find the most common pitch in a window
        for i, onset_time in enumerate(onsets):
            # Define window (from onset to next onset or end)
            window_start = onset_time
            window_end = onsets[i + 1] if i + 1 < len(onsets) else len(audio) / sr
            
            # Find pitches in this window
            window_pitches = [
                p for p in pitches
                if window_start <= p['time'] < window_end
            ]
            
            if window_pitches:
                # Take the most confident pitch or median pitch
                window_pitches.sort(key=lambda x: x['confidence'], reverse=True)
                main_pitch = window_pitches[0]
                
                notes.append({
                    'start_time': float(onset_time),
                    'duration': float(window_end - window_start),
                    'pitch': main_pitch['note'],
                    'frequency': main_pitch['frequency'],
                    'confidence': main_pitch['confidence']
                })
        
        return notes
