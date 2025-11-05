from bookstack.conftest import (
    BookStackTestData,
)
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect


def test_global_search(logged_in_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(logged_in_page)

    logged_in_page.get_by_role("textbox", name="Search").click()
    logged_in_page.get_by_role("textbox", name="Search").fill(
        test_data.book_description
    )

    # Search
    logged_in_page.locator("#header-search-box-button").click()

    expect(logged_in_page.locator("#search-system")).to_contain_text(
        test_data.book_name1
    )
    expect(logged_in_page.locator("#search-system")).to_contain_text(
        test_data.chapter_name1
    )

    # Test filters
    logged_in_page.get_by_role("checkbox", name="Chapter").uncheck()

    logged_in_page.get_by_role("button", name="Update Search").click()
    expect(logged_in_page.locator("#search-system")).to_contain_text(
        test_data.book_name1
    )
    expect(logged_in_page.locator("#search-system")).not_to_contain_text(
        test_data.chapter_name1
    )
