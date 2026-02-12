import ast
import logging
import re
import time
from copy import deepcopy

from playwright.sync_api import Locator, Frame, Page

# -------------------------
# Globals
# -------------------------
logger = logging.getLogger(__name__)
_current_page: Page | None = None
_trace: list[dict] = []
_no_answer: bool = False


def _get_current_page() -> Page:
    global _current_page
    if _current_page is None:
        raise RuntimeError("No active page. Call set_page() first.")
    return _current_page


def _get_som_mapping() -> dict[int, str]:
    global _som_mapping
    if _som_mapping is None:
        raise RuntimeError("No SoM mapping. Get SoM from page first.")
    return _som_mapping


def _set_page(page: Page):
    global _current_page
    _current_page = page


def _set_som_mapping(som_mapping: dict[int, str]):
    global _som_mapping
    _som_mapping = som_mapping


def _set_no_answer(no_answer: bool):
    global _no_answer
    _no_answer = no_answer


def click_by_label(label: int):
    page: Page = _get_current_page()
    som_mapping: dict[int, str] = _get_som_mapping()
    xpath: str = som_mapping.get(int(label), "/html/body")

    logger.info(f"Clicking element with label: [{label}] and xpath: {xpath}")

    # find first matching locator across all frames
    target: Locator | None = None
    target_frame: Frame | None = None
    for frame in page.frames:
        loc = frame.locator(f"xpath={xpath}")
        if loc.count() > 0:
            target = loc.first
            target_frame = frame
            break

    if not target:
        raise RuntimeError(f"Element not found in any frame for xpath: {xpath}")
    
    box = target.bounding_box()
    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2
    if target_frame != page.main_frame:
        iframe_el = target_frame.frame_element()
        iframe_box = iframe_el.bounding_box()
        x += iframe_box["x"]
        y += iframe_box["y"]

    # Simulate hover and click
    page.mouse.move(x, y)

    try:
        target.click()
    except Exception:
        page.mouse.click(x, y)
    finally:
        _trace.append({"action": "click", "label": int(label), "xpath": xpath, "coordinates": [x, y]})


def type(label: int, content: str):
    page: Page = _get_current_page()
    som_mapping: dict[int, str] = _get_som_mapping()
    xpath: str = som_mapping.get(int(label), "/html/body")

    # find first matching locator across all frames
    target: Locator | None = None
    target_frame: Frame | None = None
    for frame in page.frames:
        loc = frame.locator(f"xpath={xpath}")
        if loc.count() > 0:
            target = loc.first
            target_frame = frame
            break

    if not target:
        raise RuntimeError(f"Element not found in any frame for xpath: {xpath}")

    box = target.bounding_box()
    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2
    if target_frame != page.main_frame:
        iframe_el = target_frame.frame_element()
        iframe_box = iframe_el.bounding_box()
        x += iframe_box["x"]
        y += iframe_box["y"]

    try:
        target.fill(content, force=True)
    except Exception:
        page.mouse.click(x, y)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.keyboard.type(content)
    finally:
        _trace.append({"action": "type", "label": int(label), "xpath": xpath, "coordinates": [x, y], "content": content})


def press(key: str):
    page: Page = _get_current_page()
    page.keyboard.press(key)
    _trace.append({"action": "press", "key": key})


def scroll_up():
    page: Page = _get_current_page()
    page.evaluate("() => {window.scrollBy(0, -window.innerHeight);}")
    _trace.append({"action": "scroll_up"})


def scroll_down():
    page: Page = _get_current_page()
    page.evaluate("() => {window.scrollBy(0, window.innerHeight);}")
    _trace.append({"action": "scroll_down"})


def no_answer():
    _set_no_answer(True)
    _trace.append({"action": "no_answer"})


def wait():
    time.sleep(5)
    _trace.append({"action": "wait"})


def finished():
    _trace.append({"action": "finished"})
    pass


def filter_python_lines(text: str) -> str:
    kept = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        try:
            ast.parse(line)
            kept.append(line)
        except SyntaxError:
            continue

    return "\n".join(kept)


def execute(code: str, page: Page, som_mapping: dict[int, str]) -> list[dict]:
    """
    Safely execute LLM-generated Python code blocks containing only automation actions.
    Automatically sets the current Playwright Page before execution.
    """
    global _no_answer

    safe_globals = {
        "click_by_label": click_by_label,
        "type": type,
        "press": press,
        "scroll_up": scroll_up,
        "scroll_down": scroll_down,
        "wait": wait,
        "no_answer": no_answer,
        "finished": finished,
    }

    # Remove triple backticks and optional 'python' tag
    try:
        _set_page(page)
        _set_som_mapping(som_mapping)
        _set_no_answer(False)

        # Extract content inside a ```python ... ``` block
        match = re.search(r"```python\s*([\s\S]*?)```", code, flags=re.IGNORECASE)
        cleaned_code = match.group(1).strip() if match else filter_python_lines(code)
        _trace.append({"action_code": cleaned_code})
        
        exec(cleaned_code, safe_globals, {})
    finally:
        trace = deepcopy(_trace)
        _trace.clear()

    return trace, _no_answer
