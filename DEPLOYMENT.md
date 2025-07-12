# Deploying TeachWise on Vercel

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Google API Key**: Get one from [Google AI Studio](https://aistudio.google.com/)
3. **GitHub Repository**: Push your code to GitHub

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

### 3. Set Environment Variables

In your Vercel dashboard:

1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add the following variable:
   - **Name**: `GOOGLE_API_KEY`
   - **Value**: Your Google API key from AI Studio
   - **Environments**: Production, Preview, Development

### 4. Deploy

1. Click "Deploy" 
2. Vercel will build and deploy your app
3. You'll get a URL like: `https://your-project-name.vercel.app`

## Configuration Files Created

- `vercel.json` - Vercel deployment configuration
- `api/index.py` - Serverless function entry point
- `requirements.txt` - Python dependencies (already exists)

## Important Notes

- The app uses Google's Gemini API for AI functionality
- Environment variables are set in Vercel dashboard, not in `.env` files
- The frontend (`index.html`) is served from the root
- All API endpoints are handled by the FastAPI backend

## Testing the Deployment

1. Visit your Vercel URL
2. Check that the homepage loads
3. Try creating a teaching scenario to test the AI integration
4. Monitor the Vercel function logs for any errors

## Troubleshooting

- **API Key Issues**: Ensure `GOOGLE_API_KEY` is set correctly in Vercel
- **Build Errors**: Check the Vercel build logs for Python dependency issues
- **Runtime Errors**: Check the Vercel function logs for application errors

## Alternative Deployment Options

If Vercel doesn't work well, consider:
- **Railway**: Good for Python apps with simple setup
- **Render**: Free tier with straightforward Python deployment
- **Heroku**: Traditional PaaS with Python support
- **Google Cloud Run**: Serverless containers, works well with Google APIs 