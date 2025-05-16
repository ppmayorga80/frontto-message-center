import os
from enum import Enum

from ai.llm_openai import LlmOpenAi
from ai.llm_deepseek import LlmDeepseek
from ai.llm_gemini import LLmGemini
from ai.llm_base import LlmBase
from cloud.get_secret import get_secret


class LlmPlatform(Enum):
    OPENAI = "OPENAI"
    CHATGPT = "OPENAI"
    GOOGLE = "GEMINI"
    GEMINI = "GEMINI"
    DEEPSEEK = "DEEPSEEK"


class Llm:
    DEFAULT_SECRET_NAME = {
        "OPENAI": "openai-api-key",
        "GEMINI": "gemini-api-key",
        "DEEPSEEK": "deepseek-api-key",
    }
    DEFAULT_MODEL = {
        "OPENAI": ChatgptUtils,
        "GEMINI": GeminiUtils,
        "DEEPSEEK": DeepseekUtils,
    }


    def __init__(self, platform: LlmPlatform=LlmPlatform.GEMINI, api_key: str = "", model_name: str = ""):
        self.project_id = os.environ.get("PROJECT_ID")
        self.model: LlmBase

        api_key = api_key or get_secret(secret_name=self.DEFAULT_SECRET_NAME[platform.value], project_id=self.project_id)
        class_object = self.DEFAULT_MODEL[platform.value]
        if model_name:
            self.model = class_object(api_key=api_key, model_name=model_name)
        else:
            self.model = class_object(api_key=api_key)

    def get_answer(self, prompt: str) -> str:
        if not self.model:
            return ""
        answer, _ = self.model.get_answer_and_json_response(prompt=prompt)
        return answer

