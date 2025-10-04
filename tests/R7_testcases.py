import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import sys
import os
import sqlite3

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from library_service import get_patron_status_report, calculate_late_fee_for_book

def test_get_patron_status_report_valid_patron():
    """Status Report on Testing Valid patron ID"""
    # Data returned by the simulated database
    mock_currently_borrowed = [
        {
            'book_id': 1,
            'title': 'Test Book 1',
            'author': 'Author 1',
            'due_date': (datetime.now() + timedelta(days=7)).isoformat(),
            'is_overdue': False
        }
    ]

    # Simulated borrow History
    mock_borrow_history = [
        {
            'book_id': 2,
            'title': 'History Book',
            'author': 'History Author',
            'borrow_date': (datetime.now() - timedelta(days=30)).isoformat(),
            'due_date': (datetime.now() - timedelta(days=16)).isoformat(),
            'return_date': (datetime.now() - timedelta(days=15)).isoformat()
        }
    ]

    with patch('library_service.get_patron_borrowed_books', return_value=mock_currently_borrowed), \
         patch('library_service.get_db_connection') as mock_db_conn, \
         patch('library_service.calculate_late_fee_for_book', return_value={'fee_amount': 0.0}), \
         patch('library_service.get_patron_status_report') as mock_report:
        
        mock_report.return_value = {
            'patron_id': "123456",
            'currently_borrowed': mock_currently_borrowed,
            'total_books_borrowed': len(mock_currently_borrowed),
            'total_late_fees_owed': 0.0,
            'borrow_history': mock_borrow_history,
            'status': 'Patron status report generated successfully'
        }
        
        result = get_patron_status_report("123456")
        
        assert result['patron_id'] == "123456"
        assert len(result['currently_borrowed']) == 1
        assert result['total_books_borrowed'] == 1
        assert result['total_late_fees_owed'] == 0.0   


def test_get_patron_status_report_invalid_patron_id():
    """Testing Invalid patron ID"""
    test_cases = [
        ("123", "two short"),
        ("1234567", "too long"),
        ("abc123", "Containing Letters"),
        ("", "Empty String"),
        (None, "None value")
    ]
    
    for patron_id, description in test_cases:
        result = get_patron_status_report(patron_id)
        assert 'error' in result
        assert 'Invalid patron ID' in result['error']

def test_get_patron_status_report_no_borrowed_books():
    """Testing Readers with No borrowing Records"""
    with patch('library_service.get_patron_borrowed_books', return_value=[]), \
         patch('library_service.get_db_connection') as mock_db_conn:
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []  
        
        result = get_patron_status_report("123456")
        
        assert result['patron_id'] == "123456"
        assert result['currently_borrowed'] == []
        assert result['total_books_borrowed'] == 0
        assert result['borrow_history'] == []
        assert result['total_late_fees_owed'] == 0.0

def test_get_patron_status_report_with_late_fees():
    """Testing the Status of Readers with Overdue fee"""
    mock_currently_borrowed = [
        {
            'book_id': 1,
            'title': 'Overdue Book',
            'author': 'Test Author',
            'due_date': datetime.now() - timedelta(days=5),
            'is_overdue': True
        }
    ]
    
    with patch('library_service.get_patron_borrowed_books', return_value=mock_currently_borrowed), \
         patch('library_service.get_db_connection') as mock_db_conn, \
         patch('library_service.calculate_late_fee_for_book') as mock_late_fee:
        
        mock_late_fee.return_value = {'fee_amount': 2.50}
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        result = get_patron_status_report("123456")
        
        assert result['total_late_fees_owed'] == 2.50
        assert result['currently_borrowed'][0]['is_overdue'] == True

def test_get_patron_status_report_database_error():
    """Testing Database Error Handling"""
    with patch('library_service.get_patron_borrowed_books', side_effect=Exception("Database connection failed")):
        result = get_patron_status_report("123456")
        
        assert 'error' in result
        assert 'Database connection failed' in result['error']
        assert result['patron_id'] == "123456"

