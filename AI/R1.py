
import pytest
import sys
import os
import sqlite3

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from library_service import add_book_to_catalog

def test_add_valid_book(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_isbn", lambda x: None)
    monkeypatch.setattr("library_service.insert_book", lambda *args, **kwargs: True)
    success, msg = add_book_to_catalog("Valid Title", "Author", "1234567890123", 3)
    assert success is True
    assert "successfully added" in msg

def test_missing_title():
    success, msg = add_book_to_catalog("", "Author", "1234567890123", 3)
    assert success is False
    assert "Title is required" in msg

def test_long_title():
    long_title = "A" * 201
    success, msg = add_book_to_catalog(long_title, "Author", "1234567890123", 3)
    assert success is False
    assert "less than 200" in msg

def test_duplicate_isbn(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_isbn", lambda x: {"isbn": x})
    success, msg = add_book_to_catalog("Title", "Author", "1234567890123", 3)
    assert success is False
    assert "already exists" in msg

def test_invalid_copies():
    success, msg = add_book_to_catalog("Title", "Author", "1234567890123", -1)
    assert success is False
    assert "positive integer" in msg
