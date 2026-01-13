"""
Main Flask application for the Music Practice Feedback System
"""
import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging

from src.sheet_music_analyzer import SheetMusicAnalyzer
from src.audio_analyzer import AudioAnalyzer
from src.feedback_generator import FeedbackGenerator
from src.session_manager import SessionManager
from src.database import init_db

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

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RECORDINGS_FOLDER'], exist_ok=True)

# Initialize database
init_db()

# Initialize components
sheet_music_analyzer = SheetMusicAnalyzer()
audio_analyzer = AudioAnalyzer()
feedback_generator = FeedbackGenerator()
session_manager = SessionManager()


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
    """Upload and analyze sheet music PDF"""
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
        
        # Analyze the sheet music
        logger.info(f"Analyzing sheet music: {filename}")
        analysis = sheet_music_analyzer.analyze(filepath)
        
        # Create a new piece entry
        piece_id = session_manager.create_piece(filename, analysis)
        
        return jsonify({
            'success': True,
            'piece_id': piece_id,
            'analysis': analysis,
            'message': 'Sheet music uploaded and analyzed successfully'
        })
    
    except Exception as e:
        logger.error(f"Error uploading sheet music: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze-performance', methods=['POST'])
def analyze_performance():
    """Analyze recorded performance against sheet music"""
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
        
        # Analyze the audio performance
        logger.info(f"Analyzing performance for piece {piece_id}")
        audio_path = os.path.join(app.config['RECORDINGS_FOLDER'], audio_file)
        audio_analysis = audio_analyzer.analyze(
            audio_path,
            instrument=instrument,
            apply_noise_reduction=True
        )
        
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
