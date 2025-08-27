import re

from invoiceninja.conftest import (
    InvoiceNinjaTestData,
    create_expense,
    setup_data_for_expense_create,
)
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect


def test_create_expense(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    created_client_page = setup_data_for_expense_create(logged_in_page, test_data)
    created_client_page.wait_for_timeout(500)

    # START
    insert_start_event_to_page(logged_in_page)

    created_expense_page = create_expense(created_client_page, test_data)
    expect(created_expense_page.get_by_role("list")).to_contain_text("Edit Expense")
    expect(created_expense_page.get_by_role("main")).to_contain_text("Logged")


def test_update_expense(
    created_expense_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_expense_page)

    created_expense_page.locator("div").filter(
        has_text=re.compile(r"^Amount$")
    ).get_by_role("textbox").click()
    created_expense_page.locator("div").filter(
        has_text=re.compile(r"^Amount$")
    ).get_by_role("textbox").fill(test_data.expense_amount_updated)

    created_expense_page.get_by_role("button", name="Save").click()

    expect(
        created_expense_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully updated expense$"))
        .first
    ).to_be_visible(timeout=1000)


def test_archive_expense(
    created_expense_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_expense_page)

    created_expense_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()
    created_expense_page.get_by_role("button", name="Archive").click()

    expect(
        created_expense_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully archived expense$"))
        .first
    ).to_be_visible(timeout=1000)

    expect(created_expense_page.get_by_role("main")).to_contain_text("Archived")


def test_restore_expense(
    created_expense_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_expense_page)

    created_expense_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()
    created_expense_page.get_by_role("button", name="Archive").click()

    expect(
        created_expense_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully archived expense$"))
        .first
    ).to_be_visible(timeout=1000)

    expect(created_expense_page.get_by_role("main")).to_contain_text("Archived")

    created_expense_page.get_by_role("button", name="Restore").click()

    expect(
        created_expense_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully restored expense$"))
        .first
    ).to_be_visible(timeout=3000)
    expect(created_expense_page.get_by_role("main")).to_contain_text("Logged")


def test_delete_expense(
    created_expense_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_expense_page)

    created_expense_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()
    created_expense_page.get_by_role("button", name="Delete").click()

    expect(
        created_expense_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully deleted expense$"))
        .first
    ).to_be_visible(timeout=1000)
    expect(created_expense_page.get_by_role("main")).to_contain_text("Deleted")


def test_clone_expense(
    created_expense_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    insert_start_event_to_page(created_expense_page)

    created_expense_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()
    created_expense_page.get_by_role("button", name="Clone", exact=True).click()

    created_expense_page.locator("div").filter(
        has_text=re.compile(r"^Amount$")
    ).get_by_role("textbox").click()
    created_expense_page.locator("div").filter(
        has_text=re.compile(r"^Amount$")
    ).get_by_role("textbox").fill(test_data.expense_amount_updated)

    created_expense_page.get_by_role("button", name="Save").click()

    expect(created_expense_page.get_by_role("main")).to_contain_text("Logged")
