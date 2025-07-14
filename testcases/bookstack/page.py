from playwright.sync_api import expect, Page

from bookstack.conftest import BookStackTestData


def test_create_page(created_page_page: Page, test_data: BookStackTestData) -> None:
    # Navigate back to book page and check
    created_page_page.get_by_label("Breadcrumb").get_by_role(
        "link", name=test_data.page_name
    ).click()

    # Check content
    expect(created_page_page.get_by_role("main")).to_contain_text(test_data.page_name)
    expect(created_page_page.get_by_role("main")).to_contain_text(test_data.page_description)

    # Check the book's chapter list
    created_page_page.get_by_label("Book Navigation").get_by_role(
        "link", name=test_data.page_name
    ).click()
    expect(created_page_page.get_by_role("list")).to_contain_text(test_data.page_name)

    # Navigate back to book page and check
    created_page_page.get_by_label("Breadcrumb").get_by_role(
        "link", name=test_data.book_name
    ).click()
    expect(created_page_page.get_by_role("main")).to_contain_text(test_data.page_name)


def test_read_page(created_page_page: Page, test_data: BookStackTestData) -> None:
    # Navigate back to the book, check the chapter
    created_page_page.get_by_label("Breadcrumb").get_by_role(
        "link", name=test_data.book_name
    ).click()

    # Click the chapter link and check content
    expect(created_page_page.get_by_role("main")).to_contain_text(test_data.page_name)
    created_page_page.get_by_role("link", name=test_data.page_name).first.click()

    expect(created_page_page.get_by_role("main")).to_contain_text(test_data.page_name)
    expect(created_page_page.get_by_role("main")).to_contain_text(test_data.page_description)


def test_update_page(created_page_page: Page, test_data: BookStackTestData) -> None:
    created_page_page.get_by_role("link", name="Edit").click()

    # Title
    created_page_page.get_by_role("textbox", name="Page Title").click()
    created_page_page.get_by_role("textbox", name="Page Title").press("ControlOrMeta+a")
    created_page_page.get_by_role("textbox", name="Page Title").fill(test_data.page_name_updated)

    # Content
    created_page_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.get_by_text(test_data.page_description).click()
    created_page_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.get_by_label("Rich Text Area. Press ALT-0").press("ControlOrMeta+a")
    created_page_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.get_by_label("Rich Text Area. Press ALT-0").fill(
        test_data.page_description_updated
    )

    created_page_page.get_by_role("button", name="Save Page").click()

    # Check content of the book page
    expect(
        created_page_page.get_by_role("alert").filter(
            has_text="Page successfully updated"
        )
    ).to_be_visible(timeout=1000)
    expect(created_page_page.get_by_role("main")).to_contain_text(test_data.page_name_updated)
    expect(created_page_page.get_by_role("main")).to_contain_text(
        test_data.page_description_updated
    )

    expect(created_page_page.get_by_role("list")).to_contain_text(test_data.page_name_updated)


def test_delete_page(created_page_page: Page) -> None:
    created_page_page.get_by_role("link", name="Delete").click()
    created_page_page.get_by_role("button", name="Confirm").click()

    expect(
        created_page_page.get_by_role("alert").filter(
            has_text="Page successfully deleted"
        )
    ).to_be_visible()
