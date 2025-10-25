#!/usr/bin/env python3
"""
Setup script for Goku Translation Bot
"""

import os
import subprocess
import sys

def setup():
    """Setup the bot environment"""
    print("🐉 Goku Bot Setup")
    print("=" * 20)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    print("✅ Python version OK")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("⚠️  .env file not found")
        print("📝 Create .env file with:")
        print("   TELEGRAM_BOT_TOKEN=your_token")
        print("   GOOGLE_API_KEY=your_key")
        return False
    
    print("✅ .env file found")
    print("\n🎉 Setup complete!")
    print("🚀 Run: python app.py")
    return True

if __name__ == "__main__":
    setup()
