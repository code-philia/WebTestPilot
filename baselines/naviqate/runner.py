import sys
import time
import subprocess
from pathlib import Path
from typing import Optional

from tqdm import tqdm
from const import ApplicationEnum, MethodEnum, ModelEnum, TestCase
from playwright.sync_api import Page, sync_playwright
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Add project directory
PROJECT_DIR = Path(__file__).parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.append(str(PROJECT_DIR))

import baselines.naviqate.method.utils.logger as logging
from baselines.naviqate.method.crawler.crawler import WebCrawler
from baselines.base_runner import BaseTestRunner, TestResult
from baselines.utils import setup_page_state


class NaviqateTestRunner(BaseTestRunner):
    """Test runner implementation for Naviqate agent."""

    def __init__(
        self,
        test_case_path: str,
        test_output_path: str,
        application: ApplicationEnum,
        model: Optional[str] = None,
        headless: bool = False,
        max_steps: int = 1,
        abstracted: bool = False,
        **kwargs,
    ):
        super().__init__(
            test_case_path,
            test_output_path,
            application,
            model=model,
            method=MethodEnum.naviqate,
            **kwargs,
        )
        self.headless = headless
        self.max_steps = max_steps
        self.abstracted = abstracted
        self.output_dir = str(self.test_output_path.parent / "naviqate_output")
        self.logger = logging.get_logger()

    def get_website_from_url(self, url: str) -> str:
        """Extract website domain from URL."""
        if not url:
            return ""

        # Remove protocol
        if "://" in url:
            url = url.split("://")[1]

        # Get domain
        domain = url.split("/")[0]

        # Add .com if no TLD present
        if "." not in domain:
            domain += ".com"

        return domain

    def get_initial_page(self, setup_function: str) -> Page:
        """Get the initial page state based on setup function."""
        self.clean_up_playwright()

        if self.playwright is not None:
            del self.playwright
            self.playwright = None

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.connect_over_cdp(
            "http://localhost:9222"
        )
        self.context = (
            self.browser.contexts[0]
            if self.browser.contexts
            else self.browser.new_context()
        )
        # page = self.context.new_page()
        page = self.context.pages[0]

        # Set up the page state based on the setup function
        self.logger.info("Setting up page state")
        page = setup_page_state(page, setup_function, application=self.application)
        return page

    async def run_test_case(self, test_case: TestCase) -> TestResult:
        """Run a single test case using Naviqate crawler."""
        actions = test_case.actions
        test_name = test_case.name
        setup_function = test_case.setup_function
        url = test_case.url

        result = TestResult(test_name=test_name, total_step=len(actions))

        # Restart browser
        script_dir = Path(__file__).parent.resolve()
        remote_browser_script = script_dir / "browser.sh"
        subprocess.run(["bash", str(remote_browser_script)], check=True)

        if setup_function is not None:
            # Setup initial page on remote browser
            self.get_initial_page(setup_function)

        # Create nested progress bar for actions
        with tqdm(
            total=len(actions),
            desc=f"  Actions for {test_name[:30]}",
            leave=False,
            unit="action",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            colour="green",
        ) as action_bar:
            website = self.get_website_from_url(url) if url else ""

            chrome_options = Options()
            chrome_options.debugger_address = "localhost:9222"
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=chrome_options
            )

            # Create crawler for this action
            crawler = WebCrawler(
                driver,
                website,
                abstracted=self.abstracted,
                headless=self.headless,
                output_dir=self.output_dir,
                model=ModelEnum.gpt4_1,
            )

            # Process each action
            start_time = time.perf_counter()
            for i, action_data in enumerate(actions):
                action = action_data.action
                crawler.task = action
                crawler.prev_context = ""

                # Update progress bar description
                action_bar.set_description(f"  Action {i + 1}: {action[:40]}")

                self.logger.info("•" * 70)
                self.logger.info(f"ACTION {i + 1}/{len(actions)}: {action}")
                self.logger.info(f"WEBSITE: {website}, MAX_STEPS: {self.max_steps}")

                try:
                    # Execute the action
                    crawler.loop(MAX_STEPS=self.max_steps)

                    # If we get here, the action succeeded
                    result.current_step += 1

                    trace_data = crawler.get_last_action_trace()
                    result.traces.append(trace_data)

                    # Update progress bar
                    action_bar.update(1)
                    action_bar.set_postfix(status="✓", refresh=True)

                except WebDriverException as e:
                    result.error_message = f"WebDriver error at step {i + 1}: {str(e)}"
                    self.logger.error(
                        f"An error occurred: {e} - Stopping at Task {i + 1}"
                    )
                    action_bar.set_postfix(status="✗", refresh=True)
                    break
                except Exception as e:
                    result.error_message = f"Error at step {i + 1}: {str(e)}"
                    self.logger.error(
                        f"Unexpected error: {e} - Stopping at Task {i + 1}"
                    )
                    import traceback

                    self.logger.error(traceback.format_exc())
                    action_bar.set_postfix(status="✗", refresh=True)
                    break

            # Run metadata
            end_time = time.perf_counter()
            result.runtime = end_time - start_time
            result.token_count = crawler.get_token_usage()

        # Mark as success if all steps completed
        result.success = result.current_step == result.total_step

        return result
