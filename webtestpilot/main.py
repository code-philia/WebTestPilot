from dotenv import load_dotenv
from baml_py import ClientRegistry

from baml_client.sync_client import b
from baml_client.types import Scenario

load_dotenv()

cr = ClientRegistry()
cr.set_primary("GPT4o")


def parser(description: str) -> Scenario:
    scenario = b.ExtractScenario(description, {"client_registry": cr})

    if any(
        "<unknown>" in part
        for step in scenario.steps
        for part in (step.condition, step.action, step.expectation)
    ):
        scenario = b.ImplicitGeneration(scenario, {"client_registry": cr})

    return scenario


test = """
From the dashboard, the user clicks the "Books" link in the navigation bar, which navigates them to the Books listing page. 
The user clicks the "Create New Book" link, opening the book creation form. 
Inside the form, the user clicks into the "Name" textbox, which becomes focused for input. 
"""

test_masked = """
From the dashboard, the user clicks the "Books" link in the navigation bar, which navigates them to the Books listing page. 
The user clicks the "Create New Book" link. 
Inside the form, the user clicks into the "Name" textbox. 
"""

result = parser(test_masked)
print(result)
