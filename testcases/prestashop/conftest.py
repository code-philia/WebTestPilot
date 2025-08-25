import json
import sys
from dataclasses import dataclass
from pathlib import Path
from random import randint

import pytest
from playwright.sync_api import Page

sys.path.append(str(Path(__file__).parent.parent))

from tracing_api import create_traced_page

pytest_plugins = ["pytest_xpath_plugin"]

BASE_URL = "http://localhost:8083"
# BASE_URL = "http://49.232.8.242:8083"


@dataclass
class PrestaShopTestData:
    """
    Thread-safe test data factory for PrestaShop entities.
    Each instance gets unique identifiers to prevent race conditions.
    Supports _unique_id = "" for deterministic baseline testing.
    """

    def __post_init__(self):
        self._unique_id = str(randint(100000, 999999))

    # Attribute properties
    @property
    def attribute_name(self) -> str:
        return f"Weight{self._unique_id}"

    @property
    def attribute_public_name(self) -> str:
        return f"Weight{self._unique_id}"

    @property
    def attribute_value(self) -> str:
        return "500g"

    # Feature properties
    @property
    def feature_name(self) -> str:
        return f"Season{self._unique_id}"

    @property
    def feature_value(self) -> str:
        return "autumn"

    # Brand properties
    @property
    def brand_name(self) -> str:
        return f"Nike{self._unique_id}"

    @property
    def brand_description(self) -> str:
        return "Description"

    @property
    def brand_logo_file(self) -> str:
        return "test_data/pictures/nike logo.jpg"

    # Category properties
    @property
    def parent_category_name(self) -> str:
        return f"Shoes{self._unique_id}"

    @property
    def parent_category_parent(self) -> str:
        return "Home"

    @property
    def parent_category_description(self) -> str:
        return "Description"

    @property
    def parent_category_image_file(self) -> str:
        return "test_data/pictures/shoes.png"

    @property
    def parent_category_link_rewrite(self) -> str:
        return f"shoes{self._unique_id}"

    @property
    def child_category_name(self) -> str:
        return f"Sports shoes{self._unique_id}"

    @property
    def child_category_parent(self) -> str:
        return f"Shoes{self._unique_id}"

    @property
    def child_category_description(self) -> str:
        return "Description"

    @property
    def child_category_image_file(self) -> str:
        return "test_data/pictures/sports shoes.jpg"

    @property
    def child_category_link_rewrite(self) -> str:
        return f"sports-shoes{self._unique_id}"

    # Customer properties
    @property
    def customer_social_title(self) -> str:
        return "Mr."

    @property
    def customer_first_name(self) -> str:
        return "Jones"

    @property
    def customer_last_name(self) -> str:
        return "Jonathan"

    @property
    def customer_email(self) -> str:
        return f"test{self._unique_id}@test.com"

    @property
    def customer_password(self) -> str:
        return "testTEST123."

    @property
    def customer_birth_year(self) -> str:
        return "2003"

    @property
    def customer_birth_month(self) -> str:
        return "1"

    @property
    def customer_birth_day(self) -> str:
        return "1"

    @property
    def customer_default_group(self) -> str:
        return "Customer"

    # Virtual product properties
    @property
    def virtual_product_name(self) -> str:
        return f"bird{self._unique_id}"

    @property
    def virtual_product_image_file(self) -> str:
        return "test_data/pictures/bird.jpg"

    @property
    def virtual_product_description(self) -> str:
        return "Description"

    @property
    def virtual_product_short_description(self) -> str:
        return "Vector graphic, format: svg. Download for personal, private and non-commercial use."

    @property
    def virtual_product_category(self) -> str:
        return "Art"

    @property
    def virtual_product_brand(self) -> str:
        return "Graphic Corner"

    @property
    def virtual_product_reference(self) -> str:
        return f"test1{self._unique_id}"

    @property
    def virtual_product_quantity(self) -> str:
        return "300"

    @property
    def virtual_product_price_tax_excl(self) -> str:
        return "9.000000"

    @property
    def virtual_product_wholesale_price(self) -> str:
        return "5.490000"

    @property
    def virtual_product_link_rewrite(self) -> str:
        return f"bird-vector-graphics{self._unique_id}"

    @property
    def virtual_product_offline_redirection(self) -> str:
        return "default"

    @property
    def virtual_product_fashion_supplier_ref(self) -> str:
        return f"test1{self._unique_id}"

    @property
    def virtual_product_fashion_supplier_price(self) -> str:
        return "6.490000"

    @property
    def virtual_product_accessories_supplier_ref(self) -> str:
        return f"test1{self._unique_id}"

    @property
    def virtual_product_accessories_supplier_price(self) -> str:
        return "5.490000"

    # Standard product properties
    @property
    def standard_product_name(self) -> str:
        return f"cat notebook{self._unique_id}"

    @property
    def standard_product_image_file(self) -> str:
        return "test_data/pictures/cat notebook.jpg"

    @property
    def standard_product_description(self) -> str:
        return "Description"

    @property
    def standard_product_short_description(self) -> str:
        return "Short description"

    @property
    def standard_product_category_search(self) -> str:
        return "Stationery"

    @property
    def standard_product_default_category(self) -> str:
        return "Stationery"

    @property
    def standard_product_brand(self) -> str:
        return "Graphic Corner"

    @property
    def standard_product_reference(self) -> str:
        return f"test2{self._unique_id}"

    @property
    def standard_product_feature_composition(self) -> str:
        return "Recycled cardboard"

    @property
    def standard_product_feature_property(self) -> str:
        return "pages"

    @property
    def standard_product_quantity(self) -> str:
        return "300"

    @property
    def standard_product_price_tax_excl(self) -> str:
        return "12.900000"

    @property
    def standard_product_wholesale_price(self) -> str:
        return "5.490000"

    @property
    def standard_product_weight(self) -> str:
        return "0.3"

    @property
    def standard_product_link_rewrite(self) -> str:
        return f"cat-notebook-vector-graphics{self._unique_id}"

    # Delete product name (reference to virtual product)
    @property
    def delete_product_name(self) -> str:
        return f"bird{self._unique_id}"

    # Supplier properties
    @property
    def supplier_name(self) -> str:
        return f"Shoes supplier{self._unique_id}"

    @property
    def supplier_phone(self) -> str:
        return "090-1234-5678"

    @property
    def supplier_address(self) -> str:
        return "Nishi-Shinjuku 1-25-1"

    @property
    def supplier_city(self) -> str:
        return "Tokyo"

    @property
    def supplier_country(self) -> str:
        return "Japan"

    @property
    def supplier_state(self) -> str:
        return "Aichi"

    @property
    def supplier_logo_active(self) -> str:
        return "Yes"

    # Buyer properties (these remain static as they reference existing products)
    @property
    def buyer_product_name(self) -> str:
        return "Hummingbird printed t-shirt"

    @property
    def buyer_size(self) -> str:
        return "M"

    @property
    def buyer_size_cnt(self) -> str:
        return "2"

    @property
    def buyer_color(self) -> str:
        return "Black"

    @property
    def buyer_star(self) -> str:
        return "5"

    @property
    def buyer_title(self) -> str:
        return "Good thing"

    @property
    def buyer_review(self) -> str:
        return "very comfortable!"

    @property
    def buyer_main_category(self) -> str:
        return "Clothes"

    @property
    def buyer_sub_category(self) -> str:
        return "Men"

    @property
    def buyer_filter_availability(self) -> str:
        return "In stock"

    @property
    def buyer_filter_selection(self) -> str:
        return "Discounted"

    @property
    def buyer_filter_size(self) -> str:
        return "M"


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
    yield page
    page.save_traces()


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
    yield page
    page.save_traces()


