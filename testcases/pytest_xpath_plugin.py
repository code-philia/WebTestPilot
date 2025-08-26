"""
Pytest Plugin for Automatic XPath Tracing

Automatically configures trace generation organized by testapp/testcollection/test_name
with minimal setup and no test code changes.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional


# Global state for current test context
_current_test_context: Optional[dict] = None


def pytest_addoption(parser: Any) -> None:
    """Add command line options for XPath tracing"""
    parser.addoption(
        "--with-xpath-tracing",
        action="store_true",
        default=False,
        help="Enable automatic XPath tracing organized by test structure",
    )
    parser.addoption(
        "--xpath-trace-dir",
        action="store",
        default="traces",
        help="Base directory for trace output (default: traces)",
    )


def pytest_configure(config: Any) -> None:
    """Configure tracing if enabled"""
    if config.getoption("--with-xpath-tracing"):
        # Set environment variables for traced_playwright.py to pick up
        os.environ["ENABLE_XPATH_TRACING"] = "true"
        os.environ["XPATH_TRACE_DEBUG"] = "true"

        # Store base trace directory
        base_dir = config.getoption("--xpath-trace-dir")
        os.environ["XPATH_BASE_TRACE_DIR"] = base_dir


def pytest_runtest_setup(item) -> None:
    """Setup tracing context for each test"""
    global _current_test_context

    if not os.getenv("ENABLE_XPATH_TRACING"):
        return

    # Extract test context from pytest node
    test_context = extract_test_context(item)
    _current_test_context = test_context

    # Set up organized output directory
    base_dir: str = os.getenv("XPATH_BASE_TRACE_DIR", "traces")
    output_path: Path = (
        Path(base_dir) / test_context["app"] / test_context["collection"]
    )
    output_path.mkdir(parents=True, exist_ok=True)

    # Set environment variables for the tracer
    os.environ["XPATH_OUTPUT_PATH"] = str(output_path)
    os.environ["XPATH_TEST_NAME"] = test_context["test_name"]
    os.environ["XPATH_TEST_APP"] = test_context["app"]
    os.environ["XPATH_TEST_COLLECTION"] = test_context["collection"]


def pytest_runtest_teardown(item, nextitem) -> None:
    """Clean up after test and save traces"""
    global _current_test_context

    # Save traces if auto-save is enabled
    from tracing.core.registry import save_all_traces, clear_registry

    # Save traces for all active TracedPage instances
    saved_count = save_all_traces()

    # Clear registry for next test
    clear_registry()

    # Debug output
    from tracing.core.utils import is_debug_enabled

    if is_debug_enabled() and saved_count > 0:
        print(f"[DEBUG] Saved traces for {saved_count} page(s)")

    _current_test_context = None


def extract_test_context(item) -> dict[str, str | None]:
    """
    Extract app/collection/test_name from pytest item

    Example:
    - File: bookstack/book.py::test_create_book
    - Returns: {"app": "bookstack", "collection": "book", "test_name": "test_create_book"}
    """
    # Get the relative path from testcases directory
    test_file: Path = Path(item.fspath)

    # Extract components
    parts: tuple[str, ...] = test_file.parts

    # Find the app name (directory containing the test)
    app_name: Optional[str] = None
    collection_name: Optional[str] = None

    # Look for the pattern: .../app_name/file.py
    for i, part in enumerate(parts):
        if part in ["bookstack", "indico", "invoiceninja", "prestashop"]:
            app_name = part
            # Collection is the filename without .py extension
            collection_name = test_file.stem
            break

    if not app_name:
        app_name = test_file.parent.name
        collection_name = test_file.stem

    return {"app": app_name, "collection": collection_name, "test_name": item.name}


def get_current_test_context() -> Optional[Dict[str, str]]:
    """Get the current test context (used by tracer)"""
    return _current_test_context


# Export plugin hooks for pytest
__all__ = [
    "pytest_addoption",
    "pytest_configure",
    "pytest_runtest_setup",
    "pytest_runtest_teardown",
]
