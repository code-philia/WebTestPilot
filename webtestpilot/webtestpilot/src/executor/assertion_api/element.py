from __future__ import annotations

import base64
import io
import logging
from typing import TYPE_CHECKING, Any, Optional

import PIL.Image
from baml_client.sync_client import b
from baml_client.type_builder import TypeBuilder
from baml_client.types import ExtractedData
from baml_py import ClientRegistry, Collector, Image

from executor.assertion_api.pydantic_schema import build_from_pydantic
from executor.assertion_api.type_utils import convert_extracted_data

if TYPE_CHECKING:
    from executor.assertion_api.session import Session
    from executor.assertion_api.state import State


logger = logging.getLogger(__name__)


class Element:
    """
    Represents a DOM-like element with spatial coordinates, dimensions, z-index, and hierarchy.
    """

    def __init__(
        self,
        data: dict[str, Any],
        client_registry: ClientRegistry,
        collector: Collector,
    ):
        self.id: int = data["id"]
        self.parentId: Optional[int] = data["parentId"]
        self.tagName: str = data["tagName"]
        self.outerHTML: str = data["outerHTML"]
        self.x: float = data["x"]
        self.y: float = data["y"]
        self.width: float = data["width"]
        self.height: float = data["height"]
        self.z_index: int = data.get("zIndex", 0) or 0
        self.visible: bool = data.get("visible", True)
        self.text_content: str = data.get("textContent", "")
        self.attributes: dict = data.get("attributes", {})

        self.children: list["Element"] = []
        self.parent: Optional["Element"] = None

        self.client_registry = client_registry
        self.collector = collector
        self.state: Optional["State"] = None

    def contains(self, px: float, py: float) -> bool:
        """
        Check if a given point lies within this element's bounding box.
        """
        return (
            self.visible
            and self.x <= px <= self.x + self.width
            and self.y <= py <= self.y + self.height
        )

    def extract(self, instruction: str, schema: ExtractedData) -> ExtractedData:
        """
        Extract structured data from the element using a schema.

        Args:
            instruction (str):
                A natural language description of information to extract.
                Example: `"get product detail"` or `"extract cart summary"`.
            schema (ExtractedData):
                A BaseModel class, primitive type, or collection type defining the expected output.

        Returns:
            ExtractedData:
                An instance of the provided `schema` type containing validated extracted data.

        Example:
            >>> class Product(BaseModel):
            ...     title: str
            ...     price: float
            ...
            >>> data = element.extract("get product detail", schema=Product)
            >>> text = element.extract("get visible text", schema=str)
            >>> items = element.extract("get all items", schema=list)
            >>> data
            {'title': 'Sample Item', 'price': 9.99}
        """
        tb = TypeBuilder()
        field_type = build_from_pydantic(schema, tb)
        tb.Output.add_property("schema", field_type)

        # Decode screenshot from base64
        image_bytes = base64.b64decode(self.state.screenshot)
        image = PIL.Image.open(io.BytesIO(image_bytes))

        # Ensure crop bounding box is within image bounds
        img_width, img_height = image.size
        x1 = max(0, min(self.x, img_width))
        y1 = max(0, min(self.y, img_height))
        x2 = max(0, min(self.x + self.width, img_width))
        y2 = max(0, min(self.y + self.height, img_height))

        crop_box = (x1, y1, x2, y2)
        cropped_image = image.crop(crop_box)

        # Convert cropped image back to base64
        buffered = io.BytesIO()
        cropped_image.save(buffered, format="PNG")
        cropped_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        screenshot = Image.from_base64("image/png", cropped_b64)

        output = b.ExtractFromElement(
            screenshot,
            self.outerHTML,
            instruction,
            baml_options={
                "tb": tb,
                "client_registry": self.client_registry,
                "collector": self.collector,
            },
        )
        data = convert_extracted_data(schema, output)
        logger.info(f"Extracted data: {data}")
        return data


class ElementFactory:
    def __init__(self, session: "Session"):
        self.client_registry: ClientRegistry = session.config.assertion_api
        self.collector: Collector = session.collector

    def create(self, data: dict[str, Any]):
        return Element(data, self.client_registry, self.collector)
