import re

from invoiceninja.conftest import (
    InvoiceNinjaTestData,
    create_credit,
    setup_data_for_credit_create,
)
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect

# Tests for credit is similar to invoice.


def test_create_credit(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    setup_data_for_credit_create(logged_in_page, test_data)
    logged_in_page.wait_for_timeout(500)

    insert_start_event_to_page(logged_in_page)

    created_credit_page = create_credit(logged_in_page, test_data)

    expect(created_credit_page.get_by_role("list")).to_contain_text(
        "Edit Credit", timeout=10000
    )


def test_update_credit(
    created_credit_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_credit_page)

    # Update quantity
    created_credit_page.get_by_role("row", name=test_data.product_name1).get_by_role(
        "textbox"
    ).nth(3).click()
    created_credit_page.get_by_role("row", name=test_data.product_name1).get_by_role(
        "textbox"
    ).nth(3).fill("10")
    created_credit_page.get_by_role("button", name="Save").click()

    expect(
        created_credit_page.get_by_role("row", name=test_data.product_name1)
        .get_by_role("textbox")
        .nth(3)
    ).to_have_value("10")


def test_mark_sent_credit(
    created_credit_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_credit_page)

    expect(created_credit_page.get_by_role("main")).to_contain_text(
        "Draft", timeout=1000
    )

    created_credit_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()
    created_credit_page.get_by_role("button", name="Mark Sent").click()

    # Status updated
    expect(created_credit_page.get_by_role("main")).to_contain_text("Sent")


def test_send_email_credit(
    created_credit_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_credit_page)

    created_credit_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()

    created_credit_page.get_by_role("link", name="Email Credit").click()
    created_credit_page.get_by_role("button", name="Send Email").click()

    # Go back to credit page and check the status
    created_credit_page.get_by_role(
        "link", name=test_data.credit_number, exact=True
    ).first.click()
    expect(created_credit_page.get_by_role("main")).to_contain_text("Sent")


def test_archive_credit(
    created_credit_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_credit_page)

    created_credit_page.wait_for_timeout(1000)

    expect(created_credit_page.get_by_role("main")).to_contain_text(
        "Draft", timeout=1000
    )

    created_credit_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()

    created_credit_page.get_by_role("button", name="Archive").click()

    expect(created_credit_page.get_by_role("main")).to_contain_text("Archived")
