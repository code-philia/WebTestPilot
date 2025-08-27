from playwright.sync_api import Page
from prestashop.conftest import PrestaShopTestData
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect

# 2 testcases


def test_create_brand(logged_in_page: Page, test_data: PrestaShopTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)

    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Brands & Suppliers").click()
    page.get_by_role(
        "link", name="add_circle_outline Add new brand", exact=True
    ).click()

    page.get_by_role("textbox", name="manufacturer_name input").fill(
        test_data.brand_name
    )
    page.locator("#manufacturer_description_1_ifr").content_frame.locator(
        "#tinymce"
    ).fill(test_data.brand_description)
    # page.get_by_role("button", name="Logo Choose file(s) Browse").set_input_files(
    #     test_data.brand_logo_file
    # )

    page.get_by_role("button", name="Save").click()
    expect(page.locator("#main-div")).to_contain_text("Successful creation")


def test_delete_brand(created_brand_page: Page, test_data: PrestaShopTestData) -> None:
    page = created_brand_page
    insert_start_event_to_page(page)

    # by human
    row = page.get_by_role("row").filter(has_text=test_data.brand_name)
    row.locator("a").nth(1).click()
    page.wait_for_timeout(1000)
    page.get_by_role("link", name="delete Delete").click()
    page.get_by_role("button", name="Delete").click()
    expect(page.get_by_text("Successful deletion")).to_be_visible()
