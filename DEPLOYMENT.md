# Mugic Deployment Guide

This application can be easily deployed to multiple platforms. Choose the one that fits your needs:

> **💡 Looking for free hosting without a credit card?** Check out options 1-4 below (PythonAnywhere, Replit, Glitch, or Koyeb). They offer truly free tiers with no credit card required!

## 💰 Free Options (No Credit Card Required)

The following platforms offer **truly free hosting without requiring a credit card**:

### 1. PythonAnywhere (Best for Python Apps - No Credit Card Required)

**Steps:**
1. Sign up at [PythonAnywhere](https://www.pythonanywhere.com) (free account, no credit card)
2. Open a Bash console from the dashboard
3. Clone your repository:
   ```bash
   git clone https://github.com/<yourusername>/mugic.git
   cd mugic
   ```
4. Create a virtual environment and install dependencies:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 mugic
   pip install -r requirements.txt
   ```
5. Go to "Web" tab → "Add a new web app"
6. Choose "Manual configuration" → Python 3.10
7. Configure WSGI file (click on the WSGI configuration file link):
   ```python
   import sys
   import os
   
   # Add your project directory to the sys.path
   # Replace '<yourusername>' with your actual username
   project_home = '/home/<yourusername>/mugic'
   if project_home not in sys.path:
       sys.path = [project_home] + sys.path
   
   # Set environment variables
   # SECURITY WARNING: Replace placeholders with your actual generated secret keys!
   # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
   os.environ['SECRET_KEY'] = '<your-generated-secret-key-here>'
   os.environ['JWT_SECRET_KEY'] = '<your-generated-jwt-secret-key-here>'
   os.environ['FLASK_ENV'] = 'production'
   
   # Import flask app
   from app import app as application
   ```
8. Set the virtualenv path to `/home/<yourusername>/.virtualenvs/mugic`
9. Reload the web app

**Pros:** 
- Completely free forever
- No credit card required
- Good for Python applications
- Includes SQLite database

**Limitations:** 
- 512MB disk space on free tier
- Limited CPU/bandwidth
- Apps sleep after inactivity

**Cost:** 100% Free (no credit card needed)

---

### 2. Replit (Great for Quick Testing - No Credit Card Required)

**Steps:**
1. Go to https://replit.com
2. Sign up for free (no credit card)
3. Click "Create Repl"
4. Choose "Import from GitHub" and paste your repository URL
5. Replit will auto-detect Python and install dependencies
6. The `.replit` configuration file is already included in the repository
7. Add secrets in the "Secrets" tab (lock icon) - **Important!**
   - `SECRET_KEY` = (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `JWT_SECRET_KEY` = (generate with the same command)
8. Click "Run" button

**Pros:**
- No credit card required
- Instant deployment
- Built-in IDE
- Collaborative features

**Limitations:**
- Resources shared with other users
- Apps sleep after inactivity
- Public by default (can upgrade for privacy)

**Cost:** 100% Free (no credit card needed)

---

### 3. Glitch (Fast & Simple - No Credit Card Required)

**Steps:**
1. Sign up at [Glitch](https://glitch.com) (free account, no credit card)
2. Click "New Project" → "Import from GitHub"
3. Enter your repository URL
4. Create a `glitch.json` file in the root:
   ```json
   {
     "install": "pip install -r requirements.txt",
     "start": "gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120",
     "watch": {
       "ignore": [
         "\\.pyc$",
         "^venv/",
         "^__pycache__/"
       ]
     }
   }
   ```
5. Add environment variables in `.env` file (Glitch creates this automatically):
   ```env
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   FLASK_ENV=production
   ```
6. Your app will auto-deploy!

**Pros:**
- No credit card required
- Instant deployment
- Auto-restarts on code changes
- Built-in editor

**Limitations:**
- 200MB disk space
- 512MB RAM
- Apps sleep after 5 minutes of inactivity

**Cost:** 100% Free (no credit card needed)

---

### 4. Koyeb (Generous Free Tier - No Credit Card Initially)

**Steps:**
1. Sign up at [Koyeb](https://www.koyeb.com) (free tier available)
2. Click "Create App" → "GitHub"
3. Select your repository
4. Configure:
   - Builder: Docker (uses your Dockerfile) or Buildpack
   - Port: 5000
   - Environment variables: `SECRET_KEY`, `JWT_SECRET_KEY`, `FLASK_ENV=production`
5. Click "Deploy"

**Pros:**
- Good free tier (no credit card initially)
- Global edge network
- Auto-scaling
- Always-on (doesn't sleep)

**Limitations:**
- May eventually require credit card verification
- Limited resources on free tier

**Cost:** Free tier available

---

## 🚀 Quick Deploy Options (May Require Credit Card)

### 5. Railway (Recommended - Easiest)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

**Steps:**
1. Click the button above or visit [Railway](https://railway.app)
2. Connect your GitHub repository
3. Railway will auto-detect the configuration from `railway.json`
4. Add environment variables in the Railway dashboard:
   - `SECRET_KEY` - Generate a random string
   - `JWT_SECRET_KEY` - Generate another random string
5. Deploy! Railway handles everything automatically

**Pros:** Free tier, automatic deployments, easy scaling
**Cost:** Free for starter projects

---

### 6. Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/masterofmagic999/mugic)

**One-Click Deploy:** Click the button above for instant deployment!

**Steps:**
1. Click the "Deploy to Render" button above
2. Sign up or log in to [Render](https://render.com)
3. Authorize GitHub access
4. Review the auto-configured settings (from `render.json`)
5. Click "Apply" - environment variables are auto-generated
6. Wait 5-15 minutes for build to complete
7. Your app is live!

**Manual Deployment:**
1. Visit [Render](https://render.com) and sign up
2. Click "New +" → "Blueprint" (or "Web Service")
3. Connect your GitHub repository
4. Render will detect `render.yaml` automatically
5. Configure environment variables (SECRET_KEY, JWT_SECRET_KEY)
6. Click "Create Web Service"

**Pros:** 
- One-click deployment with `render.json` blueprint
- Free tier with 750 hours/month
- Automatic SSL certificates
- Docker support with full Audiveris OMR
- Easy database add-ons

**Important:** 
- Uses Docker deployment with Java/Audiveris support
- See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed instructions
- Troubleshooting guide included for common issues

**Cost:** Free for starter (512MB RAM, sleeps after 15 min inactivity)

---

### 7. Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch (uses fly.toml)
fly launch

# Deploy
fly deploy

# Set secrets
fly secrets set SECRET_KEY=your-secret-key
fly secrets set JWT_SECRET_KEY=your-jwt-secret-key
```

**Pros:** Global edge deployment, great performance
**Cost:** Free allowance, pay-as-you-go

---

### 8. Docker Deployment (Any Platform)

```bash
# Build the image
docker build -t mugic .

# Run locally
docker run -p 5000:5000 \
  -e SECRET_KEY=your-secret \
  -e JWT_SECRET_KEY=your-jwt-secret \
  mugic

# Or use docker-compose
docker-compose up
```

**Deploy to:**
- **Google Cloud Run**
- **AWS ECS/Fargate**
- **Azure Container Instances**
- **DigitalOcean App Platform**

---

### 9. Heroku

```bash
# Install Heroku CLI
# Visit: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set JWT_SECRET_KEY=your-jwt-secret-key

# Deploy
git push heroku main

# Open app
heroku open
```

**Pros:** Easy deployment, many add-ons
**Cost:** Paid plans only (discontinued free tier)

---

## 📊 Platform Comparison

| Platform | Credit Card Required? | Free Tier | Always On? | Setup Difficulty |
|----------|----------------------|-----------|------------|------------------|
| **PythonAnywhere** | ❌ No | ✅ Yes (512MB) | ⚠️ Sleeps after inactivity | ⭐⭐⭐ Medium |
| **Replit** | ❌ No | ✅ Yes | ⚠️ Sleeps after inactivity | ⭐ Easy |
| **Glitch** | ❌ No | ✅ Yes (200MB) | ⚠️ Sleeps after 5 min | ⭐ Easy |
| **Koyeb** | ⚠️ Eventually | ✅ Yes | ✅ Yes | ⭐⭐ Easy-Medium |
| Railway | ✅ Yes | ✅ Yes (limited) | ✅ Yes | ⭐ Easy |
| Render | ⚠️ For some features | ✅ Yes (750 hrs) | ⚠️ Sleeps on free | ⭐ Easy |
| Fly.io | ✅ Yes | ✅ Yes | ✅ Yes | ⭐⭐⭐ Medium |
| Heroku | ✅ Yes | ❌ No | ✅ Yes | ⭐⭐ Easy-Medium |

**Recommendation for beginners:** Start with **PythonAnywhere**, **Replit**, or **Glitch** if you want to avoid credit cards entirely.

---

## ⚙️ Environment Variables

Required for all deployments:

```env
SECRET_KEY=<random-string-min-32-chars>
JWT_SECRET_KEY=<random-string-min-32-chars>
FLASK_ENV=production
```

Generate secure keys:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🔧 Platform-Specific Notes

### Railway
- Automatically detects Python and installs dependencies
- Provides PostgreSQL addon if needed
- Auto-generates PORT environment variable

### Render
- Auto-detects from `render.yaml`
- Free tier includes 750 hours/month
- Automatic SSL certificates
- Add PostgreSQL in one click

### Fly.io
- Uses `fly.toml` configuration
- Global CDN and edge computing
- Automatic scaling
- Free allowance: 3 VMs, 3GB storage

### Docker Platforms
- Universal deployment option
- Full control over environment
- Can bundle Audiveris in image
- Scalable and portable

---

## 📦 Additional Setup

### Audiveris (Optional)

For best OMR quality, install Audiveris:

**In Docker:**
```dockerfile
# Add to Dockerfile
RUN wget https://github.com/Audiveris/audiveris/releases/download/5.3.1/Audiveris-5.3.1.tar.gz && \
    tar -xzf Audiveris-5.3.1.tar.gz && \
    mv Audiveris-5.3.1 /opt/audiveris
```

**On Server:**
```bash
# Download and extract
wget https://github.com/Audiveris/audiveris/releases/download/5.3.1/Audiveris-5.3.1.tar.gz
tar -xzf Audiveris-5.3.1.tar.gz
sudo mv Audiveris-5.3.1 /opt/audiveris

# Set environment variable
export AUDIVERIS_PATH=/opt/audiveris
```

---

## 🗄️ Database Options

**SQLite (Default)**
- Included, no setup needed
- Good for development and small deployments
- Stored in file system

**PostgreSQL (Recommended for Production)**
```python
# Set DATABASE_URL environment variable
DATABASE_URL=postgresql://user:password@host:port/database
```

All platforms above offer easy PostgreSQL add-ons.

---

## ✅ Health Check

All deployments include a health check endpoint:
```
GET /health
```

Returns:
```json
{
  "status": "healthy",
  "service": "mugic",
  "version": "1.0.0"
}
```

---

## 🔍 Monitoring

Configure platform-specific monitoring:

- **Railway**: Built-in metrics dashboard
- **Render**: Automatic logging and metrics
- **Fly.io**: `fly logs` and metrics dashboard
- **Docker**: Use Prometheus, Grafana, or platform tools

---

## 🆘 Troubleshooting

**Build fails:**
- Check Python version (requires 3.11+)
- Ensure all dependencies in requirements.txt
- Check platform-specific build logs

**App crashes:**
- Check environment variables are set
- Review application logs
- Ensure PORT is correctly configured

**Slow performance:**
- Upgrade to paid tier for more resources
- Enable caching
- Optimize LLM model loading

---

## 🎯 Recommended Setup

**For Production:**
```
Platform: Railway or Render
Database: PostgreSQL
Instance: 1GB RAM minimum
LLM: DistilGPT2 (lighter than TinyLlama)
```

**For Development:**
```
Platform: Local Docker
Database: SQLite
LLM: TinyLlama (best quality)
```

---

## 📞 Support

- Platform issues: Check platform documentation
- Application issues: Open GitHub issue
- Deployment help: See platform community forums
