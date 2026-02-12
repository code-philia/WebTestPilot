import base64
import io

from baml_py.baml_py import BamlImagePy
from PIL import Image as PILImage
from playwright.sync_api import Page


def get_screenshot(page: Page, full_page: bool = False) -> PILImage.Image:
    """
    Captures a screenshot of the current page state.

    Args:
        page (Page): The Playwright page object.
        full_page (bool): When true, takes a screenshot of the full scrollable page, instead of the currently visible viewport.
        
    Returns:
        PILImage.Image: The captured screenshot as a PIL Image.
    """
    page.wait_for_load_state(timeout=0)
    screenshot_bytes = page.screenshot(type="png", full_page=full_page, timeout=0)
    return PILImage.open(io.BytesIO(screenshot_bytes))


def pil_to_baml(pil_img: PILImage.Image) -> BamlImagePy:
    """
    Convert a PIL image to BamlImagePy format.

    Args:
        pil_img (PILImage.Image): The PIL image to convert.

    Returns:
        BamlImagePy: The converted BAML image.
    """
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return BamlImagePy.from_base64("image/png", b64)


def wait_for_dom_stability(page: Page, idle_ms: int = 500, timeout_ms: int = 5000) -> bool:
    """
    Waits until the DOM stops mutating for `idle_ms`, with a hard timeout.
    """
    try:
        return page.evaluate(
            """
            ({ idleMs, timeoutMs }) => {
                return new Promise(resolve => {
                    let lastMutation = Date.now();
                    const start = Date.now();

                    const observer = new MutationObserver(() => {
                        lastMutation = Date.now();
                    });

                    observer.observe(document, {
                        subtree: true,
                        childList: true,
                        attributes: true,
                    });

                    const check = () => {
                        const now = Date.now();

                        if (now - lastMutation >= idleMs) {
                            observer.disconnect();
                            resolve(true);
                            return;
                        }

                        if (now - start >= timeoutMs) {
                            observer.disconnect();
                            resolve(false);
                            return;
                        }

                        requestAnimationFrame(check);
                    };

                    check();
                });
            }
            """,
            {"idleMs": idle_ms, "timeoutMs": timeout_ms},
        )
    except Exception as e:
        if "Execution context was destroyed" in str(e):
            return False
        raise
