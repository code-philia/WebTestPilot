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
    create_chapter_test,
    create_page_test,
    create_shelf_test,
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
def created_book_page(logged_in_page: Page, test_data: BookStackTestData) -> Page:
    logged_in_page = create_book(
        logged_in_page, test_data.book_name, test_data.book_description
    )
    expect(
        logged_in_page.get_by_role("alert").filter(has_text="Book successfully created")
    ).to_be_visible(timeout=1000)

    return logged_in_page


def create_chapter(
    created_book_page: Page, chapter_name: str, chapter_description: str
) -> Page:
    created_book_page.get_by_role("link", name="New Chapter").click()

    # Name
    created_book_page.get_by_role("textbox", name="Name").click()
    created_book_page.get_by_role("textbox", name="Name").fill(chapter_name)

    # Description
    created_book_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.get_by_label("Rich Text Area. Press ALT-0").click()
    created_book_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.get_by_label("Rich Text Area. Press ALT-0").fill(
        chapter_description
    )

    # Tags
    created_book_page.get_by_role("button", name="▸ Chapter Tags").click()
    created_book_page.get_by_role("textbox", name="Tag Name").click()
    created_book_page.get_by_role("textbox", name="Tag Name").fill("Sample Tag")
    created_book_page.locator('input[name="tags[0][value]"]').click()
    created_book_page.locator('input[name="tags[0][value]"]').fill("Sample Tag")

    created_book_page.get_by_role("button", name="Save Chapter").click()
    return created_book_page


@pytest.fixture
def created_chapter_page(created_book_page: Page, test_data: BookStackTestData) -> Page:
    created_chapter_page = create_chapter(
        created_book_page, test_data.chapter_name, test_data.chapter_description
    )
    expect(
        created_chapter_page.get_by_role("alert").filter(
            has_text="Chapter successfully created"
        )
    ).to_be_visible(timeout=1000)

    return created_chapter_page


def create_page(
    created_book_page: Page,
    page_name: str,
    page_description: str,
) -> Page:
    created_book_page.get_by_role("link", name="New Page").first.click()

    # Title
    created_book_page.get_by_role("textbox", name="Page Title").click()
    created_book_page.get_by_role("textbox", name="Page Title").fill(page_name)

    # Content
    created_book_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.get_by_label("Rich Text Area. Press ALT-0").click()
    created_book_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.get_by_label("Rich Text Area. Press ALT-0").fill(page_description)

    created_book_page.get_by_role("button", name="Save Page").click()

    return created_book_page


@pytest.fixture
def created_page_page(created_book_page: Page, test_data: BookStackTestData) -> Page:
    created_page_page = create_page(
        created_book_page, test_data.page_name, test_data.page_description
    )
    expect(
        created_page_page.get_by_role("alert").filter(
            has_text="Page successfully created"
        )
    ).to_be_visible(timeout=1000)

    return created_page_page


def create_shelf(
    logged_in_page: Page,
    shelf_name: str,
    shelf_description: str,
    book_names: list[str],
    book_description: str,
):
    setup_data_for_shelf_create(logged_in_page, book_names, book_description)

    logged_in_page.get_by_role("link", name="Shelves").click()
    logged_in_page.get_by_role("link", name="New Shelf").click()

    # Name & Description
    logged_in_page.get_by_role("textbox", name="Name").fill(shelf_name)
    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_label(
        "Rich Text Area. Press ALT-0"
    ).click()
    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_label(
        "Rich Text Area. Press ALT-0"
    ).fill(shelf_description)

    # Add books to shelf
    for book_name in book_names:
        # Add position to make sure it clicks the button, not the scroll.
        logged_in_page.get_by_role("listitem").filter(
            has_text=book_name
        ).first.get_by_role("button", name="Add").click(position={"x": 0, "y": 0})

    logged_in_page.get_by_role("button", name="Save Shelf").click()
    return logged_in_page


def setup_data_for_shelf_create(
    logged_in_page: Page, book_names: list[str], book_description: str
):
    for book_name in book_names:
        create_book(logged_in_page, book_name, book_description)

    return logged_in_page


@pytest.fixture
def created_sort_rule_page(logged_in_page: Page, test_data: BookStackTestData) -> Page:
    logged_in_page = create_sort_rule(logged_in_page, test_data)
    expect(
        logged_in_page.get_by_role("alert").filter(
            has_text="Sort rule successfully created"
        )
    ).to_be_visible(timeout=1000)

    return logged_in_page


