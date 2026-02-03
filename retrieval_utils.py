import sqlite3
from typing import List, Tuple
import json

# Constants
DB_PATH = "anime.db"

def get_recommendations(requested_genres: List[str], limit: int = 5) -> str:
    # Establish Connection and Cursor
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Prepare placeholders for the SQL Query
    placeholders = ', '.join(['?'] * len(requested_genres))

    # Define SQL Query for the Weighted Ranking Logic
    query = f"""
    -- Project only Anime's name, score, and synopsis
    SELECT 
        A.name,
        A.score,
        A.synopsis
    
    -- From Anime Table
    FROM Anime A

    -- Join Anime Table with AnimeGenre on ids
    JOIN AnimeGenre AG ON A.id = AG.anime_id

    -- Join Genre Table with AnimeGenre on ids
    JOIN Genre G ON AG.genre_id = G.id

    -- Filter by only genre_name which belong in the list of requested genres
    WHERE G.genre_name IN ({placeholders})

    -- Group by Anime id
    GROUP BY A.id

    -- Primary Sort by Count of Matches in the requested_genres list
    -- Secondary Sort by Anime's score
    ORDER BY COUNT(G.id) DESC, A.score DESC

    -- Return only the top 5 matches
    LIMIT ?
    """

    # Execute the Query with the requested genres and the limit
    cursor.execute(query, requested_genres + [limit])

    # Gather the results
    results = cursor.fetchall()

    # Close the Connection
    connection.close()

    # Compose a JSON String from the results and return it
    return jsonify_recommendations(results)


def jsonify_recommendations(recommendations: List[Tuple[str, float, str]]) -> str:
    # Process each anime recommendations into a list of dicts (for easy JSON conversion)
    list_of_dicts = []
    for anime in recommendations:
        list_of_dicts.append({
            'name': anime[0],
            'score': anime[1],
            'description': anime[2]
        })

    # JSONify and return the list of dicts
    return json.dumps(list_of_dicts, indent=4)


# Driver Code
if __name__ == '__main__':
    requested_genres = ["Action", "Drama"]
    recommendations = get_recommendations(requested_genres)
    print(recommendations)