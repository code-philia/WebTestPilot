import json
import re

import pytest
from playwright.sync_api import Page
from tracing_api import traced_expect as expect

# 7 testcases

with open("test_data/buyer_data.json", "r") as f:
    data_list = json.load(f)


@pytest.mark.parametrize("buyer_data", data_list)
def test_add_to_cart(logged_in_buyer_page: Page, buyer_data: dict) -> None:
    page = logged_in_buyer_page
    page.get_by_role("link", name=buyer_data["product_name"]).nth(1).click()
    page.get_by_label("Size").select_option(buyer_data["size_cnt"])
    page.get_by_role("radio", name=buyer_data["color"]).check()
    page.get_by_role("button", name=" Add to cart").click()
    expect(
        page.get_by_role("heading", name=" Product successfully added")
    ).to_be_visible()


@pytest.mark.parametrize("buyer_data", data_list)
def test_search_product(logged_in_buyer_page: Page, buyer_data: dict) -> None:
    page = logged_in_buyer_page
    page.get_by_role("textbox", name="Search").fill(buyer_data["product_name"])
    page.get_by_role("textbox", name="Search").press("Enter")
    expect(
        page.get_by_role("article").filter(has_text=buyer_data["product_name"])
    ).to_be_visible()


@pytest.mark.parametrize("buyer_data", data_list)
def test_like_product(logged_in_buyer_page: Page, buyer_data: dict) -> None:
    page = logged_in_buyer_page
    page.get_by_role("textbox", name="Search").fill(buyer_data["product_name"])
    page.get_by_role("textbox", name="Search").press("Enter")
    product_article = page.get_by_role("article").filter(
        has_text=buyer_data["product_name"]
    )
    product_article.locator(".wishlist-button-add").click()
    page.get_by_role("listitem").filter(has_text="My wishlist").click()
    expect(page.get_by_text("Product added")).to_be_visible()


@pytest.mark.parametrize("buyer_data", data_list)
def test_add_and_remove_product(logged_in_buyer_page: Page, buyer_data: dict) -> None:
    page = logged_in_buyer_page
    # because this web doesn't memorize the product in the cart, so we need to add the product to the cart again
    page.get_by_role("link", name=buyer_data["product_name"]).nth(1).click()
    page.get_by_label("Size").select_option(buyer_data["size"])
    page.get_by_role("radio", name=buyer_data["color"]).check()
    page.get_by_role("button", name=" Add to cart").click()
    page.get_by_role("button", name="Continue shopping").click()
    page.get_by_role("link", name="Shopping cart link containing").click()
    product_item = page.get_by_role("listitem").filter(
        has_text=buyer_data["product_name"]
    )

    size_text = f"Size: {buyer_data['size']}"
    expect(product_item.get_by_text(size_text)).to_be_visible()

    color_text = f"Color: {buyer_data['color']}"
    expect(product_item.get_by_text(color_text)).to_be_visible()

    product_item.get_by_role("link", name="delete").click()
    expect(page.get_by_text("There are no more items in")).to_be_visible()


@pytest.mark.parametrize("buyer_data", data_list)
def test_dislike_product(logged_in_buyer_page: Page, buyer_data: dict) -> None:
    page = logged_in_buyer_page
    page.get_by_role("textbox", name="Search").fill(buyer_data["product_name"])
    page.get_by_role("textbox", name="Search").press("Enter")
    product_article = page.get_by_role("article").filter(
        has_text=buyer_data["product_name"]
    )
    product_article.locator(".wishlist-button-add").click()
    # page.get_by_role("button", name="favorite", exact=True).click()
    expect(page.get_by_text("Product successfully removed")).to_be_visible()


@pytest.mark.parametrize("buyer_data", data_list)
def test_write_review(logged_in_buyer_page: Page, buyer_data: dict) -> None:
    page = logged_in_buyer_page
    page.get_by_role("link", name=buyer_data["product_name"]).nth(1).click()
    page.get_by_label("Size").select_option(buyer_data["size_cnt"])
    page.get_by_role("radio", name=buyer_data["color"]).check()
    page.get_by_role("button", name="edit Be the first to write").click()
    page.locator(f".star-content > div:nth-child({buyer_data['star']})").first.click()
    page.get_by_role("textbox", name="Title*").fill(buyer_data["title"])
    page.get_by_role("textbox", name="Review*").fill(buyer_data["review"])
    page.get_by_role("button", name="Send").click()
    expect(page.get_by_text("Your comment has been")).to_be_visible()


@pytest.mark.parametrize("buyer_data", data_list)
def test_click_category(logged_in_buyer_page: Page, buyer_data: dict) -> None:
    page = logged_in_buyer_page
    page.get_by_role("link", name=buyer_data["main_category"]).click()
    page.get_by_title(buyer_data["sub_category"], exact=True).click()
    page.get_by_label(buyer_data["filters"]["availability"]).check()
    page.get_by_label(buyer_data["filters"]["selection"]).check()
    page.get_by_role("checkbox", name=buyer_data["filters"]["size"]).check()

    # don't set the expected_result, because the number of products is not fixed
    expect(
        page.get_by_text(re.compile(r"There (is|are) \d+ product(s)?\."))
    ).to_be_visible()
