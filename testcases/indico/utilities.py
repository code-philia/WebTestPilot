from playwright.sync_api import Page


def create_lecture(
    logged_in_page: Page,
    name: str = "Lecture",
    venue_name: str = "Venue",
    room_name: str = "Room",
) -> Page:
    logged_in_page.get_by_role("link", name="Create event ").click()
    logged_in_page.get_by_role("link", name="Lecture").first.click()

    # Name
    logged_in_page.get_by_role("textbox", name="Event title").fill(name)

    # Venue and Room
    logged_in_page.get_by_role("textbox", name="Venue").click()
    logged_in_page.get_by_role("textbox", name="Venue").fill(venue_name)
    logged_in_page.get_by_role("textbox", name="Room").click()
    logged_in_page.get_by_role("textbox", name="Room").fill(room_name)

    # Event protection mode
    logged_in_page.locator("#event-creation-protection_mode").get_by_text(
        "Public"
    ).click()

    logged_in_page.get_by_role("button", name="Create event", exact=True).click()
    return logged_in_page


def create_meeting(
    logged_in_page: Page,
    name: str = "Meeting",
    end_date: str = "10/10/2040",
    end_time: str = "12",
    venue_name: str = "Venue",
    room_name: str = "Room",
) -> Page:
    logged_in_page.get_by_role("link", name="Create event ").click()
    logged_in_page.get_by_role("link", name="Meeting").first.click()

    # Name
    logged_in_page.get_by_role("textbox", name="Event title").fill(name)

    # End date
    logged_in_page.locator("#event-creation-end_dt").get_by_role(
        "textbox", name="DD/MM/YYYY"
    ).click()
    logged_in_page.locator("#event-creation-end_dt").get_by_role(
        "textbox", name="DD/MM/YYYY"
    ).fill(end_date)

    # End time
    logged_in_page.locator("#event-creation-end_dt").get_by_role(
        "textbox", name="--:--"
    ).click()
    logged_in_page.get_by_role("button", name=end_time).first.click()

    # Venue and Room
    logged_in_page.get_by_role("textbox", name="Venue").click()
    logged_in_page.get_by_role("textbox", name="Venue").fill(venue_name)
    logged_in_page.get_by_role("textbox", name="Room").click()
    logged_in_page.get_by_role("textbox", name="Room").fill(room_name)

    # Event protection mode
    logged_in_page.locator("#event-creation-protection_mode").get_by_text(
        "Public"
    ).click()

    logged_in_page.get_by_role("button", name="Create event", exact=True).click()
    return logged_in_page


def create_conference(
    logged_in_page: Page,
    name: str = "Conference",
    end_date: str = "10/10/2040",
    end_time: str = "12",
    venue_name: str = "Venue",
    room_name: str = "Room",
) -> Page:
    logged_in_page.get_by_role("link", name="Create event ").click()
    logged_in_page.get_by_role("link", name="Conference").first.click()

    # Name
    logged_in_page.get_by_role("textbox", name="Event title").fill(name)

    # End date
    logged_in_page.locator("#event-creation-end_dt").get_by_role(
        "textbox", name="DD/MM/YYYY"
    ).click()
    logged_in_page.locator("#event-creation-end_dt").get_by_role(
        "textbox", name="DD/MM/YYYY"
    ).fill(end_date)

    # End time
    logged_in_page.locator("#event-creation-end_dt").get_by_role(
        "textbox", name="--:--"
    ).click()
    logged_in_page.get_by_role("button", name=end_time).first.click()

    # Venue and Room
    logged_in_page.get_by_role("textbox", name="Venue").click()
    logged_in_page.get_by_role("textbox", name="Venue").fill(venue_name)
    logged_in_page.get_by_role("textbox", name="Room").click()
    logged_in_page.get_by_role("textbox", name="Room").fill(room_name)

    # Event protection mode
    logged_in_page.locator("#event-creation-protection_mode").get_by_text(
        "Public"
    ).click()

    logged_in_page.get_by_role("button", name="Create event", exact=True).click()
    return logged_in_page


def navigate_to_conference_edit_page(page: Page) -> None:
    # From homepage, go to conference edit page
    page.get_by_role("link", name="Conference").click()
    page.get_by_role("link", name="").click()


def navigate_to_meeting_edit_page(page: Page) -> None:
    # From homepage, go to meeting edit page
    page.get_by_role("link", name="Meeting").click()
    page.get_by_role("link", name="").click()


def navigate_to_lecture_edit_page(page: Page) -> None:
    # From homepage, go to lecture edit page
    page.get_by_role("link", name="Lecture").click()
    page.get_by_role("link", name="").click()
