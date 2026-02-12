import logging
import re
from pathlib import Path
from typing import Dict, TypeAlias

from PIL import Image as PILImage
from playwright.sync_api import Page

from webtestpilot.baml_client.sync_client import b
from webtestpilot.utils import pil_to_baml

BASE_DIR = Path(__file__).parent
logger = logging.getLogger(__name__)

# Type aliases
Mapping: TypeAlias = Dict[int, str]


def trim_xpath(xpath: str) -> str:
    """
    Trims and simplifies an XPath string for better readability.

    Args:
        xpath (str): The original XPath string.

    Returns:
        str: The simplified XPath string.
    """
    xpath = xpath.replace("/html/body", "", 1)
    xpath = re.sub(r"\[\d+\]", "", xpath)
    parts = [p for p in xpath.split("/") if p]
    return "/" + "/".join(parts[-3:])


def propose_som_actions(
    pil_img: PILImage.Image,
    action: str,
    som_mapping: Dict[int, str],
    text_mapping: Dict[int, str],
    baml_options: dict,
) -> str:
    """
    Proposes actions based on Set-of-Mark (SoM) elements.

    Args:
        pil_img (PILImage.Image): The cropped screenshot containing the relevant area.
        action (str): The description of the action to perform.
        som_mapping (Dict[int, str]): A mapping of SoM IDs to their XPaths.
        text_mapping (Dict[int, str]): A mapping of SoM IDs to their text content.
        config (Config): Configuration object containing model registry settings.
        session (Session): The current session object.

    Returns:
        str: The generated code or action description.
    """
    screenshot_baml = pil_to_baml(pil_img)
    active_elements = []
    for k, xpath in som_mapping.items():
        text = text_mapping.get(k, "")
        text = text if len(text) <= 50 else text[:50] + "…"
        active_elements.append(f"[{k}] -> {trim_xpath(xpath)} | text='{text}'")

    code = b.ProposeActions(
        screenshot_baml,
        action,
        "\n".join(active_elements),
        baml_options=baml_options,
    )
    logger.info(f"Proposed action:\n{code}")
    return code


def propose_coordinates(
    pil_img: PILImage.Image, action: str, baml_options: dict
) -> tuple[int, int]:
    """
    Proposes (x, y) coordinates for a given action using a GUI grounding model.

    Args:
        pil_img (PILImage.Image): The full page screenshot.
        action (str): The description of the element/action to locate.
        config (Config): Configuration object containing model registry settings.
        session (Session): The current session object.

    Returns:
        tuple[int, int]: The (x, y) coordinates of the proposed location.
    """

    def _parse_coordinates(output_text: str) -> tuple[int, int]:
        """
        Get (x, y) coordinates from GUI grounding model output.
        Note: this assumes screenshot is 1280 * 720px (standardized for model input).
        """
        box = eval(output_text)
        input_height = 728
        input_width = 1288
        abs_x1 = float(box[0]) / input_width
        abs_y1 = float(box[1]) / input_height
        abs_x2 = float(box[2]) / input_width
        abs_y2 = float(box[3]) / input_height
        bbox = [abs_x1, abs_y1, abs_x2, abs_y2]
        point = [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]
        return int(point[0] * 1280), int(point[1] * 720)

    screenshot_baml = pil_to_baml(pil_img)
    coords = b.LocateUIElement(
        screenshot=screenshot_baml, description=action, baml_options=baml_options
    )
    x, y = _parse_coordinates(coords)

    logger.info(f"Proposed location: ({int(x)}, {int(y)})")
    return x, y


def crop_screenshot(
    pil_img: PILImage.Image, center: tuple[int, int], size: int = 200
) -> PILImage.Image:
    """
    Crop a square of `size` centered at `center` (x, y) from the screenshot.

    Args:
        pil_img (PILImage.Image): The original screenshot.
        center (tuple[int, int]): The center coordinates (x, y).
        size (int, optional): The width/height of the crop square. Defaults to 200.

    Returns:
        PILImage.Image: The cropped image.
    """
    x, y = center
    w, h = pil_img.size

    half = size // 2
    left = max(min(x - half, w - size), 0)
    upper = max(min(y - half, h - size), 0)
    right = left + size
    lower = upper + size

    return pil_img.crop((left, upper, right, lower))


def mask_screenshot(
    pil_img: PILImage.Image, center: tuple[int, int], size: int = 200
) -> PILImage.Image:
    """
    Mask (black out) a square of `size` centered at `center` (x, y) on the full screenshot.

    Args:
        pil_img (PILImage.Image): The original screenshot.
        center (tuple[int, int]): The center coordinates (x, y) to mask.
        size (int, optional): The size of the masked square. Defaults to 200.

    Returns:
        PILImage.Image: The modified screenshot with the masked area.
    """
    x, y = center
    w, h = pil_img.size

    half = size // 2
    left = max(min(x - half, w - size), 0)
    upper = max(min(y - half, h - size), 0)
    right = left + size
    lower = upper + size

    # Create a mask rectangle and paste it
    mask = PILImage.new("RGB", (right - left, lower - upper), color=(255, 255, 255))
    result = pil_img.copy()
    result.paste(mask, (left, upper))

    return result


def mark_page(page: Page, x: int, y: int) -> tuple[Mapping, Mapping]:
    """
    Injects the marking script and retrieves Set-of-Mark (SoM) candidates near the target coordinates.

    Args:
        page (Page): The Playwright page object.
        x (int): The target X coordinate.
        y (int): The target Y coordinate.

    Returns:
        tuple[Mapping, Mapping]: A tuple containing:
            - som_mapping: Dict mapping IDs to XPaths.
            - text_mapping: Dict mapping IDs to text content.
    """
    page.add_script_tag(path=BASE_DIR / "mark.js")

    som_data: dict = page.evaluate(
        "(arr) => window.markWidgets({ targetX: arr[0], targetY: arr[1], maxNearby: 5 })",
        [int(x), int(y)],
    )
    som_mapping: dict = som_data.get("highlightedMap", {})
    som_mapping = {int(k): v for k, v in som_mapping.items()}
    text_mapping: dict = som_data.get("textMap", {})
    text_mapping = {int(k): v for k, v in text_mapping.items()}

    lines = []
    for k, xpath in som_mapping.items():
        text = text_mapping.get(k, "")
        text = text if len(text) <= 50 else text[:50] + "…"
        lines.append(f"[{k}]: {trim_xpath(xpath)} | text='{text}'")
    logger.info("SoM candidates:\n" + "\n".join(lines))

    return som_mapping, text_mapping


def unmark_page(page: Page) -> None:
    """
    Removes the Set-of-Mark highlights from the page.

    Args:
        page (Page): The Playwright page object.
    """
    page.add_script_tag(path=BASE_DIR / "unmark.js")
    page.evaluate("() => window.unmarkWidgets()")
