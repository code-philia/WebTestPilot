from typing import TypeGuard, final, override

from VTAAS.llm.llm_client import LLMProvider
from VTAAS.llm.utils import create_llm_client
from VTAAS.schemas.llm import Message, MessageRole, WorkerType
from VTAAS.utils.banner import add_banner
from VTAAS.utils.logger import get_logger

from ..schemas.verdict import AssertorResult, Status
from ..workers.browser import Browser
from ..schemas.worker import (
    AssertorInput,
    Worker,
    WorkerInput,
)


@final
class Assertor(Worker):
    """Assertor implementation."""

    def __init__(
        self,
        name: str,
        query: str,
        browser: Browser,
        llm_provider: LLMProvider,
        start_time: float,
        output_folder: str,
    ):
        super().__init__(name, query, browser)
        self.type = WorkerType.ASSERTOR
        self.start_time = start_time
        self.output_folder = output_folder
        self.llm_client = create_llm_client(
            self.name, llm_provider, start_time, self.output_folder
        )
        self.logger = get_logger(
            "Assertor - " + self.name + " - " + self.id,
            self.start_time,
            self.output_folder,
        )
        self.logger.info(f"initialized with query: {self.query}")

    @override
    async def process(self, input: WorkerInput) -> AssertorResult:
        if not self._is_assertor_input(input):
            raise TypeError("Expected input of type AssertorInput")
        screenshot = await self.browser.screenshot()
        page_info: str = await self.browser.get_page_info()
        viewport_info: str = await self.browser.get_viewport_info()
        self._setup_conversation(input, screenshot, page_info, viewport_info)
        self.logger.info(f"\n\nprocessing query '{self.query}'")
        try:
            response = await self.llm_client.assert_(self.conversation)
        except Exception as e:
            return AssertorResult(
                query=self.query,
                status=Status.FAIL,
                synthesis=str(e),
                screenshot=add_banner(screenshot, f'assert("{self.query}"'),
            )
        return AssertorResult(
            query=self.query,
            status=response.verdict.status,
            synthesis=response.get_cot(),
            screenshot=add_banner(screenshot, f'assert("{self.query}"'),
        )

    @property
    def system_prompt(self) -> str:
        return "You are part of a multi-agent systems. Your role is to assert the expected state of a web application, given a query."

    def _setup_conversation(
        self,
        input: AssertorInput,
        screenshot: bytes,
        page_info: str,
        viewport_info: str,
    ):
        self.conversation = [
            Message(role=MessageRole.System, content=self.system_prompt),
            Message(
                role=MessageRole.User,
                content=self._build_user_prompt(input, page_info, viewport_info),
                screenshot=[screenshot],
            ),
        ]
        self.logger.debug(f"User prompt:\n\n{self.conversation[1].content}")

    def _build_user_prompt(
        self,
        input: AssertorInput,
        page_info: str,
        viewport_info: str,
    ) -> str:
        with open(
            "./src/VTAAS/workers/assertor_prompt.txt", "r", encoding="utf-8"
        ) as prompt_file:
            prompt_template = prompt_file.read()

        current_step = input.test_step[0] + "; " + input.test_step[1]

        return prompt_template.format(
            test_case=input.test_case,
            current_step=current_step,
            assertion=self.query,
            page_info=page_info,
            viewport_info=viewport_info,
        )

    def _is_assertor_input(self, input: WorkerInput) -> TypeGuard[AssertorInput]:
        return isinstance(input, AssertorInput)

    @override
    def __str__(self) -> str:
        return f"Assert({self.query})"
