from playwright.sync_api import Page
from tracing_api import traced_expect as expect

from bookstack.conftest import (
    BookStackTestData,
    create_book,
    create_chapter,
    create_page,
)


def test_sort_chapter_book(logged_in_page: Page, test_data: BookStackTestData) -> None:
    # Create book, create 1 chapter, create 2 pages.
    # Sort the chapter and pages in the chapter.
    create_book_page = create_book(
        logged_in_page, test_data.book_name, test_data.book_description
    )
    chapter_created_page = create_chapter(
        create_book_page, test_data.chapter_name, test_data.chapter_description
    )

    # Go back to book page and create a page.
    chapter_created_page.get_by_role("link", name=test_data.book_name).first.click()
    page_created_page = create_page(
        chapter_created_page, test_data.page_name1, test_data.page_description
    )
    chapter_created_page.get_by_role("link", name=test_data.book_name).first.click()
    page_created_page = create_page(
        chapter_created_page, test_data.page_name2, test_data.page_description
    )

    # Go back to book to start sorting.
    page_created_page.get_by_role("link", name=test_data.book_name).first.click()
    page_created_page.get_by_role("link", name="Sort").click()

    page_created_page.get_by_role("button", name="Move Up").first.click()

    # Optionally, pause for a bit to allow user to see the change
    # page_created_page.wait_for_timeout(1000)
    page_created_page.get_by_role("button", name="Move Down").nth(1).click()
    # page_created_page.wait_for_timeout(1000)
    page_created_page.get_by_role("button", name="Move Up").nth(1).click()
    # page_created_page.wait_for_timeout(1000)

    page_created_page.get_by_role("button", name="Save New Order").click()
    expect(
        page_created_page.get_by_role("alert").filter(
            has_text="Book successfully re-sorted"
        )
    ).to_be_visible(timeout=1000)


def test_sort_by_name(logged_in_page: Page, test_data: BookStackTestData) -> None:
    # Create book, create 1 chapter, create 2 pages.
    # Sort the chapter and pages in the chapter.
    create_book_page = create_book(
        logged_in_page, test_data.book_name, test_data.book_description
    )
    chapter_created_page = create_chapter(
        create_book_page, test_data.chapter_name, test_data.chapter_description
    )

    # Go back to book page and create a page.
    chapter_created_page.get_by_role("link", name=test_data.book_name).first.click()
    page_created_page = create_page(
        chapter_created_page, test_data.page_name1, test_data.page_description
    )
    chapter_created_page.get_by_role("link", name=test_data.book_name).first.click()
    page_created_page = create_page(
        chapter_created_page, test_data.page_name2, test_data.page_description
    )

    # Go back to book to start sorting.
    page_created_page.get_by_role("link", name=test_data.book_name).first.click()
    page_created_page.get_by_role("link", name="Sort").click()
    page_created_page.get_by_role("button", name="Sort by Name").first.click()
    page_created_page.get_by_role("button", name="Save New Order").click()
    expect(
        page_created_page.get_by_role("alert").filter(
            has_text="Book successfully re-sorted"
        )
    ).to_be_visible(timeout=1000)


def test_create_sort_rules(
    created_sort_rule_page: Page, test_data: BookStackTestData
) -> None:
    expect(
        created_sort_rule_page.get_by_role("link", name=test_data.sort_rule_name)
    ).to_be_attached()


def test_update_sort_rules(
    created_sort_rule_page: Page, test_data: BookStackTestData
) -> None:
    created_sort_rule_page.get_by_role("link", name=test_data.sort_rule_name).click()
    created_sort_rule_page.get_by_role("textbox", name="Name").click()
    created_sort_rule_page.get_by_role("textbox", name="Name").fill(
        test_data.sort_rule_name_updated
    )

    # Add more rule
    created_sort_rule_page.get_by_role("listitem").filter(
        has_text="Chapters First"
    ).get_by_role("button").click()

    created_sort_rule_page.get_by_role("button", name="Save").click()
    expect(
        created_sort_rule_page.get_by_role("alert").filter(
            has_text="Sort rule successfully updated"
        )
    ).to_be_visible(timeout=1000)

    expect(created_sort_rule_page.locator("#main-content")).to_contain_text(
        test_data.sort_rule_name_updated
    )


def test_delete_sort_rules(
    created_sort_rule_page: Page, test_data: BookStackTestData
) -> None:
    created_sort_rule_page.get_by_role("link", name=test_data.sort_rule_name).click()
    created_sort_rule_page.get_by_role("button", name="Delete").click()

    expect(
        created_sort_rule_page.get_by_role("alert").filter(
            has_text="Sort rule successfully deleted"
        )
    ).to_be_visible(timeout=1000)
