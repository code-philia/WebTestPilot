from dataclasses import dataclass
from xml.etree.ElementTree import Element


@dataclass
class State:
    page_id: str
    description: str
    url: str
    title: str
    content: str
    screenshot: str
    tree: list[Element]
