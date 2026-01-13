"""
Main Flask application for the Music Practice Feedback System
Real implementations: Audiveris OMR + Spotify basic-pitch
"""
import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import logging

# Real implementations
from src.audiveris_omr import AudiverisOMR
from src.real_audio_analyzer import RealAudioAnalyzer
from src.real_omr_system import RealOMRSystem  # Fallback if Audiveris not available
from src.real_feedback_generator import RealFeedbackGenerator
from src.session_manager import SessionManager
from src.database import init_db
from src.auth import init_auth, AuthManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RECORDINGS_FOLDER'] = 'recordings'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RECORDINGS_FOLDER'], exist_ok=True)

# Initialize database
init_db()

# Initialize authentication
init_auth(app)

# Initialize REAL components with actual functionality
try:
    # Try Audiveris first (best quality OMR)
    audiveris_omr = AudiverisOMR()
    if audiveris_omr.is_available():
        omr_system = audiveris_omr
        logger.info("✓ Using Audiveris OMR (GitHub open-source)")
    else:
        # Fallback to computer vision-based OMR
        omr_system = RealOMRSystem()
        logger.info("⚠ Audiveris not found, using computer vision OMR fallback")
        logger.info("  Install Audiveris from: https://github.com/Audiveris/audiveris")
except Exception as e:
    logger.error(f"OMR initialization error: {e}")
    omr_system = RealOMRSystem()

# Initialize real audio analyzer with Spotify basic-pitch
try:
    audio_analyzer = RealAudioAnalyzer()
    logger.info("✓ Using Spotify basic-pitch for audio transcription")
except Exception as e:
    logger.error(f"Audio analyzer initialization error: {e}")
    raise RuntimeError("basic-pitch is required. Install with: pip install basic-pitch")

# Real feedback generator with LLM
feedback_generator = RealFeedbackGenerator()
session_manager = SessionManager()

logger.info("=" * 60)
logger.info("Mugic Application Initialized - ALL REAL IMPLEMENTATIONS")
logger.info("OMR: Audiveris (if available) or Computer Vision")
logger.info("Audio: Spotify basic-pitch")
logger.info("Feedback: Open-source LLM (TinyLlama/DistilGPT2)")
logger.info("Auth: JWT with bcrypt")
logger.info("=" * 60)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')


