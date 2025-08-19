import os
from datetime import datetime
from typing import TypeGuard, final, override

from playwright_dompath.dompath_async import xpath_path

from VTAAS.llm.llm_client import LLMClient, LLMProvider
from VTAAS.llm.utils import create_llm_client
from VTAAS.schemas.llm import (
    ClickCommand,
    Command,
    FillCommand,
    FinishCommand,
    GotoCommand,
    Message,
    MessageRole,
    ScrollCommand,
    SelectCommand,
    WorkerType,
)
from VTAAS.utils.banner import add_banner
from VTAAS.utils.logger import get_logger

from ..schemas.verdict import (
    ActorAction,
    ActorResult,
    Status,
    WorkerResult,
)
from ..schemas.worker import (
    ActorInput,
    Worker,
    WorkerInput,
)
from ..workers.browser import Browser, Mark


@final
class Actor(Worker):
    """The Actor receives an ACT query and issues browser commands to perform the query"""

    def __init__(
        self,
        name: str,
        query: str,
        browser: Browser,
        llm_provider: LLMProvider,
        start_time: float,
        output_folder: str,
        max_rounds: int = 8,
        model_name: str = "gpt-4o-2024-11-20",
    ):
        super().__init__(name, query, browser)
        self.type = WorkerType.ACTOR
        self.start_time = start_time
        self.actions: list[ActorAction] = []
        self.traces: list[dict] = []
        self.query = query
        self.max_rounds = max_rounds
        self.output_folder = output_folder
        self.logger = get_logger(
            "Actor - " + self.name + " - " + self.id,
            self.start_time,
            self.output_folder,
        )
        self.llm_client: LLMClient = create_llm_client(
            self.name,
            llm_provider,
            start_time,
            self.output_folder,
            model_name=model_name,
        )
        # self.logger.setLevel(logging.DEBUG)
        self.logger.info(f"Initialized with query: {self.query}")

    @override
    async def process(self, input: WorkerInput) -> WorkerResult:
        """Actor execution loop"""
        if not self._is_actor_input(input):
            raise TypeError("Expected input of type ActorInput")
        # Reset traces for this process call
        self.traces = []
        await self.browser.mark_page()
        screenshot = await self.browser.screenshot()
        marks: list[Mark] = await self.browser.get_marks()
        page_info: str = await self.browser.get_page_info()
        viewport_info: str = await self.browser.get_viewport_info()
        self._setup_conversation(input, screenshot, page_info, viewport_info, marks)
        verdict: WorkerResult | None = None
        round = 0
        self.logger.info(f"Actor {self.id[:8]} processing query '{self.query}'")
        while verdict is None and round < self.max_rounds:
            round += 1
            response = await self.llm_client.act(self.conversation)
            command = response.command

            # Capture trace for this command
            trace = await self.command_to_trace(command, self.browser)
            self.traces.append(trace)

            if command.name == "finish":
                self.logger.info(
                    f'("{self.query}") is DONE: {command.status} - {command.reason or "No reason"}'
                )
                verdict = ActorResult(
                    query=self.query,
                    status=command.status,
                    actions=self.actions,
                    screenshot=self._add_banner(screenshot, f'act("{self.query}")'),
                    explaination=command.reason,
                )
                break
            self.conversation.append(
                Message(
                    role=MessageRole.Assistant,
                    content=response.model_dump_json(),
                )
            )
            outcome = f"Browser response:\n{await self.run_command(command)}"
            self.actions.append(
                ActorAction(action=outcome, chain_of_thought=response.get_cot())
            )
            self.logger.info(outcome)
            await self.browser.unmark_page()
            await self.browser.mark_page()
            screenshot = await self.browser.screenshot()
            marks_str = "\n" + self._format_marks(await self.browser.get_marks())
            self.logger.debug(marks_str)
            outcome += marks_str
            outcome += f'\nIs the task "{self.query}" now complete?'
            self.conversation.append(
                Message(role=MessageRole.User, content=outcome, screenshot=[screenshot])
            )

        await self.browser.unmark_page()
        return verdict or ActorResult(
            query=self.query,
            status=Status.FAIL,
            actions=self.actions,
            screenshot=self._add_banner(screenshot, f'act("{self.query}")'),
            explaination="stopped after 3 rounds",
        )

    async def command_to_trace(self, command: Command, browser: Browser) -> dict:
        """Convert a command to trace format compatible with evaluation."""

        # Helper function to extract XPath for commands with labels
        async def get_xpath_for_label(label: str) -> str | None:
            try:
                result = await browser._resolve_mark(label)
                if "locator" in result:
                    return await xpath_path(result["locator"], False)
            except Exception as e:
                self.logger.warning(f"Failed to extract XPath for label {label}: {e}")
                return f"error: {str(e)}"
            return None

        match command:
            case ClickCommand(name="click"):
                xpath = await get_xpath_for_label(str(command.label))
                return {
                    "action": {
                        "name": "click",
                        "args": {"label": str(command.label), "xpath": xpath},
                    }
                }
            case GotoCommand(name="goto"):
                return {"action": {"name": "goto", "args": {"url": command.url}}}
            case FillCommand(name="fill"):
                xpath = await get_xpath_for_label(str(command.label))
                return {
                    "action": {
                        "name": "fill",
                        "args": {
                            "label": str(command.label),
                            "value": command.value,
                            "xpath": xpath,
                        },
                    }
                }
            case SelectCommand(name="select"):
                xpath = await get_xpath_for_label(str(command.label))
                return {
                    "action": {
                        "name": "select",
                        "args": {
                            "label": str(command.label),
                            "options": command.options,
                            "xpath": xpath,
                        },
                    }
                }
            case ScrollCommand(name="scroll"):
                return {
                    "action": {
                        "name": "scroll",
                        "args": {"direction": command.direction},
                    }
                }
            case FinishCommand(name="finish"):
                return {
                    "action": {
                        "name": "finish",
                        "args": {
                            "status": command.status.value,
                            "reason": command.reason,
                        },
                    }
                }

    async def run_command(self, command: Command) -> str:
        self.logger.info(f"Received command: {command!r}, type: {type(command)}")
        self.logger.info(f"Type of command: {type(command)}, id: {id(type(command))}")

        match command:
            case ClickCommand(name="click"):
                return await self.browser.click(str(command.label))
            case GotoCommand(name="goto"):
                return await self.browser.goto(command.url)
            case FillCommand(name="fill"):
                return await self.browser.fill(str(command.label), command.value)
            case SelectCommand(name="select"):
                return await self.browser.select(str(command.label), command.options)
            case ScrollCommand(name="scroll"):
                return await self.browser.vertical_scroll(command.direction)
            case FinishCommand(name="finish"):
                return ""

    @property
    def system_prompt(self) -> str:
        return "You are part of a multi-agent systems. Your role is to perform the provided query on a web application"

    def _setup_conversation(
        self,
        input: ActorInput,
        screenshot: bytes,
        page_info: str,
        viewport_info: str,
        marks: list[Mark],
    ):
        self.conversation = [
            Message(role=MessageRole.System, content=self.system_prompt),
            Message(
                role=MessageRole.User,
                content=self._build_user_prompt(input, page_info, viewport_info)
                + "\n"
                + self._format_marks(marks),
                screenshot=[screenshot],
            ),
        ]
        self.logger.debug(f"User prompt:\n\n{self.conversation[1].content}")

    def _is_actor_input(self, input: WorkerInput) -> TypeGuard[ActorInput]:
        return isinstance(input, ActorInput)

    def _add_banner(self, screenshot: bytes, query: str) -> bytes:
        banner_screenshot = add_banner(screenshot, query)
        self._save_screenshot(banner_screenshot)
        return banner_screenshot

    def _save_screenshot(self, screenshot: bytes):
        os.makedirs("screenshots", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"screenshots/{self.id}_act_{timestamp}.png"
        with open(filename, "wb") as f:
            _ = f.write(screenshot)

    def _build_user_prompt(
        self, input: ActorInput, page_info: str, viewport_info: str
    ) -> str:
        with open(
            "./baselines/pinata/src/VTAAS/workers/actor_prompt.txt",
            "r",
            encoding="utf-8",
        ) as prompt_file:
            prompt_template = prompt_file.read()
        history = (
            "<previous_actions>\n" + input.history + "\n</previous_actions>"
            if input.history is not None
            else ""
        )
        return prompt_template.format(
            history=history,
            page_info=page_info,
            viewport_info=viewport_info,
            query=self.query,
        )

    def _format_marks(self, marks: list[Mark]) -> str:
        output = "The labels on the screenshot correspons to these html elements\n:"
        for m in marks:
            output += f"{m['mark']}. {m['element']}\n"
        return output

    @override
    def __str__(self) -> str:
        return f"Act({self.query})"
