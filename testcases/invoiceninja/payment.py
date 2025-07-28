import re

from playwright.sync_api import Page
from tracing_api import traced_expect as expect

from invoiceninja.conftest import InvoiceNinjaTestData


def test_create_payment(
    created_payment_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    expect(created_payment_page.get_by_role("list")).to_contain_text("Edit Payment")


def test_update_payment(
    created_payment_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    expect(created_payment_page.get_by_role("list")).to_contain_text("Edit Payment")
    created_payment_page.locator("#date").fill(test_data.invoice_date)

    created_payment_page.get_by_role("button", name="Save").click()

    expect(
        created_payment_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully updated payment$"))
        .first
    ).to_be_visible()


def test_email_payment(
    created_payment_page: Page, test_data: InvoiceNinjaTestData
) -> None:
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
    expect(created_payment_page.locator("form")).to_contain_text("Completed")

    created_payment_page.get_by_role("button", name="More Actions").click()
    created_payment_page.get_by_role("button", name="Delete").click()

    expect(
        created_payment_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully deleted payment$"))
        .first
    ).to_be_visible()
    expect(created_payment_page.locator("form")).to_contain_text("Deleted")
