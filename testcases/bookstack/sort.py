from bookstack.conftest import (
    BookStackTestData,
    create_sort_rule,
)
from playwright.sync_api import Page
from testcases.bookstack.utilities import navigate_to_book
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect


def test_sort_chapter_book(logged_in_page: Page, test_data: BookStackTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)

    # Go back to book to start sorting.
    navigate_to_book(page, test_data.book_name)

    page.get_by_role("link", name="Sort").click()
    page.get_by_role("button", name="Move Up").first.click()

    # Optionally, pause for a bit to allow user to see the change
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Move Down").nth(1).click()
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Move Up").nth(1).click()
    page.wait_for_timeout(1000)

    page.get_by_role("button", name="Save New Order").click()
    expect(
        page.get_by_role("alert").filter(has_text="Book successfully re-sorted")
    ).to_be_visible(timeout=1000)


def test_sort_by_name(logged_in_page: Page, test_data: BookStackTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)

    # Go back to book to start sorting.
    navigate_to_book(page, test_data.book_name)

    page.get_by_role("link", name="Sort").click()
    page.get_by_role("button", name="Sort by Name").first.click()
    page.get_by_role("button", name="Save New Order").click()
    expect(
        page.get_by_role("alert").filter(has_text="Book successfully re-sorted")
    ).to_be_visible(timeout=1000)


def test_create_sort_rules(logged_in_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(logged_in_page)

    logged_in_page = create_sort_rule(logged_in_page, test_data.sort_rule_name_new)
    expect(
        logged_in_page.get_by_role("alert").filter(
            has_text="Sort rule successfully created"
        )
    ).to_be_visible(timeout=1000)
    expect(
        logged_in_page.get_by_role("link", name=test_data.sort_rule_name_new)
    ).to_be_attached()


def test_update_sort_rules(logged_in_page: Page, test_data: BookStackTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)

    page.get_by_role("link", name="Settings", exact=True).click()
    page.get_by_role("link", name="Sorting", exact=True).click()

    page.get_by_role("link", name=test_data.sort_rule_name, exact=True).click()
    page.get_by_role("textbox", name="Name").click()
    page.get_by_role("textbox", name="Name").fill(test_data.sort_rule_name_updated)

    # Add more rule
    page.get_by_role("listitem").filter(has_text="Chapters First").get_by_role(
        "button"
    ).click()

    page.get_by_role("button", name="Save").click()
    expect(
        page.get_by_role("alert").filter(has_text="Sort rule successfully updated")
    ).to_be_visible(timeout=1000)

    expect(page.locator("#main-content")).to_contain_text(
        test_data.sort_rule_name_updated
    )


def test_delete_sort_rules(logged_in_page: Page, test_data: BookStackTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)

    page.get_by_role("link", name="Settings", exact=True).click()
    page.get_by_role("link", name="Sorting", exact=True).click()

    page.get_by_role("link", name=test_data.sort_rule_name, exact=True).click()
    page.get_by_role("button", name="Delete").click()

    expect(
        page.get_by_role("alert").filter(has_text="Sort rule successfully deleted")
    ).to_be_visible(timeout=1000)
