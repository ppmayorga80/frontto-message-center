import os
import json
import time
from random import random

import requests
import functions_framework

from cloud.get_secret import get_secret
from facebook import try_to_process_verification, all_phone_and_messages
from history import History
from ai.llm import Llm, LlmPlatform
from lprint import lprint

lprint("STARTING SERVICES...")

# GET ENV VARIABLES
PROJECT_ID = os.environ.get("PROJECT_ID", "")
LLM_PLATFORM = os.environ.get("LLM_PLATFORM", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "")
AVERAGE_CHARACTERS_PER_SECOND = float(os.environ.get("AVERAGE_WORDS_PER_MINUTE", "48"))*5/60.0

# Get credentials from Secret Manager
ACCESS_TOKEN = get_secret("wa-access-token", project_id=PROJECT_ID)
PHONE_NUMBER_ID = get_secret("wa-phone-id", project_id=PROJECT_ID)
VERIFY_TOKEN = get_secret("wa-verify-token", project_id=PROJECT_ID)

# BUILD THE FORMATTED GLOBAL VARIABLES
WHATSAPP_API_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
lprint("PRECONFIGURATION DONE.")


@functions_framework.http
def whatsapp_webhook(request):
    lprint("1. INSIDE FUNCTION.")

    # check if facebook tries to verify the hook with the token
    lprint("2. GET: VERIFICATION TOKEN")
    flag, response_challenge, response_code = try_to_process_verification(request, VERIFY_TOKEN)
    if flag:
        return response_challenge, response_code

    lprint("3. POST: GET ALL MESSAGES")
    # read all messages in the request if applicable
    phone_and_messages = all_phone_and_messages(request)
    lprint(f"4. POST: {len(phone_and_messages)} message(s)")
    if phone_and_messages:
        # for every message
        last_status_code = 0
        for phone, message in phone_and_messages.items():
            t1 = time.perf_counter()
            # 1. read the history from phone number
            history: list[History] = History.read_history_and_update(phone=phone, message=message)
            # 2. process the history with AI and clean
            last_answer = process_history_with_ai(phone=phone, history=history)
            last_answer.clean()
            # 3. add the last history message to the history list and save the result
            history.append(last_answer)
            History.write_history(phone=phone, history=history)
            # 4. compute elapsed time in seconds and decide how long to wait before send the message
            t2 = time.perf_counter()
            dt = t2 - t1
            message_length = len(last_answer.message)
            expected_duration = message_length / AVERAGE_CHARACTERS_PER_SECOND
            # pause a little if necessary before send a reply
            if dt < expected_duration:
                # never exceeds 1min +- 7 sec
                seconds_to_wait = min(expected_duration - dt, 60) + random() * 7.0
                lprint(f"4.1 WAIT: {seconds_to_wait:0.2f} seconds before reply")
                time.sleep(seconds_to_wait)

            # 5. senf a reply message through whatsapp api
            lprint(f"4.2 BEFORE SEND REPLY: {last_answer.message}")
            response, status_code = send_reply(phone, last_answer.message)
            last_status_code = status_code
            lprint(f"4.3 LAST RESPONSE: {last_status_code}")

        return "OK", last_status_code
    else:
        return "No messages received", 200


def process_history_with_ai(phone: str, history: list[History]) -> History:
    if LLM_PLATFORM == "openai":
        platform = LlmPlatform(LLM_PLATFORM)
        llm = Llm(platform=platform, model_name=LLM_MODEL)

        prompt_text = history[0].message
        list_of_messages = f"\n\n\n".join([f"[{k+1}:{xk.dt}:{xk.who}]\n{xk.message}" for k, xk in enumerate(history[1:])])
        full_message = f"{prompt_text}\n{list_of_messages}"
        lprint(f">>>>> FULL MESSAGE:\n{full_message}")

        try:
            answer = llm.get_answer(prompt=full_message)
        except Exception as e:
            lprint(f"LLM>>>>> ERROR: {e}")
            answer = "<<agente no disponible>>"

        last_answer = History(phone=phone, message=answer)
        return last_answer


def send_reply(to, text):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    data = json.dumps(payload)
    try:
        response = requests.post(WHATSAPP_API_URL, headers=headers, data=data)
        status_code = response.status_code
    except Exception as e:
        response = None
        status_code = 500
        lprint(f"ERROR: {e}")
    return response, status_code

