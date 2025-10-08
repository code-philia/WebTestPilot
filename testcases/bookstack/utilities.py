from playwright.sync_api import Page

BOOKSTACK_HOST = "http://localhost:8081/"


def navigate_to_book(logged_in_page: Page, book_name: str) -> Page:
    logged_in_page.goto(BOOKSTACK_HOST)
    logged_in_page.get_by_role("link", name="Books", exact=True).click()
    logged_in_page.locator("#main-content").get_by_role(
        "link", name=book_name + " Description"
    ).click()
    return logged_in_page


def navigate_to_chapter(
    logged_in_page: Page, book_name: str, chapter_name: str
) -> Page:
    navigate_to_book(logged_in_page, book_name)
    logged_in_page.get_by_role("link", name=chapter_name).first.click()
    return logged_in_page


def navigate_to_page(logged_in_page: Page, book_name: str, page_name: str) -> Page:
    navigate_to_book(logged_in_page, book_name)
    logged_in_page.get_by_role("link", name=page_name).first.click()
    return logged_in_page


def navigate_to_shelf(logged_in_page: Page, shelf_name: str) -> Page:
    logged_in_page.goto(BOOKSTACK_HOST)
    logged_in_page.get_by_role("link", name="Shelves").click()
    logged_in_page.locator("h2", has_text=shelf_name).click()
    return logged_in_page


def create_shelf_test(
    logged_in_page: Page,
    shelf_name: str,
    shelf_description: str,
    book_names: list[str],
):
    logged_in_page.get_by_role("link", name="Shelves").click()
    logged_in_page.get_by_role("link", name="New Shelf").click()

    # Name & Description
    logged_in_page.get_by_role("textbox", name="Name").fill(shelf_name)
    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_label(
        "Rich Text Area. Press ALT-0"
    ).click()
    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_label(
        "Rich Text Area. Press ALT-0"
    ).fill(shelf_description)

    # Add books to shelf
    for book_name in book_names:
        # Add position to make sure it clicks the button, not the scroll.
        logged_in_page.get_by_role("listitem").filter(
            has_text=book_name
        ).first.get_by_role("button", name="Add").click(position={"x": 0, "y": 0})

    logged_in_page.get_by_role("button", name="Save Shelf").click()
    return logged_in_page


def create_book(logged_in_page: Page, book_name: str, book_description: str) -> Page:
    # To make sure when called multiple times, it starts fresh
    logged_in_page.goto(BOOKSTACK_HOST)

    # Navigate to books and create a new book
    logged_in_page.get_by_role("link", name="Books", exact=True).click()
    logged_in_page.get_by_role("link", name="Create New Book").click()

    # Title and Description
    logged_in_page.get_by_role("textbox", name="Name").click()
    logged_in_page.get_by_role("textbox", name="Name").fill(book_name)
    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_label(
        text="Rich Text Area. Press ALT-0"
    ).click()
    logged_in_page.locator('iframe[title="Rich Text Area"]').content_frame.get_by_label(
        "Rich Text Area. Press ALT-0"
    ).fill(book_description)

    # Book Tags
    logged_in_page.get_by_role("button", name="▸ Book Tags").click()
    logged_in_page.get_by_role("textbox", name="Tag Name").fill("env")
    logged_in_page.locator('input[name="tags[0][value]"]').fill("test")

    # Save
    logged_in_page.get_by_role("button", name="Save Book").click()

    return logged_in_page


def create_chapter_test(
    created_book_page: Page, chapter_name: str, chapter_description: str
) -> Page:
    created_book_page.get_by_role("link", name="New Chapter").click()

    # Name
    created_book_page.get_by_role("textbox", name="Name").click()
    created_book_page.get_by_role("textbox", name="Name").fill(chapter_name)

    # Description
    created_book_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.get_by_label("Rich Text Area. Press ALT-0").click()
    created_book_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.get_by_label("Rich Text Area. Press ALT-0").fill(
        chapter_description
    )

    # Tags
    created_book_page.get_by_role("button", name="▸ Chapter Tags").click()
    created_book_page.get_by_role("textbox", name="Tag Name").click()
    created_book_page.get_by_role("textbox", name="Tag Name").fill("Sample Tag")
    created_book_page.locator('input[name="tags[0][value]"]').click()
    created_book_page.locator('input[name="tags[0][value]"]').fill("Sample Tag")

    created_book_page.get_by_role("button", name="Save Chapter").click()
    return created_book_page


def create_page_test(
    created_book_page: Page,
    page_name: str,
    page_description: str,
) -> Page:
    created_book_page.get_by_role("link", name="New Page").first.click()

    # Title
    created_book_page.get_by_role("textbox", name="Page Title").click()
    created_book_page.get_by_role("textbox", name="Page Title").fill(page_name)

    # Content
    created_book_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.get_by_label("Rich Text Area. Press ALT-0").click()
    created_book_page.locator(
        'iframe[title="Rich Text Area"]'
    ).content_frame.get_by_label("Rich Text Area. Press ALT-0").fill(page_description)

    created_book_page.get_by_role("button", name="Save Page").click()

    return created_book_page
