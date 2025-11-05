from playwright.sync_api import Page
from prestashop.conftest import PrestaShopTestData, create_supplier
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect

from .utilities import go_to_supplier_page

# 2 test cases


def test_create_supplier(logged_in_page: Page) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)

    page = create_supplier(page)
    expect(page.get_by_text("Successful creation")).to_be_visible()


def test_delete_supplier(logged_in_page: Page, test_data: PrestaShopTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_supplier_page(page)

    row = page.locator("tr", has_text=test_data.supplier_name).first
    row.locator("a").nth(2).click()
    page.get_by_role("link", name="delete Delete").click()
    page.get_by_role("button", name="Delete").click()
    expect(page.get_by_text("Successful deletion")).to_be_visible()
    expect(page.get_by_text(test_data.supplier_name)).not_to_be_visible()
