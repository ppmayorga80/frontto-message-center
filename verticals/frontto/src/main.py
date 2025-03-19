import os
import json
import sys

import requests
import functions_framework
from google.cloud import secretmanager

import logging
logging.basicConfig(level=logging.INFO)


def log(msg):
    logging.info(msg)
    logging.warning(msg)
    logging.error(msg)
    sys.stdout.flush()


def get_secret(secret_name, project_id="", version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    secret_value = response.payload.data.decode("UTF-8")
    return secret_value




# GET ENV VARIABLES
PROJECT_ID = os.environ.get("PROJECT_ID", "")

log("BBB Env variables loaded")


# Get credentials from Secret Manager
ACCESS_TOKEN = get_secret("wa-access-token", project_id=PROJECT_ID)
PHONE_NUMBER_ID = get_secret("wa-phone-id", project_id=PROJECT_ID)
VERIFY_TOKEN = get_secret("wa-verify-token", project_id=PROJECT_ID)

log("CCC Secrets loaded")

# BUILD THE FORMATTED GLOBAL VARIABLES
WHATSAPP_API_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

log("DDD Global variables defined")

@functions_framework.http
def whatsapp_webhook(request):

    log(f"Method: {request.method}")

    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        mode = request.args.get("hub.mode")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            log("Verification successful!")
            return challenge, 200
        else:
            log("Verification failed!")
            return "Verification failed", 403

    elif request.method == "POST":
        data = request.get_json()
        log(f"Data: {json.dumps(data, indent=3)}")

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
    log("WWW Sending a Reply")
    to = fix_phone(to)
    
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type":"text", "text": {"body": text}}
    data = json.dumps(payload)
    response = requests.post(WHATSAPP_API_URL, headers=headers, data=data)
    log(f"XXX Reply sent to {to}")
    log(f"YYY Response: {response.text}")
    return response
