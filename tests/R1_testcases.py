import pytest
import sys
import os
import sqlite3

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import  (
    get_db_connection
)

from library_service import (
    add_book_to_catalog
)

# Test case 1: Positive test case - Valid book data    
def test_add_book_with_valid_data():
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
    # Add first book
    success, message = add_book_to_catalog("Memory", "Memory Author", "8888567890215", 3)
    assert success == True
    assert "successfully added" in message.lower()
    # Try to add book with same ISBN
    success, message = add_book_to_catalog("Memory", "Memory Author", "8888567890215", 1)
    assert success == False

# Test case 5: Negative case - Copies must be at least 1
def test_add_book_with_zero_copies():
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890216", 0)
    assert success == False

