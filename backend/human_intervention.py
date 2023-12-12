### firebase ###
from collections import deque

import yaml
import firebase_admin
from firebase_admin import credentials, db, firestore
from telegram import Bot

# Initialize Firebase with your service account key
SERVICE_ACCOUNT_PATH = "persuasivechatbot-deccc-firebase-adminsdk.json"
cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Access a specific collection and document
collection_ref = db.collection("conversations")

# write to firebase
BOT_NAME = "PersuasiveChatbot"

# store message in firebase
def store_message(update, response=None):
    conversation_id = update.message.chat_id
    date = update.message.date
    is_bot = response != None
    
    # message id is message_id + 1 for bot messages because the message id that gets passed in is the user's message that the bot is responding to
    message_id = update.message.message_id
    bot_message_id = message_id + 1
    # message text is response if bot because message text that is passed in is the user's message
    message_text = update.message.text
    bot_message_response = response
    
    username = str(update.message.from_user.username)
    bot_user = BOT_NAME
    user = username if username != "None" else str(update.message.from_user.id)
    current_user = bot_user if is_bot else user

    # only set conversation data if it does not already exist
    # otherwise, can update users and time_last_modified
    conversation_data = {
        "id": conversation_id,
        "time_created": str(date),
        "time_last_modified": str(date), # will be updated with the timestamp of the last message we add
        "users": [], # will be updated each time a new user contributes to the conversation
        "overview": [],
    }

    message_data = {
        "id": message_id,
        "user": user,
        "message": message_text,
        "timestamp": str(date),
        "is_bot": False
    }

    # once we have draft(s) of the bot's response in the "response" parameter, we can populate the bot's response in the "message_draft" field
    bot_message_data = {
        "id": bot_message_id,
        "user": bot_user,
        "message_final": "",
        "message_draft": bot_message_response,
        "timestamp": str(date),
        "is_bot": True,
        "misinformation": {
            "user_message_id": message_id,
            "user_message_text": message_text,
            "user_id": user
        },
    }

    # store message in Firebase
    document_ref = db.collection("conversations").document(f"{conversation_id}")
    document = document_ref.get()

    # check if the document exists
    if document.exists:
        # update convo's last timestamp
        document_ref.set({"time_last_modified": date}, merge=True)

        # add new user if necessary
        if current_user not in document.to_dict().get("users"):
            document_ref.update({
                "users": firestore.ArrayUnion([current_user])
            })
        
    else:
        # add current user in users
        conversation_data["users"].append(current_user)
        # create new document w/ all convo info
        document_ref.set(conversation_data)

    # add new message to logs
    message_info = document_ref.collection("logs").document(f"{message_id if not is_bot else bot_message_id}")
    message_info.set(message_data if not is_bot else bot_message_data)
    current_message_text = message_text if not is_bot else bot_message_response
    overview_message = {"user": current_user, "message": current_message_text}
    document_ref.update({"overview": firestore.ArrayUnion([overview_message])})


##### HUMAN INTERVENTION #####
# if sequentiality is enforced, then we can just a deque (treated as a deque)
# dictionary that holds the conversation and message id of messages that contain misinformation in the format of (conversation_id, message_id)
misinformation_queue = {}

# response = tuple of (response, sources, score)
# update has the misinformation message data
def human_intervention(update, response):
    # add message ids into misinformation_queue
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    misinformation_queue[(chat_id, message_id)] = True

    # store bot message in firebase
    bot_response, _, _ = response
    store_message(update, bot_response)


##### ENDPOINT FUNCTIONS #####

# get all messages of a conversation
def get_conversation(conversation_id: str, bot_only=False):
    docs = {}
    if bot_only:
        docs = db.collection("conversations").document(f"{conversation_id}").collection("logs").where("is_bot", "==", True).stream()
    else:
        docs = db.collection("conversations").document(f"{conversation_id}").collection("logs").stream()
    
    messages = {}
    for doc in docs:
        messages[doc.id] = doc.to_dict()
    
    return messages

# get all misinformation messages in all conversations
def get_misinformation_ids():
    misinformation_queue[(0, 0)] = True
    misinformation_queue[(0, 6)] = True

    return list(misinformation_queue.keys())

# get details of a specific misinformation message 
def get_misinformation_message(conversation_id: int, message_id: int):
    message = db.collection("conversations").document(f"{conversation_id}").collection("logs").document(f"{message_id}").get()
    # this should always be the case
    if message.exists:
        return message.to_dict()
    return "Misinformation message not found"

# reply to misinformation message
def send_misinformation_response(conversation_id: int, message_id: int, final_response: str):
    # bot replies to user message
    bot_token = ''
    with open('./constants.yaml', 'r') as keys_file:
        keys = yaml.load(keys_file, Loader=yaml.FullLoader)
        bot_token = keys['api_key']

    telegram_bot = Bot(token=bot_token)
    telegram_bot.send_message(chat_id=conversation_id, text=final_response, reply_to_message_id=message_id)

    # delete misinformation messages from queue
    if (conversation_id, message_id) in misinformation_queue:
        del misinformation_queue[(conversation_id, message_id)]

    # update bot message in database with final version of sent message
    bot_message_id = message_id + 1
    document_ref = db.collection("conversations").document(f"{conversation_id}").collection("logs").document(f"{bot_message_id}")
    document = document_ref.get()
    if document.exists:
        # update bot message
        document_ref.set({"message_final": final_response}, merge=True)
    
    resolution = {
        "conversation_id": conversation_id,
        "message_id": message_id,
        "bot_message_id": bot_message_id,
        "final_response": final_response
    }

    return resolution
    