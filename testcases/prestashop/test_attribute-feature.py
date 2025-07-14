from os import name
from pyexpat import features
import re
import pytest
from playwright.sync_api import Page, expect
import json

with open("test_data/attribute-feature_data.json", "r") as f:
    data_list = json.load(f)


# 6 testcases

@pytest.mark.parametrize("attribute_data", data_list["attributes"])
@pytest.mark.dependency(name='attribute')
def test_create_attribute(logged_in_page: Page, attribute_data: dict) -> None:
    page = logged_in_page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Attributes & Features").click()
    page.get_by_role("link", name="Add new attribute").click()
    page.locator("#name_1").fill(attribute_data["name"])
    page.locator("#public_name_1").fill(attribute_data["public_name"])
    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Successful creation")).to_be_visible()

@pytest.mark.parametrize("attribute_data", data_list["attributes"])
@pytest.mark.dependency(depends=["attribute"])
def test_create_attribute_value(logged_in_page: Page, attribute_data: dict) -> None:
    page = logged_in_page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Attributes & Features").click()
    page.get_by_role("link", name="Add new value").click()
    # use the name of the attribute to select the option
    page.locator("#id_attribute_group").select_option(label="Weight")
    page.locator("#name_1").fill(attribute_data["value"])
    page.get_by_role("button", name="Save", exact=True).click()
    expect(page.get_by_text("Successful creation")).to_be_visible()

@pytest.mark.parametrize("attribute_data", data_list["attributes"])
# @pytest.mark.dependency(depends=["attribute"])
def test_delete_attribute(logged_in_page: Page, attribute_data: dict) -> None:
    page = logged_in_page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Attributes & Features").click()
    #page.get_by_role("row", name="Weight 1  5  View ").get_by_role("button").click()
    # Find the row that contains the specific attribute name, then find the button within that row
    page.get_by_role("row", name=re.compile(attribute_data["name"])).get_by_role("button").click()
    page.get_by_role("link", name="Delete").click()
    page.get_by_role("button", name="Yes").click()
    expect(page.get_by_text("Successful deletion")).to_be_visible()

@pytest.mark.parametrize("feature_data", data_list["features"])
@pytest.mark.dependency(name='feature')
def test_create_feature(logged_in_page: Page, feature_data: dict) -> None:
    page = logged_in_page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Attributes & Features").click()
    page.get_by_role("link", name="Features", exact=True).click()
    page.get_by_role("link", name=" Add new feature", exact=True).click()
    page.locator("#name_1").fill(feature_data["name"])
    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Successful creation")).to_be_visible()

@pytest.mark.parametrize("feature_data", data_list["features"])
@pytest.mark.dependency(depends=["feature"])
def test_create_feature_value(logged_in_page: Page, feature_data: dict) -> None:
    page = logged_in_page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Attributes & Features").click()
    page.get_by_role("link", name="Features", exact=True).click()
    page.get_by_role("link", name=" Add new feature value").click()
    # use the name of the feature to select the option  
    page.locator("#id_feature").select_option(label=feature_data["name"])
    page.locator("#value_1").fill(feature_data["value"])
    page.get_by_role("button", name="Save", exact=True).click()
    expect(page.get_by_text("× Successful creation")).to_be_visible()

@pytest.mark.parametrize("feature_data", data_list["features"])
#@pytest.mark.dependency(depends=["feature"])
def test_delete_feature(logged_in_page: Page, feature_data: dict) -> None:
    page = logged_in_page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Attributes & Features").click()
    page.get_by_role("link", name="Features", exact=True).click()
    #page.get_by_role("row", name="Season 1  3  View ").get_by_role("button").click()
    page.get_by_role("row", name=re.compile(feature_data["name"])).get_by_role("button").click()
    page.get_by_role("link", name="Delete").click()
    page.get_by_role("button", name="Yes").click()
    expect(page.get_by_text("Successful deletion")).to_be_visible()