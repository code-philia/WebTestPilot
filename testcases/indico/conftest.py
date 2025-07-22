from dataclasses import dataclass
from random import randint

import pytest
from playwright.sync_api import Page, expect

INDICO_HOST = "http://localhost:8080"
USER = "admin@admin.com"
PASSWORD = "webtestpilot"


@dataclass
class IndicoTestData:
    def __post_init__(self):
        self._unique_id = str(randint(100000, 999999))

    @property
    def lecture_name(self) -> str:
        return f"Lecture{self._unique_id}"

    @property
    def venue_name(self) -> str:
        return f"Venue{self._unique_id}"

    @property
    def room_name(self) -> str:
        return f"Room{self._unique_id}"

    @property
    def meeting_name(self) -> str:
        return f"Meeting{self._unique_id}"

    @property
    def meeting_contribution_name(self) -> str:
        return f"Meeting Contribution{self._unique_id}"

    @property
    def meeting_contribution_description(self) -> str:
        return f"Description{self._unique_id}"

    @property
    def break_name(self) -> str:
        return f"Break{self._unique_id}"

    @property
    def break_description(self) -> str:
        return f"Description{self._unique_id}"

    @property
    def end_date(self) -> str:
        return "22/07/2025"

    @property
    def end_time(self) -> str:
        return "12"


@pytest.fixture
def test_data() -> IndicoTestData:
    """Provides fresh, unique test data for each test"""
    return IndicoTestData()


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    page.goto(INDICO_HOST)
    page.get_by_role("link", name=" Login").click()
    page.get_by_role("textbox", name="Username or email").fill(USER)
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill(PASSWORD)
    page.get_by_role("button", name="Login with Indico").click()

    expect(page.locator("#global-menu")).to_contain_text("My profile")

    return page


@pytest.fixture
def created_lecture_page(logged_in_page: Page, test_data: IndicoTestData) -> Page:
    logged_in_page.get_by_role("link", name="Create event ").click()
    logged_in_page.get_by_role("link", name="Lecture").first.click()

    # Name
    logged_in_page.get_by_role("textbox", name="Event title").fill(
        test_data.lecture_name
    )

    # Venue and Room
    logged_in_page.get_by_role("textbox", name="Venue").click()
    logged_in_page.get_by_role("textbox", name="Venue").fill(test_data.venue_name)
    logged_in_page.get_by_role("textbox", name="Room").click()
    logged_in_page.get_by_role("textbox", name="Room").fill(test_data.room_name)

    # Event protection mode
    logged_in_page.locator("#event-creation-protection_mode").get_by_text(
        "Public"
    ).click()

    logged_in_page.get_by_role("button", name="Create event", exact=True).click()
    return logged_in_page


@pytest.fixture
def created_meeting_page(logged_in_page: Page, test_data: IndicoTestData) -> Page:
    logged_in_page.get_by_role("link", name="Create event ").click()
    logged_in_page.get_by_role("link", name="Meeting").first.click()

    # Name
    logged_in_page.get_by_role("textbox", name="Event title").fill(
        test_data.meeting_name
    )

    # End date
    logged_in_page.locator("#event-creation-end_dt").get_by_role(
        "textbox", name="DD/MM/YYYY"
    ).click()
    logged_in_page.locator("#event-creation-end_dt").get_by_role(
        "textbox", name="DD/MM/YYYY"
    ).fill(test_data.end_date)

    # End time
    logged_in_page.locator("#event-creation-end_dt").get_by_role(
        "textbox", name="--:--"
    ).click()
    logged_in_page.get_by_role("button", name=test_data.end_time).first.click()

    # Venue and Room
    logged_in_page.get_by_role("textbox", name="Venue").click()
    logged_in_page.get_by_role("textbox", name="Venue").fill(test_data.venue_name)
    logged_in_page.get_by_role("textbox", name="Room").click()
    logged_in_page.get_by_role("textbox", name="Room").fill(test_data.room_name)

    # Event protection mode
    logged_in_page.locator("#event-creation-protection_mode").get_by_text(
        "Public"
    ).click()

    logged_in_page.get_by_role("button", name="Create event", exact=True).click()

    return logged_in_page
