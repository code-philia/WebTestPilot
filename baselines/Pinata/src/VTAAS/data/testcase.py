import csv
import logging
import os
from pathlib import Path
import re
import sys
import json
import argparse
import time
from typing import override
from collections.abc import Sequence
from uuid import uuid4

# Add parent directory to path for relative imports when running as script
if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent.parent))

#from VTAAS.utils.logger import get_logger
from ..utils.logger import  get_logger


class TestCase:
    def __init__(
        self,
        full_name: str,
        actions: list[str],
        expected_results: list[str],
        url: str,
        failing_info: None | tuple[int, str],
        output_folder: str,
    ):
        self.start_time: float = time.time()
        self.output_folder: str = output_folder
        self.logger: logging.Logger = get_logger(
            #__name__ + str(time.time())[-8:], self.start_time, self.output_folder
            __name__ + " - " + uuid4().hex, self.start_time, self.output_folder
        )
        self._full_name: str = full_name
        self._parse_full_name(full_name)
        self.actions: list[str] = actions
        self.expected_results: list[str] = expected_results
        self.url: str = url
        self.steps: Sequence[tuple[str, str]] = list(
            zip(self.actions, self.expected_results)
        )

        if self.type == "F":
            if not failing_info:
                self.logger.warning(
                    f"Test Case {self.id} is of type failing but does not have failing info"
                )
            else:
                self.failing_step: int = failing_info[0]
                self.failing_message: str = failing_info[1]

    def get_step(self, n: int) -> tuple[str, str]:
        """Get the nth step in the test case"""
        if n < 1:
            raise ValueError("Steps start at 1")
        if n > len(self.steps):
            raise ValueError(
                f"Step #{n} does not exist. Test case length: {len(self.steps)}"
            )
        return self.steps[n - 1]

    def _parse_full_name(self, full_name: str) -> None:
        """
        Parses the full name in the format "Test Case: TC-28-P :: Edit Account Information"
        to extract id, type, and name
        """
        # Extract the parts after "Test Case: TC-" and after "::"
        pattern = r"TC-(\d+)-([A-Z]) :: (.+)$"
        match = re.match(pattern, full_name)

        if match:
            self.id: str = match.group(1)
            self.type: str = match.group(2)
            self.name: str = match.group(3).strip()
        else:
            raise ValueError(f"Invalid test case format: {full_name}")

    @property
    def full_name(self) -> str:
        return f"TC-{self.id}-{self.type}: {self.name}"

    @override
    def __str__(self) -> str:
        output = self.full_name
        for idx, test_step in enumerate(self.steps):
            output += "\n"
            output += f"{idx + 1}. {test_step[0]}"
            if test_step[1]:
                output += f"; Assertion: {test_step[1]}"
        return output

    @override
    def __repr__(self) -> str:
        return (
            f"TestCase(id='{self.id}', type='{self.type}', "
            f"name='{self.name}', actions={self.actions}, "
            f"expected_results={self.expected_results})"
        )

    # We admit there can be empty assertions, and it's ok.
    def __len__(self) -> int:
        return len(self.actions)

    def __iter__(self):
        for step in self.steps:
            yield step


