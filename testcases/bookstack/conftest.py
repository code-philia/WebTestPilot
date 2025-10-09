import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

# from playwright.async_api import Page as AsyncPage
from playwright.sync_api import Page

sys.path.append(str(Path(__file__).parent.parent))

from tracing_api import TracedPage, create_traced_page
from tracing_api import traced_expect as expect

from .utilities import (
    create_book,
    create_chapter,
    create_page,
    create_role,
    create_shelf,
    create_sort_rule,
    navigate_to_book,
)

pytest_plugins = ["pytest_xpath_plugin"]
BOOKSTACK_HOST = "http://localhost:8081/"


@dataclass
class BookStackTestData:
    """
    Thread-safe test data factory for BookStack entities.
    Each instance gets unique identifiers to prevent race conditions.
    """

    # Book properties
    book_name: str = "Book"
    book_name1: str = "Book1"
    book_name2: str = "Book2"
    book_description: str = "Description"
    book_name_updated: str = "Book Updated"
    book_description_updated: str = "Description Updated"

    # Chapter properties
    chapter_name: str = "Chapter"
    chapter_name_new: str = "Chapter New"
    chapter_name1: str = "Chapter 1"
    chapter_name2: str = "Chapter 2"
    chapter_description: str = "Description"
    chapter_name_updated: str = "Chapter Updated"
    chapter_description_updated: str = "Description Updated"

    # Page properties
    page_name: str = "Page"
    page_name1: str = "Page 1"
    page_name2: str = "Page 2"
    page_description: str = "Page Description"
    page_name_updated: str = "Page Updated"
    page_description_updated: str = "Page Description Updated"

    # Page template properties
    page_template_name: str = "Page Template"
    page_template_description: str = "Page Description Template"

    # Shelf properties
    shelf_name: str = "Shelf"
    shelf_description: str = "Shelf Description"
    shelf_name_updated: str = "Shelf Updated"
    shelf_description_updated: str = "Shelf Description Updated"

    # Sort rule properties
    sort_rule_name: str = "Rule"
    sort_rule_name_new: str = "Rule New"
    sort_rule_name_updated: str = "Rule updated"

    # Role properties
    role_name: str = "Role"
    role_description: str = "Role description"


@pytest.fixture
def test_data() -> BookStackTestData:
    """Provides fresh, unique test data for each test"""
    return BookStackTestData()


def go_to_bookstack(page: Page | TracedPage) -> Page | TracedPage:
    page.goto(BOOKSTACK_HOST)
    return page


def login_to_bookstack(page: Page | TracedPage) -> Page | TracedPage:
    """
    Login to BookStack and return a traced page.
    Can be used outside of pytest fixtures.

    Args:
        page: A Playwright page object

    Returns:
        Page: A traced page object with user logged in
    """
    page = go_to_bookstack(page)

    # Perform login
    page.get_by_role("link", name="Log in").click()

    page.get_by_role("textbox", name="Email").click()
    page.get_by_role("textbox", name="Email").fill("admin@admin.com")
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill("password")
    page.get_by_role("button", name="Log In").click()

    # Verify login was successful by checking for Books link
    expect(page.get_by_role("link", name="Books", exact=True)).to_be_visible()

    return page


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """
    Fixture that provides a page with user already logged in to BookStack demo.
    Optionally wraps with tracing based on environment variable.

    Returns:
        Page: A Playwright page object with user logged in (possibly traced)
    """
    traced_page = create_traced_page(page)
    return login_to_bookstack(traced_page)


@pytest.fixture
def seed(logged_in_page: Page, test_data: BookStackTestData) -> Page:
    """
    Comprehensive seed function that creates all necessary test data for BookStack test suite.
    Creates 3 books, 4 chapters, 6 pages, 1 shelf, 1 sort rule, 1 role, and 2 page templates.
    """

    # === BOOK CREATION ===
    # Create Book1 - Primary book with multiple chapters and pages
    book1 = create_book(
        logged_in_page, test_data.book_name1, test_data.book_description
    )

    # Create Book2 - Secondary book for move operations and shelf assignments
    book2 = create_book(book1, test_data.book_name2, test_data.book_description)

    # Create Book - Additional book for complex scenarios
    book = create_book(book2, test_data.book_name, test_data.book_description)

    # === CHAPTER CREATION ===
    # Create Chapter1 in Book1
    navigate_to_book(book, test_data.book_name)
    chapter1 = create_chapter(
        book, test_data.chapter_name, test_data.chapter_description
    )

    # Create Chapter2 in Book1 (for sorting tests)
    navigate_to_book(chapter1, test_data.book_name1)
    chapter2 = create_chapter(
        chapter1, test_data.chapter_name2, test_data.chapter_description
    )

    # Create Chapter3 in Book2 (for move operations)
    navigate_to_book(chapter2, test_data.book_name2)
    chapter3 = create_chapter(
        chapter2, test_data.chapter_name1, test_data.chapter_description
    )
    navigate_to_book(chapter2, test_data.book_name2)
    chapter3 = create_chapter(
        chapter2, test_data.chapter_name2, test_data.chapter_description
    )

    # === PAGE CREATION ===
    # Create Page1 in Book1 (basic CRUD)
    navigate_to_book(chapter3, test_data.book_name1)
    page1 = create_page(chapter3, test_data.page_name1, test_data.page_description)

    # Create Page2 in Book1 (for sorting tests)
    navigate_to_book(page1, test_data.book_name1)
    page2 = create_page(page1, test_data.page_name2, test_data.page_description)

    # Create Page3 in Chapter1 of Book1 (for move operations)
    navigate_to_book(page2, test_data.book_name1)
    page3 = create_page(page2, test_data.page_name, test_data.page_description)

    # Create Page4 in Book2 (cross-book operations)
    navigate_to_book(page3, test_data.book_name2)
    page4 = create_page(page3, test_data.page_name1, test_data.page_description)

    # Create Page5 in Book3 (template page)
    navigate_to_book(page4, test_data.book_name)
    page5 = create_page(
        page4, test_data.page_template_name, test_data.page_template_description
    )

    # Create Page6 in Book3 (template user page)
    navigate_to_book(page5, test_data.book_name)
    page6 = create_page(page5, test_data.page_name, test_data.page_description)

    # === SHELF CREATION ===
    # Create shelf with Book1 and Book2 assigned
    shelf_page = create_shelf(
        page6,
        test_data.shelf_name,
        test_data.shelf_description,
        [test_data.book_name1, test_data.book_name2],
        test_data.book_description,
    )

    # === SORT RULE CREATION ===
    # Create sort rule for sorting tests
    sort_rule_page = create_sort_rule(shelf_page, test_data.sort_rule_name)

    # === ROLE CREATION ===
    # Create role with permissions for permission tests
    role_page = create_role(sort_rule_page, test_data)

    # Return to home page and wait for stability
    role_page.goto(BOOKSTACK_HOST)
    role_page.wait_for_timeout(1000)

    return role_page
