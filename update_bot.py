#!/usr/bin/env python3
"""
Quick Bot Update Script
Updates bot code and automatically deploys
"""

import os
import sys
import subprocess
from datetime import datetime

def update_bot():
    """Update bot and deploy"""
    print("🐉 Goku Bot Update Script")
    print("=" * 30)
    
    # Check if we're in the right directory
    if not os.path.exists('bot.py'):
        print("❌ bot.py not found! Make sure you're in the project directory.")
        return False
    
    # Get update description
    if len(sys.argv) > 1:
        description = sys.argv[1]
    else:
        description = input("📝 Enter update description: ").strip()
        if not description:
            description = f"Bot update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Git commands
    commands = [
        ("git add .", "Adding changes"),
        (f'git commit -m "{description}"', "Committing changes"),
        ("git push origin main", "Pushing to GitHub")
    ]
    
    for command, desc in commands:
        print(f"🔄 {desc}...")
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"✅ {desc} completed")
        except subprocess.CalledProcessError as e:
            print(f"❌ {desc} failed!")
            return False
    
    print("\n🎉 Update successful!")
    print("🌐 GitHub: https://github.com/mimosamir04/goku-translation-bot")
    print("🔄 Render will automatically deploy")
    
    return True

if __name__ == "__main__":
    update_bot()
