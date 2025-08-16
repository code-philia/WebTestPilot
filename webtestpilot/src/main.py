import logging
import traceback
from typing import Union, Optional, Callable

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
                execute_action(session, step.action, config)
                verify_postcondition(session, step.action, step.expectation, config)

            except BugReport as report:
                logger.error(f"Bug reported: {str(report)}")
                for hook in hooks:
                    try:
                        hook(report)
                    except Exception:
                        logger.error("Exception in hook:", traceback.format_exc())
                        raise

            except Exception:
                logger.error("Exception in test session:", traceback.format_exc())
                raise


def login_to_indico(page):
    page.goto("http://localhost:8080/")
    page.get_by_role("link", name=" Login").click()
    page.get_by_role("textbox", name="Username or email").fill("admin@admin.com")
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill("webtestpilot")
    page.get_by_role("button", name="Login with Indico").click()


if __name__ == "__main__":
    # test_description = input("Test description: ")
    test_steps = [
        Step(
            condition="",
            action='Click "Create event" link in navigation',
            expectation="Create event dropdown menu appears",
        ),
        Step(
            condition="",
            action='Click "Lecture" option',
            expectation="Lecture creation form opens",
        ),
        Step(
            condition="",
            action='Click in the "Event title" textbox',
            expectation="Event title field is focused for input",
        ),
        Step(
            condition="",
            action='Type "Lecture123456" in the title field',
            expectation="Title field contains the unique lecture name",
        ),
        Step(
            condition="",
            action='Click in the "Venue" textbox',
            expectation="Venue field is focused and ready for input",
        ),
        Step(
            condition="",
            action='Type "Venue123456" in the venue field',
            expectation="Venue field contains unique venue name",
        ),
        Step(
            condition="",
            action='Click in the "Room" textbox',
            expectation="Room field is focused and ready for input",
        ),
        Step(
            condition="",
            action='Type "Room123456" in the room field',
            expectation="Room field contains unique room name",
        ),
        Step(
            condition="",
            action='Click "Public" option for event protection mode',
            expectation="Public protection mode is selected",
        ),
        Step(
            condition="",
            action='Click "Create event" button',
            expectation="Lecture is created and saved",
        ),
        Step(
            condition="",
            action="Verify lecture name appears in page heading",
            expectation="Lecture page displays with correct name in heading",
        ),
        Step(
            condition="",
            action="Verify venue and room information is displayed",
            expectation="Location details are shown on the lecture page",
        ),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()

        login_to_indico(page)
        config = Config.load("config.yaml")
        session = Session(page, config)
        WebTestPilot.run(session, test_steps)

        context.tracing.stop(path="trace.zip")
        context.close()
        browser.close()


# TODO: Test run

# TODO: Setup run RQ3, RQ4 scripts
