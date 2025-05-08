from openai import OpenAI
from ai.llm_base import LlmBase


class ChatgptUtils(LlmBase):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        super().__init__(api_key, model_name)
        self.client = OpenAI(api_key=api_key)

    def list_models(self):
        return self.client.models.list()

    def get_answer_and_json_response(self, text: str) -> tuple[str, dict]:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": text,
                    }
                ],
            )
            response_content_string = response.choices[0].message.content.strip()
            response_dict = response.to_dict()
            return response_content_string, response_dict
        except Exception as e:
            raise e
