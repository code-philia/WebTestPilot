import re
from typing import TYPE_CHECKING
from playwright.sync_api import Page

from tracing_api import traced_expect as expect

if TYPE_CHECKING:
    from .conftest import InvoiceNinjaTestData


def create_client(
    logged_in_page: Page, company_name: str, test_data: "InvoiceNinjaTestData"
) -> Page:
    logged_in_page.get_by_role("link", name="Clients").click()
    logged_in_page.get_by_role("link", name="New Client").click()

    # Fill the form
    logged_in_page.locator("div").filter(has_text=re.compile(r"^Name$")).get_by_role(
        "textbox"
    ).click()
    logged_in_page.locator("div").filter(has_text=re.compile(r"^Name$")).get_by_role(
        "textbox"
    ).fill(company_name)
    logged_in_page.locator("div").filter(has_text=re.compile(r"^Number$")).get_by_role(
        "textbox"
    ).click()
    logged_in_page.locator("div").filter(has_text=re.compile(r"^Number$")).get_by_role(
        "textbox"
    ).fill(company_name)

    logged_in_page.locator("div").filter(
        has_text=re.compile(r"^ID Number$")
    ).get_by_role("textbox").click()
    logged_in_page.locator("div").filter(
        has_text=re.compile(r"^ID Number$")
    ).get_by_role("textbox").fill(company_name)
    logged_in_page.locator("div").filter(
        has_text=re.compile(r"^VAT Number$")
    ).get_by_role("textbox").click()
    logged_in_page.locator("div").filter(
        has_text=re.compile(r"^VAT Number$")
    ).get_by_role("textbox").fill(test_data.vat_number)
    logged_in_page.locator("div").filter(has_text=re.compile(r"^Website$")).get_by_role(
        "textbox"
    ).click()
    logged_in_page.locator("div").filter(has_text=re.compile(r"^Website$")).get_by_role(
        "textbox"
    ).fill(test_data.company_website)

    # Phone number
    logged_in_page.locator(
        "div:nth-child(8) > .mt-4 > section > .relative > .w-full"
    ).click()
    logged_in_page.locator(
        "div:nth-child(8) > .mt-4 > section > .relative > .w-full"
    ).fill(test_data.company_phone)

    # Contact information
    logged_in_page.locator("#first_name_0").click()
    logged_in_page.locator("#first_name_0").fill(test_data.contact_first_name)
    logged_in_page.locator("#last_name_0").click()
    logged_in_page.locator("#last_name_0").fill(test_data.contact_last_name)
    logged_in_page.locator("#email_0").click()
    logged_in_page.locator("#email_0").fill(test_data.contact_email)
    logged_in_page.locator("#phone_0").click()
    logged_in_page.locator("#phone_0").fill(test_data.contact_phone)

    logged_in_page.get_by_role("button", name="Save").click()
    logged_in_page.wait_for_timeout(1000)
    return logged_in_page


def create_product(
    logged_in_page: Page, product_name: str, test_data: "InvoiceNinjaTestData"
) -> Page:
    logged_in_page.wait_for_timeout(500)
    logged_in_page.get_by_role("link", name="Products").first.click()
    logged_in_page.get_by_role("link", name="New Product").click()

    # Name
    logged_in_page.locator("div").filter(has_text=re.compile(r"^Item\*$")).get_by_role(
        "textbox"
    ).click()
    logged_in_page.locator("div").filter(has_text=re.compile(r"^Item\*$")).get_by_role(
        "textbox"
    ).fill(product_name)

    # Description
    logged_in_page.locator('textarea[type="text"]').click()
    logged_in_page.locator('textarea[type="text"]').fill(test_data.product_description)

    # Price
    logged_in_page.locator("div").filter(has_text=re.compile(r"^Price$")).get_by_role(
        "textbox"
    ).click()
    logged_in_page.locator("div").filter(has_text=re.compile(r"^Price$")).get_by_role(
        "textbox"
    ).fill(test_data.product_price)

    # Default quantity
    logged_in_page.locator("div").filter(
        has_text=re.compile(r"^Default Quantity$")
    ).get_by_role("textbox").dblclick()
    logged_in_page.locator("div").filter(
        has_text=re.compile(pattern=r"^Default Quantity$")
    ).get_by_role("textbox").fill(test_data.product_default_quantity)

    # Max quantity
    logged_in_page.locator("div").filter(
        has_text=re.compile(r"^Max Quantity$")
    ).get_by_role("textbox").click()
    logged_in_page.locator("div").filter(
        has_text=re.compile(r"^Max Quantity$")
    ).get_by_role("textbox").fill(test_data.product_max_quantity)

    logged_in_page.get_by_role("button", name="Save").click()

    expect(
        logged_in_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully created product$"))
        .first
    ).to_be_visible()

    return logged_in_page


