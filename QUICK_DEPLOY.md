# Quick Deployment Guide for Free Platforms (No Credit Card)

This guide will help you deploy Mugic to free hosting platforms without needing a credit card.

## Generate Your Secret Keys First

Before deploying, generate secure secret keys. Run these commands in Python:

```python
import secrets
print("SECRET_KEY:", secrets.token_hex(32))
print("JWT_SECRET_KEY:", secrets.token_hex(32))
```

Or use this one-liner in terminal:
```bash
python -c "import secrets; print('SECRET_KEY:', secrets.token_hex(32)); print('JWT_SECRET_KEY:', secrets.token_hex(32))"
```

Save these keys - you'll need them for deployment!

---

## Option 1: PythonAnywhere (Recommended for Beginners)

**Best for:** Python developers, long-term hosting, no sleep

**Steps:**
1. Go to https://www.pythonanywhere.com
2. Sign up for a free account (no credit card needed)
3. Click "Open Bash console" from dashboard
4. Run:
   ```bash
   git clone https://github.com/yourusername/mugic.git
   cd mugic
   mkvirtualenv --python=/usr/bin/python3.10 mugic
   pip install -r requirements.txt
   ```
5. Go to "Web" tab → "Add a new web app"
6. Choose "Manual configuration" → Python 3.10
7. Set virtualenv: `/home/yourusername/.virtualenvs/mugic`
8. Edit WSGI file (update paths and add your secret keys from step 1)
9. Reload web app

**URL:** Your app will be at `yourusername.pythonanywhere.com`

---

## Option 2: Replit (Fastest Setup)

**Best for:** Testing, quick demos, collaborative development

**Steps:**
1. Go to https://replit.com
2. Sign up for free (no credit card)
3. Click "Create Repl" → "Import from GitHub"
4. Paste your repository URL
5. In "Secrets" tab (🔒 icon), add:
   - `SECRET_KEY` = your generated key
   - `JWT_SECRET_KEY` = your generated key
6. Click "Run"

**URL:** Your app will be at `your-repl-name.yourusername.repl.co`

---

## Option 3: Glitch (Simplest)

**Best for:** Quick deployment, live editing

**Steps:**
1. Go to https://glitch.com
2. Sign up for free (no credit card)
3. Click "New Project" → "Import from GitHub"
4. Paste your repository URL
5. Edit `.env` file in Glitch editor:
   ```
   SECRET_KEY=your-generated-key
   JWT_SECRET_KEY=your-generated-key
   FLASK_ENV=production
   ```
6. App auto-deploys!

**URL:** Your app will be at `your-project-name.glitch.me`

---

## Option 4: Koyeb (Best Performance for Free)

**Best for:** Production-like environment, always-on apps

**Steps:**
1. Go to https://www.koyeb.com
2. Sign up for free
3. Click "Create App" → "GitHub"
4. Select your repository
5. Add environment variables:
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `FLASK_ENV` = production
6. Click "Deploy"

**URL:** Your app will be at `app-name.koyeb.app`

---

## Troubleshooting

**App won't start:**
- Check that all environment variables are set correctly
- Verify Python version is 3.10 or higher
- Check platform logs for error messages

**Dependencies fail to install:**
- Some free platforms have limited resources
- Try reducing the ML model size in requirements.txt
- Consider removing heavy dependencies like torch if needed

**App is slow:**
- Free tiers have limited CPU/RAM
- Consider upgrading or using a lighter configuration
- Some platforms sleep after inactivity - first request will be slow

**Need help?**
- Check the full DEPLOYMENT.md for detailed instructions
- Open an issue on GitHub
- Consult platform-specific documentation

---

## What's Next?

After deployment:
1. Test your app thoroughly
2. Set up your user account
3. Upload sheet music and start practicing!
4. Consider upgrading if you need more resources

For detailed instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)
