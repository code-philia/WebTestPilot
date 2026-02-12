from webtestpilot.baml_client.sync_client import b
from webtestpilot.baml_client.types import Step, TestCase
from webtestpilot.data_models import Session


class MissingStepsError(Exception):
    def __init__(self, steps):
        super().__init__(
            f"Missing steps, please update test description to address <unknown> parts. Steps: {steps}"
        )
        self.steps = steps


def parse(description: str, session: Session) -> list[Step]:
    """
    Parse a natural language test description into a structured test case.

    Args:
        description (str):
            A plain-text description of a test scenario, written in natural language.

    Returns:
        TestCase:
            A structured test case object containing:
            - scenario: A list of steps.
            - Each step has three components:
                * condition: Preconditions or setup.
                * action: The event or interaction being performed.
                * expectation: The expected outcome or assertion.
    """

    def contains_unknown(steps: list[Step]):
        return any(
            "<unknown>" in part
            for step in steps
            for part in (step.condition, step.action, step.expectation)
        )

    client_registry = session.config.parser
    test_case: TestCase = b.ExtractTestCase(description, {"client_registry": client_registry})
    session.trace.append({"parser": "extract_test_case", "test_case": test_case.model_dump_json()})

    if contains_unknown(test_case.steps):
        if session.config.infer_missing_steps:
            test_case: TestCase = b.ImplicitGeneration(test_case, {"client_registry": client_registry})
            session.trace.append({"parser": "implicit_generation", "test_case": test_case.model_dump_json()})
            return test_case.steps
        
        raise MissingStepsError(test_case.steps)

    return test_case.steps
