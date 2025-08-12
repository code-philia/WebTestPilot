import sys
from pathlib import Path
from typing import Literal

from playwright.sync_api import Page

# Add testcases directory to Python path
testcases_dir = Path(__file__).parent.parent
sys.path.append(str(testcases_dir))

from bookstack.conftest import (
    BookStackTestData,
    create_book,
    create_chapter,
    create_page,
    create_role,
    create_shelf,
    create_sort_rule,
    login_to_bookstack,
    setup_data_for_create_page_template,
    setup_data_for_global_search_page,
    setup_data_for_sort_chapter_and_page,
)

ApplicationType = Literal["bookstack", "invoiceninja", "indico", "prestashop"]


def setup_page_state(
    page: Page, setup_function: str, application: ApplicationType
) -> Page:
    if application == "bookstack":
        return setup_bookstack_page(page, setup_function)

    return page


def setup_bookstack_page(page: Page, setup_function: str) -> Page:
    """Setup BookStack page with the specified state using sync fixtures."""
    # Create test data for unique IDs
    test_data = BookStackTestData()

    # Map setup functions to their sync implementations
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
        return create_sort_rule(logged_in_page, test_data.sort_rule_name)

    elif setup_function == "created_role_page":
        return create_role(
            logged_in_page, test_data.role_name, test_data.role_description
        )

    elif setup_function == "created_data_template_page":
        return setup_data_for_create_page_template(logged_in_page, test_data)

    elif setup_function == "created_data_for_sort_page":
        return setup_data_for_sort_chapter_and_page(logged_in_page, test_data)

    elif setup_function == "created_global_search_page":
        return setup_data_for_global_search_page(logged_in_page, test_data)

    else:
        return page
