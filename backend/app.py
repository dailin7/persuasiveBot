from flask import Flask, request
from human_intervention import get_misinformation_ids, get_misinformation_message, send_misinformation_response
from bot import Bot
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# bot = Bot()

@app.route('/start_bot/', methods=['PUT'])
def start():
    bot.start()

@app.route('/end_bot/', methods=['PUT'])
def stop():
    bot.stop()

@app.route('/get_ids/', methods=['GET'])
def get_ids():
    return get_misinformation_ids()

@app.route('/get_misinformation/<string:conversation_id>/<string:message_id>/', methods=['GET'])
def get_misinformation(conversation_id, message_id):
    return get_misinformation_message(conversation_id, message_id)

@app.route('/send_response/', methods=['POST'])
def send_response():
    # get parameters
    print(request)
    data = request.get_json()
    print(data)
    conversation_id = data.get('conversation_id', '')
    message_id = data.get('message_id', '')
    final_response = data.get('final_response', '')

    # handle reply and cleanup actions
    return send_misinformation_response(conversation_id, message_id, final_response)

if __name__ == '__main__':
    app.run(debug=True)
