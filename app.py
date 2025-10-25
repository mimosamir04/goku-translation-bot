#!/usr/bin/env python3
"""
Goku Translation Bot - Main Application
Combines web server and bot in one process
"""

import os
import sys
import threading
import time
from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask app for health check
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Goku Bot is alive and running!"

@app.route('/health')
def health():
    return {"status": "ok", "bot": "goku", "version": "4.0"}

def run_flask():
    """Run Flask health check server"""
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False, threaded=True)

def run_bot():
    """Run the Telegram bot"""
    try:
        from bot import main
        main()
    except Exception as e:
        print(f"Bot error: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)
        try:
            from bot import main
            main()
        except Exception as e2:
            print(f"Bot failed again: {e2}")
            sys.exit(1)

def main():
    """Main startup function"""
    print("Starting Goku Translation Bot...")
    
    required_vars = ['TELEGRAM_BOT_TOKEN', 'GOOGLE_API_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your deployment platform:")
        for var in missing_vars:
            print(f"  - {var}")
        sys.exit(1)
    
    if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        print("Warning: GOOGLE_APPLICATION_CREDENTIALS not set")
        print("Make sure your Google Cloud credentials are configured")
    
    print("Environment variables found")
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    print("Waiting for Flask server to start...")
    time.sleep(5)
    
    print("Starting Telegram bot...")
    run_bot()

if __name__ == "__main__":
    main()
