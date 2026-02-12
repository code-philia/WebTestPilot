import logging
from pathlib import Path
from typing import Protocol

from baml_py.baml_py import BamlImagePy

from webtestpilot.baml_client.sync_client import b
from webtestpilot.baml_client.types import Feedback, History, Step
from webtestpilot.data_models import BugReport, Session
from webtestpilot.assertion_api.oracle_execution.executor import execute
from webtestpilot.assertion_api.history import serialize_history
from webtestpilot.utils import get_screenshot, pil_to_baml


BASE_DIR = Path(__file__).parent
logger = logging.getLogger(__name__)


class GenerateAssertion(Protocol):
    def __call__(
        self,
        screenshot: BamlImagePy,
        history: list[History],
        action: str,
        assertion: str,
        feedback: list[Feedback],
        baml_options: dict,
    ) -> str: ...


def _verify_assertion(
    function: GenerateAssertion,
    session: Session,
    action: str,
    assertion: str,
    max_tries: int,
) -> None:
    assertion_options = {
        "client_registry": session.config.assertion_generation,
        "collector": session.collector,
    }
    history = serialize_history(session)
    screenshot: BamlImagePy = pil_to_baml(get_screenshot(session.page, full_page=True))
    feedback: list[Feedback] = []

    for trial in range(1, max_tries + 1):
        assertion_code = function(
            screenshot, history, action, assertion, feedback, assertion_options
        )
        logger.info(f"Assertion: {assertion_code}")

        passed, message = execute(assertion_code, session)
        trace = {"assertion": assertion, "trial": trial, "code": assertion_code, "passed": passed}
        if passed:
            logger.info("Assertion passed")
            session.trace.append(trace)
            return

        logger.error(f"Assertion failed: {message}")
        session.trace.append({**trace, "message": message})
        feedback_item = Feedback(response=assertion_code, reason=message)
        feedback.append(feedback_item)

    logger.error("Assertion failed after all retries, raising bug report")
    raise BugReport(message or "assertion failed")


def verify_precondition(session: Session, step: Step) -> None:
    _verify_assertion(
        function=b.GeneratePrecondition,
        session=session,
        action=step.action,
        assertion=step.condition,
        max_tries=1,
    )


def verify_postcondition(session: Session, step: Step) -> None:
    _verify_assertion(
        function=b.GeneratePostcondition,
        session=session,
        action=step.action,
        assertion=step.expectation,
        max_tries=session.config.max_tries,
    )