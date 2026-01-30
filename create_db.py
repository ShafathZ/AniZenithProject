import pandas as pd

# Load the Anime Dataset as a Pandas DataFrame
df = pd.read_csv('data/anime-dataset-2023.csv')

# Separate the DataFrame into separate tables
# Genre Table
# Create a separate DataFrame using Genres column
genres_df = df['Genres'].str.split(', ').explode().str.strip().drop_duplicates().reset_index(drop=True)
genres_df = pd.DataFrame({'genre_id': range(1, len(genres_df) + 1), 'genre_name': genres_df})

# Exclude some Genres
excluded_genres = ['Hentai', 'UNKNOWN', 'Erotica', 'Ecchi']
genres_df = genres_df[~genres_df['genre_name'].isin(excluded_genres)]

# Anime Table
# Filter out animes that contain excluded genres
pattern = '|'.join(excluded_genres)
anime_df = df[~df['Genres'].str.contains(pattern, na=True)]

# Filter out animes without English Names
anime_df = anime_df[anime_df['English name'] != 'UNKNOWN']

# Filter out animes without Synopsis
anime_df = anime_df[anime_df['Synopsis'] != 'No description available for this anime.']

# Keep only anime_id, Name, Score and Synopsis Columns
anime_df = anime_df[['anime_id', 'English name', 'Score', 'Synopsis']]


