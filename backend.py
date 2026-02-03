from typing import List

from huggingface_hub import InferenceClient
from transformers import pipeline

from retrieval_utils import get_recommendations

genre_list = open("genrelist.txt", "r").read().splitlines()

def process_user_query(system_message: str, history: List[dict], user_message: str, use_local_model: bool, max_tokens: int, temperature: float, top_p: float, hf_token):
    # 1. Retrieve genres from the user message using naive approach
    genre_list = detect_genres(user_message)
    #print(f"Requested genres: {genre_list}")

    # 2. Retrieve relevant results from DB
    recommendations_string = get_recommendations(genre_list)
    #print(f"Recommendations found: {recommendations_string}")

    # 3. Append recommendation string to system message
    # TODO: Use few-shot conversation method instead of appending to system prompt for better results
    system_message = system_message + recommendations_string

    # 4. Query the model
    for result in query_model(system_message, history, user_message, use_local_model, max_tokens, temperature, top_p, hf_token):
        yield result

def detect_genres(message: str) -> List[str]:
    requested_genres = []
    # Simple naive genre check by detecting if any of our system stored genres are within the user query
    # TODO: Improve genre detection instead to use Retriever and RAG framework in the future
    for genre in genre_list:
        if message.__contains__(genre):
            requested_genres.append(genre)
    return requested_genres

def query_model(
        system_message: str,
        history: List[dict],
        user_message: str,
        use_local_model: bool,
        max_tokens: int,
        temperature: float,
        top_p: float,
        hf_token):
    # Construct prompt for language model
    messages = [{"role": "system", "content": system_message}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    # Determine which model to use (local or external)
    if use_local_model:
        # Local Model -- Use pipeline
        # TODO: Change to non-thinking model since it does not make sense for our application currently
        pipe_liquid = pipeline(task='text-generation',
                               model='LiquidAI/LFM2.5-1.2B-Thinking',
                               max_new_tokens=max_tokens,
                               temperature=temperature,
                               do_sample=False,
                               top_p=top_p)
        response = pipe_liquid(messages)
        # TODO: Once non-thinking model is implemented, streaming can be added. If we decide to keep thinking model, streaming needs delay to first End-Think token
        response_string = response[0]['generated_text'][-1]['content'].split('</think>')[-1].strip()
        yield response_string
    elif not use_local_model:
        # Non-local Model -- Use InferenceClient
        client = InferenceClient(
            token=hf_token.token,
            model="openai/gpt-oss-20b",
        )

        response = ""
        for chunk in client.chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                stream=True,
                temperature=temperature,
                top_p=top_p,
        ):
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                response += token
                yield response

