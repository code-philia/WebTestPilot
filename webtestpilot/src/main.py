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
                execute_action(session, step.action, config)
                if (
                    assertion and step.expectation
                ):  # Newly added, only verify if expectation is provided.
                    verify_postcondition(session, step.action, step.expectation, config)

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


def login_to_indico(page):
    page.goto("http://localhost:8080/")
    page.get_by_role("link", name=" Login").click()
    page.get_by_role("textbox", name="Username or email").fill("admin@admin.com")
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill("webtestpilot")
    page.get_by_role("button", name="Login with Indico").click()


def run_test_with_playwright(
    test_steps: list[Step],
    cdp_endpoint: str = "http://localhost:9222",
    config_path: str = "config.yaml",
    enable_assertions: bool = True,
    trace_output: str = "trace.zip",
    url: Optional[str] = None,
) -> dict:
    """
    Run a test using Playwright connected to a remote browser.

    Args:
        test_steps: List of Step objects to execute
        cdp_endpoint: Chrome DevTools Protocol endpoint URL
        config_path: Path to config.yaml file
        enable_assertions: Whether to verify expectations/postconditions
        trace_output: Path to save Playwright trace
        url: Optional URL to navigate to before running test

    Returns:
        Dict with test results
    """
    result = {"success": True, "steps_executed": 0, "errors": []}

    with sync_playwright() as p:
        browser = None
        context = None
        page = None

        try:
            # Connect to browser
            logger.info(f"Connecting to browser at {cdp_endpoint}")
            browser = p.chromium.connect_over_cdp(cdp_endpoint)
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
            page = context.pages[0] if context.pages else context.new_page()

            # Navigate to URL if provided
            if url:
                logger.info(f"Navigating to {url}")
                page.goto(url)

            # Load config and create session
            config = Config.load(config_path)
            session = Session(page, config)

            # Run the test
            logger.info(f"Starting test execution with {len(test_steps)} steps")
            WebTestPilot.run(session, test_steps, assertion=enable_assertions)
            result["steps_executed"] = len(test_steps)

            logger.info("✅ Test completed successfully!")

        except Exception as e:
            logger.error(f"❌ Test failed: {str(e)}", exc_info=True)
            result["success"] = False
            result["errors"].append(str(e))

        finally:
            # Save trace if context was created
            if context:
                context.tracing.stop(path=trace_output)

    return result


if __name__ == "__main__":
    """
    Example usage of WebTestPilot for direct script execution.
    For VS Code integration, use cli.py instead.
    
    To run this example:
        1. Start Chrome with remote debugging: 
           chrome --remote-debugging-port=9222
        2. Run this script:
           python main.py
    """
    import sys

    # Example test steps - customize for your application
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
    ]

    # Configuration
    cdp_endpoint = "http://localhost:9222"
    config_path = "config.yaml"
    enable_assertions = True

    print(f"Running test with {len(test_steps)} steps...")
    print(f"CDP Endpoint: {cdp_endpoint}")
    print(f"Config: {config_path}")
    print(f"Assertions: {'enabled' if enable_assertions else 'disabled'}")
    print("-" * 60)

    # Run the test
    result = run_test_with_playwright(
        test_steps=test_steps,
        cdp_endpoint=cdp_endpoint,
        config_path=config_path,
        enable_assertions=enable_assertions,
        trace_output="trace.zip",
    )

    # Print results
    print("-" * 60)
    if result["success"]:
        print(f"✅ Test PASSED - {result['steps_executed']} steps executed")
    else:
        print(f"❌ Test FAILED")
        for error in result["errors"]:
            print(f"   Error: {error}")
        sys.exit(1)
    print("-" * 60)
