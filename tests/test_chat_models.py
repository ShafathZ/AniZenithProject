import os
import pytest
from backend.inference_manager import InferenceManager

# TODO: Need help re-integrating monkeypatch, leave until after config management refactor
TEST_SYSTEM_MESSAGE = "You are a friendly chatbot."
TEST_USER_MESSAGE = "Hello!"
HF_TOKEN = os.getenv("HF_TOKEN")

@pytest.fixture(scope="module")
def get_manager():
    return InferenceManager()

def test_HF_token_exists():
    token = os.getenv("HF_TOKEN")
    assert token is not None
    assert len(token) > 1


def test_local_model_runs(get_manager):
    collected_result = ""
    for result in get_manager.chat(messages=[{"role":"user","content": TEST_USER_MESSAGE}]):
        collected_result += result

    assert len(collected_result) > 0


def test_external_model_runs(get_manager):
    collected_result = ""
    for result in get_manager.chat(messages=[{"role": "user", "content": TEST_USER_MESSAGE}]):
        collected_result = result
    assert len(collected_result) > 0

if __name__ == "__main__":
    pytest.main()


