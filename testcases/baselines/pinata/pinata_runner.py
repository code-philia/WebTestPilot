import asyncio
import sys
from pathlib import Path
from typing import Dict

from base_runner import BaseTestRunner, TestResult
from const import ApplicationEnum
from playwright.async_api import Page as AsyncPage
from playwright.async_api import async_playwright
from tqdm import tqdm
from utils import setup_page_state

from .src.VTAAS.data.testcase import TestCase
from .src.VTAAS.llm.llm_client import LLMProvider
from .src.VTAAS.orchestrator.orchestrator import Orchestrator
from .src.VTAAS.schemas.verdict import Status
from .src.VTAAS.workers.browser import Browser

sys.path.append(str(Path(__file__).parent.parent))  # baselines dir
sys.path.append(str(Path(__file__).parent.parent.parent))  # testcases dir


class PinataTestRunner(BaseTestRunner):
    """Test runner implementation for Pinata agent."""

    def __init__(
        self,
        test_case_path: str,
        test_output_path: str,
        application: ApplicationEnum,
        provider: str = "openai",
        headless: bool = False,
        save_screenshot: bool = True,
        tracer: bool = True,
        **kwargs,
    ):
        super().__init__(test_case_path, test_output_path, application, **kwargs)
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

    def get_initial_page(self, setup_function: str) -> AsyncPage:
        """Get the initial page state based on setup function.

        This method converts a sync page to async page for Pinata compatibility.
        """
        # This will be called from async context
        # We'll handle the actual page setup in run_test_case_async
        return setup_function  # Return setup function to be used later

    def convert_test_case_to_pinata_format(self, test_case: Dict) -> TestCase:
        """Convert standard test case format to Pinata's TestCase format."""
        actions = [action["action"] for action in test_case.get("actions", [])]
        expected_results = [
            action.get("expectedResult", "") for action in test_case.get("actions", [])
        ]

        return TestCase(
            full_name=test_case.get("name", "Unnamed"),
            actions=actions,
            expected_results=expected_results,
            url=test_case.get("url", ""),
            failing_info=None,
            output_folder=str(self.test_output_path.parent),
        )

    async def run_test_case_async(self, test_case: Dict) -> TestResult:
        """Async implementation of test case execution."""
        test_name = test_case.get("name", "Unnamed")
        setup_function = test_case.get("setup_function", "")
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

                    browser._page = setup_page_state(
                        browser._page, setup_function, application=self.application
                    )

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

        return result

    def run_test_case(self, test_case: Dict) -> TestResult:
        """Run a single test case using Pinata agent."""
        # Run the async method in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.run_test_case_async(test_case))
        finally:
            loop.close()
