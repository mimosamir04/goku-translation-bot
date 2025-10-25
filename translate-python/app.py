#!/usr/bin/env python3
"""
Translation App - Cloud Shell Workspace
Google Cloud Translate service
"""

from flask import Flask, request, jsonify
import os
from google.cloud import translate_v2 as translate

app = Flask(__name__)

# Initialize Google Cloud Translate client
try:
    translate_client = translate.Client()
    print("✅ Google Cloud Translate client initialized")
except Exception as e:
    print(f"⚠️ Google Cloud Translate not available: {e}")
    translate_client = None

@app.route('/')
def home():
    return "🌐 Google Cloud Translation Service is running!"

@app.route('/health')
def health():
    return {
        "status": "ok", 
        "service": "google-cloud-translate", 
        "version": "1.0",
        "translate_available": translate_client is not None
    }

@app.route('/translate', methods=['POST'])
def translate_text():
    """Translation endpoint using Google Cloud Translate"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        source_lang = data.get('source', 'auto')
        target_lang = data.get('target', 'en')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        if not translate_client:
            return jsonify({"error": "Translation service not available"}), 503
        
        # Use Google Cloud Translate
        if source_lang == 'auto':
            # Detect language first
            detection = translate_client.detect_language(text)
            source_lang = detection['language']
        
        # Translate the text
        result = translate_client.translate(
            text, 
            source_language=source_lang, 
            target_language=target_lang
        )
        
        return jsonify({
            "original": text,
            "translated": result['translatedText'],
            "source": source_lang,
            "target": target_lang,
            "confidence": result.get('detectedSourceLanguage', {}).get('confidence', 1.0)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/languages', methods=['GET'])
def get_languages():
    """Get supported languages"""
    try:
        if not translate_client:
            return jsonify({"error": "Translation service not available"}), 503
        
        languages = translate_client.get_languages()
        return jsonify({
            "languages": languages,
            "count": len(languages)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 Starting Translation Service on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
