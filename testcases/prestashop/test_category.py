import pytest
from playwright.sync_api import Page, expect
import json

# 3 test cases
with open("test_data/category_data.json", "r") as f:
    data_list = json.load(f)

@pytest.mark.parametrize("test_data", data_list)
@pytest.mark.dependency(name='category')
def test_create_category(logged_in_page: Page, test_data: dict) -> None:
    page = logged_in_page
    parent_category_info = test_data["parent_category"]

    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Categories").click()
    page.get_by_role("link", name="add_circle_outline Add new").click()
    
    page.get_by_role("textbox", name="category_name_1 input").fill(parent_category_info["name"])
    page.get_by_text("expand_more Expand").click()
    page.get_by_text(parent_category_info["parent"], exact=True).click()
    page.locator("#category_description_1_ifr").content_frame.locator("#tinymce").fill(parent_category_info["description"])
    page.locator("#category_cover_image").set_input_files(parent_category_info["image_file"])
    page.locator("#category_thumbnail_image").set_input_files(parent_category_info["image_file"])
    page.get_by_role("button", name="Choose file(s) Browse").set_input_files(parent_category_info["image_file"])
    page.get_by_role("textbox", name="category_link_rewrite_1 input").fill(parent_category_info["link_rewrite"])
    
    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Successful creation")).to_be_visible()

@pytest.mark.parametrize("test_data", data_list)
@pytest.mark.dependency(depends=["category"])
def test_create_son_category(logged_in_page: Page, test_data: dict) -> None:
    page = logged_in_page
    child_category_info = test_data["child_category"]

    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Categories").click()
    page.get_by_role("link", name="add_circle_outline Add new").click()
    
    page.get_by_role("textbox", name="category_name_1 input").fill(child_category_info["name"])
    page.get_by_text("expand_more").click()
    # mayebe there exist other better way to handle this instead of wait_for_timeout
    page.wait_for_timeout(2000)
    page.locator("label").filter(has_text=child_category_info["parent"]).locator("i").click()
    page.locator("#category_description_1_ifr").content_frame.locator("#tinymce").fill(child_category_info["description"])
    page.locator("#category_cover_image").set_input_files(child_category_info["image_file"])
    page.locator("#category_thumbnail_image").set_input_files(child_category_info["image_file"])
    page.get_by_role("button", name="Choose file(s) Browse").set_input_files(child_category_info["image_file"])
    page.get_by_role("textbox", name="category_link_rewrite_1 input").fill(child_category_info["link_rewrite"])
    
    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Successful creation")).to_be_visible()


@pytest.mark.parametrize("test_data", data_list)
@pytest.mark.dependency(depends=["category"])
def test_delete_category(logged_in_page: Page, test_data: dict) -> None:
    page = logged_in_page
    parent_category_name = test_data["parent_category"]["name"]

    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Categories").click()
    
    row = page.get_by_role("row").filter(has_text=parent_category_name)
    row.locator("a").nth(2).click()
    page.get_by_role("link", name="delete Delete").click()
    page.locator("#delete_categories_delete_mode i").first.click()
    page.get_by_role("button", name="Delete").click()
    
    expect(page.get_by_text("Successful deletion")).to_be_visible()