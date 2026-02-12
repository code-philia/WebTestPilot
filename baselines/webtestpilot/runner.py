import os
import time
import json
import logging
from pathlib import Path
from typing import Optional, Iterator

from pydantic import BaseModel
from playwright.sync_api import Page, Browser, BrowserContext, Playwright, sync_playwright

from baselines.config import WebTestPilotConfig
from baselines.const import Viewport
from baselines.test_model import TestCase, TestStep, TestContext, StepResult
from baselines.test_setup_functions import setup_page_state
from baselines.base_runner import BaseTestRunner
from webtestpilot import WebTestPilot, Config, BugReport, Session, Step as WebTestPilotStep
from webtestpilot.assertion_api import serialize_history
from webtestpilot.parser import parse


os.environ['BAML_LOG'] = "OFF"
logger = logging.getLogger(__name__)


class WebTestPilotTestContext(TestContext):
    test_output_dir: Path
    session: Session
    page: Page
    browser_context: BrowserContext
    browser: Browser
    playwright: Playwright
    parsed_steps: Optional[Iterator[WebTestPilotStep]]


class WebTestPilotTestRunner(BaseTestRunner):

    def __init__(self, config: WebTestPilotConfig):
        super().__init__(config)
        self.parser = config.parser
        self.assertion = config.assertion
        self.config = Config.load(config.config_path)


    def _setup_test_case(self, test_case: TestCase, test_output_dir: Path) -> WebTestPilotTestContext:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=self.headless)
        browser_context = browser.new_context(viewport={"width": Viewport.WIDTH, "height": Viewport.HEIGHT})
        browser_context.tracing.start(screenshots=True, snapshots=True)
        page = browser_context.new_page()
        page = setup_page_state(self.application, page, test_case.setup_function)
        session = Session(page, self.config)

        parsed_steps = None
        if self.parser:
            description = getattr(test_case, "paragraph")
            parsed_steps = iter(parse(description, session))

        return WebTestPilotTestContext(
            test_output_dir=test_output_dir,
            session=session,
            page=page,
            browser=browser,
            browser_context=browser_context,
            playwright=playwright,
            parsed_steps=parsed_steps
        )
    

    def _inject_bug(self, bug_script: str, test_context: WebTestPilotTestContext) -> None:
        test_context.page.add_init_script(bug_script)
        test_context.page.evaluate(bug_script)


    def _teardown_test_case(self, test_context: WebTestPilotTestContext) -> None:
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
    

    def _step(self, step: TestStep, test_context: WebTestPilotTestContext) -> StepResult:
        session = test_context.session
        
        # Handle bugs reported by WebTestPilot
        bugs = []
        def _hook(report: BugReport):
            bugs.append(report)
        
        start_usage = session.collector.usage
        start_tokens = start_usage.input_tokens + start_usage.output_tokens

        if self.parser:
            wtp_step = next(test_context.parsed_steps)
        else:
            wtp_step = WebTestPilotStep(condition="", action=step.action, expectation=step.expectation)

        # Execute
        start_time = time.perf_counter()
        WebTestPilot.run(session, [wtp_step], assertion=self.assertion, hooks=[_hook])
        end_time = time.perf_counter()
        
        end_usage = session.collector.usage
        end_tokens = end_usage.input_tokens + end_usage.output_tokens
        tokens = end_tokens - start_tokens

        # Save trace
        trace_path = test_context.test_output_dir / "trace.json"
        trace_path.write_text(json.dumps(session.trace, indent=2), encoding="utf-8")

        # Save history
        history_path = test_context.test_output_dir / "history.json"
        history: list[BaseModel] = serialize_history(test_context.session)
        history_path.write_text(
            json.dumps(
                [h.model_dump() for h in history],
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        try:
            is_action_correct = step.ground_truth(test_context.page)
        except:
            logger.warn("Step ground truth check failed, defaulting to False")
            is_action_correct = False

        return StepResult(
            step=step,
            is_action_correct=is_action_correct,
            is_bug_reported=len(bugs) > 0,
            start_time=start_time,
            end_time=end_time,
            tokens=tokens
        )