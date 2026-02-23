import os
import pytest
from backend.backend_utils import chat_with_llm
import backend.backend_utils as backend_utils

TEST_SYSTEM_MESSAGE = "You are a friendly chatbot."
TEST_USER_MESSAGE = "Hello!"
HF_TOKEN = os.getenv("HF_TOKEN")


def test_HF_token_exists():
    token = os.getenv("HF_TOKEN")
    assert token is not None
    assert len(token) > 1


def test_local_model_runs(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(backend_utils, "SYSTEM_PROMPT", TEST_SYSTEM_MESSAGE)
    use_local_model = True
    collected_result = ""
    for result in chat_with_llm(messages=[{"role": "user", "content": TEST_USER_MESSAGE}],
                                use_local_model=use_local_model):
        collected_result = result

    assert len(collected_result) > 0


def test_external_model_runs(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(backend_utils, "SYSTEM_PROMPT", TEST_SYSTEM_MESSAGE)
    use_local_model = False
    collected_result = ""
    for result in chat_with_llm(messages=[{"role": "user", "content": TEST_USER_MESSAGE}],
                                use_local_model=use_local_model):
        collected_result = result
    assert len(collected_result) > 0

if __name__ == "__main__":
    pytest.main()


