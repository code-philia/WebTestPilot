from baml_py import ClientRegistry

from baml_client.sync_client import b
from baml_client.types import TestCase


def parse(description: str, cr: ClientRegistry) -> TestCase:
    """
    Parse a natural language test description into a structured test case.

    Args:
        description (str):
            A plain-text description of a test scenario, written in natural language.
        cr (ClientRegistry):
            A BAML client registry containing configuration and runtime context
            for model execution.

    Returns:
        TestCase:
            A structured test case object containing:
            - scenario: A list of steps.
            - Each step has three components:
                * condition: Preconditions or setup.
                * action: The event or interaction being performed.
                * expectation: The expected outcome or assertion.
    """
    test_case = b.ExtractTestCase(description, {"client_registry": cr})

    if any(
        "<unknown>" in part
        for step in test_case.steps
        for part in (step.condition, step.action, step.expectation)
    ):
        test_case = b.ImplicitGeneration(test_case, {"client_registry": cr})

    return test_case
