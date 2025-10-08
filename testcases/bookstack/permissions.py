from bookstack.conftest import BookStackTestData, create_role
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect


def test_create_role(logged_in_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(logged_in_page)

    created_role_page = create_role(logged_in_page, test_data)

    expect(created_role_page.locator("#main-content")).to_contain_text(
        test_data.role_name
    )


def test_assign_role_to_user(
    logged_in_page: Page, test_data: BookStackTestData
) -> None:
    insert_start_event_to_page(logged_in_page)
    logged_in_page.get_by_role("link", name="Settings").click()
    logged_in_page.get_by_role("link", name="Users").click()
    logged_in_page.get_by_role("link", name="Guest guest@example.com").click()
    logged_in_page.locator("label").filter(has_text=test_data.role_name).get_by_role(
        "checkbox"
    ).click()

    logged_in_page.get_by_role("button", name="Save").click()

    expect(
        logged_in_page.get_by_role("alert").filter(has_text="User successfully updated")
    ).to_be_visible(timeout=1000)
    pass
