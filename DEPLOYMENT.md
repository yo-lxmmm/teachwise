# Deploying TeachWise on Vercel

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Push your code to GitHub

**Note**: No server-side API key setup required! Users provide their own Google Gemini API keys.

## Step-by-Step Deployment

### 1. Push Code to GitHub

```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 2. Deploy on Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will automatically detect the Python project

### 3. Deploy (No Environment Variables Needed!)

1. Click "Deploy" 
2. Vercel will build and deploy your app
3. You'll get a URL like: `https://your-project-name.vercel.app`

## Configuration Files Created

- `vercel.json` - Vercel deployment configuration
- `api/index.py` - Serverless function entry point
- `requirements.txt` - Python dependencies (already exists)

## Important Notes

- **User-Provided API Keys**: Users enter their own Google Gemini API keys in the app
- **No Server Setup**: No environment variables or API key configuration needed
- **Secure**: API keys are only used per-session and never stored
- The frontend (`index.html`) is served from the root
- All API endpoints are handled by the FastAPI backend

## Testing the Deployment

1. Visit your Vercel URL
2. Check that the homepage loads
3. Get a free Google Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
4. Enter your API key in the app and try creating a teaching scenario
5. Monitor the Vercel function logs for any errors

## Troubleshooting

- **API Key Issues**: Ensure users enter a valid Google Gemini API key
- **Build Errors**: Check the Vercel build logs for Python dependency issues  
- **Runtime Errors**: Check the Vercel function logs for application errors

## Alternative Deployment Options

If Vercel doesn't work well, consider:
- **Railway**: Good for Python apps with simple setup
- **Render**: Free tier with straightforward Python deployment
- **Heroku**: Traditional PaaS with Python support
- **Google Cloud Run**: Serverless containers, works well with Google APIs 