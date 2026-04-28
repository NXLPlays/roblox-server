from flask import Flask, request, jsonify

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

import json
import os

creds_dict = json.loads(os.environ["creds"])

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)

sheet = client.open_by_key("15_GGlx6HeQR-UjxWEcR0oBPBvgKamXozO-ANUveGPFw").sheet1


app = Flask(__name__)

@app.route('/')
def home():
    return "Server is running!"

@app.route('/submit', methods=['POST'])
def receive_data():
    data = request.json
    print("Received:", data)

    username = data.get("username")
    goals = data.get("goals")

    try:
        sheet.append_row([username, goals])
        print("SUCCESS writing to sheet")
    except Exception as e:
        print("SHEET ERROR:", e)

    return {
        "status": "success",
        "message": f"Added {username} with {goals} goals"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)