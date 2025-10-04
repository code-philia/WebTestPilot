import re

from invoiceninja.conftest import InvoiceNinjaTestData, create_client
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect

from .utilities import go_to_client_detail_page


def test_create_client(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    insert_start_event_to_page(logged_in_page)

    created_client_page = create_client(
        logged_in_page, test_data.company_name, test_data
    )
    expect(created_client_page.get_by_role("list")).to_contain_text(
        test_data.company_name
    )
    expect(
        created_client_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully created client$"))
        .first
    ).to_be_visible()

    created_client_page.get_by_role("heading", name=test_data.company_name).click()
    expect(created_client_page.get_by_role("heading")).to_contain_text(
        test_data.company_name
    )


def test_read_client(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_client_detail_page(page, test_data)

    page.get_by_role("textbox", name="Filter").click()
    page.get_by_role("textbox", name="Filter").fill(test_data.company_name)

    page.get_by_role("link", name=test_data.company_name).click(timeout=10000)
    page.wait_for_timeout(5000)
    expect(page.get_by_role("list")).to_contain_text(test_data.company_name)
    expect(page.get_by_role("main")).to_contain_text(test_data.company_website)
    expect(page.get_by_text(test_data.contact_email)).to_be_visible()
    expect(page.get_by_role("main")).to_contain_text(test_data.contact_email)


def test_update_client(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_client_detail_page(page, test_data)

    page.get_by_role("button", name="Edit").click()

    page.locator("div").filter(has_text=re.compile(r"^Name$")).get_by_role(
        "textbox"
    ).click()
    page.locator("div").filter(has_text=re.compile(r"^Name$")).get_by_role(
        "textbox"
    ).fill(test_data.company_name_updated)

    page.get_by_role("button", name="Save").click()

    expect(page.get_by_text("Successfully updated client")).to_be_visible()
    expect(
        page.get_by_role("link", name=test_data.company_name_updated)
    ).to_be_visible()
    expect(page.get_by_role("list")).to_contain_text(test_data.company_name_updated)
    expect(page.get_by_role("heading")).to_contain_text(test_data.company_name_updated)


def test_delete_client(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_client_detail_page(page, test_data)

    page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeEdit$")
    ).get_by_role("button").nth(2).click()

    page.get_by_role("button", name="Delete").click()
    expect(
        page.locator("div")
        .filter(has_text=re.compile(r"^Successfully deleted client$"))
        .first
    ).to_be_visible()


def test_restore_client(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_client_detail_page(page, test_data)

    # Delete first
    page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeEdit$")
    ).get_by_role("button").nth(2).click()
    page.get_by_role("button", name="Delete").click()
    expect(
        page.locator("div")
        .filter(has_text=re.compile(r"^Successfully deleted client$"))
        .first
    ).to_be_visible()

    # Restore
    page.get_by_role("button", name="Restore").click()
    expect(
        page.locator("div")
        .filter(has_text=re.compile(r"^Successfully restored client$"))
        .first
    ).to_be_visible()


def test_purge_client(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> None:
    page = logged_in_page
    insert_start_event_to_page(page)
    go_to_client_detail_page(page, test_data)

    page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeEdit$")
    ).get_by_role("button").nth(2).click()

    # Delete
    page.get_by_role("button", name="Purge").click()
    page.get_by_role("button", name="Continue").click()
    expect(
        page.locator("div")
        .filter(has_text=re.compile(r"^Successfully purged client$"))
        .first
    ).to_be_visible()

    expect(page.locator("tbody")).not_to_contain_text(test_data.company_name)
