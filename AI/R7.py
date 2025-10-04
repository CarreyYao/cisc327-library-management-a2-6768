import pytest
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from library_service import get_patron_status_report

def test_invalid_patron():
    result = get_patron_status_report("12")
    assert "Invalid patron ID" in result["error"]

def test_valid_report(monkeypatch):
    monkeypatch.setattr("library_service.get_patron_borrowed_books", lambda x: [{"book_id": 1, "is_overdue": False}])

    class DummyCursor:
        def fetchall(self): return []  # simulate empty borrow history
    class DummyConn:
        def execute(self, *a, **k): return DummyCursor()
        def close(self): pass

    monkeypatch.setattr("library_service.get_db_connection", lambda: DummyConn())
    result = get_patron_status_report("123456")
    assert "status" in result
    assert result["status"] == "Patron status report generated successfully"

def test_with_overdue(monkeypatch):
    monkeypatch.setattr("library_service.get_patron_borrowed_books", lambda x: [{"book_id": 1, "is_overdue": True}])
    monkeypatch.setattr("library_service.calculate_late_fee_for_book", lambda *a, **k: {"fee_amount": 5.0})

    class DummyCursor:
        def fetchall(self): return []
    class DummyConn:
        def execute(self, *a, **k): return DummyCursor()
        def close(self): pass

    monkeypatch.setattr("library_service.get_db_connection", lambda: DummyConn())
    result = get_patron_status_report("123456")
    assert result["total_late_fees_owed"] == 5.0

def test_history_includes_books(monkeypatch):
    dummy_row = {
        "book_id": 1, "title": "Book", "author": "A",
        "borrow_date": datetime.now().isoformat(),
        "due_date": datetime.now().isoformat(),
        "return_date": datetime.now().isoformat()
    }

    class DummyCursor:
        def fetchall(self): return [dummy_row]
    class DummyConn:
        def execute(self, *a, **k): return DummyCursor()
        def close(self): pass

    monkeypatch.setattr("library_service.get_db_connection", lambda: DummyConn())
    monkeypatch.setattr("library_service.get_patron_borrowed_books", lambda x: [])
    result = get_patron_status_report("123456")
    assert "borrow_history" in result
    assert result["borrow_history"][0]["title"] == "Book"

def test_error_handling(monkeypatch):
    monkeypatch.setattr("library_service.get_db_connection", lambda: 1/0)
    monkeypatch.setattr("library_service.get_patron_borrowed_books", lambda x: [])
    result = get_patron_status_report("123456")
    assert "error" in result
