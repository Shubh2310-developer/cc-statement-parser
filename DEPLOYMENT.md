# 🚀 Deployment Guide

Complete guide to deploy the Credit Card Statement Parser to production.

## Architecture Overview

```
Frontend (Vercel)  ←→  Backend (Render.com)
   React + Vite         FastAPI + Python
   Port: 443 (HTTPS)    Port: 10000
```

---

## 📋 Prerequisites

- [GitHub Account](https://github.com) (for code hosting)
- [Render.com Account](https://render.com) (for backend - FREE tier available)
- [Vercel Account](https://vercel.com) (for frontend - FREE tier available)
- Git installed locally

---

## Part 1: Backend Deployment (Render.com)

### Step 1: Push Code to GitHub

```bash
# Navigate to project directory
cd /home/ghost/cc-statement-parser

# Initialize git (if not already done)
git init
git add .
git commit -m "Prepare for deployment"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/cc-statement-parser.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render.com

1. **Go to [Render.com](https://render.com)** and sign up/login

2. **Click "New +" → "Web Service"**

3. **Connect your GitHub repository:**
   - Select `cc-statement-parser` repository
   - Click "Connect"

4. **Configure the service:**
   ```
   Name: cc-statement-parser-backend
   Region: Singapore / Frankfurt (choose nearest)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

5. **Select Plan:**
   - Choose **"Free"** plan (0 cost)
   - Note: Free tier sleeps after 15 min inactivity

6. **Add Environment Variables:**
   Click "Advanced" → "Add Environment Variable":
   ```
   PYTHON_VERSION=3.10.12
   ENVIRONMENT=production
   DATABASE_URL=sqlite:///./data/db/cc_parser.db
   UPLOAD_DIR=./data/uploads
   LOG_DIR=./logs
   DEBUG=False
   ```

7. **Add Disk Storage (Important!):**
   - Click "Add Disk"
   - Mount Path: `/opt/render/project/src/data`
   - Size: 1 GB (Free tier)
   - This persists uploaded PDFs and database

8. **Click "Create Web Service"**
   - Wait 5-10 minutes for build
   - You'll get a URL like: `https://cc-statement-parser-backend.onrender.com`

9. **Test Backend:**
   ```bash
   curl https://YOUR-BACKEND-URL.onrender.com/health
   ```
   Should return:
   ```json
   {
     "status": "healthy",
     "version": "1.0.0",
     "app_name": "CC Statement Parser",
     "timestamp": "2025-10-15T..."
   }
   ```

### Step 3: Update CORS Settings

After deployment, update the backend config to allow your Vercel domain:

1. **Go to Render Dashboard** → Your Service → Environment

2. **Add CORS environment variable:**
   ```
   CORS_ORIGINS=["https://your-app.vercel.app","http://localhost:5173"]
   ```

3. **Click "Save Changes"** (service will auto-redeploy)

---

## Part 2: Frontend Deployment (Vercel)

### Step 1: Create Environment File

```bash
cd /home/ghost/cc-statement-parser/frontend

# Create production environment file
cat > .env.production << EOF
VITE_API_URL=https://YOUR-BACKEND-URL.onrender.com
EOF
```

Replace `YOUR-BACKEND-URL` with your actual Render backend URL.

### Step 2: Test Build Locally

```bash
# Install dependencies
npm install

# Test production build
npm run build

# Preview production build
npm run preview
```

### Step 3: Deploy on Vercel

**Option A: Via Vercel Dashboard (Recommended)**

1. **Go to [Vercel](https://vercel.com)** and login

2. **Click "Add New..." → "Project"**

3. **Import Git Repository:**
   - Select `cc-statement-parser` from GitHub
   - Click "Import"

4. **Configure Project:**
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

5. **Add Environment Variables:**
   Click "Environment Variables" → Add:
   ```
   Key: VITE_API_URL
   Value: https://YOUR-BACKEND-URL.onrender.com
   ```

6. **Click "Deploy"**
   - Wait 2-3 minutes
   - You'll get a URL like: `https://cc-statement-parser.vercel.app`

**Option B: Via Vercel CLI**

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
cd /home/ghost/cc-statement-parser/frontend
vercel --prod

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? cc-statement-parser
# - Directory? ./
# - Override settings? Yes
# - Build Command? npm run build
# - Output Directory? dist
# - Development Command? npm run dev
```

### Step 4: Update Backend CORS

Go back to Render.com and update the CORS environment variable with your Vercel URL:

```
CORS_ORIGINS=["https://cc-statement-parser.vercel.app","http://localhost:5173"]
```

---

## Part 3: Post-Deployment

### Verify Deployment

1. **Test Backend Health:**
   ```bash
   curl https://YOUR-BACKEND-URL.onrender.com/health
   ```

2. **Test Frontend:**
   - Open `https://YOUR-FRONTEND-URL.vercel.app`
   - Try uploading a PDF
   - Check if results are displayed

3. **Check Browser Console:**
   - Open DevTools (F12)
   - Verify no CORS errors
   - Check API requests are going to correct backend URL

### Monitor Services

**Render.com (Backend):**
- Dashboard → Your Service → Logs
- Monitor for errors, memory usage, response times

**Vercel (Frontend):**
- Dashboard → Your Project → Logs
- Check build logs, deployment status

---

## 🔧 Configuration Files Created

| File | Purpose |
|------|---------|
| `backend/render.yaml` | Render.com deployment config |
| `backend/.env.production` | Production environment variables |
| `frontend/.env.example` | Template for environment variables |
| `DEPLOYMENT.md` | This deployment guide |

---

## 🌐 URLs After Deployment

| Service | URL | Purpose |
|---------|-----|---------|
| **Backend API** | `https://YOUR-APP.onrender.com` | FastAPI endpoints |
| **API Docs** | `https://YOUR-APP.onrender.com/docs` | Swagger UI |
| **Health Check** | `https://YOUR-APP.onrender.com/health` | Service health |
| **Frontend** | `https://YOUR-APP.vercel.app` | React UI |

---

## 🎯 Final Checklist

- [ ] Backend deployed on Render.com
- [ ] Backend health endpoint returns 200
- [ ] Backend disk storage configured (1GB)
- [ ] Frontend deployed on Vercel
- [ ] Frontend environment variable set (`VITE_API_URL`)
- [ ] Backend CORS updated with Vercel domain
- [ ] Test file upload end-to-end
- [ ] Check browser console for errors
- [ ] Monitor logs for 24 hours

---

## 🐛 Troubleshooting

### Issue: CORS Error in Browser

**Symptom:** `Access-Control-Allow-Origin` error in console

**Solution:**
1. Check backend CORS settings include your Vercel domain
2. Update environment variable in Render:
   ```
   CORS_ORIGINS=["https://your-app.vercel.app"]
   ```
3. Wait for auto-redeploy (2-3 minutes)

### Issue: Backend Returns 404

**Symptom:** API requests fail with 404

**Solution:**
1. Verify API URL in frontend `.env.production`
2. Check backend is running: `curl YOUR-BACKEND-URL/health`
3. Verify Root Directory is set to `backend` in Render

### Issue: File Upload Fails

**Symptom:** 500 error on upload

**Solution:**
1. Check disk storage is mounted in Render
2. Mount path: `/opt/render/project/src/data`
3. Verify logs in Render dashboard

### Issue: Backend Sleeps (Free Tier)

**Symptom:** First request after inactivity takes 30s+

**Solution:**
- This is expected on Render's free tier
- Backend "wakes up" on first request
- Consider upgrading to paid tier ($7/month) for 24/7 uptime
- Or implement a ping service (cron-job.org) to keep it alive

### Issue: Database Resets

**Symptom:** Uploaded files disappear after redeployment

**Solution:**
1. Ensure disk storage is configured in Render
2. Database and uploads should persist in `/opt/render/project/src/data`
3. Check disk is properly mounted

---

## 💰 Cost Breakdown

| Service | Plan | Cost | Features |
|---------|------|------|----------|
| **Render.com** | Free | $0/month | 750 hrs/month, sleeps after 15min |
| **Vercel** | Hobby | $0/month | Unlimited bandwidth, auto-scaling |
| **Total** | | **$0/month** | Perfect for demo/personal use |

### Upgrade Options (Optional)

| Service | Plan | Cost | Benefits |
|---------|------|------|----------|
| **Render.com** | Starter | $7/month | 24/7 uptime, no sleeping |
| **Render.com** | Standard | $25/month | More CPU/RAM, faster |

---

## 🔄 Continuous Deployment

Both Vercel and Render support automatic deployments:

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```

2. **Automatic Deployment:**
   - Render detects changes and rebuilds backend
   - Vercel detects changes and rebuilds frontend
   - Both deploy automatically (2-5 minutes)

3. **Rollback:**
   - Both platforms support instant rollback via dashboard
   - Vercel: Deployments → Previous Deployment → "Promote to Production"
   - Render: Events → Previous Deploy → "Rollback"

---

## 📊 Performance Optimization

### Backend (Render)

1. **Enable Compression:**
   ```python
   # Add to app/main.py
   from fastapi.middleware.gzip import GZipMiddleware
   app.add_middleware(GZipMiddleware, minimum_size=1000)
   ```

2. **Add Caching:**
   ```python
   from fastapi_cache import FastAPICache
   from fastapi_cache.backends.inmemory import InMemoryBackend
   ```

3. **Upgrade Plan:**
   - Free tier: 512MB RAM, 0.1 CPU
   - Starter: 512MB RAM, 0.5 CPU (faster)

### Frontend (Vercel)

1. **Code Splitting:** Already enabled via Vite
2. **Image Optimization:** Use Vercel Image Optimization
3. **Edge Functions:** Move API calls to edge (optional)

---

## 🔐 Security Recommendations

1. **Environment Variables:**
   - Never commit `.env` files
   - Use platform-specific environment variable managers

2. **API Rate Limiting:**
   ```python
   # Add to backend
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   ```

3. **HTTPS Only:**
   - Both platforms provide free SSL
   - Enforce HTTPS in backend CORS settings

4. **File Upload Security:**
   - Already validated: PDF only, 10MB max
   - Consider adding virus scanning for production

---

## 📧 Support

- **Render Issues:** [Render Docs](https://render.com/docs)
- **Vercel Issues:** [Vercel Docs](https://vercel.com/docs)
- **Project Issues:** Create GitHub issue

---

## 🎉 Success!

Your Credit Card Statement Parser is now live and accessible worldwide!

**Next Steps:**
1. Share your deployment URL
2. Gather user feedback
3. Monitor logs and performance
4. Add more banks/features
5. Consider upgrading plans for production use

---

**Deployed by:** [Your Name]
**Date:** 2025-10-15
**Version:** 1.0.0
