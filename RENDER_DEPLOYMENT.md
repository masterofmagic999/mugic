# Deploying Mugic to Render

This guide provides detailed, step-by-step instructions for deploying Mugic to Render.com, including troubleshooting common deployment issues.

## 🚀 One-Click Deploy (Fastest!)

Click the button below to deploy Mugic to Render in one click:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/masterofmagic999/mugic)

This will:
- ✅ Automatically create a new web service
- ✅ Configure all environment variables
- ✅ Use the optimized Docker configuration
- ✅ Set up health checks
- ✅ Deploy with Java/Audiveris support included

**Just click, wait 5-15 minutes, and your app is live!**

---

## 🎯 Overview

Render is a modern cloud platform that makes it easy to deploy web applications. Mugic supports two deployment methods on Render:

1. **Docker Deployment** (Recommended) - Uses `Dockerfile.render` for a containerized deployment with full Audiveris OMR support
2. **Native Python Deployment** - Direct Python environment deployment (limited - no Audiveris)

The Docker method is **strongly recommended** as it includes Java and full Audiveris OMR functionality, which is required for optimal sheet music analysis.

## 📋 Prerequisites

- A GitHub account with your Mugic repository forked/cloned
- A Render account (free signup at https://render.com)
- Your repository must be connected to Render

**Note**: Mugic requires Java Runtime Environment (JRE) for Audiveris OMR system. The Docker deployment handles this automatically.

## 🚀 Deployment Methods

### Method 1: One-Click Deploy (Easiest!)

The fastest way to deploy Mugic to Render:

1. **Click the Deploy Button**
   
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/masterofmagic999/mugic)
   
   Or visit: `https://render.com/deploy?repo=https://github.com/masterofmagic999/mugic`

2. **Authorize GitHub**
   - If not already connected, authorize Render to access your GitHub
   - This allows Render to read your repository

3. **Configure Your Service**
   - Render automatically reads `render.json` blueprint
   - Service name: `mugic` (you can change this)
   - All environment variables are pre-configured
   - `SECRET_KEY` and `JWT_SECRET_KEY` are auto-generated

4. **Deploy!**
   - Click "Apply" or "Create Resources"
   - Render will build your Docker image (5-15 minutes)
   - Watch the build logs in real-time
   - Once complete, you'll get your live URL!

5. **Access Your App**
   - Your app will be available at: `https://mugic-xxxx.onrender.com`
   - Click the URL to start using Mugic

**That's it!** Your Mugic instance is now live with full Audiveris OMR support.

---

### Method 2: Blueprint Deployment

If you prefer more control or need to customize settings:

1. **Sign up/Login to Render**
   - Go to https://render.com
   - Click "Get Started for Free" or "Sign In"
   - Authenticate with GitHub

2. **Create New Web Service from Blueprint**
   - Click "New +" button in the dashboard
   - Select "Blueprint"
   - Connect your GitHub account if not already connected
   - Select your Mugic repository
   - Render will automatically detect the `render.yaml` file

3. **Configure the Service**
   - **Service Name**: `mugic` (or your preferred name)
   - **Region**: Choose closest to your users (Oregon, Frankfurt, Singapore, etc.)
   - **Branch**: `main` (or your deployment branch)
   - **Environment**: Docker (pre-configured in render.yaml)
   - **Plan**: Starter (Free tier)
   
4. **Review Environment Variables**
   Render automatically generates these from `render.yaml`:
   - `SECRET_KEY` - Auto-generated secure random string
   - `JWT_SECRET_KEY` - Auto-generated secure random string
   - `FLASK_ENV` - Set to "production"
   - `FLASK_APP` - Set to "app.py"
   - `PYTHON_VERSION` - Set to "3.11.0"

5. **Deploy**
   - Click "Apply" or "Create Web Service"
   - Render will build and deploy your application
   - Build time: 5-15 minutes (first deployment)
   - You'll see real-time build logs

