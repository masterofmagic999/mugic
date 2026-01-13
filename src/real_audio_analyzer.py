"""
Real Audio Analyzer using Spotify's basic-pitch
No simulations - actual audio-to-MIDI transcription and analysis
"""
import logging
import os
from typing import Dict, List, Any, Tuple
import numpy as np
import librosa
import soundfile as sf
import noisereduce as nr

try:
    from basic_pitch.inference import predict
    from basic_pitch import ICASSP_2022_MODEL_PATH
    BASIC_PITCH_AVAILABLE = True
except ImportError:
    BASIC_PITCH_AVAILABLE = False

import pretty_midi
import mido

logger = logging.getLogger(__name__)


class RealAudioAnalyzer:
    """Real audio analyzer using Spotify's basic-pitch for transcription"""
    
    def __init__(self):
        self.logger = logger
        self.sample_rate = 22050
        
        if not BASIC_PITCH_AVAILABLE:
            raise ImportError("basic-pitch is required. Install with: pip install basic-pitch==0.2.5")
        
        self.logger.info("Real Audio Analyzer initialized with Spotify's basic-pitch")
    
    def analyze(
        self,
        audio_path: str,
        instrument: str = 'piano',
        apply_noise_reduction: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze audio file using Spotify's basic-pitch
        
        Args:
            audio_path: Path to audio file
            instrument: Instrument type
            apply_noise_reduction: Apply noise reduction
            
        Returns:
            Comprehensive analysis with real transcription
        """
        try:
            self.logger.info(f"Analyzing audio with basic-pitch: {audio_path}")
            
            # Load and preprocess audio
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Apply noise reduction if requested
            if apply_noise_reduction:
                audio = self._reduce_noise(audio, sr)
            
            # Save preprocessed audio temporarily
            temp_audio_path = audio_path + "_preprocessed.wav"
            sf.write(temp_audio_path, audio, sr)
            
            # Run basic-pitch transcription
            self.logger.info("Running Spotify basic-pitch transcription...")
            model_output, midi_data, note_events = predict(
                temp_audio_path,
                ICASSP_2022_MODEL_PATH
            )
            
            # Clean up temp file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            
            # Extract notes from MIDI data
            notes = self._extract_notes_from_midi(midi_data)
            
            # Calculate tempo from note onsets
            tempo = self._calculate_tempo(notes)
            
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
                'transcription_method': 'Spotify basic-pitch',
                'total_notes': len(notes),
                'sample_rate': sr,
                'has_real_transcription': True
            }
            
            self.logger.info(f"Analysis complete: {len(notes)} notes transcribed")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in audio analysis: {str(e)}")
            raise
    
    def _reduce_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply noise reduction"""
        try:
            # Stationary noise reduction
            audio_reduced = nr.reduce_noise(
                y=audio,
                sr=sr,
                stationary=True,
                prop_decrease=0.8
            )
            
            self.logger.info("Noise reduction applied")
            return audio_reduced
            
        except Exception as e:
            self.logger.warning(f"Noise reduction failed: {e}")
            return audio
    
    def _extract_notes_from_midi(self, midi_data: pretty_midi.PrettyMIDI) -> List[Dict]:
        """Extract notes from MIDI data"""
        notes = []
        
        for instrument in midi_data.instruments:
            for note in instrument.notes:
                notes.append({
                    'pitch': librosa.midi_to_note(note.pitch),
                    'midi_note': note.pitch,
                    'start_time': float(note.start),
                    'end_time': float(note.end),
                    'duration': float(note.end - note.start),
                    'velocity': note.velocity,
                    'frequency': librosa.midi_to_hz(note.pitch)
                })
        
        # Sort by start time
        notes.sort(key=lambda x: x['start_time'])
        
        return notes
    
    def _calculate_tempo(self, notes: List[Dict]) -> float:
        """Calculate tempo from note onsets"""
        if len(notes) < 2:
            return 120.0
        
        # Calculate inter-onset intervals
        onsets = [n['start_time'] for n in notes]
        intervals = np.diff(onsets)
        
        # Filter out very short intervals (likely grace notes)
        intervals = intervals[intervals > 0.1]
        
        if len(intervals) == 0:
            return 120.0
        
        # Calculate median interval
        median_interval = np.median(intervals)
        
        # Convert to BPM (assuming quarter notes)
        tempo = 60.0 / median_interval
        
        # Clamp to reasonable range
        tempo = max(40.0, min(240.0, tempo))
        
        return float(tempo)
    
    def _analyze_dynamics(self, audio: np.ndarray, sr: int) -> List[Dict]:
        """Analyze dynamic levels over time"""
        # Calculate RMS energy in windows
        hop_length = 512
        frame_length = 2048
        
        rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
        rms_db = librosa.amplitude_to_db(rms, ref=np.max)
        
        times = librosa.frames_to_time(range(len(rms)), sr=sr, hop_length=hop_length)
        
        dynamics = []
        for time, db in zip(times, rms_db):
            # Classify dynamic level
            if db > -10:
                level = 'ff'
            elif db > -20:
                level = 'f'
            elif db > -30:
                level = 'mf'
            elif db > -40:
                level = 'mp'
            elif db > -50:
                level = 'p'
            else:
                level = 'pp'
            
            dynamics.append({
                'time': float(time),
                'db': float(db),
                'level': level
            })
        
        return dynamics
    
    def _analyze_rhythm(self, notes: List[Dict]) -> Dict[str, Any]:
        """Analyze rhythm patterns from transcribed notes"""
        if len(notes) < 2:
            return {
                'inter_onset_intervals': [],
                'mean_ioi': 0,
                'std_ioi': 0,
                'rhythm_consistency': 0
            }
        
        # Get inter-onset intervals
        onsets = [n['start_time'] for n in notes]
        iois = np.diff(onsets)
        
        # Calculate consistency
        if len(iois) > 0:
            mean_ioi = float(np.mean(iois))
            std_ioi = float(np.std(iois))
            consistency = max(0, 1.0 - (std_ioi / (mean_ioi + 1e-6)))
        else:
            mean_ioi = 0
            std_ioi = 0
            consistency = 0
        
        return {
            'inter_onset_intervals': iois.tolist(),
            'mean_ioi': mean_ioi,
            'std_ioi': std_ioi,
            'rhythm_consistency': float(consistency),
            'num_notes': len(notes)
        }
    
    def _calculate_pitch_range(self, notes: List[Dict]) -> Dict[str, Any]:
        """Calculate pitch range from transcribed notes"""
        if not notes:
            return {
                'lowest': 'N/A',
                'highest': 'N/A',
                'range_semitones': 0
            }
        
        midi_notes = [n['midi_note'] for n in notes]
        lowest_midi = min(midi_notes)
        highest_midi = max(midi_notes)
        
        return {
            'lowest': librosa.midi_to_note(lowest_midi),
            'highest': librosa.midi_to_note(highest_midi),
            'range_semitones': highest_midi - lowest_midi,
            'lowest_midi': lowest_midi,
            'highest_midi': highest_midi
        }
    
    def _analyze_articulation(self, notes: List[Dict]) -> Dict[str, Any]:
        """Analyze articulation from note durations"""
        if not notes:
            return {'type': 'unknown', 'average_duration': 0}
        
        durations = [n['duration'] for n in notes]
        avg_duration = np.mean(durations)
        
        # Classify articulation
        if avg_duration < 0.15:
            articulation_type = 'staccato'
        elif avg_duration > 0.5:
            articulation_type = 'legato'
        else:
            articulation_type = 'normal'
        
        # Calculate gaps between notes
        gaps = []
        for i in range(len(notes) - 1):
            gap = notes[i + 1]['start_time'] - notes[i]['end_time']
            if gap > 0:
                gaps.append(gap)
        
        legato_count = sum(1 for gap in gaps if gap < 0.05)
        legato_percentage = (legato_count / len(gaps) * 100) if gaps else 0
        
        return {
            'type': articulation_type,
            'average_duration': float(avg_duration),
            'legato_percentage': float(legato_percentage),
            'staccato_percentage': float(100 - legato_percentage) if articulation_type == 'staccato' else 0
        }
    
    def save_transcription_midi(self, midi_data: pretty_midi.PrettyMIDI, output_path: str):
        """Save transcribed MIDI to file"""
        try:
            midi_data.write(output_path)
            self.logger.info(f"MIDI transcription saved to: {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save MIDI: {e}")
