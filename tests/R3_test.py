import pytest
import sys
import os
import sqlite3
from unittest.mock import Mock, patch
from datetime import datetime

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import  (
    get_db_connection
)

from library_service import (
    borrow_book_by_patron
)

# Test case 1: Positive test case - borrow book with valid data    
def test_borrow_book_with_valid_data():
    '''
    success, message = borrow_book_by_patron("123456", 1)
    assert success == True
    '''
    # Mock all external dependencies
    mock_book = {
        'id': 1,
        'title': 'Test Book',
        'author': 'Test Author',
        'isbn': '1234567890123',
        'total_copies': 5,
        'available_copies': 3
    }
    
    with patch('library_service.get_book_by_id', return_value=mock_book), \
         patch('library_service.get_patron_borrow_count', return_value=2), \
         patch('library_service.insert_borrow_record', return_value=True), \
         patch('library_service.update_book_availability', return_value=True), \
         patch('library_service.datetime') as mock_datetime:
        
        # Mock current time
        fixed_time = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_time
        
        success, message = borrow_book_by_patron("123456", 1)
        
        assert success == True
        assert "Successfully borrowed" in message
        assert "Test Book" in message
        assert "2023-01-15" in message  # After 14 days

# Test case 2: Negative test case - borrow book with oversized patron ID greater than 6 digits  
def test_borrow_book_with_oversized_patronID():
    success, message = borrow_book_by_patron("1234567", 1)
    assert success == False

# Test case 3: Negative test case - borrow book with undersized patron ID less than 6 digits  
def test_borrow_book_with_undersized_patronID():
    success, message = borrow_book_by_patron("12345", 1)
    assert success == False
    
# Test case 4: Negative test case - borrow book with Non-existent book ID   
def test_borrow_book_with_Nonexistent_bookID():
    success, message = borrow_book_by_patron("123456", 999999)
    assert success == False

# Test case 5: Negative test case - borrow book with invalid book ID   
def test_borrow_book_with_invalid_bookID():
    success, message = borrow_book_by_patron("123456", "abc")
    assert success == False

