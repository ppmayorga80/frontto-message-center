from cloud.get_secret import get_secret
from ai.chatgpt_utils import ChatgptUtils


def test_chatgpt():
    PROJECT_ID = "frontto-message-center"
    api_key = get_secret("openai-api-key", project_id=PROJECT_ID)
    gpt = ChatgptUtils(api_key=api_key)
    con, res = gpt.get_content_and_json_response("Cual es la mejor pelicula de la serie star wars?")

    # Basic assertions to ensure the function is returning what we expect
    assert con is not None, "Expected 'con' (string response) to be non-empty"
    assert isinstance(con, str), "Expected 'con' to be a string"
    assert res is not None, "Expected 'res' (JSON) to be non-empty"
    assert isinstance(res, dict), "Expected 'res' to be a dictionary"

    # Optionally print or log the content to see the output
    print(f"Content: {con}")
    print(f"JSON Response: {res}")
