from playwright.sync_api import Page, expect

from indico.conftest import IndicoTestData


def test_create_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    expect(created_conference_page.locator("#event-settings-data")).to_contain_text(
        test_data.meeting_name
    )
    expect(created_conference_page.locator("#event-settings-location")).to_contain_text(
        test_data.room_name
    )
    expect(created_conference_page.locator("#event-settings-location")).to_contain_text(
        test_data.venue_name
    )


def test_lock_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    created_conference_page.get_by_role("button", name=" ").click()
    created_conference_page.get_by_role("button", name="Lock").click()
    created_conference_page.get_by_role("button", name="Lock event").click()

    expect(created_conference_page.get_by_role("main")).to_contain_text(
        "This event has been locked and cannot be modified."
    )
    expect(created_conference_page.locator("#flashed-messages")).to_contain_text(
        "The event is now locked."
    )


def test_unlock_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    # Lock first
    created_conference_page.get_by_role("button", name=" ").click()
    created_conference_page.get_by_role("button", name="Lock").click()
    created_conference_page.get_by_role("button", name="Lock event").click()

    expect(created_conference_page.get_by_role("main")).to_contain_text(
        "This event has been locked and cannot be modified."
    )
    expect(created_conference_page.locator("#flashed-messages")).to_contain_text(
        "The event is now locked."
    )

    # Then unlock it
    created_conference_page.get_by_role("button", name=" ").click()
    created_conference_page.get_by_role("button", name="Unlock").click()
    expect(created_conference_page.locator("#flashed-messages")).to_contain_text(
        "The event is now unlocked."
    )


def test_add_track_to_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    created_conference_page.get_by_role("link", name="Programme").click()
    created_conference_page.get_by_role("link", name=" Add track", exact=True).click()
    created_conference_page.get_by_role("textbox", name="Title").fill(
        test_data.conference_track_name
    )
    created_conference_page.get_by_role("textbox", name="Code").click()
    created_conference_page.get_by_role("textbox", name="Code").fill("OC")
    created_conference_page.get_by_role("textbox", name="Description").click()
    created_conference_page.get_by_role("textbox", name="Description").fill(
        test_data.conference_track_description
    )
    created_conference_page.get_by_role("button", name="Save").click()
    expect(created_conference_page.locator("#track-list-container")).to_contain_text(
        test_data.conference_track_name
    )
    expect(created_conference_page.locator("#flashed-messages")).to_contain_text(
        f'Track "{test_data.conference_track_name}" has been created.'
    )


def test_add_track_group_to_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    created_conference_page.get_by_role("link", name="Programme").click()
    created_conference_page.get_by_role("link", name=" Add track group").click()
    created_conference_page.get_by_role("textbox", name="Title").fill(
        test_data.conference_track_group_name
    )
    created_conference_page.get_by_role("textbox", name="Description").click()
    created_conference_page.get_by_role("textbox", name="Description").fill(
        test_data.conference_track_group_description
    )
    created_conference_page.get_by_role("button", name="Save").click()

    expect(created_conference_page.locator("#track-list-container")).to_contain_text(
        test_data.conference_track_group_name
    )
    expect(created_conference_page.locator("#track-list-container")).to_contain_text(
        test_data.conference_track_group_description
    )


def test_enable_call_for_abstracts_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    # Open the collapsible menu
    created_conference_page.get_by_role("listitem").filter(
        has_text="Workflows Call for Abstracts"
    ).locator("div").click()

    created_conference_page.get_by_role("link", name="Call for Abstracts").click()
    created_conference_page.get_by_role("button", name="Enable module").click()

    expect(created_conference_page.locator("#reviewing-page")).to_contain_text(
        "The call for abstracts is not open yet"
    )

    created_conference_page.get_by_role("button", name="Start now").click()
    created_conference_page.get_by_role("button", name="Close now").click()

    created_conference_page.get_by_role("button", name="Reopen now").click()
    created_conference_page.get_by_label("Confirm action").locator("div").filter(
        has_text="Confirm action"
    ).get_by_role("button").click()


def test_enable_notifications_for_call_for_abstracts_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    # Open the collapsible menu
    created_conference_page.get_by_role("listitem").filter(
        has_text="Workflows Call for Abstracts"
    ).locator("div").click()

    created_conference_page.get_by_role("link", name="Call for Abstracts").click()
    created_conference_page.get_by_role("button", name="Enable module").click()

    created_conference_page.get_by_role("button", name=" Notifications").click()

    # Add notification title.
    created_conference_page.get_by_role("button", name=" Add new one").click()
    created_conference_page.get_by_role("textbox", name="Title").fill(
        test_data.email_notification_title
    )

    created_conference_page.get_by_role("button", name=" Add new rule").click()

    # Event: "Submitted"
    created_conference_page.get_by_role("group", name="Rules").get_by_role(
        "combobox"
    ).select_option("Submitted")

    created_conference_page.get_by_role("button", name="Save").click()


