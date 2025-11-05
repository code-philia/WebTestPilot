import logging
import traceback
from typing import Optional, Callable

from playwright.sync_api import sync_playwright

from baml_client.types import Step
from executor import (
    execute_action,
    verify_postcondition,
    BugReport,
)
from executor.assertion_api import Session
from parser import parse
from config import Config


logger = logging.getLogger(__name__)
Hook = Callable[[BugReport], None]


class WebTestPilot:
    @staticmethod
    def parse(config: Config, description: str) -> list["Step"]:
        test_case = parse(description, config)
        return test_case.steps

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
        assert isinstance(steps, list)
        assert all(isinstance(s, Step) for s in steps)

        config = session.config
        hooks = hooks or []

        for step in steps:
            try:
                screenshot_after = execute_action(session, step.action, config)
                if assertion and step.expectation:
                    verify_postcondition(
                        session, step.action, step.expectation, config, screenshot_after
                    )

            except BugReport as report:
                logger.error(f"Bug reported: {str(report)}")
                for hook in hooks:
                    try:
                        hook(report)
                    except Exception:
                        logger.error("Exception in hook:", traceback.format_exc())
                        raise
                raise report
            except Exception:
                logger.error("Exception in test session:", traceback.format_exc())
                raise


if __name__ == "__main__":
    pass

