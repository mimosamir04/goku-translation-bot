#!/bin/bash

# Translation Service Startup Script
echo "🌐 Starting Translation Service..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Start the service
echo "🚀 Starting Flask application..."
python3 app.py
