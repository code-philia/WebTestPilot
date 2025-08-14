import base64
from typing import Any

from baml_py import Image
from playwright.sync_api import Page
from xml.etree.ElementTree import Element as XMLElement

from config import Config
from baml_client.sync_client import b
from baml_client.types import PageAbstract
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
        self._history: list[State] = []
        self._state: State = self.capture_state(prev_action=None)

        self.trace: list[dict] = []
        self.page = page
        self.config = config
        self.state_factory = StateFactory(config)
        self.element_factory = ElementFactory(config)

    @property
    def history(self) -> list[State]:
        """
        Get the chronological history of captured states.

        Returns:
            list[State]: A read-only copy of all previously captured states in the test session,
                    ordered chronologically from oldest to newest.
        """
        return self._history.copy()

    @property
    def state(self) -> State:
        """
        Return the most recent captured state.
        """
        return self._state

    def capture_state(self, prev_action: str | None) -> State:
        """
        Capture and return the current state of the browser page after an action.
        """
        # Add previously recorded state into history
        self._history.append(self._state)

        # Extract accessibility tree in XML format
        tree = AccessibilityTree(self.page)
        xml_tree = to_xml_tree(tree)

        screenshot = base64.b64encode(self.page.screenshot(type="png")).decode("utf-8")
        elements = self.capture_elements()
        page_id, description = self._page_reidentification(xml_tree, screenshot)

        # Update with new state
        self._state = self.state_factory.create(
            page_id=page_id,
            description=description,
            layout=None,
            url=self.page.url,
            title=self.page.title(),
            content=self.page.content(),
            screenshot=self.page.screenshot(),
            elements=elements,
            prev_action=prev_action,
            xml_tree=xml_tree,
        )
        return self._state

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

    def _page_reidentification(
        self, xml_tree: list[XMLElement], screenshot: str
    ) -> tuple[str, str]:
        """
        Determine if the current page matches any previously visited logical page.
        If matched, return the existing page ID and description.
        Otherwise, generate a new page ID and description.

        Returns:
            tuple[str, str]: A tuple containing:
                - page_id: A short identifier or name of the logical page.
                - description: A detailed textual description of the page.
        """
        # Find the history state with the smallest tree distance to current page
        closest_state = min(
            self.history, key=lambda s: tree_distance(xml_tree, s.xml_tree)
        )

        current_img = Image.from_base64("image/png", screenshot)
        closest_img = Image.from_base64("image/png", closest_state.screenshot)

        if b.IsSameLogicalPage(
            current_img,
            closest_img,
            baml_options={"client_registry": self.config.page_reidentification},
        ):
            return (
                closest_state.page_id,
                closest_state.description,
                closest_state.layout,
            )

        page_abstract: PageAbstract = b.AbstractPage(
            current_img,
            baml_options={"client_registry": self.config.page_reidentification},
        )
        return page_abstract.name, page_abstract.description, page_abstract.layout
