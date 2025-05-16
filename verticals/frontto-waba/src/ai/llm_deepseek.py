from openai import OpenAI
from ai.llm_openai import LlmOpenAi


class LlmDeepseek(LlmOpenAi):
    def __init__(self, api_key: str, model_name: str = "deepseek-chat"):
        super().__init__(api_key, model_name)

        deepseek_base_url = "https://api.deepseek.com/v1"  # Make sure '/v1' is included if needed by the library version
        self.client = OpenAI(api_key=api_key, base_url=deepseek_base_url)


