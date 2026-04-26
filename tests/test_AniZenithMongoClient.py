import os
from backend.mongo.AniZenithMongoClient import AniZenithMongoClient, AnimeDocument
from backend.mongo.AniZenithVectorSearchResult import AniZenithVectorSearchResult
from dotenv import load_dotenv
import pytest

load_dotenv()

@pytest.fixture(scope="module")
def test_db_client():
    CONN_STRING = os.getenv("ATLAS_URI")
    return AniZenithMongoClient(CONN_STRING)

# ┌───────────────────────────────────────────────┐
# │              VECTOR SEARCH TESTS              │
# └───────────────────────────────────────────────┘
def test_perform_vector_search_basic_retrieval(test_db_client: AniZenithMongoClient):
    """Test that a basic query returns a list with the default limit (5)."""
    results = test_db_client.perform_vector_search("Which anime has the character Saitama?")
    
    # Check that it returns a list
    assert isinstance(results, list)

    # Check that it returns exactly the default limit of items (5)
    assert len(results) == 5


def test_perform_vector_search_limit_parameter(test_db_client: AniZenithMongoClient):
    """Test that the limit parameter is respected."""
    custom_limit = 2
    results = test_db_client.perform_vector_search("A dark fantasy anime", limit=custom_limit)
    
    assert len(results) == custom_limit


def test_perform_vector_search_document_structure(test_db_client: AniZenithMongoClient):
    """Test that the projected fields are correct and _id is excluded."""
    results = test_db_client.perform_vector_search("ninja")
    
    assert len(results) > 0
    top_doc = results[0]
    
    # Check that it returned the correct object
    assert isinstance(top_doc, AniZenithVectorSearchResult)
    
    # Assert on the fields of the vector search result object
    assert isinstance(top_doc.title, str)
    assert isinstance(top_doc.similarity_score, float)


def test_perform_vector_search_relevance(test_db_client: AniZenithMongoClient):
    """
    Test semantic relevance: A specific query should return the target anime 
    with a relatively high similarity score.
    """
    results = test_db_client.perform_vector_search("Saitama hero for fun")
    
    top_doc = results[0]
    
    # Assert that one punch man is present in the name
    assert "one punch man" in top_doc.title.lower()
    
    # The similarity score should exist and be decently high
    assert top_doc.similarity_score > 0.5 


def test_perform_vector_search_empty_query(test_db_client: AniZenithMongoClient):
    """Test how the system handles an empty query."""
    results = test_db_client.perform_vector_search("")
    
    # Even empty strings get embedded and matched against DB.
    # It shouldn't crash, but it should return results (though arbitrary).
    assert isinstance(results, list)
    assert len(results) > 0



# ┌───────────────────────────────────────────────┐
# │                 ADD ANIME TESTS               │
# └───────────────────────────────────────────────┘
def test_add_anime(test_db_client: AniZenithMongoClient):
    """Test inserting a new anime document, checking its fields, and cleaning up."""
    
    # Create a dummy AnimeDocument
    test_anime_title = "Test Anime: Super Adventure"

    test_anime = AnimeDocument(
        mal_id=999999,
        title=test_anime_title,
        alt_titles={
            "en": test_anime_title,
        },
        score=9.9,
        synopsis="A completely unique and fake anime created for Testing purposes.",
        genres=[],
        demographic="Shounen",
        age_rating="pg-13",
        cover_image_url="",
        date_aired="2025-01-01",
        status="finished_airing",
        episode_count=1,
        avg_episode_len_mins=1,
        publishing_company="Test Studio",
        recommendations={}
    )
    
    try:
        # Add the anime to the database
        test_db_client.add_anime(test_anime)
        
        # Verify it was inserted by fetching it back
        query = {"title": test_anime_title}
        results = test_db_client.execute_read_query(query)
        
        # Assert the document exists
        assert len(results) >= 1
        inserted_doc = results[0]
        
        # Assert the basic fields match
        assert inserted_doc["title"] == test_anime.title
        assert inserted_doc["score"] == test_anime.score
        assert inserted_doc["synopsis"] == test_anime.synopsis
        assert inserted_doc["genres"] == test_anime.genres
        
        # Assert that the embedding was successfully created and stored as a list
        assert "text_metadata_embedding" in inserted_doc
        assert isinstance(inserted_doc["text_metadata_embedding"], list)
        assert len(inserted_doc["text_metadata_embedding"]) > 0
        
        # Assert the concatenated text_metadata was generated correctly
        assert "Testing" in inserted_doc["text_metadata"]
        
    finally:
        # Clean up - delete the test document so it doesn't pollute the DB
        test_db_client.anime_collection.delete_one({"title": test_anime_title})



# ┌───────────────────────────────────────────────┐
# │              RUN READ QUERY TESTS             │
# └───────────────────────────────────────────────┘
def test_execute_mongo_read_query_basic(test_db_client: AniZenithMongoClient):
    """Test that a basic find query works and respects the limit."""
    # An empty dictionary matches all documents
    query = {}
    test_limit = 3
    
    results = test_db_client.execute_read_query(query, limit=test_limit)
    
    # Assert it returns a list of the exact limited size
    assert isinstance(results, list)
    assert len(results) == test_limit
    
    # Assert that the items inside are parsed as dictionaries (documents)
    assert isinstance(results[0], dict)
    
    # Assert standard MongoDB fields exist
    assert "_id" in results[0]
    assert "title" in results[0]


def test_execute_mongo_read_query_invalid_input(test_db_client: AniZenithMongoClient):
    """Test that passing an invalid query format safely returns an empty list."""
    # The method expects a dictionary. Passing a list should trigger the ValueError
    # which is caught in the try-except block, returning an empty list [].
    invalid_query = ["this", "is", "a", "list", "not", "a", "dict"]
    
    results = test_db_client.execute_read_query(invalid_query)
    
    assert isinstance(results, list)
    assert len(results) == 0