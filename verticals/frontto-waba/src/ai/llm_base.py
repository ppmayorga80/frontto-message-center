from abc import ABC, abstractmethod

class LlmBase(ABC):
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    def get_answer_and_json_response(self, prompt: str) -> tuple[str, dict]:
        """Abstract method for retrieving answer and the full JSON response."""
        pass

    @ abstractmethod
    def list_models(self)->list:
        pass