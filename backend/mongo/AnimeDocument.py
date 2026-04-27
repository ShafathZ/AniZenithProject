from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict

# Class to Model a typical Anime Document
class AnimeDocument(BaseModel):
    mal_id: int                     # ID of anime on MyAnimeList
    name: str                      # English title of anime
    alt_titles: Dict[str, str]      # { "en": ENGLISH_TITLE, "jp": JAPANESE_TITLE, ...}
    score: float                    # MAL User Mean Score -- Typically 6-10
    synopsis: str                   # Short synopsis of shows, does not contain spoilers beyond first episode
    genres: List[str]               # Genres list not including demographic genre
    demographic: str                # Primary demographic
    age_rating: str                 # g | pg | pg-13 | r | r+ | rx
    cover_image_url: str            # link to MAL image (not CDN)
    date_aired: datetime            # date aired as datetime (YYYY-MM-DD stored, not hr/mins/secs/ms)
    status: str                     # finished_airing | currently_airing | not_aired
    episode_count: int              # number of episodes in the anime
    avg_episode_len_mins: int       # average duration per episode in mins
    publishing_company: str         # publishing company name | Unknown
    recommendations: Dict[str, int] # {"TITLE1":#_OF_RECOMMENDATIONS, "TITLE2":#_OF_RECOMMENDATIONS, ...}
    node_name: str                  # Title of anime (node) -- May not be English, but always matches recommendations title