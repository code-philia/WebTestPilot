from pathlib import Path
import re
import pytest
from unittest.mock import patch
import pytest_asyncio
from collections.abc import AsyncGenerator
from playwright.async_api import Browser as PWBrowser, Locator, Page
from VTAAS.workers.browser import Browser

TEST_HTML = """

<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page</title>
</head>
<body>
    <h1>Test Page for Browser Class</h1>

    <h2>Clicks/h2>
    <button data-mark="simple-button">Click Me</button>
    <a href="https://www.example.com" data-mark="navigation-link">Go to example.com</a>

    <h2>Filling Forms</h2>
    <input type="text" data-mark="text-input" placeholder="Enter text">
    <input type="date" data-mark="date-input">

    <h2>Select Options</h2>
    <label for="dropdownId">Choose an option:</label>
    <select id="dropdownId" data-mark="dropdown">
        <option value="option1">Option 1</option>
        <option value="option2">Option 2</option>
        <option value="option3">Option 3</option>
    </select>
    <div id="notSelectId" data-mark="not-a-select">Not a select element</div>

    <h2>Scrolling</h2>
    <div style="height: 1500px; background-color: lightblue;">
        Scroll down to test scrolling functionality.
    </div>

</body>
</html>
"""


@pytest_asyncio.fixture(scope="session")
async def dummy_page_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a dummy HTML page for testing browser commands."""
    tmp_dir: Path = tmp_path_factory.mktemp("test_pages")
    file_path: Path = tmp_dir / "scroll_test.html"
    _ = file_path.write_text(TEST_HTML)
    return file_path


@pytest_asyncio.fixture
async def browser() -> AsyncGenerator[Browser, None]:
    """create and close Browser"""
    browser_instance = await Browser.create(
        name="browser_tu", timeout=1000, id="test_browser"
    )
    yield browser_instance
    await browser_instance.close()


@pytest.mark.asyncio
async def test_browser_initialization():
    """Test initialization"""
    browser = await Browser.create(timeout=1000, id="test_browser")
    try:
        assert browser.id == "test_browser"
        assert browser.scrolled_to == -1
        assert isinstance(browser.browser, PWBrowser)
        assert isinstance(browser.page, Page)
    finally:
        await browser.close()


@pytest.mark.asyncio
async def test_browser_properties_before_initialization():
    """Test can't access page and browser if create has not been called"""
    browser = Browser(timeout=1000, id="test_browser")  # Not initialized

    with pytest.raises(
        RuntimeError,
        match=re.escape(
            "Browser has not been initialized yet. Do Browser.create(name)."
        ),
    ):
        _ = browser.browser

    with pytest.raises(
        RuntimeError,
        match=re.escape(
            "Browser has not been initialized yet. Do Browser.create(name)."
        ),
    ):
        _ = browser.page


@pytest.mark.asyncio
async def test_goto_valid_url(browser: Browser):
    """Test navigation to a valid URL"""
    result = await browser.goto("https://www.example.com")
    assert result == "Successfully navigated to https://www.example.com"


@pytest.mark.asyncio
async def test_goto_invalid_url(browser: Browser):
    """Test navigation to an invalid URL"""
    result = await browser.goto("not-a-valid-url")
    assert result == "Invalid URL"


@pytest.mark.asyncio
async def test_goto_nonexistent_domain(browser: Browser):
    """Test navigation to a nonexistent domain"""
    result = await browser.goto("https://nonex1stent-domain-name-25115.com")
    assert result.startswith("An error happened while navigating to")


@pytest.mark.parametrize(
    "url,expected_valid",
    [
        ("https://www.example.com", True),
        ("http://localhost:8000", True),
        ("not-a-valid-url", False),
        ("", False),
        (
            "ftp://invalid-protocol.com",
            False,
        ),
    ],
)
def test_is_valid_url(url: str, expected_valid: bool):
    """Test URL validation"""
    assert Browser._is_valid_url(url) == expected_valid


@pytest.mark.asyncio
async def test_reload_valid_url(browser: Browser):
    """Test navigation to a valid URL"""
    url = "https://www.example.com/"
    _ = await browser.goto(url)
    result = await browser.reload()
    assert result == f"Successfully reloaded url {url}"


@pytest.mark.asyncio
async def test_reload_invalid_url(browser: Browser):
    """Test navigation to an invalid URL"""
    url = "not-a-valid-url"
    _ = await browser.goto(url)
    result = await browser.reload()
    assert "Reloaded url about:blank but received" in result