def create_invoice(
    logged_in_page: Page,
    invoice_number: str,
    test_data: "InvoiceNinjaTestData",
    status: str = "draft",
) -> Page:
    logged_in_page.get_by_role("link", name="Invoices", exact=True).click()
    logged_in_page.get_by_role("link", name="New Invoice").click()

    # Choose client for invoice
    logged_in_page.get_by_test_id("combobox-input-field").click()
    logged_in_page.get_by_test_id("combobox-input-field").fill(test_data.company_name)
    logged_in_page.get_by_role("option", name=test_data.company_name).click()

    # Invoice number
    logged_in_page.locator("#number").click()
    logged_in_page.locator("#number").fill(invoice_number)

    # Add invoice line items
    logged_in_page.get_by_role("button", name="Add Item").click()
    logged_in_page.get_by_role("row", name="$ 0.00").get_by_role(
        "textbox"
    ).first.click()
    logged_in_page.get_by_role("cell", name="New Product").get_by_role("textbox").fill(
        test_data.product_name1
    )
    logged_in_page.get_by_role("listitem").filter(
        has_text=test_data.product_name1
    ).click()
    logged_in_page.get_by_role("button", name="Add Item").click()
    logged_in_page.get_by_role("row", name="$ 0.00").get_by_role(
        "textbox"
    ).first.click()
    logged_in_page.get_by_role("cell", name="New Product").get_by_role("textbox").fill(
        test_data.product_name2
    )
    logged_in_page.get_by_text(test_data.product_name2).click()
    logged_in_page.get_by_role("button", name="Save").click()
    logged_in_page.wait_for_timeout(2000)

    if status == "sent":
        # Mark sent
        logged_in_page.locator("div").filter(
            has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
        ).get_by_role("button").nth(2).click()
        logged_in_page.get_by_role("button", name="Mark Sent").click()
        logged_in_page.wait_for_timeout(2000)

    return logged_in_page


def create_payment(
    created_invoice_page: Page, invoice_number: str, test_data: "InvoiceNinjaTestData"
):
    # Navigate
    created_invoice_page.get_by_role("link", name="Payments").click()
    created_invoice_page.wait_for_timeout(500)
    created_invoice_page.get_by_role("link", name="Enter Payment").click()

    # Choose client
    created_invoice_page.get_by_test_id("combobox-input-field").click()
    created_invoice_page.get_by_test_id("combobox-input-field").fill(
        test_data.company_name
    )
    created_invoice_page.wait_for_timeout(2000)
    created_invoice_page.get_by_text(test_data.company_name).click(timeout=3000)

    # Choose invoice
    created_invoice_page.get_by_test_id("combobox-input-field").nth(1).click()
    created_invoice_page.get_by_test_id("combobox-input-field").nth(1).fill(
        invoice_number
    )
    created_invoice_page.wait_for_timeout(2000)
    created_invoice_page.get_by_text(f"Invoice #{invoice_number}").first.click(
        timeout=3000
    )

    # Payment type
    created_invoice_page.locator("div").filter(
        has_text=re.compile(r"^Select\.\.\.$")
    ).nth(2).click()
    created_invoice_page.get_by_role("option", name="Bank Transfer", exact=True).click()

    created_invoice_page.get_by_role("button", name="Save").click()
    return created_invoice_page


