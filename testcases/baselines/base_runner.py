import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from const import ApplicationEnum, TestCase
from playwright.sync_api import Page, sync_playwright
from tqdm import tqdm
from utils import setup_page_state


@dataclass
class TestResult:
    test_name: str
    success: bool = False
    current_step: int = 0
    total_step: int = 0
    traces: list = field(default_factory=list)
    error_message: Optional[str] = None
    runtime: float = 0.0
    token_count: int = 0

    @property
    def correct_trace(self) -> float:
        return self.current_step / self.total_step if self.total_step > 0 else 0.0

    @property
    def runtime_per_step(self) -> float:
        return self.runtime / self.current_step if self.current_step > 0 else 0.0

    def __str__(self):
        status = "✓" if self.success else "✗"
        status_color = "\033[92m" if self.success else "\033[91m"  # Green or Red
        reset_color = "\033[0m"

        return (
            f"{status_color}{status}{reset_color} {self.test_name:<45}: "
            f"Steps={self.current_step:>2}/{self.total_step:<2} "
            f"({self.correct_trace})"
        )


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

    @property
    def success_rate(self) -> float:
        return (
            sum(1 for result in self.results if result.success) / len(self.results)
            if self.results
            else 0.0
        )

    def save_results(self, file_path: str):
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            results_data = []
            for result in self.results:
                result_dict = result.__dict__.copy()
                result_dict["correct_trace"] = result.correct_trace
                result_dict["runtime_per_step"] = result.runtime_per_step
                results_data.append(result_dict)
            json.dump(results_data, f, indent=4)

        print(f"Results saved to {file_path}")

    def print_summary(self):
        """Print a summary of test results."""
        print()
        print("=" * 80)
        print("TEST RESULT SUMMARY")
        print("=" * 80)

        # Create a summary progress bar for visual representation
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = len(self.results) - passed_tests

        for result in sorted(self.results, key=lambda r: r.test_name):
            print(result)

        print("=" * 80)
        print(f"Total Tests: {len(self.results)}")
        print(
            f"\033[92mPassed: {passed_tests}\033[0m | \033[91mFailed: {failed_tests}\033[0m"
        )
        print(f"Success Rate: {self.success_rate:.1%}")
        print(f"Overall Correct Trace: {self.correct_trace:.1%}")
        print("=" * 80)


class BaseTestRunner(ABC):
    """Abstract base class for all test runner implementations."""

    def __init__(
        self,
        test_case_path: str,
        test_output_path: str,
        application: ApplicationEnum,
        model: Optional[str] = None,
        **kwargs,
    ):
        self.test_case_path = Path(test_case_path)
        self.test_output_path = Path(test_output_path)
        self.application = application
        self.model = model
        self.config = kwargs

        # For configuring Playwright
        self.playwright = None
        self.browser = None
        self.context = None

    def load_test_cases(self, filter_pattern: Optional[str] = None) -> list[TestCase]:
        """Load test cases from test case directory."""
        test_cases: list[TestCase] = []

        if not self.test_case_path.exists():
            print(f"Test case path does not exist: {self.test_case_path}")
            return test_cases

        for file_path in sorted(
            self.test_case_path.glob("*.json"), key=lambda p: p.stem
        )[1:2]:
            if filter_pattern and filter_pattern not in file_path.stem:
                continue

            try:
                with open(file_path, "r") as f:
                    test_case_data = json.load(f)
                    test_case = TestCase.from_dict(test_case_data)
                    test_cases.append(test_case)
            except json.JSONDecodeError as e:
                print(f"Error loading {file_path}: {e}")
                raise e

        return test_cases

    def clean_up_playwright(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def get_initial_page(self, setup_function: str) -> Page:
        """Get the initial page state based on setup function."""
        self.clean_up_playwright()

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context()
        page = self.context.new_page()

        # Set up the page state based on the setup function
        page = setup_page_state(page, setup_function, application=self.application)
        return page

    @abstractmethod
    def run_test_case(self, test_case: TestCase) -> TestResult:
        """Run a single test case.

        Args:
            test_case: TestCase object containing test case data

        Returns:
            TestResult object with execution results
        """
        pass

    def restart_application(self, application: ApplicationEnum):
        """Restart the specified application."""
        pass

    def run_test_cases(self, filter_pattern: Optional[str] = None) -> TestResultDataset:
        """Run all test cases and return results."""
        test_cases = self.load_test_cases(filter_pattern)
        results = TestResultDataset()

        if not test_cases:
            print(f"No test cases found in {self.test_case_path}")
            return results

        print(f"Running {len(test_cases)} test cases...")
        print()

        # Main progress bar for all tests
        with tqdm(
            total=len(test_cases),
            desc="Test Suite Progress",
            unit="test",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            colour="blue",
        ) as pbar:
            for test_case in test_cases:
                self.restart_application(self.application)

                test_name = test_case.name
                pbar.set_description(f"Running: {test_name[:40]}")

                try:
                    result = self.run_test_case(test_case)
                    results.results.append(result)

                    if result.success:
                        tqdm.write(f"✓ Test passed: {test_name}")
                        pbar.set_postfix(status="✓", refresh=True)
                    else:
                        tqdm.write(
                            f"✗ Test failed: {test_name} (completed {result.current_step}/{result.total_step} steps)"
                        )
                        if result.error_message:
                            tqdm.write(f"  Error: {result.error_message}")
                        pbar.set_postfix(status="✗", refresh=True)

                except Exception as e:
                    tqdm.write(f"✗ Test crashed: {test_name} - {str(e)}")
                    result = TestResult(
                        test_name=test_name, success=False, error_message=str(e)
                    )
                    results.results.append(result)
                    pbar.set_postfix(status="✗", refresh=True)

                pbar.update(1)

        # Save results & get summary
        self.test_output_path.parent.mkdir(parents=True, exist_ok=True)
        results.save_results(str(self.test_output_path))
        results.print_summary()

        return results

    def __del__(self):
        self.clean_up_playwright()
