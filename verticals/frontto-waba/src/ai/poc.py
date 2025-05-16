import os
from enum import Enum

import requests
from openai import api_type

from ai.llm_openai import LlmOpenAi
from ai.llm_gemini import LLmGemini
from ai.llm_deepseek import LlmDeepseek
from utils.dt import now

from dotenv import load_dotenv

load_dotenv()

QUESTION="hola, explicame como obtener ternas pitagoricas en menos de 80 tokens (no codigo, solo matematicas)"

def call_llm(class_name):
    model_name = class_name.__name__.upper()[3:]
    api_key = os.getenv(f"{model_name}_APIKEY")
    llm = class_name(api_key=api_key)
    answer, _ = llm.get_answer_and_json_response(QUESTION)
    print(answer)

def main():
    prompt = open(os.path.join(os.path.dirname(__file__), '../../cli/llm-prompt.md')).read()

    chatgpt_apikey = os.getenv('CHATGPT_APIKEY', "")
    gemini_apikey = os.getenv('GEMINI_APIKEY', "")
    deepseek_apikey = os.getenv('DEEPSEEK_APIKEY', "")

    model = "gemini"
    llms = {
        "chatgpt": LlmOpenAi(api_key=chatgpt_apikey),
        "gemini": LLmGemini(api_key=gemini_apikey),
        "deepseek": LlmDeepseek(api_key=deepseek_apikey),
    }

    history = prompt

    input_text = ""
    while input_text.upper().strip() != "EXIT":
        llm = llms[model]

        input_text = input(f"[USER][{now()}]>\n")
        history_input_text = f"[USER][{now()}]\n{input_text}"
        history += f"\n\n{history_input_text}"

        ans, _ = llm.get_answer_and_json_response(prompt=history)

        history_ans = f"[USER][{now()}]\n{ans}"
        history += f"\n\n{history_ans}"

        print(history_ans)

def openai_scrape_princing():
    url="https://platform.openai.com/docs/pricing"
    response = requests.get(url)
    print(response.status_code)
    print(response.text)

if __name__ == '__main__':
    # main()
    # call_gemini()
    # call_chatgpt()
    # call_llm(LlmOpenAi)
    # call_llm(LlmDeepseek)
    # call_llm(LLmGemini)
    openai_scrape_princing()