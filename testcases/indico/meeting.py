from playwright.sync_api import Page, expect

from indico.conftest import IndicoTestData


def test_create_meeting(created_meeting_page: Page, test_data: IndicoTestData) -> None:
    expect(created_meeting_page.locator("#event-settings-data")).to_contain_text(
        test_data.meeting_name
    )
    expect(created_meeting_page.locator("#event-settings-location")).to_contain_text(
        test_data.room_name
    )
    expect(created_meeting_page.locator("#event-settings-location")).to_contain_text(
        test_data.venue_name
    )


def test_add_contribution_to_timetable(
    created_meeting_page: Page, test_data: IndicoTestData
) -> None:
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
    # Lock first
    created_meeting_page.get_by_role("button", name=" ").click()
    created_meeting_page.get_by_role("button", name="Lock").click()
    created_meeting_page.get_by_role("button", name="Lock event").click()

    created_meeting_page.get_by_role("button", name=" ").click()
    created_meeting_page.get_by_role("button", name="Unlock").click()
    expect(created_meeting_page.locator("#flashed-messages")).to_contain_text(
        "The event is now unlocked."
    )


# def test_unlock_meeting(created_meeting_page: Page, test_data: IndicoTestData) -> None:
#     created_meeting_page.get_by_role("button", name=" ").click()
#     created_meeting_page.get_by_role("button", name="Change type").click()
#     created_meeting_page.get_by_text("Home » meeting title Switch").click()
#     created_meeting_page.get_by_text(
#         "Admin User1 - contributionRoom, Location11:00 - 11:"
#     ).click()
#     created_meeting_page.get_by_role("link", name="Add new ").click()
#     created_meeting_page.get_by_role("link", name="Break").click()
#     created_meeting_page.get_by_role("textbox", name="Title").click()

#     created_meeting_page.get_by_role("link", name="Add new ").click()
#     created_meeting_page.get_by_role("link", name="Session block").click()
#     created_meeting_page.get_by_role("textbox", name="Title").click()
#     created_meeting_page.get_by_role("textbox", name="Title").fill("Session block")
#     created_meeting_page.get_by_role("textbox", name="Description").click()
#     created_meeting_page.get_by_role("textbox", name="Description").fill(
#         "session bloick description"
#     )
#     created_meeting_page.get_by_role("button", name="Save").click()
#     created_meeting_page.get_by_role("textbox", name="Title").click()
#     created_meeting_page.get_by_label("Add session block").locator("div").filter(
#         has_text="Add session block"
#     ).get_by_role("button").click()
#     expect(created_meeting_page.locator("#timetable_canvas")).to_contain_text("Break")
#     created_meeting_page.get_by_role("link", name=" Settings").click()
#     created_meeting_page.get_by_role("button", name=" ").click()
#     created_meeting_page.get_by_role("link", name=" Timetable").click()
#     created_meeting_page.get_by_role("link", name="Add new ").click()
#     created_meeting_page.get_by_role("link", name="Add new ").click()
#     created_meeting_page.get_by_role("link", name=" Switch to display view").click()
#     created_meeting_page.locator('[id="1-contribution"]').get_by_role(
#         "button", name=" "
#     ).click()
#     created_meeting_page.get_by_role("link", name="Add minutes").click()
#     created_meeting_page.locator(
#         'iframe[title="Rich Text Area"]'
#     ).content_frame.locator("html").click()
#     created_meeting_page.locator(
#         'iframe[title="Rich Text Area"]'
#     ).content_frame.get_by_label("Rich Text Area. Press ALT-0").fill("meeting minutes")
#     created_meeting_page.get_by_role("button", name="Save").click()
#     expect(
#         created_meeting_page.locator(
#             'iframe[title="Rich Text Area"]'
#         ).content_frame.get_by_role("paragraph")
#     ).to_contain_text("meeting minutes")
#     expect(created_meeting_page.locator("body")).to_match_aria_snapshot(
#         '- button "Save" [disabled]'
#     )
#     created_meeting_page.get_by_role("button", name="Close").click()
#     created_meeting_page.get_by_role("button", name=" ").first.click()
#     created_meeting_page.get_by_role("link", name="Material editor").click()
#     created_meeting_page.get_by_role("button", name=" Add link").click()
#     created_meeting_page.get_by_role("textbox", name="URL").fill("https://demo.com")
#     created_meeting_page.get_by_role("textbox", name="Title").click()
#     created_meeting_page.get_by_role("textbox", name="Title").fill("Demo Website")
#     created_meeting_page.get_by_role("button", name="Submit").click()
#     expect(created_meeting_page.locator("#ui-id-3")).to_contain_text(
#         "The link has been added"
#     )
#     expect(created_meeting_page.locator("#ui-id-3")).to_contain_text(
#         "The link has been added"
#     )
#     expect(created_meeting_page.get_by_role("row")).to_contain_text("Demo Website")
#     created_meeting_page.get_by_role("button", name=" Upload files").click()
#     created_meeting_page.get_by_role("button", name="Choose from your computer").click()
#     created_meeting_page.get_by_role(
#         "button", name="Choose from your computer"
#     ).set_input_files("mqp1380-320x320h_upscale.jpeg")
#     created_meeting_page.get_by_role("button", name="Upload", exact=True).click()
#     expect(created_meeting_page.get_by_text("The attachment has been")).to_be_visible()
#     expect(created_meeting_page.locator("#ui-id-3")).to_contain_text(
#         "The attachment has been uploaded"
#     )
#     created_meeting_page.get_by_label("Manage materials for 'meeting").locator(
#         "div"
#     ).filter(has_text="Manage materials for 'meeting").get_by_role("button").click()
#     created_meeting_page.goto(
#         "http://localhost:8080/event/28/manage/timetable/#20250721"
#     )
#     created_meeting_page.get_by_role("button", name=" ").click()
#     created_meeting_page.get_by_role("button", name="Delete").click()
#     created_meeting_page.get_by_role(
#         "checkbox", name="I understand what this means"
#     ).check()
#     created_meeting_page.get_by_role("button", name="Delete event").click()
#     expect(created_meeting_page.locator("#flashed-messages")).to_contain_text(
#         'Event "meeting title" successfully deleted.'
#     )


def test_delete_meeting(created_meeting_page: Page, test_data: IndicoTestData) -> None:
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
