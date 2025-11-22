# playwright.config.py
import pytest
from playwright.sync_api import Playwright

@pytest.fixture(scope="session")
def playwright():
    """Playwright instance for the test session"""
    with Playwright() as playwright:
        yield playwright

@pytest.fixture(scope="session")
def browser(playwright):
    """Browser instance for the test session"""
    browser = playwright.chromium.launch(
        headless=True,  # Set to False for visible browser during development
        slow_mo=1000   # Slow down actions for better visibility when headless=False
    )
    yield browser
    browser.close()

@pytest.fixture(scope="session")
def context(browser):
    """Browser context for the test session"""
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        record_video_dir="videos/" if not True else None  # Enable video recording for debugging
    )
    yield context
    context.close()
