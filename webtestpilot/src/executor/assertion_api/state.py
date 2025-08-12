from dataclasses import dataclass
from xml.etree.ElementTree import Element
from typing import Optional


@dataclass(frozen=True)
class State:
    page_id: str
    description: str
    url: str
    title: str
    content: str
    screenshot: str
    elements: dict[int, Element]
    prev_action: Optional[str]

    # TODO: Implement extract(), get_element()