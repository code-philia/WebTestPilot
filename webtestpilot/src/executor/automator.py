import re
import time
from baml_py import ClientRegistry

from baml_client.sync_client import b
from baml_client.types import TestCase
from playwright.sync_api import Page, ElementHandle


_current_page = None


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

    if handle:
        return handle.as_element()
    return None


def set_page(page: Page):
    global _current_page
    _current_page = page


def click(target_description: str):
    if _current_page is None:
        raise RuntimeError("Page is not set")
    
    coordinates = b.LocateUIElement(target_description)
    x, y = _parse_coordinates(coordinates)
    element: ElementHandle = _get_element(_current_page, x, y)
    element.click()


def type(target_description: str, content: str):
    if _current_page is None:
        raise RuntimeError("Page is not set")
    
    coordinates = b.LocateUIElement(target_description)
    x, y = _parse_coordinates(coordinates)
    element: ElementHandle = _get_element(_current_page, x, y)
    element.type(content)


def drag(source_description: str, target_description: str):
    if _current_page is None:
        raise RuntimeError("Page is not set")
    
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


def scroll(target_description: str, direction: str):
    direction = direction.lower()
    if direction not in {"up", "down", "left", "right"}:
        raise ValueError("direction must be one of 'up', 'down', 'left', or 'right'")
    
    coordinates = b.LocateUIElement(target_description)
    x, y = _parse_coordinates(coordinates)

    _current_page.evaluate(f"""
    (x, y, direction) => {{
      const el = document.elementFromPoint(x, y);
      if (!el) return;

      const rect = el.getBoundingClientRect();
      const scrollAmountVertical = rect.height;
      const scrollAmountHorizontal = rect.width;

      switch (direction) {{
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
      }}
    }}
    """, x, y, direction)


def wait(duration: int):
    time.sleep()