import asyncio
import re
import sys
import traceback
from pathlib import Path
from typing import Optional

from base_runner import BaseTestRunner, TestResult
from const import ApplicationEnum, TestCase
from playwright.async_api import async_playwright
from playwright.sync_api import Page
from tqdm import tqdm

sys.path.append(str(Path(__file__).parent.parent))  # baselines dir
sys.path.append(str(Path(__file__).parent.parent.parent))  # testcases dir
sys.path.append(str(Path(__file__).parent / "src"))  # src dir

from .src.VTAAS.data.testcase import TestCase as PinataTestCase
from .src.VTAAS.llm.llm_client import LLMProvider
from .src.VTAAS.orchestrator.orchestrator import Orchestrator
from .src.VTAAS.schemas.verdict import Status
from .src.VTAAS.workers.browser import Browser


class PinataTestRunner(BaseTestRunner):
    """Test runner implementation for Pinata agent."""

    def __init__(
        self,
        test_case_path: str,
        test_output_path: str,
        application: ApplicationEnum,
        model: Optional[str] = None,
        provider: str = "openai",
        headless: bool = False,
        save_screenshot: bool = True,
        tracer: bool = True,
        **kwargs,
    ):
        super().__init__(
            test_case_path, test_output_path, application, model=model, **kwargs
        )
        self.provider = provider
        self.headless = headless
        self.save_screenshot = save_screenshot
        self.tracer = tracer

    def get_llm_provider(self) -> LLMProvider:
        """Get the LLM provider enum based on string input."""
        provider_map = {
            "openai": LLMProvider.OPENAI,
            "anthropic": LLMProvider.ANTHROPIC,
            "google": LLMProvider.GOOGLE,
            "mistral": LLMProvider.MISTRAL,
            "openrouter": LLMProvider.OPENROUTER,
        }

        if self.provider not in provider_map:
            raise ValueError(f"Unknown provider: {self.provider}")

        return provider_map[self.provider]

    def convert_test_name_to_pinata_format(
        self, test_name: str, test_type: str = "P"
    ) -> str:
        """
        Convert test name from current format to Pinata's expected format.

        Args:
            test_name: Current format like "02::Book Create"
            test_type: Test type (P for Pass, F for Fail, etc.)

        Returns:
            Converted name like "TC-02-P :: Book Create"

        Raises:
            ValueError: If test_name doesn't match expected format
        """
        # Pattern to match current format: "02::Book Create"
        pattern = r"(\d+)::(.+)"
        match = re.match(pattern, test_name.strip())

        if not match:
            raise ValueError(
                f"Test name '{test_name}' doesn't match expected format 'ID::Description'"
            )

        test_id = match.group(1)
        description = match.group(2).strip()

        # Convert to Pinata format: "TC-02-P :: Book Create"
        return f"TC-{test_id}-{test_type} :: {description}"

    def convert_test_case_to_pinata_format(self, test_case: TestCase) -> PinataTestCase:
        """Convert standard test case format to Pinata's TestCase format."""
        actions = [action.action for action in test_case.actions]
        expected_results = [action.expectedResult for action in test_case.actions]

        # Convert test name to Pinata format
        converted_name = self.convert_test_name_to_pinata_format(test_case.name)

        return PinataTestCase(
            full_name=converted_name,
            actions=actions,
            expected_results=expected_results,
            url=test_case.url,
            failing_info=None,
            output_folder=str(self.test_output_path.parent),
        )

    async def run_test_case_async(self, test_case: TestCase) -> TestResult:
        """Async implementation of test case execution."""
        test_name = test_case.name
        setup_function = test_case.setup_function
        pinata_test_case = self.convert_test_case_to_pinata_format(test_case)

        result = TestResult(
            test_name=test_name, total_step=len(pinata_test_case.actions)
        )

        # Create nested progress bar for test steps
        with tqdm(
            total=len(pinata_test_case.actions),
            desc=f"  Steps for {test_name[:30]}",
            leave=False,
            unit="step",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            colour="green",
        ) as step_bar:
            try:
                sync_initial_page: Page = self.get_initial_page(
                    setup_function, application=self.application
                )

                async with async_playwright() as p:
                    # Create browser instance
                    step_bar.set_description("  Initializing browser")
                    browser = await Browser.create(
                        id=f"testcase #{pinata_test_case.id}",
                        headless=self.headless,
                        playwright=p,
                        save_screenshot=self.save_screenshot,
                        tracer=self.tracer,
                        trace_folder=str(self.test_output_path.parent),
                    )
                    initial_url = sync_initial_page.url

                    # OVERRIDEN implementation over browser.initialize() -> extracted out and override.
                    # This is to make sure all the setup and login is in place.
                    # Has to do this work-around because our setup and LaVague only support Playwright sync, but Pinata is Async
                    browser._context = await browser._browser.new_context(
                        bypass_csp=True,
                        storage_state=sync_initial_page.context.storage_state(),
                    )
                    browser._context.set_default_timeout(browser._params["timeout"])
                    if browser._params["tracer"]:
                        browser.logger.info(
                            f"Setting Playwright tracing ON: {browser._params['trace_folder']}"
                        )
                        await browser._context.tracing.start(
                            screenshots=True, snapshots=True
                        )
                    browser._page = await browser._context.new_page()
                    browser._page.on("load", lambda load: browser.load_js())
                    browser._page.on("framenavigated", lambda load: browser.load_js())

                    # Go to the setup URL.
                    await browser._page.goto(initial_url)

                    # Create orchestrator
                    llm_provider = self.get_llm_provider()
                    orchestrator = Orchestrator(
                        browser=browser,
                        llm_provider=llm_provider,
                        tracer=self.tracer,
                        output_folder=str(self.test_output_path.parent),
                    )

                    # Monkey-patch orchestrator to update progress bar
                    original_process = orchestrator.process_testcase

                    async def process_with_progress(test_case):
                        # We'll track progress based on step completions
                        result = await original_process(test_case)
                        # Update progress based on completed steps
                        if hasattr(result, "step_index"):
                            step_bar.n = result.step_index
                            step_bar.refresh()
                        return result

                    step_bar.set_description(f"  Executing {test_name[:30]}")

                    # Process test case
                    execution_result = await process_with_progress(pinata_test_case)

                    # Update result based on execution
                    if execution_result.status == Status.PASS:
                        result.success = True
                        result.current_step = result.total_step
                        step_bar.n = result.total_step
                        step_bar.refresh()
                        orchestrator.logger.info("Test PASSED!")
                    else:
                        result.success = False
                        result.current_step = execution_result.step_index
                        step_bar.n = execution_result.step_index
                        step_bar.refresh()
                        result.error_message = (
                            f"Failed at step {execution_result.step_index}"
                        )
                        orchestrator.logger.info(
                            f"Test FAILED at step {execution_result.step_index}!"
                        )

                    # Store traces if available
                    if hasattr(execution_result, "traces"):
                        result.traces = execution_result.traces

            except Exception as e:
                result.error_message = f"Test execution error: {str(e)}"
                result.success = False
                step_bar.n = result.current_step
                step_bar.refresh()
                traceback.print_exc()

        return result

    def run_test_case(self, test_case: TestCase) -> TestResult:
        """Run a single test case using Pinata agent."""
        # Run the async method in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.run_test_case_async(test_case))
        finally:
            loop.close()
