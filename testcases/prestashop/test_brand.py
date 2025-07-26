import pytest
from playwright.sync_api import Page, expect
import json 

# 2 testcases

with open("test_data/brand_data.json", "r") as f:
    data_list = json.load(f)


@pytest.mark.parametrize("brand_data", data_list)
@pytest.mark.dependency(name='brand')
def test_create_brand(logged_in_page: Page, brand_data: dict) -> None: 
    page = logged_in_page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Brands & Suppliers").click()
    page.get_by_role("link", name="add_circle_outline Add new brand", exact=True).click()
    
    page.get_by_role("textbox", name="manufacturer_name input").fill(brand_data["name"])
    page.locator("#manufacturer_description_1_ifr").content_frame.locator("#tinymce").fill(brand_data["description"]) 
    page.get_by_role("button", name="Logo Choose file(s) Browse").set_input_files(brand_data["logo_file"])
    
    page.get_by_role("button", name="Save").click()
    expect(page.locator("#main-div")).to_contain_text("Successful creation")

@pytest.mark.parametrize("brand_data", data_list)
@pytest.mark.dependency(depends=["brand"])
def test_delete_brand(logged_in_page: Page, brand_data: dict) -> None:
    page = logged_in_page
    page.get_by_role("link", name="shopping_basket Orders").click()
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Brands & Suppliers").click()
    # by human
    row = page.get_by_role("row").filter(has_text=brand_data["name"])
    row.locator("a").nth(1).click()
    page.wait_for_timeout(1000)
    page.get_by_role("link", name="delete Delete").click()
    page.get_by_role("button", name="Delete").click()
    expect(page.get_by_text("Successful deletion")).to_be_visible()