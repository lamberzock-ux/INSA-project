from flask import Flask, render_template, jsonify
import random
import datetime

app = Flask(__name__)

# Fake alerts for demo
alerts = [
    {"time": "2025-09-18 12:00", "type": "Failed Login", "severity": "Medium"},
    {"time": "2025-09-18 12:05", "type": "SQL Injection Attempt", "severity": "High"},
    {"time": "2025-09-18 12:07", "type": "Anomaly Detected", "severity": "Critical"},
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/alerts")
def get_alerts():
    return jsonify(alerts)

@app.route("/api/metrics")
def metrics():
    # Fake counts
    data = {
        "failed_logins": random.randint(10, 50),
        "sqli": random.randint(1, 10),
        "anomalies": random.randint(0, 5),
        "timestamps": [str((datetime.datetime.now() - datetime.timedelta(minutes=i)).time()) for i in range(10)],
        "values": [random.randint(1, 20) for _ in range(10)]
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
