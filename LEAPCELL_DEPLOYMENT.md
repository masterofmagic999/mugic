# Deploying Mugic to Leapcell with Docker + Java Support

## 🎯 Overview

Leapcell supports Docker deployments, which means you can run both Python AND Java (for Audiveris OMR) in the same container! This guide will walk you through deploying Mugic to Leapcell using our optimized Docker configuration.

**Why Leapcell?**
- ✅ Full Docker support (Python + Java in one container)
- ✅ Audiveris OMR fully functional
- ✅ Easy environment variable management
- ✅ Automatic SSL certificates
- ✅ Health check monitoring
- ✅ Free tier available

## 📋 Prerequisites

Before you begin, you'll need:
- A [Leapcell](https://leapcell.io) account (free tier available)
- A [GitHub](https://github.com) account with your Mugic repository
- 10-15 minutes for deployment

## 🚀 Deployment Steps

### 1. Connect Your Repository

1. **Sign up/Log in to Leapcell**
   - Visit [https://leapcell.io](https://leapcell.io)
   - Sign up using your GitHub account for easiest integration
   - Authorize Leapcell to access your repositories

2. **Create a New Project**
   - Click **"New Project"** or **"Deploy"** in the Leapcell dashboard
   - Select **"Import from GitHub"**
   - Choose your `mugic` repository from the list
   - Leapcell will automatically detect the configuration files

### 2. Configure Docker Deployment

Leapcell will automatically detect the `Dockerfile.leapcell` in your repository. This Dockerfile is specifically optimized for Leapcell and includes:

- ✅ Python 3.11-slim base image
- ✅ Java (OpenJDK 17/11) for Audiveris OMR
- ✅ All necessary system dependencies (gcc, g++, make, libsndfile1, ffmpeg)
- ✅ Port 8080 configuration (Leapcell's required port)
- ✅ Gunicorn with 4 workers and 120-second timeout
- ✅ Health check endpoint monitoring

**Configuration Options:**
- **Dockerfile**: Select `Dockerfile.leapcell` (should be auto-detected)
- **Port**: 8080 (already configured in the Dockerfile)
- **Region**: Choose the region closest to your users (default: us-east-1)
- **Resources**: 1GB RAM recommended (configurable based on your needs)

### 3. Environment Variables Setup - IMPORTANT! 🔐

Leapcell needs several environment variables to run securely. Here's how to set them up:

#### Generate Your Secret Keys

**CRITICAL**: Never use default or example keys in production! Generate your own secure keys.

Run these commands locally to generate secure keys:

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate JWT_SECRET_KEY (use a different key!)
python -c "import secrets; print(secrets.token_hex(32))"
```

**Example output (DO NOT USE THESE):**
```
a7f3e9c2b5d8f1a4e6c9b2d5f8e1c4a7b0d3f6e9c2b5d8f1a4e7c0b3f6e9c2b5
b8g4f0d3c6e9b2d5f8e1c4a7b0d3f6e9c2b5d8f1a4e7c0b3f6e9c2b5d8f1a4
```

#### Add Variables to Leapcell UI

1. Go to your Leapcell dashboard
2. Select your **mugic-web** service
3. Navigate to **"Settings"** → **"Environment Variables"**
4. Add each variable by clicking **"Add Variable"** or **"New Environment Variable"**

**Required Variables:**

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `FLASK_ENV` | `production` | Sets Flask to production mode (no debug info) |
| `SECRET_KEY` | `[your-generated-key-1]` | Flask session encryption key (copy from your first generation) |
| `JWT_SECRET_KEY` | `[your-generated-key-2]` | JWT token signing key (copy from your second generation) |

**Optional Variables:**

| Variable Name | Example Value | Description |
|---------------|---------------|-------------|
| `FLASK_APP` | `app.py` | Flask application entry point (default: app.py) |
| `PORT` | `8080` | Application port (default: 8080) |
| `DATABASE_URL` | `postgresql://user:pass@host:5432/db` | PostgreSQL connection string (if using external DB) |

#### Security Best Practices 🔒

**IMPORTANT - READ CAREFULLY:**

1. **Never commit secrets to GitHub**
   - The `.env.example` file shows the format but uses placeholders
   - Real secrets should ONLY be set in Leapcell's UI
   - Add `.env` to `.gitignore` (already done in this repo)

2. **Use different keys for each environment**
   - Development: One set of keys
   - Staging: Different set of keys
   - Production: Yet another different set of keys

3. **Keep your keys safe**
   - These keys protect your users' sessions and authentication
   - If compromised, regenerate immediately
   - Don't share them in chat, email, or screenshots

4. **Use strong, random keys**
   - Always use the `secrets.token_hex(32)` method
   - Never use dictionary words or predictable patterns
   - Minimum 64 characters (hex) recommended

### 4. Deploy Your Application

1. **Review Configuration**
   - Verify all environment variables are set
   - Confirm Dockerfile is `Dockerfile.leapcell`
   - Check that port is set to 8080

2. **Click Deploy**
   - Click the **"Deploy"** or **"Create Service"** button
   - Leapcell will begin building your Docker image

3. **Monitor Build Progress**
   - Watch the build logs in real-time
   - Build typically takes 5-10 minutes for first deployment
   - Java installation is the longest step (~2-3 minutes)

4. **Wait for Deployment**
   - Leapcell will:
     - Clone your repository
     - Build the Docker image (install Java, Python dependencies)
     - Start the container with Gunicorn
     - Run health checks
     - Assign a public URL (e.g., `https://mugic-web-xxxx.leapcell.io`)

### 5. Verify Deployment ✅

Once deployed, verify everything is working:

#### 5.1 Check Health Endpoint

Visit your app's health endpoint:
```
https://your-app.leapcell.io/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 5.2 Test Homepage

Visit your app's homepage:
```
https://your-app.leapcell.io
```

You should see the Mugic interface with:
- Upload button for sheet music
- Instrument selector
- Recording controls

#### 5.3 Verify Java/Audiveris (Check Logs)

In Leapcell dashboard:
1. Go to your service → **"Logs"** or **"Runtime Logs"**
2. Look for these indicators:

**Successful Java Installation:**
```
openjdk version "17.0.X" 2024-XX-XX
OpenJDK Runtime Environment (build 17.0.X+X)
```

**Audiveris OMR System Ready:**
```
[INFO] Using Audiveris OMR system
[INFO] Java runtime detected: /usr/lib/jvm/java-17-openjdk-amd64
```

If you see "Using OEMER OMR" instead, that's also fine - it's the Python-based fallback.

#### 5.4 Test Authentication

1. Click **"Sign In"** in the header
2. Click **"Sign up"** to create a test account
3. Enter username, email, and password
4. Verify you receive a success message

#### 5.5 Test Upload Feature

1. Upload a PDF sheet music file (any music PDF)
2. Wait for analysis to complete
3. Check that you see the analysis results:
   - Notes detected
   - Time signature
   - Key signature
   - Tempo

#### 5.6 Test Recording Feature

1. Click **"Start Recording"**
2. Allow microphone access if prompted
3. Play a note or hum
4. Click **"Stop Recording"**
5. Verify analysis completes and you receive feedback

## 🔧 Advanced Configuration

### Using PostgreSQL Database

For production deployments with multiple users, consider PostgreSQL instead of SQLite:

**Option 1: Leapcell Managed Database**
1. Add a PostgreSQL addon in Leapcell dashboard
2. Leapcell will automatically provide a `DATABASE_URL` environment variable
3. The application will detect and use it automatically

**Option 2: External PostgreSQL**
1. Use a service like [Neon](https://neon.tech), [Supabase](https://supabase.com), or [ElephantSQL](https://www.elephantsql.com)
2. Get the connection string (format: `postgresql://user:password@host:5432/database`)
3. Add as `DATABASE_URL` environment variable in Leapcell

**Why PostgreSQL?**
- Better for concurrent users
- More reliable for production
- Better query performance
- ACID compliance
- Better for long-term data storage

### Scaling Your Application

As your user base grows, you may need to scale:

**Vertical Scaling (More Resources):**
1. Go to project settings in Leapcell
2. Increase memory allocation (512MB → 1GB → 2GB)
3. Increase CPU allocation if available
4. Restart the service

**Horizontal Scaling (More Workers):**

Modify the Gunicorn workers in `Dockerfile.leapcell`:
```dockerfile
# Change from 4 workers to 8
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "8", ...]
```

**Worker Formula:**
```
workers = (2 × CPU cores) + 1
```

For 2 CPU cores: 5 workers recommended
For 4 CPU cores: 9 workers recommended

### Custom Domain Setup

To use your own domain (e.g., `mugic.yourdomain.com`):

1. **In Leapcell Dashboard:**
   - Go to your project → **Settings** → **Domains**
   - Click **"Add Custom Domain"**
   - Enter your domain (e.g., `mugic.yourdomain.com`)

2. **In Your DNS Provider:**
   - Add a CNAME record:
     - Name: `mugic` (or your subdomain)
     - Value: `your-app.leapcell.io` (provided by Leapcell)
     - TTL: 3600 (1 hour) or Auto

3. **Wait for SSL Provisioning:**
   - Leapcell will automatically provision a Let's Encrypt SSL certificate
   - This usually takes 5-15 minutes
   - Once ready, your app will be accessible via HTTPS at your custom domain

### File Storage Considerations

**Important Note:** Docker containers in Leapcell are **ephemeral**, meaning:

- The `uploads/` and `recordings/` directories are temporary
- Files are lost when the container restarts or redeploys
- Not suitable for long-term file storage

**Solutions for Persistent Storage:**

**Option 1: External Object Storage (Recommended)**
- Use AWS S3, Cloudflare R2, or Backblaze B2
- Store uploaded PDFs and recordings externally
- Modify `app.py` to upload files to object storage
- Reference files by URL instead of local path

**Option 2: Volume Mounting (If Supported)**
- Check if Leapcell supports persistent volumes
- Mount a volume to `/app/uploads` and `/app/recordings`
- Consult Leapcell documentation for volume setup

**Option 3: Database Storage (For Small Files)**
- Store file contents in PostgreSQL BYTEA fields
- Good for small files (<1MB)
- Not recommended for large PDFs or audio files

## 📊 Monitoring and Logs

### Viewing Application Logs

1. **Access Logs:**
   - Go to Leapcell dashboard
   - Select your **mugic-web** service
   - Click **"Logs"** or **"Runtime Logs"**

2. **Log Types:**
   - **Build Logs**: Docker image build process
   - **Runtime Logs**: Application stdout/stderr
   - **Access Logs**: HTTP requests (from Gunicorn)
   - **Error Logs**: Application errors (from Gunicorn)

3. **Filtering Logs:**
   - Filter by time range
   - Search for specific keywords
   - Filter by log level (INFO, WARNING, ERROR)

### Key Metrics to Monitor

**Performance Metrics:**
- Response time (should be <2 seconds for most requests)
- Request count (track usage patterns)
- Error rate (should be <1%)
- Memory usage (should stay under 80% of allocated)
- CPU usage (spikes are normal during OMR processing)

**Health Indicators:**
- Health check success rate (should be 100%)
- Container restart count (should be 0 or very low)
- Build success rate (should be 100% for deployments)

### Setting Up Alerts (If Available)

Configure alerts in Leapcell for:
- High error rate (>5% of requests)
- Memory usage >90%
- Health check failures
- Container crashes/restarts

## 🐛 Troubleshooting Common Issues

### Issue: Build Fails During Dependency Installation

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement [package]
```

**Solutions:**
1. Check that `requirements-flask.txt` exists and is valid
2. Verify Python 3.11 compatibility of all packages
3. Review build logs for specific package errors
4. Try pinning problematic package to a specific version

### Issue: Application Crashes on Startup

**Symptoms:**
- Container restarts repeatedly
- Health checks fail immediately
- "Application Error" page displayed

**Solutions:**

1. **Check Environment Variables:**
   ```bash
   # Verify SECRET_KEY and JWT_SECRET_KEY are set
   # They should be 64+ character hex strings
   ```

2. **Review Startup Logs:**
   - Look for Python exceptions
   - Check for missing dependencies
   - Verify database connection (if using PostgreSQL)

3. **Common Startup Errors:**
   - `RuntimeError: SECRET_KEY not set` → Set SECRET_KEY in environment variables
   - `sqlalchemy.exc.OperationalError` → Database connection issue
   - `ImportError: No module named 'X'` → Missing dependency

### Issue: OMR/Sheet Music Analysis Fails

**Symptoms:**
- Upload succeeds but analysis fails
- Error: "Could not analyze sheet music"
- Timeout during OMR processing

**Solutions:**

1. **Verify Java Installation:**
   ```bash
   # Check logs for:
   openjdk version "17.0.X"
   ```

2. **Check File Format:**
   - Ensure file is a valid PDF
   - Check file size (should be <50MB)
   - Try with a different PDF

3. **Fallback to OEMER:**
   - If Audiveris fails, OEMER will be used automatically
   - OEMER is Python-based (no Java required)
   - Check logs: "Using OEMER OMR system"

4. **Increase Timeout:**
   - Large PDFs may need more time
   - Gunicorn timeout is 120 seconds
   - Consider increasing in Dockerfile.leapcell

### Issue: Audio Recording Not Working

**Symptoms:**
- Recording button doesn't start
- No audio is captured
- Analysis fails with "No audio data"

**Solutions:**

1. **Browser Permissions:**
   - Ensure HTTPS is enabled (required for microphone access)
   - Check browser microphone permissions
   - Try a different browser (Chrome recommended)

2. **Microphone Access:**
   - Check system microphone settings
   - Ensure microphone is not muted
   - Test microphone with another app

3. **File Upload:**
   - Try uploading a pre-recorded audio file instead
   - Check audio format (WAV, MP3, OGG supported)

### Issue: Health Check Failing

**Symptoms:**
```
Health check failed: Connection refused
Health check timeout
```

**Solutions:**

1. **Verify Port Configuration:**
   - Ensure Dockerfile uses port 8080
   - Check `EXPOSE 8080` in Dockerfile
   - Verify Gunicorn binds to `0.0.0.0:8080`

2. **Check Health Endpoint:**
   ```python
   # In app.py, verify this exists:
   @app.route('/health')
   def health_check():
       return jsonify({"status": "healthy"}), 200
   ```

3. **Review Health Check Settings:**
   - Interval: 30 seconds (time between checks)
   - Timeout: 10 seconds (how long to wait)
   - Retries: 3 (failures before marking unhealthy)
   - Start period: 40 seconds (grace period at startup)

### Issue: Slow Performance / Timeouts

**Symptoms:**
- Requests take >30 seconds
- 504 Gateway Timeout errors
- OMR processing times out

**Solutions:**

1. **Increase Resources:**
   - Upgrade to 2GB RAM
   - Request more CPU cores
   - Check resource usage in Leapcell dashboard

2. **Optimize Workers:**
   - Too many workers can cause memory issues
   - Too few workers can cause queuing
   - Formula: `workers = (2 × CPU_cores) + 1`

3. **Use Async Processing (Advanced):**
   - Implement background jobs for OMR
   - Use Celery or Redis Queue
   - Return immediately, notify user when complete

### Issue: Database Errors

**Symptoms:**
```
sqlalchemy.exc.OperationalError: unable to open database file
sqlalchemy.exc.IntegrityError: UNIQUE constraint failed
```

**Solutions:**

1. **SQLite Issues (Default):**
   - SQLite may have permission issues in containers
   - Consider switching to PostgreSQL
   - Check write permissions on database file

2. **Switch to PostgreSQL:**
   ```bash
   # Add DATABASE_URL environment variable
   DATABASE_URL=postgresql://user:password@host:5432/database
   ```

3. **Database Migrations:**
   - The app auto-creates tables on first run
   - If issues persist, check SQLAlchemy logs
   - May need manual database initialization

## 🔄 Updating Your Deployment

### Automatic Deployments (Recommended)

Enable automatic deployments for continuous integration:

1. **In Leapcell Dashboard:**
   - Go to project settings
   - Find **"Auto Deploy"** or **"Automatic Deployments"**
   - Enable for your `main` or `master` branch

2. **How It Works:**
   - Every push to GitHub triggers a new build
   - Leapcell pulls the latest code
   - Rebuilds the Docker image
   - Deploys automatically
   - Zero-downtime deployment

### Manual Deployments

To manually trigger a deployment:

1. **Push Changes to GitHub:**
   ```bash
   git add .
   git commit -m "Update feature X"
   git push origin main
   ```

2. **In Leapcell Dashboard:**
   - Go to your **mugic-web** service
   - Click **"Redeploy"** or **"Deploy Latest"**
   - Wait for build to complete

### Rollback to Previous Version

If a deployment breaks something:

1. **In Leapcell Dashboard:**
   - Go to **"Deployments"** or **"History"**
   - Find the previous working deployment
   - Click **"Rollback"** or **"Redeploy"**

2. **Fix Issue Locally:**
   - Debug the problem
   - Test locally
   - Push fix to GitHub
   - Redeploy

## 💰 Cost Considerations

### Free Tier

Leapcell typically offers a free tier with:
- ✅ 512MB-1GB RAM
- ✅ Public subdomain (`*.leapcell.io`)
- ✅ Basic resources
- ✅ Community support
- ⏰ May have usage limits (hours per month or concurrent users)

**Good for:**
- Personal projects
- Testing and development
- Small user base (<100 users)
- Portfolio projects

### Paid Plans

For production use with more users, consider upgrading:

| Feature | Free Tier | Paid Tier |
|---------|-----------|-----------|
| Memory | 512MB-1GB | 2GB-8GB+ |
| CPU | Shared | Dedicated |
| Uptime | Best effort | 99.9% SLA |
| Support | Community | Priority |
| Custom domain | ❌ | ✅ |
| Auto-scaling | ❌ | ✅ |
| Advanced metrics | ❌ | ✅ |

**Typical Pricing:**
- ~$5-10/month for 1GB RAM dedicated
- ~$20-30/month for 2GB RAM + features
- ~$50+/month for high-performance setup

### Optimization Tips to Reduce Costs

1. **Use Efficient OMR:**
   - OEMER is faster than Audiveris
   - Consider caching OMR results

2. **Implement Caching:**
   - Cache analyzed sheet music
   - Cache audio analysis results
   - Use Redis for session storage

3. **Optimize Docker Image:**
   - Use multi-stage builds
   - Remove unnecessary dependencies
   - Compress assets

4. **Monitor Usage:**
   - Track peak usage times
   - Identify expensive operations
   - Optimize hot paths

## 🔒 Security Best Practices

### 1. Environment Variables

✅ **DO:**
- Use Leapcell's environment variable UI
- Generate strong random keys
- Use different keys per environment
- Rotate keys periodically (every 90 days)

❌ **DON'T:**
- Commit secrets to Git
- Use default or example keys
- Share keys in chat/email
- Reuse keys across projects

### 2. HTTPS Configuration

✅ **DO:**
- Always use HTTPS in production
- Enable HSTS (HTTP Strict Transport Security)
- Use secure cookies
- Redirect HTTP to HTTPS

❌ **DON'T:**
- Allow HTTP in production
- Disable SSL verification
- Use self-signed certificates

### 3. Database Security

✅ **DO:**
- Use PostgreSQL in production
- Use strong database passwords
- Restrict database access by IP
- Enable SSL for database connections
- Regular backups

❌ **DON'T:**
- Use default database passwords
- Expose database ports publicly
- Store sensitive data unencrypted

### 4. Application Security

✅ **DO:**
- Keep dependencies updated
- Use Flask security best practices
- Implement rate limiting
- Validate all user input
- Log security events

❌ **DON'T:**
- Run in debug mode in production
- Trust user input without validation
- Ignore security updates
- Disable CORS protections

## 📚 Additional Resources

### Leapcell Documentation
- Official Docs: Check Leapcell's documentation site
- Docker Guide: Leapcell Docker deployment guide
- Environment Variables: How to manage secrets
- Custom Domains: Setting up your own domain

### Mugic Documentation
- [Main README](README.md): Overview and features
- [General Deployment Guide](DEPLOYMENT.md): All deployment options
- [Render Deployment](RENDER_DEPLOYMENT.md): Alternative Docker deployment
- [Vercel Deployment](VERCEL_DEPLOYMENT.md): Serverless deployment

### Related Technologies
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Docker Documentation](https://docs.docker.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### Getting Help

**Leapcell Support:**
- Documentation: Official Leapcell docs
- Community: Join Leapcell Discord/Slack
- Support Email: Contact Leapcell support team

**Mugic Support:**
- GitHub Issues: [Report bugs or request features](https://github.com/masterofmagic999/mugic/issues)
- Discussions: Ask questions in GitHub Discussions
- Pull Requests: Contribute improvements

## 🎉 Success Checklist

Before considering your deployment complete, verify:

- [ ] Application is accessible via public URL
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Homepage loads without errors
- [ ] User registration works
- [ ] User login works
- [ ] PDF upload and analysis works
- [ ] Audio recording works
- [ ] Feedback generation works
- [ ] All environment variables are set
- [ ] Logs show no critical errors
- [ ] Java/Audiveris logs show "Using Audiveris OMR" (or OEMER fallback)
- [ ] SSL certificate is active (HTTPS working)
- [ ] Custom domain configured (if applicable)
- [ ] Database backups configured (if using PostgreSQL)
- [ ] Monitoring/alerts set up

## 🚀 Next Steps

Now that Mugic is deployed on Leapcell:

1. **Share Your App:**
   - Share the URL with musicians
   - Get feedback from users
   - Iterate on features

2. **Monitor Performance:**
   - Check logs regularly
   - Monitor resource usage
   - Track user engagement

3. **Scale as Needed:**
   - Upgrade resources when needed
   - Enable auto-scaling
   - Optimize performance bottlenecks

4. **Keep It Updated:**
   - Apply security updates
   - Add new features
   - Fix bugs promptly

5. **Consider Enhancements:**
   - Add PostgreSQL for better performance
   - Implement file storage (S3, etc.)
   - Add caching (Redis)
   - Set up CI/CD pipeline
   - Add monitoring (DataDog, New Relic, etc.)

---

**Congratulations!** 🎊 You've successfully deployed Mugic to Leapcell with full Docker and Java support! Your users can now practice music with AI-powered feedback anywhere, anytime.

**Questions or issues?** Open an issue on [GitHub](https://github.com/masterofmagic999/mugic/issues) or consult the [DEPLOYMENT.md](DEPLOYMENT.md) for more options.

**Made with ❤️ for musicians everywhere**

