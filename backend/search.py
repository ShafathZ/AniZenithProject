from datetime import datetime
from typing import List, Optional

from fastapi import Query, APIRouter
from pydantic import BaseModel
from starlette.requests import Request

search_router = APIRouter()

class Anime(BaseModel):
    id: int
    cover_image_url: str
    title: str
    genres: List[str]
    short_description: str
    score: float
    date_added: int

class SearchResponse(BaseModel):
    total_count: int
    shows: List[Anime]

def date_to_millis(date_str: str) -> int:
    dt = datetime.strptime(date_str, "%b %d, %Y")
    return int(dt.timestamp() * 1000)

# TODO: Remove this and hook up to real database
MOCK_ANIME_LIST = [
    Anime(
        id=1,
        cover_image_url="https://cdn.myanimelist.net/images/anime/1223/96541.jpg",
        title="Fullmetal Alchemist: Brotherhood",
        genres=["Action", "Adventure", "Drama", "Fantasy"],
        short_description="Two brothers search for the Philosopher's Stone to restore their bodies after a failed alchemy experiment.",
        date_added=date_to_millis("Apr 5, 2009"),
        score=9.09
    ),
    Anime(
        id=2,
        cover_image_url="https://cdn.myanimelist.net/images/anime/1935/127974.jpg",
        title="Steins;Gate",
        genres=["Sci-Fi", "Thriller", "Drama"],
        short_description="A group of friends accidentally invent a method of sending messages to the past, altering the present.",
        date_added=date_to_millis("Apr 6, 2011"),
        score=9.07
    ),
    Anime(
        id=3,
        cover_image_url="https://cdn.myanimelist.net/images/anime/1337/99013.jpg",
        title="Hunter x Hunter (2011)",
        genres=["Action", "Adventure", "Fantasy"],
        short_description="Gon Freecss aspires to become a Hunter to find his father, meeting friends and facing deadly challenges.",
        date_added=date_to_millis("Oct 2, 2011"),
        score=9.03
    ),
    Anime(
        id=4,
        cover_image_url="https://cdn.myanimelist.net/images/anime/10/73274.jpg",
        title="Gintama",
        genres=["Action", "Comedy", "Sci-Fi"],
        short_description="In an alternate Edo period invaded by aliens, a samurai freelancer takes odd jobs to make ends meet.",
        date_added=date_to_millis("Apr 4, 2006"),
        score=8.94
    ),
    Anime(
        id=5,
        cover_image_url="https://cdn.myanimelist.net/images/anime/1000/110531.jpg",
        title="Attack on Titan Final Season",
        genres=["Action", "Drama", "Fantasy"],
        short_description="The epic conclusion of humanity's battle against the Titans and the truth behind their existence.",
        date_added=date_to_millis("Dec 7, 2020"),
        score=8.79
    ),
    Anime(
        id=6,
        cover_image_url="https://cdn.myanimelist.net/images/anime/1295/106551.jpg",
        title="Kaguya-sama: Love is War",
        genres=["Comedy", "Romance", "School"],
        short_description="Two geniuses at a prestigious academy engage in psychological warfare to make the other confess love first.",
        date_added=date_to_millis("Apr 11, 2020"),
        score=8.41
    ),
    Anime(
        id=7,
        cover_image_url="https://cdn.myanimelist.net/images/anime/1500/103005.jpg",
        title="Vinland Saga",
        genres=["Action", "Adventure", "Drama", "Historical"],
        short_description="A young Viking seeks revenge against his father's killer while navigating a world of war and slavery.",
        date_added=date_to_millis("Jul 7, 2019"),
        score=8.75
    ),
    Anime(
        id=8,
        cover_image_url="https://cdn.myanimelist.net/images/anime/6/86733.jpg",
        title="Made in Abyss",
        genres=["Adventure", "Drama", "Fantasy", "Mystery"],
        short_description="An orphan girl and a robot boy descend into a mysterious, perilous chasm to find her mother.",
        date_added=date_to_millis("Jul 7, 2017"),
        score=8.65
    ),
    Anime(
        id=9,
        cover_image_url="https://cdn.myanimelist.net/images/anime/5/87048.jpg",
        title="Your Name.",
        genres=["Drama", "Romance", "Supernatural"],
        short_description="Two teenagers swap bodies across time and space, leading to a race against fate.",
        date_added=date_to_millis("Aug 26, 2016"),
        score=8.84
    ),
    Anime(
        id=10,
        cover_image_url="https://cdn.myanimelist.net/images/anime/6/79597.jpg",
        title="Spirited Away",
        genres=["Adventure", "Fantasy", "Supernatural"],
        short_description="A young girl becomes trapped in a spirit world and must work in a bathhouse to free herself and her parents.",
        date_added=date_to_millis("Jul 20, 2001"),
        score=8.77
    ),
]

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
    total_results = len(MOCK_ANIME_LIST)
    start = idx_from
    end = min(idx_to + 1, total_results)

    shows = []
    for i in range(start, end):
        show = MOCK_ANIME_LIST[i].model_copy()
        shows.append(show)

    return SearchResponse(
        total_count=total_results,
        shows=shows
    )