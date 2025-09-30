import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
from playwright.sync_api import Page

sys.path.append(str(Path(__file__).parent.parent))

from tracing_api import create_traced_page

from .utilities import (
    create_attribute,
    create_brand,
    create_child_category,
    create_customer,
    create_feature,
    create_parent_category,
    create_supplier,
    create_virtual_product,
)

pytest_plugins = ["pytest_xpath_plugin"]

BASE_URL = "http://localhost:8083"


@dataclass
@dataclass
class PrestaShopTestData:
    """
    Thread-safe test data factory for PrestaShop entities.
    Each instance gets unique identifiers to prevent race conditions.
    """

    # Attribute properties
    attribute_name: str = "Weight"
    attribute_public_name: str = "Weight"
    attribute_value: str = "500g"

    # Feature properties
    feature_name: str = "Season"
    feature_value: str = "autumn"

    # Brand properties
    brand_name: str = "Nike"
    brand_description: str = "Description"
    brand_logo_file: str = "prestashop/test_data/pictures/nike logo.jpg"

    # Category properties
    parent_category_name: str = "Shoes"
    parent_category_parent: str = "Home"
    parent_category_description: str = "Description"
    parent_category_image_file: str = "prestashop/test_data/pictures/shoes.png"
    parent_category_link_rewrite: str = "shoes"
    child_category_name: str = "Sports shoes"
    child_category_parent: str = "Shoes"
    child_category_description: str = "Description"
    child_category_image_file: str = "prestashop/test_data/pictures/sports shoes.jpg"
    child_category_link_rewrite: str = "sports-shoes"

    # Customer properties
    customer_social_title: str = "Mr."
    customer_first_name: str = "Jones"
    customer_last_name: str = "Jonathan"
    customer_email: str = "test@test.com"
    customer_password: str = "testTEST123."
    customer_birth_year: str = "2003"
    customer_birth_month: str = "1"
    customer_birth_day: str = "1"
    customer_default_group: str = "Customer"

    # Virtual product properties
    virtual_product_name: str = "bird"
    virtual_product_image_file: str = "prestashop/test_data/pictures/bird.jpg"
    virtual_product_description: str = "Description"
    virtual_product_short_description: str = "Vector graphic, format: svg. Download for personal, private and non-commercial use."
    virtual_product_category: str = "Art"
    virtual_product_brand: str = "Graphic Corner"
    virtual_product_reference: str = "test1"
    virtual_product_quantity: str = "300"
    virtual_product_price_tax_excl: str = "9.000000"
    virtual_product_wholesale_price: str = "5.490000"
    virtual_product_link_rewrite: str = "bird-vector-graphics"
    virtual_product_offline_redirection: str = "default"
    virtual_product_fashion_supplier_ref: str = "test1"
    virtual_product_fashion_supplier_price: str = "6.490000"
    virtual_product_accessories_supplier_ref: str = "test1"
    virtual_product_accessories_supplier_price: str = "5.490000"

    # Standard product properties
    standard_product_name: str = "cat notebook"
    standard_product_image_file: str = "prestashop/test_data/pictures/cat notebook.jpg"
    standard_product_description: str = "Description"
    standard_product_short_description: str = "Short description"
    standard_product_category_search: str = "Stationery"
    standard_product_default_category: str = "Stationery"
    standard_product_brand: str = "Graphic Corner"
    standard_product_reference: str = "test2"
    standard_product_feature_composition: str = "Recycled cardboard"
    standard_product_feature_property: str = "pages"
    standard_product_quantity: str = "300"
    standard_product_price_tax_excl: str = "12.900000"
    standard_product_wholesale_price: str = "5.490000"
    standard_product_weight: str = "0.3"
    standard_product_link_rewrite: str = "cat-notebook-vector-graphics"

    # Delete product name
    delete_product_name: str = "bird"

    # Supplier properties
    supplier_name: str = "Shoes supplier"
    supplier_phone: str = "090-1234-5678"
    supplier_address: str = "Nishi-Shinjuku 1-25-1"
    supplier_city: str = "Tokyo"
    supplier_country: str = "Japan"
    supplier_state: str = "Aichi"
    supplier_logo_active: str = "Yes"

    # Buyer properties
    buyer_product_name: str = "Hummingbird printed t-shirt"
    buyer_size: str = "M"
    buyer_size_cnt: str = "2"
    buyer_color: str = "Black"
    buyer_star: str = "5"
    buyer_title: str = "Good thing"
    buyer_review: str = "very comfortable!"
    buyer_main_category: str = "Clothes"
    buyer_sub_category: str = "Men"
    buyer_filter_availability: str = "In stock"
    buyer_filter_selection: str = "Discounted"
    buyer_filter_size: str = "M"


