# Mugic Deployment Guide

This application can be easily deployed to multiple platforms. Choose the one that fits your needs:

## 🚀 Quick Deploy Options

### 1. Railway (Recommended - Easiest)

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

### 2. Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

**Steps:**
1. Visit [Render](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will detect `render.yaml` automatically
5. Configure environment variables (SECRET_KEY, JWT_SECRET_KEY)
6. Click "Create Web Service"

**Pros:** Free tier, automatic SSL, easy database add-ons
**Cost:** Free for starter

---

### 3. Fly.io

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

### 4. Docker Deployment (Any Platform)

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

### 5. Heroku

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
