from xml.etree.ElementTree import Element, indent, tostring
from playwright.sync_api import sync_playwright, Page

from page_model.accessibility_tree import AccessibilityTree
from page_model.abstract_tree import to_xml_tree, to_xml_string, tree_distance

playwright = sync_playwright().start()
browser = playwright.chromium.launch()
context = browser.new_context()
page = context.new_page()


trees = []
for url in [
    "https://demo.bookstackapp.com/books",
    "https://demo.bookstackapp.com/shelves",
    "https://demo.bookstackapp.com/shelves/demo-content",
    "https://demo.bookstackapp.com/books/accounts-department",
    "https://demo.bookstackapp.com/",
    "https://demo.bookstackapp.com/search?term=a"
]:
    page.goto(url)
    tree = AccessibilityTree(page)
    xml = to_xml_tree(tree)
    trees.append(xml)

import itertools

n = len(trees)
distance_matrix = [[0] * n for _ in range(n)]
for i, j in itertools.combinations(range(n), 2):
    dist = tree_distance(trees[i], trees[j])
    distance_matrix[i][j] = dist
    distance_matrix[j][i] = dist

def pretty_print_matrix(matrix, labels=None):
    n = len(matrix)
    labels = labels or list(range(n))

    # Width for each cell based on max string length in matrix or labels
    cell_width = max(
        max(len(f"{val:.2f}") for row in matrix for val in row),
        max(len(str(label)) for label in labels)
    ) + 2

    # Header row
    header = " " * (cell_width) + "".join(f"{str(label):>{cell_width}}" for label in labels)
    print(header)

    # Rows
    for i, row in enumerate(matrix):
        row_str = "".join(f"{val:.2f}".rjust(cell_width) for val in row)
        print(f"{str(labels[i]).rjust(cell_width)}{row_str}")

pretty_print_matrix(distance_matrix)