def create_sort_rule(logged_in_page: Page, name: str) -> Page:
    logged_in_page.get_by_role("link", name="Settings", exact=True).click()
    logged_in_page.get_by_role("link", name="Sorting", exact=True).click()
    logged_in_page.get_by_role("link", name="Create Sort Rule", exact=True).click()

    # Name
    logged_in_page.get_by_role("textbox", name="Name").click()
    logged_in_page.get_by_role("textbox", name="Name").fill(name)

    # Sort rule configs
    logged_in_page.get_by_role("listitem").filter(
        has_text="Name - Alphabetical (Asc)"
    ).get_by_role("button").click()
    logged_in_page.get_by_role("listitem").filter(
        has_text="Created Date (Asc)"
    ).get_by_role("button").click()

    logged_in_page.get_by_role("button", name="Save").click()
    return logged_in_page


@pytest.fixture
def created_role_page(logged_in_page: Page, test_data: BookStackTestData) -> Page:
    logged_in_page = create_role(logged_in_page, test_data)
    expect(
        logged_in_page.get_by_role("alert").filter(has_text="Role successfully created")
    ).to_be_visible(timeout=1000)

    return logged_in_page


def create_role(logged_in_page: Page, test_data: BookStackTestData) -> Page:
    # Navigate
    logged_in_page.get_by_role("link", name="Settings").click()
    logged_in_page.get_by_role("link", name="Roles").click()
    logged_in_page.get_by_role("link", name="Create New Role").click()

    # Name
    logged_in_page.get_by_role("textbox", name="Role Name").click()
    logged_in_page.get_by_role("textbox", name="Role Name").fill(test_data.role_name)

    # Description
    logged_in_page.get_by_role("textbox", name="Short Description of Role").click()
    logged_in_page.get_by_role("textbox", name="Short Description of Role").fill(
        test_data.role_description
    )

    # Add permissions to role
    logged_in_page.get_by_text("Manage all book, chapter &").click()

    # Use "toggle all" to select all permissions
    logged_in_page.locator(
        ".item-list-row.flex-container-row.items-center.wrap > .flex.py-s.px-m.min-width-s > .text-small"
    ).first.click()
    logged_in_page.locator(
        "div:nth-child(3) > .flex.py-s.px-m.min-width-s > .text-small"
    ).click()
    logged_in_page.locator(
        "div:nth-child(4) > .flex.py-s.px-m.min-width-s > .text-small"
    ).click()
    logged_in_page.locator(
        "div:nth-child(5) > .flex.py-s.px-m.min-width-s > .text-small"
    ).click()

    logged_in_page.get_by_role("button", name="Save Role").click()
    return logged_in_page


@pytest.fixture
def created_data_for_sort_page(
    logged_in_page: Page, test_data: BookStackTestData
) -> Page:
    return setup_data_for_sort_chapter_and_page(logged_in_page, test_data)


def setup_data_for_sort_chapter_and_page(
    logged_in_page: Page, test_data: BookStackTestData
) -> Page:
    # Create book, create 1 chapter, create 2 pages.
    # Sort the chapter and pages in the chapter.
    create_book_page = create_book(
        logged_in_page, test_data.book_name, test_data.book_description
    )
    chapter_created_page = create_chapter(
        create_book_page, test_data.chapter_name, test_data.chapter_description
    )

    # Go back to book page and create a page.
    chapter_created_page.get_by_role(
        "link", name=test_data.book_name, exact=True
    ).first.click()
    page_created_page = create_page(
        chapter_created_page, test_data.page_name1, test_data.page_description
    )
    chapter_created_page.get_by_role(
        "link", name=test_data.book_name, exact=True
    ).first.click()
    page_created_page = create_page(
        chapter_created_page, test_data.page_name2, test_data.page_description
    )
    return page_created_page


@pytest.fixture
def created_data_template_page(
    logged_in_page: Page, test_data: BookStackTestData
) -> Page:
    return setup_data_for_create_page_template(logged_in_page, test_data)


