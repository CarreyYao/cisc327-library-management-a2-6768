"""
Playwright
"""
import pytest
from playwright.sync_api import Browser, BrowserContext, Page

@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,  
            slow_mo=500    
        )
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def context(browser: Browser):
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        ignore_https_errors=True
    )
    yield context
    context.close()

@pytest.fixture(scope="function")
def page(context: BrowserContext):
    page = context.new_page()
    yield page
    page.close()
