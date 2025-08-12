from bookstack.conftest import (
    BookStackTestData,
)
from playwright.sync_api import Page
from tracing_api import traced_expect as expect


def test_move_page(created_page_move_page: Page, test_data: BookStackTestData) -> None:
    # Create book, create 1 chapter, create 1 page.
    # Move the page to the chapter.
    page = created_page_move_page

    # Move the page to the chapter.
    page.get_by_role("link", name="Move").click()

    # During tests, we create many instances, for stable test, we will search by name.
    page.locator("#main-content").get_by_role("textbox", name="Search").click()
    page.locator("#main-content").get_by_role("textbox", name="Search").fill(
        test_data.chapter_name
    )
    page.wait_for_timeout(500)  # Wait for search results to load
    page.get_by_role("link", name=test_data.chapter_name).click()
    page.get_by_role("button", name="Move Page").click()

    # Verify the page was moved successfully.
    expect(page.get_by_role("menu")).to_contain_text(test_data.page_name)

    # Check the page's breadcrumb hierarchy.
    expect(page.get_by_label("Breadcrumb")).to_contain_text(test_data.book_name)
    expect(page.get_by_label("Breadcrumb")).to_contain_text(test_data.chapter_name)
    expect(page.get_by_label("Breadcrumb")).to_contain_text(test_data.page_name)

    # Go to chapter and check.
    page.get_by_label("Breadcrumb").get_by_role(
        "link", name=test_data.chapter_name
    ).click()
    expect(page.get_by_role("main")).to_contain_text(test_data.page_name)


def test_move_chapter(
    created_page_move_chapter: Page, test_data: BookStackTestData
) -> None:
    # Create 2 books, create 1 chapter in each book.
    # Move the chapter from book 1 to book 2.
    page = created_page_move_chapter

    # Move the chapter from book 2 to book 1.
    page.get_by_role("link", name="Move").click()

    # During tests, we create many instances, for stable test, we will search by name.
    page.locator("#main-content").get_by_role("textbox", name="Search").click()
    page.locator("#main-content").get_by_role("textbox", name="Search").fill(
        test_data.book_name1
    )
    page.wait_for_timeout(1000)  # Wait for search results to load

    page.get_by_role("link", name=test_data.book_name1).click()
    page.get_by_role("button", name="Move Chapter").click()

    # Go to book & verify the chapter was moved successfully.
    page.get_by_role("link", name="Books", exact=True).first.click()

    # Choose from the "Recently Viewed" list, as the full list may not include the book
    # when there are many records requiring pagination.
    page.locator("#recents").get_by_role("link", name=test_data.book_name1).click()

    expect(page.get_by_role("main")).to_contain_text(test_data.chapter_name1)
    expect(page.get_by_role("main")).to_contain_text(test_data.chapter_name2)
