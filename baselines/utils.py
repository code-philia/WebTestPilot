from __future__ import annotations
import yaml
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar, Type, Callable, Optional

from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from playwright.sync_api import expect

from baselines.const import MethodEnum, ApplicationEnum
from baselines.test_model import TestCase, TestStep, TestResult

if TYPE_CHECKING:
    from baselines.config import MethodConfig
    from baselines.base_runner import BaseTestRunner


MC = TypeVar("MC", bound="MethodConfig")

console = Console()
    

def collect_files(paths: list[Path], extension: str = "json") -> list[Path]:
    """
    Collect all files (by extension) from the provided paths.
    """
    collected_files: list[Path] = []

    for path in paths:
        if path.is_file() and path.suffix.lower() == f".{extension.lower()}":
            collected_files.append(path)
        elif path.is_dir():
            collected_files.extend(sorted(path.rglob(f"*.{extension.lower()}")))

    return collected_files


def get_test_cases(inject_bug: bool, test_paths: list[Path], bug_paths: list[Path]) -> list[TestCase]:
    """
    Load test case definitions from JSON files and (optionally) attach the
    corresponding bug file path to each TestCase based on matching filename stems.

    If `inject_bug` is True, each TestCase will receive a `bug_path` whose filename
    (without extension) matches the test file's stem. A 1:1 correspondence between
    test and bug stems is required; otherwise a ValueError is raised.

    If `inject_bug` is False, `bug_path` on each returned TestCase remains None.
    
    Args:
        inject_bug: Whether to enable bug file mapping.
        test_paths: List of Paths for test files.
        bug_paths: List of Paths for bug files.

    Returns:
        A list of TestCase instances with `bug_path` set (or None if disabled).

    Raises:
        ValueError: if there are duplicate files or unmatched files in inject_bug.
    """
    def _compile_ground_truth(code: str) -> Callable:
        """
        Turns a ground_truth code string into a callable(page) oracle.
        Returns True if all assertions pass, False if any AssertionError is raised.
        """
        def expected(page) -> bool:
            try:
                exec(code, {"page": page, "expect": expect, "__builtins__": __builtins__})
                return True
            except AssertionError:
                return False

        return expected

    test_map = {f.stem: f for f in test_paths}
    bug_map = {f.stem: f for f in bug_paths}

    if len(test_map) != len(test_paths):
        raise ValueError("Duplicate items detected in test files.")
    
    if len(bug_map) != len(bug_paths):
        raise ValueError("Duplicate items detected in bug files.")
    
    if inject_bug:
        unmatched_tests = set(test_map) - set(bug_map)
        unmatched_bugs = set(bug_map) - set(test_map)

        if unmatched_tests or unmatched_bugs:
            msg = (
                "The following are not matched. "
                f"tests: {sorted(unmatched_tests)}, "
                f"patches: {sorted(unmatched_bugs)}. "
                "Please check and make sure 1:1 mapping."
            )
            raise ValueError(msg)
        
    result: list[TestCase] = []

    for test_path in test_paths:
        data: dict = yaml.safe_load(test_path.read_text("utf-8"))

        steps = [
            {**step, "ground_truth": _compile_ground_truth(step["ground_truth"])}
            for step in data.get("steps", [])
        ]

        name = data.pop("name", None)
        setup_function = data.pop("setup_function", None)
        data.pop("steps", None)

        test_case = TestCase(
            test_path=test_path,
            bug_path=bug_map.get(test_path.stem) if inject_bug else None,
            steps=steps,
            name=name,
            setup_function=setup_function,
            **data
        )

        result.append(test_case)

    return result


def get_method_config(
    config_class: Type[MC],
    method_config_path: Optional[Path],
    *,
    run_output_dir: Path,
    application: ApplicationEnum,
    headless: bool,
    inject_bug: bool,
) -> MethodConfig:
    """
    Load a YAML method config file and expand it into a MethodConfig.
    Returns a MethodConfig built only from explicit args if no path is provided.
    """
    if method_config_path is None:
        config_dict = {}
    else:
        try:
            with method_config_path.open("r", encoding="utf-8") as f:
                config_dict = yaml.safe_load(f) or {}
        except Exception as e:
            raise RuntimeError(
                f"Failed to load method config from {method_config_path}: {e}"
            )

        if not isinstance(config_dict, dict):
            raise ValueError(
                f"Method config file {method_config_path} must contain a YAML mapping (dict) at top level."
            )

    try:
        method_config = config_class(
            run_output_dir=run_output_dir,
            application=application,
            headless=headless,
            inject_bug=inject_bug,
            **config_dict,
        )
    except TypeError as e:
        raise ValueError(
            f"Invalid fields in method config {method_config_path}: {e}"
        )

    return method_config


