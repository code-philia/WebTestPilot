import logging
from typing import Any, TYPE_CHECKING

from baml_py import Collector
from playwright.sync_api import Page

from webtestpilot.config import Config
from webtestpilot.page_reidentification import page_reidentification

if TYPE_CHECKING:
    from .element import Element
    from .state import State


logger = logging.getLogger(__name__)


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
        from .state import State

        assert isinstance(page, Page) and not page.is_closed()

        self.trace: list[dict] = []
        self.page: Page = page
        self.config: Config = config
        self.collector: Collector = Collector()
        # Cumulative token counts from browser-use LLM calls (tracked separately from BAML).
        self.browser_use_input_tokens: int = 0
        self.browser_use_output_tokens: int = 0

        self._history: list[State] = []
        self.capture_state(prev_action=None)

    @property
    def history(self) -> list["State"]:
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
        from .state import State

        abstract_page = page_reidentification(self)
        elements = self.capture_elements()
        state = State(
            session=self,
            page=abstract_page, 
            elements=elements,
            prev_action=prev_action
        )

        self._history.append(state)

    def capture_elements(self) -> dict[int, "Element"]:
        from .element import Element

        def _build_tree(
            elements_data: list[dict[str, Any]],
        ) -> tuple[dict[int, Element], Element]:

            # Build elements
            elements: dict[int, Element] = {}
            for data in elements_data:
                element_id = data.get("id")
                elements[element_id] = Element(session=self, **data)

            # If element has parentId, assign as child to parent
            root = None
            for el in elements.values():
                if el.parent_id is not None:
                    parent = elements.get(el.parent_id)
                    if parent:
                        el.parent = parent
                        parent.children.append(el)
                else:
                    root = el
            return elements, root  # type: ignore

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