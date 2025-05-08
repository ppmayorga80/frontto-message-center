from ai.gemini_utils import GeminiUtils
from cloud.get_secret import get_secret
import json

def test_gemini_utils():
    # Replace the API key below with a valid key if testing locally
    PROJECT_ID = "frontto-message-center"
    api_key = get_secret("gemini-api-key", project_id=PROJECT_ID)
    gem = GeminiUtils(api_key=api_key, model_name="gemini-2.5-flash-preview-04-17")
    answer, response = gem.get_answer_and_json_response("""
    Cual es el area de un circulo de radio $\frac{1}{\sqrt{\pi}}$?
        """)

    assert isinstance(answer, str)
    assert answer.strip() != ""
    assert isinstance(response, dict)
    assert response

    print("ANSWER:", answer)
    print("RESPONSE:", json.dumps(response, indent=3))

def test_gemini_utils_list_models():
    PROJECT_ID = "frontto-message-center"
    api_key = get_secret("gemini-api-key", project_id=PROJECT_ID)
    gem = GeminiUtils(api_key=api_key)
    models = gem.list_models()
    assert isinstance(models, list)
    assert len(models)>0

    for k,mk in enumerate(models):
        model_name, model_display_name = mk.split("::")
        print(k,model_name," ::=> ", model_display_name)