def login_to_prestashop_as_buyer(page: Page) -> Page:
    page = go_to_buyer_page(page)
    page.get_by_role("link", name=" Sign in").click()

    # Must create user with docker exec -it prestashop-app-1 php /var/www/html/tools/create_user.php
    # See webapps/prestashop/Dockerfile for more info
    page.get_by_role("textbox", name="Email").fill("auto.customer@example.com")
    page.get_by_role("textbox", name="Password input").fill("mypassword")
    page.get_by_role("button", name="Sign in").click()
    return page


def create_attribute(page: Page, test_data: PrestaShopTestData) -> Page:
    """Create an attribute in PrestaShop."""
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Attributes & Features").click()
    page.get_by_role("link", name="Add new attribute").click()
    page.locator("#name_1").fill(test_data.attribute_name)
    page.locator("#public_name_1").fill(test_data.attribute_public_name)
    page.get_by_role("button", name="Save").click()
    return page


def create_feature(page: Page, test_data: PrestaShopTestData) -> Page:
    """Create a feature in PrestaShop."""
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Attributes & Features").click()
    page.get_by_role("link", name="Features", exact=True).click()
    page.get_by_role("link", name=" Add new feature", exact=True).click()
    page.locator("#name_1").fill(test_data.feature_name)
    page.get_by_role("button", name="Save").click()
    return page


