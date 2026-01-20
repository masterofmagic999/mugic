# 🎵 Mugic - Streamlit Cloud Version

This is the Streamlit Cloud deployment version of Mugic with a fabulous UI and maintained OMR power!

## Quick Deploy to Streamlit Cloud

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

### One-Click Deployment

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select this repository
5. Set main file: `streamlit_app.py`
6. Click "Deploy"!

That's it! Your Mugic app will be live in minutes.

## Features

✨ **Fabulous UI/UX**
- Premium gradient design with animations
- Glassmorphism effects
- Smooth transitions and hover effects
- Responsive layout

🎼 **Powerful OMR**
- Maintains full OMR capabilities
- Audiveris support (local/Docker)
- OEMER for Streamlit Cloud (excellent quality)
- Computer Vision fallback

🎤 **Audio Analysis**
- Spotify basic-pitch AI transcription
- Multi-stage noise reduction
- Instrument-specific analysis

💡 **AI Feedback**
- Real-time performance analysis
- Detailed metrics (pitch, rhythm, tempo, dynamics)
- Progress tracking

## For More Details

See [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md) for comprehensive deployment guide.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

## OMR Systems

The app uses a smart fallback system:

1. **Audiveris** (Best) - Requires Java, works locally
2. **OEMER** (Excellent) - Python-only, perfect for cloud
3. **CV OMR** (Good) - Always available fallback

On Streamlit Cloud, OEMER provides excellent results without Java!

## Authentication

- Secure user registration and login
- JWT-based authentication  
- Password hashing with bcrypt
- Guest mode available

## Support

Questions? Issues? 
- 📖 Read the [deployment guide](STREAMLIT_DEPLOYMENT.md)
- 🐛 Open an issue on GitHub
- 💬 Check existing issues

---

Made with ❤️ for musicians everywhere
