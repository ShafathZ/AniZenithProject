from sentence_transformers import SentenceTransformer
from typing import List, Tuple

def create_text_metadata_and_embedding(
        embedding_model: SentenceTransformer,
        anime_name: str,
        anime_genres: List[str],
        anime_synopsis: str
    ) -> Tuple[str, List]:
    # Create text_metadata field using synopsis, genres and name
    text_metadata = f"Synopsis: {anime_synopsis}\n\nGenres: {', '.join(anime_genres)}\n\nName: {anime_name}"
    
    # Create embedding for the text_metadata field
    text_metadata_embedding = embedding_model.encode(text_metadata).tolist()

    return text_metadata, text_metadata_embedding