import sys
from dataclasses import dataclass
from pathlib import Path
from random import randint

import pytest

# from playwright.async_api import Page as AsyncPage
from playwright.sync_api import Page

sys.path.append(str(Path(__file__).parent.parent))

from tracing_api import create_traced_page
from tracing_api import traced_expect as expect
from .utilities import create_book_test,create_chapter_test,create_page_test,create_shelf_test


pytest_plugins = ["pytest_xpath_plugin"]
BOOKSTACK_HOST = "http://localhost:8081/"


@dataclass
class BookStackTestData:
    """
    Thread-safe test data factory for BookStack entities.
    Each instance gets unique identifiers to prevent race conditions.
    """

    def __post_init__(self):
        self._unique_id = ""

    # Book properties
    @property
    def book_name(self) -> str:
        return f"Book"

    @property
    def book_name1(self) -> str:
        return self.book_name + "1"

    @property
    def book_name2(self) -> str:
        return self.book_name + "2"

    @property
    def book_description(self) -> str:
        return "Description"

    @property
    def book_name_updated(self) -> str:
        return f"Book Updated"

    @property
    def book_description_updated(self) -> str:
        return "Description Updated"

    # Chapter properties
    @property
    def chapter_name(self) -> str:
        return f"Chapter"

    @property
    def chapter_name1(self) -> str:
        return self.chapter_name + " 1"

    @property
    def chapter_name2(self) -> str:
        return self.chapter_name + " 2"

    @property
    def chapter_description(self) -> str:
        return "Description"

    @property
    def chapter_name_updated(self) -> str:
        return f"Chapter Updated"

    @property
    def chapter_description_updated(self) -> str:
        return "Description Updated"

    # Page properties
    @property
    def page_name(self) -> str:
        return f"Page"

    @property
    def page_name1(self) -> str:
        return self.page_name + " 1"

    @property
    def page_name2(self) -> str:
        return self.page_name + " 2"

    @property
    def page_description(self) -> str:
        return "Page Description"

    @property
    def page_name_updated(self) -> str:
        return f"Page Updated"

    # Page template properties
    @property
    def page_template_name(self) -> str:
        return self.page_name + " Template"

    @property
    def page_template_description(self) -> str:
        return self.page_description + " Template"

    @property
    def page_description_updated(self) -> str:
        return "Page Description Updated"

    # Shelf properties
    @property
    def shelf_name(self) -> str:
        return f"Shelf"

    @property
    def shelf_description(self) -> str:
        return "Shelf Description"

    @property
    def shelf_name_updated(self) -> str:
        return f"Shelf Updated"

    @property
    def shelf_description_updated(self) -> str:
        return "Shelf Description Updated"

    # Sort rule properties
    @property
    def sort_rule_name(self) -> str:
        return f"Rule"

    @property
    def sort_rule_name_updated(self) -> str:
        return f"Rule updated"

    @property
    def role_name(self) -> str:
        return f"Role"

    @property
    def role_description(self) -> str:
        return f"Role description"


@pytest.fixture
def test_data() -> BookStackTestData:
    """Provides fresh, unique test data for each test"""
    return BookStackTestData()


def go_to_bookstack(page: Page) -> Page:
    page.set_viewport_size({"width": 1280, "height": 720})
    page.goto(BOOKSTACK_HOST)
    return page


def login_to_bookstack(page: Page) -> Page:
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
    expect(
        created_page_page.get_by_role("alert").filter(
            has_text="Page successfully created"
        )
    ).to_be_visible(timeout=1000)

    return created_page_page


@pytest.fixture
def created_shelf_page(logged_in_page: Page, test_data: BookStackTestData) -> Page:
    logged_in_page = create_shelf(
        logged_in_page,
        test_data.shelf_name,
        test_data.shelf_description,
        [test_data.book_name1, test_data.book_name2],
        test_data.book_description,
    )
    expect(
        logged_in_page.get_by_role("alert").filter(
            has_text="Shelf successfully created"
        )
    ).to_be_visible(timeout=1000)
    expect(logged_in_page.get_by_role("main")).to_contain_text(test_data.book_name1)
    expect(logged_in_page.get_by_role("main")).to_contain_text(test_data.book_name2)

    return logged_in_page


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


def create_sort_rule(logged_in_page: Page, test_data: BookStackTestData) -> Page:
    logged_in_page.get_by_role("link", name="Settings", exact=True).click()
    logged_in_page.get_by_role("link", name="Sorting", exact=True).click()
    logged_in_page.get_by_role("link", name="Create Sort Rule", exact=True).click()

    # Name
    logged_in_page.get_by_role("textbox", name="Name").click()
    logged_in_page.get_by_role("textbox", name="Name").fill(test_data.sort_rule_name)

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
    page_template_description = test_data.page_template_description
    created_page_page.get_by_role(
        "link", name=test_data.book_name, exact=True
    ).first.click()
    created_page_page = create_page(
        created_page_page,
        test_data.page_template_name,
        page_template_description,
    )

    return created_page_page


def setup_data_for_global_search_page(
    logged_in_page: Page, test_data: BookStackTestData
) -> Page:
    created_book_page = create_book(
        logged_in_page, test_data.book_name, test_data.book_description
    )
    created_chapter_page = create_chapter(
        created_book_page, test_data.chapter_name, test_data.chapter_description
    )
    created_chapter_page.goto(BOOKSTACK_HOST)
    return created_chapter_page


@pytest.fixture
def created_global_search_page(
    logged_in_page: Page, test_data: BookStackTestData
) -> Page:
    return setup_data_for_global_search_page(logged_in_page, test_data)


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
def seed(logged_in_page: Page):
    # Seed data is created in individual fixtures as needed.
    # Run this to start seeding: pytest ./bookstack/seed.py::test_seed -v --tb=short -s --headed
    # TODO: Jingyu setup the data.
    data = BookStackTestData()

    # create book1
    logged_in_page = create_book_test(logged_in_page, data.book_name1, data.book_description)
    # create chapter for book1
    logged_in_page = create_chapter_test(
        logged_in_page, data.chapter_name1, data.chapter_description
    )
    # create page for book1
    logged_in_page = create_page_test(logged_in_page, data.page_name1, data.page_description)

    logged_in_page.goto(BOOKSTACK_HOST)
    logged_in_page.wait_for_timeout(1000)

    # create book2
    logged_in_page = create_book_test(logged_in_page, data.book_name2, data.book_description)
    # create chapter for book1
    logged_in_page = create_chapter_test(
        logged_in_page, data.chapter_name2, data.chapter_description
    )
    # create page for book1
    logged_in_page = create_page_test(logged_in_page, data.page_name2, data.page_description)

    logged_in_page.goto(BOOKSTACK_HOST)
    logged_in_page.wait_for_timeout(1000)

    # create shelf
    logged_in_page = create_shelf_test(
        logged_in_page,
        data.shelf_name,
        data.shelf_description,
        [data.book_name1, data.book_name2],
    )
    return logged_in_page
