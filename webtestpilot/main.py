import traceback
from typing import Union
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Page
from baml_py import ClientRegistry

from webtestpilot.src.baml_client.types import Step
from webtestpilot.src.executor import (
    verify_precondition,
    execute_action,
    verify_postcondition,
    BugReport
)
from webtestpilot.src.executor.assertion_api import Session
from webtestpilot.src.parser import parse


load_dotenv()

cr = ClientRegistry()
cr.set_primary("GPT")


class WebTestPilot:

    @staticmethod
    def run(
        session: Session,
        client_registry: ClientRegistry,
        test_input: Union[str, "Step", list["Step"]],
        bug_hooks: Optional[list[Hook]] = None
    ) -> None:
        """
        Execute a test case on the given Session.

        Params:
            session: The current test session.
            client_registry: BAML ClientRegistry instance.
            test_input: Description string, single Step, or list of Steps.
            bug_hooks: Optional list of callables called when a BugReport occurs.
        """
        bug_hooks = bug_hooks or []

        # Normalize to steps
        if isinstance(test_input, str):
            test_case = parse(test_input, client_registry)
            steps = test_case.steps
        elif hasattr(test_input, "__iter__") and not isinstance(test_input, (str, bytes)):
            steps = list(test_input)
        else:
            steps = [test_input]

        for step in steps:
            try:
                verify_precondition(session, step.condition)
                execute_action(session, step.action)
                verify_postcondition(session, step.expectation)

            except BugReport as report:
                for hook in bug_hooks:
                    try:
                        hook(report)
                    except:
                        pass

            except Exception:
                print(traceback.format_exc())
                raise


if __name__ == "__main__":
    test_description = input("Test description: ")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        with browser.new_context() as context:
            page = context.new_page()
            session = Session(page)
            WebTestPilot.run(session, client_registry, test_description)

        browser.close()


# TODO: Unified way to manage clientregistry for each llm function call

# TODO: Run experiments