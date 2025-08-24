import sys
import json
import os
import re
import subprocess
import time
import traceback
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable
from tqdm import tqdm
from playwright.sync_api import Page, sync_playwright
from playwright.sync_api._generated import Browser, BrowserContext, Playwright

PROJECT_DIR = Path(__file__).parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.append(str(PROJECT_DIR))

from baselines.const import ApplicationEnum, MethodEnum, ModelEnum, TestCase
from baselines.utils import setup_page_state


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
    has_bug: bool = False
    bug_name: Optional[str] = None

    @property
    def correct_trace_percentage(self) -> float:
        return self.current_step / self.total_step if self.total_step > 0 else 0.0

    @property
    def runtime_per_step(self) -> float:
        # If the step fails -> it's not counted, so we need to increase by
        try:
            return self.runtime / min(self.current_step + 1, self.total_step)
        except:
            return 0

    def __str__(self):
        status = "✓" if self.success else "✗"
        status_color = "\033[92m" if self.success else "\033[91m"  # Green or Red
        reset_color = "\033[0m"

        return (
            f"{status_color}{status}{reset_color} {self.test_name:<45}: "
            f"Steps={self.current_step:>2}/{self.total_step:<2} "
            f"({self.correct_trace_percentage})"
        )


@dataclass
class TestResultDataset:
    results: list[TestResult] = field(default_factory=list)

    @property
    def correct_trace_percentage(self) -> float:
        return (
            sum(result.correct_trace_percentage for result in self.results)
            / len(self.results)
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

    @property
    def buggy_results(self) -> list[TestResult]:
        return [r for r in self.results if r.has_bug]

    @property
    def normal_results(self) -> list[TestResult]:
        return [r for r in self.results if not r.has_bug]

    @property
    def bug_detection_rate(self) -> float:
        """Percentage of buggy tests that failed (detected the bug)."""
        buggy = self.buggy_results
        if not buggy:
            return 0.0
        return sum(1 for r in buggy if not r.success) / len(buggy)

    def save_results(self, file_path: str):
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            results_data = []
            for result in self.results:
                result_dict = result.__dict__.copy()
                result_dict["correct_trace_percentage"] = (
                    result.correct_trace_percentage
                )
                result_dict["runtime_per_step"] = result.runtime_per_step
                results_data.append(result_dict)

            # Add summary statistics
            summary = {
                "total_runs": len(self.results),
                "success_rate": self.success_rate,
                "correct_trace_percentage": self.correct_trace_percentage,
                "normal_tests": len(self.normal_results),
                "buggy_tests": len(self.buggy_results),
                "bug_detection_rate": self.bug_detection_rate,
            }

            output = {"summary": summary, "results": results_data}
            json.dump(output, f, indent=4)

        print(f"Results saved to {file_path}")

    def print_summary(self):
        """Print a summary of test results."""
        print()
        print("=" * 80)
        print("TEST RESULT SUMMARY")
        print("=" * 80)

        # Separate results by bug status
        normal_results = self.normal_results
        buggy_results = self.buggy_results

        # Print normal test results
        if normal_results:
            print("\nNormal Test Runs:")
            for result in sorted(normal_results, key=lambda r: r.test_name):
                print(result)

        # Print buggy test results
        if buggy_results:
            print("\nBuggy Test Runs (🐛):")
            for result in sorted(buggy_results, key=lambda r: r.test_name):
                print(result)

        print("=" * 80)

        # Overall statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests

        print(f"Total Runs: {total_tests}")
        print(
            f"\033[92mPassed: {passed_tests}\033[0m | \033[91mFailed: {failed_tests}\033[0m"
        )
        print(f"Overall Success Rate: {self.success_rate:.1%}")
        print(f"Overall Correct Trace: {self.correct_trace_percentage:.1%}")

        # Bug-specific statistics
        if buggy_results:
            print("\n" + "-" * 40)
            print("BUG INJECTION STATISTICS:")
            print("-" * 40)

            bugs_detected = sum(1 for r in buggy_results if not r.success)
            bugs_missed = len(buggy_results) - bugs_detected

            print(f"Total Bugs Injected: {len(buggy_results)}")
            print(
                f"\033[92mBugs Detected: {bugs_detected}\033[0m | "
                f"\033[91mBugs Missed: {bugs_missed}\033[0m"
            )
            print(f"Bug Detection Rate: {self.bug_detection_rate:.1%}")

            # Normal vs Buggy success rates
            if normal_results:
                normal_success_rate = sum(1 for r in normal_results if r.success) / len(
                    normal_results
                )
                buggy_success_rate = sum(1 for r in buggy_results if r.success) / len(
                    buggy_results
                )
                print(f"\nNormal Test Success Rate: {normal_success_rate:.1%}")
                print(f"Buggy Test Success Rate: {buggy_success_rate:.1%}")

        print("=" * 80)


class BaseTestRunner(ABC):
    """Abstract base class for all test runner implementations."""

    # Application URL mapping
    APPLICATION_URLS = {
        ApplicationEnum.indico: "http://localhost:8080",
        ApplicationEnum.bookstack: "http://localhost:8081/",
        ApplicationEnum.invoiceninja: "http://localhost:8082",
        ApplicationEnum.prestashop: "http://localhost:8083",
    }

    def __init__(
        self,
        test_case_path: str,
        test_output_path: str,
        application: ApplicationEnum,
        model: Optional[ModelEnum] = None,
        headless: bool = False,
        method: Optional[MethodEnum] = None,
        rerun_numbers: Optional[list[int]] = None,
        **kwargs,
    ):
        self.test_case_path = Path(test_case_path)
        self.test_output_path = Path(test_output_path)
        self.application = application
        self.model = model
        self.config = kwargs
        self.headless = headless
        self.method = method
        self.rerun_numbers = rerun_numbers

        # For configuring Playwright, to load initial page.
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

        self.bug_mapping = self._load_bug_mapping()
        self.checkpoint_folder: Optional[Path] = None

    @staticmethod
    def extract_test_number(test_name: str) -> Optional[int]:
        """From: 02::Book Create -> 2"""
        match = re.match(r"(\d+)::", test_name)
        if match:
            return int(match.group(1))
        return None

    def load_test_cases(self, filter_pattern: Optional[str] = None) -> list[TestCase]:
        """Load test cases from test case directory."""
        test_cases: list[TestCase] = []

        if not self.test_case_path.exists():
            print(f"Test case path does not exist: {self.test_case_path}")
            return test_cases

        for file_path in sorted(
            self.test_case_path.glob("*.json"), key=lambda p: p.stem
        ):
            if filter_pattern and filter_pattern not in file_path.stem:
                continue

            try:
                with open(file_path, "r") as f:
                    test_case_data = json.load(f)
                    test_case = TestCase.from_dict(test_case_data)

                    # Re-run subset of tests
                    if self.rerun_numbers:
                        test_number = self.extract_test_number(test_case.name)
                        if not test_number or test_number not in self.rerun_numbers:
                            continue

                    test_cases.append(test_case)
            except json.JSONDecodeError as e:
                print(f"Error loading {file_path}: {e}")
                raise e

        return test_cases

    def clean_up_playwright(self):
        for item in [self.context, self.browser, self.playwright]:
            try:
                if isinstance(item, Playwright):
                    item.stop()
                elif isinstance(item, Browser):
                    item.close()
                elif isinstance(item, BrowserContext):
                    item.close()
            except:
                pass
            finally:
                del item

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

    def run_single_test(
        self,
        test_case: TestCase,
        pbar: tqdm,
        is_buggy: bool = False,
        patch_file: Optional[str] = None,
    ) -> TestResult:
        """Execute a test case with proper error handling and status reporting.

        Args:
            test_case: TestCase to execute
            pbar: Progress bar for status updates
            is_buggy: Whether this is a buggy test run
            patch_file: Optional patch file for bug injection

        Returns:
            TestResult with execution results
        """
        test_name = test_case.name
        display_name = f"{test_name} - Bug" if is_buggy else test_name

        # Update progress bar description
        if is_buggy:
            pbar.set_description(f"🐛 {test_name[:35]}")
        else:
            pbar.set_description(test_name[:40])

        # Restart application with or without bug
        self.restart_application(self.application, patch_file)
        try:
            result = self.run_test_case(test_case)

            if is_buggy:
                result.test_name = display_name
                result.has_bug = True
                result.bug_name = patch_file

            status = (
                "✓"
                if result.success
                else f"✗({result.current_step}/{result.total_step})"
            )
            tqdm.write(f"{status} {display_name}")
            return result

        except Exception as e:
            result = TestResult(
                test_name=display_name,
                success=False,
                error_message=str(e),
                has_bug=is_buggy,
                bug_name=patch_file if is_buggy else None,
            )
            tqdm.write(f"✗ {display_name}: {str(e)[:50]}")
            traceback.print_exc()
            return result

    def _load_bug_mapping(self) -> dict[str, str]:
        """Load test case to bug mapping from JSON file."""
        webapps_dir = Path(__file__).parent.parent / "webapps"
        mapping_file = webapps_dir / self.application / "testcase_to_bug.json"

        if mapping_file.exists():
            try:
                with open(mapping_file, "r") as f:
                    bug_mapping = json.load(f)

                    # Filter bug mapping by rerun numbers if specified
                    if self.rerun_numbers:
                        filtered_mapping = {}
                        for test_name, bug_file in bug_mapping.items():
                            test_number = self.extract_test_number(test_name)
                            if test_number and test_number in self.rerun_numbers:
                                filtered_mapping[test_name] = bug_file
                        return filtered_mapping

                    return bug_mapping
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to load bug mapping file: {e}")
                return {}
        return {}

    def wait_for_application(self, application: ApplicationEnum, max_wait: int = 240):
        """Wait for application to be accessible via HTTP."""

        READY_CHECKS: dict[str, Callable[[str], bool]] = {
            "indico": lambda text: "All events" in text,
            "invoiceninja": lambda text: "Invoice Ninja" in text,
            "prestashop": lambda text: "Ecommerce software by PrestaShop" in text,
            "bookstack": lambda text: "BookStack" in text,  # adjust as needed
        }

        url = self.APPLICATION_URLS.get(application)
        assert url, f"URL for {application} not found"

        print(f"Waiting for {application} to be ready at {url}...")
        start_time = time.time()
        check_func: Callable[[str], bool] = READY_CHECKS.get(application, lambda _: True)

        while time.time() - start_time < max_wait:
            try:
                response = urllib.request.urlopen(url, timeout=5)
                text = response.read().decode("utf-8", errors="ignore")

                if check_func(text):
                    print(f"✓ {application} is ready")
                    return
            except Exception as e:
                print(f"{application} is giving error: {e}")

            time.sleep(15)

        print(f"Warning: {application} may not be fully ready after {max_wait}s")

    def restart_application(
        self, application: ApplicationEnum, patch_file: Optional[str] = None
    ):
        """Restart the specified application with optional bug injection."""
        WEBAPPS_DIR = Path(__file__).parent.parent / "webapps"

        # Stop the application
        subprocess.run(
            ["bash", str(WEBAPPS_DIR / "stop_app.sh"), application],
            text=True,
        )

        # Start with optional bug injection
        cmd = ["bash", str(WEBAPPS_DIR / "start_app.sh"), application]
        if patch_file:
            cmd.append(patch_file)

        _ = subprocess.run(cmd, text=True, check=True)

        # Wait for application to be accessible
        self.wait_for_application(application)

    def run_all_test_cases(
        self, filter_pattern: Optional[str] = None
    ) -> TestResultDataset:
        """Run all test cases and return results."""
        test_cases = self.load_test_cases(filter_pattern)
        results = TestResultDataset()

        if not test_cases:
            print(f"No test cases found in {self.test_case_path}")
            return results

        # Create checkpoint folder with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.checkpoint_folder = (
            self.test_output_path.parent / f"checkpoint_{timestamp}"
        )
        self.checkpoint_folder.mkdir(parents=True, exist_ok=True)

        checkpoint_file = self.checkpoint_folder / f"{self.test_output_path.name}"
        print(f"Checkpoint folder: {self.checkpoint_folder}")

        disable_buggy_tests = self.method in [MethodEnum.naviqate, MethodEnum.lavague]

        # Calculate total runs
        if disable_buggy_tests:
            bug_count = 0
            total_runs = len(test_cases)
            print(
                f"Running {len(test_cases)} normal test(s) (buggy tests disabled for {self.method.value if self.method else 'unknown'})...\n"
            )
        else:
            bug_count = sum(1 for tc in test_cases if tc.name in self.bug_mapping)
            total_runs = len(test_cases) + bug_count
            print(
                f"Running ({bug_count} 🐛 buggy +  {len(test_cases)} normal = {total_runs} runs)...\n"
            )

        # Main progress bar
        with tqdm(
            total=total_runs,
            desc="Test Suite Progress",
            unit="run",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            colour="blue",
        ) as pbar:
            for test_case in test_cases:
                # Run buggy test if mapping exists and method supports it
                if test_case.name in self.bug_mapping and not disable_buggy_tests:
                    result = self.run_single_test(
                        test_case,
                        pbar,
                        is_buggy=True,
                        patch_file=self.bug_mapping[test_case.name],
                    )
                    results.results.append(result)
                    pbar.update(1)

                    # Save checkpoint
                    results.save_results(str(checkpoint_file))

                # Run normal test
                result = self.run_single_test(test_case, pbar)
                results.results.append(result)
                pbar.update(1)

                # Save checkpoint after each test
                results.save_results(str(checkpoint_file))

        # Final results
        self.test_output_path.parent.mkdir(parents=True, exist_ok=True)
        results.save_results(str(self.test_output_path))

        # Final checkpoint
        results.save_results(str(checkpoint_file))
        print(f"Checkpoints saved in: {self.checkpoint_folder}")

        results.print_summary()

        return results

    def __del__(self):
        self.clean_up_playwright()
