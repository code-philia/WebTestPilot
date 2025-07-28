from playwright.sync_api import Page
from tracing_api import traced_expect as expect

from indico.conftest import IndicoTestData


def test_create_lecture(created_lecture_page: Page, test_data: IndicoTestData) -> None:
    expect(created_lecture_page.locator("#event-settings-data")).to_contain_text(
        test_data.lecture_name
    )
    expect(created_lecture_page.locator("#event-settings-location")).to_contain_text(
        test_data.room_name
    )
    expect(created_lecture_page.locator("#event-settings-location")).to_contain_text(
        test_data.venue_name
    )


def test_delete_lecture(created_lecture_page: Page, test_data: IndicoTestData) -> None:
    created_lecture_page.get_by_role("button", name=" ").click()
    expect(created_lecture_page.locator("#event-action-menu-actions")).to_contain_text(
        "Delete"
    )
    created_lecture_page.get_by_role("button", name="Delete").click()
    created_lecture_page.get_by_role(
        "checkbox", name="I understand what this means"
    ).check()
    created_lecture_page.get_by_role("button", name="Delete event").click()
    expect(created_lecture_page.locator("#flashed-messages")).to_contain_text(
        f'Event "{test_data.lecture_name}" successfully deleted.'
    )


def test_lock_lecture(created_lecture_page: Page) -> None:
    created_lecture_page.get_by_role("button", name=" ").click()
    created_lecture_page.get_by_role("button", name="Change type").click()
    created_lecture_page.get_by_role("button", name="Lock").click()
    created_lecture_page.get_by_role("button", name="Lock event").click()

    expect(created_lecture_page.get_by_role("main")).to_contain_text(
        "This event has been locked and cannot be modified."
    )
    expect(created_lecture_page.locator("#flashed-messages")).to_contain_text(
        "The event is now locked."
    )


def test_unlock_lecture(created_lecture_page: Page, test_data: IndicoTestData) -> None:
    # Lock first
    created_lecture_page.get_by_role("button", name=" ").click()
    created_lecture_page.get_by_role("button", name="Change type").click()
    created_lecture_page.get_by_role("button", name="Lock").click()
    created_lecture_page.get_by_role("button", name="Lock event").click()

    expect(created_lecture_page.get_by_role("main")).to_contain_text(
        "This event has been locked and cannot be modified."
    )
    expect(created_lecture_page.locator("#flashed-messages")).to_contain_text(
        "The event is now locked."
    )

    # Then unlock it
    created_lecture_page.get_by_role("button", name=" ").click()
    created_lecture_page.get_by_role("button", name="Unlock").click()
    expect(created_lecture_page.locator("#flashed-messages")).to_contain_text(
        "The event is now unlocked."
    )


def test_clone_lecture(created_lecture_page: Page, test_data: IndicoTestData) -> None:
    created_lecture_page.get_by_role("button", name=" Clone").click()
    created_lecture_page.get_by_label("Clone Event").locator("div").filter(
        has_text="Clone Event"
    ).get_by_role("button").click()

    expect(created_lecture_page.locator("#event-settings-data")).to_contain_text(
        test_data.lecture_name
    )
    expect(created_lecture_page.locator("#event-settings-location")).to_contain_text(
        test_data.room_name
    )
    expect(created_lecture_page.locator("#event-settings-location")).to_contain_text(
        test_data.venue_name
    )
