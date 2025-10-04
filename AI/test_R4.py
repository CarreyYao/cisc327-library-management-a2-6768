import pytest
import sys
import os

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from library_service import return_book_by_patron

def test_valid_return(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_id", lambda x: {"id": x, "title": "Book"})
    monkeypatch.setattr("library_service.update_borrow_record_return_date", lambda *a, **k: True)
    monkeypatch.setattr("library_service.update_book_availability", lambda *a, **k: True)
    monkeypatch.setattr("library_service.calculate_late_fee_for_book", lambda *a, **k: {"fee_amount": 0, "days_overdue": 0})
    success, msg = return_book_by_patron("123456", 1)
    assert success is True
    assert "returned successfully" in msg

def test_invalid_patron():
    success, msg = return_book_by_patron("12", 1)
    assert success is False
    assert "Invalid patron ID" in msg

def test_book_not_found(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_id", lambda x: None)
    success, msg = return_book_by_patron("123456", 1)
    assert success is False
    assert "Book not found" in msg

def test_no_active_borrow(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_id", lambda x: {"title": "Book"})
    monkeypatch.setattr("library_service.update_borrow_record_return_date", lambda *a, **k: False)
    success, msg = return_book_by_patron("123456", 1)
    assert success is False
    assert "No active borrow record" in msg

def test_late_fee(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_id", lambda x: {"title": "Book"})
    monkeypatch.setattr("library_service.update_borrow_record_return_date", lambda *a, **k: True)
    monkeypatch.setattr("library_service.update_book_availability", lambda *a, **k: True)
    monkeypatch.setattr("library_service.calculate_late_fee_for_book", lambda *a, **k: {"fee_amount": 5.0, "days_overdue": 3})
    success, msg = return_book_by_patron("123456", 1)
    assert "Late fee" in msg
