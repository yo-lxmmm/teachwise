# Quick Deploy to Vercel

## ✅ Fixed Issues
- Serverless function crashes resolved
- API key handling improved
- Error handling added
- Type safety fixed

## 🚀 Deploy Now

### 1. Push to GitHub
```bash
git add .
git commit -m "Fix Vercel deployment - add error handling"
git push origin main
```

### 2. Deploy on Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repo
4. Vercel will auto-detect Python

### 3. Set Environment Variable
In Vercel dashboard → Project Settings → Environment Variables:
- **Name**: `GOOGLE_API_KEY`
- **Value**: Your Google API key from [AI Studio](https://aistudio.google.com/)
- **Environments**: Production, Preview, Development

### 4. Deploy
Click "Deploy" and wait for build to complete.

## 🔧 Test Your Deployment

Visit these URLs to test:
- `https://your-app.vercel.app/` - Main app
- `https://your-app.vercel.app/health` - Health check
- `https://your-app.vercel.app/test` - Test endpoint

## 🐛 Troubleshooting

**If it still crashes:**
1. Check Vercel function logs
2. Ensure `GOOGLE_API_KEY` is set correctly
3. Try the `/health` endpoint to see API key status

**Common Issues:**
- Missing API key → Set `GOOGLE_API_KEY` in Vercel
- Build errors → Check `requirements.txt` is correct
- Runtime errors → Check function logs in Vercel dashboard

## 📁 Files Created
- `vercel.json` - Vercel config
- `api/index.py` - Serverless entry point
- `.gitignore` - Git ignore rules
- `DEPLOYMENT.md` - Detailed guide 