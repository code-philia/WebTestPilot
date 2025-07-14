import logging
import time
from dataclasses import dataclass, field
from typing import TypedDict, Unpack
from uuid import uuid4
from VTAAS.llm.llm_client import LLMClient, LLMProvider
from VTAAS.llm.utils import create_llm_client
from VTAAS.schemas.llm import (
    DataExtractionEntry,
    Message,
    MessageRole,
    SequenceType,
    WorkerConfig,
    WorkerType,
)
from ..data.testcase import TestCase
from ..schemas.verdict import (
    ActorResult,
    BaseResult,
    TestCaseVerdict,
    Status,
    TestStepVerdict,
    WorkerResult,
)
from ..workers.browser import Browser
from ..utils.logger import get_logger
from ..workers.actor import Actor
from ..workers.assertor import Assertor
from ..schemas.worker import (
    ActorInput,
    AssertorInput,
    Worker,
    WorkerInput,
)


@dataclass
class TestExecutionContext:
    test_case: TestCase
    current_step: tuple[str, str]
    step_index: int
    history: list[str] = field(default_factory=list)


class OrchestratorParams(TypedDict, total=False):
    name: str
    browser: Browser | None
    llm_provider: LLMProvider
    tracer: bool
    output_folder: str


class Orchestrator:
    """Orchestrator class to spawn and run actors and assertors."""

    def __init__(self, **kwargs: Unpack[OrchestratorParams]):
        default_params: OrchestratorParams = {
            "name": "missing name",
            "browser": None,
            "llm_provider": LLMProvider.OPENAI,
            "tracer": False,
            "output_folder": ".",
        }
        custom_params = kwargs
        if custom_params and set(custom_params.keys()).issubset(
            set(default_params.keys())
        ):
            default_params.update(custom_params)
        elif custom_params:
            raise ValueError("unknown orchestrator parameter(s) received")

        self.params: OrchestratorParams = default_params
        self.workers: list[Worker] = []
        self.active_workers: list[Worker] = []
        self.name: str = self.params["name"]
        self._browser: Browser | None = self.params["browser"]
        self.llm_provider: LLMProvider = self.params["llm_provider"]
        self.tracer: bool = self.params["tracer"]
        self.output_folder: str = self.params["output_folder"]
        self.start_time: float = time.time()
        self.logger: logging.Logger = get_logger(
            "Orchestrator - " + self.name + " - " + uuid4().hex,
            self.start_time,
            self.output_folder,
        )
        self.logger.debug("Orchestrator initialized")
        if self.name == "missing name":
            self.logger.warning("This orchestrator should have a proper name!")
        self.logger.info(f"Orchestrator output folder: {self.output_folder}")
        self.llm_client: LLMClient = create_llm_client(
            self.name, self.llm_provider, self.start_time, self.output_folder
        )
        self._exec_context: TestExecutionContext | None = None
        self._followup_prompt: str | None = None
        self._recover_prompt: str | None = None
        self.worker_reports: dict[str, list[str]] = {}
        self.worker_counter: dict[str, int] = {"actor": 0, "assertor": 0}
        self.conversation: list[Message] = []

    async def process_testcase(self, test_case: TestCase) -> TestCaseVerdict:
        """Manages the main execution loop for the given Test Case."""
        self.logger.info(f"Processing test case {test_case.name}")
        exec_context = TestExecutionContext(
            test_case=test_case,
            current_step=test_case.get_step(1),
            step_index=1,
            history=[],
        )
        if self._browser is None:
            self._browser = await Browser.create(
                name=self.name,
                timeout=3500,
                headless=True,
                start_time=self.start_time,
                tracer=self.tracer,
                trace_folder=self.output_folder,
            )
        _ = await self.browser.goto(exec_context.test_case.url)
        verdict = TestCaseVerdict(step_index=1, status=Status.UNK)
        try:
            for idx, test_step in enumerate(test_case):
                exec_context.current_step = test_step
                exec_context.step_index = idx + 1
                verdict = await self.process_step(exec_context)
                if verdict.status != Status.PASS:
                    self.logger.info(
                        (
                            f"Test case FAILED at step {exec_context.step_index}."
                            f" {exec_context.current_step[0]} -> {exec_context.current_step[1]}"
                        )
                    )
                    return TestCaseVerdict(
                        status=Status.FAIL,
                        step_index=exec_context.step_index,
                        explaination=None,
                    )
                step_str = (
                    f"{exec_context.step_index}. {test_step[0]} -> {test_step[1]}"
                )
                step_synthesis = await self.step_postprocess(
                    exec_context, verdict.history, exec_context.history
                )
                exec_context.history.append(step_str)
                if len(step_synthesis) > 0:
                    exec_context.history.append(
                        Orchestrator.synthesis_str(step_synthesis)
                    )
            return TestCaseVerdict(status=Status.PASS, explaination=None)
        except Exception as e:
            self.logger.warning(f"got this error: {str(e)}")
            return TestCaseVerdict(
                status=Status.FAIL,
                step_index=exec_context.step_index,
                explaination=f"Got error: {str(e)}",
            )
        finally:
            await self.browser.close()

    async def process_step(
        self, exec_context: TestExecutionContext, max_tries: int = 4
    ) -> TestStepVerdict:
        screenshot = await self.browser.screenshot()
        page_info: str = await self.browser.get_page_info()
        viewport_info: str = await self.browser.get_viewport_info()
        results: list[WorkerResult] = []
        step_history: list[str | tuple[str, list[bytes]]] = []
        self.logger.info(
            (
                f"Planning for test step "
                f"{exec_context.step_index}. {exec_context.current_step[0][:20]} => {exec_context.current_step[1][:20]}"
            )
        )
        sequence_type = await self.plan_step_init(
            exec_context, screenshot, page_info, viewport_info
        )
        step_history.append(
            (
                "Orchestrator: Planned for test step "
                f"{exec_context.current_step[0]} => {exec_context.current_step[1]}"
            )
        )
        for i in range(max_tries + 1):
            self.logger.info(
                f"step #{exec_context.step_index}: processing iteration {i + 1}"
            )
            results = await self.execute_step(exec_context)
            success = not any(verdict.status != Status.PASS for verdict in results)
            if not success and i >= max_tries:
                break
            workers_result = self._merge_worker_results(success, results)
            step_history.append(workers_result[0])
            self.logger.debug(f"workers merged results:\n{workers_result[0]}")
            if sequence_type == SequenceType.full and success:
                self.logger.info(f"Test step #{exec_context.step_index} PASSED")
                return TestStepVerdict(status=Status.PASS, history=step_history)
            page_info = await self.browser.get_page_info()
            viewport_info = await self.browser.get_viewport_info()
            if success:
                sequence_type = await self.plan_step_followup(
                    workers_result, page_info, viewport_info
                )
                step_history.append("Orchestrator: Planned the step further")
            else:
                recovery = await self.plan_step_recover(
                    workers_result, page_info, viewport_info
                )
                step_history.append("Orchestrator: Came up with a recovery solution")
                if not recovery:
                    self.logger.info(
                        f"No recovery solution found -> Test step #{exec_context.step_index} FAIL"
                    )
                    return TestStepVerdict(status=Status.FAIL, history=step_history)
                else:
                    sequence_type = recovery

        self.logger.info(
            f"{max_tries} failed attempts at performing step #{exec_context.step_index} -> Test step FAIL"
        )
        return TestStepVerdict(status=Status.FAIL, history=step_history)

    async def plan_step_init(
        self,
        exec_context: TestExecutionContext,
        screenshot: bytes,
        page_info: str,
        viewport_info: str,
    ) -> SequenceType:
        """Planning for the test step: spawn workers based on LLM call."""
        self._setup_conversation(exec_context, screenshot, page_info, viewport_info)
        response = await self.llm_client.plan_step(self.conversation)
        self.conversation.append(
            Message(
                role=MessageRole.Assistant,
                content=response.model_dump_json(),
            )
        )
        for config in response.workers:
            _ = self.spawn_worker(config)
        self.logger.debug(f"Initialized {len(self.active_workers)} new workers")
        return response.sequence_type

    async def plan_step_followup(
        self,
        workers_result: tuple[str, list[bytes]],
        page_info: str,
        viewport_info: str,
    ) -> SequenceType:
        """Continuing planning for the test step: spawn workers based on LLM call."""
        results_str, screenshots = workers_result
        with open(
            "./src/VTAAS/orchestrator/followup_prompt.txt", "r", encoding="utf-8"
        ) as prompt_file:
            results_str += prompt_file.read()

        results_str += f"\n{page_info}"
        results_str += f"\n{viewport_info}"

        user_msg = Message(
            role=MessageRole.User,
            content=results_str,
            screenshot=screenshots,
        )
        self.conversation.append(user_msg)
        response = await self.llm_client.followup_step(self.conversation)
        self.conversation.append(
            Message(
                role=MessageRole.Assistant,
                content=response.model_dump_json(),
            )
        )
        for config in response.workers:
            _ = self.spawn_worker(config)
        self.logger.info(f"Initialized {len(self.active_workers)} new workers")
        return response.sequence_type

    async def plan_step_recover(
        self,
        workers_result: tuple[str, list[bytes]],
        page_info: str,
        viewport_info: str,
    ) -> SequenceType | bool:
        """Recover planning of the test step: spawn workers based on LLM call."""
        results_str, screenshots = workers_result
        with open(
            "./src/VTAAS/orchestrator/recover_prompt.txt", "r", encoding="utf-8"
        ) as prompt_file:
            results_str += prompt_file.read()

        results_str += f"\n{page_info}"
        results_str += f"\n{viewport_info}"

        user_msg = Message(
            role=MessageRole.User, content=results_str, screenshot=screenshots
        )
        self.conversation.append(user_msg)
        response = await self.llm_client.recover_step(self.conversation)
        self.conversation.append(
            Message(
                role=MessageRole.Assistant,
                content=response.model_dump_json(),
            )
        )
        if not response.plan or not response.plan.workers:
            return False
        for config in response.plan.workers:
            _ = self.spawn_worker(config)
        self.logger.info(f"Initialized {len(self.active_workers)} new workers")
        return response.plan.sequence_type

    async def execute_step(
        self, exec_context: TestExecutionContext
    ) -> list[WorkerResult]:
        """
        Run active workers and retire them afterwards.
        """
        results: list[WorkerResult] = []
        result = BaseResult(status=Status.PASS)
        local_history: list[str] = []
        while self.active_workers and result.status == Status.PASS:
            worker = self.active_workers[0]
            input: WorkerInput = self._prepare_worker_input(
                exec_context, worker.type, local_history
            )
            result = await worker.process(input=input)
            if isinstance(result, ActorResult):
                local_history.append(worker.__str__())
                for action in result.actions:
                    if action:
                        local_history.append(action.action)
            elif result.status == Status.PASS:
                local_history.append(f"{worker.__str__()}: Assertion Verified")
            else:
                local_history.append(
                    f"{worker.__str__()}: Assertion could not be verified"
                )
            results.append(result)
            worker.retire()
            self.active_workers.remove(worker)
        self.active_workers.clear()
        return results

    async def step_postprocess(
        self,
        exec_context: TestExecutionContext,
        step_history: list[str | tuple[str, list[bytes]]],
        existing_synthesis: list[str],
    ) -> list[DataExtractionEntry]:
        """Test step execution post-processing: keeping relevant info for future steps"""
        screenshots = [
            sshot
            for entry in step_history
            if isinstance(entry, tuple)
            for sshot in entry[1]
        ]
        system = "You are an expert in meaningful data extraction"
        synthesis = "\n".join(existing_synthesis)
        raw_step_history = "\n-----\n".join(
            [entry if isinstance(entry, str) else entry[0] for entry in step_history]
        )
        user = self._build_synthesis_prompt(exec_context, synthesis, raw_step_history)
        self.logger.debug("Data Extraction prompt:\n" + user)
        response = await self.llm_client.step_postprocess(system, user, screenshots)
        return response.entries

    def _merge_worker_results(
        self, success: bool, results: list[WorkerResult]
    ) -> tuple[str, list[bytes]]:
        outcome: str = "successfully" if success else "but eventually failed"
        merged_results: str = f"The sequence of workers was executed {outcome}:\n"
        screenshots: list[bytes] = []
        for result in results:
            screenshots.append(result.screenshot)
            if isinstance(result, ActorResult):
                actions_str = "\n".join(
                    [f"  - {action.chain_of_thought}" for action in result.actions]
                )
                merged_results += (
                    f'Act("{result.query}") -> {result.status.value}\n'
                    f"  Actions:\n{actions_str}\n"
                    "-----------------\n"
                )
            else:
                merged_results += (
                    f'Assert("{result.query}") -> {result.status.value}\n'
                    f"  Report: {result.synthesis}\n"
                    "-----------------\n"
                )
        return merged_results, screenshots

    def _prepare_worker_input(
        self,
        exec_context: TestExecutionContext,
        type: WorkerType,
        step_history: list[str],
    ) -> WorkerInput:
        full_history = "\n".join(exec_context.history + step_history)
        match type:
            case WorkerType.ACTOR:
                return ActorInput(
                    test_case=exec_context.test_case.__str__(),
                    test_step=exec_context.current_step,
                    history=full_history or None,
                )
            case WorkerType.ASSERTOR:
                return AssertorInput(
                    test_case=exec_context.test_case.__str__(),
                    test_step=exec_context.current_step,
                    history=full_history or None,
                )

    def spawn_worker(self, config: WorkerConfig) -> Worker:
        """Spawn a new worker based on the provided configuration."""
        worker: Worker
        match config.type:
            case WorkerType.ACTOR:
                worker = Actor(
                    self.name,
                    config.query,
                    self.browser,
                    self.llm_provider,
                    self.start_time,
                    self.output_folder,
                )
                self.workers.append(worker)
                self.active_workers.append(worker)
            case WorkerType.ASSERTOR:
                worker = Assertor(
                    self.name,
                    config.query,
                    self.browser,
                    self.llm_provider,
                    self.start_time,
                    self.output_folder,
                )
                self.workers.append(worker)
                self.active_workers.append(worker)
        return worker

    def _setup_conversation(
        self,
        context: TestExecutionContext,
        screenshot: bytes,
        page_info: str,
        viewport_info: str,
    ):
        self.conversation = [
            Message(role=MessageRole.System, content=self._build_system_prompt()),
            Message(
                role=MessageRole.User,
                content=self._build_user_init_prompt(context, page_info, viewport_info),
                screenshot=[screenshot],
            ),
        ]
        self.logger.debug(f"User prompt:\n{self.conversation[1].content}")

    def _build_system_prompt(self) -> str:
        with open(
            "./src/VTAAS/orchestrator/system_prompt.txt", "r", encoding="utf-8"
        ) as prompt_file:
            prompt_template = prompt_file.read()
        return prompt_template

    def _build_user_init_prompt(
        self, exec_context: TestExecutionContext, page_info: str, viewport_info: str
    ) -> str:
        with open(
            "./src/VTAAS/orchestrator/init_prompt.txt", "r", encoding="utf-8"
        ) as prompt_file:
            prompt_template = prompt_file.read()
        test_case = exec_context.test_case
        action, assertion = exec_context.current_step
        test_step = (
            f"{exec_context.step_index}. action: {action}, assertion: {assertion}"
        )
        history = (
            "<history>\n" + "\n".join(exec_context.history) + "\n</history>"
            if len(exec_context.history) > 0
            else ""
        )
        return prompt_template.format(
            test_case=test_case,
            current_step=test_step,
            history=history,
            page_info=page_info,
            viewport_info=viewport_info,
        )

    def _build_synthesis_prompt(
        self,
        exec_context: TestExecutionContext,
        previous_synthesis: str,
        step_history: str,
    ) -> str:
        with open(
            "./src/VTAAS/orchestrator/synthesis_prompt.txt", "r", encoding="utf-8"
        ) as prompt_file:
            prompt_template = prompt_file.read()
        saved_data = (
            ""
            if not previous_synthesis
            else (
                "The following synthesis has already been done on previous steps:\n"
                "<current_synthesis>"
                f"{previous_synthesis}"
                "</current_synthesis>"
            )
        )
        test_step = f"{exec_context.step_index}. {exec_context.current_step[0]} -> {exec_context.current_step[1]}"
        return prompt_template.format(
            test_case=exec_context.test_case,
            current_step=test_step,
            saved_data=saved_data,
            execution_logs=step_history,
        )

    @staticmethod
    def synthesis_str(synthesis: list[DataExtractionEntry]):
        output: str = ""
        for entry in synthesis:
            output += " ----- \n"
            output += f"type: {entry.entry_type}\n"
            output += f"value: {entry.value}\n"
        return output

    @property
    def browser(self) -> Browser:
        """Get the browser instance, ensuring it is initialized"""
        if self._browser is None:
            raise RuntimeError(
                "Browser has not been initialized yet. Do Browser.create(name)."
            )
        return self._browser

    @property
    def followup_prompt(self) -> str:
        """Get the followup prompt"""
        if self._followup_prompt is None:
            with open(
                "./src/VTAAS/orchestrator/followup_prompt.txt", "r", encoding="utf-8"
            ) as prompt_file:
                self._followup_prompt = prompt_file.read()
        return self._followup_prompt

    @property
    def recover_prompt(self) -> str:
        """Get the recover prompt"""
        if self._recover_prompt is None:
            with open(
                "./src/VTAAS/orchestrator/recover_prompt.txt", "r", encoding="utf-8"
            ) as prompt_file:
                self._recover_prompt = prompt_file.read()
        return self._recover_prompt

    async def close(self):
        self.logger.handlers.clear()
        self.llm_client.close()
        await self.browser.close()
