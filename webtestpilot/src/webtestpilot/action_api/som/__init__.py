import logging

from webtestpilot.action_api.som.automator import execute
from webtestpilot.action_api.som.utils import (
    crop_screenshot,
    mark_page,
    mask_screenshot,
    propose_coordinates,
    propose_som_actions,
    unmark_page,
)
from webtestpilot.data_models import Session
from webtestpilot.utils import get_screenshot, wait_for_dom_stability

logger = logging.getLogger(__name__)


def execute_action_som(session: Session, action: str) -> None:
    """
    Executes a natural language action using the two-stage SoM pipeline:
    1. GUI Grounding: propose (x, y) coordinates for the target element.
    2. Set-of-Mark: annotate nearby elements and generate interaction code.

    Retries up to 3 times, masking failed regions on each retry.
    """
    som_options = {
        "client_registry": session.config.action_proposer,
        "collector": session.collector,
    }
    grounding_options = {
        "client_registry": session.config.ui_locator,
        "collector": session.collector,
    }

    page = session.page
    mask_points = []

    for _ in range(3):
        # Step 1: GUI grounding model
        # Capture a fresh screenshot each time to account for masks
        grounding_screenshot = get_screenshot(page)
        for mask_point in mask_points:
            grounding_screenshot = mask_screenshot(grounding_screenshot, mask_point)

        x, y = propose_coordinates(grounding_screenshot, action, grounding_options)

        # Step 2: Set-of-Mark prompt model
        # Generate executable code based on the cropped, marked screenshot
        som_mapping, text_mapping = mark_page(page, x, y)
        cropped_screenshot = crop_screenshot(get_screenshot(page), center=(x, y))
        code = propose_som_actions(
            cropped_screenshot, action, som_mapping, text_mapping, som_options
        )
        session.trace.append({"action": action, "action_code": code})

        unmark_page(page)

        try:
            trace, no_answer = execute(code, page, som_mapping)
            session.trace.extend(trace)

            if no_answer:
                # Mask this area and retry to force the model to look elsewhere
                logger.info(f"No answer found at ({x}, {y}). Masking and retrying.")
                mask_points.append((x, y))
                continue
            else:
                session.page.wait_for_load_state(timeout=0)
                wait_for_dom_stability(page)
                session.capture_state(prev_action=action)
                break

        except Exception as e:
            logger.error(f"Action failed: {e}")
            raise
