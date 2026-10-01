import logging
from abc import ABC, abstractmethod
from pathlib import Path

from baselines.test_model import TestCase, TestStep, TestContext, TestResult, StepResult
from baselines.config import MethodConfig
from baselines.environment import TaskEnvironment
from baselines.utils import iter_test_cases, iter_test_steps

MAX_ENVIRONMENT_ATTEMPTS = 3

logger = logging.getLogger(__name__)


class BaseTestRunner(ABC):
    """Abstract base class for all test runner implementations."""

    def __init__(self, config: MethodConfig):
        self.run_output_dir = config.run_output_dir
        self.application = config.application
        self.inject_bug = config.inject_bug


    def run_test_cases(self, test_cases: list[TestCase]) -> list[TestResult]:
        """
        Run a list of test cases.
        """
        test_results = []
        for test_case in iter_test_cases(test_cases):
            test_result = self._run_test_case(test_case)
            test_results.append(test_result)

        return test_results


    @abstractmethod
    def _setup_test_case(self, test_case: TestCase, test_output_dir: Path, cdp_url: str) -> TestContext:
        """
        This method is called **automatically before each test case** and should set up
        everything the agent needs, such as attaching to the browser and initializing
        page objects.

        The browser at `cdp_url` runs in the test case's environment and is already
        logged in via the test case's setup function, with the bug (if any) injected.
        Use `baselines.environment.connect_to_environment` to attach with Playwright.

        Returns:
            Any object representing the context (`test_context`) of the test case.
            It is automatically passed to `_run` when executing the test case.
            Users are free to extend from TestContext.
        """
        pass


    @abstractmethod
    def _step(self, step: TestStep, test_context: TestContext) -> StepResult: 
        """
        Execute a single test step in the test case.

        Args:
            step: The TestStep object describing the action and expected result to execute.
            test_context: The current test context containing data and resources shared across steps.

        Returns:
            StepResult: The outcome of executing this step, including status,
                    timestamps, and any captured tokens or logs.
        """
        pass


    @abstractmethod
    def _teardown_test_case(self, test_context: TestContext) -> None:
        """
        Perform cleanup after a test case has finished.

        This method is called **automatically after each test case** and should release
        any resources or reset the application state prepared in `_before_test_case`.
        """
        pass


    def _run_test_case(self, test_case: TestCase) -> TestResult:
        """
        Run a single test case step by step.

        Lifecycle. For each test case:
            1. Start a fresh environment with `_start_environment`.
            2. Setup test case with `_setup_test_case`.
            3. Execute each step with `_step`.
            4. Tear down the test case with `_teardown_test_case`, then the environment.
        """
        test_output_dir = self.run_output_dir / str(test_case.test_path.stem)
        test_output_dir.mkdir()

        environment = None
        test_context = None
        step_results = []

        try:
            environment, cdp_url = self._start_environment(test_case, test_output_dir)
            test_context = self._setup_test_case(test_case, test_output_dir, cdp_url)

            for test_step in iter_test_steps(test_case):
                step_result = self._step(test_step, test_context)
                step_results.append(step_result)

        except Exception as e:
            logger.error(
                "Error when running test case: %s", e, exc_info=True
            )

        finally:
            try:
                if test_context is not None:
                    self._teardown_test_case(test_context)
            except Exception as e:
                logger.error("Error when tearing down test case: %s", e, exc_info=True)
            finally:
                if environment is not None:
                    environment.stop()

            test_result = TestResult(test_case=test_case, steps=step_results)
            test_result_path = test_output_dir / "result.json"
            test_result_path.write_text(
                test_result.model_dump_json(indent=2),
                encoding="utf-8"
            )

            return test_result


    def _start_environment(self, test_case: TestCase, test_output_dir: Path) -> tuple[TaskEnvironment, str]:
        """Start the test case's environment, retrying on failure."""
        if self.inject_bug:
            logger.info(f"Injecting bug: {test_case.bug_path}")

        for attempt in range(1, MAX_ENVIRONMENT_ATTEMPTS + 1):
            environment = TaskEnvironment(
                application=self.application,
                setup_function=test_case.setup_function,
                bug_path=test_case.bug_path if self.inject_bug else None,
                log_path=test_output_dir / "environment.log",
            )
            try:
                return environment, environment.start()
            except Exception as e:
                environment.stop()
                if attempt == MAX_ENVIRONMENT_ATTEMPTS:
                    raise
                logger.error(f"Failed to start environment (attempt {attempt}/{MAX_ENVIRONMENT_ATTEMPTS}): {e}. Retrying")
