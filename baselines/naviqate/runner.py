import json
import time
import logging
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from playwright.sync_api import sync_playwright, Playwright, Browser, Page

from baselines.test_model import TestCase, TestStep, TestContext, StepResult
from baselines.config import NaviqateConfig
from baselines.naviqate.method.crawler.crawler import WebCrawler
from baselines.base_runner import BaseTestRunner
from baselines.environment import connect_to_environment

logger = logging.getLogger(__name__)


class NaviqateTestContext(TestContext):
    crawler: WebCrawler
    page: Page
    browser: Browser
    playwright: Playwright


class NaviqateTestRunner(BaseTestRunner):

    def __init__(self, config: NaviqateConfig):
        super().__init__(config)
        self.model = config.model
        self.max_steps = config.max_steps
        self.abstracted = config.abstracted


    def _setup_test_case(self, test_case: TestCase, test_output_dir: Path, cdp_url: str) -> NaviqateTestContext:
        # Use Playwright to check ground truth on the environment's set-up page
        playwright = sync_playwright().start()
        browser, _, page = connect_to_environment(playwright, cdp_url)

        # ChromeDriver must match the environment's Chromium, not a locally installed Chrome
        with urllib.request.urlopen(f"{cdp_url}/json/version") as response:
            browser_version = json.load(response)["Browser"].split("/", 1)[1]

        # Use Selenium as the method's main driver
        chrome_options = Options()
        chrome_options.debugger_address = urlparse(cdp_url).netloc
        chrome_service = Service(ChromeDriverManager(driver_version=browser_version).install())
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
        )


    def _teardown_test_case(self, test_context: NaviqateTestContext) -> None:
        for item in test_context.model_dump().values():
            try:
                if isinstance(item, WebCrawler): item.quit()
                elif isinstance(item, Browser): item.close()
                elif isinstance(item, Playwright): item.stop()
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