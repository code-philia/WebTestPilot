import re
import io
import time
import base64
import logging
import traceback
from functools import partial
from copy import deepcopy

import PIL.Image
from baml_py import Image, ClientRegistry, Collector
from playwright.sync_api import Page, ElementHandle

from executor.assertion_api.session import Session
from baml_client.sync_client import b


# -------------------------
# Globals
# -------------------------
logger = logging.getLogger(__name__)
_current_page: Page | None = None
_trace: list[dict] = []


# -------------------------
# Helpers
# -------------------------
def _parse_coordinates(output_text: str) -> tuple[int, int]:
    # Note: this assumes screenshot is 1920 * 1080px
    box = eval(output_text)
    input_height = 1092
    input_width = 1932
    abs_x1 = float(box[0]) / input_width
    abs_y1 = float(box[1]) / input_height
    abs_x2 = float(box[2]) / input_width
    abs_y2 = float(box[3]) / input_height
    bbox = [abs_x1, abs_y1, abs_x2, abs_y2]
    point = [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]
    return point[0] * 1920, point[1] * 1080


def _get_element(page: Page, x: int, y: int) -> ElementHandle:
    handle = page.evaluate_handle(f"""
    () => {{
      const clickableTags = ['BUTTON','A','INPUT','TEXTAREA','SELECT'];
      const clickableRoles = ['button','link','menuitem'];

      // create a temporary highlight circle at (x,y)
      try {{
        const highlightId = '__wpt_highlight_circle';
        const existing = document.getElementById(highlightId);
        if (existing) existing.remove();

        const r = 35; // radius in px
        const div = document.createElement('div');
        div.id = highlightId;
        Object.assign(div.style, {{
          position: 'absolute',
          left: ({x} - r) + 'px',
          top: ({y} - r) + 'px',
          width: (r * 2) + 'px',
          height: (r * 2) + 'px',
          borderRadius: '50%',
          background: 'rgba(255,200,0,0.20)',
          boxShadow: '0 0 12px 4px rgba(255,200,0,0.6)',
          border: '2px solid rgba(255,165,0,0.95)',
          pointerEvents: 'none',
          zIndex: '2147483647',
          transition: 'opacity 0.45s ease-out, transform 0.45s ease-out',
          transform: 'scale(1)'
        }});
        document.body.appendChild(div);
        // fade and remove after a short delay
        setTimeout(() => {{
          div.style.opacity = '0';
          div.style.transform = 'scale(1.4)';
          setTimeout(() => div.remove(), 450);
        }}, 600);
      }} catch (e) {{
        // ignore highlight errors
      }}

      const els = document.elementsFromPoint({x}, {y});
      for (const el of els) {{
        const style = window.getComputedStyle(el);
        if (
          style.pointerEvents !== 'none' &&
          style.visibility !== 'hidden' &&
          el.offsetWidth > 0 &&
          el.offsetHeight > 0 &&
          (clickableTags.includes(el.tagName) ||
           clickableRoles.includes(el.getAttribute('role')) ||
           el.getAttribute('onclick'))
        ) {{
          return el;
        }}
      }}
      return els[0] || null; // fallback
    }}
    """)

    return handle.as_element() if handle else None


def _get_xpath(element: ElementHandle) -> str:
    return element.evaluate("""
    (el) => {
        if (!el) return '';
        const parts = [];
        while (el && el.nodeType === Node.ELEMENT_NODE) {
            let idx = 1;
            let sibling = el.previousElementSibling;
            while (sibling) {
                if (sibling.tagName === el.tagName) idx++;
                sibling = sibling.previousElementSibling;
            }
            parts.unshift(el.tagName.toLowerCase() + '[' + idx + ']');
            el = el.parentElement;
        }
        return '/' + parts.join('/');
    }
    """)


def _get_screenshot() -> Image:
    screenshot = base64.b64encode(_current_page.screenshot(type="png")).decode("utf-8")
    return Image.from_base64("image/png", screenshot)


def _set_page(page: Page):
    global _current_page
    _current_page = page


def _require_page():
    if _current_page is None:
        raise RuntimeError("No active page. Call set_page() first.")


def _focus(x: int, y: int):
    _current_page.evaluate(
        """({ x, y }) => {
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            const docWidth = document.documentElement.scrollWidth;
            const docHeight = document.documentElement.scrollHeight;

            if (docWidth <= viewportWidth && docHeight <= viewportHeight) {
                // No scrolling possible
                return false;
            }

            let scrollX = x - viewportWidth / 2;
            let scrollY = y - viewportHeight / 2;

            const maxScrollX = docWidth - viewportWidth;
            const maxScrollY = docHeight - viewportHeight;
            scrollX = Math.max(0, Math.min(scrollX, maxScrollX));
            scrollY = Math.max(0, Math.min(scrollY, maxScrollY));

            window.scrollTo(scrollX, scrollY);
            return true;
        }""",
        {"x": x, "y": y},
    )