@pytest.mark.asyncio
async def test_vertical_scroll(browser: Browser, dummy_page_path: Path):
    """Test vertical scrolling"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        file_url = f"file://{dummy_page_path}"
        _ = await browser.goto(file_url)

        result = await browser.vertical_scroll("down")
        assert "Successfully scrolled" in result

        await browser.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        result = await browser.vertical_scroll("down")
        assert "already at the bottom" in result

        result = await browser.vertical_scroll("up")
        assert "Successfully scrolled" in result

        await browser.page.evaluate("window.scrollTo(0, 0)")
        result = await browser.vertical_scroll("up")
        assert "already at the top" in result


@pytest.mark.asyncio
async def test_vertical_scroll_with_different_pixels(
    browser: Browser, dummy_page_path: Path
):
    """Test vertical scrolling with -- custom pixel values"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        file_url = f"file://{dummy_page_path}"
        _ = await browser.goto(file_url)

        pixel_values = [100, 200, 500]
        for pixels in pixel_values:
            result = await browser.vertical_scroll("down", pixels)
            print(f"went {pixels} pixels down")
            assert f"Successfully scrolled {pixels} down" in result

            result = await browser.vertical_scroll("up", pixels)
            print(f"went {pixels} pixels up")
            assert f"Successfully scrolled {pixels} up" in result


@pytest.mark.asyncio
async def test_vertical_scroll_invalid_direction(
    browser: Browser, dummy_page_path: Path
):
    """Test vertical scrolling negative direction"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        file_url = f"file://{dummy_page_path}"
        _ = await browser.goto(file_url)

        result = await browser.vertical_scroll("low")
        assert "Invalid direction" in result

        result = await browser.vertical_scroll("down")
        assert "Successfully scrolled" in result


@pytest.mark.asyncio
async def test_vertical_scroll_bad_pixels(browser: Browser, dummy_page_path: Path):
    """Test vertical scrolling bad pixels values"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        file_url = f"file://{dummy_page_path}"
        _ = await browser.goto(file_url)

        result = await browser.vertical_scroll("down", -100)
        assert "negative pixel" in result

        result = await browser.vertical_scroll("down", 9)
        assert "too low" in result

        result = await browser.vertical_scroll("down")
        assert "Successfully scrolled" in result


@pytest.mark.asyncio
async def test_scroll_to(browser: Browser, dummy_page_path: Path):
    """Test scrolled_to properly updated"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        file_url = f"file://{dummy_page_path}"
        _ = await browser.goto(file_url)

        initial_scrolled_to = browser.scrolled_to
        pixels = 450

        _ = await browser.vertical_scroll("down", pixels)
        assert browser.scrolled_to == initial_scrolled_to + pixels

        _ = await browser.vertical_scroll("up", pixels)
        assert browser.scrolled_to == initial_scrolled_to + pixels


@pytest.mark.asyncio
async def test_resolve_mark_select(browser: Browser, dummy_page_path: Path):
    """Test resolving an existing mark"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        file_url = f"file://{dummy_page_path}"
        _ = await browser.goto(file_url)

        result = await browser._resolve_mark("dropdown")
        assert "error" not in result
        assert "locator" in result

        locator = result["locator"]
        assert isinstance(locator, Locator)

        tag_name: str = await locator.evaluate("element => element.tagName")
        assert tag_name == "SELECT"

        tag_name: str = await locator.evaluate("element => element.id")
        assert tag_name == "dropdownId"


@pytest.mark.asyncio
async def test_resolve_mark_fake_select(browser: Browser, dummy_page_path: Path):
    """Test resolving an existing mark"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        file_url = f"file://{dummy_page_path}"
        _ = await browser.goto(file_url)

        result = await browser._resolve_mark("not-a-select")
        assert "error" not in result
        assert "locator" in result

        locator = result["locator"]
        assert isinstance(locator, Locator)

        tag_name: str = await locator.evaluate("element => element.tagName")
        assert tag_name == "DIV"

        tag_name: str = await locator.evaluate("element => element.id")
        assert tag_name == "notSelectId"


@pytest.mark.asyncio
async def test_resolve_mark_fake_select(browser: Browser, dummy_page_path: Path):
    """Test resolving an existing mark"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        file_url = f"file://{dummy_page_path}"
        _ = await browser.goto(file_url)

        result = await browser._resolve_mark("not-a-select")
        assert "error" not in result
        assert "locator" in result


@pytest.mark.asyncio
async def test_resolve_invalid_mark(browser: Browser, dummy_page_path: Path):
    """Test resolving an existing mark"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        file_url = f"file://{dummy_page_path}"
        _ = await browser.goto(file_url)

        result = await browser._resolve_mark("bad-mark")
        assert "error" in result
        assert "locator" not in result

        error = result["error"]
        assert "does not exist" in error


@pytest.mark.asyncio
async def test_get_marks(browser: Browser, dummy_page_path: Path):
    """Test return marked elements as html strings"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        file_url = f"file://{dummy_page_path}"
        _ = await browser.goto(file_url)

        result = await browser.get_marks()
        assert len(result) == 6
        assert result[0]["mark"] == "simple-button"
        assert result[0]["element"] == "<button >Click Me</button>"
        assert result[1]["mark"] == "navigation-link"
        assert (
            result[1]["element"]
            == '<a href="https://www.example.com" >Go to example.com</a>'
        )


