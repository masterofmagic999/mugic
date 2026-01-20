# Streamlit Cloud Deployment Guide

## 🚀 Quick Deploy to Streamlit Community Cloud

Mugic can be deployed to Streamlit Community Cloud while maintaining its powerful OMR capabilities.

### Prerequisites
- GitHub account
- Streamlit Community Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

## Deployment Steps

### 1. Fork or Clone the Repository
```bash
git clone https://github.com/masterofmagic999/mugic.git
cd mugic
```

### 2. Push to Your GitHub Repository
```bash
git remote set-url origin https://github.com/YOUR-USERNAME/mugic.git
git push origin main
```

### 3. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository: `YOUR-USERNAME/mugic`
4. Set **Main file path**: `streamlit_app.py`
5. Click "Deploy"

### 4. Configuration

Streamlit Cloud will automatically:
- Install Python dependencies from `requirements-streamlit.txt`
- Install system packages from `packages.txt`
- Use settings from `.streamlit/config.toml`

## OMR Technology Stack

### Hierarchy of OMR Systems

Mugic uses a fallback hierarchy for maximum reliability:

1. **Audiveris OMR** (Best Quality)
   - Industry-standard OMR
   - Requires Java Runtime (JRE 11+)
   - **Not available on Streamlit Cloud by default**

2. **OEMER** (Excellent Quality, Cloud-Friendly)
   - End-to-end neural OMR
   - Pure Python, works on Streamlit Cloud
   - **Recommended for Streamlit deployment**

3. **Computer Vision OMR** (Good Quality, Always Available)
   - OpenCV-based fallback
   - Always works as last resort

### Setting Up Audiveris (Advanced - Not on Streamlit Cloud)

Audiveris requires Java, which is not available on Streamlit Community Cloud's default environment.

**For local development with Audiveris:**

1. **Install Java 11+**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install openjdk-17-jre
   
   # macOS
   brew install openjdk@17
   
   # Windows
   # Download from https://adoptium.net/
   ```

2. **Download Audiveris**:
   ```bash
   # Download from GitHub releases
   wget https://github.com/Audiveris/audiveris/releases/download/5.3.1/Audiveris-5.3.1.tar.gz
   
   # Extract
   tar -xzf Audiveris-5.3.1.tar.gz -C /opt/
   
   # Make executable
   chmod +x /opt/audiveris/bin/audiveris
   ```

3. **Set environment variable** (optional):
   ```bash
   export AUDIVERIS_PATH=/opt/audiveris
   ```

**For Streamlit Cloud:**
- Audiveris is not supported due to Java requirement
- OEMER will automatically be used instead
- OEMER provides excellent quality for most use cases

## Optimizing for Streamlit Cloud

### 1. Use OEMER for Best Cloud Performance

OEMER is specifically designed for cloud/serverless environments:
- Pure Python (no Java needed)
- Lightweight models
- Fast inference
- Excellent accuracy

### 2. System Dependencies

The `packages.txt` file includes:
```
tesseract-ocr       # For text detection in scores
tesseract-ocr-eng   # English language data
libsndfile1         # Audio file support
ffmpeg              # Audio processing
poppler-utils       # PDF rendering
```

### 3. Python Dependencies

The `requirements-streamlit.txt` includes all necessary packages:
- `streamlit` - UI framework
- `oemer` - OMR system
- `basic-pitch` - Audio transcription
- `opencv-python` - Computer vision
- `music21` - Music analysis
- And more...

## Environment Variables (Optional)

You can set these in Streamlit Cloud's "Advanced settings":

```bash
SECRET_KEY=your-secret-key-here
STREAMLIT_THEME_PRIMARY_COLOR=#667eea
```

## File Storage on Streamlit Cloud

Streamlit Cloud has limited file system access:
- Uploaded files are stored in `/tmp` or local folders
- Files persist only during the session
- For production, consider adding cloud storage (S3, Google Cloud Storage)

## Audio Recording

Streamlit's `audio_input` component allows browser-based recording:
- Available in Streamlit 1.28+
- Works in modern browsers
- For older Streamlit versions, use file upload fallback

## Performance Optimization

### For faster OMR processing:
1. Use high-resolution PDFs (300 DPI+)
2. Ensure clear, well-lit scans
3. Single-page PDFs process faster

### For faster audio analysis:
1. Use WAV format when possible
2. Keep recordings under 2 minutes
3. Record in quiet environment

## Troubleshooting

### OMR Issues

**Problem**: "OEMER not found"
**Solution**: Check that `oemer==0.1.8` is in requirements file

**Problem**: Low accuracy
**Solution**: Use higher resolution PDFs, ensure clear notation

### Audio Issues

**Problem**: "basic-pitch not found"
**Solution**: Verify `basic-pitch==0.2.5` in requirements

**Problem**: Microphone not working
**Solution**: Browser must have microphone permissions enabled

### Deployment Issues

**Problem**: App crashes on startup
**Solution**: Check Streamlit Cloud logs, verify all dependencies

**Problem**: Out of memory
**Solution**: Reduce model sizes, use lighter alternatives

## Advanced: Custom Docker Deployment

For full Audiveris support with Java:

```dockerfile
FROM python:3.9-slim

# Install Java for Audiveris
RUN apt-get update && apt-get install -y \
    openjdk-17-jre \
    tesseract-ocr \
    libsndfile1 \
    ffmpeg \
    poppler-utils

# Install Audiveris
RUN wget https://github.com/Audiveris/audiveris/releases/download/5.3.1/Audiveris-5.3.1.tar.gz && \
    tar -xzf Audiveris-5.3.1.tar.gz -C /opt/ && \
    rm Audiveris-5.3.1.tar.gz

# Install Python dependencies
COPY requirements-streamlit.txt .
RUN pip install -r requirements-streamlit.txt

# Copy application
COPY . /app
WORKDIR /app

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "streamlit_app.py"]
```

Deploy this to:
- Google Cloud Run
- AWS ECS/Fargate
- Azure Container Instances
- DigitalOcean App Platform

## Monitoring

### Check OMR System Status

The app displays which OMR system is active:
- Look for the green "POWERED BY" banner
- Shows: "Audiveris OMR", "OEMER", or "Computer Vision OMR"

### Performance Metrics

Monitor in Streamlit Cloud dashboard:
- Response time
- Memory usage
- CPU usage
- Error rates

## Support

For issues:
1. Check Streamlit Cloud logs
2. Verify system requirements
3. Review error messages
4. Open issue on GitHub

## OMR Quality Comparison

| System | Accuracy | Speed | Cloud-Friendly | Requires |
|--------|----------|-------|----------------|----------|
| **Audiveris** | ⭐⭐⭐⭐⭐ | Medium | ❌ | Java 11+ |
| **OEMER** | ⭐⭐⭐⭐ | Fast | ✅ | Python only |
| **CV OMR** | ⭐⭐⭐ | Fast | ✅ | Python only |

## Recommended Setup for Production

1. **Streamlit Cloud (Free Tier)**:
   - Use OEMER
   - Great for demos and testing
   - Limited resources

2. **Streamlit Cloud (Teams)**:
   - Use OEMER
   - More resources
   - Better performance

3. **Self-Hosted (Docker)**:
   - Use Audiveris (best quality)
   - Full control
   - Requires server/VPS

## Conclusion

Streamlit Cloud deployment provides excellent OMR quality through OEMER while maintaining ease of use. For the absolute best OMR quality with Audiveris, consider self-hosting with Docker.

The application automatically adapts to the available OMR system, ensuring users always get the best experience possible for their deployment environment.
