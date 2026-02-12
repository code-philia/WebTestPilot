from typing import Optional
from dataclasses import dataclass

from playwright.sync_api import Page

from baselines.const import ApplicationEnum


@dataclass
class Bookstack:
    URL = "http://localhost:8081"
    USERNAME = "admin@admin.com"
    PASSWORD = "password"


@dataclass
class Invoiceninja:
    URL = "http://localhost:8082"
    USERNAME = "admin@admin.com"
    PASSWORD = "password"


@dataclass
class Indico:
    URL = "http://localhost:8080"
    USERNAME = "admin@admin.com"
    PASSWORD = "webtestpilot"


@dataclass
class Prestashop:
    URL = "http://localhost:8083"
    BUYER_USERNAME = "auto.customer@example.com"
    BUYER_PASSWORD = "mypassword"
    SELLER_USERNAME = "admin@admin.com"
    SELLER_PASSWORD = "admin12345"


def login_to_bookstack(page: Page) -> Page:
    page.goto(Bookstack.URL)
    page.get_by_role("link", name="Log in").click()
    page.get_by_role("textbox", name="Email").fill(Bookstack.USERNAME)
    page.get_by_role("textbox", name="Password").fill(Bookstack.PASSWORD)
    page.get_by_role("button", name="Log In").click()
    return page


def login_to_invoiceninja(page: Page) -> Page:
    page.goto(f"{Invoiceninja.URL}/login")
    page.locator('input[name="email"]').fill(Invoiceninja.USERNAME)
    page.get_by_role("textbox", name="Password").fill(Invoiceninja.PASSWORD)
    page.get_by_role("button", name="Login").click()
    page.get_by_role("button", name="Save").click()
    return page


def login_to_indico(page: Page) -> Page:
    page.goto(Indico.URL)
    page.get_by_role("link", name=" Login").click()
    page.get_by_role("textbox", name="Username or email").fill(Indico.USERNAME)
    page.get_by_role("textbox", name="Password").fill(Indico.PASSWORD)
    page.get_by_role("button", name="Login with Indico").click()

    heading = page.get_by_role("heading", name="February 2025")
    show = page.get_by_role("link", name="Show").first
    for _ in range(50):
        if heading.is_visible():
            break

        if show.is_visible():
            show.click()

        page.wait_for_timeout(200)
    else:
        raise TimeoutError("February 2025 heading never appeared")

    return page


def login_to_prestashop_as_buyer(page: Page) -> Page:
    page.goto(Prestashop.URL)
    page.get_by_role("link", name=" Sign in").click()
    page.get_by_role("textbox", name="Email").fill(Prestashop.BUYER_USERNAME)
    page.get_by_role("textbox", name="Password input").fill(Prestashop.BUYER_PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    return page


def login_to_prestashop_as_seller(page: Page) -> Page:
    page.goto(f"{Prestashop.URL}/webtestpilot/")
    page.get_by_role("textbox", name="Email address").click()
    page.get_by_role("textbox", name="Email address").fill(Prestashop.SELLER_USERNAME)
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill(Prestashop.SELLER_PASSWORD)
    page.get_by_role("button", name="Log in").click()
    page.get_by_role("heading", name="Dashboard").wait_for(state="visible")
    return page


def setup_page_state(application: ApplicationEnum, page: Page, setup_function: Optional[str]) -> Page:
    # Mapping of applications to their setup functions
    app_funcs = {
        ApplicationEnum.bookstack: {
            "login_to_bookstack": login_to_bookstack,
        },
        ApplicationEnum.invoiceninja: {
            "login_to_invoiceninja": login_to_invoiceninja,
        },
        ApplicationEnum.indico: {
            "login_to_indico": login_to_indico,
        },
        ApplicationEnum.prestashop: {
            "login_to_prestashop_as_seller": login_to_prestashop_as_seller,
            "login_to_prestashop_as_buyer": login_to_prestashop_as_buyer
        }
    }

    func = app_funcs.get(application, {}).get(setup_function)

    if func is None:
        raise ValueError(f"Unknown application: {application}, setup_function: {setup_function}")
    
    return func(page)