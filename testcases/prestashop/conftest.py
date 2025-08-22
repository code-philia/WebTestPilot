import sys
from pathlib import Path

import pytest
from playwright.sync_api import Page

sys.path.append(str(Path(__file__).parent.parent))

from tracing_api import create_traced_page

pytest_plugins = ["pytest_xpath_plugin"]

BASE_URL = "http://localhost:8083"
# BASE_URL = "http://49.232.8.242:8083"


def go_to_prestashop(page: Page) -> Page:
    page.goto(f"{BASE_URL}/webtestpilot/")
    return page


def go_to_buyer_page(page: Page) -> Page:
    page.goto(f"{BASE_URL}/")
    return page


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    page = create_traced_page(page, enable_tracing=True)
    page = login_to_prestashop(page)
    yield page
    page.save_traces()


def login_to_prestashop(page: Page) -> Page:
    go_to_prestashop(page)
    page.get_by_role("textbox", name="Email address").click()
    page.get_by_role("textbox", name="Email address").fill("admin@admin.com")
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill("admin12345")
    page.get_by_role("button", name="Log in").click()
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Products", exact=True).first.click()
    page.get_by_title("Close Toolbar").click()
    page.get_by_role("link", name="trending_up Dashboard").click()
    # expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()
    return page


@pytest.fixture
def logged_in_buyer_page(page: Page) -> Page:
    page = create_traced_page(page, enable_tracing=True)
    page = login_to_prestashop_as_buyer(page)
    yield page
    page.save_traces()


def login_to_prestashop_as_buyer(page: Page) -> Page:
    page = go_to_buyer_page(page)
    page.get_by_role("link", name=" Sign in").click()

    # Must create user with docker exec -it prestashop-app-1 php /var/www/html/tools/create_user.php
    # See webapps/prestashop/Dockerfile for more info
    page.get_by_role("textbox", name="Email").fill("auto.customer@example.com")
    page.get_by_role("textbox", name="Password input").fill("mypassword")
    page.get_by_role("button", name="Sign in").click()
    return page
