import base64

from baml_py import Image
from playwright.sync_api import Page

from executor.assertion_api.state import State
from baml_client.sync_client import b
from baml_client.types import PageDescription
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

    Raises:
        AssertionError: If the provided page is not a valid Page instance or is closed.

    Attributes:
        page (Page): The Playwright page instance being managed by this session.
    """

    def __init__(self, page: Page):
        assert isinstance(page, Page) and not page.is_closed()
        self._history: list[State] = []
        self.page = page

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
        Capture and return the current state of the browser page.
        """
        tree = AccessibilityTree(self.page)
        screenshot = base64.b64encode(self.page.screenshot(type="png")).decode("utf-8")
        page_id, description = self._page_reidentification(tree, screenshot)

        return State(
            page_id=page_id,
            description=description,
            url=self.page.url,
            title=self.page.title(),
            content=self.page.content(),
            screenshot=self.page.screenshot(),
        )

    def _page_reidentification(
        self, tree: AccessibilityTree, screenshot: str
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
        current_tree = to_xml_tree(tree)

        # Find the history state with the smallest tree distance to current page
        closest_state = min(
            self.history, key=lambda s: tree_distance(current_tree, s.tree)
        )

        current_img = Image.from_base64("image/png", screenshot)
        closest_img = Image.from_base64("image/png", closest_state.screenshot)

        if b.IsSameLogicalPage(current_img, closest_img):
            return closest_state.page_id, closest_state.description

        page_desc: PageDescription = b.DescribePage(current_img)
        return page_desc.name, page_desc.description