6. **Access Your App**
   - Once deployed, you'll get a URL like: `https://mugic-xxxx.onrender.com`
   - Click the URL to open your application

### Method 3: Manual Deployment

If you prefer more control or need to customize settings:

1. **Sign up/Login to Render**
   - Go to https://render.com
   - Sign in with GitHub

2. **Create New Web Service**
   - Click "New +" in the dashboard
   - Select "Web Service"

3. **Connect Repository**
   - Select "Build and deploy from a Git repository"
   - Choose your Mugic repository
   - Click "Connect"

4. **Configure Build Settings**
   
   **For Docker Deployment (Recommended):**
   - **Name**: `mugic`
   - **Region**: Choose your preferred region
   - **Branch**: `main`
   - **Runtime**: Docker
   - **Dockerfile Path**: `./Dockerfile.render`
   - **Docker Build Context**: `.`
   
   **For Native Python Deployment (Not Recommended - Missing Audiveris):**
   - **Name**: `mugic`
   - **Region**: Choose your preferred region
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements-flask.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120`
   - **Note**: This method does NOT include Java/Audiveris OMR support

5. **Set Environment Variables**
   Click "Advanced" and add these environment variables:
   
   ```
   FLASK_ENV=production
   FLASK_APP=app.py
   SECRET_KEY=<click "Generate" to create>
   JWT_SECRET_KEY=<click "Generate" to create>
   PYTHON_VERSION=3.11.0
   ```

6. **Choose Plan**
   - Select "Starter" (Free tier)
   - Free tier includes:
     - 750 hours/month
     - Automatic SSL
     - 512 MB RAM
     - Shared CPU
     - App sleeps after 15 min of inactivity

7. **Create Web Service**
   - Click "Create Web Service"
   - Render begins building your app
   - Monitor the deployment logs

## 📊 Deployment Methods Comparison

| Feature | One-Click Deploy | Blueprint | Manual Docker | Native Python |
|---------|------------------|-----------|---------------|---------------|
| **Setup Time** | < 1 minute | 2-3 minutes | 5-10 minutes | 5-10 minutes |
| **Configuration** | Automatic | Automatic | Manual | Manual |
| **Java/Audiveris** | ✅ Included | ✅ Included | ✅ Included | ❌ Not available |
| **Recommended** | ✅ Best for most | ✅ Good | ✅ For customization | ⚠️ Limited features |
| **Build Time** | 5-15 minutes | 5-15 minutes | 5-15 minutes | 3-10 minutes |

## 🔧 Configuration Details

### Dockerfile.render Explained

The `Dockerfile.render` is optimized for Render deployment with full Audiveris support:

- **Base Image**: `python:3.11-slim` - Lightweight Python 3.11
- **System Dependencies**: gcc, g++, make, libsndfile1, ffmpeg
- **Java Runtime**: OpenJDK 21, 17, or 11 (required for Audiveris OMR)
- **Port Binding**: Uses `$PORT` environment variable provided by Render
- **Production Ready**: Includes gunicorn with 4 workers, 120s timeout
- **Health Check**: Monitors `/health` endpoint

### Environment Variables

| Variable | Purpose | Value |
|----------|---------|-------|
| `SECRET_KEY` | Flask session security | Auto-generated by Render |
| `JWT_SECRET_KEY` | JWT token signing | Auto-generated by Render |
| `FLASK_ENV` | Flask environment mode | `production` |
| `FLASK_APP` | Flask app entry point | `app.py` |
| `PYTHON_VERSION` | Python version hint | `3.11.0` |
| `PORT` | Server port (auto-set) | Provided by Render |

### Health Check

Render automatically monitors your app using the health check endpoint:
- **Endpoint**: `/health`
- **Method**: GET
- **Expected**: 200 OK response with `{"status": "healthy"}`
- **Configured**: In `render.yaml` and `render.json`

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Build Fails: "failed to solve: process did not complete successfully: exit code: 100"

**Problem**: This error occurs when apt-get fails to install packages, specifically when trying to install Java.

**Solutions**:
- ✅ **Use One-Click Deploy** - Pre-configured to work correctly
- ✅ **Use `Dockerfile.render`** - This optimized Dockerfile handles Java installation with fallbacks
- ✅ **Use `Dockerfile.render`** - This optimized Dockerfile handles Java installation with fallbacks
- ✅ **Updated Dockerfile** - Now tries OpenJDK 21 first (latest), then falls back to 17 or 11
- The Dockerfiles now set `DEBIAN_FRONTEND=noninteractive` to avoid interactive prompts
- Removed unnecessary packages that caused build failures

**How to Verify**:
- Check build logs for "java -version" output
- Successful Java installation will show: `openjdk version "21.x.x"` (or `"17.x.x"` or `"11.x.x"` as fallbacks)

**If Still Failing**:
```dockerfile
# The Dockerfile.render now includes smart fallback:
RUN apt-get update && \
    (apt-get install -y --no-install-recommends openjdk-21-jre-headless || \
     apt-get install -y --no-install-recommends openjdk-17-jre-headless || \
     apt-get install -y --no-install-recommends openjdk-11-jre-headless) && \
    rm -rf /var/lib/apt/lists/* && \
    java -version
```

#### 2. App Build Takes Too Long / Times Out

**Problem**: Build exceeds Render's free tier time limits.

**Solutions**:
- Use `Dockerfile.render` which is optimized for faster builds
- Remove heavy dependencies if not needed
- Consider using native Python deployment
- Upgrade to paid plan for longer build times

#### 3. App Crashes on Start

**Problem**: Application fails to start after successful build.

**Check**:
```bash
# View logs in Render dashboard
# Common issues:
- Missing environment variables
- Port binding issues
- Database connection errors
```

**Solutions**:
- Verify all environment variables are set
- Check that `PORT` is not hardcoded in your app
- Review startup logs in Render dashboard

#### 4. "Module Not Found" Errors

**Problem**: Python can't find required modules.

**Solutions**:
- Ensure `requirements.txt` is complete
- Check that build command ran successfully
- Verify Python version compatibility (3.11+)
- Try clearing build cache (Render dashboard → Settings → Clear Build Cache)

#### 5. App is Slow or Times Out

**Problem**: Requests take too long or timeout.

**Solutions**:
- Free tier has limited resources (512 MB RAM)
- App sleeps after 15 minutes of inactivity (first request is slow)
- Increase gunicorn timeout if needed
- Consider upgrading to paid plan
- Optimize heavy operations (ML model loading, etc.)

#### 6. "Health Check Failed"

**Problem**: Render can't reach `/health` endpoint.

**Solutions**:
- Verify app is actually running (check logs)
- Test endpoint locally first: `curl http://localhost:5000/health`
- Check if app is binding to correct port (`$PORT`)
- The `/health` endpoint requires no authentication

#### 7. Docker Build Fails: "Cannot Install openjdk-17"

**Problem**: Java installation fails during Docker build.

**Solutions**:
- ✅ **Use One-Click Deploy** - Handles this automatically
- ✅ **Use `Dockerfile.render`** - Has smart fallback from OpenJDK 17 to 11
- ✅ The Dockerfile tries multiple Java versions automatically
- Java is **required** for Audiveris OMR functionality

**Verification**:
```bash
# In the build logs, look for:
java -version
# Should output: openjdk version "21.x.x" (or "17.x.x" or "11.x.x" as fallbacks)
```

### Viewing Logs

**To view deployment logs**:
1. Go to Render dashboard
2. Click on your service
3. Click "Logs" tab
4. View real-time logs during deployment and runtime

**To view specific error details**:
```bash
# Logs show:
- Build progress
- Package installation
- Application startup
- Runtime errors
- Request logs
```

## 🎯 Post-Deployment

### Test Your Deployment

1. **Visit Your App**
   - Open the Render URL: `https://your-app.onrender.com`
   - Verify the homepage loads

2. **Test Authentication**
   - Create a user account
   - Log in
   - Verify JWT tokens work

3. **Test Core Functionality**
   - Upload a PDF sheet music file (tests Audiveris OMR with Java)
   - Verify OMR analysis completes successfully
   - Record audio
   - Get feedback

4. **Monitor Performance**
   - Check response times
   - Monitor memory usage in Render dashboard
   - Review error logs

### Custom Domain (Optional)

To use your own domain:

1. Go to Render dashboard → Your service
2. Click "Settings" tab
3. Scroll to "Custom Domain"
4. Click "Add Custom Domain"
5. Follow DNS configuration instructions
6. Render provides free SSL for custom domains

### Environment Updates

To update environment variables:

1. Go to Render dashboard → Your service
2. Click "Environment" tab
3. Add/edit variables
4. Click "Save"
5. App will automatically redeploy

## 📈 Scaling

### Free Tier Limitations

- **750 hours/month** (enough for 24/7 if single service)
- **512 MB RAM** (adequate for light usage)
- **Shared CPU** (limited processing power)
- **Sleeps after 15 min** (first request takes ~30s to wake)
- **Build time limits**

### Upgrading for Production

If you need more resources:

| Plan | Price | RAM | Features |
|------|-------|-----|----------|
| **Starter** | Free | 512 MB | Good for testing |
| **Basic** | $7/mo | 512 MB | No sleep, better support |
| **Standard** | $25/mo | 2 GB | Auto-scaling, more resources |
| **Pro** | $85/mo | 4 GB | Production-grade |

### Manual Scaling

To manually scale:
1. Go to Settings → Instance Type
2. Choose larger instance
3. Adjust number of instances (Horizontal scaling)

## 🔐 Security Best Practices

1. **Never commit secrets** to your repository
2. **Use Render's "Generate" feature** for SECRET_KEY and JWT_SECRET_KEY
3. **Enable HTTPS** (automatic with Render)
4. **Regular updates**: Keep dependencies up to date
5. **Monitor logs** for suspicious activity

## 💡 Tips for Success

1. **Use Docker deployment** (`Dockerfile.render`) - Most reliable
2. **Monitor your app** - Check logs regularly
3. **Set up alerts** - Render can notify you of failures
4. **Test locally first** - Ensure app works before deploying
5. **Use staging environment** - Test changes before production
6. **Keep it simple** - Remove unnecessary dependencies
7. **Optimize startup time** - Lazy load heavy models

## 🆘 Getting Help

**Render-specific issues**:
- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com
- Render Status: https://status.render.com

**Mugic-specific issues**:
- GitHub Issues: https://github.com/masterofmagic999/mugic/issues
- Check DEPLOYMENT.md for general deployment help
- Review TROUBLESHOOTING.md (if available)

## 📚 Additional Resources

- [Render Docker Deployment Docs](https://render.com/docs/docker)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Render Build & Deploy](https://render.com/docs/builds-deploys)
- [Mugic Main Documentation](README.md)
- [General Deployment Guide](DEPLOYMENT.md)

## ✅ Success Checklist

Before considering your deployment complete:

- [ ] App builds successfully without errors
- [ ] App starts and responds to health checks
- [ ] Environment variables are set correctly
- [ ] Homepage loads in browser
- [ ] User registration works
- [ ] User login works
- [ ] PDF upload and analysis works
- [ ] Audio recording and analysis works
- [ ] Feedback generation works
- [ ] No errors in Render logs
- [ ] SSL certificate is active (https://)
- [ ] Custom domain configured (if applicable)

## 🎉 Congratulations!

Your Mugic app should now be successfully deployed on Render! Share your deployment URL and start helping musicians practice more effectively.

---

**Need more help?** Open an issue on GitHub or consult the Render documentation.
