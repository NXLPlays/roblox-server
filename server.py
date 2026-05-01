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

    passes = int(data.get("passes", 0))
    goals = int(data.get("goals", 0))
    assists = int(data.get("assists", 0))
    points = int(data.get("points", 0))

    try:
        usernames = sheet.col_values(1)

        row_index = None

        for i, name in enumerate(usernames, start=1):
            if name == username:
                row_index = i
                break

        if row_index:
            # read current values safely
            current_passes = int(sheet.cell(row_index, 2).value or 0)
            current_goals = int(sheet.cell(row_index, 3).value or 0)
            current_assists = int(sheet.cell(row_index, 4).value or 0)
            current_points = int(sheet.cell(row_index, 5).value or 0)

            # update totals
            sheet.update_cell(row_index, 2, current_passes + passes)
            sheet.update_cell(row_index, 3, current_goals + goals)
            sheet.update_cell(row_index, 4, current_assists + assists)
            sheet.update_cell(row_index, 5, current_points + points)

            print("UPDATED existing player")

        else:
            sheet.append_row([username, passes, goals, assists, points])
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