from bookstack.conftest import BookStackTestData, create_chapter
from playwright.sync_api import Page
from tracing_api import insert_start_event_to_page
from tracing_api import traced_expect as expect


def test_create_chapter(created_book_page: Page, test_data: BookStackTestData) -> None:
    # Check content of the chapter page
    insert_start_event_to_page(created_book_page)

    created_chapter_page = create_chapter(
        created_book_page, test_data.chapter_name, test_data.chapter_description
    )

    expect(created_chapter_page.locator("h1")).to_contain_text(test_data.chapter_name)
    expect(created_chapter_page.get_by_role("main")).to_contain_text(
        test_data.chapter_description
    )

    # Check the book's chapter list
    created_chapter_page.get_by_label("Book Navigation").get_by_role(
        "link", name=test_data.chapter_name
    ).click()
    expect(created_chapter_page.get_by_role("list")).to_contain_text(
        test_data.chapter_name
    )

    # Navigate back to book page and check
    created_chapter_page.get_by_label("Breadcrumb").get_by_role(
        "link", name=test_data.book_name
    ).click()
    expect(created_chapter_page.get_by_role("main")).to_contain_text(
        test_data.book_name
    )


def test_read_chapter(created_chapter_page: Page, test_data: BookStackTestData) -> None:
    # Navigate back to the book, check the chapter
    insert_start_event_to_page(created_chapter_page)

    created_chapter_page.get_by_label("Breadcrumb").get_by_role(
        "link", name=test_data.book_name
    ).click()

    # Click the chapter link and check content
    expect(created_chapter_page.get_by_role("main")).to_contain_text(
        test_data.chapter_name
    )
    created_chapter_page.get_by_role("link", name=test_data.chapter_name).first.click()

    expect(created_chapter_page.locator("h1")).to_contain_text(test_data.chapter_name)
    expect(created_chapter_page.get_by_role("main")).to_contain_text(
        test_data.chapter_description
    )


def test_update_chapter(
    created_chapter_page: Page, test_data: BookStackTestData
) -> None:
    insert_start_event_to_page(created_chapter_page)

    created_chapter_page.get_by_role("link", name="Edit").click()

    # Name
    created_chapter_page.get_by_role("textbox", name="Name").click()
    created_chapter_page.get_by_role("textbox", name="Name").fill(
        test_data.chapter_name_updated
    )

    # Description
    created_chapter_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.get_by_text(test_data.chapter_description).click()
    created_chapter_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.get_by_label("Rich Text Area. Press ALT-0").fill(
        test_data.chapter_description_updated
    )

    # Tags
    created_chapter_page.get_by_text("Chapter Tags Add some tags to").click()
    created_chapter_page.locator('input[name="tags[0][value]"]').click()
    created_chapter_page.locator('input[name="tags[0][value]"]').fill(
        "Sample Tag Updated"
    )

    created_chapter_page.get_by_role("button", name="Save Chapter").click()

    # Check content.
    expect(
        created_chapter_page.get_by_role("alert").filter(
            has_text="Chapter successfully updated"
        )
    ).to_be_visible(timeout=1000)
    expect(created_chapter_page.locator("h1")).to_contain_text(
        test_data.chapter_name_updated
    )
    expect(created_chapter_page.get_by_role("main")).to_contain_text(
        test_data.chapter_description_updated
    )


def test_delete_chapter(created_chapter_page: Page) -> None:
    insert_start_event_to_page(created_chapter_page)

    created_chapter_page.get_by_role("link", name="Delete").click()
    created_chapter_page.get_by_role("button", name="Confirm").click()

    expect(
        created_chapter_page.get_by_role("alert").filter(
            has_text="Chapter successfully deleted"
        )
    ).to_be_visible()
