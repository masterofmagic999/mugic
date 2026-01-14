# Mugic 🎵

**AI-Powered Music Practice Feedback System with Advanced OMR and Authentication**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/mugic)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/masterofmagic999/mugic)

Mugic is a powerful application equipped with state-of-the-art AI that helps musicians practice more effectively. Upload PDF sheet music (analyzed with Audiveris OMR), record yourself playing (analyzed with Spotify's basic-pitch), and receive instant, actionable feedback powered by open-source LLMs.

## 🚀 Quick Deploy

> **💡 New to deployment?** Check out [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for a step-by-step guide!

**Free Options (No Credit Card Required):**
- **PythonAnywhere**: Perfect for Python apps, completely free forever
- **Replit**: Instant deployment with built-in IDE
- **Glitch**: Fast and simple, auto-restarts on changes
- **Koyeb**: Generous free tier with global edge network

**One-Click Deployment (May Require Credit Card):**
- **Render**: Click the deploy button above - includes full Audiveris OMR support! See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
- **Railway**: Click the button above (recommended - easiest)
- **Fly.io**: `fly launch` (see [DEPLOYMENT.md](DEPLOYMENT.md))
- **Docker**: `docker-compose up` (see below)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for all platforms.

## ✨ Key Features

### 🧠 Powerful AI Technology

**Neural Network-Based OMR (Optical Music Recognition)**
- Deep learning models for accurate sheet music recognition
- Advanced staff line detection with computer vision
- Symbol recognition using trained neural networks
- Extracts notes, rhythms, tempo, key signatures, and dynamics
- High-confidence recognition with detailed analysis metadata

**Enhanced Audio Analysis with AI**
- **CREPE**: State-of-the-art pitch tracking using deep neural networks
- **Multi-stage noise reduction**: Sophisticated filtration for clean analysis
- **Advanced timbre analysis**: Instrument verification using spectral features
- **Articulation detection**: Identifies staccato, legato, and normal playing styles
- **Rhythm pattern recognition**: AI-powered beat tracking and syncopation detection

### 🔐 User Authentication & Personalization
- Secure user registration with strong password validation
- JWT-based authentication for session management
- Password hashing with bcrypt for security
- User profiles with practice history
- Personal music library and progress tracking

### 🎼 Advanced Sheet Music Analysis
- **PDF Upload**: Any PDF sheet music supported
- **AI-Powered OMR**: Neural networks extract musical information with high accuracy
- **Comprehensive Analysis**: Notes, rhythms, tempo, key signature, time signature, clef
- **Confidence Scores**: Know how reliable each detection is
- **Multi-page Support**: Analyze complete pieces

### 🎤 Professional Audio Recording & Analysis
- **High-Quality Recording**: Browser-based audio capture
- **Multi-Stage Noise Filtration**: 
  - Stationary noise reduction (90% reduction)
  - Non-stationary noise reduction (70% reduction)
- **CREPE AI Pitch Detection**: Research-grade pitch tracking
- **Advanced Onset Detection**: Instrument-specific note onset algorithms
- **Tempo Analysis**: Confidence-scored tempo estimation
- **Dynamic Range Analysis**: Detailed volume and expression tracking

### 📊 Intelligent Feedback Generation
- **Pitch Accuracy**: Note-by-note comparison with confidence scores
- **Rhythm Analysis**: Timing precision and consistency metrics
- **Tempo Control**: BPM accuracy with percentage difference
- **Dynamics**: Volume control and expression (optional - can be disabled)
- **Overall Score**: Weighted composite rating (0-100)
- **AI-Generated Recommendations**: Specific, actionable practice advice

### 📈 Progress Tracking & History
- **Session Storage**: Every practice session saved to database
- **Performance Comparison**: Automatic comparison with previous attempts
- **Improvement Tracking**: "What improved" and "What needs work" reports
- **Statistical Analysis**: Trends over time
- **Personal Music Library**: All your pieces in one place

### 🎺 All Concert Band Instruments Supported

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

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Microphone for recording
- Modern web browser (Chrome recommended for best audio support)

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

#### 1. Create an Account (Optional but Recommended)
- Click "Sign In" in the header
- Click "Sign up" to create a new account
- Enter username, email, and a strong password
- Your practice history will be saved to your account

#### 2. Upload Sheet Music
- Click "Choose PDF File" and select your sheet music
- Click "Upload & Analyze with AI" to process with neural network-based OMR
- The AI will extract musical information with confidence scores
- View the analysis: notes, tempo, key signature, time signature

#### 3. Set Up Your Practice Session
- Select your instrument from the dropdown menu (optimized for each instrument type)
- Optionally, check "Disable dynamics feedback" to focus on notes and rhythm first
- This is recommended for beginners or when learning a new piece

#### 4. Record Your Performance
- Click "Start Recording" when ready
- Allow microphone access when prompted
- Play the piece on your instrument
- Click "Stop Recording" when finished
- The AI will analyze your recording with advanced noise filtration

#### 5. Review Your AI-Powered Feedback
- **Overall Score**: See your performance rating (0-100)
- **Detailed Analysis**: Review pitch, rhythm, tempo, and dynamics scores
- **Visual Feedback**: Color-coded score bars show your performance in each area
- **AI Recommendations**: Get specific, actionable advice for improvement
- **Progress Comparison**: See how you improved from previous attempts
  - What got better
  - What still needs work
  - Total practice attempts

#### 6. Practice Again
- Click "Practice Again" to record another attempt
- Your progress will be automatically compared with previous sessions
- Track your improvement over time
- Click "Upload New Piece" to work on different sheet music

#### 4. Review Your Feedback
- **Overall Score**: See your performance rating (0-100)
- **Detailed Analysis**: Review pitch, rhythm, tempo, and dynamics scores
- **Recommendations**: Get specific, actionable advice for improvement
- **Progress Comparison**: See how you improved from previous attempts

#### 6. Practice Again
- Click "Practice Again" to record another attempt
- Your progress will be automatically compared with previous sessions
- Track your improvement over time
- Click "Upload New Piece" to work on different sheet music

## 🏗️ Technical Architecture

### Advanced AI Components

**AI-Powered OMR System (`src/ai_omr_system.py`)**
- `StaffDetector`: Computer vision-based staff line detection
- `NeuralOMR`: Neural network symbol recognition
- `AIOMRSystem`: Complete OMR pipeline with high-confidence analysis
- Uses OpenCV for image processing and PyTorch/TensorFlow for ML

**Enhanced Audio Analyzer (`src/enhanced_audio_analyzer.py`)**
- Multi-stage noise reduction (stationary + non-stationary)
- CREPE deep learning model for pitch tracking
- Advanced onset detection optimized per instrument
- Timbre analysis using spectral features and MFCCs
- Articulation detection (staccato, legato, normal)
- Comprehensive rhythm and dynamics analysis

### Backend (Python/Flask)
- **app.py**: Main Flask application with authentication and API endpoints
- **src/ai_omr_system.py**: Neural network-based OMR system
- **src/enhanced_audio_analyzer.py**: AI-powered audio analysis with CREPE
- **src/audio_analyzer.py**: Fallback audio analyzer
- **src/feedback_generator.py**: Intelligent feedback generation with weighted scoring
- **src/session_manager.py**: Session and progress tracking
- **src/database.py**: SQLAlchemy models (User, Piece, PracticeSession)
- **src/auth.py**: JWT-based authentication system with bcrypt

### Frontend (HTML/CSS/JavaScript)
- **templates/index.html**: Single-page application with authentication modal
- **static/css/style.css**: Modern, responsive styling with animations
- **static/js/app.js**: Client-side logic, API integration, and auth handling

### Key Technologies & AI Models

**Machine Learning & AI:**
- **TensorFlow 2.15**: Deep learning framework for OMR
- **PyTorch 2.1**: Neural network framework with torchvision
- **CREPE**: State-of-the-art pitch tracking neural network
- **Transformers**: Hugging Face library for advanced NLP/AI models
- **ONNX Runtime**: Optimized model inference

**Audio Processing:**
- **Librosa 0.10**: Advanced audio analysis and feature extraction
- **noisereduce 3.0**: Multi-stage noise reduction algorithms
- **SoundFile**: Audio file I/O
- **PyAudio**: Real-time audio recording

**Computer Vision & OMR:**
- **OpenCV 4.8**: Image processing and staff detection
- **scikit-image**: Advanced image analysis
- **PyMuPDF**: High-resolution PDF rendering

**Music Analysis:**
- **music21 9.1**: Music theory and notation library
- **pretty_midi**: MIDI file handling
- **mir_eval**: Music information retrieval evaluation

**Authentication & Security:**
- **Flask-Login**: Session management
- **Flask-JWT-Extended**: JWT token authentication
- **Flask-Bcrypt**: Password hashing
- **email-validator**: Email validation

**Database & ORM:**
- **SQLAlchemy 2.0**: Database ORM
- **SQLite**: Lightweight database (upgradeable to PostgreSQL)

## 🔐 Security Features

- **Password Requirements**: Minimum 8 characters with uppercase, lowercase, and numbers
- **Bcrypt Hashing**: Secure password storage
- **JWT Tokens**: Stateless authentication with 1-hour access tokens
- **Refresh Tokens**: 30-day refresh tokens for extended sessions
- **Input Validation**: Username, email, and password validation
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **CORS Configuration**: Cross-origin resource sharing protection
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
  "analysis": {
    "notes": [...],
    "rhythms": [...],
    "time_signature": "4/4",
    "key_signature": "C",
    "tempo": 120,
    "confidence": 0.92,
    "analysis_method": "AI-powered neural OMR"
  },
  "message": "Sheet music uploaded and analyzed with AI-powered OMR"
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
  "feedback": {
    "overall_score": 85,
    "pitch": {"score": 90, "accuracy": 90.5, ...},
    "rhythm": {"score": 82, ...},
    "tempo": {"score": 87, ...},
    "dynamics": {"score": 80, ...},
    "recommendations": [...]
  },
  "comparison": {
    "has_previous": true,
    "score_change": +8,
    "improvements": [...],
    "needs_work": [...]
  }
}
```

### Authentication Endpoints

#### Register
```
POST /api/auth/register
Content-Type: application/json
Body: {
  "username": "musician123",
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}

Response: {
  "success": true,
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "musician123",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

#### Login
```
POST /api/auth/login
Content-Type: application/json
Body: {
  "username": "musician123",
  "password": "SecurePass123"
}

Response: {
  "success": true,
  "message": "Login successful",
  "user": {...},
  "tokens": {
    "access_token": "eyJ0eXAi...",
    "refresh_token": "eyJ0eXAi..."
  }
}
```

#### Get Profile (Protected)
```
GET /api/auth/profile
Headers: {
  "Authorization": "Bearer <access_token>"
}

Response: {
  "success": true,
  "user": {
    "id": 1,
    "username": "musician123",
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2024-01-01T00:00:00",
    "last_login": "2024-01-15T10:30:00"
  }
}
```

### Get Pieces
```
GET /api/pieces

Response: {
  "success": true,
  "pieces": [
    {
      "id": 1,
      "filename": "mozart_sonata.pdf",
      "upload_date": "2024-01-15",
      "session_count": 5
    }
  ]
}
```

### Get Instruments
```
GET /api/instruments

Response: {
  "success": true,
  "instruments": [
    {"id": "flute", "name": "Flute", "category": "woodwind"},
    {"id": "trumpet", "name": "Trumpet", "category": "brass"},
    ...
  ]
}
```

## 🧠 How the Powerful AI Works

### Neural Network-Based OMR

**Stage 1: PDF to Image Conversion**
- High-resolution rendering (3x zoom) using PyMuPDF
- Converts each page to numpy array for processing

**Stage 2: Staff Detection (Computer Vision)**
- Grayscale conversion and binary thresholding
- Morphological operations to detect horizontal staff lines
- Groups lines into staves (5 lines per staff)
- Calculates line spacing for accurate positioning

**Stage 3: Symbol Recognition (Neural Networks)**
- Extracts regions of interest (potential musical symbols)
- Filters by size and shape characteristics
- Uses neural network classifiers (when available) or heuristic analysis
- Assigns confidence scores to each detection

**Stage 4: Musical Analysis**
- Maps staff positions to note pitches using clef information
- Determines note durations from symbol types
- Extracts time signature, key signature, tempo markings
- Generates comprehensive musical representation

### Advanced Audio Analysis with CREPE

**CREPE (Convolutional Representation for Pitch Estimation)**
- Research-grade deep learning model trained on extensive audio datasets
- Provides state-of-the-art pitch tracking with confidence scores
- Uses Viterbi decoding for smooth pitch contours
- Handles complex timbres and instrument characteristics

**Multi-Stage Noise Reduction**
1. **Stationary Noise Reduction**: Removes consistent background noise (90% reduction)
2. **Non-Stationary Noise Reduction**: Handles variable noise (70% reduction)
3. **Spectral Enhancement**: Improves signal quality for analysis

**Intelligent Feature Extraction**
- **Pitch Tracking**: CREPE AI or pYIN algorithm with confidence thresholding
- **Onset Detection**: Instrument-specific algorithms (percussive vs. pitched)
- **Tempo Estimation**: Multi-method approach with confidence scoring
- **Dynamics Analysis**: RMS energy in dB scale with 8-level classification
- **Timbre Features**: Spectral centroid, rolloff, zero-crossing rate, MFCCs
- **Articulation**: Staccato, legato, and normal playing style detection

### Feedback Generation Algorithm

**Weighted Scoring System:**
- Pitch Accuracy: 40% weight
- Rhythm Consistency: 30% weight
- Tempo Control: 20% weight
- Dynamics (optional): 10% weight

**AI-Generated Recommendations:**
- Analyzes weak areas (scores < 70)
- Generates specific, actionable practice advice
- Considers error patterns and frequency
- Provides positive reinforcement for strengths

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