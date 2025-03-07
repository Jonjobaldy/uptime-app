from flask import Flask, jsonify, send_file
import requests
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# API Details
API_URL = "https://vev-iq.com/ocpi/cpo/2.1.1/locations"
TOKEN = "eyJhayI6MzEsInRpZCI6ImV6Y2hhcmdlIiwiemsiOjczfQ=="
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

# Log file
LOG_FILE = "charger_uptime_log.csv"

def fetch_charger_status():
    """Fetch data from API and return as DataFrame"""
    response = requests.get(API_URL, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()["data"]
        records = []
        
        for location in data:
            for evse in location.get("evses", []):
                records.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "location_id": location["id"],
                    "charger_id": evse["uid"],
                    "status": evse["status"]
                })
        
        return pd.DataFrame(records)
    else:
        return None

@app.route("/fetch", methods=["GET"])
def fetch_and_log():
    """Fetch latest data and log it to CSV"""
    df_new = fetch_charger_status()
    
    if df_new is None or df_new.empty:
        return jsonify({"message": "No data fetched"}), 500

    if os.path.exists(LOG_FILE):
        df_old = pd.read_csv(LOG_FILE)
        df_combined = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_csv(LOG_FILE, index=False)
    return jsonify({"message": "Data logged successfully", "entries": len(df_new)})

@app.route("/download", methods=["GET"])
def download_csv():
    """Allow user to download the log"""
    if os.path.exists(LOG_FILE):
        return send_file(LOG_FILE, as_attachment=True)
    return jsonify({"message": "No data available"}), 404

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Flask API is running! Available routes: /fetch, /download"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
