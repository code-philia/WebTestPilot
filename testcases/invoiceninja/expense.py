import re

from invoiceninja.conftest import (
    InvoiceNinjaTestData,
    create_expense,
)
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect

from .utilities import go_to_expense_detail_page


def test_create_expense(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    insert_start_event_to_page(logged_in_page)

    page = create_expense(logged_in_page, test_data)
    expect(page.get_by_role("list")).to_contain_text("Edit Expense")
    expect(page.get_by_role("main")).to_contain_text("Logged")


def test_update_expense(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_expense_detail_page(page)

    page.locator("div").filter(has_text=re.compile(r"^Amount$")).get_by_role(
        "textbox"
    ).click()
    page.locator("div").filter(has_text=re.compile(r"^Amount$")).get_by_role(
        "textbox"
    ).fill(test_data.expense_amount_updated)

    page.get_by_role("button", name="Save").click()

    expect(
        page.locator("div")
        .filter(has_text=re.compile(r"^Successfully updated expense$"))
        .first
    ).to_be_visible(timeout=1000)


def test_archive_expense(logged_in_page: Page) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)

    page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()
    page.get_by_role("button", name="Archive").click()

    expect(
        page.locator("div")
        .filter(has_text=re.compile(r"^Successfully archived expense$"))
        .first
    ).to_be_visible(timeout=1000)

    expect(page.get_by_role("main")).to_contain_text("Archived")


def test_restore_expense(logged_in_page: Page) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)

    page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()
    page.get_by_role("button", name="Archive").click()

    expect(
        page.locator("div")
        .filter(has_text=re.compile(r"^Successfully archived expense$"))
        .first
    ).to_be_visible(timeout=1000)

    expect(page.get_by_role("main")).to_contain_text("Archived")

    page.get_by_role("button", name="Restore").click()

    expect(
        page.locator("div")
        .filter(has_text=re.compile(r"^Successfully restored expense$"))
        .first
    ).to_be_visible(timeout=3000)
    expect(page.get_by_role("main")).to_contain_text("Logged")


def test_delete_expense(logged_in_page: Page) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)

    page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()
    page.get_by_role("button", name="Delete").click()

    expect(
        page.locator("div")
        .filter(has_text=re.compile(r"^Successfully deleted expense$"))
        .first
    ).to_be_visible(timeout=1000)
    expect(page.get_by_role("main")).to_contain_text("Deleted")


def test_clone_expense(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)

    page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()
    page.get_by_role("button", name="Clone", exact=True).click()

    page.locator("div").filter(has_text=re.compile(r"^Amount$")).get_by_role(
        "textbox"
    ).click()
    page.locator("div").filter(has_text=re.compile(r"^Amount$")).get_by_role(
        "textbox"
    ).fill(test_data.expense_amount_updated)

    page.get_by_role("button", name="Save").click()

    expect(page.get_by_role("main")).to_contain_text("Logged")
