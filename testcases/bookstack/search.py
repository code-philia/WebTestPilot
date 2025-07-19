from playwright.sync_api import Page, expect

from bookstack.conftest import (
    BOOKSTACK_HOST,
    BookStackTestData,
)


def test_global_search(created_chapter_page: Page, test_data: BookStackTestData) -> None:
    created_chapter_page.goto(BOOKSTACK_HOST)

    created_chapter_page.get_by_role("textbox", name="Search").click()
    created_chapter_page.get_by_role("textbox", name="Search").fill(
        f'"{test_data._unique_id}"'
    )

    # Shows chapter and book in the pop-up
    expect(
        created_chapter_page.locator("#header").get_by_role(
            "link", name=test_data.book_name, exact=True
        )
    ).to_be_visible(timeout=1000)
    expect(
        created_chapter_page.locator("#header").get_by_role(
            "link", name=test_data.chapter_name
        )
    ).to_be_visible(timeout=1000)

    # See list page
    created_chapter_page.get_by_role("button", name="View All").click()

    expect(created_chapter_page.locator("#search-system")).to_contain_text(
        test_data.book_name
    )
    expect(created_chapter_page.locator("#search-system")).to_contain_text(
        test_data.chapter_name
    )

    # Test filters
    created_chapter_page.get_by_role("checkbox", name="Chapter").uncheck()

    created_chapter_page.get_by_role("button", name="Update Search").click()
    expect(created_chapter_page.locator("#search-system")).to_contain_text(
        test_data.book_name
    )
    expect(created_chapter_page.locator("#search-system")).not_to_contain_text(
        test_data.chapter_name
    )
