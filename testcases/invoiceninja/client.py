import re

from playwright.sync_api import Page
from tracing_api import traced_expect as expect

from invoiceninja.conftest import InvoiceNinjaTestData


def test_create_client(
    created_client_page: Page, test_data: InvoiceNinjaTestData
) -> None:
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


def test_read_client(
    created_client_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    # Go back to listing page and check
    created_client_page.get_by_label("Breadcrumb").get_by_role(
        "link", name="Clients"
    ).click()
    created_client_page.get_by_role("textbox", name="Filter").click()
    created_client_page.get_by_role("textbox", name="Filter").fill(
        test_data.company_name
    )

    created_client_page.get_by_role("link", name=test_data.company_name).click(
        timeout=10000
    )
    expect(created_client_page.get_by_role("list")).to_contain_text(
        test_data.company_name
    )
    expect(created_client_page.get_by_role("main")).to_contain_text(
        test_data.company_website
    )
    expect(created_client_page.get_by_text(test_data.contact_email)).to_be_visible()
    expect(created_client_page.get_by_role("main")).to_contain_text(
        test_data.contact_email
    )


def test_update_client(
    created_client_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    created_client_page.get_by_role("button", name="Edit").click()

    created_client_page.locator("div").filter(
        has_text=re.compile(r"^Name$")
    ).get_by_role("textbox").click()
    created_client_page.locator("div").filter(
        has_text=re.compile(r"^Name$")
    ).get_by_role("textbox").fill(test_data.company_name_updated)

    created_client_page.get_by_role("button", name="Save").click()

    expect(
        created_client_page.get_by_text("Successfully updated client")
    ).to_be_visible()
    expect(
        created_client_page.get_by_role("link", name=test_data.company_name_updated)
    ).to_be_visible()
    expect(created_client_page.get_by_role("list")).to_contain_text(
        test_data.company_name_updated
    )
    expect(created_client_page.get_by_role("heading")).to_contain_text(
        test_data.company_name_updated
    )


def test_delete_client(
    created_client_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    created_client_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeEdit$")
    ).get_by_role("button").nth(2).click()

    created_client_page.get_by_role("button", name="Delete").click()
    expect(
        created_client_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully deleted client$"))
        .first
    ).to_be_visible()


def test_restore_client(
    created_client_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    # Delete first
    created_client_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeEdit$")
    ).get_by_role("button").nth(2).click()
    created_client_page.get_by_role("button", name="Delete").click()
    expect(
        created_client_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully deleted client$"))
        .first
    ).to_be_visible()

    # Restore
    created_client_page.get_by_role("button", name="Restore").click()
    expect(
        created_client_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully restored client$"))
        .first
    ).to_be_visible()


def test_purge_client(
    created_client_page: Page, test_data: InvoiceNinjaTestData
) -> None:
    created_client_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeEdit$")
    ).get_by_role("button").nth(2).click()

    # Delete
    created_client_page.get_by_role("button", name="Purge").click()
    created_client_page.get_by_role("button", name="Continue").click()
    expect(
        created_client_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully purged client$"))
        .first
    ).to_be_visible()

    expect(created_client_page.locator("tbody")).not_to_contain_text(
        test_data.company_name
    )
