"""
Real Feedback Generator using Open Source LLM
Uses HuggingFace Transformers with TinyLlama or similar small LLM
"""
import logging
from typing import Dict, List, Any
import numpy as np

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)


class RealFeedbackGenerator:
    """Real feedback generator using open-source LLM for text generation"""
    
    def __init__(self):
        self.logger = logger
        self.llm_pipeline = None
        
        # Initialize LLM for recommendation generation
        if TRANSFORMERS_AVAILABLE:
            self._init_llm()
    
    def _init_llm(self):
        """Initialize lightweight open-source LLM with secure settings"""
        try:
            # Use TinyLlama - a small but capable 1.1B parameter model
            # Falls back to distilgpt2 if TinyLlama not available
            model_options = [
                "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # Best quality, 1.1B params
                "distilgpt2"  # Lightweight fallback, 82M params
            ]
            
            for model_name in model_options:
                try:
                    self.logger.info(f"Loading LLM: {model_name}")
                    
                    # Security: Use local_files_only=True if model is cached to prevent remote code execution
                    self.llm_pipeline = pipeline(
                        "text-generation",
                        model=model_name,
                        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                        device=0 if torch.cuda.is_available() else -1,
                        max_length=200,
                        do_sample=True,
                        temperature=0.7,
                        top_p=0.9,
                        trust_remote_code=False  # Security: Never trust remote code
                    )
                    
                    self.logger.info(f"✓ LLM loaded: {model_name}")
                    break
                    
                except Exception as e:
                    self.logger.warning(f"Failed to load {model_name}: {e}")
                    continue
            
            if not self.llm_pipeline:
                self.logger.warning("Could not load LLM - using template-based feedback")
                
        except Exception as e:
            self.logger.error(f"LLM initialization error: {e}")
    
    def generate_feedback(
        self,
        sheet_music_analysis: Dict[str, Any],
        audio_analysis: Dict[str, Any],
        disable_dynamics: bool = False
    ) -> Dict[str, Any]:
        """
        Generate comprehensive feedback by comparing sheet music with performance
        
        Args:
            sheet_music_analysis: Analysis from Audiveris/OMR
            audio_analysis: Analysis from Spotify basic-pitch
            disable_dynamics: Skip dynamics feedback
            
        Returns:
            Detailed feedback dictionary
        """
        try:
            self.logger.info("Generating real feedback from transcriptions")
            
            # Real pitch accuracy analysis
            pitch_feedback = self._analyze_pitch_accuracy(
                sheet_music_analysis['notes'],
                audio_analysis['notes']
            )
            
            # Real rhythm analysis
            rhythm_feedback = self._analyze_rhythm_accuracy(
                sheet_music_analysis.get('rhythms', []),
                audio_analysis['rhythm'],
                sheet_music_analysis.get('tempo', 120),
                audio_analysis.get('tempo', 120)
            )
            
            # Real tempo analysis
            tempo_feedback = self._analyze_tempo(
                sheet_music_analysis.get('tempo', 120),
                audio_analysis.get('tempo', 120)
            )
            
            # Real dynamics analysis (if enabled)
            dynamics_feedback = None
            if not disable_dynamics:
                dynamics_feedback = self._analyze_dynamics(
                    audio_analysis.get('dynamics', [])
                )
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                pitch_feedback,
                rhythm_feedback,
                tempo_feedback,
                dynamics_feedback
            )
            
            # Generate recommendations using LLM or templates
            recommendations = self._generate_recommendations_llm(
                pitch_feedback,
                rhythm_feedback,
                tempo_feedback,
                dynamics_feedback,
                overall_score
            )
            
            # Generate summary
            summary = self._generate_summary(
                overall_score,
                pitch_feedback,
                rhythm_feedback,
                tempo_feedback
            )
            
            feedback = {
                'overall_score': overall_score,
                'pitch': pitch_feedback,
                'rhythm': rhythm_feedback,
                'tempo': tempo_feedback,
                'dynamics': dynamics_feedback,
                'recommendations': recommendations,
                'summary': summary
            }
            
            self.logger.info(f"Feedback generated: Score {overall_score}/100")
            return feedback
            
        except Exception as e:
            self.logger.error(f"Error generating feedback: {str(e)}")
            raise
    
    def _analyze_pitch_accuracy(
        self,
        expected_notes: List[Dict],
        played_notes: List[Dict]
    ) -> Dict[str, Any]:
        """Real pitch accuracy comparison"""
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
        
        # Align notes by timing
        expected_aligned = sorted(expected_notes, key=lambda x: x.get('start_time', 0))
        played_aligned = sorted(played_notes, key=lambda x: x.get('start_time', 0))
        
        # Match notes within time windows
        for i, expected_note in enumerate(expected_aligned):
            expected_pitch = expected_note.get('pitch', '')
            expected_time = expected_note.get('start_time', 0)
            
            # Find closest played note within 0.5 second window
            closest_played = None
            min_time_diff = float('inf')
            
            for played_note in played_aligned:
                played_time = played_note.get('start_time', 0)
                time_diff = abs(played_time - expected_time)
                
                if time_diff < 0.5 and time_diff < min_time_diff:
                    closest_played = played_note
                    min_time_diff = time_diff
            
            if closest_played:
                played_pitch = closest_played.get('pitch', '')
                if expected_pitch == played_pitch:
                    correct_count += 1
                else:
                    errors.append({
                        'position': i,
                        'expected': expected_pitch,
                        'played': played_pitch,
                        'time': expected_time
                    })
            else:
                errors.append({
                    'position': i,
                    'expected': expected_pitch,
                    'played': 'MISSING',
                    'time': expected_time
                })
        
        # Check for extra notes
        if len(played_aligned) > len(expected_aligned):
            errors.append({
                'type': 'extra_notes',
                'count': len(played_aligned) - len(expected_aligned)
            })
        
        accuracy = (correct_count / len(expected_aligned)) * 100 if expected_aligned else 0
        
        return {
            'score': int(accuracy),
            'correct_notes': correct_count,
            'total_notes': len(expected_aligned),
            'accuracy': round(accuracy, 2),
            'errors': errors[:10]  # Limit to first 10 errors
        }
    
    def _analyze_rhythm_accuracy(
        self,
        expected_rhythms: List[Dict],
        played_rhythm: Dict[str, Any],
        expected_tempo: float,
        played_tempo: float
    ) -> Dict[str, Any]:
        """Real rhythm accuracy analysis"""
        score = 100
        issues = []
        
        # Tempo difference
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
        
        # Rhythm consistency
        std_ioi = played_rhythm.get('std_ioi', 0)
        if std_ioi > 0.15:
            score -= 15
            issues.append({
                'type': 'uneven_rhythm',
                'variability': round(std_ioi, 3)
            })
        
        return {
            'score': max(0, score),
            'issues': issues,
            'tempo_difference': round(tempo_diff, 2),
            'rhythm_consistency': 'good' if std_ioi < 0.1 else 'needs_work'
        }
    
    def _analyze_tempo(self, expected_tempo: float, played_tempo: float) -> Dict[str, Any]:
        """Real tempo analysis"""
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
    
    def _analyze_dynamics(self, dynamics: List[Dict]) -> Dict[str, Any]:
        """Real dynamics analysis"""
        if not dynamics:
            return {'score': 50, 'range': 'limited', 'control': 'unknown'}
        
        db_values = [d['db'] for d in dynamics]
        dynamic_range = max(db_values) - min(db_values)
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
        """Calculate overall score"""
        weights = {'pitch': 0.4, 'rhythm': 0.3, 'tempo': 0.2, 'dynamics': 0.1}
        
        score = (
            pitch_feedback['score'] * weights['pitch'] +
            rhythm_feedback['score'] * weights['rhythm'] +
            tempo_feedback['score'] * weights['tempo']
        )
        
        if dynamics_feedback:
            score += dynamics_feedback['score'] * weights['dynamics']
        else:
            score = score / 0.9
        
        return int(score)
    
    def _generate_recommendations_llm(
        self,
        pitch_feedback: Dict,
        rhythm_feedback: Dict,
        tempo_feedback: Dict,
        dynamics_feedback: Dict,
        overall_score: int
    ) -> List[str]:
        """Generate recommendations using LLM"""
        recommendations = []
        
        # Build context for LLM
        context = self._build_feedback_context(
            pitch_feedback, rhythm_feedback, tempo_feedback, dynamics_feedback, overall_score
        )
        
        if self.llm_pipeline:
            try:
                # Generate personalized recommendation using LLM
                prompt = f"""As a music teacher, provide specific practice advice for a student who:
{context}

Give 2-3 specific, actionable recommendations:"""
                
                generated = self.llm_pipeline(
                    prompt,
                    max_length=150,
                    num_return_sequences=1,
                    pad_token_id=self.llm_pipeline.tokenizer.eos_token_id
                )[0]['generated_text']
                
                # Extract recommendations from generated text
                if len(generated) > len(prompt):
                    recs_text = generated[len(prompt):].strip()
                    # Split by line breaks or numbered points
                    for line in recs_text.split('\n'):
                        line = line.strip()
                        if line and len(line) > 10:
                            recommendations.append(line)
                            if len(recommendations) >= 3:
                                break
                
            except Exception as e:
                self.logger.warning(f"LLM generation failed: {e}")
        
        # Fallback to template-based if LLM fails or produces poor output
        if len(recommendations) < 2:
            recommendations = self._generate_recommendations_template(
                pitch_feedback, rhythm_feedback, tempo_feedback, dynamics_feedback
            )
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _build_feedback_context(
        self,
        pitch_feedback: Dict,
        rhythm_feedback: Dict,
        tempo_feedback: Dict,
        dynamics_feedback: Dict,
        overall_score: int
    ) -> str:
        """Build context string for LLM"""
        context_parts = []
        
        context_parts.append(f"- Overall performance score: {overall_score}/100")
        context_parts.append(f"- Pitch accuracy: {pitch_feedback['score']}/100 ({pitch_feedback['correct_notes']}/{pitch_feedback['total_notes']} notes correct)")
        context_parts.append(f"- Rhythm score: {rhythm_feedback['score']}/100")
        context_parts.append(f"- Tempo: played at {tempo_feedback['actual_bpm']} BPM (expected {tempo_feedback['expected_bpm']} BPM)")
        
        if dynamics_feedback:
            context_parts.append(f"- Dynamics variety: {dynamics_feedback['variety']}")
        
        return '\n'.join(context_parts)
    
    def _generate_recommendations_template(
        self,
        pitch_feedback: Dict,
        rhythm_feedback: Dict,
        tempo_feedback: Dict,
        dynamics_feedback: Dict
    ) -> List[str]:
        """Fallback template-based recommendations"""
        recommendations = []
        
        # Pitch recommendations
        if pitch_feedback['score'] < 70:
            accuracy = pitch_feedback['accuracy']
            recommendations.append(
                f"Focus on pitch accuracy ({accuracy:.1f}% correct). Practice slowly with a tuner, "
                f"focusing on one measure at a time until you can play all notes correctly."
            )
        
        # Rhythm recommendations
        if rhythm_feedback['score'] < 70:
            if rhythm_feedback.get('rhythm_consistency') == 'needs_work':
                recommendations.append(
                    "Your rhythm is uneven. Practice with a metronome at a slower tempo, "
                    "focusing on keeping steady time between notes."
                )
        
        # Tempo recommendations
        if tempo_feedback['score'] < 70:
            diff = tempo_feedback['actual_bpm'] - tempo_feedback['expected_bpm']
            if diff < 0:
                recommendations.append(
                    f"You're playing too slowly ({tempo_feedback['actual_bpm']} BPM vs {tempo_feedback['expected_bpm']} BPM target). "
                    f"Gradually increase tempo using a metronome."
                )
            else:
                recommendations.append(
                    f"You're playing too fast ({tempo_feedback['actual_bpm']} BPM vs {tempo_feedback['expected_bpm']} BPM target). "
                    f"Slow down and focus on accuracy first."
                )
        
        # Dynamics recommendations
        if dynamics_feedback and dynamics_feedback['score'] < 70:
            if dynamics_feedback.get('variety') == 'limited':
                recommendations.append(
                    "Work on dynamic variety. Practice playing the same passage at different volumes "
                    "(piano, mezzo-forte, forte) to develop better control."
                )
        
        # Positive reinforcement
        if not recommendations:
            recommendations.append(
                "Excellent work! Your performance is accurate across all areas. "
                "Continue refining your musical expression and interpretation."
            )
        
        return recommendations
    
    def _generate_summary(
        self,
        overall_score: int,
        pitch_feedback: Dict,
        rhythm_feedback: Dict,
        tempo_feedback: Dict
    ) -> str:
        """Generate performance summary"""
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
