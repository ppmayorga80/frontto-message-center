from cloud.get_secret import get_secret
from ai.deepseek_utils import DeepseekUtils

def test_deepseek_utils_list():
    PROJECT_ID = "frontto-message-center"
    api_key = get_secret("deepseek-api-key", project_id=PROJECT_ID)

    ds = DeepseekUtils(api_key=api_key)
    models = ds.list_models()
    assert len(models) > 0

    for model in models:
        print(model)

def test_deepseek_utils():
    PROJECT_ID = "frontto-message-center"
    api_key = get_secret("deepseek-api-key", project_id=PROJECT_ID)

    ds = DeepseekUtils(api_key=api_key)
    answer, response = ds.get_answer_and_json_response("""
    cual es el area de un circulo de radio $\frac{1}{\sqrt{\pi}}$?
    """)

    assert isinstance(answer, str)
    assert isinstance(response, dict)
    assert answer!=""
    assert response

    print(answer)
