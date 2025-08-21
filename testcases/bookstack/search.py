from bookstack.conftest import (
    BookStackTestData,
)
from playwright.sync_api import Page
from tracing_api import traced_expect as expect


def test_global_search(
    created_global_search_page: Page, test_data: BookStackTestData
) -> None:
    page = created_global_search_page

    page.get_by_role("textbox", name="Search").click()
    page.get_by_role("textbox", name="Search").fill(f'"{test_data._unique_id}"')

    # Search
    page.locator("#header-search-box-button").click()

    expect(page.locator("#search-system")).to_contain_text(test_data.book_name)
    expect(page.locator("#search-system")).to_contain_text(test_data.chapter_name)

    # Test filters
    page.get_by_role("checkbox", name="Chapter").uncheck()

    page.get_by_role("button", name="Update Search").click()
    expect(page.locator("#search-system")).to_contain_text(test_data.book_name)
    expect(page.locator("#search-system")).not_to_contain_text(test_data.chapter_name)