def setup_data_for_attribute_tests(page: Page, test_data: PrestaShopTestData) -> Page:
    """Setup data for attribute tests - creates attribute from test data and navigates to attributes page."""
    create_attribute(page, test_data)
    # Navigate back to the attributes page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Attributes & Features").click()
    return page


def setup_data_for_feature_tests(page: Page, test_data: PrestaShopTestData) -> Page:
    """Setup data for feature tests - creates feature from test data and navigates to features page."""
    create_feature(page, test_data)
    # Navigate back to the features page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Attributes & Features").click()
    page.get_by_role("link", name="Features", exact=True).click()
    return page


def create_brand(page: Page, test_data: PrestaShopTestData) -> Page:
    """Create a brand in PrestaShop."""
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Brands & Suppliers").click()
    page.get_by_role(
        "link", name="add_circle_outline Add new brand", exact=True
    ).click()

    page.get_by_role("textbox", name="manufacturer_name input").fill(
        test_data.brand_name
    )
    page.locator("#manufacturer_description_1_ifr").content_frame.locator(
        "#tinymce"
    ).fill(test_data.brand_description)
    page.get_by_role("button", name="Logo Choose file(s) Browse").set_input_files(
        test_data.brand_logo_file
    )

    page.get_by_role("button", name="Save").click()
    return page


def setup_data_for_brand_tests(page: Page, test_data: PrestaShopTestData) -> Page:
    """Setup data for brand tests - creates brand from test data and navigates to brands page."""
    create_brand(page, test_data)
    # Navigate back to the brands page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Brands & Suppliers").click()
    return page


@pytest.fixture
def created_attribute_page(logged_in_page: Page, test_data: PrestaShopTestData) -> Page:
    """Create an attribute and return to attributes page."""
    return setup_data_for_attribute_tests(logged_in_page, test_data)


@pytest.fixture
def created_feature_page(logged_in_page: Page, test_data: PrestaShopTestData) -> Page:
    """Create a feature and return to features page."""
    return setup_data_for_feature_tests(logged_in_page, test_data)


@pytest.fixture
def created_brand_page(logged_in_page: Page, test_data: PrestaShopTestData) -> Page:
    """Create a brand and return to brands page."""
    return setup_data_for_brand_tests(logged_in_page, test_data)


def add_product_to_cart(page: Page, test_data: PrestaShopTestData) -> Page:
    """Add a product to the shopping cart."""
    page.get_by_role("link", name=test_data.buyer_product_name).nth(1).click()
    page.get_by_label("Size").select_option(test_data.buyer_size)
    page.get_by_role("radio", name=test_data.buyer_color).check()
    page.get_by_role("button", name=" Add to cart").click()
    # Wait for the modal to appear and close it
    page.wait_for_timeout(1000)
    # Check if Continue shopping button exists, if so click it
    continue_btn = page.get_by_role("button", name="Continue shopping")
    if continue_btn.is_visible():
        continue_btn.click()
    return page


