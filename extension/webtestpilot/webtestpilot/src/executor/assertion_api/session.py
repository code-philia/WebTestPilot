import base64
from typing import Any

from baml_py import Image, Collector
from playwright.sync_api import Page
from xml.etree.ElementTree import Element as XMLElement

from config import Config
from baml_client.sync_client import b
from baml_client.types import PageAbstract, History
from executor.assertion_api.state import State, StateFactory
from executor.assertion_api.element import Element, ElementFactory
from executor.page_reidentification.accessibility import AccessibilityTree
from executor.page_reidentification.abstract import to_xml_tree
from executor.page_reidentification.distance import tree_distance


class Session:
    """
    Manages a browser test session with state tracking capabilities.

    Args:
        page (Page): A Playwright Page instance that accesses the application under test.
            It's assumed that the application is already loaded
            and any necessary prerequisites (e.g., fixtures, authentication) have been set up.
        config (Config): Runtime configurations for this test session.

    Raises:
        AssertionError: If the provided page is not a valid Page instance or is closed.
    """

    def __init__(self, page: Page, config: Config):
        assert isinstance(page, Page) and not page.is_closed()

        self.trace: list[dict] = []
        self.page = page
        self.config = config
        self.collector = Collector()
        self.state_factory = StateFactory(self)
        self.element_factory = ElementFactory(self)

        self._history: list[State] = []
        self.capture_state(prev_action=None)

    @property
    def history(self) -> list[State]:
        """
        Get the chronological history of captured states.

        Returns:
            list[State]: A read-only copy of all previously captured states in the test session,
                    ordered chronologically from oldest to newest.
        """
        return self._history.copy()

    def capture_state(self, prev_action: str | None):
        """
        Capture the current state of the browser page after an action.
        """
        # Extract accessibility tree in XML format
        tree = AccessibilityTree(self.page)
        xml_tree = to_xml_tree(tree)

        screenshot = base64.b64encode(self.page.screenshot(type="png")).decode("utf-8")
        page_id, description, layout = self._page_reidentification(xml_tree, screenshot)
        elements = self.capture_elements()

        # Update with new state
        state = self.state_factory.create(
            page_id=page_id,
            description=description,
            layout=layout,
            url=self.page.url,
            title=self.page.title(),
            content=self.page.content(),
            screenshot=screenshot,
            elements=elements,
            prev_action=prev_action,
            xml_tree=xml_tree,
        )

        for e in elements.values():
            e.state = state

        self._history.append(state)

    def capture_elements(self) -> dict[int, Element]:
        def _build_tree(
            elements_data: list[dict[str, Any]],
        ) -> tuple[dict[int, Element], Element]:
            elements: dict[str, Element] = {
                data["id"]: self.element_factory.create(data) for data in elements_data
            }
            root = None
            for el in elements.values():
                if el.parentId is not None:
                    parent = elements.get(el.parentId)
                    if parent:
                        parent.children.append(el)
                else:
                    root = el
            return elements, root

        elements_data = self.page.evaluate("""
            (() => {
                let idCounter = 1;
                const nodes = [];

                function traverse(node, parentId = null) {
                    const id = idCounter++;
                    const rect = node.getBoundingClientRect();
                    const style = window.getComputedStyle(node);

                    const attributes = {};
                    for (const attr of node.attributes) {
                        attributes[attr.name] = attr.value;
                    }

                    nodes.push({
                        id,
                        parentId,
                        tagName: node.tagName,
                        outerHTML: node.outerHTML,
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height,
                        zIndex: parseInt(style.zIndex) || 0,
                        visible: style.visibility !== 'hidden' && style.display !== 'none' && style.opacity !== '0',
                        attributes,
                        textContent: node.textContent.trim() || null
                    });

                    for (const child of node.children) {
                        traverse(child, id);
                    }
                }

                traverse(document.documentElement, null);
                return nodes;
            })()
        """)

        elements, _ = _build_tree(elements_data)
        return elements

    def get_history(
        self,
    ) -> list[History]:
        seen_pages = set()
        history = []
        for state in self.history:
            layout = state.layout if state.page_id not in seen_pages else None
            description = state.description if state.page_id not in seen_pages else None
            history.append(
                History(
                    page_id=state.page_id,
                    layout=layout,
                    description=description,
                    prev_action=state.prev_action,
                )
            )
            seen_pages.add(state.page_id)
        return history

    def _page_reidentification(
        self, xml_tree: list[XMLElement], screenshot: str
    ) -> tuple[str, str, str]:
        """
        Determine if the current page matches any previously visited logical page.
        If matched, return the existing page ID and description.
        Otherwise, generate a new page ID and description.

        Returns:
            tuple[str, str]: A tuple containing:
                - page_id: A short identifier or name of the logical page.
                - description: A detailed textual description of the page.
        """
        current_img = Image.from_base64("image/png", screenshot)

        # Handle empty history — no page to compare
        if not self.history:
            page_abstract: PageAbstract = b.AbstractPage(
                current_img,
                baml_options={
                    "client_registry": self.config.page_reidentification,
                    "collector": self.collector,
                },
            )
            return page_abstract.name, page_abstract.description, page_abstract.layout

        # Find the history state with the smallest tree distance to current page
        closest_state = min(
            self.history, key=lambda s: tree_distance(xml_tree, s.xml_tree)
        )
        closest_img = Image.from_base64("image/png", closest_state.screenshot)

        if b.IsSameLogicalPage(
            current_img,
            closest_img,
            baml_options={
                "client_registry": self.config.page_reidentification,
                "collector": self.collector,
            },
        ):
            return (
                closest_state.page_id,
                closest_state.description,
                closest_state.layout,
            )

        page_abstract: PageAbstract = b.AbstractPage(
            current_img,
            baml_options={
                "client_registry": self.config.page_reidentification,
                "collector": self.collector,
            },
        )
        return page_abstract.name, page_abstract.description, page_abstract.layout
