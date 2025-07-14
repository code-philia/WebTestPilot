from playwright.sync_api import Page, expect

from bookstack.conftest import (
    BookStackTestData,
    create_book,
    create_chapter,
    create_page,
)


def test_move_page(logged_in_page: Page, test_data: BookStackTestData) -> None:
    # Create book, create 1 chapter, create 1 page.
    # Move the page to the chapter.
    create_book_page = create_book(
        logged_in_page, test_data.book_name, test_data.book_description
    )
    chapter_created_page = create_chapter(
        create_book_page, test_data.chapter_name, test_data.chapter_description
    )

    # Go back to book page and create a page.
    chapter_created_page.get_by_role("link", name=test_data.book_name).first.click()
    page_created_page = create_page(
        chapter_created_page, test_data.page_name, test_data.page_description
    )

    # Move the page to the chapter.
    page_created_page.get_by_role("link", name="Move").click()

    # During tests, we create many instances, for stable test, we will search by name.
    page_created_page.locator("#main-content").get_by_role(
        "textbox", name="Search"
    ).click()
    page_created_page.locator("#main-content").get_by_role(
        "textbox", name="Search"
    ).fill(test_data.chapter_name)
    page_created_page.wait_for_timeout(500)  # Wait for search results to load
    page_created_page.get_by_role("link", name=test_data.chapter_name).click()
    page_created_page.get_by_role("button", name="Move Page").click()

    # Verify the page was moved successfully.
    expect(page_created_page.get_by_role("menu")).to_contain_text(test_data.page_name)

    # Check the page's breadcrumb hierarchy.
    expect(page_created_page.get_by_label("Breadcrumb")).to_contain_text(
        test_data.book_name
    )
    expect(page_created_page.get_by_label("Breadcrumb")).to_contain_text(
        test_data.chapter_name
    )
    expect(page_created_page.get_by_label("Breadcrumb")).to_contain_text(
        test_data.page_name
    )

    # Go to chapter and check.
    page_created_page.get_by_label("Breadcrumb").get_by_role(
        "link", name=test_data.chapter_name
    ).click()
    expect(page_created_page.get_by_role("main")).to_contain_text(test_data.page_name)


def test_move_chapter(logged_in_page: Page, test_data: BookStackTestData) -> None:
    # Create 2 books, create 1 chapter in each book.
    # Move the chapter from book 1 to book 2.
    book1_page = create_book(
        logged_in_page, test_data.book_name + " 1", test_data.book_description
    )
    book1_chapter = create_chapter(
        book1_page, test_data.chapter_name + " 1", test_data.chapter_description
    )
    book2_page = create_book(
        book1_chapter, test_data.book_name + " 2", test_data.book_description
    )
    book2_chapter = create_chapter(
        book2_page, test_data.chapter_name + " 2", test_data.chapter_description
    )

    # Move the chapter from book 2 to book 1.
    book2_chapter.get_by_role("link", name="Move").click()

    # During tests, we create many instances, for stable test, we will search by name.
    book2_chapter.locator("#main-content").get_by_role("textbox", name="Search").click()
    book2_chapter.locator("#main-content").get_by_role("textbox", name="Search").fill(
        test_data.book_name + " 1"
    )
    book2_chapter.wait_for_timeout(500)  # Wait for search results to load

    book2_chapter.get_by_role("link", name=test_data.book_name + " 1").click()
    book2_chapter.get_by_role("button", name="Move Chapter").click()

    # Go to book & verify the chapter was moved successfully.
    book2_chapter.get_by_role("link", name="Books", exact=True).first.click()
    book2_chapter.locator("h2", has_text=test_data.book_name + " 1").click()
    expect(book2_chapter.get_by_role("main")).to_contain_text(
        test_data.chapter_name + " 1"
    )
    expect(book2_chapter.get_by_role("main")).to_contain_text(
        test_data.chapter_name + " 2"
    )
