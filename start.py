#!/usr/bin/env python3
"""
Startup script for Goku Translation Bot
Handles both web service and bot worker
"""

import os
import sys
import subprocess
import threading
import time
from flask import Flask

# Flask app for health check
app = Flask(__name__)

@app.route('/')
def health_check():
    return "OK - Goku bot alive"

def run_flask():
    """Run Flask health check server"""
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)

def run_bot():
    """Run the Telegram bot"""
    try:
        # Import and run the bot
        from bot import main
        main()
    except Exception as e:
        print(f"Bot error: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🐉 Starting Goku Translation Bot...")
    
    # Check if we have required environment variables
    required_vars = ['TELEGRAM_BOT_TOKEN', 'GOOGLE_API_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your Render dashboard:")
        for var in missing_vars:
            print(f"  - {var}")
        sys.exit(1)
    
    print("✅ Environment variables found")
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Give Flask time to start
    time.sleep(2)
    
    # Start the bot
    print("🤖 Starting Telegram bot...")
    run_bot()

if __name__ == "__main__":
    main()
