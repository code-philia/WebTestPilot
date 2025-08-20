import sys
from pathlib import Path

from const import ApplicationEnum
from playwright.sync_api import Page

# Add project directory
PROJECT_DIR = Path(__file__).parent.parent
sys.path.append(str(PROJECT_DIR))

from testcases.bookstack.conftest import (
    BookStackTestData,
    create_book,
    create_chapter,
    create_page,
    create_role,
    create_shelf,
    create_sort_rule,
    go_to_bookstack,
    login_to_bookstack,
    setup_data_for_create_page_template,
    setup_data_for_global_search_page,
    setup_data_for_page_move_chapter,
    setup_data_for_page_move_page,
    setup_data_for_sort_chapter_and_page,
)
from testcases.indico.conftest import (
    IndicoTestData,
    create_conference,
    create_lecture,
    create_meeting,
    go_to_indico,
    login_to_indico,
)
from testcases.invoiceninja.conftest import (
    InvoiceNinjaTestData,
    create_client,
    create_product,
    go_to_invoiceninja,
    login_to_invoiceninja,
    setup_for_credit_page,
    setup_for_expense_page,
    setup_for_invoice_page,
    setup_for_payment_page,
)
from testcases.prestashop.conftest import (
    login_to_prestashop,
    login_to_prestashop_as_buyer,
)


def setup_page_state(
    page: Page, setup_function: str, application: ApplicationEnum
) -> Page:
    """Set up the page state based on the application and setup function.

    Args:
        page: The Playwright page object
        setup_function: The setup function name from test case
        application: The application type

    Returns:
        The configured page object
    """
    if application == ApplicationEnum.bookstack:
        return setup_bookstack_page(page, setup_function)
    elif application == ApplicationEnum.invoiceninja:
        return setup_invoiceninja_page(page, setup_function)
    elif application == ApplicationEnum.indico:
        return setup_indico_page(page, setup_function)
    elif application == ApplicationEnum.prestashop:
        return setup_prestashop_page(page, setup_function)

    raise ValueError(f"Unknown application type: {application}")


def setup_invoiceninja_page(page: Page, setup_function: str) -> Page:
    """Set up InvoiceNinja page based on setup function."""
    test_data = InvoiceNinjaTestData()

    # No setup.
    if setup_function == "":
        return go_to_invoiceninja(page)

    logged_in_page = login_to_invoiceninja(page)

    if setup_function == "logged_in_page":
        return logged_in_page

    elif setup_function == "created_client_page":
        return create_client(logged_in_page, test_data.company_name, test_data)

    elif setup_function == "created_product_page":
        return create_product(logged_in_page, test_data.product_name, test_data)

    elif setup_function == "created_invoice_page":
        return setup_for_invoice_page(logged_in_page, test_data)

    elif setup_function == "created_payment_page":
        return setup_for_payment_page(logged_in_page, test_data)

    elif setup_function == "created_expense_page":
        return setup_for_expense_page(logged_in_page, test_data)

    elif setup_function == "created_credit_page":
        return setup_for_credit_page(logged_in_page, test_data=test_data)

    else:
        raise ValueError(f"Unknown invoiceninja setup function: {setup_function}")


def setup_indico_page(page: Page, setup_function: str) -> Page:
    """Set up Indico page based on setup function."""
    test_data = IndicoTestData()

    # No setup.
    if setup_function == "":
        return go_to_indico(page)

    logged_in_page = login_to_indico(page)

    if setup_function == "logged_in_page":
        return logged_in_page

    elif setup_function == "created_lecture_page":
        return create_lecture(logged_in_page, test_data)

    elif setup_function == "created_meeting_page":
        return create_meeting(logged_in_page, test_data)

    elif setup_function == "created_conference_page":
        return create_conference(logged_in_page, test_data)

    else:
        raise ValueError(f"Unknown indico setup function: {setup_function}")


def setup_prestashop_page(page: Page, setup_function: str) -> Page:
    """Set up PrestaShop page based on setup function."""
    if setup_function == "logged_in_page":
        return login_to_prestashop(page)
    elif setup_function == "logged_in_buyer_page":
        return login_to_prestashop_as_buyer(page)
    else:
        raise ValueError(f"Unknown prestashop setup function: {setup_function}")


def setup_bookstack_page(page: Page, setup_function: str) -> Page:
    """Set up BookStack page based on setup function."""
    test_data = BookStackTestData()

    # No setup.
    if setup_function == "":
        return go_to_bookstack(page)

    logged_in_page = login_to_bookstack(page)

    if setup_function == "logged_in_page":
        return logged_in_page

    elif setup_function == "created_book_page":
        return create_book(
            logged_in_page, test_data.book_name, test_data.book_description
        )

    elif setup_function == "created_chapter_page":
        book_page = create_book(
            logged_in_page, test_data.book_name, test_data.book_description
        )
        return create_chapter(
            book_page, test_data.chapter_name, test_data.chapter_description
        )

    elif setup_function == "created_page_page":
        book_page = create_book(
            logged_in_page, test_data.book_name, test_data.book_description
        )
        return create_page(book_page, test_data.page_name, test_data.page_description)

    elif setup_function == "created_shelf_page":
        return create_shelf(
            logged_in_page,
            test_data.shelf_name,
            test_data.shelf_description,
            [test_data.book_name1, test_data.book_name2],
            test_data.book_description,
        )

    elif setup_function == "created_sort_rule_page":
        return create_sort_rule(logged_in_page, test_data)

    elif setup_function == "created_role_page":
        return create_role(logged_in_page, test_data)

    elif setup_function == "created_data_template_page":
        return setup_data_for_create_page_template(logged_in_page, test_data)

    elif setup_function == "created_data_for_sort_page":
        return setup_data_for_sort_chapter_and_page(logged_in_page, test_data)

    elif setup_function == "created_global_search_page":
        return setup_data_for_global_search_page(logged_in_page, test_data)

    elif setup_function == "created_page_move_page":
        return setup_data_for_page_move_page(logged_in_page, test_data)

    elif setup_function == "created_page_move_chapter":
        return setup_data_for_page_move_chapter(logged_in_page, test_data)

    else:
        raise ValueError(f"Unknown bookstack setup function: {setup_function}")
