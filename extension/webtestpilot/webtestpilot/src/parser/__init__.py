from config import Config
from baml_client.sync_client import b
from baml_client.types import TestCase, Step


class MissingStepsError(Exception):
    def __init__(self, steps):
        super().__init__(
            f"Missing steps, please update test description to address <unknown> parts. Steps: {steps}"
        )
        self.steps = steps


def parse(description: str, config: Config) -> TestCase:
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

    client_registry = config.parser
    test_case = b.ExtractTestCase(description, {"client_registry": client_registry})

    if contains_unknown(test_case.steps):
        if config.infer_missing_steps:
            return b.ImplicitGeneration(test_case, {"client_registry": client_registry})
        raise MissingStepsError(test_case.steps)

    return test_case
