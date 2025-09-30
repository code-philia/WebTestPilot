from playwright.sync_api import Page
from prestashop.conftest import PrestaShopTestData
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect

from .utilities import go_to_category_page

# 3 test cases


def test_create_category(logged_in_page: Page, test_data: PrestaShopTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)

    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Categories").click()
    page.get_by_role("link", name="add_circle_outline Add new").click()

    page.get_by_role("textbox", name="category_name_1 input").fill(
        test_data.parent_category_name
    )
    page.get_by_text("expand_more Expand").click()
    page.get_by_text(test_data.parent_category_parent, exact=True).click()
    page.locator("#category_description_1_ifr").content_frame.locator("#tinymce").fill(
        test_data.parent_category_description
    )
    page.get_by_role("textbox", name="category_link_rewrite_1 input").fill(
        test_data.parent_category_link_rewrite
    )

    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Successful creation")).to_be_visible()


def test_create_son_category(
    logged_in_page: Page, test_data: PrestaShopTestData
) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)

    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Categories").click()
    page.get_by_role("link", name="add_circle_outline Add new").click()

    page.get_by_role("textbox", name="category_name_1 input").fill(
        test_data.child_category_name
    )
    page.wait_for_timeout(1000)
    page.get_by_text("expand_more").click()
    # mayebe there exist other better way to handle this instead of wait_for_timeout
    page.wait_for_timeout(2000)
    # page.locator("label").filter(has_text=child_category_info["parent"]).locator("i").click()
    page.get_by_text(test_data.child_category_parent).click()
    page.locator("#category_description_1_ifr").content_frame.locator("#tinymce").fill(
        test_data.child_category_description
    )
    page.get_by_role("textbox", name="category_link_rewrite_1 input").fill(
        test_data.child_category_link_rewrite
    )

    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Successful creation")).to_be_visible()


def test_delete_category(logged_in_page: Page, test_data: PrestaShopTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_category_page(page)

    row = page.get_by_role("row").filter(has_text=test_data.parent_category_name)
    row.locator("a").nth(2).click()
    page.wait_for_timeout(1000)
    page.get_by_role("link", name="delete Delete").click()
    page.wait_for_timeout(1000)
    page.locator("#delete_categories_delete_mode i").first.click()
    page.get_by_role("button", name="Delete").click()

    expect(page.get_by_text("Successful deletion")).to_be_visible()
