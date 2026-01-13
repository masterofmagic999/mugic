"""
Session Manager - Manages practice sessions and historical data
"""
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from src.database import db_session, Piece, PracticeSession

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages pieces and practice sessions"""
    
    def __init__(self):
        """Initialize the session manager"""
        self.logger = logger
    
    def create_piece(self, filename: str, analysis: Dict[str, Any]) -> int:
        """
        Create a new piece entry
        
        Args:
            filename: Name of the sheet music file
            analysis: Analysis results from sheet music analyzer
            
        Returns:
            ID of the created piece
        """
        try:
            piece = Piece(
                filename=filename,
                analysis=json.dumps(analysis),
                upload_date=datetime.utcnow()
            )
            
            db_session.add(piece)
            db_session.commit()
            
            self.logger.info(f"Created piece: {filename} with ID {piece.id}")
            return piece.id
            
        except Exception as e:
            db_session.rollback()
            self.logger.error(f"Error creating piece: {str(e)}")
            raise
    
    def get_piece(self, piece_id: int) -> Optional[Dict[str, Any]]:
        """Get a piece by ID"""
        try:
            piece = db_session.query(Piece).filter_by(id=piece_id).first()
            
            if not piece:
                return None
            
            return {
                'id': piece.id,
                'filename': piece.filename,
                'analysis': json.loads(piece.analysis),
                'upload_date': piece.upload_date.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting piece: {str(e)}")
            raise
    
    def get_all_pieces(self) -> List[Dict[str, Any]]:
        """Get all pieces"""
        try:
            pieces = db_session.query(Piece).order_by(Piece.upload_date.desc()).all()
            
            return [{
                'id': p.id,
                'filename': p.filename,
                'upload_date': p.upload_date.isoformat(),
                'session_count': len(p.sessions)
            } for p in pieces]
            
        except Exception as e:
            self.logger.error(f"Error getting pieces: {str(e)}")
            raise
    
    def save_session(
        self,
        piece_id: int,
        audio_analysis: Dict[str, Any],
        feedback: Dict[str, Any],
        instrument: str
    ) -> int:
        """
        Save a practice session
        
        Args:
            piece_id: ID of the piece
            audio_analysis: Analysis of the audio performance
            feedback: Generated feedback
            instrument: Instrument used
            
        Returns:
            ID of the created session
        """
        try:
            session = PracticeSession(
                piece_id=piece_id,
                audio_analysis=json.dumps(audio_analysis),
                feedback=json.dumps(feedback),
                instrument=instrument,
                score=feedback['overall_score'],
                session_date=datetime.utcnow()
            )
            
            db_session.add(session)
            db_session.commit()
            
            self.logger.info(f"Saved session for piece {piece_id} with ID {session.id}")
            return session.id
            
        except Exception as e:
            db_session.rollback()
            self.logger.error(f"Error saving session: {str(e)}")
            raise
    
    def get_piece_sessions(self, piece_id: int) -> List[Dict[str, Any]]:
        """Get all practice sessions for a piece"""
        try:
            sessions = db_session.query(PracticeSession).filter_by(
                piece_id=piece_id
            ).order_by(PracticeSession.session_date.desc()).all()
            
            return [{
                'id': s.id,
                'session_date': s.session_date.isoformat(),
                'score': s.score,
                'instrument': s.instrument
            } for s in sessions]
            
        except Exception as e:
            self.logger.error(f"Error getting sessions: {str(e)}")
            raise
    
    def compare_with_previous(
        self,
        piece_id: int,
        current_session_id: int
    ) -> Dict[str, Any]:
        """
        Compare current session with previous attempts
        
        Args:
            piece_id: ID of the piece
            current_session_id: ID of the current session
            
        Returns:
            Comparison results
        """
        try:
            # Get current session
            current = db_session.query(PracticeSession).filter_by(
                id=current_session_id
            ).first()
            
            if not current:
                return {
                    'has_previous': False,
                    'message': 'This is your first attempt at this piece!'
                }
            
            # Get previous sessions
            previous_sessions = db_session.query(PracticeSession).filter(
                PracticeSession.piece_id == piece_id,
                PracticeSession.id != current_session_id
            ).order_by(PracticeSession.session_date.desc()).all()
            
            if not previous_sessions:
                return {
                    'has_previous': False,
                    'message': 'This is your first attempt at this piece!'
                }
            
            # Compare with most recent previous session
            previous = previous_sessions[0]
            
            current_feedback = json.loads(current.feedback)
            previous_feedback = json.loads(previous.feedback)
            
            score_change = current.score - previous.score
            
            improvements = []
            needs_work = []
            
            # Compare pitch
            pitch_change = (
                current_feedback['pitch']['score'] -
                previous_feedback['pitch']['score']
            )
            if pitch_change > 5:
                improvements.append(f"Pitch accuracy improved by {pitch_change} points")
            elif pitch_change < -5:
                needs_work.append(f"Pitch accuracy decreased by {abs(pitch_change)} points")
            
            # Compare rhythm
            rhythm_change = (
                current_feedback['rhythm']['score'] -
                previous_feedback['rhythm']['score']
            )
            if rhythm_change > 5:
                improvements.append(f"Rhythm improved by {rhythm_change} points")
            elif rhythm_change < -5:
                needs_work.append(f"Rhythm needs more work (decreased by {abs(rhythm_change)} points)")
            
            # Compare tempo
            tempo_change = (
                current_feedback['tempo']['score'] -
                previous_feedback['tempo']['score']
            )
            if tempo_change > 5:
                improvements.append(f"Tempo control improved by {tempo_change} points")
            elif tempo_change < -5:
                needs_work.append(f"Tempo control needs work (decreased by {abs(tempo_change)} points)")
            
            # General message
            if score_change > 0:
                message = f"Great job! Your overall score improved by {score_change} points."
            elif score_change < 0:
                message = f"Your score decreased by {abs(score_change)} points. Keep practicing!"
            else:
                message = "Your score remained the same. Try focusing on specific areas for improvement."
            
            return {
                'has_previous': True,
                'previous_date': previous.session_date.isoformat(),
                'previous_score': previous.score,
                'current_score': current.score,
                'score_change': score_change,
                'message': message,
                'improvements': improvements if improvements else ['Keep up the consistent work!'],
                'needs_work': needs_work if needs_work else ['All areas maintained or improved!'],
                'total_attempts': len(previous_sessions) + 1
            }
            
        except Exception as e:
            self.logger.error(f"Error comparing sessions: {str(e)}")
            return {
                'has_previous': False,
                'error': str(e)
            }
