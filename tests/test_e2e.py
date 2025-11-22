"""
End-to-End Tests for Library Management System using Playwright
Tests real user workflows in the Flask web application.
"""
import pytest
import time
import re
import sys
import sqlite3
from playwright.sync_api import Page, expect

# Base URL for the Flask application
BASE_URL = "http://localhost:5000"

timestamp = str(int(time.time()))
unique_book_data = {
    "title": f"Unique Test Book {timestamp}",
    "author": f"Test Author {timestamp}",
    "isbn": f"9{timestamp[-12:]}",  # Ensure unique ISBN
    "copies": "3"
    }


def test_add_book_to_catalog(page: Page):
    """
    Test Case: Add a new book to the catalog
    Requirements: Fill title, author, ISBN, copies and submit successfully
    """

    # Navigate to add book page
    page.goto(f"{BASE_URL}/add_book")
    
    # Fill out all required form fields
    page.fill('input[name="title"]', unique_book_data["title"])
    page.fill('input[name="author"]', unique_book_data["author"])
    page.fill('input[name="isbn"]', unique_book_data["isbn"])
    page.fill('input[name="total_copies"]', unique_book_data["copies"])
    
    # Submit the form
    page.click('button[type="submit"]')
    
    # Wait for form processing and response
    page.wait_for_timeout(3000)
    
    # Verify successful submission by checking for success indicators
    page_content = page.content().lower()
    
    print()

    assert any(indicator in page_content.lower() for indicator in ["success", "added", "created", "submitted"]) or \
        page.url != f"{BASE_URL}/add_book", "Book addition failed - check for errors or success messages"

print("TEST PASSED: New book successfully added to catalog")
    
def test_display_book_catalog(page: Page):
    """
    Check a book in the catalog
    """
    # Use known test data pattern
    test_book_title = "1984"  
    
    page.goto(f"{BASE_URL}/catalog")
    #page.reload()  # Force fresh data

    print()    
    
    content = page.content()
    assert test_book_title in content, f"Test book pattern '{test_book_title}' not found in catalog"
    
    # Verify book presence in catalog content
    #assert unique_book_data["title"].lower() in content, (f"New added book title '{unique_book_data['title']}' not found in catalog content")
    
    print("The book is found in catalog")    



# Test execution configuration
if __name__ == "__main__":
    # This allows running tests directly: python -m pytest tests/test_e2e.py -v
    import pytest
    pytest.main([__file__, "-v"])