def test_enable_default_notifications_for_call_for_abstracts_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    # Open the collapsible menu
    created_conference_page.get_by_role("listitem").filter(
        has_text="Workflows Call for Abstracts"
    ).locator("div").click()

    created_conference_page.get_by_role("link", name="Call for Abstracts").click()
    created_conference_page.get_by_role("button", name="Enable module").click()

    created_conference_page.get_by_role(
        "button", name=" Setup default notifications"
    ).click()
    expect(created_conference_page.locator("#flashed-messages")).to_contain_text(
        'Default notification templates added. You may customize them using the "Notifications" button.'
    )


def test_add_sessions_to_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    created_conference_page.get_by_role("link", name="Sessions").click()

    # Create session type
    created_conference_page.locator("#contributions-settings-dropdown").click()
    created_conference_page.get_by_role("link", name="Session types").click()
    created_conference_page.get_by_role("button", name=" New session type").click()
    created_conference_page.get_by_role("textbox", name="Name").fill(
        test_data.session_type
    )
    created_conference_page.get_by_role("button", name="Save").click()
    expect(created_conference_page.locator("tbody")).to_contain_text(
        test_data.session_type
    )
    created_conference_page.get_by_role("button", name="Close").click()

    # Start adding new session
    created_conference_page.get_by_role("button", name=" Add new session").click()
    created_conference_page.get_by_role("textbox", name="Title").click()
    created_conference_page.get_by_role("textbox", name="Title").fill(
        test_data.session_title
    )

    # Choose the just created session type
    created_conference_page.get_by_label("Type").click()
    created_conference_page.get_by_label("Type").select_option(
        f"{test_data.session_type}"
    )
    created_conference_page.get_by_role("textbox", name="Description").click()
    created_conference_page.get_by_role("textbox", name="Description").fill(
        test_data.session_description
    )
    created_conference_page.get_by_role("button", name="Save").click()

    expect(created_conference_page.locator("tbody")).to_contain_text(
        test_data.session_title
    )


def test_edit_sessions_in_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    created_conference_page.get_by_role("link", name="Sessions").click()

    # Add new session
    created_conference_page.get_by_role("button", name=" Add new session").click()
    created_conference_page.get_by_role("textbox", name="Title").click()
    created_conference_page.get_by_role("textbox", name="Title").fill(
        test_data.session_title
    )
    created_conference_page.get_by_role("textbox", name="Description").click()
    created_conference_page.get_by_role("textbox", name="Description").fill(
        test_data.session_description
    )
    created_conference_page.get_by_role("button", name="Save").click()
    expect(created_conference_page.locator("tbody")).to_contain_text(
        test_data.session_title
    )

    # Click configure (gear) button to edit
    created_conference_page.get_by_role("link", name="").first.click()
    created_conference_page.get_by_role("textbox", name="Title").click()
    created_conference_page.get_by_role("textbox", name="Title").click()
    created_conference_page.get_by_role("textbox", name="Title").fill(
        test_data.session_title_updated
    )
    created_conference_page.get_by_role("button", name="Save").click()
    expect(created_conference_page.locator("tbody")).to_contain_text(
        test_data.session_title_updated
    )


def test_delete_sessions_in_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    created_conference_page.get_by_role("link", name="Sessions").click()
    expect(
        created_conference_page.locator("#sessions-wrapper div").first
    ).to_contain_text("There are no sessions yet.")

    # Add new session
    created_conference_page.get_by_role("button", name=" Add new session").click()
    created_conference_page.get_by_role("textbox", name="Title").click()
    created_conference_page.get_by_role("textbox", name="Title").fill(
        test_data.session_title
    )
    created_conference_page.get_by_role("textbox", name="Description").click()
    created_conference_page.get_by_role("textbox", name="Description").fill(
        test_data.session_description
    )
    created_conference_page.get_by_role("button", name="Save").click()
    expect(created_conference_page.locator("tbody")).to_contain_text(
        test_data.session_title
    )

    # Click the trash button to delete
    created_conference_page.get_by_role("link", name="").first.click()
    created_conference_page.get_by_role("button", name="OK").click()

    # Check it's deleted
    expect(
        created_conference_page.locator(selector="#sessions-wrapper div").first
    ).to_contain_text("There are no sessions yet.")


def test_add_contribution_session_to_timetable_in_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    # Go to timetable and add session to it
    created_conference_page.get_by_role("link", name=" Timetable").click()

    created_conference_page.get_by_role("link", name="Add new ").click()
    created_conference_page.get_by_role("link", name="Contribution", exact=True).click()
    created_conference_page.get_by_role("textbox", name="Title").click()
    created_conference_page.get_by_role("textbox", name="Title").fill(
        test_data.session_contribution_name
    )
    created_conference_page.get_by_role("button", name="Save").click()
    expect(created_conference_page.locator("#timetable_canvas")).to_contain_text(
        f"1 - {test_data.session_contribution_name}"
    )


