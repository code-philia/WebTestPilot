import re

from playwright.sync_api import Page
from prestashop.conftest import PrestaShopTestData, create_virtual_product
from tracing_api import traced_expect as expect

# 3 test cases


def test_create_virtual_product(
    logged_in_page: Page, test_data: PrestaShopTestData
) -> None:
    page = logged_in_page
    page = create_virtual_product(page, test_data)

    expect(page.get_by_text("Successful update")).to_be_visible()


def test_create_standard_product(
    logged_in_page: Page, test_data: PrestaShopTestData
) -> None:
    page = logged_in_page

    page.get_by_role("link", name="store Catalog").click()
    page.locator("#subtab-AdminProducts").get_by_role("link", name="Products").click()
    page.get_by_role("link", name="add_circle_outline New product").click()
    page.frame_locator('iframe[name="modal-create-product-iframe"]')
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Standard product checkroom").click()
    page.get_by_role("button", name="Add new product").click()

    page.get_by_role("textbox", name="product_header_name_1 input").fill(
        test_data.standard_product_name
    )
    # page.locator("input.dz-hidden-input").set_input_files(
    #     test_data.standard_product_image_file
    # )
    page.locator("#product_description_description_1_ifr").content_frame.locator(
        "#tinymce"
    ).fill(test_data.standard_product_description)
    page.locator("#product_description_description_short_1_ifr").content_frame.locator(
        "#tinymce"
    ).fill(test_data.standard_product_short_description)

    # Categories
    page.get_by_role("button", name="Add categories").click()
    page.get_by_role("textbox", name="Search categories").fill(
        test_data.standard_product_category_search
    )
    page.locator("div").filter(
        has_text=re.compile(f"^{test_data.standard_product_category_search}$")
    ).nth(2).click()
    page.get_by_text("Accessories", exact=True).click()
    page.get_by_role("button", name="Apply").click()
    page.get_by_role("textbox", name="Home").click()
    page.get_by_role("option", name=test_data.standard_product_default_category).click()

    # Brand
    page.get_by_role("textbox", name="No brand").click()
    page.get_by_role("option", name=test_data.standard_product_brand).click()

    # Tab details
    page.get_by_role("tab", name="Details").click()
    page.get_by_role("textbox", name="product_details_references_reference input").fill(
        test_data.standard_product_reference
    )
    page.get_by_role("button", name="add_circle Add a feature").click()
    page.get_by_role("textbox", name="Choose a feature").click()
    page.get_by_role("option", name="Composition").click()
    page.get_by_role("textbox", name="Choose a value").click()
    page.get_by_role(
        "option", name=test_data.standard_product_feature_composition
    ).click()
    page.get_by_role("button", name="add_circle Add a feature").click()
    page.get_by_role("textbox", name="Choose a feature").click()
    page.get_by_role("option", name="Property").click()
    page.get_by_role("textbox", name="Choose a value").click()
    page.get_by_role("option", name=test_data.standard_product_feature_property).click()

    # Tab stocks
    page.get_by_role("tab", name="Stocks").click()
    page.get_by_role("spinbutton", name="Add or subtract items").fill(
        test_data.standard_product_quantity
    )

    # Tab pricing
    page.get_by_role("tab", name="Pricing").click()
    page.get_by_role("textbox", name="Retail price (tax excl.)").fill(
        test_data.standard_product_price_tax_excl
    )
    page.locator("#product_pricing_wholesale_price").fill(
        test_data.standard_product_wholesale_price
    )

    page.get_by_role("tab", name="Shipping").click()
    page.get_by_role("textbox", name="Weight").fill(test_data.standard_product_weight)

    # Tab SEO
    page.get_by_role("tab", name="SEO").click()
    page.get_by_role("textbox", name="product_seo_link_rewrite_1").fill(
        test_data.standard_product_link_rewrite
    )
    page.get_by_label("Redirection when offline").select_option("default")

    # Tab Options
    page.get_by_role("tab", name="Options").click()
    page.wait_for_timeout(1000)
    page.locator("#product_options_suppliers_supplier_ids").get_by_text(
        "Accessories supplier"
    ).click()

    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Successful update")).to_be_visible()


def test_delete_one_product(
    created_product_for_delete_page: Page, test_data: PrestaShopTestData
) -> None:
    page = created_product_for_delete_page

    page.get_by_role("textbox", name="product_name input").fill(
        test_data.delete_product_name
    )
    page.get_by_role("textbox", name="product_name input").press("Enter")
    page.get_by_role("button", name="search Search").click()
    page.wait_for_load_state("networkidle")
    # page.locator("tr:nth-child(1) > .bulk_action-type").click()
    # page.locator(".bulk_action-type").first.click()
    page.locator(".btn-group > a:nth-child(2)").first.click()
    page.get_by_role("link", name="delete Delete").click()
    page.get_by_role("button", name="Delete").click()
    expect(page.get_by_text("Successful deletion")).to_be_visible()