@app.route('/api/upload-sheet-music', methods=['POST'])
def upload_sheet_music():
    """Upload and analyze sheet music PDF with AI-powered OMR"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload a PDF'}), 400
        
        # Save the file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Analyze the sheet music with REAL OMR (Audiveris or CV-based)
        logger.info(f"Analyzing sheet music with real OMR: {filename}")
        analysis = omr_system.analyze_sheet_music(filepath)
        
        # Create a new piece entry
        piece_id = session_manager.create_piece(filename, analysis)
        
        return jsonify({
            'success': True,
            'piece_id': piece_id,
            'analysis': analysis,
            'message': f'Sheet music analyzed with {analysis.get("analysis_method", "OMR")}'
        })
    
    except Exception as e:
        logger.error(f"Error uploading sheet music: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze-performance', methods=['POST'])
def analyze_performance():
    """Analyze recorded performance against sheet music with enhanced AI"""
    try:
        data = request.get_json()
        piece_id = data.get('piece_id')
        audio_file = data.get('audio_file')
        instrument = data.get('instrument', 'piano')
        disable_dynamics = data.get('disable_dynamics', False)
        
        if not piece_id or not audio_file:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Get sheet music analysis
        piece = session_manager.get_piece(piece_id)
        if not piece:
            return jsonify({'error': 'Piece not found'}), 404
        
        # Analyze the audio performance with REAL Spotify basic-pitch
        logger.info(f"Analyzing performance with Spotify basic-pitch for piece {piece_id}")
        audio_path = os.path.join(app.config['RECORDINGS_FOLDER'], audio_file)
        
        # Use real audio analyzer (Spotify basic-pitch)
        audio_analysis = audio_analyzer.analyze(
            audio_path,
            instrument=instrument,
            apply_noise_reduction=True
        )
        logger.info(f"Real audio transcription complete: {audio_analysis.get('total_notes', 0)} notes")
        
        # Generate feedback
        feedback = feedback_generator.generate_feedback(
            sheet_music_analysis=piece['analysis'],
            audio_analysis=audio_analysis,
            disable_dynamics=disable_dynamics
        )
        
        # Save the session
        session_id = session_manager.save_session(
            piece_id=piece_id,
            audio_analysis=audio_analysis,
            feedback=feedback,
            instrument=instrument
        )
        
        # Get comparison with previous attempts
        comparison = session_manager.compare_with_previous(piece_id, session_id)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'feedback': feedback,
            'comparison': comparison
        })
    
    except Exception as e:
        logger.error(f"Error analyzing performance: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/pieces', methods=['GET'])
def get_pieces():
    """Get all uploaded pieces"""
    try:
        pieces = session_manager.get_all_pieces()
        return jsonify({
            'success': True,
            'pieces': pieces
        })
    except Exception as e:
        logger.error(f"Error fetching pieces: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/piece/<int:piece_id>/sessions', methods=['GET'])
def get_piece_sessions(piece_id):
    """Get all practice sessions for a piece"""
    try:
        sessions = session_manager.get_piece_sessions(piece_id)
        return jsonify({
            'success': True,
            'sessions': sessions
        })
    except Exception as e:
        logger.error(f"Error fetching sessions: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/instruments', methods=['GET'])
def get_instruments():
    """Get list of supported instruments"""
    instruments = [
        # Woodwinds
        {'id': 'flute', 'name': 'Flute', 'category': 'woodwind'},
        {'id': 'piccolo', 'name': 'Piccolo', 'category': 'woodwind'},
        {'id': 'clarinet', 'name': 'Clarinet', 'category': 'woodwind'},
        {'id': 'bass_clarinet', 'name': 'Bass Clarinet', 'category': 'woodwind'},
        {'id': 'oboe', 'name': 'Oboe', 'category': 'woodwind'},
        {'id': 'bassoon', 'name': 'Bassoon', 'category': 'woodwind'},
        {'id': 'saxophone_soprano', 'name': 'Soprano Saxophone', 'category': 'woodwind'},
        {'id': 'saxophone_alto', 'name': 'Alto Saxophone', 'category': 'woodwind'},
        {'id': 'saxophone_tenor', 'name': 'Tenor Saxophone', 'category': 'woodwind'},
        {'id': 'saxophone_baritone', 'name': 'Baritone Saxophone', 'category': 'woodwind'},
        
        # Brass
        {'id': 'trumpet', 'name': 'Trumpet', 'category': 'brass'},
        {'id': 'cornet', 'name': 'Cornet', 'category': 'brass'},
        {'id': 'french_horn', 'name': 'French Horn', 'category': 'brass'},
        {'id': 'trombone', 'name': 'Trombone', 'category': 'brass'},
        {'id': 'euphonium', 'name': 'Euphonium', 'category': 'brass'},
        {'id': 'tuba', 'name': 'Tuba', 'category': 'brass'},
        
        # Percussion (pitched)
        {'id': 'xylophone', 'name': 'Xylophone', 'category': 'percussion'},
        {'id': 'marimba', 'name': 'Marimba', 'category': 'percussion'},
        {'id': 'vibraphone', 'name': 'Vibraphone', 'category': 'percussion'},
        {'id': 'glockenspiel', 'name': 'Glockenspiel', 'category': 'percussion'},
        {'id': 'timpani', 'name': 'Timpani', 'category': 'percussion'},
    ]
    
    return jsonify({
        'success': True,
        'instruments': instruments
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for deployment platforms"""
    return jsonify({
        'status': 'healthy',
        'service': 'mugic',
        'version': '1.0.0'
    })


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        
        if not username or not email or not password:
            return jsonify({
                'success': False,
                'error': 'Username, email, and password are required'
            }), 400
        
        success, message, user_data = AuthManager.register_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'user': user_data
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'success': False, 'error': 'Registration failed'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user and return tokens"""
    try:
        data = request.get_json()
        username_or_email = data.get('username')
        password = data.get('password')
        
        if not username_or_email or not password:
            return jsonify({
                'success': False,
                'error': 'Username/email and password are required'
            }), 400
        
        success, message, user_data, tokens = AuthManager.authenticate_user(
            username_or_email=username_or_email,
            password=password
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'user': user_data,
                'tokens': tokens
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 401
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'success': False, 'error': 'Login failed'}), 500


@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = AuthManager.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get profile'}), 500


@app.route('/api/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        success, message = AuthManager.update_user(user_id, **data)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return jsonify({'success': False, 'error': 'Update failed'}), 500


@app.route('/api/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({
                'success': False,
                'error': 'Old and new password are required'
            }), 400
        
        success, message = AuthManager.change_password(
            user_id=user_id,
            old_password=old_password,
            new_password=new_password
        )
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return jsonify({'success': False, 'error': 'Password change failed'}), 500


if __name__ == '__main__':
    # Get port from environment variable (for deployment platforms)
    port = int(os.environ.get('PORT', 5000))
    # Disable debug in production
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
