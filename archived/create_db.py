import pandas as pd
import sqlite3

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

# Filter out animes without Scores
anime_df = anime_df[anime_df['Score'] != 'UNKNOWN']

# Filter out animes without Synopsis
anime_df = anime_df[anime_df['Synopsis'] != 'No description available for this anime.']

# Sort by Score and Keep only Top 1000 Animes
anime_df = anime_df.sort_values(by='Score', ascending=False)
anime_df = anime_df.head(1000)

# Rename Columns
anime_df = anime_df.rename(columns={'English name': 'name', 'Score': 'score', 'Synopsis': 'synopsis'})




# AnimeGenre Table
# Create a mapping of genre_name to genre_id
genre_mapping = genres_df.set_index('genre_name')['genre_id'].to_dict()

# Explode genres for filtered animes and map to genre_ids
anime_genre_df = anime_df[['anime_id', 'Genres']].copy()
anime_genre_df = anime_genre_df.assign(genre_name=anime_genre_df['Genres'].str.split(', ')).explode('genre_name')
anime_genre_df['genre_name'] = anime_genre_df['genre_name'].str.strip()
anime_genre_df['genre_id'] = anime_genre_df['genre_name'].map(genre_mapping)
anime_genre_df = anime_genre_df[['anime_id', 'genre_id']].dropna()
anime_genre_df['genre_id'] = anime_genre_df['genre_id'].astype(int)



# Final Clean Up
# Keep only anime_id, Name, Score and Synopsis Columns
anime_df = anime_df[['anime_id', 'name', 'score', 'synopsis']]
anime_df = anime_df.rename(columns={'anime_id': 'id'})
genres_df = genres_df.rename(columns={'genre_id': 'id'})


SCHEMA_SQL = '''
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Anime (
  id INTEGER PRIMARY KEY,
  name VARCHAR(50),
  score FLOAT,
  synopsis TEXT
);

CREATE TABLE IF NOT EXISTS Genre (
  id INTEGER PRIMARY KEY,
  genre_name VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS AnimeGenre (
  anime_id INTEGER NOT NULL,
  genre_id INTEGER NOT NULL,
  PRIMARY KEY (anime_id, genre_id),
  FOREIGN KEY (anime_id) REFERENCES Anime(id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (genre_id) REFERENCES Genre(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_anime_id ON AnimeGenre(anime_id);
CREATE INDEX IF NOT EXISTS idx_genre_id ON AnimeGenre(genre_id);
'''

with sqlite3.connect('../data/anime.db') as conn:
    conn.executescript(SCHEMA_SQL)
    anime_df.to_sql('Anime', conn, if_exists='delete_rows', index=False, method='multi')
    genres_df.to_sql('Genre', conn, if_exists='delete_rows', index=False, method='multi')
    anime_genre_df.to_sql('AnimeGenre', conn, if_exists='delete_rows', index=False, method='multi')
