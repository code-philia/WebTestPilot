from playwright.sync_api import Page


def create_attribute(
    page: Page, name: str = "Weight", public_name: str = "Weight"
) -> Page:
    """Create an attribute in PrestaShop."""
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Attributes & Features").click()
    page.get_by_role("link", name="Add new attribute").click()
    page.locator("#name_1").fill(name)
    page.locator("#public_name_1").fill(public_name)
    page.get_by_role("button", name="Save").click()
    return page


def create_feature(page: Page, name: str = "Season") -> Page:
    """Create a feature in PrestaShop."""
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Attributes & Features").click()
    page.get_by_role("link", name="Features", exact=True).click()
    page.get_by_role("link", name=" Add new feature", exact=True).click()
    page.locator("#name_1").fill(name)
    page.get_by_role("button", name="Save").click()
    return page


def create_brand(
    page: Page, name: str = "Nike", description: str = "Description"
) -> Page:
    """Create a brand in PrestaShop."""
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Brands & Suppliers").click()
    page.get_by_role(
        "link", name="add_circle_outline Add new brand", exact=True
    ).click()

    page.get_by_role("textbox", name="manufacturer_name input").fill(name)
    page.locator("#manufacturer_description_1_ifr").content_frame.locator(
        "#tinymce"
    ).fill(description)

    page.get_by_role("button", name="Save").click()
    return page


def create_parent_category(
    page: Page,
    name: str = "Shoes",
    parent: str = "Home",
    description: str = "Description",
    link_rewrite: str = "shoes",
) -> Page:
    """Create a parent category in PrestaShop."""
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Categories").click()
    page.get_by_role("link", name="add_circle_outline Add new").click()

    page.get_by_role("textbox", name="category_name_1 input").fill(name)
    page.get_by_text("expand_more Expand").click()
    page.get_by_text(parent, exact=True).click()
    page.locator("#category_description_1_ifr").content_frame.locator("#tinymce").fill(
        description
    )
    page.get_by_role("textbox", name="category_link_rewrite_1 input").fill(link_rewrite)

    page.get_by_role("button", name="Save").click()
    return page


def create_child_category(
    page: Page,
    name: str = "Sports shoes",
    parent: str = "Shoes",
    description: str = "Description",
    link_rewrite: str = "sports-shoes",
) -> Page:
    """Create a child category in PrestaShop."""
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Categories").click()
    page.get_by_role("link", name="add_circle_outline Add new").click()

    page.get_by_role("textbox", name="category_name_1 input").fill(name)
    page.get_by_text("expand_more Expand").click()
    page.get_by_text(parent, exact=True).click()
    page.locator("#category_description_1_ifr").content_frame.locator("#tinymce").fill(
        description
    )
    page.get_by_role("textbox", name="category_link_rewrite_1 input").fill(link_rewrite)

    page.get_by_role("button", name="Save").click()
    return page


def create_customer(
    page: Page,
    social_title: str = "Mr.",
    first_name: str = "Jones",
    last_name: str = "Jonathan",
    email: str = "test@test.com",
    password: str = "testTEST123.",
    birth_year: str = "2003",
    birth_month: str = "1",
    birth_day: str = "1",
) -> Page:
    """Create a customer in PrestaShop."""
    page.get_by_role("link", name="account_circle Customers").click()
    page.get_by_role("link", name="Customers", exact=True).click()
    page.get_by_role("link", name="add_circle_outline Add new").click()

    page.locator("label").filter(has_text=social_title).locator("i").click()
    page.get_by_role("textbox", name="customer_first_name input").fill(first_name)
    page.get_by_role("textbox", name="customer_last_name input").fill(last_name)
    page.get_by_role("textbox", name="* Email").fill(email)
    page.get_by_role("textbox", name="Password").fill(password)
    page.locator("#customer_birthday_year").select_option(birth_year)
    page.locator("#customer_birthday_month").select_option(birth_month)
    page.locator("#customer_birthday_day").select_option(birth_day)

    page.get_by_role("button", name="Save").click()
    return page


