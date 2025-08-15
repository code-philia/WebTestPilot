import logging
import traceback
from typing import Union, Optional, Callable
from playwright.sync_api import sync_playwright

from baml_client.types import Step
from executor import (
    verify_precondition,
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
    def run(
        session: Session,
        test_input: Union[str, "Step", list["Step"]],
        hooks: Optional[list[Hook]] = None,
    ) -> None:
        """
        Execute a test case on the given Session.

        Params:
            session: The current test session.
            test_input: Description string, a single Step, or list of Steps.
            hooks: Optional list of hooks to trigger (Callables) when a BugReport occurs.
        """
        config = session.config
        hooks = hooks or []

        # Normalize to steps
        if isinstance(test_input, str):
            test_case = parse(test_input, config)
            steps = test_case.steps
        elif hasattr(test_input, "__iter__") and not isinstance(
            test_input, (str, bytes)
        ):
            steps = list(test_input)
        else:
            steps = [test_input]

        for step in steps:
            try:
                #verify_precondition(session, step.condition, config)
                execute_action(session, step.action, config)
                #verify_postcondition(session, step.expectation, config)

            except BugReport as report:
                for hook in hooks:
                    try:
                        hook(report)
                    except Exception:
                        logger.error("Exception in hook:", traceback.format_exc())
                        raise

            except Exception:
                logger.error("Exception in test session:", traceback.format_exc())
                raise


if __name__ == "__main__":
    test_url = input("Test url: ")
    test_description = input("Test description: ")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="videos",
            record_video_size={"width": 1280, "height": 720}
        )
        page = context.new_page()
        page.goto(test_url)
        config = Config.load("config.yaml")
        session = Session(page, config)
        WebTestPilot.run(session, test_description)

        context.close()
        browser.close()


# TODO: Test run

# TODO: Setup run RQ3, RQ4 scripts