def setup_data_for_create_page_template(
    logged_in_page: Page, test_data: BookStackTestData
) -> Page:
    created_book_page = create_book(
        logged_in_page, test_data.book_name, test_data.book_description
    )
    created_page_page = create_page(
        created_book_page, test_data.page_name, test_data.page_description
    )

    # Create 1 more page, 1 is a template, 1 uses the template.
    page_template_description = test_data.page_description + " Template"
    created_page_page.get_by_role(
        "link", name=test_data.book_name, exact=True
    ).first.click()
    created_page_page = create_page(
        created_page_page,
        test_data.page_template_name,
        page_template_description,
    )

    return created_page_page


def setup_data_for_page_move_page(
    logged_in_page: Page, test_data: BookStackTestData
) -> Page:
    # Create book, create 1 chapter, create 1 page.
    # Move the page to the chapter.
    create_book_page = create_book(
        logged_in_page, test_data.book_name, test_data.book_description
    )
    chapter_created_page = create_chapter(
        create_book_page, test_data.chapter_name, test_data.chapter_description
    )

    # Go back to book page and create a page.
    chapter_created_page.get_by_role(
        "link", name=test_data.book_name, exact=True
    ).first.click()
    page_created_page = create_page(
        chapter_created_page, test_data.page_name, test_data.page_description
    )
    return page_created_page


@pytest.fixture
def created_page_move_page(logged_in_page: Page, test_data: BookStackTestData) -> Page:
    return setup_data_for_page_move_page(logged_in_page, test_data)


def setup_data_for_page_move_chapter(
    logged_in_page: Page, test_data: BookStackTestData
) -> Page:
    book1_page = create_book(
        logged_in_page, test_data.book_name1, test_data.book_description
    )
    book1_chapter = create_chapter(
        book1_page, test_data.chapter_name1, test_data.chapter_description
    )
    book2_page = create_book(
        book1_chapter, test_data.book_name2, test_data.book_description
    )
    book2_chapter = create_chapter(
        book2_page, test_data.chapter_name2, test_data.chapter_description
    )
    return book2_chapter


@pytest.fixture
def created_page_move_chapter(
    logged_in_page: Page, test_data: BookStackTestData
) -> Page:
    return setup_data_for_page_move_chapter(logged_in_page, test_data)


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
    book.goto(BOOKSTACK_HOST)
    book.get_by_role("link", name="Books", exact=True).click()
    book.locator("h2", has_text=test_data.book_name1).click()
    chapter1 = create_chapter(
        book, test_data.chapter_name1, test_data.chapter_description
    )

    # Create Chapter2 in Book1 (for sorting tests)
    chapter1.goto(BOOKSTACK_HOST)
    chapter1.get_by_role("link", name="Books", exact=True).click()
    chapter1.locator("h2", has_text=test_data.book_name1).click()
    chapter2 = create_chapter(
        chapter1, test_data.chapter_name2, test_data.chapter_description
    )

    # Create Chapter3 in Book2 (for move operations)
    chapter2.goto(BOOKSTACK_HOST)
    chapter2.get_by_role("link", name="Books", exact=True).click()
    chapter2.locator("h2", has_text=test_data.book_name2).click()
    chapter3 = create_chapter(
        chapter2, test_data.chapter_name, test_data.chapter_description
    )

    # Create Chapter4 in Book2 (additional chapter)
    chapter3.goto(BOOKSTACK_HOST)
    chapter3.get_by_role("link", name="Books", exact=True).click()
    chapter3.locator("h2", has_text=test_data.book_name2).click()
    chapter4_page = create_chapter(
        chapter3, test_data.chapter_name, test_data.chapter_description
    )

    # === PAGE CREATION ===
    # Create Page1 in Book1 (basic CRUD)
    navigate_to_book(chapter4_page, test_data.book_name1)
    page1 = create_page(chapter4_page, test_data.page_name1, test_data.page_description)

    # Create Page2 in Book1 (for sorting tests)
    navigate_to_book(page1, test_data.book_name1)
    page2 = create_page(page1, test_data.page_name2, test_data.page_description)

    # Create Page3 in Chapter1 of Book1 (for move operations)
    navigate_to_book(page2, test_data.book_name1)
    page2.get_by_role("link", name=test_data.chapter_name1).first.click()
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
    page5.goto(BOOKSTACK_HOST)
    page5.get_by_role("link", name="Books", exact=True).click()
    page5.locator("h2", has_text=test_data.book_name).click()
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
