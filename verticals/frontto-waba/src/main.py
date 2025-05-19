import os

import requests
import functions_framework

from cloud.get_secret import get_secret
from utils.lprint import lprint
from utils import fix_phone

lprint("STARTING SERVICES...")

# GET ENV VARIABLES
PROJECT_ID = os.environ.get("PROJECT_ID", "")
LLM_PLATFORM = os.environ.get("LLM_PLATFORM", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "")
AVERAGE_CHARACTERS_PER_SECOND = float(os.environ.get("AVERAGE_WORDS_PER_MINUTE", "48")) * 5 / 60.0

# Get credentials from Secret Manager
WABA_APIKEY = get_secret("waba-apikey", project_id=PROJECT_ID)
WABA_ID = get_secret("waba-id", project_id=PROJECT_ID)
WABA_PHONE = get_secret("waba-phone", project_id=PROJECT_ID)
WA_VERIFY_TOKEN = get_secret("wa-verify-token", project_id=PROJECT_ID)

# BUILD THE FORMATTED GLOBAL VARIABLES
GRAPH_API_URL = f"https://graph.facebook.com/v17.0/{WABA_PHONE}/messages"
lprint("PRECONFIGURATION DONE.")


def send_whatsapp_message(to_number: str, text: str):
    """
    Send a simple text message via WhatsApp Business API.
    """
    headers = {
        "Authorization": f"Bearer {WABA_APIKEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    resp = requests.post(GRAPH_API_URL, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()


@functions_framework.http
def webhook(request):
    """
    HTTP Cloud Function:
      - GET: verify webhook with Facebook
      - POST: handle inbound WhatsApp messages & status updates
    """

    lprint(f"Method: {request.method}")

    # --- Verification handshake ---
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == WA_VERIFY_TOKEN:
            return challenge, 200
        return "Verification token mismatch", 403

    # --- Incoming events ---
    if request.method == "POST":
        # parse JSON body
        try:
            data = request.get_json(force=True)
        except Exception as e:
            return f"Invalid JSON: {e}", 204

        lprint(f"Data: {data}")
        # TODO: save data as a raw data

        sender = data.get("payload", {}).get("source", "")
        sender = fix_phone(sender)
        text = data.get("payload", {}).get("payload", {}).get("text", "")

        lprint(f"Sender: {sender}")
        lprint(f"Text: {text}")

        if not sender or not text:
            return f"Invalid Message with data: {data}", 204

        try:
            send_whatsapp_message(sender, f"You said: {text}")
        except Exception as e:
            lprint(f"Error: {e}")

        return f"EVENT_RECEIVED WITH DATA: {data}", 200

    # unsupported methods
    return f"Method Not Allowed: {request.method}", 204
