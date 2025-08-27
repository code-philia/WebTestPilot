from bookstack.conftest import BookStackTestData
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect


def test_create_page_template(
    created_data_template_page: Page, test_data: BookStackTestData
) -> None:
    insert_start_event_to_page(created_data_template_page)

    # 1 is a template, 1 uses the template.
    page = created_data_template_page

    # Convert it to template
    page.get_by_role("link", name="Edit").click()

    # Wait and click the Templates button
    page.wait_for_timeout(250)
    page.get_by_role("button", name="Templates").click()
    page.wait_for_timeout(250)
    page.get_by_role("checkbox").click()
    page.get_by_role("button", name="Save Page").click()

    page.get_by_label("Breadcrumb").get_by_role(
        "link", name=test_data.book_name
    ).click()
    page.get_by_role("link", name=test_data.page_name, exact=True).click()

    page.get_by_role("link", name="Edit").click()
    page.wait_for_timeout(250)
    page.get_by_role("button", name="Templates").click()
    page.wait_for_timeout(250)

    # Use the template
    page.get_by_role(
        "button",
        name=f"Prepend to page content - {test_data.page_template_name}",
    ).click()
    page.get_by_role(
        "button",
        name=f"Append to page content -- {test_data.page_template_name}",
    ).click()

    expect(
        page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_text(
            test_data.page_description, exact=True
        )
    ).to_contain_text(test_data.page_description)

    page.get_by_role("button", name="Save Page").click()