@pytest.mark.asyncio
async def test_select_valid_option(browser: Browser, dummy_page_path: Path):
    """Test selecting a valid option from dropdown"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        file_url = f"file://{dummy_page_path}"
        _ = await browser.goto(file_url)

        result = await browser.select("dropdown", "option1")
        assert 'Options "option1" have been selected' in result


@pytest.mark.asyncio
async def test_select_multiple_valid_options(browser: Browser, dummy_page_path: Path):
    """Test selecting multiple valid options"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        file_url = f"file://{dummy_page_path}"
        _ = await browser.goto(file_url)

        result = await browser.select("dropdown", "option1", "option2")
        assert 'Options "option1, option2" have been selected' in result


@pytest.mark.asyncio
async def test_select_invalid_option(browser: Browser, dummy_page_path: Path):
    """Test selecting an invalid option"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        file_url = f"file://{dummy_page_path}"
        _ = await browser.goto(file_url)

        result = await browser.select("dropdown", "invalid_option")
        assert "Available options: option1, option2, option3" in result


@pytest.mark.asyncio
async def test_select_nonexistent_mark(browser: Browser, dummy_page_path: Path):
    """Test selecting from a dropdown that doesn't exist"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        file_url = f"file://{dummy_page_path}"
        _ = await browser.goto(file_url)

        result = await browser.select("nonexistent-dropdown", "option1")
        assert "This mark does not exist" in result


@pytest.mark.asyncio
async def test_select_non_select_element(browser: Browser, dummy_page_path: Path):
    """Test selecting from an element that isn't a select"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        file_url = f"file://{dummy_page_path}"
        _ = await browser.goto(file_url)

        result = await browser.select("not-a-select", "option1")
        assert "does not seem to match a <select> element" in result


@pytest.mark.asyncio
async def test_select_empty_values(browser: Browser, dummy_page_path: Path):
    """Test selecting with no values provided"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        file_url = f"file://{dummy_page_path}"
        _ = await browser.goto(file_url)

        result = await browser.select("dropdown")
        assert "Missing option" in result


@pytest.mark.asyncio
async def test_select_with_page_not_loaded(browser: Browser):
    """Test selecting before navigating to any page"""
    result = await browser.select("dropdown", "option1")
    assert "This mark does not exist" in result


@pytest.mark.asyncio
async def test_click_simple_button(browser: Browser, dummy_page_path: Path):
    """Test clicking a simple button"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        _ = await browser.goto(f"file://{dummy_page_path}")

        result = await browser.click("simple-button")
        assert "Clicked on ['simple-button']" in result
        assert "<button" in result


@pytest.mark.asyncio
async def test_click_navigation(browser: Browser, dummy_page_path: Path):
    """Test clicking a link that takes to another page"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        _ = await browser.goto(f"file://{dummy_page_path}")

        result = await browser.click("navigation-link")
        assert "Clicked on ['navigation-link']" in result
        assert "<a" in result
        assert "page change occurred" in result
        assert "example.com" in result


@pytest.mark.asyncio
async def test_click_nonexistent_mark(browser: Browser, dummy_page_path: Path):
    """Test clicking nonexistant mark"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        _ = await browser.goto(f"file://{dummy_page_path}")

        result = await browser.click("nonexistent-mark")
        assert "This mark does not exist" in result


@pytest.mark.asyncio
async def test_fill_text_input(browser: Browser, dummy_page_path: Path):
    """Test filling a simple text input"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        _ = await browser.goto(f"file://{dummy_page_path}")

        result = await browser.fill("text-input", "This is an ATA")
        assert "Filled value This is an ATA" in result
        assert "text-input" in result

        value = await browser.page.locator('[data-mark="text-input"]').input_value()
        assert value == "This is an ATA"


@pytest.mark.asyncio
async def test_fill_date_input(browser: Browser, dummy_page_path: Path):
    """Test filling a date input"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        _ = await browser.goto(f"file://{dummy_page_path}")

        result = await browser.fill("date-input", "2025-01-01")
        assert "Filled value 2025-01-01" in result

        value = await browser.page.locator('[data-mark="date-input"]').input_value()
        assert value == "2025-01-01"


@pytest.mark.asyncio
async def test_fill_select(browser: Browser, dummy_page_path: Path):
    """Test filling a select element"""
    with patch.object(browser, "_is_valid_url", return_value=True):
        _ = await browser.goto(f"file://{dummy_page_path}")

        result = await browser.fill("dropdown", "option2")
        assert "Filled value option2" in result

        value = await browser.page.locator('[data-mark="dropdown"]').input_value()
        assert value == "option2"
