import re
import time
from playwright.sync_api import Page, ElementHandle

_current_page: Page | None = None


def _set_page(page: Page):
    global _current_page
    _current_page = page


def _require_page():
    if _current_page is None:
        raise RuntimeError("No active page. Call _set_page() first.")


def _parse_point(point_str: str) -> tuple[int, int]:
    """
    Parse string like '<point>x1 y1</point>' into (x1, y1).
    """
    match = re.match(r"<point>\s*(-?\d+)\s+(-?\d+)\s*</point>", point_str)
    if not match:
        raise ValueError(f"Invalid point format: {point_str}")
    x, y = map(int, match.groups())
    return x, y


def _get_element(page: Page, x: int, y: int) -> ElementHandle | None:
    handle = page.evaluate_handle(f"""
    () => {{
        const clickableTags = ['BUTTON', 'A', 'INPUT', 'TEXTAREA', 'SELECT'];
        const clickableRoles = ['button', 'link', 'menuitem'];

        const els = document.elementsFromPoint({x}, {y});
        for (const el of els) {{
            const style = window.getComputedStyle(el);
            if (
                style.pointerEvents !== 'none' &&
                style.visibility !== 'hidden' &&
                el.offsetWidth > 0 &&
                el.offsetHeight > 0 &&
                (
                    clickableTags.includes(el.tagName) ||
                    clickableRoles.includes(el.getAttribute('role')) ||
                    el.getAttribute('onclick')
                )
            ) {{
                return el;
            }}
        }}
        return els[0] || null;
    }}
    """)
    return handle.as_element() if handle else None


def click(point: str):
    _require_page()
    x, y = _parse_point(point)
    el = _get_element(_current_page, x, y)
    if el:
        el.click()
    else:
        _current_page.mouse.click(x, y)


def left_double(point: str):
    _require_page()
    x, y = _parse_point(point)
    el = _get_element(_current_page, x, y)
    if el:
        el.dblclick()
    else:
        # Playwright mouse doesn't have dblclick with coordinates directly, do two clicks quickly
        _current_page.mouse.click(x, y, click_count=2)


def right_single(point: str):
    _require_page()
    x, y = _parse_point(point)
    el = _get_element(_current_page, x, y)
    if el:
        el.click(button="right")
    else:
        _current_page.mouse.click(x, y, button="right")


def drag(start_point: str, end_point: str):
    _require_page()
    sx, sy = _parse_point(start_point)
    ex, ey = _parse_point(end_point)

    _current_page.mouse.move(sx, sy)
    _current_page.mouse.down()
    # interpolate steps for smooth dragging
    steps = 10
    for i in range(1, steps + 1):
        nx = sx + (ex - sx) * i / steps
        ny = sy + (ey - sy) * i / steps
        _current_page.mouse.move(nx, ny)
        time.sleep(0.02)
    _current_page.mouse.up()


def hotkey(key: str):
    _require_page()
    keys = key.lower().split()
    if not (1 <= len(keys) <= 3):
        raise ValueError("Hotkey supports 1 to 3 keys only")
    # Press keys sequentially with down and up events for modifiers
    for k in keys[:-1]:
        _current_page.keyboard.down(k)
    _current_page.keyboard.press(keys[-1])
    for k in reversed(keys[:-1]):
        _current_page.keyboard.up(k)


def type(content: str):
    _require_page()
    # The content may contain escape sequences, e.g., \n
    decoded_content = content.encode('utf-8').decode('unicode_escape')
    _current_page.keyboard.type(decoded_content)


def scroll(point: str | None, direction: str):
    _require_page()
    direction = direction.lower()
    if direction not in {"up", "down", "left", "right"}:
        raise ValueError("Invalid scroll direction")

    coords = None
    if point is not None:
        coords = _parse_point(point)

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


def wait():
    _require_page()
    # Sleep 5 seconds
    time.sleep(5)
    # Optional: take screenshot for change detection
    # For example:
    # _current_page.screenshot(path="wait_screenshot.png")


def finished(content: str):
    _require_page()
    decoded_content = content.encode('utf-8').decode('unicode_escape')
    print(f"UITARS finished with content:\n{decoded_content}")


def execute(code: str, page: Page):
    """
    Execute LLM-generated UITARS Python code blocks by exposing only the allowed functions.
    """
    _set_page(page)

    safe_globals = {
        "click": click,
        "left_double": left_double,
        "right_single": right_single,
        "drag": drag,
        "hotkey": hotkey,
        "type": type,
        "scroll": scroll,
        "wait": wait,
        "finished": finished,
    }

    # Clean triple backticks if present
    cleaned_code = re.sub(r"^```(?:python)?|```$", "", code.strip(), flags=re.MULTILINE).strip()
    exec(cleaned_code, safe_globals, {})