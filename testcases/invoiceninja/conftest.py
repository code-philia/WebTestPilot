import re
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
from playwright.sync_api import Page

sys.path.append(str(Path(__file__).parent.parent))

from tracing_api import create_traced_page
from tracing_api import traced_expect as expect

from .utilities import (
    create_client,
    create_credit,
    create_expense,
    create_invoice,
    create_payment,
    create_product,
)

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

    # Company
    company_name: str = "company_name"
    company_name_updated: str = "company_name_updated"
    company_number: str = "company_number"
    company_id: str = "company_id"
    vat_number: str = "vat_number"
    company_website: str = "website.com"
    company_phone: str = "0987654321"

    # Contact
    contact_first_name: str = "first_name"
    contact_last_name: str = "last_name"
    contact_email: str = "email@example.com"
    contact_phone: str = "0912345678"

    # Product
    product_name: str = "product_name"
    product_name1: str = "product_name1"
    product_name2: str = "product_name2"
    product_name_updated: str = "product_name_updated"
    product_description: str = "product_description"
    product_price: str = "60000"
    product_default_quantity: str = "200"
    product_max_quantity: str = "1000"

    # Invoice
    invoice_number: str = "123456"
    invoice_date: str = "2025-07-15"

    # Expense
    expense_amount: str = "2,3234"
    expense_amount_updated: str = "23,2340"

    # Credit
    credit_number: str = "123456"


@pytest.fixture
def test_data() -> InvoiceNinjaTestData:
    """Provides fresh, unique test data for each test"""
    return InvoiceNinjaTestData()


def go_to_invoiceninja(page: Page) -> Page:
    page.set_viewport_size({"width": 1280, "height": 720})
    page.goto(f"{INVOICE_NINJA_HOST}/login")
    return page


def login_to_invoiceninja(page: Page) -> Page:
    page = go_to_invoiceninja(page)

    # Perform login
    page.locator('input[name="email"]').click()
    page.locator('input[name="email"]').fill(INITIAL_USER)
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill(INITIAL_PASSWORD)
    page.get_by_role("button", name="Login").click()
    page.get_by_role("button", name="Save").click()

    return page


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """
    Fixture that provides a page with user already logged in to InvoiceNinja demo.

    Returns:
        Page: A Playwright page object with user logged in
    """
    traced_page = create_traced_page(page)
    traced_page = login_to_invoiceninja(traced_page)
    return traced_page


