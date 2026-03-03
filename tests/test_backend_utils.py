import pytest
import backend.backend_utils as backend_utils


def test_one_genre(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(backend_utils, "GENRE_LIST", ["Action", "Mystery"])
    assert backend_utils.detect_genres("I like Action") == ["Action"]


def test_multiple_genres(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(backend_utils, "GENRE_LIST", ["Action", "Mystery"])
    assert backend_utils.detect_genres("I like Action and Mystery") == ["Action", "Mystery"]


def test_no_genres(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(backend_utils, "GENRE_LIST", ["Action", "Mystery"])
    assert backend_utils.detect_genres("I like Interesting shows") == []

