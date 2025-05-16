import json
import requests

from ai.llm_base import LlmBase


class LLmGemini(LlmBase):
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-preview-04-17"):
        super().__init__(api_key, model_name)
        # Include the API key as a query parameter to the endpoint (this is the typical approach for PaLM endpoints).
        # Replace with the correct URL for your specific model/version if needed.
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"

    def get_answer_and_json_response(self, prompt: str) -> tuple[str, dict]:
        headers = {
            "Content-Type": "application/json"
        }
        # Adjust the JSON body to match the endpoint's requirements.
        # The structure below is an example; your actual body may differ depending on
        # the model's expected request format.
        data = {
            "contents": [
                {
                    "parts": {
                        "text": prompt
                    }
                }
            ]
        }

        raw_response = requests.post(self.url, headers=headers, json=data)
        if raw_response.status_code == 200:
            response_dict = raw_response.json()
            try:
                # Navigate to the text content of the first candidate
                candidates = response_dict["candidates"]
                first_candidate = candidates[0]
                content_parts = first_candidate["content"]["parts"]
                # Collect text from each 'part'
                response_content_string = "\n".join(
                    part["text"] for part in content_parts if "text" in part
                )
            except (KeyError, IndexError, TypeError) as e:
                raise ValueError(
                    f"Unexpected response structure: {json.dumps(response_dict, indent=2)}"
                ) from e

            return response_content_string, response_dict

        # Provide more context if the request failed
        raise ValueError(
            f"GEMINI request failed - status_code: {raw_response.status_code}, "
            f"reason: {raw_response.reason}, response: {raw_response.text}"
        )

    def list_models(self) -> list:
        api_version = "v1beta"  # Or try "v1" if v1beta gives issues
        base_url = "https://generativelanguage.googleapis.com"
        list_models_endpoint = f"{base_url}/{api_version}/models"
        headers = {
            'Content-Type': 'application/json',
        }

        # The API key is passed as a query parameter for this GET request
        params = {
            'key': self.api_key
        }

        try:
            response = requests.get(list_models_endpoint, headers=headers, params=params)

            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()

            # Parse the JSON response
            response_data = response.json()

            # --- Process and Print the Results ---
            if 'models' in response_data and response_data['models']:
                models = []
                count = 0
                for model in response_data['models']:
                    # The 'name' field contains the identifier you need
                    model_name = model.get('name', 'N/A')
                    if model_name.startswith('models/'):
                        model_name = model_name.replace('models/', '')
                    display_name = model.get('displayName', 'N/A')  # Often more user-friendly
                    models.append(f"{model_name}::{display_name}")
                return models
            else:
                return []

        except Exception as e:
            return None

