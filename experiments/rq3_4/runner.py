import sys
from pathlib import Path
from typing import Optional

# Ensure repo root and webtestpilot/src are importable
REPO_ROOT = Path(__file__).resolve().parents[2]
WEBTESTPILOT_SRC = REPO_ROOT / "webtestpilot" / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))
if str(WEBTESTPILOT_SRC) not in sys.path:
    sys.path.append(str(WEBTESTPILOT_SRC))

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
from testcases.baselines.webtestpilot.webtestpilot_runner import WebTestPilotTestRunner
from testcases.baselines.const import TestCase
from testcases.baselines.base_runner import TestResult

# Reuse the same imports the baseline runner uses
from main import Config, WebTestPilot


class WebTestPilotTestRunner_RQ3_4(WebTestPilotTestRunner):
    """
    RQ3 & 4 experiment-specific runner that:
    - Modifies load_test_case() to support loading from YAML (natural language paragraph) and convert to list[TestCase]
    - Support custom WebTestPilot configurations (Config)
    """

    def __init__(
        self,
        test_case_path: str,
        test_output_path: str,
        application,
        config: Config,
        headless: bool = True,
        **kwargs,
    ):
        super().__init__(
            test_case_path, test_output_path, application, headless=headless, **kwargs
        )
        self.config = config

    def load_test_cases(self, filter_pattern: Optional[str] = None) -> list[TestCase]:
        """Load test cases from test case directory."""
        test_cases: list[TestCase] = []

        if not self.test_case_path.exists():
            print(f"Test case path does not exist: {self.test_case_path}")
            return test_cases

        for file_path in sorted(
            self.test_case_path.glob("*.yaml"), key=lambda p: p.stem
        )[1:2]:
            if filter_pattern and filter_pattern not in file_path.stem:
                continue

            try:
                yaml = YAML()
                with open(file_path, "r") as f:
                    data: dict = yaml.load(f)

                    # Convert description -> actions list
                    description: str = data.get("description")
                    steps = WebTestPilot.parse(self.config, description)
                    actions = {
                        "actions": [
                            {"action": step.action, "expectedResult": step.expectation}
                            for step in steps
                        ]
                    }
                    data["actions"] = actions

                    # Parse as TestCase
                    test_case = TestCase.from_dict(data)
                    test_cases.append(test_case)

            except ParserError as e:
                print(f"Error loading {file_path}: {e}")
                raise e

        return test_cases

    def run_test_case(self, test_case: TestCase) -> TestResult:
        return super().run_test_case(test_case, self.config)
