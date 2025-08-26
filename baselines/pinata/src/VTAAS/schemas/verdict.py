import ast
from enum import Enum
from typing import Generic, TypeVar, override

from pydantic import BaseModel, Field


class Status(str, Enum):
    UNK = "unknown"
    PASS = "success"
    FAIL = "fail"


class BaseResult(BaseModel):
    """Base result schema"""

    status: Status = Field(..., description="Status of the result")
    explaination: str | None = None

    class Config:
        use_enum_values: bool = True


class WorkerBaseResult(BaseModel):
    """Worker Base result schema"""

    query: str
    status: Status = Field(..., description="Status of the result")
    explaination: str | None = None
    screenshot: bytes


class ActorAction(BaseModel):
    action: str
    chain_of_thought: str


class ActorResult(WorkerBaseResult):
    actions: list[ActorAction]


class AssertorResult(WorkerBaseResult):
    synthesis: str
    step_index: int = -1

    def to_dict(self) -> dict:
        # Parse synthesis string to dict using library
        synthesis_dict = ast.literal_eval(self.synthesis)

        return {
            "query": self.query,
            "status": self.status,
            "explaination": self.explaination,
            "synthesis": synthesis_dict,
            "step_index": self.step_index,
        }


class TestStepVerdict(BaseResult):
    history: list[str | tuple[str, list[bytes]]]
    assertor_results: list[AssertorResult] = []


class TestCaseVerdict(BaseResult):
    step_index: int = -1  # type: ignore
    traces: list[dict | None] = []
    assertor_results: list[AssertorResult] = []


WorkerResult = ActorResult | AssertorResult


class AssertionReport(BaseModel):
    status: Status = Field(..., description="Verdict Status")
    discrepancies: str = None  # type: ignore
