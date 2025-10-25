#!/usr/bin/env python3
"""
Setup script for Goku Translation Bot
"""

import os
import subprocess
import sys

def setup():
    """Setup the bot environment"""
    print("Goku Bot Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Python 3.8+ required")
        return False
    
    print("Python version OK")
    
    # Install dependencies
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Dependencies installed")
    except subprocess.CalledProcessError:
        print("Failed to install dependencies")
        return False
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("Creating .env file template...")
        with open('.env', 'w') as f:
            f.write("""# Telegram Bot Token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Google API Key (for Gemini AI)
GOOGLE_API_KEY=your_google_api_key_here

# Google Cloud Credentials (path to JSON file)
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
""")
        print(".env file created. Please edit it with your credentials.")
        return False
    
    print(".env file found")
    print("\nSetup complete!")
    print("Run: python app.py")
    return True

if __name__ == "__main__":
    setup()
