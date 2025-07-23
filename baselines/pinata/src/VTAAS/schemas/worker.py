from enum import Enum
from logging import Logger
from uuid import uuid4

from pydantic import BaseModel

from VTAAS.llm.llm_client import LLMClient
from VTAAS.schemas.llm import Message, WorkerType
from VTAAS.workers.browser import Browser
from ..schemas.verdict import WorkerResult
from abc import ABC, abstractmethod


class WorkerStatus(str, Enum):
    ACTIVE = "active"
    RETIRED = "retired"


class ActorInput(BaseModel):
    test_case: str
    test_step: tuple[str, str]
    history: str | None


class AssertorInput(BaseModel):
    test_case: str
    test_step: tuple[str, str]
    history: str | None


WorkerInput = ActorInput | AssertorInput


class Worker(ABC):
    """Abstract worker with common attributes."""

    type: WorkerType
    logger: Logger
    llm_client: LLMClient

    def __init__(self, name: str, query: str, browser: Browser):
        self.name: str = name
        self.status: WorkerStatus = WorkerStatus.ACTIVE
        self.query: str = query
        self.id: str = uuid4().hex
        self.browser: Browser = browser
        self.conversation: list[Message] = []

    @abstractmethod
    async def process(self, input: WorkerInput) -> WorkerResult: ...

    def retire(self):
        self.status = WorkerStatus.RETIRED
        self.llm_client.close()
        self.logger.handlers.clear()
