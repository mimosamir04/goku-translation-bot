#!/usr/bin/env python3
"""
Auto-Deploy Script for Goku Translation Bot
Automatically commits and pushes changes to GitHub
"""

import subprocess
import sys
import datetime
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    """Main deployment function"""
    print("🐉 Goku Bot Auto-Deploy Script")
    print("=" * 40)
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not in a git repository!")
        sys.exit(1)
    
    # Get commit message
    if len(sys.argv) > 1:
        commit_msg = sys.argv[1]
    else:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        commit_msg = f"Auto-update: {timestamp}"
    
    # Step 1: Add all changes
    if not run_command("git add .", "Adding all changes"):
        sys.exit(1)
    
    # Step 2: Check if there are changes
    result = subprocess.run("git diff --staged --quiet", shell=True)
    if result.returncode == 0:
        print("✅ No changes to commit")
        return
    
    # Step 3: Commit changes
    if not run_command(f'git commit -m "{commit_msg}"', "Committing changes"):
        sys.exit(1)
    
    # Step 4: Push to GitHub
    if not run_command("git push origin main", "Pushing to GitHub"):
        sys.exit(1)
    
    print("\n🎉 Deployment successful!")
    print("🌐 GitHub: https://github.com/mimosamir04/goku-translation-bot")
    print("🔄 Render will automatically deploy from GitHub")
    print("\n📝 Next time, you can use:")
    print("   python auto_deploy.py 'Your commit message'")

if __name__ == "__main__":
    main()
