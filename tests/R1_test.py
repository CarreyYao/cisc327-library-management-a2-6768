import pytest
import sys
import os
import sqlite3
from unittest.mock import Mock, patch

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import  (
    get_db_connection
)

from services.library_service import (
    add_book_to_catalog
)

# Test case 1: Positive test case - Valid book data
def test_add_book_with_valid_data():
    with patch('R1_test.add_book_to_catalog', return_value=(True, "Book successfully added")):
        success, message = add_book_to_catalog("Fine Book", "Good Author", "7777567890140", 9)
        
        assert success == True
        assert "successfully added" in message.lower()

# Test case 2: Negative test case - Empty title
def test_add_book_with_empty_title():
    success, message = add_book_to_catalog("", "Test Author", "1234567890102", 3)
    assert success == False
    
# Test case 3: Negative test case - Invalid ISBN format
def test_add_book_invalid_isbn():
    success, message = add_book_to_catalog("Test Book", "Test Author", "invalid-isbn", 5)
    assert success == False
    
# Test case 4: Negative test case - Duplicate ISBN
def test_add_book_duplicate_isbn(): 
    with patch('R1_test.add_book_to_catalog', return_value=(False, "Duplicate ISBN found")):
        success, message = add_book_to_catalog("Memory", "Memory Author", "8888567890215", 3)
        
        assert success == False
        assert "duplicate" in message.lower()

# Test case 5: Negative case - Copies must be at least 1
def test_add_book_with_zero_copies():
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890216", 0)
    assert success == False
    
# Test case 6: Title at maximum length boundary (200 characters)
def test_add_book_with_max_length_title():
    max_length_title = "a" * 200  
    success, message = add_book_to_catalog(max_length_title, "Test Author", "1234567890123", 5)
    
    with patch('services.library_service.get_book_by_isbn') as mock_get_book, \
         patch('services.library_service.insert_book') as mock_insert:
        
        mock_get_book.return_value = None
        mock_insert.return_value = True
        
        success, message = add_book_to_catalog(max_length_title, "Test Author", "1234567890123", 5)
        assert success == True

# Test case 7: Title exceeding maximum length (201 characters)
def test_add_book_with_title_exceeding_max_length():
    long_title = "a" * 201  
    success, message = add_book_to_catalog(long_title, "Test Author", "1234567890123", 5)
    assert success == False
    assert "200 characters" in message

# Test case 8: Author with only whitespace characters
def test_add_book_with_whitespace_only_author():
    success, message = add_book_to_catalog("Test Book", "   ", "1234567890123", 5)
    assert success == False
    assert "Author is required" in message

# Test case 9: Non-integer total_copies
def test_add_book_with_non_integer_copies():
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", "5")
    assert success == False
    assert "positive integer" in message

# Test case 10: Negative total_copies
def test_add_book_with_negative_copies():
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", -1)
    assert success == False
    assert "positive integer" in message