def add_product_to_wishlist(page: Page, test_data: PrestaShopTestData) -> Page:
    """Add a product to the wishlist."""
    page.get_by_role("textbox", name="Search").fill(test_data.buyer_product_name)
    page.get_by_role("textbox", name="Search").press("Enter")
    product_article = page.get_by_role("article").filter(
        has_text=test_data.buyer_product_name
    )
    product_article.locator(".wishlist-button-add").click()
    page.wait_for_timeout(1000)
    return page


def setup_data_for_cart_tests(page: Page, test_data: PrestaShopTestData) -> Page:
    """Setup data for cart tests - adds product to cart from test data."""
    add_product_to_cart(page, test_data)
    # Navigate to cart page
    page.get_by_role("link", name="Shopping cart link containing").click()
    return page


def setup_data_for_wishlist_tests(page: Page, test_data: PrestaShopTestData) -> Page:
    """Setup data for wishlist tests - adds product to wishlist from test data."""
    add_product_to_wishlist(page, test_data)
    return page


@pytest.fixture
def created_cart_item_page(
    logged_in_buyer_page: Page, test_data: PrestaShopTestData
) -> Page:
    """Add item to cart and navigate to cart page."""
    return setup_data_for_cart_tests(logged_in_buyer_page, test_data)


@pytest.fixture
def created_wishlist_item_page(
    logged_in_buyer_page: Page, test_data: PrestaShopTestData
) -> Page:
    """Add item to wishlist."""
    return setup_data_for_wishlist_tests(logged_in_buyer_page, test_data)


def create_parent_category(page: Page, test_data: PrestaShopTestData) -> Page:
    """Create a parent category in PrestaShop."""
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Categories").click()
    page.get_by_role("link", name="add_circle_outline Add new").click()

    page.get_by_role("textbox", name="category_name_1 input").fill(
        test_data.parent_category_name
    )
    page.get_by_text("expand_more Expand").click()
    page.get_by_text(test_data.parent_category_parent, exact=True).click()
    page.locator("#category_description_1_ifr").content_frame.locator("#tinymce").fill(
        test_data.parent_category_description
    )
    page.locator("#category_cover_image").set_input_files(
        test_data.parent_category_image_file
    )
    page.locator("#category_thumbnail_image").set_input_files(
        test_data.parent_category_image_file
    )
    page.get_by_role("button", name="Choose file(s) Browse").set_input_files(
        test_data.parent_category_image_file
    )
    page.get_by_role("textbox", name="category_link_rewrite_1 input").fill(
        test_data.parent_category_link_rewrite
    )

    page.get_by_role("button", name="Save").click()
    return page


def create_child_category(page: Page, test_data: PrestaShopTestData) -> Page:
    """Create a child category in PrestaShop."""
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Categories").click()
    page.get_by_role("link", name="add_circle_outline Add new").click()

    page.get_by_role("textbox", name="category_name_1 input").fill(
        test_data.child_category_name
    )
    page.get_by_text("expand_more Expand").click()
    page.get_by_text(test_data.child_category_parent, exact=True).click()
    page.locator("#category_description_1_ifr").content_frame.locator("#tinymce").fill(
        test_data.child_category_description
    )
    page.locator("#category_cover_image").set_input_files(
        test_data.child_category_image_file
    )
    page.locator("#category_thumbnail_image").set_input_files(
        test_data.child_category_image_file
    )
    page.get_by_role("button", name="Choose file(s) Browse").set_input_files(
        test_data.child_category_image_file
    )
    page.get_by_role("textbox", name="category_link_rewrite_1 input").fill(
        test_data.child_category_link_rewrite
    )

    page.get_by_role("button", name="Save").click()
    return page


def setup_data_for_parent_category_tests(
    page: Page, test_data: PrestaShopTestData
) -> Page:
    """Setup data for parent category tests - creates parent category from test data."""
    create_parent_category(page, test_data)
    # Navigate back to categories page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Categories").click()
    return page


