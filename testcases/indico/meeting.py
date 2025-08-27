from indico.conftest import IndicoTestData, create_meeting
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect


def test_create_meeting(logged_in_page: Page, test_data: IndicoTestData) -> None:
    insert_start_event_to_page(logged_in_page)

    create_meeting(logged_in_page, test_data)

    expect(logged_in_page.locator("#event-settings-data")).to_contain_text(
        test_data.meeting_name
    )
    expect(logged_in_page.locator("#event-settings-location")).to_contain_text(
        test_data.room_name
    )
    expect(logged_in_page.locator("#event-settings-location")).to_contain_text(
        test_data.venue_name
    )


def test_add_contribution_to_timetable(
    created_meeting_page: Page, test_data: IndicoTestData
) -> None:
    insert_start_event_to_page(created_meeting_page)

    created_meeting_page.get_by_role("link", name=" Timetable").click()
    created_meeting_page.get_by_role("link", name="Add new ").click()
    created_meeting_page.get_by_role("link", name="Contribution").click()

    # Title & Description
    created_meeting_page.get_by_role("textbox", name="Title").click()
    created_meeting_page.get_by_role("textbox", name="Title").fill(
        test_data.meeting_contribution_name
    )
    created_meeting_page.get_by_role("textbox", name="Description").click()
    created_meeting_page.get_by_role("textbox", name="Description").fill(
        test_data.meeting_contribution_description
    )

    # Date & Time
    created_meeting_page.get_by_role("textbox", name="--:--").click()
    created_meeting_page.get_by_role("button", name="11").first.click()

    # Add author
    created_meeting_page.get_by_role("button", name="Add myself").click()
    created_meeting_page.get_by_role("button", name="Save").click()

    expect(created_meeting_page.locator("#timetable_canvas")).to_contain_text(
        test_data.meeting_contribution_name
    )


def test_add_break_to_timetable(
    created_meeting_page: Page, test_data: IndicoTestData
) -> None:
    insert_start_event_to_page(created_meeting_page)

    created_meeting_page.get_by_role("link", name=" Timetable").click()
    created_meeting_page.get_by_role("link", name="Add new ").click()
    created_meeting_page.get_by_role("link", name="Break").click()

    # Title & Description
    created_meeting_page.get_by_role("textbox", name="Title").fill(test_data.break_name)
    created_meeting_page.get_by_role("textbox", name="Description").click()
    created_meeting_page.get_by_role("textbox", name="Description").fill(
        test_data.break_description
    )

    # Date & Time
    created_meeting_page.get_by_role("textbox", name="--:--").click()
    created_meeting_page.get_by_role("button", name="11").first.click()

    created_meeting_page.get_by_role("button", name="Save").click()

    expect(created_meeting_page.locator("#timetable_canvas")).to_contain_text("Break")


def test_lock_meeting(created_meeting_page: Page, test_data: IndicoTestData) -> None:
    insert_start_event_to_page(created_meeting_page)

    created_meeting_page.get_by_role("button", name=" ").click()
    created_meeting_page.get_by_role("button", name="Lock").click()
    created_meeting_page.get_by_role("button", name="Lock event").click()

    expect(created_meeting_page.get_by_role("main")).to_contain_text(
        "This event has been locked and cannot be modified."
    )
    expect(created_meeting_page.locator("#flashed-messages")).to_contain_text(
        "The event is now locked."
    )


def test_unlock_meeting(created_meeting_page: Page, test_data: IndicoTestData) -> None:
    insert_start_event_to_page(created_meeting_page)

    # Lock first
    created_meeting_page.get_by_role("button", name=" ").click()
    created_meeting_page.get_by_role("button", name="Lock").click()
    created_meeting_page.get_by_role("button", name="Lock event").click()

    # Then unlock it
    created_meeting_page.get_by_role("button", name=" ").click()
    created_meeting_page.get_by_role("button", name="Unlock").click()
    expect(created_meeting_page.locator("#flashed-messages")).to_contain_text(
        "The event is now unlocked."
    )


def test_add_minutes_to_meeting(
    created_meeting_page: Page, test_data: IndicoTestData
) -> None:
    insert_start_event_to_page(created_meeting_page)

    created_meeting_page.get_by_role("link", name=" Switch to display view").click()
    created_meeting_page.get_by_role("button", name=" ").click()
    created_meeting_page.get_by_role("link", name="Add minutes").click()
    created_meeting_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.locator("html").click()
    created_meeting_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.get_by_label("Rich Text Area. Press ALT-0").fill(
        test_data.meeting_minute_name
    )
    created_meeting_page.get_by_role("button", name="Save").click()

    expect(
        created_meeting_page.locator(
            'iframe[title="Rich Text Area"]'
        ).content_frame.get_by_role("paragraph")
    ).to_contain_text(test_data.meeting_minute_name)
    expect(created_meeting_page.locator("body")).to_match_aria_snapshot(
        '- button "Save" [disabled]'
    )

    created_meeting_page.get_by_role("button", name="Close").click()


def test_delete_meeting(created_meeting_page: Page, test_data: IndicoTestData) -> None:
    insert_start_event_to_page(created_meeting_page)

    created_meeting_page.get_by_role("button", name=" ").click()
    expect(created_meeting_page.locator("#event-action-menu-actions")).to_contain_text(
        "Delete"
    )
    created_meeting_page.get_by_role("button", name="Delete").click()
    created_meeting_page.get_by_role(
        "checkbox", name="I understand what this means"
    ).check()
    created_meeting_page.get_by_role("button", name="Delete event").click()
    expect(created_meeting_page.locator("#flashed-messages")).to_contain_text(
        f'Event "{test_data.meeting_name}" successfully deleted.'
    )


def test_clone_meeting(created_meeting_page: Page, test_data: IndicoTestData) -> None:
    insert_start_event_to_page(created_meeting_page)

    created_meeting_page.get_by_role("button", name=" Clone").click()
    created_meeting_page.get_by_label("Clone Event").locator("div").filter(
        has_text="Clone Event"
    ).get_by_role("button").click()

    expect(created_meeting_page.locator("#event-settings-data")).to_contain_text(
        test_data.meeting_name
    )
    expect(created_meeting_page.locator("#event-settings-location")).to_contain_text(
        test_data.room_name
    )
    expect(created_meeting_page.locator("#event-settings-location")).to_contain_text(
        test_data.venue_name
    )
