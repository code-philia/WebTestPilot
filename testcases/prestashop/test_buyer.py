import re

from playwright.sync_api import Page
from prestashop.conftest import PrestaShopTestData
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect

# 7 testcases


def test_add_to_cart(logged_in_buyer_page: Page, test_data: PrestaShopTestData) -> None:
    page = logged_in_buyer_page
    insert_start_event_to_page(page)

    page.get_by_role("link", name=test_data.buyer_product_name).nth(1).click()
    page.get_by_label("Size").select_option(test_data.buyer_size_cnt)
    page.get_by_role("radio", name=test_data.buyer_color).check()
    page.get_by_role("button", name=" Add to cart").click()
    expect(
        page.get_by_role("heading", name=" Product successfully added")
    ).to_be_visible()


def test_search_product(
    logged_in_buyer_page: Page, test_data: PrestaShopTestData
) -> None:
    page = logged_in_buyer_page
    insert_start_event_to_page(page)

    page.get_by_role("textbox", name="Search").fill(test_data.buyer_product_name)
    page.get_by_role("textbox", name="Search").press("Enter")
    expect(
        page.get_by_role("article").filter(has_text=test_data.buyer_product_name)
    ).to_be_visible()


def test_like_product(
    logged_in_buyer_page: Page, test_data: PrestaShopTestData
) -> None:
    page = logged_in_buyer_page
    insert_start_event_to_page(page)

    page.get_by_role("textbox", name="Search").fill(test_data.buyer_product_name)
    page.get_by_role("textbox", name="Search").press("Enter")
    product_article = page.get_by_role("article").filter(
        has_text=test_data.buyer_product_name
    )
    product_article.locator(".wishlist-button-add").click()
    page.get_by_role("listitem").filter(has_text="My wishlist").click()
    expect(page.get_by_text("Product added")).to_be_visible()


def test_add_and_remove_product(
    logged_in_buyer_page: Page, test_data: PrestaShopTestData
) -> None:
    page = logged_in_buyer_page
    insert_start_event_to_page(page)

    # because this web doesn't memorize the product in the cart, so we need to add the product to the cart again
    page.get_by_role("link", name=test_data.buyer_product_name).nth(1).click()
    page.get_by_label("Size").select_option(test_data.buyer_size)
    page.get_by_role("radio", name=test_data.buyer_color).check()
    page.get_by_role("button", name=" Add to cart").click()
    page.get_by_role("button", name="Continue shopping").click()
    page.get_by_role("link", name="Shopping cart link containing").click()
    product_item = page.get_by_role("listitem").filter(
        has_text=test_data.buyer_product_name
    )

    size_text = f"Size: {test_data.buyer_size}"
    expect(product_item.get_by_text(size_text)).to_be_visible()

    color_text = f"Color: {test_data.buyer_color}"
    expect(product_item.get_by_text(color_text)).to_be_visible()

    product_item.get_by_role("link", name="delete").click()
    expect(page.get_by_text("There are no more items in")).to_be_visible()


def test_dislike_product(
    created_wishlist_item_page: Page, test_data: PrestaShopTestData
) -> None:
    page = created_wishlist_item_page
    insert_start_event_to_page(page)

    # Product is already in wishlist, search for it and remove it
    page.get_by_role("textbox", name="Search").fill(test_data.buyer_product_name)
    page.get_by_role("textbox", name="Search").press("Enter")
    product_article = page.get_by_role("article").filter(
        has_text=test_data.buyer_product_name
    )
    product_article.locator(".wishlist-button-add").click()
    page.get_by_role("listitem").filter(has_text="My wishlist").click()

    product_article.locator(".wishlist-button-add").click()
    expect(page.get_by_text("Product successfully removed")).to_be_visible()


def test_write_review(
    logged_in_buyer_page: Page, test_data: PrestaShopTestData
) -> None:
    page = logged_in_buyer_page
    insert_start_event_to_page(page)

    page.get_by_role("link", name=test_data.buyer_product_name).nth(1).click()
    page.get_by_role("button", name="edit Be the first to write").click()
    page.locator(f".star-content > div:nth-child({test_data.buyer_star})").first.click()
    page.get_by_role("textbox", name="Title*").fill(test_data.buyer_title)
    page.get_by_role("textbox", name="Review*").fill(test_data.buyer_review)
    page.get_by_role("button", name="Send").click()
    expect(page.get_by_text("Your comment has been")).to_be_visible()


def test_click_category(
    logged_in_buyer_page: Page, test_data: PrestaShopTestData
) -> None:
    page = logged_in_buyer_page
    insert_start_event_to_page(page)

    page.get_by_role("link", name=test_data.buyer_main_category).click()
    page.get_by_title(test_data.buyer_sub_category, exact=True).click()
    page.get_by_label(test_data.buyer_filter_availability).check()
    page.get_by_label(test_data.buyer_filter_selection).check()
    page.get_by_role("checkbox", name=test_data.buyer_filter_size).check()

    # don't set the expected_result, because the number of products is not fixed
    expect(
        page.get_by_text(re.compile(r"There (is|are) \d+ product(s)?\."))
    ).to_be_visible()
