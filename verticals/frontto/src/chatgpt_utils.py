import os
from openai import OpenAI
from get_secret import get_secret

class ChatgptUtils:
    def __init__(self, api_key:str, model_name:str="gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def list_models(self):
        return self.client.models.list()

    def get_content_and_json_response(self, text: str, model_name: str = "") -> tuple[str, dict]:
        model_name = model_name or self.model_name
        try:
            response = self.client.chat.completions.create(
                model=model_name,
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
            print("---")
            print(f"Input Text: {text}")
            print(f"Unexpected error: {e}")
            raise e


if __name__ == "__main__":
    PROJECT_ID = "frontto-message-center"
    api_key = get_secret("openai-api-key", project_id=PROJECT_ID)
    gpt = ChatgptUtils(api_key=api_key)
    con,res = gpt.get_content_and_json_response("Cual es la mejor pelicula de la serie star wars?")
    print(con)