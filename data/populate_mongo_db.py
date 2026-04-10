from pymongo import MongoClient
from dotenv import load_dotenv
import os
import pandas as pd

# Load all Env variables
load_dotenv()

# Load the Anime Dataset as a Pandas DataFrame
df = pd.read_csv('data/anime-dataset-2023.csv')

# Exclude some Genres
excluded_genres = ['Hentai', 'UNKNOWN', 'Erotica', 'Ecchi']
pattern = '|'.join(excluded_genres)

# Filter out animes that contain excluded genres
anime_df = df[~df['Genres'].str.contains(pattern, na=True)]

# Filter out animes without English Names
anime_df = anime_df[anime_df['English name'] != 'UNKNOWN']

# Filter out animes without Scores
anime_df = anime_df[anime_df['Score'] != 'UNKNOWN']

# Filter out animes without Synopsis
anime_df = anime_df[anime_df['Synopsis'] != 'No description available for this anime.']

# Convert Score column type to float
anime_df['Score'] = anime_df['Score'].astype(float)

# Sort by Score and Keep only Top 1000 Animes
anime_df = anime_df.sort_values(by='Score', ascending=False).head(1000)

# Convert the comma-separated Genres string into a Python list
anime_df['Genres'] = anime_df['Genres'].apply(lambda x: [g.strip() for g in str(x).split(',')] if pd.notnull(x) else [])

# TODO: Remove extra newlines within synopsis

# Create a new field called text_metadata
anime_df['text_metadata'] = anime_df.apply(
    lambda row: f"Name: {row['English name']}\n\nGenres: {', '.join(row['Genres'])}\n\nSynopsis: {row['Synopsis'].replace('\n', '')}",
    axis = 1
)

# Keep only the columns we need and rename them
anime_df = anime_df[['English name', 'Score', 'Synopsis', 'Genres', 'text_metadata']]
print(anime_df.head())

anime_df = anime_df.rename(columns={
    'English name': 'name',
    'Score': 'score',
    'Synopsis': 'synopsis',
    'Genres': 'genres'
})

# Convert DataFrame to a list of dictionaries (documents) suitable for MongoDB
documents = anime_df.to_dict(orient='records')
print(f"Successfully prepared {len(documents)} anime records for DB inserts!")


# Connect to MongoDB Atlas
client = MongoClient(os.environ["ATLAS_URI"])
print(f"Successfully connected to MongoDB Atlas")

# Create / Access the "anizenith" DB
db = client["anizenith"]

# Create / Access the "anime" collection
collection = db["anime"]

# Clear existing data
collection.delete_many({})

# Insert the documents into the collection
if documents:
    result = collection.insert_many(documents)
    print(f"Successfully inserted {len(result.inserted_ids)} anime documents.")
else:
    print("No valid documents found to insert.")

