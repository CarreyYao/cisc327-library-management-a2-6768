import pytest
import sys
import os

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from library_service import display_all_book_in_catalog

def test_display_books_success(monkeypatch):
    monkeypatch.setattr("library_service.get_all_books", lambda: [{"title": "Book1"}])
    books = display_all_book_in_catalog()
    assert len(books) == 1
    assert books[0]["title"] == "Book1"

def test_display_books_empty(monkeypatch):
    monkeypatch.setattr("library_service.get_all_books", lambda: [])
    books = display_all_book_in_catalog()
    assert books == []

def test_display_books_exception(monkeypatch):
    monkeypatch.setattr("library_service.get_all_books", lambda: 1/0)
    books = display_all_book_in_catalog()
    assert books == []

def test_display_books_multiple(monkeypatch):
    monkeypatch.setattr("library_service.get_all_books", lambda: [{"title": "B1"}, {"title": "B2"}])
    books = display_all_book_in_catalog()
    assert len(books) == 2

def test_display_books_type(monkeypatch):
    monkeypatch.setattr("library_service.get_all_books", lambda: [{"title": "B1"}])
    books = display_all_book_in_catalog()
    assert isinstance(books, list)
