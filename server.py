from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is running!"

@app.route('/submit', methods=['POST'])
def receive_data():
    data = request.json
    print("Received from Roblox:", data)

    return jsonify({
        "status": "success",
        "message": "Data received!"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)