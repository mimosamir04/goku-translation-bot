#!/usr/bin/env python3
"""
Simple deployment script for Goku Bot
"""

import subprocess
import sys
import datetime

def deploy(message=None):
    """Deploy the bot to GitHub"""
    if not message:
        message = f"Update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    print("🐉 Deploying Goku Bot...")
    
    commands = [
        "git add .",
        f'git commit -m "{message}"',
        "git push origin main"
    ]
    
    for cmd in commands:
        print(f"🔄 Running: {cmd}")
        try:
            subprocess.run(cmd, shell=True, check=True)
            print("✅ Success")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed: {e}")
            return False
    
    print("\n🎉 Deployment successful!")
    print("🌐 GitHub: https://github.com/mimosamir04/goku-translation-bot")
    print("🔄 Render will auto-deploy")
    return True

if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else None
    deploy(message)
