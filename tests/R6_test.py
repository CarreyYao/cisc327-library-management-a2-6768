import pytest
import sys
import os
import sqlite3
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import  (
    get_db_connection
)

from library_service import (
    search_books_in_catalog
)

# Test case 1: Positive test case - Search by title with exact match
def test_search_books_by_title_exact_match():
    with patch('library_service.get_all_books') as mock_get_all:
        mock_get_all.return_value = [
            {'id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'isbn': '9780743273565'},
            {'id': 2, 'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'isbn': '9780061120084'}
        ]
        results = search_books_in_catalog("The Great Gatsby", "title")
        assert len(results) == 1
        assert results[0]['title'] == 'The Great Gatsby'

# Test case 2: Positive test case - Search by author with partial match (case-insensitive)
def test_search_books_by_author_partial_match():
    with patch('library_service.get_all_books') as mock_get_all:
        mock_get_all.return_value = [
            {'id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'isbn': '9780743273565'},
            {'id': 2, 'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'isbn': '9780061120084'},
            {'id': 3, 'title': 'The Catcher in the Rye', 'author': 'J.D. Salinger', 'isbn': '9780316769488'}
        ]
        
        results = search_books_in_catalog("fitzgerald", "author")
        assert len(results) == 1
        assert "Fitzgerald" in results[0]['author']

# Test case 3: Positive test case - Search by ISBN with exact match
def test_search_books_by_isbn_exact_match():
    with patch('library_service.get_all_books') as mock_get_all:
        mock_get_all.return_value = [
            {'id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'isbn': '9780743273565'},
            {'id': 2, 'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'isbn': '9780061120084'}
        ]
        
        results = search_books_in_catalog("9780061120084", "isbn")
        assert len(results) == 1
        assert results[0]['isbn'] == '9780061120084'

# Test case 4: Negative test case - Empty search term
def test_search_books_empty_search_term():
    with patch('library_service.get_all_books') as mock_get_all:
        mock_get_all.return_value = [
            {'id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'isbn': '9780743273565'}
        ]
        
        results = search_books_in_catalog("", "title")
        assert len(results) == 0

# Test case 5: Negative test case - Invalid search type
def test_search_books_invalid_search_type():
    with patch('library_service.get_all_books') as mock_get_all:
        mock_get_all.return_value = [
            {'id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'isbn': '9780743273565'}
        ]
        
        results = search_books_in_catalog("Gatsby", "invalid_type")
        assert len(results) == 0
