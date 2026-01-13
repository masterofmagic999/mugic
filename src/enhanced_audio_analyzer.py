"""
Enhanced AI Audio Analyzer with advanced pitch tracking and analysis
"""
import logging
import numpy as np
import librosa
import noisereduce as nr
from typing import Dict, List, Any, Optional

try:
    import crepe
    CREPE_AVAILABLE = True
except ImportError:
    CREPE_AVAILABLE = False

logger = logging.getLogger(__name__)


class EnhancedAudioAnalyzer:
    """Advanced audio analyzer with AI-powered pitch detection"""
    
    def __init__(self):
        self.logger = logger
        self.sample_rate = 22050
        self.use_crepe = CREPE_AVAILABLE  # CREPE is a state-of-the-art pitch tracker
    
    def analyze(
        self,
        audio_path: str,
        instrument: str = 'piano',
        apply_noise_reduction: bool = True
    ) -> Dict[str, Any]:
        """
        Perform advanced AI-powered audio analysis
        
        Args:
            audio_path: Path to audio file
            instrument: Instrument type for optimized analysis
            apply_noise_reduction: Apply sophisticated noise reduction
            
        Returns:
            Comprehensive audio analysis
        """
        try:
            self.logger.info(f"Starting enhanced AI audio analysis: {audio_path}")
            
            # Load audio
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Advanced noise reduction
            if apply_noise_reduction:
                audio = self._advanced_noise_reduction(audio, sr)
            
            # Extract features with AI
            if self.use_crepe:
                pitches = self._extract_pitches_crepe(audio, sr)
                self.logger.info("Using CREPE AI model for pitch detection")
            else:
                pitches = self._extract_pitches_librosa(audio, sr)
                self.logger.info("Using librosa for pitch detection")
            
            # Advanced onset detection
            onsets = self._detect_note_onsets_advanced(audio, sr, instrument)
            
            # Tempo estimation with confidence
            tempo, tempo_confidence = self._estimate_tempo_advanced(audio, sr)
            
            # Detailed dynamics analysis
            dynamics = self._analyze_dynamics_advanced(audio, sr)
            
            # Advanced rhythm analysis
            rhythm = self._analyze_rhythm_advanced(audio, sr, onsets)
            
            # Extract notes with AI
            notes = self._extract_notes_advanced(audio, sr, pitches, onsets, instrument)
            
            # Timbre analysis for instrument verification
            timbre_features = self._analyze_timbre(audio, sr)
            
            # Articulation analysis
            articulation = self._analyze_articulation(audio, sr, onsets)
            
            analysis = {
                'notes': notes,
                'tempo': tempo,
                'tempo_confidence': tempo_confidence,
                'dynamics': dynamics,
                'rhythm': rhythm,
                'pitches': pitches,
                'onsets': onsets,
                'duration': len(audio) / sr,
                'instrument': instrument,
                'timbre_features': timbre_features,
                'articulation': articulation,
                'analysis_method': 'AI-enhanced with CREPE' if self.use_crepe else 'Enhanced librosa',
                'sample_rate': sr,
                'total_notes': len(notes),
                'pitch_range': self._calculate_pitch_range(notes),
                'dynamic_range': self._calculate_dynamic_range(dynamics)
            }
            
            self.logger.info(f"Enhanced analysis complete: {len(notes)} notes, "
                           f"tempo: {tempo:.1f} BPM (confidence: {tempo_confidence:.2f})")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in enhanced audio analysis: {str(e)}")
            raise
    
    def _advanced_noise_reduction(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply advanced multi-stage noise reduction"""
        try:
            # Stage 1: Stationary noise reduction
            audio = nr.reduce_noise(
                y=audio,
                sr=sr,
                stationary=True,
                prop_decrease=0.9
            )
            
            # Stage 2: Non-stationary noise reduction
            audio = nr.reduce_noise(
                y=audio,
                sr=sr,
                stationary=False,
                prop_decrease=0.7
            )
            
            self.logger.info("Advanced multi-stage noise reduction applied")
            return audio
            
        except Exception as e:
            self.logger.warning(f"Advanced noise reduction failed: {e}, using original")
            return audio
    
    def _extract_pitches_crepe(self, audio: np.ndarray, sr: int) -> List[Dict]:
        """Extract pitches using CREPE AI model (state-of-the-art)"""
        try:
            # CREPE pitch tracking
            time, frequency, confidence, activation = crepe.predict(
                audio,
                sr,
                viterbi=True,  # Use Viterbi decoding for smoother pitch contours
                model_capacity='full'  # Use full model for best accuracy
            )
            
            pitches = []
            for t, f, c in zip(time, frequency, confidence):
                if c > 0.7 and f > 0:  # High confidence threshold
                    note = librosa.hz_to_note(f)
                    pitches.append({
                        'time': float(t),
                        'frequency': float(f),
                        'note': note,
                        'confidence': float(c)
                    })
            
            return pitches
            
        except Exception as e:
            self.logger.error(f"CREPE pitch extraction failed: {e}")
            return self._extract_pitches_librosa(audio, sr)
    
    def _extract_pitches_librosa(self, audio: np.ndarray, sr: int) -> List[Dict]:
        """Extract pitches using librosa (fallback)"""
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'),
            sr=sr,
            fill_na=None
        )
        
        pitches = []
        hop_length = 512
        times = librosa.frames_to_time(range(len(f0)), sr=sr, hop_length=hop_length)
        
        for i, (time, freq, voiced, prob) in enumerate(zip(times, f0, voiced_flag, voiced_probs)):
            if voiced and not np.isnan(freq) and prob > 0.6:
                note = librosa.hz_to_note(freq)
                pitches.append({
                    'time': float(time),
                    'frequency': float(freq),
                    'note': note,
                    'confidence': float(prob)
                })
        
        return pitches
    
    def _detect_note_onsets_advanced(
        self,
        audio: np.ndarray,
        sr: int,
        instrument: str
    ) -> np.ndarray:
        """Advanced onset detection optimized for instrument type"""
        # Use different detection methods based on instrument
        if instrument in ['timpani', 'xylophone', 'marimba']:
            # Percussive instruments - use energy-based detection
            onset_frames = librosa.onset.onset_detect(
                y=audio,
                sr=sr,
                units='frames',
                backtrack=True,
                pre_max=20,
                post_max=20,
                pre_avg=100,
                post_avg=100,
                delta=0.2,
                wait=10
            )
        else:
            # Pitched instruments - use spectral flux
            onset_frames = librosa.onset.onset_detect(
                y=audio,
                sr=sr,
                units='frames',
                backtrack=True
            )
        
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        return onset_times
    
    def _estimate_tempo_advanced(self, audio: np.ndarray, sr: int) -> tuple[float, float]:
        """Estimate tempo with confidence score"""
        # Use multiple methods for robust estimation
        tempo_static, beats = librosa.beat.beat_track(y=audio, sr=sr)
        
        # Calculate tempo confidence based on beat strength
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
        beat_frames = librosa.beat.beat_track(y=audio, sr=sr, onset_envelope=onset_env)[1]
        
        if len(beat_frames) > 2:
            # Calculate inter-beat intervals
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)
            intervals = np.diff(beat_times)
            
            # Confidence based on interval consistency
            std_dev = np.std(intervals)
            mean_interval = np.mean(intervals)
            confidence = max(0.0, min(1.0, 1.0 - (std_dev / mean_interval)))
        else:
            confidence = 0.5
        
        return float(tempo_static), float(confidence)
    
    def _analyze_dynamics_advanced(self, audio: np.ndarray, sr: int) -> List[Dict]:
        """Advanced dynamics analysis with more granular levels"""
        # Use both RMS and spectral centroid for better dynamics detection
        rms = librosa.feature.rms(y=audio, frame_length=2048, hop_length=512)[0]
        
        # Convert to dB scale
        rms_db = librosa.amplitude_to_db(rms, ref=np.max)
        
        hop_length = 512
        times = librosa.frames_to_time(range(len(rms)), sr=sr, hop_length=hop_length)
        
        dynamics = []
        for time, db in zip(times, rms_db):
            # More detailed dynamic classification
            if db > -5:
                level = 'fff'  # fortississimo
            elif db > -12:
                level = 'ff'   # fortissimo
            elif db > -18:
                level = 'f'    # forte
            elif db > -25:
                level = 'mf'   # mezzo-forte
            elif db > -32:
                level = 'mp'   # mezzo-piano
            elif db > -40:
                level = 'p'    # piano
            elif db > -50:
                level = 'pp'   # pianissimo
            else:
                level = 'ppp'  # pianississimo
            
            dynamics.append({
                'time': float(time),
                'db': float(db),
                'level': level
            })
        
        return dynamics
    
    def _analyze_rhythm_advanced(
        self,
        audio: np.ndarray,
        sr: int,
        onsets: np.ndarray
    ) -> Dict[str, Any]:
        """Advanced rhythm analysis with pattern detection"""
        if len(onsets) < 2:
            return {
                'inter_onset_intervals': [],
                'mean_ioi': 0,
                'std_ioi': 0,
                'rhythm_consistency': 0,
                'syncopation': 0
            }
        
        # Calculate inter-onset intervals
        iois = np.diff(onsets)
        
        # Rhythm consistency score
        if len(iois) > 0:
            consistency = 1.0 - min(1.0, np.std(iois) / (np.mean(iois) + 1e-6))
        else:
            consistency = 0.0
        
        # Simple syncopation measure (deviation from regular grid)
        tempo = 120  # Assumed tempo
        beat_duration = 60.0 / tempo
        syncopation = 0.0
        
        if len(onsets) > 0:
            # Calculate how far onsets are from nearest beat
            deviations = []
            for onset in onsets:
                nearest_beat = round(onset / beat_duration) * beat_duration
                deviation = abs(onset - nearest_beat)
                deviations.append(deviation)
            
            syncopation = float(np.mean(deviations))
        
        return {
            'inter_onset_intervals': iois.tolist(),
            'mean_ioi': float(np.mean(iois)),
            'std_ioi': float(np.std(iois)),
            'rhythm_consistency': float(consistency),
            'syncopation': float(syncopation),
            'num_notes': len(onsets)
        }
    
    def _extract_notes_advanced(
        self,
        audio: np.ndarray,
        sr: int,
        pitches: List[Dict],
        onsets: np.ndarray,
        instrument: str
    ) -> List[Dict]:
        """Advanced note extraction with better segmentation"""
        notes = []
        
        if len(onsets) == 0:
            return notes
        
        for i, onset_time in enumerate(onsets):
            # Define window
            window_start = onset_time
            window_end = onsets[i + 1] if i + 1 < len(onsets) else len(audio) / sr
            
            # Find pitches in window
            window_pitches = [
                p for p in pitches
                if window_start <= p['time'] < window_end
            ]
            
            if window_pitches:
                # Use median pitch for robustness
                frequencies = [p['frequency'] for p in window_pitches]
                confidences = [p['confidence'] for p in window_pitches]
                
                median_freq = np.median(frequencies)
                mean_confidence = np.mean(confidences)
                
                note_name = librosa.hz_to_note(median_freq)
                
                notes.append({
                    'start_time': float(onset_time),
                    'duration': float(window_end - window_start),
                    'pitch': note_name,
                    'frequency': float(median_freq),
                    'confidence': float(mean_confidence),
                    'num_samples': len(window_pitches)
                })
        
        return notes
    
    def _analyze_timbre(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analyze timbre features for instrument verification"""
        # Extract spectral features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sr))
        zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(audio))
        
        # Extract MFCCs
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfccs, axis=1)
        
        return {
            'spectral_centroid': float(spectral_centroid),
            'spectral_rolloff': float(spectral_rolloff),
            'zero_crossing_rate': float(zero_crossing_rate),
            'brightness': float(spectral_centroid / (sr / 2)),  # Normalized
            'mfcc_coefficients': mfcc_mean.tolist()
        }
    
    def _analyze_articulation(
        self,
        audio: np.ndarray,
        sr: int,
        onsets: np.ndarray
    ) -> Dict[str, Any]:
        """Analyze articulation characteristics"""
        if len(onsets) < 2:
            return {'type': 'unknown', 'legato_percentage': 0}
        
        # Calculate note durations and gaps
        note_durations = []
        gaps = []
        
        for i in range(len(onsets) - 1):
            # Estimate note end (simplified - would use offset detection in production)
            note_end = onsets[i + 1]
            duration = note_end - onsets[i]
            note_durations.append(duration)
            
            # Gap would be calculated with proper offset detection
            gaps.append(0)  # Placeholder
        
        # Estimate articulation type
        avg_duration = np.mean(note_durations)
        
        if avg_duration < 0.2:
            articulation_type = 'staccato'
        elif avg_duration > 0.8:
            articulation_type = 'legato'
        else:
            articulation_type = 'normal'
        
        return {
            'type': articulation_type,
            'average_note_duration': float(avg_duration),
            'legato_percentage': 0.5  # Placeholder
        }
    
    def _calculate_pitch_range(self, notes: List[Dict]) -> Dict[str, str]:
        """Calculate the pitch range of the performance"""
        if not notes:
            return {'lowest': 'N/A', 'highest': 'N/A', 'range_semitones': 0}
        
        frequencies = [n['frequency'] for n in notes]
        lowest_freq = min(frequencies)
        highest_freq = max(frequencies)
        
        lowest_note = librosa.hz_to_note(lowest_freq)
        highest_note = librosa.hz_to_note(highest_freq)
        
        # Calculate range in semitones
        range_semitones = 12 * np.log2(highest_freq / lowest_freq)
        
        return {
            'lowest': lowest_note,
            'highest': highest_note,
            'range_semitones': int(range_semitones)
        }
    
    def _calculate_dynamic_range(self, dynamics: List[Dict]) -> float:
        """Calculate dynamic range in dB"""
        if not dynamics:
            return 0.0
        
        db_values = [d['db'] for d in dynamics]
        return float(max(db_values) - min(db_values))
