import re
import sys
from dataclasses import dataclass
from pathlib import Path
from random import randint

import pytest
from playwright.sync_api import Page

sys.path.append(str(Path(__file__).parent.parent))

from tracing_api import create_traced_page
from tracing_api import traced_expect as expect

pytest_plugins = ["pytest_xpath_plugin"]


INVOICE_NINJA_HOST = "http://localhost:8082"
INITIAL_USER = "admin@example.com"
INITIAL_PASSWORD = "changeme!"


@dataclass
class InvoiceNinjaTestData:
    """
    Thread-safe test data factory for InvoiceNinja entities.
    Each instance gets unique identifiers to prevent race conditions.
    """

    def __post_init__(self):
        self._unique_id = str(randint(100000, 999999))

    @property
    def company_name(self) -> str:
        return f"company_name{self._unique_id}"

    @property
    def company_name_updated(self) -> str:
        return f"company_name_updated{self._unique_id}"

    @property
    def company_number(self) -> str:
        return f"company_number{self._unique_id}"

    @property
    def company_id(self) -> str:
        return f"company_id{self._unique_id}"

    @property
    def vat_number(self) -> str:
        return f"vat_number{self._unique_id}"

    @property
    def company_website(self) -> str:
        return f"website{self._unique_id}.com"

    @property
    def company_phone(self) -> str:
        return f"09{self._unique_id}"

    @property
    def contact_first_name(self) -> str:
        return f"first_name{self._unique_id}"

    @property
    def contact_last_name(self) -> str:
        return f"last_name{self._unique_id}"

    @property
    def contact_email(self) -> str:
        return f"email{self._unique_id}@example.com"

    @property
    def contact_phone(self) -> str:
        return f"099{self._unique_id}"

    @property
    def product_name(self) -> str:
        return f"product_name{self._unique_id}"

    @property
    def product_name_updated(self) -> str:
        return f"product_name_updated{self._unique_id}"

    @property
    def product_description(self) -> str:
        return f"product_description{self._unique_id}"

    @property
    def product_price(self) -> str:
        return f"{self._unique_id}"

    @property
    def product_default_quantity(self) -> str:
        return "200"

    @property
    def product_max_quantity(self) -> str:
        return "1000"

    @property
    def invoice_number(self) -> str:
        return str(self._unique_id)

    @property
    def invoice_date(self) -> str:
        return "2025-07-15"

    @property
    def expense_amount(self) -> str:
        return "2,3234"

    @property
    def expense_amount_updated(self) -> str:
        return "23,2340"


@pytest.fixture
def test_data() -> InvoiceNinjaTestData:
    """Provides fresh, unique test data for each test"""
    return InvoiceNinjaTestData()


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """
    Fixture that provides a page with user already logged in to InvoiceNinja demo.

    Returns:
        Page: A Playwright page object with user logged in
    """
    traced_page = create_traced_page(page)

    traced_page.set_viewport_size({"width": 1280, "height": 720})
    traced_page.goto(f"{INVOICE_NINJA_HOST}/login")

    # Perform login
    traced_page.locator('input[name="email"]').click()
    traced_page.locator('input[name="email"]').fill(INITIAL_USER)
    traced_page.get_by_role("textbox", name="Password").click()
    traced_page.get_by_role("textbox", name="Password").fill(INITIAL_PASSWORD)
    traced_page.get_by_role("button", name="Login").click()

    traced_page.get_by_role("button", name="Save").click()

    return traced_page


def create_client(
    logged_in_page: Page, company_name: str, test_data: InvoiceNinjaTestData
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
    ).fill(test_data.company_number)

    logged_in_page.locator("div").filter(
        has_text=re.compile(r"^ID Number$")
    ).get_by_role("textbox").click()
    logged_in_page.locator("div").filter(
        has_text=re.compile(r"^ID Number$")
    ).get_by_role("textbox").fill(test_data.company_id)
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


