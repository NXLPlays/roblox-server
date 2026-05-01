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

    passes = int(data.get("passes") or 0)
    goals = int(data.get("goals") or 0)
    assists = int(data.get("assists") or 0)

    # points = goals + assists (your rule)
    points = goals + assists

    try:
        usernames = sheet.col_values(1)

        row_index = None

        for i, name in enumerate(usernames, start=1):
            if name == username:
                row_index = i
                break

        if row_index:
            row = sheet.row_values(row_index)

            current_passes = int(row[1]) if len(row) > 1 and row[1] else 0
            current_goals = int(row[2]) if len(row) > 2 and row[2] else 0
            current_assists = int(row[3]) if len(row) > 3 and row[3] else 0
            current_points = int(row[4]) if len(row) > 4 and row[4] else 0

            sheet.update(
                range_name=f"B{row_index}:E{row_index}",
                values=[[
                    current_passes + passes,
                    current_goals + goals,
                    current_assists + assists,
                    current_points + points
                ]]
            )

            print("UPDATED existing player (batch)")

        else:
            sheet.append_row([
                username,
                passes,
                goals,
                assists,
                points
            ])

            print("ADDED new player")

    except Exception as e:
        print("FULL ERROR:")
        traceback.print_exc()

    return {
        "status": "success",
        "message": f"Updated {username}"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)