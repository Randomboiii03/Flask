from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from claude_api import Client

app = Flask(__name__)

@app.route("/upload", methods=['POST'])
def upload():
    cookie = request.args.get("cookie")

    f = request.files['file']
    f.save(secure_filename(f.filename))

    try:
        claude_api = Client(cookie)
        prompt = "Hello, Claude! Can you explain this for me?"
        conversation_id = claude_api.create_new_chat()['uuid']
        response = claude_api.send_message(prompt, conversation_id, attachment=f.filename, timeout=600)

        return jsonify(response), 201

    except:
        if conversation_id:
            claude_api.delete_conversation(conversation_id)

        return {"Error": "Something went wrong, please try again."}, 403


# @app.route("/")
# def home():
#     response = {
#         "status": "ok"
#     }
#
#     cookie = request.args.get("cookie")
#
#     if cookie:
#         response["cookie"] = cookie
#
#         claude_api = Client(cookie)
#
#         conversations = claude_api.list_all_conversations()
#
#         return conversations, 200
#     else:
#         return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)