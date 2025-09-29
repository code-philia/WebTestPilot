import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
from playwright.sync_api import Page

sys.path.append(str(Path(__file__).parent.parent))

from tracing_api import TracedPage, create_traced_page, traced_expect as expect
from .utilities import create_conference, create_lecture, create_meeting

pytest_plugins = ["pytest_xpath_plugin"]

INDICO_HOST = "http://localhost:8080"
USER = "admin@admin.com"
PASSWORD = "webtestpilot"


@dataclass
class IndicoTestData:
    @property
    def lecture_name(self) -> str:
        return "Lecture"

    @property
    def venue_name(self) -> str:
        return "Venue"

    @property
    def room_name(self) -> str:
        return "Room"

    @property
    def meeting_name(self) -> str:
        return "Meeting"

    @property
    def meeting_minute_name(self) -> str:
        return "Meeting Minute"

    @property
    def meeting_contribution_name(self) -> str:
        return "Meeting Contribution"

    @property
    def meeting_contribution_description(self) -> str:
        return "Description"

    @property
    def break_name(self) -> str:
        return "Break"

    @property
    def break_description(self) -> str:
        return "Description"

    @property
    def end_date(self) -> str:
        return "10/10/2040"

    @property
    def end_time(self) -> str:
        return "12"

    @property
    def conference_name(self) -> str:
        return "Conference"

    @property
    def conference_track_name(self) -> str:
        return "Track"

    @property
    def conference_track_group_name(self) -> str:
        return "Track group"

    @property
    def conference_track_code(self) -> str:
        return "T"

    @property
    def conference_track_description(self) -> str:
        return "Papers about"

    @property
    def conference_track_group_description(self) -> str:
        return "Many papers about"

    @property
    def email_notification_title(self) -> str:
        return "Email"

    @property
    def email_notification_rule_set(self) -> str:
        return "Notification rule"

    @property
    def session_type(self) -> str:
        return "Session type"

    @property
    def session_title(self) -> str:
        return "Session title"

    @property
    def session_title_updated(self) -> str:
        return "Session title updated"

    @property
    def session_description(self) -> str:
        return "Session description"

    @property
    def session_contribution_name(self) -> str:
        return "Session Contribution"

    @property
    def session_contribution_description(self) -> str:
        return "Description"

    @property
    def registration_form_name(self) -> str:
        return "Registration Form"


@pytest.fixture
def test_data() -> IndicoTestData:
    """Provides fresh, unique test data for each test"""
    return IndicoTestData()


def go_to_indico(page: TracedPage | Page) -> TracedPage | Page:
    page.goto(INDICO_HOST)
    return page


def login_to_indico(page: TracedPage | Page) -> TracedPage | Page:
    go_to_indico(page)
    page.get_by_role("link", name=" Login").click()
    page.get_by_role("textbox", name="Username or email").fill(USER)
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill(PASSWORD)
    page.get_by_role("button", name="Login with Indico").click()
    return page


@pytest.fixture
def logged_in_page(page: Page) -> TracedPage:
    traced_page = create_traced_page(page)
    login_to_indico(traced_page)
    expect(traced_page.locator("#global-menu")).to_contain_text("My profile")
    return traced_page


@pytest.fixture
def seed(logged_in_page: Page):
    create_lecture(logged_in_page)
    logged_in_page.wait_for_timeout(1000)
    logged_in_page.goto(INDICO_HOST)

    create_meeting(logged_in_page)
    logged_in_page.wait_for_timeout(1000)
    logged_in_page.goto(INDICO_HOST)

    create_conference(logged_in_page)
    return logged_in_page