def click(cr: ClientRegistry, collector: Collector, target_description: str):
    _require_page()

    screenshot = _get_screenshot()
    logger.debug(f"Locating element to click: {target_description}")
    coordinates = b.LocateUIElement(
        screenshot,
        target_description,
        baml_options={"client_registry": cr, "collector": collector},
    )
    x, y = _parse_coordinates(coordinates)

    _focus(x, y)
    element: ElementHandle = _get_element(_current_page, x, y)
    xpath = _get_xpath(element)
    logger.debug(f"Clicking element at ({x}, {y}) with element: {element} and xpath: {xpath}")
    element.click(force=True)

    _trace.append({"action": {"name": "click", "args": {"xpath": xpath}}})


def type(
    cr: ClientRegistry, collector: Collector, target_description: str, content: str
):
    _require_page()

    screenshot = _get_screenshot()
    coordinates = b.LocateUIElement(
        screenshot,
        target_description,
        baml_options={"client_registry": cr, "collector": collector},
    )
    x, y = _parse_coordinates(coordinates)

    _focus(x, y)
    element: ElementHandle = _get_element(_current_page, x, y)
    element.type(content)

    _trace.append({"action": {"name": "fill", "args": {"xpath": _get_xpath(element)}}})


def drag(
    cr: ClientRegistry,
    collector: Collector,
    source_description: str,
    target_description: str,
):
    _require_page()

    screenshot = _get_screenshot()
    source_coordinates = b.LocateUIElement(
        screenshot,
        source_description,
        baml_options={"client_registry": cr, "collector": collector},
    )
    source_x, source_y = _parse_coordinates(source_coordinates, screenshot)
    target_coordinates = b.LocateUIElement(
        screenshot,
        target_description,
        baml_options={"client_registry": cr, "collector": collector},
    )
    target_x, target_y = _parse_coordinates(target_coordinates, screenshot)

    # Move to source position
    _current_page.mouse.move(source_x, source_y)

    # Press mouse button down
    _current_page.mouse.down()

    # Move to target position with intermediate steps
    steps = 10
    delay_ms = 200
    for i in range(1, steps + 1):
        ratio = i / steps
        intermediate_x = int(source_x + (target_x - source_x) * ratio)
        intermediate_y = int(source_y + (target_y - source_y) * ratio)
        _current_page.mouse.move(intermediate_x, intermediate_y)
        time.sleep(delay_ms / 1000)

    # Move to final target position
    _current_page.mouse.move(target_x, target_y)

    # Move again to ensure dragover events are properly triggered
    _current_page.mouse.move(target_x, target_y)

    # Release mouse button
    _current_page.mouse.up()

    _trace.append(
        {
            "action": {
                "name": "drag",
                "args": {
                    "source_xpath": _get_xpath(
                        _get_element(_current_page, source_x, source_y)
                    ),
                    "target_xpath": _get_xpath(
                        _get_element(_current_page, target_x, target_y)
                    ),
                },
            }
        }
    )


def scroll(
    cr: ClientRegistry,
    collector: Collector,
    target_description: str | None,
    direction: str,
):
    _require_page()

    direction = direction.lower()
    if direction not in {"up", "down", "left", "right"}:
        raise ValueError("direction must be one of 'up', 'down', 'left', or 'right'")

    # Default values: scroll window
    coords = None
    screenshot = _get_screenshot()
    if target_description is not None:
        coords = _parse_coordinates(
            b.LocateUIElement(
                screenshot,
                target_description,
                baml_options={"client_registry": cr, "collector": collector},
            ),
            screenshot,
        )

    _current_page.evaluate(
        """
    (coords, direction) => {
      let el, scrollAmountVertical, scrollAmountHorizontal;

      if (coords) {
        const [x, y] = coords;
        el = document.elementFromPoint(x, y);
        if (!el) return;
        const rect = el.getBoundingClientRect();
        scrollAmountVertical = rect.height;
        scrollAmountHorizontal = rect.width;
      } else {
        el = window;
        scrollAmountVertical = window.innerHeight;
        scrollAmountHorizontal = window.innerWidth;
      }

      switch (direction) {
        case 'up':
          el.scrollBy(0, -scrollAmountVertical);
          break;
        case 'down':
          el.scrollBy(0, scrollAmountVertical);
          break;
        case 'left':
          el.scrollBy(-scrollAmountHorizontal, 0);
          break;
        case 'right':
          el.scrollBy(scrollAmountHorizontal, 0);
          break;
      }
    }
    """,
        coords,
        direction,
    )


def wait(duration: int):
    if duration <= 0:
        raise ValueError("Wait duration must be >0 miliseconds")

    time.sleep(duration / 1000)


def finished():
    pass


def execute(code: str, page: Page, session: Session) -> list[dict]:
    """
    Safely execute LLM-generated Python code blocks containing only automation actions.
    Automatically sets the current Playwright Page before execution.
    """
    cr: ClientRegistry = session.config.ui_locator
    collector: Collector = session.collector
    safe_globals = {
        "click": partial(click, cr, collector),
        "type": partial(type, cr, collector),
        "drag": partial(drag, cr, collector),
        "scroll": partial(scroll, cr, collector),
        "wait": wait,
        "finished": finished,
    }

    # Remove triple backticks and optional 'python' tag
    try:
        _set_page(page)  # Bind this run to the given page

        cleaned_code = re.sub(
            r"^```(?:python)?|```$", "", code.strip(), flags=re.MULTILINE
        ).strip()

        exec(cleaned_code, safe_globals, {})
    finally:
        trace = deepcopy(_trace)
        _trace.clear()

    return trace
