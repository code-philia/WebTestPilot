import os
import re
import time
import logging
from pathlib import Path

# Disable telemetry
os.environ["LAVAGUE_TELEMETRY"] = "NONE"

from lavague.contexts.openai import OpenaiContext
from lavague.core import ActionEngine, WorldModel
from lavague.core.agents import WebAgent
from lavague.core.token_counter import TokenCounter
from lavague.drivers.playwright import PlaywrightDriver
from playwright.sync_api import Page, Browser, BrowserContext, Playwright, sync_playwright

from baselines.base_runner import BaseTestRunner
from baselines.test_model import TestCase, TestContext, TestStep, StepResult
from baselines.const import Viewport
from baselines.config import LavagueConfig
from baselines.test_setup_functions import setup_page_state

from lavague.core.agents import logging_print as lp1
from lavague.core.navigation import logging_print as lp2
from lavague.core.utilities.telemetry import logging_print as lp3


for lp in [lp1, lp2, lp3]:
    lp.handlers = []
    lp.propagate = True

logger = logging.getLogger(__name__)


class LaVagueTestContext(TestContext):
    test_output_dir: Path
    agent: WebAgent
    page: Page
    browser_context: BrowserContext
    browser: Browser
    playwright: Playwright


class LavagueTestRunner(BaseTestRunner):

    def __init__(self, config: LavagueConfig):
        super().__init__(config)
        self.model = config.model

    
    def _setup_test_case(self, test_case: TestCase, test_output_dir: Path) -> LaVagueTestContext:
        # Get initial page with setup
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=self.headless)
        browser_context = browser.new_context(viewport={"width": Viewport.WIDTH, "height": Viewport.HEIGHT})
        browser_context.tracing.start(screenshots=True, snapshots=True)
        page = browser_context.new_page()
        page = setup_page_state(self.application, page, test_case.setup_function)

        # Create PlaywrightDriver with the setup page
        def _get_page():
            return page
        
        playwright_driver = PlaywrightDriver(get_sync_playwright_page=_get_page)
        playwright_driver.page = page

        # Create LaVague components
        base_url = os.getenv("OPENAI_BASE_URL")
        api_key = os.getenv("OPENAI_API_KEY")
        token_counter = TokenCounter(log=False)
        context = OpenaiContext(base_url=base_url, api_key=api_key, llm=self.model, mm_llm=self.model)
        action_engine = ActionEngine.from_context(context, playwright_driver)
        world_model = WorldModel.from_context(context)
        agent = WebAgent(world_model, action_engine, n_steps=4, token_counter=token_counter, clean_screenshot_folder=False)

        return LaVagueTestContext(
            test_output_dir=test_output_dir,
            playwright=playwright,
            browser=browser,
            browser_context=browser_context,
            page=page,
            agent=agent
        )
    

    def _inject_bug(self, bug_script: str, test_context: LaVagueTestContext) -> None:
        test_context.page.add_init_script(bug_script)
        test_context.page.evaluate(bug_script)

    
    def _teardown_test_case(self, test_context: LaVagueTestContext) -> None:
        playwright_trace_path = test_context.test_output_dir / "trace.zip"

        for item in test_context.model_dump().values():
            try:
                if isinstance(item, Page): item.close()
                elif isinstance(item, Browser): item.close()
                elif isinstance(item, Playwright): item.stop()
                elif isinstance(item, BrowserContext):
                    item.tracing.stop(path=playwright_trace_path)
                    item.close()
            except Exception as e:
                logger.warning("Failed to close resource %s: %s", type(item).__name__, e)


    def _step(self, step: TestStep, test_context: LaVagueTestContext) -> StepResult:   
        agent = test_context.agent
        test_output_dir = test_context.test_output_dir

        # LaVague uses a fixed screenshot folder, override it to the run results folder
        screenshot_folder = test_output_dir / re.sub(r'[^a-zA-Z0-9\s]', '', step.action).lower().replace(" ", "_")[:30]
        screenshot_folder.mkdir(parents=True)
        PlaywrightDriver.get_current_screenshot_folder = lambda _self: screenshot_folder

        # Execute
        start_time = time.perf_counter()
        _ = agent.run(step.action)
        end_time = time.perf_counter()

        # Save aggregated steps data from all agentic runs
        steps_data = agent.logger.return_pandas()
        steps_data.to_pickle(test_output_dir / "steps.pkl")
        steps_tokens = steps_data.groupby("run_id", sort=False)["total_step_tokens"].sum().reset_index()
        tokens = steps_tokens.iloc[-1]["total_step_tokens"]

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
            tokens=tokens,
        )
