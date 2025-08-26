from bookstack.conftest import BookStackTestData, create_shelf
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect


def test_create_shelf(logged_in_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(logged_in_page)

    logged_in_page = create_shelf(
        logged_in_page,
        test_data.shelf_name,
        test_data.shelf_description,
        [test_data.book_name1, test_data.book_name2],
        test_data.book_description,
    )
    expect(
        logged_in_page.get_by_role("alert").filter(
            has_text="Shelf successfully created"
        )
    ).to_be_visible(timeout=1000)
    expect(logged_in_page.get_by_role("main")).to_contain_text(test_data.book_name1)
    expect(logged_in_page.get_by_role("main")).to_contain_text(test_data.book_name2)
    pass


def test_read_shelf(created_shelf_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(created_shelf_page)

    created_shelf_page.get_by_role("link", name="Shelves").first.click()

    created_shelf_page.get_by_role("link", name=test_data.shelf_name).first.click()
    expect(created_shelf_page.locator("h1")).to_contain_text(test_data.shelf_name)
    expect(created_shelf_page.get_by_role("main")).to_contain_text(
        test_data.shelf_description
    )
    expect(created_shelf_page.get_by_role("main")).to_contain_text(test_data.book_name1)
    expect(created_shelf_page.get_by_role("main")).to_contain_text(test_data.book_name2)
    pass


def test_update_shelf(created_shelf_page: Page, test_data: BookStackTestData) -> None:
    insert_start_event_to_page(created_shelf_page)

    created_shelf_page.get_by_role("link", name="Edit").click()

    # Name & Description
    created_shelf_page.get_by_role("textbox", name="Name").fill(
        test_data.shelf_name_updated
    )
    created_shelf_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.get_by_label("Rich Text Area. Press ALT-0").click()
    created_shelf_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.get_by_label("Rich Text Area. Press ALT-0").fill(
        test_data.shelf_description_updated
    )

    created_shelf_page.get_by_role("button", name="Save Shelf").click()

    # Check content
    expect(
        created_shelf_page.get_by_role("alert").filter(
            has_text="Shelf successfully updated"
        )
    ).to_be_visible(timeout=1000)
    expect(created_shelf_page.locator("h1")).to_contain_text(
        test_data.shelf_name_updated
    )
    expect(created_shelf_page.get_by_role("main")).to_contain_text(
        test_data.shelf_description_updated
    )


def test_delete_shelf(created_shelf_page: Page) -> None:
    insert_start_event_to_page(created_shelf_page)

    created_shelf_page.get_by_role("link", name="Delete").click()
    created_shelf_page.get_by_role("button", name="Confirm").click()

    expect(
        created_shelf_page.get_by_role("alert").filter(
            has_text="Shelf successfully deleted"
        )
    ).to_be_visible()
