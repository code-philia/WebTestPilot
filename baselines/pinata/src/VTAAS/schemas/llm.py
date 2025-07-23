from enum import Enum
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


from ..schemas.verdict import AssertionReport, Status


class MessageRole(str, Enum):
    System = "system"
    User = "user"
    Assistant = "assistant"


class Message(BaseModel):
    role: MessageRole
    content: str
    screenshot: list[bytes] | None = None

    class Config:
        use_enum_values: bool = True


class WorkerType(str, Enum):
    ACTOR = "act"
    ASSERTOR = "assert"


class WorkerConfig(BaseModel):
    type: WorkerType
    query: str


class AssertionChecking(BaseModel):
    observation: str
    verification: str


class SequenceType(str, Enum):
    full = "full"
    partial = "partial"


class LLMRequest(BaseModel):
    """Schema for the request sent to LLM."""

    conversation: tuple[str, str] = Field(
        ..., description="Conversation for the request to the LLM"
    )  # noqa
    screenshot: bytes | None = Field(..., description="Main objective to be achieved")


class LLMTestStepPlanResponse(BaseModel):
    """Schema for the response received from LLM."""

    current_step_analysis: str
    screenshot_analysis: str
    previous_actions_analysis: str
    workers: list[WorkerConfig]
    sequence_type: SequenceType


class LLMTestStepFollowUpResponse(BaseModel):
    """Schema for the response received from LLM."""

    workers_analysis: str
    last_screenshot_analysis: str
    workers: list[WorkerConfig]
    sequence_type: SequenceType


class DataExtractionEntry(BaseModel):
    entry_type: str
    value: str


class LLMDataExtractionResponse(BaseModel):
    entries: list[DataExtractionEntry]


class LLMTestSequencePart(BaseModel):
    workers: list[WorkerConfig]
    sequence_type: SequenceType


class RecoverDecision(str, Enum):
    try_again = "try new plan"
    stop = "assign verdict"


class LLMTestStepRecoverResponse(BaseModel):
    """Schema for the response received from LLM."""

    workers_analysis: str
    recovery: str
    decision: RecoverDecision
    plan: LLMTestSequencePart = None
    # status: Status = None


class ClickCommand(BaseModel):
    name: Literal["click"]
    label: int


class GotoCommand(BaseModel):
    name: Literal["goto"]
    url: str


class FillCommand(BaseModel):
    name: Literal["fill"]
    label: int
    value: str


class SelectCommand(BaseModel):
    name: Literal["select"]
    label: int
    options: str


class ScrollCommand(BaseModel):
    name: Literal["scroll"]
    direction: Literal["up", "down"]


class FinishCommand(BaseModel):
    name: Literal["finish"]
    status: Status
    reason: str = None


Command = (
    ClickCommand
    | GotoCommand
    | FillCommand
    | SelectCommand
    | ScrollCommand
    | FinishCommand
)


class LLMActResponse(BaseModel):
    """Schema for the response received from LLM."""

    current_webpage_identification: str
    screenshot_analysis: str
    query_progress: str
    next_action: str
    element_recognition: str
    command: Command

    def get_cot(self) -> str:
        data = self.model_dump_json(exclude={"command"})
        return str(data)


class ClickGoogleCommand(BaseModel):
    name: str = "click"
    label: int

    @field_validator("name")
    def check_name(cls, value: str) -> str:
        if value != "click":
            raise ValueError("Invalid name for ClickCommand, expected 'click'")
        return value


class GotoGoogleCommand(BaseModel):
    name: str = "goto"
    url: str

    @field_validator("name")
    def check_name(cls, value: str) -> str:
        if value != "goto":
            raise ValueError("Invalid name for GotoCommand, expected 'goto'")
        return value


class FillGoogleCommand(BaseModel):
    name: str = "fill"
    label: int
    value: str

    @field_validator("name")
    def check_name(cls, value: str) -> str:
        if value != "fill":
            raise ValueError("Invalid name for FillCommand, expected 'fill'")
        return value


class SelectGoogleCommand(BaseModel):
    name: str = "select"
    label: int
    options: str

    @field_validator("name")
    def check_name(cls, value: str) -> str:
        if value != "select":
            raise ValueError("Invalid name for SelectCommand, expected 'select'")
        return value


class ScrollGoogleCommand(BaseModel):
    name: str = "scroll"
    direction: Literal["up", "down"]

    @field_validator("name")
    def check_name(cls, value: str) -> str:
        if value != "scroll":
            raise ValueError("Invalid name for ScrollCommand, expected 'scroll'")
        return value


class FinishGoogleCommand(BaseModel):
    name: str = "finish"
    status: Status
    reason: str = None

    @field_validator("name")
    def check_name(cls, value: str) -> str:
        if value != "finish":
            raise ValueError("Invalid name for FinishCommand, expected 'finish'")
        return value


GoogleCommand = (
    ClickGoogleCommand
    | GotoGoogleCommand
    | FillGoogleCommand
    | SelectGoogleCommand
    | ScrollGoogleCommand
    | FinishGoogleCommand
)


class LLMActGoogleResponse(BaseModel):
    """Schema for the response received from LLM."""

    current_webpage_identification: str
    screenshot_analysis: str
    query_progress: str
    next_action: str
    element_recognition: str
    command: GoogleCommand

    def get_cot(self) -> str:
        data = self.model_dump_json(exclude={"command"})
        return str(data)


class LLMAssertResponse(BaseModel):
    """Schema for the response received from LLM."""

    page_description: str
    assertion_checking: AssertionChecking
    verdict: AssertionReport

    def get_cot(self) -> str:
        data = self.model_dump_json()
        return str(data)
