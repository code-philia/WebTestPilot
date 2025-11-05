from indico.conftest import IndicoTestData
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect

from .utilities import create_meeting, navigate_to_meeting_edit_page


def test_create_meeting(logged_in_page: Page, test_data: IndicoTestData) -> None:
    insert_start_event_to_page(logged_in_page)

    create_meeting(logged_in_page)

    expect(logged_in_page.locator("#event-settings-data")).to_contain_text(
        test_data.meeting_name
    )
    expect(logged_in_page.locator("#event-settings-location")).to_contain_text(
        test_data.room_name
    )
    expect(logged_in_page.locator("#event-settings-location")).to_contain_text(
        test_data.venue_name
    )


# def test_add_contribution_to_timetable(
#     logged_in_page: Page, test_data: IndicoTestData
# ) -> None:
#     insert_start_event_to_page(logged_in_page)
#     navigate_to_meeting_edit_page(logged_in_page)

#     logged_in_page.get_by_role("link", name=" Timetable").click()
#     logged_in_page.get_by_role("link", name="Add new ").click()
#     logged_in_page.get_by_role("link", name="Contribution").click()

#     # Title & Description
#     logged_in_page.get_by_role("textbox", name="Title").click()
#     logged_in_page.get_by_role("textbox", name="Title").fill(
#         test_data.meeting_contribution_name
#     )
#     logged_in_page.get_by_role("textbox", name="Description").click()
#     logged_in_page.get_by_role("textbox", name="Description").fill(
#         test_data.meeting_contribution_description
#     )

#     # Date & Time
#     logged_in_page.get_by_role("textbox", name="--:--").click()
#     logged_in_page.get_by_role("button", name="11").first.click()

#     # Add author
#     logged_in_page.get_by_role("button", name="Add myself").click()
#     logged_in_page.get_by_role("button", name="Save").click()

#     expect(logged_in_page.locator("#timetable_canvas")).to_contain_text(
#         test_data.meeting_contribution_name
#     )


# def test_add_break_to_timetable(
#     logged_in_page: Page, test_data: IndicoTestData
# ) -> None:
#     insert_start_event_to_page(logged_in_page)
#     navigate_to_meeting_edit_page(logged_in_page)

#     logged_in_page.get_by_role("link", name=" Timetable").click()
#     logged_in_page.get_by_role("link", name="Add new ").click()
#     logged_in_page.get_by_role("link", name="Break").click()

#     # Title & Description
#     logged_in_page.get_by_role("textbox", name="Title").fill(test_data.break_name)
#     logged_in_page.get_by_role("textbox", name="Description").click()
#     logged_in_page.get_by_role("textbox", name="Description").fill(
#         test_data.break_description
#     )

#     # Date & Time
#     logged_in_page.get_by_role("textbox", name="--:--").click()
#     logged_in_page.get_by_role("button", name="11").first.click()

#     logged_in_page.get_by_role("button", name="Save").click()

#     expect(logged_in_page.locator("#timetable_canvas")).to_contain_text("Break")


def test_lock_meeting(logged_in_page: Page, test_data: IndicoTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_meeting_edit_page(logged_in_page)

    logged_in_page.get_by_role("button", name=" ").click()
    logged_in_page.get_by_role("button", name="Lock").click()
    logged_in_page.get_by_role("button", name="Lock event").click()

    expect(logged_in_page.get_by_role("main")).to_contain_text(
        "This event has been locked and cannot be modified."
    )
    expect(logged_in_page.locator("#flashed-messages")).to_contain_text(
        "The event is now locked."
    )


def test_unlock_meeting(logged_in_page: Page, test_data: IndicoTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_meeting_edit_page(logged_in_page)

    # Lock first
    logged_in_page.get_by_role("button", name=" ").click()
    logged_in_page.get_by_role("button", name="Lock").click()
    logged_in_page.get_by_role("button", name="Lock event").click()

    # Then unlock it
    logged_in_page.get_by_role("button", name=" ").click()
    logged_in_page.get_by_role("button", name="Unlock").click()
    expect(logged_in_page.locator("#flashed-messages")).to_contain_text(
        "The event is now unlocked."
    )


def test_add_minutes_to_meeting(
    logged_in_page: Page, test_data: IndicoTestData
) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_meeting_edit_page(logged_in_page)

    logged_in_page.get_by_role("link", name=" Switch to display view").click()
    logged_in_page.get_by_role("button", name=" ").click()
    logged_in_page.get_by_role("link", name="Add minutes").click()
    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.locator(
        "html"
    ).click()
    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_label(
        "Rich Text Area. Press ALT-0"
    ).fill(test_data.meeting_minute_name)
    logged_in_page.get_by_role("button", name="Save").click()

    expect(
        logged_in_page.locator(
            'iframe[title="Rich Text Area"]'
        ).content_frame.get_by_role("paragraph")
    ).to_contain_text(test_data.meeting_minute_name)
    expect(logged_in_page.locator("body")).to_match_aria_snapshot(
        '- button "Save" [disabled]'
    )

    logged_in_page.get_by_role("button", name="Close").click()


def test_delete_meeting(logged_in_page: Page, test_data: IndicoTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_meeting_edit_page(logged_in_page)

    logged_in_page.get_by_role("button", name=" ").click()
    expect(logged_in_page.locator("#event-action-menu-actions")).to_contain_text(
        "Delete"
    )
    logged_in_page.get_by_role("button", name="Delete").click()
    logged_in_page.get_by_role("checkbox", name="I understand what this means").check()
    logged_in_page.get_by_role("button", name="Delete event").click()
    expect(logged_in_page.locator("#flashed-messages")).to_contain_text(
        f'Event "{test_data.meeting_name}" successfully deleted.'
    )


def test_clone_meeting(logged_in_page: Page, test_data: IndicoTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    navigate_to_meeting_edit_page(logged_in_page)

    logged_in_page.get_by_role("button", name=" Clone").click()
    logged_in_page.get_by_label("Clone Event").locator("div").filter(
        has_text="Clone Event"
    ).get_by_role("button").click()

    expect(logged_in_page.locator("#event-settings-data")).to_contain_text(
        test_data.meeting_name
    )
    expect(logged_in_page.locator("#event-settings-location")).to_contain_text(
        test_data.room_name
    )
    expect(logged_in_page.locator("#event-settings-location")).to_contain_text(
        test_data.venue_name
    )
