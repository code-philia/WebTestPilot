import sys
import time
import subprocess
from pathlib import Path
from typing import Optional

from const import ApplicationEnum, TestCase
from playwright.sync_api import Page, sync_playwright
from selenium.common.exceptions import WebDriverException
from tqdm import tqdm

# Add project directory
PROJECT_DIR = Path(__file__).parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.append(str(PROJECT_DIR))

import baselines.naviqate.method.utils.logger as logging
import baselines.naviqate.method.utils.utils as utils
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
            test_case_path, test_output_path, application, model=model, **kwargs
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

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.connect_over_cdp("http://localhost:9222")
        self.context = self.browser.contexts[0] if self.browser.contexts else self.browser.new_context()
        page = self.context.new_page()

        # Set up the page state based on the setup function
        page = setup_page_state(page, setup_function, application=self.application)
        return page

    def run_test_case(self, test_case: TestCase) -> TestResult:
        """Run a single test case using Naviqate crawler."""
        actions = test_case.actions
        test_name = test_case.name
        setup_function = test_case.setup_function
        url = test_case.url

        result = TestResult(test_name=test_name, total_step=len(actions))

        # Get initial page setup if needed
        if setup_function:
            # Restart browser
            script_dir = Path(__file__).parent.resolve()
            remote_browser_script = script_dir / "browser.sh"
            subprocess.run(["bash", str(remote_browser_script)], check=True)

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
            # Process each action
            for i, action_data in enumerate(actions):
                action = action_data.action
                website = self.get_website_from_url(url) if url else ""

                # Update progress bar description
                action_bar.set_description(f"  Action {i + 1}: {action[:40]}")

                self.logger.info("•" * 70)
                self.logger.info(f"ACTION {i + 1}/{len(actions)}: {action}")
                self.logger.info(f"WEBSITE: {website}, MAX_STEPS: {self.max_steps}")

                start_time = time.time()

                try:
                    # Create crawler for this action
                    crawler = WebCrawler(
                        website,
                        action,
                        abstracted=self.abstracted,
                        headless=self.headless,
                        output_dir=self.output_dir,
                    )

                    # Execute the action
                    crawler.loop(MAX_STEPS=self.max_steps)

                    # If we get here, the action succeeded
                    result.current_step += 1
                    result.traces.append(
                        {
                            "action": action,
                            "website": website,
                            "duration": time.time() - start_time,
                        }
                    )

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
                    action_bar.set_postfix(status="✗", refresh=True)
                    break

                end_time = time.time()
                self.logger.info(
                    f"DURATION: {utils.calculate_time_interval(start_time, end_time)}"
                )

        # Mark as success if all steps completed
        result.success = result.current_step == result.total_step

        return result