class TestCaseCollection:
    # To ensure it is ignored by pytest
    __test__: bool = False

    def __init__(self, file_path: str, url: str, output_folder: str = "."):
        self.file_path: str = file_path
        self.name: str = self._get_file_name()
        self.url: str = url
        self.output_folder: str = output_folder
        self.test_cases: list[TestCase] = []
        self._parse_file()
        self.start_time: float = time.time()
        self.logger: logging.Logger = get_logger(
            "TC collection " + uuid4().hex, self.start_time, output_folder
        )

    def _get_file_name(self) -> str:
        """
        Extracts the file name without extension from the file path
        """
        return os.path.splitext(os.path.basename(self.file_path))[0]

    def _parse_file(self) -> None:
        """
        Parses the file and creates TestCase instances.
        Currently supports CSV files only.
        """
        if not self.file_path.lower().endswith(".csv"):
            raise ValueError("Currently only CSV files are supported")

        test_cases_data = self._parse_csv()
        self._create_test_cases(test_cases_data[0], test_cases_data[1])

    def _parse_csv(
        self,
    ) -> tuple[dict[str, dict[str, list[str]]], list[tuple[int, str] | None]]:
        """
        Parses the CSV file and returns a dictionary of test cases.
        """
        test_cases: dict[str, dict[str, list[str]]] = {}

        with open(self.file_path, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            current_test_case = None
            failing_info: list[tuple[int, str] | None] = []
            for row in reader:
                if not row or not row[0].strip():
                    continue

                # Check for the test case title
                pattern = r"TC-(\d+)-([A-Z]) :: (.+)$"
                match = re.match(pattern, row[1])

                if match:
                    failing_info.append(None)
                    current_test_case = row[1].strip()
                    test_cases[current_test_case] = {
                        "actions": [],
                        "expected_results": [],
                    }
                else:
                    # Add actions and expected results if a test case is defined
                    if current_test_case and len(row) >= 2:
                        msg_candidate = None
                        action = row[1].strip() if len(row) > 1 else ""
                        expected_result = row[2].strip() if len(row) > 2 else ""
                        failing_row = row[3].strip() if len(row) > 3 else ""
                        if action != "Actions":
                            test_cases[current_test_case]["actions"].append(action)
                        if expected_result != "Expected Result":
                            test_cases[current_test_case]["expected_results"].append(
                                expected_result
                            )
                        match failing_row:
                            case "Expected Failure" | "":
                                continue
                            case "Fail":
                                self.logger.critical(
                                    f"Malformed TC number {current_test_case}. Check if the title of the next test is properly formatted"
                                )
                                break
                            case _:
                                if not msg_candidate:
                                    msg_candidate = (int(row[0]), failing_row)
                                else:
                                    self.logger.warning(
                                        f"{current_test_case} has more than one failing information. Taking the first one by default"
                                    )

                    failing_info.pop()
                    failing_info.append(msg_candidate)
        return test_cases, failing_info

    def _create_test_cases(
        self,
        test_cases_dict: dict[str, dict[str, list[str]]],
        failing_info: list[None | tuple[int, str]],
    ) -> None:
        """
        Creates TestCase instances from the parsed dictionary.
        """
        for i, (full_name, data) in enumerate(test_cases_dict.items()):
            test_case = TestCase(
                full_name=full_name,
                actions=data["actions"],
                expected_results=data["expected_results"],
                url=self.url,
                failing_info=failing_info[i],
                output_folder=self.output_folder,
            )
            self.test_cases.append(test_case)

    def get_test_case_by_id(self, id: str) -> TestCase:
        """
        Returns a test case by its ID.
        """
        for test_case in self.test_cases:
            if test_case.id == id:
                return test_case
        raise ValueError(f"No test case found with ID: {id}")

    def get_test_cases_by_type(self, type: str) -> list[TestCase]:
        """
        Returns all test cases of a specific type.
        """
        return [tc for tc in self.test_cases if tc.type == type]

    def get_test_case_by_name(self, name: str) -> TestCase:
        """
        Returns a test case by its name.
        """
        for test_case in self.test_cases:
            if test_case.name == name:
                return test_case
        raise ValueError(f"No test case found with name: {name}")

    def __iter__(self):
        return iter(self.test_cases)

    def __len__(self):
        return len(self.test_cases)

    @override
    def __str__(self) -> str:
        return f"TestCaseCollection: {self.name} ({len(self)} test cases)"


def _test_case_to_dict(test_case: TestCase) -> dict:
    """Convert a TestCase object to a dictionary"""
    test_case_dict = {
        "id": test_case.id,
        "type": test_case.type,
        "name": test_case.name,
        "full_name": test_case.full_name,
        "url": test_case.url,
        "steps": [
            {"action": action, "expected_result": expected_result}
            for action, expected_result in test_case.steps
        ],
    }

    # Add failing information if it exists
    if hasattr(test_case, "failing_step") and hasattr(test_case, "failing_message"):
        test_case_dict["failing_step"] = str(test_case.failing_step)
        test_case_dict["failing_message"] = test_case.failing_message

    return test_case_dict


def _collection_to_dict(collection: TestCaseCollection) -> dict:
    """Convert a TestCaseCollection object to a dictionary"""
    return {
        "name": collection.name,
        "url": collection.url,
        "file_path": collection.file_path,
        "test_cases": [_test_case_to_dict(tc) for tc in collection.test_cases],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Parse test cases from a CSV file and output as JSON"
    )
    parser.add_argument(
        "-f", "--file", required=True, help="Path to the CSV file containing test cases"
    )
    parser.add_argument(
        "-u", "--url", default="http://localhost", help="Base URL for the test cases"
    )
    parser.add_argument("-o", "--output", help="Output JSON file path (optional)")

    args = parser.parse_args()

    try:
        # Create TestCaseCollection
        collection = TestCaseCollection(args.file, args.url)

        # Convert to dictionary and then to JSON
        collection_dict = _collection_to_dict(collection)
        json_output = json.dumps(collection_dict, indent=2)

        if args.output:
            # Write to file if output path is specified
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_output)
            print(f"JSON output written to {args.output}")
        else:
            # Print to stdout
            print(json_output)

    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
