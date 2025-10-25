import os
from flask import Flask

app = Flask(__name__)

@app.get("/")
def home():
    return "OK - Goku bot alive"

def run():
    port = int(os.environ.get("PORT", 8080))  # Render يعطي PORT تلقائياً
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    run()