def test_add_break_session_to_timetable_in_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    created_conference_page.get_by_role("link", name=" Timetable").click()

    created_conference_page.get_by_role("link", name="Add new ").click()
    created_conference_page.get_by_role("link", name="Break").click()
    created_conference_page.get_by_role("textbox", name="Title").click()
    created_conference_page.get_by_role("textbox", name="Title").fill("Break")
    created_conference_page.get_by_role("button", name="Save").click()

    expect(created_conference_page.locator("#timetable_canvas")).to_contain_text(
        "Break"
    )


def test_payment_setup_in_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    created_conference_page.get_by_role("link", name="Registration").click()

    # Enable payments
    expect(
        created_conference_page.get_by_role("link", name="Enable payments")
    ).to_be_visible()

    created_conference_page.get_by_role("link", name="Enable payments").click()
    created_conference_page.get_by_role("button", name="OK").click()

    # Will enable a new "Payments" page, go to payment page to continue configuring
    created_conference_page.get_by_role("link", name="Payments").click()
    expect(created_conference_page.get_by_role("main")).to_contain_text("enabled")

    # Bank transfer is disabled at first
    expect(created_conference_page.locator("#plugin-payment_manual")).to_contain_text(
        "disabled"
    )
    expect(
        created_conference_page.get_by_role("link", name="Bank Transfer disabled")
    ).to_be_visible()

    # Enable Bank Transfer payment method
    created_conference_page.get_by_role("link", name="Bank Transfer disabled").click()
    created_conference_page.get_by_role("checkbox", name="Enabled").check()
    created_conference_page.get_by_role("textbox", name="Payment details").click()
    created_conference_page.get_by_role("textbox", name="Payment details").fill(
        "Payment details"
    )
    created_conference_page.get_by_role("button", name="Save").click()

    expect(created_conference_page.locator("#flashed-messages")).to_contain_text(
        "Settings for Bank Transfer saved"
    )


def test_registration_setup_in_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    created_conference_page.get_by_role("link", name="Registration").click()
    created_conference_page.get_by_role("link", name=" Create form").click()
    created_conference_page.get_by_role("textbox", name="Title").click()
    created_conference_page.get_by_role("textbox", name="Title").fill(
        test_data.registration_form_name
    )
    created_conference_page.get_by_role("button", name="Create", exact=True).click()

    expect(created_conference_page.locator("#flashed-messages")).to_contain_text(
        "Registration form has been successfully created"
    )


def test_registration_change_state_in_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    created_conference_page.get_by_role("link", name="Registration").click()
    created_conference_page.get_by_role("link", name=" Create form").click()
    created_conference_page.get_by_role("textbox", name="Title").click()
    created_conference_page.get_by_role("textbox", name="Title").fill(
        test_data.registration_form_name
    )
    created_conference_page.get_by_role("button", name="Create", exact=True).click()

    expect(created_conference_page.locator("#flashed-messages")).to_contain_text(
        "Registration form has been successfully created"
    )

    # Start
    created_conference_page.get_by_role("button", name="Start now").click()
    expect(created_conference_page.locator("#flashed-messages")).to_contain_text(
        f"Registrations for {test_data.registration_form_name} are now open"
    )

    # Close
    created_conference_page.get_by_role("link", name="Close now").click()
    expect(created_conference_page.locator("#flashed-messages")).to_contain_text(
        f"Registrations for {test_data.registration_form_name} are now closed"
    )

    # Reopen
    created_conference_page.get_by_role("button", name="Reopen now").click()
    created_conference_page.get_by_role("button", name="OK").click()
    expect(created_conference_page.locator("#flashed-messages")).to_contain_text(
        f"Registrations for {test_data.registration_form_name} are now open"
    )


def test_create_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    expect(created_conference_page.locator("#event-settings-data")).to_contain_text(
        test_data.conference_name
    )
    expect(created_conference_page.locator("#event-settings-location")).to_contain_text(
        test_data.room_name
    )
    expect(created_conference_page.locator("#event-settings-location")).to_contain_text(
        test_data.venue_name
    )


def test_delete_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    created_conference_page.get_by_role("button", name=" ").click()
    expect(
        created_conference_page.locator("#event-action-menu-actions")
    ).to_contain_text("Delete")
    created_conference_page.get_by_role("button", name="Delete").click()
    created_conference_page.get_by_role(
        "checkbox", name="I understand what this means"
    ).check()
    created_conference_page.get_by_role("button", name="Delete event").click()
    expect(created_conference_page.locator("#flashed-messages")).to_contain_text(
        f'Event "{test_data.conference_name}" successfully deleted.'
    )


def test_clone_conference(
    created_conference_page: Page, test_data: IndicoTestData
) -> None:
    created_conference_page.get_by_role("button", name=" Clone").click()
    created_conference_page.get_by_label("Clone Event").locator("div").filter(
        has_text="Clone Event"
    ).get_by_role("button").click()

    expect(created_conference_page.locator("#event-settings-data")).to_contain_text(
        test_data.conference_name
    )
    expect(created_conference_page.locator("#event-settings-location")).to_contain_text(
        test_data.room_name
    )
    expect(created_conference_page.locator("#event-settings-location")).to_contain_text(
        test_data.venue_name
    )
