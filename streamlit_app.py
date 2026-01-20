"""
Main Streamlit application for the Music Practice Feedback System
Streamlit Cloud Deployment - Maintains Full OMR Power
"""
import os
import streamlit as st
from pathlib import Path
import tempfile
from datetime import datetime
import logging
import time

# Real implementations - Full OMR Power Maintained
from src.audiveris_omr import AudiverisOMR
from src.oemer_omr import OemerOMR
from src.real_audio_analyzer import RealAudioAnalyzer
from src.real_omr_system import RealOMRSystem
from src.real_feedback_generator import RealFeedbackGenerator
from src.session_manager import SessionManager
from src.database import init_db
from src.auth_streamlit import AuthManager  # Streamlit-compatible auth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration - Optimized for Streamlit Cloud
st.set_page_config(
    page_title="🎵 Mugic - AI Music Practice Feedback",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/masterofmagic999/mugic',
        'Report a bug': 'https://github.com/masterofmagic999/mugic/issues',
        'About': '# Mugic 🎵\n**AI-Powered Music Practice Feedback**\nWith Advanced OMR Technology'
    }
)

# Initialize directories
UPLOAD_FOLDER = Path('uploads')
RECORDINGS_FOLDER = Path('recordings')
UPLOAD_FOLDER.mkdir(exist_ok=True)
RECORDINGS_FOLDER.mkdir(exist_ok=True)

# Initialize database
@st.cache_resource
def initialize_database():
    """Initialize database once"""
    init_db()
    return True

initialize_database()

# Initialize OMR system
@st.cache_resource
def initialize_omr():
    """Initialize OMR system with fallback priority"""
    omr_system = None
    omr_method = "Unknown"
    
    try:
        # Try Audiveris first (best quality OMR, but requires Java)
        audiveris_omr = AudiverisOMR()
        if audiveris_omr.is_available():
            omr_system = audiveris_omr
            omr_method = "Audiveris OMR"
            logger.info("✓ Using Audiveris OMR (GitHub open-source)")
    except Exception as e:
        logger.warning(f"Audiveris initialization error: {e}")
    
    # Try OEMER as second choice
    if omr_system is None:
        try:
            oemer_omr = OemerOMR()
            if oemer_omr.is_available():
                omr_system = oemer_omr
                omr_method = "OEMER (End-to-end OMR)"
                logger.info("✓ Using OEMER OMR by BreezeWhite")
            else:
                logger.info("⚠ OEMER not found, trying fallback")
        except Exception as e:
            logger.warning(f"OEMER initialization error: {e}")
    
    # Final fallback to computer vision-based OMR
    if omr_system is None:
        try:
            omr_system = RealOMRSystem()
            omr_method = "Computer Vision OMR"
            logger.info("⚠ Using computer vision OMR fallback")
        except Exception as e:
            logger.error(f"All OMR systems failed: {e}")
            raise RuntimeError("No OMR system available")
    
    return omr_system, omr_method

# Initialize audio analyzer
@st.cache_resource
def initialize_audio_analyzer():
    """Initialize audio analyzer"""
    try:
        audio_analyzer = RealAudioAnalyzer()
        logger.info("✓ Using Spotify basic-pitch for audio transcription")
        return audio_analyzer
    except Exception as e:
        logger.error(f"Audio analyzer initialization error: {e}")
        raise RuntimeError("basic-pitch is required. Install with: pip install basic-pitch")

# Initialize components
omr_system, omr_method = initialize_omr()
audio_analyzer = initialize_audio_analyzer()
feedback_generator = RealFeedbackGenerator()
session_manager = SessionManager()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_piece_id' not in st.session_state:
    st.session_state.current_piece_id = None
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None
if 'audio_file_path' not in st.session_state:
    st.session_state.audio_file_path = None

