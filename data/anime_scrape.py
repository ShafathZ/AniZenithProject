import json
import time
from typing import List, Dict

import pandas as pd
import requests

from backend.configs import backend_app_config
from backend.mongo.AnimeDocument import AnimeDocument

# Jikan is a web scraping REST API for anime data, but not all data can be available (specific anime search 100% uptime)
JIKAN_ENDPOINT = "https://api.jikan.moe/v4/anime"

# MyAnimeList (MAL) is an anime database access REST API service with limited features
MAL_ENDPOINT = "https://api.myanimelist.net/v2/anime/ranking"
MAL_CLIENT_ID = backend_app_config.MAL_CLIENT_ID

# API limits
ANIME_PER_PAGE = 25
JIKAN_RATE_LIMIT = 1.0 # Jikan: (~3 req/sec, 60 req/min)
MAL_RATE_LIMIT = 0.5
MAL_MAX_PER_PAGE = 100

# Used for data cleaning
DEMOGRAPHIC_GENRES = {"Shounen", "Shoujo", "Seinen", "Josei", "Kids", "Demographic", "Shonen", "Shojo"}

def _get_jikan_recommendations(mal_id: int, limit: int = 10) -> Dict[str, int]:
    """Fetch anime user recommendations from Jikan."""
    url = f"{JIKAN_ENDPOINT}/{mal_id}/recommendations"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return {
            entry.get("entry", {}).get("title"): entry.get("votes", 0)
            for entry in data[:limit]
        }
    except Exception:
        return {}

def _normalize_from_mal(item: Dict) -> Dict:
    """Convert MAL API response (node) into a flat dict with required fields for an AnimeDocument."""
    node = item.get("node", item)

    # ----- Data Cleaning -----
    duration = node.get("average_episode_duration")
    age_rating = node.get("rating", "")
    studios = node.get("studios", [])
    publishing_company = studios[0].get("name", "Unknown") if studios else "Unknown"
    synopsis = node.get("synopsis").replace("[Written by MAL Rewrite]", "").strip()

    # Alt titles (in case main is not en)
    alt_titles = node.get("alternative_titles")
    alt_titles.pop("synonyms")

    # Extract genre
    genre_list = [g["name"] for g in node.get("genres", [])]
    genres = [g for g in genre_list if g not in DEMOGRAPHIC_GENRES]
    demographic = next((g for g in genre_list if g in DEMOGRAPHIC_GENRES), "All")

    return {
        "mal_id": node["id"],
        "title": node.get("title"),
        "alt_titles": alt_titles,
        "score": node.get("mean"),
        "synopsis": synopsis,
        "genres": genres,
        "demographic": demographic,
        "cover_image_url": node.get("main_picture").get("medium", ""),
        "date_aired": node.get("start_date"),
        "status": node.get("status", "not_aired"),
        "episode_count": node.get("num_episodes", 0),
        "publishing_company": publishing_company,
        "avg_episode_len_mins": int(duration // 60),
        "age_rating": age_rating.split(" - ")[0] if age_rating else "Unknown",
    }

def _build_documents(mal_items: List[Dict], search_recommended: bool = False) -> List[AnimeDocument]:
    """Convert MAL items into AnimeDocument, enriching with Jikan."""
    results = []

    for raw in mal_items:
        entry = _normalize_from_mal(raw)

        # Fetch recommendations if requested
        recs = []
        if search_recommended:
            time.sleep(JIKAN_RATE_LIMIT)
            recs = _get_jikan_recommendations(entry["mal_id"])

        try:
            results.append(
                AnimeDocument(
                    mal_id=entry["mal_id"],
                    node_name=entry["title"],
                    title=entry["title"],
                    alt_titles=entry["alt_titles"],
                    score=entry["score"],
                    synopsis=entry["synopsis"],
                    genres=entry["genres"],
                    demographic=entry["demographic"],
                    age_rating=entry["age_rating"],
                    cover_image_url=entry["cover_image_url"],
                    date_aired=entry["date_aired"],
                    status=entry["status"],
                    episode_count=entry["episode_count"],
                    avg_episode_len_mins=entry["avg_episode_len_mins"],
                    publishing_company=entry["publishing_company"],
                    recommendations=recs,
                )
            )
        except Exception:
            print(f"[SCRAPE ERR] Failed to append anime: {entry["title"]} ({entry['mal_id']})")

    return results

# Fetch data from MAL
def _fetch_mal_page(ranking_type: str, page: int, limit: int) -> List[Dict]:
    headers = {"X-MAL-CLIENT-ID": MAL_CLIENT_ID}
    params = {
        "ranking_type": ranking_type,
        "limit": limit,
        "offset": (page - 1) * limit,
        "fields": "id,title,alternative_titles,mean,synopsis,genres,main_picture,start_date,status,studios,num_episodes,average_episode_duration,rating",
    }
    resp = requests.get(MAL_ENDPOINT, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json().get("data", [])

# Search API
def search_anime(sort_by: str = "score", n: int = 10, search_recommended: bool = False) -> List[AnimeDocument]:
    """
    Search anime using MAL ranking, then enrich with Jikan.

    Args:
        sort_by: 'score' (top rated) or 'popularity' (most members)
        n: number of results
        search_recommended: if True, fetch recommendations from Jikan per anime
    Returns:
        List[AnimeDocument]
    """
    results = []
    page = 1

    ranking_type = {"score": "all", "popularity": "bypopularity"}.get(sort_by, "all")

    with open("./data/anime_scrape.jsonl", "w", encoding="utf-8") as f:
        while len(results) < n:
            remaining = n - len(results)
            limit = min(MAL_MAX_PER_PAGE, remaining) # Limit in case requesting more data than needed
            print(f"[MAL INFO] Fetching page {page} sorted by {sort_by} (need {remaining} more items, requesting {limit} items)")
            try:
                data = _fetch_mal_page(ranking_type, page, limit)
                documents = _build_documents(data, search_recommended)
                [f.write(json.dumps(doc.model_dump(), ensure_ascii=False) + "\n") for doc in documents]
                results.extend(documents)
                page += 1
                time.sleep(MAL_RATE_LIMIT)
            except Exception as e:
                print(f"[MAL WARN] Page {page} failed: {e}")
                page += 1
                continue

    return results[:n]

if __name__ == "__main__":
    results = search_anime(sort_by="popularity", n=5000, search_recommended=True)

    data = [r.model_dump() for r in results]
    df = pd.DataFrame(data)
    df.to_json("./data/anime.json", orient="records", indent=2, force_ascii=False)
    print(f"Saved {len(df)} records to ./data/anime.json")