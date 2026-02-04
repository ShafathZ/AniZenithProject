from typing import List
from huggingface_hub import InferenceClient
from transformers import pipeline
from retrieval_utils import get_recommendations

genre_list = open("genrelist.txt", "r").read().splitlines()

SYSTEM_PROMPT = f"""
You are an expert on recommending Anime shows. Please use the RECOMMENDATIONS to answer the user's question.
The RECOMMENDATIONS is a JSON String that contains information of top Anime sorted in descending order by:
1. Number of Requested Genre Matches from the User
2. The Score of the Anime

If the RECOMMENDATIONS JSON String is not given: 
1. Then answer the question like a Friendly Chatbot!
2. Do not reference anything about a RECOMMENDATION JSON
3. Ask the user to provide their favorite genre(s) for Anime Recommendations
"""

def process_user_query(system_message: str, history: List[dict], user_message: str, use_local_model: bool, max_tokens: int, temperature: float, top_p: float, hf_token):
    # 1. Retrieve genres from the user message using naive approach
    genre_list = detect_genres(user_message)

    # 2. Retrieve relevant results from DB if the genre_list is not empty
    recommendations_string = ""
    if len(genre_list) > 0:
        recommendations_string = get_recommendations(genre_list)

    # 3. Query the model
    for result in query_model(system_message, 
                              history, 
                              user_message,
                              recommendations_string, 
                              use_local_model, 
                              max_tokens, 
                              temperature, 
                              top_p, 
                              hf_token):
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
        recommendations_string: str,
        use_local_model: bool,
        max_tokens: int,
        temperature: float,
        top_p: float,
        hf_token):
    
    # Construct messages for the language model
    # Start by adding system prompt
    system_prompt = SYSTEM_PROMPT
    if recommendations_string:
        system_prompt += "\nRECOMMENDATION JSON:" + f"\n{recommendations_string}"
    messages = [{"role": "system", "content": system_prompt}]

    # Add the rest of the history
    messages.extend(history)

    # Add the current user prompt
    messages.append({"role": "user", "content": user_message})

    # Determine which model to use (local or external)
    if use_local_model:
        # Local Model -- Uses pipeline from transformers library
        pipeline_local_model = pipeline(task='text-generation',
                               model='google/gemma-3-1b-it',
                               max_new_tokens=max_tokens,
                               temperature=temperature,
                               do_sample=False,
                               top_p=top_p
                               )
        # Get the response from the local model
        response = pipeline_local_model(messages)
        
        # Parse the output and yield it
        yield response[0]['generated_text'][-1]['content'].strip()
            

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

