import os
from backend.mongodb_utils import AniZenithMongoClient, AnimeDocument
from dotenv import load_dotenv

load_dotenv()

CONN_STRING = os.getenv("ATLAS_URI")
TEST_DB_CLIENT = AniZenithMongoClient(CONN_STRING)


# ┌───────────────────────────────────────────────┐
# │              VECTOR SEARCH TESTS              │
# └───────────────────────────────────────────────┘
def test_perform_vector_search_basic_retrieval():

    # Test User Queries
    test_user_query_1 = "Which anime has the character Saitama?"

    # Test Query 1
    results_1 = TEST_DB_CLIENT.perform_vector_search(test_user_query_1)

    # Assert on the results
    assert isinstance(results_1, list)
    assert len(results_1) == 5


def test_perform_vector_search_basic_retrieval():
    """Test that a basic query returns a list with the default limit (5)."""
    results = TEST_DB_CLIENT.perform_vector_search("Which anime has the character Saitama?")
    
    # Check that it returns a list
    assert isinstance(results, list)

    # Check that it returns exactly the default limit of items (5)
    assert len(results) == 5


def test_perform_vector_search_limit_parameter():
    """Test that the limit parameter is respected."""
    custom_limit = 2
    results = TEST_DB_CLIENT.perform_vector_search("A dark fantasy anime", limit=custom_limit)
    
    assert len(results) == custom_limit


def test_perform_vector_search_document_structure():
    """Test that the projected fields are correct and _id is excluded."""
    results = TEST_DB_CLIENT.perform_vector_search("ninja")
    
    assert len(results) > 0
    top_doc = results[0]
    
    # Check for expected fields
    expected_keys = {"name", "genres", "score", "synopsis", "similarity_score"}
    assert set(top_doc.keys()) == expected_keys
    
    # Ensure _id is excluded as defined in the projection
    assert "_id" not in top_doc
    
    # Check data types
    assert isinstance(top_doc["name"], str)
    assert isinstance(top_doc["similarity_score"], float)


def test_perform_vector_search_relevance():
    """
    Test semantic relevance: A specific query should return the target anime 
    with a relatively high similarity score.
    """
    results = TEST_DB_CLIENT.perform_vector_search("Saitama hero for fun")
    
    # Given the query, "One Punch Man" should ideally be the top result
    top_doc = results[0]
    assert "one punch man" in top_doc["name"].lower()
    
    # The similarity score should exist and be decently high
    assert top_doc["similarity_score"] > 0.5 


def test_perform_vector_search_empty_query():
    """Test how the system handles an empty query."""
    results = TEST_DB_CLIENT.perform_vector_search("")
    
    # Even empty strings get embedded and matched against DB.
    # It shouldn't crash, but it should return results (though arbitrary).
    assert isinstance(results, list)
    assert len(results) > 0



# ┌───────────────────────────────────────────────┐
# │                 ADD ANIME TESTS               │
# └───────────────────────────────────────────────┘
def test_add_anime():
    """Test inserting a new anime document, checking its fields, and cleaning up."""
    
    # Create a dummy AnimeDocument
    test_anime_name = "Test Anime: Super Adventure"
    test_anime = AnimeDocument(
        name=test_anime_name,
        score=9.9,
        synopsis="A completely unique and fake anime created for testing purposes.",
        genres=["Action", "Adventure", "Testing"]
    )
    
    try:
        # Add the anime to the database
        TEST_DB_CLIENT.add_anime(test_anime)
        
        # Verify it was inserted by fetching it back
        query = {"name": test_anime_name}
        results = TEST_DB_CLIENT.execute_mongo_read_query(query)
        
        # Assert the document exists
        assert len(results) >= 1
        inserted_doc = results[0]
        
        # Assert the basic fields match
        assert inserted_doc["name"] == test_anime.name
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
        TEST_DB_CLIENT.anime_collection.delete_many({"name": test_anime_name})



# ┌───────────────────────────────────────────────┐
# │              RUN READ QUERY TESTS             │
# └───────────────────────────────────────────────┘
def test_execute_mongo_read_query_basic():
    """Test that a basic find query works and respects the limit."""
    # An empty dictionary matches all documents
    query = {}
    test_limit = 3
    
    results = TEST_DB_CLIENT.execute_mongo_read_query(query, limit=test_limit)
    
    # Assert it returns a list of the exact limited size
    assert isinstance(results, list)
    assert len(results) == test_limit
    
    # Assert that the items inside are parsed as dictionaries (documents)
    assert isinstance(results[0], dict)
    
    # Assert standard MongoDB fields exist
    assert "_id" in results[0]
    assert "name" in results[0]


def test_execute_mongo_read_query_invalid_input():
    """Test that passing an invalid query format safely returns an empty list."""
    # The method expects a dictionary. Passing a list should trigger the ValueError
    # which is caught in the try-except block, returning an empty list [].
    invalid_query = ["this", "is", "a", "list", "not", "a", "dict"]
    
    results = TEST_DB_CLIENT.execute_mongo_read_query(invalid_query)
    
    assert isinstance(results, list)
    assert len(results) == 0