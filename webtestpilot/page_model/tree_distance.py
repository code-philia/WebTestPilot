from xml.etree.ElementTree import Element

import zss
import Levenshtein


class XMLNode(zss.Node):
    def __init__(self, element: Element):
        self.element = element
        super().__init__(self.element.tag)

    def label(self):
        tag = self.element.tag
        name = self.element.get("name", "").strip()
        text = (self.element.text or "").strip()
        content = name or text
        return f"{tag}:{content}" if content else tag
    
    def get_children(self):
        if self.element.tag == "dynamic":
            return []
        
        return [XMLNode(child) for child in list(self.element)]
    
    @staticmethod
    def label_edit_cost(a: str, b: str) -> float:
        if a == b:
            return 0
        a_tag, _, a_val = a.partition(":")
        b_tag, _, b_val = b.partition(":")
        if a_tag != b_tag:
            # Different tags: max cost 2 (1 + 1)
            return 2
        # Compute normalized similarity ratio between contents
        similarity = Levenshtein.ratio(a_val, b_val)  # between 0 and 1
        return 1 + (1 - similarity)  # between 1 and 2
    

def tree_distance(e1: list[Element], e2: list[Element]) -> int:
    return zss.simple_distance(
        XMLNode(e1),
        XMLNode(e2),
        get_children=XMLNode.get_children,
        get_label=XMLNode.label,
        label_dist=XMLNode.label_edit_cost
    )