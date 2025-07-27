import os
from dataclasses import dataclass
from random import randint

import pytest
from playwright.sync_api import Page
from tracing_api import create_traced_page
from tracing_api import traced_expect as expect

pytest_plugins = ["pytest_xpath_plugin"]


BOOKSTACK_HOST = "http://localhost:8081/"


@dataclass
class BookStackTestData:
    """
    Thread-safe test data factory for BookStack entities.
    Each instance gets unique identifiers to prevent race conditions.
    """

    def __post_init__(self):
        self._unique_id = str(randint(100000, 999999))

    # Book properties
    @property
    def book_name(self) -> str:
        return f"Book{self._unique_id}"

    @property
    def book_description(self) -> str:
        return "Description"

    @property
    def book_name_updated(self) -> str:
        return f"Book Updated {self._unique_id}"

    @property
    def book_description_updated(self) -> str:
        return "Description Updated"

    # Chapter properties
    @property
    def chapter_name(self) -> str:
        return f"Chapter{self._unique_id}"

    @property
    def chapter_description(self) -> str:
        return "Description"

    @property
    def chapter_name_updated(self) -> str:
        return f"Chapter Updated {self._unique_id}"

    @property
    def chapter_description_updated(self) -> str:
        return "Description Updated"

    # Page properties
    @property
    def page_name(self) -> str:
        return f"Page{self._unique_id}"

    @property
    def page_description(self) -> str:
        return "Page Description"

    @property
    def page_name_updated(self) -> str:
        return f"Page Updated {self._unique_id}"

    @property
    def page_description_updated(self) -> str:
        return "Page Description Updated"

    # Shelf properties
    @property
    def shelf_name(self) -> str:
        return f"Shelf{self._unique_id}"

    @property
    def shelf_description(self) -> str:
        return "Shelf Description"

    @property
    def shelf_name_updated(self) -> str:
        return f"Shelf Updated {self._unique_id}"

    @property
    def shelf_description_updated(self) -> str:
        return "Shelf Description Updated"

    # Sort rule properties
    @property
    def sort_rule_name(self) -> str:
        return f"Rule{self._unique_id}"

    @property
    def sort_rule_name_updated(self) -> str:
        return f"Rule updated {self._unique_id}"

    @property
    def role_name(self) -> str:
        return f"Role {self._unique_id}"

    @property
    def role_description(self) -> str:
        return f"Role description {self._unique_id}"


@pytest.fixture
def test_data() -> BookStackTestData:
    """Provides fresh, unique test data for each test"""
    return BookStackTestData()


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """
    Fixture that provides a page with user already logged in to BookStack demo.
    Optionally wraps with tracing based on environment variable.

    Returns:
        Page: A Playwright page object with user logged in (possibly traced)
    """
    # Wrap with tracing if enabled
    traced_page = create_traced_page(page)

    # Navigate to the demo site
    # Change viewport size for better visibility
    traced_page.set_viewport_size({"width": 1280, "height": 720})
    traced_page.goto(BOOKSTACK_HOST)

    # Perform login
    traced_page.get_by_role("link", name="Log in").click()

    traced_page.get_by_role("textbox", name="Email").click()
    traced_page.get_by_role("textbox", name="Email").fill("admin@admin.com")
    traced_page.get_by_role("textbox", name="Password").click()
    traced_page.get_by_role("textbox", name="Password").fill("password")
    traced_page.get_by_role("button", name="Log In").click()

    # Verify login was successful by checking for Books link
    expect(traced_page.get_by_role("link", name="Books", exact=True)).to_be_visible()

    return traced_page


