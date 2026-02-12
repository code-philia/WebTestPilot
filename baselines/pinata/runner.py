import time
import json
import logging
from pathlib import Path

from playwright.sync_api import sync_playwright, Playwright

from baselines.pinata.src.VTAAS.workers.browser import Browser
from baselines.pinata.src.VTAAS.llm.llm_client import LLMProvider
from baselines.pinata.src.VTAAS.schemas.verdict import Status
from baselines.pinata.src.VTAAS.orchestrator.orchestrator import Orchestrator, TestExecutionContext

from baselines.config import PinataConfig
from baselines.base_runner import BaseTestRunner
from baselines.test_setup_functions import setup_page_state
from baselines.test_model import TestCase, TestStep, TestContext, StepResult


logger = logging.getLogger(__name__)


class PinataTestContext(TestContext):
    test_output_dir: Path
    browser: Browser
    playwright: Playwright
    exec_context: TestExecutionContext
    orchestrator: Orchestrator


class PinataTestRunner(BaseTestRunner):
    """Test runner implementation for Pinata agent."""

    def __init__(self, config: PinataConfig):
        super().__init__(config)
        self.model = config.model
        self.tracer = config.tracer
        self.assertion = config.assertion
        self.save_screenshot = config.save_screenshot
        self.max_tries = config.max_tries


    def _setup_test_case(self, test_case: TestCase, test_output_dir: Path) -> PinataTestContext:
        pinata_test_name = f"TC-01-P :: {test_case.name}"
        playwright = sync_playwright().start()
        browser = Browser.create(
            id=pinata_test_name,
            headless=self.headless,
            playwright=playwright,
            save_screenshot=self.save_screenshot,
            tracer=self.tracer,
            trace_folder=str(test_output_dir),
            name=test_case.name,
        )
        setup_page_state(
            self.application, browser.page, test_case.setup_function 
        )
        orchestrator = Orchestrator(
            browser=browser,
            llm_provider=LLMProvider.OPENAI,
            tracer=self.tracer,
            output_folder=str(test_output_dir),
            model_name=self.model,
            name=test_case.name,
            assertion=self.assertion
        )
        exec_context = TestExecutionContext(
            test_case=test_case,
            current_step=None,
            step_index=0,
            history=[],
        )

        time.sleep(2)

        return PinataTestContext(
            test_output_dir=test_output_dir,
            browser=browser,
            playwright=playwright,
            exec_context=exec_context,
            orchestrator=orchestrator
        )
    

    def _inject_bug(self, bug_script: str, test_context: PinataTestContext) -> None:
        test_context.browser.page.add_init_script(bug_script)
        test_context.browser.page.evaluate(bug_script)
        

    def _teardown_test_case(self, test_context: PinataTestContext) -> None:
        for item in test_context.model_dump().values():
            try:
                if isinstance(item, Browser): item.close()
                elif isinstance(item, Playwright): item.stop()
                elif isinstance(item, Orchestrator): item.close()
            except Exception as e:
                logger.warning("Failed to close resource %s: %s", type(item).__name__, e)
            finally:
                item = None


    def _step(self, step: TestStep, test_context: PinataTestContext) -> StepResult: 
        exec_context = test_context.exec_context
        orchestrator = test_context.orchestrator
        test_output_dir = test_context.test_output_dir

        start_time = time.perf_counter()
        start_tokens = orchestrator.get_total_token_usage()

        # Execute
        # Step -> Planner -> [Actor/Assertor, ...] -> Step Done? -> Step Verdict
        exec_context.current_step = (step.action, step.expectation) if self.assertion else (step.action, "")
        exec_context.step_index += 1
        verdict = orchestrator.process_step(exec_context, self.max_tries)
        orchestrator.assertor_results.extend(verdict.assertor_results)

        # Check action results
        if verdict.status != Status.PASS:
            logger.error(
                (
                    f"Test case FAILED at step {exec_context.step_index}."
                    f" {exec_context.current_step[0]} -> {exec_context.current_step[1]}"
                )
            )

        # Update history
        step_str = f"{exec_context.step_index}. {step.action} -> {step.expectation}"
        step_synthesis = orchestrator.step_postprocess(
            exec_context, 
            verdict.history, 
            exec_context.history
        )
        exec_context.history.append(step_str)
        if len(step_synthesis) > 0:
            exec_context.history.append(Orchestrator.synthesis_str(step_synthesis))

        # Record step runtime
        end_time = time.perf_counter()            

        # Record step token usage
        end_tokens = orchestrator.get_total_token_usage()
        tokens = end_tokens - start_tokens

        # Record history
        history_file_path = test_output_dir / "history.log"
        history_file_path.write_text("\n".join(exec_context.history) + "\n", encoding="utf-8")

        # Record traces
        traces_file_path = test_output_dir / "traces.json"
        traces_file_path.write_text(json.dumps(orchestrator.traces, indent=2), encoding="utf-8")

        # Record assertion results
        assertor_results_path = test_output_dir / "assertor_results.json"
        assertor_results_path.write_text(
            json.dumps([r.to_dict() for r in orchestrator.assertor_results], indent=2), 
            encoding="utf-8"
        )

        try:
            is_action_correct = step.ground_truth(test_context.browser.page)
        except:
            logger.warn("Step ground truth check failed, defaulting to False")
            is_action_correct = False

        return StepResult(
            step=step,
            is_action_correct=is_action_correct,
            is_bug_reported=any([r.to_dict().get("status") == "fail" for r in orchestrator.assertor_results]),
            start_time=start_time,
            end_time=end_time,
            tokens=tokens
        )