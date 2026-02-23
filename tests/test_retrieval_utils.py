import json
import sqlite3
from pathlib import Path
import pytest
import backend.retrieval_utils as retrieval_utils
from backend.retrieval_utils import get_recommendations

# Setup Test DB
def _setup_test_db(db_path: str):
    # Setup the DB Connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Create Test Anime Table
    cursor.execute(
        """
        CREATE TABLE Anime (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            score REAL NOT NULL,
            synopsis TEXT
        );
        """
    )

    # Create Test Genre Table
    cursor.execute(
        """
        CREATE TABLE Genre (
            id INTEGER PRIMARY KEY,
            genre_name TEXT NOT NULL
        );
        """
    )

    # Create Test AnimeGenre Table
    cursor.execute(
        """
        CREATE TABLE AnimeGenre (
            anime_id INTEGER NOT NULL,
            genre_id INTEGER NOT NULL
        );
        """
    )

    # Define new values to be inserted in the Anime Table
    anime_rows = [
        (1, "Alpha", 9.1, "Alpha synopsis"),
        (2, "Beta", 8.7, "Beta synopsis"),
        (3, "Gamma", 8.9, "Gamma synopsis"),
        (4, "Delta", 7.5, "Delta synopsis"),
    ]

    # Define new values to be inserted in the Genre Table
    genre_rows = [
        (1, "Action"),
        (2, "Drama"),
        (3, "Comedy"),
    ]

    # Define new values to be inserted in the AnimeGenre Table
    anime_genre_rows = [
        (1, 1), (1, 2),  # Alpha: Action, Drama (2 matches)
        (2, 1),          # Beta: Action (1 match)
        (3, 2),          # Gamma: Drama (1 match)
        (4, 3),          # Delta: Comedy (0 matches for Action/Drama)
    ]

    # Insert into all Tables the defined new values above
    cursor.executemany("INSERT INTO Anime VALUES (?, ?, ?, ?);", anime_rows)
    cursor.executemany("INSERT INTO Genre VALUES (?, ?);", genre_rows)
    cursor.executemany("INSERT INTO AnimeGenre VALUES (?, ?);", anime_genre_rows)

    # Commit all the writes to the DB file
    connection.commit()

    # Close the cursor and the connection
    cursor.close()
    connection.close()


def test_get_recommendations_orders_by_match_count_then_score(tmp_path: Path, 
                                                              monkeypatch: pytest.MonkeyPatch):
    # Setup Test Data and Mocks
    # Construct a temporary path for the Test DB
    db_path = tmp_path / "test.db"

    # Setup the test db
    _setup_test_db(str(db_path))

    # Monkeypatch the DB_PATH variable of retrieval_utils file
    monkeypatch.setattr(retrieval_utils, "DB_PATH", str(db_path))

    # Execute the Method under Test
    result_json = get_recommendations(["Action", "Drama"], limit=3)
    result = json.loads(result_json)

    # Assert on the results
    assert [item["name"] for item in result] == ["Alpha", "Gamma", "Beta"]
    assert result[0]["score"] == 9.1
    assert "description" in result[0]


def test_get_recommendations_respects_limit(tmp_path: Path, 
                                            monkeypatch: pytest.MonkeyPatch):
    # Setup Test Data and Mocks
    # Construct a temporary path for the Test DB
    db_path = tmp_path / "test.db"

    # Setup the test db
    _setup_test_db(str(db_path))

    # Monkeypatch the DB_PATH variable of retrieval_utils file
    monkeypatch.setattr(retrieval_utils, "DB_PATH", str(db_path))

    # Execute the Method under Test
    result_json = get_recommendations(["Action", "Drama"], limit=1)
    result = json.loads(result_json)

    # Assert on the results
    assert len(result) == 1
    assert result[0]["name"] == "Alpha"


def test_get_recommendations_single_genre(tmp_path: Path, 
                                          monkeypatch: pytest.MonkeyPatch):
    # Setup Test Data and Mocks
    # Construct a temporary path for the Test DB
    db_path = tmp_path / "test.db"

    # Setup the test db
    _setup_test_db(db_path)

    # Monkeypatch the DB_PATH variable of retrieval_utils file
    monkeypatch.setattr(retrieval_utils, "DB_PATH", str(db_path))

    # Execute the Method under Test
    result_json = get_recommendations(["Drama"], limit=5)
    result = json.loads(result_json)

    # Assert on the results
    assert [item["name"] for item in result] == ["Alpha", "Gamma"]
    assert all("description" in item for item in result)


def test_get_recommendations_no_genre(tmp_path: Path, 
                                      monkeypatch: pytest.MonkeyPatch):
    # Setup Test Data and Mocks
    # Construct a temporary path for the Test DB
    db_path = tmp_path / "test.db"

    # Setup the test db
    _setup_test_db(db_path)

    # Monkeypatch the DB_PATH variable of retrieval_utils file
    monkeypatch.setattr(retrieval_utils, "DB_PATH", str(db_path))

    # Execute the Method under Test
    result_json = get_recommendations([], limit=5)
    result = json.loads(result_json)

    # Assert on the results
    assert len(result) == 0