from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)  # Allow all origins for testing

@app.route('/agent_act/plan', methods=['POST'])
def agent_act_plan():
    data = request.get_json()
    print(f"[plan] Received data: {data}")

    x = random.randint(1, 19)
    y = random.randint(2, 13)

    default_response = {
        "agent_id": data.get("agent_id", "agent_1"),
        "action_type": "move",
        "content": {
            "destination_coordinates": [x, y]
        },
        "emoji": "🚶",
        "current_tile": [5, 5],
        "current_location": "kitchen"
    }

    return jsonify(default_response), 200

@app.route('/agent_act/confirm', methods=['POST'])
def agent_act_confirm():
    data = request.get_json()
    print(f"[confirm] Received data: {data}")

    return jsonify({"status": "ok"}), 200

@app.route('/agent_state/', methods=['GET'])
def agent_state():
    agent_id = request.args.get("agent_id", "agent_1")
    print(f"[agent_state] Querying agent_id: {agent_id}")

    state_response = {
        "agent_id": agent_id,
        "action_type": "perceive",
        "content": {},
        "emoji": "👀",
        "current_tile": [0, 0],
        "current_location": "starting_area"
    }

    return jsonify(state_response), 200

if __name__ == '__main__':
    app.run(port=8000)
