import ast
import sys
import time
import traceback
from pathlib import Path
from typing import Optional

from base_runner import BaseTestRunner, TestResult
from const import ApplicationEnum, TestCase
from lavague.contexts.openai import OpenaiContext
from lavague.core import ActionEngine, WorldModel
from lavague.core.agents import WebAgent
from lavague.core.token_counter import TokenCounter
from lavague.drivers.playwright import PlaywrightDriver
from tqdm import tqdm

# Add project directory
PROJECT_DIR = Path(__file__).parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.append(str(PROJECT_DIR))


class LavagueTestRunner(BaseTestRunner):
    """Test runner implementation for LaVague agent."""

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

    def extract_trace_from_code(self, code: str) -> list[dict]:
        """Lavague's trace contains code, the last trace contains all the actions.
        i.e.: from playwright.sync_api import sync_playwright\n\npage.set_viewport_size({\"width\": 1080, \"height\": 1080})\n[\n    {\n        \"action\": {\n            \"name\": \"click\",\n            \"args\": {\n                \"xpath\": \"/html/body/header/nav/div/a\"\n            }\n        }\n    }\n][\n    {\n        \"action\": {\n            \"name\": \"click\",\n            \"args\": {\n                \"xpath\": \"/html/body/div[4]/div/div[2]/form/div/div[2]/input\"\n            }\n        }\n    }\n][\n    {\n        \"action\": {\n            \"name\": \"setValue\",\n            \"args\": {\n                \"xpath\": \"/html/body/div[4]/div/div[2]/form/div/div[2]/input\",\n                \"value\": \"password\"\n            }\n        }\n    }\n][\n    {\n        \"action\": {\n            \"name\": \"click\",\n            \"args\": {\n                \"xpath\": \"/html/body/div[4]/div/div[2]/form/div[2]/div[2]/button\"\n            }\n        }\n    }\n]
        """
        # First 3 lines are code, remove
        code = "\n".join(code.split("\n")[3:])

        # Parse the remaining data (arrays concatenated together)
        # Split the arrays but keep the brackets
        arrays = code.split("][")
        arrays = [arr + "]" if not arr.endswith("]") else arr for arr in arrays]
        arrays = ["[" + arr if not arr.startswith("[") else arr for arr in arrays]
        traces = []
        for arr in arrays:
            traces.extend(ast.literal_eval(arr))

        print(traces)
        return traces

    def run_test_case(self, test_case: TestCase) -> TestResult:
        """Run a single test case using LaVague agent."""
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
                # Get initial page with setup
                step_bar.set_description("  Setting up page")
                page = self.get_initial_page(setup_function)

                def get_page():
                    return page

                # Create PlaywrightDriver with the setup page
                playwright_driver = PlaywrightDriver(get_sync_playwright_page=get_page)
                playwright_driver.page = page

                # Set up LaVague components
                step_bar.set_description("  Initializing LaVague")
                token_counter = TokenCounter(log=False)

                if self.model:
                    context = OpenaiContext(llm=self.model, mm_llm=self.model)
                    action_engine = ActionEngine.from_context(
                        context, playwright_driver
                    )
                    world_model = WorldModel.from_context(context)
                else:
                    # Use defaults
                    action_engine = ActionEngine(playwright_driver)
                    world_model = WorldModel()

                agent = WebAgent(
                    world_model, action_engine, n_steps=1, token_counter=token_counter
                )

                start_time = time.perf_counter()
                # Execute actions
                for i, action in enumerate(actions):
                    try:
                        step_bar.set_description(
                            f"  Step {i + 1}: {action.action[:40]}"
                        )

                        # Actual run step
                        action_result = agent.run(action.action)

                        result.token_count = action_result.total_estimated_tokens
                        # Save trace, the latest action result contains all the previous actions.
                        result.traces = self.extract_trace_from_code(action_result.code)

                        if not action_result.success:
                            result.error_message = f"Action {i + 1} failed"
                            step_bar.set_postfix(status="✗", refresh=True)
                            break

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
