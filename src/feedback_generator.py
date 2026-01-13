"""
Feedback Generator - Generates actionable feedback by comparing sheet music with performance
"""
import logging
from typing import Dict, List, Any
import numpy as np

logger = logging.getLogger(__name__)


class FeedbackGenerator:
    """Generates detailed feedback on music performance"""
    
    def __init__(self):
        """Initialize the feedback generator"""
        self.logger = logger
    
    def generate_feedback(
        self,
        sheet_music_analysis: Dict[str, Any],
        audio_analysis: Dict[str, Any],
        disable_dynamics: bool = False
    ) -> Dict[str, Any]:
        """
        Generate feedback by comparing sheet music with actual performance
        
        Args:
            sheet_music_analysis: Analysis of the sheet music
            audio_analysis: Analysis of the recorded performance
            disable_dynamics: If True, don't provide dynamics feedback
            
        Returns:
            Dictionary containing detailed feedback
        """
        try:
            self.logger.info("Generating performance feedback")
            
            # Compare notes (pitch accuracy)
            pitch_feedback = self._analyze_pitch_accuracy(
                sheet_music_analysis['notes'],
                audio_analysis['notes']
            )
            
            # Compare rhythm and timing
            rhythm_feedback = self._analyze_rhythm_accuracy(
                sheet_music_analysis['rhythms'],
                audio_analysis['rhythm'],
                sheet_music_analysis['tempo'],
                audio_analysis['tempo']
            )
            
            # Analyze tempo consistency
            tempo_feedback = self._analyze_tempo(
                sheet_music_analysis['tempo'],
                audio_analysis['tempo']
            )
            
            # Analyze dynamics (if enabled)
            dynamics_feedback = None
            if not disable_dynamics:
                dynamics_feedback = self._analyze_dynamics(
                    audio_analysis.get('dynamics', [])
                )
            
            # Generate overall assessment
            overall_score = self._calculate_overall_score(
                pitch_feedback,
                rhythm_feedback,
                tempo_feedback,
                dynamics_feedback
            )
            
            # Generate actionable recommendations
            recommendations = self._generate_recommendations(
                pitch_feedback,
                rhythm_feedback,
                tempo_feedback,
                dynamics_feedback
            )
            
            feedback = {
                'overall_score': overall_score,
                'pitch': pitch_feedback,
                'rhythm': rhythm_feedback,
                'tempo': tempo_feedback,
                'dynamics': dynamics_feedback,
                'recommendations': recommendations,
                'summary': self._generate_summary(
                    overall_score,
                    pitch_feedback,
                    rhythm_feedback,
                    tempo_feedback
                )
            }
            
            self.logger.info(f"Feedback generated: Overall score {overall_score}/100")
            return feedback
            
        except Exception as e:
            self.logger.error(f"Error generating feedback: {str(e)}")
            raise
    
    def _analyze_pitch_accuracy(
        self,
        expected_notes: List[Dict],
        played_notes: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze pitch accuracy"""
        if not expected_notes or not played_notes:
            return {
                'score': 0,
                'correct_notes': 0,
                'total_notes': len(expected_notes),
                'accuracy': 0.0,
                'errors': []
            }
        
        correct_count = 0
        errors = []
        
        # Simple matching - in production would use more sophisticated alignment
        min_length = min(len(expected_notes), len(played_notes))
        
        for i in range(min_length):
            expected = expected_notes[i]['pitch']
            played = played_notes[i]['pitch']
            
            if expected == played:
                correct_count += 1
            else:
                errors.append({
                    'position': i,
                    'expected': expected,
                    'played': played,
                    'time': played_notes[i]['start_time']
                })
        
        # Check for missing or extra notes
        if len(played_notes) < len(expected_notes):
            errors.append({
                'type': 'missing_notes',
                'count': len(expected_notes) - len(played_notes)
            })
        elif len(played_notes) > len(expected_notes):
            errors.append({
                'type': 'extra_notes',
                'count': len(played_notes) - len(expected_notes)
            })
        
        accuracy = (correct_count / len(expected_notes)) * 100 if expected_notes else 0
        
        return {
            'score': int(accuracy),
            'correct_notes': correct_count,
            'total_notes': len(expected_notes),
            'accuracy': round(accuracy, 2),
            'errors': errors
        }
    
    def _analyze_rhythm_accuracy(
        self,
        expected_rhythms: List[Dict],
        played_rhythm: Dict[str, Any],
        expected_tempo: float,
        played_tempo: float
    ) -> Dict[str, Any]:
        """Analyze rhythm and timing accuracy"""
        score = 100
        issues = []
        
        # Check tempo consistency
        tempo_diff = abs(expected_tempo - played_tempo)
        if tempo_diff > 10:
            score -= 20
            issues.append({
                'type': 'tempo_inconsistent',
                'expected': expected_tempo,
                'actual': played_tempo,
                'difference': round(tempo_diff, 2)
            })
        elif tempo_diff > 5:
            score -= 10
        
        # Check rhythm consistency (inter-onset interval variance)
        if played_rhythm.get('std_ioi', 0) > 0.1:
            score -= 15
            issues.append({
                'type': 'uneven_rhythm',
                'variability': round(played_rhythm['std_ioi'], 3)
            })
        
        return {
            'score': max(0, score),
            'issues': issues,
            'tempo_difference': round(tempo_diff, 2),
            'rhythm_consistency': 'good' if played_rhythm.get('std_ioi', 0) < 0.1 else 'needs_work'
        }
    
    def _analyze_tempo(
        self,
        expected_tempo: float,
        played_tempo: float
    ) -> Dict[str, Any]:
        """Analyze tempo accuracy"""
        difference = abs(expected_tempo - played_tempo)
        percentage_diff = (difference / expected_tempo) * 100
        
        if percentage_diff < 5:
            rating = 'excellent'
            score = 100
        elif percentage_diff < 10:
            rating = 'good'
            score = 85
        elif percentage_diff < 15:
            rating = 'fair'
            score = 70
        else:
            rating = 'needs_improvement'
            score = 50
        
        return {
            'score': score,
            'expected_bpm': round(expected_tempo, 1),
            'actual_bpm': round(played_tempo, 1),
            'difference_bpm': round(difference, 1),
            'percentage_difference': round(percentage_diff, 2),
            'rating': rating
        }
    
    def _analyze_dynamics(
        self,
        dynamics: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze dynamic range and control"""
        if not dynamics:
            return {
                'score': 50,
                'range': 'limited',
                'control': 'unknown'
            }
        
        # Calculate dynamic range
        db_values = [d['db'] for d in dynamics]
        dynamic_range = max(db_values) - min(db_values)
        
        # Check for dynamic variety
        levels = set(d['level'] for d in dynamics)
        
        score = 70
        if dynamic_range > 30:
            score += 15
        if len(levels) >= 4:
            score += 15
        
        return {
            'score': min(100, score),
            'range_db': round(dynamic_range, 2),
            'levels_used': list(levels),
            'variety': 'good' if len(levels) >= 3 else 'limited'
        }
    
    def _calculate_overall_score(
        self,
        pitch_feedback: Dict,
        rhythm_feedback: Dict,
        tempo_feedback: Dict,
        dynamics_feedback: Dict = None
    ) -> int:
        """Calculate overall performance score"""
        # Weighted average
        weights = {
            'pitch': 0.4,
            'rhythm': 0.3,
            'tempo': 0.2,
            'dynamics': 0.1
        }
        
        score = (
            pitch_feedback['score'] * weights['pitch'] +
            rhythm_feedback['score'] * weights['rhythm'] +
            tempo_feedback['score'] * weights['tempo']
        )
        
        if dynamics_feedback:
            score += dynamics_feedback['score'] * weights['dynamics']
        else:
            # Redistribute dynamics weight to other categories
            score = score / 0.9  # Normalize to 100
        
        return int(score)
    
    def _generate_recommendations(
        self,
        pitch_feedback: Dict,
        rhythm_feedback: Dict,
        tempo_feedback: Dict,
        dynamics_feedback: Dict = None
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Pitch recommendations
        if pitch_feedback['score'] < 70:
            recommendations.append(
                f"Focus on pitch accuracy. You got {pitch_feedback['correct_notes']} out of "
                f"{pitch_feedback['total_notes']} notes correct. "
                "Practice slowly and use a tuner to verify each note."
            )
            
            if pitch_feedback['errors']:
                error_notes = [e['expected'] for e in pitch_feedback['errors'] if 'expected' in e]
                if error_notes:
                    recommendations.append(
                        f"Pay special attention to these notes: {', '.join(set(error_notes[:5]))}"
                    )
        
        # Rhythm recommendations
        if rhythm_feedback['score'] < 70:
            if rhythm_feedback.get('rhythm_consistency') == 'needs_work':
                recommendations.append(
                    "Your rhythm is uneven. Practice with a metronome to develop steady timing."
                )
        
        # Tempo recommendations
        if tempo_feedback['score'] < 70:
            if tempo_feedback['actual_bpm'] < tempo_feedback['expected_bpm']:
                recommendations.append(
                    f"You're playing too slowly. Gradually increase your tempo from "
                    f"{tempo_feedback['actual_bpm']} BPM to the target {tempo_feedback['expected_bpm']} BPM."
                )
            else:
                recommendations.append(
                    f"You're playing too fast. Slow down from {tempo_feedback['actual_bpm']} BPM "
                    f"to the target {tempo_feedback['expected_bpm']} BPM and focus on accuracy."
                )
        
        # Dynamics recommendations
        if dynamics_feedback and dynamics_feedback['score'] < 70:
            if dynamics_feedback.get('variety') == 'limited':
                recommendations.append(
                    "Work on dynamic variety. Practice playing softer (piano) and louder (forte) sections."
                )
        
        # Positive reinforcement
        if not recommendations:
            recommendations.append(
                "Excellent work! Your performance is accurate. Continue refining your interpretation."
            )
        
        return recommendations
    
    def _generate_summary(
        self,
        overall_score: int,
        pitch_feedback: Dict,
        rhythm_feedback: Dict,
        tempo_feedback: Dict
    ) -> str:
        """Generate a text summary of the performance"""
        if overall_score >= 90:
            performance = "outstanding"
        elif overall_score >= 80:
            performance = "very good"
        elif overall_score >= 70:
            performance = "good"
        elif overall_score >= 60:
            performance = "fair"
        else:
            performance = "needs improvement"
        
        summary = f"Your performance was {performance} with an overall score of {overall_score}/100. "
        
        # Add specific highlights
        strengths = []
        if pitch_feedback['score'] >= 80:
            strengths.append("pitch accuracy")
        if rhythm_feedback['score'] >= 80:
            strengths.append("rhythmic consistency")
        if tempo_feedback['score'] >= 80:
            strengths.append("tempo control")
        
        if strengths:
            summary += f"Your strengths include: {', '.join(strengths)}. "
        
        return summary
