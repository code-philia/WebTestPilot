import re
import time
import logging
import traceback
from copy import deepcopy

from baml_client.sync_client import b
from playwright.sync_api import Page, ElementHandle


# -------------------------
# Globals
# -------------------------
logger = logging.getLogger(__name__)
_current_page: Page | None = None
_trace: list[dict] = []

# -------------------------
# Helpers
# -------------------------
def _parse_coordinates(coordinates: str) -> tuple[int, int]:
    match = re.match(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", coordinates)
    if match:
        x, y = map(int, match.groups())
    else:
        raise ValueError("Invalid coordinate format")
    return x, y


def _get_element(page: Page, x: int, y: int) -> ElementHandle:
    handle = page.evaluate_handle(f"""
    () => {{
      const clickableTags = ['BUTTON','A','INPUT','TEXTAREA','SELECT'];
      const clickableRoles = ['button','link','menuitem'];

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


def _set_page(page: Page):
    global _current_page
    _current_page = page


def _require_page():
    if _current_page is None:
        raise RuntimeError("No active page. Call set_page() first.")


def click(target_description: str):
    _require_page()

    coordinates = b.LocateUIElement(target_description)
    x, y = _parse_coordinates(coordinates)
    element: ElementHandle = _get_element(_current_page, x, y)
    element.click()

    _trace.append({"action": {"name": "click", "args": {"xpath": _get_xpath(element)}}})


def type(target_description: str, content: str):
    _require_page()
    coordinates = b.LocateUIElement(target_description)
    x, y = _parse_coordinates(coordinates)
    element: ElementHandle = _get_element(_current_page, x, y)
    element.type(content)

    _trace.append({"action": {"name": "fill", "args": {"xpath": _get_xpath(element)}}})


def drag(source_description: str, target_description: str):
    _require_page()
    source_coordinates = b.LocateUIElement(source_description)
    source_x, source_y = _parse_coordinates(source_coordinates)
    target_coordinates = b.LocateUIElement(target_description)
    target_x, target_y = _parse_coordinates(target_coordinates)

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
      {"action": {"name": "drag", "args": {
          "source_xpath": _get_xpath(_get_element(_current_page, source_x, source_y)),
          "target_xpath": _get_xpath(_get_element(_current_page, target_x, target_y))
      }}}
    )


def scroll(target_description: str | None, direction: str):
    _require_page()

    direction = direction.lower()
    if direction not in {"up", "down", "left", "right"}:
        raise ValueError("direction must be one of 'up', 'down', 'left', or 'right'")

    # Default values: scroll window
    coords = None
    if target_description is not None:
        coords = _parse_coordinates(b.LocateUIElement(target_description))

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


def execute(code: str, page: Page) -> list[dict]:
    """
    Safely execute LLM-generated Python code blocks containing only automation actions.
    Automatically sets the current Playwright Page before execution.
    """
    safe_globals = {
        "click": click,
        "type": type,
        "drag": drag,
        "scroll": scroll,
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

    except Exception:
        logger.error("Failed to execute action:", traceback.format_exc())
    
    finally:
        trace = deepcopy(_trace)
        _trace.clear()
        
    return trace