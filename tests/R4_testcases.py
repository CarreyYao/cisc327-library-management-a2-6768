import pytest
import sys
import os
import sqlite3

from unittest.mock import patch, Mock

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import  (
    get_db_connection
)

from library_service import (
    return_book_by_patron, borrow_book_by_patron
)

# Test case 1: Positive test case - return book with valid data    
def test_return_book_with_valid_data():
    """Test successful book return with valid data"""  
    # Mock book
    mock_book = {
        'id': 4,
        'title': 'Test Book',
        'author': 'Test Author',
        'isbn': '1234567890123',
        'total_copies': 5,
        'available_copies': 3
    }
    
    # Simulate all required functions
    with patch('library_service.get_book_by_id', return_value=mock_book), \
         patch('library_service.update_borrow_record_return_date', return_value=True), \
         patch('library_service.update_book_availability', return_value=True), \
         patch('library_service.calculate_late_fee_for_book') as mock_late_fee:
        
        # Simulate no late fee
        mock_late_fee.return_value = {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'No late fees'
        }
        
        success, message = return_book_by_patron("123456", 4)
        
        assert success == True
        assert "returned successfully" in message
        assert "No late fees" in message
    
# Test case 2: Negative test case - return book with oversized patron ID greater than 6 digits  
def test_return_book_with_oversized_patronID():
    success, message = return_book_by_patron("1234567", 1)
    assert success == False

# Test case 3: Negative test case - return book with undersized patron ID less than 6 digits  
def test_return_book_with_undersized_patronID():
    success, message = return_book_by_patron("12345", 1)
    assert success == False
    
# Test case 4: Negative test case - return book with Non-existent book ID   
def test_return_book_with_Nonexistent_bookID():
    success, message = return_book_by_patron("123456", 999999)
    assert success == False
    
# Test case 5: Negative test case - borrower and returner are not the same person
def test_return_book_with_different_borrower():
    """Test returning a book borrowed by a different patron"""
    
    # Mock book
    mock_book = {
        'id': 2,
        'title': 'Test Book 2',
        'author': 'Author 2',
        'isbn': '1234567890124',
        'total_copies': 3,
        'available_copies': 2
    }
    
    # First call get_book_by_id()- return available book
    # Secod call get_book_by_id()- return the same book
    mock_get_book = Mock()
    mock_get_book.side_effect = [mock_book, mock_book]
    
    # Simulated borrowing success
    with patch('library_service.get_book_by_id', mock_get_book), \
         patch('library_service.get_patron_borrow_count', return_value=2), \
         patch('library_service.insert_borrow_record', return_value=True), \
         patch('library_service.update_book_availability', return_value=True):
        
        # patron id 111111 borrow book
        borrow_success, borrow_message = borrow_book_by_patron("111111", 2)
        assert borrow_success == True
    
    # Simulated book return failure (different borrowers)
    with patch('library_service.get_book_by_id', return_value=mock_book), \
         patch('library_service.update_borrow_record_return_date', return_value=False):
        
        return_success, return_message = return_book_by_patron("123456", 2)
        
        assert return_success == False
        assert "No active borrow record" in return_message
    

    

    
