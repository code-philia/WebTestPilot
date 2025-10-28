import base64
import logging

from baml_py import Image
from executor.assertion_api.session import Session

from config import Config
from baml_client.sync_client import b
from baml_client.types import Feedback
from executor.assertion_api import execute_assertion


logger = logging.getLogger(__name__)


class BugReport(Exception):
    def __init__(self, message, screenshots=None, steps=None):
        super().__init__(message)
        self.screenshots = screenshots or []
        self.steps = steps or []


def verify_precondition(
    session: Session, condition: str, action: str, config: Config
) -> None:
    logger.info(f"Condition: {condition}")
    client_registry = config.assertion_generation
    collector = session.collector
    screenshot = base64.b64encode(session.page.screenshot(type="png")).decode("utf-8")
    screenshot = Image.from_base64("image/png", screenshot)
    history = session.get_history()

    response = b.GeneratePrecondition(
        screenshot,
        history,
        action,
        condition,
        feedback=[],
        baml_options={"client_registry": client_registry, "collector": collector},
    )
    passed, message = execute_assertion(response, session)
    if passed:
        logger.info("Precondition passed.")
        return
    else:
        logger.info(f"Precondition failed: {message}")
        raise BugReport(message)


def execute_action(session: Session, action: str, config: Config) -> None:
    # Increment step counter and output step info for VSCode parsing
    session.step_counter += 1
    logger.info(f"Action: {action}")
    # Also output in a format that's easy for VSCode to parse
    logger.info(f"STEP_{session.step_counter}: {action}")
    client_registry = config.action_proposer
    client_name = config.action_proposer_name
    collector = session.collector
    screenshot = base64.b64encode(session.page.screenshot(type="png")).decode("utf-8")
    screenshot = Image.from_base64("image/png", screenshot)

    code = b.ProposeActions(
        screenshot,
        action,
        baml_options={"client_registry": client_registry, "collector": collector},
    )

    try:
        if client_name == "UITARS":
            import executor.automators.uitars as automator
            automator.execute(code, session.page)
        elif client_name == "InternVL3":
            import executor.automators.pyautogui as automator
            automator.execute(code, session.page)
        else:
            import executor.automators.custom as automator
            automator.execute(code, session.page, session)
        session.capture_state(prev_action=action)
        logger.info(f"STEP_{session.step_counter}_PASSED")
    except Exception as e:
        logger.info(f"STEP_{session.step_counter}_FAILED: {str(e)}")
        raise


def verify_postcondition(
    session: Session, action: str, expectation: str, config: Config
) -> None:
    logger.info(f"Expectation: {expectation}")
    # Output step verification info for VSCode parsing
    logger.info(f"VERIFYING_STEP_{session.step_counter}: {expectation}")
    client_registry = config.assertion_generation
    collector = session.collector
    max_retries = config.max_retries
    screenshot = base64.b64encode(session.page.screenshot(type="png")).decode("utf-8")
    screenshot = Image.from_base64("image/png", screenshot)
    history = session.get_history()

    feedback = []
    message = "Post-condition verification failed after all retries"
    
    for _ in range(0, max_retries + 1):
        response = b.GeneratePostcondition(
            screenshot,
            history,
            action,
            expectation,
            feedback,
            baml_options={"client_registry": client_registry, "collector": collector},
        )
        logger.info(f"Postcondition: {response}")
        passed, current_message = execute_assertion(response, session)
        if passed:
            logger.info("Postcondition passed.")
            logger.info(f"VERIFYING_STEP_{session.step_counter}_PASSED")
            return
        else:
            message = current_message  # Update message for potential error reporting
            logger.info(f"Postcondition failed: {message}")
            feedback_item = Feedback(response=response, reason=message)
            feedback.append(feedback_item)

    logger.info(f"VERIFYING_STEP_{session.step_counter}_FAILED: {message}")
    raise BugReport(message)
