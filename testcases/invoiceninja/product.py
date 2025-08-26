import re

from invoiceninja.conftest import InvoiceNinjaTestData, create_product
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect


def test_create_product(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    created_product_page = create_product(
        logged_in_page, test_data.product_name, test_data
    )

    insert_start_event_to_page(created_product_page)

    expect(created_product_page.get_by_role("list")).to_contain_text(
        "Edit Product", timeout=10000
    )


def test_update_product(
    created_product_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_product_page)

    expect(created_product_page.get_by_role("list")).to_contain_text("Edit Product")

    created_product_page.locator("div").filter(
        has_text=re.compile(r"^Item\*$")
    ).get_by_role("textbox").click()
    created_product_page.locator("div").filter(
        has_text=re.compile(r"^Item\*$")
    ).get_by_role("textbox").fill(test_data.product_name_updated)

    created_product_page.get_by_role("button", name="Save").click()

    expect(
        created_product_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully updated product$"))
        .first
    ).to_be_visible()


def test_delete_product(
    created_product_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_product_page)

    created_product_page.get_by_role("button").nth(4).click()
    created_product_page.get_by_role("button", name="Delete").click()

    expect(
        created_product_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully deleted product$"))
        .first
    ).to_be_visible()


def test_restore_product(
    created_product_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_product_page)

    created_product_page.get_by_role("button").nth(4).click()
    created_product_page.get_by_role("button", name="Delete").click()

    expect(
        created_product_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully deleted product$"))
        .first
    ).to_be_visible()

    created_product_page.get_by_role("button", name="Restore").click()
    expect(
        created_product_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully restored product$"))
        .first
    ).to_be_visible()


def test_archive_product(
    created_product_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_product_page)

    created_product_page.get_by_role("button").nth(4).click()
    created_product_page.get_by_role("button", name="Archive").click()
    expect(
        created_product_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully archived product$"))
        .first
    ).to_be_visible()
