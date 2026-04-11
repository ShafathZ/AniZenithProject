from pydantic import BaseModel
from typing import List

# Class to Model a typical Anime Document
class AnimeDocument(BaseModel):
    name: str
    score: float
    synopsis: str
    genres: List[str]