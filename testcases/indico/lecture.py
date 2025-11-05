from indico.conftest import IndicoTestData
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect
from .utilities import create_lecture, navigate_to_lecture_edit_page


def test_create_lecture(logged_in_page: Page, test_data: IndicoTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    create_lecture(logged_in_page)

    expect(logged_in_page.locator("#event-settings-data")).to_contain_text(
        test_data.lecture_name
    )
    expect(logged_in_page.locator("#event-settings-location")).to_contain_text(
        test_data.room_name
    )
    expect(logged_in_page.locator("#event-settings-location")).to_contain_text(
        test_data.venue_name
    )


def test_delete_lecture(logged_in_page: Page, test_data: IndicoTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_lecture_edit_page(logged_in_page)

    logged_in_page.get_by_role("button", name=" ").click()
    expect(logged_in_page.locator("#event-action-menu-actions")).to_contain_text(
        "Delete"
    )
    logged_in_page.get_by_role("button", name="Delete").click()
    logged_in_page.get_by_role("checkbox", name="I understand what this means").check()
    logged_in_page.get_by_role("button", name="Delete event").click()
    expect(logged_in_page.locator("#flashed-messages")).to_contain_text(
        f'Event "{test_data.lecture_name}" successfully deleted.'
    )


def test_lock_lecture(logged_in_page: Page) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_lecture_edit_page(logged_in_page)

    logged_in_page.get_by_role("button", name=" ").click()
    logged_in_page.get_by_role("button", name="Change type").click()
    logged_in_page.get_by_role("button", name="Lock").click()
    logged_in_page.get_by_role("button", name="Lock event").click()

    expect(logged_in_page.get_by_role("main")).to_contain_text(
        "This event has been locked and cannot be modified."
    )
    expect(logged_in_page.locator("#flashed-messages")).to_contain_text(
        "The event is now locked."
    )


def test_unlock_lecture(logged_in_page: Page, test_data: IndicoTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_lecture_edit_page(logged_in_page)

    # Lock first
    logged_in_page.get_by_role("button", name=" ").click()
    logged_in_page.get_by_role("button", name="Change type").click()
    logged_in_page.get_by_role("button", name="Lock").click()
    logged_in_page.get_by_role("button", name="Lock event").click()

    expect(logged_in_page.get_by_role("main")).to_contain_text(
        "This event has been locked and cannot be modified."
    )
    expect(logged_in_page.locator("#flashed-messages")).to_contain_text(
        "The event is now locked."
    )

    # Then unlock it
    logged_in_page.get_by_role("button", name=" ").click()
    logged_in_page.get_by_role("button", name="Unlock").click()
    expect(logged_in_page.locator("#flashed-messages")).to_contain_text(
        "The event is now unlocked."
    )


def test_clone_lecture(logged_in_page: Page, test_data: IndicoTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_lecture_edit_page(logged_in_page)

    logged_in_page.get_by_role("button", name=" Clone").click()
    logged_in_page.get_by_label("Clone Event").locator("div").filter(
        has_text="Clone Event"
    ).get_by_role("button").click()

    expect(logged_in_page.locator("#event-settings-data")).to_contain_text(
        test_data.lecture_name
    )
    expect(logged_in_page.locator("#event-settings-location")).to_contain_text(
        test_data.room_name
    )
    expect(logged_in_page.locator("#event-settings-location")).to_contain_text(
        test_data.venue_name
    )
