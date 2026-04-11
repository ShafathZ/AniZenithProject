from typing import List, Dict
from huggingface_hub import InferenceClient
from transformers import pipeline
from backend.constants import *
from backend.prometheus_utils import *
from dotenv import load_dotenv
import os
import json
from backend.mongo.AniZenithMongoClient import AniZenithMongoClient
from backend.mongo.AniZenithVectorSearchResult import AniZenithVectorSearchResult

# Load all Environment Variables
load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN')

# Init AniZenithMongoClient
CONN_STRING = os.getenv("ATLAS_URI")
DB_CLIENT = AniZenithMongoClient(CONN_STRING)


# Load the Local Pipeline Model at App Startup
PIPELINE_LOCAL_MODEL = pipeline(task='text-generation',
                                model='Qwen/Qwen3-0.6B',
                                max_new_tokens=MAX_NEW_TOKENS,
                                temperature=TEMPERATURE,
                                do_sample=False,
                                top_p=TOP_P)


# TODO: Make this Method Async Later
def chat_with_llm(messages: List[Dict[str, str]], use_local_model: bool):

    # TODO: Replace with actual IDs from a config
    model = "Qwen/Qwen3-0.6B" if use_local_model else "openai/gpt-oss-20b"
    with CHATBOT_PIPELINE_LATENCY_SUMMARY.labels(model=model, stage="full_pipeline").time():

        # Use the last message as the user message (it should always be a user message)
        user_query = messages[-1]['content']

        # Retrieve relevant results from DB using vector search
        with CHATBOT_PIPELINE_LATENCY_SUMMARY.labels(model=model, stage="db_retrieval").time():

            # Perform Vector Search using user query
            # This method returns a List[AniZenithVectorSearchResult]
            recommendations: List[AniZenithVectorSearchResult] = DB_CLIENT.perform_vector_search(user_query)
            
            # Convert the list of vector search objects into a list of dicts
            # model_dump() is a special Pydantic method to generate a dict representation of any Pydantic object
            recommendations_dict = [recommendation.model_dump() for recommendation in recommendations]
            
            # Serialize to a JSON string
            recommendations_string = json.dumps(recommendations_dict, indent = 4)

        # Query the model
        with CHATBOT_PIPELINE_LATENCY_SUMMARY.labels(model=model, stage="model_generation").time():
            for result in query_model(messages, use_local_model, recommendations_string):
                yield result


# TODO: Make this method Async later
def query_model(messages: List[Dict[str, str]], use_local_model: bool, recommendations_string: str):
    # --- Determine System Prompt ---
    # Start with the Fixed System Prompt
    system_prompt = SYSTEM_PROMPT

    # Append recommendation string data to the System Prompt if it exists
    if recommendations_string:
        system_prompt += "\nRECOMMENDATION JSON:" + f"\n{recommendations_string}"

    # Add the System Prompt to the Input Messages to the LLM
    input_messages = [{"role": "system", "content": system_prompt}]
    # Add the rest of the messages
    input_messages.extend(messages)

    # --- Determine which model to use (local or external) ---
    # Constants for logging
    response = ""
    input_token_count = 0
    output_token_count = 0

    # --- Local Model ---
    if use_local_model:
        # Uses pipeline from transformers library
        response = PIPELINE_LOCAL_MODEL(input_messages)

        # Get the response from the local model, parse it, and yield
        generated_text = response[0]['generated_text'][-1]['content'].split('</think>')[-1].strip()
        yield generated_text

        # Log token counts (there is no clean way to do this besides re-tokenizing)
        tokenizer = PIPELINE_LOCAL_MODEL.tokenizer
        formatted_input = tokenizer.apply_chat_template(
            input_messages,
            tokenize=False,
            add_generation_prompt=True
        )
        input_tokens = tokenizer.encode(formatted_input)
        generated_tokens = tokenizer.encode(generated_text)
        input_token_count = len(input_tokens)
        output_token_count = len(generated_tokens)
            
    # --- Non-local Model (Use InferenceClient) ---
    else:
        client = InferenceClient(
            token=HF_TOKEN,
            model="openai/gpt-oss-20b",
        )

        # Stream inference client output and yield the text chunk
        usage = None
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
            # Add usage data for logging
            if hasattr(chunk, 'usage') and chunk.usage:
                usage = chunk.usage

        if usage:
            input_token_count = usage.prompt_tokens
            output_token_count = usage.completion_tokens

    # Log the model usage output
    # TODO: Record the specific model ID once the backend is refactored
    model = "Qwen/Qwen3-0.6B" if use_local_model else "openai/gpt-oss-20b"
    # TODO: Use real Inference Manager / session ID
    observe_user_message(user_id="0", user_message=messages[-1]['content'], token_count=input_token_count, model=model)
    observe_bot_message(user_id="0", bot_message=response, token_count=output_token_count, model=model)

