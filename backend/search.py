from typing import List, Optional

from fastapi import Query, APIRouter
from pydantic import BaseModel
from starlette.requests import Request

search_router = APIRouter()

class Anime(BaseModel):
    cover_image_uri: str
    title: str
    genres: List[str]
    short_description: str

class SearchResponse(BaseModel):
    total_count: int
    shows: List[Anime]

PLACEHOLDER_ANIME = Anime(
    cover_image_uri="null",
    title="Placeholder Anime Title",
    genres=["Action", "Comedy"],
    short_description="This is a placeholder description for the anime. It's a fun and exciting show that you will enjoy!"
)

@search_router.get("/anizenith/search")
async def search(
        request: Request,
        q: Optional[str] = Query(None, description="Search query"),
        genre: Optional[List[str]] = Query(None, description="Selected genres"),
        year_min: Optional[int] = Query(None, description="Minimum year"),
        year_max: Optional[int] = Query(None, description="Maximum year"),
        score_min: Optional[float] = Query(None, description="Minimum score"),
        score_max: Optional[float] = Query(None, description="Maximum score"),
        status: Optional[str] = Query(None, description="Anime status"),
        idx_from: int = Query(0, ge=0, description="Starting index (inclusive)"),
        idx_to: int = Query(19, ge=0, description="Ending index (inclusive)")
) -> SearchResponse:
    """
    Search endpoint that returns paginated results.
    TODO: Integrate with real backend DB queries
    """
    # Calculate how many items to return in this page
    total_results = 100
    start = idx_from
    end = min(idx_to + 1, total_results)

    shows = []
    for i in range(start, end):
        show = PLACEHOLDER_ANIME.model_copy()
        show.title = f"Placeholder Anime #{i + 1}"
        shows.append(show)

    return SearchResponse(
        total_count=total_results,
        shows=shows
    )