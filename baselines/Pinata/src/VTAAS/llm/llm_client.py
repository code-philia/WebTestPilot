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

    async def plan_step(
        self, conversation: list[Message]
    ) -> LLMTestStepPlanResponse: ...

    async def followup_step(
        self, conversation: list[Message]
    ) -> LLMTestStepFollowUpResponse: ...

    async def recover_step(
        self, conversation: list[Message]
    ) -> LLMTestStepRecoverResponse: ...

    async def act(self, conversation: list[Message]) -> LLMActResponse: ...

    async def assert_(self, conversation: list[Message]) -> LLMAssertResponse: ...

    async def step_postprocess(
        self, system: str, user: str, screenshots: list[bytes]
    ) -> LLMDataExtractionResponse: ...

    def close(self):
        self.logger.handlers.clear()


class LLMProvider(str, Enum):
    GOOGLE = "google"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    MISTRAL = "mistral"
