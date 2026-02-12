import subprocess
import logging
from abc import ABC, abstractmethod
from pathlib import Path

from baselines.test_model import TestCase, TestStep, TestContext, TestResult, StepResult
from baselines.config import MethodConfig
from baselines.bug_injector import prepare_bug_script 
from baselines.utils import iter_test_cases, iter_test_steps

PROJECT_DIR = Path(__file__).parent.parent
WEBAPPS_DIR = PROJECT_DIR / "webapps"

logger = logging.getLogger(__name__)


class BaseTestRunner(ABC):
    """Abstract base class for all test runner implementations."""

    def __init__(self, config: MethodConfig):
        self.run_output_dir = config.run_output_dir
        self.application = config.application
        self.headless = config.headless
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
    def _setup_test_case(self, test_case: TestCase, test_output_dir: Path) -> TestContext:
        """
        This method is called **automatically before each test case** and should set up
        everything required for the test to run correctly, such as logging in, navigating
        to the starting page, or initializing page objects.

        Returns:
            Any object representing the context (`test_context`) of the test case.
            It is automatically passed to `_run` when executing the test case.
            Users are free to extend from TestContext.
        """
        pass


    @abstractmethod
    def _inject_bug(self, bug_script: str, test_context: TestContext) -> None:
        """
        This method is called **automatically after setup test case and before the test
        case is executed**, and is responsible for injecting a bug or modification into
        the system under test.

        Args:
            bug_script: A JavaScript snippet representing the bug to inject into the webpage.
            test_context: The current test context containing data and resources shared across steps.
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
            1. Restart the application with `_restart_app`.
            2. Setup test case with `_setup_test_case`.
            3. Inject bug into system under test with `_inject_bug`.
            4. Execute each step with `_step`.
            5. Tear down the test case with `_teardown_test_case`.
        """

        def _restart_app():
            app_name = self.application.value
            cmd = ["bash", str(WEBAPPS_DIR / "start_app.sh"), app_name]

            while True:
                logger.info(f"Restarting webapp: {app_name}")
                result = subprocess.run(
                    cmd,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                if result.returncode == 0:
                    logger.info(f"Webapp restarted successfully")
                    break
                else:
                    logger.error(
                        f"Failed to start webapp '{app_name}' (returncode={result.returncode}).\n"
                        f"STDOUT:\n{result.stdout}\n"
                        f"STDERR:\n{result.stderr}\n"
                        f"Retrying"
                    )

        def _create_test_output_dir():
            test_output_dir = self.run_output_dir / str(test_case.test_path.stem)
            test_output_dir.mkdir()
            return test_output_dir

        
        try:
            _restart_app()
            test_output_dir = _create_test_output_dir()
            test_context = self._setup_test_case(test_case, test_output_dir)

            if self.inject_bug:
                bug_path = test_case.bug_path
                logger.info(f"Injecting bug: {bug_path}")
                bug_script = prepare_bug_script(bug_path)
                self._inject_bug(bug_script, test_context)

            step_results = []
            for test_step in iter_test_steps(test_case):
                step_result = self._step(test_step, test_context)
                step_results.append(step_result)

        except Exception as e:
            logger.error(
                "Error when running test case: %s", e, exc_info=True
            )

        finally:
            self._teardown_test_case(test_context)
            
            test_result = TestResult(
                test_case=test_case, 
                steps=step_results if step_results else []
            )
            test_result_path = test_output_dir / "result.json"
            test_result_path.write_text(
                test_result.model_dump_json(indent=2),
                encoding="utf-8"
            )

            return test_result