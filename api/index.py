from fastapi import FastAPI
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up environment for Vercel
os.environ.setdefault("GOOGLE_API_KEY", "")

# Import the FastAPI app from the main module
from simple_app import app

# Export the app for Vercel
handler = app 