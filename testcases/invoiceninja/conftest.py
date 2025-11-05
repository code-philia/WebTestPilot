import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
from playwright.async_api import Page as AsyncPage
from playwright.sync_api import Page

sys.path.append(str(Path(__file__).parent.parent))

from tracing_api import create_traced_page

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
    company_name_new: str = "company_name_new"
    company_name_updated: str = "company_name_updated"
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
    invoice_number_paid: str = "123456"
    invoice_number_sent: str = "123456_sent"  # used for creating new payment
    invoice_number_new: str = "123456_new"
    invoice_number_draft: str = "123456_draft"
    invoice_date: str = "2025-07-15"

    # Expense
    expense_amount: str = "2,3234"
    expense_amount_updated: str = "23,2340"

    # Credit
    credit_number: str = "123456"
    credit_number_new: str = "123456_new"


@pytest.fixture
def test_data() -> InvoiceNinjaTestData:
    """Provides fresh, unique test data for each test"""
    return InvoiceNinjaTestData()


def go_to_invoiceninja(page: Page) -> Page:
    page.set_viewport_size({"width": 1280, "height": 720})
    page.goto(f"{INVOICE_NINJA_HOST}/login")
    return page


async def go_to_invoiceninja_async(page: AsyncPage) -> AsyncPage:
    await page.set_viewport_size({"width": 1280, "height": 720})
    await page.goto(f"{INVOICE_NINJA_HOST}/login")
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


async def login_to_invoiceninja_async(page: AsyncPage) -> AsyncPage:
    page = await go_to_invoiceninja_async(page)

    # Perform login
    await page.locator('input[name="email"]').click()
    await page.locator('input[name="email"]').fill(INITIAL_USER)
    await page.get_by_role("textbox", name="Password").click()
    await page.get_by_role("textbox", name="Password").fill(INITIAL_PASSWORD)
    await page.get_by_role("button", name="Login").click()
    await page.get_by_role("button", name="Save").click()

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
def seed(logged_in_page: Page, test_data: InvoiceNinjaTestData) -> Page:
    """Seed minimal data for InvoiceNinja tests."""
    # Create base data: 1 client and 3 products (needed for invoices/credits)
    logged_in_page = create_client(logged_in_page, test_data.company_name, test_data)
    logged_in_page.wait_for_timeout(1000)
    logged_in_page = create_product(logged_in_page, test_data.product_name, test_data)
    logged_in_page.wait_for_timeout(1000)
    logged_in_page = create_product(logged_in_page, test_data.product_name1, test_data)
    logged_in_page.wait_for_timeout(1000)
    logged_in_page = create_product(logged_in_page, test_data.product_name2, test_data)
    logged_in_page.wait_for_timeout(1000)

    # Create 1 sent invoice for payment seed
    logged_in_page = create_invoice(
        logged_in_page, test_data.invoice_number_paid, test_data, status="sent"
    )
    logged_in_page = go_to_invoiceninja(logged_in_page)
    logged_in_page.wait_for_timeout(1000)

    # 1 sent invoice for new payment create test.
    logged_in_page = create_invoice(
        logged_in_page, test_data.invoice_number_sent, test_data, status="sent"
    )
    logged_in_page = go_to_invoiceninja(logged_in_page)
    logged_in_page.wait_for_timeout(1000)

    # 1 sent draft invoice invoice RUD tests.
    logged_in_page = create_invoice(
        logged_in_page, test_data.invoice_number_draft, test_data
    )
    logged_in_page = go_to_invoiceninja(logged_in_page)
    logged_in_page.wait_for_timeout(1000)

    # Create credit
    logged_in_page = create_credit(logged_in_page, test_data.credit_number, test_data)
    logged_in_page.wait_for_timeout(1000)

    # Create payment linked to the invoice
    logged_in_page = create_payment(
        logged_in_page, test_data.invoice_number_paid, test_data
    )
    logged_in_page.wait_for_timeout(1000)

    # Create expense linked to the client (need to setup client first)
    page_with_client = create_client(logged_in_page, test_data.company_name, test_data)
    page_with_client = create_expense(page_with_client, test_data)
    logged_in_page.wait_for_timeout(1000)

    # Navigate back to dashboard
    logged_in_page.get_by_role("link", name="Dashboard").click()
    logged_in_page.wait_for_timeout(1000)

    return logged_in_page
