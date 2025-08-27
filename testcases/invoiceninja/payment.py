import re

from invoiceninja.conftest import (
    InvoiceNinjaTestData,
    create_payment,
    setup_data_for_create_payment,
)
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect


def test_create_payment(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    created_invoice_page = setup_data_for_create_payment(logged_in_page, test_data)

    insert_start_event_to_page(created_invoice_page)

    created_payment_page = create_payment(created_invoice_page, test_data)

    expect(created_payment_page.get_by_role("list")).to_contain_text("Edit Payment")


def test_update_payment(
    created_payment_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_payment_page)

    expect(created_payment_page.get_by_role("list")).to_contain_text("Edit Payment")
    created_payment_page.locator("#transaction_reference").fill("123123")

    created_payment_page.get_by_role("button", name="Save").click()

    expect(
        created_payment_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully updated payment$"))
        .first
    ).to_be_visible()


def test_email_payment(
    created_payment_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_payment_page)

    expect(created_payment_page.locator("form")).to_contain_text("Completed")

    created_payment_page.get_by_role("button", name="More Actions").click()
    created_payment_page.get_by_role("button", name="Email Payment").click()

    expect(
        created_payment_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully emailed payment$"))
        .first
    ).to_be_visible()


def test_archive_payment(
    created_payment_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_payment_page)

    expect(created_payment_page.locator("form")).to_contain_text("Completed")

    created_payment_page.get_by_role("button", name="More Actions").click()
    created_payment_page.get_by_role("button", name="Archive").click()

    expect(
        created_payment_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully archived payment$"))
        .first
    ).to_be_visible()
    expect(created_payment_page.locator("form")).to_contain_text("Archived")


def test_delete_payment(
    created_payment_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_payment_page)

    expect(created_payment_page.locator("form")).to_contain_text("Completed")

    created_payment_page.get_by_role("button", name="More Actions").click()
    created_payment_page.get_by_role("button", name="Delete").click()

    expect(
        created_payment_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully deleted payment$"))
        .first
    ).to_be_visible()
    expect(created_payment_page.locator("form")).to_contain_text("Deleted")
