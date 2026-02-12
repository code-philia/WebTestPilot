from __future__ import annotations

import logging
import textwrap
from typing import TYPE_CHECKING, Optional, Union, Type

from pydantic import BaseModel, ConfigDict, Field

from webtestpilot.assertion_api import baml_to_python_type, python_to_baml_type
from webtestpilot.baml_client.sync_client import b
from webtestpilot.baml_client.type_builder import TypeBuilder
from webtestpilot.baml_client.types import ExtractedData
from webtestpilot.utils import pil_to_baml

if TYPE_CHECKING:
    from webtestpilot.data_models import AbstractPage, Element, Session


logger = logging.getLogger(__name__)


class State(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    session: "Session"
    page: "AbstractPage"
    prev_action: Optional[str] = None
    elements: dict[int, "Element"] = Field(default_factory=dict)

    def model_post_init(self, __context):
        for e in self.elements.values():
            e.state = self

    @property
    def page_id(self):
        return self.page.page_id
    
    @property
    def title(self):
        return self.page.title
    
    @property
    def url(self):
        return self.page.url

    def extract(self, instruction: str, schema: Union[Type[BaseModel], Type]) -> ExtractedData:
        """
        Extract structured data from the state using a schema.

        Args:
            instruction (str):
                A natural language description of the information to extract.
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
            >>> data = session.extract("get product detail", schema=Product)
            >>> text = session.extract("get visible text", schema=str)
            >>> items = session.extract("get all items", schema=list)
            >>> data
            {'title': 'Sample Item', 'price': 9.99}
        """
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

        screenshot = pil_to_baml(self.page.screenshot)
        baml_options = {
            "tb": tb,
            "client_registry": self.session.config.assertion_api,
            "collector": self.session.collector,
        }
        output = b.ExtractFromState(screenshot, instruction, baml_options)
        
        data = baml_to_python_type(schema, output)
        logger.info(f"Extracted data: {data}")
        return data