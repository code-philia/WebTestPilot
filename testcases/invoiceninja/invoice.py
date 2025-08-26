import re

from invoiceninja.conftest import (
    InvoiceNinjaTestData,
    create_invoice,
    setup_data_for_create_invoice,
)
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect


def test_create_invoice(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    setup_data_for_create_invoice(logged_in_page, test_data)
    logged_in_page.wait_for_timeout(1000)

    insert_start_event_to_page(logged_in_page)

    created_invoice_page = create_invoice(logged_in_page, test_data)

    expect(created_invoice_page.get_by_role("list")).to_contain_text("Edit Invoice")


def test_update_invoice(
    created_invoice_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_invoice_page)

    created_invoice_page.get_by_role("button", name="Add Item").click()

    # Update quantity
    created_invoice_page.get_by_role("row", name=test_data.product_name1).get_by_role(
        "textbox"
    ).nth(3).click()
    created_invoice_page.get_by_role("row", name=test_data.product_name1).get_by_role(
        "textbox"
    ).nth(3).fill("10")
    created_invoice_page.get_by_role("button", name="Save").click()

    expect(
        created_invoice_page.get_by_role("row", name=test_data.product_name1)
        .get_by_role("textbox")
        .nth(3)
    ).to_have_value("10")


def test_mark_sent_invoice(
    created_invoice_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_invoice_page)

    expect(created_invoice_page.get_by_role("main")).to_contain_text(
        "Draft", timeout=1000
    )

    created_invoice_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()
    created_invoice_page.get_by_role("button", name="Mark Sent").click()

    # Status updated
    expect(created_invoice_page.get_by_role("main")).to_contain_text("Sent")


def test_mark_paid_invoice(
    created_invoice_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_invoice_page)

    expect(created_invoice_page.get_by_role("main")).to_contain_text(
        "Draft", timeout=1000
    )
    created_invoice_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()
    created_invoice_page.get_by_role("button", name="Mark Paid").click()

    # Status updated
    expect(created_invoice_page.get_by_role("main")).to_contain_text("Paid")


def test_send_email_invoice(
    created_invoice_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_invoice_page)

    created_invoice_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()

    created_invoice_page.get_by_role("link", name="Email Invoice").click()
    created_invoice_page.get_by_role("button", name="Send Email").click()

    # Go back to invoice page and check the status
    created_invoice_page.get_by_role(
        "link", name=test_data.invoice_number, exact=True
    ).first.click()
    expect(created_invoice_page.get_by_role("main")).to_contain_text("Sent")


def test_archive_invoice(
    created_invoice_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_invoice_page)

    expect(created_invoice_page.get_by_role("main")).to_contain_text(
        "Draft", timeout=1000
    )
    created_invoice_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()

    created_invoice_page.get_by_role("button", name="Archive").click()

    expect(created_invoice_page.get_by_role("main")).to_contain_text("Archived")
