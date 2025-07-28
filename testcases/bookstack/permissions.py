from playwright.sync_api import Page
from tracing_api import traced_expect as expect

from bookstack.conftest import BookStackTestData


def test_create_role(created_role_page: Page, test_data: BookStackTestData) -> None:
    expect(created_role_page.locator("#main-content")).to_contain_text(
        test_data.role_name
    )


# TODO: It does not update due to permission in the demo site.
def test_assign_role_to_user(
    created_role_page: Page, test_data: BookStackTestData
) -> None:
    created_role_page.get_by_role("link", name="Users").click()
    created_role_page.get_by_role("link", name="Guest guest@example.com").click()
    created_role_page.locator("label").filter(has_text=test_data.role_name).get_by_role(
        "checkbox"
    ).click()

    created_role_page.get_by_role("button", name="Save").click()

    expect(
        created_role_page.get_by_role("alert").filter(
            has_text="User successfully updated"
        )
    ).to_be_visible(timeout=1000)
    pass
