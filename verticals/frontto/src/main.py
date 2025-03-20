import os
import json

import requests
import functions_framework


from get_secret import get_secret
from lprint import lprint
from json import Jsonl

# GET ENV VARIABLES
PROJECT_ID = os.environ.get("PROJECT_ID", "")
LLM_PROMPT_PATH = os.environ.get("LLM_PROMPT_PATH", "")

# Get credentials from Secret Manager
ACCESS_TOKEN = get_secret("wa-access-token", project_id=PROJECT_ID)
PHONE_NUMBER_ID = get_secret("wa-phone-id", project_id=PROJECT_ID)
VERIFY_TOKEN = get_secret("wa-verify-token", project_id=PROJECT_ID)

# BUILD THE FORMATTED GLOBAL VARIABLES
WHATSAPP_API_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

# READ THE PROMPT
LLM_PROMPT = Jsonl.read(LLM_PROMPT_PATH)


@functions_framework.http
def whatsapp_webhook(request):
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        mode = request.args.get("hub.mode")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403

    elif request.method == "POST":
        data = request.get_json()
        lprint(f"Data: {json.dumps(data, indent=3)}")

        return_flag = False

        if data:
            if "entry" in data:
                for entry in data["entry"]:
                    for change in entry.get("changes", []):
                        if "messages" in change["value"]:
                            for message in change["value"]["messages"]:
                                sender_id = message["from"]
                                text = message.get("text", {}).get("body", "")
                                send_reply(sender_id, f"Received: {text}")
                                return_flag = True
        if return_flag:
            return "OK", 200
        else:
            return "No messages received", 200

def fix_phone(to):
    # for now only fix mexico phone numbers
    if to.startswith("52"):
        if len(to)==13 and to[2]=="1":
            to = to[:2]+to[-10:]
    return to


def send_reply(to, text):
    to = fix_phone(to)
    
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type":"text", "text": {"body": text}}
    data = json.dumps(payload)
    response = requests.post(WHATSAPP_API_URL, headers=headers, data=data)
    return response
