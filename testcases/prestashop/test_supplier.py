from playwright.sync_api import Page
from prestashop.conftest import PrestaShopTestData
from tracing_api import traced_expect as expect

# 2 test cases


def test_create_supplier(logged_in_page: Page, test_data: PrestaShopTestData) -> None:
    page = logged_in_page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Brands & Suppliers").click()
    page.get_by_role("link", name="Suppliers", exact=True).click()
    page.get_by_role("link", name="add_circle_outline Add new").click()

    page.get_by_role("textbox", name="supplier_name input").fill(
        test_data.supplier_name
    )
    page.get_by_role("textbox", name="supplier_phone input").fill(
        test_data.supplier_phone
    )
    page.get_by_role("textbox", name="supplier_address input").fill(
        test_data.supplier_address
    )
    page.get_by_role("textbox", name="supplier_city input").fill(
        test_data.supplier_city
    )

    page.get_by_role("textbox", name="United Kingdom").click()
    page.get_by_role("option", name=test_data.supplier_country).click()

    # page.get_by_role("textbox", name="Aichi").click()
    # can't use this, because the value of state is different each time the page is opened
    state_container = page.locator(".js-supplier-state")
    # find the combobox and click it to expand the options
    state_container.get_by_role("combobox").click()
    page.get_by_role("option", name=test_data.supplier_state).click()

    page.get_by_role("radio", name=test_data.supplier_logo_active).check()
    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Successful creation")).to_be_visible()


def test_delete_supplier(
    created_supplier_page: Page, test_data: PrestaShopTestData
) -> None:
    page = created_supplier_page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Brands & Suppliers").click()
    page.get_by_role("link", name="Suppliers", exact=True).click()

    row = page.locator("tr", has_text=test_data.supplier_name).first
    row.locator("a").nth(2).click()
    page.get_by_role("link", name="delete Delete").click()
    page.get_by_role("button", name="Delete").click()
    expect(page.get_by_text("Successful deletion")).to_be_visible()
