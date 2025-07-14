import pytest
from playwright.sync_api import Page, expect
import json

# 2 test cases
with open("test_data/supplier_data.json", "r", encoding="utf-8") as f:
    data_list = json.load(f)


@pytest.mark.parametrize("supplier_data", data_list)
@pytest.mark.dependency(name='supplier')
def test_create_supplier(logged_in_page: Page, supplier_data: dict) -> None:
    page = logged_in_page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Brands & Suppliers").click()
    page.get_by_role("link", name="Suppliers", exact=True).click()
    page.get_by_role("link", name="add_circle_outline Add new").click()

    page.get_by_role("textbox", name="supplier_name input").fill(supplier_data["name"])
    page.get_by_role("textbox", name="supplier_phone input").fill(supplier_data["phone"])
    page.get_by_role("textbox", name="supplier_address input").fill(supplier_data["address"])
    page.get_by_role("textbox", name="supplier_city input").fill(supplier_data["city"])
 
    page.get_by_role("textbox", name="United Kingdom").click() 
    page.get_by_role("option", name=supplier_data["country"]).click()
   
    #page.get_by_role("textbox", name="Aichi").click() 
    #can't use this, because the value of state is different each time the page is opened
    state_container = page.locator(".js-supplier-state")
    # find the combobox and click it to expand the options
    state_container.get_by_role("combobox").click()
    page.get_by_role("option", name=supplier_data["state"]).click()

    page.get_by_role("radio", name=supplier_data["logo_active"]).check()
    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Successful creation")).to_be_visible()

@pytest.mark.parametrize("supplier_data", data_list)
@pytest.mark.dependency(depends=['supplier'])
def test_delete_supplier(logged_in_page: Page, supplier_data: dict) -> None:
    page = logged_in_page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Brands & Suppliers").click()
    page.get_by_role("link", name="Suppliers", exact=True).click()
    
    row = page.locator("tr", has_text=supplier_data["name"]).first
    row.locator("a").nth(2).click()
    page.get_by_role("link", name="delete Delete").click()
    page.get_by_role("button", name="Delete").click()
    expect(page.get_by_text("Successful deletion")).to_be_visible()