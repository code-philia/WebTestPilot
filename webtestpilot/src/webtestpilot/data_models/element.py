from __future__ import annotations

import logging
import textwrap
from typing import TYPE_CHECKING, Any, Optional

from baml_py.baml_py import BamlImagePy
from pydantic import BaseModel, ConfigDict, Field

from webtestpilot.assertion_api import baml_to_python_type, python_to_baml_type
from webtestpilot.baml_client.sync_client import b
from webtestpilot.baml_client.type_builder import TypeBuilder
from webtestpilot.baml_client.types import ExtractedData
from webtestpilot.utils import pil_to_baml

if TYPE_CHECKING:
    from webtestpilot.data_models import State


logger = logging.getLogger(__name__)


class Element(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="ignore", populate_by_name=True)

    state: Optional["State"] = None

    # Position and shape
    x: float
    y: float
    width: float
    height: float
    z_index: int = Field(0, alias="zIndex")

    # Visible content
    visible: bool = True
    text_content: Optional[str] = Field("", alias="textContent")
    outer_html: str = Field(..., alias="outerHTML")

    # Tag
    id: int = Field(..., alias="id")
    tag_name: str = Field(..., alias="tagName")
    attributes: dict[str, Any] = Field(default_factory=dict)

    # Hierarchy
    children: list["Element"] = Field(default_factory=list)
    parent_id: Optional[int] = Field(None, alias="parentId")
    parent: Optional["Element"] = None

    def contains(self, x: float, y: float) -> bool:
        """
        Check if a given point lies within this element's bounding box.
        """
        return (
            self.visible
            and self.x <= x <= self.x + self.width
            and self.y <= y <= self.y + self.height
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
        if not self.state:
            raise ValueError("Element not attached to State.")

        def _get_element_image() -> BamlImagePy:
            # Ensure crop bounding box is within image bounds
            image = self.state.page.screenshot
            img_width, img_height = image.size
            x1 = max(0, min(self.x, img_width))
            y1 = max(0, min(self.y, img_height))
            x2 = max(0, min(self.x + self.width, img_width))
            y2 = max(0, min(self.y + self.height, img_height))

            crop_box = (x1, y1, x2, y2)
            cropped_image = image.crop(crop_box)

            return pil_to_baml(cropped_image)


        baml_schema, baml_type = python_to_baml_type(schema)
        
        tb = TypeBuilder()
        tb.add_baml(
            textwrap.dedent(f"""
                {baml_schema}

                dynamic class Output {{
                    data {baml_type}
                }}
            """).strip()
        )

        screenshot = _get_element_image()
        baml_options = {
            "tb": tb,
            "client_registry": self.state.session.config.assertion_api,
            "collector": self.state.session.collector,
        }
        output = b.ExtractFromElement(
            screenshot, self.outer_html, instruction, baml_options
        )

        data = baml_to_python_type(schema, output)
        logger.info(f"Extracted data: {data}")
        return data
