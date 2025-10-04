import pytest
import sys
import os

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from library_service import borrow_book_by_patron
from datetime import datetime, timedelta

def test_valid_borrow(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_id", lambda x: {"id": x, "title": "Book1", "available_copies": 1})
    monkeypatch.setattr("library_service.get_patron_borrow_count", lambda x: 2)
    monkeypatch.setattr("library_service.insert_borrow_record", lambda *a, **k: True)
    monkeypatch.setattr("library_service.update_book_availability", lambda *a, **k: True)
    success, msg = borrow_book_by_patron("123456", 1)
    assert success is True
    assert "Successfully borrowed" in msg

def test_invalid_patron_id():
    success, msg = borrow_book_by_patron("abc", 1)
    assert success is False
    assert "Invalid patron ID" in msg

def test_book_not_found(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_id", lambda x: None)
    success, msg = borrow_book_by_patron("123456", 1)
    assert success is False
    assert "Book not found" in msg

def test_no_copies(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_id", lambda x: {"available_copies": 0})
    success, msg = borrow_book_by_patron("123456", 1)
    assert success is False
    assert "not available" in msg

def test_patron_limit(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_id", lambda x: {"available_copies": 1, "title": "Book"})
    monkeypatch.setattr("library_service.get_patron_borrow_count", lambda x: 6)
    success, msg = borrow_book_by_patron("123456", 1)
    assert success is False
    assert "maximum borrowing limit" in msg
