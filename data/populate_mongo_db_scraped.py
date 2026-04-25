from pymongo import MongoClient
from dotenv import load_dotenv
import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from pymongo.operations import SearchIndexModel

from backend.mongo.utils import create_text_metadata_and_embedding

from backend.configs import model_config

# Load all Env variables
load_dotenv()

# Load Sentence Transformer Model
embedding_model = SentenceTransformer(model_config.embedding_model_id)

def clean_data():
    # Load the Anime Dataset as a Pandas DataFrame
    anime_df = pd.read_json('./data/anime.json')

    # Exclude Adult Rated Content
    anime_df = anime_df[anime_df["age_rating"] != "rx"]

    # Project current title as its own node_name column (since they may not be english, but useful data)
    anime_df["node_name"] = anime_df["title"]

    # Filter out animes without English Names (check alt_titles dict for "en" key, and ensure it is not empty value)
    anime_df = anime_df[anime_df["alt_titles"].apply(lambda x: "en" in x and x["en"] != "")]

    # Project en titles as new title column
    anime_df["title"] = anime_df["alt_titles"].apply(lambda x: x.pop("en"))

    # Filter out animes without scores
    anime_df = anime_df[anime_df["score"].notna()]

    # Filter out animes without synopsis
    anime_df = anime_df[anime_df["synopsis"].notna() & (anime_df["synopsis"] != "")]

    # Generate text metadata
    # TODO: Make this metadata better for retrieval
    print("Generating text metadata and embeddings... this might take a minute...")
    anime_df[['text_metadata', 'text_metadata_embedding']] = anime_df.apply(
        lambda row: create_text_metadata_and_embedding(
            embedding_model=embedding_model,
            anime_name=row['title'],
            anime_genres=row['genres'],
            anime_synopsis=row['synopsis']
        ),
        axis=1,
        result_type='expand'
    )

    return anime_df

def create_mongodb_and_indexes(df):
    # Convert DataFrame to a list of dictionaries (documents) suitable for MongoDB
    documents = df.to_dict(orient='records')
    print(f"Successfully prepared {len(documents)} anime records for DB inserts!")

    # Connect to MongoDB Atlas
    client = MongoClient(os.environ["ATLAS_URI"])
    print(f"Successfully connected to MongoDB Atlas")

    # Create / Access the "anizenith" DB
    # TODO: Move hardcoded configs to a central config object
    db = client["anizenith"]

    # Create / Access the "anime" collection
    # TODO: Move hardcoded configs to a central config object
    collection = db["anime"]

    # Clear existing data
    collection.delete_many({})

    # Insert the documents into the collection
    if documents:
        # Define the Vector Search index
        search_index_model = SearchIndexModel(
            definition={
                "fields": [
                    {
                        "type": "vector",
                        "path": "text_metadata_embedding",
                        "numDimensions": embedding_model.get_embedding_dimension(),
                        "similarity": "cosine"    # Options: "cosine", "dotProduct", "euclidean"
                    }
                ]
            },
            name="vector_index",
            type="vectorSearch"
        )

        # Create the index on your collection
        result = collection.create_search_index(model=search_index_model)
        print(f"Index creation started: {result}")

        result = collection.insert_many(documents)
        print(f"Successfully inserted {len(result.inserted_ids)} anime documents.")
    else:
        print("No valid documents found to insert.")

if __name__ == "__main__":
    # Clean data if not already existing
    if not os.path.exists("./data/anime_cleaned.json"):
        output_df = clean_data()
        print(f"Built new records:\n{output_df.head(10)}")
        # Save temporarily in case of failure
        output_df.to_json("./data/anime_cleaned.json", orient="records")

    # TODO: Output to MongoDB Client

