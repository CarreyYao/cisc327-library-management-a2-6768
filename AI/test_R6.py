import pytest
import sys
import os

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from library_service import search_books_in_catalog

def test_search_by_title(monkeypatch):
    monkeypatch.setattr("library_service.get_all_books", lambda: [{"title": "Python", "author": "X", "isbn": "111"}])
    results = search_books_in_catalog("python", "title")
    assert len(results) == 1

def test_search_by_author(monkeypatch):
    monkeypatch.setattr("library_service.get_all_books", lambda: [{"title": "B", "author": "Alice", "isbn": "222"}])
    results = search_books_in_catalog("alice", "author")
    assert len(results) == 1

def test_search_by_isbn(monkeypatch):
    monkeypatch.setattr("library_service.get_all_books", lambda: [{"title": "B", "author": "A", "isbn": "333"}])
    results = search_books_in_catalog("333", "isbn")
    assert len(results) == 1

def test_search_empty_term():
    results = search_books_in_catalog("", "title")
    assert results == []

def test_search_no_match(monkeypatch):
    monkeypatch.setattr("library_service.get_all_books", lambda: [{"title": "B", "author": "A", "isbn": "123"}])
    results = search_books_in_catalog("zzz", "title")
    assert results == []