def setup_data_for_child_category_tests(
    page: Page, test_data: PrestaShopTestData
) -> Page:
    """Setup data for child category tests - creates both parent and child categories."""
    # Create parent category first
    create_parent_category(page, test_data)
    # Create child category
    create_child_category(page, test_data)
    # Navigate back to categories page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Categories").click()
    return page


@pytest.fixture
def created_parent_category_page(
    logged_in_page: Page, test_data: PrestaShopTestData
) -> Page:
    """Create parent category and return to categories page."""
    return setup_data_for_parent_category_tests(logged_in_page, test_data)


@pytest.fixture
def created_child_category_page(
    logged_in_page: Page, test_data: PrestaShopTestData
) -> Page:
    """Create both parent and child categories and return to categories page."""
    return setup_data_for_child_category_tests(logged_in_page, test_data)


def create_customer(page: Page, test_data: PrestaShopTestData) -> Page:
    """Create a customer in PrestaShop."""
    page.get_by_role("link", name="account_circle Customers").click()
    page.get_by_role("link", name="Customers", exact=True).click()
    page.get_by_role("link", name="add_circle_outline Add new").click()

    page.locator("label").filter(has_text=test_data.customer_social_title).locator(
        "i"
    ).click()
    page.get_by_role("textbox", name="customer_first_name input").fill(
        test_data.customer_first_name
    )
    page.get_by_role("textbox", name="customer_last_name input").fill(
        test_data.customer_last_name
    )
    page.get_by_role("textbox", name="* Email").fill(test_data.customer_email)
    page.get_by_role("textbox", name="Password").fill(test_data.customer_password)
    page.locator("#customer_birthday_year").select_option(test_data.customer_birth_year)
    page.locator("#customer_birthday_month").select_option(
        test_data.customer_birth_month
    )
    page.locator("#customer_birthday_day").select_option(test_data.customer_birth_day)

    page.get_by_role("button", name="Save").click()
    return page


def setup_data_for_customer_tests(page: Page, test_data: PrestaShopTestData) -> Page:
    """Setup data for customer tests - creates customer from test data and navigates to customers page."""
    create_customer(page, test_data)
    # Navigate back to customers page
    page.get_by_role("link", name="account_circle Customers").click()
    page.get_by_role("link", name="Customers", exact=True).click()
    return page


@pytest.fixture
def created_customer_page(logged_in_page: Page, test_data: PrestaShopTestData) -> Page:
    """Create a customer and return to customers page."""
    return setup_data_for_customer_tests(logged_in_page, test_data)


def create_virtual_product(page: Page, test_data: PrestaShopTestData) -> Page:
    """Create a virtual product in PrestaShop."""
    page.get_by_role("link", name="store Catalog").click()
    page.locator("#subtab-AdminProducts").get_by_role("link", name="Products").click()
    page.get_by_role("link", name="add_circle_outline New product").click()
    page.frame_locator('iframe[name="modal-create-product-iframe"]')
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Virtual product qr_code").click()
    page.get_by_role("button", name="Add new product").click()

    page.get_by_role("textbox", name="product_header_name_1 input").fill(
        test_data.virtual_product_name
    )
    page.locator("#product_description_description_1_ifr").content_frame.locator(
        "#tinymce"
    ).fill(test_data.virtual_product_description)
    page.locator("#product_description_description_short_1_ifr").content_frame.locator(
        "#tinymce"
    ).fill(test_data.virtual_product_short_description)
    page.get_by_role("button", name="Add categories").click()
    page.get_by_text(test_data.virtual_product_category, exact=True).click()
    page.get_by_role("button", name="Apply").click()
    page.get_by_role("textbox", name="No brand").click()
    page.get_by_role("option", name=test_data.virtual_product_brand).click()

    page.get_by_role("tab", name="Details").click()
    page.get_by_role("textbox", name="product_details_references_reference input").fill(
        test_data.virtual_product_reference
    )

    page.get_by_role("tab", name="Virtual product").click()
    page.get_by_role("spinbutton", name="Add or subtract items").fill(
        test_data.virtual_product_quantity
    )

    page.get_by_role("tab", name="Pricing").click()
    page.get_by_role("textbox", name="Retail price (tax excl.)").fill(
        test_data.virtual_product_price_tax_excl
    )
    page.locator("#product_pricing_wholesale_price").fill(
        test_data.virtual_product_wholesale_price
    )

    page.get_by_role("tab", name="SEO").click()
    page.get_by_role("textbox", name="product_seo_link_rewrite_1").fill(
        test_data.virtual_product_link_rewrite
    )
    page.get_by_label("Redirection when offline").select_option(
        test_data.virtual_product_offline_redirection
    )

    page.get_by_role("tab", name="Options").click()
    page.locator("#product_options_suppliers_supplier_ids").get_by_text(
        "Accessories supplier"
    ).click()
    page.locator("#product_options_suppliers_supplier_ids").get_by_text(
        "Fashion supplier"
    ).click()

    page.get_by_role(
        "textbox", name="product_options_product_suppliers_1_reference input"
    ).fill(test_data.virtual_product_fashion_supplier_ref)
    page.locator("#product_options_product_suppliers_1_price_tax_excluded").fill(
        test_data.virtual_product_fashion_supplier_price
    )
    page.get_by_role(
        "textbox", name="product_options_product_suppliers_2_reference input"
    ).fill(test_data.virtual_product_accessories_supplier_ref)
    page.locator("#product_options_product_suppliers_2_price_tax_excluded").fill(
        test_data.virtual_product_accessories_supplier_price
    )

    page.get_by_role("button", name="Save").click()
    return page


