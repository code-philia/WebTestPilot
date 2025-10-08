import re

from invoiceninja.conftest import (
    InvoiceNinjaTestData,
    create_credit,
)
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect

from .utilities import go_to_credit_detail_page

# Tests for credit is similar to invoice.


def test_create_credit(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    logged_in_page.wait_for_timeout(500)
    insert_start_event_to_page(logged_in_page)

    page = create_credit(logged_in_page, test_data)

    expect(page.get_by_role("list")).to_contain_text("Edit Credit", timeout=10000)


def test_update_credit(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_credit_detail_page(page, test_data)

    # Update quantity
    page.get_by_role("row", name=test_data.product_name1).get_by_role("textbox").nth(
        3
    ).click()
    page.get_by_role("row", name=test_data.product_name1).get_by_role("textbox").nth(
        3
    ).fill("10")
    page.get_by_role("button", name="Save").click()

    expect(
        page.get_by_role("row", name=test_data.product_name1)
        .get_by_role("textbox")
        .nth(3)
    ).to_have_value("10")


def test_mark_sent_credit(
    logged_in_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_credit_detail_page(page, test_data)
    expect(page.get_by_role("main")).to_contain_text("Draft", timeout=1000)

    page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()
    page.get_by_role("button", name="Mark Sent").click()

    # Status updated
    expect(page.get_by_role("main")).to_contain_text("Sent")


def test_send_email_credit(
    logged_in_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_credit_detail_page(page, test_data)

    page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()

    page.get_by_role("link", name="Email Credit").click()
    page.get_by_role("button", name="Send Email").click()

    # Go back to credit page and check the status
    page.get_by_role("link", name=test_data.credit_number, exact=True).first.click()
    expect(page.get_by_role("main")).to_contain_text("Sent")


def test_archive_credit(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_credit_detail_page(page, test_data)

    page.wait_for_timeout(1000)

    expect(page.get_by_role("main")).to_contain_text("Draft", timeout=1000)

    page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()

    page.get_by_role("button", name="Archive").click()

    expect(page.get_by_role("main")).to_contain_text("Archived")
