# Streamlit Cloud Deployment Troubleshooting Guide

## ✅ Recent Fixes (January 2026)

### TensorFlow/Python 3.13 Dependency Issue - FIXED ✓

**Problem:** 
- Error: "No solution found when resolving dependencies" with TensorFlow
- Python 3.13.11 compatibility issues with TensorFlow

**Solution Applied:**
1. **Updated Python version** to 3.10.15 in `runtime.txt`
2. **Upgraded basic-pitch** from 0.3.3 to 0.4.0 in `requirements.txt`
3. Python 3.10 < 3.11 triggers basic-pitch to use `tflite-runtime` instead of full TensorFlow

**Why This Works:**
- basic-pitch 0.4.0 has smart dependency resolution
- For Python < 3.11 on Linux, it uses lightweight `tflite-runtime` 
- For Python >= 3.11, it would require full TensorFlow (which doesn't support Python 3.13 yet)
- This completely eliminates the TensorFlow dependency conflict

## 🚀 Deployment Checklist

Before deploying to Streamlit Cloud, verify:

- [ ] `runtime.txt` contains `python-3.10.15` (or another 3.10.x version)
- [ ] `requirements.txt` contains `basic-pitch==0.4.0` (not 0.3.3)
- [ ] `packages.txt` lists all system dependencies (tesseract-ocr, ffmpeg, etc.)
- [ ] Repository is pushed to GitHub
- [ ] All sensitive data is in `.env` (not committed to repo)

## 📋 Common Issues and Solutions

### 1. Installer Returns Non-Zero Exit Code

**Symptoms:**
```
❗️ installer returned a non-zero exit code
❗️ Error during processing dependencies!
```

**Solutions:**

#### A. Python Version Issues
- **Check:** Ensure `runtime.txt` exists and contains `python-3.10.15`
- **Fix:** Create or update `runtime.txt` with the correct Python version
- **Why:** Streamlit Cloud may default to Python 3.13 which has compatibility issues

#### B. Dependency Conflicts
- **Check:** Look for conflicting version requirements in `requirements.txt`
- **Fix:** Use compatible versions (see "Tested Dependency Versions" below)
- **Why:** Some packages have strict version requirements

#### C. Missing System Packages
- **Check:** Ensure `packages.txt` lists all required system packages
- **Fix:** Add missing packages like `tesseract-ocr`, `ffmpeg`, `libsndfile1`
- **Why:** Some Python packages need system-level dependencies

### 2. TensorFlow Not Available Error

**Symptoms:**
```
ModuleNotFoundError: No module named 'tensorflow'
```

**Solution:**
- This should NOT happen with Python 3.10 and basic-pitch 0.4.0
- basic-pitch 0.4.0 automatically installs `tflite-runtime` on Linux with Python < 3.11
- If you see this error, verify your `runtime.txt` uses Python 3.10.x

### 3. Out of Memory Errors

**Symptoms:**
```
Killed
MemoryError
```

**Solutions:**
- Reduce model sizes in memory
- Use lazy loading for heavy dependencies
- Consider Streamlit Cloud's upgraded plans for more resources

### 4. Import Errors on Startup

**Symptoms:**
```
ImportError: cannot import name 'X' from 'Y'
```

**Solutions:**
- Verify all dependencies in `requirements.txt` are installed
- Check for version conflicts
- Ensure system packages are in `packages.txt`

## 📦 Tested Dependency Versions

These versions work together on Streamlit Cloud (as of January 2026):

```
python==3.10.15  # In runtime.txt
streamlit==1.32.0
basic-pitch==0.4.0  # Uses tflite-runtime automatically
numpy==1.26.4
scipy==1.11.4
librosa==0.10.1
torch==2.6.0
transformers==4.48.0
```

## 🔍 Debugging Deployment Issues

### Step 1: Check Streamlit Cloud Logs
1. Go to your app on share.streamlit.io
2. Click on "Manage app" → "Logs"
3. Look for the first error message (usually the root cause)

### Step 2: Verify Files in Repository
```bash
# Check these files exist and are correct
cat runtime.txt         # Should show: python-3.10.15
cat packages.txt        # Should list system dependencies
head -n 50 requirements.txt  # Verify basic-pitch==0.4.0
```

### Step 3: Test Locally (Optional)
```bash
# Create clean environment
python3.10 -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt

# If successful locally, issue is environment-specific
```

### Step 4: Force Rebuild on Streamlit Cloud
1. Make a small change (add a comment to any file)
2. Commit and push
3. Streamlit Cloud will rebuild from scratch

## 🎯 Streamlit Cloud Specific Notes

### Python Version Handling
- Streamlit Cloud reads Python version from `runtime.txt`
- Format must be exactly: `python-X.Y.Z` (e.g., `python-3.10.15`)
- If `runtime.txt` is missing, Streamlit may use a default Python version (currently 3.13.x)

### Package Installation Order
1. System packages from `packages.txt` are installed first
2. Python packages from `requirements.txt` are installed next
3. Installation must complete in ~10 minutes on free tier

### Resource Limits (Free Tier)
- **Memory:** 1 GB RAM
- **CPU:** Shared
- **Storage:** Limited
- **Timeout:** Inactive apps sleep after inactivity

### Best Practices for Streamlit Cloud
1. **Use lightweight alternatives when possible:**
   - ✅ basic-pitch with tflite-runtime (lighter than TensorFlow)
   - ✅ OEMER for OMR (pure Python)
   - ❌ Avoid Audiveris (requires Java, not available)

2. **Optimize startup time:**
   - Use `@st.cache_resource` for one-time loading
   - Lazy import heavy libraries

3. **Handle missing dependencies gracefully:**
   ```python
   try:
       from basic_pitch.inference import predict
       BASIC_PITCH_AVAILABLE = True
   except ImportError:
       BASIC_PITCH_AVAILABLE = False
       st.warning("Audio transcription unavailable")
   ```

## 📞 Getting Help

If issues persist:

1. **Check Streamlit Community Forum:** https://discuss.streamlit.io/
2. **Review Streamlit Cloud Docs:** https://docs.streamlit.io/streamlit-community-cloud
3. **Check this repository's issues:** Look for similar problems
4. **Create a new issue** with:
   - Full error logs from Streamlit Cloud
   - Your `runtime.txt` content
   - Relevant lines from `requirements.txt`

## ✅ Success Indicators

Your deployment is successful when:
- ✅ App loads without errors in Streamlit Cloud logs
- ✅ No "Error during processing dependencies" messages
- ✅ Main page renders correctly
- ✅ basic-pitch (audio transcription) functionality works
- ✅ OMR (sheet music recognition) functionality works

## 🔄 Quick Fix Command Sequence

If you encounter the TensorFlow issue again:

```bash
cd /path/to/mugic

# Update runtime.txt
echo "python-3.10.15" > runtime.txt

# Update basic-pitch in requirements.txt
sed -i 's/basic-pitch==0.3.3/basic-pitch==0.4.0/' requirements.txt

# Commit and push
git add runtime.txt requirements.txt
git commit -m "Fix: Update to Python 3.10.15 and basic-pitch 0.4.0 for Streamlit Cloud compatibility"
git push origin main

# Wait for Streamlit Cloud to rebuild (2-5 minutes)
```

---

**Last Updated:** January 2026  
**Status:** TensorFlow dependency issue resolved ✓
