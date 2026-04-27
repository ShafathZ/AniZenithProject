from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from backend.mongo.AnimeDocument import AnimeDocument
from backend.mongo.utils import create_text_metadata_and_embedding
from backend.mongo.AniZenithVectorSearchResult import AniZenithVectorSearchResult


# Class to model Anizenith MongoDB Client related utilities
class AniZenithMongoClient:
    def __init__(self, conn_string):
        # Validate connection string 
        if not isinstance(conn_string, str) or not conn_string.strip():
            raise ValueError("ATLAS_URI must be set to a non-empty MongoDB connection string")
        
        self.conn_string = conn_string        
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        # Set internals to None for lazy init
        self._db_client = None
        self._anime_collection = None
    
    @property
    def db_client(self):
        """
        Lazily initialize the MongoDB client.
        @property decorator defines this as a property of a class, rather than a class method
        """
        if self._db_client is None:
            self._db_client = MongoClient(self.conn_string)
        return self._db_client
    

    @property
    def anime_collection(self):
        """
        Lazily initialize the anime collection.
        @property decorator defines this as a property of a class, rather than a class method
        """
        if self._anime_collection is None:
            # TODO: Move the hardcoded DB name and collection name into a central Config object
            self._anime_collection = self.db_client["anizenith"]["anime_enriched"]
        return self._anime_collection


    def add_anime(self, anime_document: AnimeDocument) -> None:

        # Create text metadata and its embedding
        text_metadata, text_metadata_embedding = create_text_metadata_and_embedding(
            self.embedding_model,
            anime_document.name,
            anime_document.genres,
            anime_document.synopsis
        )

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


    def execute_read_query(self, query, skip = None, limit = None) -> List[Dict]:
        try:
            if isinstance(query, dict):
                # Execute a standard find operation (e.g., {"score": {"$gt": 8.0}})
                # "find()" is a standard read-only MongoDB command
                cursor = self.anime_collection.find(query)
                if skip is not None:
                    cursor = cursor.skip(skip)
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


    def perform_vector_search(self, user_query: str, limit: int = 5, num_candidates: int = 100) -> List[AniZenithVectorSearchResult]:
        # Validate limit and num_candidates 
        if limit <= 0:
            raise ValueError("limit must be a positive integer")
        if num_candidates <= 0:
            raise ValueError("num_candidates must be a positive integer")
        if num_candidates < limit:
            raise ValueError("num_candidates should be atleast as much as limit")

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
        
        # Execute the pipeline and retrieve the cursor
        cursor = self.anime_collection.aggregate(pipeline)
        
        # Convert the cursor to a list of dicts
        return [AniZenithVectorSearchResult(**doc) for doc in cursor]