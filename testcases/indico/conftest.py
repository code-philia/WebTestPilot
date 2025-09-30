import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
from playwright.sync_api import Page
from playwright.async_api import Page as AsyncPage

sys.path.append(str(Path(__file__).parent.parent))

from tracing_api import TracedPage, create_traced_page, traced_expect as expect
from .utilities import create_conference, create_lecture, create_meeting

pytest_plugins = ["pytest_xpath_plugin"]

INDICO_HOST = "http://localhost:8080"
USER = "admin@admin.com"
PASSWORD = "webtestpilot"


@dataclass
class IndicoTestData:
    # Lecture properties
    lecture_name: str = "Lecture"

    # Venue properties
    venue_name: str = "Venue"
    room_name: str = "Room"

    # Meeting properties
    meeting_name: str = "Meeting"
    meeting_minute_name: str = "Meeting Minute"
    meeting_contribution_name: str = "Meeting Contribution"
    meeting_contribution_description: str = "Description"
    break_name: str = "Break"
    break_description: str = "Description"

    # Date/time properties
    end_date: str = "10/10/2040"
    end_time: str = "12"

    # Conference properties
    conference_name: str = "Conference"
    conference_track_name: str = "Track"
    conference_track_group_name: str = "Track group"
    conference_track_code: str = "T"
    conference_track_description: str = "Papers about"
    conference_track_group_description: str = "Many papers about"

    # Notification properties
    email_notification_title: str = "Email"
    email_notification_rule_set: str = "Notification rule"

    # Session properties
    session_type: str = "Session type"
    session_title: str = "Session title"
    session_title_updated: str = "Session title updated"
    session_description: str = "Session description"
    session_contribution_name: str = "Session Contribution"
    session_contribution_description: str = "Description"

    # Registration properties
    registration_form_name: str = "Registration Form"


@pytest.fixture
def test_data() -> IndicoTestData:
    """Provides fresh, unique test data for each test"""
    return IndicoTestData()


def go_to_indico(page: TracedPage | Page) -> TracedPage | Page:
    page.goto(INDICO_HOST)
    return page


async def go_to_indico_async(page: AsyncPage) -> AsyncPage:
    await page.goto(INDICO_HOST)
    return page


def login_to_indico(page: TracedPage | Page) -> TracedPage | Page:
    go_to_indico(page)
    page.get_by_role("link", name=" Login").click()
    page.get_by_role("textbox", name="Username or email").fill(USER)
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill(PASSWORD)
    page.get_by_role("button", name="Login with Indico").click()
    return page


async def login_to_indico_async(page: AsyncPage) -> AsyncPage:
    await go_to_indico_async(page)
    await page.get_by_role("link", name=" Login").click()
    await page.get_by_role("textbox", name="Username or email").fill(USER)
    await page.get_by_role("textbox", name="Password").click()
    await page.get_by_role("textbox", name="Password").fill(PASSWORD)
    await page.get_by_role("button", name="Login with Indico").click()
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
