from flask import Flask, request, jsonify
from claude_api import Client

app = Flask(__name__)

@app.route("/get_user/<user_id>")
def get_user(user_id):
    user_data = {
        "user_id": user_id
    }

    extra = request.args.get("extra")

    if extra:
        user_data["extra"] = extra

    return jsonify(user_data), 200

@app.route("/")
def home():
    response = {
        "status": "ok"
    }

    cookie = request.args.get("cookie")

    if cookie:
        response["cookie"] = cookie

        claude_api = Client(cookie)

        conversations = claude_api.list_all_conversations()

        return conversations, 200
    else:
        return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)