def create_virtual_product(
    page: Page,
    name: str = "bird",
    description: str = "Description",
    short_description: str = "Vector graphic, format: svg. Download for personal, private and non-commercial use.",
    category: str = "Art",
    brand: str = "Graphic Corner",
    reference: str = "test1",
    quantity: str = "300",
    price_tax_excl: str = "9.000000",
    wholesale_price: str = "5.490000",
    link_rewrite: str = "bird-vector-graphics",
    offline_redirection: str = "default",
    fashion_supplier_ref: str = "test1",
    fashion_supplier_price: str = "6.490000",
    accessories_supplier_ref: str = "test1",
    accessories_supplier_price: str = "5.490000",
) -> Page:
    """Create a virtual product in PrestaShop."""
    page.get_by_role("link", name="store Catalog").click()
    page.locator("#subtab-AdminProducts").get_by_role("link", name="Products").click()
    page.get_by_role("link", name="add_circle_outline New product").click()
    page.frame_locator('iframe[name="modal-create-product-iframe"]')
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Virtual product qr_code").click()
    page.get_by_role("button", name="Add new product").click()

    page.get_by_role("textbox", name="product_header_name_1 input").fill(name)
    page.locator("#product_description_description_1_ifr").content_frame.locator(
        "#tinymce"
    ).fill(description)
    page.locator("#product_description_description_short_1_ifr").content_frame.locator(
        "#tinymce"
    ).fill(short_description)
    page.get_by_role("button", name="Add categories").click()
    page.get_by_text(category, exact=True).click()
    page.get_by_role("button", name="Apply").click()
    page.get_by_role("textbox", name="No brand").click()
    page.get_by_role("option", name=brand).click()

    page.get_by_role("tab", name="Details").click()
    page.get_by_role("textbox", name="product_details_references_reference input").fill(
        reference
    )

    page.get_by_role("tab", name="Virtual product").click()
    page.get_by_role("spinbutton", name="Add or subtract items").fill(quantity)

    page.get_by_role("tab", name="Pricing").click()
    page.get_by_role("textbox", name="Retail price (tax excl.)").fill(price_tax_excl)
    page.locator("#product_pricing_wholesale_price").fill(wholesale_price)

    page.get_by_role("tab", name="SEO").click()
    page.get_by_role("textbox", name="product_seo_link_rewrite_1").fill(link_rewrite)
    page.get_by_label("Redirection when offline").select_option(offline_redirection)

    page.get_by_role("tab", name="Options").click()
    page.locator("#product_options_suppliers_supplier_ids").get_by_text(
        "Accessories supplier"
    ).click()
    page.locator("#product_options_suppliers_supplier_ids").get_by_text(
        "Fashion supplier"
    ).click()

    page.get_by_role(
        "textbox", name="product_options_product_suppliers_1_reference input"
    ).fill(fashion_supplier_ref)
    page.locator("#product_options_product_suppliers_1_price_tax_excluded").fill(
        fashion_supplier_price
    )
    page.get_by_role(
        "textbox", name="product_options_product_suppliers_2_reference input"
    ).fill(accessories_supplier_ref)
    page.locator("#product_options_product_suppliers_2_price_tax_excluded").fill(
        accessories_supplier_price
    )

    page.get_by_role("button", name="Save").click()
    return page


def create_supplier(
    page: Page,
    name: str = "Shoes supplier",
    phone: str = "090-1234-5678",
    address: str = "Nishi-Shinjuku 1-25-1",
    city: str = "Tokyo",
    country: str = "Japan",
    state: str = "Aichi",
    logo_active: str = "Yes",
) -> Page:
    """Create a supplier in PrestaShop."""
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Brands & Suppliers").click()
    page.get_by_role("link", name="Suppliers", exact=True).click()
    page.get_by_role("link", name="add_circle_outline Add new").click()

    page.get_by_role("textbox", name="supplier_name input").fill(name)
    page.get_by_role("textbox", name="supplier_phone input").fill(phone)
    page.get_by_role("textbox", name="supplier_address input").fill(address)
    page.get_by_role("textbox", name="supplier_city input").fill(city)

    page.get_by_role("textbox", name="United Kingdom").click()
    page.get_by_role("option", name=country).click()

    # Handle dynamic state selection
    state_container = page.locator(".js-supplier-state")
    state_container.get_by_role("combobox").click()
    page.get_by_role("option", name=state).click()

    page.get_by_role("radio", name=logo_active).check()
    page.get_by_role("button", name="Save").click()
    return page


# Functions used for navigation in tests
def go_to_attribute_page(page: Page) -> None:
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Attributes & Features").click()


def go_to_brand_page(page: Page) -> None:
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Brands & Suppliers").click()


def go_to_customer_page(page: Page) -> None:
    page.get_by_role("link", name="account_circle Customers").click()
    page.get_by_role("link", name="Customers", exact=True).click()


def go_to_product_page(page: Page) -> None:
    page.get_by_role("link", name="store Catalog").click()
    page.locator("#subtab-AdminProducts").get_by_role("link", name="Products").click()


def go_to_category_page(page: Page) -> None:
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Categories").click()


def go_to_supplier_page(page: Page) -> None:
    page.get_by_role("link", name="store Catalog").click()
    page.get_by_role("link", name="Brands & Suppliers").click()
    page.get_by_role("link", name="Suppliers", exact=True).click()


def add_product_to_wishlist(
    page: Page, search_name: str = "Hummingbird printed t-shirt"
) -> Page:
    """Add a product to the wishlist."""
    page.get_by_role("textbox", name="Search").fill(search_name)
    page.get_by_role("textbox", name="Search").press("Enter")
    product_article = page.get_by_role("article").filter(has_text=search_name)
    product_article.locator(".wishlist-button-add").click()
    page.wait_for_timeout(1000)
    return page
