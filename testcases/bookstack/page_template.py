from playwright.sync_api import Page
from tracing_api import traced_expect as expect

from bookstack.conftest import BookStackTestData, create_page


def test_create_page_template(
    created_page_page: Page, test_data: BookStackTestData
) -> None:
    # Create 1 more page, 1 is a template, 1 uses the template.
    page_template_name = test_data.page_name + " Template"
    page_template_description = test_data.page_description + " Template"
    created_page_page.get_by_role("link", name=test_data.book_name).first.click()
    created_page_page = create_page(
        created_page_page,
        page_template_name,
        page_template_description,
    )

    # Convert it to template
    created_page_page.get_by_role("link", name="Edit").click()
    # Wait and click the Templates button
    created_page_page.wait_for_timeout(250)
    created_page_page.get_by_role("button", name="Templates").click()
    created_page_page.wait_for_timeout(250)
    created_page_page.get_by_role("checkbox").click()
    created_page_page.get_by_role("button", name="Save Page").click()

    created_page_page.get_by_label("Breadcrumb").get_by_role(
        "link", name=test_data.book_name
    ).click()
    created_page_page.get_by_role("link", name=test_data.page_name, exact=True).click()

    created_page_page.get_by_role("link", name="Edit").click()
    created_page_page.wait_for_timeout(250)
    created_page_page.get_by_role("button", name="Templates").click()
    created_page_page.wait_for_timeout(250)

    # Use the template
    created_page_page.get_by_role(
        "button",
        name=f"Prepend to page content - {page_template_name}",
    ).click()
    created_page_page.get_by_role(
        "button",
        name=f"Append to page content -- {page_template_name}",
    ).click()

    expect(
        created_page_page.locator(
            'iframe[title="Rich Text Area"]'
        ).content_frame.get_by_text(test_data.page_description, exact=True)
    ).to_contain_text(test_data.page_description)

    created_page_page.get_by_role("button", name="Save Page").click()
