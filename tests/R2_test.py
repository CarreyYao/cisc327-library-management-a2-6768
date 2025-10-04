import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_db_connection
)

from library_service import display_all_book_in_catalog

# Test case 1: Positive test case - Display books with valid data
def test_display_all_books_with_valid_data():

    # Mock get_all_books(), rather than connecting to a real database
    mock_books = [
        {'id': 1, 'title': "Test Book 1", 'author': "Author 1", 'isbn': "1234567890123", 'total_copies': 5, 'available_copies': 3},
        {'id': 2, 'title': "Test Book 2", 'author': "Author 2", 'isbn': "1234567890124", 'total_copies': 2, 'available_copies': 1}
    ]
    
    # Simulate get_all_books() to return mock data
    with patch('library_service.get_all_books', return_value=mock_books):
        result = display_all_book_in_catalog()
        
        # Verify whether the function returns the expected data
        assert result is not None
        assert len(result) == 2
        assert result[0]['title'] == "Test Book 1"
        assert result[1]['author'] == "Author 2"


# Test case 2: Negative test case - Empty catalog
def test_display_all_books_empty_catalog():
    # Mock the database connection and cursor
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock empty database response
    mock_cursor.fetchall.return_value = []
    
    with patch('database.get_db_connection', return_value=mock_conn):
        result = display_all_book_in_catalog()
        
        # Verify the function returns empty list
        assert result == []
        assert len(result) == 0

# Test case 3: Negative test case - Database connection error
def test_display_all_books_database_error():    
    # Mock database connection failure
    with patch('database.get_db_connection', side_effect=Exception("Database connection failed")):
        result = display_all_book_in_catalog()
        
        # Verify whether the function returns an empty list.
        assert result == []
        

# Test case 4: Boundary test case - Large number of books
def test_display_all_books_large_dataset(): 
    # 创建模拟的大型数据集
    mock_books = [
        {
            'id': i,
            'title': f"Book {i}",
            'author': f"Author {i}",
            'isbn': f"1234567890{i:03d}",
            'total_copies': 10,
            'available_copies': 5
        } for i in range(1000)
    ]
    
    with patch('library_service.get_all_books', return_value=mock_books):
        result = display_all_book_in_catalog()
        
        # Verify the function handles large dataset
        assert result is not None
        assert len(result) == 1000
        assert result[999]['id'] == 999
        assert result[0]['title'] == "Book 0"


# Test case 5: Data format test case - Verify all required fields are present
def test_display_all_books_required_fields():   
    # Mock database response with complete data
    mock_data = [
        {
            'book_id': 1, 
            'title': "Test Book", 
            'author': "Test Author", 
            'isbn': "1234567890123", 
            'total_copies': 10, 
            'available_copies': 7
        }
    ]
    
    with patch('library_service.get_all_books', return_value=mock_data):
        result = display_all_book_in_catalog()
        
        # Verify all required fields are present in the result
        assert 'book_id' in result[0]
        assert 'title' in result[0]
        assert 'author' in result[0]
        assert 'isbn' in result[0]
        assert 'total_copies' in result[0]
        assert 'available_copies' in result[0]
        
        # Verify data types
        assert isinstance(result[0]['book_id'], int)
        assert isinstance(result[0]['title'], str)
        assert isinstance(result[0]['author'], str)
        assert isinstance(result[0]['isbn'], str)
        assert isinstance(result[0]['total_copies'], int)
        assert isinstance(result[0]['available_copies'], int)
