import re

from invoiceninja.conftest import (
    InvoiceNinjaTestData,
    create_payment,
)
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect

from .utilities import go_to_payment_detail_page


def test_create_payment(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    insert_start_event_to_page(logged_in_page)

    created_payment_page = create_payment(
        logged_in_page, test_data.invoice_number_sent, test_data
    )

    expect(created_payment_page.get_by_role("list")).to_contain_text("Edit Payment")


def test_update_payment(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    go_to_payment_detail_page(logged_in_page)

    expect(logged_in_page.get_by_role("list")).to_contain_text("Edit Payment")
    logged_in_page.locator("#transaction_reference").fill("123123")

    logged_in_page.get_by_role("button", name="Save").click()

    expect(
        logged_in_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully updated payment$"))
        .first
    ).to_be_visible()


def test_email_payment(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    go_to_payment_detail_page(logged_in_page)

    expect(logged_in_page.locator("form")).to_contain_text("Completed")

    logged_in_page.get_by_role("button", name="More Actions").click()
    logged_in_page.get_by_role("button", name="Email Payment").click()

    expect(
        logged_in_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully emailed payment$"))
        .first
    ).to_be_visible()


def test_archive_payment(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    go_to_payment_detail_page(logged_in_page)

    expect(logged_in_page.locator("form")).to_contain_text("Completed")

    logged_in_page.get_by_role("button", name="More Actions").click()
    logged_in_page.get_by_role("button", name="Archive").click()

    expect(
        logged_in_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully archived payment$"))
        .first
    ).to_be_visible()
    expect(logged_in_page.locator("form")).to_contain_text("Archived")


def test_delete_payment(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    insert_start_event_to_page(logged_in_page)
    go_to_payment_detail_page(logged_in_page)

    expect(logged_in_page.locator("form")).to_contain_text("Completed")

    logged_in_page.get_by_role("button", name="More Actions").click()
    logged_in_page.get_by_role("button", name="Delete").click()

    expect(
        logged_in_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully deleted payment$"))
        .first
    ).to_be_visible()
    expect(logged_in_page.locator("form")).to_contain_text("Deleted")
