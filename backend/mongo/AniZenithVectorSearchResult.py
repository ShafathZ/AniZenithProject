from pydantic import BaseModel, Field
from typing import List

# Class to Model a typical AniZenith Vector Search Result Object
class AniZenithVectorSearchResult(BaseModel):
    name: str = Field(..., min_length=1, description="The name of the anime")
    genres: List[str] = Field(default_factory=list, description="List of genres")
    score: float = Field(..., ge=0.0, description="The score of the anime (0 or higher)")
    synopsis: str = Field(..., description="The synopsis of the anime")
    similarity_score: float = Field(..., description="The vector search similarity score")
