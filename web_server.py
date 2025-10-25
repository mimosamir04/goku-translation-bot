#!/usr/bin/env python3
"""
Web server for Goku Bot - Health check endpoint
"""

import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "🐉 Goku Translation Bot is running!"

@app.route('/health')
def health():
    return {"status": "ok", "bot": "goku", "version": "3.0"}

@app.route('/status')
def status():
    return "OK - Goku bot alive"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 Starting web server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
