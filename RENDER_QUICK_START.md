# 🚀 Render Quick Start

Deploy Mugic to Render in 3 easy ways!

## ⚡ Option 1: One-Click Deploy (Recommended)

**Fastest deployment - takes less than 1 minute to start!**

1. Click here: [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/masterofmagic999/mugic)

2. Authorize GitHub access

3. Click "Apply" - all settings are pre-configured!

4. Wait 5-15 minutes for build

5. Done! Your app is live at `https://mugic-xxxx.onrender.com`

---

## 📘 Option 2: Blueprint Deploy

1. Fork this repository to your GitHub account

2. Visit https://render.com and sign up/login

3. Click "New +" → "Blueprint"

4. Select your forked repository

5. Render auto-detects `render.yaml`

6. Click "Apply"

---

## 🔧 Option 3: Manual Deploy

1. Visit https://render.com and sign up/login

2. Click "New +" → "Web Service"

3. Connect your repository

4. Configure:
   - **Environment**: Docker
   - **Dockerfile Path**: `./Dockerfile.render`
   - **Region**: Oregon (or nearest)

5. Add environment variables:
   - `SECRET_KEY` = (click Generate)
   - `JWT_SECRET_KEY` = (click Generate)
   - `FLASK_ENV` = production

6. Click "Create Web Service"

---

## ✅ What's Included

- ✅ Full Java/Audiveris OMR support (OpenJDK 21)
- ✅ All Python dependencies pre-installed
- ✅ Automatic SSL certificates
- ✅ Health check monitoring
- ✅ Auto-scaling (on paid plans)
- ✅ 750 hours/month free tier

---

## 🐛 Troubleshooting

**Build fails with apt-get error?**
- The updated Dockerfiles now use OpenJDK 21 with fallbacks
- This should work automatically

**App won't start?**
- Check environment variables are set
- Review logs in Render dashboard
- Ensure `render.json` is in your repository

**Need more help?**
- See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed guide
- See [DEPLOYMENT.md](DEPLOYMENT.md) for all deployment options

---

## 🎯 After Deployment

1. Visit your app URL
2. Create an account
3. Upload PDF sheet music
4. Record and get feedback!

---

**Questions?** Open an issue on GitHub or check the documentation.
