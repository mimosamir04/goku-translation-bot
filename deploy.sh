#!/bin/bash

# Goku Bot Auto-Deploy Script
# This script automatically commits and pushes changes to GitHub

echo "🐉 Goku Bot Auto-Deploy Script"
echo "================================"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository!"
    exit 1
fi

# Add all changes
echo "📁 Adding all changes..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "✅ No changes to commit"
    exit 0
fi

# Get commit message from user or use default
if [ -z "$1" ]; then
    COMMIT_MSG="Auto-update: $(date '+%Y-%m-%d %H:%M:%S')"
else
    COMMIT_MSG="$1"
fi

# Commit changes
echo "💾 Committing changes: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin main

echo "✅ Successfully deployed!"
echo "🌐 GitHub: https://github.com/mimosamir04/goku-translation-bot"
echo "🔄 Render will automatically deploy from GitHub"
