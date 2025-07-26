import re
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    page.goto("http://49.232.8.242:8083/webtestpilot/")
    page.get_by_role("textbox", name="Email address").click()
    page.get_by_role("textbox", name="Email address").fill("admin@admin.com")
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill("admin12345")
    page.get_by_role("button", name="Log in").click()
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Products", exact=True).first.click()
    page.get_by_title("Close Toolbar").click()
    page.get_by_role("link", name="trending_up Dashboard").click()
    return page
    # expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

@pytest.fixture
def logged_in_buyer_page(page: Page) -> Page:
    page.goto("http://49.232.8.242:8083/")
    page.get_by_role("link", name=" Sign in").click()
    page.get_by_role("textbox", name="Email").fill("pub@prestashop.com")
    page.get_by_role("textbox", name="Password input").fill("testTEST123.")
    page.get_by_role("button", name="Sign in").click()
    return page