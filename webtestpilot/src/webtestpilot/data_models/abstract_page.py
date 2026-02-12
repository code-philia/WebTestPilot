from xml.dom.minidom import Document
from xml.etree.ElementTree import Element as XMLElement

from PIL import Image as PILImage
from pydantic import AnyUrl, BaseModel, ConfigDict


class AbstractPage(BaseModel):
    """
    An abstract representation of a browser page.

    This model captures the *logical identity* of a page, independent of
    transient UI changes. Pages with the same `page_id` are considered the
    same logical page (e.g., the shopping cart page observed at different
    points in a test session).
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Logical page identifier. Pages sharing the same ID represent the same
    # conceptual page across time or navigation events
    page_id: str

    # Detailed description of the page’s visual structure and functionality.
    description: str

    # Abstracted page layout serialized as XML.
    layout: Document

    # Current page URL.
    url: AnyUrl

    # Browser tab title.
    title: str

    # Full page screenshot.
    screenshot: PILImage.Image

    # Raw textual content extracted from the page.
    content: str

    # Accessibility tree serialized as XML.
    accessibility_tree: list[XMLElement]
