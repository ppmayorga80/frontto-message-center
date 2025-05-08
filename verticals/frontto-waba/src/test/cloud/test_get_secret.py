from cloud.get_secret import get_secret

def test_get_secret():
    PROJECT_ID = "frontto-message-center"
    api_key = get_secret("openai-api-key", project_id=PROJECT_ID)
    assert isinstance(api_key, str)
    assert api_key.strip()!=""

def test_get_secret_fail():
    # case 1: wrong secret name
    PROJECT_ID = "frontto-message-center"
    api_key = get_secret("WRONG-SECRET-NAME", project_id=PROJECT_ID)
    assert api_key is None

    # case 2: wrong project name
    PROJECT_ID = "WRONG-PROJECT-ID"
    api_key = get_secret("openai-api-key", project_id=PROJECT_ID)
    assert api_key is None
