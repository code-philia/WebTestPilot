from playwright.sync_api import Page
from tracing_api import traced_expect as expect

from bookstack.conftest import BOOKSTACK_HOST, BookStackTestData


def test_create_book(created_book_page: Page, test_data: BookStackTestData) -> None:
    expect(
        created_book_page.get_by_role("heading", name=test_data.book_name)
    ).to_be_visible()
    expect(created_book_page.get_by_text(test_data.book_description)).to_be_visible()


def test_read_book(created_book_page: Page, test_data: BookStackTestData) -> None:
    created_book_page.goto(BOOKSTACK_HOST)
    created_book_page.get_by_role("link", name="Books", exact=True).click()
    created_book_page.locator("h2", has_text=test_data.book_name).click()
    expect(created_book_page.locator("h1")).to_contain_text(test_data.book_name)


def test_update_book(created_book_page: Page, test_data: BookStackTestData) -> None:
    # For test reliability, create a new book then update it
    created_book_page.get_by_role("link", name="Edit").click()

    created_book_page.get_by_role("textbox", name="Name").click()
    created_book_page.get_by_role("textbox", name="Name").fill(
        test_data.book_name_updated
    )

    created_book_page.locator('iframe[title="Rich Text Area"]').click()
    created_book_page.keyboard.type(test_data.book_description_updated)

    created_book_page.get_by_role("button", name="Save Book").click()

    # Check content of the book page
    expect(
        created_book_page.get_by_role("alert").filter(
            has_text="Book successfully updated"
        )
    ).to_be_visible(timeout=1000)
    expect(created_book_page.locator("h1")).to_contain_text(test_data.book_name_updated)
    expect(created_book_page.get_by_role("main")).to_contain_text(
        test_data.book_description_updated
    )


def test_delete_book(created_book_page: Page) -> None:
    # For test reliability, create a new book then delete it
    created_book_page.get_by_role("link", name="Delete").click()
    created_book_page.get_by_role("button", name="Confirm").click()

    expect(
        created_book_page.get_by_role("alert").filter(
            has_text="Book successfully deleted"
        )
    ).to_be_visible()
