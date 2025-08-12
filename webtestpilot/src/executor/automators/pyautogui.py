import ast
import time
from playwright.sync_api import Page

_page: Page | None = None


def _set_page(page: Page):
    global _page
    _page = page


def _map_key(key: str) -> str:
    key_map = {
        "enter": "Enter",
        "esc": "Escape",
        "escape": "Escape",
        "ctrl": "Control",
        "alt": "Alt",
        "shift": "Shift",
        "backspace": "Backspace",
        "tab": "Tab",
        "space": " ",
        "up": "ArrowUp",
        "down": "ArrowDown",
        "left": "ArrowLeft",
        "right": "ArrowRight",
    }
    return key_map.get(key, key.capitalize())


def _get_func_name(func):
    if isinstance(func, ast.Attribute):
        return _get_func_name(func.value) + "." + func.attr
    elif isinstance(func, ast.Name):
        return func.id
    return ""


def _eval_literal(node):
    if isinstance(node, ast.Constant):
        return node.value
    raise ValueError("Only literal arguments are supported")


def _execute_call(call_node: ast.Call):
    func_name = _get_func_name(call_node.func)
    args = [_eval_literal(arg) for arg in call_node.args]
    kwargs = {kw.arg: _eval_literal(kw.value) for kw in call_node.keywords}

    if func_name == "pyautogui.click":
        # Support optional button and clicks
        x = args[0] if len(args) > 0 else None
        y = args[1] if len(args) > 1 else None
        button = kwargs.get("button", "left")
        clicks = kwargs.get("clicks", 1)

        if x is not None and y is not None:
            for _ in range(clicks):
                _page.mouse.click(x, y, button=button)

    elif func_name == "pyautogui.moveTo":
        x = args[0]
        y = args[1]
        _page.mouse.move(x, y)

    elif func_name == "pyautogui.dragTo":
        x = args[0]
        y = args[1]
        button = kwargs.get("button", "left")
        _page.mouse.down(button=button)
        _page.mouse.move(x, y)
        _page.mouse.up(button=button)

    elif func_name == "pyautogui.scroll":
        # Scroll amount is vertical scroll by default
        clicks = args[0]
        # Optional x,y coords (not always used in pyautogui)
        x = args[1] if len(args) > 1 else None
        y = args[2] if len(args) > 2 else None
        # Playwright scroll wheel, x and y are scroll deltas
        # PyAutoGUI scroll: positive is up, negative down
        _page.mouse.wheel(0, clicks * 100)

    elif func_name == "pyautogui.typewrite":
        text = args[0]
        _page.keyboard.type(text)

    elif func_name == "pyautogui.press":
        key = args[0].lower()
        key = _map_key(key)
        _page.keyboard.press(key)

    elif func_name in ("pyautogui.sleep", "time.sleep", "pyautogui.pause"):
        duration = args[0]
        time.sleep(duration)

    else:
        print(f"Unsupported PyAutoGUI function: {func_name}")


def execute(page: Page, response: str):
    _set_page(page)

    tree = ast.parse(response)
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            _execute_call(node.value)