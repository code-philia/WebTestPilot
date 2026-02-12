import time
import logging
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import psutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from playwright.sync_api import sync_playwright, Playwright, Browser, Page

from baselines.test_model import TestCase, TestStep, TestContext, StepResult
from baselines.config import NaviqateConfig
from baselines.naviqate.method.crawler.crawler import WebCrawler
from baselines.base_runner import BaseTestRunner
from baselines.test_setup_functions import setup_page_state

logger = logging.getLogger(__name__)


class NaviqateTestContext(TestContext):
    crawler: WebCrawler
    page: Page
    browser: Browser
    playwright: Playwright
    browser_port: int
    browser_process: psutil.Process


class NaviqateTestRunner(BaseTestRunner):

    def __init__(self, config: NaviqateConfig):
        super().__init__(config)
        self.model = config.model
        self.max_steps = config.max_steps
        self.abstracted = config.abstracted
        self.browser_script_path = config.browser_script_path


    def _setup_test_case(self, test_case: TestCase, test_output_dir: Path) -> NaviqateTestContext:
        # Launch remote browser
        browser_subprocess = subprocess.run(["bash", str(self.browser_script_path)], capture_output=True, check=True)
        output = browser_subprocess.stdout.decode()
        browser_pid = next(
            (int(line.split(":", 1)[1].strip()) 
            for line in output.splitlines()
            if line.strip().startswith("Chrome PID:")),
            None
        )

        browser_port = next(
            (urlparse(line.split(":", 1)[1].strip()).port 
            for line in output.splitlines()
            if line.strip().startswith("DevTools endpoint:")),
            None
        )

        if browser_port is None:
            raise RuntimeError("Failed to get DevTools endpoint from Chrome output")
        if browser_pid is None or not psutil.pid_exists(browser_pid):
            raise RuntimeError(f"Chrome process with PID {browser_pid} is not running")
        
        # Use Playwright to initialize application state
        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp(f"http://localhost:{browser_port}")
        page = browser.new_page()
        page = setup_page_state(self.application, page, test_case.setup_function)

        # Use Selenium as the method's main driver
        chrome_options = Options()
        chrome_options.debugger_address = f"localhost:{browser_port}"
        chrome_service = Service(ChromeDriverManager().install())
        chrome_driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        crawler = WebCrawler(
            chrome_driver,
            website=self.application.value,
            output_dir=test_output_dir,
            model=self.model,
        )
    
        return NaviqateTestContext(
            crawler=crawler,
            page=page,
            browser=browser,
            playwright=playwright,
            browser_port=browser_port,
            browser_process=psutil.Process(browser_pid),
        )


    def _inject_bug(self, bug_script: str, test_context: NaviqateTestContext) -> None:
        test_context.page.add_init_script(bug_script)
        test_context.page.evaluate(bug_script)


    def _teardown_test_case(self, test_context: NaviqateTestContext) -> None:
        for item in test_context.model_dump().values():
            try:
                if isinstance(item, WebCrawler): item.quit()
                elif isinstance(item, Page): item.close()
                elif isinstance(item, Browser): item.close()
                elif isinstance(item, Playwright): item.stop()
                elif isinstance(item, psutil.Process): item.kill()
            except Exception as e:
                logger.warning("Failed to close resource %s: %s", type(item).__name__, e)


    def _step(self, step: TestStep, test_context: NaviqateTestContext) -> StepResult:
        crawler = test_context.crawler
        crawler.task = step.action
        crawler.prev_context = ""

        # Execute
        start_token = crawler.get_token_usage()
        start_time = time.perf_counter()
        crawler.loop(MAX_STEPS=self.max_steps)
        end_time = time.perf_counter()
        end_token = crawler.get_token_usage()
        tokens = end_token - start_token

        try:
            is_action_correct = step.ground_truth(test_context.page)
        except:
            logger.warn("Step ground truth check failed, defaulting to False")
            is_action_correct = False

        return StepResult(
            step=step,
            is_action_correct=is_action_correct,
            is_bug_reported=False,
            start_time=start_time,
            end_time=end_time,
            tokens=tokens
        )