def create_book(logged_in_page: Page, book_name: str, book_description: str) -> Page:
    # To make sure when called multiple times, it starts fresh
    logged_in_page.goto(BOOKSTACK_HOST)

    # Navigate to books and create a new book
    logged_in_page.get_by_role("link", name="Books", exact=True).click()
    expect(logged_in_page.get_by_role("link", name="Create New Book")).to_be_visible()
    logged_in_page.get_by_role("link", name="Create New Book").click()

    # Title and Description
    logged_in_page.get_by_role("textbox", name="Name").click()
    logged_in_page.get_by_role("textbox", name="Name").fill(book_name)
    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_label(
        text="Rich Text Area. Press ALT-0"
    ).click()
    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_label(
        "Rich Text Area. Press ALT-0"
    ).fill(book_description)

    # Cover image
    logged_in_page.get_by_role("button", name="▸ Cover image").click()
    with logged_in_page.expect_file_chooser() as fc_info:
        logged_in_page.get_by_text("Select Image").click()

    file_chooser = fc_info.value
    file_chooser.set_files(os.path.abspath("./assets/minion.jpeg"))

    # Book Tags
    logged_in_page.get_by_role("button", name="▸ Book Tags").click()
    logged_in_page.get_by_role("textbox", name="Tag Name").fill("env")
    logged_in_page.locator('input[name="tags[0][value]"]').fill("test")

    # Save
    logged_in_page.get_by_role("button", name="Save Book").click()

    return logged_in_page


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

    # Check content and visibility
    expect(
        created_page_page.get_by_role("alert").filter(
            has_text="Page successfully created"
        )
    ).to_be_visible(timeout=1000)

    return created_page_page


@pytest.fixture
def created_shelf_page(logged_in_page: Page, test_data: BookStackTestData) -> Page:
    # Setup book data
    create_book(logged_in_page, test_data.book_name + " 1", test_data.book_description)
    create_book(logged_in_page, test_data.book_name + " 2", test_data.book_description)

    logged_in_page.get_by_role("link", name="Shelves").click()
    logged_in_page.get_by_role("link", name="New Shelf").click()

    # Name & Description
    logged_in_page.get_by_role("textbox", name="Name").fill(test_data.shelf_name)
    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_label(
        "Rich Text Area. Press ALT-0"
    ).click()
    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_label(
        "Rich Text Area. Press ALT-0"
    ).fill(test_data.shelf_description)

    # Add books to shelf
    # Add position to make sure it clicks the button, not the scroll.
    logged_in_page.get_by_role("listitem").filter(
        has_text=test_data.book_name + " 1"
    ).first.get_by_role("button", name="Add").click(position={"x": 0, "y": 0})
    logged_in_page.get_by_role("listitem").filter(
        has_text=test_data.book_name + " 2"
    ).first.get_by_role("button", name="Add").click(position={"x": 0, "y": 0})

    # Cover image
    logged_in_page.get_by_role("button", name="▸ Cover image").click()
    logged_in_page.get_by_text("Select Image").click()
    logged_in_page.get_by_role("button", name="Select Image").set_input_files(
        os.path.abspath("./assets/minion.jpeg")
    )

    logged_in_page.get_by_role("button", name="Save Shelf").click()

    # Check content and visibility
    expect(
        logged_in_page.get_by_role("alert").filter(
            has_text="Shelf successfully created"
        )
    ).to_be_visible(timeout=1000)

    expect(logged_in_page.get_by_role("main")).to_contain_text(
        test_data.book_name + " 1"
    )
    expect(logged_in_page.get_by_role("main")).to_contain_text(
        test_data.book_name + " 2"
    )

    return logged_in_page


@pytest.fixture
def created_sort_rule_page(logged_in_page: Page, test_data: BookStackTestData) -> Page:
    logged_in_page.get_by_role("link", name="Settings", exact=True).click()
    logged_in_page.get_by_role("link", name="Sorting", exact=True).click()
    logged_in_page.get_by_role("link", name="Create Sort Rule", exact=True).click()

    # Name
    logged_in_page.get_by_role("textbox", name="Name").click()
    logged_in_page.get_by_role("textbox", name="Name").fill(test_data.sort_rule_name)

    # Sort rule configs
    logged_in_page.get_by_text("Configure the sort actions to").click()
    logged_in_page.get_by_role("listitem").filter(
        has_text="Name - Alphabetical (Asc)"
    ).get_by_role("button").click()
    logged_in_page.get_by_role("listitem").filter(
        has_text="Created Date (Asc)"
    ).get_by_role("button").click()

    logged_in_page.get_by_role("button", name="Save").click()
    expect(
        logged_in_page.get_by_role("alert").filter(
            has_text="Sort rule successfully created"
        )
    ).to_be_visible(timeout=1000)

    return logged_in_page


@pytest.fixture
def created_role_page(logged_in_page: Page, test_data: BookStackTestData) -> Page:
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

    expect(
        logged_in_page.get_by_role("alert").filter(has_text="Role successfully created")
    ).to_be_visible(timeout=1000)

    return logged_in_page
