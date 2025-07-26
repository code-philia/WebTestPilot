import pytest
from playwright.sync_api import Page, expect
import json 

# 2 test cases
with open("test_data/customer_data.json", "r") as f:
    data_list = json.load(f)

@pytest.mark.parametrize("customer_data", data_list)
@pytest.mark.dependency(name='customer')
def test_create_customer(logged_in_page: Page, customer_data: dict) -> None: # 4. 添加 customer_data 参数
    page = logged_in_page
    page.get_by_role("link", name="account_circle Customers").click()
    page.get_by_role("link", name="Customers", exact=True).click()
    page.get_by_role("link", name="add_circle_outline Add new").click()

    page.locator("label").filter(has_text=customer_data["social_title"]).locator("i").click()
    page.get_by_role("textbox", name="customer_first_name input").fill(customer_data["first_name"])
    page.get_by_role("textbox", name="customer_last_name input").fill(customer_data["last_name"])
    page.get_by_role("textbox", name="* Email").fill(customer_data["email"])
    page.get_by_role("textbox", name="Password").fill(customer_data["password"])
    page.locator("#customer_birthday_year").select_option(customer_data["birth_year"])
    page.locator("#customer_birthday_month").select_option(customer_data["birth_month"])
    page.locator("#customer_birthday_day").select_option(customer_data["birth_day"])
    
    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Successful creation")).to_be_visible()

@pytest.mark.parametrize("customer_data", data_list)
#@pytest.mark.dependency(depends=["customer"])
def test_delete_customer(logged_in_page: Page, customer_data: dict) -> None:
    page = logged_in_page
    page.get_by_role("link", name="account_circle Customers").click()
    page.get_by_role("link", name="Customers", exact=True).click()
    row = page.get_by_role("row").filter(has_text=customer_data["email"])
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
    