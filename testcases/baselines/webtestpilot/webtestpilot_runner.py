import sys
import time
import traceback
from pathlib import Path
from typing import Optional

from const import ApplicationEnum, TestCase
from dotenv import load_dotenv
from tqdm import tqdm

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent))  # baselines dir
sys.path.append(str(Path(__file__).parent.parent.parent))  # testcases dir
webtestpilot_src_path = str(
    Path(__file__).parent.parent.parent.parent / "webtestpilot" / "src"
)
sys.path.append(webtestpilot_src_path)
CONFIG_PATH = Path(webtestpilot_src_path) / "config.yaml"

from base_runner import BaseTestRunner, TestResult
from main import Config, Session, Step, WebTestPilot

load_dotenv()


class WebTestPilotTestRunner(BaseTestRunner):
    """Test runner implementation for WebTestPilot agent."""

    def __init__(
        self,
        test_case_path: str,
        test_output_path: str,
        application: ApplicationEnum,
        model: Optional[str] = None,
        headless: bool = True,
        **kwargs,
    ):
        super().__init__(
            test_case_path, test_output_path, application, model=model, **kwargs
        )
        self.headless = headless

    def run_test_case(self, test_case: TestCase) -> TestResult:
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
                config = Config.load(CONFIG_PATH)
                session = Session(page, config)

                # Execute each action
                start_time = time.perf_counter()
                for i, action in enumerate(actions):
                    try:
                        action_text = action.action[:40]
                        step_bar.set_description(f"  Step {i + 1}: {action_text}")
                        step = Step(condition="", action=action.action, expectation=action.expectedResult)

                        WebTestPilot.run(session, step)

                        result.traces = session.trace
                        result.current_step += 1
                        step_bar.update(1)
                        step_bar.set_postfix(status="✓", refresh=True)

                    except Exception as e:
                        result.error_message = f"Error at step {i + 1}: {str(e)}"
                        step_bar.set_postfix(status="✗", refresh=True)
                        tqdm.write(f"    Error: {e}")
                        break

                end_time = time.perf_counter()
                result.runtime = end_time - start_time

                # Mark as success if all steps completed
                result.success = result.current_step == result.total_step

                # Close the page
                page.close()

            except Exception as e:
                result.error_message = f"Test setup error: {str(e)}"
                result.success = False
                step_bar.set_postfix(status="✗", refresh=True)
                traceback.print_exc()

        return result
