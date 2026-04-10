from pymongo import MongoClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
from typing import List, Dict


# Class to Model a typical Anime Document
class AnimeDocument(BaseModel):
    name: str
    score: float
    synopsis: str
    genres: List[str]


# Class to model Anizenith MongoDB Client related utilities
class AniZenithMongoClient:
    def __init__(self, conn_string):
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.db_client = MongoClient(conn_string)
        self.anime_collection = self.db_client["anizenith"]["anime"]


    def add_anime(self, anime_document: AnimeDocument) -> None:
        # Create text_metadata field using synopsis, genres and name
        text_metadata = f"Synopsis: {anime_document.synopsis}\n\nGenres: {', '.join(anime_document.genres)}\n\nName: {anime_document.name}"
        
        # Create embedding for the text_metadata field
        text_metadata_embedding = self.embedding_model.encode(text_metadata).tolist()

        # Create a new document to be inserted into MongoDB
        anime_document_dict = {
            "name": anime_document.name,
            "score": anime_document.score,
            "synopsis": anime_document.synopsis,
            "genres": anime_document.genres,
            "text_metadata": text_metadata,
            "text_metadata_embedding": text_metadata_embedding
        }

        # Insert the new document
        self.anime_collection.insert_one(anime_document_dict)


    def execute_mongo_read_query(self, query, limit = None) -> List[Dict]:
        try:
            if isinstance(query, dict):
                # Execute a standard find operation (e.g., {"score": {"$gt": 8.0}})
                cursor = self.anime_collection.find(query)
                if limit is not None:
                    cursor = cursor.limit(limit)

            else:
                raise ValueError("Query must be a dict (filter)")
            
            # Convert the cursor to a list of dictionaries to return
            return list(cursor)
        
        # Catch any Exception that happened
        except Exception as e:
            print(f"Error executing MongoDB query: {e}")
            return []


    def perform_vector_search(self, user_query: str, limit: int = 5, num_candidates: int = 100) -> List[Dict]:
         # Embed the search query
        query_vector = self.embedding_model.encode(user_query).tolist()
        
        # Define the $vectorSearch aggregation pipeline
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",                  
                    "path": "text_metadata_embedding",       
                    "queryVector": query_vector,

                    # Number of candidates to evaluate (must be >= limit)  
                    # Uses HNSW           
                    "numCandidates": num_candidates,                     
                    "limit": limit                              
                }
            },
            {
                # Project only the fields we want to see, plus the search score
                "$project": {
                    "_id": 0,
                    "name": 1,
                    "genres": 1,
                    "score": 1,
                    "synopsis": 1,
                    "similarity_score": {"$meta": "vectorSearchScore"}         # Include the similarity score
                }
            },
        ]
        
        # Execute the pipeline
        cursor = self.anime_collection.aggregate(pipeline)
        
        # Convert the cursor to a list of dicts
        return list(cursor)