from typing import List, Dict
from huggingface_hub import InferenceClient
from transformers import pipeline, GenerationConfig
from backend.retrieval_utils import get_recommendations
from backend.configs import model_config, backend_app_config

# Load the List of All Supported Genres in Memory, at App Startup
GENRE_LIST = open("backend/genrelist.txt", "r").read().splitlines()


# Load the Local Pipeline Model at App Startup
PIPELINE_LOCAL_MODEL = pipeline(task='text-generation', model=model_config.local_model_id)


# TODO: Make this Method Async Later
def chat_with_llm(messages: List[Dict[str, str]], use_local_model: bool):
    
    # Retrieve genres from the user message using naive approach
    # The Last Message should be user's message
    genre_list = detect_genres(messages[-1]['content'])

    # 2. Retrieve relevant results from DB if the genre_list is not empty
    recommendations_string = ""
    if len(genre_list) > 0:
        recommendations_string = get_recommendations(genre_list)

    # 3. Query the model
    for result in query_model(messages, use_local_model, recommendations_string):
        yield result


def detect_genres(message: str) -> List[str]:
    requested_genres = []
    # Simple naive genre check by detecting if any of our system stored genres are within the user query
    # TODO: Improve genre detection instead to use Retriever and RAG framework in the future
    for genre in GENRE_LIST:
        if message.lower().__contains__(genre.lower()):
            requested_genres.append(genre)
    return requested_genres


# TODO: Make this method Async later
def query_model(messages: List[Dict[str, str]], use_local_model: bool, recommendations_string: str):

    # Determine System Prompt
    # Start with the Fixed System Prompt
    system_prompt = model_config.system_prompt

    # If the recommendations_string is not None
    if recommendations_string:

        # Append its data to the System Prompt
        system_prompt += "\nRECOMMENDATION JSON:" + f"\n{recommendations_string}"

    # Add the System Prompt to the Input Messages to the LLM
    input_messages = [{"role": "system", "content": system_prompt}]

    # Add the rest of the messages
    input_messages.extend(messages)

    # Determine which model to use (local or external)
    if use_local_model:
        # Local Model
        # Uses pipeline from transformers library w/ Generation Config (since old method is now deprecated)
        # Get the response from the local model
        generation_config = GenerationConfig(
            max_new_tokens=model_config.max_new_tokens,
            temperature=model_config.temperature,
            top_p=model_config.top_p,
            do_sample=True
        )
        response = PIPELINE_LOCAL_MODEL(input_messages, generation_config=generation_config)
        
        # Parse the output and yield it
        yield response[0]['generated_text'][-1]['content'].split('</think>')[-1].strip()
            
    # Use Inference Client for the default case
    else:
        # Non-local Model -- Use InferenceClient
        client = InferenceClient(
            token=backend_app_config.HF_TOKEN,
            model=model_config.external_model_id,
        )

        response = ""
        for chunk in client.chat_completion(
                messages=input_messages,
                max_tokens=model_config.max_new_tokens,
                stream=True,
                temperature=model_config.temperature,
                top_p=model_config.top_p,
        ):
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                response += token
                yield response

