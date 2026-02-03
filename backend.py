from typing import List

from retrieval_utils import get_recommendations

def detect_genres(message: str) -> List[str]:
    # TODO: Detect genres from a genrelist.txt file. If message contains any, append that as genre to the list.
    pass

def query_model(system_message, history, user_message, use_local_model, max_tokens, temperature, top_p, hf_token):
    # TODO: Program calling model using Amaan's code
    pass

def process_user_query(system_message, history, user_message, use_local_model, max_tokens, temperature, top_p, hf_token):
    # 1. Retrieve genres from the user message using naive approach
    genre_list = detect_genres(user_message)

    # 2. Retrieve relevant results from DB
    recommendations_string = get_recommendations(genre_list)

    # 3. Append recommendation string to system message
    system_message = system_message + recommendations_string

    # 4. Query the model
    for result in query_model(system_message, history, user_message, use_local_model, max_tokens, temperature, top_p, hf_token):
        yield result

