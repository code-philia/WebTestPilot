from playwright.sync_api import Page
from prestashop.conftest import PrestaShopTestData
from tracing_api import traced_expect as expect

# 2 test cases


def test_create_customer(logged_in_page: Page, test_data: PrestaShopTestData) -> None:
    page = logged_in_page
    page.get_by_role("link", name="account_circle Customers").click()
    page.get_by_role("link", name="Customers", exact=True).click()
    page.get_by_role("link", name="add_circle_outline Add new").click()

    page.locator("label").filter(has_text=test_data.customer_social_title).locator(
        "i"
    ).click()
    page.get_by_role("textbox", name="customer_first_name input").fill(
        test_data.customer_first_name
    )
    page.get_by_role("textbox", name="customer_last_name input").fill(
        test_data.customer_last_name
    )
    page.get_by_role("textbox", name="* Email").fill(test_data.customer_email)
    page.get_by_role("textbox", name="Password").fill(test_data.customer_password)
    page.locator("#customer_birthday_year").select_option(test_data.customer_birth_year)
    page.locator("#customer_birthday_month").select_option(
        test_data.customer_birth_month
    )
    page.locator("#customer_birthday_day").select_option(test_data.customer_birth_day)

    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Successful creation")).to_be_visible()


def test_delete_customer(
    created_customer_page: Page, test_data: PrestaShopTestData
) -> None:
    page = created_customer_page

    row = page.get_by_role("row").filter(has_text=test_data.customer_email)
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
