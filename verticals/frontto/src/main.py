import os
import json

import requests
import functions_framework

from get_secret import get_secret
from utils import fix_phone
from facebook import try_to_process_verification,all_phone_and_messages
from history import History
from chatgpt_utils import ChatgptUtils


# GET ENV VARIABLES
PROJECT_ID = os.environ.get("PROJECT_ID", "")
LLM_PLATFORM = os.environ.get("LLM_PLATFORM","")
LLM_MODEL = os.environ.get("LLM_MODEL", "")

# Get credentials from Secret Manager
ACCESS_TOKEN = get_secret("wa-access-token", project_id=PROJECT_ID)
PHONE_NUMBER_ID = get_secret("wa-phone-id", project_id=PROJECT_ID)
VERIFY_TOKEN = get_secret("wa-verify-token", project_id=PROJECT_ID)
LLM_API_KEY = get_secret("openai-api-key", project_id=PROJECT_ID)

# BUILD THE FORMATTED GLOBAL VARIABLES
WHATSAPP_API_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"


@functions_framework.http
def whatsapp_webhook(request):

    # check if facebook tries to verify the hook with the token
    flag, response_challenge, response_code = try_to_process_verification(request, VERIFY_TOKEN)
    if flag:
        return response_challenge, response_code
    
    # read all messages in the request if applicable
    phone_and_messages = all_phone_and_messages(request)
    if phone_and_messages:
        #for every message
        for phone, message in phone_and_messages.items():
            # 1. read the history from phone number
            history:list[History] = History.read_history_and_update(phone=phone, message=message)
            # 2. process the history with ai and clean
            last_answer = process_history_with_ai(phone=phone, history=history)
            last_answer.clean()
            # 3. add the last history message to the history list and save the result
            history.append(last_answer)
            History.write_history(phone=phone, history=history)
            # 4. senf a reply message through whatsapp api
            send_reply(phone, last_answer.message)

        return "OK", 200
    else:
        return "No messages received", 200

def process_history_with_ai(phone:str, history:list[History])->History:
    if LLM_PLATFORM == "openai":
        gpt = ChatgptUtils(api_key=LLM_API_KEY, model_name=LLM_MODEL)
        answer, _ = gpt.get_content_and_json_response("\n\n".join([x.message for x in history]))
        last_answer = History(phone=phone,message=answer)
        last_answer.clean()
        return last_answer
        

def send_reply(to, text):
    to = fix_phone(to)
    
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type":"text", "text": {"body": text}}
    data = json.dumps(payload)
    response = requests.post(WHATSAPP_API_URL, headers=headers, data=data)
    return response
