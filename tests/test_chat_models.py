import os

import pytest

from backend import process_user_query

TEST_SYSTEM_MESSAGE = "You are a friendly chatbot."
TEST_USER_MESSAGE = "Hello!"
HF_TOKEN = os.getenv("HF_TOKEN")

def test_HF_token_exists():
    token = os.getenv("HF_TOKEN")
    assert token is not None
    assert len(token) > 1

def test_local_model_runs():
    use_local_model = True
    collected_result = ""
    for result in process_user_query(system_message=TEST_SYSTEM_MESSAGE,
                       history=[],
                       user_message=TEST_USER_MESSAGE,
                       use_local_model=use_local_model,
                       max_tokens=100,
                       temperature=0.7,
                       top_p=0.7,
                       hf_token=HF_TOKEN):
        collected_result = result

    assert len(collected_result) > 0

def test_external_model_runs():
    use_local_model = False
    collected_result = ""
    for result in process_user_query(system_message=TEST_SYSTEM_MESSAGE,
                                     history=[],
                                     user_message=TEST_USER_MESSAGE,
                                     use_local_model=use_local_model,
                                     max_tokens=100,
                                     temperature=0.7,
                                     top_p=0.7,
                                     hf_token=HF_TOKEN):
        collected_result = result
    assert len(collected_result) > 0

if __name__ == "__main__":
    pytest.main()


