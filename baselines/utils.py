import sys
from pathlib import Path

from playwright.async_api import Page as AsyncPage
from playwright.sync_api import Page

from .const import ApplicationEnum

# Add project directory
PROJECT_DIR = Path(__file__).parent.parent
sys.path.append(str(PROJECT_DIR))

from testcases.bookstack.conftest import (
    go_to_bookstack,
    login_to_bookstack,
)
from testcases.indico.conftest import (
    login_to_indico,
    login_to_indico_async,
)
from testcases.invoiceninja.conftest import (
    go_to_invoiceninja,
    login_to_invoiceninja,
)
from testcases.prestashop.conftest import (
    login_to_prestashop,
    login_to_prestashop_as_buyer,
    login_to_prestashop_as_buyer_async,
    login_to_prestashop_async,
)


async def setup_page_state(
    page: Page | AsyncPage, setup_function: str, application: ApplicationEnum
) -> Page | AsyncPage:
    if application == ApplicationEnum.bookstack:
        return await setup_bookstack_page(page, setup_function)
    elif application == ApplicationEnum.invoiceninja:
        return await setup_invoiceninja_page(page, setup_function)
    elif application == ApplicationEnum.indico:
        return await setup_indico_page(page, setup_function)
    elif application == ApplicationEnum.prestashop:
        return await setup_prestashop_page(page, setup_function)
    else:
        raise ValueError(f"Unknown application type: {application}")


async def setup_invoiceninja_page(page: Page, setup_function: str) -> Page:
    """Set up InvoiceNinja page based on setup function."""

    # No setup.
    if setup_function == "":
        return go_to_invoiceninja(page)

    logged_in_page = login_to_invoiceninja(page)

    if setup_function == "logged_in_page":
        return logged_in_page

    else:
        raise ValueError(f"Unknown invoiceninja setup function: {setup_function}")


async def setup_indico_page(
    page: Page | AsyncPage, setup_function: str
) -> Page | AsyncPage:
    if isinstance(page, Page):
        return login_to_indico(page)
    else:
        return await login_to_indico_async(page)


async def setup_prestashop_page(
    page: Page | AsyncPage, setup_function: str
) -> Page | AsyncPage:
    if isinstance(page, Page):
        if setup_function == "logged_in_buyer_page":
            logged_in_page = login_to_prestashop_as_buyer(page)
        else:
            logged_in_page = login_to_prestashop(page)

        if setup_function in ("logged_in_page", "logged_in_buyer_page"):
            return logged_in_page
    else:
        if setup_function == "logged_in_buyer_page":
            logged_in_page = await login_to_prestashop_as_buyer_async(page)
        else:
            logged_in_page = await login_to_prestashop_async(page)

        if setup_function in ("logged_in_page", "logged_in_buyer_page"):
            return logged_in_page

    raise ValueError(f"Unknown prestashop setup function: {setup_function}")


async def setup_bookstack_page(page: Page, setup_function: str) -> Page:
    """Set up BookStack page based on setup function."""

    # No setup.
    if setup_function == "":
        return go_to_bookstack(page)

    logged_in_page = login_to_bookstack(page)

    if setup_function == "logged_in_page":
        return logged_in_page

    else:
        raise ValueError(f"Unknown bookstack setup function: {setup_function}")
