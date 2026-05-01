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

sheet = client.open_by_key("1f0iLPm1i63NYDHGi4QSqKO8E27PCj4IbQoACHhzbMlg").worksheet("StatInput")


app = Flask(__name__)

@app.route('/')
def home():
    return "Server is running!"

@app.route('/submit', methods=['POST'])
def receive_data():
    data = request.json
    print("Received:", data)

    username = data.get("username")
    goals = int(data.get("goals"))

    try:
        usernames = sheet.col_values(1)

        row_index = None

        for i, name in enumerate(usernames, start=1):
            if name == username:
                row_index = i
                break

        if row_index:
            current_goals = sheet.cell(row_index, 2).value or 0
            current_goals = int(current_goals)

            new_goals = current_goals + goals

            sheet.update_cell(row_index, 2, new_goals)
            print("UPDATED existing player")
        else:
            sheet.append_row([username, goals])
            print("ADDED new player")

    except Exception as e:
        print("SHEET ERROR:", e)

    return {
        "status": "success",
        "message": f"Added {username} with {goals} goals"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)