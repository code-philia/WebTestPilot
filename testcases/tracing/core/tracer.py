"""
Core XPath Tracer

Enhanced implementation that tracks:
1. Page URL
2. Locator XPath
3. Action
4. Test context (app/collection/test_name)
5. Method coverage and missing traces
"""

import json
import os
from dataclasses import dataclass
from typing import Any, Optional

from .constants import ActionType


@dataclass
class TraceEntry:
    """Simplified trace entry with only essential fields"""

    url: str
    xpath: str
    action: str
    success: bool = True
    error_message: str = ""
    value: Optional[str] = None
    action_type: str = ActionType.ACTION

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary (exclude error fields if no errors)"""
        trace_dict = {
            "url": self.url,
            "action_type": self.action_type,
            "xpath": self.xpath,
            "action": self.action,
        }

        if self.value is not None:
            trace_dict["value"] = self.value

        if self.error_message:
            trace_dict["error_message"] = self.error_message

        return trace_dict


class XPathTracer:
    """Enhanced tracer with test context and method coverage tracking"""

    def __init__(self, output_dir: str = "./traces") -> None:
        self.traces: list[TraceEntry] = []
        self.output_dir: str = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Method coverage tracking
        self.attempted_methods: set[str] = set()
        self.successful_methods: set[str] = set()
        self.failed_methods: set[str] = set()

        # Test context from environment/plugin
        self.test_name: str = os.getenv("XPATH_TEST_NAME", "unknown_test")
        self.app: str = os.getenv("XPATH_TEST_APP", "unknown_app")
        self.collection: str = os.getenv("XPATH_TEST_COLLECTION", "unknown_collection")

    def log_action(
        self,
        url: str,
        xpath: str,
        action: str,
        success: bool = True,
        error_message: str = "",
        value: Optional[str] = None,
        action_type: str = ActionType.ACTION,
    ) -> None:
        """Log a single action with simplified format"""
        trace = TraceEntry(
            url=url,
            xpath=xpath,
            action=action,
            success=success,
            error_message=error_message,
            value=value,
            action_type=action_type,
        )
        self.traces.append(trace)

        # Update method coverage
        self.attempted_methods.add(action)
        if success:
            self.successful_methods.add(action)
        else:
            self.failed_methods.add(action)

    def save_traces(self) -> str:
        """Save traces to JSON file with simplified format"""
        # Clean up test name - remove [chromium] and similar browser identifiers
        clean_test_name = (
            self.test_name.split("[")[0] if "[" in self.test_name else self.test_name
        )
        filename = f"{clean_test_name}.json"
        filepath = os.path.join(self.output_dir, filename)

        # Debug output
        print(f"\n[DEBUG] Saving {len(self.traces)} traces to {filepath}")

        # Calculate coverage statistics
        missing_methods: set[str] = self.failed_methods - self.successful_methods
        coverage_stats: dict[str, Any] = {
            "attempted_methods": sorted(list(self.attempted_methods)),
            "successful_methods": sorted(list(self.successful_methods)),
            "failed_methods": sorted(list(self.failed_methods)),
            "missing_methods": sorted(list(missing_methods)),
        }

        simplified_traces = [trace.to_simplified_dict() for trace in self.traces]

        # Only start from the [START] mark
        truncated_traces = []
        start = False
        for trace in simplified_traces:
            if start:
                truncated_traces.append(trace)

            if trace["action"] == "START":
                start = True

        data: dict[str, Any] = {
            "test": clean_test_name,
            "app": self.app,
            "collection": self.collection,
            "total_traces": len(self.traces),
            "successful_traces": len([t for t in self.traces if t.success]),
            "failed_traces": len([t for t in self.traces if not t.success]),
            "coverage_stats": coverage_stats,
            "traces": truncated_traces,
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        return filepath

    def report_coverage(self) -> None:
        missing_methods: set[str] = self.failed_methods - self.successful_methods

        print("\n=== XPath Tracing Coverage Report ===")
        clean_test_name: str = (
            self.test_name.split("[")[0] if "[" in self.test_name else self.test_name
        )
        print(f"Test: {self.app}/{self.collection}/{clean_test_name}")
        print(f"Total traces: {len(self.traces)}")
        print(f"Attempted methods: {len(self.attempted_methods)}")
        print(f"Successful methods: {len(self.successful_methods)}")
        print(f"Failed methods: {len(self.failed_methods)}")

        if missing_methods:
            print(f"\nMissing methods (failed to trace): {list(missing_methods)}")
        else:
            print("\nAll attempted methods traced successfully!")

        print("====================================\n")
