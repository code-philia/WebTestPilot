import sys
import time
import traceback
from pathlib import Path
from typing import Optional

# Add project directory
PROJECT_DIR = Path(__file__).parent.parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.append(str(PROJECT_DIR))

# Add webtestpilot directory
WEBTESTPILOT_DIR = PROJECT_DIR / "webtestpilot" / "src"
if str(WEBTESTPILOT_DIR) not in sys.path:
    sys.path.append(str(WEBTESTPILOT_DIR))

from baselines.base_runner import BaseTestRunner, TestResult
from baselines.const import ApplicationEnum, MethodEnum, TestCase

# Reuse the same imports the baseline runner uses
from main import Config, Session, Step, WebTestPilot
from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
from tqdm import tqdm


class WebTestPilotTestRunner(BaseTestRunner):
    """Test runner implementation for WebTestPilot agent."""

    def __init__(
        self,
        test_case_path: str,
        test_output_path: str,
        application: ApplicationEnum,
        model: Optional[str] = None,
        headless: bool = True,
        config: Config = None
    ):
        super().__init__(
            test_case_path,
            test_output_path,
            application,
            model=model,
            method=MethodEnum.webtestpilot
        )
        self.headless = headless
        self.config = config

    def _load_test_cases(self, filter_pattern: Optional[str] = None) -> list[TestCase]:
        """Load test cases from test case directory."""
        test_cases: list[TestCase] = []

        if not self.test_case_path.exists():
            print(f"Test case path does not exist: {self.test_case_path}")
            return test_cases

        for file_path in sorted(
            self.test_case_path.glob("*.yaml"), key=lambda p: p.stem
        ):
            if filter_pattern and filter_pattern not in file_path.stem:
                continue

            try:
                yaml = YAML()
                with open(file_path, "r") as f:
                    data: dict = yaml.load(f)

                    # Convert description -> actions list
                    description: str = data.get("description")
                    steps = WebTestPilot.parse(self.config, description)
                    actions = [
                        {"action": step.action, "expectedResult": step.expectation}
                        for step in steps
                    ]

                    # Parse as TestCase
                    test_case = TestCase.from_dict({
                        **data,
                        "actions": actions
                    })
                    print(test_case)
                    test_cases.append(test_case)

            except ParserError as e:
                print(f"Error loading {file_path}: {e}")
                raise e

        return test_cases
    
    async def run_test_case(self, test_case: TestCase, is_buggy: bool) -> TestResult:
        """Run a single test case using WebTestPilot agent."""
        actions = test_case.actions
        test_name = test_case.name
        setup_function = test_case.setup_function

        result = TestResult(test_name=test_name, total_step=len(actions))

        # Create nested progress bar for actions
        with tqdm(
            total=len(actions),
            desc=f"  Steps for {test_name[:30]}",
            leave=False,
            unit="step",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            colour="green",
        ) as step_bar:
            try:
                # Get initial page with proper setup
                step_bar.set_description("  Setting up page")
                page = self.get_initial_page(setup_function)

                # If there's a custom config, load it; otherwise load default config
                session = Session(page, self.config)

                # Execute each action
                start_time = time.perf_counter()
                for i, action in enumerate(actions):
                    try:
                        action_text = action.action[:40]
                        step_bar.set_description(f"  Step {i + 1}: {action_text}")
                        step = Step(
                            condition="",
                            action=action.action,
                            expectation=action.expectedResult,
                        )

                        if is_buggy:
                            print("Running with assertion")
                            WebTestPilot.run(session, [step], assertion=True)
                        else:
                            print("Running without assertion")
                            WebTestPilot.run(session, [step], assertion=False)

                        result.traces = session.trace
                        result.current_step += 1
                        step_bar.update(1)
                        step_bar.set_postfix(status="✓", refresh=True)

                    except Exception as e:
                        result.error_message = f"Error at step {i + 1}: {str(e)}"
                        step_bar.set_postfix(status="✗", refresh=True)
                        tqdm.write(f"    Error: {e}")
                        print(traceback.format_exc())
                        break

                # Record total runtime
                end_time = time.perf_counter()
                result.runtime = end_time - start_time

                # Record cumulative token usage
                usage = session.collector.usage
                result.token_count = usage.input_tokens + usage.output_tokens

                # Mark as success if all steps completed
                result.success = result.current_step == result.total_step

                # Close the page
                page.close()

            except Exception as e:
                result.error_message = f"Test setup error: {str(e)}"
                result.success = False
                step_bar.set_postfix(status="✗", refresh=True)
                print(traceback.format_exc())
                # traceback.print_exc()

        return result
