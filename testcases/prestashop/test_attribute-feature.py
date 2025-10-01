import re

from playwright.sync_api import Page
from prestashop.conftest import PrestaShopTestData
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect

from .utilities import go_to_attribute_page, go_to_feature_page

# 6 testcases


def test_create_attribute(logged_in_page: Page, test_data: PrestaShopTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)

    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Attributes & Features").click()
    page.get_by_role("link", name="Add new attribute").click()
    page.locator("#name_1").fill(test_data.attribute_name)
    page.locator("#public_name_1").fill(test_data.attribute_public_name)
    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Successful creation")).to_be_visible()


def test_create_attribute_value(
    logged_in_page: Page, test_data: PrestaShopTestData
) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_attribute_page(page)

    page.get_by_role("link", name="Add new value").click()
    # use the name of the attribute to select the option
    page.locator("#id_attribute_group").select_option(label=test_data.attribute_name)
    page.locator("#name_1").fill(test_data.attribute_value)
    page.get_by_role("button", name="Save", exact=True).click()
    expect(page.get_by_text("Successful creation")).to_be_visible()


def test_delete_attribute(logged_in_page: Page, test_data: PrestaShopTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_attribute_page(page)

    # page.get_by_role("row", name="Weight 1  5  View ").get_by_role("button").click()
    # Find the row that contains the specific attribute name, then find the button within that row
    page.get_by_role("row", name=re.compile(test_data.attribute_name)).get_by_role(
        "button"
    ).click()
    page.get_by_role("link", name="Delete").click()
    page.get_by_role("button", name="Yes").click()
    expect(page.get_by_text("Successful deletion")).to_be_visible()


def test_create_feature(logged_in_page: Page, test_data: PrestaShopTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_feature_page(page)

    page.get_by_role("link", name=" Add new feature", exact=True).click()
    page.locator("#name_1").fill(test_data.feature_name)
    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Successful creation")).to_be_visible()


def test_create_feature_value(
    logged_in_page: Page, test_data: PrestaShopTestData
) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_feature_page(page)

    page.get_by_role("link", name=" Add new feature value").click()
    # use the name of the feature to select the option
    page.locator("#id_feature").select_option(label=test_data.feature_name)
    page.locator("#value_1").fill(test_data.feature_value)
    page.get_by_role("button", name="Save", exact=True).click()
    expect(page.get_by_text("× Successful creation")).to_be_visible()


def test_delete_feature(logged_in_page: Page, test_data: PrestaShopTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_feature_page(page)

    # page.get_by_role("row", name="Season 1  3  View ").get_by_role("button").click()
    page.get_by_role("row", name=re.compile(test_data.feature_name)).get_by_role(
        "button"
    ).click()
    page.get_by_role("link", name="Delete").click()
    page.get_by_role("button", name="Yes").click()
    expect(page.get_by_text("Successful deletion")).to_be_visible()