def create_expense(
    created_client_page: Page,
    test_data: "InvoiceNinjaTestData",
) -> Page:
    created_client_page.get_by_role("link", name="Expenses").first.click()
    created_client_page.get_by_role("link", name="Enter Expense").click()

    # ID & Choose client
    created_client_page.get_by_test_id("combobox-input-field").nth(1).click()
    created_client_page.get_by_test_id("combobox-input-field").nth(1).fill(
        test_data.company_name
    )
    created_client_page.get_by_text(test_data.company_name).click()

    # Amount & Currency
    created_client_page.locator("div").filter(
        has_text=re.compile(r"^Amount$")
    ).get_by_role("textbox").click()
    created_client_page.locator("div").filter(
        has_text=re.compile(r"^Amount$")
    ).get_by_role("textbox").fill(test_data.expense_amount)

    created_client_page.locator("div").filter(
        has_text=re.compile(r"^Select\.\.\.$")
    ).nth(3).click()
    created_client_page.get_by_role("option", name="Australian Dollar (AUD)").click()

    created_client_page.get_by_role("button", name="Save").click()

    expect(
        created_client_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully created expense$"))
        .first
    ).to_be_visible(timeout=2000)
    expect(created_client_page.get_by_role("list")).to_contain_text("Edit Expense")
    expect(created_client_page.get_by_role("main")).to_contain_text("Logged")

    created_client_page.wait_for_timeout(1000)
    return created_client_page


def create_credit(
    logged_in_page: Page, credit_number: str, test_data: "InvoiceNinjaTestData"
) -> Page:
    logged_in_page.get_by_role("link", name="Credits", exact=True).click()
    logged_in_page.get_by_role("link", name="Enter Credit").click()

    logged_in_page.get_by_test_id("combobox-input-field").click()
    logged_in_page.get_by_test_id("combobox-input-field").fill(test_data.company_name)
    logged_in_page.get_by_role("option", name=test_data.company_name).click()

    logged_in_page.locator("#number").click()
    logged_in_page.locator("#number").fill(credit_number)

    # Add items
    logged_in_page.get_by_role("button", name="Add Item").click()
    logged_in_page.get_by_role("row", name="$ 0.00").get_by_role(
        "textbox"
    ).first.click()
    logged_in_page.get_by_role("cell", name="New Product").get_by_role("textbox").fill(
        test_data.product_name1
    )
    logged_in_page.get_by_role("listitem").filter(
        has_text=test_data.product_name1
    ).click()
    logged_in_page.get_by_role("button", name="Add Item").click()
    logged_in_page.get_by_role("row", name="$ 0.00").get_by_role(
        "textbox"
    ).first.click()
    logged_in_page.get_by_role("cell", name="New Product").get_by_role("textbox").fill(
        test_data.product_name2
    )
    logged_in_page.get_by_text(test_data.product_name2).click()
    logged_in_page.get_by_role("button", name="Save").click()
    logged_in_page.wait_for_timeout(2000)

    return logged_in_page


def go_to_credit_detail_page(
    logged_in_page: Page, test_data: "InvoiceNinjaTestData"
) -> Page:
    logged_in_page.get_by_role("link", name="Credits", exact=True).click()
    logged_in_page.get_by_role("link", name=test_data.credit_number).click()
    return logged_in_page


def go_to_client_detail_page(
    logged_in_page: Page, test_data: "InvoiceNinjaTestData"
) -> Page:
    logged_in_page.get_by_role("link", name="Clients").click()
    logged_in_page.get_by_role("link", name=test_data.company_name).click()
    return logged_in_page


def go_to_expense_detail_page(logged_in_page: Page) -> Page:
    logged_in_page.get_by_role("link", name="Expenses").first.click()
    logged_in_page.get_by_role("link", name="0001").click()
    return logged_in_page


def go_to_invoice_detail_page(
    logged_in_page: Page, test_data: "InvoiceNinjaTestData"
) -> Page:
    logged_in_page.get_by_role("link", name="Invoices", exact=True).click()
    logged_in_page.get_by_role(
        "link", name=test_data.invoice_number_draft, exact=True
    ).click()
    return logged_in_page


def go_to_payment_detail_page(logged_in_page: Page) -> Page:
    logged_in_page.get_by_role("link", name="Payments").click()
    logged_in_page.get_by_role("link", name="0001").first.click()
    return logged_in_page


def go_to_product_detail_page(
    logged_in_page: Page, test_data: "InvoiceNinjaTestData"
) -> Page:
    logged_in_page.get_by_role("link", name="Products").first.click()
    logged_in_page.get_by_role("link", name=test_data.product_name, exact=True).click()
    return logged_in_page
