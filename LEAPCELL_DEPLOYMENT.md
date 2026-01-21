# Leapcell Deployment Guide for Mugic 🎵

## Overview

Leapcell is our recommended deployment platform for Mugic. It provides modern, fast deployment with excellent Flask support, automatic SSL, and easy scaling.

## Prerequisites

- A [GitHub](https://github.com) account
- A [Leapcell](https://leapcell.io) account (sign up for free)
- Your Mugic repository forked or accessible

## Quick Deployment Steps

### 1. Sign Up for Leapcell

1. Visit [https://leapcell.io](https://leapcell.io)
2. Sign up using your GitHub account
3. Authorize Leapcell to access your repositories

### 2. Create a New Project

1. Click **"New Project"** or **"Deploy"** in the Leapcell dashboard
2. Select **"Import from GitHub"**
3. Choose your `mugic` repository
4. Leapcell will automatically detect the `leapcell.json` configuration

### 3. Configure Environment Variables

Before deploying, set the following required environment variables in the Leapcell dashboard:

#### Required Variables

1. **`SECRET_KEY`**
   - Used for Flask session encryption
   - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
   - Example: `a7f3e9c2b5d8f1a4e6c9b2d5f8e1c4a7b0d3f6e9c2b5d8f1a4e7c0b3f6e9c2b5`

2. **`JWT_SECRET_KEY`**
   - Used for JWT token signing
   - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
   - Example: `b8g4f0d3c6e9b2d5f8e1c4a7b0d3f6e9c2b5d8f1a4e7c0b3f6e9c2b5d8f1a4`

#### Optional Variables

- **`FLASK_ENV`**: Set to `production` (default in leapcell.json)
- **`DATABASE_URL`**: If using PostgreSQL instead of SQLite
- **`PORT`**: Application port (default: 8080)

### 4. Deploy

1. Click **"Deploy"** or **"Create"**
2. Leapcell will:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Start the application using Gunicorn
   - Assign a public URL
3. Wait 2-5 minutes for the first deployment

### 5. Verify Deployment

Once deployed, visit your app's URL and verify:

1. **Homepage loads** - You should see the Mugic interface
2. **Health check** - Visit `https://your-app.leapcell.io/health`
3. **Authentication** - Try signing up/logging in
4. **Upload feature** - Test uploading a PDF sheet music
5. **Recording** - Test the audio recording feature

## Configuration Details

### leapcell.json

The repository includes a `leapcell.json` configuration file:

```json
{
  "name": "mugic",
  "type": "web",
  "runtime": "python",
  "version": "3.11",
  "buildCommand": "pip install -r requirements.txt",
  "startCommand": "gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120",
  "env": {
    "FLASK_ENV": "production",
    "SECRET_KEY": "",
    "JWT_SECRET_KEY": "",
    "PORT": "8080"
  },
  "health": {
    "path": "/health",
    "interval": 30
  }
}
```

### Key Settings

- **Runtime**: Python 3.11
- **Workers**: 2 Gunicorn workers for handling concurrent requests
- **Timeout**: 120 seconds for long-running OMR operations
- **Health Check**: `/health` endpoint checked every 30 seconds

## Advanced Configuration

### Using PostgreSQL Database

For production deployments, consider using PostgreSQL instead of SQLite:

1. Add a PostgreSQL addon in Leapcell dashboard
2. Leapcell will provide a `DATABASE_URL` environment variable
3. The application will automatically use it if present

### Scaling

Leapcell allows you to scale your application:

1. Go to your project settings
2. Increase the number of workers
3. Adjust memory/CPU allocation
4. Enable auto-scaling if available

### Custom Domain

To use a custom domain:

1. Go to project settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed
4. Leapcell will provision SSL automatically

## Troubleshooting

### Build Failures

**Issue**: Dependencies fail to install

**Solutions**:
- Check that `requirements.txt` is present and valid
- Verify Python 3.11 compatibility of all packages
- Check Leapcell build logs for specific errors

### Application Won't Start

**Issue**: Application crashes on startup

**Solutions**:
- Verify `SECRET_KEY` and `JWT_SECRET_KEY` are set
- Check application logs in Leapcell dashboard
- Ensure `app.py` runs locally without errors
- Verify port configuration matches

### OMR Not Working

**Issue**: Sheet music analysis fails

**Solutions**:
- OEMER is the primary OMR system (no Java needed)
- Check if PDF files are valid
- Verify `opencv-python` and dependencies installed correctly
- Check application logs for OMR errors

### Audio Recording Issues

**Issue**: Audio recording or analysis fails

**Solutions**:
- Ensure browser has microphone permissions
- Check if `basic-pitch` is installed correctly
- Verify `ffmpeg` system package is available
- Test with different audio file formats

## Monitoring and Logs

### Viewing Logs

1. Go to your project in Leapcell dashboard
2. Click on **"Logs"** or **"Runtime Logs"**
3. Filter by time range or search for specific errors

### Performance Monitoring

Monitor these metrics in Leapcell dashboard:
- Response times
- Memory usage
- CPU usage
- Request count
- Error rate

## Updating Your Deployment

### Automatic Deployments

Enable automatic deployments for continuous deployment:

1. Go to project settings
2. Enable **"Auto Deploy"** for your main branch
3. Every push to GitHub will trigger a new deployment

### Manual Deployments

To manually deploy:

1. Push changes to GitHub
2. Go to Leapcell dashboard
3. Click **"Redeploy"** or **"Deploy Latest"**

## Cost Considerations

### Free Tier

Leapcell typically offers a free tier with:
- Limited hours per month
- Basic resources (512MB-1GB RAM)
- Public subdomain
- Community support

### Paid Plans

For production use, consider:
- More compute resources
- Custom domains
- Higher uptime guarantees
- Priority support
- Advanced monitoring

## Security Best Practices

1. **Never commit secrets** to Git
   - Use environment variables for all secrets
   - Add `.env` to `.gitignore`

2. **Use strong keys**
   - Generate random SECRET_KEY and JWT_SECRET_KEY
   - Never reuse keys across environments

3. **Enable HTTPS**
   - Leapcell provides automatic SSL
   - Enforce HTTPS redirects

4. **Regular updates**
   - Keep dependencies updated
   - Monitor security advisories
   - Apply patches promptly

## Support and Resources

### Leapcell Resources
- Documentation: Check Leapcell docs site
- Community: Join Leapcell Discord/Slack
- Support: Contact Leapcell support team

### Mugic Resources
- Repository: [https://github.com/masterofmagic999/mugic](https://github.com/masterofmagic999/mugic)
- Issues: Report bugs on GitHub Issues
- Deployment Docs: See [DEPLOYMENT.md](DEPLOYMENT.md)

## Comparison with Other Platforms

| Feature | Leapcell | Render | Railway | Vercel |
|---------|----------|--------|---------|--------|
| Flask Support | ✅ Excellent | ✅ Good | ✅ Good | ⚠️ Limited |
| Python 3.11+ | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Free Tier | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Auto SSL | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| WebSocket | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Limited |
| Long Timeouts | ✅ Yes | ✅ Yes | ✅ Yes | ❌ 10s limit |
| Setup Time | ⚡ 5 min | ⚡ 5 min | ⚡ 5 min | ⚡ 3 min |

**Why Leapcell?**
- Modern platform optimized for Flask
- Easy configuration with `leapcell.json`
- Good balance of features and simplicity
- Suitable for OMR processing (long timeouts)

---

**Ready to deploy?** Follow the steps above and you'll have Mugic running on Leapcell in minutes! 🚀
