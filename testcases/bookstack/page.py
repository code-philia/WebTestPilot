from bookstack.conftest import BookStackTestData, create_page
from bookstack.utilities import (
    navigate_back_to_book_from_page,
    navigate_to_book,
    navigate_to_page,
)
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect


def test_create_page(logged_in_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(logged_in_page)

    navigate_to_book(logged_in_page, test_data.book_name)

    created_page_page = create_page(
        logged_in_page, test_data.page_name, test_data.page_description
    )

    expect(created_page_page.get_by_role("main")).to_contain_text(test_data.page_name)
    expect(created_page_page.get_by_role("main")).to_contain_text(
        test_data.page_description
    )

    navigate_back_to_book_from_page(created_page_page, test_data.book_name)
    expect(created_page_page.get_by_role("main")).to_contain_text(test_data.page_name)


def test_read_page(logged_in_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_page(logged_in_page, test_data.book_name, test_data.page_name)

    expect(logged_in_page.get_by_role("main")).to_contain_text(test_data.page_name)
    expect(logged_in_page.get_by_role("main")).to_contain_text(
        test_data.page_description
    )


def test_update_page(logged_in_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_page(logged_in_page, test_data.book_name, test_data.page_name)

    logged_in_page.get_by_role("link", name="Edit").click()

    logged_in_page.get_by_role("textbox", name="Page Title").click()
    logged_in_page.get_by_role("textbox", name="Page Title").press("ControlOrMeta+a")
    logged_in_page.get_by_role("textbox", name="Page Title").fill(
        test_data.page_name_updated
    )

    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_text(
        test_data.page_description
    ).click()
    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_label(
        "Rich Text Area. Press ALT-0"
    ).press("ControlOrMeta+a")
    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_label(
        "Rich Text Area. Press ALT-0"
    ).fill(test_data.page_description_updated)

    logged_in_page.get_by_role("button", name="Save Page").click()

    expect(
        logged_in_page.get_by_role("alert").filter(has_text="Page successfully updated")
    ).to_be_visible(timeout=1000)
    expect(logged_in_page.get_by_role("main")).to_contain_text(
        test_data.page_name_updated
    )
    expect(logged_in_page.get_by_role("main")).to_contain_text(
        test_data.page_description_updated
    )

    expect(logged_in_page.get_by_role("list")).to_contain_text(
        test_data.page_name_updated
    )


def test_delete_page(logged_in_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_page(logged_in_page, test_data.book_name, test_data.page_name)

    logged_in_page.get_by_role("link", name="Delete").click()
    logged_in_page.get_by_role("button", name="Confirm").click()

    expect(
        logged_in_page.get_by_role("alert").filter(has_text="Page successfully deleted")
    ).to_be_visible()
