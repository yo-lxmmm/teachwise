# Quick Deploy to Vercel

## ✅ New Features
- **User-provided API keys**: No server setup needed!
- **Secure**: API keys never stored, only used per session
- **Simple deployment**: No environment variables required
- **Better UX**: Users get their own free API keys

## 🚀 Deploy Now

### 1. Push to GitHub
```bash
git add .
git commit -m "Add user-provided API key support"
git push origin main
```

### 2. Deploy on Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repo
4. Vercel will auto-detect Python
5. Click "Deploy" and wait for build to complete

**That's it! No environment variables needed!**

## 🔧 Test Your Deployment

1. Visit `https://your-app.vercel.app/` - Main app should load
2. Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
3. Enter your API key in the app
4. Try creating a teaching scenario
5. Check `https://your-app.vercel.app/health` - Should show `"api_mode": "user_provided"`

## 🐛 Troubleshooting

**If the app doesn't work:**
1. Check Vercel function logs for errors
2. Ensure users enter a valid Google Gemini API key (starts with "AIza")
3. Try the `/health` endpoint to verify deployment

**Common Issues:**
- Invalid API key → Guide users to get a valid key from Google AI Studio
- Build errors → Check `requirements.txt` is correct  
- Runtime errors → Check function logs in Vercel dashboard

## 📁 Files Created
- `vercel.json` - Vercel config
- `api/index.py` - Serverless entry point
- `.gitignore` - Git ignore rules
- `DEPLOYMENT.md` - Detailed guide 