@pytest.fixture
def created_client_page(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> Page:
    logged_in_page = create_client(logged_in_page, test_data.company_name, test_data)
    return logged_in_page


def create_product(
    logged_in_page: Page, product_name: str, test_data: InvoiceNinjaTestData
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


@pytest.fixture
def created_product_page(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> Page:
    create_product(logged_in_page, test_data.product_name, test_data)
    return logged_in_page


@pytest.fixture
def created_invoice_page(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> Page:
    # Data setup
    create_client(logged_in_page, test_data.company_name, test_data)
    create_product(logged_in_page, test_data.product_name + "1", test_data)
    create_product(logged_in_page, test_data.product_name + "2", test_data)

    # Navigate
    logged_in_page.wait_for_timeout(1000)
    logged_in_page.get_by_role("link", name="Invoices", exact=True).click()
    logged_in_page.get_by_role("link", name="New Invoice").click()

    # Choose client for invoice
    logged_in_page.get_by_test_id("combobox-input-field").click()
    logged_in_page.get_by_test_id("combobox-input-field").fill(test_data.company_name)
    logged_in_page.get_by_role("option", name=test_data.company_name).click()

    # Invoice number
    logged_in_page.locator("#number").click()
    logged_in_page.locator("#number").fill(test_data.invoice_number)

    # Add invoice line items
    logged_in_page.get_by_role("button", name="Add Item").click()
    logged_in_page.get_by_role("row", name="$ 0.00").get_by_role(
        "textbox"
    ).first.click()
    logged_in_page.get_by_role("cell", name="New Product").get_by_role("textbox").fill(
        test_data.product_name + "1"
    )
    logged_in_page.get_by_role("listitem").filter(
        has_text=test_data.product_name + "1"
    ).click()
    logged_in_page.get_by_role("button", name="Add Item").click()
    logged_in_page.get_by_role("row", name="$ 0.00").get_by_role(
        "textbox"
    ).first.click()
    logged_in_page.get_by_role("cell", name="New Product").get_by_role("textbox").fill(
        test_data.product_name + "2"
    )
    logged_in_page.get_by_text(test_data.product_name + "2").click()
    logged_in_page.get_by_role("button", name="Save").click()
    logged_in_page.wait_for_timeout(2000)
    return logged_in_page


@pytest.fixture
def created_payment_page(
    created_invoice_page: Page, test_data: InvoiceNinjaTestData
) -> Page:
    # Invoice has to be sent to be chosen in payment
    created_invoice_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()
    created_invoice_page.get_by_role("button", name="Mark Sent").click()

    created_invoice_page.wait_for_timeout(1000)
    expect(created_invoice_page.get_by_role("main")).to_contain_text(
        "Sent", timeout=5000
    )

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
        test_data.invoice_number
    )
    created_invoice_page.wait_for_timeout(2000)
    created_invoice_page.get_by_text(
        f"Invoice #{test_data.invoice_number}"
    ).first.click(timeout=3000)

    # Payment type
    created_invoice_page.locator("div").filter(
        has_text=re.compile(r"^Select\.\.\.$")
    ).nth(2).click()
    created_invoice_page.get_by_role("option", name="Bank Transfer", exact=True).click()

    created_invoice_page.get_by_role("button", name="Save").click()
    expect(
        created_invoice_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully created payment$"))
        .first
    ).to_be_visible(timeout=2000)

    return created_invoice_page


@pytest.fixture
def created_expense_page(
    created_client_page: Page, test_data: InvoiceNinjaTestData
) -> Page:
    created_client_page.wait_for_timeout(500)
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


@pytest.fixture
def created_credit_page(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> Page:
    create_client(logged_in_page, test_data.company_name, test_data)
    create_product(logged_in_page, test_data.product_name + "1", test_data)
    create_product(logged_in_page, test_data.product_name + "2", test_data)

    logged_in_page.wait_for_timeout(500)
    logged_in_page.get_by_role("link", name="Credits", exact=True).click()
    logged_in_page.get_by_role("link", name="Enter Credit").click()

    logged_in_page.get_by_test_id("combobox-input-field").click()
    logged_in_page.get_by_test_id("combobox-input-field").fill(test_data.company_name)
    logged_in_page.get_by_role("option", name=test_data.company_name).click()

    logged_in_page.locator("#number").click()
    logged_in_page.locator("#number").fill(test_data.invoice_number)

    # Add items
    logged_in_page.get_by_role("button", name="Add Item").click()
    logged_in_page.get_by_role("row", name="$ 0.00").get_by_role(
        "textbox"
    ).first.click()
    logged_in_page.get_by_role("cell", name="New Product").get_by_role("textbox").fill(
        test_data.product_name + "1"
    )
    logged_in_page.get_by_role("listitem").filter(
        has_text=test_data.product_name + "1"
    ).click()
    logged_in_page.get_by_role("button", name="Add Item").click()
    logged_in_page.get_by_role("row", name="$ 0.00").get_by_role(
        "textbox"
    ).first.click()
    logged_in_page.get_by_role("cell", name="New Product").get_by_role("textbox").fill(
        test_data.product_name + "2"
    )
    logged_in_page.get_by_text(test_data.product_name + "2").click()
    logged_in_page.get_by_role("button", name="Save").click()
    logged_in_page.wait_for_timeout(2000)
    return logged_in_page
