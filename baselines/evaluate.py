import warnings
import logging
from datetime import datetime
from pathlib import Path
from rich.logging import RichHandler

warnings.filterwarnings("ignore", category=UserWarning)
logging.basicConfig(
    level=logging.INFO, 
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
    force=True
)


import typer
from dotenv import load_dotenv
from typing_extensions import Annotated

load_dotenv()

from baselines.const import ApplicationEnum, MethodEnum
from baselines.config import MethodConfig
from baselines.base_runner import BaseTestRunner
from baselines.test_model import TestCase
from baselines.utils import (
    collect_files, 
    get_test_cases, 
    get_runner_class,
    get_config_class,
    get_method_config, 
    display_run_input,
    display_run_output
)


logger = logging.getLogger()
app = typer.Typer(
    help="Run test cases using different agent implementations",
    no_args_is_help=True,
)


@app.command()
def main(
    method: Annotated[
        MethodEnum,
        typer.Argument(help="The test method/agent to use for running tests"),
    ],    
    application: Annotated[
        ApplicationEnum, typer.Argument(help="The application to test")
    ],
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            "-o",
            help="Custom output directory for results",
            exists=False
        ),
    ],
    headless: Annotated[
        bool,
        typer.Option(
            "--headless",
            help="Run browser in headless mode"
        ),
    ] = False,
    inject_bug: Annotated[
        bool,
        typer.Option(
            "--inject-bug",
            help=(
                "Inject bugs into application when running test cases. "
                "If enabled, there must be a 1:1 mapping between "
                "--bug-paths and --test-paths by filename stem."
            )
        ),
    ] = False,
    method_config_path: Annotated[
        Path,
        typer.Option(
            "--method-config-path",
            help="Path of configuration file (.yaml file) for test method/agent",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ] = None,
    test_paths: Annotated[
        list[Path],
        typer.Option(
            "--test-paths",
            help="List of paths (.yaml files or directories) to load test cases from",
        ),
    ] = [],
    bug_paths: Annotated[
        list[Path],
        typer.Option(
            "--bug-paths",
            help="List of paths (.js files or directories) to load bugs from",
        ),
    ] = [],
):
    # Create timestamped run directory in output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_output_dir = output_dir / f"run_{timestamp}"
    run_output_dir.mkdir(parents=True, exist_ok=False)

    # Collect test case files
    collected_test_files = collect_files(test_paths, extension="yaml")
    if not collected_test_files:
        logger.error("Provide one or more --test-paths (YAML files and/or directories)")
        raise typer.Exit(code=1)
    
    # Collect bug patch files
    collected_bug_files = collect_files(bug_paths, extension="js") if inject_bug else []

    # Load test case as TestCase, get runner class, get method config
    try:
        test_cases: list[TestCase] = get_test_cases(inject_bug, collected_test_files, collected_bug_files)
        RunnerClass = get_runner_class(method)
        ConfigClass = get_config_class(method)
        method_config = get_method_config(
            ConfigClass,
            method_config_path,
            run_output_dir=run_output_dir,
            application=application,
            headless=headless,
            inject_bug=inject_bug
        )
        
    except ValueError as e:
        logger.error(e)
        raise typer.Exit(code=1)
    
    # Create and run the test runner
    try:
        display_run_input(method_config, test_cases)

        logger.info(f"Initializing {method.value} test runner.")
        runner: BaseTestRunner = RunnerClass(method_config)

        logger.info("Starting test execution.")
        test_results = runner.run_test_cases(test_cases)
        return

    except Exception as e:
        logger.error(e, exc_info=True)
        raise typer.Exit(code=1)
    
    finally:
        display_run_output(test_results if test_results else [])


if __name__ == "__main__":
    app()
