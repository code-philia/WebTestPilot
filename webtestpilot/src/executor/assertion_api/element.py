from typing import Optional, Any


class Element:
    def __init__(self, data: dict[str, Any]):
        self.id: int = data['id']
        self.parentId: Optional[int] = data['parentId']
        self.tagName: str = data['tagName']
        self.outerHTML: str = data['outerHTML']
        self.x: float = data['x']
        self.y: float = data['y']
        self.width: float = data['width']
        self.height: float = data['height']
        self.z_index: int = data.get('zIndex', 0) or 0
        self.visible: bool = data.get('visible', True)
        self.idAttr: Optional[str] = data.get('idAttr')
        self.className: Optional[str] = data.get('className')

        self.children: list['Element'] = []
        self.parent: Optional['Element'] = None

    def add_child(self, child: 'Element'):
        self.children.append(child)
        child.parent = self

    def contains_point(self, px: float, py: float) -> bool:
        return (
            self.visible and
            self.x <= px <= self.x + self.width and
            self.y <= py <= self.y + self.height
        )

    def contains_descendant(self, target_id: int) -> bool:
        if self.id == target_id:
            return True
        return any(child.contains_descendant(target_id) for child in self.children)

    def get_subtree_html(self, depth=0) -> str:
        indent = '  ' * depth
        s = f"{indent}<{self.tagName}"
        if self.idAttr:
            s += f' id="{self.idAttr}"'
        if self.className:
            s += f' class="{self.className}"'
        s += ">\n"
        for child in self.children:
            s += child.get_subtree_html(depth + 1)
        s += f"{indent}</{self.tagName}>\n"
        return s

    def get_subtree_html_with_ancestors(self, depth=0, target_id=None) -> str:
        indent = '  ' * depth
        s = f"{indent}<{self.tagName}"
        if self.idAttr:
            s += f' id="{self.idAttr}"'
        if self.className:
            s += f' class="{self.className}"'
        s += ">\n"

        if target_id is None or self.id == target_id:
            # This is the target node, include all children fully
            for child in self.children:
                s += child.get_subtree_html(depth + 1)
        else:
            # Find the child branch leading to target_id (if any)
            for child in self.children:
                if child.contains_descendant(target_id):
                    s += child.get_subtree_html_with_ancestors(depth + 1, target_id)
                    break
            # Siblings outside the target branch are skipped

        s += f"{indent}</{self.tagName}>\n"
        return s

    def get_full_region(self) -> str:
        # Find topmost ancestor
        root = self
        while root.parent:
            root = root.parent
        # Return HTML including ancestors down to self
        return root.get_subtree_html_with_ancestors(target_id=self.id)
    
    # TODO: Implement extract()


def find_elements_at_point(elements_data: list[dict[str, Any]], x: float, y: float) -> list[Element]:
    elements = [Element(d) for d in elements_data]
    hits = [el for el in elements if el.contains_point(x, y)]

    # Sort by z-index descending, then by area ascending (smaller box is more specific)
    hits.sort(key=lambda el: (-el.z_index, el.width * el.height))

    return hits