from pathlib import Path
from typing import Optional, Callable

from playwright.sync_api import Page
from pydantic import BaseModel, ConfigDict, Field, model_validator


class TestContext(BaseModel, validate_assignment=True):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class TestStep(BaseModel):
    """Represents a single test action with its expected result."""
    action: str
    expectation: str
    ground_truth: Callable[[Page], bool] = Field(..., exclude=True)


class TestCase(BaseModel):
    """Represents a complete test case with all its properties and actions."""
    model_config = ConfigDict(extra="allow")
    
    test_path: Path
    bug_path: Optional[Path]

    name: str
    setup_function: str
    steps: list[TestStep]


class StepResult(BaseModel):
    step: TestStep
    is_action_correct: bool # Did the agent arrive at the correct state after the action?
    is_bug_reported: bool # Did the agent report any bug after the action?
    start_time: float
    end_time: float
    tokens: int

    @property
    def duration(self):
        return self.end_time - self.start_time

    @model_validator(mode="after")
    def check_times(cls, values: "StepResult"):
        if values.end_time < values.start_time:
            raise ValueError("end_time cannot be before start_time")
        return values
    

class TestResult(BaseModel):
    test_case: TestCase
    steps: list[StepResult]

    @property
    def is_task_complete(self) -> bool:
        # Equal length
        if len(self.steps) != len(self.test_case.steps):
            return False
        
        # Equal steps in sequence
        for step_result, test_step in zip(self.steps, self.test_case.steps):
            if step_result.step != test_step:
                return False
            
        # All step marked as is_completed=True
        return all(step_result.is_action_correct for step_result in self.steps)
    
    @property
    def duration(self) -> float:
        return sum([step.duration for step in self.steps])
    
    @property
    def tokens(self) -> int:
        return sum([step.tokens for step in self.steps])