from hashlib import sha1
from collections import defaultdict
from xml.etree.ElementTree import Element, indent, tostring

from executor.tree.accessibility import AccessibilityTree


def _convert_node_to_xml(node: dict, parent: Element = None) -> Element:
    """
    Convert a node in the accessibility tree into an XML Element.
    """
    role_value = node["role"]["value"]
    id = node.get("id", "")
    ignored = node.get("ignored", False)
    name_value = node.get("name", {}).get("value", "")
    properties = node.get("properties", [])
    children = node.get("nodes", [])

    if role_value == "StaticText":
        parent.text = name_value
    elif role_value == "none" or ignored:
        if children:
            for child in children:
                _convert_node_to_xml(child, parent)
    elif role_value == "generic" and not children:
        return None
    else:
        # Create the XML element for the node
        xml_element = Element(role_value)

        if name_value and len(name_value) > 0:
            xml_element.set("name", name_value)

        # Assign a unique ID to the element
        xml_element.set("id", str(id))

        if properties:
            for property in properties:
                xml_element.set(
                    property["name"],
                    str(property.get("value", {}).get("value", "")),
                )

        # Add children recursively
        if children:
            for child in children:
                _convert_node_to_xml(child, xml_element)

        if parent is not None:
            parent.append(xml_element)

        return xml_element


def _get_texts(node: Element) -> list[str]:
    """
    Get the text content of an element.
    """
    texts = set()
    if node.get("name"):
        texts.add(node.get("name"))
    if node.get("label"):
        texts.add(node.get("label"))
    if node.text:
        texts.add(node.text)

    return list(texts)


def _prune_redundant_name(node: Element) -> list[str]:
    """
    Recursively traverses the tree, removes redundant name information from parent nodes,
    and returns a list of all content (names) in the current subtree.
    """
    # Remove name if it equals text
    if node.get("name") and node.text and node.get("name") == node.text:
        del node.attrib["name"]

    if not len(node):
        return _get_texts(node)

    # Recursively process children and gather all descendant content
    descendant_content = []
    for child in node:
        descendant_content.extend(_prune_redundant_name(child))

    # Sort by length, longest first, to handle overlapping substrings correctly
    descendant_content.sort(key=len, reverse=True)

    for content in descendant_content:
        if node.get("name"):
            node.set("name", node.get("name").replace(content, "").strip())
        if node.get("label"):
            node.set("label", node.get("label").replace(content, "").strip())
        if node.text:
            node.text = node.text.replace(content, "").strip()

    # The content of the current subtree is its own (potentially pruned) name
    # plus all the content from its descendants.
    current_subtree_content = descendant_content
    if node.get("name"):
        current_subtree_content.extend(_get_texts(node))

    return current_subtree_content


def _hash_element(elem: Element, cache: dict[str, str]) -> str:
    """
    Hash an Element and its subtree structure using the element's 'id'.
    A per-tree `cache` must be provided to avoid cross-tree contamination.
    """
    elem_id = elem.get("id")
    if not elem_id:
        raise ValueError("Element is missing 'id' attribute")

    if elem_id in cache:
        return cache[elem_id]

    structure = elem.tag
    for child in elem:
        structure += _hash_element(child, cache)

    digest = sha1(structure.encode()).hexdigest()
    cache[elem_id] = digest
    return digest


def _group_similar_children(node: Element, cache: dict[str, str]):
    """
    Groups structurally similar children under a <dynamic> node.
    """
    grouped = defaultdict(list)
    for child in list(node):  # Copy to avoid mutation during iteration
        try:
            child_hash = _hash_element(child, cache)
            grouped[child_hash].append(child)
        except ValueError:
            continue  # Skip children without 'id'

    for group in grouped.values():
        if len(group) >= 2:
            # Remove children from original node
            for child in group:
                node.remove(child)

            # Create a Dynamic wrapper and reattach the group
            dynamic_elem = Element("dynamic")
            dynamic_elem.set("id", str(int(node.get("id", "0")) + 1000))
            dynamic_elem.set("summary", f"{len(group)} similar items")
            for child in group:
                dynamic_elem.append(child)

            node.append(dynamic_elem)

    # Recurse into children that are not Dynamic
    for child in node:
        if child.tag != "dynamic":
            _group_similar_children(child, cache)


def to_xml_tree(tree: AccessibilityTree) -> list[Element]:
    """
    Abstracted tree for page reidentification.
    """
    if not isinstance(tree, AccessibilityTree):
        raise ValueError("Expected AccessibilityTree")

    if len(tree.root) != 1:
        raise ValueError(f"Expected 1 root node, got {len(tree.root)}")

    ((_, root_node),) = tree.root.items()
    element = _convert_node_to_xml(root_node)
    _prune_redundant_name(element)
    _group_similar_children(element, cache={})
    return element


def to_xml_string(tree: Element) -> str:
    """
    String representation of abstracted tree for prompting.
    """
    if not isinstance(tree, Element):
        raise ValueError("Expected xml.etree.ElementTree.Element")

    indent(tree)
    return tostring(tree, encoding="unicode")
