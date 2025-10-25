# 🌐 Translation Service

A simple translation service built with Flask.

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python app.py
```

### Cloud Shell
```bash
# In Google Cloud Shell
cd translate-python
pip install -r requirements.txt
python app.py
```

## 📡 API Endpoints

### Health Check
```
GET /
GET /health
```

### Translation
```
POST /translate
Content-Type: application/json

{
  "text": "Hello world",
  "source": "en",
  "target": "es"
}
```

## 🔧 Environment Variables

- `PORT` - Server port (default: 8080)

## 📁 Project Structure

```
translate-python/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🌟 Features

- ✅ RESTful API
- ✅ JSON responses
- ✅ Health check endpoints
- ✅ Cloud Shell ready
- ✅ Simple and lightweight
