import logging
import traceback
from typing import Callable, Optional

from webtestpilot.baml_client.types import Step
from webtestpilot.data_models import BugReport, Session
from webtestpilot.action_api import execute_action
from webtestpilot.assertion_api import verify_precondition, verify_postcondition


logger = logging.getLogger(__name__)
Hook = Callable[[BugReport], None]


class WebTestPilot:
    @staticmethod
    def run(
        session: Session,
        steps: list["Step"],
        assertion: bool,
        hooks: Optional[list[Hook]] = None,
    ) -> None:
        """
        Execute a test case on the given Session.

        Params:
            session: The current test session.
            test_input: Description string, a single Step, or list of Steps.
            hooks: Optional list of hooks to trigger (Callables) when a BugReport occurs.
        """
        if isinstance(steps, list):
            assert all(isinstance(s, Step) for s in steps)
        else:
            raise TypeError("steps must be a list of Step objects")

        hooks = hooks or []

        for step in steps:
            try:
                if assertion and step.condition and step.condition.strip():
                    logger.info(f"Condition: {step.condition}")
                    verify_precondition(session, step)

                execute_action(session, step.action)

                if assertion and step.expectation and step.expectation.strip():
                    logger.info(f"Expectation: {step.expectation}")
                    verify_postcondition(session, step)

            except BugReport as report:
                logger.error(f"Bug reported: {str(report)}")
                for hook in hooks:
                    hook(report)

            except Exception:
                logger.error(f"Exception in test session:\n{traceback.format_exc()}")
                raise
