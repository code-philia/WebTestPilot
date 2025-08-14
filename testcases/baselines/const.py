from dataclasses import dataclass, field
from enum import Enum


class MethodEnum(str, Enum):
    lavague = "lavague"
    pinata = "pinata"
    naviqate = "naviqate"
    webtestpilot = "webtestpilot"


class ApplicationEnum(str, Enum):
    bookstack = "bookstack"
    invoiceninja = "invoiceninja"
    indico = "indico"
    prestashop = "prestashop"


class ProviderEnum(str, Enum):
    openai = "openai"
    anthropic = "anthropic"
    google = "google"
    mistral = "mistral"
    openrouter = "openrouter"


@dataclass
class TestAction:
    """Represents a single test action with its expected result."""

    action: str
    expectedResult: str = ""


@dataclass
class TestCase:
    """Represents a complete test case with all its properties and actions."""

    name: str
    url: str
    actions: list[TestAction] = field(default_factory=list)
    setup_function: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "TestCase":
        # Extract basic fields
        name = data.get("name", "Unnamed")
        url = data.get("url", "")
        setup_function = data.get("setup_function", "")

        # Convert actions from dict format to TestAction objects
        actions = []
        for action_data in data.get("actions", []):
            if isinstance(action_data, dict):
                action = TestAction(
                    action=action_data.get("action", ""),
                    expectedResult=action_data.get("expectedResult", ""),
                )
                actions.append(action)

        return cls(name=name, url=url, actions=actions, setup_function=setup_function)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "url": self.url,
            "setup_function": self.setup_function,
            "actions": [
                {"action": action.action, "expectedResult": action.expectedResult}
                for action in self.actions
            ],
        }