def get_config_class(method: MethodEnum) -> Type[MethodConfig]:
    """
    Get the appropriate config class based on method.
    """
    from baselines.config import LavagueConfig, PinataConfig, NaviqateConfig, WebTestPilotConfig

    RUNNER_CONFIGS: dict[MethodEnum, Type[MethodConfig]] = {
        MethodEnum.lavague: LavagueConfig,
        MethodEnum.pinata: PinataConfig,
        MethodEnum.naviqate: NaviqateConfig,
        MethodEnum.webtestpilot: WebTestPilotConfig
    }

    try:
        return RUNNER_CONFIGS[method]
    except KeyError:
        raise ValueError(f"Unknown method: {method}")


def get_runner_class(method: MethodEnum) -> Type[BaseTestRunner]:
    """
    Get the appropriate runner class based on method.
    """
    match method:
        case MethodEnum.lavague:
            from baselines.lavague.runner import LavagueTestRunner
            return LavagueTestRunner
    
        case MethodEnum.pinata:
            from baselines.pinata.runner import PinataTestRunner
            return PinataTestRunner
        
        case MethodEnum.naviqate:
            from baselines.naviqate.runner import NaviqateTestRunner
            return NaviqateTestRunner
    
        case MethodEnum.webtestpilot:
            from baselines.webtestpilot.runner import WebTestPilotTestRunner
            return WebTestPilotTestRunner
        
        case _:
            raise ValueError(f"Unknown method: {method}")


def display_run_input(method_config: MethodConfig, test_cases: list[TestCase]) -> None:
    # First table
    t1 = Table(title="Configuration", show_header=True, title_justify="left")
    t1.add_column("Key")
    t1.add_column("Value")

    t1.add_row("Method", str(method_config.method.value))
    t1.add_row("Application", str(method_config.application.value))
    t1.add_row("Output", str(method_config.run_output_dir))
    t1.add_row("Headless", str(method_config.headless))
    t1.add_row("Inject bug", str(method_config.inject_bug))

    # Second table
    t2 = Table(title="Test Cases", show_header=True, title_justify="left")
    t2.add_column("No.")
    t2.add_column("Test Case")
    t2.add_column("Bug Name")

    for i, test_case in enumerate(test_cases):
        bug_path = test_case.bug_path.stem if isinstance(test_case.bug_path, Path) else "-"
        t2.add_row(str(i + 1), test_case.test_path.stem, bug_path)

    # Create combined panel
    title = Text("Run Input", style="bold yellow")
    panel = Panel(renderable=Group(title, t1, t2))
    console.print(panel)


def display_run_output(test_results: list[TestResult]) -> None:
    t1 = Table(title="Test Cases", show_header=True, title_justify="left")
    t1.add_column("No.")
    t1.add_column("Test Case")
    t1.add_column("Completed")
    t1.add_column("Duration")

    completed_count = 0
    total_duration = 0.0

    for i, test_result in enumerate(test_results):
        test_case = test_result.test_case
        is_task_completed = test_result.is_task_complete
        duration = test_result.duration

        if is_task_completed:
            status = "[green]✓[/green]"
            completed_count += 1
        else:
            status = "[red]✗[/red]"

        t1.add_row(str(i + 1), test_case.test_path.stem, status, f"{duration:.2f}s")
        total_duration += duration

    # summary (n out of m)
    m = len(test_results)
    pct = (completed_count / m * 100) if m else 0
    summary = Text(
        f"Completed: {completed_count}/{m} ({pct:.1f}%)\n"
        f"Total duration: {total_duration:.2f}s"
    )

    title = Text("Run Output", style="bold yellow")
    panel = Panel(Group(title, t1, summary))
    console.print(panel)


def iter_test_cases(test_cases: list[TestCase]):
    total = len(test_cases)

    def _display_panel(idx: int, total: int, test_case: TestCase):
        title = Text(f"Test Case {idx}/{total}: {test_case.name}", style="bold yellow")
        panel = Panel(title)
        console.print()
        console.print(panel)
        console.print()

    for idx, test_case in enumerate(test_cases, start=1):
        _display_panel(idx, total, test_case)
        yield test_case


def iter_test_steps(test_case: TestCase):
    total = len(test_case.steps)

    def _display_panel(idx: int, total: int, step: TestStep):
        title = Text(f"Step {idx}/{total}", style="bold cyan")
        action = Text(f"Action: {step.action}", style="cyan")
        expected = Text(f"Expected Result: {step.expectation}", style="cyan")

        panel = Panel(Group(title, action, expected))

        console.print()
        console.print(panel)
        console.print()

    for idx, step in enumerate(test_case.steps, start=1):
        _display_panel(idx, total, step)
        yield step