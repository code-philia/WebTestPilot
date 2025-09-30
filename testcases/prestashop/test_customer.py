from playwright.sync_api import Page
from prestashop.conftest import PrestaShopTestData, create_customer
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect

from .utilities import go_to_customer_page

# 2 test cases


def test_create_customer(logged_in_page: Page, test_data: PrestaShopTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)

    page = create_customer(page)
    expect(page.get_by_text("Successful creation")).to_be_visible()


def test_delete_customer(logged_in_page: Page, test_data: PrestaShopTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_customer_page(page)

    row = page.get_by_role("row").filter(has_text=test_data.customer_email)
    page.wait_for_timeout(1000)
    row.locator("a").nth(1).click()
    # page.wait_for_timeout(2000)
    # page.get_by_role("link", name="delete Delete").click()
    delete_link = page.get_by_role("link", name="delete Delete")
    # wait for the link to be visible
    delete_link.wait_for()
    # now it is safe to click it
    delete_link.click()
    page.get_by_role("button", name="Delete").click()
    expect(page.get_by_text("Successful deletion")).to_be_visible()
