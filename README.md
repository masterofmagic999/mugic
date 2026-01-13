# Mugic 🎵

**AI-Powered Music Practice Feedback System**

Mugic is a powerful application that helps musicians practice more effectively by providing instant, actionable feedback on their performances. Upload PDF sheet music, record yourself playing, and receive detailed analysis with AI-powered insights.

## Features

### 🎼 Sheet Music Analysis
- **PDF Upload**: Upload any PDF sheet music
- **AI-Powered OMR**: Optical Music Recognition extracts notes, rhythms, tempo, and key signatures
- **High Accuracy**: Advanced computer vision and machine learning for precise music notation analysis

### 🎤 Audio Recording & Analysis
- **Professional Recording**: High-quality audio capture
- **Advanced Noise Filtration**: Removes background noise for accurate analysis
- **Real-Time Processing**: Instant pitch detection and rhythm analysis
- **Multi-Instrument Support**: Optimized for all concert band instruments

### 📊 Detailed Feedback
- **Pitch Accuracy**: Identifies correct and incorrect notes
- **Rhythm Analysis**: Evaluates timing and rhythmic consistency
- **Tempo Control**: Measures tempo accuracy and consistency
- **Dynamics (Optional)**: Analyzes volume and expression (can be disabled)
- **Overall Score**: Comprehensive performance rating

### 📈 Progress Tracking
- **Session History**: All practice sessions are saved
- **Performance Comparison**: See what improved and what needs work
- **Trend Analysis**: Track progress over time
- **Actionable Recommendations**: Get specific suggestions for improvement

### 🎺 Supported Instruments

**Woodwinds:**
- Flute, Piccolo
- Clarinet, Bass Clarinet
- Oboe, Bassoon
- Soprano, Alto, Tenor, Baritone Saxophone

**Brass:**
- Trumpet, Cornet
- French Horn
- Trombone
- Euphonium, Tuba

**Percussion (Pitched):**
- Xylophone, Marimba
- Vibraphone, Glockenspiel
- Timpani

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Microphone for recording

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/masterofmagic999/mugic.git
   cd mugic
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   The database will be automatically created when you first run the application.

## Usage

### Starting the Application

1. **Run the Flask server**
   ```bash
   python app.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:5000`

### Using Mugic

#### 1. Upload Sheet Music
- Click "Choose PDF File" and select your sheet music
- Click "Upload & Analyze" to process the sheet music
- The AI will extract musical information (notes, tempo, key, etc.)

#### 2. Set Up Your Practice Session
- Select your instrument from the dropdown menu
- Optionally, check "Disable dynamics feedback" to focus on notes and rhythm first

#### 3. Record Your Performance
- Click "Start Recording" when ready
- Play the piece
- Click "Stop Recording" when finished

#### 4. Review Your Feedback
- **Overall Score**: See your performance rating (0-100)
- **Detailed Analysis**: Review pitch, rhythm, tempo, and dynamics scores
- **Recommendations**: Get specific, actionable advice for improvement
- **Progress Comparison**: See how you improved from previous attempts

#### 5. Practice Again
- Click "Practice Again" to record another attempt
- Click "Upload New Piece" to work on different sheet music

## Technical Architecture

### Backend (Python/Flask)
- **app.py**: Main Flask application and API endpoints
- **src/sheet_music_analyzer.py**: PDF processing and OMR
- **src/audio_analyzer.py**: Audio processing with noise reduction
- **src/feedback_generator.py**: Intelligent feedback generation
- **src/session_manager.py**: Session and progress tracking
- **src/database.py**: SQLAlchemy models and database management

### Frontend (HTML/CSS/JavaScript)
- **templates/index.html**: Single-page application UI
- **static/css/style.css**: Modern, responsive styling
- **static/js/app.js**: Client-side logic and API integration

### Key Technologies
- **Flask**: Web framework
- **TensorFlow**: Machine learning for OMR
- **OpenCV**: Computer vision for sheet music analysis
- **Librosa**: Audio analysis and feature extraction
- **noisereduce**: Advanced noise filtration
- **music21**: Music theory and notation
- **SQLAlchemy**: Database ORM
- **PyMuPDF**: PDF processing

## API Endpoints

### Upload Sheet Music
```
POST /api/upload-sheet-music
Content-Type: multipart/form-data
Body: file (PDF)

Response: {
  "success": true,
  "piece_id": 1,
  "analysis": {...},
  "message": "Sheet music uploaded and analyzed successfully"
}
```

### Analyze Performance
```
POST /api/analyze-performance
Content-Type: application/json
Body: {
  "piece_id": 1,
  "audio_file": "recording.wav",
  "instrument": "flute",
  "disable_dynamics": false
}

Response: {
  "success": true,
  "session_id": 1,
  "feedback": {...},
  "comparison": {...}
}
```

### Get Pieces
```
GET /api/pieces

Response: {
  "success": true,
  "pieces": [...]
}
```

### Get Instruments
```
GET /api/instruments

Response: {
  "success": true,
  "instruments": [...]
}
```

## Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
MAX_CONTENT_LENGTH=52428800  # 50MB
```

### Customization
- **Tempo tolerance**: Adjust in `feedback_generator.py`
- **Noise reduction level**: Modify in `audio_analyzer.py`
- **Supported file types**: Update in `app.py`

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

### Code Style
```bash
# Install development dependencies
pip install black flake8

# Format code
black .

# Lint code
flake8 src/
```

## Troubleshooting

### Microphone Access
If recording doesn't work:
- Ensure your browser has microphone permissions
- Check your system microphone settings
- Try a different browser (Chrome recommended)

### PDF Upload Issues
If PDF upload fails:
- Ensure the file is a valid PDF
- Check file size (max 50MB)
- Verify the PDF contains sheet music notation

### Audio Analysis Issues
If analysis is inaccurate:
- Record in a quiet environment
- Speak/play directly into the microphone
- Ensure proper instrument selection
- Try disabling dynamics feedback initially

## Future Enhancements

- [ ] Mobile app support (iOS/Android)
- [ ] Real-time feedback during playing
- [ ] Collaborative practice sessions
- [ ] Integration with popular music notation software
- [ ] Advanced ML models for improved OMR accuracy
- [ ] Support for ensemble/group practice
- [ ] Video recording and analysis
- [ ] Gamification and achievement system

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Sheet music analysis powered by computer vision and machine learning
- Audio processing using industry-standard libraries
- Inspired by the need for accessible, intelligent music practice tools

## Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Contact: [Add your contact information]

---

**Made with ❤️ for musicians everywhere**