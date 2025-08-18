"""
Usage:
    python evaluate.py lavague bookstack
    python evaluate.py pinata bookstack --provider openai
    python evaluate.py naviqate bookstack
"""

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from const import ApplicationEnum, MethodEnum, ModelEnum, ProviderEnum
from typing_extensions import Annotated

# Disable output buffering for immediate log display
os.environ["PYTHONUNBUFFERED"] = "1"

# Add project directory
PROJECT_DIR = Path(__file__).parent.parent
sys.path.append(str(PROJECT_DIR))

cli = typer.Typer(
    help="Run test cases using different agent implementations",
    no_args_is_help=True,
)


def get_runner_class(method: MethodEnum):
    """Get the appropriate runner class based on method."""
    if method == MethodEnum.lavague:
        from lavague.runner import LavagueTestRunner

        return LavagueTestRunner
    elif method == MethodEnum.pinata:
        from pinata.runner import PinataTestRunner

        return PinataTestRunner
    elif method == MethodEnum.naviqate:
        from naviqate.runner import NaviqateTestRunner

        return NaviqateTestRunner
    elif method == MethodEnum.webtestpilot:
        from webtestpilot.runner import WebTestPilotTestRunner

        return WebTestPilotTestRunner
    else:
        raise ValueError(f"Unknown method: {method}")


@cli.command()
def main(
    method: Annotated[
        MethodEnum,
        typer.Argument(help="The test method/agent to use for running tests"),
    ],
    application: Annotated[
        ApplicationEnum, typer.Argument(help="The application to test")
    ],
    model: Annotated[
        Optional[ModelEnum],
        typer.Option(
            "--model",
            "-m",
            help="LLM model to use for the agent"
        ),
    ] = ModelEnum.gpt4_1,
    provider: Annotated[
        Optional[ProviderEnum],
        typer.Option(
            "--provider",
            "-p",
            help="LLM provider (deprecated, will be removed in future versions)",
            show_default=True,
        ),
    ] = ProviderEnum.openai,
    headless: Annotated[
        bool,
        typer.Option(
            "--headless/--no-headless",
            help="Run browser in headless mode",
            show_default=True,
        ),
    ] = False,
    filter: Annotated[
        Optional[str],
        typer.Option(
            "--filter",
            "-f",
            help="Filter pattern for test case files (e.g., 'book_create')",
        ),
    ] = None,
    max_steps: Annotated[
        int,
        typer.Option(
            "--max-steps",
            help="Maximum steps for naviqate method",
            show_default=True,
        ),
    ] = 1,
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            "-o",
            help="Custom output directory for results",
        ),
    ] = ...,
    test_dir: Annotated[
        Path,
        typer.Option(
            "--test-dir",
            "-t",
            help="Custom test cases directory",
        ),
    ] = ...,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose/--no-verbose",
            "-v",
            help="Enable verbose output",
        ),
    ] = False,
):
    """Main entry point for the evaluation script."""

    # Input (Test cases) directory
    test_case_path = test_dir

    # Output directory
    output_path = output_dir / f"{method.value}_{application.value}.json"

    # Print configuration
    print("=" * 80)
    print("TEST EXECUTION CONFIGURATION")
    print("=" * 80)
    print(f"Method.    : {method.value}")
    print(f"Application: {application.value}")
    print(f"Test cases : {test_case_path}")
    print(f"Output     : {output_path}")
    print(f"Headless   : {headless}")

    if model:
        print(f"Model      : {model.value}")

    if method == MethodEnum.pinata and provider:
        print(f"LLM Provider: {provider.value}")
    elif method == MethodEnum.naviqate:
        print(f"Max Steps: {max_steps}")

    if filter:
        print(f"Filter: {filter}")

    print("=" * 80)
    print()

    # Verify test cases directory exists
    if not test_case_path.exists():
        print(f"Error: Test cases directory does not exist: {test_case_path}")
        raise typer.Exit(code=1)

    # Get the appropriate runner class
    try:
        RunnerClass = get_runner_class(method)
    except ValueError as e:
        print(f"Error: {e}")
        raise typer.Exit(code=1)

    # Prepare runner kwargs
    runner_kwargs = {
        "test_case_path": str(test_case_path),
        "test_output_path": str(output_path),
        "application": application.value,
        "headless": headless,
    }

    # Add model parameter if provided
    if model:
        runner_kwargs["model"] = model.value

    # Add method-specific parameters
    if method == MethodEnum.pinata:
        if provider:
            runner_kwargs["provider"] = provider.value
        runner_kwargs["save_screenshot"] = True
        runner_kwargs["tracer"] = True
    elif method == MethodEnum.naviqate:
        runner_kwargs["max_steps"] = max_steps
        runner_kwargs["abstracted"] = False

    # Create and run the test runner
    try:
        print(f"Initializing {method.value} test runner...")
        runner = RunnerClass(**runner_kwargs)

        print("Starting test execution...")
        results = runner.run_test_cases(filter_pattern=filter)

        # Exit with appropriate code
        if results.success_rate == 1.0:
            print("\n✓ All tests passed!")
            raise typer.Exit(code=0)
        else:
            failed_count = len([r for r in results.results if not r.success])
            print(f"\n✗ {failed_count} tests failed")
            raise typer.Exit(code=1)
    except Exception as e:
        print(f"Error during test execution: {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        raise typer.Exit(code=1)


if __name__ == "__main__":
    cli()
