# health_app.py
from flask import Flask

app = Flask(__name__)

@app.get("/")
def root():
    return "ok", 200

@app.get("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    # Render injects PORT
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
