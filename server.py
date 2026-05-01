from flask import Flask, request, jsonify

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

import json
import os
import traceback

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
    goals = int(data.get("goals") or 0)

    try:
        usernames = sheet.col_values(1)

        row_index = None

        for i, name in enumerate(usernames, start=1):
            if name == username:
                row_index = i
                break

        if row_index:
            row = sheet.row_values(row_index)

            current_goals = int(row[1] or 0)

            new_goals = current_goals + goals

            sheet.update(
                f"B{row_index}",
                [[new_goals]]
            )

            print("UPDATED existing player (batch)")

        else:
            sheet.append_row([username, goals, 0, 0, goals])

            print("ADDED new player")

    except Exception as e:
        print("FULL ERROR:")
        traceback.print_exc()

    return {
        "status": "success",
        "message": f"Added {username} with {goals} goals"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)