# Vercel API Setup Guide

## 🔧 Fixing API Issues on Vercel

If AI generation is not working on Vercel, it's most likely because the `GOOGLE_API_KEY` environment variable is not set.

## ✅ Step-by-Step Fix:

### 1. **Set Environment Variable in Vercel**

1. Go to [vercel.com](https://vercel.com) and sign in
2. Navigate to your **TeachWise project**
3. Go to **Settings** → **Environment Variables**
4. Add a new environment variable:
   - **Name**: `GOOGLE_API_KEY`
   - **Value**: Your Google Gemini API key (get one from [Google AI Studio](https://aistudio.google.com/app/apikey))
   - **Environment**: Select **Production**, **Preview**, and **Development** (or just Production if you only deploy to production)
5. Click **Save**

### 2. **Redeploy Your Application**

After adding the environment variable, you need to redeploy:

**Option A: Via Vercel Dashboard**
- Go to **Deployments** tab
- Click the **⋯** (three dots) menu on the latest deployment
- Select **Redeploy**

**Option B: Via Git Push**
```bash
git commit --allow-empty -m "Trigger Vercel redeploy"
git push origin main
```

### 3. **Verify the Setup**

1. Check the health endpoint: `https://your-app.vercel.app/health`
   - Should return: `"api_key": "available"` and `"ai_ready": true`

2. Test the AI generation:
   - Go to your Vercel URL
   - Try generating a question
   - It should work now!

## 🔍 Troubleshooting

### Issue: Still getting "AI service unavailable"

**Check:**
1. ✅ Environment variable is named exactly `GOOGLE_API_KEY` (case-sensitive)
2. ✅ Environment variable is set for the correct environment (Production/Preview/Development)
3. ✅ You've redeployed after adding the variable
4. ✅ Your API key is valid (starts with `AIza`)

**Verify in Vercel:**
- Go to **Settings** → **Environment Variables**
- Confirm `GOOGLE_API_KEY` is listed
- Check which environments it's enabled for

### Issue: Getting import errors in logs

**Check Vercel Function Logs:**
1. Go to **Deployments** → Click on latest deployment
2. Go to **Functions** tab
3. Check for any import errors
4. Common issues:
   - Missing dependencies in `requirements.txt`
   - Python version mismatch

### Issue: API key works locally but not on Vercel

**Common causes:**
- Environment variable not set for Production environment
- Old deployment before variable was added (need to redeploy)
- API key format issue (make sure there are no extra spaces)

## 📋 Current Git Status

The latest version includes:
- ✅ Fixed `api/index.py` with better error handling
- ✅ Traditional Chinese language support
- ✅ Improved health check endpoint
- ✅ Better API error messages

## 🚀 Quick Deploy Command

```bash
# Commit and push changes
git add .
git commit -m "Fix Vercel API configuration and error handling"
git push origin main

# Vercel will auto-deploy
# Then add GOOGLE_API_KEY in Vercel dashboard
```

## 📝 Environment Variable Format

Your `GOOGLE_API_KEY` should:
- Start with `AIza` (all Gemini API keys start with this prefix)
- Be 39 characters long
- Be obtained from [Google AI Studio](https://aistudio.google.com/app/apikey)

**Important:** 
- Never commit API keys to git
- Always use environment variables
- If you accidentally commit an API key, rotate it immediately in Google AI Studio

