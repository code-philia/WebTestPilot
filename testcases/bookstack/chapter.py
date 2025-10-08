from bookstack.conftest import BookStackTestData, create_chapter
from bookstack.utilities import (
    navigate_to_book,
    navigate_to_chapter,
)
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect


def test_create_chapter(logged_in_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_book(logged_in_page, test_data.book_name)

    created_chapter_page = create_chapter(
        logged_in_page, test_data.chapter_name, test_data.chapter_description
    )

    expect(created_chapter_page.locator("h1")).to_contain_text(test_data.chapter_name)
    expect(created_chapter_page.get_by_role("main")).to_contain_text(
        test_data.chapter_description
    )

    # Check the book's chapter list
    created_chapter_page.get_by_label("Book Navigation").get_by_role(
        "link", name=test_data.chapter_name
    ).click()
    expect(created_chapter_page.get_by_role("list")).to_contain_text(
        test_data.chapter_name
    )

    # Navigate back to book page and check
    created_chapter_page.get_by_label("Breadcrumb").get_by_role(
        "link", name=test_data.book_name
    ).click()
    expect(created_chapter_page.get_by_role("main")).to_contain_text(
        test_data.book_name
    )


def test_read_chapter(logged_in_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_chapter(logged_in_page, test_data.book_name, test_data.chapter_name)

    expect(logged_in_page.locator("h1")).to_contain_text(test_data.chapter_name)
    expect(logged_in_page.get_by_role("main")).to_contain_text(
        test_data.chapter_description
    )


def test_update_chapter(logged_in_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_chapter(logged_in_page, test_data.book_name, test_data.chapter_name)

    logged_in_page.get_by_role("link", name="Edit").click()

    # Name
    logged_in_page.get_by_role("textbox", name="Name").click()
    logged_in_page.get_by_role("textbox", name="Name").fill(
        test_data.chapter_name_updated
    )

    # Description
    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_text(
        test_data.chapter_description
    ).click()
    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_label(
        "Rich Text Area. Press ALT-0"
    ).fill(test_data.chapter_description_updated)

    # Tags
    logged_in_page.get_by_text("Chapter Tags Add some tags to").click()
    logged_in_page.locator('input[name="tags[0][value]"]').click()
    logged_in_page.locator('input[name="tags[0][value]"]').fill("Sample Tag Updated")

    logged_in_page.get_by_role("button", name="Save Chapter").click()

    # Check content.
    expect(
        logged_in_page.get_by_role("alert").filter(
            has_text="Chapter successfully updated"
        )
    ).to_be_visible(timeout=1000)
    expect(logged_in_page.locator("h1")).to_contain_text(test_data.chapter_name_updated)
    expect(logged_in_page.get_by_role("main")).to_contain_text(
        test_data.chapter_description_updated
    )


def test_delete_chapter(logged_in_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_chapter(logged_in_page, test_data.book_name, test_data.chapter_name)

    logged_in_page.get_by_role("link", name="Delete").click()
    logged_in_page.get_by_role("button", name="Confirm").click()

    expect(
        logged_in_page.get_by_role("alert").filter(
            has_text="Chapter successfully deleted"
        )
    ).to_be_visible()
