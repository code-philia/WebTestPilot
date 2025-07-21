from playwright.sync_api import Page, expect

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


# def test_move_lecture(created_lecture_page: Page) -> None:
#     created_lecture_page.get_by_role("button", name=" ").click()
#     created_lecture_page.get_by_role("button", name="Move").click()
#     created_lecture_page.get_by_role("button", name="Close").click()
#     created_lecture_page.locator("#global-menu").get_by_role(
#         "link", name="Home"
#     ).click()
#     created_lecture_page.get_by_role("link", name="Create event ").click()
#     created_lecture_page.get_by_role("link", name="Lecture").click()
#     created_lecture_page.get_by_role("textbox", name="Event title").fill("event title")
#     created_lecture_page.get_by_text("Add occurrence").click()
#     created_lecture_page.get_by_role("textbox", name="DD/MM/YYYY").nth(1).click()
#     created_lecture_page.get_by_role("textbox", name="DD/MM/YYYY").nth(1).dblclick()
#     created_lecture_page.get_by_role("textbox", name="DD/MM/YYYY").nth(1).press(
#         "ArrowLeft"
#     )
#     created_lecture_page.get_by_role("textbox", name="DD/MM/YYYY").nth(1).press(
#         "ArrowLeft"
#     )
#     created_lecture_page.get_by_role("textbox", name="DD/MM/YYYY").nth(1).press(
#         "ArrowLeft"
#     )
#     created_lecture_page.get_by_role("textbox", name="DD/MM/YYYY").nth(1).press(
#         "ArrowLeft"
#     )
#     created_lecture_page.get_by_role("textbox", name="DD/MM/YYYY").nth(1).press(
#         "ArrowLeft"
#     )
#     created_lecture_page.get_by_role("textbox", name="DD/MM/YYYY").nth(1).press(
#         "Shift+ArrowLeft"
#     )
#     created_lecture_page.get_by_role("textbox", name="DD/MM/YYYY").nth(1).fill(
#         "22/07/2025"
#     )
#     created_lecture_page.locator("#event-creation-occurrences-container").click()
#     created_lecture_page.get_by_text("Dates* Open a").click()
#     created_lecture_page.get_by_text("Add occurrence").click()
#     created_lecture_page.get_by_role("textbox", name="Venue").click()
#     created_lecture_page.get_by_role("textbox", name="Venue").fill("Shanghai")
#     created_lecture_page.get_by_role("textbox", name="Room").click()
#     created_lecture_page.get_by_role("textbox", name="Shanghai").fill("Shanghai")
#     created_lecture_page.get_by_role("textbox", name="Room").click()
#     created_lecture_page.get_by_role("textbox", name="Room").click()
#     created_lecture_page.get_by_role("textbox", name="Room").fill("102")
#     created_lecture_page.locator("#event-creation-protection_mode").get_by_text(
#         "Public"
#     ).click()
#     created_lecture_page.get_by_role("button", name="Create event", exact=True).click()
#     expect(
#         created_lecture_page.locator("#event-management-header-right")
#     ).to_contain_text("event title (1/3) 20 Jul")
#     expect(created_lecture_page.locator("#flashed-messages")).to_contain_text(
#         "2 additional events have been created. 22 Jul 2025: event title 23 Jul 2025: event title"
#     )
#     created_lecture_page.get_by_role("button", name=" ").click()
#     created_lecture_page.get_by_text("Settings Title event title").click()


def test_clone_lecture(created_lecture_page: Page, test_data: IndicoTestData) -> None:
    created_lecture_page.get_by_role("button", name=" Clone").click()
    created_lecture_page.get_by_label("Clone Event").locator("div").filter(
        has_text="Clone Event"
    ).get_by_role("button").click()
