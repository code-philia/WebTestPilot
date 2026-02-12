import logging
import html
import os
from xml.dom import minidom
from xml.etree.ElementTree import Element as XMLElement
from typing import TYPE_CHECKING

from PIL import Image as PILImage
from baml_py.baml_py import BamlImagePy

from webtestpilot.baml_client.sync_client import b
from webtestpilot.data_models import AbstractPage
from webtestpilot.page_reidentification.accessibility_tree import AccessibilityTree
from webtestpilot.page_reidentification.tree_distance import tree_distance
from webtestpilot.page_reidentification.tree_parser import to_xml_tree
from webtestpilot.utils import get_screenshot, pil_to_baml

if TYPE_CHECKING:
    from webtestpilot.data_models import Session

logger = logging.getLogger(__name__)


def _process_image(image: PILImage.Image) -> BamlImagePy:
    w, h = image.size
    new_h = min(720, h)
    img_cropped = image.crop((0, 0, w, new_h))
    return pil_to_baml(img_cropped)


def _page_abstraction(
    session: "Session", screenshot: PILImage, accessibility_tree: list[XMLElement]
) -> AbstractPage:
    """
    Abstract a new page.
    """
    baml_options = {
        "client_registry": session.config.page_reidentification,
        "collector": session.collector,
    }

    used_page_names = set([state.page.page_id for state in session.history])
    used_page_names = ", ".join(sorted(used_page_names))
    results = b.AbstractPage(_process_image(screenshot), used_page_names, baml_options)

    layout = os.linesep.join([s for s in results.layout.splitlines() if s])

    try:
        layout = minidom.parseString(layout)
    except:
        escaped = html.escape(layout, quote=True)
        wrapper = f'<layout _raw="{escaped}"></layout>'
        layout = minidom.parseString(wrapper)

    logger.info("Abstracted Page")
    logger.info("Name: '%s'", results.name)
    logger.info("Description: '%s'", results.description)
    logger.info(layout.toprettyxml(indent="  ", newl=""))

    return AbstractPage(
        page_id=results.name,
        description=results.description,
        layout=layout,
        url=session.page.url,
        title=session.page.title(),
        content=session.page.content(),
        screenshot=screenshot,
        accessibility_tree=accessibility_tree,
    )


def page_reidentification(session: "Session") -> AbstractPage:
    """
    Determine if the current page matches any previously visited logical page.
    Return an existing page if matched; otherwise abstract a new page.
    """
    baml_options = {
        "client_registry": session.config.page_reidentification,
        "collector": session.collector,
    }
    accessibility_tree = to_xml_tree(AccessibilityTree(session.page))
    current_img = get_screenshot(session.page, full_page=True)

    # Cold start: no prior pages to compare
    if not session.history:
        return _page_abstraction(session, current_img, accessibility_tree)

    # Find the most similar historical page by tree distance
    closest_state = min(
        session.history,
        key=lambda s: tree_distance(accessibility_tree, s.page.accessibility_tree),
    )
    closest_page = closest_state.page
    closest_img_baml = pil_to_baml(closest_page.screenshot)

    # Check if the page is logically the same; If so, reuse existing page ID, description, and layout
    if b.IsSameLogicalPage(_process_image(current_img), closest_img_baml, baml_options):
        return AbstractPage(
            page_id=closest_page.page_id,
            description=closest_page.description,
            layout=closest_page.layout,
            url=session.page.url,
            title=session.page.title(),
            content=session.page.content(),
            screenshot=current_img,
            accessibility_tree=accessibility_tree,
        )

    # Otherwise, create a new abstracted page
    return _page_abstraction(session, current_img, accessibility_tree)
