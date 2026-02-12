from enum import Enum
from logging import Logger
from typing import Protocol

from ..schemas.llm import (
    LLMActResponse,
    LLMAssertResponse,
    LLMDataExtractionResponse,
    LLMTestStepFollowUpResponse,
    LLMTestStepPlanResponse,
    LLMTestStepRecoverResponse,
    Message,
)


class LLMClient(Protocol):
    logger: Logger

    def plan_step(
        self, conversation: list[Message]
    ) -> LLMTestStepPlanResponse: ...

    def followup_step(
        self, conversation: list[Message]
    ) -> LLMTestStepFollowUpResponse: ...

    def recover_step(
        self, conversation: list[Message]
    ) -> LLMTestStepRecoverResponse: ...

    def act(self, conversation: list[Message]) -> LLMActResponse: ...

    def assert_(self, conversation: list[Message]) -> LLMAssertResponse: ...

    def step_postprocess(
        self, system: str, user: str, screenshots: list[bytes]
    ) -> LLMDataExtractionResponse: ...

    def get_token_usage(self) -> int: ...

    def close(self):
        self.logger.handlers.clear()


class LLMProvider(str, Enum):
    OPENAI = "openai"