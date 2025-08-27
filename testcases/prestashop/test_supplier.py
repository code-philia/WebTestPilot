from playwright.sync_api import Page
from prestashop.conftest import PrestaShopTestData, create_supplier
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect

# 2 test cases


def test_create_supplier(logged_in_page: Page, test_data: PrestaShopTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)

    page = create_supplier(page, test_data)
    expect(page.get_by_text("Successful creation")).to_be_visible()


def test_delete_supplier(
    created_supplier_page: Page, test_data: PrestaShopTestData
) -> None:
    page = created_supplier_page
    insert_start_event_to_page(page)

    row = page.locator("tr", has_text=test_data.supplier_name).first
    row.locator("a").nth(2).click()
    page.get_by_role("link", name="delete Delete").click()
    page.get_by_role("button", name="Delete").click()
    expect(page.get_by_text("Successful deletion")).to_be_visible()