def setup_data_for_product_delete_tests(
    page: Page, test_data: PrestaShopTestData
) -> Page:
    """Setup data for product delete tests - creates virtual product from test data and navigates to products page."""
    create_virtual_product(page, test_data)
    # Navigate back to products page
    page.get_by_role("link", name="store Catalog").click()
    page.locator("#subtab-AdminProducts").get_by_role("link", name="Products").click()
    return page


@pytest.fixture
def created_product_for_delete_page(
    logged_in_page: Page, test_data: PrestaShopTestData
) -> Page:
    """Create a virtual product for deletion and return to products page."""
    return setup_data_for_product_delete_tests(logged_in_page, test_data)


def create_supplier(page: Page, test_data: PrestaShopTestData) -> Page:
    """Create a supplier in PrestaShop."""
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Brands & Suppliers").click()
    page.get_by_role("link", name="Suppliers", exact=True).click()
    page.get_by_role("link", name="add_circle_outline Add new").click()

    page.get_by_role("textbox", name="supplier_name input").fill(
        test_data.supplier_name
    )
    page.get_by_role("textbox", name="supplier_phone input").fill(
        test_data.supplier_phone
    )
    page.get_by_role("textbox", name="supplier_address input").fill(
        test_data.supplier_address
    )
    page.get_by_role("textbox", name="supplier_city input").fill(
        test_data.supplier_city
    )

    page.get_by_role("textbox", name="United Kingdom").click()
    page.get_by_role("option", name=test_data.supplier_country).click()

    # Handle dynamic state selection
    # page.get_by_role("textbox", name="Aichi").click()
    # can't use this, because the value of state is different each time the page is opened
    state_container = page.locator(".js-supplier-state")
    state_container.get_by_role("combobox").click()
    page.get_by_role("option", name=test_data.supplier_state).click()

    page.get_by_role("radio", name=test_data.supplier_logo_active).check()
    page.get_by_role("button", name="Save").click()
    return page


def setup_data_for_supplier_tests(page: Page, test_data: PrestaShopTestData) -> Page:
    """Setup data for supplier tests - creates supplier from test data and navigates to suppliers page."""
    create_supplier(page, test_data)
    # Navigate back to suppliers page
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Brands & Suppliers").click()
    page.get_by_role("link", name="Suppliers", exact=True).click()
    return page


@pytest.fixture
def created_supplier_page(logged_in_page: Page, test_data: PrestaShopTestData) -> Page:
    """Create a supplier and return to suppliers page."""
    return setup_data_for_supplier_tests(logged_in_page, test_data)
