# 🚀 Quick Deployment Summary

## What You Need to Do

### Method 1: Vercel (Frontend) + Render.com (Backend) ✅ RECOMMENDED

This is the **easiest and FREE** way to deploy your project.

---

## 📍 Step-by-Step (5 Minutes)

### Step 1: Push to GitHub

```bash
cd /home/ghost/cc-statement-parser

# If not already a git repo
git init
git add .
git commit -m "Ready for deployment"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/cc-statement-parser.git
git push -u origin main
```

---

### Step 2: Deploy Backend on Render.com (FREE)

1. **Go to:** https://render.com
2. **Sign up** with GitHub
3. **Click:** "New +" → "Web Service"
4. **Select:** Your `cc-statement-parser` repository
5. **Configure:**
   ```
   Name: cc-parser-backend
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   Plan: Free
   ```
6. **Add Environment Variables:**
   ```
   PYTHON_VERSION=3.10.12
   ENVIRONMENT=production
   DEBUG=False
   ```
7. **Add Disk (Important!):**
   - Click "Add Disk"
   - Mount Path: `/opt/render/project/src/data`
   - Size: 1GB
8. **Click:** "Create Web Service"
9. **Wait:** 5-10 minutes for deployment
10. **Copy:** Your backend URL (e.g., `https://cc-parser-backend.onrender.com`)

---

### Step 3: Deploy Frontend on Vercel (FREE)

1. **Go to:** https://vercel.com
2. **Sign up** with GitHub
3. **Click:** "Add New..." → "Project"
4. **Select:** Your `cc-statement-parser` repository
5. **Configure:**
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   ```
6. **Add Environment Variable:**
   ```
   Name: VITE_API_URL
   Value: https://cc-parser-backend.onrender.com
   ```
   *(Replace with YOUR backend URL from Step 2)*
7. **Click:** "Deploy"
8. **Wait:** 2-3 minutes
9. **Copy:** Your frontend URL (e.g., `https://cc-parser.vercel.app`)

---

### Step 4: Update CORS (Important!)

1. **Go back to Render.com** → Your service → "Environment"
2. **Add Environment Variable:**
   ```
   Name: CORS_ORIGINS
   Value: ["https://cc-parser.vercel.app","http://localhost:5173"]
   ```
   *(Replace with YOUR Vercel URL from Step 3)*
3. **Save** (service will auto-restart)

---

## ✅ Done! Test Your Deployment

1. Open your Vercel URL: `https://cc-parser.vercel.app`
2. Upload a credit card statement PDF
3. Check if extraction works

---

## 🎯 Final URLs

After deployment, you'll have:

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | `https://cc-parser.vercel.app` | ✅ Live 24/7 |
| **Backend** | `https://cc-parser-backend.onrender.com` | ⚠️ Sleeps after 15 min (free tier) |
| **API Docs** | `https://cc-parser-backend.onrender.com/docs` | 📚 Swagger UI |

---

## 💰 Cost

**Total: $0/month** (Free tier)

Both services are FREE with these limits:
- **Vercel:** Unlimited bandwidth, auto-scaling
- **Render:** 750 hours/month, sleeps after 15 min inactivity

---

## 🔧 Troubleshooting

### ❌ CORS Error in Browser

**Problem:** "Access-Control-Allow-Origin" error

**Fix:**
1. Go to Render → Environment
2. Update `CORS_ORIGINS` to include your Vercel URL
3. Save and wait 2 minutes for restart

### ❌ 404 Error on API Calls

**Problem:** API requests fail

**Fix:**
1. Check frontend `.env` has correct backend URL
2. Verify backend is running: `curl YOUR_BACKEND_URL/health`
3. Check Vercel environment variable is set

### ⚠️ Backend Slow on First Request

**Problem:** First request takes 30+ seconds

**This is normal!** Free tier sleeps after 15 min inactivity. Backend "wakes up" on first request.

**Solutions:**
- Upgrade to Render Starter plan ($7/month) for 24/7 uptime
- Use a ping service to keep it alive (cron-job.org)

---

## 📖 Need More Details?

Read the complete guide: **[DEPLOYMENT.md](DEPLOYMENT.md)**

---

## 🎉 Success Indicators

Your deployment is working if:

- ✅ Frontend loads without errors
- ✅ You can upload a PDF
- ✅ Extraction results appear
- ✅ No CORS errors in browser console (F12)
- ✅ Backend `/health` endpoint returns 200

---

## 🚀 Next Steps After Deployment

1. **Share Your App:** Send the Vercel URL to users
2. **Monitor Logs:**
   - Render: Dashboard → Logs
   - Vercel: Dashboard → Logs
3. **Add Custom Domain** (Optional):
   - Vercel: Settings → Domains
   - Render: Settings → Custom Domain
4. **Upgrade Plans** (Optional):
   - Render Starter: $7/month for 24/7 uptime
   - Vercel Pro: $20/month for team features

---

## 🔄 Updating Your App

Just push to GitHub:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Both Vercel and Render will **auto-deploy** in 2-5 minutes.

---

**Questions?** Check [DEPLOYMENT.md](DEPLOYMENT.md) or create an issue on GitHub.

**Version:** 1.0.0
**Last Updated:** 2025-10-15
