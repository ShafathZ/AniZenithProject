import os
import time
from typing import List, Dict

from dotenv import load_dotenv

from backend.mongo.AniZenithMongoClient import AniZenithMongoClient
from backend.mongo.AniZenithVectorSearchResult import AniZenithVectorSearchResult
from backend.prometheus_utils import *
from backend.models import HFInferenceClientModel, HFLocalModel, Model
from backend.reranker import AniZenithReranker
from constants import *

load_dotenv()
# TODO: Move to config management system
MONGO_CONN_STRING = os.getenv("ATLAS_URI")

VECTOR_SEARCH_LIMIT = 20
RERANK_LIMIT = 5

MODEL_DOWNTIME_SECONDS = 120


class InferenceManager:

    def __init__(self):
        # Initialize Models for use in descending order of importance
        self.models: List[Model] = [HFInferenceClientModel(), HFLocalModel()]
        self.current_model_idx = 0 # Current model idx being used
        self.model_available_at = [0.0 for _ in self.models] # Controls fallback timer in case error occurs

        # Load a DB Client Instance
        self.db_client = AniZenithMongoClient(MONGO_CONN_STRING)

        # Load a Reranker model instance
        self.reranker = AniZenithReranker()

    # Gets the current most prioritized model for use
    def get_best_model(self) -> Model:
        now = time.time()

        for i, model in enumerate(self.models):
            if now >= self.model_available_at[i]:
                self.current_model_idx = i
                return model

        # If all models are cooling down, throw error models not available
        # TODO: Make custom exception
        raise Exception("No model available")


    def chat(self, messages: List[Dict[str, str]], user_id: str = None):
        """
        Enhanced inference chat function with retrieval and reranking.
        Steps:
          1. Retrieve relevant documents from MongoDB
          2. Rerank them with the reranker
          3. Build LLM messages prompt
          4. Stream the model output
        """
        # TODO: Make this an agentic framework using LangChain
        # TODO: Use user_id in logging
        # TODO: Add queue system to make blocking better
        current_model = self.get_best_model()
        with CHATBOT_PIPELINE_LATENCY_SUMMARY.labels(model=current_model.get_name(), stage="full_pipeline").time():
            # 1) Retrieve results from DB Client
            with CHATBOT_PIPELINE_LATENCY_SUMMARY.labels(model=current_model.get_name(), stage="db_retrieval").time():
                # Use the last message as the user message (it should always be a user message)
                user_query = messages[-1]['content']
                retrieved_docs: List[AniZenithVectorSearchResult] = self.db_client.perform_vector_search(user_query, limit=VECTOR_SEARCH_LIMIT)

            # 2) Rerank results using the reranker based on document info and user query
            with CHATBOT_PIPELINE_LATENCY_SUMMARY.labels(model=current_model.get_name(), stage="reranker").time():
                recommended_docs: List[AniZenithVectorSearchResult] = self.reranker.rerank(user_query, retrieved_docs, limit=RERANK_LIMIT)

            # 3) Construct system prompt with recommended docs
            system_prompt = self._build_system_prompt(recommended_docs)

            # 4) Insert system prompt into messages
            messages.insert(0, {"role": "system", "content": system_prompt})

            # 5) Stream output of the model using the stream method
            with CHATBOT_PIPELINE_LATENCY_SUMMARY.labels(model=current_model.get_name(), stage="model_generation").time():
                try:
                    for token in current_model.stream(messages):
                        yield token

                except Exception as e:
                    # TODO: Log error
                    # Sets next available time to current time in seconds + downtime
                    self.model_available_at[self.current_model_idx] = time.time() + MODEL_DOWNTIME_SECONDS

    def _build_system_prompt(self, recommendations: List[AniZenithVectorSearchResult]) -> str:
        lines = []

        # Add base system prompt
        lines.append(SYSTEM_PROMPT)
        lines.append("Here are the recommendation system's top shows:\n")

        # Add recommendation docs
        # model_dump() is a special Pydantic method to generate a dict representation of any Pydantic object
        recommendations = [recommendation.model_dump() for recommendation in recommendations]
        recommendation_string = "\n\n".join(recommendations) if recommendations else "No good recommendations found."
        lines.append(recommendation_string)

        return "\n".join(lines)
