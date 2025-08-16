from __future__ import annotations
import re
import logging
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel
from baml_py import Image, ClientRegistry
from xml.etree.ElementTree import Element as XMLElement

from config import Config
from baml_client.sync_client import b
from baml_client.type_builder import TypeBuilder
from executor.assertion_api.pydantic_schema import build_from_pydantic


if TYPE_CHECKING:
    from executor.assertion_api.element import Element


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class State:
    page_id: str
    description: str
    layout: str

    url: str
    title: str
    content: str
    screenshot: str
    elements: dict[int, "Element"]
    prev_action: Optional[str]

    xml_tree: list[XMLElement]

    _cr_assertion_api: ClientRegistry
    _cr_ui_locator: ClientRegistry

    def extract(self, instruction: str, schema: type[BaseModel]) -> BaseModel:
        """
        Extract structured data from the state using a Pydantic schema.

        Args:
            instruction (str):
                A natural language description of the information to extract.
                Example: `"get product detail"` or `"extract cart summary"`.
            schema (type[BaseModel]):
                A Pydantic model class defining the expected structure of the output.

        Returns:
            BaseModel:
                An instance of the provided `schema` containing validated extracted data.

        Example:
            >>> class Product(BaseModel):
            ...     title: str
            ...     price: float
            ...
            >>> data = session.extract("get product detail", schema=Product)
            >>> data
            {'title': 'Sample Item', 'price': 9.99}
        """
        tb = TypeBuilder()
        field_types = build_from_pydantic([schema], tb)
        for field_type in field_types:
            tb.Output.add_property("schema", field_type)

        screenshot = Image.from_base64("image/png", self.screenshot)
        output = b.ExtractFromState(
            screenshot,
            instruction,
            baml_options={"tb": tb, "client_registry": self._cr_assertion_api},
        )
        data = schema.model_validate(output.model_dump().get("schema", {}))
        logger.info(f"Extracted data: {data}")
        return data

    def get_element(self, description: str) -> "Element" | None:
        """
        Locate the topmost visible Element at the coordinates corresponding
        to a UI description.

        Args:
            description (str): A textual description used to locate the UI element.

        Returns:
            Element | None: The topmost visible element containing the point,
            or `None` if no such element exists or the coordinates could not
            be parsed.
        """
        # Find the (x, y) screen coordinates of the given description.
        screenshot = Image.from_base64("image/png", self.screenshot)
        coordinates = b.LocateUIElement(
            screenshot,
            description,
            baml_options={"client_registry": self._cr_ui_locator},
        )
        match = re.match(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", coordinates)

        if not match:
            return None

        # Filters all known elements to those that are visible and contain the (x, y) point.
        x, y = map(int, match.groups())
        elements: list[Element] = [e for e in self.elements.values()]
        hits = [el for el in elements if el.visible and el.contains(x, y)]

        if not hits:
            return None

        # Sorts candidate elements first by descending z-index (topmost first)
        # and then by area (smaller elements preferred when z-index ties).
        hits.sort(key=lambda el: (-el.z_index, el.width * el.height))
        return hits[0]


class StateFactory:
    def __init__(self, config: Config):
        self.assertion_api: ClientRegistry = config.assertion_api
        self.ui_locator: ClientRegistry = config.ui_locator

    def create(
        self,
        page_id: str,
        description: str,
        layout: str,
        url: str,
        title: str,
        content: str,
        screenshot: str,
        elements: dict[int, "Element"],
        prev_action: Optional[str] = None,
        xml_tree: Optional[list[XMLElement]] = None,
    ) -> State:
        return State(
            page_id=page_id,
            description=description,
            layout=layout,
            url=url,
            title=title,
            content=content,
            screenshot=screenshot,
            elements=elements,
            prev_action=prev_action,
            xml_tree=xml_tree or [],
            _cr_assertion_api=self.assertion_api,
            _cr_ui_locator=self.ui_locator,
        )