@pytest.fixture
def created_client_page(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> Page:
    logged_in_page = create_client(logged_in_page, test_data.company_name, test_data)
    return logged_in_page


@pytest.fixture
def created_product_page(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> Page:
    create_product(logged_in_page, test_data.product_name, test_data)
    return logged_in_page


@pytest.fixture
def created_invoice_page(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> Page:
    # Data setup
    logged_in_page = setup_for_invoice_page(logged_in_page, test_data)
    return logged_in_page


def setup_for_invoice_page(
    logged_in_page: Page, test_data: InvoiceNinjaTestData
) -> Page:
    setup_data_for_create_invoice(logged_in_page, test_data)

    # Navigate
    logged_in_page.wait_for_timeout(1000)
    logged_in_page = create_invoice(logged_in_page, test_data)

    return logged_in_page


def setup_data_for_create_invoice(logged_in_page, test_data: InvoiceNinjaTestData):
    create_client(logged_in_page, test_data.company_name, test_data)
    create_product(logged_in_page, test_data.product_name1, test_data)
    create_product(logged_in_page, test_data.product_name2, test_data)


@pytest.fixture
def created_payment_page(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> Page:
    # Invoice has to be sent to be chosen in payment
    created_invoice_page = setup_for_payment_page(logged_in_page, test_data)
    expect(
        created_invoice_page.locator("div")
        .filter(has_text=re.compile(r"^Successfully created payment$"))
        .first
    ).to_be_visible(timeout=2000)

    return created_invoice_page


def setup_for_payment_page(logged_in_page: Page, test_data: InvoiceNinjaTestData):
    created_invoice_page = setup_data_for_create_payment(logged_in_page, test_data)
    created_payment_page = create_payment(created_invoice_page, test_data)
    return created_payment_page


def setup_data_for_create_payment(
    logged_in_page: Page, test_data: InvoiceNinjaTestData
):
    created_invoice_page = setup_for_invoice_page(logged_in_page, test_data)

    created_invoice_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()
    created_invoice_page.get_by_role("button", name="Mark Sent").click()

    created_invoice_page.wait_for_timeout(1000)
    expect(created_invoice_page.get_by_role("main")).to_contain_text(
        "Sent", timeout=5000
    )

    return created_invoice_page


@pytest.fixture
def created_expense_page(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> Page:
    created_client_page = setup_for_expense_page(logged_in_page, test_data)
    return created_client_page


def setup_for_expense_page(
    logged_in_page: Page, test_data: InvoiceNinjaTestData
) -> Page:
    created_expense_page = setup_data_for_expense_create(logged_in_page, test_data)
    created_expense_page.wait_for_timeout(500)
    created_expense_page = create_expense(created_expense_page, test_data)
    return created_expense_page


def setup_data_for_expense_create(
    logged_in_page: Page, test_data: InvoiceNinjaTestData
):
    created_client_page = create_client(
        logged_in_page, test_data.company_name, test_data
    )

    return created_client_page


@pytest.fixture
def created_credit_page(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> Page:
    logged_in_page = setup_for_credit_page(logged_in_page, test_data)
    return logged_in_page


def setup_for_credit_page(
    logged_in_page: Page, test_data: InvoiceNinjaTestData
) -> Page:
    setup_data_for_credit_create(logged_in_page, test_data)

    logged_in_page.wait_for_timeout(500)

    logged_in_page = create_credit(logged_in_page, test_data)

    return logged_in_page


def setup_data_for_credit_create(logged_in_page: Page, test_data: InvoiceNinjaTestData):
    create_client(logged_in_page, test_data.company_name, test_data)
    create_product(logged_in_page, test_data.product_name1, test_data)
    create_product(logged_in_page, test_data.product_name2, test_data)


@pytest.fixture
def seed(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> Page:
    """Seed minimal data for InvoiceNinja tests."""
    # Create base data: 1 client and 2 products (needed for invoices/credits)
    logged_in_page = create_client(logged_in_page, test_data.company_name, test_data)
    logged_in_page.wait_for_timeout(1000)

    # Create first product
    logged_in_page = create_product(logged_in_page, test_data.product_name1, test_data)
    logged_in_page.wait_for_timeout(1000)

    # Create second product
    logged_in_page = create_product(logged_in_page, test_data.product_name2, test_data)
    logged_in_page.wait_for_timeout(1000)

    # Create invoice with line items
    logged_in_page = create_invoice(logged_in_page, test_data)
    logged_in_page.wait_for_timeout(1000)

    # Mark invoice as sent (required for payment creation)
    logged_in_page.locator("div").filter(
        has_text=re.compile(r"^Purchase White LabelUpgradeSave$")
    ).get_by_role("button").nth(2).click()
    logged_in_page.get_by_role("button", name="Mark Sent").click()
    logged_in_page.wait_for_timeout(1000)

    # Create payment linked to the invoice
    logged_in_page = create_payment(logged_in_page, test_data)
    logged_in_page.wait_for_timeout(1000)

    # Create expense linked to the client (need to setup client first)
    page_with_client = create_client(logged_in_page, test_data.company_name, test_data)
    page_with_client = create_expense(page_with_client, test_data)
    logged_in_page.wait_for_timeout(1000)

    # Navigate back to dashboard
    logged_in_page.get_by_role("link", name="Dashboard").click()
    logged_in_page.wait_for_timeout(1000)

    return logged_in_page
