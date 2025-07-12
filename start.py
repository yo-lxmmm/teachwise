#!/usr/bin/env python3
"""
Simple startup script for TeachWise
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for Google API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY not found in environment variables")
        print("Please set your Google API key in the .env file:")
        print("GOOGLE_API_KEY='your_api_key_here'")
        print("")
        
        # Ask user if they want to continue anyway
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("🚀 Starting TeachWise - AI Teaching Simulator")
    print("📖 Open your browser to: http://localhost:8000")
    print("⌨️  Press Ctrl+C to stop the server")
    print("")
    
    # Run the app
    try:
        uvicorn.run(
            "simple_app:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
    except KeyboardInterrupt:
        print("\n👋 TeachWise stopped. Thanks for using the app!")

if __name__ == "__main__":
    main() 