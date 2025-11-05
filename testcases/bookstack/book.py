from bookstack.conftest import BookStackTestData, create_book
from bookstack.utilities import navigate_to_book
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect


def test_create_book(logged_in_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(logged_in_page)

    created_book_page = create_book(
        logged_in_page, test_data.book_name, test_data.book_description
    )
    expect(
        created_book_page.get_by_role("alert").filter(
            has_text="Book successfully created"
        )
    ).to_be_visible(timeout=1000)
    expect(
        created_book_page.get_by_role("heading", name=test_data.book_name)
    ).to_be_visible()
    expect(created_book_page.get_by_text(test_data.book_description)).to_be_visible()


def test_read_book(logged_in_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_book(logged_in_page, test_data.book_name)

    expect(logged_in_page.locator("h1")).to_contain_text(test_data.book_name)


def test_update_book(logged_in_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_book(logged_in_page, test_data.book_name)

    # Update the book
    logged_in_page.get_by_role("link", name="Edit").click()

    logged_in_page.get_by_role("textbox", name="Name").click()
    logged_in_page.get_by_role("textbox", name="Name").fill(test_data.book_name_updated)

    logged_in_page.locator('iframe[title="Rich Text Area"]').click()
    logged_in_page.keyboard.type(test_data.book_description_updated)

    logged_in_page.get_by_role("button", name="Save Book").click()

    # Check content of the book page
    expect(
        logged_in_page.get_by_role("alert").filter(has_text="Book successfully updated")
    ).to_be_visible(timeout=1000)
    expect(logged_in_page.locator("h1")).to_contain_text(test_data.book_name_updated)
    expect(logged_in_page.get_by_role("main")).to_contain_text(
        test_data.book_description_updated
    )


def test_delete_book(logged_in_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_book(logged_in_page, test_data.book_name)

    # Delete the book
    logged_in_page.get_by_role("link", name="Delete").click()
    logged_in_page.get_by_role("button", name="Confirm").click()

    expect(
        logged_in_page.get_by_role("alert").filter(has_text="Book successfully deleted")
    ).to_be_visible()