# Fabulous Custom CSS - Premium UI/UX
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Hero Header with gradient text */
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem;
        font-weight: 700;
        padding: 1rem 0;
        text-shadow: 0 4px 6px rgba(0,0,0,0.1);
        animation: fadeInDown 0.8s ease-out;
    }
    
    /* Animated gradient background for cards */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Info box - Modern glass morphism */
    .info-box {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-left: 5px solid #667eea;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
        animation: slideInLeft 0.6s ease-out;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .info-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3);
    }
    
    /* Success box - Vibrant green */
    .success-box {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        border-left: 5px solid #28a745;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(40, 167, 69, 0.2);
        color: #155724;
        font-weight: 500;
        animation: slideInRight 0.6s ease-out;
    }
    
    /* Warning box - Warm yellow/orange */
    .warning-box {
        background: linear-gradient(135deg, #FFD89B 0%, #19547B 100%);
        border-left: 5px solid #ff9800;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(255, 152, 0, 0.2);
        color: #1a1a1a;
        font-weight: 500;
    }
    
    /* Score display - Animated and stunning */
    .score-display {
        font-size: 6rem;
        font-weight: 800;
        text-align: center;
        margin: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: scorePopIn 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        text-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    @keyframes scorePopIn {
        0% { transform: scale(0); opacity: 0; }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    /* Metric cards - Premium design */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transform: rotate(45deg);
        transition: all 0.5s ease;
    }
    
    .metric-card:hover::before {
        left: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.3);
    }
    
    /* Button styling - Premium gradient buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 50px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* Progress bars - Animated gradient */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 100%;
        animation: gradientShift 3s ease infinite;
    }
    
    /* File uploader - Modern style */
    .uploadedFile {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 1rem;
        background: rgba(102, 126, 234, 0.05);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Animation keyframes */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Metric value styling */
    .css-1xarl3l {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 1rem 2rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.1);
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 10px;
        font-weight: 600;
        border-left: 4px solid #667eea;
    }
    
    /* Toast/Alert messages */
    .stAlert {
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid rgba(102, 126, 234, 0.3);
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Select box styling */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    /* Checkbox styling */
    .stCheckbox {
        background: rgba(102, 126, 234, 0.05);
        padding: 0.5rem;
        border-radius: 8px;
    }
    
    /* Badge/Tag styling */
    .badge {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        font-size: 0.875rem;
        font-weight: 600;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 50px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

def show_authentication_page():
    """Display authentication (login/register) page"""
    st.markdown("<h1 class='main-header'>🎵 Mugic - AI-Powered Music Practice Feedback</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Sign In")
        with st.form("login_form"):
            username = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In")
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    success, message, user_data, tokens = AuthManager.authenticate_user(
                        username_or_email=username,
                        password=password
                    )
                    
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user = user_data
                        st.success(f"Welcome back, {user_data['username']}!")
                        st.rerun()
                    else:
                        st.error(message)
    
    with tab2:
        st.subheader("Create Account")
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            new_full_name = st.text_input("Full Name (optional)")
            register = st.form_submit_button("Register")
            
            if register:
                if not new_username or not new_email or not new_password:
                    st.error("Username, email, and password are required")
                else:
                    success, message, user_data = AuthManager.register_user(
                        username=new_username,
                        email=new_email,
                        password=new_password,
                        full_name=new_full_name
                    )
                    
                    if success:
                        st.success(message)
                        st.info("You can now sign in with your credentials")
                    else:
                        st.error(message)
    
    st.markdown("---")
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    st.markdown("""
    ### Continue as Guest
    You can use Mugic without an account, but your progress won't be saved.
    """)
    if st.button("Continue as Guest"):
        st.session_state.authenticated = True
        st.session_state.user = {'username': 'Guest', 'id': None}
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def show_main_application():
    """Display main application interface with fabulous UI"""
    
    # Hero Header
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='font-size: 3.5rem; font-weight: 800; 
                       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       margin-bottom: 0.5rem;'>
                🎵 Mugic
            </h1>
            <p style='font-size: 1.2rem; color: #6c757d; font-weight: 500;'>
                AI-Powered Music Practice Feedback
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # User info and OMR status banner
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.session_state.user:
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            padding: 1rem; border-radius: 15px; text-align: center; color: white;'>
                    <div style='font-size: 2rem;'>👤</div>
                    <div style='font-weight: 600;'>{st.session_state.user['username']}</div>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # OMR Power Status - Highlighting the Technology
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
                        padding: 1.5rem; border-radius: 20px; text-align: center;
                        box-shadow: 0 8px 32px rgba(132, 250, 176, 0.3);
                        animation: slideInRight 0.6s ease-out;'>
                <div style='font-size: 1.1rem; font-weight: 700; color: #155724; margin-bottom: 0.5rem;'>
                    🚀 POWERED BY
                </div>
                <div style='font-size: 1.3rem; font-weight: 800; color: #0c3d20;'>
                    {omr_method}
                </div>
                <div style='font-size: 0.9rem; color: #155724; margin-top: 0.3rem;'>
                    Audio: Spotify basic-pitch AI
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.current_piece_id = None
            st.session_state.current_analysis = None
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📚 Your Music Library")
        
        # Get all pieces
        try:
            pieces = session_manager.get_all_pieces()
            if pieces:
                st.write(f"Total pieces: {len(pieces)}")
                selected_piece = st.selectbox(
                    "Load existing piece",
                    options=[None] + pieces,
                    format_func=lambda x: "Select a piece..." if x is None else f"{x['filename']} ({x['session_count']} sessions)"
                )
                
                if selected_piece:
                    if st.button("Load Selected Piece"):
                        st.session_state.current_piece_id = selected_piece['id']
                        st.session_state.current_analysis = selected_piece['analysis']
                        st.success(f"Loaded: {selected_piece['filename']}")
                        st.rerun()
            else:
                st.info("No pieces yet. Upload your first sheet music!")
        except Exception as e:
            st.error(f"Error loading pieces: {e}")
        
        st.markdown("---")
        st.header("⚙️ Settings")
        st.info("System initialized with real AI components")
    
    # Main content area
    if st.session_state.current_piece_id is None:
        # Upload new sheet music
        show_upload_section()
    else:
        # Practice with existing piece
        show_practice_section()

def show_upload_section():
    """Display sheet music upload section with beautiful UI"""
    
    # Stunning header
    st.markdown("""
        <div style='text-align: center; padding: 2rem; 
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                    border-radius: 20px; margin-bottom: 2rem;
                    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>📄</div>
            <h2 style='color: #667eea; font-weight: 700; margin-bottom: 0.5rem;'>
                Upload Your Sheet Music
            </h2>
            <p style='color: #6c757d; font-size: 1.1rem;'>
                Powered by industry-leading OMR technology
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # OMR Technology Info Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class='metric-card'>
                <div style='font-size: 2.5rem; text-align: center; margin-bottom: 0.5rem;'>🧠</div>
                <div style='font-weight: 700; text-align: center; color: #667eea;'>Neural OMR</div>
                <div style='text-align: center; color: #6c757d; font-size: 0.9rem;'>
                    Deep learning models for accurate music recognition
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class='metric-card'>
                <div style='font-size: 2.5rem; text-align: center; margin-bottom: 0.5rem;'>🎼</div>
                <div style='font-weight: 700; text-align: center; color: #764ba2;'>Full Analysis</div>
                <div style='text-align: center; color: #6c757d; font-size: 0.9rem;'>
                    Notes, rhythms, tempo, dynamics & more
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class='metric-card'>
                <div style='font-size: 2.5rem; text-align: center; margin-bottom: 0.5rem;'>⚡</div>
                <div style='font-weight: 700; text-align: center; color: #667eea;'>High Speed</div>
                <div style='text-align: center; color: #6c757d; font-size: 0.9rem;'>
                    Fast processing with {omr_method}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Upload area
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    st.markdown("""
    ### What our OMR system extracts:
    
    ✨ **Musical Content:**
    - 🎵 Individual notes with precise pitches
    - 🥁 Rhythmic patterns and note durations
    - 🎹 Key signatures and accidentals
    - ⏱️ Time signatures and tempo markings
    
    ✨ **Performance Details:**
    - 🔊 Dynamic markings (piano, forte, etc.)
    - 🎭 Articulation symbols (staccato, legato)
    - 📈 Crescendos and diminuendos
    - 🎼 Multi-staff arrangements
    """)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # File uploader with enhanced styling
    uploaded_file = st.file_uploader(
        "📎 Choose your PDF sheet music file",
        type=['pdf'],
        help="Upload a clear, high-resolution PDF for best OMR results"
    )
    
    if uploaded_file is not None:
        # Show file info
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
        st.markdown(f"""
            <div class='success-box'>
                <strong>✓ File Ready:</strong> {uploaded_file.name} ({file_size:.2f} MB)
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Analyze with Powerful OMR", type="primary", use_container_width=True):
            # Progress indicator
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Save uploaded file
                status_text.markdown("**Step 1/4:** Saving uploaded file...")
                progress_bar.progress(25)
                file_path = UPLOAD_FOLDER / uploaded_file.name
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                time.sleep(0.3)
                
                # Analyze with OMR
                status_text.markdown(f"**Step 2/4:** Running {omr_method} analysis...")
                progress_bar.progress(50)
                logger.info(f"Analyzing sheet music: {uploaded_file.name}")
                analysis = omr_system.analyze_sheet_music(str(file_path))
                time.sleep(0.3)
                
                # Create piece entry
                status_text.markdown("**Step 3/4:** Saving to your library...")
                progress_bar.progress(75)
                piece_id = session_manager.create_piece(uploaded_file.name, analysis)
                time.sleep(0.3)
                
                # Update session state
                st.session_state.current_piece_id = piece_id
                st.session_state.current_analysis = analysis
                
                # Complete
                status_text.markdown("**Step 4/4:** Analysis complete!")
                progress_bar.progress(100)
                time.sleep(0.5)
                
                # Success animation
                st.balloons()
                
                # Display stunning results
                st.markdown("""
                    <div class='success-box' style='text-align: center; font-size: 1.2rem;'>
                        <div style='font-size: 3rem; margin-bottom: 1rem;'>🎉</div>
                        <strong>Sheet Music Analyzed Successfully!</strong><br>
                        <span style='font-size: 0.9rem;'>Powered by {}</span>
                    </div>
                """.format(analysis.get('analysis_method', 'OMR')), unsafe_allow_html=True)
                
                # Display analysis results in stunning cards
                st.markdown("### 📊 Analysis Results")
                
                col1, col2, col3, col4 = st.columns(4)
                
                metrics = [
                    ("🎵", "Notes Detected", analysis.get('total_notes', len(analysis.get('notes', []))), col1),
                    ("⏱️", "Tempo", f"{analysis.get('tempo', 'N/A')} BPM", col2),
                    ("🎼", "Time Signature", analysis.get('time_signature', 'N/A'), col3),
                    ("🎹", "Key", analysis.get('key_signature', 'N/A'), col4)
                ]
                
                for icon, label, value, col in metrics:
                    with col:
                        st.markdown(f"""
                            <div class='metric-card' style='text-align: center;'>
                                <div style='font-size: 2rem;'>{icon}</div>
                                <div style='font-size: 2rem; font-weight: 800; 
                                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                            -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                                    {value}
                                </div>
                                <div style='color: #6c757d; font-size: 0.9rem; font-weight: 600;'>{label}</div>
                            </div>
                        """, unsafe_allow_html=True)
                
                # Additional info
                if 'confidence' in analysis:
                    st.markdown("<br>", unsafe_allow_html=True)
                    confidence_pct = int(analysis['confidence'] * 100)
                    st.progress(analysis['confidence'], text=f"OMR Confidence: {confidence_pct}%")
                
                st.markdown("""
                    <div class='info-box' style='text-align: center;'>
                        <strong>✨ Ready to practice!</strong> Scroll down to record your performance.
                    </div>
                """, unsafe_allow_html=True)
                
                time.sleep(1)
                st.rerun()
                    
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.markdown(f"""
                    <div class='warning-box'>
                        <strong>⚠️ Analysis Error:</strong><br>
                        {str(e)}<br><br>
                        <em>Please ensure your PDF contains clear sheet music notation.</em>
                    </div>
                """, unsafe_allow_html=True)
                logger.error(f"Error analyzing sheet music: {str(e)}")

def show_practice_section():
    """Display practice/recording section"""
    st.header("🎤 Practice Session")
    
    # Get current piece info
    piece = session_manager.get_piece(st.session_state.current_piece_id)
    if not piece:
        st.error("Piece not found")
        return
    
    st.markdown(f"**Current Piece:** {piece['filename']}")
    
    # Display piece analysis
    with st.expander("📊 Sheet Music Analysis", expanded=False):
        analysis = st.session_state.current_analysis
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Notes", analysis.get('total_notes', 'N/A'))
        with col2:
            st.metric("Tempo", f"{analysis.get('tempo', 'N/A')} BPM")
        with col3:
            st.metric("Time Signature", analysis.get('time_signature', 'N/A'))
        with col4:
            st.metric("Key", analysis.get('key_signature', 'N/A'))
        
        st.write("**Analysis Method:**", analysis.get('analysis_method', 'OMR'))
        if 'confidence' in analysis:
            st.progress(analysis['confidence'], text=f"Confidence: {analysis['confidence']:.0%}")
    
    # Instrument selection
    instruments = [
        ('flute', 'Flute'), ('piccolo', 'Piccolo'),
        ('clarinet', 'Clarinet'), ('bass_clarinet', 'Bass Clarinet'),
        ('oboe', 'Oboe'), ('bassoon', 'Bassoon'),
        ('saxophone_soprano', 'Soprano Saxophone'), ('saxophone_alto', 'Alto Saxophone'),
        ('saxophone_tenor', 'Tenor Saxophone'), ('saxophone_baritone', 'Baritone Saxophone'),
        ('trumpet', 'Trumpet'), ('cornet', 'Cornet'),
        ('french_horn', 'French Horn'), ('trombone', 'Trombone'),
        ('euphonium', 'Euphonium'), ('tuba', 'Tuba'),
        ('xylophone', 'Xylophone'), ('marimba', 'Marimba'),
        ('vibraphone', 'Vibraphone'), ('glockenspiel', 'Glockenspiel'),
        ('timpani', 'Timpani')
    ]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        instrument = st.selectbox(
            "Select your instrument",
            options=[i[0] for i in instruments],
            format_func=lambda x: next(i[1] for i in instruments if i[0] == x)
        )
    with col2:
        disable_dynamics = st.checkbox("Disable dynamics feedback", value=False, 
                                       help="Focus on notes and rhythm only")
    
    st.markdown("---")
    
    # Audio recording section
    st.subheader("🎙️ Record Your Performance")
    
    st.markdown("<div class='warning-box'>", unsafe_allow_html=True)
    st.markdown("""
    **Recording Instructions:**
    1. Click the microphone button below to record
    2. Play your piece
    3. Click stop when finished
    4. Click "Analyze Performance" to get feedback
    """)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Use Streamlit's audio_input (available in newer versions) or file uploader as fallback
    try:
        audio_data = st.audio_input("Record your performance")
        if audio_data is not None:
            # Save the recorded audio
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"recording_{timestamp}.wav"
            audio_path = RECORDINGS_FOLDER / audio_filename
            
            with open(audio_path, 'wb') as f:
                f.write(audio_data.getbuffer())
            
            st.session_state.audio_file_path = str(audio_path)
            st.success("✓ Recording saved!")
    except AttributeError:
        # Fallback for older Streamlit versions
        st.info("Upload a pre-recorded audio file (WAV, MP3, or OGG)")
        uploaded_audio = st.file_uploader("Upload recording", type=['wav', 'mp3', 'ogg'])
        
        if uploaded_audio is not None:
            # Save the uploaded audio
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"recording_{timestamp}.{uploaded_audio.name.split('.')[-1]}"
            audio_path = RECORDINGS_FOLDER / audio_filename
            
            with open(audio_path, 'wb') as f:
                f.write(uploaded_audio.getbuffer())
            
            st.session_state.audio_file_path = str(audio_path)
            st.success("✓ Audio file uploaded!")
    
    # Analyze performance button
    if st.session_state.audio_file_path:
        if st.button("🎯 Analyze Performance", type="primary"):
            with st.spinner("Analyzing your performance with AI..."):
                try:
                    # Analyze audio
                    audio_analysis = audio_analyzer.analyze(
                        st.session_state.audio_file_path,
                        instrument=instrument,
                        apply_noise_reduction=True
                    )
                    logger.info(f"Audio analysis complete: {audio_analysis.get('total_notes', 0)} notes")
                    
                    # Generate feedback
                    feedback = feedback_generator.generate_feedback(
                        sheet_music_analysis=st.session_state.current_analysis,
                        audio_analysis=audio_analysis,
                        disable_dynamics=disable_dynamics
                    )
                    
                    # Save session
                    session_id = session_manager.save_session(
                        piece_id=st.session_state.current_piece_id,
                        audio_analysis=audio_analysis,
                        feedback=feedback,
                        instrument=instrument
                    )
                    
                    # Get comparison
                    comparison = session_manager.compare_with_previous(
                        st.session_state.current_piece_id,
                        session_id
                    )
                    
                    # Display results
                    display_feedback(feedback, comparison)
                    
                except Exception as e:
                    st.error(f"Error analyzing performance: {str(e)}")
                    logger.error(f"Error analyzing performance: {str(e)}")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Practice Again"):
            st.session_state.audio_file_path = None
            st.rerun()
    with col2:
        if st.button("📄 Upload New Piece"):
            st.session_state.current_piece_id = None
            st.session_state.current_analysis = None
            st.session_state.audio_file_path = None
            st.rerun()

def display_feedback(feedback, comparison):
    """Display feedback results"""
    st.markdown("---")
    st.header("📊 Performance Feedback")
    
    # Overall score
    overall_score = feedback.get('overall_score', 0)
    st.markdown(f"<div class='score-display' style='color: {'#28a745' if overall_score >= 70 else '#ffc107' if overall_score >= 50 else '#dc3545'}'>{overall_score}</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.5rem;'>Overall Score</p>", unsafe_allow_html=True)
    
    # Detailed metrics
    st.subheader("Detailed Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pitch
        pitch = feedback.get('pitch', {})
        st.markdown("#### 🎵 Pitch Accuracy")
        st.progress(pitch.get('score', 0) / 100)
        st.write(f"**Score:** {pitch.get('score', 0)}/100")
        st.write(f"**Accuracy:** {pitch.get('accuracy', 0):.1f}%")
        if pitch.get('total_notes_compared'):
            st.write(f"**Notes Compared:** {pitch.get('total_notes_compared', 0)}")
        
        # Tempo
        tempo = feedback.get('tempo', {})
        st.markdown("#### ⏱️ Tempo Control")
        st.progress(tempo.get('score', 0) / 100)
        st.write(f"**Score:** {tempo.get('score', 0)}/100")
        st.write(f"**Your Tempo:** {tempo.get('performed_tempo', 0):.0f} BPM")
        st.write(f"**Expected:** {tempo.get('expected_tempo', 0):.0f} BPM")
    
    with col2:
        # Rhythm
        rhythm = feedback.get('rhythm', {})
        st.markdown("#### 🥁 Rhythm Consistency")
        st.progress(rhythm.get('score', 0) / 100)
        st.write(f"**Score:** {rhythm.get('score', 0)}/100")
        st.write(f"**Consistency:** {rhythm.get('consistency', 0):.1f}%")
        
        # Dynamics (if enabled)
        dynamics = feedback.get('dynamics', {})
        if dynamics:
            st.markdown("#### 🔊 Dynamics")
            st.progress(dynamics.get('score', 0) / 100)
            st.write(f"**Score:** {dynamics.get('score', 0)}/100")
            st.write(f"**Range:** {dynamics.get('range', 0):.1f} dB")
    
    # Recommendations
    st.subheader("💡 Recommendations")
    recommendations = feedback.get('recommendations', [])
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
    else:
        st.info("Great job! Keep practicing to maintain your performance.")
    
    # Comparison with previous attempts
    if comparison and comparison.get('has_previous'):
        st.markdown("---")
        st.subheader("📈 Progress Comparison")
        
        score_change = comparison.get('score_change', 0)
        if score_change > 0:
            st.success(f"🎉 Your score improved by {score_change} points!")
        elif score_change < 0:
            st.warning(f"Your score decreased by {abs(score_change)} points. Keep practicing!")
        else:
            st.info("Your score is the same as last time.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**✅ What Improved:**")
            improvements = comparison.get('improvements', [])
            if improvements:
                for imp in improvements:
                    st.markdown(f"- {imp}")
            else:
                st.write("No improvements detected")
        
        with col2:
            st.markdown("**⚠️ Needs Work:**")
            needs_work = comparison.get('needs_work', [])
            if needs_work:
                for need in needs_work:
                    st.markdown(f"- {need}")
            else:
                st.write("Nothing specific needs work")
        
        st.write(f"**Total Practice Sessions:** {comparison.get('total_sessions', 1)}")

# Main application logic
def main():
    """Main application entry point"""
    if not st.session_state.authenticated:
        show_authentication_page()
    else:
        show_main_application()

if __name__ == "__main__":
    main()
