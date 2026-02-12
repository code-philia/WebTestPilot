from typing import Any

from playwright.sync_api import Page


class AccessibilityTree:
    """
    A model representing the accessibility tree of a Playwright `Page`.

    This tree is extracted using the Chrome DevTools Protocol (CDP)
    via `Accessibility.getFullAXTree`, and is reconstructed as a proper
    parent-child structure in memory.
    """

    def __init__(self, page: Page):
        """
        Initialize the AccessibilityTree by retrieving and building the tree
        from the root document's accessibility structure.

        Args:
            page (Page): The Playwright page to extract the accessibility tree from.
        """
        self.session = page.context.new_cdp_session(page)
        self.root: dict[str, dict] = {}  # nodeId -> node (only roots)
        self.mapping: dict[int, Any] = {}  # internal node ID -> backendDOMNodeId

        nodes = self._fetch_accessibility_nodes()
        self._build_tree(nodes)

    def _fetch_accessibility_nodes(self) -> list[dict]:
        """
        Fetch raw accessibility nodes from the CDP.

        Returns:
            List of accessibility node dictionaries.
        """
        response = self.session.send("Accessibility.getFullAXTree")
        return response.get("nodes", [])

    def _build_tree(self, nodes: list[dict]):
        """
        Construct the in-memory tree from flat node list, identifying roots
        and building parent-child relationships.

        Args:
            nodes: List of node dictionaries from the accessibility snapshot.
        """
        node_lookup: dict[str, dict] = {node["nodeId"]: node for node in nodes}

        for internal_id, (node_id, node) in enumerate(node_lookup.items()):
            node["id"] = internal_id
            self.mapping[internal_id] = node.get("backendDOMNodeId", "")

            parent_id = node.get("parentId")

            if parent_id is None:
                # This is a root node (no parent in accessibility tree)
                self.root[node_id] = node
            else:
                # Attach this node to its parent
                parent = node_lookup[parent_id]
                parent.setdefault("nodes", []).append(node)

                # Clean up linkage fields from the child
                node.pop("childIds", None)
                node.pop("parentId", None)
