import re
import pytest
from playwright.sync_api import Page, expect
import json

# 3 test cases
with open("test_data/product_data.json", "r", encoding="utf-8") as f:
    data_list = json.load(f)

@pytest.mark.parametrize("test_data", data_list)
@pytest.mark.dependency(name='product')
def test_create_virtual_product(logged_in_page: Page, test_data: dict) -> None:
    page = logged_in_page
    product_info = test_data["virtual_product"]
    
    page.get_by_role("link", name="store Catalog").click()
    page.locator("#subtab-AdminProducts").get_by_role("link", name="Products").click()
    page.get_by_role("link", name="add_circle_outline New product").click()
    page.frame_locator("iframe[name=\"modal-create-product-iframe\"]")
    # page.get_by_role("button", name="Virtual product qr_code").click()
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Virtual product qr_code").click()
    page.get_by_role("button", name="Add new product").click()


    page.get_by_role("textbox", name="product_header_name_1 input").fill(product_info["name"])
    page.locator("input.dz-hidden-input").set_input_files(product_info["image_file"])
    page.locator("#product_description_description_1_ifr").content_frame.locator("#tinymce").fill(product_info["description"])
    page.locator("#product_description_description_short_1_ifr").content_frame.locator("#tinymce").fill(product_info["short_description"])
    page.get_by_role("button", name="Add categories").click()
    page.get_by_text(product_info["category"], exact=True).click()
    page.get_by_role("button", name="Apply").click()
    page.get_by_role("textbox", name="No brand").click()
    page.get_by_role("option", name=product_info["brand"]).click()
    
    page.get_by_role("tab", name="Details").click()
    page.get_by_role("textbox", name="product_details_references_reference input").fill(product_info["reference"])
    
    page.get_by_role("tab", name="Virtual product").click()
    page.get_by_role("spinbutton", name="Add or subtract items").fill(product_info["quantity"])
    
    page.get_by_role("tab", name="Pricing").click()
    page.get_by_role("textbox", name="Retail price (tax excl.)").fill(product_info["price_tax_excl"])
    page.locator("#product_pricing_wholesale_price").fill(product_info["wholesale_price"])

    page.get_by_role("tab", name="SEO").click()
    page.get_by_role("textbox", name="product_seo_link_rewrite_1").fill(product_info["link_rewrite"])
    page.get_by_label("Redirection when offline").select_option(product_info["offline_redirection"])

    page.get_by_role("tab", name="Options").click()
    page.locator("#product_options_suppliers_supplier_ids").get_by_text("Accessories supplier").click()
    page.locator("#product_options_suppliers_supplier_ids").get_by_text("Fashion supplier").click()
    
    page.get_by_role("textbox", name="product_options_product_suppliers_1_reference input").fill(product_info["suppliers"]["fashion_supplier_ref"])
    page.locator("#product_options_product_suppliers_1_price_tax_excluded").fill(product_info["suppliers"]["fashion_supplier_price"])
    page.get_by_role("textbox", name="product_options_product_suppliers_2_reference input").fill(product_info["suppliers"]["accessories_supplier_ref"])
    page.locator("#product_options_product_suppliers_2_price_tax_excluded").fill(product_info["suppliers"]["accessories_supplier_price"])
    
    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Successful update")).to_be_visible()

@pytest.mark.parametrize("test_data", data_list)
@pytest.mark.dependency(name='standard_product')
def test_create_standard_product(logged_in_page: Page, test_data: dict) -> None:
    page = logged_in_page
    product_info = test_data["standard_product"]

    page.get_by_role("link", name="store Catalog").click()
    page.locator("#subtab-AdminProducts").get_by_role("link", name="Products").click()
    page.get_by_role("link", name="add_circle_outline New product").click()
    page.frame_locator("iframe[name=\"modal-create-product-iframe\"]")
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Standard product checkroom").click()
    page.get_by_role("button", name="Add new product").click()
    
    page.get_by_role("textbox", name="product_header_name_1 input").fill(product_info["name"])
    page.locator("input.dz-hidden-input").set_input_files(product_info["image_file"])
    page.locator("#product_description_description_1_ifr").content_frame.locator("#tinymce").fill(product_info["description"])
    page.locator("#product_description_description_short_1_ifr").content_frame.locator("#tinymce").fill(product_info["short_description"])
    
    page.get_by_role("button", name="Add categories").click()
    page.get_by_role("textbox", name="Search categories").fill(product_info["category_search"])
    page.locator("div").filter(has_text=re.compile(f"^{product_info['category_search']}$")).nth(2).click()
    page.get_by_text("Accessories", exact=True).click()
    page.get_by_role("button", name="Apply").click()
    page.get_by_role("textbox", name="Home").click()
    page.get_by_role("option", name=product_info["default_category"]).click()
    page.get_by_role("textbox", name="No brand").click()
    page.get_by_role("option", name=product_info["brand"]).click()
    
    page.get_by_role("tab", name="Details").click()
    page.get_by_role("textbox", name="product_details_references_reference input").fill(product_info["reference"])
    page.get_by_role("button", name="add_circle Add a feature").click()
    page.get_by_role("textbox", name="Choose a feature").click()
    page.get_by_role("option", name="Composition").click()
    page.get_by_role("textbox", name="Choose a value").click()
    page.get_by_role("option", name=product_info["features"]["composition"]).click()
    page.get_by_role("button", name="add_circle Add a feature").click()
    page.get_by_role("textbox", name="Choose a feature").click()
    page.get_by_role("option", name="Property").click()
    page.get_by_role("textbox", name="Choose a value").click()
    page.get_by_role("option", name=product_info["features"]["property"]).click()
    
    page.get_by_role("tab", name="Stocks").click()
    page.get_by_role("spinbutton", name="Add or subtract items").fill(product_info["quantity"])

    page.get_by_role("tab", name="Pricing").click()
    page.get_by_role("textbox", name="Retail price (tax excl.)").fill(product_info["price_tax_excl"])
    page.locator("#product_pricing_wholesale_price").fill(product_info["wholesale_price"])

    page.get_by_role("tab", name="Shipping").click()
    page.get_by_role("textbox", name="Weight").fill(product_info["weight"])

    page.get_by_role("tab", name="SEO").click()
    page.get_by_role("textbox", name="product_seo_link_rewrite_1").fill(product_info["link_rewrite"])
    page.get_by_label("Redirection when offline").select_option("default")

    page.get_by_role("tab", name="Options").click()
    page.wait_for_timeout(1000)
    page.locator("#product_options_suppliers_supplier_ids").get_by_text("Accessories supplier").click()
    
    
    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Successful update")).to_be_visible()


@pytest.mark.parametrize("test_data", data_list)
#@pytest.mark.dependency(depends=['product'])
def test_delete_one_product(logged_in_page: Page, test_data: dict) -> None:
    page = logged_in_page
    product_to_delete = test_data["delete_product_name"]
    
    page.get_by_role("link", name="store Catalog").click()
    page.locator("#subtab-AdminProducts").get_by_role("link", name="Products").click()
    
    page.get_by_role("textbox", name="product_name input").fill(product_to_delete)
    page.get_by_role("textbox", name="product_name input").press("Enter")
    page.get_by_role("button", name="search Search").click()
    page.wait_for_load_state("networkidle")
    #page.locator("tr:nth-child(1) > .bulk_action-type").click()
    #page.locator(".bulk_action-type").first.click()
    page.locator(".btn-group > a:nth-child(2)").first.click()
    page.get_by_role("link", name="delete Delete").click()
    page.get_by_role("button", name="Delete").click()
    expect(page.get_by_text("Successful deletion")).to_be_visible()