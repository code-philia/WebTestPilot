from indico.conftest import IndicoTestData
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect

from .utilities import create_conference, navigate_to_conference_edit_page


def test_create_conference(logged_in_page: Page, test_data: IndicoTestData) -> None:
    insert_start_event_to_page(logged_in_page)

    create_conference(logged_in_page, test_data)

    expect(logged_in_page.locator("#event-settings-data")).to_contain_text(
        test_data.conference_name
    )
    expect(logged_in_page.locator("#event-settings-location")).to_contain_text(
        test_data.room_name
    )
    expect(logged_in_page.locator("#event-settings-location")).to_contain_text(
        test_data.venue_name
    )


def test_lock_conference(logged_in_page: Page) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    navigate_to_conference_edit_page(page)

    page.get_by_role("button", name=" ").click()
    page.get_by_role("button", name="Lock").click()
    page.get_by_role("button", name="Lock event").click()

    expect(page.get_by_role("main")).to_contain_text(
        "This event has been locked and cannot be modified."
    )
    expect(page.locator("#flashed-messages")).to_contain_text(
        "The event is now locked."
    )


def test_unlock_conference(logged_in_page: Page, test_data: IndicoTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    navigate_to_conference_edit_page(page)

    # Lock first
    page.get_by_role("button", name=" ").click()
    page.get_by_role("button", name="Lock").click()
    page.get_by_role("button", name="Lock event").click()

    expect(page.get_by_role("main")).to_contain_text(
        "This event has been locked and cannot be modified."
    )
    expect(page.locator("#flashed-messages")).to_contain_text(
        "The event is now locked."
    )

    # Then unlock it
    page.get_by_role("button", name=" ").click()
    page.get_by_role("button", name="Unlock").click()
    expect(page.locator("#flashed-messages")).to_contain_text(
        "The event is now unlocked."
    )


def test_add_track_to_conference(
    logged_in_page: Page, test_data: IndicoTestData
) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    navigate_to_conference_edit_page(page)

    page.get_by_role("link", name="Programme").click()
    page.get_by_role("link", name=" Add track", exact=True).click()
    page.get_by_role("textbox", name="Title").fill(test_data.conference_track_name)
    page.get_by_role("textbox", name="Code").click()
    page.get_by_role("textbox", name="Code").fill("OC")
    page.get_by_role("textbox", name="Description").click()
    page.get_by_role("textbox", name="Description").fill(
        test_data.conference_track_description
    )
    page.get_by_role("button", name="Save").click()
    expect(page.locator("#track-list-container")).to_contain_text(
        test_data.conference_track_name
    )
    expect(page.locator("#flashed-messages")).to_contain_text(
        f'Track "{test_data.conference_track_name}" has been created.'
    )


def test_add_track_group_to_conference(
    logged_in_page: Page, test_data: IndicoTestData
) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    navigate_to_conference_edit_page(page)

    page.get_by_role("link", name="Programme").click()
    page.get_by_role("link", name=" Add track group").click()
    page.get_by_role("textbox", name="Title").fill(
        test_data.conference_track_group_name
    )
    page.get_by_role("textbox", name="Description").click()
    page.get_by_role("textbox", name="Description").fill(
        test_data.conference_track_group_description
    )
    page.get_by_role("button", name="Save").click()

    expect(page.locator("#track-list-container")).to_contain_text(
        test_data.conference_track_group_name
    )
    expect(page.locator("#track-list-container")).to_contain_text(
        test_data.conference_track_group_description
    )


def test_enable_call_for_abstracts_conference(
    logged_in_page: Page, test_data: IndicoTestData
) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    navigate_to_conference_edit_page(page)

    # Open the collapsible menu
    page.get_by_role("listitem").filter(
        has_text="Workflows Call for Abstracts"
    ).locator("div").click()

    page.get_by_role("link", name="Call for Abstracts").click()
    page.get_by_role("button", name="Enable module").click()

    expect(page.locator("#reviewing-page")).to_contain_text(
        "The call for abstracts is not open yet"
    )

    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Close now").click()

    page.get_by_role("button", name="Reopen now").click()
    page.get_by_label("Confirm action").locator("div").filter(
        has_text="Confirm action"
    ).get_by_role("button").click()


def test_enable_notifications_for_call_for_abstracts_conference(
    logged_in_page: Page, test_data: IndicoTestData
) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    navigate_to_conference_edit_page(page)

    # Open the collapsible menu
    page.get_by_role("listitem").filter(
        has_text="Workflows Call for Abstracts"
    ).locator("div").click()

    page.get_by_role("link", name="Call for Abstracts").click()
    page.get_by_role("button", name="Enable module").click()

    page.get_by_role("button", name=" Notifications").click()

    # Add notification title.
    page.get_by_role("button", name=" Add new one").click()
    page.get_by_role("textbox", name="Title").fill(test_data.email_notification_title)

    page.get_by_role("button", name=" Add new rule").click()

    # Event: "Submitted"
    page.get_by_role("group", name="Rules").get_by_role("combobox").select_option(
        "Submitted"
    )

    page.get_by_role("button", name="Save").click()


def test_enable_default_notifications_for_call_for_abstracts_conference(
    logged_in_page: Page,
) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    navigate_to_conference_edit_page(page)

    # Open the collapsible menu
    page.get_by_role("listitem").filter(
        has_text="Workflows Call for Abstracts"
    ).locator("div").click()

    page.get_by_role("link", name="Call for Abstracts").click()
    page.get_by_role("button", name="Enable module").click()

    page.get_by_role("button", name=" Setup default notifications").click()
    expect(page.locator("#flashed-messages")).to_contain_text(
        'Default notification templates added. You may customize them using the "Notifications" button.'
    )


def test_add_sessions_to_conference(
    logged_in_page: Page, test_data: IndicoTestData
) -> None:
    page = logged_in_page
    insert_start_event_to_page(logged_in_page)
    navigate_to_conference_edit_page(page)

    page.get_by_role("link", name="Sessions").click()

    # Create session type
    page.locator("#contributions-settings-dropdown").click()
    page.get_by_role("link", name="Session types").click()
    page.get_by_role("button", name=" New session type").click()
    page.get_by_role("textbox", name="Name").fill(test_data.session_type)
    page.get_by_role("button", name="Save").click()
    expect(page.locator("tbody")).to_contain_text(test_data.session_type)
    page.get_by_role("button", name="Close").click()

    # Start adding new session
    page.get_by_role("button", name=" Add new session").click()
    page.get_by_role("textbox", name="Title").click()
    page.get_by_role("textbox", name="Title").fill(test_data.session_title)

    # Choose the just created session type
    page.get_by_label("Type").click()
    page.get_by_label("Type").select_option(f"{test_data.session_type}")
    page.get_by_role("textbox", name="Description").click()
    page.get_by_role("textbox", name="Description").fill(test_data.session_description)
    page.get_by_role("button", name="Save").click()

    expect(page.locator("tbody")).to_contain_text(test_data.session_title)


def test_edit_sessions_in_conference(
    logged_in_page: Page, test_data: IndicoTestData
) -> None:
    page = logged_in_page
    insert_start_event_to_page(logged_in_page)
    navigate_to_conference_edit_page(page)

    page.get_by_role("link", name="Sessions").click()

    # Add new session
    page.get_by_role("button", name=" Add new session").click()
    page.get_by_role("textbox", name="Title").click()
    page.get_by_role("textbox", name="Title").fill(test_data.session_title)
    page.get_by_role("textbox", name="Description").click()
    page.get_by_role("textbox", name="Description").fill(test_data.session_description)
    page.get_by_role("button", name="Save").click()
    expect(page.locator("tbody")).to_contain_text(test_data.session_title)

    # Click configure (gear) button to edit
    page.get_by_role("link", name="").first.click()
    page.get_by_role("textbox", name="Title").click()
    page.get_by_role("textbox", name="Title").click()
    page.get_by_role("textbox", name="Title").fill(test_data.session_title_updated)
    page.get_by_role("button", name="Save").click()
    expect(page.locator("tbody")).to_contain_text(test_data.session_title_updated)


def test_delete_sessions_in_conference(
    logged_in_page: Page, test_data: IndicoTestData
) -> None:
    insert_start_event_to_page(page)

    page.get_by_role("link", name="Sessions").click()
    expect(page.locator("#sessions-wrapper div").first).to_contain_text(
        "There are no sessions yet."
    )

    # Add new session
    page.get_by_role("button", name=" Add new session").click()
    page.get_by_role("textbox", name="Title").click()
    page.get_by_role("textbox", name="Title").fill(test_data.session_title)
    page.get_by_role("textbox", name="Description").click()
    page.get_by_role("textbox", name="Description").fill(test_data.session_description)
    page.get_by_role("button", name="Save").click()
    expect(page.locator("tbody")).to_contain_text(test_data.session_title)

    # Click the trash button to delete
    page.get_by_role("link", name="").first.click()
    page.get_by_role("button", name="OK").click()

    # Check it's deleted
    expect(page.locator(selector="#sessions-wrapper div").first).to_contain_text(
        "There are no sessions yet."
    )


def test_add_contribution_session_to_timetable_in_conference(
    logged_in_page: Page, test_data: IndicoTestData
) -> None:
    page = logged_in_page
    insert_start_event_to_page(logged_in_page)
    navigate_to_conference_edit_page(page)

    # Go to timetable and add session to it
    page.get_by_role("link", name=" Timetable").click()

    page.get_by_role("link", name="Add new ").click()
    page.get_by_role("link", name="Contribution", exact=True).click()
    page.get_by_role("textbox", name="Title").click()
    page.get_by_role("textbox", name="Title").fill(test_data.session_contribution_name)
    page.get_by_role("button", name="Save").click()
    expect(page.locator("#timetable_canvas")).to_contain_text(
        f"1 - {test_data.session_contribution_name}"
    )


def test_add_break_session_to_timetable_in_conference(
    logged_in_page: Page, test_data: IndicoTestData
) -> None:
    page = logged_in_page
    insert_start_event_to_page(logged_in_page)
    navigate_to_conference_edit_page(page)

    page.get_by_role("link", name=" Timetable").click()

    page.get_by_role("link", name="Add new ").click()
    page.get_by_role("link", name="Break").click()
    page.get_by_role("textbox", name="Title").click()
    page.get_by_role("textbox", name="Title").fill("Break")
    page.get_by_role("button", name="Save").click()

    expect(page.locator("#timetable_canvas")).to_contain_text("Break")


def test_payment_setup_in_conference(
    logged_in_page: Page, test_data: IndicoTestData
) -> None:
    page = logged_in_page
    insert_start_event_to_page(logged_in_page)
    navigate_to_conference_edit_page(page)

    page.get_by_role("link", name="Registration").click()

    # Enable payments
    expect(page.get_by_role("link", name="Enable payments")).to_be_visible()

    page.get_by_role("link", name="Enable payments").click()
    page.get_by_role("button", name="OK").click()

    # Will enable a new "Payments" page, go to payment page to continue configuring
    page.get_by_role("link", name="Payments").click()
    expect(page.get_by_role("main")).to_contain_text("enabled")

    # Bank transfer is disabled at first
    expect(page.locator("#plugin-payment_manual")).to_contain_text("disabled")
    expect(page.get_by_role("link", name="Bank Transfer disabled")).to_be_visible()

    # Enable Bank Transfer payment method
    page.get_by_role("link", name="Bank Transfer disabled").click()
    page.get_by_role("checkbox", name="Enabled").check()
    page.get_by_role("textbox", name="Payment details").click()
    page.get_by_role("textbox", name="Payment details").fill("Payment details")
    page.get_by_role("button", name="Save").click()

    expect(page.locator("#flashed-messages")).to_contain_text(
        "Settings for Bank Transfer saved"
    )


def test_registration_setup_in_conference(
    logged_in_page: Page, test_data: IndicoTestData
) -> None:
    page = logged_in_page
    insert_start_event_to_page(logged_in_page)
    navigate_to_conference_edit_page(page)

    page.get_by_role("link", name="Registration").click()
    page.get_by_role("link", name=" Create form").click()
    page.get_by_role("textbox", name="Title").click()
    page.get_by_role("textbox", name="Title").fill(test_data.registration_form_name)
    page.get_by_role("button", name="Create", exact=True).click()

    expect(page.locator("#flashed-messages")).to_contain_text(
        "Registration form has been successfully created"
    )


def test_registration_change_state_in_conference(
    logged_in_page: Page, test_data: IndicoTestData
) -> None:
    page = logged_in_page
    insert_start_event_to_page(logged_in_page)
    navigate_to_conference_edit_page(page)

    page.get_by_role("link", name="Registration").click()
    page.get_by_role("link", name=" Create form").click()
    page.get_by_role("textbox", name="Title").click()
    page.get_by_role("textbox", name="Title").fill(test_data.registration_form_name)
    page.get_by_role("button", name="Create", exact=True).click()

    expect(page.locator("#flashed-messages")).to_contain_text(
        "Registration form has been successfully created"
    )

    # Start
    page.get_by_role("button", name="Start now").click()
    expect(page.locator("#flashed-messages")).to_contain_text(
        f"Registrations for {test_data.registration_form_name} are now open"
    )

    # Close
    page.get_by_role("link", name="Close now").click()
    expect(page.locator("#flashed-messages")).to_contain_text(
        f"Registrations for {test_data.registration_form_name} are now closed"
    )

    # Reopen
    page.get_by_role("button", name="Reopen now").click()
    page.get_by_role("button", name="OK").click()
    expect(page.locator("#flashed-messages")).to_contain_text(
        f"Registrations for {test_data.registration_form_name} are now open"
    )


def test_delete_conference(logged_in_page: Page, test_data: IndicoTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(logged_in_page)
    navigate_to_conference_edit_page(page)

    page.get_by_role("button", name=" ").click()
    expect(page.locator("#event-action-menu-actions")).to_contain_text("Delete")
    page.get_by_role("button", name="Delete").click()
    page.get_by_role("checkbox", name="I understand what this means").check()
    page.get_by_role("button", name="Delete event").click()
    expect(page.locator("#flashed-messages")).to_contain_text(
        f'Event "{test_data.conference_name}" successfully deleted.'
    )


def test_clone_conference(logged_in_page: Page, test_data: IndicoTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(logged_in_page)
    navigate_to_conference_edit_page(page)

    page.get_by_role("button", name=" Clone").click()
    page.get_by_label("Clone Event").locator("div").filter(
        has_text="Clone Event"
    ).get_by_role("button").click()

    expect(page.locator("#event-settings-data")).to_contain_text(
        test_data.conference_name
    )
    expect(page.locator("#event-settings-location")).to_contain_text(
        test_data.room_name
    )
    expect(page.locator("#event-settings-location")).to_contain_text(
        test_data.venue_name
    )
