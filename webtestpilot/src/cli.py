import argparse
import json
import logging
import sys
from typing import Any, Optional

from baml_client.types import Step
from config import Config
from executor import BugReport
from executor.assertion_api import Session
from main import WebTestPilot
from playwright.sync_api import Page, sync_playwright

logger = logging.getLogger(__name__)
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080


def parse_test_action_to_step(action: dict[str, Any]) -> Step:
    """
    Convert a test action from VS Code format to WebTestPilot Step format

    VS Code format:
    {
        "action": "Click the login button",
        "expectedResult": "Login form appears"
    }

    WebTestPilot Step format:
    Step(condition="", action="...", expectation="...")
    """
    return Step(
        condition="",
        action=action.get("action", ""),
        expectation=action.get("expectedResult", ""),
    )


def inject_environment_values(
    environment_data: dict[str, str], test_steps: list[Step]
) -> list[Step]:
    """i.e. ${{username}} -> actual value from environment file"""
    injected_steps = []
    for step in test_steps:
        injected_action = step.action
        injected_expectation = step.expectation

        for var_name, var_value in environment_data.items():
            placeholder = f"${{{var_name}}}"
            injected_action = injected_action.replace(placeholder, var_value)
            injected_expectation = injected_expectation.replace(placeholder, var_value)

        injected_steps.append(
            Step(
                condition=step.condition,
                action=injected_action,
                expectation=injected_expectation,
            )
        )

    return injected_steps


def load_and_parse_test_file(
    test_file_path: str,
    fixture_file_path: str | None,
    environment_file_path: str | None,
) -> tuple[dict[str, Any], list[Step]]:
    """
    Load and parse a JSON test file

    Args:
        test_file_path: Path to the test JSON file

    Returns:
        Tuple of (test_data, test_steps)

    Raises:
        FileNotFoundError: If test file doesn't exist
        json.JSONDecodeError: If test file contains invalid JSON
        ValueError: If no actions are defined in the test file
    """
    # Order: Load test -> Fixtures -> Parse Test + Fixture -> Merge -> Inject Environment values
    with open(test_file_path, "r") as f:
        test_data = json.load(f)

    logger.debug(f"Loaded test: {test_data.get('name', 'Unnamed Test')}")
    logger.debug(f"Test URL: {test_data.get('url', 'No URL specified')}")

    # Fixtures will be pre-pended to test steps.
    fixture_actions = []
    if fixture_file_path:
        logger.debug(f"Using fixture file: {fixture_file_path}")
        with open(fixture_file_path, "r") as fixture_file:
            fixture_data: dict = json.load(fixture_file)
            fixture_actions = fixture_data.get("actions", [])

    actions = test_data.get("actions", [])
    if not actions:
        raise ValueError("No actions defined in test")

    fixture_steps = [parse_test_action_to_step(action) for action in fixture_actions]
    test_steps = [parse_test_action_to_step(action) for action in actions]

    logger.debug(f"Converted {len(test_steps)} actions to test steps")
    merged_steps = fixture_steps + test_steps
    logger.debug(f"Total steps after merging fixture: {len(merged_steps)}")

    # Inject last to ensure all placeholders are replaced.
    if environment_file_path:
        logger.debug(f"Using environment file: {environment_file_path}")
        with open(environment_file_path, "r") as env_file:
            environment_data = json.load(env_file)
            test_steps = inject_environment_values(
                environment_data=environment_data,
                test_steps=test_steps,
            )

    return test_data, merged_steps


