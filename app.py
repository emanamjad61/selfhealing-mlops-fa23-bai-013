from flask import Flask, request, jsonify, render_template
from transformers import pipeline
import time
import random
import os

app = Flask(__name__)
classifier = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english")

LOG_DIR = "/app/logs"
LOG_FILE = os.path.join(LOG_DIR, "predictions.log")
DRIFT_FILE = os.path.join(LOG_DIR, "drift.flag")
os.makedirs(LOG_DIR, exist_ok=True)

_request_count = 0
_drift_injected = False


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "model": "distilbert-sentiment-v1",
                    "model_version": "unstable-v1"})


@app.route("/predict", methods=["POST"])
def predict():
    global _request_count
    _request_count += 1
    data = request.get_json() or {}
    text = data.get("text", "")
    result = classifier(text)[0]
    confidence = result["score"]

    if _drift_injected or os.path.exists(DRIFT_FILE):
        confidence = min(confidence * random.uniform(0.30, 0.50), 0.55)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{time.time()},{confidence:.4f}\n")

    return jsonify({"label": result["label"], "confidence": round(confidence, 4),
                    "model_version": "unstable-v1", "request_count": _request_count})


@app.route("/api/latest-confidence", methods=["GET"])
def latest_confidence():
    """Polled by exporter.py on EC2."""
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        if lines:
            _, conf = lines[-1].split(",")
            return jsonify({"confidence": float(conf)})
    except Exception:
        pass
    return jsonify({"confidence": 1.0})


@app.route("/inject-drift", methods=["POST"])
def inject_drift():
    global _drift_injected
    _drift_injected = True
    with open(DRIFT_FILE, "w", encoding="utf-8") as f:
        f.write(str(time.time()))
    return jsonify({"status": "drift_injected"})


@app.route("/reset", methods=["POST"])
def reset():
    global _drift_injected, _request_count
    _drift_injected = False
    _request_count = 0
    try:
        os.remove(DRIFT_FILE)
    except FileNotFoundError:
        pass
    try:
        os.remove(LOG_FILE)
    except FileNotFoundError:
        pass
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
