import os
import time
from uuid import uuid4
from urllib.parse import urlparse
from datetime import datetime
from typing import (
    Literal,
    NotRequired,
    TypeAlias,
    TypeVar,
    TypedDict,
    Unpack,
    cast,
    final,
)

import playwright.sync_api as pw

from ..utils.logger import get_logger


T = TypeVar("T", bound="Browser")

ScrollDirection: TypeAlias = Literal["up", "down"]


class ViewportData(TypedDict):
    scrollX: int
    scrollY: int
    viewportWidth: int
    viewportHeight: int
    pageWidth: int
    pageHeight: int


class BrowserParams(TypedDict, total=False):
    name: str
    playwright: pw.Playwright | None
    headless: bool
    timeout: int
    id: str
    save_screenshot: bool
    start_time: float
    tracer: bool
    trace_folder: str


class Mark(TypedDict):
    mark: str
    element: str


class MarkLocatorResult(TypedDict):
    locator: NotRequired[pw.Locator]
    error: NotRequired[str]


@final
class Browser:
    """Playwright based Browser"""

    def __init__(self, **kwargs: Unpack[BrowserParams]):
        default_params: BrowserParams = {
            "name": "missing name",
            "headless": True,
            "timeout": 10000,
            "id": uuid4().hex,
            "playwright": None,
            "save_screenshot": True,
            "start_time": time.time(),
            "tracer": False,
            "trace_folder": ".",
        }
        custom_params = kwargs
        if custom_params and set(custom_params.keys()).issubset(
            set(default_params.keys())
        ):
            default_params.update(custom_params)
        elif custom_params:
            raise ValueError("unknown browser parameter(s) received")

        self._params = default_params
        self._scrolled_to: int = -1
        self._browser: pw.Browser | None = None
        self._context: pw.BrowserContext | None = None
        self._page: pw.Page | None = None
        self.name: str = self._params["name"]
        self.logger = get_logger(
            "Browser - " + self.name + " - " + self._params["id"],
            self._params["start_time"],
            self._params["trace_folder"],
        )
        self.logger.info(f"Browser {self.id} instanciated")
        if self.name == "missing name":
            self.logger.warning("This browser should have a proper name!")

    def initialize(self) -> None:
        """Initialize the browser instance"""
        if not self._params["playwright"]:
            self._params["playwright"] = pw.async_playwright().start()
        self._browser = self._params["playwright"].chromium.launch(
            headless=self._params["headless"], traces_dir=self._params["trace_folder"]
        )
        self._context = self._browser.new_context(bypass_csp=True)
        self._context.set_default_timeout(self._params["timeout"])
        if self._params["tracer"]:
            self.logger.info(
                f"Setting Playwright tracing ON: {self._params['trace_folder']}"
            )
            self._context.tracing.start(screenshots=True, snapshots=True)
        self._page = self._context.new_page()

        self._page.on("load", lambda load: self.load_js())
        self._page.on("framenavigated", lambda load: self.load_js())
        self.logger.info(f"Browser {self.id} started")

    def set_event_for_page(self):
        self._page.on("load", lambda load: self.load_js())
        self._page.on("framenavigated", lambda load: self.load_js())

    def load_js(self):
        _ = self.page.add_script_tag(path="./baselines/pinata/js/mark_page.js")
        _ = self.page.wait_for_function(
            "() => typeof window.markPage === 'function'"
        )
        _ = self.page.add_script_tag(
            path="./baselines/pinata/js/element_to_html_string.js"
        )
        _ = self.page.wait_for_function(
            "() => typeof window.elementToHtmlString  === 'function'"
        )

    @classmethod
    def create(cls: type[T], **kwargs: Unpack[BrowserParams]) -> T:
        """Class method to create and initialize a Browser instance"""
        instance = cls(**kwargs)
        instance.initialize()
        return instance

    @property
    def browser(self) -> pw.Browser:
        """Get the browser instance, ensuring it is initialized"""
        if self._browser is None:
            raise RuntimeError(
                "Browser has not been initialized yet. Do Browser.create(name)."
            )
        return self._browser

    @property
    def context(self) -> pw.BrowserContext:
        """Get the context instance, ensuring it is initialized"""
        if self._context is None:
            raise RuntimeError(
                "Browser has not been initialized yet. Do Browser.create(name)."
            )
        return self._context

    @property
    def page(self) -> pw.Page:
        """Get the page instance, ensuring it is initialized"""
        if self._page is None:
            raise RuntimeError(
                "Browser has not been initialized yet. Do Browser.create(name)."
            )
        return self._page

    @property
    def scrolled_to(self) -> int:
        """Get the maximum scroll value for the current page"""
        return self._scrolled_to

    @property
    def id(self) -> str:
        """Get the maximum scroll value for the current page"""
        return self._params["id"]

    def goto(self, url: str) -> str:
        """Navigate to a URL"""
        if not self._is_valid_url(url):
            return "Invalid URL"
        try:
            response = self.page.goto(url, wait_until="networkidle")
            if response and response.ok:
                return f"Successfully navigated to {url}"
            else:
                status = response.status if response else "unknown"
                return f"Navigate to {url} but page return an {status} status"
        except Exception as e:
            self.logger.error(f"Navigation error: {str(e)}")
            return f"An error happened while navigating to {url}"

    def reload(self) -> str:
        url = self.page.url
        try:
            response = self.page.reload(wait_until="networkidle")
            if response and response.ok:
                return f"Successfully reloaded url {url}"
            else:
                status = response.status if response else "unknown"
                return f"Reloaded url {url} but received a {status} status"
        except Exception as e:
            self.logger.error(f"Reload error: {str(e)}")
            return f"An error happened while reloading url {url}"

    def click(self, mark: str) -> str:

        before_url = self.page.url
        outcome = ""
        result = self._resolve_mark(mark)

        if "error" in result or "locator" not in result:
            error_message = result.get("error", "Unknown error")
            self.logger.error(
                f"[DEBUG] Failed to resolve mark '{mark}' into a clickable element. Error: {error_message}"
            )
            return error_message

        locator = result["locator"]
        html_element_str = self.get_html_element_from_locator(result["locator"])
        outcome += f"Clicked on ['{mark}'] ==> {html_element_str}. "

        try:
            # Using force=True and a timeout is a more robust way to click
            locator.click(force=True, timeout=5000)
            self.page.wait_for_load_state("domcontentloaded")
        except Exception as error:
            # Log the full traceback information
            self.logger.error(
                f"[DEBUG] A fatal error occurred while clicking element '{mark}': {error}",
                exc_info=True,
            )
            return f"Unable to click on element '{mark}' due to a timeout or error: {error}"

        after_url = self.page.url
        is_url_effect = before_url != after_url
        if is_url_effect:
            outcome += f"A page change occurred. New URL: {after_url}"
        else:
            self.logger.info("[DEBUG] URL did not change after click.")

        return outcome.strip()

    def fill(self, mark: str, value: str) -> str:
        result = self._resolve_mark(mark)
        if "error" in result or "locator" not in result:
            return result.get("error", "Unknown error")

        locator = result["locator"]
        html_element_str = self.get_html_element_from_locator(result["locator"])
        tag: str = locator.evaluate("element => element.nodeName")

        try:
            if (
                tag == "INPUT"
                and locator.evaluate("element => element.type") == "date"
            ):
                locator.fill(value)
            elif tag == "SELECT":
                _ = locator.select_option(value)
            else:
                locator.clear()
                locator.type(value, delay=50)

            typed_value = locator.input_value()
            if typed_value == value:
                outcome = (
                    f"Filled value {value} in element [{mark}] ==> {html_element_str}"
                )
                return outcome

            return f"Could not fill {html_element_str} element. Are you sure this is the right label?"
        except Exception as e:
            print(e)
            return f"There was an error while filling {html_element_str} element."

    def vertical_scroll(self, direction: str, pixels: int = 450) -> str:
        """Scroll the page vertically"""
        if pixels < 0:
            return "negative pixel values not allowed."
        if pixels < 10:
            return "Pixel value is too low. Expecting 10 or more."
        viewport_data = self._get_viewport_data()
        scroll_y = viewport_data["scrollY"]
        viewport_height = viewport_data["viewportHeight"]
        page_height = viewport_data["pageHeight"]

        try:
            match direction:
                case "up":
                    print(
                        f"page_height: {page_height}, viewport_height: {viewport_height}, scroll_y: {scroll_y}"
                    )
                    if scroll_y == 0:
                        return (
                            "You can't scroll up: you're already at the top of the page"
                        )
                    self.page.mouse.wheel(0, -pixels)
                    target = max(scroll_y - pixels, 0)
                    _ = self.page.wait_for_function(
                        f"window.scrollY === {target}"
                    )

                case "down":
                    max_scroll = page_height - viewport_height
                    if scroll_y >= max_scroll - 10:
                        return "You can't scroll down: you're already at the bottom of the page"
                    remaining_scroll = max_scroll - scroll_y
                    scroll_amount = min(pixels, max_scroll - scroll_y)
                    self._scrolled_to += scroll_amount
                    self.page.mouse.wheel(0, scroll_amount)
                    _ = self.page.wait_for_function(
                        f"window.scrollY >= {scroll_amount}"
                    )

                case _:
                    return 'Invalid direction. Expected "up" or "down".'

            return f"Successfully scrolled {pixels} {direction}"

        except Exception as e:
            error_msg = f"An error happened while scrolling {pixels} {direction}"
            self.logger.error(f"{error_msg}: {str(e)}")
            return error_msg

    def select(self, mark: str, *values: str) -> str:
        """
        Select options in a dropdown element identified by its label
        """
        if not values:
            return "Missing option(s) to select"

        result = self._resolve_mark(mark)
        if "error" in result or "locator" not in result:
            return result.get("error", "Unknown error")

        locator = result["locator"]
        try:
            result = locator.select_option(values)
            if result:
                outcome = f'Options "{", ".join(values)}" have been selected'
            else:
                outcome = "No option selected"
            return outcome

        except Exception as e:
            error_msg = str(e)
            if "did not find some options" in error_msg:
                available_options: list[str] = locator.evaluate("""
                    (element) => {
                        if (element instanceof HTMLSelectElement) {
                            return Array.from(element.options).map(option => option.value);
                        } else return []
                    }
                """)

                available_options_str = (
                    ", ".join(available_options) if available_options else "unknown"
                )
                return (
                    f"The select element exists but does not contain the provided option. "
                    f"Available options: {available_options_str}. "
                )

            return "The label does not seem to match a <select> element. Maybe it is a styled DIV?"

    def screenshot(self) -> bytes:
        try:
            screenshot = self.page.screenshot()
            if self._params["save_screenshot"]:
                self._save_screenshot(screenshot)
            return screenshot

        except Exception as e:
            self.logger.error(f"Screenshot error: {str(e)}")
            return b""

    def _save_screenshot(self, screenshot: bytes):
        screenshots_path = os.path.join(self._params["trace_folder"], "screenshots")
        os.makedirs(screenshots_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{self.id}_{timestamp}.png"
        with open(os.path.join(screenshots_path, filename), "wb") as f:
            _ = f.write(screenshot)

    def mark_page(self):
        _ = self.page.wait_for_function(
            "() => typeof window.markPage === 'function'"
        )
        self.page.evaluate("window.markPage()")

    def unmark_page(self):
        _ = self.page.wait_for_function(
            "() => typeof window.unmarkPage === 'function'"
        )
        self.page.evaluate("window.unmarkPage()")

    def get_marks(self) -> list[Mark]:
        return cast(
            list[Mark],
            self.page.evaluate("""async () => {
          const marks = []
          document.querySelectorAll('[data-mark]').forEach((e) => {
            marks.push({ mark: e.getAttribute('data-mark'), element: window.elementToHtmlString(e) })
          })
          return marks
        }"""),
        )

    def get_html_element_from_locator(self, locator: pw.Locator) -> str:
        _ = self.page.wait_for_function(
            "() => typeof window.elementToHtmlString === 'function'"
        )
        element: str = locator.evaluate(
            """(element) => window.elementToHtmlString(element)"""
        )
        return element

    def get_page_info(self) -> str:
        """Get current page information"""
        title = self.page.title()
        url = self.page.url
        return f"Current URL: {url}\nPage title: {title}"

    def get_viewport_info(self) -> str:
        viewport_data = self._get_viewport_data()
        scroll_X, scroll_Y, viewport_height, viewport_width, page_height, page_width = (
            viewport_data["scrollX"],
            viewport_data["scrollY"],
            viewport_data["viewportHeight"],
            viewport_data["viewportWidth"],
            viewport_data["pageHeight"],
            viewport_data["pageWidth"],
        )
        position_description = ""
        if scroll_Y == 0:
            position_description = "You are at the top of the page. "
        elif scroll_Y >= page_height - viewport_height - 10:
            position_description = "You are at the bottom of the page. "
        return f"{position_description}Viewport size: {viewport_width} x {viewport_height}, Viewport position: ({scroll_X}, {scroll_Y}), Page size: {page_width} x {page_height}"

    def close(self) -> None:
        """Close the browser instance"""
        output_path = os.path.join(self._params["trace_folder"], "trace.zip")
        if self._params["tracer"]:
            self.logger.info(f"Saving trace to {output_path}")
            self.context.tracing.stop(path=output_path)
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self._browser:
            self._browser.close()
        self.logger.handlers.clear()

    def _resolve_mark(self, mark: str) -> MarkLocatorResult:
        """
        Resolve a mark to a Playwright locator
        """
        try:
            locators = self.page.locator(f'[data-mark="{mark}"]').all()
            if len(locators) < 1:
                return {
                    "error": "This mark does not exist",
                }
            return {"locator": locators[0]}
        except Exception as e:
            return {"error": f"Could not resolve mark: {str(e)}"}

    def _get_viewport_data(self) -> ViewportData:
        """Get viewport related data"""
        return cast(
            ViewportData,
            self.page.evaluate("""
            () => ({
                scrollX: window.scrollX,
                scrollY: window.scrollY,
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                pageWidth: document.documentElement.scrollWidth,
                pageHeight: document.documentElement.scrollHeight
            })
        """),
        )

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return bool(result.scheme in ["http", "https"] and result.netloc)
        except Exception:
            return False
