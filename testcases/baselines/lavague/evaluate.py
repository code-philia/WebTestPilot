import argparse
import json
import os
from pathlib import Path
import sys
from dataclasses import dataclass, field

from dotenv import load_dotenv
from lavague.core import ActionEngine, WorldModel
from lavague.core.agents import WebAgent
from lavague.core.token_counter import TokenCounter
from lavague.drivers.playwright import PlaywrightDriver
from playwright.sync_api import sync_playwright
from tqdm import tqdm
from .utils import ApplicationType, setup_page_state

# Add the testcases and baselines directory to Python path
testcases_dir = str(Path(__file__).parent.parent.parent)
baselines_dir = str(Path(__file__).parent.parent)
sys.path.append(testcases_dir)
sys.path.append(baselines_dir)

load_dotenv()

# Get the testcases directory (parent of parent of parent)
TESTCASES_DIR = Path(__file__).parent.parent.parent


@dataclass
class TestResult:
    test_name: str
    success: bool = False
    current_step: int = 0
    total_step: int = 0
    traces: list = field(default_factory=list)

    @property
    def correct_trace(self) -> float:
        return self.current_step / self.total_step if self.total_step > 0 else 0.0


@dataclass
class TestResultDataset:
    results: list[TestResult] = field(default_factory=list)

    @property
    def correct_trace(self) -> float:
        return (
            sum(result.correct_trace for result in self.results) / len(self.results)
            if self.results
            else 0.0
        )

    def save_results(self, file_path: str):
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            json.dump([result.__dict__ for result in self.results], f, indent=4)

        print(f"Results saved to {file_path}")


class TestRunner:
    def __init__(
        self, test_case_path: str, test_output_path: str, application: ApplicationType
    ):
        self.test_case_path = test_case_path
        self.test_output_path = test_output_path
        self.application = application

    def load_test_cases(self) -> list[dict]:
        files = os.listdir(self.test_case_path)
        test_cases = []
        for file in files:
            if not file.endswith(".json"):
                continue

            if "tc_02_book_create" not in file:
                continue

            with open(f"{self.test_case_path}/{file}", "r") as f:
                test_case = json.load(f)
                test_cases.append(test_case)

        return test_cases

    def run_test_case(self, test_case: dict):
        actions = test_case.get("actions", [])
        test_name = test_case.get("name", "Unnamed")
        setup_function = test_case.get("setup_function", "")
        result = TestResult(test_name=test_name, total_step=len(actions))

        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page = setup_page_state(page, setup_function, application=self.application)

        def get_page():
            return page

        # Create PlaywrightDriver with the captured page
        playwright_driver = PlaywrightDriver(get_sync_playwright_page=get_page)
        playwright_driver.page = (
            page  # Set the page directly as the lib implementation does not support.
        )

        token_counter = TokenCounter(log=True)
        action_engine = ActionEngine(playwright_driver)
        world_model = WorldModel()
        # TODO: Max steps?
        agent = WebAgent(
            world_model, action_engine, n_steps=1, token_counter=token_counter
        )

        for i, action in tqdm(enumerate(actions), total=len(actions)):
            try:
                print(f"Executing action {i}: {action}")
                action_result = agent.run(action["action"])
            except Exception as e:
                print(f"Error executing action {i}: {e}")
                action_result = None

            if not action_result:
                print(f"Action {i} failed: {action['action']}")
                result.success = False
                break

            result.traces.append(action_result.code)
            result.current_step = min(result.current_step + 1, result.total_step)
            result.success = result.current_step == result.total_step

        print(agent.process_token_usage())
        return result

    def run_test_cases(self):
        test_cases = self.load_test_cases()
        results = TestResultDataset()

        for test_case in tqdm(test_cases, desc="Running test cases"):
            actions = test_case.get("actions", [])
            if not actions:
                print(
                    f"No actions found in test case {test_case.get('name', 'Unnamed')}"
                )
                continue

            result = self.run_test_case(test_case)
            results.results.append(result)

        results.save_results(self.test_output_path)
        return results


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Run baseline evaluation for web applications"
    )
    parser.add_argument(
        "--application",
        type=str,
        choices=["bookstack", "invoiceninja", "indico", "prestashop"],
        help="Application to run tests against",
    )

    args = parser.parse_args()
    application = args.application
    test_case_path = TESTCASES_DIR / "eval_data" / "test_cases" / application
    output_path = (
        TESTCASES_DIR / "eval_data" / "results" / "lavague" / f"{application}.json"
    )

    print(f"Running LaVague evaluation for: {application}")
    print(f"Test cases path: {test_case_path}")
    print(f"Output path: {output_path}")

    # Create and run test runner
    test_runner = TestRunner(str(test_case_path), str(output_path), application)
    results = test_runner.run_test_cases()

    # Print the results
    print("\n" + "=" * 50)
    print("EVALUATION RESULTS")
    print("=" * 50)

    for result in results.results:
        print(
            f"Test: {result.test_name}, Success: {result.success}, "
            f"Correct Trace: {result.correct_trace:.2f}"
        )

    print("=" * 50)
    print(f"Overall Correct Trace: {results.correct_trace:.2f}")
    print("=" * 50)


if __name__ == "__main__":
    main()
