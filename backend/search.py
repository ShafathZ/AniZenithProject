from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any

from fastapi import Query, APIRouter
from pydantic import BaseModel
from starlette.requests import Request

from backend.mongo.AnimeDocument import AnimeDocument
from backend.utils.model_utils import DB_CLIENT

search_router = APIRouter()

class SearchResponse(BaseModel):
    total_count: int
    shows: List[AnimeDocument]

def get_mongo_query(
    q: Optional[str] = None,
    genre: Optional[List[str]] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    score_min: Optional[float] = None,
    score_max: Optional[float] = None,
    status: Optional[str] = None,
    idx_from: int = 0,
    idx_to: int = 19,
) -> Tuple[Dict[str, Any], int, int]:
    query: Dict[str, Any] = {}

    # Text search
    if q:
        regex = {"$regex": q, "$options": "i"}
        query["$or"] = [
            {"title": regex},
            {"synopsis": regex},
        ]

    # Genre filter
    if genre:
        query["genres"] = {"$in": genre}

    # Year range
    if year_min is not None or year_max is not None:
        year_filter: Dict[str, Any] = {}
        if year_min is not None:
            year_filter["$gte"] = datetime(year_min, 1, 1)
        if year_max is not None:
            year_filter["$lt"] = datetime(year_max + 1, 1, 1)

        if year_filter:
            query["date_aired"] = year_filter

    # Score range
    if score_min is not None or score_max is not None:
        score_filter: Dict[str, Any] = {}
        if score_min is not None:
            score_filter["$gte"] = score_min
        if score_max is not None:
            score_filter["$lte"] = score_max
        if score_filter:
            query["score"] = score_filter

    # Exact status match
    if status:
        query["status"] = status

    # Convert idx_from / idx_to to skip + limit
    skip = idx_from
    limit = max(0, idx_to - idx_from + 1)

    return query, skip, limit

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
    """
    # Calculate how many items to return in this page
    filter_query, skip, limit = get_mongo_query(
        q=q,
        genre=genre,
        year_min=year_min,
        year_max=year_max,
        score_min=score_min,
        score_max=score_max,
        status=status,
        idx_from=idx_from,
        idx_to=idx_to,
    )

    # TODO: Remove count documents as it is expensive
    total_count = DB_CLIENT.anime_collection.count_documents(filter_query)

    # TODO: Convert skip and limit to cursor-based search with $gt
    docs = DB_CLIENT.execute_read_query(query=filter_query, skip=skip, limit=limit)
    shows = [AnimeDocument(**doc) for doc in docs]


    return SearchResponse(
        total_count=total_count,
        shows=shows
    )