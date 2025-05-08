from ai.llm import Llm, LlmPlatform


def test_llm_default():
    # case 1: Default
    model = Llm()
    ans = model.get_answer(prompt="What is your name?")
    assert isinstance(ans, str)
    assert ans != ""
    print(ans)

def test_llm_gemini():
    # case 1: Default
    model = Llm(platform=LlmPlatform.GEMINI)
    ans = model.get_answer(prompt="If you say my name I not exist anymore, who am I?")
    assert isinstance(ans, str)
    assert ans != ""
    print(ans)
