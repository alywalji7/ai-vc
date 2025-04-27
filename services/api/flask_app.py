from flask import Flask, jsonify
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    })

@app.route('/')
def root():
    return jsonify({"message": "Welcome to the Supabase API Service"})

if __name__ == '__main__':
    logger.info("Starting Supabase API Service with Flask")
    # Use port 4000 to avoid conflicts with other services
    app.run(host='0.0.0.0', port=4000, debug=True)