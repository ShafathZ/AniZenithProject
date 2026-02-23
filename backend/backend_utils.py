from typing import List, Dict
from huggingface_hub import InferenceClient
from transformers import pipeline
from backend.retrieval_utils import get_recommendations
from backend.constants import *
from dotenv import load_dotenv
import os

# Load all Environment Variables
load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN')

# Load the List of All Supported Genres in Memory, at App Startup
genre_list = open("backend/genrelist.txt", "r").read().splitlines()


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
    for genre in genre_list:
        if message.__contains__(genre):
            requested_genres.append(genre)
    return requested_genres


# TODO: Make this method Async later
def query_model(messages: List[Dict[str, str]], use_local_model: bool, recommendations_string: str):

    # Determine System Prompt
    # Start with the Fixed System Prompt
    system_prompt = SYSTEM_PROMPT

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
        # Uses pipeline from transformers library
        pipeline_local_model = pipeline(task='text-generation',
                                        model='Qwen/Qwen3-0.6B',
                                        max_new_tokens=MAX_NEW_TOKENS,
                                        temperature=TEMPERATURE,
                                        do_sample=False,
                                        top_p=TOP_P)
        
        # Get the response from the local model
        response = pipeline_local_model(input_messages)
        
        # Parse the output and yield it
        yield response[0]['generated_text'][-1]['content'].split('</think>')[-1].strip()
            
    # Use Inference Client for the default case
    else:
        # Non-local Model -- Use InferenceClient
        client = InferenceClient(
            token=HF_TOKEN,
            model="openai/gpt-oss-20b",
        )

        response = ""
        for chunk in client.chat_completion(
                messages=input_messages,
                max_tokens=MAX_NEW_TOKENS,
                stream=True,
                temperature=TEMPERATURE,
                top_p=TOP_P,
        ):
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                response += token
                yield response

