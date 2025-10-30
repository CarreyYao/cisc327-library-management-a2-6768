import pytest
import sys
import os
import sqlite3
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta


# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from library_service import (
    return_book_by_patron, borrow_book_by_patron, calculate_late_fee_for_book
)

def test_calculate_late_fee_no_borrow_record():
    """When there is no borrowing record in the test, 0 fee and the correct status shall be returned."""
    # It is intended that get_patron_borrowed_books returns an empty list (no borrowing records).
    with patch('library_service.get_patron_borrowed_books') as mock_get_books:
        mock_get_books.return_value = []  
        
        result = calculate_late_fee_for_book("999999", 4)
        
        assert result['fee_amount'] == 0.00
        assert result['days_overdue'] == 0
        assert 'No active borrow record found for this book' in result['status']

def test_calculate_late_fee_on_time_return():
    """Testing the calculation of late fees for returning books on time"""
    with patch('library_service.get_patron_borrowed_books') as mock_get_books:
        # Simulating non-overdue borrowing records
        mock_get_books.return_value = [
            {
                'book_id': 1,
                'title': 'Test Book',
                'author': 'Test Author',
                'borrow_date': datetime.now() - timedelta(days=5),
                'due_date': datetime.now() + timedelta(days=9),  # Expires in 9 days
                'is_overdue': False
            }
        ]
        
        result = calculate_late_fee_for_book("111111", 1)
        assert result['fee_amount'] == 0.00
        assert result['days_overdue'] == 0
        assert 'not yet due' in result['status']

def test_calculate_late_fee_three_days_overdue():
    """Testing the calculation of late payment fees for a 3-day overdue period"""
    with patch('library_service.get_patron_borrowed_books') as mock_get_books:
        mock_get_books.return_value = [
            {
                'book_id': 2,
                'title': 'Overdue Book',
                'author': 'Test Author',
                'borrow_date': datetime.now() - timedelta(days=17),
                'due_date': datetime.now() - timedelta(days=3),  # Expired 3 days ago
                'is_overdue': True
            }
        ]
        
        result = calculate_late_fee_for_book("666666", 2)
        assert result['fee_amount'] == 1.50  # 3 days * 0.50 = 1.50
        assert result['days_overdue'] == 3

def test_calculate_maximum_late_fee():
    """Testing calculating the upper limit of late fees"""
    with patch('library_service.get_patron_borrowed_books') as mock_get_books:
        # Simulating borrowing records with a 30-day overdue period
        mock_get_books.return_value = [
            {
                'book_id': 4,
                'title': 'Very Overdue Book',
                'author': 'Test Author',
                'borrow_date': datetime.now() - timedelta(days=44),
                'due_date': datetime.now() - timedelta(days=30),  
                'is_overdue': True
            }
        ]
        
        result = calculate_late_fee_for_book("222222", 4)
        assert result['fee_amount'] == 15.00  
        assert result['days_overdue'] == 30

def test_calculate_late_fee_multiple_books():
    """Testing the accurate calculation of late payment fees for specific books when a patron borrows multiple books"""
    with patch('library_service.get_patron_borrowed_books') as mock_get_books:
        # The simulated reader borrowed 3 books, but only the 2nd book is overdued.
        mock_get_books.return_value = [
            {
                'book_id': 1,
                'title': 'Book 1',
                'author': 'Author 1',
                'borrow_date': datetime.now() - timedelta(days=5),
                'due_date': datetime.now() + timedelta(days=9),
                'is_overdue': False
            },
            {
                'book_id': 2,
                'title': 'Book 2',
                'author': 'Author 2',
                'borrow_date': datetime.now() - timedelta(days=20),
                'due_date': datetime.now() - timedelta(days=6),  # Expired 6 days
                'is_overdue': True
            },
            {
                'book_id': 3,
                'title': 'Book 3',
                'author': 'Author 3',
                'borrow_date': datetime.now() - timedelta(days=10),
                'due_date': datetime.now() + timedelta(days=4),
                'is_overdue': False
            }
        ]
        
        # Only calculate the late fee for the 2nd book
        result = calculate_late_fee_for_book("333333", 2)
        assert result['fee_amount'] == 3.00  
        assert result['days_overdue'] == 6