def run_test_from_file(
    test_file_path: str,
    config_path: str,
    cdp_endpoint: str,
    target_id: Optional[str],
    fixture_file_path: Optional[str],
    environment_file_path: Optional[str],
    enable_assertions: bool,
) -> dict[str, Any]:
    try:
        # Load and parse test data
        test_data, test_steps = load_and_parse_test_file(
            test_file_path, fixture_file_path, environment_file_path
        )
        config = Config.load(config_path)

        result: dict = {
            "success": True,
            "test_name": test_data.get("name"),
            "url": test_data.get("url"),
            "steps_executed": 0,
            "errors": [],
        }

        with sync_playwright() as p:
            logger.info(f"Connecting to browser at {cdp_endpoint}")

            # Connect to existing browser via CDP
            browser = p.chromium.connect_over_cdp(cdp_endpoint)

            # Get or create context
            context = (
                browser.contexts[0]
                if browser.contexts
                else browser.new_context(
                    viewport={
                        "width": VIEWPORT_WIDTH,
                        "height": VIEWPORT_HEIGHT,
                    }
                )
            )

            # Get the correct page based on tab_index
            page: Page | None = None
            if target_id:
                for tab in context.pages:
                    cdp = context.new_cdp_session(tab)
                    info = cdp.send("Target.getTargetInfo")

                    if info["targetInfo"]["targetId"] == target_id:
                        page = tab
                        break

                if not page:
                    raise ValueError(
                        f"Tab with target id {target_id} not found in browser context."
                    )
            else:
                # Fallback to original behavior
                page = context.pages[0] if context.pages else context.new_page()
                logger.info("Using first available page (no tab index specified)")

            assert page

            # This is important for consistent grounding results.
            page.set_viewport_size(
                {
                    "width": VIEWPORT_WIDTH,
                    "height": VIEWPORT_HEIGHT,
                }
            )

            # Navigate to test URL if specified
            test_url = test_data.get("url")
            assert test_url, "Test URL must be specified in the test data"

            logger.info(f"Navigating to {test_url}")
            page.goto(test_url, timeout=5000, wait_until="domcontentloaded")

            # Create session
            session = Session(page, config)

            try:
                # Run the test
                logger.info(f"Starting test execution with {len(test_steps)} steps")
                WebTestPilot.run(session, test_steps, assertion=enable_assertions)
                result["steps_executed"] = len(test_steps)
            except BugReport as report:
                result["success"] = False
                result["errors"].append(str(report))
            except Exception as e:
                logger.error(f"Test execution failed: {str(e)}", exc_info=True)
                result["success"] = False
                result["errors"].append(str(e))

        return result
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="WebTestPilot CLI - Run automated web tests from VS Code"
    )

    parser.add_argument("test_file", type=str, help="Path to the test JSON file")

    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to config.yaml file (default: config.yaml)",
    )

    parser.add_argument(
        "--cdp-endpoint",
        type=str,
        default="http://localhost:9222",
        help="CDP endpoint URL (default: http://localhost:9222)",
    )

    parser.add_argument(
        "--target-id",
        type=str,
        help="id of cdp session",
    )

    parser.add_argument(
        "--no-assertions",
        action="store_true",
        help="Disable assertion verification (only execute actions)",
    )

    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results as JSON instead of human-readable format",
    )

    parser.add_argument(
        "--fixture-file-path",
        type=Optional[str],
        default=None,
        help="Path to fixture file",
    )

    parser.add_argument(
        "--environment-file-path",
        type=Optional[str],
        default=None,
        help="Path to environment file",
    )

    args = parser.parse_args()

    # Run the test
    result = run_test_from_file(
        test_file_path=args.test_file,
        config_path=args.config,
        cdp_endpoint=args.cdp_endpoint,
        target_id=getattr(args, "target_id", None),
        fixture_file_path=args.fixture_file_path,
        environment_file_path=args.environment_file_path,
        enable_assertions=not args.no_assertions,
    )

    # Output results
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'=' * 60}")
        print(f"Test: {result.get('test_name', 'Unknown')}")
        print(f"{'=' * 60}")

        if result["success"]:
            print("✅ Test PASSED")
            print(f"   Steps executed: {result.get('steps_executed', 0)}")
        else:
            print("❌ Test FAILED")

        print(f"{'=' * 60}\n")

    # Exit with appropriate code
    logger.debug(f"Exiting with code: {0 if result['success'] else 1}")
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