@pytest.fixture
def test_data() -> PrestaShopTestData:
    """Provides fresh, unique test data for each test"""
    return PrestaShopTestData()


def go_to_prestashop(page: Page) -> Page:
    page.goto(f"{BASE_URL}/webtestpilot/")
    return page


def go_to_buyer_page(page: Page) -> Page:
    page.goto(f"{BASE_URL}/")
    return page


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    page = create_traced_page(page, enable_tracing=True)
    page = login_to_prestashop(page)
    return page


def login_to_prestashop(page: Page) -> Page:
    go_to_prestashop(page)
    page.get_by_role("textbox", name="Email address").click()
    page.get_by_role("textbox", name="Email address").fill("admin@admin.com")
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill("admin12345")
    page.get_by_role("button", name="Log in").click()
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Products", exact=True).first.click()
    page.get_by_title("Close Toolbar").click()
    page.get_by_role("link", name="trending_up Dashboard").click()
    # expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()
    return page


@pytest.fixture
def logged_in_buyer_page(page: Page) -> Page:
    page = create_traced_page(page, enable_tracing=True)
    page = login_to_prestashop_as_buyer(page)
    return page


def login_to_prestashop_as_buyer(page: Page) -> Page:
    page = go_to_buyer_page(page)
    page.get_by_role("link", name=" Sign in").click()

    # Must create user with docker exec -it prestashop-app-1 php /var/www/html/tools/create_user.php
    # See webapps/prestashop/Dockerfile for more info
    page.get_by_role("textbox", name="Email").fill("auto.customer@example.com")
    page.get_by_role("textbox", name="Password input").fill("mypassword")
    page.get_by_role("button", name="Sign in").click()
    return page


@pytest.fixture
def seed(logged_in_page: Page, test_data: PrestaShopTestData) -> Page:
    """Seed minimal data for prestashop tests."""
    create_customer(logged_in_page)
    logged_in_page.wait_for_timeout(1000)
    logged_in_page.goto(f"{BASE_URL}/webtestpilot/")

    create_attribute(logged_in_page)
    logged_in_page.wait_for_timeout(1000)
    logged_in_page.goto(f"{BASE_URL}/webtestpilot/")

    create_feature(logged_in_page)
    logged_in_page.wait_for_timeout(1000)
    logged_in_page.goto(f"{BASE_URL}/webtestpilot/")

    create_brand(logged_in_page)
    logged_in_page.wait_for_timeout(1000)
    logged_in_page.goto(f"{BASE_URL}/webtestpilot/")

    create_parent_category(logged_in_page)
    logged_in_page.wait_for_timeout(1000)
    logged_in_page.goto(f"{BASE_URL}/webtestpilot/")

    create_child_category(logged_in_page)
    logged_in_page.wait_for_timeout(1000)
    logged_in_page.goto(f"{BASE_URL}/webtestpilot/")

    create_virtual_product(logged_in_page)
    logged_in_page.wait_for_timeout(1000)
    logged_in_page.goto(f"{BASE_URL}/webtestpilot/")

    create_supplier(logged_in_page)
    return logged_in_page
